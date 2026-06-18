# Release-readiness Blocker Disposition Plan

日期：2026-06-11

角色：planning worker

Gate：`Release-readiness blocker disposition planning gate`

Classification：`heavy`

Accepted NOT_READY evidence checkpoint：`d0d9672`

Control sync checkpoint：`5bdc717`

Primary accepted evidence：

- `docs/reviews/mvp-release-readiness-cleanliness-evidence-20260611.md`
- `docs/reviews/mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-153309.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`

## 1. Plan Status

This artifact is a planning artifact only.

It does not accept release readiness, PR readiness, cleanup completion, `.gitignore` acceptance, archive/delete/move authorization, artifact promotion, live evidence acceptance, provider acceptance, PDF corpus acceptance, golden/readiness promotion or external release state.

It does not implement any disposition action. No residue is deleted, moved, archived, ignored, imported, staged, promoted, committed, pushed, merged, marked ready or used as proof by this plan.

The starting fact is the accepted `NOT_READY` evidence: A6 failed because visible blocker residue remains unresolved and has not been explicitly accepted as release-readiness residual.

PR 22 pane/footer/context text is residue only. It is not reviewer unavailability evidence, release-state evidence, readiness evidence or proof. MiMo and DS are usable for this gate's required independent plan reviews.

## 2. Decision Enum

Allowed disposition paths for this plan:

- `ACCEPT_AS_RELEASE_RESIDUAL`: a future controller judgment may accept the group as a non-clean residual for release-readiness purposes, with explicit owner, reason, release impact and next gate. This does not clean or promote the files.
- `PROMOTE_WITH_PROVENANCE`: a future provenance gate may map exact paths to accepted gates and promote only those exact artifacts that are reviewed as durable evidence. Promotion requires path-level provenance and controller judgment.
- `DEFER_TO_IGNORE_RULE_GATE`: a future ignore-rule gate may add or adjust ignore rules for repeatable generated output only. This plan does not edit `.gitignore`.
- `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE`: a future gate may archive, delete or move exact paths only after explicit authorization and reviewed path list. This plan grants no destructive permission.
- `USER_DECISION_REQUIRED`: user-owned, ambiguous or local-data paths remain blocked until the user chooses leave-as-local, archive, delete, move, import, or another non-destructive treatment.
- `REJECT_AS_RELEASE_EVIDENCE`: the group may remain in the workspace only if it is not used as source truth, fixture, product scope, proof, readiness evidence or release evidence.

## 3. Disposition Matrix

