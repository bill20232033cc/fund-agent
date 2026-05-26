# Gate 1 Implementation Review: Quality Gate Correctness Report-Year Scope

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Gate**: Gate 1 correctness report_year scope fix
> **Implementation agent**: AgentCodex
> **Plan**: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> **Plan reviews**: MiMo (`release-maintenance-quality-gate-correctness-year-scope-plan-review-mimo-20260527.md`), GLM (`release-maintenance-quality-gate-correctness-year-scope-plan-review-glm-20260527.md`)
> **Controller judgment**: `release-maintenance-quality-gate-correctness-year-scope-plan-controller-judgment-20260527.md`
> **Implementation evidence**: `release-maintenance-quality-gate-correctness-year-scope-implementation-evidence-20260527.md`

---

## Verdict

**PASS_WITH_FINDINGS**

实现正确完成了 plan 的全部目标。Oracle identity 从 `fund_code + field_name + sub_field` 升级为 `fund_code + report_year + field_name + sub_field`，同年 golden/snapshot 比对保持 FQ1/block 语义不变，跨年 golden 不会产生 false mismatch，legacy JSON 兼容规则安全，`year_not_covered` 正确映射为 FQ0/info/pass。无越界修改。

发现 2 条 informational finding 和 0 条 correctness bug。所有 controller judgment F1-F5 要求均已覆盖。

---

## Review Focus 1: 多基金、多年份混合 snapshot 时 coverage_scope 和 fund code 聚合正确性

### 结论：当前单 bundle 集成路径下正确；批量路径有已知的 coverage 粒度限制

**代码路径分析**：

`_correctness_coverage()` 的覆盖判定逻辑（`extraction_score.py`）：

1. `snapshot_fund_identities` 是 `(fund_code, report_year)` 元组集合
2. `golden_identities` 是 `{(fund.fund_code, fund.report_year) for fund in golden_funds}`
3. 先判 `fund_not_covered`（全部 fund_code 不在 golden_codes）
4. 再判 `year_not_covered`（全部 `(fund_code, year)` 不在 golden_identities）
5. 后续 `no_comparable_fields` → `partially_covered` → `covered`

**当前安全**：`run_quality_gate_for_bundle()` 每次只处理一只基金的单 bundle，snapshot records 中只有一个 `(fund_code, report_year)`。在单基金单年份场景下，`year_not_covered` 判定是精确的。

**批量路径限制**：如果 `compare_snapshot_correctness` 被用于多基金多年份批量 snapshot（当前未发生），且 snapshot 同时包含 `(A, 2024)`（golden 有）和 `(A, 2025)`（golden 无），则 `_correctness_coverage()` 会因 `(A, 2024)` 匹配 golden 而跳过 `year_not_covered` 分支，落入 `partially_covered`。此行为仍是 FQ0/info，不产生 false FQ1/block，但 coverage_reason 消息可能不够精确。

**Finding F1 — Informational**: 批量多基金多年份混合 snapshot 场景下，`_correctness_coverage()` 的 `year_not_covered` 判定粒度为全量（所有 identities 都不匹配才触发），不是逐 fund 逐 year 判定。当前单 bundle 集成路径不触发此场景。

- **Severity**: informational
- **File/function**: `extraction_score.py` / `_correctness_coverage()`
- **Impact**: 当前生产路径不受影响；未来批量 correctness 场景需重新评估
- **Required disposition**: 无需当前 gate 修改；记为 residual，未来批量 multi-year golden 维护 gate 应考虑

---

## Review Focus 2: 2025 snapshot + 2024 golden 是否完全不产生 mismatch row；unavailable rows 是否影响 FQ0/info 合理性

### 结论：完全正确

**代码路径追踪**（snapshot `(004393, 2025)` + golden `(004393, 2024)`）：

1. `_snapshot_actual_index()` 构建 key `(004393, 2025, field, sub_field)` → actual_index
2. `_compare_golden_record()` 对 golden record `(004393, 2024)` 构造查找 key `(004393, 2024, field, sub_field)`
3. `(004393, 2024, ...)` 不在 actual_index 中（actual_index 只有 `(004393, 2025, ...)` 条目）
4. 返回 `CorrectnessRecordResult(status=CORRECTNESS_UNAVAILABLE, reason="snapshot 未显式暴露该 golden 子字段...")`
5. **0 条 mismatch row，0 条 comparable record**

`_correctness_coverage()` 路径：

- `snapshot_fund_identities = (("004393", 2025),)`
- `golden_identities = {("004393", 2024)}`
- `target_identities = {("004393", 2025)}`
- `comparable_codes` = 空（无 match/mismatch rows 且 `(fund_code, report_year)` 不在 target_identities）
- `target_results` = 空（所有 record_results 的 report_year=2024，不在 target_identities={(004393, 2025)}）
- 第一判：004393 ∈ golden_codes → 非 fund_not_covered
- 第二判：`(004393, 2025)` ∉ `{(004393, 2024)}` → **year_not_covered** ✓

