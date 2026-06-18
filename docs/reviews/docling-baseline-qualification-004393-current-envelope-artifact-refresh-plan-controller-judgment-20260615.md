# 004393 Current-envelope Candidate Artifact Refresh Plan Controller Judgment - 2026-06-15

Gate: `004393 Current-envelope Candidate Artifact Refresh Planning Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes plan review for refreshing `004393_2025` into the current candidate representation envelope.

Reviewed plan:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-review-mimo-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-rereview-ds-20260615.md`

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/reviews/docling-baseline-qualification-baseline-candidate-decision-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-locator-stability-controller-judgment-20260615.md`

## 3. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Path A could silently wrap 004393 route-specific EID HTML JSON into table-bearing current envelope and bypass deferred EID HTML mapping gate. | DS `DS-PLAN-F1` | ACCEPT_FIXED | Plan now allows EID HTML only as blocked current-envelope with route failure and zero sections/tables/cells unless a separate EID HTML Candidate Envelope Mapping Gate accepts table-bearing rules. DS targeted re-review passed. |
| Path A needs tests proving missing locator fields remain missing. | MiMo residual | ACCEPT_AS_REQUIREMENT | Plan already requires targeted tests for missing locator preservation. Implementation gate must satisfy this. |
| Path B local conversion requires explicit authorization. | DS + MiMo | ACCEPT | Plan separates Path B and requires additional authorization for CPU-heavy local PDF/Docling/pdfplumber processing. |
| Output paths must avoid clobbering legacy artifacts. | DS + MiMo | ACCEPT | Plan uses `*_current_envelope.json` paths and no-clobber requirement. |

## 4. Accepted Plan Requirements

Implementation/evidence gate must:

- prefer Path A no-conversion wrapper first;
- read 004393 legacy JSON as candidate input only, not source truth;
- avoid inventing missing page, bbox, row/column, header, section, table, or cell facts;
- write only new current-envelope output paths;
- keep 004393 EID HTML blocked unless a separate accepted EID HTML mapping gate exists;
- validate outputs through `project_candidate_representation`;
- keep all statuses non-proof and blocked claims complete;
- keep release/readiness as `NOT_READY`;
- avoid production repository/source/parser/Service/Host/UI/renderer/quality gate changes.

If Path A cannot map Docling/pdfplumber without inventing facts, implementation/evidence must stop with:

```text
NEEDS_NO_LIVE_LOCAL_CONVERSION_GATE_NOT_READY
```

## 5. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 6. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_004393_CURRENT_ENVELOPE_REFRESH_IMPLEMENTATION_EVIDENCE_GATE_NOT_READY`

Next gate:

`004393 Current-envelope Candidate Artifact Refresh No-live Implementation/Evidence Gate`

Default path:

`Path A no-conversion wrapper first`

Do not proceed to Path B local conversion unless Path A is insufficient and a separate authorization/decision records that local PDF/Docling/pdfplumber processing is allowed.
