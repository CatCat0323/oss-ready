# oss-ready

[![CI](https://github.com/CatCat0323/oss-ready/actions/workflows/ci.yml/badge.svg)](https://github.com/CatCat0323/oss-ready/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

`oss-ready` is a zero-runtime-dependency CLI that checks whether a repository is
ready for healthy open-source collaboration. It turns common repository hygiene
into an actionable score and works locally or in CI.

> 中文文档：[docs/README.zh-CN.md](docs/README.zh-CN.md)

## Why oss-ready?

Publishing source code is easy. Making a project understandable, safe to
contribute to, and maintainable is harder. `oss-ready` checks the files and
automation that help users and contributors succeed without sending repository
contents to an external service.

It currently checks:

- README, license, package/build metadata, and `.gitignore`
- contribution guide, code of conduct, support policy, and templates
- security policy and automated dependency updates
- automated tests and continuous integration
- changelog and release hygiene

## Installation

From PyPI after the first release:

```bash
python -m pip install oss-ready
```

From a source checkout:

```bash
python -m pip install -e .
```

Python 3.11 or newer is required. The installed CLI has no runtime dependencies.

## Quick start

Scan the current repository:

```bash
oss-ready
```

Scan another repository and create a Markdown report:

```bash
oss-ready ../my-project --format markdown --output reports/oss-ready.md
```

Produce JSON for automation:

```bash
oss-ready --format json --fail-on never
```

Use a stricter CI gate:

```bash
oss-ready --min-score 90 --fail-on score
```

Exit codes are stable and automation-friendly:

| Code | Meaning |
|---:|---|
| `0` | The selected policy passed |
| `1` | The repository failed the selected policy |
| `2` | The path, configuration, or output was invalid |

## Configuration

Add settings to `pyproject.toml`:

```toml
[tool.oss-ready]
min-score = 80
fail-on = "score" # score, required, or never
ignore = ["community.support"]
```

Alternatively, place the same keys at the top level of `.oss-ready.toml`.
That dedicated file takes precedence over `pyproject.toml`.

Use ignored checks sparingly. A check is removed from both the earned score and
the available-point denominator, so the report remains mathematically fair.

## Python API

```python
from oss_ready import scan_repository

report = scan_repository(".")
print(report.score, report.grade)
for result in report.required_failures:
    print(result.id, result.recommendation)
```

## Design principles

- **Local first:** source files never leave the machine.
- **Explainable:** every point maps to a named check and concrete evidence.
- **Portable:** the CLI uses only the Python standard library at runtime.
- **Useful before perfect:** recommendations help a project improve incrementally.
- **Honest:** the score measures repository readiness, not project popularity or quality.

## Development

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m oss_ready . --no-color
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow.

## Roadmap

- SPDX license identification
- Git history and release cadence checks
- GitHub Action with pull-request annotations
- Custom rules and organization policy packs
- SARIF output for code-scanning integrations

## License

MIT © 2026 [CatCat0323](https://github.com/CatCat0323)

