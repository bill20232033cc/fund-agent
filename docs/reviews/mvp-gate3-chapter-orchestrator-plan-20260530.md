# MVP Gate 3: chapter_orchestrator plan

日期：2026-05-30

角色：Gateflow planning specialist。本文只写 code-generation-ready plan，不实现、不提交、不 push、不开 PR、不做 release/promotion。

## 1. Gate 定位

Gate：`MVP Gate 3: chapter_orchestrator plan gate`

分类：`heavy`。理由：本 gate 规划 Service 层 write-audit-repair policy、跨章依赖状态机和 public typed orchestration contract，会影响未来 LLM 报告生成路径、失败语义、章节接受条件和后续 Gate 4 CLI 接入。按 `AGENTS.md`，分类不确定时选择更重一级。

目标：设计最小安全实现，在 Service 层新增 `chapter_orchestrator`，消费 Gate 1 `ChapterFactProvider` typed projection 与 Gate 2 Fund 层 `chapter_writer` / `chapter_auditor` 单章 primitives，形成可审计的第 1-6 章 write-audit-repair 编排结果，并为 Gate 4 的 final assembler、第 0 章 assembly 和 CLI `--use-llm` 准备 accepted chapter conclusions。

本 gate 只规划实现，不写代码。后续 implementation gate 不得实现 final assembler、第 0 章最终装配、CLI `--use-llm`、Host/Agent/dayu runtime、release、promotion 或 source probing。

## 2. Preflight 事实

- 当前分支：`codex/local-reconciliation`。
- `git status --short` 只有既有未跟踪文件；`git status --short --untracked-files=no` 为空，未见 tracked dirty。
- 目标计划文件此前不存在。
- 当前控制面：`docs/current-startup-packet.md` 与 `docs/implementation-control.md` 均记录 Gate 2 accepted locally，下一入口为 `MVP Gate 3: chapter_orchestrator plan gate`。
- 现有未跟踪 artifact 属于 unrelated workspace residue，本计划不读取为 accepted evidence，后续不得 stage/delete。

## 3. 已读真源与直接证据

- `AGENTS.md`
  - 目标架构固定为 `UI -> Service -> Host -> Agent`。
  - Service 负责业务用例编排、场景定义、prompt/ExecutionContract 语义、报告生成和质量策略选择；Fund 作为 Agent 层基金领域能力包拥有 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、审计规则和证据锚点语义。
  - 所有显式参数必须声明在 typed request / contract / config 中，禁止 `extra_payload`。
  - 生产年报 PDF 访问必须经 `FundDocumentRepository`；Service/UI/Host/renderer/quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
  - Host 必须使用 `dayu.host`、Agent runtime 必须使用 `dayu.engine`，但当前 gate 不引入 Host/Agent/dayu。
- `docs/current-startup-packet.md`
  - Gate 1 已接受 Fund 层 `project_chapter_facts()` / `ChapterFactProvider.project()`，只消费内存 `StructuredFundDataBundle`。
  - Gate 2 已接受 Fund 层 `chapter_writer.py` / `chapter_auditor.py`，只消费 Gate 1 chapter facts 和显式注入的 LLM Protocol client。
  - 当前没有 write-audit-repair loop、chapter orchestrator、final LLM assembler、CLI `--use-llm` 或 Host/Agent/dayu runtime。
- `docs/implementation-control.md`
  - Next implementation work 是 Gate 3：plan Service-owned `chapter_orchestrator` and write-audit-repair policy against Gate 1 / Gate 2 primitives。
  - Gate 3 边界：Service owns write-audit-repair policy；通过显式 contract 调用 Agent/Fund capabilities。
- `docs/design.md` §5.4 / §5.4.1
  - 章节写作和审计只能读取 structured facts、derived calculations、EvidenceAnchor 和明确数据缺口。
  - 审计失败必须产生 repair decision；可局部修复的问题 patch，结构错误/关键逻辑不成立/不可修补时 regenerate；修复后必须重新审计。
  - 当前 8 章模板与未来 0-10 章体系映射尚未裁决，不得把当前 renderer 改写为 0-10 章。
  - Route C Gate 3 是 Service-owned write-audit-repair loop；Gate 4 才是 `final_chapter_assembler`、第 0 章 assembly 和 CLI `--use-llm`。
- `docs/fund-analysis-template-draft.md`
  - 当前模板是第 0-7 章。
  - 第 0 章是投资要点概览，不能按普通三段结构渲染，必须后置依赖 accepted conclusions。
  - 第 1-6 章默认应包含“结论要点 / 详细情况 / 证据与出处”三段结构。
  - 第 7 章是最终判断，依赖前序章节结论和最小验证计划，不得由 prompt 自由发挥。
  - CHAPTER_CONTRACT、preferred_lens、ITEM_RULE 是章节写作/审计约束。
- Gate 1 controller judgment
  - Gate 1 accepted public API：`project_chapter_facts()` / `ChapterFactProvider.project()`。
  - Gate 1 output：`ChapterFactProjection` -> `ChapterFactInput`，包含 contract、fund_type、classification_basis、facet/lens/item rule projection、facts、evidence_anchors、missing_reasons、source_field_ids。
  - `facet_recognizer` 与 full `FundToolService` 仍是未来候选，不是 Gate 3 依赖。
- Gate 2 controller judgment
  - Gate 2 accepted Fund-layer primitives：`build_chapter_writer_input()`、`write_chapter()`、`ChapterAuditInput`、`audit_chapter()`。
  - writer/auditor fail-closed 覆盖 missing anchor、unknown fund type、LLM unavailable、ITEM_RULE deletion、`non_asserted_facets`、chapter 5 cross-period gap、must_not_cover、L1 numerical closure、E2 deferral。
  - Gate 2 不授权 orchestrator、repair loop、final assembler、chapter 0 assembly、CLI `--use-llm`、Service orchestration、Host/Agent/dayu runtime、promotion 或 golden fixture 变更。

