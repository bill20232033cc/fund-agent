# FundDisclosureDocument S5 Facade Integration Plan Controller Judgment

Date: 2026-06-19

Gate: `FundDisclosureDocument S5 Facade Integration Planning Gate`

Verdict: `ACCEPT_PLAN_READY_FOR_S5_FACADE_INTEGRATION_IMPLEMENTATION_NOT_READY`

## Scope

This judgment accepts the S5 facade integration plan as code-generation-ready for a future implementation gate.

Accepted plan:

- `docs/reviews/funddisclosuredocument-s5-facade-integration-plan-20260618.md`

Plan reviews:

- DS route/fail-closed review: `docs/reviews/plan-review-20260619-000634.md`
- MiMo architecture/test-boundary review: `docs/reviews/plan-review-20260619-000638.md`
- MiMo targeted re-review: `docs/reviews/plan-review-20260619-001232.md`
- DS targeted re-review: `docs/reviews/plan-review-20260619-001234.md`

## Controller Finding Disposition

| Finding | Disposition | Reason |
|---|---|---|
| DS Finding 1: disclosure route must explicitly handle `bond_risk_evidence` and `drawdown_metric` | accepted, fixed | Plan now requires the disclosure helper to call `_load_drawdown_metric_for_bond_fund()` and `extract_bond_risk_evidence()` using the loaded `ParsedAnnualReport`. |
| DS Finding 2: AST guard test location ambiguity | accepted, fixed | Plan now places the AST import guard in `tests/fund/test_data_extractor.py`. |
| DS Finding 3: `_active_processor_result_to_bundle()` naming ambiguity | rejected-with-reason | The helper remains semantically valid because S5 still routes only exact `active_fund`; the plan added clarification without requiring rename. |
| MiMo F2: `dispatch_key.source_kind="annual_report"` rationale missing | accepted, fixed | Plan now distinguishes route/report category from candidate artifact provenance and forbids future processors from inferring provenance from dispatch key source kind. |
| MiMo F3: missing non-candidate success-path test | accepted, fixed | Plan now requires `test_explicit_disclosure_non_candidate_admitted_produces_missing_bundle()`. |
| MiMo F4: registry resolution failure test missing | accepted, fixed | Plan now requires `test_explicit_disclosure_registry_resolution_failure_raises_no_fallback()`. |
| MiMo F5: non-active disclosure test ambiguity | accepted, fixed | Plan now separates explicit-disclosure failure from default no-disclosure legacy preservation. |
| MiMo F7: non-processor-family output semantics unclear | accepted, fixed | Plan now specifies `index_profile`, `bond_risk_evidence`, `portfolio_managers`, and `risk_characteristic_text` sources and missing/fallback behavior. |

## Accepted Plan Contract

The accepted S5 implementation gate may add only an explicit keyword-only internal/test opt-in facade parameter:

```python
disclosure_intermediate: FundDisclosureDocumentIntermediate | None = None
```

The default `FundDataExtractor.extract()` route with `disclosure_intermediate=None` must remain the current production path:

`ParsedAnnualReport` -> `FundProcessorRegistry` -> `ActiveFundAnnualProcessor` -> `StructuredFundDataBundle`.

The `fund_disclosure_document.v1` route may be exercised only when the explicit parameter is supplied. It must:

- load and identity-check `ParsedAnnualReport` through `FundDocumentRepository`;
- classify fund type from the loaded `ParsedAnnualReport`, not from candidate content;
- route only exact `active_fund + annual_report + fund_disclosure_document.v1`;
- fail closed for candidate/source/provenance/identity/processor mismatch;
- not fall back to parsed annual production route when explicit disclosure input fails;
- not fall back to direct legacy path for non-active explicit disclosure input;
- preserve candidate-only, `not_proven`, and `NOT_READY` boundaries.

## Boundaries

This judgment does not authorize:

- implementation before the next implementation gate;
- S6+ field-family extraction;
- source truth, full field correctness, parser replacement, golden/readiness, release or PR ready/merge;
- repository/source/fallback behavior changes;
- `EvidenceSourceKind` or `EvidenceAnchor` expansion;
- Service/UI/Host/renderer/quality-gate/LLM prompt/template direct consumption of candidate internals;
- live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM commands;
- cleanup, deletion or classification of unrelated Slice C residual files.

## Validation

Controller-side validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s5-facade-integration-plan-20260618.md docs/reviews/plan-review-20260619-000634.md docs/reviews/plan-review-20260619-000638.md docs/reviews/plan-review-20260619-001232.md docs/reviews/plan-review-20260619-001234.md
git status --short -- docs/reviews/funddisclosuredocument-s5-facade-integration-plan-20260618.md docs/reviews/plan-review-20260619-000634.md docs/reviews/plan-review-20260619-000638.md docs/reviews/plan-review-20260619-001232.md docs/reviews/plan-review-20260619-001234.md
```

Observed result:

- diff-check passed.
- All five plan/review artifacts are new untracked files before accepted-plan commit.

## Next Entry Point

`FundDisclosureDocument S5 Facade Integration Implementation Gate`

Release/readiness remains `NOT_READY`.
