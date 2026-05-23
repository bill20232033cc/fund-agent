# Post-P12-S2 Follow-up Plan Review — AgentGLM（2026-05-22）

- **Reviewer**: AgentGLM
- **Review target**: `docs/reviews/post-p12-s2-follow-up-planning-20260522.md`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Cross-references**: P12-S1 controller judgment, P12-S2 controller judgment, repo-audit baseline
- **Git base verified**: `ba77e02` = `docs: accept P11-S2 summary dedupe`，确认为 P11-S2 accepted baseline
- **Output only**: 本 artifact 只做 review；不修改 plan/source/test/control doc，不 commit/push/PR

---

## Verdict

**PASS_WITH_FINDINGS**

Plan 的战略判断正确、证据充分、residual 分配合理。Findings 均为 LOW 级别的 scope 描述精确度问题和 MEDIUM 级别的 branch/PR reconciliation 推荐不够明确。无阻断性 finding。

---

## Challenge 1: P12 是否应该关闭功能开发进入 aggregate deepreview

**结论：正确。**

Plan 的论证链路成立：

1. **P12 goal 收口明确**。Control doc P12 Current Phase Notes 定义 P12 goal 为"让 ITEM_RULE deterministic compliance 在 final renderer/audit path 中 observable"。这决定了 P12 的最小闭环是 renderer 决策生成 + C2 审计消费 + 证据边界展示，而非补齐所有指数基金数据。
2. **P12-S1/S2 已完成 goal 的最小闭环**。P12-S1 让 renderer 从 `classified_fund_type` + `facets=()` 生成 ITEM_RULE decisions/context，确定性段落只在目标章节 body 渲染，C2 消费同一 decisions/context 验证 compliance（controller judgment 确认）。P12-S2 让 `_item_rule_evidence_bullet()` 渲染全部去重锚点（controller judgment 确认）。
3. **继续开新 slice 会改变 phase 性质**。Tracking-error、指数编制方法、成分股抽取涉及新数据源、日频序列、计算口径、schema、缓存和审计。这些属于新数据能力，不是 ITEM_RULE deterministic compliance 的闭环补丁。Plan 的第一性原理分析（section 1）准确识别了这一边界。
4. **Candidate comparison table 完整**。7 个 candidate 均有 Fit / Product-safety / Scope / Decision 栏位，裁决逻辑可追溯。Defer 和 Keep human-owned 的理由均为已记录的 control doc 事实。

无 finding。

---

## Challenge 2: 显式 base `ba77e02..HEAD` 是否正确、充分

**结论：正确且充分，有 2 个 LOW 级别 scope 描述精确度问题。**

### 验证结果

| 检查项 | 结果 |
|--------|------|
| `ba77e02` commit 消息 | `docs: accept P11-S2 summary dedupe` ✅ 与 plan 描述一致 |
| `ba77e02..HEAD` commit 数量 | 7 个，全部为 P12 commits ✅ |
| P12 accepted commits 列表 | `79fb3e3`, `aad094f`, `c757036`, `617ca58`, `a9c1ac5`, `24a35b4`, `c44f063` — 与 git log 完全匹配 ✅ |
| 非 P12 commit 泄入 | 无 ✅ |
| `docs/repo-audit-20260521.md` 在 diff 中 | 不在 ✅ |
| RR-13 source data 在 diff 中 | 不在 ✅ |

### 实际 diff 文件清单（去重 docs/reviews/）

```
docs/implementation-control.md
fund_agent/fund/README.md
fund_agent/fund/audit/audit_programmatic.py
fund_agent/fund/template/__init__.py
fund_agent/fund/template/item_rules.py
fund_agent/fund/template/renderer.py
tests/README.md
tests/fund/audit/test_audit_programmatic.py
tests/fund/template/test_renderer.py
```

### Findings

**F1 (LOW): scope 描述多列 `test_item_rules.py`**

Plan section 6 将 `tests/fund/template/test_item_rules.py` 列为 P12 diff 预期文件，但该文件不在 `ba77e02..HEAD` diff 中。实际 diff 只有 `test_renderer.py` 和 `test_audit_programmatic.py` 两个测试文件。

