"""Command-line interface for oss-ready."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence, TextIO

from . import __version__
from .config import ConfigError, VALID_FAIL_MODES, load_config
from .reporters import render_json, render_markdown, render_terminal
from .scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-ready",
        description="Check whether a repository is ready for healthy open-source collaboration.",
    )
    parser.add_argument("path", nargs="?", default=".", help="repository directory (default: current directory)")
    parser.add_argument("--format", choices=("terminal", "markdown", "json"), default="terminal", dest="output_format")
    parser.add_argument("--output", type=Path, help="write the report to a file instead of stdout")
    parser.add_argument("--min-score", type=int, help="override the configured minimum score (0-100)")
    parser.add_argument("--fail-on", choices=tuple(sorted(VALID_FAIL_MODES)), help="failure policy: score, required, or never")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors in terminal output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _should_fail(*, score: int, minimum: int, required_failures: int, mode: str) -> bool:
    if mode == "never":
        return False
    if mode == "required":
        return required_failures > 0
    return score < minimum


def run(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.path).expanduser()

    try:
        config = load_config(root.resolve())
        minimum = config.min_score if args.min_score is None else args.min_score
        if not 0 <= minimum <= 100:
            parser.error("--min-score must be between 0 and 100")
        fail_on = config.fail_on if args.fail_on is None else args.fail_on
        report = scan_repository(root, ignored_checks=config.ignore)
    except (ConfigError, FileNotFoundError, NotADirectoryError, OSError) as exc:
        print(f"oss-ready: error: {exc}", file=stderr)
        return 2

    if args.output_format == "json":
        rendered = render_json(report)
    elif args.output_format == "markdown":
        rendered = render_markdown(report)
    else:
        use_color = not args.no_color and args.output is None and getattr(stdout, "isatty", lambda: False)()
        rendered = render_terminal(report, color=use_color)

    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"oss-ready: error: could not write {args.output}: {exc}", file=stderr)
            return 2
    else:
        stdout.write(rendered)

    return int(
        _should_fail(
            score=report.score,
            minimum=minimum,
            required_failures=len(report.required_failures),
            mode=fail_on,
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    return run(argv)

