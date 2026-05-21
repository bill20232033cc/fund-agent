# P12-S2 Plan Review — AgentGLM（2026-05-22）

## Verdict

**PASS_WITH_FINDINGS**

Plan 可进入下一 gate；findings 均为非阻塞，implementation agent 可在执行时直接处理。

---

## 1. Review Scope

- **Plan**: `docs/reviews/post-p12-s1-follow-up-planning-20260522.md`
- **Design truth**: `docs/design.md` v1.1
- **Control truth**: `docs/implementation-control.md`（Startup Packet gate `P12-S1 accepted`）
- **P12-S1 code review**: `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md`
- **Renderer source**: `fund_agent/fund/template/renderer.py`
- **Renderer tests**: `tests/fund/template/test_renderer.py`
- **Repo audit**: `docs/repo-audit-20260521.md`（excluded，保持未跟踪）

---

## 2. Slice Selection Assessment

### 2.1 是否是最小、最直接、风险收益最高的 product-safety slice

**结论：是。**

代码事实：`_item_rule_evidence_bullet`（renderer.py:598-613）当前只取 `anchors[0]`，丢弃了 `_render_tracking_error_segment` 已合并去重的全部 anchor。对 `enhanced_index` 类型的跟踪误差段落，benchmark anchors 和 RABC anchors 合并后应产生多个不同 anchor，但用户只能看到一个。

第一性原理判断成立：这个 slice 只修复已有报告输出的信息损失，不新增判断、不改变分析结论、不引入新数据契约或外部依赖。改动面是 renderer 一个 helper + 对应测试。

Candidate comparison table（plan §3）对 7 个候选的排除理由均有证据支撑且符合 control doc 残余清单。

### 2.2 不应推迟或替换的理由

- 真实 tracking-error extractor 需要 schema、时间序列口径、指数净值来源，远超当前 slice 边界。Plan 明确列为 non-goal。
- RR-13 duplicate `016492` 需要 user/App 源确认，代码不能自动裁决。Control doc 保持 human-owned。
- `docs/repo-audit-20260521.md` 保持 excluded，control doc 已明确。
- Audit noise cleanup 和 dispatch extensibility 当前无需求，plan 正确识别为 premature。

---

## 3. Code-Generation Readiness Assessment

### 3.1 Allowed files

Plan §6 列出 `renderer.py`、`test_renderer.py`、`fund_agent/fund/README.md`、`tests/README.md`，并声明"No other source/test/doc files are allowed without stopping for controller approval"。与 AGENTS.md 模块边界和 design.md 三层架构一致，所有改动在 Fund Capability 内部。

### 3.2 Exact changes

Plan §9 Slice 1 精确指定了 `_item_rule_evidence_bullet` 的变更逻辑：

- empty 保持当前 no-anchor 文本不变
- otherwise compute `anchor_references = tuple(_body_anchor_reference(anchor) for anchor in _dedupe_anchors(anchors))`
- return `f"- 证据边界：{'；'.join(anchor_references)}。"`

这足够让 implementation agent 直接修改，不需要重新设计。注意 `_dedupe_anchors` 已在 renderer.py:1177-1197 实现，`_body_anchor_reference` 已在 renderer.py:834-854 实现，无新增依赖。

### 3.3 测试断言

Plan 要求：
- `enhanced_index` 第 2 章 `#### 跟踪误差分析` 的 `- 证据边界：...` 行包含 benchmark 和 RABC 两个来源的 anchor 文本
- 该行包含 `；`
- 跟踪误差仍说 `数据不足`

**见 F1：断言精度不足。** Plan 未明确要求验证每个 anchor 引用的具体文本是否出现在 bullet 中，仅要求含 `；`。`；` 存在只能证明 joins 发生，不能证明所有 anchor 均被渲染。

### 3.4 Failure paths / stop conditions

Plan §13 列出 5 条 stop condition，包括 schema 变更、输出过长、fixture 不足、越界文件和 review 争议。覆盖面充分。

---

## 4. Multi-Anchor Bullet Semantics Assessment

### 4.1 是否会误导为 evidence sufficiency

**不会。**

