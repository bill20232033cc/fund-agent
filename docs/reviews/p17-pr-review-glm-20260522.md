# P17-S1 PR Review — GLM Independent Review (2026-05-22)

## Verdict

**PASS_WITH_FINDINGS**

PR #11 diff 与 accepted local artifacts 一致，tracking_error 实现满足 plan/aggregate review 要求，design.md v2.2 与 implementation-control.md 统一，PR body 准确描述了 scope、validation 和 residuals。无阻断性 finding。

---

## Review Scope

| Input | Role |
|---|---|
| PR #11 (`p17-tracking-error-thermometer-direction` → `main`) | 待审 PR |
| `docs/design.md` v2.2 diff | 设计真源变更 |
| `docs/implementation-control.md` v1.1 diff | 总控变更 |
| `fund_agent/fund/extractors/performance.py` diff | tracking_error 实现变更 |
| `tests/fund/extractors/test_performance.py` diff | 测试变更 |
| `docs/reviews/p17-s1-plan-review-controller-judgment-20260522.md` | 计划审查约束 |
| `docs/reviews/p17-s1-aggregate-deepreview-controller-judgment-20260522.md` | 聚合审查约束 |
| `docs/reviews/p17-s1-ready-to-open-draft-pr-reconciliation-20260522.md` | PR 就绪 reconciliation |
| `docs/reviews/thermometer-self-owned-design-direction-20260522.md` | 温度计方向裁决 |
| `AGENTS.md` | Agent 执行规则 |

Excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`。

---

## Finding 1: PR diff 与 accepted artifacts 一致性

**结论：一致。**

- 27 个变更文件中，25 个是 `docs/reviews/*` 或 design/control 文档，2 个是实际源码（`performance.py` + `test_performance.py`），加上 `README.md` 和 `tests/README.md` 的用户手册/测试手册更新。
- Excluded local drafts（`docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`）均未出现在 PR diff 中。`gh pr diff 11 --name-only` 验证通过。
- `docs/design-control-alignment-guide.md` 被包含在 PR 中，与 implementation-control 记录的 "accepted as a scoped alignment input, not as a replacement truth document" 一致。
- `git diff --check origin/main..HEAD` 通过，无空白或冲突标记问题。

---

## Finding 2: tracking_error 实现满足 plan/aggregate review 要求

**结论：满足。**

逐一核对 P17-S1 plan/review 和 aggregate review 的实现约束：

| 约束 | 实现状态 | 证据 |
|------|---------|------|
| 消除 stale `tracking_error_ambiguous` | ✅ 满足 | `grep -rn "tracking_error_ambiguous"` 全仓零命中 |
| 具体 fail-closed notes 替代通用模糊语义 | ✅ 满足 | 10 个具体 note 常量：target_or_limit、manager_narrative、benchmark_only、standard_deviation_only、mixed_actual_and_target、unparseable、incomplete_anchor、table_text_inconsistent、multi_match、missing |
| target-only 不早退，继续扫描后续直接披露 | ✅ 满足 | `_extract_tracking_error_from_text` 对 target/ambiguous 行仅追加 blocker_notes，不 break；测试 `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line` 验证 |
| mixed actual/target fail closed | ✅ 满足 | `_classify_tracking_error_target_context` 检测 actual keywords 后返回 `_TRACKING_ERROR_NOTE_MIXED_ACTUAL_AND_TARGET`；测试 `test_extract_performance_fails_closed_on_mixed_actual_target_tracking_error_text` 验证 |
| 多候选 table/text inconsistency | ✅ 满足 | `_select_consistent_tracking_error_match` 比较解析值；不一致返回 `None` 触发 `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT`；两个测试分别验证一致和不一致场景 |
| 表格级多候选 | ✅ 满足 | `_extract_tracking_error_from_tables` 检查 `len(matches) > 1` 返回 `_TRACKING_ERROR_NOTE_MULTI_MATCH`；测试 `test_extract_performance_marks_table_level_multiple_tracking_error_matches` 验证 |
| §2 fallback | ✅ 满足 | `_extract_tracking_error_from_text` 按 `("§3", "§2")` 顺序迭代；测试 `test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` 验证 |
| 直接披露契约保持 | ✅ 满足 | 成功命中时返回 `extraction_mode="direct"`、`source_type="direct_disclosure"`、`calculation_method="disclosed"`、`provenance_note` 不变 |
| blocker 优先级排序 | ✅ 满足 | `_TRACKING_ERROR_BLOCKER_PRECEDENCE` 元组定义了从最严重到最不严重的固定顺序 |
| manager/benchmark note 可达性 | ✅ 满足 | `_classify_tracking_error_nonmatch_context` 和 `_classify_tracking_error_line_without_parseable_value` 两个分类路径均能生成 manager_narrative 和 benchmark_only note |

---

## Finding 3: design.md v2.2 与 implementation-control.md 统一

**结论：统一。**

### 温度计口径

design.md v2.2 §1.3 明确三件事：

1. 当前有知有行公开页抓取是**过渡能力**（"不把当前有知有行公开页面抓取视为长期温度计真源"）
2. 后续应开发项目内**自建温度计**（"后续应在本项目内开发自建温度计计算与数据契约"）
3. 自动映射 `valuation_state` 仍需**独立规则设计**（"映射阈值、适用范围、证据来源和缺失策略必须单独设计并通过 gate"）

implementation-control §"2026-05-22 Thermometer Self-Owned Direction" 精确反映这三点：
- "`docs/design.md` is updated to v2.2"
- "Current code remains a read-only `ThermometerService`"
- "Future self-owned thermometer work must define market/index coverage, source datasets, formulas..."
- "Automatic thermometer-to-`valuation_state` mapping remains a separate design problem"

**关键检查**：PR 没有把温度计未来方向误写成当前已实现。design.md §6.3 表格中 "自建温度计（后续方向）" 行的 "代码位置" 列写的是 "待后续 phase"。✅

**关键检查**：PR 没有建议立即自动映射 valuation_state。design.md §6.3 新增段落明确写道 "即使自建温度计落地，也不得默认把温度计数值自动映射为买入前检查清单的 `valuation_state`"。✅

### §9 CLI 命令清单

design.md §9.0 新增 8 个 CLI 命令的当前状态表，与 `fund_agent/ui/cli.py` 实现一致。`checklist` 标记为 "占位"。✅

### §11 Plan Review 设计边界检查

design.md §11 新增的 5 项检查清单与 implementation-control Resume checklist 中 "future plan reviews must include design-boundary checks" 一致。✅

### 版本引用

implementation-control header 和 Design / Control Alignment Rules 均引用 `docs/design.md (v2.2)`。✅

---

## Finding 4: PR body 准确性

**结论：准确。**

| PR body 声明 | 验证 |
|-------------|------|
| "harden tracking_error direct-disclosure extraction with explicit fail-closed notes" | `performance.py` 新增 10 个具体 note 常量和优先级排序 ✅ |
| "add focused tests for target/limit, mixed actual/target, manager narrative, benchmark-only, standard-deviation-only, unparseable, multi-match, table/text inconsistency, table multi-match, section 2 fallback, and blocker continuation" | `test_performance.py` 新增/修改 12 个 tracking-error 相关测试覆盖所有场景 ✅ |
| "reconcile design/control docs so thermometer public-page query is transitional" | design.md v2.2 §1.3 和 §6.3 已更新 ✅ |
| "no production golden rows or selected CSV/RR-13 changes" | PR 文件列表无 golden JSON 或 CSV 文件 ✅ |
| "no Service/UI/Runtime/Engine/source orchestration/document adapter/PDF/cache helper changes" | PR 仅修改 `performance.py`（Capability 层 extractor）✅ |
| "no Dayu runtime, LLM audit, Evidence Confirm, calculated tracking error, or external index series introduced" | diff 无此类变更 ✅ |
| "excluded local drafts are not included" | `gh pr diff 11 --name-only` 验证无 excluded 文件 ✅ |

---

## Finding 5: 未使用常量

**严重程度：低**

`_TRACKING_ERROR_NOTE_INCOMPLETE_ANCHOR` 在 `performance.py` 第 67 行定义，并在 `_TRACKING_ERROR_BLOCKER_PRECEDENCE`（第 74 行）中列出，但当前无任何分类函数会赋值此 note。这是前向预留常量 / 死代码。

**建议**：保留但不阻塞——此常量不参与任何运行时决策路径，且如果未来出现 anchor 不完整的场景可以立即使用。如果后续清理 pass 选择移除，影响为零。

---

## Residual Risks

| 风险 | 归属 | 说明 |
|------|------|------|
| Production `tracking_error` golden rows 仍被 blocked | Future golden gate | `001548` 和 P16 五只增强指数候选仍需直接观测披露证据 |
| 未来自建温度计需要独立设计/实现 phase | Future phase | 当前仅记录方向，无代码变更 |
| 未来 temperature-to-valuation_state 映射需要独立 gate | Future gate | 当前明确为非目标 |
| `_TRACKING_ERROR_NOTE_INCOMPLETE_ANCHOR` 未使用 | Low / future pass | 不影响运行时行为 |
| P17-S1 aggregate review 记录的 low-risk note 精度和测试 residuals | Future pass | 已由 controller 接受并分配归属 |
| Repo-hygiene 候选 D-1 / D-8-C5 / C-9 | Future phase | 不在本 PR scope |

---

## Validation Reviewed

| 验证项 | 状态 |
|--------|------|
| `git diff --check origin/main..HEAD` | 通过（无空白/冲突标记） |
| Excluded drafts 不在 PR diff | 通过 |
| Stale `tracking_error_ambiguous` 全仓零命中 | 通过 |
| design.md v2.2 版本引用一致性 | 通过 |
| implementation-control design truth 指向 v2.2 | 通过 |
| 温度计未来方向未误写成当前已实现 | 通过 |
| valuation_state 自动映射未声称已实现 | 通过 |
| 无 golden/CSV/RR-13/Service/UI/Engine/外部数据变更 | 通过 |

---

## Controller Follow-up Needed

无。本 PR 无阻断性 finding，所有 finding 均为低优先级或信息级别。

如果 controller 接受本 review，下一步是用户授权 draft PR gate 后 push 和创建 draft PR。
