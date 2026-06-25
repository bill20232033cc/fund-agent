# Atomic Source Fact Store Aggregate Deepreview Fix

## Gate

- Gate: Atomic Source Fact Store / Composite Analysis View Split Aggregate Deepreview Fix Gate.
- Branch: `evidence-confirm-productionization`.
- Accepted finding: `F-01` from `docs/reviews/code-review-atomic-source-fact-store-aggregate-20260625.md`.
- Scope: Evidence Confirm bridge resolver fail-closed behavior for ambiguous bridge identity and duplicate derived-view target.

## Finding Disposition

- `F-01`: fixed in current gate.
- Ambiguous bridge identity now returns unresolved when a `ChapterFactEntry` carries both non-empty `source_fact_ids` and non-`None` `derived_view_id`.
- Derived view lookup now requires exactly one matching `projection.derived_views[*].view_id`; zero or duplicate matches return unresolved.
- V2 unresolved paths continue to produce E3 blocking issues through existing `bridge fact 无法解析 material value。` and derived provenance failure handling.
- Diagnostics now receives `_UNRESOLVED_FACT_MATERIAL` for dual bridge identity and emits zero material tokens instead of materializing arbitrary atomic or derived values.

## Changed Files

- `fund_agent/fund/evidence_confirm.py`
  - Added resolver-level mutual exclusivity guard in `_resolved_fact_material_value()`.
  - Changed `_derived_view_for_fact()` from first-match selection to exactly-one cardinality lookup.
- `tests/fund/test_evidence_confirm_atomic.py`
  - Added dual bridge identity E3 blocking regression.
  - Added duplicate derived view target E3 blocking regression.
  - Added valid single atomic bridge value-match regression.
  - Existing legacy no-bridge coverage remains unchanged.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_atomic.py -q`
  - `9 passed in 0.39s`
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q`
  - `108 passed in 0.98s`
- `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_chapter_facts_atomic.py -q`
  - `237 passed in 0.58s`
- `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_atomic.py`
  - `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_atomic.py docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-aggregate-fix-20260625.md`
  - passed

## Residual Risks

- No live/PDF/repository/source-helper/parser/provider/LLM/product CLI validation was run by instruction.
- No Service/UI/Host/renderer/quality-gate/report body/checklist/readiness behavior was modified or validated by instruction.
- Existing unrelated dirty/untracked workspace residue was observed and left untouched.
- This artifact is not a release/readiness claim; release/readiness remains not proven in this gate.

## Verdict

ATOMIC_SOURCE_FACT_STORE_AGGREGATE_FIX_READY_FOR_REREVIEW_NOT_READY
