# Plan: Research/User-owned/Tooling Residue Disposition

Date: 2026-06-12

Gate: `Research/user-owned/tooling residue disposition planning gate`

Classification: `standard`

## 0. Worker Self-check

- Role: planning worker only.
- Current accepted input: `Runtime/live report residue disposition metadata evidence gate` accepted at `e48b642`.
- Truth docs read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- This plan does not implement, clean, archive, delete, move, ignore, import, promote, stage report artifacts, run live commands, or change source/test/runtime behavior.
- This plan does not use arbitrary untracked residue as source truth, release evidence, readiness proof, fixture proof, golden proof or product evidence.

## 1. Problem Statement

The release-readiness residue chain has already produced accepted non-proof classification for:

- review/audit residue under the previous review-artifact evidence gates;
- runtime/live report residue under `reports/live-evidence/` and `reports/manual-llm-smoke/`.

The workspace still contains visible untracked residue outside those accepted groups. The next step is to plan a bounded disposition pass for remaining research, user-owned and tooling paths without reading report bodies, importing corpus files, changing runtime behavior, or performing cleanup.

## 2. Current Path-level Scope

The planning pass uses `git status --short` and path listings only. No file body was read for this plan.

### 2.1 Excluded From This Gate

| Path/root | Reason |
|---|---|
| `docs/reviews/` untracked review artifacts | Already handled by review-artifact residue evidence chain; remaining historical review/audit residue remains non-proof unless a later exact-path gate says otherwise. |
| `docs/audit/` | Already handled as audit input/residue by prior review/audit disposition chain; not source truth. |
| `reports/live-evidence/` | Runtime/live report residue metadata accepted at `e48b642`; content provenance remains deferred. |
| `reports/manual-llm-smoke/` | Runtime/live report residue metadata accepted at `e48b642`; content provenance remains deferred. |

### 2.2 Candidate Paths For This Gate Family

| Path/root | Initial category | Current disposition | Required future gate |
|---|---|---|---|
| `docs/learning-roadmap.md` | research/user planning doc | unclassified residue; not truth source | metadata evidence gate, then user/controller disposition |
| `docs/next-development-phaseflow.md` | research/user planning doc | unclassified residue; not truth source | metadata evidence gate, then user/controller disposition |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research/spec residue | unclassified residue; not design truth | metadata evidence gate, then spec disposition gate if needed |
| `docs/tmux-agent-memory-store.md` | tooling/agent-ops note | unclassified residue; not control truth | metadata evidence gate, then tooling disposition gate if needed |
| `reviews/` | top-level review/audit-style residue outside `docs/reviews/` | unclassified residue; not release evidence | metadata evidence gate; may be routed to review/audit follow-up instead of research/tooling acceptance |
| `scripts/claude_mimo_simple.py` | local tooling script residue | unclassified source-like/tooling residue; not runtime source | metadata evidence gate, then source-like tooling ownership gate if needed |
| `基金年报/` | user-owned PDF/document corpus | unclassified user-owned corpus; not repository source truth and not production access path | metadata-only corpus listing gate; import/use requires separate document-repository ingestion gate |
| `定性分析模板.md` | user-owned template/research doc | unclassified user-owned doc; not template truth | metadata evidence gate, then user/controller disposition |

## 3. Non-goals

- No file deletion, movement, archive, cleanup, ignore-rule change, import or promotion.
- No changes to `.gitignore`, README, `pyproject.toml`, source, tests, runtime code, docs/design truth, or release state.
- No PDF, report, Markdown, Python or review body reads in the planning gate.
- No live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release command.
- No direct filesystem use of annual-report PDFs for production analysis; production annual report access remains through `FundDocumentRepository`.
- No acceptance of `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/...`, `docs/tmux-agent-memory-store.md`, `reviews/`, `scripts/claude_mimo_simple.py`, `基金年报/` or `定性分析模板.md` as source truth, design truth, template truth, release evidence or readiness proof.

## 4. Proposed Next Evidence Gate

Name: `Research/user-owned/tooling residue metadata evidence gate`

Purpose: produce path-level metadata rows for the candidate paths in section 2.2, with mandatory non-proof flags and next-owner routing.

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
- `git status --short -- docs/learning-roadmap.md docs/next-development-phaseflow.md docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md docs/tmux-agent-memory-store.md reviews scripts/claude_mimo_simple.py 基金年报 定性分析模板.md`
- `find reviews -maxdepth 3 -type f -print | sort`
- `find 基金年报 -maxdepth 2 -type f -print | sort`
- `git diff --check`

These commands list path presence only. They do not authorize reading file bodies.

### 4.3 Required Evidence Fields

Each future evidence row must include:

- `path`
- `status_seen`
- `initial_category`
- `path_listing_authorized`
- `body_read=false`
- `not_source_truth=true`
- `not_design_truth=true`
- `not_template_truth=true`
- `not_release_evidence=true`
- `not_readiness_proof=true`
- `owner`
- `next_gate`

### 4.4 Required Counts

The evidence gate must report:

- candidate path/root count;
- `reviews/` file count from path listing only;
- `基金年报/` file count from path listing only;
- count by `initial_category`;
- count by `next_gate`;
- any candidate path missing from the expected status/listing.

## 5. Review Requirements

- DS review: verify scope, allowed commands, excluded groups, non-proof fields, and no source/test/runtime/design-truth changes.
- MiMo review: verify route completeness, top-level `reviews/` ambiguity, user-owned PDF/corpus boundary, and source-like tooling script risk.
- Controller judgment: accept/rewrite/defer/reject each major plan element and recommend a single next entry.

## 6. Proposed Controller Decision Matrix

| Decision item | Proposed disposition |
|---|---|
| Research/user docs (`docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`) | DEFER to metadata evidence; no truth-source acceptance |
| Template/spec-like docs (`docs/superpowers/...`, `定性分析模板.md`) | DEFER to metadata evidence; no design/template-truth acceptance |
| Tooling note/script (`docs/tmux-agent-memory-store.md`, `scripts/claude_mimo_simple.py`) | DEFER to metadata evidence; source-like script may require separate tooling ownership gate |
| User-owned PDF corpus (`基金年报/`) | DEFER to metadata evidence; never production source truth without repository ingestion gate |
| Top-level `reviews/` | DEFER to metadata evidence; likely route to review/audit residue follow-up |
| Release/readiness | Remains `NOT_READY` |

## 7. Next Entry

Mainline next entry: `Research/user-owned/tooling residue metadata evidence gate`.

Deferred entries:

- top-level review/audit residue follow-up gate;
- source-like tooling ownership gate for `scripts/claude_mimo_simple.py`;
- user-owned PDF corpus ingestion/disposition gate;
- user-owned template/spec truth-source decision gate;
- cleanup/archive/delete/ignore policy gate;
- release-readiness cleanliness re-evidence gate;
- PR/push/merge/mark-ready/release gate.

## 8. Validation

For this planning gate:

- `git status --short`
- `git status --branch --short`
- `git diff --check`

Expected result: dirty/untracked workspace remains visible; `git diff --check` passes; release/readiness remains `NOT_READY`.