## 4. 当前代码事实

- Service 包当前位于 `fund_agent/services/`，`FundAnalysisService` 是现有 analyze/checklist 用例编排层。
- 当前 production report generation 仍是 deterministic `fund-analysis analyze`：Service 调用 `FundDataExtractor` 取得 `StructuredFundDataBundle`，执行确定性分析，调用 `render_template_report()`，再调用 `run_programmatic_audit()`。
- `fund_agent/fund/chapter_facts.py`
  - `project_chapter_facts(bundle, chapter_ids=tuple(range(8))) -> ChapterFactProjection`。
  - `ChapterFactProvider.project(bundle, chapter_ids=...)` 是 concrete façade。
  - `ChapterFactMissingReason` 已包含 `accepted_chapter_conclusions_missing`、`cross_period_comparison_missing`、`classified_fund_type_*`、`evidence_missing` 等 Gate 3 必须处理的状态。
  - `project_chapter_facts()` 对 `chapter_ids` 做非空、唯一、0-7 校验。
- `fund_agent/fund/chapter_writer.py`
  - `build_chapter_writer_input(projection, chapter_id, mode="llm", citation_style="body_quote", max_output_chars=12000) -> ChapterWriterInput`。
  - `write_chapter(input_data, llm_client=...) -> ChapterWriteResult`。
  - `mode="prompt_only"` 返回 blocked prompt，不生成 fake draft。
  - chapter 0 / 7 遇到 `accepted_chapter_conclusions_missing` 会 blocked `chapter_requires_accepted_conclusions`。
  - `llm_client is None` 且 `mode="llm"` 会 blocked `llm_unavailable`。
- `fund_agent/fund/chapter_auditor.py`
  - `ChapterAuditInput(writer_input, draft, run_programmatic=True, run_llm=True)`。
  - `audit_chapter(input_data, llm_client=...) -> ChapterAuditResult`。
  - `accepted=True` 只在 programmatic 和 LLM audit 均 pass 时成立。
  - `repair_hint` 闭集为 `none`、`patch`、`regenerate`、`needs_more_facts`。
- Gate 2 tests 已使用 local fake writer/auditor LLM clients；生产代码没有真实 provider SDK、env/config loading 或 default fake pass。

## 4.1 Review Finding Disposition

本 plan-fix pass 已读取并处理：

- `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-ds-20260530.md`
- `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-mimo-20260530.md`

| Finding | Disposition | Plan change |
|---|---|---|
| DS-1 / DS-4 writer stop reason mapping 不完整且含“或”歧义 | Fixed | §7.1 增加 `llm_empty_response` / `llm_contract_violation`；§8.1 新增完整一对一 mapping table，覆盖每个 `ChapterWriteStopReason` |
| DS-2 / MiMo-3 `ChapterOrchestrator` façade 与 standalone function 注入语义不一致 | Fixed | §7.6 固定 `ChapterOrchestrator.__init__(fact_provider=None)` 存储 provider，`orchestrate()` 委托 `orchestrate_chapters(..., fact_provider=self._fact_provider)` |
| DS-3 / MiMo-2 auditor LLM unavailable 会浪费 writer retry | Fixed | §8 step 3 和 §9.7 固定 early stop：`run_llm_audit=True` 且 auditor client 缺失时不调用 writer、不进入 retry |
| DS-5 accepted conclusion fallback 可能过长 | Fixed | §7.5 增加 length cap 字段；§10 支持 `###` / `##` heading、500 字符硬上限、fallback 只取前 3 个非空行 |
| DS-6 `_decide_repair()` 未定义签名和决策表 | Fixed | §8.2 新增函数签名、remaining budget 语义和完整 decision table，覆盖 auditor unavailable、LLM blocked、`max_repair_attempts=0` |
| DS-7 Service `__init__.py` 导出不明确 | Fixed | §12 Slice 4 明确 exact exports，只导出主入口和顶层 request/result/policy/client bundle |
| MiMo-1 patch -> regenerate 同 prompt 修复率不明 | Accepted residual | §6 / §16 明确 best-effort residual；implementation tests 必须覆盖 budget exhaustion |
| MiMo-4 `partial` status Gate 4 消费契约未裁决 | Accepted residual for Gate 4 | §7.1 / §17 明确 Gate 4 必须裁决 partial assembly 行为，Gate 3 不把 partial 当 complete report |
| MiMo-5 `max_repair_attempts=0` 未显式 | Fixed | §7.3 / §8.2 明确 0 表示初始 audit fail 后不进入 repair retry |

## 5. Non-goals

Gate 3 implementation 不做：

- 不实现 final chapter assembler。
- 不生成或装配第 0 章最终摘要；第 0 章留给 Gate 4。
- 不生成或装配第 7 章最终判断正文；第 7 章留给 Gate 4 与 final assembler。
- 不新增 CLI `--use-llm`，不改变 `fund-analysis analyze/checklist` 默认生产路径。
- 不修改 deterministic renderer、programmatic audit、quality gate、FQ0-FQ6、score、snapshot、final judgment。
- 不修改 golden fixtures、golden answers、manifests、promotion state。
- 不修改 `docs/fund-analysis-template-draft.md` 或 `AGENTS.md`。
- 不新增 `fund_agent/host`、`fund_agent/agent`、dayu 依赖、runner、ToolRegistry、ToolTrace、session/run lifecycle、并发、取消、恢复或 outbox。
- 不读取 `FundDocumentRepository`、PDF/cache/source helper/downloader/parser；Service orchestrator 只能消费调用方提供的 `StructuredFundDataBundle` 或 `ChapterFactProjection`。
- 不实现真实 LLM provider client、env/config 读取、HTTP/OpenAI SDK、streaming、并发或 provider retry。
- 不把 fake LLM path 暴露给生产 contract；fake 只能存在于 tests。
- 不把 LLM unavailable、writer blocked、auditor fail/blocked 伪装为 accepted chapter。
- 不把 Route C 写成 MVP complete。

