# Plan Review: MVP Gate 3 chapter_orchestrator

日期：2026-05-30
角色：AgentMiMo independent plan reviewer
审查目标：`docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`
审查范围：Service/Fund boundary, typed contracts, scope creep, write-audit-repair policy, fail-closed states, repair budget, Gate 4 accepted conclusions, test adequacy, implementation readiness

## Assumptions Tested

1. Service 层 owns write-audit-repair policy — 对照 `AGENTS.md`、`docs/design.md` §5.4.1 Route C Gate 3 和 `docs/implementation-control.md` Gate 3 边界。
2. Gate 1 / Gate 2 accepted public APIs 与 plan 描述一致 — 对照 code facts 和 controller judgments。
3. Plan 不引入 Host/Agent/dayu/runtime/CLI/promotion — 对照 non-goals 和 design docs。
4. Repair policy 可在现有 Gate 2 primitives 上实现 — 对照 `chapter_writer.py` 和 `chapter_auditor.py` 代码。
5. Accepted conclusion extraction 方式可 deterministic 执行 — 对照 Gate 2 auditor 的结构检查。
6. `ChapterFactProjection` 支持部分章节投影 — 对照 `project_chapter_facts()` 校验逻辑。

## Findings

### 1-未修复-MEDIUM-repair loop 对程序化审计 patch 问题实际无效
- **位置**: §8 步骤 6 repair loop，§6 核心决策"patch 和 regenerate 都映射为 regenerate attempt"
- **问题类型**: 非最优方案
- **当前写法**: "`patch` -> MVP 映射为 `regenerate`，因为 Gate 2 尚无 typed patch API，不能 ad hoc string patch"；"重新调用 writer 时必须使用同一个 `ChapterWriterInput`"
- **反例/失败场景**: 章节草稿包含 `must_not_cover` 禁区短语（C2/patch hint）、缺少 required output item marker（C2/patch hint）或 R=A+B-C 数字断言缺少邻近 anchor marker（L1/patch hint）。Repair hint 为 `patch`，映射为 `regenerate`，但 writer 收到完全相同的 `ChapterWriterInput`，大概率生成包含相同问题的相同输出，浪费一次 LLM 调用后仍以 `repair_budget_exhausted` 停止。
- **为什么有问题**: Gate 2 auditor 的 `repair_hint` 是程序审计对问题的精确分类，但相同输入无法传递修复意图。对于 patch 类问题（删除特定短语、添加缺失标记），writer 需要具体的修复指令才能有效改善。当前设计下，`max_repair_attempts=1` 意味着每次 patch 问题都必然浪费一次 writer 调用后才停止。
- **直接证据**: `chapter_auditor.py:549` — `repair_hint="patch"` for C2 missing required items; `chapter_auditor.py:579` — `repair_hint="patch"` for must_not_cover; plan §8 step 6 "重新调用 writer 时必须使用同一个 ChapterWriterInput"
- **影响**: 修复循环对所有 patch 类问题实际退化为"再试一次同样的事"。不产生安全问题（budget 有限，最终正确停止），但每次 patch 类 audit fail 都浪费一次 LLM writer 调用。
- **建议改法和验证点**: 接受为 MVP 安全策略，但应在 plan 中显式记录：(1) patch -> regenerate 映射在当前设计下是 best-effort；(2) 如果实测 patch 类问题的 regenerate 成功率接近 0%，Gate 3/4 应考虑传递 repair context 到 writer prompt。验证点：实现后用 fake writer 测试 patch 问题是否确实浪费预算后停止。
- **修复风险（低/中/高）**: 中 — 需要 contract extension 才能真正解决
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-MEDIUM-auditor None 时 regenerate 重试浪费 writer 调用
- **位置**: §9.7 "LLM unavailable / exceptions"，§8 step 6 repair loop
- **问题类型**: fail-closed 状态处理不精确
- **当前写法**: "`llm_clients.auditor is None` 且 `run_llm_audit=True`：audit blocked，orchestrator 可按 repair policy 重试一次，但若 auditor 仍 unavailable，最终必须 blocked/partial，不得 pass"
- **反例/失败场景**: 调用方传入 `ChapterOrchestratorLLMClients(writer=real_client, auditor=None)`，`run_llm_audit=True`。首次 write 成功 → audit 阻塞（`LLM_UNAVAILABLE`）→ repair hint `regenerate` → orchestrator 重新调用 writer（消耗一次 LLM 调用）→ 再次 audit 阻塞 → 最终停止。第二次 writer 调用完全无意义，因为 auditor 不可用是 structural 状态，不会因重试改变。
- **为什么有问题**: Gate 2 `audit_chapter_llm` 在 `llm_client is None` 时返回 `status="blocked"` 且 issue `repair_hint="regenerate"`。Orchestrator 的 `_decide_repair()` 按 repair hint 决策，未区分"audit blocked 因为 auditor client 缺失"和"audit blocked 因为 LLM response 解析失败"。前者是 fail-closed structural 状态，重试无法改善。
- **直接证据**: `chapter_auditor.py:377-393` — `llm_client is None` 返回 `status="blocked"`, `repair_hint="regenerate"`; plan §9.7 承认可重试但最终仍 blocked
- **影响**: 每次 auditor None 场景浪费一次 writer LLM 调用。不产生安全问题（budget=1，最终正确停止），但增加了不必要的成本。
- **建议改法和验证点**: 在 `_decide_repair()` 中增加判断：若 `audit_result.llm.status == "blocked"` 且 issue 中包含 `LLM_UNAVAILABLE` rule code，直接返回 `stop` 而非 `regenerate`。验证点：测试 auditor=None 场景应 0 次 writer 重试。
- **修复风险（低/中/高）**: 低 — 纯新增 guard 条件
- **严重程度（低/中/高/严重）**: 中

