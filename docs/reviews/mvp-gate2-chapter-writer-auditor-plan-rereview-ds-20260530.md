# Plan Re-Review: MVP Gate 2 chapter_writer + chapter_auditor (post-fixes)

日期：2026-05-30
角色：AgentDS — independent re-reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor plan gate`
分类：`heavy`

## Reviewed Target

`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`（已根据 prior reviews 修复的版本）

## Re-Review Scope

逐一验证以下 10 项 prior-finding 修复和 3 个额外关注点已在更新后的 plan 中足够清晰、可供 implementation agent 安全执行：

1. Writer anchor marker / missing marker 解析契约
2. LLM audit line format 解析契约
3. prompt_only stop_reason 语义
4. Chapter 5 cross-period 程序审计检测
5. evidence_missing critical judgment 判定算法
6. declared_missing_reasons 提取机制
7. repair_hint 聚合规则
8. non_asserted_facets 误用审计
9. E2 显式 deferred
10. bond_risk_evidence 内部锚点错误消息
11. （额外）controller-only control-doc 更新边界
12. （额外）LLM audit 零 issue 通过条件
13. （额外）Slice 结构与 allowed files 一致性

## Source of Truth（不变）

- `AGENTS.md`、`docs/design.md` §5.4/§5.4.1/§5.4.3
- `docs/current-startup-packet.md`、`docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- Gate 1 code fact: `fund_agent/fund/chapter_facts.py`
- Prior reviews: MiMo、GLM、DS-original（均已被 plan §4.1 disposition table 引用）

---

## Prior Finding Verification

### 1. Writer anchor marker / missing marker 解析（MiMo-01 / DS-07）

Plan 新增 **§7.5**，完整定义了解析契约：

- Anchor marker 精确格式 `<!-- anchor:<anchor_id> -->`，正则 `<!-- anchor:([^<>\s]+) -->`
- 大小写敏感、空格敏感、unknown id → blocked `llm_contract_violation`
- Missing marker 精确格式 `<!-- missing:<reason> -->`，正则 `<!-- missing:([a-z_]+) -->`
- `reason` 必须属于 `ChapterFactMissingReason` 闭集 **且** 出现在 `ChapterFactInput.missing_reasons` 中
- 没有 marker 时 `declared_missing_reasons=()`，不从中文自由文本推断
- 标准正文证据行必须有对应 anchor marker，否则 blocked
- `max_output_chars` 为 hard post-check 阈值，超过 blocked 不截断

**判定**: **已修复**。解析规则精确到正则，边缘情况（大小写、空格、unknown id、invalid marker、省略 marker）均有明确 fail-closed 行为。

### 2. LLM audit line format（MiMo-02 / DS-07）

Plan 新增 **§8.4**，完整定义了解析契约：

- `audit_focus` 默认值为 5 项，与 §9 LLM audit 职责完全对应
- 行格式 `SEVERITY|LOCATION|MESSAGE`，SEVERITY 闭集 `BLOCKING/REVIEWABLE/INFO/PASS`
- `PASS|chapter|no issues` 必须单独出现
- 空响应 → blocked；parse failure → blocked（单条 C1 blocking issue，`repair_hint="regenerate"`）
- 零 issue（规范化后等价于 `PASS|chapter|no issues`）→ LLM pass
- INFO-only → LLM pass，不阻断 acceptance
- REVIEWABLE → LLM fail，`repair_hint="patch"`
- BLOCKING → LLM fail，`repair_hint="regenerate"`
- 不从 raw text 识别 fact/anchor ids

**判定**: **已修复**。格式精确定义，所有 severities 的行为明确，parse failure 与空响应均已 fail-closed。

### 3. prompt_only stop_reason（MiMo-03 / GLM-F1）

- `ChapterWriteStopReason` **§7.1** 新增 `"prompt_only"` 为第 10 个 literal value
- **§7.4 第 6 点** 固定为 `status="blocked"`、`stop_reason="prompt_only"`、`draft=None`
- Slice 1 测试 `test_prompt_only_does_not_create_fake_draft_and_uses_prompt_only_stop_reason` 显式断言 stop_reason

**判定**: **已修复**。消除了"由实现选一"的歧义，语义清晰。

