# MVP LLM writer/auditor contract hardening plan

日期：2026-05-31

角色：Gateflow planning specialist。本文只写 handoff-ready / code-generation-ready implementation plan，不进入 implementation，不修改运行时代码，不 commit、不 push、不开 PR、不 merge。

## 1. Worker self-check

- Current gate / role：当前是 `MVP LLM writer/auditor contract hardening gate` 的 plan gate；我是 planning worker，不是 controller。
- Scope boundary：本轮只允许创建或编辑本文档 `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`。
- Prohibited actions：不启动 `$gateflow` / `/gateflow`，不进入 implementation，不修改运行时代码，不改 golden / fixtures / score / quality gate，不进入 Gate 5 dayu/Host/Agent，不 commit / push / PR / merge。
- Evidence hygiene：只使用允许读取的控制面和脱敏诊断摘要；不记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- Completion signal：产出可直接交给 implementation agent 的计划，包含目标、范围、证据、契约变更、切片、测试、验证矩阵、stop conditions 和完成报告格式。

## 2. Goal / motivation

目标：修复真实 provider smoke 中 writer/auditor contract 适配失败，使：

```bash
fund-analysis analyze 006597 --report-year 2024 --use-llm
```

在真实 provider 下更稳定地产生可审计的模板章节，或者以更精确、可修复的原因 fail-closed。

动机：

- provider/auth 已验证可用，当前 blocker 不应再归因于 missing provider config 或 HTTP 401。
- 真实 smoke 已到达第 1 章 writer/auditor 路径，但 writer 输出协议、auditor 行协议和 regenerate 输入不足，导致可修复问题变成低可诊断的 `llm_exception` / timeout。
- 本 gate 的核心不是放松审计，而是把 writer 输出协议、parser failure category、LLM audit line protocol 和 regenerate 行为收紧，让模型在最低认知负担下稳定做对下一步动作。

## 3. Controller state / gate sequencing

Controller 指定的 gate sequence 必须保持为三段，不得在当前 gate 内合并后续工作：

1. Current gate：`MVP LLM writer/auditor contract hardening gate`
   - Goal：make real model output protocol controllable and failure reasons classifiable。
   - 本计划只覆盖 writer prompt/protocol、writer parser failure category、auditor line protocol、repair context 和 timeout 分类。
   - 完成信号是 fake-client validation 和真实 provider smoke 前置能力已经足以让后续 acceptance gate 判断成功或精确 blocker；不是要求本 gate 自行关闭全部真实 provider acceptance 风险。
2. Next gate：`MVP real provider smoke acceptance gate`
   - Goal：至少 `006597 / 2024` 产生完整 chapters `0-7`，或清晰识别剩余 blocker。
   - 该 gate 才负责把真实 provider smoke 作为 acceptance gate 做最终裁决、记录 acceptance evidence、判断是否仍需修复或进入下一 gate。
   - 当前 contract-hardening gate 可以运行真实 smoke 作为验证，但不得把 next gate 的 controller acceptance、外部 PR 状态、release readiness 或后续裁决提前并入当前 gate。
3. Later gate：`MVP chapter generation score improvement loop gate`
   - Goal 不是 generic score improvement；它必须建立 real-provider generated chapters 的可重复评分，并按 failure category 自动形成 pro-codex repair tasks，持续提升 chapter generation pass rate 和 evidence compliance rate。
   - 该 gate 才设计 scoring schema、score history、failure-category task generation、自动 repair task 队列、pass-rate/evidence-compliance-rate 趋势跟踪。
   - 当前 contract-hardening gate 只输出可分类 failure reasons；不得实现 score loop、自动任务生成或评分体系。

## 4. Non-goals / scope

本 gate 做：

- 强化 Fund 层 writer prompt 输出协议和 writer response parser。
- 强化 Fund 层 auditor LLM line protocol 和 parse failure 分类。
- 强化 Service 层 write-audit-repair regenerate 输入与 timeout 分类。
- 用 fake client tests 覆盖已知 failure modes，并允许用真实 provider smoke 验证 failure reason 是否可分类；最终 smoke acceptance 裁决属于下一 gate。

本 gate不做：

- 不修改 deterministic `fund-analysis analyze` / `fund-analysis checklist` 默认行为。
- 不增加 deterministic fallback 到 `--use-llm`。
- 不改 golden / fixtures / score / snapshot / FQ0-FQ6 quality gate / promotion state。
- 不进入 Gate 5，不新增 Host/Agent/dayu runtime，不新增 `dayu.host` / `dayu.engine` 依赖。
- 不改 PR 状态，不 push，不 merge，不 release。
- 不记录 API key、Authorization header、完整 provider response、完整 writer draft。
- 不把弱证据或缺证据包装成通过。
- 不把 `non_asserted_facets` 写成 asserted facets。
- 不放松证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred 等安全边界。
- 不引入 provider fallback、多模型 writer/auditor split、streaming、并发、Evidence Confirm、chapter 0/7 LLM polish。
- 不把 `MVP real provider smoke acceptance gate` 的完整 acceptance 裁决提前并入当前 gate；当前 gate 的真实 smoke 只作为 contract hardening 验证和 blocker 分类输入。
- 不实现 `MVP chapter generation score improvement loop gate` 的任何 score schema、score history、自动 pro-codex repair task generation、pass-rate/evidence-compliance-rate dashboard 或持续优化循环。

