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
| Current gate | `MVP Gate 4 Slice 4B: Service analyze_with_llm` |
| Current gate classification | `heavy` |
| Current gate status | `accepted locally` |
| Next entry point | `MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate` |
| Control truth | `docs/implementation-control.md` |
| Design truth | `docs/design.md` |
| Accepted plan commit | `beb6891` |

The next owner should start from Gate 4 Slice 4C CLI opt-in. Release-maintenance and golden-promotion blockers are residuals for later gates, not the active mainline.

## 3. Current Implementation Facts

- Current report generation is deterministic `fund-analysis analyze`.
- Current checklist generation is deterministic `fund-analysis checklist`.
- Current path is UI -> Service -> `fund_agent/fund`.
- Service orchestrates the current use case and calls Fund public capabilities directly as a transition path.
- Fund owns the Agent-layer domain rules: fund-type recognition, annual-report facts, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, audit rules and evidence anchors.
- Current report rendering uses the 8-chapter deterministic template.
- Current audit is programmatic and deterministic.
- Current FQ0-FQ6 quality gate remains unchanged.
- Fund now has a Gate 1 typed projection capability: `project_chapter_facts()` / `ChapterFactProvider.project()` maps an in-memory `StructuredFundDataBundle` to `chapter_fact_projection.v1`.
- Gate 1 typed projection is Fund-layer only: it consumes existing bundle data, CHAPTER_CONTRACT, preferred_lens and ITEM_RULE truth APIs; it does not read annual reports, repositories, PDF/cache/source helpers, parsers, LLM, Service, Host or dayu.
- Facet assertion remains fail-closed: exact `facets` is empty unless structured evidence exists; compatible labels may appear only as `non_asserted_facets`.
- Fund now has Gate 2 single-chapter writer/auditor primitives: `chapter_writer.py` and `chapter_auditor.py`.
- Gate 2 writer/auditor only consume Gate 1 chapter facts and explicit fake/test or injected LLM clients; production code has no provider SDK, env/config loading, repository/PDF/source access, Service orchestration, Host, dayu or CLI integration.
- Gate 2 freezes fail-closed contracts for anchor/missing markers, LLM audit line parsing, `prompt_only`, `llm_unavailable`, `must_not_cover`, L1 numerical closure, `non_asserted_facets`, chapter 5 cross-period gaps, E2 deferral and `repair_hint` aggregation.
- Service now has Gate 3 `ChapterOrchestrator` / `orchestrate_chapters()` as `chapter_orchestrator.v1`.
- Gate 3 consumes only explicit `StructuredFundDataBundle` or `ChapterFactProjection`, explicit writer/auditor LLM Protocol clients and optional `ChapterFactProvider`; it runs write-audit-repair policy for template chapters 1-6 and outputs accepted chapter conclusions for Gate 4.
- Gate 3 does not generate chapters 0 or 7, does not construct production LLM providers, does not read repositories/PDF/cache/source helpers/parsers, and does not integrate Host/Agent/dayu.
- Service now has Gate 4 Slice 4A `FinalChapterAssembler` / `assemble_final_chapters()` as `final_chapter_assembler.v1`.
- Slice 4A deterministic assembly generates chapter 7 from existing `FinalJudgmentDecision`, then chapter 0 from accepted conclusions plus a Gate 4-local typed chapter 7 summary; render order is `0 -> 1-6 -> 7`.
- Service now has Gate 4 Slice 4B `FundAnalysisService.analyze_with_llm()` and `FundLLMAnalysisResult`: it reuses `_run_analysis_core()`, calls Gate 3 with explicit injected LLM clients, always calls Slice 4A final assembly, and does not fall back to deterministic markdown.
- Slice 4B does not implement CLI `--use-llm`, production LLM provider construction, chapter 0/7 LLM polish/audit, or Evidence Confirm.
- There is no CLI `--use-llm`.
- There is no Host/Agent/dayu runtime in the production path.

## 4. Route C Accepted Future Route

Route C is the accepted MVP LLM report generation route. Gates 1-3 and Gate 4 Slices 4A/4B are accepted local code facts; remaining Gate 4 slices and Gate 5 remain future design.

| Gate | Status / scope |
|---|---|
| Gate 1 | `ChapterFactProvider` typed projection is accepted locally as Fund-layer code fact; `facet_recognizer` and full `FundToolService` remain future candidates |
| Gate 2 | `chapter_writer` + `chapter_auditor` accepted locally as Fund-layer single-chapter primitives |
| Gate 3 | `chapter_orchestrator` accepted locally as Service-owned write-audit-repair façade for chapters 1-6 |
| Gate 4 | Slice 4A `final_chapter_assembler` and Slice 4B Service `analyze_with_llm` accepted locally; next Slice 4C CLI `--use-llm`; Slice 4D provider remains separate |
| Gate 5 | Optional `dayu.host` / `dayu.engine` integration |

