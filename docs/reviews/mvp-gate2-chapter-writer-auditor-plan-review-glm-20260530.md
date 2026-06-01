# Plan Review: MVP Gate 2 chapter_writer + chapter_auditor plan

日期：2026-05-30
角色：AgentGLM，独立 plan reviewer
Verdict：**PASS_WITH_NON_BLOCKING**

---

## Reviewed Target

- **Plan artifact**: `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`
- **Scope**: MVP Gate 2 `chapter_writer` + `chapter_auditor`，Fund 层单章 LLM 写作/审计 primitives
- **Classification**: `heavy`

## Assumptions Tested

| # | Assumption | Evidence source | Result |
|---|-----------|----------------|--------|
| A1 | Gate 1 `ChapterFactProjection` / `ChapterFactInput` 是完整 typed 输入，writer/auditor 不需要额外 repository/PDF/source 访问 | `chapter_facts.py` 全文 1495 行，Gate 1 controller judgment + implementation evidence | **Confirmed**: ChapterFactInput 含 contract、fund_type、facet/lens/item_rule、facts、anchors、missing_reasons、source_field_ids |
| A2 | Writer/auditor 属于 Fund 层，不跨层 | `AGENTS.md` 归属判定规则：CHAPTER_CONTRACT/preferred_lens/审计规则执行 → Agent 层 fund_agent/fund | **Confirmed**: Plan 明确 writer/auditor 理解 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点，属于 Fund 层 |
| A3 | LLM client 通过 typed Protocol 注入，Fund 模块不直接依赖 OpenAI/HTTP SDK | `AGENTS.md` 禁止 extra_payload；`design.md` §5.4.1 Gate 2 边界约束 | **Confirmed**: Plan 定义 `ChapterLLMClient` / `ChapterAuditLLMClient` Protocol，无 env/config/retry/streaming |
| A4 | 缺少 LLM client 时 fail-closed，不产生 fake pass | `AGENTS.md` 第一性原理；`design.md` §5.2 审计规则边界 | **Confirmed**: Plan §7.4/§9/§11 多处显式 fail-closed |
| A5 | ITEM_RULE delete/skip 必须严格执行，不得输出空表/占位/暗示 | `fund-analysis-template-draft.md` HTML 注释；`item_rules.py` `TemplateItemRuleDecisionStatus` = render \| delete | **Confirmed**: Plan §7.4/§9/§11 反复强调 |
| A6 | `non_asserted_facets` 不得驱动写作结论或 ITEM_RULE | Gate 1 controller judgment: "Compatible labels are carried only as non_asserted_facets and must not drive ITEM_RULE" | **Confirmed**: Plan §7.4 point 3 |
| A7 | `fund_type="unknown"` 不得应用类型 lens 或输出类型化判断 | `chapter_facts.py` L766-774: unknown 时跳过 lens resolve | **Confirmed**: Plan §7.4 point 4 blocked |
| A8 | `ChapterFactEntry.value: object | None` 可被 conservative serialization 消费 | Gate 1 implementation evidence residual: value remains broad | **Accepted as residual**: Plan §17 承认；writer 序列化为 prompt 文本属于实现层 |
| A9 | Programmatic audit 与 LLM audit 职责边界清晰 | `design.md` §5.4: "规则审计负责结构、锚点、CHAPTER_CONTRACT/ITEM_RULE、数值闭合与边界条件；LLM 审计负责证据是否支撑断言、语义越界、投资建议措辞和读者可理解性" | **Confirmed**: Plan §9 与 design.md §5.4 一致 |
| A10 | 不实现 orchestrator / repair loop / final assembler / CLI `--use-llm` / Host/Agent/dayu | `current-startup-packet.md` §4 Route C gate sequence | **Confirmed**: Plan §5 non-goals 与 §17 next gates 一致 |

## Findings

### F1-未修复-MEDIUM-prompt_only mode stop_reason 语义模糊