## 5. Direct evidence

控制面证据：

- `docs/current-startup-packet.md` 和 `docs/implementation-control.md` 均记录：`MVP provider auth/config verification gate` 已完成，下一入口是 `MVP LLM writer/auditor contract hardening gate`。
- provider auth/config controller judgment 结论为 `provider_auth_passed_then_blocked_by_llm_contract`：当前 MiMo-compatible provider 可用，真实 `--use-llm` smoke 的 root cause 已从 provider auth 转移到 writer/auditor contract。

脱敏诊断摘要证据：

- `chapter1-api-diagnostic.json` 中 `api_status=completed`，`orchestrator_status=blocked`，`final_assembly_status=incomplete`。
- 第 1 章 writer 已产生 draft，但 programmatic audit 阻断：
  - 缺少第 1-6 章结构段落 marker：`结论要点`、`详细情况`、`证据与出处`。
  - 缺少 required output item marker：`会改变产品理解的特别情况（如有）`。
  - `non_asserted_facets` 中的候选 facet 被写成 asserted fact。
- LLM audit 返回 `llm:parse_failure`，当前已 fail-closed，但需要让 prompt/line protocol 更可执行并稳定归类。
- repair decision 选择 `regenerate`，后续 provider call timed out；当前 Service 层将 provider exception 汇总为 `llm_exception`，缺少更细的 timeout stop reason 和上一轮失败原因回灌。

代码事实证据：

- `fund_agent/fund/chapter_writer.py`
  - `build_chapter_prompt()` 已要求 anchor/missing marker，但没有明确要求第 1-6 章必须输出固定结构段落、每个 `required_output_items` 必须以稳定 marker 出现。
  - `_draft_from_llm_response()` 已处理空响应、超长响应、非法 marker、未知 anchor、未知 missing reason 和禁用措辞，但缺少“缺 required output marker / 缺结构段落 / finish_reason 不完整或内容过滤”在 writer parser 阶段的稳定 failure category。
- `fund_agent/fund/chapter_auditor.py`
  - `_parse_llm_audit_response()` 已将非行协议返回变成 `llm:parse_failure` blocked，没有 silent pass。
  - LLM audit prompt 只有 `SEVERITY|LOCATION|MESSAGE`，未明确 PASS 唯一格式、禁止解释性前后缀、parse failure repair category 和示例。
- `fund_agent/services/chapter_orchestrator.py`
  - `ChapterOrchestrationPolicy.max_repair_attempts` 已存在，默认 1；预算为 0 时不重试，预算耗尽返回 `repair_budget_exhausted`。
  - `_run_single_chapter()` regenerate 时复用同一个 writer input；没有把上一轮 audit issue ids / messages / required corrections 显式传入 writer prompt。
  - provider timeout 当前通过 `_exception_result()` 归为 `llm_exception`，不区分 timeout / network / malformed / rate limit。
- `fund_agent/services/llm_provider.py`
  - `OpenAICompatibleChapterLLMClient._complete()` 已把 `httpx.TimeoutException` 映射为 `LLMProviderRuntimeError("LLM provider request timed out")` 且测试覆盖不泄漏 prompt/key。

## 6. Plan review fix log

Controller accepted plan-review findings and amendments fixed in this plan:

| Finding ID | Status | Plan change |
|---|---|---|
| MiMo F-001 | fixed-in-plan | Slice B 明确要求 auditor `_audit_contract_markers()` 按 `<!-- required_output:<item> -->` 做 defense-in-depth 审计，不再只检查裸 item text。 |
| MiMo F-002 | fixed-in-plan | Slice B tests 明确更新 auditor `_valid_markdown()` helper，使合法测试章节包含 required output markers。 |
| MiMo F-003 | fixed-in-plan | Slice B 固定 facet 去重策略：MVP 只报告每个 unique facet text 的第一个 blocking occurrence；任一 asserted occurrence 仍 blocking。 |
| MiMo F-005 | fixed-in-plan | Slice A 增加新增 writer stop reason 到 Service `ChapterRunStopReason` 的显式映射表，优先保留诊断 category。 |
| MiMo F-004 | fixed-in-plan | Validation matrix 将真实 provider smoke 命令显式标注为 `Real provider smoke command (label: real-provider-smoke-006597-2024)`。 |
| GLM N-1 | fixed-in-plan | 统一使用 `INCOMPLETE_FINISH_REASONS` / `response_incomplete` 命名，避免把 `content_filter` 误称为 truncation。 |
| GLM N-2 | fixed-in-plan | Slice C 明确 `required_corrections` 由已知 rule/location/message pattern 的确定性映射生成，未知规则使用 sanitized issue message fallback。 |
| GLM N-3 | fixed-in-plan | 同 MiMo F-005，Service 映射表保留 writer parser 诊断 category。 |
| GLM N-4 | fixed-in-plan | 同 MiMo F-003，固定 first blocking occurrence per unique facet text。 |

## 7. Affected files / modules for implementation

后续 implementation agent 只能在 approved slices 中编辑下列文件：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_provider.py`
- `tests/ui/test_cli.py`
- `fund_agent/fund/README.md`，仅当 writer/auditor public contract 变更需要同步当前 Fund 包开发手册。
- `tests/README.md`，仅当新增测试分层或运行约定需要同步。

明确禁止编辑：

- `docs/fund-analysis-template-draft.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- golden / fixtures / score / quality gate / snapshot / promotion state
- `fund_agent/host/`、`fund_agent/agent/` 或任何 dayu integration 文件

