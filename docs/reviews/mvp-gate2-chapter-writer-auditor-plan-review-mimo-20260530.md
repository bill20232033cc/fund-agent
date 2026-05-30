# Plan Review: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：AgentMiMo — independent plan reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor plan gate`
分类：`heavy`

## Reviewed Target

`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`

## Scope

Review the Gate 2 plan for code-generation readiness, architecture boundary compliance, ChapterFactProjection consumption correctness, LLM contract fail-closed semantics, CHAPTER_CONTRACT/ITEM_RULE handling, programmatic vs LLM audit separation, test coverage, and any required business decisions before implementation.

## Source of Truth

- `AGENTS.md` — Agent 执行规则唯一权威
- `docs/design.md` v2.3 — 设计真源，§5.4 / §5.4.1 / §5.4.3
- `docs/current-startup-packet.md` — 当前控制面
- `docs/fund-analysis-template-draft.md` — CHAPTER_CONTRACT / ITEM_RULE / preferred_lens
- Gate 1 controller judgment: `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md`
- Gate 1 code fact: `fund_agent/fund/chapter_facts.py` — `ChapterFactProjection` / `ChapterFactInput`
- `fund_agent/fund/audit/audit_programmatic.py` — 现有程序审计
- `fund_agent/fund/report_writing_audit.py` — dev-only 写作审计

## Assumptions Tested

1. Plan scope is strictly Gate 2 (writer + auditor primitives only, no orchestrator/repair/CLI/dayu).
2. Writer/auditor correctly belong to Agent-layer `fund_agent/fund`.
3. Plan consumes `ChapterFactProjection` / `ChapterFactInput` without repository/PDF/source access.
4. LLM client injection via Protocol is explicit, typed, and fail-closed.
5. CHAPTER_CONTRACT must_answer/must_not_cover, preferred_lens, ITEM_RULE, evidence anchors, non_asserted_facets, and fund_type unknown are handled.
6. Programmatic vs LLM audit responsibilities and stop conditions are clear.
7. Slices are fine-grained enough for safe implementation.
8. Tests are sufficient and not overbroad.

---

## Findings

