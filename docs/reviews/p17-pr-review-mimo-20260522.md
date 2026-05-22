# P17-S1 PR Review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

PR #11 核心实现与已接受的 P17-S1 aggregate deepreview scope 一致，tracking_error extractor hardening 满足全部 plan success signals，design.md v2.2 与 implementation-control.md 统一口径正确（当前公开页温度计是过渡实现，未来 self-owned thermometer 是方向，valuation_state 自动映射仍需单独 gate），PR body 准确描述 scope/validation/residuals。无 blocking finding。CI `test` 通过。

发现 1 个 low-severity finding：PR 缺少 3 个已接受的 review artifact 文件（aggregate deepreview controller judgment + independent reviews + thermometer direction），需 push 更新。

## Reviewed Artifacts

| Artifact | Role |
|---|---|
| PR #11 body | PR scope/validation/residuals |
| PR #11 diff (28 files) | Actual PR content |
| `docs/reviews/p17-s1-aggregate-deepreview-mimo-20260522.md` | Accepted aggregate review baseline |
| `docs/reviews/p17-s1-aggregate-deepreview-controller-judgment-20260522.md` | Controller judgment baseline |
| `docs/reviews/p17-s1-ready-to-open-draft-pr-reconciliation-20260522.md` | PR inclusion/exclusion reconciliation |
| `docs/reviews/thermometer-self-owned-design-direction-20260522.md` | Thermometer design direction |
| `docs/design.md` v2.2 | Design truth |
| `docs/implementation-control.md` v1.1 | Control truth |
| `fund_agent/fund/extractors/performance.py` | Production extractor |
| `tests/fund/extractors/test_performance.py` | Focused tests |

## 1. PR Diff 与 Accepted Local Artifacts 一致性

### 1.1 Core Implementation 一致性

| 检查项 | 结果 | 证据 |
|---|---|---|
| `performance.py` diff 与 aggregate review 一致 | ✅ | aggregate review 验证 `d069862..2327309` 范围内仅 touch `performance.py` + `test_performance.py` + `tests/README.md`；PR 包含同一 `performance.py` diff |
| `test_performance.py` diff 与 aggregate review 一致 | ✅ | 22 个测试（含 16 个 tracking_error 相关）全部在 PR 中 |
| `tests/README.md` 同步 | ✅ | README 描述与实际测试一致 |
| 无 production golden rows | ✅ | `reports/golden-answers/` 未修改 |
| 无 CSV/RR-13 修改 | ✅ | 无 CSV 或 RR-13 文件变更 |
| 无 Service/UI/Runtime/Engine 改动 | ✅ | 仅 Capability 层 extractor |

### 1.2 Excluded Drafts 检查

| Excluded File | 在 PR 中？ |
|---|---|
| `docs/design0522.md` | ❌ 不在 PR ✅ |
| `docs/implementation-control0522.md` | ❌ 不在 PR ✅ |
| `docs/repo-audit-20260521.md` | ❌ 不在 PR ✅ |

### 1.3 PR 包含文件完整性

PR 包含 28 个文件。与 readiness artifact（`db63f19`，期望 31 个文件）对比：