控制面文档同步如需发生，应由 controller closeout 单独授权；implementation slices 不得自行修改控制面真源。

## 8. Contract / schema / public-interface changes

本 gate 允许的 public-interface changes 是向后兼容的 typed contract 扩展；不得删除现有字段或改变 deterministic CLI 默认语义。

### 8.1 Writer output protocol

在 `ChapterWriterPrompt` / `ChapterLLMRequest.user_prompt` 中明确以下协议：

- 第 1-6 章 Markdown 必须包含且只用以下顶层结构段落：
  - `### 结论要点`
  - `### 详细情况`
  - `### 证据与出处`
- `contract.required_output_items` 中每个 item 必须以稳定 marker 输出，格式固定为：

```markdown
<!-- required_output:<exact required output item> -->
```

- anchor marker 继续只允许：

```markdown
<!-- anchor:<anchor_id> -->
```

- missing marker 继续只允许：

```markdown
<!-- missing:<reason> -->
```

- 如果 required output item 缺少同源事实或证据，writer 不得编造内容，必须在对应 item marker 后写缺口表达，并使用 allowed `missing` marker；没有 allowed missing reason 时写“未披露 / 数据不足 / 下一步最小验证问题”，但不得断言事实。
- `non_asserted_facets` 只能以候选/未断言语言出现，推荐固定写法：

```markdown
候选/未断言信息：<facet> 仅为候选标签，当前结构化证据不足，不能写成本基金属于/是/定位为该 facet。
```

- 明确禁止以下断言形式命中 `non_asserted_facets`：`是<facet>`、`为<facet>`、`属于<facet>`、`定位为<facet>`、`可判定为<facet>`。
- `required_anchor_ids` 是 allowed anchor set，不是必须全量使用；使用任一证据断言时必须引用其中的 anchor。
- writer 不得输出 JSON 包裹、解释性前后缀或“以下是章节”等非章节正文。

### 8.2 Writer parser failure categories

扩展 `ChapterWriteStopReason`，建议新增：

```python
"missing_required_structure"
"missing_required_output_marker"
"unknown_anchor"
"response_too_long"
"response_incomplete"
```

映射要求：

- 缺 `### 结论要点` / `### 详细情况` / `### 证据与出处`：`missing_required_structure`。
- 缺任一 `<!-- required_output:<item> -->`：`missing_required_output_marker`。
- anchor marker 引用未授权 anchor：`unknown_anchor`。
- `len(text) > max_output_chars`：`response_too_long`。
- provider `finish_reason` 表示输出不完整或内容被过滤，例如 `length`、`max_tokens`、`content_filter` 或同义可配置集合：`response_incomplete`，禁止从部分文本猜测通过。
- 空响应继续为 `llm_empty_response`。
- 其他 marker 格式非法、禁用交易建议、未知 missing reason 继续可归入 `llm_contract_violation`，但 issue message 必须可修复。

Service `_WRITER_STOP_REASON_MAPPING` 必须同步接受新增 stop reason，并优先保留诊断 category：

| Writer stop reason | Service `ChapterRunStatus` | Service `ChapterRunStopReason` |
|---|---|---|
| `missing_required_structure` | `blocked` | `missing_required_structure` |
| `missing_required_output_marker` | `blocked` | `missing_required_output_marker` |
| `unknown_anchor` | `blocked` | `unknown_anchor` |
| `response_too_long` | `blocked` | `response_too_long` |
| `response_incomplete` | `blocked` | `response_incomplete` |

只有现有泛化 marker 格式非法、未知 missing reason、禁用措辞等仍可映射到 `llm_contract_violation`。timeout / provider runtime exception 不得混在 writer parser failure 内。

### 8.3 Auditor LLM line protocol

强化 `ChapterAuditLLMRequest.user_prompt`：

- 唯一 pass 响应必须精确为：

```text
PASS|chapter|no issues
```

- 非 pass 行只允许以下三种 severity：

```text
BLOCKING|<location>|<message>
REVIEWABLE|<location>|<message>
INFO|<location>|<message>
```

- 禁止 Markdown、编号列表、解释性前缀、总结句、JSON、空行以外的额外文本。
- `<location>` 不得为空，优先使用 required output item / heading / anchor id / line:N。
- `<message>` 必须说明“为什么不通过”和“最小修复动作”，但不能要求补外部来源。
- parse failure 必须保持 `status="blocked"`、`accepted=False`、issue id `llm:parse_failure` 或兼容稳定前缀，repair hint 为 `regenerate`；不得把 parse failure 当 pass。
- Programmatic auditor 的 `_audit_contract_markers()` 必须与 writer required output marker 协议对齐：每个 `contract.required_output_items` 必须检查 `<!-- required_output:<exact item> -->`，不得只检查裸 item text。裸 item text 可以作为辅助 message context，但不能作为 pass 条件。

### 8.4 Repair / regenerate behavior

扩展 `ChapterWriterInput` 或 `ChapterLLMRequest`，显式携带上一轮失败摘要。推荐最小字段：

```python
repair_context: ChapterRepairContext | None = None
```

