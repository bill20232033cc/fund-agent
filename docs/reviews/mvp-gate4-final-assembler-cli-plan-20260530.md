# MVP Gate 4 final_chapter_assembler + chapter 0 + CLI --use-llm Plan

日期：2026-05-30
角色：AgentCodex planning worker
Gate：`MVP Gate 4: final_chapter_assembler + chapter 0 + CLI --use-llm plan gate`
分类：`heavy`
状态：planning artifact，未实现、未 commit、未 push、未 PR。

## 1. Source Of Truth Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/design.md` §5.4 / §5.4.1
- `docs/fund-analysis-template-draft.md` 第 0 章、第 7 章、`CHAPTER_CONTRACT`、`ITEM_RULE`
- `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md`
- `docs/reviews/mvp-gate2-chapter-writer-auditor-controller-judgment-20260530.md`
- `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md`
- 当前代码事实：
  - `fund_agent/fund/chapter_facts.py`
  - `fund_agent/fund/chapter_writer.py`
  - `fund_agent/fund/chapter_auditor.py`
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/ui/cli.py`
  - `fund_agent/services/__init__.py`
  - `pyproject.toml`

当前 branch：`codex/local-reconciliation`。

当前 workspace 已有 unrelated untracked review files。Gate 4 implementation 不得清理、删除或纳入无关 untracked artifacts。

## 2. Goal

实现 Route C Gate 4 的最小可接受生产边界：

1. 在 Service 层新增 `final_chapter_assembler.v1`，把 Gate 3 第 1-6 章 accepted drafts/conclusions、现有 `FinalJudgmentDecision` 和严格 assembly policy 组装成完整 LLM 路径报告。
2. 生成第 7 章“最终判断”但不改变现有 final judgment 语义：第 7 章只能渲染 `derive_final_judgment()` 已经给出的 `FinalJudgmentDecision`。
3. 生成第 0 章“投资要点概览”，且第 0 章只能消费第 1-7 章 accepted conclusions，禁止读取结构化 facts、PDF、repository、cache、source helper 或重新推断。
4. 在 `fund-analysis analyze` 增加显式 opt-in `--use-llm` 路径；不传该 flag 时，当前 deterministic `analyze` 输出、`checklist` 输出、quality gate、score、golden、FQ0-FQ6 和 final judgment 语义完全不变。

## 3. Non-Goals

- 不修改 golden fixtures、golden answers、manifests、score、snapshot、quality gate、FQ0-FQ6 或 promotion state。
- 不修改 `derive_final_judgment()`、`FinalJudgmentDecision` 语义或最终判断优先级。
- 不接入 Host/Agent/dayu，不创建 `fund_agent/host` 或 `fund_agent/agent`。
- 不读取 repository/PDF/cache/source helper/downloader/parser；Gate 4 只能消费已有 `StructuredFundDataBundle`、Gate 3 result 和 typed Service inputs。
- 不把业务参数放进 `extra_payload`。
- 不实现 promotion、push、PR、release。
- 不把 `ChapterOrchestrationResult(status="partial")` 当完整报告输出。
- 不为 CLI 默认路径引入 LLM、副作用或 provider 依赖。

## 4. Required Decisions

### 4.1 Gate 4 是否拆分 implementation slices

应拆分，且必须按以下顺序实施：

| Slice | 名称 | 目的 | 是否可独立 review |
|---|---|---|---|
| 4A | Service final assembler | 新增 `final_chapter_assembler.v1` typed contract、partial policy、第 7 章 deterministic assembly、第 0 章 accepted-conclusion-only assembly | 是 |
| 4B | Service LLM analyze use case | 在 `FundAnalysisService` 增加 `analyze_with_llm()`，串起现有 `_run_analysis_core()`、Gate 3 orchestrator 和 Gate 4 assembler | 是 |
| 4C | CLI opt-in + docs | `fund-analysis analyze --use-llm` 显式进入 LLM use case；默认 `analyze/checklist` 不变；更新 README/tests docs | 是 |
| 4D | production LLM provider construction | 不并入 4A/4B/4C；作为子 gate 或 residual，由 controller 决定是否立即开启 | 是 |

拆分原因：

- 4A 是纯 Service assembly contract，必须先稳定 partial/incomplete/final judgment/chapter 0 语义。
- 4B 才触碰现有 `FundAnalysisService` 分析核心复用，风险高于纯 assembler。
- 4C 触碰 UI/CLI 用户行为，必须在 Service contract 稳定后接入。
- 4D 涉及外部 provider、secret/config、模型选择、网络失败和依赖策略，应独立 review；否则会把 assembly 语义和 provider 运维问题混在一起。

### 4.2 final_chapter_assembler 属于 Fund 还是 Service

属于 Service。

理由：

- `AGENTS.md` 规定 Service 负责业务用例编排、报告生成、质量策略选择和 prompt/ExecutionContract 组装。
- Gate 3 `ChapterOrchestrator` 已是 Service 层 write-audit-repair facade，输出 accepted chapter conclusions 供 Gate 4 使用。
- final assembler 不理解基金类型、年报章节、ITEM_RULE 或 preferred_lens 的领域规则；它只消费已 accepted 的章节结果和现有最终判断 contract。
- Fund 层继续拥有：CHAPTER_CONTRACT / ITEM_RULE / preferred_lens、single chapter writer/auditor、证据锚点和基金领域规则。

禁止把 final assembler 放入 `fund_agent/fund`，也禁止让 assembler 读取 PDF/repository/source helper。

### 4.3 typed input/output contract

新增文件：`fund_agent/services/final_chapter_assembler.py`。

建议 public schema：

```python
FinalChapterAssemblerSchemaVersion = Literal["final_chapter_assembler.v1"]
FinalAssemblyStatus = Literal["accepted", "incomplete", "blocked"]
FinalAssemblyIssueReason = Literal[
    "orchestration_not_accepted",
    "missing_required_chapter",
    "duplicate_chapter",
    "missing_accepted_draft",
    "missing_accepted_conclusion",
    "final_judgment_missing",
    "chapter0_source_missing",
    "chapter0_contract_violation",
    "chapter7_contract_violation",
]
```

新增 dataclasses：

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyPolicy:
    require_orchestration_accepted: bool = True
    required_body_chapter_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    include_chapter0: bool = True
    include_chapter7: bool = True
    allow_incomplete_debug_markdown: bool = False
    max_chapter0_chars: int = 5000
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class FinalChapterAssemblyInput:
    fund_code: str
    report_year: int
    orchestration_result: ChapterOrchestrationResult
    final_judgment_decision: FinalJudgmentDecision
    policy: FinalAssemblyPolicy = field(default_factory=FinalAssemblyPolicy)
    schema_version: Literal["final_chapter_assembler.v1"] = "final_chapter_assembler.v1"
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyIssue:
    issue_id: str
    severity: Literal["blocking", "informational"]
    reason: FinalAssemblyIssueReason
    message: str
    chapter_ids: tuple[int, ...] = ()
```

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class FinalChapterAssemblyResult:
    status: FinalAssemblyStatus
    fund_code: str
    report_year: int
    report_markdown: str | None
    chapter0_markdown: str | None
    chapter7_markdown: str | None
    assembled_chapter_ids: tuple[int, ...]
    source_accepted_chapter_ids: tuple[int, ...]
    final_judgment_selected: FinalJudgment
    issues: tuple[FinalAssemblyIssue, ...]
    schema_version: Literal["final_chapter_assembler.v1"] = "final_chapter_assembler.v1"
