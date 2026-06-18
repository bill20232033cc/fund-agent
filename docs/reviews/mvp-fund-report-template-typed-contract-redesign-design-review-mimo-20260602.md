# MVP fund report template typed contract redesign design — adversarial plan review (MiMo)

## Reviewer Self-Check

- Role: independent adversarial plan/design reviewer (AgentMiMo), not controller.
- Gate: `MVP fund report template typed contract redesign gate`.
- Target: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`.
- Classification: heavy.
- Scope: adversarial plan/design review only. No implementation, no code, no truth-source edits, no commit, no push, no PR.
- Required read set: all 9 files consumed. Evidence references are to `summary.json`, controller design artifact, external redesign spec, slice1 controller judgment, and Agent-engine controller judgment.
- Review lens: evidence-backed, first-principles, scope-safe, handoff-ready, UI -> Service -> Host -> Agent consistency.

## Finding 1: audit_focus 控制边界存在歧义 — 可能侵入程序化审计领域

**Evidence:**

Decision 7 明确约束: "audit_focus controls LLM auditor instruction emphasis and repair hint grouping. Programmatic C2, required markers, anchor validation, missing/degrade policy, forbidden investment advice, and implemented L1/R rules stay always-on."

但外部草案 `AuditFocusLiteral` 列表包含 4 个新增项 (`evidence_gap_declaration`, `evidence_conditional_phrase`, `cross_chapter_consistency`, `data_availability_match`, `first_class_facet_respect`)，其中多项听起来可以程序化检查:

- `data_availability_match`: "不允许写 '近 5 年' 当 5Y availability=False" — 这是词法匹配 + 可用性标志检查，完全可程序化。
- `evidence_gap_declaration`: "必须显式 EVIDENCE_GAP" — 这是标记存在性检查，完全可程序化。
- `cross_chapter_consistency`: "Ch0 结论必须等于 Ch9 结论" — 这是跨章字段比对，完全可程序化。
- `first_class_facet_respect`: "非 first-class 章节不展开 facet" — 这是 facet 归属检查，可程序化。

**Impact:**

如果实现团队将 `audit_focus` 解释为"也控制程序化规则选择"，则违反 Decision 7 的 always-on 约束，可能悄悄放松 C2/L1/R 阻断规则。如果解释为"仅控制 LLM 语义审计"，则这 4 个新增项对 LLM 是好的指导，但它们描述的检查需要在程序化审计层单独实现，否则 `data_availability_match` 等规则不会被执行。

**Suggested fix:**

在 Decision 7 或 "What Must Not Enter Accepted Future Design Yet" 中显式声明: 新增 `AuditFocusLiteral` 项仅控制 LLM 审计员指令强调；对应的程序化检查实现属于独立的程序化审计扩展 gate，不在本 gate scope 内。

**Fix risk:** low — 仅需补充声明文字。

**Severity:** high — 直接影响审计语义是否被悄悄放松。

---

## Finding 2: `EvidenceAvailability.source_strength_by_requirement` 语义未定义

**Evidence:**

Decision 2 的 `EvidenceAvailability` 未来 contract shape 包含 `source_strength_by_requirement` 字段，但:

- 外部草案的 `EvidenceAvailability` 定义 (`docs/superpowers/specs/2026-06-02-template-redesign-from-first-principles.md` Section 3.3) 不包含此字段。
- 设计 artifact 未定义"strength"的等级、如何影响审计决策、或与 `MustAnswerClause.data_availability_tier` 的交互关系。
- 残留风险列表未提及此字段。

**Impact:**

实现 gate 可能发现此字段无法实现或与其他字段冲突，导致设计返工。如果"strength"与 `data_availability_tier` 语义重叠，会产生两套不一致的可用性表示。

**Suggested fix:**

在 Decision 2 中将 `source_strength_by_requirement` 移至 Deferred 列表，或定义其语义: 等级枚举、与 `data_availability_tier` 的关系、审计决策中的使用方式。

**Fix risk:** low — 补充定义或移至 Deferred。

**Severity:** high — 未定义字段可能导致实现时设计返工。

---

## Finding 3: `MustNotCoverClause.allowed_contexts` 程序化审计行为未指定

**Evidence:**

Decision 3 定义 `allowed_contexts: required_label | evidence_gap_statement | quote | anchor_caption`，但:

- 未指定程序化审计是否检查 `allowed_contexts`。
- 控制器证据显示 Ch3 writer 在 attempt 0 已尝试 missing-evidence framing ("无法判断一致性")，但仍然触发 C2。这表明当前程序化审计不区分上下文。
- 如果新设计中程序化审计不检查 `allowed_contexts`，则该字段仅对 LLM 语义审计有意义，Ch3 的程序化 C2 问题不会被解决。
- 如果程序化审计检查 `allowed_contexts`，则需要明确的匹配规则。

**Impact:**

Ch3 的核心问题 (程序化 C2 在 `言行一致` 上的误触发) 可能不会被 evidence-conditional `must_not_cover` 解决，除非 `allowed_contexts` 被程序化审计使用。设计 artifact 将 evidence-conditional 标记为"最重要的未来合同变更"，但未说明它是否解决程序化 C2 还是仅解决 LLM 语义审计。

**Suggested fix:**

在 Decision 3 中明确: (a) evidence-conditional `must_not_cover` 是否影响程序化 C2 检查; (b) 如果是，`allowed_contexts` 如何被程序化匹配; (c) 如果否，程序化 C2 的修复路径是什么。

**Fix risk:** medium — 需要明确设计决策，可能影响 implementation scope。

**Severity:** high — 直接影响 Ch3 核心问题是否被解决。

---

## Finding 4: 外部草案 timeout 根因分析与控制器证据不一致，但未被显式反驳

**Evidence:**

外部草案 F-2 声称: "Ch2/Ch4/Ch6 的 60s timeout 不是 prompt size 问题"，D-2 声称 "timeout 根因的 60% 在合同复杂度，30% 在 audit_focus 不分章，10% 在 prompt 长度"。

但 `summary.json` 运行时诊断显示:

- Ch2: `provider_runtime_category=timeout`, `timeout_root_cause_hint=small_prompt_provider_timeout`, `user_prompt_chars=2917`, `elapsed_ms=60003`。
- Ch4: `provider_runtime_category=timeout`, `timeout_root_cause_hint=small_prompt_provider_timeout`, `user_prompt_chars=2280`, `elapsed_ms=60003`。
- Ch6: `provider_runtime_category=timeout`, `timeout_root_cause_hint=small_prompt_provider_timeout`, `user_prompt_chars=2868`, `elapsed_ms=60003`。

控制器 slice1 judgment 将 Ch2/Ch6 分类为 "provider runtime blocker"，不是 "contract complexity blocker"。`small_prompt_provider_timeout` 提示 provider 在小 prompt 下也超时，这与合同复杂度无关。

控制器正确拒绝了 D-11 的具体百分比，但未显式指出外部草案的根因分析 (60% 合同复杂度) 与 `small_prompt_provider_timeout` 证据不一致。

**Impact:**

如果未来 gate 接受外部草案的根因分析，可能错误地优先考虑模板重构而非 provider runtime 调查。

**Suggested fix:**

在 "Retained LLM Evidence" 或 "Residual Risks" 中显式记录: 外部草案 D-2 的根因分配 (60% 合同复杂度) 与 `small_prompt_provider_timeout` 诊断不一致；Ch2/Ch4/Ch6 timeout 的根因应优先通过 provider runtime 预算 gate 调查。

**Fix risk:** low — 补充事实记录。

**Severity:** medium — 可能误导未来 gate 优先级。

---

## Finding 5: evidence-conditional "最重要的未来合同变更" 声明基于单一章节证据

**Evidence:**

Decision 3 声称: "Accept evidence-conditional must_not_cover as the most important future contract change."

支撑证据全部来自 Ch3:

- Ch3 must_answer 要求 "言行一致性判断"。
- Ch3 must_not_cover 禁止 "言行一致" 短语。
- Ch3 writer 两次尝试都触发 C2。
- Ch3 `failure_category=prompt_contract`。

Ch0/Ch1/Ch4/Ch5/Ch7 的 retained evidence 中没有 must_not_cover 误触发记录。Ch2/Ch6 的失败是 `llm_timeout`，不是 `prompt_contract`。

**Impact:**

"最重要" 的声明暗示广泛适用性，但证据仅支持 Ch3。如果其他章节没有类似的 must_not_cover 问题，则构建通用 evidence-conditional 框架的投入产出比可能不如预期。

**Suggested fix:**

将 "the most important future contract change" 限定为 "the most important future contract change for Ch3"，或补充说明广泛适用性需要更多章节的 evidence-conditional 校准证据。

**Fix risk:** low — 限定声明范围。

**Severity:** medium — 可能误导优先级排序。

---

## Finding 6: `allowed_contexts` 中 `quote` 上下文的边界条件未定义

**Evidence:**

Decision 3 的 `allowed_contexts` 包含 `quote`，但:

- 未定义什么构成 "quote" (直接引用? 间接引用? 模板原文引用?)。
- 未定义 `quote` 上下文是否允许正面 `言行一致` 结论。
- 外部草案 F-1 证据显示 `_must_not_cover_phrases` 使用纯词法匹配，不区分引用和作者陈述。

**Impact:**

如果 `quote` 上下文允许包含 `言行一致` 的引用，LLM 可能通过引用模板原文来绕过 C2 阻断。如果 `quote` 不允许正面结论，则需要定义"引用中提及但不做正面结论"的边界。

**Suggested fix:**

在 Decision 3 中定义 `quote` 上下文的边界: 是否允许在引用中包含 forbidden phrase、是否允许在引用后附加正面结论、程序化审计如何区分引用和作者陈述。

**Fix risk:** medium — 需要明确语义边界。

**Severity:** medium — 可能成为 LLM 规避审计的路径。

---

## Finding 7: EvidenceAvailability 与现有 ChapterFactProjection 的关系未定义

**Evidence:**

Decision 2 接受 `EvidenceAvailability` 作为 "the source of evidence-present/evidence-missing decisions"，但:

- 当前设计 (`docs/design.md`) 使用 `ChapterFactProjection` 提供结构化事实。
- `EvidenceAvailability` 的 `available_fact_ids` / `available_anchor_ids` 与 `ChapterFactProjection` 的事实投射语义重叠。
- 设计 artifact 未说明 `EvidenceAvailability` 是 `ChapterFactProjection` 的包装器、替代品、还是补充层。
- 残留风险列表包含 "Whether EvidenceAvailability should be derived from current ChapterFactProjection only, or require a new evidence bundle before implementation"，但未给出设计判断。

**Impact:**

实现团队可能假设 `EvidenceAvailability` 直接替代 `ChapterFactProjection`，引入不必要的复杂性；或假设它是包装器，遗漏语义差异。

**Suggested fix:**

在 Decision 2 中明确 `EvidenceAvailability` 与 `ChapterFactProjection` 的关系: 包装器、替代品、或补充层。如果需要新 evidence bundle，将其标记为 Deferred。

**Fix risk:** medium — 需要明确架构关系。

**Severity:** medium — 可能导致实现时架构返工。

---

## Finding 8: Ch7 依赖链在 Ch2 拆分推迟的情况下未闭合

**Evidence:**

Decision 5 接受 Ch0 消费 Ch7 结论。Ch7 (最终判断) 的 `must_answer` 包含 "R=A+B-C 收益归因结论"。当前 Ch2 包含 R/B/A/C。

如果未来 gate 接受 Ch2 拆分 (控制器 Deferred)，Ch7 需要从 Ch2 (业绩) + Ch3 (归因) + Ch4 (成本) 消费结论。但:

- Decision 6 拒绝了 Ch2 拆分作为 accepted future design。
- Decision 5 的 `consumes_chapter_conclusions` 未考虑 Ch2 拆分后的依赖链。
- 外部草案 0+9 结构中 Ch9 消费 Ch2/Ch3/Ch4，但控制器拒绝了 0+9。

**Impact:**

如果未来 gate 接受 Ch2 拆分，Ch7 的 `consumes_chapter_conclusions` 需要重新设计，可能产生设计债务。

**Suggested fix:**

在 Decision 6 的 "If a later controller accepts a split" 部分显式添加: Ch7 的 `consumes_chapter_conclusions` 必须同步更新，以反映拆分后的依赖链。

**Fix risk:** low — 补充未来 gate 的检查项。

**Severity:** medium — 设计债务，不阻塞当前 gate。

---

## Finding 9: 接受 typed ChapterContract 与拒绝 Ch2 拆分的一致性未显式论证

**Evidence:**

外部草案将 typed ChapterContract 和 Ch2 拆分作为同一提案的一部分 (Section 3.1-3.2)。控制器接受 typed ChapterContract (Decision 1) 但拒绝 Ch2 拆分 (Decision 6)。

"与现有 spec 的关系" 部分提到 "本文是 plan A 的深化与重设计"，但未显式论证接受 typed contract 而拒绝结构拆分的一致性。

**Impact:**

未来 reviewer 可能质疑: 如果 typed contract 是好的，为什么结构拆分不是? 如果结构拆分的证据不足，typed contract 的证据是否也仅基于 Ch3?

**Suggested fix:**

在 Decision 6 中补充一句: typed ChapterContract 与章节结构拆分是独立的设计维度；前者改善契约表达精度，后者改变章节粒度。接受前者不要求接受后者。

**Fix risk:** low — 补充论证。

**Severity:** low — 逻辑清晰性，不阻塞。

---

## Finding 10: Ch2 拆分推迟但外部草案 0+9 重编号未被显式隔离

**Evidence:**

外部草案 Section 3.1 定义了 0+9 结构，包含 Ch0-Ch9 的新编号。控制器拒绝了 0+9 (Decision 6)，但:

- 外部草案的 `ChapterContract` 草案 (Section 3.2) 使用 `chapter_id: int`，未指定是 0-7 还是 0-9。
- Decision 1 的 `ChapterContract` shape 包含 `chapter_id` 但未指定编号范围。
- 如果未来 gate 接受 Ch2 拆分，需要决定是保持 0-7 还是扩展到 0-9。

**Impact:**

实现团队可能假设 `chapter_id` 范围是 0-9 (跟随外部草案)，与当前 0-7 事实冲突。

**Suggested fix:**

在 Decision 1 中显式声明: 当前 accepted future design 的 `chapter_id` 范围是 0-7，与现有模板一致。任何编号变更需要独立 gate。

**Fix risk:** low — 补充范围约束。

**Severity:** low — 范围澄清。

---

## Finding 11: 部分证据可用性场景的审计行为未设计

**Evidence:**

Decision 3 的 Ch3 示例展示了三种状态:

- `actual_behavior.turnover_rate.available`
- `actual_behavior.holdings_snapshot.missing_or_unreviewed`
- `style_change_evidence.cross_period.missing_or_unreviewed`

但未设计当部分证据可用时的审计行为:

- 如果 `turnover_rate` 可用但 `style_change_evidence` 不可用，LLM 是否可以写 "基于换手率数据，未观察到频繁调仓，但缺乏跨期风格变化证据，无法做出完整判断"?
- 这种部分结论是否触发 C2?
- `evidence_conditional` 如何处理部分满足条件?

**Impact:**

实现时可能发现部分可用性是常见场景，但没有明确的审计规则，导致不一致的行为。

**Suggested fix:**

在 Decision 3 中添加 "Partial availability" 小节: 定义当 `evidence_conditional` 的部分条件满足时的审计行为。

**Fix risk:** medium — 需要明确设计决策。

**Severity:** medium — 常见场景未覆盖。

---

## Finding 12: `MustAnswerClause.fallback` 与 `RequiredOutputItem.when_evidence_missing` 语义重叠

**Evidence:**

Decision 1 定义 `MustAnswerClause.fallback: Literal["evidence_gap", "delete_section", "degrade_to_question"]`。

Decision 4 定义 `RequiredOutputItem.when_evidence_missing: render_evidence_gap | render_minimum_verification_question | delete_if_not_applicable | block`。

两者语义重叠:

- `MustAnswerClause.fallback="evidence_gap"` ≈ `RequiredOutputItem.when_evidence_missing="render_evidence_gap"`
- `MustAnswerClause.fallback="degrade_to_question"` ≈ `RequiredOutputItem.when_evidence_missing="render_minimum_verification_question"`
- `MustAnswerClause.fallback="delete_section"` ≈ `RequiredOutputItem.when_evidence_missing="delete_if_not_applicable"`

但 `MustAnswerClause` 有 `delete_section` (删除整个章节段落)，而 `RequiredOutputItem` 有 `block` (阻断)。两者的交互关系未定义: 如果 `MustAnswerClause.fallback="evidence_gap"` 但对应的 `RequiredOutputItem.when_evidence_missing="block"`，应该执行哪个?

**Impact:**

实现时可能发现两套 fallback 机制冲突，导致不一致的行为。

**Suggested fix:**

在 Decision 1 和 Decision 4 中明确: `MustAnswerClause.fallback` 和 `RequiredOutputItem.when_evidence_missing` 的优先级关系; 或合并为统一的 missing-behavior 机制。

**Fix risk:** medium — 需要明确设计决策。

**Severity:** medium — 可能导致实现时语义冲突。

---

## Conclusion

**Pass with risks.** 12 findings, 0 blocking. 3 high-severity, 6 medium-severity, 3 low-severity。

设计 artifact 整体证据充分、范围安全、non-goal 声明完整。7 个 Decision 中 6 个有直接 retained evidence 支撑，1 个 (Ch2 split) 正确推迟。"What Must Not Enter Accepted Future Design Yet" 覆盖全面。

主要风险集中在: (1) audit_focus 控制边界歧义 (Finding 1); (2) EvidenceAvailability 新增字段未定义 (Finding 2); (3) allowed_contexts 程序化审计行为未指定 (Finding 3)。这三个 high-severity findings 都是"设计未完成"而非"设计错误"，应在实施 gate 前补充。

## Residual Risks / Open Questions

1. **audit_focus 程序化 vs 语义边界**: 需要在实施 gate 显式定义 audit_focus 的控制范围，避免悄悄放松程序化审计。
2. **EvidenceAvailability 与 ChapterFactProjection 关系**: 需要在实施 gate 决定架构关系 (包装器/替代品/补充层)。
3. **allowed_contexts 程序化实现**: 需要在实施 gate 决定程序化审计是否使用 allowed_contexts。
4. **部分证据可用性**: 需要在实施 gate 设计 partial availability 的审计规则。
5. **MustAnswerClause.fallback 与 RequiredOutputItem.when_evidence_missing 交互**: 需要在实施 gate 合并或定义优先级。
6. **Ch2 拆分后的 Ch7 依赖链**: 需要在 Ch2 split gate 显式更新。
7. **外部草案 D-2 根因分析与 small_prompt_provider_timeout 不一致**: 需要在 provider runtime budget gate 显式调查。
8. **assertion polarity 中文文本匹配**: 需要在实施 gate 设计具体的匹配规则。
9. **quote 上下文边界**: 需要在实施 gate 定义引用 vs 作者陈述的区分规则。
10. **evidence-conditional 广泛适用性**: 需要更多章节的校准证据验证。

## Validation

```bash
git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-mimo-20260602.md
```

Secret-safety statement: this artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw prompt body, or secret-bearing runtime payload. It references only safe local artifact paths, safe diagnostic labels, and short public/template excerpts needed for design review.
