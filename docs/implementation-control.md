# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.3
> **日期**: 2026-05-30
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`
> **短启动入口**: `docs/current-startup-packet.md`
> **当前状态**: MVP fund analysis report generation phase；当前 gate 为 `MVP Gate 4 draft PR gate`，用户已授权外部 draft PR 操作；PR #21 已更新为 draft，当前分支正在完成 `origin/main` merge-conflict reconciliation 和本地验证后再推送修复。

---

## Startup Packet

本文件只保留当前控制面。详细恢复入口见 `docs/current-startup-packet.md`；历史 release-maintenance 长账本只作为证据链，不再作为当前 phase 或 next entry。

### Current Truth Guardrails

- `AGENTS.md` 是最高优先级执行规则真源；若与本文档或 `docs/design.md` 冲突，先调整方案/实现，再回写文档。
- 当前 phase 是 `MVP fund analysis report generation phase`；当前 gate 是 `MVP Gate 4 draft PR gate`，分类为 `heavy`，状态为 user-authorized draft PR gate in progress。
- 当前默认实现仍以确定性 `fund-analysis analyze/checklist` 为生产主链路：结构化抽取、确定性分析、模板渲染、程序审计和 FQ0-FQ6 quality gate。
- Gate 1 已新增 Fund 层 typed projection：`project_chapter_facts()` / `ChapterFactProvider.project()` 将内存中的 `StructuredFundDataBundle` 投影为 `chapter_fact_projection.v1`。
- Gate 1 typed projection 只消费现有 bundle、CHAPTER_CONTRACT、preferred_lens 和 ITEM_RULE truth APIs；不读取仓库、PDF/cache/source helper、parser、LLM、Service、Host 或 dayu。
- facet 断言保持 fail-closed：无结构化精确证据时 `facets=()`；兼容标签只进入 `non_asserted_facets`，不得驱动 ITEM_RULE。
- Gate 2 已新增 Fund 层单章 writer/auditor primitives：`chapter_writer.py` 和 `chapter_auditor.py`。
- Gate 2 writer/auditor 只消费 Gate 1 chapter facts、writer draft 和显式注入的 LLM Protocol client；生产代码不读取仓库、PDF/cache/source helper、parser、真实 provider SDK、env/config、Service、Host 或 dayu。
- Gate 2 冻结了 anchor/missing marker、LLM audit 行协议、`prompt_only`、`llm_unavailable`、must_not_cover、L1 数值闭合、`non_asserted_facets`、第 5 章跨期缺口、E2 deferred 和 `repair_hint` 聚合等 fail-closed 合约。
- Gate 3 已新增 Service 层 `ChapterOrchestrator` / `orchestrate_chapters()`，作为 `chapter_orchestrator.v1` write-audit-repair façade：只消费显式 `StructuredFundDataBundle` 或 `ChapterFactProjection`、显式 writer/auditor LLM Protocol client 和可选 `ChapterFactProvider`，只生成模板第 1-6 章 accepted conclusions。
- Gate 3 不生成第 0/7 章，不构造生产 LLM provider，不读取仓库、PDF/cache/source helper、parser，不接入 Host/Agent/dayu。
- Gate 4 Slice 4A 已新增 Service 层 `FinalChapterAssembler` / `assemble_final_chapters()`，作为 `final_chapter_assembler.v1` deterministic final assembly：用现有 `FinalJudgmentDecision` 生成第 7 章，再用 accepted conclusions 与 Gate 4-local typed chapter 7 summary 生成第 0 章，最终渲染顺序为 `0 -> 1-6 -> 7`。
- Gate 4 Slice 4B 已新增 Service 层 `FundAnalysisService.analyze_with_llm()` / `FundLLMAnalysisResult`：复用 `_run_analysis_core()`，通过显式注入的 `ChapterOrchestratorLLMClients` 调用 Gate 3，始终调用 Slice 4A final assembly，partial/blocked 不回退确定性报告。
- Gate 4 Slice 4C/4D 已为 `fund-analysis analyze` 增加显式 `--use-llm` opt-in provider-backed 路径；配置完整时读取 typed env config，构造 Service-owned `openai_compatible` HTTP chat-completions writer/auditor clients，并调用 Service `analyze_with_llm()`。`checklist` 不支持 `--use-llm`。
- Gate 4 Slice 4D provider contract 是 typed env config + openai-compatible HTTP chat-completions over existing `httpx`；无 vendor SDK、无默认 vendor/model/base URL、无 provider fallback、无 retry/backoff、无 live pytest smoke。
- Missing/invalid config/construction fail-closed；provider runtime error、blocked/partial orchestration 或 incomplete final assembly fail-closed；无 deterministic fallback。pytest 使用 fake env、`httpx.MockTransport` 和 monkeypatch，不需要真实 key。
- 当前生产路径仍是 UI -> Service -> `fund_agent/fund` 的过渡路径；尚未接入 Host/Agent 调度。
- Route C 是已接受的 MVP LLM report generation route；Gate 1-3 与 Gate 4 Slices 4A/4B/4C/4D 已作为当前代码事实 accepted locally。不得把 Host scheduling、Agent runner/tool loop 或 dayu runtime 写成已实现事实。
- 目标架构保持 UI -> Service -> Host -> Agent。未来 Host 必须使用 `dayu.host`；未来 Agent engine/tool loop/runner/ToolRegistry/ToolTrace 必须使用 `dayu.engine`。
- Service 可以组装业务用例、prompt/ExecutionContract 语义、报告生成策略和未来 write-audit-repair loop；Fund 作为 Agent 层基金领域能力包，拥有基金类型识别、CHAPTER_CONTRACT / preferred_lens / ITEM_RULE、事实抽取、审计规则和证据锚点语义。
- 所有业务参数必须在 typed request / contract / config 中显式声明；禁止通过 `extra_payload` 传递显式参数。
- 生产年报访问必须通过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
- 年报来源 fallback 继续按 `not_found` / `unavailable` eligible，`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed。
- 本 gate 不改变 runtime、schema、score、snapshot、quality gate、golden fixture、golden answer、manifest、promotion state、模板或 `AGENTS.md`。

