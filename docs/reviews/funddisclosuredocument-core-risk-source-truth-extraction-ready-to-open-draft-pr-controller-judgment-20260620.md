# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: Ready-to-open-draft-PR Gate
- Branch: `funddisclosure-core-risk-source-truth`
- Local head: `91c2576`
- Stacked base branch: `funddisclosure-current-stage-source-truth`
- Stacked base remote head: `647a32eda3828705b8763de44258a9c821c86396`
- Draft PR base candidate: `funddisclosure-current-stage-source-truth`
- Draft PR head candidate: `funddisclosure-core-risk-source-truth`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-ready-to-open-draft-pr-controller-judgment-20260620.md`

## Verdict

`ACCEPT_READY_TO_OPEN_DRAFT_PR_NOT_READY`

The work unit has passed plan, implementation/code review, and aggregate deepreview gates locally. It is ready for a stacked draft PR surface after pushing a new remote branch.

## PR Surface Decision

Use a stacked draft PR:

- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`

Rationale:

- Local branch `funddisclosure-core-risk-source-truth` is ahead of `origin/funddisclosure-current-stage-source-truth` by three accepted commits:
  - `75cd23d` plan acceptance
  - `8332595` implementation/code review acceptance
  - `91c2576` aggregate deepreview acceptance
- Remote branch `origin/funddisclosure-core-risk-source-truth` does not exist yet.
- No open PR exists for head `funddisclosure-core-risk-source-truth`.
- PR 33 is open/draft with base `funddisclosure-investor-experience-source-truth`, head `funddisclosure-current-stage-source-truth`, merge state `CLEAN`, and CI `test` success at head `647a32e`.
- PR 32 is open/draft, merge state `CLEAN`, and CI `test` success at head `f81030d`.

## Scope Boundary

The draft PR must remain limited to `core_risk.v1.risk_characteristic_text` source-truth direct extraction.

No complete core-risk source truth, parser replacement, `EvidenceSourceKind` / public `EvidenceAnchor` expansion, `StructuredFundDataBundle.core_risk`, Service/UI/Host/renderer/quality-gate consumption, real-report correctness, golden/readiness, release, mark-ready, or merge is authorized.

## Next Gate

`FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Push Gate`

Release/readiness remains `NOT_READY`.
