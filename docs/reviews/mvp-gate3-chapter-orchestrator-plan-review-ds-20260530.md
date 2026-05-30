# MVP Gate 3 chapter_orchestrator — Plan Review (AgentDS)

日期：2026-05-30
审查角色：AgentDS，独立 plan reviewer
审查目标：`docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`
审查结论：**BLOCKED**

---

## Reviewed Target and Scope

Target: MVP Gate 3 `chapter_orchestrator` implementation plan。该 plan 声称设计 Service 层 write-audit-repair policy，编排第 1–6 章 write-audit 闭环，输出 `AcceptedChapterConclusion` 供 Gate 4 final assembler 消费。

Scope of this review: Service/Fund 边界正确性、typed contract（禁止 extra_payload）、第 0/7 章/final assembler/CLI/dayu/source/promotion scope creep、write-audit-repair policy 正确性、依赖与 fail-closed 状态、repair budget、Gate 4 输入契约、测试/验证充分性、implementation readiness。

---

## Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|--------|
| A1 | `ChapterRunStopReason` literal 覆盖所有 writer/auditor 可能产生的停止原因 | **证伪** — 缺少 `llm_empty_response`、`llm_contract_violation`；`evidence_anchor_missing`、`item_rule_deleted_required_content` 映射歧义 |
| A2 | `ChapterOrchestrator.orchestrate()` 与 `orchestrate_chapters()` 契约一致 | **证伪** — class façade 缺少 `fact_provider` 参数 |
| A3 | Repair loop 能区分可重试失败与基础设施不可用 | **证伪** — auditor LLM unavailable 触发无意义 regenerate retry |
| A4 | 所有 writer stop reason 到 orchestrator stop reason 的映射是显式且无歧义的 | **证伪** — 多个 writer reason 映射为 "或" 关系 |
| A5 | Plan 足够具体，implementation agent 无需自行设计 public contract | **部分证伪** — `_decide_repair()` 未定义签名/逻辑；Service `__init__.py` 导出未指定 |
| A6 | `AcceptedChapterConclusion` 提取逻辑的边界条件已覆盖 | **证伪** — 无 `###` 标题时整篇 draft 可能成为 conclusion |

---

## Findings

### 1-BLOCKING-ChapterRunStopReason 未覆盖全部 writer 停止原因

- **位置**: §7.1 `ChapterRunStopReason` literal；§8 step 5 writer blocked mapping；§9.8
- **问题类型**: 契约缺失
- **当前写法**: `ChapterRunStopReason` 定义了 12 个 literal 成员。§8 step 5 对 writer blocked 的映射仅覆盖 `llm_unavailable`、`fund_type_unknown`、`missing_required_facts`/`evidence_anchor_missing`/`item_rule_deleted_required_content`（映射为 `missing_required_facts` 或 `writer_blocked`）、`chapter_requires_accepted_conclusions`。未提及 `llm_empty_response` 和 `llm_contract_violation`。
- **反例/失败场景**: writer 调用 LLM，LLM 返回空字符串 → `write_chapter()` 返回 status=blocked, stop_reason=`llm_empty_response` → orchestrator 的 `ChapterRunStopReason` 无对应成员 → implementation agent 必须自行决定映射为 `writer_blocked`（泛化）或修改 literal（重新设计 contract）。
- **为什么有问题**: plan 自身 §9.8 规定 "stop reason 必须来自 writer stop reason 的显式 mapping，不得泛化为 unknown"，但 mapping 表本身不完整。implementation agent 收到 plan 后无法 code-generation-ready 地实现映射逻辑。
- **直接证据**:
  - `chapter_writer.py:29-39` — `ChapterWriteStopReason` 包含 `llm_empty_response`、`llm_contract_violation`
  - plan §7.1 `ChapterRunStopReason` — 不含上述两项
  - plan §8 step 5 — mapping 表未提及上述两项