新增 dataclass：

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRepairContext:
    """章节重写上下文，见模板第 1-6 章 write-audit-repair。"""

    attempt_index: int
    previous_issue_ids: tuple[str, ...]
    previous_messages: tuple[str, ...]
    required_corrections: tuple[str, ...]
```

约束：

- `repair_context` 必须是显式 typed field，禁止放入 `extra_payload`。
- 初始 attempt 使用 `None`。
- regenerate attempt 必须携带上一轮 audit issue ids、脱敏 messages、required corrections。
- required corrections 至少包含：
  - 补齐固定结构段落。
  - 补齐缺失 required output marker。
  - 把候选 facet 改成“候选/未断言”，不得断言。
  - 遵守 audit line protocol 反馈中指出的位置。
- `required_corrections` 必须由 deterministic mapping 生成：
  - `rule_code="P1"` 且 location/message 命中结构段落：`补齐 ### 结论要点 / ### 详细情况 / ### 证据与出处 固定结构段落。`
  - `rule_code="C2"` 且 location/message 命中 required output：`为对应 required output item 补齐 <!-- required_output:<item> --> marker，并在 marker 后只写有同源证据或明确缺口的内容。`
  - `rule_code="C2"` 且 message 命中候选 facet：`将候选 facet 改写为候选/未断言信息，不得使用 是/为/属于/定位为/可判定为 等断言动词。`
  - `rule_code="E1"` 或 message 命中 anchor：`只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。`
  - `issue_id="llm:parse_failure"`：`按 auditor 行协议修复：PASS|chapter|no issues 或 SEVERITY|LOCATION|MESSAGE，禁止解释性文本。`
  - 其他未知规则：使用 sanitized issue message fallback，去除换行、过长文本、provider raw response、draft 全文、key/header/prompt 等敏感内容，并限制单条 correction 长度。
- `max_repair_attempts` 继续由 `ChapterOrchestrationPolicy` 控制；不得无限重试。

### 8.5 Timeout classification

扩展 Service stop reason，建议新增：

```python
"llm_timeout"
"llm_rate_limited"
"llm_malformed_response"
"llm_network_error"
```

实现要求：

- 在 `fund_agent/services/llm_provider.py` 中新增 typed subclasses 或稳定 category 属性，至少把 timeout 和 network 区分开。
- `OpenAICompatibleChapterLLMClient._complete()` 捕获 timeout 时抛出可由 Service 识别的 timeout type，例如 `LLMProviderTimeoutError`。
- `chapter_orchestrator._exception_result()` 根据异常类型分类 stop reason；不再把 timeout 只写成 `llm_exception`。
- issue message 仍不得包含 prompt、API key、Authorization header、完整 provider response。

## 9. Concrete implementation decisions

1. 第一修复点是 prompt contract，不是审计放松。真实 provider 输出缺少结构段落和 required output marker，说明 writer 没拿到足够刚性的输出协议。
2. Parser 必须前置 fail-closed。缺 marker、未知 anchor、超长、输出不完整或内容过滤都应在 writer parser 阶段产生稳定 category，不等待 auditor 从自由文本猜测。
3. Auditor parse failure 已经不能 pass，本 gate 只强化 prompt 和 tests，保留 fail-closed 语义。
4. Repair 不实现 typed patch API。本 gate 继续把 `patch` / `regenerate` 映射为预算内整章 regenerate，但 regenerate 必须带上一轮失败原因。
5. Timeout 是 provider/runtime 分类，不是 writer/auditor contract violation。Service 必须能把 timeout 显示为 `llm_timeout`，让 operator 可修复 provider timeout 配置或重跑。
6. Audit rule calibration 只减少 false positive 的表达歧义，不降低安全边界：
   - 可调整 `non_asserted_facets` qualifier window 或断言动词识别，避免“未断言说明”被误杀。
   - 不允许把 asserted candidate facet 放过。
   - 不允许放松 evidence anchor、ITEM_RULE、交易建议、E2 deferred、must_not_cover。
7. 真实 provider smoke 成功标准不是“任何 markdown 退出 0”，而是包含 0-7 章、证据锚点、章节审计状态，且没有 deterministic fallback。
8. 当前 gate 只产出“可控协议 + 可分类失败原因”。完整真实 provider acceptance 的 controller 裁决属于下一 gate；repeatable scoring 和自动 pro-codex repair task loop 属于 later gate。

## 10. Implementation slices

### Slice A: writer prompt protocol and parser hardening

Objective：让 writer 输出协议足够刚性，并在 writer parser 阶段稳定分类缺结构、缺 required output marker、未知 anchor、超长、输出不完整或内容过滤。

Allowed files：

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Prerequisites：

- 不改 Service orchestration policy 语义。
- 不修改 auditor 规则阈值。

Exact changes：

