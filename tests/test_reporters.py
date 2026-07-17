from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from oss_ready.reporters import render_json, render_markdown, render_terminal
from oss_ready.scanner import scan_repository


class ReporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.report = scan_repository(Path(self.temporary_directory.name))

    def test_json_is_machine_readable(self) -> None:
        payload = json.loads(render_json(self.report))
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["score"], 0)
        self.assertEqual(len(payload["checks"]), 14)

    def test_markdown_has_summary_and_actions(self) -> None:
        output = render_markdown(self.report)
        self.assertIn("# oss-ready report", output)
        self.assertIn("## Recommended next steps", output)
        self.assertIn("README", output)

    def test_plain_terminal_has_no_ansi_codes(self) -> None:
        output = render_terminal(self.report, color=False)
        self.assertIn("Score: 0/100 (F)", output)
        self.assertNotIn("\033[", output)


if __name__ == "__main__":
    unittest.main()