影响：aggregate reviewer 按 plan scope 检查时可能误以为 `test_item_rules.py` 应包含 P12 变更。建议在 aggregate review 时以实际 `git diff --name-only ba77e02..HEAD` 为准，section 6 列表作为参考但不作为精确 scope 真源。

**F2 (LOW): scope 描述漏列 `__init__.py`**

Plan section 6 未提及 `fund_agent/fund/template/__init__.py`，但该文件在 P12 diff 中（可能因 P12-S1 的 `item_rules` 导出变更）。

影响：低。`__init__.py` 变更通常是 re-export 调整，aggregate reviewer 不会因此遗漏重要逻辑。但精确 scope 描述应包含此文件。

---

## Challenge 3: Aggregate review scope、validation、stop conditions、branch/PR reconciliation

### Scope

Plan section 6 的 focus questions 覆盖了关键审计维度：ITEM_RULE 决策单一来源、fail-closed 路径、chapter-scoped marker 语义、FQ5 不变、boundary 不越界。Explicit exclusions 清晰排除了 repo-audit、RR-13 和非 P12 hygiene。

评估：scope 定义质量高，focus questions 可直接作为 aggregate review checklist。

### Validation

Plan section 7 的验证命令组合理：
- Targeted template/audit suite
- Adjacent extraction-score/quality-gate suite
- Ruff lint
- Full suite with baseline `403 passed`

评估：验证充分。但建议 aggregate reviewer 额外运行 `git diff --stat ba77e02..HEAD` 以获得变更量概览。

### Stop conditions

Plan section 7 列出 5 个 stop conditions，覆盖意外 scope 泄入、renderer/audit 决策分歧、验证失败、reviewer 不可用和 branch/PR 状态不明。

评估：stop conditions 合理。特别是 reviewer 不可用的 stop condition（"必须 record limitation 或 ask user for risk exception"）与 P9-S2 的 reviewer limitation 教训一致。

### Branch/PR reconciliation

**F3 (MEDIUM): plan 提出 branch/PR reconciliation 问题但未给出推荐答案**

Plan section 4 和 section 9 都正确指出 P12 commits 已在 main 上，不存在 draft PR，controller 必须在 aggregate review 通过后 reconcile branch reality。但 plan 将此列为"open question"而非给出推荐。

根据项目既有 gateflow 模式（P10 经历了完整的 draft PR → PR review → squash merge via PR #6），P12 面临两种路径：

- **路径 A**：接受 main-branch closeout。承认 P12 以 main 直接提交方式完成，aggregate review 通过后直接标记 P12 closed，不创建 PR。适用条件：P12 不涉及产品行为变更（P12-S1/S2 只改变 renderer/audit 内部 compliance 逻辑，不改变用户可见报告语义）。
- **路径 B**：retroactively 创建 feature branch 和 PR。从 main 上切出 P12 commits 到新分支，然后在 main 上 revert，再走 draft PR 流程。成本高、风险大（已推送到远端的 main commit 需要 force push 或 revert commit）。

**推荐**：路径 A 更合理。理由：(1) P12 不改变 Service/UI/CLI 面向用户的行为；(2) P10 PR #6 的 squash merge 已将 main 置于干净基线，P12 在此之上是纯 Capability 内部 compliance 改进；(3) 路径 B 的 force push 或 revert 风险不值得。

建议 controller 在 aggregate review 通过后，输出一个 main-branch closeout artifact 记录这一决策理由，而非尝试发明一个不存在的 PR gate。

---

## Challenge 4: Residual owners 是否合理

**结论：合理，所有 residual 有明确 owner。**

