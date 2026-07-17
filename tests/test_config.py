from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from oss_ready.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def test_defaults(self) -> None:
        with TemporaryDirectory() as directory:
            config = load_config(Path(directory))

        self.assertEqual(config.min_score, 70)
        self.assertEqual(config.fail_on, "score")
        self.assertEqual(config.ignore, ())

    def test_dedicated_file_takes_precedence(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[tool.oss-ready]\nmin-score = 10\n', encoding="utf-8"
            )
            (root / ".oss-ready.toml").write_text(
                'min-score = 90\nfail-on = "required"\nignore = ["community.support"]\n',
                encoding="utf-8",
            )
            config = load_config(root)

        self.assertEqual(config.min_score, 90)
        self.assertEqual(config.fail_on, "required")
        self.assertEqual(config.ignore, ("community.support",))

    def test_invalid_score_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".oss-ready.toml").write_text("min-score = 101\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(root)


if __name__ == "__main__":
    unittest.main()

