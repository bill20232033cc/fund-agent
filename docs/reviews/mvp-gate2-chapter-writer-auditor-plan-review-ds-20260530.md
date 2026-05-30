# Plan Review: MVP Gate 2 chapter_writer + chapter_auditor

日期：2026-05-30
角色：AgentDS — independent plan reviewer (replacement for GLM, which did not produce artifact within controller timeout)
Gate：`MVP Gate 2: chapter_writer + chapter_auditor plan gate`
分类：`heavy`

## Reviewed Target

`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-20260530.md`

## Scope

Review the Gate 2 plan for code-generation readiness, architecture boundary compliance, correct ChapterFactProjection consumption, LLM contract fail-closed semantics, CHAPTER_CONTRACT/ITEM_RULE handling completeness, programmatic vs LLM audit separation clarity, test coverage sufficiency, and any required business decisions before implementation.

Also aware of MiMo independent review (`docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-mimo-20260530.md`) — findings here are additive, not duplicative.

## Source of Truth

- `AGENTS.md` — Agent 执行规则唯一权威，四层边界 UI->Service->Host->Agent
- `docs/design.md` v2.3 §5.4 / §5.4.1 / §5.4.3 — Route C accepted future route, fact/evidence input contract
- `docs/current-startup-packet.md` — 当前控制面，Gate 2 = next entry point
- `docs/implementation-control.md` — 实施总控
- `docs/fund-analysis-template-draft.md` — 8章模板，CHAPTER_CONTRACT / ITEM_RULE / preferred_lens / 审计规则码
- Gate 1 controller judgment: `docs/reviews/mvp-gate1-chapter-fact-provider-controller-judgment-20260530.md`
- Gate 1 code fact: `fund_agent/fund/chapter_facts.py` — `ChapterFactProjection` / `ChapterFactInput` / `ChapterFactEntry` / `ChapterEvidenceAnchor` / `ChapterFacetResolution` / `ChapterLensResolution` / `ChapterItemRuleProjection`
- `fund_agent/fund/template/contracts.py` — `ChapterContract` with `must_answer`, `must_not_cover`, `required_output_items`

## Assumptions Tested

1. Plan scope is strictly Gate 2: writer + auditor primitives only, no orchestrator/repair/CLI/dayu.
2. Writer/auditor correctly belong to Agent-layer `fund_agent/fund`, consuming only `ChapterFactProjection` / `ChapterFactInput`.
3. LLM client injection via typed Protocol is explicit, fail-closed, and not fake-pass.
4. CHAPTER_CONTRACT must_answer/must_not_cover, preferred_lens, ITEM_RULE delete/render, evidence anchors, missing semantics, fund_type unknown, and non_asserted_facets are handled.
5. Programmatic vs LLM audit responsibilities and stop conditions are unambiguous.
6. Slices are fine-grained enough; tests cover happy path, blocked path, and import boundary.
7. No user business decision or design_doc change is required before implementation.

---

## Findings

### 01-未修复-HIGH-Writer deterministic preflight "支撑数值/关键判断" 判定标准缺失

