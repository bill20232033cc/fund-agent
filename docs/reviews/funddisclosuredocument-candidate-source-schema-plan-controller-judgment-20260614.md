# FundDisclosureDocument Candidate Source Schema Plan Controller Judgment

Date: 2026-06-14

Gate: `FundDisclosureDocument Candidate Source Schema Planning Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_WITH_PLAN_FIX_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`

## 1. Scope

This judgment closes the schema planning gate for `eid_xbrl_html_render_candidate`.

This judgment does not authorize:

- code implementation;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- `EvidenceAnchor` schema change;
- CHAPTER_CONTRACT change;
- extractor/renderer/audit/source-label or production consumer integration;
- Service / Host / UI / renderer / quality gate direct access to EID XBRL HTML endpoints;
- raw XML/XBRL route;
- raw XML direct download claim;
- field correctness claim;
- taxonomy compatibility claim;
- source truth claim;
- readiness/release/PR claim.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-controller-judgment-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-review-ds-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-review-mimo-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-rereview-mimo-20260614.md`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/sources.py`

## 3. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS | `PASS` | `ACCEPT` |
| MiMo initial review | `FAIL` | `ACCEPT_FINDING_AND_FIX_PLAN` |
| MiMo re-review | `PASS` | `ACCEPT` |

Accepted finding:

| Finding | Controller disposition |
|---|---|
| The initial schema plan did not strongly bind same-report EID HTML render versus current pdfplumber representation evidence before any consumer integration. | `ACCEPT`; plan was patched with sequencing constraints. |

No unresolved blocker remains.

## 4. Accepted Plan Facts

| Plan fact | Controller judgment |
|---|---|
| Current `EvidenceSourceKind` is a closed literal: `annual_report`, `external_api`, `derived`. | `ACCEPT` |
| `eid_xbrl_html_render_candidate` cannot be treated as current `EvidenceAnchor.source_kind` support without a schema decision. | `ACCEPT` |
| Option B, an intermediate candidate object without mutating current `EvidenceAnchor`, is the recommended next implementation-planning strategy. | `ACCEPT` |
| Option C, representing HTML render as production `annual_report`, is not acceptable for production use because it hides missing PDF page coordinates and raw XML context. | `ACCEPT` |
| Candidate failure classes must map to canonical `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` semantics. | `ACCEPT` |
| Next implementation planning may cover only candidate representation internals. | `ACCEPT` |
| Extractor/renderer/audit/source-label or production consumer integration must wait for same-report EID HTML render versus current pdfplumber representation evidence. | `ACCEPT` |
| Docling remains later and optional after same-report comparison, not current parser replacement. | `ACCEPT` |

## 5. Binding Residuals

| Residual | Required handling |
|---|---|
| `redirect_unavailable` and `render_unavailable` need testable split rules between temporary unavailable and stable render contract drift. | Carry to no-live implementation planning. |
| Same-report comparison has not run. | Do not plan consumer integration or field projection before that evidence gate. |
| Ordinary non-REIT annual/interim HTML render coverage remains unproven. | Carry as evidence/sample residual. |
| Field correctness, unit/date semantics, raw XML/taxonomy proof and source truth remain unproven. | Separate evidence gates only. |
| Release/readiness remains `NOT_READY`. | No readiness/release/PR claim. |

## 6. Next Gate

Recommended next gate:

```text
FundDisclosureDocument Candidate Source No-live Implementation Planning Gate
```

Allowed scope:

- planning only;
- candidate representation internals only;
- candidate dataclass/module location;
- serialization / deserialization;
- locator round-trip behavior;
- canonical failure mapping tests;
- non-consumption guards proving no Service/UI/Host/renderer/quality gate direct endpoint access;
- no production `FundDocumentRepository.load_annual_report()` behavior change.

Forbidden scope:

- code implementation;
- live/provider/PDF/FDR/source/analyze/checklist/golden/readiness/release/PR commands;
- extractor/renderer/audit/source-label or production consumer integration;
- raw XML, field correctness, taxonomy compatibility, source truth or readiness claims;
- Docling adapter or parser replacement;
- Eastmoney/CNINFO/fallback expansion.

Deferred gates:

- same-report comparison evidence: EID HTML render versus current pdfplumber;
- ordinary non-REIT annual/interim sample expansion;
- optional Docling benchmark;
- raw XML endpoint research;
- field correctness validation;
- implementation gate;
- readiness/release/PR gates.

## 7. Final Verdict

`VERDICT: ACCEPT_WITH_PLAN_FIX_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`

Stop here for this gate. Do not enter implementation.