### 4. Chapter 5 cross-period 程序审计（GLM-F2）

Plan **§9** 新增完整的 chapter 5 检测策略：

- 触发条件：`chapter_id == 5` 且 `missing_reasons` 含 `cross_period_comparison_missing`
- Assertion phrase 集合：14 个中文短语（`风格稳定`、`言行一致`、`阶段切换` 等）
- Negation / gap prefix 集合：9 个前缀（`不判断`、`无法判断`、`数据不足` 等）
- 检测窗口：assertion phrase 前 12 个中文字符
- 问题式表达（`是否风格稳定`、`下一步验证风格是否稳定`）不阻断
- Fail → rule `C2`，`repair_hint="needs_more_facts"`
- Slice 3 新增两个对应测试

**判定**: **已修复**。phrase 集合来自现有 `report_writing_audit._STABILITY_PHRASES` 并扩展，策略确定性、保守（fail-closed）。

### 5. evidence_missing critical judgment 算法（DS-01）

Plan **§7.4 第 5 点** 定义了 `_fact_supports_critical_judgment()` helper：

- `required_by` 以 `CHAPTER_CONTRACT.` 开头 → 支撑关键判断
- `required_by` 以 `ITEM_RULE.` 开头 → 支撑条件条目关键判断
- `source_field_id` 属于 11 个显式列出的数值/证据强依赖字段 → 支撑数值/关键判断
- `value` 是 `int/float/Decimal` 或容器中直接含数值叶子 → 支撑数值判断
- Helper 只决定 fail-closed，不打开 repository/source
- Slice 1 新增 2 个对应测试

**判定**: **已修复**。算法有 4 条确定规则，`source_field_id` 集合显式列出，`required_by` 去引用 Gate 1 code fact，可实施。

### 6. declared_missing_reasons 提取（DS-02）

见 §7.5 missing marker 解析（与 item 1 共用同一套解析契约）。

- 精确 marker `<!-- missing:<reason> -->`
- `reason` 闭集校验 + 章节内 `missing_reasons` 成员校验
- 没有 marker → `declared_missing_reasons=()`（不从自由文本推断）
- Invalid/unknown reason → blocked

**判定**: **已修复**。提取机制精确确定，与 anchor marker 解析同构设计。

### 7. repair_hint 聚合（DS-03）

Plan **§9 汇总规则** 明确定义：

- 聚合优先级：`needs_more_facts` > `regenerate` > `patch` > `none`
- 无 issue → `none`
- `status="blocked"` 且无具体 hint → 默认 `regenerate`
- 缺 facts / missing semantics 导致 blocked → 默认 `needs_more_facts`
- Slice 4 新增测试 `test_audit_repair_hint_uses_highest_priority`

**判定**: **已修复**。优先级全序，默认值逻辑覆盖所有 blocked 场景。

### 8. non_asserted_facets 误用审计（DS-04）

Plan **§9 C2 non_asserted_facets** 新增确定性检查：

- 候选 facet 字符串出现在正文中，且前后 12 个中文字符内无 7 个限定词之一 → fail
- `facets=()` 且正文出现"属于/是/为/定位为 + 候选 facet" → 一律 blocking
- Writer prompt 要求 LLM 使用"（未断言）"或同义限定语
- Slice 3 新增测试 `test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact`

**判定**: **已修复**。策略确定性，使用与 chapter 5 同构的 12-char 窗口检测，fail-closed。

### 9. E2 显式 deferred（DS-05）

- **§9 末尾**：显式声明 E2 需要重新对照年报原文，超出 Gate 2 writer/auditor 不读 PDF/source 的边界，deferred 到 Evidence Confirm gate
- **§17 residual risks**：显式列出 E2 evidence-vs-assertion source verification 为后续 gate
- **§13 test plan**：明确无 Gate 2 E2 测试
- **§8.1** `ChapterAuditRuleCode` 保留了 `E2` literal 以文档化存在（forward-looking）

**判定**: **已修复**。三处显式声明，不会误认为 E2 已在 Gate 2 实现。

### 10. bond_risk_evidence 内部锚点错误消息（DS-06）

