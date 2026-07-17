"""Built-in repository-readiness rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from .models import CheckResult


@dataclass(frozen=True, slots=True)
class RepositoryView:
    root: Path
    files: frozenset[str]

    def matching(self, candidates: Iterable[str]) -> tuple[str, ...]:
        candidate_set = {item.casefold() for item in candidates}
        return tuple(sorted(path for path in self.files if path.casefold() in candidate_set))

    def any_prefix(self, prefixes: Iterable[str]) -> tuple[str, ...]:
        normalized = tuple(prefix.casefold() for prefix in prefixes)
        return tuple(
            sorted(path for path in self.files if path.casefold().startswith(normalized))
        )

    def any_name_contains(self, fragments: Iterable[str]) -> tuple[str, ...]:
        normalized = tuple(fragment.casefold() for fragment in fragments)
        return tuple(
            sorted(
                path
                for path in self.files
                if any(fragment in Path(path).name.casefold() for fragment in normalized)
            )
        )


Rule = Callable[[RepositoryView], CheckResult]


def _file_rule(
    *,
    rule_id: str,
    category: str,
    title: str,
    points: int,
    candidates: tuple[str, ...],
    detail_ok: str,
    detail_missing: str,
    recommendation: str,
    required: bool = False,
) -> Rule:
    def check(view: RepositoryView) -> CheckResult:
        matches = view.matching(candidates)
        passed = bool(matches)
        return CheckResult(
            id=rule_id,
            category=category,
            title=title,
            passed=passed,
            points=points if passed else 0,
            max_points=points,
            required=required,
            detail=detail_ok if passed else detail_missing,
            recommendation=None if passed else recommendation,
            evidence=matches,
        )

    return check


def _prefix_rule(
    *,
    rule_id: str,
    category: str,
    title: str,
    points: int,
    prefixes: tuple[str, ...],
    detail_ok: str,
    detail_missing: str,
    recommendation: str,
) -> Rule:
    def check(view: RepositoryView) -> CheckResult:
        matches = view.any_prefix(prefixes)
        passed = bool(matches)
        return CheckResult(
            id=rule_id,
            category=category,
            title=title,
            passed=passed,
            points=points if passed else 0,
            max_points=points,
            required=False,
            detail=detail_ok if passed else detail_missing,
            recommendation=None if passed else recommendation,
            evidence=matches[:5],
        )

    return check


def _tests_rule(view: RepositoryView) -> CheckResult:
    matches = tuple(
        sorted(
            path
            for path in view.files
            if path.casefold().startswith(("tests/", "test/", "spec/"))
            or Path(path).name.casefold().startswith(("test_", "spec_"))
            or Path(path).name.casefold().endswith(("_test.py", ".test.js", ".spec.ts"))
        )
    )
    passed = bool(matches)
    return CheckResult(
        id="quality.tests",
        category="Quality",
        title="Automated tests",
        passed=passed,
        points=10 if passed else 0,
        max_points=10,
        required=False,
        detail="Automated test files are present." if passed else "No automated tests were detected.",
        recommendation=None if passed else "Add a test suite that contributors can run locally.",
        evidence=matches[:5],
    )


def _issue_templates_rule(view: RepositoryView) -> CheckResult:
    matches = tuple(
        sorted(
            path
            for path in view.files
            if path.casefold().startswith(".github/issue_template/")
            and Path(path).suffix.casefold() in {".md", ".yml", ".yaml"}
        )
    )
    passed = bool(matches) or ".github/issue_template/config.yml" in {
        path.casefold() for path in view.files
    }
    return CheckResult(
        id="community.issue-templates",
        category="Community",
        title="Issue templates",
        passed=passed,
        points=5 if passed else 0,
        max_points=5,
        required=False,
        detail="Issue intake is structured." if passed else "No GitHub issue templates were detected.",
        recommendation=None if passed else "Add bug report and feature request templates under .github/ISSUE_TEMPLATE/.",
        evidence=matches[:5],
    )


def _dependency_updates_rule(view: RepositoryView) -> CheckResult:
    matches = view.matching((".github/dependabot.yml", ".github/dependabot.yaml", "renovate.json", ".renovaterc"))
    passed = bool(matches)
    return CheckResult(
        id="security.dependency-updates",
        category="Security",
        title="Automated dependency updates",
        passed=passed,
        points=4 if passed else 0,
        max_points=4,
        required=False,
        detail="Automated dependency updates are configured." if passed else "No dependency update automation was detected.",
        recommendation=None if passed else "Configure Dependabot or Renovate for supported package ecosystems.",
        evidence=matches,
    )


RULES: tuple[Rule, ...] = (
    _file_rule(
        rule_id="docs.readme", category="Documentation", title="README",
        points=12, candidates=("README.md", "README.rst", "README.txt", "README"),
        detail_ok="A project README is present.", detail_missing="No project README was found.",
        recommendation="Add a README with purpose, installation, usage, and contribution instructions.", required=True,
    ),
    _file_rule(
        rule_id="legal.license", category="Legal", title="Open-source license",
        points=12, candidates=("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md"),
        detail_ok="A license file is present.", detail_missing="No license file was found.",
        recommendation="Choose an OSI-approved license and add it at the repository root.", required=True,
    ),
    _file_rule(
        rule_id="community.contributing", category="Community", title="Contribution guide",
        points=8, candidates=("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"),
        detail_ok="Contribution instructions are documented.", detail_missing="No contribution guide was found.",
        recommendation="Add CONTRIBUTING.md with setup, testing, and pull-request guidance.", required=True,
    ),
    _file_rule(
        rule_id="community.code-of-conduct", category="Community", title="Code of conduct",
        points=6, candidates=("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md", "docs/CODE_OF_CONDUCT.md"),
        detail_ok="A code of conduct is present.", detail_missing="No code of conduct was found.",
        recommendation="Add a community code of conduct and an enforcement contact.",
    ),
    _file_rule(
        rule_id="security.policy", category="Security", title="Security policy",
        points=8, candidates=("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"),
        detail_ok="A vulnerability reporting policy is present.", detail_missing="No security policy was found.",
        recommendation="Add SECURITY.md with supported versions and private reporting instructions.", required=True,
    ),
    _file_rule(
        rule_id="community.support", category="Community", title="Support policy",
        points=3, candidates=("SUPPORT.md", ".github/SUPPORT.md", "docs/SUPPORT.md"),
        detail_ok="Support expectations are documented.", detail_missing="No support policy was found.",
        recommendation="Add SUPPORT.md explaining where users should ask questions.",
    ),
    _file_rule(
        rule_id="release.changelog", category="Release", title="Changelog",
        points=4, candidates=("CHANGELOG.md", "CHANGES.md", "HISTORY.md", "NEWS.md"),
        detail_ok="A changelog is present.", detail_missing="No changelog was found.",
        recommendation="Track notable user-facing changes in CHANGELOG.md.",
    ),
    _issue_templates_rule,
    _file_rule(
        rule_id="community.pull-request-template", category="Community", title="Pull request template",
        points=4, candidates=(".github/PULL_REQUEST_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md", "docs/PULL_REQUEST_TEMPLATE.md"),
        detail_ok="A pull request template is present.", detail_missing="No pull request template was found.",
        recommendation="Add a PR template covering motivation, testing, and documentation.",
    ),
    _prefix_rule(
        rule_id="quality.ci", category="Quality", title="Continuous integration",
        points=10, prefixes=(".github/workflows/", ".gitlab-ci.yml", ".circleci/"),
        detail_ok="Continuous integration configuration is present.", detail_missing="No continuous integration configuration was detected.",
        recommendation="Run tests and static checks automatically for pull requests.",
    ),
    _tests_rule,
    _file_rule(
        rule_id="project.metadata", category="Project", title="Package or build metadata",
        points=4, candidates=("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Makefile"),
        detail_ok="Project metadata or build configuration is present.", detail_missing="No recognized package or build metadata was found.",
        recommendation="Add ecosystem-standard package or build metadata.",
    ),
    _file_rule(
        rule_id="project.gitignore", category="Project", title="Git ignore rules",
        points=4, candidates=(".gitignore",),
        detail_ok="Git ignore rules are present.", detail_missing="No .gitignore file was found.",
        recommendation="Add a .gitignore appropriate for the project's toolchain.",
    ),
    _dependency_updates_rule,
)

