# MVP Release-readiness Residual / Artifact Disposition Plan - 2026-06-12

## 0. Worker Self-check

- Current gate / role: `release-readiness residual/artifact disposition planning gate`; planning worker only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, required controller judgments, current `git status`.
- Scope boundary: write this planning artifact only. Do not modify source/tests/runtime behavior, truth docs, `.gitignore`, reports, residue, PR/release state or external state.
- Evidence rule: current untracked files are inventory/residue only. Do not use arbitrary untracked residue content as proof.
- Stop condition: artifact written, then run `git status --short`, `git status --branch --short`, `git diff --check`; do not commit.

## 1. Goal

Plan the next non-live, non-destructive release-readiness residual/artifact disposition path after:

- accepted annual-period narrative/reporting implementation checkpoint `b3254b3`;
- accepted truth sync checkpoint `08f836f`;
- current control truth showing release/readiness remains `NOT_READY`.

The plan must enable future evidence workers to classify visible residue families, decide which can be accepted as non-release residuals with owners/next gates, and identify which require separate authorization before cleanup, ignore, live evidence, PR/release or readiness claims.

## 2. Non-goals

This plan does not authorize:

- source/test/runtime behavior changes;
- `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` edits;
- deletion, move, archive, cleanup, import, promotion, ignore-rule edits, staging, commit, push, PR, merge, mark-ready or release-state changes;
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands;
- reading PDF/report/runtime artifact contents as proof;
- accepting release readiness, PR readiness, golden promotion, additional live samples or all-market acceptance.

## 3. Fact Separation

### 3.1 Repo Facts

Observed from current local status:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Branch status: ahead of `origin/feat/mvp-llm-incomplete-run-artifacts` by 128 commits.
- `git status --short` shows no tracked modified/staged files before this plan artifact, only untracked residue groups.
- Current visible untracked top-level families:
  - `docs/audit/`
  - 35 exact `docs/reviews/*` paths
  - `docs/learning-roadmap.md`
  - `docs/next-development-phaseflow.md`
  - `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md`
  - `docs/tmux-agent-memory-store.md`
  - `reports/live-evidence/`
  - `reports/manual-llm-smoke/`
  - `reviews/`
  - `scripts/claude_mimo_simple.py`
  - `基金年报/`
  - `定性分析模板.md`
- Current status does not show `fund_agent/tools/`; prior control truth says exact source-like residue was closed.

These are inventory facts only. They do not prove source truth, release evidence, readiness proof, reviewer availability, live acceptance or artifact validity.

### 3.2 Truth-doc Facts

From `docs/current-startup-packet.md` and `docs/implementation-control.md`:

- Current phase is `MVP typed-template-to-agent report generation stabilization phase`.
- Current active gate is `release-readiness residual/artifact disposition planning gate`.
- Gate classification is `standard`; planning only, non-live, non-destructive, no PR/release external state.
- `b3254b3` accepted deterministic annual-period narrative/reporting implementation.
- Current deterministic `analyze-annual-period` product path is accepted as code fact, including explicit `annual_period_report`.
- Controlled live evidence is accepted only for single sample `004393 / 2021-2025`; additional live samples/readiness remain deferred.
- Release/readiness remains unclaimed and blocked by unresolved residue disposition.
- `docs/reviews/` and `docs/archive/` are evidence-chain only and do not override `AGENTS.md`, `docs/design.md`, startup packet or control doc.

From `docs/design.md`:

- Current architecture remains `UI -> Service -> Host -> Agent`.
- EID single-source annual-report access is current source policy; fallback/source expansion and broader live acceptance are future scope.
- Current product/reporting implementation does not prove release/readiness, golden promotion, additional live sample acceptance or provider/LLM behavior.
- Production annual-report access must remain through `FundDocumentRepository`; this planning gate does not touch production document access.

### 3.3 Prior Reviewer / Controller Judgments

- `mvp-multi-year-annual-narrative-writer-reporting-implementation-controller-judgment-20260612-002524.md`: verdict `ACCEPT`; no source-policy/fallback/provider/LLM/live/release drift; accepted residuals include additional controlled live samples, release/readiness claim, coverage measurement, source identity extension and runtime/live evidence artifacts.
- `mvp-control-doc-compression-untracked-residue-disposition-20260611.md`: accepted residue index only; no residue was deleted, moved, archived, cleaned, ignored, staged, imported, promoted, committed, pushed or used as proof.
- `mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-153309.md`: verdict `ACCEPT_WITH_RESIDUALS_NOT_READY`; release-readiness cleanliness remains `NOT_READY` because visible blocker groups remain unresolved.
- `mvp-review-artifact-provenance-disposition-evidence-controller-judgment-20260611-160126.md`: verdict `ACCEPT_WITH_RESIDUALS_NOT_READY`; review/audit paths were narrowed to exact path-level disposition, but no exact path was accepted as current or historical chain.
- `mvp-review-artifact-residual-acceptance-plan-controller-judgment-20260611-162326.md`: verdict `ACCEPT_WITH_NONBLOCKING_RESIDUALS`; future evidence must record exact `path`, `owner`, `reason`, `next_gate`, `classification`, and explicit `not_source_truth`, `not_release_evidence`, `not_readiness_proof`.