- **影响**: 实施 Agent 必须自行设计 stop reason mapping，可能引入歧义或违反 plan 自身 fail-closed 约束
- **建议改法和验证点**:
  1. 在 `ChapterRunStopReason` 中补入 `llm_empty_response` 和 `llm_contract_violation`，或显式声明它们统一映射为 `writer_blocked`
  2. `evidence_anchor_missing` 和 `item_rule_deleted_required_content` 的去向必须精确（当前用"或"连接两个不同目标），建议统一为 `writer_blocked` 并说明原因
  3. 在 §8 step 5 列出 **完整映射表**：每个 `ChapterWriteStopReason` → `ChapterRunStopReason`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: BLOCKING

---

### 2-BLOCKING-ChapterOrchestrator.orchestrate() 缺少 fact_provider 参数

- **位置**: §7.6 Public API
- **问题类型**: 契约缺失 / 不可直接实施
- **当前写法**:
  ```python
  def orchestrate_chapters(input_data, *, llm_clients, fact_provider=None)  # 有 fact_provider
  class ChapterOrchestrator:
      def orchestrate(self, input_data, *, llm_clients)  # 无 fact_provider
  ```
- **反例/失败场景**: 调用方使用 `ChapterOrchestrator().orchestrate()` 并传入 `input_kind="structured_bundle"` → orchestrator 需要调用 `ChapterFactProvider.project()` → 若类未持有 provider 引用且方法签名无此参数，只能 hardcode `ChapterFactProvider()` 或 raise runtime error。
- **为什么有问题**: plan §7.6 明确声明 `fact_provider` 是"可注入 façade，不是 Service 重新实现 domain projection"。class façade 不符合该声明。同时与 module-level 函数的签名不一致，implementation agent 需自行裁决。
- **直接证据**: plan §7.6 两个函数签名对比；plan §7.6 约束描述 "fact_provider 是可注入 façade"
- **影响**: 实施 Agent 必须修改 public contract 才能实现；两个 API 入口行为不同，导致测试与生产路径不一致
- **建议改法和验证点**:
  1. `ChapterOrchestrator.__init__` 接受 `fact_provider: ChapterFactProvider | None = None`，在 `orchestrate()` 中使用 `self._fact_provider`
  2. 或 `orchestrate()` 增加 `fact_provider` 参数与 standalone 函数对齐
  3. 验证两种路径在 `structured_bundle` 输入模式下行为一致
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: BLOCKING

---

### 3-BLOCKING-Auditor LLM unavailable 触发无意义 regenerate retry

- **位置**: §8 step 6 repair loop；§9.7 LLM unavailable；§9.9 auditor fail/blocked
- **问题类型**: 状态机漏洞
- **当前写法**: §9.9 — `audit_result.status == "blocked"` → chapter blocked，unless repair hint 是 `regenerate`/`patch` 且 budget 仍可用。§9.7 — auditor unavailable 时 audit blocked，orchestrator 可按 repair policy 重试一次。
- **反例/失败场景**:
  1. `llm_clients.auditor is None` 且 `run_llm_audit=True`
  2. writer 成功 drafted → audit → `audit_chapter()` 返回 status=blocked, repair_hint=regenerate（`_aggregate_repair_hint` 源码 `chapter_auditor.py:959`: empty issues + blocked status → regenerate）
  3. orchestrator repair loop 判定 regenerate 且 budget>0 → 重新调用 writer（成功）→ 重新调用 auditor（再次 blocked，原因相同）→ 浪费一次 repair attempt
  4. 若 `max_repair_attempts=1`，唯一一次修复被浪费在不可修复的问题上
- **为什么有问题**: repair loop 无法区分"内容有问题可以重写修复"与"基础设施缺失重试无意义"。`repair_hint` 是审计层语义，表达的是"草稿的可修复性"，不是"审计失败的可重试性"。当审计本身因为缺少 client 而 blocked 时，repair_hint 不应驱动 retry。
- **直接证据**:
  - `chapter_auditor.py:377-396` — `audit_chapter_llm()` 在 `llm_client is None` 时返回 status=blocked, repair_hint=regenerate
  - `chapter_auditor.py:958-960` — `_aggregate_repair_hint` 逻辑
  - plan §9.9 — blocked 状态下仍按 repair_hint 决策重试
