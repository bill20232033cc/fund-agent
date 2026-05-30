# Source Provenance Primary Failure Category Propagation Implementation Evidence

> Date: 2026-05-27
> Role: implementation worker
> Gate: `source provenance primary-failure-category propagation implementation gate`
> Basis: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md` and controller judgment `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-controller-judgment-20260527.md`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `source provenance primary-failure-category propagation implementation gate` |
| Truth sources | `AGENTS.md`, `docs/design.md` current sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted plan and controller judgment |
| Worker boundary | implementation only; no commit, push, PR, controller ledger update, or bounded evidence rerun |

Current architecture remains `UI -> Service -> Host -> Agent`; this implementation only touched the Agent-layer `fund_agent/fund` document/source provenance boundary. No Host/Agent/dayu package work was performed.

## Files Changed

Implementation:

- `fund_agent/fund/documents/models.py`
  - Moved ownership of `AnnualReportSourceFailureCategory` next to `AnnualReportSourceName`.
  - Added optional `AnnualReportSourceMetadata.primary_failure_category`.
  - Added exact `to_dict()` key `primary_failure_category`.
  - Updated `from_dict()` with `_normalize_failure_category()` compatibility behavior.
  - Unknown or missing category normalizes to `None`.
- `fund_agent/fund/documents/sources.py`
  - Imports `AnnualReportSourceFailureCategory` from `documents.models`.
  - Removed the local failure-category alias.
  - Updated `_mark_fallback_used(result, *, primary_failure_category=...)`.
  - In `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()`, successful fallback after prior failure records `failures[0].category`.
- `fund_agent/fund/source_provenance.py`
  - Computes `effective_category` from `source_metadata.primary_failure_category` first, falling back to the existing keyword override.
  - Keeps existing public enums and reason codes.
  - Keeps missing category as `unknown_public_metadata_absent`.

Tests:

- `tests/fund/documents/test_annual_report_sources.py`
- `tests/fund/documents/test_cache.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`

Documentation sync:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Behavior Summary

- Fallback eligibility and fail-closed source strategy were not changed.
- When the primary annual-report source fails with `not_found` or `unavailable` and a later source succeeds, the successful source metadata now records the primary failure category.
- Public source provenance now classifies fallback-backed metadata with persisted `not_found` / `unavailable` as `eligible` and `complete`.
- Defensive fail-closed categories in metadata still project as `fail_closed` and `incomplete`.
- Old cache rows or fixtures with `fallback_used=true` but no `primary_failure_category` remain `unknown_public_metadata_absent`.
- Metadata category wins over the existing test/development keyword override; the keyword remains compatible when metadata lacks a category.

## Validation Results

All required validations were feasible and passed:

| Command | Result |
|---|---|
| `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q` | passed, 69 tests |
| `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py -q` | passed, 23 tests |
| `uv run pytest tests/fund/test_extraction_snapshot.py -q` | passed, 8 tests |
| `uv run pytest tests/fund/test_extraction_score.py -q` | passed, 44 tests |
| `uv run pytest tests/fund/test_report_quality_validation.py tests/fund/test_report_writing_audit.py -q` | passed, 44 tests |
| `uv run ruff check fund_agent/fund tests/fund` | passed |
| `git diff --check` | passed |

## Residual Risks

- Existing cached metadata with `fallback_used=true` and missing `primary_failure_category` will continue to classify as `unknown_public_metadata_absent` until refreshed. This is accepted compatibility behavior.
- Multi-source chains beyond current primary + fallback semantics remain out of scope and would require a future provenance-chain schema gate.
- No bounded `110020` / `017641` evidence rerun was performed in this worker task, per handoff.
- `docs/implementation-control.md` was not updated because this worker is not the controller.

## Git Status Note

Implementation touched only the files listed above plus this evidence artifact. At validation time, the worktree also contained pre-existing untracked files not touched by this worker:

- `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
- `docs/reviews/repo-review-20260526-231040.md`
- `docs/tmux-agent-memory-store.md`
