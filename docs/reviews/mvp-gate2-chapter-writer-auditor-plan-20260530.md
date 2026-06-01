# MVP Gate 2: chapter_writer + chapter_auditor plan

日期：2026-05-30

角色：Gateflow planning specialist。本文只写 code-generation-ready plan，不实现、不提交、不 push、不开 PR、不做 release/promotion。

## 1. Gate 定位

Gate：`MVP Gate 2: chapter_writer + chapter_auditor`

分类：`heavy`。理由：本 gate 新增 LLM 章节写作/审计输入输出公共契约，影响 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点和 fail-closed 语义。按 `AGENTS.md`，分类不确定时选择更重一级。

目标：在 Fund 层新增最小安全的章节写作与章节审计能力，让 writer/auditor 只消费 Gate 1 `ChapterFactProjection` / `ChapterFactInput`，为后续 Gate 3 Service-owned `chapter_orchestrator` 和 write-audit-repair policy 提供 typed building blocks。

本 gate 不接入生产 CLI，不改变 deterministic `fund-analysis analyze/checklist`，不实现 orchestrator、repair loop、final assembler、chapter 0 assembly 或 Host/Agent/dayu runtime。

## 2. Preflight 事实

- 当前分支：`codex/local-reconciliation`。
- `git status --short` 只有既有未跟踪文件；`git status --short --untracked-files=no` 为空，未见 tracked dirty。
- 当前控制面：`docs/current-startup-packet.md` 和 `docs/implementation-control.md` 均指向 `MVP Gate 2: chapter_writer + chapter_auditor plan gate`。
- Gate 1 已由 controller accepted locally：`4eae4ad`，并新增 Fund 层 `chapter_fact_projection.v1`。
- 本计划未把任何既有未跟踪 artifact 纳入证据，后续 implementation 也不得 stage/delete unrelated untracked files。

## 3. 已读真源与直接证据

- `AGENTS.md`
  - 目标边界固定为 `UI -> Service -> Host -> Agent`。
  - `fund_agent/fund` 是当前 Agent 层基金领域能力包，拥有基金类型、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、审计规则和证据锚点语义。
  - 所有显式业务参数必须声明在 typed request / contract / config 中，禁止藏入 `extra_payload`。
  - 生产年报访问必须经过 `FundDocumentRepository`；Service/UI/Host/renderer/quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
- `docs/current-startup-packet.md`
  - 当前生产路径仍是 deterministic `fund-analysis analyze/checklist`。
  - Gate 2 scope 是 `chapter_writer` + `chapter_auditor`。
  - 当前没有 LLM chapter writing、LLM audit、write-audit-repair loop、chapter orchestrator、final LLM assembler、CLI `--use-llm`、Host/Agent/dayu runtime。
- `docs/design.md` §5.4 / §5.4.1 / §5.4.3
  - 章节写作和审计只能消费 structured facts、derived calculations、explicit data gaps 和 EvidenceAnchor。
  - 每条关键判断必须绑定 `EvidenceAnchor` 或 derived 计算来源；没有同源证据时只能写“未披露 / 数据不足 / 下一步最小验证问题”。
  - 规则审计负责结构、锚点、CHAPTER_CONTRACT / ITEM_RULE、数值闭合与边界条件；LLM 审计负责证据是否支撑断言、语义越界、投资建议措辞和读者可理解性。
  - Gate 3 才引入 Service-owned write-audit-repair policy；Gate 4 才引入 final assembler、chapter 0 assembly 和 CLI `--use-llm`。
- `docs/fund-analysis-template-draft.md`
  - 当前模板是第 0-7 章。
  - CHAPTER_CONTRACT 规定每章 `must_answer`、`must_not_cover`、`required_output_items`、`preferred_lens`。
  - ITEM_RULE 当前覆盖第 1/2 章条件条目，规则不满足时必须删除对应内容，不得输出占位或暗示内容存在。
  - 正文证据格式为 `> 📎 证据：年报§[章节] [内容描述]`，附录汇总格式为 `年报[年份]§[章节]表[编号]行[行号]`。
- Gate 1 artifacts
  - `docs/reviews/mvp-gate1-chapter-fact-provider-plan-20260530.md`
  - `docs/reviews/mvp-gate1-chapter-fact-provider-implementation-evidence-20260530.md`
  - `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md`
  - Gate 1 accepted public API：`project_chapter_facts()` / `ChapterFactProvider.project()`。
  - Gate 1 output：`ChapterFactProjection` -> `ChapterFactInput`，包含 contract、fund_type、classification_basis、facet_resolution、lens_resolution、item_rule_projection、facts、evidence_anchors、missing_reasons、source_field_ids。
  - Gate 1 明确不读取 repository/PDF/cache/source helper/parser/LLM/Service/Host/dayu。

## 4. 当前事实

- Fund 层已有 `fund_agent/fund/chapter_facts.py`，schema version 为 `chapter_fact_projection.v1`。
- `ChapterFactEntry.status` 闭集包含 `available`、`missing`、`not_applicable`、`unavailable`、`unknown`。
- `ChapterFactMissingReason` 已包含 `classified_fund_type_missing`、`classified_fund_type_invalid`、`field_missing`、`field_not_applicable`、`field_unavailable`、`evidence_missing`、`accepted_chapter_conclusions_missing`、`cross_period_comparison_missing`、`unsupported_facet_inference`。
- `fund_type="unknown"` 时 Gate 1 跳过 preferred_lens 和 ITEM_RULE 有效路径。
- exact `facets` 当前保持 fail-closed；兼容标签只能进入 `non_asserted_facets`，不得驱动 ITEM_RULE。
- `bond_risk_evidence` 的组级 anchors 保留在 `value.anchors`，未展开为普通 `ChapterEvidenceAnchor`。
- 现有 `fund_agent/fund/audit/audit_programmatic.py` 是 deterministic renderer 后的程序审计，不是 Gate 2 LLM semantic audit。
- 现有 `fund_agent/fund/report_writing_audit.py` 是 dev-only 写作审计，不接入产品链路；Gate 2 可以复用其已验证的禁用措辞思想，但不得把它包装成完整 LLM audit 已实现。