- **影响**: repair budget 被浪费；orchestrator 对外表现为 `partial` + `repair_budget_exhausted`，掩盖真实原因（auditor 不可用）
- **建议改法和验证点**:
  1. orchestrator 在调用 auditor 前做 preflight：若 `run_llm_audit=True` 且 `llm_clients.auditor is None`，直接 blocked `llm_unavailable`，不进入 repair loop
  2. `audit_result.status == "blocked"` 时检查 blocked 原因：若来自 `LLM_UNAVAILABLE`，直接 stop，不重试
  3. repair loop 决策应考虑 `audit_result.llm.status == "blocked"` 作为不可重试信号
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: BLOCKING

---

### 4-HIGH-Stop reason 映射存在歧义（"或"）

- **位置**: §8 step 5 writer blocked mapping
- **问题类型**: 不可直接实施
- **当前写法**: `missing_required_facts` / `evidence_anchor_missing` / `item_rule_deleted_required_content` -> blocked `missing_required_facts` **或** `writer_blocked`
- **反例/失败场景**: writer 因 `evidence_anchor_missing` blocked → implementation agent 需在 `ChapterRunStatus.blocked` + `stop_reason` 中选择 `missing_required_facts` 还是 `writer_blocked` → 两个选择语义不同：前者暗示"数据不够"，后者暗示"写作失败但可重试"
- **为什么有问题**: 歧义映射使 implementation agent 必须自行裁决语义，可能在不同章节产生不一致的 stop reason，影响 Gate 4 对失败模式的判断
- **直接证据**: plan §8 step 5 原文 "blocked `missing_required_facts` 或 `writer_blocked`"
- **影响**: 实施 Agent 自行裁决 → 行为不一致 → Gate 4 收到不可靠的 stop reason 信号
- **建议改法和验证点**:
  1. 统一映射：所有 writer preflight 导致的 blocked（包括 `evidence_anchor_missing`、`item_rule_deleted_required_content`、`missing_required_facts`）统一为 `missing_required_facts`（因为都是数据不足，不是写作能力不足）
  2. `writer_blocked` 保留给 writer 返回 blocked 但原因不属于已知分类时使用
  3. 在 §8 step 5 用表格替代 prose，每个 writer stop reason → 恰好一个 orchestrator stop reason
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高）**: HIGH

---

### 5-HIGH-AcceptedChapterConclusion 无长度上限

- **位置**: §10 Accepted conclusion extraction
- **问题类型**: 契约缺失
- **当前写法**: §10 step 2 — "若没有 `### 结论要点` 但 audit accepted，取 markdown 第一段非空文本作为 fallback"
- **反例/失败场景**: 章节 draft 不使用 `###` 标题（例如 LLM 输出使用 `##` 或其他格式），整个 draft 被当作"第一段" → `conclusion_markdown` 包含完整章节正文（可达 12000 字符）→ `ChapterOrchestrationResult.accepted_conclusions` 膨胀 → Gate 4 消费时收到超长 conclusion
- **为什么有问题**: `AcceptedChapterConclusion` 的定位是"结论摘要"供 Gate 4 assembly 使用，不是完整章节正文（正文已有 `accepted_draft`）。无长度上限的 fallback 违反该语义。
- **直接证据**: plan §10 step 2；plan §7.5 `AcceptedChapterConclusion` 无 `max_chars` 约束
- **影响**: Gate 4 收到不可预期的超长 conclusion；Chapter 0 摘要基于超长文本产生低质量输出
- **建议改法和验证点**:
  1. `conclusion_markdown` 增加硬上限（如 500 字符），超过则截断并标记
  2. fallback 场景同时检查 `###` 和 `##` 标题
  3. 若 draft 完全没有标题分段，使用前 N 个非空行而非整篇
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高）**: HIGH

---

### 6-MEDIUM-_decide_repair() 未定义签名和决策逻辑

