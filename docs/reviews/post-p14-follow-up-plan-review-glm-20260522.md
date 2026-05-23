# Post-P14 Follow-up Planning Review — AgentGLM（2026-05-22）

## Verdict

**PASS_WITH_FINDINGS**

该 artifact 是一份结构完整、scope 清晰、边界正确的 next-phase selection 文档。推荐 P15-S1 production tracking_error golden evidence plan-review 作为下一 gate 的决策与 design.md / implementation-control.md 的目标一致；候选项比较覆盖了所有 control doc 已知 residuals；non-goals 显式排除了 scope creep 风险项；stop condition、evidence requirements、success signals 和 residual owners 均有明确定义；handoff prompt 为下一份 plan artifact 提供了 code-generation-ready 级别的指令。

以下 3 个 finding 均为 low / informational severity，不阻断 acceptance。

---

## Lens 1: 推荐下一 gate 是否是最佳下一步

**结论：是。**

artifact 推荐 `P15-S1 production tracking_error golden evidence plan-review`，与 design.md 和 implementation-control.md 的目标完全对齐：

- design.md 第 3.4 节 preferred_lens 明确将「跟踪误差」列为指数基金和指数增强基金的优先分析视角（design.md L133-136）。
- design.md 第 7 节 quality gate 体系要求 golden answer pipeline 提供可复核基准（design.md L389-390）。
- P14 已把 `tracking_error` 纳入条件化 P1 质量分母（control doc P14 archive），但 production golden correctness 仍无真实基金行。
- artifact baseline 正确引用 P14 最后验证 `428 passed`、PR 9 squash-merged at `746bfda`，与 control doc startup packet 一致。

从 first-principles 角度：P13 建立了 direct-disclosure extraction path，P14 把该字段纳入 quality denominator 并补齐了 `index_profile` production golden。最小残余缺口就是 `tracking_error` production golden correctness。选择关闭这个缺口而不是扩大到 methodology/constituents、external adapter、QDII subtype 或 E1-E3 是正确的优先级判断。

artifact L70 明确表述了核心设计问题："Can the current deterministic path be locked by production evidence?" 这与 design.md「证据可审计」原则和 deterministic MVP 主链路设计一致。

---

## Lens 2: 候选项比较是否充分

**结论：充分。**

artifact 候选项表格（L42-51）覆盖了 8 个候选项，与 control doc Active Residuals（L122-133）的已知 residuals 完全对应：

| Control doc residual | Artifact 候选项 | 覆盖 |
|---|---|---|
| RR-13 duplicate `016492` | RR-13 duplicate `016492` — exclude | ✓ |
| `docs/repo-audit-20260521.md` excluded | repo-hygiene candidates — exclude | ✓ |
| Future tracking-error / index methodology / constituents | methodology / constituents extraction — defer | ✓ |
| Future E1-E3 / Evidence Confirm | E1-E3 / Evidence Confirm — defer | ✓ |
| Future evidence-display / ITEM_RULE cleanup | evidence-display / ITEM_RULE cleanup — defer | ✓ |
| Repo-hygiene D-1/D-8/C-5/C-9 | repo-hygiene candidates — exclude | ✓ |

此外 artifact 还补充了 control doc residuals 中未单独立项但 P14 context 合理推导出的候选项：
- calculated tracking error / external index series adapter
- QDII tracking-error subtype applicability

每个候选项都有 product value 评估、scope/boundary risk 评估和明确的 defer/exclude 决策及理由。比较逻辑清晰：先关闭同源最小正确性缺口，再扩展到新架构或更广业务策略。

---

## Lens 3: 是否有 scope creep

**结论：无 scope creep。**

artifact non-goals（L86-96）显式排除了以下范围外项目：

- 不实施本 phase ✓
- 不添加 calculated tracking error、external index series adapter ✓
- 不添加 methodology / constituents extraction 或新 document source contract ✓
- 不重新设计 QDII subtype ✓
- 不引入 E1-E3、Evidence Confirm、LLM writing、semantic audit、Dayu runtime ✓
- 不修改 ExtractionMode、snapshot schema、quality gate severity ✓
- 不使用 benchmark-only evidence 作为 proof ✓
- 不修改 RR-13 或 source CSV ✓
- 不触碰 `docs/repo-audit-20260521.md` ✓
- 不更新 design.md 或 implementation-control.md ✓

scope 定义为纯 plan-review gate：调查现有 production selected-fund 是否有 reviewed direct tracking_error disclosure evidence，如有则规划 golden row 添加，如无则记录 blocker。这完全符合 phase selection artifact 的定位。

handoff prompt（L139-161）的 do-not-modify 列表同样完备，且明确拒绝 criteria（L155-161）覆盖了六种越界场景。

---

## Lens 4: stop condition、evidence requirements、success signals、residual owners

**结论：完整。**

