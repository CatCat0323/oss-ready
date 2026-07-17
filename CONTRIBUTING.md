# Contributing to oss-ready

Thank you for helping repositories become easier to use and maintain.

## Before opening a change

- Search existing issues and pull requests.
- Open an issue first for large features or scoring changes.
- Keep checks objective, explainable, and detectable without network access.
- Do not add telemetry or upload repository contents.

## Local setup

```bash
git clone https://github.com/CatCat0323/oss-ready.git
cd oss-ready
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

Run the tests and scan this repository:

```bash
python -m unittest discover -s tests -v
oss-ready . --no-color
```

## Pull requests

1. Add or update tests for behavior changes.
2. Update the README and changelog when users will notice the change.
3. Keep commits focused and write a clear pull-request description.
4. Confirm that CI passes.

## Adding a rule

A new rule should have a stable ID, category, bounded point value, useful failure
message, actionable recommendation, and evidence when it passes. Avoid rules that
reward vanity metrics or impose one ecosystem's conventions on every project.

## Reporting security issues

Do not open a public issue for a vulnerability. Follow [SECURITY.md](SECURITY.md).

