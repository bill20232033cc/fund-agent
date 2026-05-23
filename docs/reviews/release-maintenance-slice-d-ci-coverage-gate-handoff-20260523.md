# Release Maintenance Slice D Handoff — CI Coverage Gate

## Context

- Source: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` Slice D.
- Accepted finding: CI currently runs `uv run pytest -q` without coverage enforcement, while dev dependencies already include `pytest-cov` and `tests/README.md` documents a coverage gate.
- Controller precheck: Slice D remains open on current main.

## Implementation Scope

Worker owns the focused implementation:

- `.github/workflows/ci.yml`
- `tests/test_repo_hygiene.py`
- `tests/README.md`
- `README.md`

## Acceptance Criteria

- CI runs pytest with coverage collection and an explicit fail-under threshold.
- Threshold remains aligned with existing documented value unless the implementation justifies a better current threshold.
- Repository hygiene test asserts the CI coverage command, not only bare `pytest -q`.
- README and `tests/README.md` describe the same CI command.
- Focused pytest and ruff pass.

## Non-Goals

- Do not raise coverage target beyond the current accepted project baseline unless separately justified.
- Do not change production code.
- Do not push or mutate GitHub remote state.
- Do not edit `docs/implementation-control.md`; controller will update tracking separately if needed.
