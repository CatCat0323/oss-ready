"""Repository scanning and score calculation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import ScanReport
from .rules import RULES, RepositoryView, Rule


IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}


def _collect_files(root: Path) -> frozenset[str]:
    paths: set[str] = set()
    for path in root.rglob("*"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in IGNORED_DIRECTORIES for part in relative.parts[:-1]):
            continue
        if path.is_file():
            paths.add(relative.as_posix())
    return frozenset(paths)


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def scan_repository(
    root: str | Path,
    *,
    ignored_checks: Iterable[str] = (),
    rules: Iterable[Rule] = RULES,
) -> ScanReport:
    """Scan *root* and return a normalized readiness report."""

    resolved = Path(root).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Repository path does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {resolved}")

    ignored = set(ignored_checks)
    view = RepositoryView(root=resolved, files=_collect_files(resolved))
    results = tuple(result for rule in rules if (result := rule(view)).id not in ignored)
    earned = sum(result.points for result in results)
    available = sum(result.max_points for result in results)
    score = round(earned * 100 / available) if available else 100
    return ScanReport(
        root=resolved,
        results=results,
        score=score,
        earned_points=earned,
        available_points=available,
        grade=_grade(score),
    )