```

Public API：

```python
class FinalChapterAssembler:
    def assemble(self, input_data: FinalChapterAssemblyInput) -> FinalChapterAssemblyResult: ...

def assemble_final_chapters(input_data: FinalChapterAssemblyInput) -> FinalChapterAssemblyResult: ...
```

Contract rules：

- `input_data.fund_code/report_year` 必须与 `orchestration_result.fund_code/report_year` 一致。
- `required_body_chapter_ids` 默认必须唯一等于 `(1,2,3,4,5,6)`。
- `orchestration_result.status != "accepted"` 时默认返回 `status="incomplete"`，`report_markdown=None`。
- 每个 required chapter 必须有 `ChapterRunResult.status == "accepted"`、`accepted_draft != None`、`accepted_conclusion != None`。
- final assembler 不接收 `StructuredFundDataBundle`、`ChapterFactProjection`、PDF path、repository、source helper 或 `extra_payload`。

### 4.4 第 0 章如何只总结 accepted chapter conclusions

第 0 章必须由 Service assembler 在第 7 章 accepted conclusion 生成之后再生成。

数据流：

```text
Gate 3 accepted chapters 1-6
  -> deterministic chapter 7 assembly from existing FinalJudgmentDecision
  -> synthetic AcceptedChapterConclusion(chapter_id=7)
  -> chapter 0 assembly from AcceptedChapterConclusion(1-7) only