| Blocker / material residual group | Current basis | Planned disposition path | Owner | Required future artifact / evidence | User authorization required? | Exact non-goals |
|---|---|---|---|---|---|---|
| Other untracked `docs/reviews/*.md` / `*.json` outside the accepted current evidence chain | A6 blocker; accepted evidence lists 34 untracked review entries and says exact path-level provenance is missing | `PROMOTE_WITH_PROVENANCE` for exact artifacts that map to accepted gates; `REJECT_AS_RELEASE_EVIDENCE` for unmapped residue; possible `ACCEPT_AS_RELEASE_RESIDUAL` only after controller judgment names exact residuals | Controller + artifact owner | Path-level provenance manifest listing every exact file, originating gate, accepted/rejected/deferred status, whether tracked promotion is requested, and direct evidence for the mapping; MiMo/DS reviews; controller judgment | No for non-destructive provenance planning/review. Yes before deleting/moving/archiving. External PR/release actions require separate authorization | Do not bulk promote `docs/reviews`; do not infer provenance from filename alone; do not use untracked review residue as truth or readiness evidence; do not rewrite historical artifacts |
| `docs/audit/` | A6 blocker; metadata-only inventory shows `docs/audit/fund-agent-repo-deepreview-20260610.md` | `PROMOTE_WITH_PROVENANCE` if controller accepts it as review input/evidence-chain artifact; otherwise `ACCEPT_AS_RELEASE_RESIDUAL` or `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` | Controller + reviewer owner | Review-artifact provenance note naming origin, role, whether it informed accepted gates, and whether it belongs in canonical `docs/reviews/` or remains local evidence-chain residue; MiMo/DS reviews; controller judgment | No for provenance classification. Yes for archive/delete/move | Do not treat audit content as design/control truth; do not import findings into current gate without separate adjudication; do not read or re-review beyond path-level provenance unless a future review gate authorizes it |
| `reports/manual-llm-smoke/` | A6 blocker; metadata-only inventory shows manual provider/runtime outputs | `REJECT_AS_RELEASE_EVIDENCE` for current release readiness; then either `ACCEPT_AS_RELEASE_RESIDUAL` with owner or `DEFER_TO_IGNORE_RULE_GATE` / `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` in a future runtime-artifact gate | Runtime evidence owner + controller | Runtime artifact disposition note listing exact run directories, whether any accepted controller judgment already references them, safe redaction status, and whether repeatable paths should be ignored; MiMo/DS reviews; controller judgment | Yes before archive/delete/move. No for rejecting as current release evidence | Do not read report contents in this gate; do not run provider/LLM/live/analyze/checklist commands; do not convert manual smoke residue into accepted provider evidence; do not alter runtime budgets or provider defaults |
| `reviews/` | A6 blocker; obsolete duplicate or external review residue outside canonical `docs/reviews/` | `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` for exact duplicate handling, or `REJECT_AS_RELEASE_EVIDENCE` if left untouched | Controller + user/reviewer owner | Duplicate-review disposition manifest comparing only metadata/path/provenance, not content unless separately authorized; exact archive/delete/move path list; MiMo/DS reviews; controller judgment | Yes for archive/delete/move; yes if ownership is ambiguous | Do not treat non-canonical `reviews/` as release evidence; do not bulk delete; do not silently merge into `docs/reviews/` |
| `基金年报/` | A8 passes only because metadata was inspected and contents were not read; A6 remains blocking question. Production annual-report access must go through `FundDocumentRepository` | `USER_DECISION_REQUIRED`; until user decides, `REJECT_AS_RELEASE_EVIDENCE` for release readiness | User + controller | User decision record naming whether the local PDF corpus should remain untracked local data, be moved outside repo, archived, deleted, or handled by a future data-artifact gate; if kept, a controller residual judgment that it is user-owned local data and not release evidence | Yes. This is user-owned/local data and any delete/move/archive/import requires explicit user authorization | Do not read PDF contents; do not use filesystem PDFs for production proof; do not call FDR/helper/fallback/EID/network/PDF commands; do not import as fixtures; do not infer readiness from presence or absence of these files |
| `docs/learning-roadmap.md` | Material residual; research input visible in status | `ACCEPT_AS_RELEASE_RESIDUAL` if controller confirms it is non-product research; otherwise `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` | User/controller | Research-doc residual judgment naming owner, non-truth status and whether it may remain untracked during release readiness | Yes for archive/delete/move | Do not treat as design/control truth; do not fold into release scope |
| `docs/next-development-phaseflow.md` | Material residual; planning/research input visible in status | `ACCEPT_AS_RELEASE_RESIDUAL` if controller confirms it is not current control truth; otherwise `PROMOTE_WITH_PROVENANCE` only if exact gate provenance exists | Controller | Planning-doc residual judgment or provenance mapping to accepted gate; controller judgment | Yes for archive/delete/move | Do not let it override `docs/implementation-control.md` or `docs/current-startup-packet.md`; do not use as current gate fact |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | Material residual; blocking question only if cited as current design | `REJECT_AS_RELEASE_EVIDENCE` for current release readiness; `ACCEPT_AS_RELEASE_RESIDUAL` as candidate/research input only if clearly labeled non-truth | Design owner + controller | Design-research residual note confirming it is not `docs/design.md` truth and not current implementation scope; controller judgment | Yes for archive/delete/move | Do not update `docs/design.md`; do not reopen template/facet design; do not treat candidate design as implemented |
| `docs/tmux-agent-memory-store.md` | Material residual; ops/scratch note visible in status | `ACCEPT_AS_RELEASE_RESIDUAL` if controller accepts as local ops note; otherwise `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` | Controller / agent setup owner | Ops-artifact residual note naming retention reason and handoff reliability impact; controller judgment | Yes for archive/delete/move | Do not treat as agent availability evidence; do not use as proof of current review completion |
| `scripts/claude_mimo_simple.py` | Material tooling residue; blocker if imported, promoted or used as proof | `REJECT_AS_RELEASE_EVIDENCE`; future `DEFER_TO_ARCHIVE_DELETE_MOVE_GATE` or dedicated tooling-support gate if owner wants to keep it | User/controller + tooling owner | Tooling residue disposition note confirming no production import, no release evidence use, and exact owner; optional future reviewed tool-support plan | Yes for delete/move/archive; no for rejecting as release evidence | Do not import into source; do not treat as sanctioned reviewer infrastructure; do not modify scripts in this gate |
| `定性分析模板.md` | Material user-owned/research/template input; blocker if cited as canonical template truth | `USER_DECISION_REQUIRED` if user-owned; otherwise `REJECT_AS_RELEASE_EVIDENCE` and `ACCEPT_AS_RELEASE_RESIDUAL` as non-canonical research only | User + controller/template owner | User or controller decision record confirming canonical template remains `docs/fund-analysis-template-draft.md` and this file is not template truth | Yes for archive/delete/move/import | Do not alter canonical template; do not cite this file as CHAPTER_CONTRACT truth; do not promote without a template design gate |
| `.gitignore` candidate patterns for repeatable generated output | A7 says `.gitignore` unchanged; deferred ignore-rule remains material residual | `DEFER_TO_IGNORE_RULE_GATE` only for repeatable generated outputs after exact pattern review | Controller + artifact owner | Ignore-rule planning artifact naming exact patterns, matched paths, false-positive risk, and future validation matrix; MiMo/DS reviews; controller judgment | No for plan/review. Yes if ignore change would hide user-owned data or broad paths | Do not edit `.gitignore` here; do not use ignore rules to hide unresolved source-like or user-owned residue |
| `fund_agent/tools` exact source-like residue | Closed for exact prior case; absent from current status | `ACCEPT_AS_RELEASE_RESIDUAL` as closed historical residual only; no action unless it reappears | Controller + implementation owner | None for current gate. If it reappears, reopen source-like residue ownership gate with exact paths | Not currently | Do not reopen closed residue without new visibility; do not infer broader tooling cleanliness from this exact closure |
| PR 22 pane/footer/context text | Accepted as non-evidence residue | `REJECT_AS_RELEASE_EVIDENCE` | Controller | No new artifact required beyond plan reviews/controller judgment acknowledging it is non-evidence | No | Do not cite as reviewer unavailability, PR state, release state, readiness evidence or proof |