## 4. Residual Inventory Families

Use current `git status` plus the accepted residue index. Do not delete or read contents.

| Family | Current status evidence | Prior index / judgment link | Planning disposition |
|---|---|---|---|
| Review/audit residue | `docs/audit/`; 35 `docs/reviews/*` untracked paths | Prior provenance gate covered earlier review/audit exact paths and kept `NOT_READY` | Mainline path: refresh exact path manifest and run residual acceptance evidence for review/audit residue |
| Runtime/live evidence reports | `reports/live-evidence/`; `reports/manual-llm-smoke/` | Prior index listed manual LLM smoke; current status adds live-evidence family | Separate runtime/live artifact disposition planning/evidence gate; no content read; no live acceptance |
| Duplicate/external review root | `reviews/` | Prior index classified as obsolete duplicate or external review residue | Separate artifact disposition gate; archive/delete requires explicit authorization |
| User-owned PDF corpus | `基金年报/` | Prior index classified as user-owned unknown/local PDF corpus | Separate user/controller decision gate; never use filesystem PDFs as production proof |
| Research/planning docs | `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/...`, `docs/tmux-agent-memory-store.md`, `定性分析模板.md` | Prior index classified as research/planning/user-owned/candidate design | Separate research-doc disposition gate; cannot override truth docs |
| Scratch tooling | `scripts/claude_mimo_simple.py` | Prior index classified as scratch helper | Separate tooling disposition gate; do not import/promote without reviewed tool-support gate |
| Source-like residue | current status does not list `fund_agent/tools/` | Control truth says exact residue closed | No current action unless reappears; future status must verify absence |

## 5. Proposed Staged Evidence Gates

### Stage A - Review/audit residual acceptance evidence

Objective: decide whether current untracked review/audit paths can be accepted as non-release residuals with owners and next gates, or remain unresolved.