## 6. 推荐总体方案

新增 Service 层模块：

- `fund_agent/services/chapter_orchestrator.py`

可选最小同步：

- `fund_agent/services/__init__.py`：仅导出 public dataclass / service façade，方便后续 Gate 4 CLI 接入。
- `fund_agent/README.md`：实现后只同步当前 Service 层新增 orchestrator 边界，不写 CLI/dayu/final assembler 已实现。
- `tests/README.md`：实现后登记 targeted Service tests。

控制面同步不属于 implementation worker 默认 scope：

- `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md` 只能由 controller closeout 或 controller 明确授权后更新。
- 本 Gate 3 implementation worker 默认不得修改上述 control/design docs；它只可产出 implementation evidence artifact。

核心决策：

- Orchestrator 属于 Service 层，因为它决定章节顺序、write-audit-repair policy、retry budget、stop/fail-closed 语义和未来 CLI use-case integration。
- Writer/auditor/domain contracts 保持 Fund 层所有权；Service 不重写 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点和审计规则。
- Gate 3 最小可用范围只编排第 1-6 章。第 0 章和第 7 章不生成正文，但 orchestrator 输出必须保留 accepted chapter conclusions，供 Gate 4 final assembler 使用。
- 输入可从 `StructuredFundDataBundle` 投影，或直接传入 `ChapterFactProjection`。二者必须是显式互斥 typed 参数，不得用 `extra_payload`。
- 生产 LLM client 必须由调用方显式注入；Gate 3 不提供默认 provider、不读 env、不 fake pass。
- Repair policy 采用最小安全策略：不做 string patch。`patch` 和 `regenerate` 都映射为 best-effort regenerate attempt，但不向 Gate 2 writer 塞入 hidden repair context；`needs_more_facts`、LLM unavailable、unknown fund type、chapter dependency missing 等 fail closed。

## 7. Proposed public contracts

新增 `fund_agent/services/chapter_orchestrator.py`。所有 public dataclass 使用 `frozen=True, slots=True, kw_only=True`。所有函数/类必须有完整中文 docstring，并引用模板第 0-7 章。

### 7.1 Literal aliases

```python
ChapterOrchestratorSchemaVersion = Literal["chapter_orchestrator.v1"]
ChapterOrchestrationStatus = Literal["accepted", "partial", "blocked"]
ChapterRunStatus = Literal["accepted", "blocked", "failed", "skipped"]
ChapterRunStopReason = Literal[
    "none",
    "chapter_not_in_scope",
    "dependency_missing",
    "fund_type_unknown",
    "missing_required_facts",
    "writer_blocked",
    "auditor_failed",
    "auditor_blocked",
    "repair_budget_exhausted",
    "needs_more_facts",
    "llm_unavailable",
    "llm_empty_response",
    "llm_contract_violation",
    "llm_exception",
]
ChapterRepairAction = Literal["none", "regenerate", "needs_more_facts", "stop"]
ChapterOrchestrationInputKind = Literal["structured_bundle", "chapter_projection"]
```

说明：

- `partial` 表示至少一个 scoped chapter accepted，但并非全部 accepted；不得供 Gate 4 assembly 作为 complete report。Gate 4 必须单独裁决 partial 输入是拒绝、降级还是生成不完整草稿，Gate 3 不预先裁决。
- `blocked` 表示没有可接受章节，或 fail-fast policy 触发停止。
- `failed` 用于 writer/auditor 有结果但未 accepted；`blocked` 用于输入、依赖、LLM unavailable 或 fail-closed 状态。

### 7.2 LLM client bundle

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestratorLLMClients:
    """章节编排 LLM client 显式注入包，见模板第 1-6 章。

    Attributes:
        writer: Gate 2 writer LLM Protocol client。
        auditor: Gate 2 auditor LLM Protocol client。
    """

    writer: ChapterLLMClient | None
    auditor: ChapterAuditLLMClient | None
```

约束：

- `writer` 和 `auditor` 可分别为 `None`，但 production request 若需要 accepted chapters 必须显式注入二者。
- Orchestrator 不构造真实 provider、不读取 env/config、不导入 OpenAI/HTTP SDK。
- Tests 可以定义 `_FakeChapterLLMClient` / `_FakeAuditLLMClient`，但 fake class 只能在 `tests/services/test_chapter_orchestrator.py` 内。

### 7.3 Policy dataclass

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationPolicy:
    """章节 write-audit-repair 策略，见模板第 1-6 章。

    Attributes:
        target_chapter_ids: 本次允许生成的章节编号。
        max_repair_attempts: 每章审计失败后的最大 regenerate 次数。
        max_output_chars: 传给 Gate 2 writer 的章节输出硬上限。
        fail_fast: 任一章节 fail-closed 后是否停止后续章节。
        run_programmatic_audit: 是否执行 Gate 2 programmatic audit。
        run_llm_audit: 是否执行 Gate 2 LLM audit。
    """

    target_chapter_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    max_repair_attempts: int = 1
    max_output_chars: int = 12000
    fail_fast: bool = True
    run_programmatic_audit: bool = True
    run_llm_audit: bool = True
```

校验规则：

- `target_chapter_ids` 必须非空、唯一、全部位于 1-6。Gate 3 禁止接受 0 或 7；若调用方传入，raise `ValueError`。
- `max_repair_attempts >= 0`，建议默认 1；MVP 不需要多轮复杂修复。`max_repair_attempts=0` 表示 attempt 0 初始写作后若 audit 未 accepted，直接 stop，不进入 repair retry。
- `max_output_chars > 0`。
- `run_programmatic_audit=False` 只允许测试显式使用；生产路径建议保持 True。计划不强行引入 environment 判断。

