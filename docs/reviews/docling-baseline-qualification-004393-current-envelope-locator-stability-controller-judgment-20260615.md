# 004393 Current-envelope Locator Stability Controller Judgment - 2026-06-15

Gate: `004393 Current-envelope Locator Stability Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes locator stability evidence for the accepted `004393_2025` current-envelope candidate artifacts.

Reviewed evidence:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-locator-stability-evidence-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-locator-stability-evidence-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-locator-stability-evidence-review-mimo-20260615.md`

## 2. Accepted Facts

| Source kind | Classification | Accepted metrics |
| --- | --- | --- |
| `docling_pdf_candidate` | `stable_for_004393_candidate_locator_evidence` | 25 sections, 95 tables, 3,493 cells, 100% page locator, 100% bbox locator, 100% row/column locator, 524 header-flag cells |
| `pdfplumber_pdf_candidate` | `partly_stable_for_004393_candidate_locator_evidence` | 8 sections, 92 tables, 3,640 cells, 100% page locator, 94.1% bbox locator, 100% row/column locator, 0 header-flag cells |
| `eid_xbrl_html_render_candidate` | `blocked_for_004393_current_envelope` | 0 sections, 0 tables, 0 cells, route failure `eid_html_current_envelope_mapping_deferred` |

## 3. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Evidence supports locator stability only, not correctness/source truth/production/readiness. | DS review | ACCEPT | Artifact keeps non-proof boundaries and routes next step to planning. |
| Validation script body was initially elided. | MiMo review | ACCEPT_FIXED | Evidence now includes replayable projection-count script. |
| Route classification is metric-supported. | DS + MiMo reviews | ACCEPT | Docling, pdfplumber, and EID classifications align with projected locator metrics. |

## 4. Controller Decision

004393 now satisfies the current-envelope locator prerequisite for a later field-family correctness pilot.

This decision means:

- Docling can be used as the candidate-layer structural locator baseline for 004393 correctness planning.
- pdfplumber remains a comparator candidate route for 004393.
- EID HTML remains blocked pending a separate EID HTML Candidate Envelope Mapping Gate.

This decision does not mean:

- extracted values are correct;
- the candidate artifacts are source truth;
- Docling or pdfplumber replaces the production parser;
- candidate internals may be consumed by production Service/Host/UI/renderer/quality gate;
- release/readiness changes.

## 5. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Field correctness remains unproven. | Deferred | `004393 Field-family Correctness Pilot Planning Gate` |
| EID HTML table-bearing current-envelope mapping remains deferred. | Deferred | Separate EID HTML Candidate Envelope Mapping Gate |
| Production consumption remains unauthorized. | Deferred | Production integration design gate only after correctness/design acceptance |
| Release/readiness remains `NOT_READY`. | Accepted residual | Controller |

## 6. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 7. Final Verdict

`VERDICT: ACCEPT_004393_LOCATOR_STABILITY_READY_FOR_FIELD_CORRECTNESS_PLANNING_NOT_READY`

Next recommended gate:

`004393 Field-family Correctness Pilot Planning Gate`

Do not proceed directly to correctness evidence, production integration, parser replacement, readiness, release, PR, or EID HTML table-bearing mapping from this gate.
