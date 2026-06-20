# FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Implementation Evidence

## Metadata

- Work unit: `FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction`
- Gate: Implementation Gate
- Branch: `funddisclosure-current-stage-source-truth`
- Accepted plan commit: `d85baadfd0250dba5cf3e367e6faea8edd070a30`
- Accepted plan artifact: `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-controller-judgment-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-implementation-evidence-20260620.md`

## Scope

Implemented exactly proof-positive `current_stage.v1` source-truth direct extraction inside `FundDisclosureDocumentProcessor`.

Allowed public `current_stage.v1` value keys:

- `schema_version`
- `basic_identity`
- `share_change`
- `holdings_snapshot`
- `portfolio_managers`

No bundle-level `current_stage` field, semantic stage summary, stage status, manager/share/holding strategy change summary, market timing, valuation state, final holding/replacement judgment, `EvidenceSourceKind` expansion, public `EvidenceAnchor` expansion, parser replacement, upper-layer consumption, readiness or release claim was added.

`core_risk.v1` remains unimplemented for source-truth direct extraction and remains candidate-only/missing.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`

## Implementation Summary

- Added `current_stage.v1` direct extraction under the existing proof-positive admission path only.
- Reused existing owning-family helper logic for:
  - `basic_identity` from product essence selection/build helpers.
  - `share_change` from investor experience share-change helper.
  - `holdings_snapshot` and `portfolio_managers` from manager profile helpers.
- Direct route returns `candidate_evidence=()` for `current_stage.v1`, including direct-route missing.
- Proof-missing, proof-invalid and candidate-boundary paths preserve public missing semantics and do not promote candidate evidence into public value or anchors.
- Facade projection remains unchanged: `StructuredFundDataBundle` has no `current_stage` field and ignores `current_stage.v1` values.

## Test Coverage

Processor tests cover:

- Positive proof-positive extraction with all allowed keys, public anchors and `candidate_evidence=()`.
- Direct-route missing with candidate suppression.
- Proof-missing fail-closed behavior.
- Proof-invalid fail-closed behavior.
- Candidate-boundary blocked behavior.
- Schema guard excluding `current_stage_summary`, `stage_status`, `manager_change`, `share_scale_change`, `holding_strategy_change`, `stage_judgment`, `market_timing` and `valuation_state`.
- `core_risk.v1` non-interference.
- Existing product essence, manager profile and investor experience focused fixtures updated to the new current-stage reuse semantics.

Facade tests cover:

- No `StructuredFundDataBundle.current_stage` attribute.
- Proof-positive current-stage-relevant FDD source text does not create a bundle-level current-stage projection.
- All-six-family projection ignores `current_stage.v1`; `basic_identity`, `share_change`, `holdings_snapshot` and `portfolio_managers` still project only from their owning families.

## Validation

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py`
  - Result: passed, `181 passed`
- `uv run pytest tests/fund/test_data_extractor.py`
  - Result: passed, `40 passed`
- `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
  - Result: passed, `All checks passed!`
- `git diff --check`
  - Result: passed, no output

Additional docs consistency scan:

- `rg -n 'current_stage\\.v1.*仍未实现|current_stage\\.v1.*source-truth extraction 仍未实现|Current next entry is .*Implementation Gate|Next entry point .*Implementation Gate' docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md`
  - Result: no stale current-stage implementation-gate pointer or current-stage-unimplemented wording; matches are expected `core_risk.v1` missing/unimplemented boundary statements or current-stage implemented/no-bundle-projection statements.

## Residual Risks

- `current_stage.v1` is a fact-input field family, not a semantic current-stage judgment. A future stage summary, market/valuation state, or final hold/replace decision requires a separate schema/public contract gate.
- `StructuredFundDataBundle` still has no `current_stage` projection by design. Any bundle-level current-stage field requires a separate public contract gate.
- `core_risk.v1` remains unimplemented for FDD source-truth direct extraction and stays candidate-only/missing.
- No live/network/PDF/FDR/Docling/pdfplumber/provider/LLM validation was run or claimed.

## Completion Status

`IMPLEMENTATION_COMPLETE_NOT_READY`

Next entry point: `FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Code Review Gate`.