### 7.4 Input dataclasses

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationInput:
    """章节编排输入，见模板第 1-6 章。

    Attributes:
        schema_version: orchestration schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        input_kind: 输入来源类型。
        structured_data: 已抽取完成的结构化基金数据包。
        chapter_projection: 已投影的 Gate 1 章节事实。
        policy: write-audit-repair 策略。
    """

    schema_version: ChapterOrchestratorSchemaVersion = "chapter_orchestrator.v1"
    fund_code: str
    report_year: int
    input_kind: ChapterOrchestrationInputKind
    structured_data: StructuredFundDataBundle | None = None
    chapter_projection: ChapterFactProjection | None = None
    policy: ChapterOrchestrationPolicy = ChapterOrchestrationPolicy()
```

校验规则：

- `input_kind="structured_bundle"` 时必须提供 `structured_data` 且 `chapter_projection is None`。
- `input_kind="chapter_projection"` 时必须提供 `chapter_projection` 且 `structured_data is None`。
- `fund_code` / `report_year` 必须与 bundle 或 projection 的字段完全一致；不一致 raise `ValueError`。
- 不允许二者同时提供，不允许二者都缺失。
- Service 不从文件系统或 repository 创建 bundle；bundle 必须由上游现有 Service/FundDataExtractor 已经取得。

### 7.5 Output dataclasses

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class AcceptedChapterConclusion:
    """已接受章节结论摘要，供 Gate 4 final assembler 消费。

    Attributes:
        chapter_id: 模板章节编号。
        title: 章节标题。
        conclusion_markdown: 从 accepted draft 中抽取的“结论要点”段落或安全 fallback。
        conclusion_truncated: 结论是否因长度上限被截断。
        conclusion_source: 结论提取来源。
        used_fact_ids: 被 accepted draft 使用的 fact id。
        used_anchor_ids: 被 accepted draft 使用的 anchor id。
        declared_missing_reasons: accepted draft 显式声明的数据缺口。
        audit_checked_rules: programmatic audit checked rules。
    """

    chapter_id: int
    title: str
    conclusion_markdown: str
    conclusion_truncated: bool
    conclusion_source: Literal["heading", "fallback_lines"]
    used_fact_ids: tuple[str, ...]
    used_anchor_ids: tuple[str, ...]
    declared_missing_reasons: tuple[ChapterFactMissingReason, ...]
    audit_checked_rules: tuple[ChapterAuditRuleCode, ...]
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRepairDecision:
    """单次审计后的 repair 决策，见模板第 1-6 章。

    Attributes:
        action: repair action。
        reason: 中文原因。
        source_repair_hint: Gate 2 聚合 repair hint。
        issue_ids: 触发 repair 的 issue id。
    """

    action: ChapterRepairAction
    reason: str
    source_repair_hint: ChapterAuditRepairHint
    issue_ids: tuple[str, ...]
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAttemptRecord:
    """单章一次 write/audit attempt 记录，见模板第 1-6 章。

    Attributes:
        attempt_index: 从 0 开始的 attempt 序号。
        writer_result: Gate 2 writer result。
        audit_result: Gate 2 audit result；writer blocked 时为 `None`。
        repair_decision: audit 后 repair 决策；未进入 audit 时为 `None`。
    """

    attempt_index: int
    writer_result: ChapterWriteResult
    audit_result: ChapterAuditResult | None
    repair_decision: ChapterRepairDecision | None
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRunResult:
    """单章编排结果，见模板第 1-6 章。

    Attributes:
        chapter_id: 模板章节编号。
        title: 章节标题。
        status: 单章状态。
        stop_reason: 停止原因。
        accepted_draft: accepted 章节草稿。
        accepted_conclusion: accepted 章节结论摘要。
        attempts: attempt 记录。
        issues: 聚合 writer/auditor issue 文本。
    """

    chapter_id: int
    title: str
    status: ChapterRunStatus
    stop_reason: ChapterRunStopReason
    accepted_draft: ChapterDraft | None
    accepted_conclusion: AcceptedChapterConclusion | None
    attempts: tuple[ChapterAttemptRecord, ...]
    issues: tuple[str, ...]
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationResult:
    """章节编排总结果，见模板第 1-6 章。

    Attributes:
        schema_version: orchestration schema 版本。
        status: 总状态。
        fund_code: 基金代码。
        report_year: 年报年份。
        projection: Gate 1 章节事实投影。
        chapter_results: 按执行顺序排列的章节结果。
        accepted_conclusions: 按章节顺序排列的 accepted 结论摘要。
        blocked_reasons: 总体阻断原因。
        generated_chapter_ids: 实际尝试生成的章节。
        skipped_chapter_ids: 因 Gate 3 scope 或 fail_fast 跳过的章节。
    """

    schema_version: ChapterOrchestratorSchemaVersion = "chapter_orchestrator.v1"
    status: ChapterOrchestrationStatus
    fund_code: str
    report_year: int
    projection: ChapterFactProjection
    chapter_results: tuple[ChapterRunResult, ...]
    accepted_conclusions: tuple[AcceptedChapterConclusion, ...]
    blocked_reasons: tuple[str, ...]
    generated_chapter_ids: tuple[int, ...]
    skipped_chapter_ids: tuple[int, ...]
```

### 7.6 Public API

```python
def build_chapter_orchestration_input(
    *,
    fund_code: str,
    report_year: int,
    structured_data: StructuredFundDataBundle | None = None,
    chapter_projection: ChapterFactProjection | None = None,
    policy: ChapterOrchestrationPolicy | None = None,
) -> ChapterOrchestrationInput:
    ...
```

```python
def orchestrate_chapters(
    input_data: ChapterOrchestrationInput,
    *,
    llm_clients: ChapterOrchestratorLLMClients,
    fact_provider: ChapterFactProvider | None = None,
) -> ChapterOrchestrationResult:
    ...
```

```python
class ChapterOrchestrator:
    def __init__(self, fact_provider: ChapterFactProvider | None = None) -> None:
        ...

    def orchestrate(
        self,
        input_data: ChapterOrchestrationInput,
        *,
        llm_clients: ChapterOrchestratorLLMClients,
    ) -> ChapterOrchestrationResult:
        ...
```

约束：

