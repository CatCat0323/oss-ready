"""Data models shared by checks, scanners, and reporters."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class CheckResult:
    """The result of one repository-readiness check."""

    id: str
    category: str
    title: str
    passed: bool
    points: int
    max_points: int
    required: bool
    detail: str
    recommendation: str | None = None
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["evidence"] = list(self.evidence)
        return value


@dataclass(frozen=True, slots=True)
class ScanReport:
    """An immutable summary of a repository scan."""

    root: Path
    results: tuple[CheckResult, ...]
    score: int
    earned_points: int
    available_points: int
    grade: str

    @property
    def passed(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def failed(self) -> int:
        return len(self.results) - self.passed

    @property
    def required_failures(self) -> tuple[CheckResult, ...]:
        return tuple(
            result for result in self.results if result.required and not result.passed
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "repository": str(self.root),
            "score": self.score,
            "grade": self.grade,
            "earned_points": self.earned_points,
            "available_points": self.available_points,
            "checks_passed": self.passed,
            "checks_failed": self.failed,
            "required_failures": [item.id for item in self.required_failures],
            "checks": [result.to_dict() for result in self.results],
        }

