# MVP truth pivot and context compaction implementation evidence

## Metadata

- Gate: `MVP truth pivot and context compaction gate`
- Role: implementation specialist, not controller
- Date: 2026-05-30
- Branch: `codex/local-reconciliation`
- Accepted plan commit: `70184d3`
- Source plan: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
- Plan reviews: `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md`

## Scope

Allowed files for this implementation slice:

- `docs/implementation-control.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`

No runtime, schema, score, snapshot, quality gate, golden fixture, golden answer, manifest, test, template, `AGENTS.md`, commit, push, PR, promotion or cleanup action was performed.

## Changed Files

| File | Change |
|---|---|
| `docs/implementation-control.md` | Replaced the release-maintenance-heavy control surface with a compact MVP control plane. |
| `docs/design.md` | Added `已接受的未来设计：MVP LLM report generation route` and clarified Route C future-only boundaries. |
| `docs/current-startup-packet.md` | Created a short phaseflow startup packet; line count after implementation: 125 lines. |
| `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` | Created this implementation evidence artifact. |

## Before / After Summary

| Area | Before | After |
|---|---|---|
| Control phase | `release maintenance` / overnight release-maintenance closeout surface | `MVP fund analysis report generation phase` |
| Current gate | Release-maintenance roadmap and strict correctness follow-up context dominated the startup surface | `MVP truth pivot and context compaction gate` |
| Next entry | `006597 same-fund unavailable field review / extractor projection gate...` | Exactly `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` |
| Release-maintenance artifacts | Long accepted-artifact list and long active ledger in the control doc | Historical Evidence Index plus roadmap/overnight closeout summary links only |
| Design truth | Existing future chapter-writing loop, but no Route C gate sequence | Route C recorded as accepted future route with Gates 1-5 |
| Startup entry | No `docs/current-startup-packet.md` file | Created compact startup packet for future phaseflow resume |

## Route C Future-Only Evidence

- `docs/design.md` states Route C is an accepted future route and explicitly says it is not current code fact.
- `docs/design.md` states current implementation remains deterministic `fund-analysis analyze/checklist`.
- `docs/design.md` states no LLM chapter writing, LLM audit, write-audit-repair loop, chapter orchestrator, final LLM assembler, CLI `--use-llm`, Host scheduling, Agent runner/tool loop or dayu runtime is implemented.
- `docs/design.md` states `facet_recognizer`, `ChapterFactProvider` and `FundToolService` are Route C Gate 1 future candidate names, not current code types, and do not replace current `FundDataExtractor` / `StructuredFundDataBundle`.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` repeat that Route C is future-only and Gate 1 is the next entry.

## Current Deterministic Implementation Evidence

- `docs/implementation-control.md` keeps current implementation as deterministic `fund-analysis analyze/checklist`.
- `docs/current-startup-packet.md` records the current path as UI -> Service -> `fund_agent/fund`.
- `docs/design.md` keeps the existing deterministic renderer, programmatic audit and FQ0-FQ6 quality gate as current behavior.

## Residual Evidence

- Golden / strict correctness / fixture promotion are now residuals for MVP report generation, not blockers for Route C Gate 1.
- `004393`, `004194` and `006597` remain not promotion-prep-ready with `fixture_state=absent` and `promotion_allowed=false`.
- QDII / FOF / `110020` / `017641` remain deferred and not full-v1 ready.
- Release-maintenance long ledger is preserved by `docs/archive/implementation-control-history-20260525.md`, `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`, `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` and `docs/reviews/overnight-release-maintenance-closeout-20260529.md`.

## Host / Agent / Dayu Evidence

- `docs/design.md` and `docs/implementation-control.md` preserve UI -> Service -> Host -> Agent.
- Current production path remains UI -> Service -> `fund_agent/fund`.
- Future Host must use `dayu.host`.
- Future Agent engine/tool loop/runner/ToolRegistry/ToolTrace must use `dayu.engine`.
- Host/Agent/dayu runtime integration is deferred to Route C Gate 5.

## Validation

Validation commands were run after the docs-only implementation.

| Command | Result |
|---|---|
| `git diff --check` | PASS; no whitespace errors reported. |
| `git diff --name-only` | PASS for tracked diff range; output only `docs/design.md` and `docs/implementation-control.md`. New docs are untracked, so the scoped status command below is the full allowed-file range check. |
| `git status --short -- docs/implementation-control.md docs/design.md docs/current-startup-packet.md docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` | PASS; output only `M docs/design.md`, `M docs/implementation-control.md`, `?? docs/current-startup-packet.md`, `?? docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`. |
| `ls docs/implementation-control.md docs/design.md docs/current-startup-packet.md docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md docs/reviews/overnight-release-maintenance-closeout-20260529.md` | PASS; all modified and referenced docs exist. |

Full `git status --short` still shows unrelated pre-existing untracked files, including `--help`, older release-maintenance follow-up artifacts, `docs/tmux-agent-memory-store.md` and `reviews/`. They were not modified, deleted, staged or referenced as accepted evidence for this gate.

Docs-only rationale for not running full `ruff` / `pytest`: this slice changed only Markdown control/design/evidence files. It did not modify Python runtime code, tests, schema, score, snapshots, quality gate semantics, golden fixtures, golden answers or manifests.

## Residual Risks / Owners

| Residual | Owner / next gate |
|---|---|
| Gate 1 public contract naming and concrete API shape | `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` |
| Golden / strict correctness / fixture promotion | Future strict golden / fixture promotion gate |
| QDII / FOF / `110020` / `017641` coverage | Future QDII / FOF / index evidence policy gates |
| Host/Agent/dayu runtime integration | Route C Gate 5 architecture gate |
| Current deterministic renderer quality | Route C Gates 2-4; no change in this docs-only slice |

## Stop Conditions Check

No need to modify runtime, golden, quality, template or `AGENTS.md` was found. No truth conflict required stopping or crossing scope boundaries.

## Review Fix Follow-up

- Review finding handled: MiMo/GLM F1 LOW wording issue on the Recent Active Gate Ledger stop action.
- Fix: `docs/implementation-control.md` now says implementation should stop after evidence/report with no push/PR/promotion, while allowing a local gateflow checkpoint commit after controller acceptance.
- Scope: docs-only follow-up; no runtime, schema, score, snapshot, quality, golden, fixture, manifest, test, template, `AGENTS.md`, commit, push, PR or promotion action.

### Follow-up Validation

| Command | Result |
|---|---|
| `git diff --check` | PASS; no whitespace errors reported. |
| `git diff --name-only` | PASS for the overall assigned task diff; output remains `docs/design.md` and `docs/implementation-control.md`. `docs/design.md` is a pre-existing diff from the docs-only slice, not modified by this follow-up. |
| `git status --short -- docs/implementation-control.md docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` | PASS for follow-up scope; output only `M docs/implementation-control.md` and `?? docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`. |
| `ls docs/implementation-control.md docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` | PASS; both follow-up files exist. |