- `build_chapter_orchestration_input()` 只做 typed input validation 和互斥输入归一化。
- `orchestrate_chapters()` 若输入为 bundle，使用 `fact_provider or ChapterFactProvider()` 调用 `project()`，chapter_ids 只传 policy target chapters。
- `ChapterOrchestrator.__init__()` 存储可选 `fact_provider`；`orchestrate()` 必须委托 `orchestrate_chapters(input_data, llm_clients=llm_clients, fact_provider=self._fact_provider)`，不得 hardcode 不可注入 provider。
- 若输入为 projection，必须确认 projection 包含 policy target chapters 的唯一输入；不要二次投影。
- `fact_provider` 是可注入 façade，不是 Service 重新实现 domain projection。

## 8. Orchestration data flow

1. Validate `ChapterOrchestrationInput`：
   - input kind 与 payload 互斥一致；
   - `fund_code` / `report_year` 同源一致；
   - policy target chapters 只允许 1-6。
2. Resolve projection：
   - from `StructuredFundDataBundle`：`ChapterFactProvider.project(bundle, chapter_ids=policy.target_chapter_ids)`。
   - from `ChapterFactProjection`：使用现有 projection，但必须校验章节覆盖。
3. Global fail-closed checks：
   - `projection.fund_type == "unknown"`：返回 `status="blocked"`，每个 target chapter 标为 blocked `fund_type_unknown`，不得调用 writer。
   - 缺少任一 target chapter：raise `ValueError`，这是 caller/projection contract 错误。
   - `policy.run_llm_audit is True and llm_clients.auditor is None`：返回 `status="blocked"`，每个 target chapter 标为 blocked `llm_unavailable`，`generated_chapter_ids=()`；不得调用 writer，不得进入 repair loop。这是审计基础设施缺失，不是草稿内容可修复问题。
4. Execute chapters sequentially in `policy.target_chapter_ids` order。
5. For each chapter:
   - `writer_input = build_chapter_writer_input(projection, chapter_id=chapter_id, max_output_chars=policy.max_output_chars)`。
   - 调用 `write_chapter(writer_input, llm_client=llm_clients.writer)`。
   - writer blocked：
     - 必须按 §8.1 完整 mapping table 转换 stop reason。
     - writer blocked 不进入 auditor，不进入 repair loop。
   - writer drafted：
     - build `ChapterAuditInput(writer_input=writer_input, draft=draft, run_programmatic=policy.run_programmatic_audit, run_llm=policy.run_llm_audit)`。
     - 调用 `audit_chapter(..., llm_client=llm_clients.auditor)`。
   - audit accepted：创建 `AcceptedChapterConclusion`，run result accepted。
   - audit blocked/fail：调用 §8.2 `_decide_repair(audit_result, remaining_budget=..., auditor_available=..., run_llm_audit=...)`。
6. Repair loop：
   - attempt 0 是初始写作。
   - `max_repair_attempts=0` 时，attempt 0 audit 未 accepted 后直接 stop；`_decide_repair()` 必须返回 `stop` 或 `needs_more_facts`，不得返回 `regenerate`。
   - 如果 `audit_result.repair_hint == "none"` 但 `accepted=False`，默认 `stop`，因为没有安全修复依据。
   - `needs_more_facts` -> `needs_more_facts`，停止本章；不调用 source/repository。
   - `patch` -> MVP best-effort 映射为 `regenerate`，因为 Gate 2 尚无 typed patch API，不能 ad hoc string patch。该映射可能重复生成同类失败，必须受 retry budget 限制。
   - `regenerate` -> 仅当 remaining budget > 0 时重新调用 writer；否则 `repair_budget_exhausted`。
   - 重新调用 writer 时必须使用同一个 `ChapterWriterInput`。Gate 3 不改变 Fund prompt contract；若需要 repair hints 进入 prompt，必须先开 Gate 2/3 contract extension。本 gate implementation 不可把 repair text 塞入 `extra_payload`。
   - LLM exception：`write_chapter()` / `audit_chapter()` 当前不保证捕获 client exceptions；orchestrator 必须捕获 `Exception`，记录 `llm_exception`，不得继续伪造结果。
7. Overall status：
   - 所有 target chapters accepted -> `accepted`。
   - 至少一个 accepted 且存在 failed/blocked/skipped -> `partial`。
   - 无 accepted -> `blocked`。
   - `fail_fast=True` 时，首次 failed/blocked 后后续未执行 target chapter 标为 skipped `dependency_missing` 或 `chapter_not_in_scope`；推荐 stop reason 使用 `dependency_missing`，因为 future final assembly 需要完整 accepted conclusions。

### 8.1 Writer stop reason mapping

Implementation 必须使用下表把每个 `ChapterWriteStopReason` 映射为唯一 `ChapterRunStopReason`，不得使用“或”、不得发明 fallback：

| `ChapterWriteStopReason` | `ChapterRunStatus` | `ChapterRunStopReason` | Rationale |
|---|---|---|---|
| `none` | `accepted` 仅在 audit accepted 后使用 | `none` | writer drafted 不是最终 accepted，只有 audit pass 后才能 accepted |
| `fund_type_unknown` | `blocked` | `fund_type_unknown` | 类型未知时禁止类型化写作 |
| `missing_required_facts` | `blocked` | `missing_required_facts` | 结构化 facts 不足 |
| `evidence_anchor_missing` | `blocked` | `missing_required_facts` | 关键 fact 缺锚点属于事实/证据不足，不是可重试 writer 问题 |
| `item_rule_deleted_required_content` | `blocked` | `missing_required_facts` | 条件条目被删除但 contract 仍强依赖，属于输入/契约事实不足 |
| `chapter_requires_accepted_conclusions` | `blocked` | `dependency_missing` | Gate 3 不生成 0/7；若出现说明依赖缺失 |
| `prompt_only` | `blocked` | `writer_blocked` | prompt-only 不生成 draft；仅测试/debug，不可 accepted |
| `llm_unavailable` | `blocked` | `llm_unavailable` | writer client 缺失 |
| `llm_empty_response` | `blocked` | `llm_empty_response` | writer LLM 返回空文本 |
| `llm_contract_violation` | `blocked` | `llm_contract_violation` | writer 输出 marker、长度、禁用措辞等违反 Gate 2 contract |