## 4.1 Review Finding Disposition

本 plan-fix pass 已读取并处理：

- `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-mimo-20260530.md`
- `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-glm-20260530.md`
- `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-ds-20260530.md`

| Finding | Disposition | Plan change |
|---|---|---|
| MiMo-01 / DS-07 writer anchor ref parsing 未冻结 | Fixed | §7.5 固定 `<!-- anchor:<anchor_id> -->` 精确格式、解析规则、unknown/invalid 行为和 hard max length post-check |
| MiMo-02 / DS-07 LLM audit 输出解析未冻结 | Fixed | §8.4 固定 `audit_focus` 默认值、`SEVERITY\|LOCATION\|MESSAGE` 行格式、parse failure blocked 行为和 pass 语义 |
| MiMo-03 / GLM-F1 prompt_only stop_reason 歧义 | Fixed | §7.1 增加 `prompt_only` literal；§7.4 固定 `status="blocked"`、`stop_reason="prompt_only"`、`draft=None` |
| GLM-F2 chapter 5 cross-period 检测欠规格 | Fixed | §9 增加 chapter 5 `cross_period_comparison_missing` 稳定/变化短语与否定前缀检测策略 |
| DS-01 evidence_missing critical judgment 算法缺失 | Fixed | §7.4 增加 `_fact_supports_critical_judgment()` 判定规则，基于 `required_by` 和数值/source field ids |
| DS-02 `declared_missing_reasons` 提取机制缺失 | Fixed | §7.5 固定 `<!-- missing:<reason> -->` 精确格式、允许集合和 invalid 行为 |
| DS-03 `repair_hint` 聚合规则缺失 | Fixed | §9 增加 `needs_more_facts > regenerate > patch > none` 聚合优先级 |
| DS-04 `non_asserted_facets` 误用未审计 | Fixed | §9 增加 deterministic C2 检查，禁止候选 facet 被写成已断言事实 |
| DS-05 E2 缺席需显式 deferred | Fixed | §9 / §17 明确 E2 evidence-vs-assertion source verification 延后到 Evidence Confirm gate |
| DS-06 `bond_risk_evidence` 内部锚点错误消息 | Fixed | §7.5 / §10 / Slice 2 要求 unknown anchor 疑似来自 `bond_risk_evidence.value.anchors` 时给出专门错误消息 |
| MiMo-04 / GLM-F3 docs/control update scope | Fixed | §6 / §12 / §15 将 `docs/design.md`、startup/control doc 更新移出 implementation slices，仅保留 controller closeout |
| MiMo-05 value serialization | Accepted residual | §17 继续作为 residual，implementation evidence 需记录 conservative serialization 策略 |

## 5. Non-goals

本 gate 明确不做：

- 不实现 `chapter_orchestrator`。
- 不实现 write-audit-repair loop、patch/regenerate policy、重试策略或多章调度。
- 不实现 final chapter assembler。
- 不生成或装配第 0 章；第 0 章依赖后续 accepted chapters，本 gate 只定义其输入缺口和 fail-closed 行为。
- 不实现 CLI `--use-llm`，不改变 `fund-analysis analyze/checklist`。
- 不新增 Service orchestration；Service-owned strategy/policy 放到 Gate 3。
- 不新增 Host/Agent/dayu package、dependency、runner、ToolRegistry、ToolTrace、session/run lifecycle、并发、取消、恢复、outbox。
- 不读取或调用 `FundDocumentRepository`、PDF/cache/source helper/downloader/parser、外部网站或文件系统文档。
- 不修改 `docs/fund-analysis-template-draft.md`、`AGENTS.md`。
- 不修改 golden fixtures/answers/manifests、score、snapshot、quality gate、FQ0-FQ6、final judgment、promotion state。
- 不运行 promotion、release readiness、snapshot refresh 或 strict correctness rerun。
- 不把 LLM client 缺失时的 stub 输出伪装为正确章节或已通过审计。

## 6. 推荐总体方案

新增 Fund 层模块：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`

可选最小同步：

- `fund_agent/fund/__init__.py`：仅当仓库当前导出模式需要 package-level export 时更新。
- `fund_agent/fund/README.md`：实现完成后只记录当前 Fund public capability，不写 orchestrator/CLI/dayu 已实现。
- `tests/README.md`：实现完成后只记录新增 targeted tests。

控制面同步不属于 implementation worker 的 slice：

- `docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md` 只能由 controller closeout 或 controller 明确追加授权后更新。
- 本 Gate 2 implementation worker 的 docs scope 默认只包括 `fund_agent/fund/README.md` 和 `tests/README.md`。

核心决策：

- writer/auditor 属于 Fund 层，因为它们理解 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点和基金专项禁用边界。
- LLM 调用通过显式注入的 typed Protocol 完成；Fund 模块不读取环境变量、不加载全局配置、不直接依赖 OpenAI/HTTP SDK。
- 缺少 LLM client/config 时 fail closed，返回 blocked result；只允许生成 prompt/debug contract，不允许输出 accepted markdown。
- programmatic audit 与 LLM audit 分离：programmatic audit 是确定性结构/证据/边界检查；LLM audit 是通过注入 client 进行语义复核，缺 client 时返回 `llm_unavailable`，不得 fake pass。
- Gate 2 只提供单章 primitive。多章排序、repair loop、重试、accepted chapters 状态机和 Service use-case policy 都属于 Gate 3。

## 7. Writer contract

新增 `fund_agent/fund/chapter_writer.py`。所有 public dataclass 使用 `frozen=True, slots=True`。所有函数/类必须有完整中文 docstring，并引用模板第 0-7 章。

### 7.1 Literal aliases

```python
ChapterWriterSchemaVersion = Literal["chapter_writer.v1"]
ChapterWriteStatus = Literal["drafted", "blocked"]
ChapterWriteStopReason = Literal[
    "none",
    "fund_type_unknown",
    "missing_required_facts",
    "evidence_anchor_missing",
    "item_rule_deleted_required_content",
    "chapter_requires_accepted_conclusions",
    "prompt_only",
    "llm_unavailable",
    "llm_empty_response",
    "llm_contract_violation",
]
ChapterWriterMode = Literal["llm", "prompt_only"]
ChapterCitationStyle = Literal["body_quote"]
```

### 7.2 LLM Protocol

```python
@dataclass(frozen=True, slots=True)
class ChapterLLMRequest:
    schema_version: Literal["chapter_llm_request.v1"]
    chapter_id: int
    fund_code: str
    report_year: int
    system_prompt: str
    user_prompt: str
    required_anchor_ids: tuple[str, ...]
    forbidden_phrases: tuple[str, ...]
    max_output_chars: int

