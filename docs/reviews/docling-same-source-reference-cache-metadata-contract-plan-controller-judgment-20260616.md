# Docling Same-source Reference Cache Metadata Contract Plan Controller Judgment - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Contract Planning Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

## Scope

This judgment accepts the metadata-only cache contract plan. It does not authorize cache/FDR/repository probing, evidence execution, correctness review, source truth, field correctness, full correctness, parser replacement, readiness, release, PR, push, or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Source/repository boundary and execution constraints |
| `docs/current-startup-packet.md` | Current gate and `NOT_READY` control state |
| `docs/implementation-control.md` | Current control truth and non-goals |
| `docs/reviews/docling-multi-sample-same-source-reference-availability-artifact-only-evidence-controller-judgment-20260616.md` | Accepted blocked evidence and next-gate rationale |
| `docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-20260616.md` | Plan under judgment |
| `docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-review-ds-tmux-20260616.md` | DS plan review |

## Accepted Plan Facts

- Current public APIs are not safe for metadata-only proof:
  - `FundDocumentRepository.load_annual_report()` may call PDF acquisition/parsing paths.
  - `AnnualReportDocumentCache.load_parsed_report()` deserializes parsed report body.
  - `get_pdf_entry()` and `get_pdf_path()` expose PDF path or path existence semantics.
- A future implementation must add a narrow bodyless metadata method before any S4/S5/S6 metadata evidence gate.
- Preferred shape is repository-facing facade over cache metadata, preserving the `FundDocumentRepository` boundary while preventing `load_annual_report()` execution.
- Allowed metadata is limited to exact identity and EID single-source/no-fallback attestation fields; no PDF path, payload path, source URL, report name/code/description, timestamps, upload IDs, body text, table data, or file hash may be returned.
- `NOT_READY` remains binding.

## Review Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS F1 unsafe API assessment | ACCEPT | Current APIs are correctly rejected as evidence routes. |
| DS F2 repository boundary | ACCEPT | Repository facade is preferred for future implementation; direct cache evidence route is not accepted. |
| DS F3 allowed metadata fields | ACCEPT | Field set is narrow and leak-free for this planning stage. |
| DS F4 implementation sequencing | ACCEPT | Implementation must precede any metadata evidence gate. |
| DS F5 no-overclaim / `NOT_READY` | ACCEPT | Plan preserves no source truth, no field correctness, no parser replacement and `NOT_READY`. |
| DS F6 policy-alignment note | ACCEPT | Future implementation should reuse or align with current EID single-source/no-fallback policy checks. |
| DS F7 cross-table semantics | DEFER_TO_IMPLEMENTATION_PLAN | Whether `available` requires only `documents` metadata or also `parsed_reports` row presence must be decided in the no-live implementation gate. |
| MiMo review | DEFERRED_REVIEW_CHANNEL_RESIDUAL | MiMo pane remained blocked in a prior interactive prompt and is not counted. |

## Binding Conditions For Next Gate

The next implementation gate must:

1. Preserve `FundDocumentRepository` as the external boundary for evidence workers.
2. Add or expose only a bodyless metadata contract.
3. Avoid `load_annual_report()`, `load_parsed_report()`, `get_pdf_entry()` and `get_pdf_path()` as evidence routes.
4. Prove through tests that no parsed body, PDF path/body/metadata, source helper, live/network acquisition, Docling conversion or pdfplumber export is accessed.
5. Decide `documents` vs `parsed_reports` row semantics explicitly.
6. Preserve `NOT_READY` and make no source-truth, field-correctness, full-correctness, parser-replacement or readiness claim.

## Next Gate

Proceed to:

```text
Docling Same-source Reference Cache Metadata No-live Implementation Gate
```

This next gate may implement a narrow metadata-only repository/cache contract and targeted tests. It still must not perform S4/S5/S6 evidence probing until implementation has been reviewed and accepted.

## Final Verdict

```text
VERDICT: ACCEPT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY
```