**FQ0/info 合理性**：

- `comparable_records=0`，`mismatched_records=0` → 不进入 FQ1/block 分母
- `unavailable_records=2`（golden 的两条记录都因 key 不匹配而标记 unavailable）
- quality gate 正确映射为 `FQ0/info`，`gate_status=pass`
- 消息："已有 strict golden answer 记录，但当前年报年份尚未覆盖；本次 correctness oracle 不使用其它年份 golden answer。"

**测试覆盖**：

- `test_compare_snapshot_correctness_marks_current_year_not_covered`：显式断言 0 mismatch、0 comparable、year_not_covered、all unavailable
- `test_run_quality_gate_for_bundle_uses_bundle_report_year_for_correctness`：完整集成链 bundle(2025) → snapshot → score → gate → FQ0/info

---

## Review Focus 3: 同 fund_code 不同年份 golden rows 是否能被 loader/build/test 安全处理

### 结论：正确

**Loader**（`load_golden_answer_json`）：

- `seen_keys: set[tuple[str, int, str, str]]` 以 `(fund_code, report_year, field_name, sub_field)` 为唯一键
- 同 fund_code 不同 report_year 允许独立出现
- `fund_report_year` 校验：record 的 report_year 必须等于所属 fund 的 report_year，不匹配报错
- Record 创建使用 fund 级别的 `fund_report_year`，不使用 record 级别解析值（即使 record 有不同值也会被校验拒绝）

**Build**（`build_golden_answer_json` / `parse_golden_answer_markdown`）：

- Markdown 解析固定使用 `LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024`
- JSON payload 通过 `asdict()` 序列化，fund 和 record 级别都输出 `report_year`
- `_json_payload()` 显式包含 `"report_year": fund.report_year`

**Test**：

- `test_load_golden_answer_json_allows_same_fund_code_different_report_year`：验证 `(004393, 2024)` 和 `(004393, 2025)` 可独立加载
- `test_load_golden_answer_json_rejects_duplicate_same_year_identity`：验证同年同字段子键重复被拒绝
- `test_build_golden_answer_json_writes_machine_readable_payload`：验证 build 输出包含 fund 级和 record 级 report_year

---

## Review Focus 4: report_year 缺失或非法 snapshot 是否 fail closed

### 结论：正确 fail closed

**Snapshot 端**（`_required_snapshot_int`）：

- `value is None` → raise ValueError("snapshot 记录缺少字段：report_year")
- `isinstance(value, bool)` → raise ValueError
- 非整数非数字字符串 → raise ValueError
- **不允许默认值，不允许静默通过**

**Golden 端**（`_json_optional_report_year`）：

- `value is None` → 返回 `LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024`（兼容 legacy JSON，这是明确的策略决定）
- `isinstance(value, bool)` → 追加 error + 返回 2024（error 会导致整体 `GoldenAnswerValidationError`）
- 非法类型 → 追加 error + 返回 2024
- **invalid report_year 导致 load 失败（fail closed），不是静默接受**
- **missing report_year 按 legacy 策略默认 2024（这是 plan 明确要求的行为）**

**测试覆盖**：

- `test_load_golden_answer_json_defaults_legacy_report_year_to_2024`：验证 legacy JSON 缺 report_year 安全默认为 2024
- Snapshot 端无 report_year 由 `_required_snapshot_int` 的 ValueError 保证，测试通过 `_snapshot_record` helper 的 `report_year: int = 2024` 参数隐式覆盖

---

## Review Focus 5: 新字段 report_year 序列化是否破坏旧 tests/README 或 score consumers

### 结论：无破坏

**`CorrectnessRecordResult` 序列化**：

- 新增 `report_year: int` 字段在 `fund_code` 之后
- `asdict()` 序列化会在 JSON 中增加 `"report_year": 2024` 字段
- 这是 additive schema 变更，旧 consumer 使用 key-based access 不受影响
- quality gate 的 `_correctness_mismatch_issue()` 从 `Mapping[str, object]` 读取已知字段，不会因新增 key 出错

**`GoldenAnswerFund` / `GoldenAnswerRecord` 序列化**：

- `_json_payload()` 显式包含 `"report_year": fund.report_year`
- Record 使用 `asdict(record)` 序列化，自动包含 `report_year`
- 新增字段对现有 JSON consumer 是 additive

**README 更新**：

- `fund_agent/fund/README.md`：正确更新 correctness identity 描述和 `year_not_covered` scope
- `tests/README.md`：正确更新测试约束，要求覆盖 `year_not_covered` 和 `report_year` identity

**Score consumers**：

