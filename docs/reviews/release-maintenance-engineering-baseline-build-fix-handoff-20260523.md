# Release Maintenance Engineering Baseline Build Fix Handoff - 2026-05-23

## Controller Context

- Current gate: `release maintenance documentation / engineering-baseline alignment`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Controller role: classify this as specialist engineering-baseline fix work and delegate the bounded patch.

## Problem

The current `pyproject.toml` alignment moves the project to setuptools with PEP 621 metadata and `license = "MIT"`.
Editable/build validation fails because the classifier list still contains the legacy license classifier:

```text
License :: OSI Approved :: MIT License
```

Setuptools rejects that combination under the current PEP 639 license-expression handling and asks for the license
classifier to be removed.

## Worker Scope

Owned files:

- `pyproject.toml`
- `uv.lock`, only if the dependency lock becomes inconsistent after the metadata fix

Out of scope:

- Source code, tests, README files, design/control documents, or unrelated workspace deletions
- Reintroducing `hatchling`
- Adding `dayu-agent`, Dayu Host/Engine/tool loop, or any external Dayu runtime dependency

## Required Fix

Apply the smallest correct metadata fix that keeps MIT license metadata through the explicit `license = "MIT"` field
while removing the setuptools-incompatible legacy license classifier.

## Required Validation

The worker must run and report:

- `uv lock --check`
- `uv run python -c "import fund_agent; import pandas; print('ok')"`
- `ruff check fund_agent tests`
- `git diff --check pyproject.toml uv.lock`

## Controller Acceptance Criteria

The controller may accept the worker result only if:

- The build/import blocker is gone.
- MIT license metadata remains explicit in `pyproject.toml`.
- No runtime Dayu dependency or entry point is introduced.
- No unrelated deleted files are restored, staged, or modified.
- Validation results are recorded in a controller judgment artifact and reflected in `docs/implementation-control.md`.