## 4. Future Gate Sequence

Recommended sequence after this plan is reviewed and accepted:

1. Independent plan review by AgentMiMo.
2. Independent plan review by AgentDS.
3. Controller judgment for this plan. The controller must explicitly decide whether the plan is accepted, accepted with amendments, rejected or needs rework.
4. If accepted, open the first non-destructive provenance/disposition evidence gate. Suggested first write set is the review-artifact provenance group because untracked `docs/reviews` is the largest blocker and has the highest chance of exact accepted-gate mapping.
5. Open separate gates for runtime artifacts, user/local data, archive/delete/move, and ignore-rule changes. Do not combine destructive actions with provenance-only evidence.

MiMo and DS are usable reviewers for this gate. PR 22 residue must not be cited as unavailability evidence.

## 5. Future Write Sets

This plan authorizes no writes beyond this artifact.

Permitted future write sets only after plan review and controller judgment:

- Plan review artifacts:
  - `docs/reviews/mvp-release-readiness-blocker-disposition-plan-review-mimo-20260611.md`
  - `docs/reviews/mvp-release-readiness-blocker-disposition-plan-review-ds-20260611.md`
- Controller judgment artifact:
  - `docs/reviews/mvp-release-readiness-blocker-disposition-plan-controller-judgment-20260611-*.md`
- Future provenance/disposition evidence artifacts under `docs/reviews/` with exact names chosen by controller for each separate gate.
- `docs/current-startup-packet.md` and `docs/implementation-control.md` only for controller status sync after accepted judgment.

Explicitly excluded from this plan and all immediate review actions:

- source, tests, runtime behavior, README, `docs/design.md`, `.gitignore`, reports, PDF corpus, residue files and external PR/release state;
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR, mark-ready or merge actions.

## 6. Evidence Requirements

Every future disposition gate must provide direct evidence for each exact path or path group it touches:

- current visibility and tracked/untracked status;
- owner;
- current category;
- selected disposition enum;
- whether it blocks release readiness before and after the controller judgment;
- required authorization status;
- proof that no untracked residue was used as source truth, fixture, product scope, proof, release evidence or readiness evidence;
- negative evidence that no live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release command was run unless a later gate explicitly authorizes it.

For user-owned/local data paths, especially `基金年报/`, the default is `USER_DECISION_REQUIRED`. A safer non-destructive residual treatment is acceptable only if the controller can record that the path remains local/user-owned, is not release evidence, is not production input, is not read through the filesystem for proof, and remains outside staging/promotion.

## 7. Stop Conditions

Stop and return to controller judgment if any of the following occurs:

- a future worker needs to read PDF/report contents rather than metadata/provenance;
- a future worker needs live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands;
- a path requires delete, move, archive, cleanup, import, staging, promotion or `.gitignore` edits without exact prior authorization;
- ownership is ambiguous, especially for `基金年报/`, `定性分析模板.md`, `reviews/` or any user-owned local data;
- a reviewer is unavailable after clean handoff verification and no approved alternate reviewer path exists;
- PR 22 footer/context residue is being used as reviewer availability, PR state, release state or readiness evidence;
- any plan/review attempts to claim release readiness before A6 has accepted disposition evidence and controller judgment.

## 8. Non-goals

This plan keeps the following out of scope:

- EID source expansion, fallback design, helper behavior, live source validation or PDF parsing;
- provider, LLM, runtime budget, retry, timeout, env/config or default behavior changes;
- extractor correctness, golden promotion, readiness scoring, score-loop or quality gate semantics;
- Host durable session/resume/memory/outbox and full Agent tool-loop/runtime expansion;
- source/test/runtime/README/design/control edits by the planning worker;
- external PR state, release state, mark-ready, merge or reviewer request actions.

## 9. Acceptance Criteria For This Plan

This plan is acceptable only if MiMo review, DS review and controller judgment confirm:

- the plan starts from accepted `NOT_READY` evidence and the A6 failure;
- every blocker/material residual group in the accepted evidence judgment has a disposition path, owner, required future evidence, authorization status and non-goals;
- user-owned/local data paths are not touched and remain `USER_DECISION_REQUIRED` unless a controller-accepted non-destructive residual treatment is recorded;
- untracked residue remains rejected as release evidence until exact provenance or residual acceptance exists;
- EID/provider/PDF/live/fallback/source expansion remains out of scope;
- the plan does not itself accept readiness or implement disposition.
