# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Plan Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: Plan Gate / Plan Review Gate / Plan Fix Gate / Plan Re-review Gate
- Branch: `funddisclosure-core-risk-source-truth`
- Base: `origin/funddisclosure-current-stage-source-truth` at PR 33 remote head
- Plan artifact: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`
- Initial plan review: `docs/reviews/plan-review-core-risk-source-truth-ds-20260620.md`
- Targeted re-reviews:
  - `docs/reviews/plan-rereview-core-risk-source-truth-ds-20260620.md`
  - `docs/reviews/plan-rereview-core-risk-source-truth-mimo-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-controller-judgment-20260620.md`

## Verdict

`ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_NOT_READY`

The fixed plan is accepted as code-generation-ready after DS findings F1-F7 were closed. AgentDS and AgentMiMo both returned `PLAN_REREVIEW_PASS`; no new planning blocker remains.

## Dispatch Record

- AgentCodex produced the fixed plan artifact after the controller restarted the Codex TUI and re-dispatched the plan-fix task.
- AgentDS completed the controlling targeted `/planreview`.
- AgentMiMo was available for this gate, completed targeted `/planreview`, and wrote an independent re-review artifact. The controller rejected MiMo's unnecessary timestamp shell command and required the exact fixed artifact path before accepting the write.

## Accepted Findings

| Finding | Decision | Status |
|---|---|---|
| F1 product_essence selector coupling | accepted | fixed; core-risk code paths must not call `_select_product_essence_values()` and must use neutral shared risk-characteristic helpers |
| F2 misleading complete-core-risk scope | accepted | fixed; plan states this gate implements only `risk_characteristic_text` and later gates are required for complete core-risk source truth |
| F3 deferred roles invisible on direct path | accepted | fixed; accepted direct results must expose four `required=False` `deferred_role` gaps |
| F4 facade fallback first activation risk | accepted | fixed; plan requires tests for the existing `data_extractor.py` core-risk fallback path |
| F5 `_select_core_risk_values()` underspecified | accepted | fixed; plan specifies neutral helper call chain and family-neutral candidate type |
| F6 ambiguous risk-characteristic test missing | accepted | fixed; plan requires ambiguous proof-positive text to fail closed with `ambiguous_table_or_locator` |
| F7 forbidden file omission | accepted | fixed; `docs/fund-analysis-template-draft.md` is forbidden |

## Accepted Plan Scope

Implementation scope is exactly `core_risk.v1` proof-positive FDD source-truth direct extraction for the existing `risk_characteristic_text.v1` public shape.

Accepted direct `core_risk.v1` value shape is:

- `schema_version`
- `risk_characteristic_text`

The four other core-risk roles remain deferred/candidate-only:

- `liquidation_or_scale_risk`
- `tracking_error_or_deviation_risk`
- `turnover_or_style_drift_risk`
- `concentration_risk`

They must not be promoted to public values or anchors in this work unit. They must appear only as `required=False` `deferred_role` gaps on accepted direct results.

## Binding Implementation Conditions

- Implement only `core_risk.v1` `risk_characteristic_text`.
- Reuse/extract neutral shared risk-characteristic selector/value helpers; do not call `_select_product_essence_values()` from any core-risk path.
- Preserve product_essence `risk_characteristic_text` shape and projection behavior.
- Keep direct-route `candidate_evidence=()`.
- Preserve proof-missing, proof-invalid, candidate-boundary, missing-provenance, failure-class and ambiguity fail-closed behavior.
- Test the existing `StructuredFundDataBundle.risk_characteristic_text` fallback from `core_risk.v1`; do not add `StructuredFundDataBundle.core_risk`.
- No parser replacement, repository/source/cache/PDF/Docling/pdfplumber/live/network/provider/LLM work.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion.
- No Service/UI/Host/renderer/quality-gate direct FDD candidate JSON consumption.
- No real-report correctness, full field correctness, golden/readiness, release, mark-ready, merge, push, or PR mutation claim.

## Required Validation For Implementation

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k "product_essence"`
- `uv run pytest tests/fund/test_data_extractor.py -q`
- `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
- `git diff --check`

## Next Gate

After the accepted plan commit, the next entry point is:

`FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Implementation Gate`

Release/readiness remains `NOT_READY`.