```

实现约束：

- 第 0 章 assembly helper 的函数签名只能接收 `tuple[AcceptedChapterConclusion, ...]` 和 `FinalAssemblyPolicy` 中的输出限制；不得接收 `StructuredFundDataBundle`、`ChapterFactProjection`、`FinalJudgmentDecision`、facts、anchors 或 extractor result。
- 第 0 章不调用 LLM provider。MVP 采用 deterministic assembly，原因是模板第 0 章要求“只总结 accepted conclusions，不引入新事实”，确定性摘取比 LLM 总结更容易 fail-closed。
- 第 0 章必须拒绝缺少第 7 章 accepted conclusion 的输入，因为“当前动作 / 升级降级阈值 / 下一步验证”应来自最终判断章，而不是重新推断。
- 第 0 章不得输出“证据与出处”小节、不得输出新的证据行、不得生成新的 anchor marker。
- 第 0 章允许复制 accepted conclusion 中已经存在的数值、判断和短句；不允许新增 accepted conclusions 中不存在的数值、百分比、基金经理名字、规模、时间或风险阈值。
- 若某 required output item 无法从 accepted conclusions 中确定，输出“见第 N 章 accepted conclusion，当前缺少可压缩为封面项的结论”，并记录 informational issue；不得自行补事实。

推荐 deterministic mapping：

| 第 0 章 required item | 来源 |
|---|---|
| 一句话这是什么基金 | 第 1 章 accepted conclusion |
| 基金简介 | 第 1 章 accepted conclusion；缺失则写“见第 1 章产品画像” |
| 当前动作 | 第 7 章 accepted conclusion 的 `最终判断` 行 |
| 当前业绩与运作状态 | 第 2/4/5 章 accepted conclusion；按可用性取第一条 |
| 支撑当前动作的最主要理由 | 第 7 章 accepted conclusion 的核心依据 |
| 当前最值得盯住的变量 | 第 7 章下一轮验证计划或第 6 章主要风险 |
| 当前最大的风险 | 第 6 章 accepted conclusion；缺失则第 7 章“最容易看错” |
| 下一步最小验证问题 | 第 7 章 accepted conclusion |
| 什么变化会升级、降级或终止当前动作 | 第 7 章阈值事件 |

### 4.5 第 7 章 / final judgment 是否纳入本 gate

纳入本 gate，但只纳入“第 7 章 assembly”，不纳入 final judgment 语义变更。

第 7 章实现规则：

- `FinalJudgmentDecision.selected_judgment` 是唯一最终动作真源。
- 第 7 章不得从 LLM、accepted conclusions 或自然语言重新选择 `worth_holding / needs_attention / suggest_replace`。
- 第 7 章不得调用或修改 `derive_final_judgment()`。
- 第 7 章 markdown 必须包含模板 required output items：
  - 最终判断
  - 支撑判断的核心依据
  - 当前最容易看错的地方
  - 下一轮最小验证计划
  - 升级/降级阈值
- `最终判断` 展示映射固定为：
  - `worth_holding` -> `🟢 值得持有`
  - `needs_attention` -> `🟡 需要关注`
  - `suggest_replace` -> `🔴 建议替换`
- `支撑判断的核心依据` 只能使用 `FinalJudgmentDecision.reasons` 和第 1-6 章 accepted conclusions 中的已有结论短句。
- 如果 `FinalJudgmentDecision.source == "developer_override"`，第 7 章必须显式保留 override source 和 conflict reasons；不得把 override 伪装成系统派生。
- 不输出买入金额、卖出时机、仓位比例或收益预测。

Residual：

- 第 7 章 LLM polish、LLM audit、Evidence Confirm/E2 源文核验不是本 gate。
- 如果 review 认为 deterministic 第 7 章不满足模板表达质量，可在后续开“chapter7 writer/auditor with accepted-conclusion facts”独立 gate，但不得在本 gate 修改 final judgment semantics。

### 4.6 CLI `--use-llm` opt-in 如何接入

CLI 行为：

- `fund-analysis analyze FUND_CODE` 不传 `--use-llm`：完全沿用当前 `FundAnalysisService().analyze(request)`，stdout/stderr/exit code 不变。
- `fund-analysis checklist FUND_CODE`：不增加 `--use-llm`，保持 deterministic checklist。
- `fund-analysis analyze FUND_CODE --use-llm`：调用新 Service use case `FundAnalysisService().analyze_with_llm(...)`。

Service 建议 API：

```python
@dataclass(frozen=True, slots=True)
class FundLLMAnalysisResult:
    deterministic_core: FundAnalysisResult | None
    llm_orchestration_result: ChapterOrchestrationResult
    final_assembly_result: FinalChapterAssemblyResult
    quality_gate_result: QualityGateResult | None = None
    quality_gate_not_run_reason: str | None = None

    @property
    def report_markdown(self) -> str:
        ...
