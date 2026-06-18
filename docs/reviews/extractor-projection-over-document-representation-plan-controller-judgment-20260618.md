# Extractor Projection Over Document Representation Plan Controller Judgment - 2026-06-18

## Verdict

`ACCEPT_PLAN_WITH_BINDING_AMENDMENT_READY_FOR_IMPLEMENTATION_NOT_READY`

## Scope

This judgment accepts the S3 planning gate for `Extractor Projection Over Document Representation`. The accepted plan is:

- `docs/reviews/extractor-projection-over-document-representation-plan-20260618.md`

Review artifacts:

- `docs/reviews/extractor-projection-over-document-representation-planreview-20260618.md`
- `docs/reviews/plan-review-20260618-140227.md`
- `docs/reviews/plan-review-20260618-190000.md`
- `docs/reviews/plan-review-20260618-141953.md`

This is still `NOT_READY`: no source truth, full field correctness, production parser replacement, golden/readiness or release claim is accepted.

## Finding Disposition

The initial plan review findings are accepted and are now dispositioned as fixed by the revised plan:

1. `EvidenceSourceKind` / `EvidenceAnchor.source_kind` pollution - fixed. The accepted plan keeps public anchor source kinds limited to `annual_report`, `external_api`, and `derived`.
2. `FundDisclosureDocumentStub` in production `documents/models.py` - fixed. The accepted plan uses only test-local stubs and does not modify production document models.
3. `FundDataExtractor.extract()` facade admission without an input path - fixed. S3 is scoped to processor-contract/admission-helper only and does not modify `FundDataExtractor`, repository behavior, or production facade behavior.
4. `fund_disclosure_dispatch.py` ambiguity - fixed. The accepted plan defines `FAILURE_CLASS_ADMISSION_MAP`, `DisclosureAdmissionDecision`, and `admit_disclosure_intermediate(...)` as the exact S3 surface.
5. Failure taxonomy projection underspecified - fixed. The accepted plan maps the five canonical source failure classes to existing processor gap/source-boundary/status literals and returns an admission-decision object, not `FundProcessorResult`.
6. Test scope drift - fixed. The accepted plan uses no-live helper/registry tests and preserves candidate-only, `not_proven`, no parser replacement, and `NOT_READY` boundaries.

## Binding Amendment

Codex targeted re-review identified one nonblocking ordering ambiguity. The accepted implementation handoff must apply this precedence rule:

1. If `intermediate.failure_class is not None`, return the mapped `DisclosureAdmissionDecision` from `FAILURE_CLASS_ADMISSION_MAP`.
2. Else if `intermediate.source_provenance is None`, return `source_provenance_unsafe` with `contract_status="blocked"`.
3. Else if `intermediate.candidate_boundary is not None`, return `candidate_boundary_blocked` with `source_boundary="candidate_only"` and `contract_status="blocked"`.
4. Else return the satisfied admission decision.

This amendment is binding on the implementation gate and closes the `source_provenance_unsafe` vs `candidate_boundary_blocked` precedence risk without reopening the plan.

## Accepted Implementation Boundary

Allowed implementation files for the next gate:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/processors/fund_disclosure_dispatch.py`
- `tests/fund/processors/test_fund_disclosure_dispatch.py`
- `tests/fund/processors/test_registry.py`

Explicitly forbidden in the next gate:

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/extractors/models.py`
- Service/UI/Host/Agent/renderer/quality-gate code
- repository behavior, source acquisition, live/network/PDF/FDR/Docling conversion, pdfplumber export, provider/LLM/analyze/checklist/golden/readiness/release commands
- any source truth, full field correctness, parser replacement, readiness or release claim

## Validation Evidence

- DS targeted re-review conclusion: `pass`
- Codex targeted re-review conclusion: `pass-with-risks`, with only the precedence-order residual handled by the binding amendment above
- `git diff --check` for the plan artifact passed during plan fix

## Next Gate

`Extractor Projection Over Document Representation Implementation Gate`

The implementation gate must stop after implementation, focused no-live validation, review artifact/evidence as required by Gateflow, and must not advance to code review without controller dispatch.
