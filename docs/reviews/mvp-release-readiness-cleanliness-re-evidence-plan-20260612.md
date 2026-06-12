# MVP Release-readiness Cleanliness Re-evidence Plan - 2026-06-12

## 0. Scope

Role: AgentCodex planning worker only, not controller.

Gate: `Release-readiness cleanliness re-evidence planning gate`.

Target future gate: non-live `Release-readiness cleanliness re-evidence gate` after accepted residual ownership evidence.

Accepted input checkpoint: `4d0e65b`, accepted by controller judgment `docs/reviews/mvp-release-readiness-residual-ownership-evidence-controller-judgment-20260612-102336.md`.

Current control-truth reconciliation:

- `docs/current-startup-packet.md` and `docs/implementation-control.md` both state the current active gate is `Release-readiness cleanliness re-evidence planning gate`.
- Both control-truth files identify the accepted residual ownership evidence checkpoint as `4d0e65b`.
- The accepted residual ownership evidence is ownership-routing evidence only. It is not source truth, design truth, control truth, release evidence or readiness proof.
- Release/readiness remains `NOT_READY`.

This plan is code-generation-ready for a future evidence worker, but it authorizes no implementation, cleanup, body reads, live execution, release action or readiness claim.

## 1. Read Boundary for Future Evidence Worker

