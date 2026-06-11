# MVP Runtime/live Report Residue Disposition Plan - 2026-06-12

## 0. Worker Self-check

- Current gate / role: `Runtime/live report residue disposition planning gate`; planning worker only.
- Scope: write this plan artifact only for `reports/live-evidence/` and `reports/manual-llm-smoke/`.
- Boundary: non-live, metadata-only planning. Do not classify individual report files in this gate.
- Forbidden now: report body reads, live execution, cleanup/archive/delete/ignore, source/test/runtime/truth-doc edits, staging, commit, push, PR, merge, mark-ready or readiness claim.
- Validation before stop: `git status --short reports/live-evidence reports/manual-llm-smoke`, `git status --branch --short`, `git diff --check`.

## 1. Goal

Plan a future non-live metadata-only disposition evidence gate for current report residue roots:

- `reports/live-evidence/`
- `reports/manual-llm-smoke/`

The plan must let a future evidence worker identify metadata-only inventory and disposition fields without treating report contents as proof and without changing release/readiness state. Release/readiness remains `NOT_READY`.

## 2. Fact Separation

### 2.1 Repo Facts

Current allowed status checks show:

- Branch: `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 132]`.
- `reports/live-evidence/` is visible as untracked root.
- `reports/manual-llm-smoke/` is visible as untracked root.
- `git diff --check` passes before this artifact is written.

These are repository metadata facts only. They do not prove report validity, live acceptance, release evidence, readiness proof, provider behavior, EID correctness or artifact ownership.

### 2.2 Truth-doc Facts

From `docs/current-startup-packet.md` and `docs/implementation-control.md`:

- Current active gate is `Runtime/live report residue disposition planning gate`.
- Gate classification is `standard`; planning only, non-live, metadata-only unless separately authorized, no report-content proof, no PR/release external state.
- Current production default remains deterministic `fund-analysis analyze/checklist`.
- Current `--use-llm` path remains explicit opt-in and fail-closed.
- Controlled live evidence is accepted only for the single sample `004393 / 2021-2025`; additional live samples and readiness remain deferred.
- Review/audit residue evidence accepted 36 paths as non-proof metadata classification; no path was accepted as source truth, release evidence or readiness proof.
- Current next entry point is this planning gate; controlled live annual-period narrative evidence is a separate explicitly authorized gate.

### 2.3 Prior Controller Judgments

- `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-controller-judgment-20260612-061558.md`: verdict `ACCEPT_WITH_RESIDUALS_NOT_READY`; release/readiness remains `NOT_READY`; next recommended mainline is this runtime/live report residue disposition planning gate.
- `docs/reviews/mvp-release-readiness-residual-artifact-disposition-plan-20260612.md`: deferred runtime/live report residue to a separate metadata-only planning/evidence path; report bodies must not be read as truth.
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`: prior metadata-only index saw `reports/manual-llm-smoke/` as scratch/runtime output or live evidence residue; no residue was deleted, moved, archived, ignored, staged, promoted or used as proof.

## 3. Non-goals

This plan does not authorize:

- classification of individual report files in the current planning gate;
- reading report body contents, PDFs, provider outputs or runtime logs as proof;
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands;
- cleanup, archive, delete, move, import, promote or `.gitignore` changes;
- source, test, runtime, README, `docs/design.md`, `docs/current-startup-packet.md` or `docs/implementation-control.md` changes;
- PR, push, merge, mark-ready, request-reviewer, external comment or release-state changes;
- release/readiness claim. Result remains `NOT_READY`.

## 4. Future Stage B Evidence Gate

### 4.1 Objective

Create a metadata-only inventory and disposition evidence artifact for `reports/live-evidence/` and `reports/manual-llm-smoke/`, preserving non-proof status unless a later live evidence gate explicitly accepts exact artifacts under direct evidence standards.

### 4.2 Allowed Read Set

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-plan-20260612.md`
- this plan's future DS/MiMo reviews, if present
- this plan's future controller judgment, if present
- `docs/reviews/mvp-release-readiness-residual-artifact-disposition-plan-20260612.md`
- `docs/reviews/mvp-review-artifact-residual-acceptance-evidence-controller-judgment-20260612-061558.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- metadata-only status/listing output for `reports/live-evidence/` and `reports/manual-llm-smoke/`

Report bodies are excluded from the allowed read set. If a file name itself contains sensitive or ambiguous semantic claims, the evidence must treat that as a path label only, not proof.

### 4.3 Allowed Write Set

- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-20260612.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-review-ds-20260612.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-review-mimo-20260612.md`
- `docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-controller-judgment-20260612-*.md`

No writes under `reports/`, source, tests, runtime, truth docs, README, `.gitignore` or external systems.

### 4.4 Future Metadata-only Commands

The future evidence gate may use metadata-only file listing/counting only if the controller handoff explicitly authorizes it. The current planning gate did not execute these commands.

Proposed exact commands:

```text
git status --short reports/live-evidence reports/manual-llm-smoke
find reports/live-evidence -maxdepth 3 -type f -print | sort
find reports/manual-llm-smoke -maxdepth 3 -type f -print | sort
find reports/live-evidence -maxdepth 3 -type f -print | wc -l
find reports/manual-llm-smoke -maxdepth 3 -type f -print | wc -l
git status --branch --short
git diff --check
```