@dataclass(frozen=True, slots=True)
class ChapterLLMResponse:
    schema_version: Literal["chapter_llm_response.v1"]
    text: str
    model_name: str | None
    finish_reason: str | None

class ChapterLLMClient(Protocol):
    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        ...
```

约束：

- `ChapterLLMClient` 只作为 Protocol，不实现 OpenAI/HTTP client。
- 不读取 env/config，不做 retry，不做 streaming，不做 concurrency。
- 所有参数显式在 `ChapterLLMRequest` / `ChapterWriterInput` 声明，禁止 `extra_payload`。
- tests 使用 fake client；fake client 只能返回测试 fixture 文本，不得进入生产 fallback。

### 7.3 Writer dataclasses

```python
@dataclass(frozen=True, slots=True)
class ChapterWriterInput:
    schema_version: ChapterWriterSchemaVersion
    projection_schema_version: ChapterFactSchemaVersion
    fund_code: str
    report_year: int
    chapter: ChapterFactInput
    mode: ChapterWriterMode = "llm"
    citation_style: ChapterCitationStyle = "body_quote"
    max_output_chars: int = 12000
```

```python
@dataclass(frozen=True, slots=True)
class ChapterWriterPrompt:
    schema_version: Literal["chapter_writer_prompt.v1"]
    chapter_id: int
    title: str
    system_prompt: str
    user_prompt: str
    must_answer: tuple[str, ...]
    must_not_cover: tuple[str, ...]
    required_output_items: tuple[str, ...]
    allowed_fact_ids: tuple[str, ...]
    allowed_anchor_ids: tuple[str, ...]
    deleted_item_rule_ids: tuple[str, ...]
    required_gap_phrases: tuple[str, ...]
```

```python
@dataclass(frozen=True, slots=True)
class ChapterDraft:
    schema_version: Literal["chapter_draft.v1"]
    chapter_id: int
    title: str
    markdown: str
    used_fact_ids: tuple[str, ...]
    used_anchor_ids: tuple[str, ...]
    declared_missing_reasons: tuple[ChapterFactMissingReason, ...]
    deleted_item_rule_ids: tuple[str, ...]
    model_name: str | None
    finish_reason: str | None
```

```python
@dataclass(frozen=True, slots=True)
class ChapterWriteIssue:
    issue_id: str
    severity: Literal["blocking", "reviewable"]
    reason: ChapterWriteStopReason
    message: str
    fact_ids: tuple[str, ...] = ()
    anchor_ids: tuple[str, ...] = ()
    item_rule_ids: tuple[str, ...] = ()
```

```python
@dataclass(frozen=True, slots=True)
class ChapterWriteResult:
    schema_version: ChapterWriterSchemaVersion
    status: ChapterWriteStatus
    stop_reason: ChapterWriteStopReason
    prompt: ChapterWriterPrompt
    draft: ChapterDraft | None
    issues: tuple[ChapterWriteIssue, ...]
```

Public API：

```python
def build_chapter_writer_input(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    mode: ChapterWriterMode = "llm",
    citation_style: ChapterCitationStyle = "body_quote",
    max_output_chars: int = 12000,
) -> ChapterWriterInput:
    ...

def build_chapter_prompt(input_data: ChapterWriterInput) -> ChapterWriterPrompt:
    ...

def write_chapter(
    input_data: ChapterWriterInput,
    *,
    llm_client: ChapterLLMClient | None,
) -> ChapterWriteResult:
    ...

class ChapterWriter:
    def write(
        self,
        input_data: ChapterWriterInput,
        *,
        llm_client: ChapterLLMClient | None,
    ) -> ChapterWriteResult:
        ...