- **§7.5 末尾**：unknown anchor id 疑似来自 `bond_risk_evidence.value.anchors` 内部 ref 时，issue message 必须写明原因
- **§10**：writer/auditor 必须 blocked 并输出专门错误消息
- 疑似判断使用子串匹配 `bond`、`risk`、`credit`、`duration` 或从对应 fact value 收集内部 ref
- Slice 2 新增测试 `test_writer_reports_bond_risk_internal_anchor_message`

**判定**: **已修复**。错误消息精确，疑似判断策略虽非精确但已有启发式指导，且 fail-closed。

---

## 额外关注点验证

### 11. Controller-only control-doc 更新边界（MiMo-04 / GLM-F3）

- **§6** 新增"控制面同步不属于 implementation worker 的 slice"段落
- **§15** 将 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md` 移入 "Controller closeout only" 区域
- **Slice 4**（§12）allowed files 不再包含这三个控制面文件
- **Slice 4** stop condition：如需要更新上述文件，停止交回 controller
- **§15** 不得更新列表中增加这三个文件

**判定**: **已修复**。边界清晰，implementation worker 不会误入控制面文件。

### 12. LLM audit 零 issue 通过条件（GLM-F4）

虽然 plan §4.1 disposition table 未单独列出 GLM-F4，但更新内容已覆盖：

- **§8.4**：`PASS|chapter|no issues` 或零 issue 等价于 LLM pass；空 raw_text 仍 blocked
- **§9 汇总规则**：LLM 零 blocking/reviewable issue 且 programmatic pass → `status="pass"`，`accepted=True`；informational-only 不阻断
- Slice 4 测试 `test_llm_audit_informational_only_passes_with_programmatic_pass` 覆盖此场景

**判定**: **已覆盖**。零 issue pass 与 empty response blocked 的区分明确。

### 13. Slice 结构与 allowed files 一致性

逐 Slice 验证：

| Slice | Allowed Files | 与目标一致 |
|-------|--------------|-----------|
| Slice 1 | `chapter_writer.py` + `test_chapter_writer.py` | ✓ Writer contract + prompt builder |
| Slice 2 | 同上 | ✓ LLM invocation + draft post-check |
| Slice 3 | `chapter_auditor.py` + `test_chapter_auditor.py` | ✓ Programmatic auditor |
| Slice 4 | `chapter_auditor.py` + `test_chapter_auditor.py` + `__init__.py` + `fund/README.md` + `tests/README.md` | ✓ LLM auditor + package/docs sync，**无控制面文件** |

Slice 4 的 stop condition 明确禁止更新 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`。

**判定**: **一致**。无 scope creep，控制面更新完全交回 controller。

---

## Findings

### 01-未修复-INFO-Chapter 5 断言检测中 `风格稳定` 可能误匹配 `风格稳定性`

- **位置**: §9 Chapter 5 cross-period assertion phrase 集合
- **问题类型**: 其它
- **当前写法**: Assertion phrase `风格稳定` 作为子串匹配，可能在 `基金的风格稳定性无法从当前数据判断` 中误命中。该句的否定词 `无法` 在 `风格稳定` 之后（不在 12 char 前置窗口内），会被误判为确定性断言。
- **为什么有问题**: 极低影响 — 系统会 fail-closed（保守阻断），不会产生错误结论。仅导致一条本应通过的草稿被 blocked。
- **直接证据**: `风格稳定` ∈ assertion phrase 集合；`风格稳定性` 是不同语义（名词短语 vs 断言）；`无法` 出现在 assertion 之后不触发 negation window。
- **影响**: 极低 — fail-closed，最多误阻断一条合法草稿
- **建议改法和验证点**: 无需修改 plan。在 implementation 时可微调 phrase 为词边界匹配（如 `风格稳定[^性]`）或追加 `稳定性` 相关排除规则。若 test fixture 触发此边缘情况，implementation evidence 应记录。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: INFO

### 02-未修复-INFO-`_fact_supports_critical_judgment` "数值叶子" 规则可能过于宽泛