- 在 `chapter_writer.py`：
  - 新增 constants：
    - `REQUIRED_BODY_SECTION_HEADINGS = ("### 结论要点", "### 详细情况", "### 证据与出处")`
    - `REQUIRED_OUTPUT_MARKER_PREFIX = "<!-- required_output:"`
    - `INCOMPLETE_FINISH_REASONS = frozenset(("length", "max_tokens", "content_filter"))`
  - 扩展 `ChapterWriteStopReason` literal，新增 `missing_required_structure`、`missing_required_output_marker`、`unknown_anchor`、`response_too_long`、`response_incomplete`。
  - `build_chapter_prompt()` 的 user prompt 写明 8.1 输出协议，并把 required output marker 格式与 `non_asserted_facets` 禁止断言示例放在靠前位置。
  - `_draft_from_llm_response()` 顺序调整为：
    1. 空响应。
    2. finish_reason 不完整 / 内容过滤。
    3. 超长。
    4. marker 格式。
    5. required section headings。
    6. required output markers。
    7. anchor/missing parsing。
    8. evidence line and forbidden phrases。
  - 新增 `_required_structure_issues()`。
  - 新增 `_required_output_marker_issues()`，以 exact required output item 匹配 `<!-- required_output:<item> -->`。
  - `_unknown_anchor_issue()` reason 改为 `unknown_anchor`，保留 bond_risk_evidence 专门 message。
  - 对 accepted draft 不做截断或部分接受；遇到不完整或内容过滤 finish reason 不从自由文本猜测 required output。
- 在 `chapter_orchestrator.py`：
  - `ChapterRunStopReason` literal 新增 `missing_required_structure`、`missing_required_output_marker`、`unknown_anchor`、`response_too_long`、`response_incomplete`。
  - `_WRITER_STOP_REASON_MAPPING` 接受新增 stop reasons，全部 fail-closed，并按下表保留诊断 category：

    | Writer stop reason | Run status | Run stop reason |
    |---|---|---|
    | `missing_required_structure` | `blocked` | `missing_required_structure` |
    | `missing_required_output_marker` | `blocked` | `missing_required_output_marker` |
    | `unknown_anchor` | `blocked` | `unknown_anchor` |
    | `response_too_long` | `blocked` | `response_too_long` |
    | `response_incomplete` | `blocked` | `response_incomplete` |

  - `test_every_writer_stop_reason_maps_to_exact_run_reason` 同步。

Tests：

- `tests/fund/test_chapter_writer.py`
  - 新增 `test_writer_prompt_requires_body_sections_and_required_output_markers()`。
  - 新增 `test_writer_blocks_missing_required_body_section_before_audit()`。
  - 新增 `test_writer_blocks_missing_required_output_marker_before_audit()`。
  - 新增 `test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text()`，覆盖 `length` 与 `content_filter` 至少一种 finish reason。
  - 更新 `_valid_chapter_markdown()`，让测试合法章节包含 required output markers。
  - 保持未知 anchor、未知 missing、超长、禁用交易建议测试。
- `tests/services/test_chapter_orchestrator.py`
  - 更新 stop reason mapping test。
  - 新增 orchestrator 对新增 writer stop reason 的 fail-closed mapping test，避免 `ValueError`。

Validation for slice：

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py -q
```

Completion signal：

- 缺 marker / 输出不完整或内容过滤 / 未授权 anchor 在 writer result 中有稳定 stop reason。
- 现有 happy path fake writer 仍 accepted。

Stop condition：

- 如果 required output marker 与现有模板 `required_output_items` 之间存在无法 exact match 的 item 文案，应停止并交回 controller，不允许 implementation agent 自行改模板。

### Slice B: auditor line protocol and calibration

Objective：强化 LLM audit prompt 的行协议，使 parse failure 可解释且稳定 blocked，同时校准 candidate facet 误杀/漏杀边界。

Allowed files：

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py`

Exact changes：

- 在 `_audit_contract_markers()`：
  - 把 contract required output 审计从“裸 item text 出现即可”改为检查 exact marker `<!-- required_output:<item> -->`。
  - 缺 marker 时继续产生 `C2` blocking issue，repair_hint=`patch`，location 使用 required output item 文案。
  - 不把裸 item text 当作 pass 条件；即使正文含 item 文案但缺 marker，也必须 fail-closed。
- 在 `_llm_request()`：
  - system prompt 明确“只返回固定行协议，不返回 Markdown/JSON/解释性文字”。
  - user prompt 明确 PASS 唯一格式、issue 行格式、severity 枚举、location/message 非空、禁止额外文字。
  - 加入 1 个 pass 示例和 1 个 blocking 示例。
- `_parse_llm_audit_response()`：
  - 保持 `PASS|chapter|no issues` 精确 pass。
  - 保持 parse failure -> blocked。
  - 对多余解释性行、未知 severity、空 location、空 message 继续 parse failure。
  - 不允许将 INFO-only 以外的 issue pass。
- `_llm_parse_failure()`：
  - message 增加最小修复提示：“auditor 必须返回 PASS|chapter|no issues 或 SEVERITY|LOCATION|MESSAGE 行协议”。
  - 不记录完整 provider response 到 issue message；`raw_response` 字段可保留现有 test fake response，但真实 smoke artifact 不得复制完整内容。
- `_audit_non_asserted_facets()`：
  - 允许“候选/未断言信息：<facet> 仅为候选标签，不能写成本基金属于该 facet”这类否定说明通过。
  - 继续阻断“本基金是/属于/定位为/可判定为 <facet>”。
  - MVP 去重策略固定为 first blocking occurrence per unique facet text：同一 facet text 出现多次时，只报告第一处 blocking occurrence；只要存在任一 asserted occurrence，该 facet 仍 blocking；不得因为后文有候选/未断言 disclaimer 而放过前文 asserted occurrence。

Tests：