- **位置**: §7.4 Writer data flow 第 4 点，"available fact 含 `evidence_missing` 且该 fact 会支撑数值/关键判断 -> blocked"
- **问题类型**: 契约缺失
- **当前写法**: "available fact 含 `evidence_missing` 且该 fact 会支撑数值/关键判断 -> blocked"，但没有给出"支撑数值/关键判断"的判定算法。
- **反例/失败场景**: 实现 agent 拿到一个 `ChapterFactEntry(status="available", evidence_anchor_ids=(), missing_reason="evidence_missing")`，其 `value` 是一个 dict 包含数值字段。这个 fact 是否"支撑数值/关键判断"？判定标准不同会导致：(a) 过于宽松：只有显式标记为 must_answer 直接依赖的 fact 才算 → 遗漏间接支撑；(b) 过于严格：任何 value 含数值的 fact 都 blocked → 大量误阻断。
- **为什么有问题**: 这是 writer 的 correctness gate。如果 evidence_missing 的 fact 被放行去支撑关键数值判断（如费率、收益率），报告就会出现无证据锚点的结论，违反 AGENTS.md "证据必须可溯源" 和模板 "所有数值判断必须标注数据来源" 的硬约束。
- **直接证据**: Gate 1 `ChapterFactEntry.required_by` 字段标记了 fact 支撑的约束（如 `("CHAPTER_CONTRACT.chapter_2", "ITEM_RULE.chapter_2_alpha_yearly_breakdown")`），但 plan §7.4 第 4 点没有引用 `required_by` 作为判定依据。第 2 章 fact `nav_benchmark_performance` 的 `required_by` 包含 `CHAPTER_CONTRACT.chapter_2`，如果该 fact 有值但缺 anchor，按 plan 当前写法无法确定是否应 blocked。
- **影响**: 实现 agent 自行定义规则 → Gate 3 orchestrator 收到的 draft 可能含无证据关键判断 → 审计漏过或返工
- **建议改法和验证点**: 在 §7.4 第 4 点增加判定算法：(a) fact.required_by 包含 CHAPTER_CONTRACT 引用 → 视为支撑关键判断；(b) fact 的 source_field_id 对应 `fee_schedule`、`nav_benchmark_performance`、`tracking_error` 等数值密集型字段 → 视为支撑数值判断；(c) 实现一个 `_fact_supports_critical_judgment(fact) -> bool` helper，在 tests 中覆盖以上两类场景。
- **修复风险（低/中/高）**: 低 — 只需明确算法，不改变 plan 结构
- **严重程度（低/中/高/严重）**: 高

### 02-未修复-MEDIUM-ChapterDraft.declared_missing_reasons 提取机制缺失

- **位置**: §7.3 `ChapterDraft` dataclass 定义，"declared_missing_reasons: tuple[ChapterFactMissingReason, ...]"
- **问题类型**: 契约缺失
- **当前写法**: `ChapterDraft` 包含 `declared_missing_reasons` 字段，说明"草稿中声明了哪些缺失原因"。但 plan 没有指定 writer 如何从 LLM 自由文本输出中提取这些 reasons。
- **反例/失败场景**: LLM 输出一段中文："由于招募说明书未披露基金经理持有情况，本项无法判断"。writer 如何知道这对应 `field_missing` 还是 `evidence_missing`？如果 LLM 措辞变化，提取逻辑不稳定，`declared_missing_reasons` 在跨 run 间不一致。
- **为什么有问题**: `declared_missing_reasons` 是 auditor 检查 missing semantics 是否被正确降级的关键输入。如果提取不可靠，auditor 无法判断 writer 是否真的声明了缺口还是偷偷补全了事实。
- **直接证据**: Plan §7.4 第 6 点只说了 LLM post-check 检查 "forbidden phrases、empty response、unauthorized anchor/fact reference、max length"，没有提及 missing reasons 提取。Slice 2 `_draft_from_llm_response()` 描述为"解析正文中显式 anchor ids 或证据锚点行"，同样没有 missing reasons 解析。
- **影响**: 实现 agent 可能 (a) 跳过提取使 `declared_missing_reasons` 恒为空；(b) 用脆弱的正则匹配 → Gate 3 audit 不可靠
- **建议改法和验证点**: 二选一：(a) 要求 LLM 在输出中用标记语法声明缺口，如 `<!-- missing:field_missing -->`，writer 用正则提取；(b) 如果 LLM 不能可靠输出标记，则 `declared_missing_reasons` 字段标记为 "Gate 2 最小实现置空，完整提取留给 Gate 3 LLM audit"，并在 `ChapterAuditInput` 中让 auditor 自行从 draft markdown 判断。无论哪种，plan 必须明确。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-MEDIUM-ChapterAuditResult 聚合 repair_hint 无计算规则

