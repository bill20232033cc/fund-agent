# P11-S1 Control Doc Hygiene / Recovery Plan

- **Date**: 2026-05-21
- **Planning specialist**: AgentCodex
- **Current gate**: `post-P10 follow-up planning accepted`
- **Next gate**: `P11-S1 control doc hygiene and recovery plan/review`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Input artifacts read**:
  - `AGENTS.md`
  - `docs/design.md`
  - `docs/implementation-control.md`
  - `docs/reviews/post-p10-follow-up-planning-20260521.md`

## Verdict

**Plan verdict: CODE-GENERATION-READY FOR DOCUMENTATION IMPLEMENTATION.**

P11-S1 should proceed as a documentation-only hygiene slice. The implementation should reduce `phaseflow` resume and handoff cost by making the active state and historical evidence navigation explicit, while preserving all accepted gate evidence, artifact paths, commit hashes, PR links, validation results, and residual-risk owners.

## Scope

### Goals

1. Make the current project state recoverable from the top of `docs/implementation-control.md` in one short read.
2. Preserve `docs/implementation-control.md` as the implementation control truth.
3. Keep every historical gate fact traceable to durable review artifacts.
4. Separate active state from historical archive without deleting history or review artifacts.
5. Define mechanical checks that catch broken artifact references after the hygiene pass.

### Non-Goals

- Do not change source code, tests, config, CLI behavior, product behavior, Fund Capability logic, audit rules, quality gate behavior, renderer output, extraction logic, or runtime wiring.
- Do not delete historical review artifacts.
- Do not rewrite prior accepted gate facts.
- Do not auto-resolve RR-13 duplicate `016492`; it remains user/App-source owned.
- Do not publish, commit, summarize as accepted evidence, or move `docs/repo-audit-20260521.md`.
- Do not introduce Dayu runtime, Host, Engine, tool loop, prompt scene registry, or LLM writing.

## First-Principles Diagnosis

The current failure mode is control-plane recovery cost, not missing evidence. `docs/implementation-control.md` contains the facts needed for phaseflow, but startup requires scanning a long mixed narrative of active state, historical phase entries, artifacts, residual risks, and PR records.

The right fix is not to discard history. The right fix is to make the first screen answer "what should the next controller do now?" and make older evidence reachable through stable indexes and anchors.

## File Ownership

Implementation should modify only documentation-control files:

- Required: `docs/implementation-control.md`
- Optional only if review explicitly accepts it: a same-directory appendix such as `docs/implementation-control-history.md`

Default recommendation: keep history inside `docs/implementation-control.md` for P11-S1. Use same-file archive sections and anchors first, because the current control doc already states that it remains the phaseflow control truth.

Do not edit `docs/design.md` unless the hygiene pass discovers a direct contradiction between the design truth and the control doc. If that happens, stop and produce a reconciliation artifact instead of silently changing both documents.

## Target Structure

Rewrite `docs/implementation-control.md` into this stable order.

### 1. Startup Packet

Keep this section near the top and short enough for a resume agent to read before doing anything else.

Hard size constraint: `Startup Packet` plus `Active Gate Ledger` should be no more than 80 lines in total. The phase history index can expand after those sections. The core target is first-screen recovery: one short read should identify the current gate, next action, open residual owners, and non-goals.

Required fields:

| Field | Required value source |
|---|---|
| Branch | current control-doc state, currently `main` |
| Current gate | currently `post-P10 follow-up planning accepted` |
| Next entry point | currently `P11-S1 control doc hygiene and recovery plan/review` |
| Current phase | currently `P11 Control doc hygiene / recovery ergonomics` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Latest accepted artifact | `docs/reviews/post-p10-follow-up-planning-20260521.md` |
| Last merged PR | PR #6, merge commit `acc692c7e84c855398de86497b0d05f30b6f5ca5` |
| Product baseline | P10 release-readiness merged; no product behavior change pending |
| Open residuals | control doc hygiene, RR-13 duplicate `016492`, excluded `docs/repo-audit-20260521.md` |
| Non-goal reminder | no source/product/runtime changes in P11-S1 |

Add a controller resume checklist directly under the table:

1. Confirm current gate and next entry point.
2. Confirm the next action is documentation planning/review, not implementation.
3. Confirm no source code or product behavior changes are in scope.
4. Check open residual owners before starting a new phase.
5. Do not run the artifact existence check as a fixed resume step; it is a P11-S1 implementation acceptance gate after the hygiene edit changes references.

### 2. Active Gate Ledger

Add a compact ledger for only the active and immediately previous gates.

Rows should include:

- `post-P10 follow-up planning accepted`
- `P11-S1 control doc hygiene and recovery plan/review`

Columns:

| Column | Meaning |
|---|---|
| Gate | Exact gate name |
| Status | `accepted`, `planned`, `blocked`, etc. |
| Artifact | Durable artifact path |
| Commit / PR | Commit hash or PR link if applicable |
| Validation | Exact validation result if applicable, or `docs-only / not run` |
| Residual owner | Person, phase, or artifact owner |
| Next action | The next controller action |