- 更新 `tests/fund/test_chapter_auditor.py` 的 `_valid_markdown()` helper：合法章节必须包含每个 `contract.required_output_items` 对应的 `<!-- required_output:<item> -->` marker，避免测试 helper 与 writer protocol 脱节。
- 新增 `test_programmatic_audit_requires_required_output_marker_not_bare_item_text()`：正文包含 required output item 裸文案但缺 marker 时触发 C2。
- 新增或更新 `test_programmatic_audit_passes_required_output_marker_protocol()`：合法 marker 存在时不因 required output marker 阻断。
- 新增 `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol()`。
- 新增 `test_llm_audit_blocks_markdown_or_explanatory_prefix()`。
- 新增 `test_non_asserted_facet_candidate_disclaimer_passes()`。
- 新增 `test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet()`：同一 facet 多处 asserted 只输出一个 issue，但仍 blocking。
- 保持 `test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact()`。
- 保持 `test_llm_audit_parse_failure_is_blocked()`，并断言 issue message 包含行协议修复提示。

Validation for slice：

```bash
uv run pytest tests/fund/test_chapter_auditor.py -q
```

Completion signal：

- LLM audit parse failure 不会 pass。
- candidate facet disclaimer 不被误杀，asserted candidate facet 仍被阻断。

Stop condition：

- 如果校准需要识别基金类型语义或外部事实，不在本 slice 实现；停止并交回 controller。

### Slice C: repair context and timeout classification

Objective：regenerate 必须携带上一轮失败原因；provider timeout 必须稳定分类；最大轮次保持 bounded。

Allowed files：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_provider.py`
- `tests/ui/test_cli.py`

Exact changes：

- 在 `chapter_writer.py`：
  - 新增 `ChapterRepairContext` dataclass。
  - `ChapterWriterInput` 新增 `repair_context: ChapterRepairContext | None = None`，默认 `None`。
  - `ChapterLLMRequest` 新增 `repair_context: ChapterRepairContext | None = None` 或等价显式字段；不得使用 dict / extra payload。
  - `build_chapter_prompt()` 在存在 repair context 时追加“上一轮失败原因”和“必须修复项”，并要求本轮不要重复上一轮 issue。
  - `_llm_request_from_prompt()` 传递 repair context。
- 在 `chapter_orchestrator.py`：
  - 新增 Service stop reason literals：`llm_timeout`、`llm_rate_limited`、`llm_malformed_response`、`llm_network_error`。
  - `_run_single_chapter()` 初始 writer input 不带 repair context。
  - 当 `_decide_repair()` 返回 `regenerate` 时，下一轮重新构造 writer input，携带从上一轮 audit result 派生的 `ChapterRepairContext`。
  - `_repair_context_from_audit()` 只使用 issue ids、rule/location/message 的脱敏摘要，不包含 draft 全文或 provider raw response。
  - `_required_corrections_from_issues()` 使用 8.4 的 deterministic mapping 生成 corrections；未知规则使用 sanitized issue message fallback，并限制长度。
  - `_exception_result()` 根据 `LLMProviderTimeoutError` / rate limit / malformed / network 分类 stop reason；未知异常继续 `llm_exception`。
  - 保持 `max_repair_attempts` bounded，不新增无限 retry/backoff。
- 在 `llm_provider.py`：
  - 新增 `LLMProviderTimeoutError(LLMProviderRuntimeError)`。
  - 可选新增 `LLMProviderNetworkError(LLMProviderRuntimeError)`。
  - timeout 捕获抛 `LLMProviderTimeoutError("LLM provider request timed out")`。
  - network 捕获抛 `LLMProviderNetworkError("LLM provider network error")`。
  - rate limit / malformed 维持现有 typed exceptions。

Tests：

- `tests/fund/test_chapter_writer.py`
  - 新增 `test_repair_context_is_rendered_into_writer_prompt_without_extra_payload()`。
  - 新增 `test_llm_request_carries_typed_repair_context()`。
- `tests/services/test_chapter_orchestrator.py`
  - 新增 `test_regenerate_request_contains_previous_failure_context()`，fake writer 第一次返回缺 marker，第二次断言 request.repair_context 包含 issue ids/messages。
  - 新增 `test_required_corrections_are_deterministic_for_known_issue_patterns()`，覆盖 P1 结构、C2 required output、C2 candidate facet、E1 anchor、`llm:parse_failure`。
  - 新增 `test_required_corrections_sanitize_unknown_issue_message()`，断言 fallback 不含 raw response、draft 全文、Authorization/Bearer/API key/prompt。
  - 更新 `test_repairable_audit_failure_retries_and_second_pass_accepts()`，断言两次 writer request 的 attempt context。
  - 保持 `test_max_repair_attempts_zero_does_not_retry_after_audit_failure()`。
  - 新增 timeout/rate limit/malformed/network exception mapping tests。
- `tests/services/test_llm_provider.py`
  - 更新 timeout test，断言抛 `LLMProviderTimeoutError` 且不泄漏 prompt/key。
  - 新增 network typed error test。
- `tests/ui/test_cli.py`
  - 增加或更新 `--use-llm` provider runtime timeout fail-closed 测试，断言 exit code `1`、empty stdout、stderr/diagnostic 不含 secret，不 fallback deterministic。

Validation for slice：

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_provider.py tests/ui/test_cli.py -q
```

Completion signal：