- **位置**: §8 step 6；§12 Slice 3
- **问题类型**: 不可直接实施
- **当前写法**: "调用 `_decide_repair(audit_result, remaining_budget)`" — 函数名和入参提及但无签名、返回值类型、决策表
- **反例/失败场景**: implementation agent 自行设计 `_decide_repair()` → 可能遗漏边界条件（如 `repair_hint="none"` + `accepted=False`、`status="blocked"` + `repair_hint="regenerate"` 但 auditor unavailable）→ repair 决策与 plan 意图偏离
- **为什么有问题**: repair 决策是 write-audit-repair loop 的核心状态机，plan 只描述行为意图但未给出可实施的函数契约
- **直接证据**: plan §8 step 6 提及 `_decide_repair` 但无签名定义；plan §7 的 dataclass 中有 `ChapterRepairDecision` 和 `ChapterRepairAction` 但未绑定到函数
- **影响**: 实施 Agent 需自行设计核心决策函数，review 无法验证 repair 语义是否正确实现
- **建议改法和验证点**:
  1. 补全 `_decide_repair()` 签名：`def _decide_repair(audit_result: ChapterAuditResult, *, remaining_budget: int, auditor_available: bool) -> ChapterRepairDecision`
  2. 提供决策表：每个 `(status, repair_hint, remaining_budget, auditor_available)` 组合 → `ChapterRepairAction`
  3. 特别处理 auditor blocked 不可重试的情况（关联 Finding 3）
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高）**: MEDIUM

---

### 7-MEDIUM-Service __init__.py 导出列表未指定

- **位置**: §6 推荐总体方案；§12 Slice 4
- **问题类型**: 不可直接实施
- **当前写法**: "fund_agent/services/__init__.py：仅导出 public dataclass / service façade"
- **反例/失败场景**: implementation agent 需自行决定哪些 dataclass 导出（共约 12 个新类型），可能与现有 `__init__.py` 模式不一致（现有导出 includes Service class + Request/Result types）
- **为什么有问题**: plan 没有列出应导出的具体类型名称，implementation agent 可能导出过多（泄漏内部类型）或过少（Gate 4 无法 import）
- **直接证据**: plan §6 描述；现有 `fund_agent/services/__init__.py` 导出 pattern
- **影响**: Gate 4 接入时可能需要调整 import 路径
- **建议改法和验证点**: 明确列出 `__all__` 应包含的类型：`ChapterOrchestrator`、`ChapterOrchestrationInput`、`ChapterOrchestrationResult`、`ChapterOrchestrationPolicy`、`ChapterOrchestratorLLMClients`、`build_chapter_orchestration_input()`、`orchestrate_chapters()`。内部 dataclass（`ChapterRunResult`、`ChapterAttemptRecord` 等）由 result 嵌套访问，不单独导出
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高）**: MEDIUM

---

### 8-LOW-Repair loop 复用相同 ChapterWriterInput，LLM 可能重复生成相同失败输出

- **位置**: §8 step 6；§16 Residual risks
- **问题类型**: 非最优方案
- **当前写法**: "重新调用 writer 时必须使用同一个 `ChapterWriterInput`。Gate 3 不改变 Fund prompt contract"
- **反例/失败场景**: audit 发现 must_not_cover 违规 → repair → 重新调用 writer 使用完全相同的 prompt → LLM 可能输出几乎相同的违规文本 → audit 再次失败 → budget 耗尽 → chapter failed
- **为什么有问题**: 不带 repair context 的 regeneration 有效性存疑。plan 已在 §16 中列为 residual risk 并接受，但未评估这对 MVP 可接受率的实际影响。
- **直接证据**: plan §8 step 6；plan §16 row 1, row 2
- **影响**: 多章可能因相同原因反复失败，orchestrator 实际 accept 率可能很低
- **建议改法和验证点**:
  1. 在 residual risk 中增加量化估计：当 audit 失败原因为结构性/内容性（非数据缺口）时，同 prompt regeneration 的预期修复率
  2. 考虑最小可行改进：在 regenerate 时追加一句 repair hint 到 user_prompt（作为显式参数，不经过 extra_payload），需先确认不违反 Gate 2 contract
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高）**: LOW