- **位置**: §7.4 第 5 点，"fact.value 是 int/float/Decimal，或 dict/list/tuple 中直接包含数值叶子，也视为支撑数值判断"
- **问题类型**: 其它
- **当前写法**: 任何 dict value 中含数值叶子即标记为支撑数值判断。`basic_identity.value = {"成立日期": "2020-01-01", "基金规模": 50.5}` 中含 `50.5`，会被标记。
- **为什么有问题**: 极低影响 — 系统 fail-closed（保守阻断），不会漏过真正的数值/关键判断。仅可能过度阻断非关键 facts。
- **直接证据**: §7.4 第 5 点第 4 条规则。
- **影响**: 极低 — fail-closed，实现时可通过 field-level 白名单或排除 `basic_identity`/`product_profile` 等非数值密集型字段进一步窄化
- **建议改法和验证点**: 无需修改 plan。implementation 可在 `_fact_supports_critical_judgment` 内增加 source_field_id 白名单，排除 `structured.basic_identity`、`structured.product_profile`、`structured.benchmark` 等描述性字段。implementation evidence 应记录最终选择的 source_field_id 范围。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: INFO

---

## Open Questions

无。所有 prior review lens 的问题已通过 plan 修复或确认为 deferred。

## Residual Risks

| 风险 | 来源 | 说明 | 跟踪位置 |
|------|------|------|---------|
| `风格稳定` 误匹配 `风格稳定性` | DS re-review 01 | 保守阻断，不影响正确性 | Gate 2 implementation evidence — 若有 fixture 触发则记录微调 |
| "数值叶子" 过宽 | DS re-review 02 | 保守阻断，不影响正确性 | Gate 2 implementation evidence — 记录最终 source_field_id 白名单 |
| value serialization 策略 | MiMo-05 | `value: object \| None` 序列化未定义 | Gate 2 implementation evidence — 记录序列化策略 |
| LLM 输出可复现性 | MiMo-01/02, DS-02 | 依赖 LLM 遵循 marker/line format | Fake client 确定性 fixture |
| bond_risk_evidence 锚点展开 | Gate 1 residual | 组级 anchors 未展开 | Gate 3 或独立 evidence gate |
| 第 0/7 章 blocked | 设计约束 | 无 accepted chapters | Gate 3 orchestrator |
| cross_period_comparison | 设计约束 | 单期 bundle | Gate 3 或独立 data gate |
| E2 source verification | DS-05 | 显式 deferred | Evidence Confirm gate |

---

## Plan Review Conclusion

**PASS**

所有 prior findings（MiMo ×5、GLM ×5、DS-original ×7）已在更新后的 plan 中处理。其中：

- 10 项 **已修复**（通过新增 §4.1/§7.5/§8.4、修订 §7.1/§7.4/§9/§10/§12/§15 等）
- 2 项 INFO 仅需 implementation 阶段微调（phrase 边界匹配、source_field_id 白名单窄化），不影响 plan 的 code-generation-readiness
- 1 项（value serialization）被接受为 residual

更新后的 plan 在以下方面达到 code-generation-ready 标准：

- **Writer 解析契约**：anchor marker + missing marker 双格式均已精确到正则，所有边缘情况 fail-closed
- **LLM audit 解析契约**：`SEVERITY|LOCATION|MESSAGE` 行格式、parse failure blocked、零 issue pass vs 空响应 blocked 均已明确
- **类型系统**：`prompt_only` 补入 literal 闭集，E2 保留在 rule code 以备 forward reference
- **程序审计**：chapter 5 cross-period phrase 检测、non_asserted_facets 误用检测均有确定性策略
- **聚合逻辑**：repair_hint 优先级全序，覆盖 blocked 默认值
- **边界控制**：控制面文件更新完全限定为 controller closeout，implementation slices 不含控制面文件
- **测试覆盖**：35+ named tests 覆盖所有 happy/blocked/semantic/parse/import 路径

无 BLOCKING 发现。2 个 INFO finding 为保守性 edge case，不影响正确性且可在实现中微调。

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth 和 prior findings 已逐项验证
- [x] findings 是 evidence-based、adversarial、可执行，且没有 style/nit/speculation
- [x] open questions、residual risks、tracking destination 与 findings 分开
- [x] conclusion 为 PASS
- [x] output path 为 `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-rereview-ds-20260530.md`
- [x] 未修改 plan 文件，未 stage/commit/push/PR