```

### 7.4 Writer data flow

1. `build_chapter_writer_input()` 从 `ChapterFactProjection.chapters` 精确选择一个 `chapter_id`；缺章或重复时 `ValueError` fail closed。
2. `build_chapter_prompt()` 只读取 `ChapterFactInput`：
   - `contract.must_answer`
   - `contract.must_not_cover`
   - `contract.required_output_items`
   - `lens_resolution.statements`、`facets_any`、`priority`
   - `item_rule_projection.decisions`
   - `facts`、`evidence_anchors`、`missing_reasons`
   - `fund_type`、`classification_basis`、`facet_resolution.non_asserted_facets`
3. Writer prompt 必须明确：
   - 只能使用 `allowed_fact_ids` 中 facts。
   - 只能引用 `allowed_anchor_ids` 中 anchors。
   - 所有数值判断必须带正文证据行。
   - `missing` / `unavailable` / `not_applicable` 必须写成缺口或不适用，不得补全。
   - `fund_type="unknown"` 不得应用类型 lens 或输出类型化判断。
   - `non_asserted_facets` 只能解释“未断言 subtype”，不得当作事实。
   - ITEM_RULE decision 为 delete/skip 的内容必须删除，不得输出对应标题、占位、暗示或空表。
4. `write_chapter()` 先执行 deterministic preflight：
   - fund type unknown -> blocked。
   - chapter 0 或 chapter 7 含 `accepted_chapter_conclusions_missing` -> blocked。
   - must-answer 直接依赖的 facts 全部 missing/unavailable 且无法以缺口回答 -> blocked。
   - available fact 含 `evidence_missing` 且 `_fact_supports_critical_judgment(fact) is True` -> blocked。
   - ITEM_RULE 删除的 section 若仍被 required_output_items 强依赖且没有 alternative gap wording -> blocked。
   - `llm_client is None` 且 `mode="llm"` -> blocked `llm_unavailable`。
5. `_fact_supports_critical_judgment(fact)` 是 deterministic helper，必须按以下规则实现：
   - `fact.required_by` 任一项以 `CHAPTER_CONTRACT.` 开头，视为支撑章节 contract 关键判断。
   - `fact.required_by` 任一项以 `ITEM_RULE.` 开头，视为支撑条件条目关键判断。
   - `fact.source_field_id` 属于数值或证据强依赖字段时，视为支撑数值/关键判断。初始集合为 `structured.nav_benchmark_performance`、`structured.investor_return`、`structured.tracking_error`、`structured.fee_schedule`、`structured.turnover_rate`、`structured.share_change`、`structured.manager_alignment`、`structured.holder_structure`、`structured.holdings_snapshot`、`structured.bond_risk_evidence`、`structured.nav_data`。
   - `fact.value` 是 `int` / `float` / `Decimal`，或 dict/list/tuple 中直接包含数值叶子，也视为支撑数值判断。
   - helper 只决定是否因 `evidence_missing` fail closed；不得打开 repository/source 复核。
6. `mode="prompt_only"` 只返回 prompt 和 blocked result，`draft=None`，`status="blocked"`，`stop_reason="prompt_only"`，issues 可为空或包含 informational/reviewable issue，但不得创建 fake draft；它用于 deterministic tests，不代表章节已写好。
7. LLM 返回空文本、超长文本、无法解析 anchor/missing markers 或包含 forbidden phrases 时，返回 blocked，不产生 accepted draft。

### 7.5 Writer LLM response parsing contract

`_draft_from_llm_response()` 必须使用以下精确、确定性的解析规则；implementation agent 不得自行发明兼容格式：

- Anchor marker 精确格式：`<!-- anchor:<anchor_id> -->`。
  - 正则：`<!-- anchor:([^<>\s]+) -->`。
  - `anchor_id` 必须逐字等于 `ChapterWriterPrompt.allowed_anchor_ids` 中的一个值。
  - 格式大小写敏感；`<!--anchor:...-->`、`<!-- anchor: ... -->`、`<!-- ANCHOR:... -->`、空 id、包含空格或尖括号的 id 均为 invalid marker。
  - `used_anchor_ids` 按正文首次出现顺序 deterministic dedupe。
  - 出现 unknown anchor id 或 invalid marker 时，`write_chapter()` 返回 blocked，`stop_reason="llm_contract_violation"`，不得保留 draft。
- Missing marker 精确格式：`<!-- missing:<reason> -->`。
  - 正则：`<!-- missing:([a-z_]+) -->`。
  - `reason` 必须属于 `ChapterFactMissingReason` 闭集，且必须出现在 `ChapterFactInput.missing_reasons` 中；否则 blocked，`stop_reason="llm_contract_violation"`。
  - `declared_missing_reasons` 按正文首次出现顺序 deterministic dedupe。
  - Gate 2 不从自由中文文本推断 missing reason；没有 marker 时 `declared_missing_reasons=()`，programmatic audit 仍可基于正文短语做 missing semantics 检查。
- 标准正文证据行仍必须面向用户显示，但不作为 anchor id 的唯一解析来源；正文证据行没有对应 anchor marker 时视为不可验证证据引用，blocked。
- `max_output_chars` 是 hard post-check 阈值，按 `len(response.text)` 计算；超过即 blocked，`stop_reason="llm_contract_violation"`，不得截断、不得部分接受。
- 若 unknown anchor id 疑似来自 `bond_risk_evidence.value.anchors` 内部 ref，issue message 必须写明：`bond_risk_evidence 组级锚点未展开为 ChapterEvidenceAnchor，需后续 conversion helper 后才能引用`。疑似判断可用子串匹配 `bond`、`risk`、`credit`、`duration` 或实现中从对应 fact value 中收集内部 ref。

## 8. Auditor contract

新增 `fund_agent/fund/chapter_auditor.py`。所有 public dataclass 使用 `frozen=True, slots=True`。所有函数/类必须有完整中文 docstring，并引用模板第 0-7 章。

### 8.1 Literal aliases

```python
ChapterAuditSchemaVersion = Literal["chapter_audit.v1"]
ChapterAuditLayer = Literal["programmatic", "llm"]
ChapterAuditStatus = Literal["pass", "fail", "blocked"]
ChapterAuditSeverity = Literal["blocking", "reviewable", "informational"]
ChapterAuditRuleCode = Literal[
    "P1",
    "P2",
    "E1",
    "E2",
    "E3",
    "C1",
    "C2",
    "L1",
    "L2",
    "R1",
    "R2",
    "LLM_UNAVAILABLE",
]
ChapterAuditRepairHint = Literal["none", "patch", "regenerate", "needs_more_facts"]
```

### 8.2 Auditor LLM Protocol

```python
@dataclass(frozen=True, slots=True)
class ChapterAuditLLMRequest:
    schema_version: Literal["chapter_audit_llm_request.v1"]
    chapter_id: int
    fund_code: str
    report_year: int
    system_prompt: str
    user_prompt: str
    draft_markdown: str
    allowed_fact_ids: tuple[str, ...]
    allowed_anchor_ids: tuple[str, ...]
    audit_focus: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class ChapterAuditLLMResponse:
    schema_version: Literal["chapter_audit_llm_response.v1"]
    raw_text: str
    model_name: str | None
    finish_reason: str | None
```

```python
class ChapterAuditLLMClient(Protocol):
    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        ...
```

约束：

- Gate 2 不解析复杂 JSON 修复计划；LLM audit 必须返回 §8.4 的 line format。
- 若无法稳定解析 LLM 输出，不得 pass；按 §8.4 返回 deterministic blocked issue。
- 不做 repair decision 执行；只输出 `repair_hint` 给 Gate 3 使用。

### 8.3 Auditor dataclasses

```python
@dataclass(frozen=True, slots=True)
class ChapterAuditInput:
    schema_version: ChapterAuditSchemaVersion
    writer_input: ChapterWriterInput
    draft: ChapterDraft
    run_programmatic: bool = True
    run_llm: bool = True
