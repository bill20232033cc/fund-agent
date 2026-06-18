# Docling Controlled Same-source Reference Acquisition Evidence Controller Judgment - 2026-06-16

Gate: `Docling Controlled Same-source Reference Acquisition Evidence Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_ALL_REFERENCES_AVAILABLE_READY_FOR_MULTI_SAMPLE_CORRECTNESS_EVIDENCE_NOT_READY`

## Scope

This judgment accepts bounded same-source reference acquisition evidence for S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024`.

The evidence used only the accepted public repository boundary and did not inspect returned parsed report content. It does not perform Docling correctness review and does not promote Docling to baseline.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-controlled-same-source-reference-acquisition-plan-controller-judgment-20260616.md` | Accepted acquisition plan |
| `docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-20260616.md` | Evidence artifact |
| `docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-review-local-20260616.md` | Local fallback evidence review |

## Accepted Results

| Sample | Fund code | Year | Pre metadata | Acquisition | Post metadata | Accepted |
| --- | --- | ---: | --- | --- | --- | --- |
| S4 | `006597` | 2024 | `unsafe_metadata:selected_source_not_eid` | `completed_return_discarded` | `available` / EID single-source / no fallback | yes |
| S5 | `017641` | 2024 | `unsafe_metadata:source_not_eid` | `completed_return_discarded` | `available` / EID single-source / no fallback | yes |
| S6 | `110020` | 2024 | `unsafe_metadata:source_not_eid` | `completed_return_discarded` | `available` / EID single-source / no fallback | yes |

## Accepted Metadata Facts

For all three samples:

```text
source = eid
selected_source = eid
source_mode = single_source_only
fallback_enabled = false
fallback_used = false
report_type = annual_report
metadata_identity_hash = present
```

## Review Disposition

| Item | Disposition | Controller judgment |
| --- | --- | --- |
| Public repository boundary | ACCEPT | Evidence command used `FundDocumentRepository` public methods only. |
| Parsed body non-use | ACCEPT | Command awaited `load_annual_report()` but discarded the return value; artifact does not cite body/text/table/anchor/path. |
| Same-source proof | ACCEPT | Post metadata for all three samples meets accepted proof criteria. |
| Review-channel residual | ACCEPT_RESIDUAL | Independent subagent review was unavailable; local fallback review is accepted for this evidence checkpoint. |

## Blocked / Non-claims

- This is not Docling field correctness proof.
- This is not full field correctness proof.
- This is not source truth beyond accepted metadata fields.
- This is not taxonomy compatibility proof.
- This is not raw XML/XBRL instance proof.
- This is not production parser replacement.
- This is not readiness/release/PR proof.

## Next Gate

Proceed to:

```text
Docling Multi-sample Field-family Correctness Evidence Gate
```

The next gate may use the accepted same-source reference availability for S4/S5/S6 as the prerequisite to resume bounded multi-sample Docling correctness review. It must still preserve candidate-only status and `NOT_READY`.

## Final Verdict

```text
VERDICT: ACCEPT_ALL_REFERENCES_AVAILABLE_READY_FOR_MULTI_SAMPLE_CORRECTNESS_EVIDENCE_NOT_READY
```