| Residual | Plan 分配 | GLM 评估 |
|----------|-----------|----------|
| Real tracking-error extraction/calculation | Future extractor/calculation phase in Fund Capability | ✅ 正确归属。design.md §3.4 已列出"跟踪误差"为指数基金 `preferred_lens` 关注点，但当前无 extractor 支撑 |
| Real index methodology / constituents data | Future documents/extractor phase through `FundDocumentRepository` boundaries | ✅ 正确归属。需新 source 和 extraction design，属于独立的 documents/extractor 能力建设 |
| Evidence sufficiency / evidence-claim matching | Future E1/E2/E3 audit or Evidence Confirm work | ✅ 正确归属。design.md §5.2 明确 E1/E2/E3 为 v2 |
| Long-anchor truncation/grouping | Future evidence-display UX slice | ✅ 正确归属。当前 fixture 无 large anchor set |
| Future ITEM_RULE expansion dispatch/tests | The future slice that adds ITEM_RULEs | ✅ 正确归属。当前 4 条规则已覆盖 |
| Chapter-mismatch duplicate C2 noise | Future maintainability cleanup | ✅ 正确归属。fail-closed 行为不隐藏问题 |
| RR-13 duplicate `016492` | User / App source | ✅ 与 control doc Active Residuals 表一致 |
| `docs/repo-audit-20260521.md` | Controller / user; keep excluded/untracked | ✅ 与 control doc 一致；repo-audit 基于 P8 基线且当前 excluded |
| Repo-audit hygiene suggestions | Future repo/docs hygiene phase | ✅ 不阻塞 P12 closeout |

无 finding。

---

## Challenge 5: 是否违反 phaseflow/gateflow

**结论：未违反，但需注意 branch 状态处理。**

### Phaseflow 合规性

| 检查项 | 结果 |
|--------|------|
| Plan 是否在 main 上提交 | 是。但 plan artifact 是 output-only（section 1: "不改 source/test/README/control doc，不 commit、不 push、不建 PR"），不违反 gateflow |
| P12-S1/S2 是否有 accepted controller judgment | 是。两份 controller judgment 均 ACCEPTED，validation 记录完整 |
| Control doc gate 是否逐步推进 | 是。Startup Packet 从 `P11-S2 accepted` → `post-P11 planning` → `P12-S1 plan` → `P12-S1 accepted` → `post-P12-S1 planning` → `P12-S2 plan` → `P12-S2 accepted` → `post-P12-S2 planning`，gate 链路完整 |
| 是否有 skip gate | 无。每个 gate 都有 plan/review/implementation/code-review/controller-judgment 完整闭环 |

### Gateflow 分支处理

Plan section 9 和 section 4 正确识别了 P12 commits 已在 main 上的事实，并明确要求 controller reconcile。这与 F3 (MEDIUM) finding 一致：plan 应在 open question 旁附上推荐路径（main-branch closeout），而非仅记录问题。

**F4 (LOW): plan 非目标列表中"不更新 design.md 或 implementation-control.md"与实际 diff 矛盾**

Plan section 5 (Non-goals) 声明"Do not update `docs/design.md` or `docs/implementation-control.md` in this planning artifact"。但实际 P12 diff 包含 `docs/implementation-control.md`（因 P12-S1/S2 accepted 后 control doc 需要更新 Startup Packet 和 gate ledger）。

理解：这个 non-goal 是针对"本 follow-up planning artifact"自身的约束，不是对 P12 整体历史的约束。P12-S1/S2 的 accepted commits 确实更新了 control doc，而本 follow-up plan 不再额外更新。表述容易引起歧义但不是实质错误。

---

## Findings Summary

| # | 严重度 | Finding | 建议 |
|---|--------|---------|------|
| F1 | LOW | Scope section 6 多列 `test_item_rules.py`，不在实际 P12 diff 中 | Aggregate review 以 `git diff --name-only ba77e02..HEAD` 为 scope 真源 |
| F2 | LOW | Scope section 6 漏列 `fund_agent/fund/template/__init__.py` | Aggregate review 注意此文件变更 |
| F3 | MEDIUM | Branch/PR reconciliation 作为 open question 未附推荐路径 | 推荐 main-branch closeout artifact，不创建 retroactive PR |
| F4 | LOW | Non-gools "不更新 implementation-control.md" 表述易歧义 | 实质无影响，controller 可忽略 |

---

## Conclusion

Plan 正确推荐关闭 P12 功能开发并进入 aggregate deepreview。战略判断基于第一性原理，证据链完整，residual 分配合理。base commit `ba77e02` 经验证准确。Findings 均不阻断 aggregate review 启动，但 F3 建议 controller 在 aggregate review 通过后明确选择 main-branch closeout 路径而非尝试 retroactive PR。

**Verdict: PASS_WITH_FINDINGS (F1-F4, 0 blocking)**
