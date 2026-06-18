# FundDisclosureDocument Candidate Source No-live Implementation Plan Controller Judgment - 2026-06-18

Verdict: PLAN_FIX_REQUIRED_NOT_READY

## Scope

Role: controller only.

Current active gate: `FundDisclosureDocument Candidate Source No-live Implementation Planning Gate`.

Reviewed artifacts:

- Plan: `docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md`
- Initial plan reviews:
  - `docs/reviews/plan-review-20260618-175426.md`
  - `docs/reviews/plan-review-20260618-195934.md`
- Targeted re-reviews:
  - `docs/reviews/plan-review-20260618-210208.md`
  - `docs/reviews/plan-review-20260618-210318.md`
- Control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Accepted schema-plan controller judgment: `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`
- S4 final closeout: `docs/reviews/s4-concrete-funddisclosuredocument-processor-final-closeout-controller-judgment-20260618.md`

This judgment does not implement code, does not accept the plan for implementation, does not authorize schema code, and does not authorize source truth, full field correctness, parser replacement, `EvidenceSourceKind` / `EvidenceAnchor` schema expansion, `FundDataExtractor` facade integration, Service/UI/Host/renderer/quality-gate direct candidate consumption, PR merge, release or readiness transition.

Release/readiness remains `NOT_READY`.

## Controller Disposition

### 1. Premature EvidenceAnchor Projection Strategy

Disposition: `accepted`

The plan currently states in §8 that future mapping will place candidate locator data in `EvidenceAnchor.note`, keeping `source_kind="annual_report"` and `page_number=None`.

This is premature for the current planning gate. The accepted schema-plan controller judgment requires no extractor/renderer/audit/source-label or production consumer integration before same-report EID HTML render versus current pdfplumber representation evidence. The current gate may define candidate schema internals only; it must not preselect the eventual `EvidenceAnchor` projection strategy.

Required plan fix:

- Replace the concrete projection statement with: projection strategy remains deferred.
- State that no `EvidenceAnchor.source_kind`, `page_number`, `note` encoding, renderer label, audit behavior or field projection strategy is selected by this gate.
- Route projection strategy to a future gate after same-report EID HTML render versus current pdfplumber representation evidence.

### 2. Failure Mapping Re-review Blockers

Disposition: `accepted`

Codex targeted re-review `docs/reviews/plan-review-20260618-210318.md` remains blocking:

- `redirect_unavailable` / `render_unavailable` split precedence is not a total ordered decision table and still conflicts on mixed facts such as non-EID redirect plus HTTP 5xx.
- `value_unvalidated` / `raw_xml_not_proven` are excluded as projection blockers in one section but the mapping function contract still accepts `FundDisclosureCandidateFailureCode` and says every value maps to a canonical category.

Required plan fix:

- Rewrite §7.3 as one total ordered decision table for `redirect_unavailable` and one for `render_unavailable`.
- Add mixed-fact tests for at least: non-EID redirect plus 5xx, non-EID redirect plus 4xx, known render URL 404, HTTP 200 empty body, HTTP 200 non-HTML body, HTML body with consistent structure absence and insufficient facts ambiguity.
- Change the mapping function input type and contract from `FundDisclosureCandidateFailureCode` to `FundDisclosureCandidateSourceFailureCode`.
- Keep an explicit fail-closed guard that raises `ValueError` if a projection blocker or unknown string reaches the mapping function.

### 3. Control Doc Drift

Disposition: `accepted-and-fixed-by-controller`

`docs/implementation-control.md` Current Gate table had stale `Implementation objective` wording from an artifact disposition / draft PR blocker gate.

Controller updated it to the current planning objective: produce a reviewed, code-generation-ready no-live implementation plan for the candidate `FundDisclosureDocument` schema, with no code implementation or boundary expansion.

## Current State

- Active gate remains `FundDisclosureDocument Candidate Source No-live Implementation Planning Gate`.
- Current sub-gate is plan fix.
- The plan is not yet accepted for implementation.
- The next worker is a planning worker, not an implementation worker.
- PR #23 remains draft/open.
- Release/readiness remains `NOT_READY`.

## Exact Next-Worker Instruction

Send to AgentDS or another planning worker:

```text
Role: planning worker, PLAN FIX gate only.

Target plan to edit:
docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md

Controller judgment to satisfy:
docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-controller-judgment-20260618.md

Allowed file:
docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md only

Required fixes:
1. In §8, remove the premature future EvidenceAnchor projection strategy that preselects `source_kind="annual_report"`, `page_number=None`, or any `EvidenceAnchor.note` encoding. Replace it with deferred projection strategy language. State that this gate does not choose `EvidenceAnchor.source_kind`, `page_number`, note encoding, renderer label, audit behavior, source-label behavior, consumer integration or field projection strategy. Route that decision to a future gate after same-report EID HTML render versus current pdfplumber representation evidence.
2. In §7.3, rewrite `redirect_unavailable` and `render_unavailable` as total ordered decision tables. Cover mixed facts explicitly: non-EID redirect plus 5xx, non-EID redirect plus 4xx, known render URL 404, HTTP 200 empty body, HTTP 200 non-HTML body, HTML body with consistent structure absence, and insufficient facts ambiguity.
3. In §7.4, change the mapping function input type and contract from `FundDisclosureCandidateFailureCode` to `FundDisclosureCandidateSourceFailureCode`. Keep explicit `ValueError` behavior for projection blockers (`value_unvalidated`, `raw_xml_not_proven`) and unknown strings.
4. Update §10.2 tests to match the total decision tables and the source-failure-only mapping function contract.

Boundaries:
- Do not edit code, tests, README, design docs, control docs, review artifacts, PR metadata or any other file.
- Do not stage, commit, push, PR, merge, or enter implementation.
- Do not run live/network/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release commands.
- Preserve `candidate_only`, `source_truth_status=not_proven`, `field_correctness_status=not_proven`, `parser_replacement_authorized=false`, `readiness_status=not_ready` and release/readiness `NOT_READY`.

Validation:
- `git diff --check -- docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md`
- `git status --short -- docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md`

Completion report:
VERDICT: PLAN_FIXED_READY_FOR_REVIEW_NOT_READY or BLOCKED_NOT_READY
ARTIFACT: docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md
VALIDATION: command results
NOTES: concise summary

Stop after plan fix. Do not run plan review.
```