| 文件 | 在 PR 中？ | 说明 |
|---|---|---|
| `README.md` | ✅ | |
| `docs/design-control-alignment-guide.md` | ✅ | |
| `docs/design.md` | ✅ | |
| `docs/implementation-control.md` | ✅ | |
| `fund_agent/fund/extractors/performance.py` | ✅ | |
| `tests/README.md` | ✅ | |
| `tests/fund/extractors/test_performance.py` | ✅ | |
| `docs/reviews/design-alignment-review-20260522.md` | ✅ | |
| `docs/reviews/design-alignment-review-controller-judgment-20260522.md` | ✅ | |
| `docs/reviews/design-alignment-review-glm-20260522.md` | ✅ | |
| `docs/reviews/design-alignment-review-mimo-20260522.md` | ✅ | |
| `docs/reviews/post-p16-follow-up-plan-review-controller-judgment-20260522.md` | ✅ | |
| `docs/reviews/post-p16-follow-up-plan-review-glm-20260522.md` | ✅ | |
| `docs/reviews/post-p16-follow-up-plan-review-mimo-20260522.md` | ✅ | |
| `docs/reviews/post-p16-follow-up-planning-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-implementation-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-code-review-controller-judgment-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-code-review-glm-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-code-review-mimo-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-plan-review-controller-judgment-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-plan-review-glm-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-plan-review-mimo-20260522.md` | ✅ | |
| `docs/reviews/p17-s1-aggregate-deepreview-controller-judgment-20260522.md` | ❌ **缺失** | 已在本地 commit `2327309` |
| `docs/reviews/p17-s1-aggregate-deepreview-glm-20260522.md` | ❌ **缺失** | 已在本地 commit `2327309` |
| `docs/reviews/p17-s1-aggregate-deepreview-mimo-20260522.md` | ❌ **缺失** | 已在本地 commit `2327309` |
| `docs/reviews/p17-s1-ready-to-open-draft-pr-reconciliation-20260522.md` | ❌ **缺失** | 已在本地 commit `2b34713` / `d5f49a6` |
| `docs/reviews/thermometer-self-owned-design-direction-20260522.md` | ❌ **缺失** | 已在本地 commit `8d73e3a` |

**缺失 3 个 review artifact 文件**（见 Finding F1）。核心实现和文档文件完整。

## 2. Tracking Error 实现审查

### 2.1 Fail-closed Notes（10 种）

| Note 常量 | 定义位置 | 测试覆盖 | 状态 |
|---|---|---|---|
| `tracking_error_target_or_limit` | `performance.py:61` | `test_extract_performance_does_not_treat_tracking_error_target_as_observed` | ✅ |
| `tracking_error_manager_narrative` | `performance.py:62` | `test_extract_performance_marks_manager_tracking_error_narrative_with_specific_note` | ✅ |
| `tracking_error_benchmark_only` | `performance.py:63` | `test_extract_performance_marks_benchmark_only_tracking_error_with_specific_note` | ✅ |
| `tracking_error_standard_deviation_only` | `performance.py:64` | `test_extract_performance_does_not_use_standard_deviation_as_tracking_error` | ✅ |
| `tracking_error_mixed_actual_and_target` | `performance.py:65` | `test_extract_performance_fails_closed_on_mixed_actual_target_tracking_error_text` | ✅ |
| `tracking_error_unparseable` | `performance.py:66` | `test_extract_performance_marks_unparseable_direct_tracking_error_with_specific_note` | ✅ |
| `tracking_error_incomplete_anchor` | `performance.py:67` | 无直接测试（aggregate review 已接受为 residual） | ⚠️ residual |
| `tracking_error_table_text_inconsistent` | `performance.py:68` | `test_extract_performance_marks_table_text_conflicting_tracking_error_as_inconsistent` | ✅ |
| `tracking_error_multi_match` | `performance.py:69` | `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note` + table-level test | ✅ |
| `年报未直接披露跟踪误差` | `performance.py:70` | 通过 `_TRACKING_ERROR_NOTE_MISSING` 在 missing 路径隐式覆盖 | ✅ |

Blocker precedence 元组 `performance.py:71-82` 包含全部 10 种，顺序正确。

### 2.2 Target/Mixed 不早退

| 路径 | 机制 | 验证 |
|---|---|---|
| Table path (`performance.py:510-512`) | `blocker_notes.append(...)` + `continue`（不 return） | `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line` ✅ |
| Text path (`performance.py:566-568`) | `blocker_notes.append(...)` + `continue`（不 return） | `test_extract_performance_accepts_direct_tracking_error_after_earlier_mixed_target_line` ✅ |

