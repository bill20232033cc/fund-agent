# Controller Judgment: source provenance primary-failure-category propagation implementation

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance primary-failure-category propagation implementation gate`
> Latest accepted checkpoint before gate: `7e91f0d docs: accept source provenance failure category plan`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering implementation | `source provenance primary-failure-category propagation design plan accepted locally` |
| Reviewed implementation gate | `source provenance primary-failure-category propagation implementation gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The implementation matches the accepted minimal slice. It persists repository primary source failure category at the document-source metadata boundary and projects it through the existing public provenance fields without changing source ordering, fallback eligibility, fail-closed behavior, renderer, score/FQ0-FQ6, default analyze/checklist control flow, Host/Agent/dayu, baseline, or golden behavior.

## Accepted Behavior

- `AnnualReportSourceFailureCategory` is owned by `fund_agent/fund/documents/models.py`.
- `AnnualReportSourceMetadata.primary_failure_category` is optional, serialized with exact key `primary_failure_category`, and old or invalid metadata degrades to `None`.
- `AnnualReportSourceOrchestrator` records `failures[0].category` only when fallback succeeds after an eligible primary failure.
- Fail-closed categories still raise before fallback success.
- `project_public_source_provenance()` uses metadata-owned category first and only falls back to the explicit keyword when metadata category is missing.
- Missing category remains `unknown_public_metadata_absent`.

## Review Summary

| Reviewer | Artifact | Verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-review-mimo-20260527.md` | `PASS` | Accepted. No material findings. |
| AgentGLM | `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-review-glm-20260527.md` | `PASS` | Accepted. No material findings. |

## Validation Summary

| Command | Result |
|---|---|
| `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q` | passed, 69 tests |
| `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py -q` | passed, 23 tests |
| `uv run pytest tests/fund/test_extraction_snapshot.py -q` | passed, 8 tests |
| `uv run pytest tests/fund/test_extraction_score.py -q` | passed, 44 tests |
| `uv run pytest tests/fund/test_report_quality_validation.py tests/fund/test_report_writing_audit.py -q` | passed, 44 tests |
| `uv run ruff check fund_agent/fund tests/fund` | passed |
| `git diff --check` | passed |

## Finding Disposition

No material findings were raised.

## Residual Risks

- Existing cached metadata with `fallback_used=true` and missing `primary_failure_category` will continue to classify as `unknown_public_metadata_absent` until refreshed. The next evidence gate must explicitly decide whether and how to refresh bounded public evidence.
- Multi-source chains beyond the current primary + fallback model remain out of scope and require a future provenance-chain schema gate.
- `110020` / `017641` still need a post-implementation bounded evidence rerun before any corpus decision.
- This gate does not promote any baseline/golden/fixture/clean-denominator state.

## Next Entry Point

`source provenance post-implementation bounded evidence rerun plan/review gate`

The next gate must plan and review a bounded public evidence rerun for `110020` / 2024 and `017641` / 2024. It must account for old cached metadata behavior, keep generated outputs ignored, classify only from public provenance and quality outputs, and keep every row `not_promoted` unless a later separate corpus gate authorizes promotion.