- Bullet 标签为 `- 证据边界：`，不是 `- 证据充分：`。
- Plan §5 non-goals 明确："不把 benchmark anchor 伪装成指数成分股、指数编制方法或 tracking error 的证明"。
- Plan §9 Slice 2 README 更新要求声明 "does not prove tracking error/index methodology/constituents"。
- E1/E2/E3 evidence matching 仍为 future audit，不在本 slice 范围。

### 4.2 是否破坏每章一条 `> 📎 证据` 契约

**不会。**

- `_item_rule_evidence_bullet` 使用 `- 证据边界：` 格式，不是 `> 📎 证据：` 格式。
- `_evidence_line`（renderer.py:816-831）是章节级证据行，使用 `> 📎 证据：` 格式，每章只调用一次。
- Plan §8 决策 4 明确用 `；` 在同一 bullet 内 join，不引入额外 `> 📎 证据` 行。
- P12-S1 code review F3 已裁决 "evidence boundary uses bullet format instead of chapter-level quote format" 为 accepted as intended。

### 4.3 Tracking error / index methodology / constituents 数据不足是否保持

Plan §9 Slice 1 non-goals 明确不改 `_render_tracking_error_segment` 正文。该段落的 `数据不足，当前输入未抽取跟踪误差。` 文本和 `后续最小验证` 文本均不在此 slice 变更范围内。

---

## 5. Boundary Compliance

| 边界 | Plan 是否遵守 | 证据 |
|------|:---:|------|
| Fund Capability only | ✅ | §6 allowed files 全部在 `fund_agent/fund/` 和 `tests/fund/` |
| 不依赖 Service/UI/CLI | ✅ | §5 non-goals 列举 Service/UI/CLI 不变 |
| 不依赖 Engine | ✅ | §5 明确排除 Engine |
| 不依赖 FundDocumentRepository | ✅ | §5 明确排除 |
| 不依赖 Dayu runtime | ✅ | §5 明确排除 Host/Engine/tool loop/Dayu |
| 不改 design.md / control doc | ✅ | §11 docs decision 明确 |
| 不改 RR-13 源文件 | ✅ | §5 non-goals |
| 不改 repo-audit | ✅ | §5 non-goals |
| 不改 audit 层 | ✅ | §7 无 schema 变更；marker 不变 |

---

## 6. Test Coverage Assessment

### 6.1 Empty anchors

Plan §9 Slice 1 明确："if anchors empty, keep current no-anchor text exactly"。这覆盖 empty 路径。当前 fixture 中 `missing=True` 路径的 bundle 不产生 ITEM_RULE segments（因 identity_missing 返回空 decisions），但 empty anchors 场景可由其他方式触发。现有测试 `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` 不检查 evidence boundary bullet 内容。

**见 F2：empty anchor 路径需要显式 fixture 或 inline 构造。**

### 6.2 Single anchor

Plan §9 Slice 1 提到 "Add or preserve a single-anchor assertion" 并建议使用 "active fund manager philosophy or index constituents segment"。代码事实：`_render_index_constituents_segment` 只消费 `benchmark.anchors`（fixture 中为 1 个），`_render_manager_philosophy_segment` 只消费 `manager_strategy_text.anchors`（fixture 中也为 1 个）。这两个是天然的单锚点测试点。

### 6.3 Multi anchor

Plan 要求用 `enhanced_index` 的跟踪误差段落测试多锚点。代码追踪：

- `_render_tracking_error_segment` 合并 `benchmark.anchors` + `_collect_rabc_anchors(rabc_attributions)`
- fixture `benchmark = _field({"benchmark": "沪深300..."}, "§2", "benchmark")` 产生 1 个 anchor
- fixture `_rabc()` 产生 2 个 anchor：`("§3", "nav_benchmark_performance")` 和 `("§2", "fee_schedule")`
- 合并去重后应得到 3 个不同 anchor

**确认：当前 fixture 可直接支持多锚点测试，无需扩展 fixture 数据。**

### 6.4 Duplicate anchor

Plan §10 failure paths 提到 "Duplicate anchors do not render twice"。