- **位置**: §8.3 `ChapterAuditResult` dataclass，"repair_hint: ChapterAuditRepairHint"
- **问题类型**: 契约缺失
- **当前写法**: `ChapterAuditIssue` 每条有 `repair_hint`，`ChapterAuditResult` 也有一个聚合 `repair_hint`。但 plan 未指定如何从多条 issue 的 hint 聚合出顶层 hint。
- **反例/失败场景**: programmatic audit 产出 3 条 issue：2 条 `repair_hint="patch"`, 1 条 `repair_hint="needs_more_facts"`。聚合 hint 应该是 `"needs_more_facts"`（取最重），还是 `"patch"`（取多数）？如果实现不一致，Gate 3 orchestrator 的 repair policy 会收到矛盾的信号。
- **为什么有问题**: `repair_hint` 是 Gate 2 给 Gate 3 的唯一修复建议通道。聚合规则不明确会导致 Gate 3 做出错误的 repair decision（比如用 patch 去修一个需要更多 facts 的问题）。
- **直接证据**: Plan §9 汇总规则只说 "LLM 只返回 informational/reviewable issues 时，Gate 2 可返回 `fail` + `repair_hint="patch"`"，但没有说明多条 issue 混合时的优先级。`ChapterAuditRepairHint` literal 值有 `"none" < "patch" < "regenerate" < "needs_more_facts"` 的自然严重度排序，但 plan 未确认这个排序。
- **影响**: Gate 3 orchestrator 收到语义不一致的 repair_hint → 修复策略选择错误 → 返工
- **建议改法和验证点**: 在 §8.3 或 §9 明确聚合规则：`repair_hint = max(issues.map(hint), key=severity_order)`，其中 `severity_order = {"none": 0, "patch": 1, "regenerate": 2, "needs_more_facts": 3}`。在 test 中覆盖多 issue 聚合场景。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 04-未修复-MEDIUM-程序审计未检查 non_asserted_facets 被误用为断言事实

- **位置**: §9 Programmatic audit 检查清单，对比 §7.4 Writer data flow 第 3 点
- **问题类型**: 契约缺失
- **当前写法**: Plan §7.4 第 3 点要求 writer prompt 明确"`non_asserted_facets` 只能解释'未断言 subtype'，不得当作事实"。§10 evidence anchor constraints 也有类似要求。但 §9 programmatic audit 的检查清单（P1/P2/E1/E3/C2/C1/L1/R1）中没有包含对 non_asserted_facets 误用的检查。
- **反例/失败场景**: Writer（或 LLM）在草稿中写了"该基金为宽基指数基金"，但 `ChapterFacetResolution.facets=()` 且 `non_asserted_facets=("宽基指数基金",)`。Programmatic audit 不会检测到"宽基指数基金"这个 facet 被当作确定事实使用，因为它不在 P1/P2/E1/E3/C2/C1 任何一条规则的检查范围内。
- **为什么有问题**: Gate 1 controller judgment 明确说 "兼容标签只进入 non_asserted_facets，不得驱动 ITEM_RULE"。如果 writer 把 non_asserted_facet 写成确定事实，这违反了 fail-closed facet assertion 语义，但 programmatic audit 没有拦阻。
- **直接证据**: Plan §9 程序审计清单没有 non_asserted_facets 检查。C2 ITEM_RULE 只检查 delete/skip 的 item 是否出现，不检查 non_asserted_facets 是否被误升格为事实。
- **影响**: non_asserted facet 被当作事实输出 → 违反 Gate 1 fail-closed 语义 → 下游误判基金类型
- **建议改法和验证点**: 在 programmatic audit 的 C2 或新增规则中增加：检查 draft 正文是否直接断言了 `non_asserted_facets` 中的 facet 名称而未加"未断言"/"可能"等限定词。最小实现可用子串匹配（facet 名出现在正文但附近没有 `non_asserted_facets` 提示词）。同时在 writer prompt 中要求 LLM 在提到 non_asserted facet 时使用明确标记如"（未断言）"。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 05-未修复-LOW-E2 审计规则缺席需显式声明为 deferred