```

更小实现可不嵌套完整 `FundAnalysisResult`，但必须保留 deterministic core 中的：

- `structured_data`
- `final_judgment_decision`
- `quality_gate_result`
- `quality_gate_not_run_reason`

新增 method：

```python
async def analyze_with_llm(
    self,
    request: FundAnalysisRequest,
    *,
    llm_clients: ChapterOrchestratorLLMClients,
    chapter_policy: ChapterOrchestrationPolicy | None = None,
    assembly_policy: FinalAssemblyPolicy | None = None,
) -> FundLLMAnalysisResult:
    ...
```

Implementation sequence inside `analyze_with_llm()`：

1. 调用现有 `_run_analysis_core(replace(request, command_source="analyze"))`，复用 extraction、quality gate、final judgment 派生、温度计和 checklist。
2. 用 `core_result.structured_data` 构造 `build_chapter_orchestration_input(...)`。
3. 调用 `orchestrate_chapters(..., llm_clients=...)` 生成第 1-6 章。
4. 调用 `assemble_final_chapters(...)` 生成第 7/0 章和最终 report。
5. 返回 typed result；不在 Service 中 fallback 到 deterministic report。

CLI provider handling：

- Slice 4C 可以先接入 `--use-llm` flag 和 Service branching，但不得注入 fake pass。
- 如果 production provider construction 仍未完成，`--use-llm` 必须 fail-closed，stderr 输出“LLM provider 未配置/未实现”，exit code `1`，不得静默回落到 deterministic report。
- 后续 provider 子 gate 完成后，CLI 再从明确 config/env 构造真实 `ChapterOrchestratorLLMClients`。

### 4.7 partial ChapterOrchestrationResult reject/degrade/incomplete policy

默认 policy：reject as incomplete。

| Orchestration status | Accepted chapter count | Assembly behavior | CLI `--use-llm` behavior |
|---|---:|---|---|
| `accepted` | 6/6 required | 进入第 7/0 assembly | 输出 LLM report |
| `partial` | 1-5/6 | `FinalAssemblyResult(status="incomplete", report_markdown=None)` | stderr 说明 incomplete，exit `1` |
| `blocked` | 0/6 | `FinalAssemblyResult(status="blocked", report_markdown=None)` | stderr 说明 blocked，exit `1` |

禁止 degrade 行为：

- 不允许把 partial report 拼成“完整报告”。
- 不允许在 `--use-llm` 下静默 fallback 到 deterministic report。
- 不允许输出缺章但标题完整的报告。

允许的 debug 行为：

- `FinalAssemblyPolicy.allow_incomplete_debug_markdown=True` 时，可在 tests 或开发调用中返回 `incomplete_debug_markdown`（如果实现者选择添加该字段），但 CLI 默认不得启用。
- debug markdown 必须显式标注“INCOMPLETE / NOT A COMPLETE REPORT”，不得通过 `report_markdown` 属性暴露。

### 4.8 production LLM provider construction 是本 gate、子 gate还是 residual

建议作为 Gate 4D 子 gate，不并入 4A/4B/4C。

裁决：

- 4A/4B/4C 必须做到 provider-agnostic：只通过 `ChapterOrchestratorLLMClients` 显式注入 writer/auditor clients。
- production provider construction 涉及外部模型供应商、secret/env/config、超时、重试、错误分类、依赖、成本和 live smoke，不应阻塞 assembler contract review。
- 若 controller 要求 `fund-analysis analyze --use-llm` 在本 MVP gate 后真实可运行，则必须紧接着开 4D 子 gate；否则 4D 记录为 residual，`--use-llm` fail-closed。

4D 子 gate 最小 scope：

- 新增 provider factory，位置建议 `fund_agent/services/llm_clients.py` 或 `fund_agent/config/llm.py` + Service adapter。
- 使用已有 `httpx` 或经独立 review 后新增 provider SDK；不得在 Fund writer/auditor 中导入 SDK。
- 显式 config/env 参数：provider name、model、base URL、API key env var、timeout、max output chars；不得通过 `extra_payload`。
- 测试只用 fake HTTP/client，不依赖真实网络。
- live smoke 只能作为人工验证或单独 evidence artifact，不能进入常规 pytest。

如果 4D 不做，本 Gate 4 closeout 必须把“production LLM provider construction remains residual”写回 control docs。

## 5. Implementation Slices

### Slice 4A: Service final assembler

Allowed files：

- 新增 `fund_agent/services/final_chapter_assembler.py`
- 更新 `fund_agent/services/__init__.py`
- 新增 `tests/services/test_final_chapter_assembler.py`
- 必要时更新 `tests/README.md`

Do not edit：

- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/analysis/final_judgment.py`
- `fund_agent/fund/template/renderer.py`