| Field | State |
|---|---|
| Branch baseline | `codex/local-reconciliation` |
| Current phase | `MVP fund analysis report generation phase` |
| Current gate | `MVP Gate 4 draft PR gate` |
| Current gate classification | `heavy` |
| Current gate status | `draft PR #21 updated; resolving origin/main merge conflicts locally before final validation/push` |
| Next entry point | `MVP Gate 4 draft PR merge-conflict reconciliation validation` |
| Next gate classification | `heavy`; runtime/tests/docs validation required after merge reconciliation |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Short startup entry | `docs/current-startup-packet.md` |
| Accepted plan commit | `beb6891` |
| Accepted provider factory commit | `26203d3` |
| Accepted CLI provider wiring commit | `ab0590a` |
| Accepted docs/control sync commit | `4d0c19f` |
| Accepted aggregate review commit | `7a3dab9` |
| Accepted closeout entrypoint commit | `b0e68e0` |

## Current Gate

### Gate Objective

The local Gate 4 closeout is accepted and the user authorized the draft PR gate. PR #21 is open as a draft and was updated to the MVP Route C / Gate 4 scope. GitHub reported `mergeable=false` / `mergeable_state=dirty` against `origin/main` (`35a6765`, PR #20), so the active task is local merge-conflict reconciliation plus full validation before pushing the reconciliation commit.

