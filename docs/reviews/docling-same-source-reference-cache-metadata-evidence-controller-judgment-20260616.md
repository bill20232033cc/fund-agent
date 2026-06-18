# Docling Same-source Reference Cache Metadata Evidence Controller Judgment - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Evidence Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_BLOCKED_UNSAFE_METADATA_NOT_READY`

## Scope

This judgment accepts metadata evidence for S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024`.

The evidence used only the accepted repository facade `FundDocumentRepository.get_annual_report_reference_metadata()`. It did not call `load_annual_report()`, cache internals, PDF paths, parsed body, live/network/EID acquisition, Docling, pdfplumber, provider/LLM, analyze/checklist/golden/readiness/release, PR, push or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-controller-judgment-20260616.md` | Accepted metadata contract implementation |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-20260616.md` | Metadata evidence |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-review-ds-tmux-20260616.md` | DS evidence review |

## Accepted Result

| Sample | Fund code | Year | Accepted status | Reason |
| --- | --- | ---: | --- | --- |
| S4 | `006597` | 2024 | `unsafe_metadata` | `selected_source_not_eid` |
| S5 | `017641` | 2024 | `unsafe_metadata` | `source_not_eid` |
| S6 | `110020` | 2024 | `unsafe_metadata` | `source_not_eid` |

Controller accepts the evidence verdict:

```text
BLOCKED_UNSAFE_METADATA_NOT_READY
```

## Review Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS F1 repository boundary | ACCEPT | Evidence called only the accepted repository facade. |
| DS F2 forbidden paths avoided | ACCEPT | No `load_annual_report()`, cache internals, PDF, parsed body, live/network, Docling or pdfplumber path was used. |
| DS F3 status interpretation | ACCEPT | `unsafe_metadata` is not same-source proof and does not prove EID public annual reports are unavailable. |
| DS F4 non-claims | ACCEPT | Source truth, field correctness, full correctness, readiness and parser replacement are not claimed. |
| DS F5 next gate recommendation | ACCEPT | Direct correctness review remains blocked; a route decision is required. |
| DS F6 residual ownership | ACCEPT | Residuals are assigned to controller/future gates. |
| DS F7 verdict consistency | ACCEPT | Evidence verdict matches sample results. |
| MiMo review | DEFERRED_REVIEW_CHANNEL_RESIDUAL | MiMo pane remained blocked in a prior interactive prompt and is not counted. |

## Blocked Claims

- S4/S5/S6 same-source reference availability is not proven.
- Multi-sample Docling field-family correctness review cannot resume.
- Docling baseline is not promoted beyond the accepted `004393 / 2025` bounded pilot.
- This evidence does not prove EID annual reports are unavailable.
- This evidence does not authorize live/EID/PDF acquisition.

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| S4/S5/S6 reference proof absent | Controller / user decision | Choose whether to keep blocked, authorize controlled acquisition, or narrow baseline. |
| Local cache metadata unsafe | Future evidence/acquisition gate | Do not use current cache metadata as proof. |
| Multi-sample correctness expansion blocked | Controller | Do not resume correctness review without a new accepted reference route. |

## Next Gate Recommendation

Proceed to:

```text
Docling Baseline Qualification Scope Decision Gate
```

The decision gate should choose exactly one main route:

1. Keep multi-sample correctness expansion blocked and narrow Docling baseline qualification to `004393 / 2025` bounded pilot.
2. Open a controlled same-source reference acquisition gate for S4/S5/S6.
3. Defer Docling baseline qualification and return to another product mainline.

Because option 2 involves source/reference acquisition, it must remain a separately explicit gate before any live/EID/PDF command.

## Final Verdict

```text
VERDICT: ACCEPT_BLOCKED_UNSAFE_METADATA_NOT_READY
```