`writer_blocked` 只用于 `prompt_only` 或未来显式新增但尚未被本 gate 接受的 writer stop reason；当前实现若遇到不在上表的 stop reason，应 raise `ValueError`，而不是静默泛化。

### 8.2 Repair decision contract

Implementation 必须定义以下 private helper；它是核心状态机，implementation agent 不得自行改变签名：

```python
def _decide_repair(
    audit_result: ChapterAuditResult,
    *,
    remaining_budget: int,
    auditor_available: bool,
    run_llm_audit: bool,
) -> ChapterRepairDecision:
    ...
```

输入语义：

- `remaining_budget` 是当前 audit 失败后剩余 regenerate 次数；`max_repair_attempts=0` 时首次 audit 后该值为 0。
- `auditor_available` 等于 `llm_clients.auditor is not None`。
- `run_llm_audit` 来自 policy；当为 False 时，auditor client 缺失不构成 LLM unavailable。
- `audit_result.accepted=True` 时不应调用 `_decide_repair()`；若被调用，返回 `action="none"`。

完整决策表：

| Condition | Action | Source repair hint | Reason / stop reason |
|---|---|---|---|
| `audit_result.accepted is True` | `none` | `audit_result.repair_hint` | 已通过，不修复 |
| `run_llm_audit and not auditor_available` | `stop` | `audit_result.repair_hint` | auditor client 缺失是基础设施阻断；最终 stop reason `llm_unavailable` |
| `audit_result.llm.status == "blocked"` and any LLM issue has `rule_code == "LLM_UNAVAILABLE"` | `stop` | `audit_result.repair_hint` | LLM audit unavailable，不重试 writer |
| `audit_result.repair_hint == "needs_more_facts"` | `needs_more_facts` | `needs_more_facts` | 需要更多事实；不 source probing |
| `audit_result.repair_hint == "none"` | `stop` | `none` | 无安全修复依据 |
| `remaining_budget <= 0` and repair hint in `("patch", "regenerate")` | `stop` | hint | retry budget exhausted；最终 stop reason `repair_budget_exhausted` |
| `audit_result.status == "blocked"` and repair hint in `("patch", "regenerate")` and `remaining_budget > 0` | `regenerate` | hint | 非 unavailable 的 blocked，可 best-effort regenerate |
| `audit_result.status == "fail"` and repair hint in `("patch", "regenerate")` and `remaining_budget > 0` | `regenerate` | hint | 内容或结构失败，可 best-effort regenerate |

`ChapterRepairDecision.issue_ids` 必须收集 `audit_result.programmatic.issues + audit_result.llm.issues` 中触发决策的 issue id；无法缩小时可包含全部 audit issue id，但不得为空，除非 audit result 没有 issue。

## 9. Chapter dependency policy

### 9.1 Gate 3 target chapters

- Gate 3 默认只生成第 1-6 章。
- 第 0 章和第 7 章即使在 projection 中存在，也必须在 policy validation 阶段拒绝作为 target。
- `ChapterOrchestrationResult.accepted_conclusions` 是 Gate 4 的输入，不是第 0/7 章正文。

### 9.2 第 0 章

- 第 0 章是封面/投资要点概览，必须后置总结 accepted chapters。
- Gate 3 不调用 `write_chapter()` 生成第 0 章。
- Gate 3 可以在 result 中保留 `accepted_conclusions`，使 Gate 4 能构造第 0 章输入。
- 若后续 Gate 4 请求第 0 章，必须只消费 accepted conclusions，不引入新事实。

### 9.3 第 7 章

- 第 7 章是最终判断，依赖前序章节 accepted 结论、风险/清单/quality gate 状态和最终判断契约。
- Gate 3 不调用 `write_chapter()` 生成第 7 章。
- Gate 3 输出的 `accepted_conclusions` 必须包含每章 conclusion、used anchors、missing reasons 和 audit checked rules，供 Gate 4 判定第 7 章是否可装配。

### 9.4 第 5 章跨期缺失

- Gate 1 当前在单期 bundle 下可能为第 5 章产生 `cross_period_comparison_missing`。
- Gate 2 auditor 对第 5 章风格稳定/变化断言执行 fail-closed 检查。
- Gate 3 不补取跨期数据、不调用 repository/source、不伪造趋势。
- 若 writer 能以“缺少跨期数据/下一步最小验证问题”方式通过 audit，章节可 accepted。
- 若 writer/auditor 因跨期缺口失败且 repair 后仍失败，run result 停止为 `auditor_failed` 或 `needs_more_facts`。

### 9.5 Unknown fund type

- `projection.fund_type == "unknown"` 是 global blocked。
- Orchestrator 不允许对 unknown fund type 应用 preferred_lens 或生成类型化判断。
- 返回 blocked result 时必须保留 projection 和 per-chapter blocked results，便于 caller 展示失败原因。

### 9.6 Missing facts

- writer preflight 已负责关键 missing/evidence fail-closed。
- Orchestrator 不重写 missing 规则，只把 writer stop reason 映射为 Service-level stop reason。
- `needs_more_facts` 永远不触发 source probing；它只作为结果状态暴露给 controller/Gate 4。

### 9.7 LLM unavailable / exceptions

- `llm_clients.writer is None`：writer 返回 `llm_unavailable`，orchestrator blocked。
- `llm_clients.auditor is None` 且 `run_llm_audit=True`：orchestrator 在全局 preflight 直接 blocked `llm_unavailable`，不得调用 writer，不得进入 audit，不得消耗 repair budget。
- `audit_result.llm.status == "blocked"` 且 issue `rule_code=="LLM_UNAVAILABLE"`：`_decide_repair()` 必须返回 `stop`，不得 regenerate。
- client 抛异常：orchestrator 捕获并记录 `llm_exception`，停止该章；`fail_fast=True` 时停止后续章节。

