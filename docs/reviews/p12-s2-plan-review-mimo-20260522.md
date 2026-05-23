# P12-S2 Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan 整体可接受，scope 控制合理，code-generation-ready 程度足够。有 1 个建议性 finding（duplicate anchor 测试覆盖）和 1 个 residual risk。

## Inputs

- Plan under review: `docs/reviews/post-p12-s1-follow-up-planning-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- P12-S1 code review: `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md`
- Source: `fund_agent/fund/template/renderer.py`（`_item_rule_evidence_bullet` L598-613, `_render_tracking_error_segment` L569-595, `_dedupe_anchors` L1177-1197）
- Tests: `tests/fund/template/test_renderer.py`

---

## 1. Slice 选择：是否为最小、最直接、风险收益最高的 product-safety slice

**结论：是。**

- Candidate comparison（§3）合理排除了 RR-13（human-owned）、repo-audit（excluded）、real tracking-error extractor（scope 太大）、index methodology/constituents（scope 太大）、audit noise cleanup（产品安全收益弱）、future ITEM_RULE dispatch（过早抽象）。
- 当前 renderer 只渲染 `anchors[0]`，对于跟踪误差段落同时携带 benchmark anchor（§2/benchmark）和 RABC anchors（§3/nav_benchmark_performance, §2/fee_schedule）的场景，确实存在 provenance 信息损失。
- 改动面窄（1 个 helper 函数 + tests），不改变 `item_rule_decisions`、`item_rule_audit_context`、C2 审计、FQ5 语义、Service/UI/CLI 行为。
- P12-S1 code review controller judgment 已明确将 multi-anchor evidence presentation 标记为 deferred residual，本 slice 直接承接。

**不阻塞。**

## 2. Code-generation-ready 评估

**结论：足够。**

- Allowed files 明确（§6）：`renderer.py` + `test_renderer.py` + READMEs + implementation artifact。
- Exact changes（§9 Slice 1）指定了 `_item_rule_evidence_bullet` 的修改逻辑：empty → 不变；otherwise → `_dedupe_anchors` + `_body_anchor_reference` + `；` join。
- 测试断言（§10）覆盖了 multi-anchor 证据边界行包含全部去重引用、`；` 分隔符、tracking error 仍为数据不足。
- Stop conditions（§13）覆盖了 schema 变更、输出过长、fixture 不足、边界越界等场景。
- Completion report format（§15）标准化。

**不阻塞。**

## 3. Multi-anchor bullet 与证据契约

**结论：设计意图正确，不破坏每章一条 `> 📎 证据` 契约。**

- Plan §4 明确："保持章节级 `> 📎 证据` 一章一条契约不变"。
- `_item_rule_evidence_bullet` 输出的是 `- 证据边界：...` bullet，不是 `> 📎 证据：...` 格式。P12-S1 code review GLM F3 已裁决这种区分是 intended。
- Multi-anchor 展示的是 provenance（哪些来源支撑了段落上下文），不声称 evidence sufficiency。
- Plan §14 明确："Multi-anchor display does not prove evidence supports the claim"。
- Tracking error / index methodology / constituents 保持数据不足（§9 Slice 1 line 7: "Do not alter `_render_tracking_error_segment()` text"）。

**不阻塞。**

## 4. 边界合规

**结论：不违反 Fund Capability 边界。**

- 所有改动在 `fund_agent/fund/template/renderer.py` 内，属于 Fund Capability template renderer。
- 不改 `EvidenceAnchor` schema、`ProgrammaticAuditInput`、`TemplateRenderResult`、Service/UI/CLI/Engine/Dayu 边界。
- 不改 `FundDocumentRepository`、PDF/cache/source helper。
- Plan §5 non-goals 完整覆盖了所有不应触碰的边界。

**不阻塞。**

## 5. 测试覆盖

**结论：基本覆盖，但缺少 duplicate anchor 显式测试路径。**

Plan §10 列出了必须测试的 failure paths：

| Path | Plan 是否覆盖 | 评估 |
|---|---|---|
| Empty anchors → 显式数据不足边界 | ✅ §10 "Empty anchors still render explicit no-anchor data-insufficient evidence boundary" | 充分 |
| Multi-anchor → 全部去重引用 | ✅ §9 Slice 1 test assertions | 充分 |
| Single-anchor → 无多余分隔符 | ✅ §9 "Add or preserve a single-anchor assertion" | 充分 |
| Duplicate anchors → 不重复渲染 | ⚠️ §10 提到但未指定显式测试 | **Finding F1** |
| Multi-anchor 不产生额外 `> 📎 证据` 行 | ✅ §10 | 充分 |

### Finding F1: Duplicate anchor 测试路径未明确要求为独立 test case

**严重度**: LOW（不阻塞，建议补充）

**描述**: Plan §10 提到 "Duplicate anchors do not render twice" 作为 failure path，但 §9 的 exact changes 和 test assertions 部分没有要求实现 agent 编写一个显式的 duplicate anchor test case。当前 `_render_tracking_error_segment` 已在调用 `_item_rule_evidence_bullet` 前通过 `_dedupe_anchors` 去重，但 `_item_rule_evidence_bullet` 本身按 plan §9 应 "call `_dedupe_anchors(anchors)` inside `_item_rule_evidence_bullet` to make the helper self-contained"。如果实现 agent 只在 `_item_rule_evidence_bullet` 内部去重而不编写 duplicate anchor 测试，则自包含性缺乏回归保护。

**建议**: 在 §9 Slice 1 的 test assertions 中增加一条："Add a test that passes duplicate anchors to `_item_rule_evidence_bullet` directly (or via a segment that receives pre-duplicated anchors) and asserts the output contains no repeated reference text."

**Owner**: Implementation agent 在实现时补充；plan 本身不阻塞。

## 6. RR-13 和 repo-audit 排除

**结论：正确。**

- Plan §5 non-goals 明确："不处理 RR-13 duplicate `016492`"、"不发布、修改或 stage `docs/repo-audit-20260521.md`"。
- `docs/repo-audit-20260521.md` 当前仍是 untracked file，control doc Startup Packet 和 Active Residuals 均保持 excluded。
- RR-13 保持 human-owned（control doc Active Residuals: "User / App source"）。

**不阻塞。**

## 7. 其他审查点

### 7.1 `_dedupe_anchors` 自包含性

Plan §9 建议在 `_item_rule_evidence_bullet` 内部调用 `_dedupe_anchors` 使 helper self-contained。这是好的防御性设计。当前 `_render_tracking_error_segment` 已在外部去重，但其他调用点（如 `_render_index_constituents_segment`、`_render_manager_philosophy_segment`）传入的是单个 `ExtractedField.anchors`，理论上不包含重复。自包含去重是低成本保险。

### 7.2 标点格式

Plan §7 提到输出格式 `- 证据边界：年报2024§...；年报2024§...。`。当前 `_body_anchor_reference` 返回值不带尾部标点，`；` 连接后追加 `。` 是安全的。如果未来 anchor 描述本身包含 `；`，可能造成解析歧义，但当前 fixture 和实际数据中不存在此情况，属于 residual risk。

### 7.3 Fixture 充分性验证

从代码事实看，`_bundle(fund_type='enhanced_index')` 的 `benchmark.anchors` 产生 1 个 anchor（§2/benchmark），`_rabc()` 的 anchors 产生 2 个 anchor（§3/nav_benchmark_performance, §2/fee_schedule）。跟踪误差段落合并后有 3 个 distinct anchors，足以验证 multi-anchor 行为。但需注意 §9 Slice 1 stop condition 第 3 条已覆盖："Tests reveal current fixtures do not contain at least two distinct anchors for a multi-anchor segment; controller should decide whether to extend fixture data or pick another slice."

## Residual Risks

| Risk | Blocking? | Note |
|---|---|---|
| Multi-anchor 行过长 | No | 当前 fixture anchors 短；real data 可能更长。Plan 已裁决不做 truncation。 |
| Anchor 描述含分隔符标点 | No | 当前 `_body_anchor_reference` 输出不含 `；`；低概率。 |
| 未来 ITEM_RULE 新增需同步更新 multi-anchor 测试 | No | Plan §14 已记录。 |

## Findings Summary

| # | Severity | Finding | Action |
|---|---|---|---|
| F1 | LOW | Duplicate anchor 测试路径未明确要求为独立 test case | Implementation agent 补充；不阻塞 plan |

## Conclusion

Plan 可接受，implementation agent 可直接执行。F1 为建议性 finding，实现时补充 duplicate anchor 测试用例即可。
