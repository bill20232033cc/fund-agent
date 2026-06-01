# MVP truth pivot and context compaction implementation review — MiMo

## Metadata

- Gate: `MVP truth pivot and context compaction gate`
- Role: Gateflow implementation reviewer
- Date: 2026-05-30
- Branch: `codex/local-reconciliation`
- Source plan: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
- Implementation evidence: `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`
- Changed files reviewed: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## Verdict

**PASS_WITH_NON_BLOCKING**

## Review Summary

Implementation correctly executes the plan. All control-truth, design-truth, and startup-packet surfaces have been pivoted from release-maintenance to MVP fund analysis report generation phase. Route C is correctly recorded as accepted future design, not current implementation. Deterministic `analyze/checklist` mainline is preserved. No out-of-scope changes detected.

## Findings

### F1 — LOW: "no commit/push/PR" wording conflicts with Gateflow local accepted checkpoint rule

**Location**: `docs/implementation-control.md` line 98 (Recent Active Gate Ledger)

**Current text**:
> Stop after evidence and report; no commit/push/PR

**Problem**: `AGENTS.md` line 55 defines that `standard` gates require "local accepted commit" as part of the gateflow checkpoint cycle. While this gate is classified `heavy` (which does not explicitly list "local accepted commit" in its description), the gateflow system's general convention is that each completed gate slice produces a local accepted checkpoint commit before reviews. The blanket "no commit/push/PR" prohibition conflicts with this convention — it blocks even local gateflow checkpoint commits, which are a core part of the gateflow evidence chain.

**Severity**: LOW (not blocking — the gate is docs-only and the implementation evidence artifact already captures the state; a local checkpoint commit can be made after review acceptance)

**Recommendation**: Change to:

> Stop after evidence and report; no push/PR/promotion; local gateflow checkpoint allowed

This preserves the intent (no external side-effects) while aligning with gateflow's local checkpoint convention.

### F2 — PASS: Current phase correctly pivoted

- `docs/implementation-control.md` header: current phase = `MVP fund analysis report generation phase` ✅
- `docs/implementation-control.md` header: next entry = exactly `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` ✅
- `docs/current-startup-packet.md` mirrors the same phase and next entry ✅
- Old release-maintenance phase no longer appears as current phase ✅

### F3 — PASS: Route C correctly recorded as accepted future design

- `docs/design.md` §5.4.1: Route C is explicitly labeled "已接受的未来设计" and states it is not current code fact ✅
- `docs/design.md`: Lists Gate 1-5 with scope and boundary constraints ✅
- `docs/design.md`: States Gate 1 names (`facet_recognizer`, `ChapterFactProvider`, `FundToolService`) are future candidate names, not current code types ✅
- `docs/implementation-control.md`: Route C future route table present with Gates 1-5 ✅
- `docs/current-startup-packet.md`: Route C section explicitly states "accepted future design" and "not current implementation" ✅

### F4 — PASS: Deterministic current implementation preserved

- `docs/implementation-control.md` Current Truth Guardrails: deterministic `fund-analysis analyze/checklist` ✅
- `docs/implementation-control.md`: UI -> Service -> `fund_agent/fund` transition path ✅
- `docs/current-startup-packet.md` §3: Lists all current implementation facts including no LLM writing, no Host/Agent/dayu runtime ✅
- `docs/design.md`: Existing deterministic renderer, programmatic audit, FQ0-FQ6 quality gate unchanged ✅

### F5 — PASS: Golden/promotion/QDII/FOF/110020/fixture correctly preserved as residuals

- `docs/implementation-control.md` Open Residuals: golden/strict correctness/fixture promotion = "Residual only for MVP report generation; no promotion allowed without a separate accepted future gate" ✅
- `004393`, `004194`, `006597`: "not promotion-prep-ready; fixture_state=absent; promotion_allowed=false" ✅
- QDII/FOF/`110020`/`017641`: "Deferred from minimum v1 and not ready for full v1" ✅
- `docs/current-startup-packet.md` §6: Same residual disposition ✅
- None of these are described as "ready" ✅

### F6 — PASS: Release-maintenance long ledger compressed

- `docs/implementation-control.md`: Historical Evidence Index links to 4 archive/review files ✅
- Long ledgers no longer embedded in active control surface ✅
- `docs/implementation-control.md` explicitly states: "historical release-maintenance 长账本只作为证据链，不再作为当前 phase 或 next entry" ✅
- `docs/current-startup-packet.md`: No release-maintenance ledger content; only residual references ✅

### F7 — PASS: Startup packet is compact and recoverable

- `docs/current-startup-packet.md`: 125 lines (target was 100-150 lines) ✅
- Contains all required sections: read order, current mainline, implementation facts, Route C, boundary guardrails, residuals, prohibited actions, resume checklist, key artifact links ✅
- Sufficiently short to work as a phaseflow startup entry ✅
- Control truth and design truth pointers are correct ✅

### F8 — PASS: No out-of-scope changes

- Only `docs/design.md` and `docs/implementation-control.md` are tracked changes ✅
- Only `docs/current-startup-packet.md` and `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` are new untracked files ✅
- No changes to: `AGENTS.md`, templates, runtime code, schema, score, snapshot, quality gate, golden fixtures, golden answers, manifests, promotion state ✅
- No unrelated untracked files modified, staged, or referenced ✅

### F9 — PASS: Design/control alignment

- `docs/design.md` version bumped to v2.3 with correct change summary ✅
- Section numbering preserved (5.4.1 inserted, old 5.4.1→5.4.2, 5.4.2→5.4.3, 5.4.3→5.4.4) ✅
- `docs/implementation-control.md` Design/Control Alignment Rules section present and consistent ✅
- Four-layer boundary UI -> Service -> Host -> Agent preserved ✅
- Host/Agent/dayu correctly deferred to Gate 5 ✅

## Residual Actions

| Action | Owner |
|---|---|
| Fix F1 wording: change "no commit/push/PR" to "no push/PR/promotion; local gateflow checkpoint allowed" in implementation-control.md Recent Active Gate Ledger | Next controller step or Gate 1 owner |
| Continue to Gate 1: `facet_recognizer` + `ChapterFactProvider` / `FundToolService` contract gate | MVP Gate 1 owner |