- **位置**: §7.4 point 5，§7.1 `ChapterWriteStopReason`
- **问题类型**: 契约缺失
- **当前写法**: "mode=prompt_only 只返回 prompt 和 blocked result，draft=None，stop_reason=llm_unavailable 或 none 由实现选一但必须 status=blocked"
- **反例/失败场景**: 实现 agent 选择 stop_reason="none"，但 "none" 在 `ChapterWriteStopReason` 中语义为"无停止原因"——与 status="blocked" 矛盾。测试断言 stop_reason 时需要猜测实现选择，导致测试不确定。反之，选择 "llm_unavailable" 则 prompt_only 模式会被误判为"LLM 不可用"而非"主动跳过 LLM 调用"。
- **为什么有问题**: `ChapterWriteStopReason="none"` 在 status="drafted" 时表示成功完成，在 status="blocked" 时语义不清。两种选择分别有不同误导风险，实现 agent 需要自行裁决一个本应由 plan 明确的语义。
- **直接证据**: Plan §7.1 定义 `ChapterWriteStopReason = Literal["none", ..., "llm_unavailable", ...]`；§7.4 point 5 说"由实现选一"。
- **影响**: 实现 agent 可能在 prompt_only 测试中断言错误 stop_reason，或未来 Gate 3 orchestrator 消费 stop_reason 时产生语义歧义。
- **建议改法和验证点**: 指定 prompt_only 模式的规范语义：(a) preflight 全部通过时 stop_reason="none"，表示"prompt 构建成功，主动不调用 LLM"；或 (b) 统一使用 "llm_unavailable"。推荐 (a)，因为 prompt_only 的目的是测试 prompt 构建，不是模拟 LLM 故障。验证点：Slice 1 测试 `test_prompt_only_does_not_create_fake_draft` 应断言明确 stop_reason。
- **修复风险**: 低
- **严重程度**: MEDIUM

### F2-未修复-MEDIUM-Chapter 5 跨期比较程序审计检测机制欠规格

- **位置**: §11 stop conditions "第 5 章包含 cross_period_comparison_missing，且草稿试图判断跨期风格/阶段变化为确定事实"；§9 programmatic audit `_audit_missing_semantics()`
- **问题类型**: 不可直接实施
- **当前写法**: §11 将"草稿试图判断跨期风格/阶段变化为确定事实"列为 fail-closed stop condition，但 §9 programmatic audit helpers 列表中 `_audit_missing_semantics()` 是唯一可能与该 stop condition 对应的 helper，未指定具体检测策略。
- **反例/失败场景**: 实现 agent 在 `_audit_missing_semantics()` 中采用三种可能策略之一：(a) 对 chapter 5 检测到 cross_period_comparison_missing 时直接 block 所有 chapter 5 草稿——过于保守，阻止了仅描述当前期数据但不做跨期判断的合法草稿；(b) 尝试基于稳定性/变化措辞的模式匹配——合理但 plan 未指定检测词表；(c) 委托给 LLM audit——与 plan 将此列为 programmatic stop condition 矛盾。
- **为什么有问题**: "草稿试图判断跨期风格/阶段变化为确定事实"是语义判断，不能纯靠结构检查完成。Plan 将其放在 programmatic audit 但未给出足够实现指导。现有 `report_writing_audit.py` 有 `_STABILITY_PHRASES`（"风格稳定"、"风格一致"、"言行一致"等）和 `_NEGATED_STABILITY_PREFIXES`（"不判断"、"无法判断"等），可作为参考，但 plan 只在 §4 提到"可复用其已验证的禁用措辞思想"，未明确引用。
- **直接证据**: Plan §4 "现有 report_writing_audit.py … Gate 2 可以复用其已验证的禁用措辞思想"；Plan §11 stop condition "第 5 章包含 cross_period_comparison_missing"；`report_writing_audit.py` `_STABILITY_PHRASES` = ("风格稳定", "风格保持稳定", "风格一致", "风格延续", "言行一致", "投资框架稳定")。
- **影响**: 实现 agent 可能选择过于保守或过于宽松的检测策略，影响 chapter 5 草稿的通过率或质量。
- **建议改法和验证点**: 在 Slice 3 `_audit_missing_semantics()` 实现说明中增加：当 chapter_id=5 且 `missing_reasons` 含 `cross_period_comparison_missing` 时，检测草稿是否包含稳定性/变化判断措辞（可引用 `report_writing_audit._STABILITY_PHRASES` 模式或重新定义 chapter-5 专用词表），且未以否定前缀修饰。增加测试用例 `test_programmatic_audit_blocks_chapter5_cross_period_assertion_when_missing`。
- **修复风险**: 低
- **严重程度**: MEDIUM

### F3-未修复-LOW-Slice 4 allowed files 与 controller-only docs 更新约束存在表面矛盾

