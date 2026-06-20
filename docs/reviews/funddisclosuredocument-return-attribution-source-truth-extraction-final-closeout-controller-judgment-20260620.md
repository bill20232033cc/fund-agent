# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Final Closeout Controller Judgment

## Verdict

`FINAL_CLOSEOUT_ACCEPTED_PR30_DRAFT_PASS_NOT_READY`

Release/readiness remains `NOT_READY`.

## Work Unit

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`

## What Changed

- Implemented proof-positive `return_attribution.v1` source-truth direct extraction in `FundDisclosureDocumentProcessor`.
- Accepted public direct values for the bounded Slice 2 shape:
  - `nav_benchmark_performance`
  - `fee_schedule`
  - `tracking_error`
- Preserved fail-closed source-truth admission:
  - missing/invalid `FundDisclosureSourceTruthAdmissionProof` does not emit public values or anchors;
  - `candidate_boundary is None` remains necessary but not sufficient;
  - non-null `failure_class` and missing provenance keep source-truth direct extraction blocked.
- Preserved candidate-only behavior for non-proof-positive FDD paths.
- Added facade regression coverage proving explicit `FundDisclosureDocument` projection to `StructuredFundDataBundle` for fee schedule and NAV/benchmark performance while preserving non-index tracking-error missing semantics.
- Synchronized `docs/design.md`, `fund_agent/fund/README.md`, controller artifacts and control/startup docs for the accepted boundary.
- Created draft PR #30:
  `https://github.com/bill20232033cc/fund-agent/pull/30`

## What Was Verified

- Slice 1 targeted validation: `125 passed`, ruff passed, `git diff --check` passed.
- Slice 2 targeted validation: `133 passed`, ruff passed, `git diff --check` passed.
- Slice 3 targeted validation: `135 passed`, ruff passed, `git diff --check` passed.
- Slice 4 targeted validation: `170 passed`, ruff passed, `git diff --check` passed.
- Aggregate deepreview: `docs/reviews/code-review-20260620-080325.md` -> no substantive findings.
- PR review: `docs/reviews/pr-30-review-20260620-081341.md` -> no substantive findings.
- PR #30 CI `test` at head `0b1bb8180a058f81e1ffe6b2e0be006897f4de6d`: success.
- PR #30 merge state after follow-up push: `CLEAN`.
- PR #30 remains open and draft; no merge, mark-ready, approval or reviewer request was performed.

## Boundary Judgment

Accepted:

- `return_attribution.v1` has proof-positive FDD source-truth direct extraction for the bounded Slice 2 public shape.
- `product_essence.v1` remains previously accepted as proof-positive FDD source-truth direct extraction.
- Candidate evidence remains candidate-only unless the proof-positive direct route is satisfied.
- Public anchors remain existing `annual_report` anchors; no new public source kind is introduced.

Not accepted / still forbidden:

- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` source-truth direct extraction.
- Real-report field correctness.
- Full field correctness.
- Production parser replacement.
- `EvidenceSourceKind` / `EvidenceAnchor` expansion.
- Repository/source/fallback/cache/PDF/live/provider/LLM behavior change.
- Direct Service/UI/Host/renderer/quality-gate/LLM prompt consumption of FDD candidates.
- PR mark-ready, merge, release or readiness transition.

## Draft PR

- PR: `https://github.com/bill20232033cc/fund-agent/pull/30`
- State: open draft.
- Head branch: `funddisclosure-return-attribution-source-truth`.
- Head: `0b1bb8180a058f81e1ffe6b2e0be006897f4de6d`.
- Merge state: `CLEAN`.
- CI: `test` success.

## Remaining Risks / Owners

| Residual | Owner | Destination |
|---|---|---|
| PR #30 remains draft/open and is not marked ready or merged | Controller / user decision | `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction PR #30 Disposition Gate` |
| `manager_profile.v1` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Future `manager_profile.v1` source-truth planning gate after PR #30 disposition |
| `investor_experience.v1` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Future `investor_experience.v1` source-truth planning gate |
| `current_stage.v1` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Future `current_stage.v1` source-truth planning gate |
| `core_risk.v1` source-truth direct extraction remains unimplemented | Fund extractor owner + controller | Future `core_risk.v1` source-truth planning gate |
| Real-report field correctness, full field correctness, parser replacement, golden/readiness and release remain unproven | Fund documents evidence owner | Separate evidence/readiness gates |
| Pre-existing untracked residue remains outside this work unit | Artifact owners/controller | Separate artifact disposition gate if authorized |

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction PR #30 Disposition Gate`

That gate may decide whether to mark PR #30 ready and/or merge it. It must not force-push/reset, implement additional source-truth families, claim parser replacement, claim real-report correctness, or claim readiness/release.