Implementation steps：

1. 定义 typed schema/dataclasses/API。
2. 实现 `_validate_assembly_input()`：
   - schema version check
   - identity check
   - required body chapter ids uniqueness
   - orchestration accepted check
   - accepted draft/conclusion presence check
3. 实现 `_build_chapter7_markdown()`：
   - 只消费 `FinalJudgmentDecision` 和第 1-6 章 accepted conclusions
   - 固定 judgment label mapping
   - 保留 `reasons/conflict_reasons/source`
4. 实现 `_chapter7_conclusion()`：
   - 构造 `AcceptedChapterConclusion(chapter_id=7, ...)`
   - `used_fact_ids/used_anchor_ids` 聚合自第 1-6 章 accepted conclusions，不新增 fact/anchor
5. 实现 `_build_chapter0_markdown()`：
   - 只接收第 1-7 章 accepted conclusions
   - 不输出证据小节/anchor marker
   - 缺项写缺口，不补事实
6. 实现 `_assemble_report_markdown()`：
   - 顺序固定：0, 1, 2, 3, 4, 5, 6, 7
   - 第 1-6 章使用 `accepted_draft.markdown`
7. 所有函数、类、模块提供中文 docstring。

Tests：

- accepted 1-6 + final judgment -> `status="accepted"`，chapter ids `(0,1,2,3,4,5,6,7)`。
- `orchestration.status="partial"` -> `status="incomplete"`，`report_markdown is None`。
- missing chapter 4 accepted draft -> incomplete/blocking issue。
- duplicated required chapter ids -> `ValueError`。
- identity mismatch -> `ValueError`。
- chapter 7 uses exact `FinalJudgmentDecision.selected_judgment` label；不重新派生。
- developer override conflict reasons preserved。
- chapter 0 helper cannot access facts: test should construct only `AcceptedChapterConclusion` inputs and assert no structured bundle/projection is required。
- chapter 0 output has no `证据与出处`、no `> 📎 证据`、no `<!-- anchor:`。
- chapter 0 missing source item records issue instead of inventing content。