**见 F3：duplicate anchor 测试需要显式要求。** 当前 fixture 中 benchmark anchor 和 rabc anchor 各不相同，不会自然产生重复。`_dedupe_anchors` 已在 renderer.py 实现去重，但 implementation agent 需要构造或找到一种方式验证重复被消除。Plan 未指定如何触发和验证此路径。

---

## 7. Findings

### F1 — LOW — 多锚点断言应验证具体 anchor 文本，不仅仅是分隔符

**Evidence**: Plan §9 Slice 1 要求 "assert the line contains `；` between references when two or more anchors exist"，但未要求断言每个 anchor 的 `_body_anchor_reference` 输出文本是否出现在 bullet 中。`；` 存在只能证明 join 执行，不能证明所有 anchor 被渲染（例如可能只 join 了两个相同的 anchor 或遗漏了某个）。

**Recommendation**: Implementation agent 应至少断言 tracking error 段落的 `- 证据边界：` 行包含两个不同来源 anchor 的 `_body_anchor_reference` 输出子串（benchmark anchor 和 rabc anchor 各至少一个）。不需要精确匹配完整 bullet 文本，但应验证多来源代表性。

**Blocking?**: 否。Implementation agent 可在编写测试时自行补充，无需 plan 修订。

### F2 — LOW — empty anchor 路径需要显式测试策略

**Evidence**: Plan §9 Slice 1 要求 "if anchors empty, keep current no-anchor text exactly"。但当前 ITEM_RULE 段落的 anchor 全部来自非空 fixture（benchmark、manager_strategy_text、rabc_attributions 均有 anchor）。空 anchor 只发生在相关抽取字段 `missing` 时，但 `missing=True` 路径因 identity_missing 不产生 ITEM_RULE segments。要测试 ITEM_RULE segment 内部 empty anchor 路径，需要在 identity_present 但特定字段 missing 的组合 fixture 下触发。

**Recommendation**: Implementation agent 可用 inline `replace()` 将某个 ITEM_RULE segment 的 anchor tuple 替换为 `()`，然后断言 bullet 仍输出 `数据不足，当前段落未携带独立证据锚点。`。不需要扩展 `_bundle` 或 `_render_input` fixture factory。

**Blocking?**: 否。Implementation agent 可自行构造。

### F3 — LOW — duplicate anchor 消除需要显式测试方案

**Evidence**: Plan §10 failure paths 列出 "Duplicate anchors do not render twice"，但 plan 未指定如何触发重复 anchor 场景。当前 fixture 中 benchmark anchor 和 rabc anchor 各不相同，`_dedupe_anchors` 虽已实现去重但无自然重复可测。

**Recommendation**: Implementation agent 可用 inline `replace()` 构造包含重复 anchor 的 tuple（例如两个相同的 benchmark anchor），传入 `_item_rule_evidence_bullet` 或通过 segment render 间接触发，然后断言 bullet 中该 anchor 只出现一次。或直接对 `_item_rule_evidence_bullet` 做单元级测试。

**Blocking?**: 否。Implementation agent 可自行补充。

---

## 8. Residual Risks

| Risk | Severity | Owner |
|------|:---:|------|
| 多锚点 bullet 输出较长时未来可能需要截断策略 | LOW | Future evidence-display UX slice；plan §14 已识别并 defer |
| Multi-anchor 显示不证明证据充分 | Info | Correct by design：plan §5 non-goals 明确排除 |
| Tracking error / index methodology / constituents 保持数据不足 | Info | Intentional non-goal；plan §14 已识别 |
| RR-13 duplicate `016492` 保持 unresolved | Info | User/App source owned；control doc 保持 |
| `docs/repo-audit-20260521.md` 保持 untracked | Info | Control doc 已明确排除 |

---

## 9. Summary

Plan 是 post-P12-S1 最小、最直接、风险收益最高的 product-safety slice。Slice 选择正确，allowed files 严格在 Fund Capability 内，不改 design/control doc/audit/Service/UI/CLI/Dayu。多锚点 bullet 不会误导为 evidence sufficiency，不会破坏每章一条 `> 📎 证据` 契约。三个 LOW finding 均关于测试精度和覆盖方案，implementation agent 可在执行时直接处理，不阻塞 plan acceptance。