- 第二轮 regenerate 的 writer request 能看到上一轮失败原因。
- timeout 被分类为 `llm_timeout` 或等价稳定 category，不再只表现为泛化 `llm_exception`。
- `max_repair_attempts` 仍阻止无限重试。

Stop condition：

- 如果需要修改 CLI exit contract 或 stdout/stderr 基本语义，停止并交回 controller；本 gate 只允许精确化 fail-closed reason。

### Slice D: acceptance smoke and docs decision

Objective：完成 fake-client 回归、真实 provider smoke、secret scan 和必要 README 同步。

Allowed files：

- `fund_agent/fund/README.md`
- `tests/README.md`
- 只在前序 slices 实际改变 public Fund/test contract 时编辑。

Exact changes：

- 如果 `ChapterRepairContext` 或 required output marker 成为 Fund writer/auditor public contract：
  - `fund_agent/fund/README.md` 增加当前 writer/auditor contract 简述：固定结构段落、required output marker、anchor/missing marker、candidate facet 边界、parse failure fail-closed。
- 如果新增测试命令或真实 smoke 说明需要记录：
  - `tests/README.md` 只记录测试分层和运行方式，不记录 API key 或 provider response。
- 如果 README 当前未涉及这些内部 primitive，可在 implementation report 中记录 docs decision 为“不更新 README，因用户-facing CLI 和包级使用入口未变”。该决定需由 reviewer 接受。

Tests / validation：

- 运行 full validation matrix 中所有命令。
- 真实 provider smoke 至少覆盖 `006597 / 2024`。

Completion signal：

- 真实 provider smoke 不是 deterministic fallback。
- 成功时输出包含第 0-7 章、证据锚点、章节审计状态。
- 失败时 fail-closed reason 属于可修复 category，例如 missing marker、parse failure、llm_timeout、repair_budget_exhausted；不得误报 missing provider config。

Stop condition：

- 如果真实 provider 出现新的 provider auth/config error，停止并交回 controller，因为 provider/auth 已由上一 gate 判定可用，本 gate 不重新设计 config。

## 11. Validation matrix

Implementation agent 完成所有 slices 后必须运行并记录结果：

```bash
uv run ruff check .
```

```bash
uv run pytest \
  tests/fund/test_chapter_writer.py \
  tests/fund/test_chapter_auditor.py \
  tests/services/test_chapter_orchestrator.py \
  tests/services/test_llm_provider.py \
  tests/ui/test_cli.py \
  -q
```

Full pytest coverage command：

```bash
uv run pytest --cov=fund_agent --cov-report=term-missing
```

Deterministic default smoke：

```bash
uv run fund-analysis analyze 006597 --report-year 2024
```

Expected：

- exit code `0`。
- 默认 deterministic 行为不变。
- 输出包含模板 0-7 章。

Missing-config fail-closed smoke：

```bash
env -u FUND_AGENT_LLM_PROVIDER -u FUND_AGENT_LLM_BASE_URL -u FUND_AGENT_LLM_API_KEY -u FUND_AGENT_LLM_MODEL \
  uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Expected：

- exit code `1`。
- stdout empty。
- stderr/diagnostic 说明 missing/invalid LLM config。
- 不 fallback deterministic report。

Real provider smoke command (label: `real-provider-smoke-006597-2024`)：

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Expected success path：

- exit code `0`。
- 输出包含第 0-7 章。
- 输出包含正文证据锚点或 anchor-derived evidence markers。
- 可定位章节审计状态 / accepted status。
- 不出现 deterministic fallback 标记或默认 deterministic report 替代。

Expected fail-closed path：

- exit code `1`。
- reason 是精确、可修复 category，例如 `missing_required_output_marker`、`missing_required_structure`、`response_incomplete`、`llm:parse_failure`、`llm_timeout`、`repair_budget_exhausted`、`unknown_anchor`。
- 不归因为 missing provider config，除非环境确实缺失且 controller 接受。
- 不泄漏 API key、Authorization header、完整 provider response 或完整 draft。

Boundary：

- 本命令在当前 gate 中只用于验证 contract-hardening 是否让输出协议可控、失败原因可分类。
- 是否将 `006597 / 2024` 作为 complete chapters `0-7` acceptance pass，由下一 gate `MVP real provider smoke acceptance gate` 裁决。
- 不得在当前 gate 中引入 scoring loop、自动 pro-codex repair task generation 或持续 pass-rate/evidence-compliance-rate 统计。

Secret scan：

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|token" docs/reviews reports tests fund_agent
```

Expected：

- 只允许出现配置变量名、测试 fake secret、或文档中的安全说明。
- 不允许出现真实 API key、Authorization header value、完整 provider response。

Diff hygiene：

```bash
git diff --check
```

Expected：

- 无 whitespace error。

## 12. Audit rule calibration guardrails

允许校准：

- 让 writer prompt 明确 required output marker 和 fixed headings，降低真实 provider 格式偏差。
- 让 `non_asserted_facets` 的否定/候选说明不被误杀。
- 按 first blocking occurrence per unique facet text 去重重复 facet issue，降低 regenerate prompt 噪音，同时保留任一 asserted occurrence 的 blocking 语义。
- 为 parse failure 和 timeout 增加更具体 category。

禁止校准：