Required reads:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-release-readiness-residual-ownership-evidence-20260612.md`
- `docs/reviews/mvp-release-readiness-residual-ownership-evidence-review-ds-20260612.md`
- `docs/reviews/mvp-release-readiness-residual-ownership-evidence-review-mimo-20260612.md`
- `docs/reviews/mvp-release-readiness-residual-ownership-evidence-controller-judgment-20260612-102336.md`
- This plan artifact

Allowed prior context only if the current evidence worker needs to explain continuity:

- `docs/reviews/mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-153309.md`
- `docs/reviews/mvp-release-readiness-blocker-disposition-plan-controller-judgment-20260611-155001.md`

Forbidden reads:

- candidate residue bodies under `reviews/`
- old/candidate `docs/reviews/` residue bodies not listed above
- `docs/audit/` bodies
- `reports/` bodies
- PDFs
- scripts
- user-owned document bodies

## 2. Allowed Validation and Metadata

The future evidence worker may run only:

```text
git status --short
git status --branch --short
git diff --check
```

Allowed metadata is limited to:

- current branch and ahead/behind marker from `git status --branch --short`;
- tracked/untracked status codes and path strings from `git status --short`;
- whitespace validation result from `git diff --check`;
- accepted ownership rows, counts, non-proof flags and next-gate routing from the accepted ownership evidence and controller judgment;
- whether a visible path in `git status --short` is covered by an accepted ownership row or remains an uncovered blocker.

The future evidence worker must not use path metadata to infer file content. A path can prove only visibility and routing coverage, not provenance, correctness, release suitability, report validity, PDF validity, script safety or readiness.

## 3. Accepted Ownership Evidence vs Missing Readiness Evidence

Accepted ownership-routing evidence:

- 11 blocker-family rows are accepted as ownership-routing evidence.
- Each row has one primary owner and secondary stakeholders where applicable.
- Counts reconcile to accepted controller judgments: 36 review/audit paths, 13 runtime/live report rows, 15 research/user/tooling rows, 39 top-level review/audit rows and 11 rollup blocker rows.
- Every row remains `body_read=false` and non-proof: not source truth, not design truth, not control truth, not template truth, not release evidence and not readiness proof.

Missing readiness evidence:

- no proof that the current workspace is clean;
- no proof that every current visible residue is either absent or covered by an accepted exception;
- no proof that accepted exception routing is still current against the latest `git status --short`;
- no proof that newly visible untracked residue has a controller-accepted owner/disposition;
- no report/PDF/script/user-document body provenance;
- no live EID/provider/LLM/FDR/extractor/analyze/checklist/golden/readiness evidence;
- no cleanup, archive, delete, ignore, import or promotion evidence;
- no PR/push/merge/mark-ready/release external-state evidence.

Therefore the next evidence gate may at most prove `workspace cleanliness or accepted exceptions` from metadata. It must preserve `NOT_READY` unless controller later accepts a separate readiness gate with broader authorization.

## 4. Future Evidence Objective

Produce one non-live evidence artifact that answers exactly:

```text
Given the current git status output and the accepted ownership evidence at checkpoint 4d0e65b, is every visible workspace residue either absent or covered by an accepted non-proof exception route?
```

The evidence artifact must classify status-visible entries into three buckets:

1. `CLEAN`: no status-visible entry for the blocker family.
2. `ACCEPTED_EXCEPTION`: visible entry is covered by an accepted ownership-routing row and remains non-proof.
3. `UNCOVERED_BLOCKER`: visible entry is not covered by accepted ownership evidence, or the current gate/checkpoint cannot be reconciled.

If any `UNCOVERED_BLOCKER` exists, the conclusion must be `NOT_READY`.

If all visible residue is either absent or `ACCEPTED_EXCEPTION`, the artifact may state only that the metadata cleanliness route is reconciled. It still must not claim release readiness, PR readiness or mark-ready eligibility unless a separate controller gate explicitly authorizes that stronger conclusion.

## 5. Minimal Evidence Matrix

| Evidence question | Allowed proof source | Accept condition | Fail condition | Required conclusion |
|---|---|---|---|---|
| Current gate and checkpoint | `docs/current-startup-packet.md`; `docs/implementation-control.md`; ownership controller judgment | Gate is `Release-readiness cleanliness re-evidence planning/evidence` lineage and accepted input checkpoint is `4d0e65b` | Gate mismatch, checkpoint mismatch, missing `NOT_READY`, or stale control truth | Stop or `NOT_READY` |
| Branch/status context | `git status --branch --short` | Branch context recorded; no external-state inference made | command unavailable or output omitted | Stop |
| Whitespace hygiene | `git diff --check` | pass | whitespace error | `NOT_READY`; route to separate fix gate if needed |
| Tracked source/test/runtime diff | `git status --short` | no status-visible tracked source/test/runtime behavior edits outside the evidence artifact itself | modified/staged tracked source/test/runtime/README/design/control files appear | `NOT_READY`; stop if outside authorization |
| Target evidence artifact appearance | `git status --short` | future evidence artifact appears only as an untracked `docs/reviews/...cleanliness-re-evidence...md` path after write | generated artifact is outside `docs/reviews/` or staged/tracked unexpectedly | `NOT_READY` |
| Previously owned blocker families | `git status --short`; accepted ownership evidence table | each visible blocker family maps to exactly one accepted ownership row and remains non-proof | visible blocker family lacks accepted row or ownership row is ambiguous | `UNCOVERED_BLOCKER`; `NOT_READY` |
| `docs/reviews/` residue | path strings from `git status --short`; accepted ownership rows | visible `docs/reviews/` entries are current evidence/review/controller artifacts or accepted non-proof review/audit residue routes | new unowned `docs/reviews/` residue appears outside current evidence-chain and accepted routes | `UNCOVERED_BLOCKER`; `NOT_READY` |
| `reviews/` residue | path strings from `git status --short`; accepted ownership rows | visible root/files map to accepted top-level review/audit non-proof route | unowned nested candidate appears or body read would be required | `UNCOVERED_BLOCKER`; `NOT_READY` |
| `docs/audit/` residue | path strings only; accepted ownership rows | visible audit root remains exclusion/non-proof route | any claim needs audit body content | Stop; `NOT_READY` |
| `reports/live-evidence/` and `reports/manual-llm-smoke/` | path strings only; accepted ownership rows | visible report roots/files remain runtime/manual-smoke non-proof routes | any report is cited as live evidence/readiness proof or body provenance is needed | Stop; `NOT_READY` |
| research/spec/tooling/user-owned/PDF/template residue | path strings only; accepted ownership rows | visible entries map to accepted owner/disposition route and are not promoted | body read, import, promotion, script inspection, PDF validation or truth-source claim is needed | Stop; `NOT_READY` |
| Unknown visible residue | `git status --short` | no unknown residue outside accepted ownership rows | any unclassified path remains | `UNCOVERED_BLOCKER`; `NOT_READY` |

## 6. Evidence Artifact Structure for Future Worker

The future evidence artifact should contain:

1. Scope and `NOT_READY` preservation statement.
2. Read-boundary statement listing required reads and forbidden reads.
3. Raw command summaries for the three allowed validation commands, without adding unauthorized commands.
4. Current gate/checkpoint reconciliation table.
5. Status-to-ownership matrix with columns:
   - `status_path_or_family`
   - `git_status_marker`
   - `ownership_row`
   - `classification` (`CLEAN`, `ACCEPTED_EXCEPTION`, `UNCOVERED_BLOCKER`)
   - `primary_owner`
   - `next_gate`
   - `body_read`
   - `not_source_truth`
   - `not_design_truth`
   - `not_control_truth`
   - `not_release_evidence`
   - `not_readiness_proof`
6. Conclusion that preserves `NOT_READY`.
7. Deferred authorization list.
8. Stop-condition log.

The artifact must not include candidate file contents, report contents, PDF contents, script contents, old review body excerpts or user-owned document contents.

## 7. Acceptance Criteria for Future Evidence Gate

The future evidence gate can be accepted only if all criteria are met:

- current gate, input checkpoint `4d0e65b` and `NOT_READY` reconcile from current control truth;
- evidence uses only required truth reads and the three allowed validation commands;
- no candidate residue bodies are read;
- every status-visible residue path or family is classified as `CLEAN`, `ACCEPTED_EXCEPTION` or `UNCOVERED_BLOCKER`;
- every `ACCEPTED_EXCEPTION` maps to an accepted ownership row and carries all non-proof flags;
- every `UNCOVERED_BLOCKER` is explicitly listed with primary owner if known, next gate if known, and `NOT_READY` conclusion;
- no cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge/mark-ready/release occurs;
- no live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release command runs;
- `git diff --check` passes, or a whitespace failure is recorded as `NOT_READY`;
- DS and MiMo reviews both confirm the evidence stayed inside this plan and did not convert accepted metadata into readiness proof.

Non-acceptance conditions:

- any unclassified status-visible residue;
- any body read outside the required truth artifacts;
- any readiness, PR readiness or release claim;
- any source/test/runtime/README/design/control mutation;
- any attempt to use accepted ownership-routing evidence as release evidence.

## 8. Stop Conditions

Stop immediately and return to controller if:

- current control truth does not name this gate lineage or checkpoint `4d0e65b`;
- `NOT_READY` cannot be preserved exactly;
- any requested read would open candidate residue bodies under `reviews/`, unlisted old/candidate `docs/reviews/` bodies, `docs/audit/`, `reports/`, PDFs, scripts or user-owned documents;
- any requested command is outside `git status --short`, `git status --branch --short` or `git diff --check`;
- any step would run live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release commands;
- any step would cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge/mark-ready/release;
- any row attempts to convert metadata-only residue into source truth, design truth, control truth, template truth, release evidence or readiness proof;
- `git status --short` shows tracked source/test/runtime/README/design/control mutations outside the future evidence artifact write set;
- classification requires reading file bodies to decide.

## 9. DS/MiMo Reviewer Handoff Criteria

Reviewers should receive:

- this plan artifact;
- future evidence artifact;
- `AGENTS.md`;
- `docs/current-startup-packet.md`;
- `docs/implementation-control.md`;
- accepted ownership evidence artifact, DS review, MiMo review and controller judgment.

DS review focus:

- gate/checkpoint/`NOT_READY` reconciliation;
- status-to-ownership matrix completeness;
- classification of all visible residue as `CLEAN`, `ACCEPTED_EXCEPTION` or `UNCOVERED_BLOCKER`;
- command boundary compliance;
- no source/test/runtime/README/design/control mutation.

MiMo review focus:

- no metadata-to-proof conversion;
- accepted ownership evidence is separated from missing readiness evidence;
- all accepted exceptions retain `body_read=false` and non-proof flags;
- deferred authorization list is complete;
- conclusion does not claim readiness, PR readiness or release readiness.

Reviewer acceptance requires zero blocking findings or explicit targeted amendments followed by re-review. Reviewer artifacts must not read forbidden residue bodies and must not run commands outside the same validation boundary unless a separate controller authorization exists.

## 10. Deferred Entries Requiring Separate Authorization

The following remain deferred and require separate reviewed authorization:

- live EID evidence;
- controlled live annual-period narrative evidence;
- provider/LLM live acceptance;
- FDR/PDF/network/source acquisition;
- extractor/analyze/checklist/golden/readiness/score-loop/release commands;
- cleanup/archive/delete/move/ignore/import/promote actions;
- body reads for `reports/`, PDFs, scripts and user-owned documents;
- candidate body reads under `reviews/`, old/candidate `docs/reviews/` residue and `docs/audit/`;
- `.gitignore` edits;
- source/test/runtime behavior changes;
- README, `docs/design.md`, `docs/current-startup-packet.md` or `docs/implementation-control.md` changes;
- PR, push, merge, mark-ready or release external-state actions.

## 11. Validation for This Planning Artifact

Allowed commands for this planning gate:

```text
git status --short
git status --branch --short
git diff --check
```

Expected post-write result:

- `git status --short` shows this plan as an untracked `docs/reviews/` artifact and existing residue remains visible.
- `git status --branch --short` records branch context without changing external state.
- `git diff --check` passes.

Release/readiness remains `NOT_READY`.