```

```python
@dataclass(frozen=True, slots=True)
class ChapterAuditIssue:
    issue_id: str
    layer: ChapterAuditLayer
    rule_code: ChapterAuditRuleCode
    severity: ChapterAuditSeverity
    message: str
    location: str | None
    fact_ids: tuple[str, ...] = ()
    anchor_ids: tuple[str, ...] = ()
    item_rule_ids: tuple[str, ...] = ()
    repair_hint: ChapterAuditRepairHint = "none"
```

```python
@dataclass(frozen=True, slots=True)
class ChapterProgrammaticAuditResult:
    status: ChapterAuditStatus
    issues: tuple[ChapterAuditIssue, ...]
    checked_rules: tuple[ChapterAuditRuleCode, ...]
```

```python
@dataclass(frozen=True, slots=True)
class ChapterLLMAuditResult:
    status: ChapterAuditStatus
    issues: tuple[ChapterAuditIssue, ...]
    raw_response: str | None
    model_name: str | None
    finish_reason: str | None
```

```python
@dataclass(frozen=True, slots=True)
class ChapterAuditResult:
    schema_version: ChapterAuditSchemaVersion
    status: ChapterAuditStatus
    programmatic: ChapterProgrammaticAuditResult
    llm: ChapterLLMAuditResult
    accepted: bool
    repair_hint: ChapterAuditRepairHint
```

Public API：

```python
def audit_chapter_programmatic(input_data: ChapterAuditInput) -> ChapterProgrammaticAuditResult:
    ...

def audit_chapter_llm(
    input_data: ChapterAuditInput,
    *,
    llm_client: ChapterAuditLLMClient | None,
) -> ChapterLLMAuditResult:
    ...

def audit_chapter(
    input_data: ChapterAuditInput,
    *,
    llm_client: ChapterAuditLLMClient | None,
) -> ChapterAuditResult:
    ...

class ChapterAuditor:
    def audit(
        self,
        input_data: ChapterAuditInput,
        *,
        llm_client: ChapterAuditLLMClient | None,
    ) -> ChapterAuditResult:
        ...