### 9.8 Writer blocked

- writer blocked 不进入 auditor。
- attempt record 的 `audit_result=None`，`repair_decision=None`。
- stop reason 必须来自 writer stop reason 的显式 mapping，不得泛化为 unknown。

### 9.9 Auditor fail/blocked

- `audit_result.status == "blocked"` -> 先按 §8.2 `_decide_repair()` 判断；LLM unavailable 永不重试，其他 `patch` / `regenerate` 且预算仍可用时可 best-effort regenerate。
- `audit_result.status == "fail"` -> chapter failed，按 repair hint 决策。
- `audit_result.repair_hint == "needs_more_facts"` -> 停止本章，不重试。
- `repair_budget_exhausted` 时必须保留所有 attempts 和 last audit issues。

## 10. Accepted conclusion extraction

`AcceptedChapterConclusion.conclusion_markdown` 必须 deterministic 从 accepted draft 提取：

1. 硬上限：`MAX_ACCEPTED_CONCLUSION_CHARS = 500`。`conclusion_markdown` 超过上限时截断到 500 字符，`conclusion_truncated=True`；不得让完整章节正文进入 conclusion。
2. Heading extraction 支持 `### 结论要点` 和 `## 结论要点`。取该 heading 到下一个同级或更高级 heading 之前的内容：
   - `### 结论要点` 截止到下一个 `### ` 或 `## `。
   - `## 结论要点` 截止到下一个 `## `。
   - 去除首尾空白，`conclusion_source="heading"`。
3. 若没有上述 heading 但 audit accepted，fallback 只取前 3 个非空行，以换行连接后再应用 500 字符上限；`conclusion_source="fallback_lines"`。不得把整篇 draft 当作 fallback。
4. 不做 LLM 总结，不改写结论，不生成新判断。
5. 保留 `used_fact_ids`、`used_anchor_ids`、`declared_missing_reasons` 和 `audit_checked_rules`。

Gate 3 不聚合最终判断、不写第 0 章摘要、不追加新 evidence anchors。

## 11. Deterministic fake LLM path

Gate 3 tests 应包含 deterministic fake LLM path，但只能在测试文件内：

- `_FakeWriterLLMClient` 实现 `ChapterLLMClient.generate_chapter()`。
- `_FakeAuditLLMClient` 实现 `ChapterAuditLLMClient.audit_chapter()`。
- Fake writer 返回包含合法 `<!-- anchor:<anchor_id> -->` 与正文证据行的章节 markdown。
- Fake auditor 默认返回 `PASS|chapter|no issues`。
- 另设 fake auditor 返回 `REVIEWABLE|...` / malformed text 以测试 repair/fail paths。
- Fake clients 记录 requests，用于断言 writer/auditor 都收到显式 typed request。

Production injection remains explicit：

- `ChapterOrchestratorLLMClients(writer=..., auditor=...)` 是唯一 client 入口。
- Orchestrator 不提供 default fake，不从 config/env 创建真实 client。
- Gate 4 或更后续 provider gate 才能决定 CLI/config 如何构造 production clients。

## 12. Implementation slices

### Slice 1: Service contract and validation

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Implement:

- Literal aliases and public dataclasses from §7。
- `build_chapter_orchestration_input()`。
- policy validation: target chapters 1-6 only, unique, non-empty, retry/output positive。
- input validation: bundle/projection mutually exclusive, fund_code/report_year match。
- projection resolution helper using injected `ChapterFactProvider` only when input kind is `structured_bundle`。

Tests:

- accepts bundle input and projects requested chapters。
- accepts projection input without calling fact provider。
- rejects both bundle and projection。
- rejects neither bundle nor projection。
- rejects fund_code/report_year mismatch。
- rejects target chapter 0/7/duplicate/out-of-range。
- rejects negative retry budget / non-positive max output chars。

### Slice 2: Single chapter run and fail-closed mappings

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Implement:

- `orchestrate_chapters()` and `ChapterOrchestrator.orchestrate()`。
- sequential execution for target chapters。
- complete writer blocked mapping from §8.1。
- auditor unavailable early stop before writer when `run_llm_audit=True`。
- audit pass -> accepted draft/conclusion。
- audit fail/blocked -> repair decision scaffolding。
- LLM exception capture as `llm_exception`。

Tests:

- happy path accepts chapter 1 with fake writer/auditor。
- writer unavailable blocks and does not call auditor。
- auditor unavailable blocks before writer when `run_llm_audit=True`。
- every `ChapterWriteStopReason` maps to exactly one `ChapterRunStopReason`。
- writer exception becomes `llm_exception` and does not leak。
- auditor exception becomes `llm_exception` and records writer attempt。
- unknown fund type returns global blocked without writer calls。

### Slice 3: Repair loop and aggregate result

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Implement:

- `_decide_repair()`。
- retry loop with `max_repair_attempts`。
- map `patch` and `regenerate` to best-effort regenerate attempt only when §8.2 permits it。
- `max_repair_attempts=0` stops after initial audit failure without retry。
- stop on `needs_more_facts`。
- stop on budget exhausted。
- `fail_fast` skipping behavior。
- overall `accepted` / `partial` / `blocked` status.

Tests:

- first audit fail with repairable hint retries and second pass accepts。
- repair budget exhausted returns failed `repair_budget_exhausted`。
- `max_repair_attempts=0` does not retry after audit fail。
- auditor LLM_UNAVAILABLE issue returns stop and does not retry writer。
- `needs_more_facts` stops without retrying source access。
- `fail_fast=True` skips later chapters after first blocked。
- `fail_fast=False` continues later chapters and returns partial when one accepted and one failed。

