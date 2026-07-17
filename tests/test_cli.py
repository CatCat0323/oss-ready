from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from oss_ready.cli import run


class CliTests(unittest.TestCase):
    def test_json_output_and_never_fail_mode(self) -> None:
        with TemporaryDirectory() as directory:
            stdout = StringIO()
            code = run(
                [directory, "--format", "json", "--fail-on", "never"],
                stdout=stdout,
                stderr=StringIO(),
            )

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["score"], 0)

    def test_score_policy_returns_one_below_threshold(self) -> None:
        with TemporaryDirectory() as directory:
            code = run(
                [directory, "--min-score", "1"],
                stdout=StringIO(),
                stderr=StringIO(),
            )

        self.assertEqual(code, 1)

    def test_report_can_be_written_to_file(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "reports" / "readiness.md"
            code = run(
                [str(root), "--format", "markdown", "--output", str(target), "--fail-on", "never"],
                stdout=StringIO(),
                stderr=StringIO(),
            )

            self.assertEqual(code, 0)
            self.assertTrue(target.is_file())
            self.assertIn("# oss-ready report", target.read_text(encoding="utf-8"))

    def test_missing_path_returns_usage_error_code(self) -> None:
        stderr = StringIO()
        code = run(
            ["this-path-should-not-exist-oss-ready"],
            stdout=StringIO(),
            stderr=stderr,
        )
        self.assertEqual(code, 2)
        self.assertIn("does not exist", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