Allowed read set:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-review-artifact-provenance-disposition-evidence-20260611.md`
- `docs/reviews/mvp-review-artifact-provenance-disposition-evidence-controller-judgment-20260611-160126.md`
- `docs/reviews/mvp-review-artifact-residual-acceptance-plan-20260611.md`
- `docs/reviews/mvp-review-artifact-residual-acceptance-plan-controller-judgment-20260611-162326.md`

Allowed metadata commands:

- `git status --short`
- `git status --branch --short`
- `git diff --check`

Allowed write set:

- `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-20260612.md`
- DS/MiMo review artifacts for that evidence gate
- controller judgment artifact for that evidence gate

Forbidden actions:

- reading untracked review/audit file contents as truth;
- accepting any rejected/deferred/user-decision path as release evidence;
- cleanup, archive, delete, move, ignore, promote, stage, commit, PR or release action.

Required output fields per exact path:

- `path`
- `status_seen`
- `prior_classification` if any
- `classification`: one of `ACCEPT_AS_NON_RELEASE_RESIDUAL`, `KEEP_REJECTED_AS_RELEASE_EVIDENCE`, `DEFER_PROVENANCE_REQUIRED`, `USER_OR_CONTROLLER_DECISION_REQUIRED`, `NEW_UNINDEXED_REVIEW_RESIDUE`
- `owner`
- `reason`
- `next_gate`
- `not_source_truth=true`
- `not_release_evidence=true`
- `not_readiness_proof=true`

Acceptance criteria:

- every currently visible `docs/reviews/*` and `docs/audit/*` residue path has exactly one classification;
- newly visible paths not present in the prior manifest are called out as new residue, not silently accepted;
- no target path is promoted to source truth, release evidence or readiness proof;
- release/readiness remains `NOT_READY`;
- validation commands pass or failures are recorded as blockers.

Validation matrix:

| Check | Expected assertion | Failure handling |
|---|---|---|
| `git status --short` | evidence artifact is the only new intended write besides pre-existing residue | stop for controller if unexpected tracked/source/test/runtime diff appears |
| `git status --branch --short` | branch remains work branch, no external state action claimed | stop if branch/context changes make ownership unclear |
| `git diff --check` | no whitespace errors in written artifacts | fix only artifact whitespace if within allowed write set; otherwise stop |

### Stage B - Runtime/live report residue inventory planning

Objective: plan non-live disposition for `reports/live-evidence/` and `reports/manual-llm-smoke/` without reading report contents and without claiming live acceptance.

Allowed read set:

- control truth docs and Stage A accepted judgment;
- prior residue index;
- path metadata only for `reports/live-evidence/` and `reports/manual-llm-smoke/`.

Allowed metadata commands:

- `git status --short reports/live-evidence reports/manual-llm-smoke`
- path listing/counting commands that do not read file contents, if controller authorizes them in the handoff.

Allowed write set:

- one planning artifact under `docs/reviews/`
- plan reviews and controller judgment under `docs/reviews/`

Forbidden actions:

- live/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness commands;
- reading report bodies as truth;
- deleting, archiving, ignoring or promoting report files.

Acceptance criteria:

- both report roots have owner and next gate;
- plan distinguishes local diagnostic residue, possible live evidence candidate, and non-evidence scratch output;
- plan states that accepting an artifact as live evidence requires separate live evidence gate and direct evidence standards;
- release/readiness remains `NOT_READY`.

### Stage C - Research/user-owned/tooling residue disposition planning

Objective: classify research docs, user-owned PDFs, duplicate review root and scratch tooling into future decision gates.

Allowed read set:

- control truth docs, prior residue index and accepted Stage A/B artifacts;
- `git status` metadata only unless the future handoff explicitly authorizes content review for a named file.

Allowed write set:

- one planning artifact under `docs/reviews/`
- plan reviews and controller judgment under `docs/reviews/`

Forbidden actions:

- filesystem PDF content reads;
- treating research docs as truth docs;
- import/use of scratch helper;
- archive/delete/ignore without separate authorization.

Acceptance criteria:

- each residue family has owner, next gate and explicit non-proof status;
- user-owned or ambiguous artifacts remain `USER_OR_CONTROLLER_DECISION_REQUIRED`;
- candidate design/research docs are not allowed to override `docs/design.md`.

### Stage D - Release-readiness cleanliness re-evidence

Prerequisite: Stages A-C accepted by controller, with no unresolved family that blocks cleanliness except explicitly accepted non-release residuals.

Objective: rerun non-live cleanliness evidence under accepted disposition matrix.

Allowed write set:

- cleanliness evidence artifact under `docs/reviews/`
- DS/MiMo reviews
- controller judgment

Forbidden actions:

- release/readiness claim unless evidence directly satisfies accepted criteria and controller explicitly judges it;
- PR/push/merge/mark-ready;
- cleanup or ignore-rule edits.

Acceptance criteria:

- all visible residue is either accepted non-release residual with owner/next gate, closed by separately authorized cleanup, or explicitly unresolved;
- if unresolved blocker remains, result must stay `NOT_READY`;
- if no blockers remain, controller may decide whether a separate readiness gate is required before any readiness claim.

## 6. Separate Authorization Required

The following cannot be performed or implied by this plan:

- live evidence: any EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release execution;
- PR/push/merge/mark-ready/request-reviewer/external comment/issue actions;
- deletion, archive, move, cleanup, import, promotion or staging of residue;
- `.gitignore` edits, especially if they affect repository policy or hide release-relevant residue;
- reading user-owned PDFs or runtime reports as proof;
- changing `docs/design.md`, startup packet, implementation-control or source/tests/runtime behavior.

## 7. Mainline Entry and Deferred Entries

Mainline entry: `Review-artifact residual acceptance evidence gate`.

Rationale: prior controller judgment already accepted a plan for this exact unresolved review/audit blocker family, and current status still shows review/audit residue. This is the narrowest next non-live path before broader report/data/research residue disposition.

Deferred entries:

- `Runtime/live report residue disposition planning gate` for `reports/live-evidence/` and `reports/manual-llm-smoke/`.
- `Research/user-owned/tooling residue disposition planning gate`.
- `Ignore-rule policy gate`, only if repeated generated outputs need scoped ignore handling.
- `Archive/delete/cleanup gate`, only with exact path authorization.
- `Controlled live annual-period narrative evidence gate`, only with explicit live authorization.
- `Release-readiness cleanliness re-evidence gate`, only after prerequisite disposition gates are accepted.
- PR/push/merge/mark-ready/release gate, only after separate explicit user authorization.

## 8. DS / MiMo Plan Review Checklist

Reviewers should verify:

- plan keeps planning-only scope and does not enter implementation, cleanup, ignore, live, PR or release actions;
- fact separation is explicit: repo facts, truth-doc facts, and prior reviewer/controller judgments are not conflated;
- current `git status` inventory is reflected, including `reports/live-evidence/` and the current review/audit residue count;
- untracked residue is never used as proof, only as inventory;
- Stage A is sufficiently exact for an evidence worker to classify every path without redesigning classification fields;
- allowed read/write sets are narrow and do not include source/tests/runtime behavior or truth-doc sync;
- acceptance criteria preserve `NOT_READY` unless later direct evidence and controller judgment prove otherwise;
- separate authorization requirements are complete for live evidence, external state, cleanup/archive/delete and ignore policy;
- mainline entry is one route only and deferred entries are not accidentally promoted.

## 9. Completion Report Format For Future Workers

Future evidence/planning workers should report:

```text
Self-check: pass | blocked - <reason>
Artifact: <path>
Gate: <gate name>
Scope: <allowed files/actions actually used>
Inventory: <families/path counts, metadata only>
Classification summary: <counts by classification>
Validation:
- git status --short: <result>
- git status --branch --short: <result>
- git diff --check: <result>
Residuals:
- <owner / next gate / blocker status>
Forbidden actions confirmed not performed:
- <list>
```