### 2.3 Multi-match / Table-text Inconsistency / §2 Fallback

| 场景 | 机制 | 验证 |
|---|---|---|
| Table multi-match | `performance.py:525-526` → `_TRACKING_ERROR_NOTE_MULTI_MATCH` | `test_extract_performance_marks_table_level_multiple_tracking_error_matches` ✅ |
| Text multi-match | `performance.py:582-583` → `_TRACKING_ERROR_NOTE_MULTI_MATCH` | `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note` ✅ |
| Table/text inconsistency | `performance.py:416` → `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT` | `test_extract_performance_marks_table_text_conflicting_tracking_error_as_inconsistent` ✅ |
| §2 fallback | `performance.py:550` 迭代 `("§3", "§2")` | `test_extract_performance_falls_back_to_section_two_tracking_error_when_section_three_missing` ✅ |

### 2.4 直接披露契约保持

成功路径 `performance.py:425-450`：
- `source_type="direct_disclosure"` ✅
- `calculation_method="disclosed"` ✅
- `frequency="annual_report_period"` ✅
- `provenance_note="年报§3直接披露的实际跟踪误差..."` ✅
- `row_locator="tracking_error"` ✅

`test_extract_performance_outputs_direct_tracking_error_when_disclosed` 验证全部字段。

### 2.5 Stale `tracking_error_ambiguous` 清除

`grep -rn "tracking_error_ambiguous" --include="*.py" .` 无输出。旧 `_has_ambiguous_tracking_error_text` 调用已移除。✅

## 3. Design.md v2.2 与 Implementation-control.md 统一性

### 3.1 温度计口径统一

| 检查项 | design.md v2.2 | implementation-control.md | 一致？ |
|---|---|---|---|
| 当前温度计是过渡实现 | §6.3 "当前温度计能力通过 ThermometerService...只做有知有行公开页只读查询与缓存复用。这是过渡实现" | "Thermometer Self-Owned Direction" 章节 "current code remains a read-only ThermometerService...query with cache over the public page" | ✅ |
| 未来 self-owned thermometer 是方向 | §6.3 "后续应开发项目内自建温度计能力" + §1.3 非目标措辞 | "User decision: the project should develop its own thermometer capability" | ✅ |
| valuation_state 自动映射仍需单独 gate | §1.3 "不把温度计数值隐式自动映射为 valuation_state...必须单独设计并通过 gate" + §6.3 "即使自建温度计落地，也不得默认把温度计数值自动映射" | "Automatic thermometer-to-valuation_state mapping remains a separate design problem" | ✅ |
| README 非目标对齐 | N/A | README.md: "温度计数据不自动映射为 analyze --valuation-state"（从"尚未接入"改为"明确非目标"） | ✅ |

### 3.2 设计真源引用

- `implementation-control.md` header: `设计真源: docs/design.md (v2.2)` ✅
- `implementation-control.md` Design truth 字段: `docs/design.md (v2.2)` ✅
- `implementation-control.md` Design/Control Alignment Rules: `docs/design.md (v2.2) remains the design truth` ✅

### 3.3 §11 Plan Review 设计边界检查

`docs/design.md` §11 已添加，要求后续 plan review 显式检查非目标、边界、年报访问路径、禁止引入项、success signal 可验证性。✅

## 4. PR Body 审查

| 检查项 | 评估 |
|---|---|
| Summary 是否准确描述 scope | ✅ 三部分（hardening + tests + docs alignment）准确 |
| Validation 命令是否完整 | ✅ 5 个验证命令覆盖 target/adjacent/full pytest + ruff + diff check |
| Scope notes 是否准确 | ✅ 明确列出不包含的内容（golden rows, CSV/RR-13, Service/UI/Runtime/Engine, Dayu/LLM/Evidence Confirm） |
| Excluded drafts 是否声明 | ✅ 明确声明 3 个 excluded local drafts |
| CI 状态 | ✅ `test` workflow SUCCESS |