### 3-未修复-LOW-ChapterOrchestrator 类与 orchestrate_chapters 函数双入口暴露范围未收敛
- **位置**: §7.6 Public API
- **问题类型**: 架构边界
- **当前写法**: 同时暴露 `orchestrate_chapters()` 自由函数和 `ChapterOrchestrator.orchestrate()` 方法，二者签名几乎相同
- **反例/失败场景**: Gate 4 CLI 接入时，实现 agent 不确定应调用哪个入口；如果两个入口有不同的注入语义（如 class 持有 state），可能导致使用不一致。
- **为什么有问题**: §7.6 约束说明 `orchestrate_chapters()` 使用注入的 `fact_provider`，但 `ChapterOrchestrator` 类的约束未说明是否应通过构造函数注入 `fact_provider` 或在 `orchestrate()` 中传入。二者职责分工不清。
- **直接证据**: plan §7.6 两个 API 签名
- **影响**: 实现 agent 需要自行判断，可能导致不一致的使用模式。
- **建议改法和验证点**: 收敛为一个主入口。推荐保留 `orchestrate_chapters()` 作为主 API（与 Gate 1/2 的 `project_chapter_facts()` / `write_chapter()` / `audit_chapter()` 风格一致），`ChapterOrchestrator` 仅作为可选 façade（如 Gate 2 的 `ChapterWriter` / `ChapterAuditor`）。明确 `ChapterOrchestrator` 不持有 state。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 4-未修复-LOW-partial 状态下 accepted_conclusions 的 Gate 4 消费契约未明确
- **位置**: §7.1 `ChapterOrchestrationStatus`、§7.5 `ChapterOrchestrationResult`
- **问题类型**: 契约缺失
- **当前写法**: "`partial` 表示至少一个 scoped chapter accepted，但并非全部 accepted；不得供 Gate 4 assembly 作为 complete report"
- **反例/失败场景**: Gate 4 final assembler 收到 `status="partial"` 的结果。`accepted_conclusions` 中有 chapter 1-3 的结论但缺少 chapter 4-6。Plan 说"不得作为 complete report"，但未说明 Gate 4 应该：(a) 拒绝 partial 结果，(b) 接受 partial 结果并生成不完整报告，还是 (c) 使用 partial accepted conclusions 跳过缺失章节。
- **为什么有问题**: Gate 3 输出是 Gate 4 输入。如果 Gate 3 不定义 partial 的消费契约，Gate 4 实现需要自行决策，可能导致不一致行为。
- **直接证据**: plan §7.1 `partial` 描述、§8 step 7 overall status
- **影响**: Gate 4 实现时可能需要额外设计决策。
- **建议改法和验证点**: 在 plan 的 §17 next gates 中增加一行记录："Gate 4 必须定义 `status=partial` 时的 assembly 行为"。验证点：Gate 4 plan review 时检查此项。
- **修复风险（低/中/高）**: 低 — 纯文档补充
- **严重程度（低/中/高/严重）**: 低