### Current Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Source-of-truth plan | `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md` |
| Independent plan reviews | `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-truth-pivot-context-compaction-plan-review-glm-20260530.md` |
| Implementation evidence | `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md` |
| Gate 1 plan | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md` |
| Gate 1 plan reviews | `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-mimo-20260530.md`; `docs/reviews/mvp-gate1-chapter-fact-provider-plan-review-glm-20260530.md` |
| Gate 1 implementation evidence | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md` |
| Gate 1 implementation reviews | `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-review-glm-20260530.md` |
| Gate 1 controller judgment | `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md` |
| Gate 2 plan | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md` |
| Gate 2 plan decision | `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-decision-20260530.md` |
| Gate 2 implementation evidence | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-evidence-20260530.md` |
| Gate 2 implementation reviews | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-review-ds-20260530.md` |
| Gate 2 implementation re-reviews | `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-ds-20260530.md` |
| Gate 2 controller judgment | `docs/reviews/mvp-gate2-chapter-writer-auditor-controller-judgment-20260530.md` |
| Gate 3 plan | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md` |
| Gate 3 plan decision | `docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md` |
| Gate 3 implementation evidence | `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md` |
| Gate 3 implementation reviews | `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-ds-20260530.md` |
| Gate 3 review fix evidence | `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-evidence-20260530.md` |
| Gate 3 review fix re-reviews | `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-rereview-ds-20260530.md` |
| Gate 3 controller judgment | `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md` |
| Gate 4 plan | `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md` |
| Gate 4 plan decision | `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md` |
| Gate 4 Slice 4A implementation evidence | `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md` |
| Gate 4 Slice 4A implementation reviews | `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-ds-20260530.md` |
| Gate 4 Slice 4A review fix evidence | `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md` |
| Gate 4 Slice 4A review fix re-reviews | `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-mimo-20260530.md`; `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-rereview-ds-20260530.md` |
| Gate 4 Slice 4A controller judgment | `docs/reviews/mvp-gate4-final-assembler-slice4a-controller-judgment-20260530.md` |
| Gate 4 Slice 4B implementation evidence | `docs/reviews/mvp-gate4-llm-service-implementation-evidence-20260530.md` |
| Gate 4 Slice 4B implementation reviews | `docs/reviews/mvp-gate4-llm-service-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-llm-service-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4B controller judgment | `docs/reviews/mvp-gate4-llm-service-controller-judgment-20260530.md` |
| Gate 4 Slice 4C implementation evidence | `docs/reviews/mvp-gate4-cli-use-llm-implementation-evidence-20260530.md` |
| Gate 4 Slice 4C implementation reviews | `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4C controller judgment | `docs/reviews/mvp-gate4-cli-use-llm-controller-judgment-20260530.md` |
| Gate 4 Slice 4D provider plan | `docs/reviews/mvp-gate4-provider-construction-plan-20260530.md` |
| Gate 4 Slice 4D provider plan reviews | `docs/reviews/mvp-gate4-provider-construction-plan-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-plan-review-glm-20260530.md` |
| Gate 4 Slice 4D provider plan decision | `docs/reviews/mvp-gate4-provider-construction-plan-decision-20260530.md` |
| Gate 4 Slice 4D1 provider factory implementation evidence | `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-evidence-20260530.md` |
| Gate 4 Slice 4D1 provider factory reviews | `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4D1 provider factory controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d1-controller-judgment-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring implementation evidence | `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring reviews | `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-glm-20260530.md` |
| Gate 4 Slice 4D2 CLI provider wiring controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d2-controller-judgment-20260530.md` |
| Gate 4 Slice 4D3 docs/control sync controller judgment | `docs/reviews/mvp-gate4-provider-construction-4d3-controller-judgment-20260530.md` |
| Gate 4 Slice 4D aggregate reviews | `docs/reviews/mvp-gate4-provider-construction-aggregate-review-mimo-20260530.md`; `docs/reviews/mvp-gate4-provider-construction-aggregate-review-glm-20260530.md` |
| Gate 4 Slice 4D aggregate controller judgment | `docs/reviews/mvp-gate4-provider-construction-aggregate-controller-judgment-20260530.md` |
| Gate 4 closeout readiness reconciliation | `docs/reviews/mvp-gate4-closeout-readiness-reconciliation-20260530.md` |
| Prior release-maintenance roadmap summary | `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` |
| Prior overnight closeout summary | `docs/reviews/overnight-release-maintenance-closeout-20260529.md` |
| Historical control snapshots | `docs/archive/implementation-control-history-20260525.md`; `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` |

The Current Accepted Artifacts table is intentionally short. Older release-maintenance artifacts remain available through the historical index and review artifacts, but are not active gate truth for this MVP phase.

### Current Decision Summary

- Route C is the accepted MVP LLM report generation route; Gates 1-3 and Gate 4 Slices 4A/4B/4C/4D are accepted local code facts; Gate 5 remains future design.
- Current deterministic `fund-analysis analyze/checklist` remains the default production report/checklist mainline; `fund-analysis analyze --use-llm` is the explicit provider-backed opt-in path.
- Gate 1 `ChapterFactProvider` typed projection is implemented and accepted locally as Fund-layer code fact.
- Gate 2 `chapter_writer` / `chapter_auditor` single-chapter primitives are implemented and accepted locally as Fund-layer code facts.
- Gate 3 `chapter_orchestrator` is implemented and accepted locally as Service-layer write-audit-repair façade for chapters 1-6.
- Gate 4 Slice 4A `final_chapter_assembler` is implemented and accepted locally as Service-layer deterministic final assembly for chapters 0 and 7 plus accepted body chapters.
- Gate 4 Slice 4B `FundAnalysisService.analyze_with_llm()` is implemented and accepted locally as Service-layer LLM analyze use case over deterministic core, Gate 3 and Slice 4A.
- Gate 4 Slice 4C/4D `fund-analysis analyze --use-llm` is implemented and accepted locally as explicit provider-backed CLI opt-in: complete typed env config constructs Service-owned `openai_compatible` writer/auditor clients and calls `analyze_with_llm()`; missing config, construction failure and incomplete LLM result fail closed without deterministic fallback.
- `facet_recognizer` and full `FundToolService` remain future candidates; Gate 1 did not implement them.
- Gate 4 Slice 4D1 provider factory was accepted in commit `26203d3`; Gate 4 Slice 4D2 CLI provider wiring was accepted in commit `ab0590a`; 4D3 docs/control sync was accepted in commit `4d0c19f`; 4D aggregate review was accepted in commit `7a3dab9`.
- Golden / strict correctness / QDII / FOF / `110020` / fixture promotion blockers are residual product-quality work, not blockers for starting MVP report generation Gate 1.
- Host/Agent/dayu runtime integration is deferred to Route C Gate 5 and must not be preintroduced in Gates 1-4.

## Route C Future Route

| Gate | Future scope | Boundary |
|---|---|---|
| MVP Gate 1 | `ChapterFactProvider` typed projection accepted locally; `facet_recognizer` / full `FundToolService` remain future candidates | Agent/Fund owns fund-type/facet/fact/evidence semantics; no Service/Host/dayu runtime introduced |
| MVP Gate 2 | `chapter_writer` + `chapter_auditor` accepted locally as Fund-layer single-chapter primitives | LLM writing/audit consumes structured facts, derived calculations, explicit data gaps and evidence anchors only; no Service/Host/dayu/CLI integration introduced |
| MVP Gate 3 | `chapter_orchestrator` accepted locally | Service owns write-audit-repair policy for chapters 1-6; calls Agent/Fund capabilities through explicit contracts |
| MVP Gate 4 | Slices 4A `final_chapter_assembler`, 4B Service `analyze_with_llm`, 4C CLI `--use-llm` and 4D provider construction accepted locally | `--use-llm` is explicit opt-in; deterministic `analyze/checklist` remains default unless a later gate changes it |
| MVP Gate 5 | Optional dayu Host/Agent integration | Future Host uses `dayu.host`; future Agent engine/tool loop uses `dayu.engine` |

## Open Residuals

| Residual | Current disposition | Owner / next gate |
|---|---|---|
| Golden / strict correctness / fixture promotion | Residual only for MVP report generation; no promotion allowed without a separate accepted future gate | Future strict golden / fixture promotion gate |
| `004393` / `004194` / `006597` promotion readiness | `004393`, `004194`, `006597` are not promotion-prep-ready; `fixture_state=absent`; `promotion_allowed=false` | Future promotion-prep readiness owner |
| QDII / FOF / `110020` / `017641` coverage | Deferred from minimum v1 and not ready for full v1; not blockers for MVP Route C Gate 1 | Future QDII / FOF / index evidence policy gates |
| Release-maintenance long ledger | Preserved by archive and review links only; not active startup surface | Historical Evidence Index |
| Host/Agent/dayu runtime integration | Deferred to Route C Gate 5; no Host/Agent packages or dependencies before explicit gate | Future architecture gate |
| Deterministic renderer default | Remains current default production behavior; provider-backed LLM report path is explicit `--use-llm` opt-in only | Current behavior |
| Provider reliability / polish | Retry/backoff, live provider smoke, multi-model writer/auditor split, provider fallback, chapter 0/7 LLM polish and Evidence Confirm are not implemented | Future provider reliability / LLM polish gates |
| Untracked unrelated workspace files | Not part of accepted evidence unless a later controller gate explicitly accepts them | Controller scope audit |

## Recent Active Gate Ledger

| Gate | Status | Summary | Next action |
|---|---|---|---|
| `MVP Gate 4 closeout / ready-to-open-draft-PR readiness reconciliation` | accepted locally | Local closeout accepted after ruff, `git diff --check`, CLI `--use-llm` fail-closed smoke and full pytest `1106 passed`, coverage `91.76%`; no runtime changes beyond accepted Gate 4 work | Await explicit user authorization for draft PR gate |
| `MVP Gate 4 Slice 4D aggregate review` | accepted locally | MiMo and GLM aggregate reviews passed with no blocking findings; controller judgment accepted provider construction as a local checkpoint in commit `7a3dab9` | Start `MVP Gate 4 closeout / ready-to-open-draft-PR readiness reconciliation gate` |
| `MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression` | accepted locally | Synced README, design and control docs after 4D1/4D2; fixed `only` vs `default` control-doc blocker; full regression `1106 passed`, coverage `91.76%`; accepted commit `4d0c19f` | Completed by accepted aggregate review commit `7a3dab9` |
| `MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring` | accepted locally | CLI `analyze --use-llm` now reads typed LLM env config, constructs Service-owned provider clients, calls `analyze_with_llm()`, keeps default `analyze` deterministic, and fail-closes missing config/construction/incomplete LLM result without deterministic fallback; accepted commit `ab0590a` | Start `MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression gate` |
| `MVP Gate 4 Slice 4D1: typed LLM config and provider factory` | accepted locally | Added typed env config and Service-owned `openai_compatible` HTTP chat-completions provider factory over existing `httpx`; tests use fake env and `httpx.MockTransport`; accepted commit `26203d3` | Start `MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate` |
| `MVP Gate 4 Slice 4D: production LLM provider construction plan` | plan accepted locally | Plan accepts `openai_compatible` HTTP chat-completions over existing `httpx`, typed env config, Service-owned provider factory, no provider SDK, no live pytest network, no deterministic fallback and controller amendments for audit prompt passthrough, API key handling and CLI temporary error removal | Start `MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate` |
| `MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed` | accepted locally | CLI `analyze --use-llm` added as explicit opt-in but fail-closes before Service LLM call because provider construction is absent; `checklist` rejects the flag; 46 CLI tests, Service regressions, full validation and two PASS reviews; no provider, Service internals, Fund, final judgment, quality, golden, score, snapshot, dayu changes | Start `MVP Gate 4 Slice 4D: production LLM provider construction plan gate` |
| `MVP Gate 4 Slice 4B: Service analyze_with_llm` | accepted locally | Service-layer `FundAnalysisService.analyze_with_llm()` implemented with explicit `llm_clients`, deterministic core reuse, Gate 3 orchestration, Slice 4A final assembly, 7 targeted tests, full validation and two PASS reviews; no CLI, provider construction, source access, final judgment semantic change, dayu, golden or quality changes | Start `MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate` |
| `MVP Gate 4 Slice 4A: final_chapter_assembler` | accepted locally | Service-layer deterministic final assembler implemented with typed contract, chapter 7 from existing final judgment, chapter 0 from accepted conclusions, 14 targeted tests, full validation, two PASS reviews and two PASS fix re-reviews; no Service LLM analyze use case, CLI, provider construction, source access, final judgment semantic change, dayu, golden or quality changes | Start `MVP Gate 4 Slice 4B: Service analyze_with_llm implementation gate` |
| `MVP Gate 3: chapter_orchestrator` | accepted locally | Service-layer chapter orchestrator implemented with explicit bundle/projection input, injected writer/auditor clients, fail-closed repair policy, 30 targeted tests, full validation, two PASS reviews and two PASS fix re-reviews; no chapter 0/7 assembly, CLI, provider construction, source access, dayu, golden or quality changes | Start `MVP Gate 4: final_chapter_assembler + chapter 0 + CLI --use-llm plan gate` |
| `MVP Gate 2: chapter_writer + chapter_auditor` | accepted locally | Fund-layer writer/auditor primitives implemented with 38 targeted tests, full validation, two PASS re-reviews and controller judgment; no orchestrator/repair loop/CLI/dayu/promotion/source access changes | Start `MVP Gate 3: chapter_orchestrator plan gate` |
| `MVP Gate 1: ChapterFactProvider typed projection` | accepted locally | Fund-layer `chapter_fact_projection.v1` implemented with tests, docs, two PASS reviews and controller judgment; no writer/auditor/orchestrator/CLI/dayu/promotion changes | Start `MVP Gate 2: chapter_writer + chapter_auditor plan gate` |
| `MVP truth pivot and context compaction gate` | accepted locally | Control truth pivots to MVP report generation; Route C future route recorded; deterministic current implementation preserved; docs-only validation recorded | Historical current-phase evidence only |
| `release-maintenance consolidation + overnight closeout` | accepted locally as historical evidence | All `promotion_allowed=false`; `004393` / `004194` / `006597` not promotion-prep-ready with `fixture_state=absent`; QDII / FOF / `110020` deferred; Host/Agent/dayu deferred; no score/quality/FQ0-FQ6/golden fixture/golden-answer/manifest/runtime promotion changes | Use Historical Evidence Index only; do not treat as current phase |

## Historical Evidence Index

Detailed historical control state is preserved outside the active startup surface:

- `docs/archive/implementation-control-history-20260525.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
- `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`
- `docs/reviews/overnight-release-maintenance-closeout-20260529.md`

Use these files only to reconstruct evidence. They must not override this Startup Packet, the Current Gate table, or `docs/design.md` current implementation sections.

## Design / Control Alignment Rules

1. `AGENTS.md` remains the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for current architecture, boundaries, current product behavior, accepted future Route C, Dayu discipline, `FundDocumentRepository` source boundary, report-quality design and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners and next entry point.
4. `docs/current-startup-packet.md` is the short resume entry for later phaseflow work; it must mirror this control surface, not replace it.
5. Historical archive/review entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat archive content as superseded unless a later controller judgment says otherwise.
6. Future updates should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

1. Read `AGENTS.md`.
2. Read `docs/current-startup-packet.md`.
3. Read `docs/design.md` current implementation and Route C future design sections.
4. Confirm current phase, current gate and next entry in this file.
5. Confirm role: controller or specialist.
6. Confirm allowed files and non-goals before edits.
7. Classify the next gate per `AGENTS.md`; default heavier when uncertain.
8. Preserve deterministic MVP boundaries and do not introduce runtime, golden, promotion, Host/Agent/dayu or template changes outside an explicit accepted gate.