- **位置**: §12 Slice 4 allowed files；§15 docs update plan
- **问题类型**: 范围漂移
- **当前写法**: Slice 4 allowed files 包含 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`，但附带"仅做 controller-approved 最小状态同步"限制。§15 说这些文件"仅由 controller closeout 或明确 implementation scope 最小同步 next entry"。
- **反例/失败场景**: 实现 agent 误读 Slice 4 allowed files 为授权在 Slice 4 实现期间修改这些控制面文件，实际上这些文件只有 controller gate closeout 才应修改。
- **为什么有问题**: allowed files 列表与 controller-only 约束并存在同一个 slice 中，可能导致实现 agent 行为不一致。
- **直接证据**: Plan §12 Slice 4: "docs/design.md、docs/current-startup-packet.md、docs/implementation-control.md，仅做 controller-approved 最小状态同步"；Plan §15: "仅在 controller 接受 implementation 后"。
- **影响**: 低——即使实现 agent 修改了这些文件，controller closeout 会覆盖；但若实现 agent 因此扩大控制面写入，review 需要额外检查。
- **建议改法和验证点**: 从 Slice 4 allowed files 中移除这三个控制面文件，或将其移到单独的 "Slice 5: controller closeout docs sync" 条目中。验证点：implementation evidence 应只记录 `fund_agent/fund/chapter_writer.py`、`fund_agent/fund/chapter_auditor.py`、`tests/`、`fund_agent/fund/README.md`、`tests/README.md` 的变更；控制面文件由 controller judgment artifact 处理。
- **修复风险**: 低
- **严重程度**: LOW

### F4-未修复-LOW-LLM 审计零 issue 通过条件未显式声明

- **位置**: §9 汇总规则
- **问题类型**: 契约缺失
- **当前写法**: 汇总规则定义了 programmatic fail、LLM unavailable、LLM 返回 informational/reviewable issues 和 programmatic pass + LLM pass 四种情况，但未显式声明 "LLM 返回零 issue" 的语义等价于 "LLM pass"。
- **反例/失败场景**: 实现 agent 可能将 LLM 返回零 issue 理解为"LLM 未运行"而非"LLM 通过"，错误返回 blocked 而非 pass。
- **为什么有问题**: 虽然 "programmatic pass 且 LLM pass 才能 accepted=True" 暗示了 LLM pass 的存在，但 LLM pass 的充分必要条件（零 blocking issue？零所有 issue？显式 pass 标记？）未明确。
- **直接证据**: Plan §9 "programmatic pass 且 LLM pass 才能 accepted=True"；§8.3 `ChapterLLMAuditResult.status: ChapterAuditStatus = Literal["pass", "fail", "blocked"]`。
- **影响**: 低——实现 agent 有 `ChapterAuditStatus` 三态类型约束，大概率能正确推断；但若错误推断则导致合法章节被 blocked。
- **建议改法和验证点**: 在 §9 汇总规则中增加一行："LLM 返回零 issue 或仅返回 informational issue 且 programmatic 通过时，`ChapterAuditResult.status="pass"`，`accepted=True`"。验证点：Slice 4 测试 `test_llm_audit_fake_pass_combines_with_programmatic_pass`。
- **修复风险**: 低
- **严重程度**: LOW

### F5-未修复-INFO-C2 规则码语义差异不构成冲突

- **位置**: §8.1 `ChapterAuditRuleCode`；`fund_agent/fund/audit/audit_programmatic.py` `AuditRuleCode`
- **问题类型**: 其它
- **当前写法**: 现有 `audit_programmatic.py` 的 `AuditRuleCode` 使用 C2 表示"内容违规（模板格式不符）"；plan 的 `ChapterAuditRuleCode` 使用 C2 表示 CHAPTER_CONTRACT must_answer/must_not_cover 合规检查和 ITEM_RULE delete 段落检查。
- **反例/失败场景**: Reviewer 或后续维护者混淆两套 C2 语义。
- **为什么有问题**: 两套规则码在不同模块、不同类型别名中，语义不同但名称相同。不构成运行时冲突。
- **直接证据**: `audit_programmatic.py` `AuditRuleCode = Literal["P1", "P2", "P3", "C2", "L1", "R1", "R2"]`；Plan §8.1 `ChapterAuditRuleCode = Literal[..., "C2", ...]`。
- **影响**: 无功能影响；文档或沟通时可能产生混淆。
- **建议改法和验证点**: 无需修改。两套规则码服务于不同审计层级（报告级 vs 章节级），使用独立类型别名。后续若需要统一，可在 Gate 3 或 Gate 4 做规则码对齐。
- **修复风险**: 无
- **严重程度**: INFO

## Architecture Boundary Review

Plan 的分层设计正确：

| 检查项 | 结果 |
|--------|------|
| Writer/auditor 在 Fund 层（Agent 层） | ✓ §6 明确归属，与 `AGENTS.md` 归属判定一致 |
| LLM client 通过 Protocol 注入 | ✓ §7.2/§8.2 独立 Protocol，不读取 env/config |
| 无 Service 编排 | ✓ §5 non-goals，§6 "Service-owned strategy/policy 放到 Gate 3" |
| 无 Host/Agent/dayu | ✓ §5 non-goals，无 package/dependency/runner/session 引入 |
| 无 repository/PDF/source 访问 | ✓ §5/§7.4/§11 多处显式禁止，AST import 隔离测试 |
| 无 CLI `--use-llm` | ✓ §5 non-goals |
| 无 orchestrator / repair loop | ✓ §5 non-goals，repair_hint 只作为输出不执行 |
| 参数显式 typed | ✓ 全部 dataclass 字段显式声明，无 extra_payload |

依赖方向正确：auditor → writer → chapter_facts → template APIs + extractor models。无循环依赖。

## Best Practice Review

| 检查项 | 结果 |
|--------|------|
| Fail-closed 语义 | ✓ §11 十条 stop conditions，全部阻止 accepted draft 生成 |
| Programmatic vs LLM 分离 | ✓ §9 职责清晰，programmatic fail 覆盖 LLM pass |
| 测试覆盖 | ✓ 20+ named tests，覆盖 happy/blocked/semantic/import boundary |
| Prompt_only 不伪装成功 | ✓ status=blocked，draft=None |
| Schema versioning | ✓ 每个 dataclass 都有 schema_version Literal |
| Frozen + slots dataclasses | ✓ 所有 public dataclass |
| Import 隔离 | ✓ AST 测试 + 多次显式禁止 |

## Optimal Solution Review

Plan 选择的方案在 credible alternatives 中是最小安全路径：

- Protocol 注入优于直接 SDK 依赖：测试友好，不引入 provider lock-in
- 单章 primitive 优于多章编排：Gate 3 处理编排，Gate 2 只提供 building blocks
- 分离 programmatic/LLM audit 优于混合：确定性检查可独立测试和验证
- `prompt_only` 模式用于确定性测试：合理的测试策略

## Overengineering Review

Plan 没有过度设计：

- 没有 builder pattern、工厂模式或抽象层
- 没有引入 event system、state machine 或 observer pattern（Gate 3 才需要）
- 没有定义修复执行器或 repair loop（只输出 repair_hint）
- 没有引入 streaming、retry、cancellation（Host 层职责）
- Dataclass 层级深度合理：writer 5 层，auditor 5 层，与输入复杂度匹配

## Overcoupling Review

Plan 的耦合度合理：

- Writer 和 auditor 独立：auditor 只依赖 writer 的 input/draft 类型，不依赖 writer 实现
- 两个独立 LLM Protocol：写作和审计有不同的 request/response schema，不共享
- 无双向依赖：auditor → writer → chapter_facts 单向
- 无共享可变状态：所有 dataclass frozen
- 测试不依赖大集成链路：每个 slice 有独立 targeted tests

## Open Questions

无。Plan §18 "Blocking Questions For Controller" 正确声明为"无"。

## Residual Risks

| Risk | Tracking destination |
|------|---------------------|
| `ChapterFactEntry.value: object \| None` 的 conservative serialization 可能导致 prompt 质量不稳定 | Gate 2 implementation evidence 应记录序列化策略和已知局限；后续 quality/evidence gate 可窄化 |
| LLM audit 只检查语义支撑，不能证明事实完全正确 | 后续 Evidence Confirm / anchor-to-source verification gate |
| 第 0 章和第 7 章需要 accepted chapters，本 gate 默认 fail closed | Gate 3 orchestrator + Gate 4 final assembler |
| RepairDecision 只作为 hint | Gate 3 chapter_orchestrator |
| 无 provider-specific LLM client | Gate 3 或独立 Service gate |

## Conclusion

**PASS_WITH_NON_BLOCKING**

Plan 是 code-generation-ready 的。两个 MEDIUM findings（F1: prompt_only stop_reason 语义模糊，F2: chapter 5 跨期比较程序审计检测机制欠规格）不阻止实现启动，但建议在实现前由 controller 或 plan owner 做最小澄清，以减少实现 agent 的歧义裁决风险。三个 LOW/INFO findings 不需要 plan 修改。

Plan 在以下方面表现良好：
- Scope 严格限制在 Gate 2 single-chapter primitives
- Fail-closed 语义贯穿 writer preflight、LLM post-check 和 auditor 汇总规则
- LLM client Protocol 注入干净，测试策略合理
- Import 隔离有 AST 测试保障
- Non-goals 和 next gates 与 startup packet / design.md 一致
