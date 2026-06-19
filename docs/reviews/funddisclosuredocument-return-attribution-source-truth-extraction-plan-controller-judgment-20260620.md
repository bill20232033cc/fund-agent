# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Plan Controller Judgment

## Gate Metadata

- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Planning Gate`
- Classification: `heavy`
- Controller role: phaseflow controller
- Plan artifact: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Plan worker: AgentCodex
- Plan reviews:
  - `docs/reviews/plan-review-20260620-063812-ds-return-attribution-source-truth.md`
  - `docs/reviews/plan-review-20260620-063812-mimo-return-attribution-source-truth.md`
- Verdict: `ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_NOT_READY`

## Controller Decision

The plan is accepted as code-generation-ready for exactly one field family: `return_attribution.v1`.

The accepted scope is a proof-positive FundDisclosureDocument source-truth direct extraction slice that reuses the existing `FundDisclosureSourceTruthAdmissionProof` guard. The plan may allow `return_attribution.v1` to produce public `value` and `anchors` only when source-truth admission is valid. Proof-missing, proof-invalid, candidate-boundary, failure-class, missing-provenance, ambiguous, unstable-locator, or no-match paths must fail closed.

## Review Disposition

Both independent reviews concluded `PASS_WITH_FINDINGS` and recommended `PLAN_REVIEW_PASS_NOT_READY`.

Accepted as non-blocking implementation clarifications:

1. `TrackingErrorValue` construction must follow the existing direct-disclosure pattern and supply all required fields, with unavailable series/benchmark fields set to `None` and `input_period_complete=True` unless the implementation proves a narrower fail-closed result.
2. `period_label` must be human-readable report/row/heading context; `annual_report_period` remains suitable for `frequency`, not as a semantic period label.
3. Facade regression, if added, must record current `_tracking_error_for_fund_type()` behavior for non-index funds as existing facade policy, not as a processor bug.
4. Fee paragraph fallback must stay explicit and fail closed; broader fee inference remains out of scope.

No plan fix or re-review is required.

## Accepted Boundaries

- Exactly one field family: `return_attribution.v1`.
- No `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1` source-truth extraction.
- No parser replacement.
- No `EvidenceSourceKind` or `EvidenceAnchor` schema expansion.
- No `FundDocumentRepository`, source policy, fallback, cache, PDF, live/network, provider, LLM, manual reference, Docling conversion, or pdfplumber export work.
- No Service/UI/Host/renderer/quality-gate direct FDD candidate consumption.
- No real-report field correctness, full correctness, golden/readiness, release, PR, push, mark-ready, or merge claim.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate`

Implementation must follow the accepted plan and carry the non-blocking review clarifications above into implementation evidence.