### 5-未修复-INFO-max_repair_attempts=0 跳过 repair loop 的行为未显式说明
- **位置**: §7.3 Policy dataclass
- **问题类型**: 不可直接实施
- **当前写法**: "`max_repair_attempts >= 0`，建议默认 1；MVP 不需要多轮复杂修复"
- **反例/失败场景**: 实现 agent 将 `max_repair_attempts=0` 解释为"允许 0 次 repair attempt"，但未明确是否应跳过 repair loop 直接标记为 failed/blocked。
- **为什么有问题**: `attempt 0 是初始写作`（§8 step 6），所以 `max_repair_attempts=0` 应该意味着"初始写作后 audit fail 直接 stop，不重试"。这是隐含的但实现 agent 可能需要显式确认。
- **直接证据**: plan §8 step 6 "attempt 0 是初始写作"、§7.3 `max_repair_attempts >= 0`
- **影响**: 轻微，实现 agent 应能推断。
- **建议改法和验证点**: 在 §7.3 或 §8 步骤 6 增加一句："`max_repair_attempts=0` 时，初始写作 audit fail 直接 stop，不进入 repair retry"。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: INFO

## Open Questions

无。所有 findings 已有直接证据支撑，不依赖 speculative concern。

## Residual Risks

| Risk | Disposition | Owner / next gate |
|---|---|---|
| patch -> regenerate 映射导致 repair 对 patch 类问题退化 | Accepted for MVP; plan 已记录 Gate 2 无 typed patch API | Future repair contract gate if regenerate success rate is near 0% |
| No repair hint injection into writer prompt | Accepted; avoids hidden prompt fields and Gate 2 contract churn | Future Gate 2/3 contract extension |
| E2 source verification remains deferred | Already accepted Gate 2 residual | Future Evidence Confirm gate |
| Chapter 5 cross-period evidence remains missing | Accept; no source probing in Gate 3 | Future cross-period data gate |
| LLM exceptions are coarse `llm_exception` | Accept for MVP; preserves fail-closed state | Future provider resilience gate |

## Reviewer Self-Check

- reviewed target, scope, source of truth 和 assumptions tested: 已写清
- findings 是否 evidence-based, adversarial, 可执行: 每个 finding 绑定到具体 plan 位置、code fact 或 design doc
- open questions, residual risks, tracking destination: 已与 findings 分开
- conclusion 只能是 pass / pass-with-risks / fail: 已确认
- output path 使用本机系统时钟: `20260530-091036`

## Conclusion

**PASS_WITH_NON_BLOCKING**

Plan 整体设计合理：Service/Fund 边界正确，typed contracts 无 extra_payload，scope 明确限制在第 1-6 章 write-audit-repair 编排，fail-closed 状态覆盖完整，implementation slices 清晰可执行。

5 个 findings 均为 MEDIUM/LOW/INFO 级别，无 BLOCKING 或 HIGH。核心发现是 repair loop 对 patch 类问题和 auditor None 场景的效率问题（各浪费一次 writer LLM 调用），但均不产生安全风险，因为 repair budget 有限且最终正确 fail-closed。建议实现时在 `_decide_repair()` 中增加 auditor LLM_UNAVAILABLE 的 early stop guard（finding #2，修复成本低），其余接受为 MVP residual。
