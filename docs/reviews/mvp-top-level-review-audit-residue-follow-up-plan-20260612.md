# Plan: Top-level Review/Audit Residue Follow-up

Date: 2026-06-12

Gate: `Top-level review/audit residue follow-up planning gate`

Classification: `standard`

## 0. Worker Self-check

- Role: planning worker only.
- Current accepted input: `Research/user-owned/tooling residue metadata evidence gate` accepted at `98f3bd2`.
- Truth docs read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- This plan does not read review/audit artifact bodies, implement cleanup, archive, delete, move, ignore, import, promote, stage report artifacts, run live commands, or change source/test/runtime behavior.
- This plan does not use untracked review/audit residue as source truth, design truth, release evidence, readiness proof or current control truth.

## 1. Problem Statement

The prior research/user-owned/tooling metadata evidence accepted that:

- top-level `reviews/` is untracked review/audit-style residue with 2 listed files;
- `docs/reviews/` remains visibly dirty with count drift from prior review-artifact evidence checkpoints;
- both groups are non-proof residue and release/readiness remains `NOT_READY`.

This gate plans the next metadata-only follow-up so the controller can separate:

- top-level `reviews/` residue from canonical `docs/reviews/` evidence-chain artifacts;
- current newly visible `docs/reviews/` drift from previously accepted review/audit residue classifications;
- review/audit residue classification from cleanup/archive/delete/import/promote decisions.

## 2. Current Scope

### 2.1 Included Groups

| Path/root | Current status | Planning disposition |
|---|---|---|
| `reviews/` | top-level untracked root; 2 files listed by prior metadata evidence | Include in next metadata evidence gate |
| `docs/reviews/` untracked entries visible in `git status --short` | review/audit residue count drift from ongoing gates and older artifacts | Include as path-status metadata only; do not read bodies |

### 2.2 Excluded Groups

| Path/root | Reason |
|---|---|
| `docs/audit/` | Prior audit input/residue chain; no body read in this gate |
| `reports/live-evidence/` | Runtime/live report metadata evidence accepted at `e48b642` |
| `reports/manual-llm-smoke/` | Runtime/live report metadata evidence accepted at `e48b642` |
| `基金年报/` | User-owned PDF corpus; separate corpus gate if needed |
| `scripts/claude_mimo_simple.py` | Source-like tooling residue; separate tooling ownership gate if needed |
| `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/...`, `docs/tmux-agent-memory-store.md`, `定性分析模板.md` | Research/user-owned/tooling residue already metadata-classified at `98f3bd2`; follow-up depends on owner-specific gates |

## 3. Non-goals

- No review/audit file body reads.
- No cleanup, archive, delete, move, ignore-rule change, import, promote, stage, commit, push, PR, merge, mark-ready or release action.
- No source/test/runtime behavior changes.
- No `docs/design.md`, `docs/implementation-control.md`, startup-packet or README changes in the evidence gate.
- No live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release commands.
- No acceptance of any path as source truth, design truth, control truth, release evidence or readiness proof.

## 4. Proposed Next Evidence Gate

Name: `Top-level review/audit residue metadata evidence gate`

Purpose: produce path-level metadata for top-level `reviews/` and visible untracked `docs/reviews/` entries, with count summaries and mandatory non-proof flags.

### 4.1 Allowed Read Set

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- this plan
- future plan reviews and controller judgment

### 4.2 Allowed Metadata Commands

Only these metadata commands are proposed for the future evidence gate:

- `git status --short`
- `git status --branch --short`
- `git status --short -- reviews docs/reviews`
- `find reviews -maxdepth 3 -type f -print | sort`
- `git diff --check`

The evidence worker may count visible `docs/reviews/` entries from `git status --short` output, but must not read their file bodies.

### 4.3 Required Evidence Fields

Each future evidence row must include:

- `path`
- `status_seen`
- `group`
- `path_listing_authorized`
- `body_read=false`
- `not_source_truth=true`
- `not_design_truth=true`
- `not_control_truth=true`
- `not_release_evidence=true`
- `not_readiness_proof=true`
- `owner`
- `next_gate`

### 4.4 Required Counts

The evidence gate must report:

- `reviews/` root count and file count;
- visible untracked `docs/reviews/` entry count from `git status --short`;
- count by `group`;
- count by `next_gate`;
- whether any top-level `reviews/` path is missing from evidence rows.

## 5. Review Requirements

- DS review: verify command boundary, count arithmetic, non-proof fields, no body reads, no cleanup/import/promotion and NOT_READY preservation.
- MiMo review: verify top-level `reviews/` routing, `docs/reviews/` drift handling, distinction between evidence-chain artifacts and current truth, and that no path is promoted to release/readiness proof.
- Controller judgment: accept/rewrite/defer/reject each plan element and choose a single next entry.

## 6. Proposed Controller Decision Matrix

| Decision item | Proposed disposition |
|---|---|
| top-level `reviews/` root | DEFER to metadata evidence; route to review/audit residue classification, not research/tooling acceptance |
| top-level `reviews/` files | DEFER to metadata evidence; no body read |
| `docs/reviews/` untracked drift | DEFER to metadata evidence; count/status only, no body read |
| cleanup/archive/delete/ignore/import/promote | DEFER; requires separate exact-path authorization |
| release/readiness | remains `NOT_READY` |

## 7. Next Entry

Mainline next entry: `Top-level review/audit residue metadata evidence gate`.

Deferred entries:

- source-like tooling ownership gate for `scripts/claude_mimo_simple.py`
- user-owned PDF corpus ingestion/disposition gate
- user-owned template/spec truth-source decision gate
- cleanup/archive/delete/ignore policy gate
- release-readiness cleanliness re-evidence gate
- PR/push/merge/mark-ready/release gate

## 8. Validation

For this planning gate:

- `git status --short`
- `git status --branch --short`
- `git diff --check`

Expected result: dirty/untracked workspace remains visible; `git diff --check` passes; release/readiness remains `NOT_READY`.