## 5. Findings

### F1 (LOW): PR 缺少 3 个已接受的 review artifact 文件

**文件**: `docs/reviews/p17-s1-aggregate-deepreview-controller-judgment-20260522.md`, `docs/reviews/p17-s1-aggregate-deepreview-glm-20260522.md`, `docs/reviews/p17-s1-aggregate-deepreview-mimo-20260522.md`

**问题**: PR commit 列表截止到 `d5f49a6`（11 commits），但本地 `origin/main..HEAD` 有更多 commits（包含 `2327309` aggregate deepreview 等）。readiness artifact 期望 31 个文件，PR 仅含 28 个。缺失的 3 个文件是 P17-S1 aggregate deepreview 的 controller judgment 和两个 independent review artifacts。

**风险**: 低。核心实现（`performance.py` + `test_performance.py`）和文档（design.md v2.2 + implementation-control.md）完整。缺失文件是 review 证据链的补充 artifacts，不影响代码正确性。aggregate deepreview 的全部结论已记录在 implementation-control.md Active Gate Ledger 中。

**建议**: push 更新 branch 以包含缺失的 review artifact 文件后再 mark PR ready。

## Residual Risks

| Residual | Owner | Handling |
|---|---|---|
| 标准差行无 TE keyword 时返回 `tracking_error_standard_deviation_only` | Future note precision pass | 仅 missing-path 诊断，不影响成功路径 |
| "年化"移除导致混杂行 note 降级 | Future note precision pass | 不影响 fail-closed 行为 |
| `_classify_tracking_error_nonmatch_context` 缺 benchmark-only 检查 | Future classifier alignment | 对齐两个 classifier 函数的检查项 |
| `tracking_error_incomplete_anchor` 无测试 fixture | Future parser malformed-table fixture | 当前 builder 自然生成完整 anchor |
| Production `tracking_error` golden rows for `001548` 及 P16 enhanced-index candidates | Future evidence-backed golden gate | 仍需 reviewed direct observed disclosure evidence |
| Self-owned thermometer | Future thermometer design/implementation phase | 定义 market/index coverage, source datasets, formulas, percentile windows, cache semantics, failure taxonomy, fixtures, tests |
| Thermometer-to-`valuation_state` mapping | Future mapping design gate if selected | 不静默连接温度计值到分析判断；保留用户显式输入 |
| RR-13 duplicate `016492` | User / App source | 保持为 human-owned；不自动编辑 source CSV |
| PR 缺失 review artifacts (F1) | Controller | push 更新 branch 后包含 |

## Validation Reviewed

| 验证项 | 来源 | 状态 |
|---|---|---|
| PR CI `test` | GitHub Actions run `26291384346` | ✅ SUCCESS |
| `test_performance.py` 22 passed | Aggregate deepreview | ✅ |
| `tests/fund/extractors` 62 passed | Aggregate deepreview | ✅ |
| snapshot/score/quality 55 passed | Aggregate deepreview | ✅ |
| ruff check | Aggregate deepreview | ✅ |
| `git diff --check origin/main..HEAD` | Aggregate deepreview | ✅ |
| `grep tracking_error_ambiguous` 无输出 | Aggregate deepreview | ✅ |
| Blocker precedence 顺序 | Aggregate deepreview | ✅ |
| Early-return append+continue 两处 | Aggregate deepreview | ✅ |
| 10 种 blocker note 常量有对应测试 | Aggregate deepreview | ✅ |
| 直接披露成功契约完整 | Aggregate deepreview | ✅ |

## Controller Follow-up Needed

1. **F1 修复**: push 更新 branch 包含缺失的 3 个 review artifact 文件后，PR 即可满足 readiness reconciliation 的完整文件集。
2. 无需 controller follow-up 的其他事项：核心实现、文档对齐、PR body 均无 blocking issue。