### Slice 4B: Service LLM analyze use case

Allowed files：

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- 新增 `tests/services/test_fund_analysis_service_llm.py`
- 可更新 `fund_agent/README.md`（Service boundary fact）
- 可更新 `tests/README.md`

Implementation steps：

1. 增加 `FundLLMAnalysisResult` dataclass。
2. 增加 `FundAnalysisService.analyze_with_llm(...)`，所有 LLM clients 通过 keyword-only explicit parameter 传入。
3. 复用 `_run_analysis_core()`，不要复制 extraction/quality gate/final judgment 逻辑。
4. 用 `ChapterOrchestrationPolicy(target_chapter_ids=(1,2,3,4,5,6))` 默认执行 Gate 3。
5. 对 orchestration accepted/partial/blocked 都调用 assembler，让 assembler 负责 incomplete policy。
6. 不修改 `analyze()` 和 `checklist()` 默认行为。

Tests：

- fake extractor + fake writer/auditor -> `analyze_with_llm()` 返回 accepted final assembly。
- `analyze()` deterministic test 仍通过，且未调用 chapter orchestrator。
- `checklist()` deterministic test 仍通过，且没有 LLM path。
- missing writer/auditor client -> typed blocked/incomplete，不 fallback deterministic。
- quality gate block/not-run 仍在 `_run_analysis_core()` 阶段按现有异常阻断。
- no repository/PDF/source helper imports in new Service path beyond existing `FundDataExtractor` transition path。

### Slice 4C: CLI opt-in + docs

Allowed files：

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `README.md`
- `tests/README.md`
- 如 Service exports 仍缺：`fund_agent/services/__init__.py`

Implementation steps：

1. 给 `analyze` command 增加：

```python
use_llm: Annotated[bool, typer.Option("--use-llm", help="显式启用 Route C LLM 分章写作路径")] = False
```

2. `use_llm is False` 时保持当前 code path 逐行等价：构造同一个 `FundAnalysisRequest`，调用 `FundAnalysisService().analyze(request)`。
3. `use_llm is True` 时调用 `FundAnalysisService().analyze_with_llm(...)`。
4. 若 4D 未实现 provider construction，则 CLI 必须在进入 Service 前 fail-closed，或用 provider factory 返回明确 unavailable error；不得传 fake client。
5. `checklist` 不增加 `--use-llm`。
6. `_echo_quality_gate_summary()` 可复用；stdout 只输出 accepted final assembly 的 report markdown。

Tests：

- `fund-analysis analyze 110011` 不传 `--use-llm`：仍调用 fake service `.analyze()`，stdout 是 deterministic fake report。
- `fund-analysis analyze 110011 --use-llm`：调用 fake service `.analyze_with_llm()`。
- `fund-analysis checklist 110011 --use-llm`：Typer 报未知参数或不接受该 flag。
- `--use-llm` provider unavailable：exit `1`，stderr 清楚说明 provider 未配置/未实现，不输出 deterministic report。
- quality gate blocked/not-run handling for deterministic path不变。

### Slice 4D: production provider construction sub gate / residual

本 plan 不授权 4D 直接 implementation。controller 必须在 4A-4C review 后二选一：

1. 开子 gate：`MVP Gate 4D: production LLM provider construction`
2. 记录 residual：`CLI --use-llm is wired but provider construction remains residual; opt-in path fail-closed`

如果开 4D，必须先补一份 provider-specific implementation plan/review，不得让 implementation worker 在 4A-4C 中自行选择供应商、SDK、env var 或重试策略。

## 6. Validation Matrix

每个 implementation slice 后至少运行：

