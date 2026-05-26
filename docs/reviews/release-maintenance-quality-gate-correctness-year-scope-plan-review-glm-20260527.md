# Quality Gate Correctness Report-Year Scope Plan Review — AgentGLM

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Plan artifact**: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> **Verdict**: **PASS_WITH_FINDINGS**

---

## 1. Review Summary

Plan 正确识别了 correctness oracle 的核心缺陷：golden answer 与 snapshot 比对仅以 `fund_code` 为 scope，缺少 `report_year`，导致 2025 snapshot 错误命中 2024 golden 行产生 false mismatch。修改范围聚焦 `golden_answer.py`、`extraction_score.py`、`quality_gate.py` 及其测试，兼容策略合理，非目标边界清晰。

发现 2 条 material finding（需实现前确认）和 3 条 informational finding（不阻断实现但应记录为 residual）。

---

## 2. Findings

### F1 — Material: `_correctness_coverage()` 需显式升级为 year-scoped 匹配

**Severity**: medium
**Evidence**: `extraction_score.py:1749-1823` `_correctness_coverage()` 当前以 `fund_code` 为覆盖判断粒度；`golden_codes = {fund.fund_code for fund in golden_funds}` 仅聚合 `fund_code` 集合。
**Impact**: Plan 要求 `GoldenAnswerFund` 增加 `report_year` 后，同一 `fund_code` 在 golden funds 中可能出现多条（不同年份）。`_correctness_coverage()` 的 `golden_codes` 集合和 `comparable_codes` 推导如果不升级为 `(fund_code, report_year)` 二元组，`year_not_covered` 判定将无法正确区分「基金无 golden」与「基金有 golden 但年份不匹配」。
**Required disposition**: 实现时必须将 `_correctness_coverage()` 的 golden fund 匹配从 `fund_code` 单键改为 `(fund_code, report_year)` 二元组；`year_not_covered` 仅当 `fund_code` 存在于 golden 但当前 `report_year` 不存在时触发。Plan 应在 Test Matrix 的 Correctness compare 条目中增加显式断言：`_correctness_coverage()` 对 `004393 / 2025`（golden 仅有 `004393 / 2024`）返回 `coverage_scope = "year_not_covered"` 而非 `fund_not_covered`。

### F2 — Material: `GoldenAnswerFund` 增加 `report_year` 后同一 fund_code 可多次出现，load 路径需明确

**Severity**: medium
**Evidence**: `golden_answer.py:186-199` `load_golden_answer_json()` 当前按 `funds` 数组逐条解析，`seen_keys` 是全局跨 fund 的 `(fund_code, field_name, sub_field)` 集合。Plan 将 seen_keys 改为 `(fund_code, report_year, field_name, sub_field)` 后，同一 `fund_code` 在不同 `report_year` 下会被允许为独立的 `GoldenAnswerFund` 条目。
**Impact**: 当前 golden JSON 结构是每基金一条 `GoldenAnswerFund`。增加 `report_year` 后，v2 JSON 可能包含同一 `fund_code` 的多条 `GoldenAnswerFund`（如 `004393 / 2024` 和 `004393 / 2025`）。Plan 未显式声明是否允许这种结构，也未说明 v1 legacy JSON（仅一条 `004393` 无 `report_year`）升级后是否仍保持单一 `GoldenAnswerFund`。如果实现时 `load_golden_answer_json()` 的 fund 级去重逻辑未更新，可能导致同 fund_code 多 year 条目被误拒。
**Required disposition**: Plan 应补充声明：(a) v2 JSON 允许同一 `fund_code` 出现在多条 `GoldenAnswerFund` 中（不同 `report_year`）；(b) v1 legacy JSON 升级后每 `fund_code` 仅产生一条默认 `report_year=2024` 的 `GoldenAnswerFund`；(c) `_compare_golden_funds()` 遍历所有 golden fund 条目时按 `(fund_code, report_year)` 与 snapshot 匹配。这些行为应在 `test_golden_answer.py` 中有显式测试覆盖。

### F3 — Informational: `quality_gate_integration.py` 未显式在 plan 的 Files To Modify 列表中

**Severity**: low
**Evidence**: `quality_gate_integration.py:48-123` `run_quality_gate_for_bundle()` 调用 `write_extraction_score_records()` 时传入 `records`（已含 `report_year`）和 `golden_answer_path`。correctness 比对通过 `compare_snapshot_correctness()` 执行，`report_year` 从 snapshot records 中隐式可用。
**Impact**: Plan 的 Files To Modify 列表不包含 `quality_gate_integration.py`，且实现分析表明该文件确实不需要修改——snapshot records 已携带 `report_year`，`compare_snapshot_correctness()` 将从 records 中提取。但 Test Matrix 的 Integration 条目应显式验证 `run_quality_gate_for_bundle()` 在 bundle `report_year=2025` 且 golden 仅有 `2024` 时正确产生 `year_not_covered`，而非依赖 bundle `report_year` 是否被正确传递。当前 integration test fixture `_bundle()` 的默认 `report_year` 值需确认。
**Required disposition**: 不需要修改 `quality_gate_integration.py`，但 integration test 中应显式构造 `report_year=2025` 的 bundle，确保 `report_year` 从 bundle → snapshot records → correctness 比对的完整传递链被验证。