- **位置**: §9 Programmatic audit 规则清单
- **问题类型**: 契约缺失
- **当前写法**: Programmatic audit 覆盖了 P1/P2/E1/E3/C1/C2/L1/R1/R2，但缺失 E2（"证据与断言不匹配"）。LLM audit 覆盖了"判断断言是否被提供的 facts/anchors 支撑"，部分对应 E2。
- **反例/失败场景**: 如果 future reader 对比模板附录 B 审计规则速查（其中 E2 标明"可复核"级别）和代码实现的 programmatic audit，会发现 E2 缺失。这可能被误认为是实现 bug 而非设计决策。
- **为什么有问题**: E2 需要重新打开年报原文对比断言，这超出 Gate 2 范围（writer/auditor 不读取 PDF/source）。但 plan 没有显式声明 E2 被推迟到 Evidence Confirm gate，可能让后续 gate 误以为 E2 已在本 gate 覆盖。
- **直接证据**: 模板附录 B 定义了 E2="证据与断言不匹配"为"可复核"级别。Plan §9 programmatic audit 有 E1（证据锚点不精确）和 E3（证据完全缺失），但没有 E2。§17 residual risks 提到 "Evidence Confirm / anchor-to-source verification 仍是后续 gate"，但没有显式点名 E2。
- **影响**: 低 — 不影响 Gate 2 实现，但缺少显式声明可能导致后续 gate 遗漏 E2
- **建议改法和验证点**: 在 §9 programmatic audit 清单末尾增加一行说明："E2（证据与断言不匹配）需要对照年报原文，超出 Gate 2 范围，推迟到 Evidence Confirm gate"。或在 §17 residual risks 中显式列出 E2。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 06-未修复-LOW-bond_risk_evidence 锚点边界在 draft 解析中需显式排除

- **位置**: §10 Evidence anchor constraints，"bond_risk_evidence 锚点" 段落；Slice 2 `_draft_from_llm_response()`
- **问题类型**: 其它
- **当前写法**: Plan §10 说 "Gate 2 最小实现不得强行正文引用其内部 ref，除非另有显式 conversion helper 并有测试覆盖"。Slice 2 `_draft_from_llm_response()` 会解析 LLM 输出中的 anchor 引用。
- **反例/失败场景**: 如果 writer prompt 的 `allowed_anchor_ids` 不包含 bond_risk_evidence 的内部 ref（因为 Gate 1 未展开为 ChapterEvidenceAnchor），但 LLM 自行从 facts 的 value 中读取了组级 anchor ref 并写入正文。Draft 解析器发现正文引用了一个不在 `allowed_anchor_ids` 中的 anchor → 正确 blocked。但 blocked 的原因消息可能不清晰（"unknown anchor reference" vs "bond_risk_evidence 内部锚点未展开"）。
- **为什么有问题**: 低影响 — 系统会正确 fail-closed，但错误消息不精确会浪费调试时间。
- **直接证据**: Gate 1 `_project_bond_risk_evidence_fact()` 返回 `evidence_anchor_ids=()` 且 `missing_detail="bond_risk_evidence 组级锚点引用保留在 value.anchors 内，未展开为 ChapterEvidenceAnchor"`。Writer 的 `allowed_anchor_ids` 因此不包含 bond_risk_evidence 锚点。
- **影响**: 低 — fail-closed 行为正确，仅错误消息可改进
- **建议改法和验证点**: 在 Slice 2 `_draft_from_llm_response()` 的 anchor 校验中，增加对 bond_risk_evidence 相关 fact 的特殊处理：如果被引用的 anchor 疑似来自 bond_risk_evidence value 内部，错误消息应提示"bond_risk_evidence 组级锚点未展开，需 conversion helper"。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 07-未修复-INFO-MiMo 已覆盖发现的确认与补充

- **位置**: MiMo review findings 01-05
- **问题类型**: 其它
- **当前写法**: MiMo 已发现 5 个 findings。本 review 独立验证后确认：
  - MiMo-01 (MEDIUM, anchor ref 解析格式)：**确认成立**。补充：如果 LLM 不能稳定输出 `<!-- anchor:... -->`，plan 没有定义降级策略（如回退到正则匹配正文证据行 `> 📎 证据：...`）。建议在 plan 中明确"优先匹配 HTML comment，回退匹配正文证据行"的两层策略。
  - MiMo-02 (MEDIUM, LLM audit 输出解析)：**确认成立**。补充：`audit_focus` 的默认值 MiMo 建议为 `["evidence_support", "must_not_cover_boundary", "missing_semantics", "readability"]`，这与 §9 LLM audit 的 4 项职责完全对应，建议直接采纳。
  - MiMo-03 (LOW, prompt_only stop_reason)：**确认成立**。
  - MiMo-04 (LOW, Slice 4 docs 范围)：**确认成立**。
  - MiMo-05 (INFO, value 序列化)：**确认成立**。
