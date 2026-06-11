# MVP Release-readiness Residual Rollup Plan - 2026-06-12

## Role And Scope

Role: AgentCodex planning worker only, not controller.

Gate: `Release-readiness residual rollup planning gate`.

Target: produce one non-live blocker map that rolls accepted non-proof residue classifications into release-readiness residual ownership before any cleanup, live, PR or release action.

This plan does not modify source, tests, runtime behavior, README, `docs/design.md`, `docs/current-startup-packet.md` or `docs/implementation-control.md`. It does not read candidate residue bodies. It does not run live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release commands. It does not authorize cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge/mark-ready/release.

Release/readiness is explicitly preserved as `NOT_READY`.

## Truth Inputs

Read inputs:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-controller-judgment-20260612-061558.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-controller-judgment-20260612-063706.md`
- `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-controller-judgment-20260612-065002.md`
- `docs/reviews/mvp-top-level-review-audit-residue-metadata-evidence-controller-judgment-20260612-070606.md`

Count reconciliation inputs only:

- `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-20260612.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-20260612.md`
- `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-20260612.md`
- `docs/reviews/mvp-top-level-review-audit-residue-metadata-evidence-20260612.md`

No candidate residue bodies under `reviews/`, old `docs/reviews/` paths, `docs/audit/`, `reports/`, PDFs, scripts or user-owned docs are truth inputs for this plan.

## Accepted Residual Families And Checkpoints

| Family | Accepted checkpoint | Accepted classification fact | Readiness effect |
|---|---|---|---|
| Review/audit residual acceptance evidence | `387d16a`; controller judgment `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-controller-judgment-20260612-061558.md` | 36 review/audit paths classified as non-proof residue: 19 `DEFER_PROVENANCE_REQUIRED`, 9 `KEEP_REJECTED_AS_RELEASE_EVIDENCE`, 7 `USER_OR_CONTROLLER_DECISION_REQUIRED`, 1 `NEW_UNINDEXED_REVIEW_RESIDUE`; 0 accepted as non-release residual | Blocks readiness claim; no source truth, release evidence or readiness proof accepted |
| Runtime/live report residue metadata evidence | `e48b642`; controller judgment `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-controller-judgment-20260612-063706.md` | `reports/live-evidence/` and `reports/manual-llm-smoke/` classified metadata-only; 13 rows total: 2 root rows and 11 path rows; 3 live-evidence files, 8 manual-smoke files; `unknown_report_residue=0` for the authorized two-root pass | Blocks readiness claim until accepted disposition or separate explicit cleanup/live gate |
| Research/user-owned/tooling residue metadata evidence | `98f3bd2`; controller judgment `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-evidence-controller-judgment-20260612-065002.md` | 15 metadata rows for 8 accepted-plan candidate paths/roots; includes 6 direct untracked files, 2 untracked roots, 2 files under `reviews/`, 5 PDFs under `基金年报/`; all rows non-proof | Blocks readiness claim; user/controller/tooling/truth-source ownership unresolved |
| Top-level review/audit residue metadata evidence | `4a1d711`; controller judgment `docs/reviews/mvp-top-level-review-audit-residue-metadata-evidence-controller-judgment-20260612-070606.md` | 39 metadata rows accepted: 3 top-level `reviews/` rows, 35 visible pre-write `docs/reviews/` rows, 1 generated evidence self-row; `docs/audit/` visible only as exclusion context | Current accepted checkpoint; blocks readiness claim; no body reads or proof promotion |

All accepted families share the same boundary: metadata classification is accepted; release-readiness proof is not accepted.

## Release-readiness Blocker Map

| Blocker family | Owner | Blocker status | Accepted facts | Missing evidence before readiness | Next gate | Cleanup/live/PR authorization required? |
|---|---|---|---|---|---|---|
| `docs/reviews/` historical review/audit residue | Controller / review-artifact owner / historical artifact owners | Blocks readiness claim | 36-path residual acceptance evidence accepted at `387d16a`; top-level follow-up accepted 35 visible pre-write `docs/reviews/` rows plus generated self-row at `4a1d711`; all rows non-proof | Exact owner disposition for unresolved `DEFER_PROVENANCE_REQUIRED`, `USER_OR_CONTROLLER_DECISION_REQUIRED` and `NEW_UNINDEXED_REVIEW_RESIDUE`; proof that no path is being used as source/control/release/readiness truth | Non-live review/audit residual ownership evidence gate | Cleanup requires separate exact-path authorization; live not required for metadata ownership; PR/release authorization not allowed |
| Historical review artifacts rejected as release evidence | Release owner / controller | Blocks readiness claim if used as evidence; may remain as non-proof residue | 9 paths accepted as `KEEP_REJECTED_AS_RELEASE_EVIDENCE`; generic historical audit/repo-review artifacts are not current readiness proof | Explicit decision whether to leave as non-proof residue, archive later, or map to historical chain; no readiness claim may cite them | Non-live residual ownership evidence gate, then optional cleanup/archive policy gate | Cleanup/archive requires separate authorization; live/PR/release not authorized |
| Runtime/live report residue under `reports/live-evidence/` | Runtime evidence owner / controller | Blocks readiness claim | Root visible as untracked metadata; 3 listed files; one path-row marked `candidate_live_run_artifact`, but marker is not accepted live evidence | Exact report-body provenance or explicit non-proof disposition; controlled live acceptance for exact paths only if separately authorized | Runtime report-body provenance gate or exact-artifact disposition gate, deferred until after rollup | Live requires separate explicit live authorization; cleanup requires exact-path authorization; PR/release not authorized |
| Manual LLM smoke residue under `reports/manual-llm-smoke/` | Runtime evidence owner / controller | Blocks readiness claim | Root visible as untracked metadata; 8 listed files; rows classified as manual smoke output or runtime diagnostics; all non-proof | Exact manual-smoke provenance or explicit non-proof disposition; no file body has been accepted | Manual-smoke provenance or exact-artifact disposition gate, deferred | Cleanup requires exact-path authorization; live only if a future gate asks for it; PR/release not authorized |
| Top-level `reviews/` residue | Controller / review-artifact owner | Blocks readiness claim | 1 root and 2 files accepted as metadata-only in research/tooling gate and top-level review/audit evidence; no body reads | Owner disposition that states whether these remain non-proof residue, need archive, or need historical provenance mapping | Top-level review/audit residual ownership evidence gate | Cleanup/archive requires separate exact-path authorization; live/PR/release not authorized |
| `docs/audit/` visible audit root / audit input | Controller / audit owner | Blocks readiness claim if treated as proof; currently exclusion context | One `docs/audit/*` path classified in review/audit residual acceptance evidence; top-level gate records `docs/audit/` visibility only as exclusion context | Explicit audit input disposition; no body-read proof is accepted by current chain | Audit residue disposition or provenance mapping gate, deferred | Cleanup/body reads require separate authorization; live/PR/release not authorized |
| Research and planning docs | Controller / artifact owner / design-spec owner | Blocks readiness claim until dispositioned | Metadata-only rows accepted for `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md`, `docs/tmux-agent-memory-store.md`; not design/template/source truth | User/controller disposition or truth-source decision for spec/template-like docs; proof that none are current truth inputs | Research/spec/tooling ownership gate, deferred | Cleanup/import/promote requires separate authorization; live/PR/release not authorized |
| `scripts/claude_mimo_simple.py` source-like tooling residue | Controller / tooling owner | Blocks readiness claim until ownership is explicit | Metadata-only source-like tooling classification accepted; not runtime source and not proof | Decision whether to keep as user-owned tooling, migrate through a source-like tooling ownership gate, ignore/archive/delete later, or remove from release surface | Source-like tooling ownership gate, deferred | Any source move/import/delete requires separate authorization; live/PR/release not authorized |
| `基金年报/` PDF corpus | User / document owner | Blocks readiness claim until excluded or dispositioned | Root and 5 PDFs accepted metadata-only; explicitly not production source path | User-owned corpus disposition or ingestion decision; no PDF body, checksum or production FDR proof accepted | PDF corpus ingestion/disposition gate, deferred | PDF reads/import/delete require separate authorization; live/PR/release not authorized |
| `定性分析模板.md` and template/spec-like residue | User / template owner / design-template owner | Blocks readiness claim if treated as template truth | Metadata-only classification accepted; not design truth or template truth | Explicit truth-source decision or user-owned-doc disposition | Template/spec truth-source decision gate, deferred | Import/promote/delete requires separate authorization; live/PR/release not authorized |
| Release/readiness claim itself | Release owner / controller | `NOT_READY` | All four accepted residue families preserve `NOT_READY` and non-proof flags | A later release-readiness evidence gate must prove accepted ownership/disposition, current workspace cleanliness or accepted exceptions, and must not rely on unaccepted residue bodies | Mainline non-live release-readiness residual ownership evidence gate | PR/release/mark-ready requires separate external-state authorization after evidence acceptance |

## Planning Steps For The Next Mainline Gate

Recommended next mainline gate: `Release-readiness residual ownership evidence gate`.

Gate classification: `standard`, non-live, metadata/control evidence only.

Purpose: turn this blocker map into a reviewed evidence artifact that assigns every accepted residual family to a release-readiness owner and next gate, without cleaning, reading bodies, running live commands or claiming readiness.

Proposed worker tasks:

1. Re-read only the current startup packet, implementation control doc, this plan, and the four accepted controller judgments.
2. Re-run only allowed status/format validation commands authorized for that evidence gate.
3. Produce one evidence artifact that maps each accepted blocker family to owner, blocking status, accepted fact, missing evidence and next gate.
4. Assert that every row remains `not_source_truth=true`, `not_release_evidence=true`, `not_readiness_proof=true` unless a later controller explicitly opens a different gate.
5. Stop at evidence review handoff. Do not update control docs, cleanup files, open PR, run readiness, or change external state.

Controller judgment after that evidence gate should decide whether the blocker map is accepted as release-readiness residual ownership truth. It must still preserve `NOT_READY` unless a separate release-readiness evidence gate later proves readiness.

## Deferred Entries

- Review/audit provenance mapping gate for exact historical paths.
- Controller/user disposition gate for unresolved review/audit and audit paths.
- Runtime report-body provenance gate for exact `reports/live-evidence/` and `reports/manual-llm-smoke/` artifacts.
- Controlled live annual-period narrative evidence gate, only with explicit live authorization.
- Source-like tooling ownership gate for `scripts/claude_mimo_simple.py`.
- User-owned PDF corpus ingestion/disposition gate for `基金年报/`.
- User-owned template/spec truth-source decision gate for `定性分析模板.md` and spec-like docs.
- Cleanup/archive/delete/ignore/import/promote policy gate, only with exact-path authorization.
- Release-readiness cleanliness re-evidence gate after accepted ownership/disposition.
- PR/push/merge/mark-ready/release gate, only with separate external-state authorization after readiness evidence is accepted.

## Validation Commands

Allowed validation for this planning gate:

```text
git status --short
git status --branch --short
git diff --check
```

Observed pre-write validation:

- `git status --short`: dirty/untracked residue remains visible, including review/audit, reports, research/user-owned/tooling and PDF corpus residue.
- `git status --branch --short`: branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts` is ahead of remote; dirty/untracked workspace remains.
- `git diff --check`: pass.

Required post-write validation:

- Run the same three allowed commands.
- Confirm this target artifact appears as untracked or changed metadata only.
- Confirm `git diff --check` remains clean.

## Stop Conditions

Stop immediately and return to controller if any of the following occurs:

- A requested action would read candidate residue bodies under `reviews/`, old `docs/reviews/` paths, `docs/audit/`, `reports/`, PDFs, scripts or user-owned docs.
- A requested command is outside `git status --short`, `git status --branch --short`, or `git diff --check`.
- Any step would run live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release commands.
- Any step would cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge/mark-ready/release.
- Any row attempts to convert accepted metadata classification into source truth, design truth, control truth, release evidence or readiness proof.
- The current gate, current accepted checkpoint, or `NOT_READY` state cannot be reconciled from the allowed truth inputs.
- Count reconciliation conflicts with accepted controller judgments and cannot be resolved without reading unauthorized candidate bodies.

## Non-proof Assertion

This plan accepts no path as source truth, design truth, control truth, template truth, release evidence or readiness proof. It only plans ownership and next-gate routing for already accepted metadata classifications. The release-readiness state remains `NOT_READY`.
