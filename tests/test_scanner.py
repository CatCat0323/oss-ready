from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from oss_ready.scanner import scan_repository


class ScannerTests(unittest.TestCase):
    def test_empty_repository_has_required_failures(self) -> None:
        with TemporaryDirectory() as directory:
            report = scan_repository(directory)

        self.assertEqual(report.score, 0)
        self.assertEqual(report.grade, "F")
        self.assertEqual(
            {result.id for result in report.required_failures},
            {
                "docs.readme",
                "legal.license",
                "community.contributing",
                "security.policy",
            },
        )

    def test_repository_with_core_files_scores_points(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md"):
                (root / filename).write_text("content", encoding="utf-8")
            report = scan_repository(root)

        self.assertGreater(report.score, 0)
        self.assertFalse(report.required_failures)

    def test_filenames_are_matched_case_insensitively(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "readme.MD").write_text("content", encoding="utf-8")
            report = scan_repository(root)

        readme = next(result for result in report.results if result.id == "docs.readme")
        self.assertTrue(readme.passed)

    def test_ignored_check_is_removed_from_denominator(self) -> None:
        with TemporaryDirectory() as directory:
            report = scan_repository(directory, ignored_checks=("docs.readme",))

        self.assertNotIn("docs.readme", {result.id for result in report.results})
        self.assertEqual(report.available_points, 82)

    def test_non_directory_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.write_text("not a repository", encoding="utf-8")
            with self.assertRaises(NotADirectoryError):
                scan_repository(path)


if __name__ == "__main__":
    unittest.main()