The `find` commands are for path metadata only. They must not use `cat`, `sed`, `head`, `tail`, parsers, checksums as content proof, JSON/Markdown body reads, report rendering, live re-run or provider replay.

### 4.5 Required Output Fields

Future evidence must output one row per authorized root and, if listing is authorized, one row per listed path:

- `root`
- `path` if listing authorized; otherwise `path_listing_authorized=false`
- `status_seen`
- `report_family`: one of `live_evidence_root`, `manual_llm_smoke_root`, `candidate_live_run_artifact`, `manual_smoke_output`, `runtime_diagnostic_output`, `unknown_report_residue`
- `possible_live_evidence_candidate`: boolean
- `not_source_truth`: must be `true`
- `not_release_evidence`: must be `true`
- `not_readiness_proof`: must be `true`
- `owner`
- `next_gate`

Allowed classification rule:

- `possible_live_evidence_candidate=true` only means a path may need a later live evidence provenance gate. It does not accept the path as live evidence.
- `not_source_truth=true`, `not_release_evidence=true`, and `not_readiness_proof=true` are mandatory for every row in this metadata-only evidence gate.

### 4.6 Acceptance Criteria

- Both report roots are covered.
- Every authorized row has the required fields.
- New or ambiguous paths are called out as unresolved residue, not silently accepted.
- No report body is read or summarized.
- No artifact is accepted as source truth, release evidence, readiness proof or final live acceptance.
- Release/readiness remains `NOT_READY`.
- Validation commands pass or failures are recorded as blockers.

## 5. Explicit Forbidden Actions

Forbidden in both this plan gate and the future Stage B evidence gate unless separately authorized:

- live execution: EID, network, PDF, FDR, provider, LLM, extractor, analyze, checklist, golden, readiness or release commands;
- report body read as proof, including Markdown/JSON/text/PDF/log parsing or summarization;
- cleanup, archive, delete, move, import, promote, stage or commit report files;
- `.gitignore` or ignore-rule changes;
- PR, push, merge, mark-ready, request-reviewer, release-state or external comment actions;
- readiness claim or wording that implies release/readiness pass.

## 6. Separate Authorization List

These require separate reviewed authorization:

- live evidence execution or replay;
- report body reading for exact artifact provenance;
- accepting any report path as live evidence;
- cleanup, archive, delete, move or import of report residue;
- `.gitignore` policy changes for repeat runtime outputs;
- PR, push, merge, mark-ready or release/readiness gate;
- control-truth or design-truth updates.

## 7. Mainline and Deferred Entries

Mainline next entry after this plan is accepted: `Runtime/live report residue disposition metadata evidence gate` for `reports/live-evidence/` and `reports/manual-llm-smoke/`.

Immediate review route before acceptance: DS/MiMo plan review, then controller judgment.

Deferred entries:

- controlled live annual-period narrative evidence gate;
- report-body provenance gate for exact artifacts;
- cleanup/archive/delete gate for report residue;
- ignore-rule policy gate;
- research/user-owned/tooling residue disposition gate;
- release-readiness cleanliness re-evidence gate;
- PR/push/merge/mark-ready/release gate.

## 8. DS / MiMo Review Checklist

Reviewers should verify:

- planning scope is narrow and does not classify individual report files now;
- fact separation distinguishes repo metadata, truth-doc facts and prior controller judgments;
- future Stage B read/write sets are exact and exclude report bodies;
- metadata-only listing/counting commands are future-only and require explicit controller authorization;
- required output fields include `root`, `path` when authorized, `status_seen`, `report_family`, `possible_live_evidence_candidate`, `not_source_truth`, `not_release_evidence`, `not_readiness_proof`, `owner`, `next_gate`;
- `possible_live_evidence_candidate=true` cannot be interpreted as accepted live evidence;
- forbidden actions and separate authorization list cover live execution, report body proof, cleanup/archive/delete, ignore rules, PR/push/merge/mark-ready and readiness claims;
- there is one accepted-plan mainline next entry and deferred entries remain deferred;
- release/readiness remains `NOT_READY`.

## 9. Completion Report Format For Future Stage B Evidence Worker

```text
Self-check: pass | blocked - <reason>
Artifact: docs/reviews/mvp-runtime-live-report-residue-disposition-evidence-20260612.md
Gate: Runtime/live report residue disposition metadata evidence gate
Scope: metadata-only, non-live, no report body reads
Inventory:
- roots covered: <count/list>
- paths listed: <count or not authorized>
Classification summary:
- live_evidence_root: <count>
- manual_llm_smoke_root: <count>
- candidate_live_run_artifact: <count>
- manual_smoke_output: <count>
- runtime_diagnostic_output: <count>
- unknown_report_residue: <count>
Validation:
- git status --short reports/live-evidence reports/manual-llm-smoke: <result>
- git status --branch --short: <result>
- git diff --check: <result>
Residuals:
- <owner / next_gate / blocker status>
Forbidden actions confirmed not performed:
- no live execution
- no report body read as proof
- no cleanup/archive/delete/ignore change
- no PR/push/merge/mark-ready/release/readiness claim
```
