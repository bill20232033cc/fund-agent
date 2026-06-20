# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Final Closeout Controller Judgment

## Verdict

`FINAL_CLOSEOUT_ACCEPTED_PR34_DRAFT_PASS_NOT_READY`

Release/readiness remains `NOT_READY`.

## Work Unit

`FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`

## What Changed

- Implemented proof-positive `core_risk.v1` source-truth direct extraction in `FundDisclosureDocumentProcessor` for the bounded subvalue:
  - `risk_characteristic_text`
- Preserved fail-closed source-truth admission:
  - missing/invalid `FundDisclosureSourceTruthAdmissionProof` does not emit public values or anchors;
  - `candidate_boundary is None` remains necessary but not sufficient;
  - non-null `failure_class` and missing provenance keep source-truth direct extraction blocked.
- Preserved candidate-only behavior for non-proof-positive FDD paths.
- Kept `core_risk.v1` public direct value intentionally narrow: `schema_version` plus the existing `risk_characteristic_text.v1` value shape.
- Exposed the four unimplemented core-risk roles only as `required=False` `deferred_role` gaps on accepted direct results.
- Kept explicit FDD facade behavior limited to the existing `StructuredFundDataBundle.risk_characteristic_text` fallback; no `StructuredFundDataBundle.core_risk` field was introduced.
- Synchronized `docs/design.md`, `fund_agent/fund/README.md`, controller artifacts and control/startup docs for the accepted boundary.
- Created draft PR #34:
  `https://github.com/bill20232033cc/fund-agent/pull/34`

## What Was Verified

- Implementation validation:
  - `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q` -> `188 passed`
  - `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k product_essence` -> `25 passed, 163 deselected`
  - `uv run pytest tests/fund/test_data_extractor.py -q` -> `42 passed`
  - `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py` -> passed
  - `git diff --check` -> passed
- Code reviews:
  - `docs/reviews/code-review-core-risk-source-truth-ds-20260620.md` -> `CODE_REVIEW_PASS`
  - `docs/reviews/code-review-core-risk-source-truth-mimo-20260620.md` -> `CODE_REVIEW_PASS`
- Aggregate deepreview:
  - `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-ds-20260620.md` -> `AGGREGATE_DEEPREVIEW_PASS`
  - `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-mimo-20260620.md` -> `AGGREGATE_DEEPREVIEW_PASS`
- PR review / fix / re-review:
  - `docs/reviews/pr-34-review-ds-20260620.md` -> `PR_REVIEW_PASS` with non-blocking residuals
  - `docs/reviews/pr-34-review-codex-20260620.md` -> Codex F1 accepted and fixed
  - `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`
  - `docs/reviews/pr-34-rereview-ds-20260620.md` -> `PR_REREVIEW_PASS`
  - `docs/reviews/pr-34-rereview-mimo-20260620.md` -> `PR_REREVIEW_PASS`
- PR #34 CI `test` at head `ad25590c91f1f9db999a01e035e8f90ab394640e`: success.
- PR #34 merge state after follow-up push: `CLEAN`.
- PR #34 remains open and draft; no merge, mark-ready, approval or reviewer request was performed.

## Boundary Judgment

Accepted:

- `core_risk.v1` has proof-positive FDD source-truth direct extraction for `risk_characteristic_text`.
- `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1` and `current_stage.v1` remain previously accepted as proof-positive FDD source-truth direct extraction within their bounded public shapes.
- Candidate evidence remains candidate-only unless the proof-positive direct route is satisfied.
- Public anchors remain existing `annual_report` anchors; no new public source kind is introduced.

Not accepted / still forbidden:

- Complete `core_risk.v1` source truth.
- Source-truth direct extraction for:
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`
- Real-report field correctness.
- Full field correctness.
- Production parser replacement.
- `EvidenceSourceKind` / `EvidenceAnchor` expansion.
- `StructuredFundDataBundle.core_risk`.
- Repository/source/fallback/cache/PDF/live/provider/LLM behavior change.
- Direct Service/UI/Host/renderer/quality-gate/LLM prompt consumption of FDD candidates.
- PR mark-ready, merge, release or readiness transition.

## Draft PR

- PR: `https://github.com/bill20232033cc/fund-agent/pull/34`
- State: open draft.
- Base: `funddisclosure-current-stage-source-truth`
- Head branch: `funddisclosure-core-risk-source-truth`
- Head: `ad25590c91f1f9db999a01e035e8f90ab394640e`
- Merge state: `CLEAN`
- CI: `test` success.

## Remaining Risks / Owners

| Residual | Owner | Destination |
|---|---|---|
| PR #34 remains draft/open and is not marked ready or merged | Controller / user decision | `FundDisclosureDocument core_risk.v1 PR #34 Disposition Gate` |
| `liquidation_or_scale_risk` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | `FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Planning Gate` |
| `tracking_error_or_deviation_risk` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Same deferred risk roles planning gate |
| `turnover_or_style_drift_risk` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Same deferred risk roles planning gate |
| `concentration_risk` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Same deferred risk roles planning gate |
| Shared `risk_characteristic_text` label config may need decoupling if product/core semantics diverge | Fund extractor owner + controller | Future risk-characteristic label divergence gate |
| Binary `_core_risk_status()` may confuse future consumers that need multi-subvalue status | Fund extractor owner + controller | Deferred risk roles public-contract planning gate |
| Real-report field correctness, full field correctness, parser replacement, golden/readiness and release remain unproven | Fund documents evidence owner | Separate evidence/readiness gates |
| Pre-existing untracked residue remains outside this work unit | Artifact owners/controller | Separate artifact disposition gate if authorized |

## Next Entry Point

`FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Planning Gate`

That gate must start from the four deferred risk roles and decide whether they should enter `core_risk.v1` public value, bundle projection, or remain candidate-only. It must not force-push/reset, mark PR #34 ready, merge, claim parser replacement, claim real-report correctness, or claim readiness/release.
