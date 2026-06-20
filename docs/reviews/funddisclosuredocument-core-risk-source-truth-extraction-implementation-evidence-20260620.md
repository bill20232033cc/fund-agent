# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Implementation Evidence

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: Implementation Gate
- Accepted plan commit: `75cd23d`
- Accepted plan: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-controller-judgment-20260620.md`
- Evidence artifact: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`

## Scope

Implemented exactly `core_risk.v1.risk_characteristic_text` source-truth direct extraction for proof-positive `FundDisclosureDocument` content input.

Out of scope and unchanged:

- No complete `core_risk.v1` source truth.
- No direct public values or anchors for `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, or `concentration_risk`.
- No `StructuredFundDataBundle.core_risk`.
- No parser replacement, repository/source/cache/PDF/Docling/pdfplumber/provider/LLM/live/readiness/release/PR/push/commit/stage work.
- No `contracts.py`, `active_annual.py`, production `data_extractor.py`, Service/UI/Host/Agent, renderer, quality gate, or template edits.

## Implementation Summary

- Added proof-positive `core_risk.v1` direct extraction in `FundDisclosureDocumentProcessor`.
- Extracted neutral risk-characteristic selector/value helpers used by both `product_essence.v1` and `core_risk.v1`.
- Preserved existing `product_essence.v1.risk_characteristic_text` value shape.
- `core_risk.v1` accepted direct value shape is exactly `schema_version` plus `risk_characteristic_text`.
- Direct `core_risk.v1` route always sets `candidate_evidence=()`, including direct missing and ambiguity.
- Accepted direct `core_risk.v1` adds four `required=False` `deferred_role` gaps for the deferred core-risk roles.
- Ambiguous risk-characteristic direct text fail-closes to `status="missing"`, `value={}`, `anchors=()`, and `ambiguous_table_or_locator`.
- Proof-missing, proof-invalid, candidate-boundary, missing provenance, and failure-class paths remain fail-closed.
- Facade tests exercise the existing core-risk fallback to `StructuredFundDataBundle.risk_characteristic_text` without editing production `fund_agent/fund/data_extractor.py`.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`
- `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`

## Validation

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
  - Result: `188 passed in 0.92s`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k product_essence`
  - Result: `25 passed, 163 deselected in 0.81s`
- `uv run pytest tests/fund/test_data_extractor.py -q`
  - Result: `42 passed in 0.83s`
- `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`
  - Result: passed with no output.

## Residual Risks

- Complete `core_risk.v1` source truth remains deferred to later independent gates.
- Deferred core-risk roles remain candidate-only/deferred and are not public values or anchors in this gate.
- This gate does not prove real-report correctness, parser replacement, full field correctness, golden/readiness, or release.

## Completion Status

Implementation, docs sync, and required validation completed locally. Ready for code review gate; no commit, stage, push, PR, readiness, or release action was performed.