### F4 — Informational: Smoke test 无关失败分类未显式列出

**Severity**: low
**Evidence**: Plan 的 Acceptance Commands 列出了 4 条 product smoke 命令（`analyze` 和 `checklist` 各两条，分别 2024 和 2025）。
**Impact**: 若 smoke 因 PDF 下载失败、网络不可用、NAV 数据源不可达、`turnover_rate` 缺失（当前为 warn 不 block）或 checklist run-id 命名问题而失败，应被分类为 unrelated 而非 Gate 1 regression。Plan 在 Expected Acceptance 中提到 "turnover_rate missing remains warn/non-blocking"，但未完整列出无关失败类别。
**Required disposition**: 不阻断 plan，但实现验收时应明确：PDF/network/NAV/turnover_rate/checklist-run-id 失败属于 unrelated failure，只有 correctness year-scoping 相关的 FQ1 变化才属于 Gate 1 regression。

### F5 — Informational: `_evaluate_correctness()` 需处理新 `year_not_covered` coverage scope

**Severity**: low
**Evidence**: `quality_gate.py:363-429` `_correctness_available_coverage_issue()` 当前处理的 coverage scope 集合为 `{None, covered, partially_covered, fund_not_covered, no_comparable_fields, not_configured}`。新增 `year_not_covered` 需在此函数中增加对应分支。
**Impact**: Plan 已在 quality_gate.py 修改描述中提到 "Accept coverage_scope='year_not_covered'"，但未指出需要在 `_correctness_available_coverage_issue()` 中新增显式分支。若实现时遗漏此分支，`_evaluate_correctness()` 会因 `raise ValueError(f"score.json correctness.coverage_scope 不受支持：{coverage_scope}")` 而崩溃。
**Required disposition**: 实现时必须在 `_correctness_available_coverage_issue()` 中新增 `year_not_covered` 分支，返回 FQ0/info issue，消息说明「基金在 golden 中有记录但当前报告年份无 golden 覆盖」。不阻断 plan，但属于实现必须覆盖点。

---

## 3. Scope Boundary Check

| Out-of-scope item | Plan 状态 | 判定 |
|---|---|---|
| Renderer | 明确排除 | ✓ 无越界 |
| Service/CLI 默认行为 | 明确排除 | ✓ 无越界 |
| Host/Agent/dayu | 明确排除 | ✓ 无越界 |
| FundDocumentRepository / source helper | 明确排除 | ✓ 无越界 |
| NAV 行为 | 明确排除 | ✓ 无越界 |
| turnover_rate | 明确排除 | ✓ 无越界 |
| checklist run-id 命名 | 明确列为 P3 residual | ✓ 无越界 |
| FQ0-FQ6 block/warn 语义 | 仅新增 `year_not_covered` FQ0/info 分支，不改变现有 block/warn | ✓ 无越界 |
| Report-writing audit | 明确排除 | ✓ 无越界 |

---

## 4. Test Matrix Adequacy

| 验收维度 | Plan 覆盖 | 评估 |
|---|---|---|
| 2024 same-year mismatch 仍 block | Test Matrix 行 2：`004393/2024` same-year mismatched scalar remains `mismatch` | ✓ 覆盖 |
| 2025 missing-year 不 block | Test Matrix 行 3：`004393/2025` 返回 `year_not_covered`，`comparable_records=0` | ✓ 覆盖，但需补充 F1 要求的 `_correctness_coverage()` 显式断言 |
| Golden schema build/load 兼容 | Test Matrix 行 1：legacy JSON 无 `report_year` 时默认 `2024`；build output 含 `report_year` | ✓ 覆盖 |
| Duplicate key | Test Matrix 行 3：duplicate rows with same `fund_code + report_year + field/subfield` rejected | ✓ 覆盖 |
| record/report_year serialization | 通过 `asdict()` 自动序列化 | ✓ 隐式覆盖 |
| Integration bundle report_year 传递 | Test Matrix Integration 行 | ⚠ 需显式构造 `report_year=2025` 的 bundle（F3） |
| Product smoke 命令 | Acceptance Commands 列出 4 条 | ✓ 基本足够，F4 建议补充无关失败分类 |
| README/control doc 同步 | Files To Modify 文档列表 | ✓ 合理 |
| Gate 2/Gate 3 内容误写成当前事实 | Residuals 明确标注为后续 gate | ✓ 无风险 |

---

## 5. Conclusion

**PASS_WITH_FINDINGS**

Plan 正确定位了 correctness oracle 缺少 `report_year` 的 root cause，修改范围与非目标边界均合理。2 条 material finding（F1: `_correctness_coverage()` year-scoped 匹配，F2: `GoldenAnswerFund` 同 fund_code 多 year 条目语义）需在实现时明确处理，不阻断 plan acceptance 但应作为 implementation review 的重点检查项。3 条 informational finding（F3-F5）属于实现细节补充，不改变 plan 方向。

Plan 可进入 implementation handoff，但 implementation 必须覆盖 F1-F5 指出的具体检查点。
