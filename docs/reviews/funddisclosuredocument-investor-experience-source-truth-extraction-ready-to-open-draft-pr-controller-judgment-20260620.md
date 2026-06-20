# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Ready-to-open-draft-PR Gate
- Branch: `funddisclosure-investor-experience-source-truth`
- Local head: `b014a4856827c2f5781c715cc9af0619a0d33bbb`
- Stack base branch: `funddisclosure-manager-profile-source-truth`
- Stack base head: `57c992f70dd6b7c43b799508bd69f37cf1b3cd02`
- Existing base PR: PR 31 `https://github.com/bill20232033cc/fund-agent/pull/31`
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-ready-to-open-draft-pr-controller-judgment-20260620.md`

## Verdict

`READY_TO_OPEN_DRAFT_PR_ACCEPTED_NOT_READY`

The work unit is ready for a stacked draft PR surface.

## Evidence

- Current branch is `funddisclosure-investor-experience-source-truth`.
- `git status --short` shows only pre-existing unrelated untracked residue outside the current gate.
- Local accepted commits after PR 31 head are:
  - `1bf4187 gateflow: accept fdd investor experience source truth plan`
  - `8dac1fc gateflow: accept fdd investor experience source truth slice`
  - `b014a48 gateflow: accept fdd investor experience deepreview`
- `git ls-remote --heads origin funddisclosure-investor-experience-source-truth` returned no existing remote branch.
- `gh pr list --head funddisclosure-investor-experience-source-truth --state all` returned no existing PR.
- PR 31 remains open draft, head branch `funddisclosure-manager-profile-source-truth`, head `57c992f70dd6b7c43b799508bd69f37cf1b3cd02`, merge state `CLEAN`, CI `test` success.

## Surface Decision

Use a stacked draft PR:

- Base: `funddisclosure-manager-profile-source-truth`
- Head: `funddisclosure-investor-experience-source-truth`

Do not open this branch directly against `main` while PR 31 remains draft/open, because a `main`-based investor PR would include the manager_profile source-truth diff from PR 31.

## Scope Boundaries

The draft PR surface may include:

- accepted investor_experience plan artifacts;
- accepted implementation/code-review/fix/re-review artifacts;
- accepted aggregate deepreview artifacts;
- code, tests and docs for proof-positive `investor_experience.v1` direct extraction of `investor_return`, `holder_structure` and `share_change`;
- control/startup packet bookkeeping for this work unit.

The draft PR surface must not claim or perform:

- PR 31 mark-ready or merge;
- PR mark-ready for the new investor PR;
- `current_stage.v1` or `core_risk.v1` implementation;
- parser replacement;
- repository/source/PDF/Docling/pdfplumber/provider/LLM/live work;
- `EvidenceSourceKind` or public `EvidenceAnchor` expansion;
- Service/UI/Host/renderer/quality-gate direct consumption;
- golden/readiness/release transition.

## Next Gate

Next entry point:

`FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Push Gate`

Release/readiness remains `NOT_READY`.
