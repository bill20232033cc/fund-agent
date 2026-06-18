# Same-report Document Representation Quality Comparison Plan Controller Judgment

Date: 2026-06-14

Verdict: `ACCEPT_WITH_REVIEW_FIXES_READY_FOR_EVIDENCE_GATE_NOT_READY`

## 1. Scope

Gate: `Same-report Document Representation Quality Comparison Plan Review Gate`

This judgment reviews and closes the plan artifact:

```text
docs/reviews/same-report-document-representation-quality-comparison-plan-20260614.md
```

No code, tests, runtime behavior, parser behavior, `FundDocumentRepository` behavior, source policy, fallback policy, readiness/release state, PR state or production consumer integration is accepted by this judgment.

## 2. Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | execution and boundary rule source |
| `docs/design.md` | design truth source |
| `docs/implementation-control.md` | current control truth |
| `docs/current-startup-packet.md` | startup/control packet |
| `docs/reviews/same-report-document-representation-quality-comparison-control-sync-20260614.md` | control sync routing this gate |
| `docs/reviews/workspace-artifact-disposition-before-same-report-comparison-20260614.md` | workspace disposition and route-scope guard |
| `docs/reviews/same-report-document-representation-quality-comparison-plan-20260614.md` | plan under review |
| `docs/reviews/same-report-document-representation-quality-comparison-plan-review-ds-20260614.md` | DS review |
| `docs/reviews/same-report-document-representation-quality-comparison-plan-review-mimo-20260614.md` | MiMo review |
| `docs/reviews/same-report-document-representation-quality-comparison-plan-rereview-ds-20260614.md` | DS re-review |
| `docs/reviews/same-report-document-representation-quality-comparison-plan-rereview-mimo-20260614.md` | MiMo re-review |

## 3. Review-channel Residual

Initial DS/MiMo worker attempts returned `FAIL` because the worker prompts lacked the target plan body while file reads were not available in those worker contexts. Controller did not accept those as plan-content findings. The target plan body was then supplied to both workers, and the resulting content reviews are the accepted reviews recorded in the review artifacts above.

Disposition: `ACCEPT_AS_PROCESS_RESIDUAL_NONBLOCKING`

## 4. Findings Disposition

| Finding | Source | Disposition | Resolution |
|---|---|---|---|
| Identity matching still allowed weak report-level proof. | DS-F1 / MIMO-F1 | `ACCEPT` | Plan now requires at least one report-level discriminator, makes `identity_partly_matched` non-decisive, and requires Tier A `identity_match` for route-strength verdicts. |
| Docling input boundary needed explicit ownership wording. | DS-F2 | `ACCEPT` | Plan now requires Docling to consume only repository-approved document handles/paths produced by Fund documents for the matched report. |
| Parser execution wording could look contradictory. | MIMO-F2 | `ACCEPT` | Plan now states the planning gate runs no parsers; parser comparison belongs only to a later explicitly authorized evidence gate. |
| Mixed partial identity lacked a precise verdict. | MIMO-F3 | `ACCEPT` | Plan now includes `PARTIAL_IDENTITY_ONLY_NO_WINNER_NOT_READY`. |
| Cell text could be mistaken for field correctness. | MIMO-F4 | `ACCEPT` | Plan now uses `rendered_text_observed` and requires a `not_field_correctness` marker. |

All accepted findings are closed by DS and MiMo re-review.

## 5. Accepted Plan Facts

- The comparison is limited to document representation quality across EID HTML render, current pdfplumber and Docling candidate outputs.
- EID HTML render remains `eid_xbrl_html_render_candidate`, not raw XML/XBRL instance, field correctness proof, taxonomy proof, source truth or readiness proof.
- pdfplumber and Docling remain inside Fund documents / `FundDocumentRepository` boundaries.
- Docling remains candidate-only; no dependency install, adapter implementation or production parser replacement is accepted.
- A route-strength verdict requires at least one exact Tier A same-report identity match.
- Partial identity samples may be recorded as exploratory evidence only and cannot decide a route winner.
- Future evidence must use `rendered_text_observed` / `not_field_correctness` language to avoid value-correctness overclaim.

## 6. Blocked Claims

| Claim | Status |
|---|---|
| Raw XML direct download proven | `BLOCKED_NOT_PROVEN` |
| Field correctness proven | `BLOCKED_NOT_PROVEN` |
| Taxonomy compatibility proven | `BLOCKED_NOT_PROVEN` |
| EID HTML render promoted to source truth | `REJECTED` |
| Docling production parser replacement accepted | `REJECTED` |
| `FundDocumentRepository` behavior change accepted | `REJECTED` |
| Service/UI/Host/renderer/quality-gate direct parser or XBRL/HTML access accepted | `REJECTED` |
| Release/readiness accepted | `REJECTED_NOT_READY` |

## 7. Next Gate

Recommended next gate:

```text
Same-report Document Representation Quality Comparison Evidence Gate
```

The evidence gate must remain bounded and may only execute parser/network work if explicitly authorized inside that gate. It must preserve `NOT_READY` and stop on identity mismatch, repository boundary violation, Docling dependency install requirement, raw XML/taxonomy/field-correctness requirement, non-official EID redirect, or readiness/release scope creep.

## 8. Validation

Required local validation before leaving this gate:

```text
git status --short
git status --branch --short
git diff --check
```

No stage, commit, push or PR is accepted by this judgment.

## 9. Final Verdict

VERDICT: `ACCEPT_WITH_REVIEW_FIXES_READY_FOR_EVIDENCE_GATE_NOT_READY`