- quality gate 只消费 `score.json` 的 correctness summary（`coverage_scope`、`comparable_records` 等），不消费 `record_results` 中的 `report_year` 字段
- `CorrectnessSummary` 本身结构未变（`status`、`coverage_scope` 等字段不变）
- score.json 的 `correctness.record_results[]` 每条多了 `report_year`，不影响 gate 逻辑

---

## Review Focus 6: 越界修改检查

### 结论：无越界

| 越界检查项 | 状态 | 证据 |
|---|---|---|
| Renderer 未修改 | PASS | `git diff --stat` 无 template/renderer.py 变更 |
| Service/CLI 默认行为未变 | PASS | 无 services/ 或 ui/ 文件变更 |
| Host/Agent/dayu 未涉及 | PASS | 无 host/ 或 agent/ 文件变更 |
| FundDocumentRepository 未改 | PASS | 无 documents/ 文件变更 |
| Source helper 未改 | PASS | 无 sources.py 变更 |
| NAV 行为未变 | PASS | 无 nav_data.py 变更 |
| turnover_rate 未变 | PASS | 无 manager_ownership.py 变更 |
| Checklist run-id 未改 | PASS | 无 checklist 相关变更 |
| FQ policy 未弱化 | PASS | FQ1/block 语义完整保留；year_not_covered 仅新增 FQ0/info |
| Report-writing audit 未改 | PASS | 无 report_writing_audit.py 变更 |
| quality_gate_integration.py 未修改 | PASS | `git diff --stat` 确认无变更；report_year 从 bundle → snapshot 自然传递 |

**变更文件清单验证**：

实现 evidence 声明 10 个文件变更。`git diff --stat HEAD` 确认变更范围与声明一致。所有变更均在 plan 的 Files To Modify 范围内。

---

## Controller Judgment F1-F5 逐项验证

| Controller Finding | 实现状态 | 验证方式 |
|---|---|---|
| MiMo: `_snapshot_actual_index` 从每条 record 提取 report_year | ✓ 已实现 | 代码确认 `_required_snapshot_int(record, "report_year")` 逐条提取 |
| MiMo: Legacy golden set 默认 2024 安全 | ✓ 已实现 | `_json_optional_report_year` → `LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024` |
| MiMo: `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` 常量 + gate handler | ✓ 已实现 | 两模块常量 + `_correctness_available_coverage_issue` + `_correctness_coverage_message` |
| GLM F1: `_correctness_coverage()` year-scoped | ✓ 已实现 | `golden_identities` / `target_identities` 均为 `(fund_code, year)` 元组 |
| GLM F2: 同 fund_code 多 year 条目允许 | ✓ 已实现 | `seen_keys` 4-tuple + 测试覆盖 |
| GLM F3: Integration test report_year=2025 bundle | ✓ 已实现 | `test_run_quality_gate_for_bundle_uses_bundle_report_year_for_correctness` |
| GLM F4: Smoke 无关失败分类 | ✓ 已记录 | Implementation evidence residuals section |
| GLM F5: quality_gate.py 处理 year_not_covered | ✓ 已实现 | `_correctness_available_coverage_issue` 含 `year_not_covered` 分支 |

---

## Additional Findings

### F2 — Informational: `covered_fund_codes`/`missing_fund_codes` 保持 fund_code 粒度

`_correctness_coverage()` 的 `covered_fund_codes` 和 `missing_fund_codes` 输出仍是 `tuple[str, ...]`（fund_code 级别），不含 year 信息。当前 `year_not_covered` 场景下 `covered_fund_codes=()` 和 `missing_fund_codes=(fund_code,)` 是正确的，但未来多 year golden 维护可能需要升级为 `(fund_code, report_year)` 粒度。

- **Severity**: informational
- **File/function**: `extraction_score.py` / `_correctness_coverage()` 返回值
- **Impact**: 当前单 bundle 路径无影响；FQ0/info issue 的 metadata 正确性不受影响
- **Required disposition**: 无需当前 gate 修改；future multi-year golden gate 应评估

---

## Validation Summary

| 验证项 | 结果 |
|---|---|
| `uv run pytest` focused tests | 74 passed in 0.81s |
| `ruff check` changed files | All checks passed (per evidence) |
| `git diff --check` | passed (per evidence) |
| Out-of-scope file changes | None detected |
| `quality_gate_integration.py` unmodified | Confirmed |

---

## Conclusion

**PASS_WITH_FINDINGS**

实现正确、完整地完成了 Gate 1 correctness report_year scope fix。核心改动聚焦在 oracle identity 升级、legacy 兼容、coverage scope 扩展和 quality gate handler，无 correctness bug，无越界修改。所有 controller judgment 要求逐项验证通过。2 条 informational finding 均为未来 multi-year 批量场景的预留考量，不影响当前 gate acceptance。

Implementation is ready for commit.