This ledger should become the default resume target. Historical phase evidence should not be duplicated here.

The ledger must stay compact enough to keep the combined `Startup Packet` + `Active Gate Ledger` under the 80-line limit. If a field would make the ledger sprawl, link to the phase history index or archive entry instead of adding prose.

### 3. Phase History Index

Add a navigation table that covers every phase and major follow-up sequence from P0 through P11.

Columns:

| Column | Required content |
|---|---|
| Phase / sequence | `P0`, `P1`, ..., `P10`, `P11`, plus post-phase follow-ups where needed |
| Status | `done`, `merged`, `planned`, `blocked-on-human`, etc. |
| Anchor | Link to the detailed same-file archive section |
| Primary artifacts | One to three highest-value artifact paths |
| Merge / accepted commit | Merge commit, accepted local commit, or `n/a` |
| Last validation | Exact suite result if recorded |
| Open residuals | Risk IDs or owner, not prose-only notes |

This table is an index, not a replacement for evidence. It should point to the detailed archive where exact gate facts remain.

Anchor format constraints:

- Archive sections must use phase-prefixed unique headings.
- Use headings like `## Archive: P0`, `## Archive: P1`, ..., `## Archive: P11`.
- Every archive heading must be unique within `docs/implementation-control.md`.
- The `Phase History Index` anchor column must point to those exact archive headings.
- If a phase needs sub-archives, use unique nested headings under the phase archive, for example `### Archive: P10 Draft PR Gate`; do not create a second `## Archive: P10`.

### 4. Current Phase Plan Block

Add a P11 block with:

- P11 goal: reduce phaseflow resume/handoff cost while preserving gate evidence.
- P11-S1 scope: documentation plan/review only.
- P11-S1 implementation guardrails:
  - documentation-only;
  - no product source changes;
  - no history deletion;
  - no RR-13 decision;
  - no `docs/repo-audit-20260521.md` inclusion;
  - no Dayu runtime/Host/Engine/tool loop/LLM writing.
- P11-S1 success signals:
  - startup packet reads as the active truth;
  - historical phase index points to every phase archive;
  - all preserved artifact references either exist or are explicitly marked external/non-file;
  - residual risks have owners;
  - design/control alignment rules are documented.

### 5. Evidence Preservation Rules

Add a subsection that defines immutable fields for every accepted gate record.

Every gate archive entry must preserve, when available:

- artifact paths;
- plan review paths;
- code review paths;
- controller judgment paths;
- re-review paths;
- implementation artifact paths;
- accepted local commit hashes;
- PR URLs;
- PR branch/head/merge commit;
- CI run IDs and status;
- validation commands and exact pass counts;
- residual risk IDs and owners;
- reviewer limitations or availability caveats.

If an old entry lacks one of these fields, do not invent it. Use `not recorded` only when the historical record truly lacks it.

### 6. Archive / Summarize Strategy

Use three levels of detail.

Level 1: Active Startup Packet

- Contains only current gate, next entry point, latest artifact, open residuals, and immediate next action.
- No deep historical prose.

Level 2: Phase History Index

- One table row per phase or major sequence.
- Preserves pointers to details, not every detail inline.

Level 3: Historical Evidence Archive

- Keeps the detailed historical gate log.
- May be reorganized into phase subsections.
- May remove duplicated prose only when the exact fact is retained in a table or archive entry.
- Must not delete artifact paths, commits, PR links, validation results, or residual owners.

Default archive location for P11-S1: same file, below active sections.

Do not move history to a separate file in this slice unless reviewers explicitly accept the tradeoff. If a future slice splits a separate history file, `docs/implementation-control.md` must still state that file is part of the control record and must link to it from the startup packet.

### 7. Design / Control Alignment Rules

Add explicit alignment rules:

1. `docs/design.md` remains the design truth for architecture, boundaries, product behavior, Dayu non-dependency, and FundDocumentRepository source boundaries.
2. `docs/implementation-control.md` remains the control truth for phase state, gates, artifacts, commits, validation, residual risks, and next entry point.
3. A control-doc hygiene pass may reorganize implementation history but may not change design facts.
4. If control history contradicts `docs/design.md`, create a reconciliation artifact before changing either document.
5. The current design facts that must not regress during P11 are:
   - `fund-analysis analyze` remains a deterministic UI -> Service -> Fund Capability path;
   - Dayu remains methodology/reference only, not production runtime;
   - `FundDocumentRepository` remains the production annual-report entry point;
   - fallback taxonomy remains `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`;
   - no prompt scene registry, Host session, Engine tool loop, or LLM writing is introduced.

### 8. Residual Risk Handling

Keep the residual risk table, but add an active residual section near the top.

Active residuals for this slice:

| Risk | Owner | Required handling |
|---|---|---|
| Control doc recovery cost | P11-S1 | Address through startup packet, history index, archive rules, existence checks |
| RR-13 duplicate `016492` | User / App source | Preserve as human-owned; do not modify CSV |
| `docs/repo-audit-20260521.md` | Controller / user | Keep excluded unless later scope accepts publication |
| Future product feature selection | Post-P11 planning | Deferred |

Historical risks should remain in the existing residual table or a phase archive table. Closed risks can be summarized, but accepted closure artifact paths must remain.

## Code-Generation-Ready Implementation Steps

1. Open `docs/implementation-control.md`.
2. Add or replace the current top snapshot with the new `Startup Packet`.
3. Add `Active Gate Ledger` immediately after the startup packet.
4. Add `Phase History Index` before detailed historical content.
5. Add `P11 Current Phase Plan` with goals, non-goals, guardrails, and success signals.
6. Add `Evidence Preservation Rules`, `Archive / Summarize Strategy`, and `Design / Control Alignment Rules`.
7. Reorganize existing detailed historical content under a clearly named `Historical Evidence Archive`.
8. Preserve all exact artifact paths, commits, PR links, validation results, and residual owners from the existing text.
9. Remove only duplicated prose that is already preserved in a table or archive entry.
10. Do not touch `docs/repo-audit-20260521.md`.
11. Run reference checks and markdown diff review.

## Artifact Existence Check Recommendation

P11-S1 should include a mechanical check for file-backed references after the documentation edit.

This check is a one-time P11-S1 implementation acceptance gate, not a fixed action for every `phaseflow` resume. Resume should stay lightweight and rely on the startup packet and active gate ledger; reference checks should run when the hygiene implementation modifies or reorganizes artifact references.

Suggested shell check for `docs/reviews/...` paths:

```bash
rg -o 'docs/reviews/[A-Za-z0-9._/-]+\.md' docs/implementation-control.md | sort -u | while read -r path; do test -f "$path" || echo "missing: $path"; done
```

Suggested broader check for local `docs/...` markdown references:

```bash
rg -o 'docs/[A-Za-z0-9._/-]+\.md' docs/implementation-control.md | sort -u | while read -r path; do test -f "$path" || echo "missing: $path"; done
```

External PR URLs, GitHub Actions run IDs, branch names, and commit hashes are not file paths. They should be preserved as strings and reviewed manually for obvious truncation.

If a historical artifact path is missing:

1. Do not delete the reference.
2. Mark it as `missing local artifact reference` in the archive.
3. Assign owner to controller reconciliation.
4. Do not silently replace it with a nearby artifact.

## Validation Plan

Documentation-only validation:

```bash
git diff --check
```

Artifact reference validation:

```bash
rg -o 'docs/reviews/[A-Za-z0-9._/-]+\.md' docs/implementation-control.md | sort -u | while read -r path; do test -f "$path" || echo "missing: $path"; done
```

Run this artifact reference validation once before accepting the P11-S1 implementation. Do not add it to the routine resume checklist.

Manual review checklist:

- `Startup Packet` plus `Active Gate Ledger` are no more than 80 lines total.
- The first screen identifies the current gate, next entry point, open residual owners, and non-goals.
- `Phase History Index` anchors point to unique phase-prefixed archive headings such as `## Archive: P0` through `## Archive: P11`.
- P10 merge facts remain visible: PR #6 and merge commit `acc692c7e84c855398de86497b0d05f30b6f5ca5`.
- `docs/reviews/post-p10-follow-up-planning-20260521.md` remains the latest accepted planning artifact.
- RR-13 remains human-owned.
- `docs/repo-audit-20260521.md` remains excluded.
- No wording implies a new product feature, Dayu runtime, Host, Engine, tool loop, scene registry, or LLM writing.

No pytest or ruff run is required for P11-S1 documentation-only implementation unless the implementation unexpectedly touches source, tests, or config. If that happens, the implementation is out of scope and should stop for controller review.

## Review Handoff

Plan reviewers should challenge:

- whether the startup packet is sufficient for phaseflow resume;
- whether the history index preserves enough evidence to avoid scanning the archive on every resume;
- whether any proposed summarization drops artifact paths, commits, PR links, validation results, or residual owners;
- whether the archive strategy weakens `docs/implementation-control.md` as control truth;
- whether P11-S1 accidentally creates scope for product, runtime, or code changes.

## Acceptance Criteria

P11-S1 plan/review can be accepted when reviewers agree that:

1. The plan is documentation-only and respects all non-goals.
2. The control doc remains the implementation control truth.
3. Active-state recovery is explicit and short.
4. Historical phase logs are indexed.
5. Phase History Index anchors point to unique phase-prefixed archive headings.
6. `Startup Packet` plus `Active Gate Ledger` stay within the 80-line limit.
7. All gate evidence categories have preservation rules.
8. Design/control alignment rules are explicit.
9. Artifact existence checks are specified as a one-time implementation acceptance gate, not as routine resume work.
10. RR-13 and `docs/repo-audit-20260521.md` remain outside automated action.