```

### 8.4 LLM audit parsing contract

`audit_chapter_llm()` 必须使用以下固定协议：

- `audit_focus` 默认值为：
  - `evidence_support`
  - `must_not_cover_boundary`
  - `missing_semantics`
  - `readability`
  - `non_asserted_facet_boundary`
- LLM response line format 精确为：`SEVERITY|LOCATION|MESSAGE`。
  - `SEVERITY` 只允许 `BLOCKING`、`REVIEWABLE`、`INFO`、`PASS`。
  - `LOCATION` 是非空字符串；章节级整体问题使用 `chapter`。
  - `MESSAGE` 是非空字符串；不得包含换行。
  - `PASS` 行必须写成 `PASS|chapter|no issues`，且只能单独出现。
- 空响应或任一非空行无法解析时，`ChapterLLMAuditResult.status="blocked"`，返回单条 issue：
  - `layer="llm"`
  - `rule_code="C1"`
  - `severity="blocking"`
  - `message` 说明 LLM audit response parse failure
  - `repair_hint="regenerate"`
  - 不得 silent pass，不得把原始自由文本当作通过。
- `PASS|chapter|no issues` 或零 issue 等价于 LLM pass。为避免空响应歧义，fake/real client 推荐显式返回 `PASS|chapter|no issues`；实现若选择支持零 issue pass，必须仅在 raw_text 去除空白后等于 `PASS|chapter|no issues` 的规范化内部结果中使用，空 raw_text 仍 blocked。
- 只有 `INFO` 行时，LLM status 为 `pass`，issues severity 为 informational，programmatic 也通过时 `accepted=True`。
- 任一 `REVIEWABLE` 行时，LLM status 为 `fail`，对应 issue `severity="reviewable"`，默认 `repair_hint="patch"`。
- 任一 `BLOCKING` 行时，LLM status 为 `fail`，对应 issue `severity="blocking"`，默认 `repair_hint="regenerate"`。
- LLM parser 不从 raw text 识别 fact ids 或 anchor ids；若后续需要结构化 ids，必须另开 gate 扩展格式。

## 9. Programmatic audit vs LLM audit

Programmatic audit 是 deterministic no-LLM 审计，最小覆盖：

- P1：章节标题/章节编号与 `ChapterFactInput.contract.title` 一致；第 1-6 章必须包含 `结论要点 / 详细情况 / 证据与出处`，第 0 章不得要求这三段。
- P2：正文非空，关键 required output item 不得是空占位；不得保留 `[基金类型]`、`X.XX%`、`[列出...]` 等模板占位。
- E1：所有 `ChapterDraft.used_anchor_ids` 必须属于 `ChapterFactInput.evidence_anchors`；正文证据行必须引用可识别年报/外部/derived 锚点。
- E3：available 数值/关键判断没有 anchor 时 fail；`evidence_missing` fact 被用于关键判断时 fail。
- C2：`must_answer` 对应 required output items 至少有结构性 marker；`must_not_cover` 中的明确禁用项不得出现。
- C2 ITEM_RULE：decision 为 delete/skip 的 item 标题或唯一 marker 不得出现在 draft；decision 为 render 的 item 若 facts available 且 anchors present，应出现，否则必须写明数据缺口。
- C2 non_asserted_facets：`ChapterFactInput.facet_resolution.non_asserted_facets` 中的候选 facet 不得被写成已断言事实。最小 deterministic 策略：
  - 若候选 facet 字符串出现在正文中，且前后 12 个中文字符内没有 `未断言`、`未确认`、`候选`、`可能`、`不可据此判断`、`不能据此判断`、`仅为 lens 候选`，则 fail。
  - Writer prompt 必须要求提到候选 facet 时使用“（未断言）”或同义限定语。
  - `facets=()` 且正文出现“属于/是/为/定位为 + 候选 facet”时，一律 blocking。
- C1：禁止“建议买入/卖出/加仓/减仓/仓位比例/预测收益/目标价/基金经理动机”等禁用措辞。
- L1：Gate 2 只做最小文本闭合检查，不重新计算 R=A+B-C；若 draft 声称 A=R-B 或 A-C，必须引用 derived/formula fact 或明确“数据不足，未计算”。完整数值闭合仍依赖后续 Evidence Confirm / existing deterministic analysis，不能假装已完成。
- R1/R2：Gate 2 单章不判断全局 final judgment consistency；若第 7 章被调用且缺 accepted conclusions，programmatic audit 必须 blocked。
- Chapter 5 cross-period missing semantics：当 `chapter_id == 5` 且 `missing_reasons` 含 `cross_period_comparison_missing` 时，programmatic audit 只阻断确定性跨期断言，不阻断当前期事实描述。
  - Assertion phrase 初始集合：`风格稳定`、`风格保持稳定`、`风格一致`、`风格延续`、`言行一致`、`投资框架稳定`、`没有明显变化`、`变化不大`、`持续改善`、`明显漂移`、`发生转型`、`阶段切换`、`相比上一期`、`过去一年变化`。
  - Negation / gap prefix 初始集合：`不判断`、`不能判断`、`无法判断`、`不足以判断`、`不能据此判断`、`证据不足`、`数据不足`、`缺少跨期`、`未披露上期`。
  - 若 assertion phrase 命中，且其前 12 个中文字符内没有 negation / gap prefix，则 fail，rule `C2`，repair_hint=`needs_more_facts`。
  - 问题式表达如 `是否风格稳定`、`能否判断风格稳定`、`下一步验证风格是否稳定` 不阻断。
- E2（证据与断言不匹配）需要重新对照年报原文、表格或来源内容，超出 Gate 2 writer/auditor 不读 PDF/source 的边界；本 gate 只做 E1/E3 与 LLM semantic support，E2 source verification 显式 deferred 到后续 Evidence Confirm gate。

LLM audit 是 semantic review，最小职责：

- 判断断言是否被提供的 facts/anchors 支撑。
- 判断是否越过 `must_not_cover` 或投资建议边界。
- 判断 missing/unavailable/not_applicable 是否被正确降级，而不是被补写成事实。
- 判断文字是否让读者能看懂下一步最小验证问题。
- 不负责修复、不负责 orchestrator policy、不覆盖 programmatic hard failure。

汇总规则：

- programmatic fail/blocking -> `ChapterAuditResult.status="fail"` 或 `"blocked"`，`accepted=False`，即使 LLM 没问题也不得 accepted。
- LLM unavailable 且 `run_llm=True` -> `status="blocked"`，`accepted=False`。
- LLM 只返回 informational/reviewable issues 时，Gate 2 可返回 `fail` + `repair_hint="patch"`；是否 patch 属于 Gate 3。
- programmatic pass 且 LLM pass 才能 `accepted=True`。
- LLM 零 blocking/reviewable issue 且 programmatic pass 时，`ChapterAuditResult.status="pass"`，`accepted=True`；informational-only issues 不阻断 acceptance。
- 顶层 `ChapterAuditResult.repair_hint` 按所有 programmatic + LLM issues 的最高优先级聚合：`needs_more_facts` > `regenerate` > `patch` > `none`。没有 issue 时为 `none`。若 status 为 `blocked` 且没有更具体 issue hint，默认 `regenerate`；若缺 facts / missing semantics 导致 blocked，默认 `needs_more_facts`。

## 10. Evidence anchor and citation constraints

Writer prompt 和 programmatic auditor 必须统一要求：

- 正文证据行格式优先为 `> 📎 证据：年报{document_year}§{section_id}表{table_id}行{row_locator}（{note}）`。
- 当 `source_kind="external_api"` 时可写 `> 📎 证据：外部数据({section_id}) {note}`，但不能冒充年报。
- 当 `source_kind="derived"` 时可写 `> 📎 证据：计算({section_id}) {note}`，并要求说明输入 fact ids。
- `source_kind="unknown"` 不能支撑关键数值判断；只能写成待复核证据或缺口。
- `ChapterFactEntry.evidence_anchor_ids=()` 且 `missing_reason="evidence_missing"` 的 available fact 不得支撑正向结论。
- `bond_risk_evidence.value.anchors` 当前不是普通章节锚点；Gate 2 最小实现不得强行正文引用其内部 ref，除非另有显式 conversion helper 并有测试覆盖。若 LLM 输出引用内部 ref，writer/auditor 必须 blocked，并用 §7.5 的专门错误消息说明“组级锚点未展开”。
- 第 0 章不输出“证据与出处”小节；本 gate 默认不生成第 0 章，因为缺 accepted chapters。

## 11. Stop conditions and fail-closed behavior

实现时遇到以下任一情况必须 fail closed，不得生成 accepted draft：

- `chapter.fund_type == "unknown"`。
- `chapter.missing_reasons` 包含 `classified_fund_type_missing` 或 `classified_fund_type_invalid`。
- 第 0 章或第 7 章包含 `accepted_chapter_conclusions_missing`。
- 第 5 章包含 `cross_period_comparison_missing`，且草稿试图判断跨期风格/阶段变化为确定事实。
- required facts 全部是 `missing` / `unavailable` / `not_applicable`，但 writer 没有输出数据缺口。
- 关键 available fact 缺少 anchors 或 `source_kind="unknown"`。
- ITEM_RULE decision 要求删除的 section 被输出，或被空表/占位文本暗示存在。
- `llm_client is None` 且请求 `mode="llm"` 或 `run_llm=True`。
- LLM 返回空文本、无法解析、包含禁用投资建议、包含未授权 anchor/fact id。
- 实现需要读取 repository/source/PDF/cache/downloader/parser、外部网站、env config、Service、Host 或 dayu。
- 实现需要修改 template manifest、golden、quality gate、final judgment 或 CLI。

## 12. Minimal implementation slices

### Slice 1：Writer contract + prompt builder

Allowed files：

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`

Exact changes：