```text
uv run ruff check fund_agent/services/final_chapter_assembler.py tests/services/test_final_chapter_assembler.py
uv run pytest tests/services/test_final_chapter_assembler.py -q
```

Slice 4B 后运行：

```text
uv run pytest tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service.py tests/services/test_fund_analysis_service_llm.py -q
```

Slice 4C 后运行：

```text
uv run pytest tests/ui/test_cli.py -q
```

Regression guard：

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py -q
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
git diff --check
```

Static boundary checks：

```text
rg -n "dayu|extra_payload|openai|anthropic|pdf|cache|source helper|download" fund_agent/services/final_chapter_assembler.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py
```

Expected:

- no `dayu`
- no `extra_payload`
- no provider SDK import unless 4D sub gate explicitly accepted
- no PDF/cache/source helper direct access in final assembler or CLI LLM branch

## 7. Review Matrix

Gate 4 remains `heavy` because it touches Service report generation, CLI user behavior and final report assembly.

Required review gates：

| Gate | Required reviewers | Artifact |
|---|---|---|
| Plan review | at least 2 independent reviewers, recommended AgentMiMo + AgentDS/GLM | `docs/reviews/mvp-gate4-final-assembler-cli-plan-review-*.md` |
| Plan decision | controller | `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md` |
| Slice 4A implementation review | at least 2 independent reviewers | `docs/reviews/mvp-gate4-final-assembler-implementation-review-*.md` |
| Slice 4B implementation review | at least 2 independent reviewers | `docs/reviews/mvp-gate4-llm-service-implementation-review-*.md` |
| Slice 4C implementation review | at least 2 independent reviewers | `docs/reviews/mvp-gate4-cli-use-llm-implementation-review-*.md` |
| Aggregate deepreview | after all accepted slices | `$deepreview --base main` artifact |

Review focus：

- partial/incomplete policy cannot leak incomplete reports as complete.
- chapter 0 has no inputs except accepted conclusions.
- chapter 7 does not alter final judgment semantics.
- deterministic `analyze/checklist` default behavior remains unchanged.
- CLI `--use-llm` does not fake success when provider is absent.
- no direct repository/PDF/cache/source helper access.
- no Host/Agent/dayu.
- no golden/quality/score/FQ/final judgment semantic changes.

## 8. Documentation Updates

Only after tests pass:

- `README.md`
  - Add `fund-analysis analyze --use-llm` as explicit experimental opt-in only if implemented.
  - State deterministic `fund-analysis analyze` remains default.
  - If 4D not implemented, document that `--use-llm` currently fail-closes until provider configuration gate lands.
- `fund_agent/README.md`
  - Add current Service boundary fact: `analyze_with_llm()` is Service orchestration around Gate 3 + Gate 4, not Host/Agent/dayu.
- `tests/README.md`
  - Add final assembler and CLI opt-in test locations.
- `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
  - Controller closeout only: mark Gate 4 accepted locally and record remaining 4D/provider residual if not implemented.

Do not update `docs/fund-analysis-template-draft.md`.

## 9. Stop Conditions

Implementation must stop and return to controller if any occurs：

- Implementation requires changing `derive_final_judgment()` or final judgment priority rules.
- Implementation requires modifying golden/score/FQ0-FQ6/quality gate semantics.
- CLI `--use-llm` cannot be implemented without choosing a production provider strategy.
- A partial orchestration result is needed for user-visible output.
- Chapter 0 cannot satisfy required output items without reading structured facts directly.
- Any plan requires Host/Agent/dayu.
- Any code path wants to access repository/PDF/cache/source helper directly from Service/CLI/assembler.
- Tests require network/live LLM calls.

## 10. Completion Report Format

Implementation worker should report:

- slices completed
- files changed
- whether 4D provider construction was implemented, opened as sub gate, or left residual
- validation commands and exact results
- explicit confirmation:
  - deterministic `analyze` default unchanged
  - `checklist` unchanged
  - no final judgment semantic change
  - no golden/score/quality/FQ changes
  - no Host/Agent/dayu
  - no repository/PDF/cache/source helper direct access
- residual risks and next entry point
