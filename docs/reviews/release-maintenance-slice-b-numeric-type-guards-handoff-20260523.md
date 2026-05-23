# Release Maintenance Slice B Handoff — Numeric Type Guards

## Context

- Source: `docs/reviews/controller-judgment-repo-deepreview-20260523.md`
- Accepted finding: Python `bool` is an `int` subclass, so numeric parsing paths must not silently accept `True` / `False` as `1` / `0`.
- Controller status: `release maintenance`; Slice A has been prechecked as already satisfied on current main.

## Implementation Scope

Worker owns the focused implementation for Slice B:

- `fund_agent/fund/analysis/_ratios.py`
- `fund_agent/fund/analysis/risk_check.py`
- `fund_agent/fund/analysis/checklist.py`
- `fund_agent/fund/quality_gate.py`
- Focused tests under `tests/fund/analysis/` and `tests/fund/test_quality_gate.py`
- README updates only if public testing or behavior documentation changes.

Worker must not modify:

- `docs/implementation-control.md`
- GitHub remote state, PRs, branches, issues, comments, or reviewers
- Untracked historical audit files

## Acceptance Criteria

- Bool inputs fail closed in ratio parsing and related analysis numeric parsing.
- Quality gate numeric reads do not accept bool as a numeric score/rate.
- Existing valid `str`, `int`, `float`, and `Decimal` behavior remains unchanged.
- Tests cover bool inputs for ratio parsing, risk/checklist decimal parsing paths, and quality gate numeric fields.
- Focused pytest and ruff pass.

## Controller Notes

This is specialist implementation work and is delegated to a worker. Controller will integrate the returned patch, review diff against `docs/design.md` and `AGENTS.md` boundaries, run verification, record judgment, and only then create an accepted local commit.
