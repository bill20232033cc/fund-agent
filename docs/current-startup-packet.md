# Current Startup Packet

Purpose: this is the short resume entry for the MVP real LLM observability and chapter acceptance phase. It is a control packet, not a historical ledger.

## 1. Read Order

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/implementation-control.md`
4. `docs/fund-analysis-template-draft.md`

Use `docs/reviews/` and `docs/archive/` only as evidence chain. They do not override the current control packet, `AGENTS.md`, or the current/future status labels in `docs/design.md`.

## 2. Current Mainline

| Field | State |
|---|---|
| Current phase | `MVP real LLM observability and chapter acceptance phase` |
| Current gate | `MVP real LLM chapter acceptance calibration gate` |
| Current gate classification | `heavy` |
| Current gate status | Plan checkpoint `a15dfcb`; DS/MiMo plan reviews PASS with no blocking findings; implementation not started |
| Next entry point | Dispatch Slice 1 evidence triage through `$init-agents`; no code changes until same-source evidence authorizes Slice 2 |
| Control truth | `docs/implementation-control.md` |
| Design truth | `docs/design.md` |
| Accepted plan commit | `beb6891` |
| Accepted provider factory commit | `26203d3` |
| Accepted CLI provider wiring commit | `ab0590a` |
| Accepted docs/control sync commit | `4d0c19f` |
| Accepted aggregate review commit | `7a3dab9` |
| Accepted closeout entrypoint commit | `b0e68e0` |
| Accepted incomplete artifact retention plan commit | `5f18715` |
| Accepted incomplete artifact retention implementation commit | `4f7903f` |
| Accepted LLM progress/timeout UX plan commit | `5dc865f` |
| Accepted LLM progress/timeout UX implementation commit | `d656816` |
| Accepted real LLM chapter acceptance calibration plan commit | `a15dfcb` |

The current phase goal is to make real LLM failures auditable, reproducible and iteratable before improving chapter accepted rate. Artifact retention is accepted locally: typed incomplete `fund-analysis analyze --use-llm` results keep stdout empty, exit `1`, and avoid deterministic fallback, while writing local ignored diagnostics under `reports/llm-runs/`. Those diagnostics include manifest, summary, per-chapter JSON, writer draft, repair draft, normalized auditor feedback, chapter matrix and first failed diagnostic with allowlist/redaction. Progress/timeout UX is also accepted locally: long-running `--use-llm` commands now have safe stderr-only progress, `--llm-progress/--no-llm-progress`, and Host generic `event_sink`, without changing stdout/fail-closed behavior. Chapter acceptance calibration plan is accepted; next step is Slice 1 evidence triage only: inspect retained artifacts, rerun real `006597 / 2024 --use-llm` smoke if provider credentials/network/cost allow, classify same-source root cause, and stop if provider runtime is the first blocker. Provider runtime budget calibration and score-loop entry remain future gates. Current `--use-llm` implementation remains `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`; default deterministic `analyze/checklist` still bypass Host. Service owns `FundLLMExecutionContract`, `FundLLMExecutionRequest`, runtime plan and provider clients; Host only receives generic operation/deadline/session fields and does not understand fund business semantics. Dayu is an architecture reference and capability source, not a production runtime dependency. Async Host runner, durable session/resume/memory/outbox and internalized Agent engine/tool-loop migration remain later gates. Gate C score-loop design is accepted as design-only and must not be treated as readiness/golden/quality-gate pass.

## 3. Current Implementation Facts

- Default report generation is deterministic `fund-analysis analyze`.
- Current checklist generation is deterministic `fund-analysis checklist`.
- Current deterministic path is `CLI -> Service -> fund_agent/fund`.
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
- CLI now exposes `fund-analysis analyze --use-llm` as an explicit opt-in provider-backed path. With complete typed env config, Service builds `FundLLMExecutionRequest` / `FundLLMExecutionContract`, runtime plan and Service-owned `openai_compatible` HTTP chat-completions writer/auditor clients over existing `httpx`; CLI gives Host only generic run parameters plus `runtime_plan.host_timeout_seconds`, and Host invokes Service `FundAnalysisService.analyze_with_llm_execution()`.
- Missing/invalid LLM config and provider construction fail before Service execution with exit code `1` and empty stdout. Provider runtime failures, writer/auditor blocked status, partial orchestration and incomplete final assembly also fail closed with exit code `1`; there is no deterministic fallback.
- Pytest coverage for the provider path uses fake env mappings, `httpx.MockTransport` and monkeypatch/test doubles; no live provider smoke or real API key is required.
- Gate A hardened the LLM writer/auditor path for real providers: writer requires fixed body sections and exact `required_output` markers, parser preserves `missing_required_structure`, `missing_required_output_marker`, `unknown_anchor`, `response_too_long` and `response_incomplete`, auditor parse failure remains blocked, regenerate receives typed `ChapterRepairContext`, and provider runtime exceptions classify to `llm_timeout`, `llm_rate_limited`, `llm_malformed_response` or `llm_network_error`.
- Provider runtime timeout hardening added typed `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` and `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`, timeout-only bounded retry, provider-safe diagnostics enriched by Service with chapter identity, and CLI incomplete-result first failed chapter summary.
- Prompt-contract calibration added code-level failure categories `llm_timeout` and `audit_rule_too_strict`, `ChapterRunResult.failure_category`, CLI `first_failed_category`, stricter auditor line protocol parsing, and shorter writer output-contract guidance while preserving fail-closed safety boundaries.
- Writer prompt contract diagnostic narrowing added safe `failure_subcategory`, `ChapterPromptContractDiagnostic` typed counters, CLI `first_failed_subcategory`, and `serialize_chapter_prompt_contract_diagnostics()` without storing prompt, draft, raw provider response, raw audit response, API key or Authorization header.
- Writer marker syntax repair replaced the missing-marker prompt guidance with an explicit contract block and kept parser / allowed missing reasons strict.
- Programmatic audit L1 calibration added safe `l1_numerical_closure` taxonomy and L1 repair guidance without relaxing `_audit_numerical_closure()` or anchor proximity; L1 unsafe cases remain fail-closed and candidate facet / forbidden phrase precedence stays higher.
- Provider runtime timeout follow-up added `serialize_chapter_runtime_diagnostics()`, provider-bound prompt/runtime cost scalar diagnostics, and CLI safe runtime summaries. It omits `message`, `model_name`, prompt, draft, raw provider response, raw audit response, API key and Authorization header from serialized evidence.
- Independent body chapter execution accepted locally: template chapters 1-6 now each run their own writer/auditor/repair attempts from the same `ChapterFactProjection`; prior body chapter failure no longer skips later body chapters; `dependency_missing` is reserved for a true writer dependency stop reason. CLI incomplete output now includes a safe all-chapter matrix; final assembly remains fail-closed and cannot turn a partial matrix into an accepted report.
- Latest prompt-cost/root-cause calibration rerun for `006597 / 2024 --use-llm`: CLI exit `1`, stdout empty, no deterministic fallback, `orchestration_status=partial`, `final_assembly_status=incomplete`; same-source Service diagnostic with `prompt_payload_mode=compact` has `generated_chapter_ids=[1,2,3,4,5,6]`, `skipped_chapter_ids=[]`, `accepted_chapter_ids=[]`, `report_markdown_present=false`. Primary blocker is `provider_runtime_timeout_small_prompt`: chapters 1-6 all fail writer timeout with approximate prompt tokens `2109`, `1590`, `2575`, `1274`, `2518`, `2110` under `60s x2` bounded writer budget. Chapter 2/6 former large prompt cost is reduced from approx `26086` / `29078` to `1590` / `2110`.
- Gate C score-loop design is accepted as design-only: it distinguishes `extraction_score`, `chapter_fact_score` and `chapter_generation_score`, routes provider runtime timeout as `not_scored` / `blocked_provider_runtime`, and remains separate from existing golden / fixtures / score / quality gate / readiness semantics.
- `--use-llm` now runs through local `HostRuntimeRunner` for run lifecycle, global deadline, cancel token, terminal run state, safe diagnostics and phase events; Host does not import Service/Fund and does not inspect fund code/year/type/chapter policy/ExecutionContract business fields; default deterministic analyze/checklist still bypass Host; no Agent tool-loop or dayu runtime is present.
- Provider runtime budget and prompt-cost diagnostics remain transitional provider-calibration evidence; Host run state now provides the MVP process-local lifecycle boundary but does not solve provider endpoint small-prompt timeouts.
- `MVP Service ExecutionContract boundary hardening gate` aggregate deepreview is accepted locally. Its accepted fixes enforce `QualityFailClosedPolicy` at the typed LLM execution boundary and keep `QualityGatePolicy` sourced from `execution_contract.py`; aggregate re-review found no blocking findings.
- `MVP incomplete LLM run artifact retention gate` is accepted locally. It adds Service-owned artifact serialization and CLI trigger wiring for typed incomplete `--use-llm` results; artifacts are local ignored diagnostics and do not change stdout, exit code, quality gate semantics, repair budget or deterministic fallback behavior.

## 4. Route C Accepted Future Route

Route C is the accepted MVP LLM report generation route. Gates 1-3 and Gate 4 Slices 4A/4B/4C/4D are accepted local code facts. Gate 5A `internalized Host runtime governance adapter` has an MVP process-local implementation; Gate 5B `internalized Agent engine/tool-loop migration` remains future design.

| Gate | Status / scope |
|---|---|
| Gate 1 | `ChapterFactProvider` typed projection is accepted locally as Fund-layer code fact; `facet_recognizer` and full `FundToolService` remain future candidates |
| Gate 2 | `chapter_writer` + `chapter_auditor` accepted locally as Fund-layer single-chapter primitives |
| Gate 3 | `chapter_orchestrator` accepted locally as Service-owned write-audit-repair façade for chapters 1-6 |
| Gate 4 | Slice 4A `final_chapter_assembler`, Slice 4B Service `analyze_with_llm`, Slice 4C CLI `--use-llm`, Slice 4D provider construction and Service-owned ExecutionContract / typed request boundary accepted locally |
| Gate 5A | internalized Host runtime governance adapter: MVP process-local implementation wraps `--use-llm`; Host is business-agnostic and only receives generic operation/deadline/session fields; async runner and durable session/resume/memory/reply outbox remain future Host scope |
| Gate 5B | internalized Agent engine/tool-loop migration: future Agent runner/tool-loop/ToolRegistry/ToolTrace work; not the minimal fix for current provider timeout |

Gate 4 Slice 4D accepted typed env config and Service-owned `openai_compatible` provider construction. The current Service ExecutionContract boundary adds `FundLLMExecutionRequest` / `FundLLMExecutionContract` ownership in Service and routes CLI `--use-llm` through `analyze_with_llm_execution()`. Provider runtime timeout hardening later added timeout-only bounded retry/backoff and safe diagnostics. The current route has local Host run governance for `--use-llm`; it still does not implement Agent/dayu integration, full FundToolService, live provider smoke acceptance, multi-model writer/auditor split, chapter 0/7 LLM polish or Evidence Confirm.

## 5. Boundary Guardrails

- Target architecture remains UI -> Service -> Host -> Agent.
- UI handles interaction, rendering and display only.
- Service handles use-case orchestration, scene/prompt/ExecutionContract semantics, report strategy and the current Gate 3 write-audit-repair facade.
- Host handles session/run lifecycle, concurrency, timeout, cancel, resume, memory, reply outbox and event delivery.
- Host runtime governance must stay internalized and must not directly depend on `dayu-agent` / `dayu.host` as production runtime.
- Host currently only receives generic operation/deadline/session fields; it must not inspect fund business semantics, Service ExecutionContract business fields, chapter policy or provider clients.
- Agent handles execution, tool loop, runner, ToolRegistry, ToolTrace, context budget, tool execution and Fund domain capabilities.
- Future Agent engine/tool loop/runner/ToolRegistry/ToolTrace migration must internalize Dayu Engine capabilities and must not directly depend on `dayu-agent` / `dayu.engine` as production runtime.
- `fund_agent/fund` is the current Agent-layer Fund domain package.
- Production annual report access must go through `FundDocumentRepository`.
- Service, UI, Host, renderer and quality gate must not call PDF cache, download helpers or concrete annual-report sources directly.
- All explicit parameters must be typed and declared.
- Do not pass business parameters through `extra_payload`.
- Fallback from annual-report sources is allowed only for `not_found` and `unavailable`.
- `schema_drift`, `identity_mismatch` and `integrity_error` must fail closed.

## 6. Current Residuals

- Golden / strict correctness / fixture promotion are residuals and do not block the next MVP Gate 4 Slice 4D planning work.
- `004393`, `004194` and `006597` are not promotion-prep-ready.
- `004393`, `004194` and `006597` keep `fixture_state=absent`.
- All promotion states remain `promotion_allowed=false`.
- QDII, FOF, `110020` and `017641` remain deferred from minimum v1 and not ready for full v1.
- Release-maintenance long ledger is preserved by links only.
- Internalized Host runtime governance adapter MVP process-local implementation is complete; async runner and durable Host capabilities remain future scope.
- Internalized Agent engine/tool-loop migration is deferred.
- Deterministic renderer remains the default production behavior; provider-backed LLM report generation is explicit `--use-llm` opt-in only.
- Live provider smoke acceptance, multi-model writer/auditor split, chapter 0/7 LLM polish and Evidence Confirm remain future residuals.
- Local real provider smoke for PR #21 remains blocked: current MiMo provider auth passes; provider timeout hardening, prompt-contract calibration, diagnostic narrowing, marker syntax repair, L1 calibration, provider runtime timeout follow-up, independent body execution and prompt-cost/root-cause calibration are accepted locally. Latest compact-mode rerun fails closed before complete chapters 0-7 with primary blocker `provider_runtime_timeout_small_prompt`; no deterministic fallback and no partial accepted report.
- Future score-loop implementation must first clarify `ChapterFactProjection` naming, its relationship to existing `extraction_score.py` / `extraction_score_service.py`, weights/value semantics, `not_scored_reason` enum, score CLI exit code, and candidate facet L2 source. It must not start before Gate B timeout is rerun or handled.
- LLM run progress and timeout UX is implemented and accepted locally; it adds only safe stderr progress/stage diagnostics and does not expose prompts, provider raw responses, API keys or Authorization headers.
- Chapter 2/3/6 acceptance calibration remains deferred until artifact evidence and progress UX are in place; it must not relax auditor rules or increase repair budget by default.
- Provider runtime budget calibration and `chapter_generation_score` entry remain future gates.
- Unrelated untracked workspace files are not accepted evidence unless a later controller gate accepts them.

## 7. Prohibited Actions

- Do not modify runtime code outside the active MVP gate scope.
- Do not modify schema, score, snapshot, quality gate, final judgment, golden fixtures, golden answers, manifests or promotion state.
- Do not modify `AGENTS.md` unless an explicit truth-source alignment gate authorizes it.
- Do not modify `docs/fund-analysis-template-draft.md`.
- Do not create `fund_agent/host` or `fund_agent/agent` before an explicit gate.
- Do not add `dayu-agent`, `dayu.host` or `dayu.engine` as production runtime dependencies.
- Do not copy or rewrite upstream Dayu code before an explicit license/compliance gate.
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
10. Check that internalized Host runtime governance is treated as the next MVP readiness prerequisite and internalized Agent engine/tool-loop remains deferred unless the active gate explicitly covers it.
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
- Gate 4 Slice 4C implementation evidence: `docs/reviews/mvp-gate4-cli-use-llm-implementation-evidence-20260530.md`
- Gate 4 Slice 4C implementation reviews: `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-glm-20260530.md`
- Gate 4 Slice 4C controller judgment: `docs/reviews/mvp-gate4-cli-use-llm-controller-judgment-20260530.md`
- Gate 4 Slice 4D provider plan: `docs/reviews/mvp-gate4-provider-construction-plan-20260530.md`
- Gate 4 Slice 4D provider plan reviews: `docs/reviews/mvp-gate4-provider-construction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-plan-review-glm-20260530.md`
- Gate 4 Slice 4D provider plan decision: `docs/reviews/mvp-gate4-provider-construction-plan-decision-20260530.md`
- MVP local acceptance / real provider smoke plan: `docs/reviews/mvp-local-acceptance-real-provider-smoke-plan-20260530.md`
- MVP local acceptance / real provider smoke evidence: `docs/reviews/mvp-local-acceptance-real-provider-smoke-evidence-20260530.md`
- MVP local acceptance / real provider smoke review: `docs/reviews/mvp-local-acceptance-real-provider-smoke-review-zeno-20260530.md`
- MVP local acceptance / real provider smoke controller judgment: `docs/reviews/mvp-local-acceptance-real-provider-smoke-controller-judgment-20260530.md`
- MVP local acceptance / real provider smoke rerun evidence: `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-evidence-20260530.md`
- MVP local acceptance / real provider smoke rerun review: `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-review-lovelace-20260530.md`
- MVP local acceptance / real provider smoke rerun controller judgment: `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-controller-judgment-20260530.md`
- MVP real provider audit-block diagnostic: `docs/reviews/mvp-real-provider-audit-block-diagnostic-20260530.md`
- MVP real provider audit-block diagnostic controller judgment: `docs/reviews/mvp-real-provider-audit-block-diagnostic-controller-judgment-20260530.md`
- MVP provider auth/config verification: `docs/reviews/mvp-provider-auth-config-verification-20260531.md`
- MVP provider auth/config verification controller judgment: `docs/reviews/mvp-provider-auth-config-verification-controller-judgment-20260531.md`
- MVP writer/auditor contract hardening controller judgment: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`
- MVP real provider smoke acceptance controller judgment: `docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`
- MVP real provider independent body matrix evidence: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md`
- MVP real provider independent body matrix reviews: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-glm-20260531.md`
- MVP real provider independent body matrix controller judgment: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-controller-judgment-20260531.md`
- MVP chapter generation score-loop design controller judgment: `docs/reviews/mvp-chapter-generation-score-loop-design-controller-judgment-20260531.md`
- MVP real-provider stabilization and score-loop phase judgment: `docs/reviews/mvp-real-provider-stabilization-score-loop-phase-controller-judgment-20260531.md`
- MVP provider runtime timeout hardening plan: `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`
- MVP provider runtime timeout hardening implementation evidence: `docs/reviews/mvp-provider-runtime-timeout-hardening-implementation-evidence-20260531.md`
- MVP provider runtime timeout hardening code reviews: `docs/reviews/mvp-provider-runtime-timeout-hardening-code-review-glm-20260531.md`; `docs/reviews/mvp-provider-runtime-timeout-hardening-code-rereview-mimo-20260531.md`
- MVP provider runtime timeout hardening controller judgment: `docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md`
- MVP prompt-contract calibration plan: `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`
- MVP prompt-contract calibration implementation evidence: `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`
- MVP prompt-contract calibration code reviews: `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-glm-20260531.md`
- MVP prompt-contract calibration controller judgment: `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-controller-judgment-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration plan: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration plan reviews: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-ds-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration implementation evidence: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-implementation-evidence-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration code reviews: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-ds-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration validation evidence: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-validation-evidence-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration deep review: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-deepreview-20260531.md`
- MVP provider runtime budget and prompt-cost root-cause calibration controller judgment: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-controller-judgment-20260531.md`
- Release-maintenance roadmap summary: `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- Overnight release-maintenance closeout: `docs/reviews/overnight-release-maintenance-closeout-20260529.md`
- Historical control snapshot: `docs/archive/implementation-control-history-20260525.md`
- Release-maintenance historical ledger: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