---

### 9-INFO-第 5 章单期 bundle 下 accept 概率未评估

- **位置**: §9.4 第 5 章跨期缺失
- **问题类型**: open question 未收敛
- **当前写法**: "若 writer 能以'缺少跨期数据/下一步最小验证问题'方式通过 audit，章节可 accepted"
- **反例/失败场景**: writer 被要求不输出跨期确定性断言 → writer 遵守 → auditor `_audit_missing_semantics()` 检查跨期断言并通过 → 第 5 章可能 accepted。但另一种情况：writer 遵守但输出过于含糊 → LLM auditor 判定 REVIEWABLE → audit fail → repair → regenerate → 同 prompt 同输出 → budget exhausted → 第 5 章永远 failed。
- **为什么有问题**: 没有评估在 `cross_period_comparison_missing` 条件下，writer 通过 programmatic + LLM audit 的实际概率。如果概率很低，`partial` 将成为 orchestrator 的常态输出。
- **直接证据**: plan §9.4；`chapter_auditor.py:707-745` `_audit_missing_semantics` 逻辑
- **影响**: orchestrator 实际可用性可能低于预期；Gate 4 经常收到不完整的 accepted_conclusions
- **建议改法和验证点**: 非 blocking — 可在 implementation 后通过实际测试数据观察；建议在 residual risk 中记录并给出可接受的 `partial` 频率阈值
- **修复风险（低/中/高）**: N/A
- **严重程度（低/中/高）**: INFO

---

## Open Questions

1. `orchestrate_chapters()` 若 `fact_provider` 为 None 且 input_kind 为 structured_bundle，是否默认使用 `ChapterFactProvider()`？plan §7.6 说 "fact_provider or ChapterFactProvider()"，但未说明 ChapterFactProvider 的无参构造是否总是安全（源码确认：`ChapterFactProvider` 是无状态 façade，无参构造安全）。

2. 当 `run_llm_audit=False` 时，`audit_chapter()` 跳过 LLM 审计返回 `status="pass"`。若 programmatic audit 也 pass，整体 accepted。这意味着仅程序审计可接受章节。plan 是否预期 production 路径使用 `run_llm_audit=False`？§7.3 policy 默认 `run_llm_audit=True`，但 §7.3 校验规则说 `run_programmatic_audit=False` 只允许测试使用。对 `run_llm_audit` 没有等价约束。

---

## Residual Risks

| Risk | Disposition |
|------|-------------|
| 同 prompt regeneration 修复率不明 | 已在 §16 接受；建议在 implementation evidence 中记录实际修复率 |
| 第 5 章单期 bundle 下可能总是 partial | 已在 §16 接受为 cross-period data gate 的前置条件 |
| LLM exception 粒度粗（`llm_exception`） | 已在 §16 接受 |
| 无 typed patch API | 已在 §16 接受 |

---

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth、assumptions tested 已写清
- [x] findings 均为 evidence-based、adversarial、可执行，不含 style/nit/speculation
- [x] open questions、residual risks 与 findings 已分开
- [x] conclusion 为 BLOCKED
- [x] output path 使用本机系统时钟生成的 timestamp

---

## Final Verdict: BLOCKED

3 个 BLOCKING findings 必须修复后 plan 才能交给 implementation agent：

1. **Finding 1** — `ChapterRunStopReason` 未覆盖全部 writer stop reason，mapping 表不完整
2. **Finding 2** — `ChapterOrchestrator.orchestrate()` 缺少 `fact_provider` 参数，与 standalone 函数不一致
3. **Finding 3** — Auditor LLM unavailable 触发无意义 regenerate retry，repair loop 未区分基础设施失败与内容失败

另有 2 个 HIGH、2 个 MEDIUM、1 个 LOW、1 个 INFO finding 建议在修复 BLOCKING 项时一并处理。

所有 finding 修复风险均为低或中，不涉及结构性重新设计。预期 plan 可在一次修订轮次内收敛到 PASS。