- 定义 §7 的 Literal aliases、Protocol、dataclasses、public API。
- 实现 `build_chapter_writer_input()` 和 `build_chapter_prompt()`。
- 实现 deterministic preflight helper：
  - `_chapter_by_id(...)`
  - `_available_facts(...)`
  - `_missing_issues(...)`
  - `_fact_supports_critical_judgment(...)`
  - `_deleted_item_rule_ids(...)`
  - `_allowed_anchor_ids(...)`
  - `_forbidden_phrases()`
- `write_chapter()` 在本 slice 可只支持 `mode="prompt_only"` 和 `llm_client is None` 的 blocked path，不调用 LLM。

Tests：

- `test_build_writer_input_selects_single_chapter_from_projection`
- `test_writer_prompt_contains_contract_lens_item_rules_and_fact_ids`
- `test_writer_prompt_marks_non_asserted_facets_as_not_asserted`
- `test_writer_blocks_unknown_fund_type`
- `test_writer_blocks_chapter_zero_and_seven_without_accepted_conclusions`
- `test_prompt_only_does_not_create_fake_draft_and_uses_prompt_only_stop_reason`
- `test_writer_blocks_evidence_missing_critical_fact_by_required_by`
- `test_writer_blocks_evidence_missing_numeric_source_field`

Stop condition：

- 如果需要改 `ChapterFactProjection` schema，停止交回 controller。

### Slice 2：Writer LLM invocation + draft post-check

Allowed files：

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`

Exact changes：

- 实现 `ChapterLLMClient.generate_chapter()` 调用路径。
- 实现 `_llm_request_from_prompt(...)`。
- 实现 `_draft_from_llm_response(...)`，只按 §7.5 解析 `<!-- anchor:<anchor_id> -->` 和 `<!-- missing:<reason> -->`；用户可见正文仍必须包含标准证据行，但标准证据行不能替代 anchor marker。
- 实现 forbidden phrase、empty response、unauthorized anchor/fact reference、max length post-check。
- 不做 retry、不做 streaming、不做 provider-specific client。

Tests：

- `test_write_chapter_with_fake_llm_returns_draft_with_allowed_anchors`
- `test_writer_parses_valid_anchor_and_missing_markers`
- `test_writer_rejects_invalid_anchor_marker_spacing_or_case`
- `test_writer_rejects_empty_llm_response`
- `test_writer_rejects_response_over_max_output_chars_without_truncation`
- `test_writer_rejects_forbidden_trading_advice`
- `test_writer_rejects_unknown_anchor_reference`
- `test_writer_rejects_unknown_missing_reason_marker`
- `test_writer_reports_bond_risk_internal_anchor_message`
- `test_writer_does_not_import_repository_source_service_dayu_or_openai`

Stop condition：

- 如果需要读取 env/config 或引入 OpenAI/http dependency，停止。

### Slice 3：Programmatic auditor

Allowed files：

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py`

Exact changes：

- 定义 §8 的 Literal aliases、Protocol、dataclasses、public API。
- 实现 `audit_chapter_programmatic()`。
- 实现 deterministic checks：
  - `_audit_structure(...)`
  - `_audit_placeholders(...)`
  - `_audit_anchor_refs(...)`
  - `_audit_contract_markers(...)`
  - `_audit_item_rule_deleted_sections(...)`
  - `_audit_non_asserted_facets(...)`
  - `_audit_forbidden_content(...)`
  - `_audit_missing_semantics(...)`
- `audit_chapter()` 在没有 LLM client 且 `run_llm=True` 时必须 blocked，不得 pass。

Tests：

- `test_programmatic_audit_passes_minimal_valid_chapter`
- `test_programmatic_audit_fails_placeholder_text`
- `test_programmatic_audit_fails_unknown_anchor`
- `test_programmatic_audit_fails_deleted_item_rule_section`
- `test_programmatic_audit_fails_forbidden_trading_advice`
- `test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact`
- `test_programmatic_audit_blocks_chapter5_cross_period_assertion_when_missing`
- `test_programmatic_audit_allows_chapter5_cross_period_gap_or_question_wording`
- `test_audit_blocks_when_llm_required_but_unavailable`

Stop condition：

- 如果 audit 需要重新打开 PDF/报告源或复算未传入 facts，停止。

### Slice 4：LLM auditor + package/test docs sync

Allowed files：

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py`
- `fund_agent/fund/__init__.py`，仅当需要 package-level export
- `fund_agent/fund/README.md`
- `tests/README.md`

Exact changes：

- 实现 `audit_chapter_llm()` 和 LLM request builder。
- 实现 §8.4 line parser；parse failure 必须 blocked，不 silent pass。
- LLM unavailable -> `LLM_UNAVAILABLE` blocked issue。
- Fake LLM pass/fail tests 覆盖 semantic issue ingest。
- 实现 `ChapterAuditResult.repair_hint` 聚合优先级。
- README 只写当前 Fund 层 single-chapter writer/auditor primitives；明确无 orchestrator、无 repair loop、无 CLI、无 dayu。

Tests：

- `test_llm_audit_unavailable_is_blocked`
- `test_llm_audit_fake_pass_combines_with_programmatic_pass`
- `test_llm_audit_informational_only_passes_with_programmatic_pass`
- `test_llm_audit_parse_failure_is_blocked`
- `test_llm_audit_fake_issue_prevents_acceptance`
- `test_audit_repair_hint_uses_highest_priority`
- `test_auditor_does_not_import_repository_source_service_dayu_or_openai`

Stop condition：

- 如果需要更新 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、声明 MVP complete、声明 CLI 可用或声明 Host/Agent/dayu 已实现，停止交回 controller。

## 13. Exact test plan

新增：

- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`

Targeted tests 必须覆盖：