### 01-未修复-MEDIUM-LLM 响应解析契约缺失
- **位置**: §7.4 Writer data flow 第 6 点, §7.6 stop conditions
- **问题类型**: 契约缺失
- **当前写法**: "LLM 返回空文本、超长文本、无法解析 anchor refs 或包含 forbidden phrases 时，返回 blocked"。Slice 2 说"最小实现可要求 fake/real client 在正文中保留 `anchor_id` HTML comment，例如 `<!-- anchor:... -->`"
- **反例/失败场景**: 实现 agent 需要自行决定：(a) HTML comment 的精确格式（是否带冒号、空格、大小写）；(b) 超长的阈值定义（`max_output_chars` 是 prompt 约束还是 post-check 截断）；(c) "无法解析"的判断标准。这些决定直接影响 writer 和 auditor 的一致性。
- **为什么有问题**: Gate 2 的核心价值是提供 typed building blocks。如果 anchor ref 解析格式和超长处理在 writer 内部未冻结，Gate 3 orchestrator 无法可靠消费 `ChapterDraft.used_anchor_ids`。
- **直接证据**: Slice 2 `_draft_from_llm_response()` 描述为"解析正文中显式 anchor ids 或证据锚点行"，但未给出解析规则。
- **影响**: 实现 agent 自行定义格式 → Gate 3 消费时需要重新适配 → 返工
- **建议改法和验证点**: 在 §7.4 或 §7.6 中增加一个小节，定义 (a) `<!-- anchor:<anchor_id> -->` 的精确正则；(b) `max_output_chars` 作为 hard post-check 阈值（超过即 blocked，不截断）；(c) 测试中验证解析器对边界格式的处理。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-MEDIUM-LLM audit 输出解析规则未指定
- **位置**: §8.2 Auditor LLM Protocol, §9 LLM audit 职责
- **问题类型**: 契约缺失
- **当前写法**: "Gate 2 不要求解析复杂 JSON 修复计划；最小实现可要求 LLM 返回 line-oriented issue text，并只作为 `reviewable` semantic signal"。"若无法稳定解析 LLM 输出，不得 pass"
- **反例/失败场景**: "line-oriented issue text" 不是正式格式。实现 agent 需要决定：(a) 每行的格式（是否包含 severity、location、fact_id）；(b) 如何把自由文本映射到 `ChapterAuditIssue.rule_code` 和 `severity`；(c) 如果 LLM 返回中文而不是预期的结构化文本怎么办。模糊定义会导致 auditor 对同一个 LLM 输出在不同实现中给出不同结果。
- **为什么有问题**: Gate 2 的 LLM audit 是 semantic signal，但如果解析逻辑不稳定，同一份 draft 的审计结果不可复现，Gate 3 无法依赖 `repair_hint` 做决策。
- **直接证据**: §8.2 说"只作为 `reviewable` semantic signal"，但未给出 `ChapterAuditLLMRequest.audit_focus` 的具体内容或 `ChapterAuditLLMResponse.raw_text` 的解析契约。
- **影响**: 实现 agent 自行定义解析 → Gate 3 repair policy 不可预测 → 返工
- **建议改法和验证点**: 在 §8.2 或 §9 中明确：(a) `audit_focus` 默认值（至少包含 `["evidence_support", "must_not_cover_boundary", "missing_semantics", "readability"]`）；(b) LLM 输出的最小格式要求（如每行 `SEVERITY|LOCATION|MESSAGE`，不可解析时降级为单条 `reviewable` issue）；(c) 解析失败时返回 `C1` blocked issue 而非 silent pass。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-LOW-mode="prompt_only" 的 stop_reason 歧义
- **位置**: §7.4 Writer data flow 第 5 点
- **问题类型**: 契约缺失
- **当前写法**: "`mode="prompt_only"` 只返回 prompt 和 blocked result，`draft=None`，stop_reason=`llm_unavailable` 或 `none` 由实现选一但必须 `status="blocked"`"
- **反例/失败场景**: 如果实现选择 `stop_reason="none"`，下游消费者会误以为没有问题；如果选择 `stop_reason="llm_unavailable"`，语义上暗示 LLM 缺失是原因，但实际上 `prompt_only` 是设计如此。这两种选择都不是正确语义。
- **为什么有问题**: `stop_reason` 的闭集定义（§7.1）中没有 `prompt_only` 选项，而现有选项都不能精确描述"这是 prompt-only 模式，不需要 LLM"的语义。
- **直接证据**: §7.1 定义了 9 种 `ChapterWriteStopReason`，没有 `prompt_only` 或 `no_llm_requested`。
- **影响**: 低。测试可以断言 `status="blocked"` 而非 `stop_reason`，但语义不精确会导致文档描述混淆。
- **建议改法和验证点**: 在 `ChapterWriteStopReason` 闭集中增加 `"prompt_only"` 作为第 10 个值，明确它只用于 `mode="prompt_only"` 路径。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 04-未修复-LOW-slice 4 把 LLM auditor 实现与 docs 合并
- **位置**: §12 Slice 4
- **问题类型**: 范围漂移
- **当前写法**: Slice 4 同时包含 `audit_chapter_llm()` 实现、fake LLM pass/fail tests、README 更新和 docs/design.md 状态同步。
- **反例/失败场景**: 如果 LLM audit 实现需要额外调试，docs 同步可能被推迟或遗忘；如果 docs 同步触发 controller 问题，LLM audit 代码会被连带阻塞。
- **为什么有问题**: Gate 1 的教训是 docs 同步应由 controller closeout 统一处理，而非 implementation worker 自行扩大。当前 plan §15 说"仅由 controller 接受 implementation 后做最小状态同步"，但 Slice 4 的 allowed files 已经包含了 docs 文件。
- **直接证据**: Slice 4 allowed files 包含 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`，但 §15 说这些文件"仅由 controller closeout 做最小状态同步"。
- **影响**: 低。Slice 4 的 docs 更新范围很窄（只写当前 Fund 层能力），且有 stop condition 保护。
- **建议改法和验证点**: 在 Slice 4 的 stop condition 中增加"如果 docs 更新需要声明 Gate 2 complete 并改变 next entry point，停止交回 controller"。或者将 docs 同步从 Slice 4 移出，作为独立 controller step。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 05-未修复-INFO-plan 对 `value: object | None` 的保守序列化策略未展开
- **位置**: §17 Residual risks 第 1 点
- **问题类型**: 其它
- **当前写法**: "`ChapterFactEntry.value` 仍是 `object | None`，writer/auditor 最小实现需以 conservative serialization 呈现 facts"
- **反例/失败场景**: LLM prompt 需要把 `value` 序列化为文本。如果 value 是 dict、list、`NavDataResult`、`ExtractedField` 等复杂类型，序列化策略直接影响 LLM 理解质量。但 plan 没有指定序列化规则。
- **为什么有问题**: 这不是 blocker，因为 Gate 2 只需要"能跑通"，不需要最优 prompt 质量。但实现 agent 可能花过多时间在 prompt engineering 上。
- **直接证据**: §17 residual risks 承认了这个问题但没有给出指导。
- **影响**: 低。这是 prompt 质量问题，不是正确性问题。
- **建议改法和验证点**: 无需修改 plan。在实现时，建议 writer 使用 `json.dumps(value, ensure_ascii=False, default=str)` 作为最小序列化策略，并在 tests 中覆盖 dict/list/None/complex value 场景。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: INFO

---

## Open Questions

无。所有 review lens 的问题已通过 findings 覆盖。

## Residual Risks

| 风险 | 说明 | 建议跟踪位置 |
|------|------|-------------|
| LLM prompt 质量 | `value: object | None` 序列化策略未定义，可能导致 LLM 对复杂 facts 理解不足 | Gate 2 implementation evidence 或 Gate 3 orchestrator prompt tuning |
| LLM audit 可复现性 | line-oriented issue text 解析不稳定可能导致同一 draft 在不同 run 中审计结果不同 | Gate 2 implementation evidence，需要记录 fake client 的确定性行为 |
| bond_risk_evidence 锚点 | Gate 1 已识别此问题：组级 anchors 保留在 `value.anchors`，Gate 2 不展开 | Gate 3 或后续 evidence gate |
| 第 0/7 章默认 blocked | 本 gate 不实现 accepted chapters，第 0/7 章永远 blocked | Gate 3 orchestrator，需要先完成 1-6 章 accepted |
| cross_period_comparison | 第 5 章需要跨期数据，当前只有单期 bundle | Gate 3 或独立 data gate |

## Plan Review Conclusion

**PASS_WITH_NON_BLOCKING**

Plan 是 code-generation-ready 的。4 个 LOW/MEDIUM findings 都不阻塞 implementation agent 开始工作，但建议在实现前或实现中修复：

- **MEDIUM x2**: LLM response parsing contracts（writer anchor refs 和 auditor issue text）需要在 plan 或实现中冻结格式，否则 Gate 3 消费端不可靠。
- **LOW x2**: `prompt_only` stop_reason 语义和 Slice 4 docs 范围的轻微不一致。

Plan 的核心架构决策正确：writer/auditor 在 Fund 层、消费 ChapterFactProjection、LLM Protocol 注入、fail-closed、programmatic/LLM 审计分离。Slices 合理，tests 覆盖 happy/blocked/import boundary 场景。Non-goals 清晰。

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] findings 是 evidence-based、adversarial、可执行，且没有 style/nit/speculation
- [x] open questions、residual risks、tracking destination 与 findings 分开
- [x] conclusion 只能是 pass / pass-with-risks / fail
- [x] output path 使用本机系统时钟生成的 timestamp，且匹配 artifact path 格式