- **为什么有问题**: 不重复计数，仅确认 MiMo 的发现仍然有效且未被 plan 修订。
- **直接证据**: MiMo artifact 第 42-100 行。
- **影响**: INFO — 对 verdict 无增量影响
- **建议改法和验证点**: Controller 在裁决时应同时考虑 MiMo 的 5 个 findings 和本 review 的前 6 个 findings。
- **修复风险（低/中/高）**: N/A
- **严重程度（低/中/高/严重）**: INFO

---

## Open Questions

无。所有 review lens 的问题已通过 findings 覆盖或确认为 deferred。

## Residual Risks

| 风险 | 说明 | 建议跟踪位置 |
|------|------|-------------|
| Writer preflight "支撑数值/关键判断" 算法未冻结 | 实现 agent 可能选择过松或过严的判定标准，影响 evidence_missing 场景的 fail-closed 正确性 | Gate 2 implementation evidence — 必须记录选定的判定算法和测试覆盖 |
| LLM prompt 质量 | `value: object \| None` 序列化策略未定义（MiMo-05）；prompt engineering 质量影响 LLM 输出稳定性 | Gate 2 implementation evidence — 记录序列化策略及其对 test fixture 的影响 |
| LLM 输出可复现性 | Anchor ref 解析（MiMo-01）、audit issue 解析（MiMo-02）、missing reasons 提取（DS-02）均依赖 LLM 遵循输出格式 | Gate 2 implementation evidence — fake client 必须返回确定性 fixture |
| bond_risk_evidence 锚点 | Gate 1 residual：组级 anchors 未展开为 ChapterEvidenceAnchor | Gate 3 或独立 evidence gate |
| 第 0/7 章默认 blocked | 本 gate 无 accepted chapters，第 0/7 章永远 blocked | Gate 3 orchestrator — 需先完成 1-6 章 |
| cross_period_comparison | 第 5 章需要跨期数据，当前只有单期 bundle | Gate 3 或独立 data gate |
| E2 审计规则 deferred | 证据与断言匹配验证需要重读年报原文 | Evidence Confirm gate |
| repair_hint 聚合 | 如果 plan 未明确聚合规则，Gate 3 收到的 hint 可能不一致 | Gate 2 implementation — 聚合规则必须在 code 中明确并测试 |

---

## Plan Review Conclusion

**PASS_WITH_NON_BLOCKING**

Plan 的核心架构决策正确且足够具体：
- Writer/auditor 正确归属 Fund 层，消费 `ChapterFactProjection` / `ChapterFactInput`，不读取 repository/PDF/source
- LLM client 通过 typed Protocol 注入，缺失时 fail-closed，不 fake pass
- CHAPTER_CONTRACT must_answer/must_not_cover、ITEM_RULE delete/render、preferred_lens、evidence anchors、fund_type unknown、non_asserted_facets 在 writer prompt 和 programmatic audit 中均有对应处理
- Programmatic audit 与 LLM audit 责任边界清晰，stop conditions 完备
- 4 个 slices 粒度合理，tests 覆盖 happy/blocked/semantic-fail/import-boundary
- Non-goals 明确排除 orchestrator、repair loop、CLI、dayu，scope 无漂移

1 个 HIGH finding（writer preflight 判定算法）可在实现阶段自然解决，不需 plan 回炉。5 个 MEDIUM/LOW findings 均可通过小幅 plan 补充或实现中记录决策来消除。加上 MiMo 的 2 个 MEDIUM + 2 个 LOW findings，总计风险可控，不阻塞 implementation agent 开始工作。

需要注意的是：如果 controller 要求所有 MEDIUM 以上 findings 在 plan 中修复后才授权实现，则本 gate 需先回炉 plan。但从 review 角度看，所有发现都不需要改变 plan 的核心架构决策或 slice 结构，实现 agent 有能力在 coding 阶段处理。

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] findings 是 evidence-based、adversarial、可执行，且没有 style/nit/speculation
- [x] open questions、residual risks、tracking destination 与 findings 分开
- [x] conclusion 只能是 PASS / PASS_WITH_NON_BLOCKING / BLOCKED — 本 review 为 PASS_WITH_NON_BLOCKING
- [x] output path 为 `docs/reviews/mvp-gate2-chapter-writer-auditor-plan-review-ds-20260530.md`
- [x] 未修改 plan 文件，未 stage/commit/push/PR