- 不允许 required output item 缺失时 pass。
- 不允许缺证据锚点的数值判断 pass。
- 不允许 ITEM_RULE delete 内容重新出现。
- 不允许 candidate facet 变成 asserted fact。
- 不允许交易建议、买入/卖出、仓位、收益预测 pass。
- 不允许 E2 source verification 从 deferred 变成假通过；E2 仍由后续 Evidence Confirm gate 处理。
- 不允许用更宽松的自由文本猜测替代 marker/parser contract。

## 13. Review gates

Plan review：

- 至少两份独立 plan review，重点检查：
  - 是否足够 code-generation-ready。
  - 是否把 writer/auditor contract 与 Service repair ownership 分清。
  - 是否有过度放松审计边界。
  - 是否遗漏 timeout、max attempts、regenerate previous failures。

Implementation review：

- 每个 slice 完成后进入 code review。
- Review 重点：
  - parser 是否 fail-closed。
  - 新 stop reason 是否全链路映射。
  - repair_context 是否 typed explicit，不走 extra payload。
  - tests 是否覆盖真实 failure modes。
  - secret hygiene 是否保持。

Aggregate review：

- 所有 slices accepted 后，controller 应运行 aggregate deepreview。
- 若有 accepted findings，必须 fix / re-review 后再进入 local acceptance。

## 14. Stop conditions

Implementation agent 必须停止并交回 controller的情况：

- 需要修改 `docs/fund-analysis-template-draft.md` 或改变模板章节结构。
- 需要修改 golden / fixtures / score / quality gate / promotion state。
- 需要进入 Host/Agent/dayu 或新增 dayu dependency。
- 需要改变 CLI `--use-llm` user-visible success/failure contract beyond precise fail-closed reason。
- 需要记录或检查真实 API key、Authorization header、完整 provider response。
- 真实 provider smoke 失败原因回到 provider auth/config，且与上一 gate 结论冲突。
- fake-client tests 通过但真实 smoke 出现新的事实/证据缺口，需要 source probing 或 FundDocumentRepository 读取；本 gate 不处理 source probing。
- required output marker exact matching 与模板 contract 文案不可兼容。
- 需要把下一 gate `MVP real provider smoke acceptance gate` 的 complete chapters `0-7` acceptance 裁决写成本 gate 完成条件。
- 需要设计或实现 later gate 的 repeatable scoring、score history、failure-category-to-task mapping、自动 pro-codex repair tasks、pass-rate/evidence-compliance-rate improvement loop。

## 15. Risks / open questions

Blocking questions：无。当前证据足以开始 implementation；provider/auth 已由上一 gate 验证，不需要重新确认。

Non-blocking risks：

- 真实 provider 仍可能偶发超时。Working assumption：本 gate 只需稳定分类 timeout，并通过 bounded retry/repair 防止无限等待；provider retry/backoff 是后续 provider reliability gate。
- Required output marker 会增加 prompt 刚性，可能让模型输出更机械。Working assumption：MVP 优先可审计性；如果输出可读性下降，由后续 polish gate 处理。
- `non_asserted_facets` 中文断言检测仍可能有边缘误判。Working assumption：本 gate 只校准已知 false positive/false negative；不能为降低误杀而放过 asserted candidate facet。
- 真实 provider smoke 成功可能受模型波动影响。Working assumption：acceptance 允许 fail-closed，但 failure category 必须精确、可修复，且不能 deterministic fallback。
- 当前 gate 和下一 gate 都会运行或消费真实 provider smoke，但职责不同。Working assumption：当前 gate 只检查 contract controllability 和 failure classification；下一 gate 才判断 `006597 / 2024` 是否达到 complete chapters `0-7` acceptance 或记录剩余 blocker。
- Later score-loop gate 需要当前 gate 的 failure categories 作为输入。Working assumption：当前 gate 只保证 category 稳定，不设计 scoring metric、历史存储或自动 repair task formation。

## 16. Completion report format

Implementation agent 完成后必须输出 durable implementation artifact，建议路径由 controller 指定。报告至少包含：

```markdown
# MVP LLM writer/auditor contract hardening implementation evidence

Gate:
Role:
Approved plan:
Slice(s):

## Scope / non-goals
- Allowed files touched:
- Prohibited files untouched:
- No commit/push/PR:

## Changes
- Writer prompt/parser:
- Auditor line protocol/calibration:
- Repair/regenerate:
- Timeout classification:
- Docs decision:

## Validation
- `uv run ruff check .`:
- targeted pytest:
- full pytest coverage:
- deterministic default smoke:
- missing-config fail-closed smoke:
- real provider smoke:
- secret scan:
- `git diff --check`:

## Smoke result summary
- `006597 / 2024 --use-llm` status:
- Chapters 0-7 present or fail-closed reason:
- Evidence anchors:
- Chapter audit statuses:
- Deterministic fallback absent:

## Residual risks
- Fixed now:
- Covered by later slice:
- Deferred with owner:
- Requires controller/user decision:

## Self-check
Self-check: pass | blocked - <reason>
```

## 17. Final worker self-check

- 只触碰指定 plan artifact：是，本文档为唯一计划产物。
- 未进入 implementation：是，本文没有运行或描述已完成的代码修改。
- 未修改运行时代码：是。
- 未 commit / push / PR / merge：是。
- Handoff-ready / code-generation-ready：是；每个 slice 已指定 allowed files、exact changes、tests、validation、completion signal 和 stop condition。