Gate 4 Slice 4B only accepted the Service LLM analyze use case. It did not implement CLI `--use-llm`, production LLM provider construction, Host/Agent/dayu integration or full FundToolService.

## 5. Boundary Guardrails

- Target architecture remains UI -> Service -> Host -> Agent.
- UI handles interaction, rendering and display only.
- Service handles use-case orchestration, scene/prompt/ExecutionContract semantics, report strategy and the current Gate 3 write-audit-repair facade.
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

- Golden / strict correctness / fixture promotion are residuals and do not block the next MVP Gate 4 Slice 4C work.
- `004393`, `004194` and `006597` are not promotion-prep-ready.
- `004393`, `004194` and `006597` keep `fixture_state=absent`.
- All promotion states remain `promotion_allowed=false`.
- QDII, FOF, `110020` and `017641` remain deferred from minimum v1 and not ready for full v1.
- Release-maintenance long ledger is preserved by links only.
- Host/Agent/dayu integration is deferred to Route C Gate 5.
- Current deterministic renderer quality remains production behavior until the explicit `--use-llm` gate.
- Unrelated untracked workspace files are not accepted evidence unless a later controller gate accepts them.

## 7. Prohibited Actions

- Do not modify runtime code outside the active MVP gate scope.
- Do not modify schema, score, snapshot, quality gate, final judgment, golden fixtures, golden answers, manifests or promotion state.
- Do not modify `AGENTS.md`.
- Do not modify `docs/fund-analysis-template-draft.md`.
- Do not create `fund_agent/host` or `fund_agent/agent` before an explicit gate.
- Do not add `dayu.host` or `dayu.engine` dependencies before Route C Gate 5 or another explicit architecture gate.
- Do not run promotion, fixture promotion, strict correctness reruns, snapshot refreshes or release-readiness workflows for this MVP gate sequence.
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
- Gate 1 plan: `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`
- Gate 1 plan review MiMo: `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-mimo-20260530.md`
- Gate 1 plan review GLM: `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-glm-20260530.md`
- Gate 1 implementation evidence: `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md`
- Gate 1 implementation review MiMo: `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-mimo-20260530.md`
- Gate 1 implementation review GLM: `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-glm-20260530.md`
- Gate 1 controller judgment: `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md`
- Gate 2 plan: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`
- Gate 2 plan decision: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md`
- Gate 2 implementation evidence: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md`
- Gate 2 implementation review MiMo: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-mimo-20260530.md`
- Gate 2 implementation review DS: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-ds-20260530.md`
- Gate 2 implementation re-review MiMo: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-mimo-20260530.md`
- Gate 2 implementation re-review DS: `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-ds-20260530.md`
- Gate 2 controller judgment: `docs/reviews/mvp-gate2-chapter-writer-auditor-controller-judgment-20260530.md`
- Gate 3 plan: `docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`
- Gate 3 plan decision: `docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md`
- Gate 3 implementation evidence: `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md`
- Gate 3 implementation reviews: `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-ds-20260530.md`
- Gate 3 review fix evidence: `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-evidence-20260530.md`
- Gate 3 review fix re-reviews: `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-ds-20260530.md`
- Gate 3 controller judgment: `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md`
- Gate 4 plan: `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- Gate 4 plan decision: `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- Gate 4 Slice 4A implementation evidence: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md`
- Gate 4 Slice 4A implementation reviews: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-ds-20260530.md`
- Gate 4 Slice 4A review fix evidence: `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md`
- Gate 4 Slice 4A review fix re-reviews: `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-ds-20260530.md`
- Gate 4 Slice 4A controller judgment: `docs/reviews/mvp-gate4-final-assembler-slice4a-controller-judgment-20260530.md`
- Gate 4 Slice 4B implementation evidence: `docs/reviews/mvp-gate4-llm-service-implementation-evidence-20260530.md`
- Gate 4 Slice 4B implementation reviews: `docs/reviews/mvp-gate4-llm-service-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-llm-service-implementation-review-glm-20260530.md`
- Gate 4 Slice 4B controller judgment: `docs/reviews/mvp-gate4-llm-service-controller-judgment-20260530.md`
- Release-maintenance roadmap summary: `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- Overnight release-maintenance closeout: `docs/reviews/overnight-release-maintenance-closeout-20260529.md`
- Historical control snapshot: `docs/archive/implementation-control-history-20260525.md`
- Release-maintenance historical ledger: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
