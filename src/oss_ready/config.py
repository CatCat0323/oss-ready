"""Configuration loading for oss-ready."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any


VALID_FAIL_MODES = {"score", "required", "never"}


class ConfigError(ValueError):
    """Raised when repository configuration is invalid."""


@dataclass(frozen=True, slots=True)
class Config:
    min_score: int = 70
    fail_on: str = "score"
    ignore: tuple[str, ...] = ()


def _table_from_file(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Could not read {path.name}: {exc}") from exc

    if path.name == "pyproject.toml":
        table = data.get("tool", {}).get("oss-ready", {})
    else:
        table = data.get("tool", {}).get("oss-ready", data)
    if not isinstance(table, dict):
        raise ConfigError(f"The oss-ready configuration in {path.name} must be a table.")
    return table


def load_config(root: Path) -> Config:
    """Load configuration, preferring .oss-ready.toml over pyproject.toml."""

    config_path = root / ".oss-ready.toml"
    pyproject_path = root / "pyproject.toml"
    table: dict[str, Any] = {}
    if config_path.is_file():
        table = _table_from_file(config_path)
    elif pyproject_path.is_file():
        table = _table_from_file(pyproject_path)

    min_score = table.get("min-score", 70)
    fail_on = table.get("fail-on", "score")
    ignore = table.get("ignore", [])

    if isinstance(min_score, bool) or not isinstance(min_score, int):
        raise ConfigError("min-score must be an integer between 0 and 100.")
    if not 0 <= min_score <= 100:
        raise ConfigError("min-score must be between 0 and 100.")
    if fail_on not in VALID_FAIL_MODES:
        raise ConfigError("fail-on must be one of: score, required, never.")
    if not isinstance(ignore, list) or not all(isinstance(item, str) for item in ignore):
        raise ConfigError("ignore must be an array of check IDs.")

    return Config(min_score=min_score, fail_on=fail_on, ignore=tuple(ignore))

