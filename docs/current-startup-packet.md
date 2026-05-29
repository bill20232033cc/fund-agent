# Current Startup Packet

Purpose: this is the short resume entry for the MVP fund analysis report generation phase. It is a control packet, not a historical ledger.

## 1. Read Order

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/implementation-control.md`
4. `docs/fund-analysis-template-draft.md`

Use `docs/reviews/` and `docs/archive/` only as evidence chain. They do not override the current control packet, `AGENTS.md`, or the current/future status labels in `docs/design.md`.

## 2. Current Mainline

| Field | State |
|---|---|
| Current phase | `MVP fund analysis report generation phase` |
| Current gate | `MVP truth pivot and context compaction gate` |
| Current gate classification | `heavy` |
| Next entry point | `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` |
| Control truth | `docs/implementation-control.md` |
| Design truth | `docs/design.md` |
| Accepted plan commit | `70184d3` |

The next owner should start from Gate 1 contract work. Release-maintenance and golden-promotion blockers are residuals for later gates, not the active mainline.

## 3. Current Implementation Facts

- Current report generation is deterministic `fund-analysis analyze`.
- Current checklist generation is deterministic `fund-analysis checklist`.
- Current path is UI -> Service -> `fund_agent/fund`.
- Service orchestrates the current use case and calls Fund public capabilities directly as a transition path.
- Fund owns the Agent-layer domain rules: fund-type recognition, annual-report facts, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, audit rules and evidence anchors.
- Current report rendering uses the 8-chapter deterministic template.
- Current audit is programmatic and deterministic.
- Current FQ0-FQ6 quality gate remains unchanged.
- There is no LLM chapter writing.
- There is no LLM audit.
- There is no write-audit-repair loop.
- There is no chapter orchestrator.
- There is no final LLM assembler.
- There is no CLI `--use-llm`.
- There is no Host/Agent/dayu runtime in the production path.

## 4. Route C Accepted Future Route

Route C is accepted future design for MVP LLM report generation. It is not current implementation.

| Gate | Future scope |
|---|---|
| Gate 1 | `facet_recognizer` + `ChapterFactProvider` / `FundToolService` contract and implementation |
| Gate 2 | `chapter_writer` + `chapter_auditor` |
| Gate 3 | `chapter_orchestrator` with Service-owned write-audit-repair policy |
| Gate 4 | `final_chapter_assembler`, chapter 0 assembly and opt-in CLI `--use-llm` |
| Gate 5 | Optional `dayu.host` / `dayu.engine` integration |

Gate 1 names are future candidate names. They are not current code types until a later accepted implementation gate creates them.

## 5. Boundary Guardrails

- Target architecture remains UI -> Service -> Host -> Agent.
- UI handles interaction, rendering and display only.
- Service handles use-case orchestration, scene/prompt/ExecutionContract semantics, report strategy and future write-audit-repair policy.
- Host handles session/run lifecycle, concurrency, timeout, cancel, resume, memory, reply outbox and event delivery.
- Future Host must use `dayu.host`.
- Agent handles execution, tool loop, runner, ToolRegistry, ToolTrace, context budget, tool execution and Fund domain capabilities.
- Future Agent engine/tool loop/runner/ToolRegistry/ToolTrace must use `dayu.engine`.
- `fund_agent/fund` is the current Agent-layer Fund domain package.
- Production annual report access must go through `FundDocumentRepository`.
- Service, UI, Host, renderer and quality gate must not call PDF cache, download helpers or concrete annual-report sources directly.
- All explicit parameters must be typed and declared.
- Do not pass business parameters through `extra_payload`.
- Fallback from annual-report sources is allowed only for `not_found` and `unavailable`.
- `schema_drift`, `identity_mismatch` and `integrity_error` must fail closed.

## 6. Current Residuals

- Golden / strict correctness / fixture promotion are residuals and do not block MVP report generation Gate 1.
- `004393`, `004194` and `006597` are not promotion-prep-ready.
- `004393`, `004194` and `006597` keep `fixture_state=absent`.
- All promotion states remain `promotion_allowed=false`.
- QDII, FOF, `110020` and `017641` remain deferred from minimum v1 and not ready for full v1.
- Release-maintenance long ledger is preserved by links only.
- Host/Agent/dayu integration is deferred to Route C Gate 5.
- Current deterministic renderer quality remains production behavior until the explicit `--use-llm` gate.
- Unrelated untracked workspace files are not accepted evidence unless a later controller gate accepts them.

## 7. Prohibited Actions

- Do not modify runtime code in this docs-only gate.
- Do not modify schema, score, snapshot, quality gate, final judgment, golden fixtures, golden answers, manifests or promotion state.
- Do not modify `AGENTS.md`.
- Do not modify `docs/fund-analysis-template-draft.md`.
- Do not create `fund_agent/host` or `fund_agent/agent` before an explicit gate.
- Do not add `dayu.host` or `dayu.engine` dependencies before Route C Gate 5 or another explicit architecture gate.
- Do not run promotion, fixture promotion, strict correctness reruns, snapshot refreshes or release-readiness workflows for this pivot gate.
- Do not commit, push or create PR unless a later controller step explicitly authorizes it.
- Do not delete or clean unrelated untracked files.

## 8. Resume Checklist

1. Confirm branch with `git branch --show-current`.
2. Confirm worktree scope with `git status --short`.
3. Confirm role: controller or specialist.
4. Confirm current gate and next entry in `docs/implementation-control.md`.
5. Read the accepted plan and reviews for the active gate.
6. Confirm allowed files before editing.
7. Classify the next gate per `AGENTS.md`; choose the heavier classification when uncertain.
8. Check that Route C text stays future-only.
9. Check that current deterministic `analyze/checklist` remains current implementation.
10. Check that Host/Agent/dayu stays deferred unless the active gate explicitly covers it.
11. Check that golden / strict correctness / QDII / FOF / `110020` / fixture promotion stay residuals unless the active gate explicitly covers them.
12. Record validation commands and results in the relevant evidence artifact.

## 9. Key Artifact Links

- Pivot plan: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
- Pivot plan review MiMo: `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md`
- Pivot plan review GLM: `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md`
- Pivot implementation evidence: `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`
- Release-maintenance roadmap summary: `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- Overnight release-maintenance closeout: `docs/reviews/overnight-release-maintenance-closeout-20260529.md`
- Historical control snapshot: `docs/archive/implementation-control-history-20260525.md`
- Release-maintenance historical ledger: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