**Stop condition**:
- L68: "stop before implementation if no production reviewed direct tracking_error evidence can be proven"
- L101-102: Risk table 第 1 行明确覆盖 "No current production selected fund has reviewed direct tracking_error disclosure evidence" → "Plan must stop and record blocker"
- L135-136: Implementation success 只有两个合法结局：golden rows 添加并验证，或证明无可用 evidence 并记录 blocker 路由下一 phase

**Evidence requirements**:
- L64: 要求 exact fund code, year, annual-report section/table/row evidence anchor, field_name, sub_field, expected_value, confidence, source text
- L119: Success signals 再次要求 exact evidence source for each proposed row
- L120: exact golden records: field_name=tracking_error, sub-field names, expected values, confidence, source strings
- L103-104: Risk table拒绝仅由 benchmark text 间接支持的 expected value

**Success signals**（L116-135）:
- code-generation-ready instructions for implementation agents
- exact evidence source、golden records、P13/P14 extraction path proof
- file ownership (golden reviewed markdown/JSON/template, golden prefill/tests, docs/tests artifacts)
- validation commands: targeted golden tests, extraction score tests, sample matrix regression, strict JSON schema, ruff, full pytest, git diff --check

**Residual owners**（Risk table L99-112）:
- 每个 deferred item 都有明确的 owner/destination 和 handling 说明
- 与 control doc Active Residuals owner 分配一致

---

## Lens 5: code-generation readiness for P15-S1 plan artifact

**结论：足够 code-generation-ready。**

handoff prompt（L139-152）提供了：
- 明确的 gate 名称和 input/output artifact 路径
- 完整的 do-not-modify 清单
- 二元决策框架（有 evidence → 规划 golden rows；无 evidence → blocker record）
- 六条 plan-review rejection criteria（L155-161）

success signals 中的 validation commands（L123-130）提供了实现阶段验收标准：
- targeted golden prefill / golden answer tests
- targeted extraction snapshot / score tests
- sample matrix regression for direct disclosure fixture
- strict golden JSON schema validation
- `ruff check fund_agent tests`
- full `pytest` with no regression from `428 passed`
- `git diff --check HEAD`

这些足以让 P15-S1 plan agent 产出一份结构化、可 review 的 plan artifact。

---

## Findings

### F1 — Low: 混合语言排版不一致

**位置**: artifact L79

**证据**: "keeps root cause and evidence source同源, using annual-report evidence rather than an external adapter"

**问题**: 英文句子中间出现中文字符「同源」无分隔，不构成语法或语义错误但降低 handoff prompt 的可读性。下游 plan agent 可能源自不同语言背景，混合排版可能造成解析歧义。

**建议**: 改为 "keeps root cause and evidence source co-located (同源)" 或统一为英文表述。

### F2 — Low: 未显式提名 `001548` 为首选候选基金

**位置**: artifact L36, L62-68

**证据**: artifact baseline 正确记录 "reviewed `001548` `index_profile` golden rows were added; no production `tracking_error` golden rows were added"（L33），但 scope 和 handoff prompt 未显式建议 `001548` 作为 tracking_error golden 的首选候选基金。

**问题**: `001548` 是当前唯一已有 reviewed production golden rows 的指数基金，其年报很可能也包含 direct tracking_error disclosure。显式提名可以减少 plan agent 的发现成本，并提前暴露 "001548 年报是否确有 tracking_error 直接披露" 这一关键不确定性。

**建议**: 在 scope 或 handoff prompt 中加入一行："`001548` is the primary candidate given its existing reviewed `index_profile` golden rows; verify whether its annual report contains direct `tracking_error` disclosure."

### F3 — Informational: `enhanced-index production golden expansion` 残余项未在 control doc Active Residuals 中单独立项

**位置**: artifact L36 vs control doc L122-133

**证据**: artifact open residuals 包含 "enhanced-index production golden expansion"，但 control doc Active Residuals 表中未将此项作为独立行追踪。control doc P14 archive 提到 `161725` enhanced-index fixture 覆盖了 direct disclosure path，但未显式将 "enhanced-index production golden expansion" 标记为 open residual。

**问题**: 如果 P15-S1 被接受，control doc Active Residuals 需要同步更新以反映此残余项，否则后续 phase 可能丢失追踪。

**建议**: 接受此 artifact 时，在 control doc reconciliation 中显式添加 "enhanced-index production golden expansion" 到 Active Residuals。

---

## Summary

该 artifact 是一份高质量的 next-phase selection 文档。推荐 P15-S1 production tracking_error golden evidence plan-review 的决策正确，候选项比较充分，scope 无 creep，stop condition / evidence requirements / success signals / residual owners 定义完整，handoff prompt 足够 code-generation-ready。3 个 finding 均为 low / informational severity，不阻碍 acceptance。

**Reviewer**: AgentGLM
**Date**: 2026-05-22
**Artifact reviewed**: `docs/reviews/post-p14-follow-up-planning-20260522.md`
**Design truth**: `docs/design.md`
**Control truth**: `docs/implementation-control.md`
