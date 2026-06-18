# Fund Processor/Extractor S1 Draft PR External-state Gate

Date: 2026-06-18

Verdict: `DRAFT_PR_EXTERNAL_STATE_UPDATED_NOT_READY`

Scope: push the accepted S1 branch, reuse/update the existing draft PR, inspect CI, and apply the minimum CI-unblock fix. This gate does not mark the PR ready for review, merge, release, or readiness.

## External State

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Draft PR: `https://github.com/bill20232033cc/fund-agent/pull/22`
- PR state: open draft
- PR title after update: `Draft PR: Fund Processor/Extractor S1`
- PR base/head: `main` <- `feat/mvp-llm-incomplete-run-artifacts`

## CI Failure Triage

GitHub check `test` failed after the first push with:

- `tests/config/test_paths.py::test_no_independent_repository_path_defaults_outside_config_paths`
  - Offenders: `fund_agent/fund/documents/candidates/representation_handlers.py:50`, `fund_agent/fund/documents/candidates/representation_export.py:22`, `fund_agent/fund/documents/candidates/representation_export.py:23`
  - Root cause: candidate representation defaults used direct `Path("reports/...")` / `Path("cache/...")` construction instead of config path constants.
- `tests/fund/documents/test_candidate_representation_handlers.py::test_default_docling_converter_binds_configured_local_artifacts_path`
  - Failure: `ModuleNotFoundError: No module named 'docling'`
  - Root cause: Docling is an optional candidate-harness dependency in CI, but the test imported it unconditionally.

## Fix

- Added config path constants for candidate representation JSON output and Docling local artifact root.
- Repointed candidate representation defaults to `fund_agent.config.paths`.
- Updated path guard tests to assert those aliases.
- Changed the default Docling converter test to `pytest.importorskip(...)` when Docling is not installed.
- Updated `fund_agent/config/README.md` to include candidate representation JSON and Docling artifact defaults.

## Validation

- `uv run pytest tests/config/test_paths.py tests/fund/documents/test_candidate_representation_handlers.py -q` -> `17 passed`
- `uv run ruff check fund_agent/config/paths.py fund_agent/fund/documents/candidates/representation_export.py fund_agent/fund/documents/candidates/representation_handlers.py tests/config/test_paths.py tests/fund/documents/test_candidate_representation_handlers.py` -> passed
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` -> `1785 passed`, total coverage `90.84%`

## Residuals

- PR remains draft.
- GitHub CI must rerun after this closeout commit is pushed.
- Release/readiness remains `NOT_READY`.
- Broader untracked historical residue remains outside this PR gate and continues to require separate disposition before any release/readiness claim.
