# Docling Baseline Qualification Acquisition Status Plan Review - DS - 2026-06-15

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY`

## Findings

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| LOW | Plan keeps Docling candidate-only and `NOT_READY`; final verdict is `READY_FOR_PLAN_REVIEW_NOT_READY`. | No change required. | no |
| LOW | Local cache visibility is separated from accepted EID provenance. S2-S4 are local candidates needing no-live provenance acceptance; S5-S6 require bounded EID-only acquisition or replacement. | No change required. | no |
| LOW | S5/S6 non-EID-labeled PDFs are not used as active inputs. | No change required. | no |
| LOW | EID single-source/no-fallback is preserved. | No change required. | no |
| LOW | Route agreement is separated from field correctness/source truth. | No change required. | no |
| LOW | Gate 0A has metadata-only boundary, output path and stop rules. | Add a metadata query allowlist for `jq` to avoid accidental full body/table review. | no |
| LOW | Fund documents boundary is preserved. | In Gate 0C, state that pdfplumber full representation export must be repository-owned and not ad hoc direct PDF filesystem body reads. | no |
| LOW | Top status and final verdict used different tokens before review. | Align status with final verdict. | no |

## Review Decision

The plan has no blocking issue. Apply the three nonblocking wording fixes above, then proceed to controller judgment.