### Slice 4: Accepted conclusions and exports/docs

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/__init__.py` if export pattern requires it。
- `fund_agent/README.md`
- `tests/README.md`
- implementation evidence artifact under `docs/reviews/`

Implement:

- deterministic conclusion extraction from `### 结论要点`。
- deterministic conclusion extraction from `## 结论要点`。
- fallback first 3 non-empty lines only after audit accepted。
- `MAX_ACCEPTED_CONCLUSION_CHARS = 500` hard cap with `conclusion_truncated` flag。
- exact package exports in `fund_agent/services/__init__.py`:
  - `ChapterOrchestrator`
  - `ChapterOrchestrationInput`
  - `ChapterOrchestrationResult`
  - `ChapterOrchestrationPolicy`
  - `ChapterOrchestratorLLMClients`
  - `build_chapter_orchestration_input`
  - `orchestrate_chapters`
- README updates limited to current implemented Service orchestrator contract and tests.

Tests:

- conclusion extraction stops before next `###` or `##` heading as specified。
- fallback first 3 non-empty lines works for accepted draft without conclusion heading。
- long conclusion is capped at 500 chars and sets `conclusion_truncated=True`。
- result includes accepted conclusions sorted by chapter order。
- result excludes chapter 0/7 generation while preserving conclusions for future Gate 4。

## 13. Validation commands

Gate 3 implementation changes runtime Service code and tests. Required validation:

```text
uv run ruff check .
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

```text
git diff --check
```

Expected assertions:

- Targeted Service tests cover validation, happy path, complete writer stop reason mapping, auditor unavailable early stop, auditor blocked, repair retry, budget exhausted, `max_repair_attempts=0`, `needs_more_facts`, fail_fast, unknown fund type, LLM exception and accepted conclusion extraction hard limits.
- Adjacent Fund primitive tests remain passing.
- Full suite coverage gate remains passing.
- No changes to golden fixture/answer/manifest, score, snapshot, quality gate, FQ0-FQ6 or final judgment.

## 14. Docs update plan

Implementation worker may update:

- `fund_agent/README.md` because Service-layer architecture and extension entry changed.
- `tests/README.md` because new `tests/services/test_chapter_orchestrator.py` tests are added.

Implementation worker must not update unless controller explicitly authorizes:

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Controller-only closeout after accepted implementation review should update:

- `docs/design.md` §5.4.1 current implemented status: Gate 3 orchestrator accepted locally as Service-layer policy, still no final assembler/chapter 0/CLI/dayu。
- `docs/current-startup-packet.md`: current gate Gate 3 accepted locally, next entry Gate 4。
- `docs/implementation-control.md`: accepted artifacts, validation summary, next entry point。

Docs must not claim MVP complete.

## 15. Review gates and stop conditions

Implementation must stop and report if:

- Any tracked dirty changes appear outside Gate 3 scope.
- Implementing orchestrator requires modifying Gate 2 writer/auditor contracts.
- Implementing repair instructions requires adding extra_payload or hidden prompt fields.
- Tests require changing template, golden, score, snapshot, quality gate, final judgment, CLI or deterministic analyze behavior.
- Real provider SDK/env/config/client construction is needed.
- Source probing, repository/PDF/cache/source helper access appears necessary.
- Target chapters 0/7 must be generated to pass tests.
- Host/Agent/dayu integration appears necessary.
- `docs/fund-analysis-template-draft.md` or `AGENTS.md` would need edits.

Plan review should verify:

- Service/Fund ownership is correct.
- Typed contracts have no `extra_payload`.
- Gate 3 cannot accidentally generate第 0/7 章。
- Repair policy is implementable with existing Gate 2 primitives.
- Failure states are explicit and fail closed.
- Fake LLM is tests-only.

## 16. Residual risks

| Risk | Disposition | Owner / next gate |
|---|---|---|
| No typed patch API; `patch` maps to best-effort regenerate with same writer input | Accepted for MVP safety; avoids ad hoc string patch. This may waste one writer call and fail again; tests should cover budget exhaustion | Future repair contract gate if regenerate success rate is near zero |
| No repair hint injection into writer prompt | Accepted; avoids hidden prompt fields and Gate 2 contract churn | Future Gate 2/3 contract extension |
| No final assembler / chapter 0 / chapter 7 output | Intentional non-goal | Gate 4 |
| No CLI `--use-llm` | Intentional non-goal | Gate 4 |
| No production LLM provider construction | Intentional; explicit injection only | Gate 4/provider config gate |
| LLM exceptions are coarse `llm_exception` | Accept for MVP; preserves fail-closed state | Future provider resilience gate |
| Chapter 5 cross-period evidence remains missing | Accept; no source probing in Gate 3 | Future cross-period data gate |
| E2 source verification remains deferred | Already accepted Gate 2 residual | Future Evidence Confirm gate |
| Host/Agent/dayu runtime absent | Intentional; deterministic Service orchestration only | Route C Gate 5 |
| `partial` result consumption is unresolved | Gate 3 must not treat partial as complete report; Gate 4 must decide reject/degrade/incomplete behavior | Gate 4 plan |

## 17. Next gates

- Gate 3 plan review / fix / re-review：review this plan before implementation.
- Gate 3 implementation：Service-owned `chapter_orchestrator` and write-audit-repair policy only.
- Gate 4：`final_chapter_assembler`、第 0 章 assembly、第 7 章 final judgment assembly and opt-in CLI `--use-llm`；必须显式裁决 `ChapterOrchestrationResult.status=="partial"` 时的 assembly 行为。
- Gate 5：optional Host/Agent/dayu integration using `dayu.host` / `dayu.engine`。
- Separate future gates：production LLM provider construction/config, Evidence Confirm E2, cross-period data, golden/strict correctness/promotion.

## 18. Completion report format for implementation

Implementation worker final report should include:

- Changed files。
- Public contracts added。
- Explicit confirmation that chapters 0/7, CLI `--use-llm`, Host/Agent/dayu, source probing, golden/quality/final judgment were untouched。
- Validation commands and results。
- Residual risks or blockers。