- 从 Gate 1 fake `ChapterFactProjection` 选择单章输入。
- writer prompt 包含 must_answer / must_not_cover / required_output_items / preferred_lens / ITEM_RULE / fact ids / anchor ids。
- writer 对 `missing` / `unavailable` / `not_applicable` 输出缺口指令，不让 LLM 补事实。
- writer 对 `non_asserted_facets` 明确“不可断言 subtype”。
- writer 对 fund_type unknown、chapter 0/7 accepted conclusions missing、critical `evidence_missing`、LLM missing、LLM empty response、超长 response fail closed。
- writer anchor marker 精确解析：valid `<!-- anchor:<anchor_id> -->` 通过；空格、大小写、unknown id、invalid id 均 blocked。
- writer missing marker 精确解析：valid `<!-- missing:<reason> -->` 进入 `declared_missing_reasons`；unknown reason 或未在 chapter missing reasons 中的 reason blocked。
- writer 不输出或接受被 ITEM_RULE 删除的 section。
- auditor programmatic pass/fail：结构、占位符、anchor refs、ITEM_RULE 删除段落、禁用交易建议、missing semantics、chapter 5 cross-period phrase、non_asserted_facets asserted-fact misuse。
- auditor LLM unavailable blocked；fake LLM `PASS|chapter|no issues` / informational-only / reviewable / blocking / parse failure 均有确定测试，不伪造 correctness。
- audit repair_hint 聚合优先级：`needs_more_facts` > `regenerate` > `patch` > `none`。
- E2 evidence-vs-assertion source verification 明确无 Gate 2 测试，因为 deferred 到 Evidence Confirm gate。
- AST import isolation：`chapter_writer.py` / `chapter_auditor.py` 不导入 `documents`、`repository`、`cache`、`pdf`、`source`、`downloader`、`parser`、`service`、`dayu`、`openai`、`httpx`。

Coverage：

- 新增/大幅修改模块单文件目标 ≥80%。
- 若未达到，implementation evidence 必须列出未覆盖行、原因、补测计划或接受依据。

## 14. Validation commands

Targeted：

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
uv run pytest tests/fund/test_chapter_facts.py -q
uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py -q
```

Full required if runtime code changes：

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Optional boundary regression if exports/docs touch package public surface：

```bash
uv run pytest tests/fund/test_report_evidence.py tests/fund/test_data_extractor.py -q
```

Implementation evidence 必须记录命令、结果、覆盖率和任何未运行原因。

## 15. Docs update plan

实现完成且测试通过后：

- `fund_agent/fund/README.md`
  - 新增 Fund 层 `chapter_writer` / `chapter_auditor` 当前能力说明。
  - 明确它们只消费 `ChapterFactInput` / `ChapterFactProjection`，不读 PDF/repository/source helper，不接 Service/CLI/dayu。
  - 明确 LLM client 是调用方注入；缺失时 fail closed。
- `tests/README.md`
  - 新增 targeted writer/auditor test 命令。
Controller closeout only，不属于 implementation worker 默认 scope：

- `docs/design.md`
  - 仅在 controller 接受 implementation 后，把 Gate 2 writer/auditor 标为当前已实现；保持 orchestrator/repair/CLI/dayu 未来状态。
- `docs/current-startup-packet.md` / `docs/implementation-control.md`
  - 仅由 controller closeout 更新 current/next gate 和 accepted artifacts。

不得更新：

- `docs/fund-analysis-template-draft.md`
- `AGENTS.md`
- `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`，除非 controller 在 implementation handoff 中显式授权
- root `README.md`，除非后续 CLI/use-case gate 改变用户路径。

## 16. Review checklist

Plan/implementation review 重点：

- 是否只新增 Fund 层 single-chapter writer/auditor primitives。
- 是否没有 Service orchestrator、repair loop、final assembler、chapter 0 assembly、CLI `--use-llm`、Host/Agent/dayu scope creep。
- 是否所有业务参数显式 typed，没有 `extra_payload`。
- 是否 writer/auditor 只消费 `ChapterFactInput` / `ChapterFactProjection`。
- 是否没有 repository/PDF/cache/source/downloader/parser/Service/dayu/OpenAI direct import。
- 是否 fund_type unknown、missing facts、missing anchors、LLM unavailable 均 fail closed。
- 是否 ITEM_RULE delete 被严格执行。
- 是否 `non_asserted_facets` 没有驱动写作结论或 ITEM_RULE。
- 是否 writer/auditor 严格执行 anchor/missing marker 和 LLM audit line parser，不 silent pass。
- 是否 chapter 5 cross-period missing 只阻断未否定的确定性跨期断言。
- 是否 `repair_hint` 聚合优先级已实现并测试。
- 是否 E2 source verification 没有被假装实现，明确 deferred。
- 是否 programmatic audit 与 LLM audit 责任边界清晰。
- 是否 no-LLM stub/prompt_only 没有 fake accepted draft。
- 是否 tests 覆盖 happy path、blocked path、semantic fail、import boundary。

## 17. Residual risks and next gates

Residual risks accepted for Gate 2 planning：

- `ChapterFactEntry.value` 仍是 `object | None`，writer/auditor 最小实现需以 conservative serialization 呈现 facts；更细字段级 typed view 可留给后续 quality/evidence gate。
- LLM audit 只能检查语义支撑，不能证明事实完全正确；E2 evidence-vs-assertion source verification、Evidence Confirm 和 anchor-to-source verification 仍是后续 gate。
- 第 0 章和第 7 章需要 accepted chapters / quality context，本 gate 默认 fail closed，不完成最终报告闭环。
- RepairDecision 只作为 hint，不执行 patch/regenerate；执行策略属于 Gate 3。
- No provider-specific LLM client；实际 Service config、provider selection、timeout/retry 属于 Gate 3 或独立 Service gate。

Next gates：

- Gate 3：`chapter_orchestrator`，Service owns write-audit-repair policy，通过显式 contract 调用 Fund writer/auditor primitives。
- Gate 4：`final_chapter_assembler`、chapter 0 assembly、opt-in CLI `--use-llm`。
- Gate 5：可选 Host/Agent/dayu integration；未来 Host 必须用 `dayu.host`，未来 Agent engine/tool loop 必须用 `dayu.engine`。

## 18. Blocking Questions For Controller

无。当前 branch 与 next entry 清晰，tracked worktree 干净；现有未跟踪 artifacts 应继续忽略。
