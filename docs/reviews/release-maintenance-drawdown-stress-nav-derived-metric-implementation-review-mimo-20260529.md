# Drawdown Stress NAV-Derived Metric Implementation Review — MiMo

日期：2026-05-29

角色：implementation code review worker only。不编辑、不 commit、不 push、不 PR、不 merge。

## Reviewed Target

当前未提交的 implementation diff（`git diff HEAD`），对照 accepted plan commit `41485d5` 和 implementation evidence artifact。

## Scope

Production files changed:

- `fund_agent/fund/data/nav_metrics.py`（新文件）
- `fund_agent/fund/data/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `fund_agent/fund/extraction_snapshot.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Test files changed:

- `tests/fund/data/test_nav_metrics.py`（新文件）
- `tests/fund/test_data_extractor.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_quality_gate.py`

Unchanged (verified): `fund_agent/fund/extraction_score.py`、`fund_agent/fund/quality_gate.py`、golden fixtures。

## Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- Accepted plan: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- Plan reviews and rereviews
- Implementation evidence: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-evidence-20260529.md`
- Real run artifacts: `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`、`reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`、`reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`

## Review Findings

### Finding 01 — 无阻断 — max drawdown 公式、符号、峰值/谷值追踪

**审查内容**: `nav_metrics.py:103-136` 的迭代算法。

**验证结果**: 正确。

- 初始 `peak_record = first`，`max_drawdown = Decimal("0")`。
- 对每条记录：若 `nav_value > peak_record.nav_value` 则更新 peak；计算 `drawdown = nav_value / peak_value - 1`；若 `drawdown < max_drawdown` 则更新最大回撤及对应 peak/trough。
- `drawdown` 非正数，`Decimal("0")` 表示无回撤。
- 相同最大回撤保留最早谷值（`<` 而非 `<=`），正确。
- 测试 `test_calculate_max_drawdown_from_accumulated_nav_path` 验证 `[1.00, 1.10, 1.05, 1.20, 1.08]` 产生 `-0.1`，peak=1.20/2024-01-05，trough=1.08/2024-01-08。公式 `1.08/1.20 - 1 = -0.1`，正确。
- 测试 `test_calculate_max_drawdown_monotonic_path_is_zero` 验证单调路径 `max_drawdown_ratio=Decimal("0")`，peak/trough 均为第一条记录。正确。

**判定**: 无 finding。

### Finding 02 — 无阻断 — 期过滤后 minimum_records 独立检查

**审查内容**: plan 要求 metric helper 独立检查 period-filtered records，不依赖 repository `minimum_records`。

**验证结果**: 正确。

- `nav_metrics.py:100-101`: `_period_records()` 先过滤，`_validate_period_records()` 再检查 `len(records) < minimum_records`。
- `data_extractor.py:305-309`: repository 调用传 `minimum_records=_BOND_DRAWDOWN_MINIMUM_RECORDS(30)`，metric helper 也传同一个值。
- 测试 `test_period_filtered_records_are_checked_independently`: 全 series 30 条（2023 年），period 为 2024 年，过滤后 0 条，`minimum_records=1`，抛出 `insufficient_records`。证明 repository 的全 series 检查和 helper 的 period-filtered 检查独立。

**判定**: 无 finding。

### Finding 03 — 无阻断 — 重复日期、非正 NAV、不合格 series 的 fail-closed

**审查内容**: `nav_metrics.py:269-283` 的 period records 校验和 `nav_metrics.py:188-209` 的 series 资格校验。

**验证结果**: 正确。

- 重复日期: `seen_dates` set 检测，`integrity_error`。测试 `test_calculate_max_drawdown_rejects_duplicate_dates` 覆盖。
- 非正 NAV: `nav_value <= 0` 检测，`integrity_error`。测试 `test_calculate_max_drawdown_rejects_non_positive_nav` 覆盖。
- `raw_unit_nav` / `strong_drawdown_evidence_eligible=False`: `adjustment_basis_unknown`。测试 `test_calculate_max_drawdown_rejects_raw_unit_or_ineligible_series` 覆盖。
- `nav_type != accumulated_nav` / `adjusted_basis != accumulated_nav`: `adjustment_basis_unknown`。同上测试覆盖。
- `identity_status != verified`: `identity_mismatch`。`_validate_metric_request` 覆盖。
- `period_start > period_end`: `missing_date_range`。`_validate_metric_request` 覆盖。

**判定**: 无 finding。

### Finding 04 — 无阻断 — contract extension 安全性

**审查内容**: `models.py` 的 Literal extension 和 validator 逻辑。

**验证结果**: 正确。

- `BondRiskEvidenceStrength` 新增 `"quantitative_derived"`。
- `BondRiskEvidenceMeasurementKind` 新增 `"derived_metric"`。
- `_BOND_RISK_EVIDENCE_STRENGTHS` 和 `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS` frozenset 同步扩展。
- `_BOND_RISK_ACCEPTED_STRENGTHS` 从 `("quantitative_direct", "qualitative_direct")` 扩展为 `("quantitative_direct", "quantitative_derived", "qualitative_direct")`。
- `models.py:292-293`: 新增 validator 约束 `if group.strength == "quantitative_derived" and group.measurement_kind != "derived_metric": raise ValueError`。精确防止 `accepted + quantitative_derived + actual_metric/actual_exposure/其他` 语义矛盾组合。
- 测试 `test_quantitative_derived_drawdown_requires_derived_metric_kind` 覆盖正向（`derived_metric` 通过）和反向（`actual_metric`、`actual_exposure`、`risk_disclosure` 均被拒绝）。
- 不改变 dataclass 字段形状，不 bump schema version，不弱化 FQ0-FQ6。

**判定**: 无 finding。MiMo plan review finding 01 已正确修复。

### Finding 05 — 无阻断 — data boundary 隔离

**审查内容**: `bond_risk_evidence.py` 是否执行 IO 或直接调用 CSRC/source/cache/stock-sdk。

**验证结果**: 正确。

- `bond_risk_evidence.py` 新增 import: `NavMaxDrawdownMetric`、`format_max_drawdown_percent`、`NavDataContractError`。全部来自 `fund_agent.fund.data` 包，不引入 IO 依赖。
- `extract_bond_risk_evidence()` 新增 keyword-only 参数 `drawdown_metric` 和 `drawdown_metric_error`，由上游 `FundDataExtractor` 传入。
- `bond_risk_evidence.py` 内不调用 `FundNavRepository`、`CsrcEidNavSource`、httpx、stock-sdk 或任何 cache。
- `data_extractor.py:256-261`: `_load_drawdown_metric_for_bond_fund()` 通过构造器注入的 `_NavSeriesRepository` 调用 `load_nav_series()`，显式参数 `fund_code`、`share_class="A"`、`start_date`、`end_date`、`minimum_records=30`、`force_refresh`。无 `extra_payload`。
- `data_extractor.py:298`: 非债券基金 `classified_fund_type != "bond_fund"` 直接返回 `(None, None)`，不调用 typed repository。

**判定**: 无 finding。

### Finding 06 — 无阻断 — share-class 边界

**审查内容**: 生产 evidence 是否只用 006597/A，无 A/C/E/F 混合。

**验证结果**: 正确。

- `data_extractor.py:39`: `_BOND_DRAWDOWN_SHARE_CLASS = "A"`，硬编码。
- `data_extractor.py:305`: `share_class=_BOND_DRAWDOWN_SHARE_CLASS`，只请求 A 类。
- 测试 `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes` 验证 repository 只调用一次 `("006597", "A", ...)`。
- 实现 evidence 的 real smoke 只使用 006597/A，C/E/F 仅作为独立诊断验证。
- `_nav_series()` fixture 构造 006597/A series，测试中无 C/E/F 混入 production extraction path。

**判定**: 无 finding。

### Finding 07 — 无阻断 — period 边界

**审查内容**: 2024-01-01..2024-12-31，无 trailing future leakage。

**验证结果**: 正确。

- `data_extractor.py:303-304`: `period_start = date(report_year, 1, 1)`，`period_end = date(report_year, 12, 31)`。对 2024 年报即 `2024-01-01..2024-12-31`。
- `nav_metrics.py:237`: period 过滤 `period_start <= record.date <= period_end`，inclusive。
- 实现 evidence real smoke: metric `period_start=2024-01-01`，`period_end=2024-12-31`，`record_count=243`。正确。
- 不使用 trailing window，不引入 2025/2026 数据。

**判定**: 无 finding。

### Finding 08 — 无阻断 — derived anchor/provenance 完整性

**审查内容**: `bond_risk_evidence.py` 的 `_derived_nav_metric_anchor_draft()` 和 `_build_group_anchors()` 的 `source_kind` 处理。

**验证结果**: 正确。

- `_derived_nav_metric_anchor_draft()`: `section_id="derived:nav"`，`row_locator="metric:max_drawdown:<share_class>:<period_start>:<period_end>"`，`evidence_role="derived_max_drawdown_metric"`。
- `note` 包含所有 plan 要求的 provenance 字段: `source=CSRC EID`、`source_name`、`source_id`、`source_url`、`source_query_params`（稳定排序序列化）、`retrieved_at`、`fund_code`、`share_class`、`date_range`、`record_count`、`nav_type`、`adjusted_basis`、`dividend_adjustment_status`、`identity_status`、`calculation_method`、`peak_date`、`peak_value`、`trough_date`、`trough_value`、`max_drawdown_ratio`。
- `_build_group_anchors()`: 新增 `source_kind = "derived" if draft.section_id.startswith("derived:") else "annual_report"`。正确区分 derived 和 annual_report 来源。
- 测试 `test_nav_derived_drawdown_metric_satisfies_drawdown_group` 验证所有 provenance token 出现在 anchor note 中，`extractor_anchor.source_kind == "derived"`，`anchor_ref.section_id == "derived:nav"`。
- 实现 evidence real smoke 的 `extractor_anchor_note` 包含 `calculation_method=max_drawdown_on_accumulated_nav_path`、`peak_date=2024-09-26`、`trough_date=2024-10-09`、`max_drawdown_ratio=-0.0010059518819683125157179982`。与 snapshot 合约一致。

**判定**: 无 finding。

### Finding 09 — 无阻断 — extraction_snapshot.py 的 narrow compatibility fix

**审查内容**: `_first_annual_report_anchor` 重命名为 `_first_traceable_anchor`，行为从返回 `None`（无年报锚点时）变为返回 `anchors[0]`（首个任意锚点）。

**验证结果**: 正确且 backward compatible。

- 函数仅在 `_build_bond_risk_evidence_record()` 中调用一次（line 1047）。
- 当 anchors 包含 `annual_report` 锚点时，行为不变——仍返回首个 `annual_report` 锚点。
- 当 anchors 仅包含 `derived` 锚点时，旧代码返回 `None`（丢失 traceability），新代码返回 `derived` 锚点（保留 traceability）。
- 测试 `test_build_snapshot_records_projects_derived_bond_risk_anchor_when_no_annual_anchor` 验证 derived-only 锚点正确投影: `section_id == "derived:nav"`、`row_id == "metric:max_drawdown:A:2024-01-01:2024-12-31"`。
- 不改变 snapshot schema，不增加新字段。
- 现有 snapshot 测试（含 `annual_report` 锚点的场景）不受影响，因为 `annual_report` 锚点仍被优先选择。

**判定**: 无 finding。实现 evidence 中对 `extraction_snapshot.py` 修改的逐项说明已满足 plan Slice 4 要求。

### Finding 10 — 无阻断 — 错误降级与 fail-closed 行为

**审查内容**: NAV source 失败时 `drawdown_stress` 组的降级路径。

**验证结果**: 正确。

- `data_extractor.py:326-336`: `NavDataContractError` 被捕获，返回 `(None, exc)`。其他 `Exception` 被包装为 `category="unavailable"` 的 `NavDataContractError`。不会冒泡阻断年报抽取。
- `bond_risk_evidence.py:567-575`:
  - 有 `drawdown_metric` → accepted `quantitative_derived`。正确。
  - 无 metric，有直接年报表格指标 → `quantitative_direct`。正确（现有逻辑未改动）。
  - 无 metric，无表格指标，有控制意图文本 → weak `qualitative_control_intent`，`na_reason` 使用 `_drawdown_error_reason(drawdown_metric_error)` 或默认 `"drawdown_metric_not_found"`。正确。
  - 无 metric，无表格指标，无控制文本，有 error → `_missing_group` with error reason。正确。
  - 无 metric，无表格指标，无控制文本，无 error → `_missing_group("drawdown_metric_not_found")`。正确。
- `_drawdown_error_reason()` 映射: `error.category` → `f"drawdown_nav_{error.category}"`。符合 plan fail-closed 表的 `drawdown_nav_*` 前缀约定。
- 测试 `test_nav_metric_error_keeps_drawdown_control_text_weak` 验证 error + 控制文本场景: `status="weak"`、`strength="qualitative_control_intent"`、`na_reason="drawdown_nav_unavailable"`、`drawdown_stress` 在 `weak_group_ids` 中。
- 测试 `test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak` 验证 `adjustment_basis_unknown` error 场景: `na_reason="drawdown_nav_adjustment_basis_unknown"`。

**判定**: 无 finding。

### Finding 11 — 无阻断 — score/quality gate/golden 未被弱化

**审查内容**: `extraction_score.py`、`quality_gate.py`、golden fixtures 是否被修改。

**验证结果**: 正确。

- `git diff HEAD` 不包含 `extraction_score.py` 或 `quality_gate.py` 的修改。
- `score.json` 的 `score_applicability_issues` 为空——七组 satisfied 后自然不再产生 `bond_risk_evidence_missing`。
- `quality_gate.json` 的 issues 中无 `reason="bond_risk_evidence_missing"` 的 FQ2F。剩余 FQ2（turnover_rate、holder_structure、share_change）、FQ2F（P1 字段失败）、FQ0（未配置 golden）、FQ4（缺失率偏高）均与本 gate 无关。
- 现有 score 回归测试 `test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group`（line 629）仍通过，证明当 `drawdown_stress` 是唯一弱组时，`bond_risk_evidence_missing` 仍正确发出。
- 新增 quality gate 测试 `test_run_quality_gate_has_no_bond_risk_fq2f_when_score_issue_absent` 验证 score 无 applicability issues 时无 FQ2F `bond_risk_evidence_missing`。
- golden fixtures 未被修改。

**判定**: 无 finding。

### Finding 12 — 无阻断 — 测试覆盖充分性

**审查内容**: 测试是否覆盖 plan 要求的 happy path 和 failure path。

**验证结果**: 充分。

| Plan 测试要求 | 覆盖状态 |
|---|---|
| NAV path `[1.00, 1.10, 1.05, 1.20, 1.08]` 产生 `-0.10` | `test_calculate_max_drawdown_from_accumulated_nav_path` ✓ |
| 单调上涨路径产生 `0` | `test_calculate_max_drawdown_monotonic_path_is_zero` ✓ |
| Peak/trough dates/values exact | 同上测试 ✓ |
| Period insufficient records | `test_period_filtered_records_are_checked_independently` ✓ |
| Full series ≥30 but period-filtered <30 | 同上测试（全 series 30 条 2023 年，period 2024 年过滤后 0 条）✓ |
| Duplicate dates → integrity_error | `test_calculate_max_drawdown_rejects_duplicate_dates` ✓ |
| Non-positive NAV → integrity_error | `test_calculate_max_drawdown_rejects_non_positive_nav` ✓ |
| Raw-unit / ineligible rejects | `test_calculate_max_drawdown_rejects_raw_unit_or_ineligible_series` ✓ |
| 006597/A accepted path | `test_nav_derived_drawdown_metric_satisfies_drawdown_group` + `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes` ✓ |
| No A/C/E/F mixing | `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes`（验证只有一次 A 类调用）✓ |
| Provenance completeness | `test_nav_derived_drawdown_metric_satisfies_drawdown_group`（验证 18 个 provenance token）✓ |
| Weak qualitative not promoted | `test_drawdown_control_text_alone_is_weak`（原有）+ `test_nav_metric_error_keeps_drawdown_control_text_weak` ✓ |
| Snapshot derived anchor projection | `test_build_snapshot_records_projects_derived_bond_risk_anchor_when_no_annual_anchor` ✓ |
| Score no bond_risk_evidence_missing when satisfied | 现有 `test_data_extractor` 七组 satisfied 路径 + real run `score_applicability_issues=[]` ✓ |
| Score regression: drawdown-only unsatisfied still blocks | `test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group`（已有）✓ |
| Quality gate no FQ2F when score issue absent | `test_run_quality_gate_has_no_bond_risk_fq2f_when_score_issue_absent` ✓ |
| Contract extension: accepted + quantitative_derived + derived_metric passes | `test_quantitative_derived_drawdown_requires_derived_metric_kind` ✓ |
| Contract extension: accepted + quantitative_derived + non-derived_metric rejects | 同上测试 ✓ |
| Non-bond fund doesn't call typed repository | `test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups` ✓ |
| Raw-unit error keeps drawdown weak | `test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak` ✓ |

**判定**: 无 finding。

### Finding 13 — 无阻断 — docs 对齐

**审查内容**: `docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md` 的更新是否与实现一致且不 overclaim。

**验证结果**: 正确。

- `docs/design.md` diff 更新了 FundNavRepository 段落: 从"当前未实现 drawdown metric"改为描述当前已实现的最大回撤派生指标路径、A 类份额、年报年度期间、derived provenance、fail-closed 行为。不提 volatility、golden readiness 或 total-return。
- 新增 `FundDataExtractor.extract()` 段落描述 bond_fund 的 typed NAV 加载和 drawdown_stress 证据投影。
- 未修改 root README（CLI 用法未变）。未修改 score policy 或 quality gate 文档。

**判定**: 无 finding。

### Finding 14 — 低风险 — `format_max_drawdown_percent` 的 Decimal quantize 语义

**审查内容**: `nav_metrics.py:152`: `f"{(value * Decimal('100')).quantize(_PERCENT_QUANT)}%"`

**观察**: `_PERCENT_QUANT = Decimal("0.01")` 作为 `quantize` 的 quantum 参数，表示"保留两位小数"。`Decimal("0.01")` 在此上下文中不是"1%"而是"精度步长 0.01"。`-0.001005...* 100 = -0.100595...`，quantize to 0.01 → `-0.10`，格式化为 `"-0.10%"`。正确。

**判定**: 低风险观察，非 finding。quantize 语义对 Decimal 熟悉的开发者无歧义。

### Finding 15 — 低风险 — `_drawdown_error_reason` category 前缀不自检

**审查内容**: `bond_risk_evidence.py:1027`: `f"drawdown_nav_{error.category}"`

**观察**: 若 `error.category` 已包含 `drawdown_` 前缀（理论上不会，因为 `NavFailureCategory` 的合法值不含此前缀），结果会出现 `drawdown_nav_drawdown_*` 冗余。当前 `NavFailureCategory` 合法值为 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`，均不含 `drawdown_` 前缀。

**判定**: 低风险观察，非 finding。当前 taxonomy 下不会触发。

## Real Run Artifacts 验证

### snapshot.jsonl

- `bond_risk_evidence` 行: `contract_status="satisfied"`，`satisfied_groups` 包含全部七组含 `drawdown_stress`，`missing_groups=[]`、`weak_groups=[]`、`ambiguous_groups=[]`。
- `section_id="§2"`、`row_id="line:21"`——来自 `_first_traceable_anchor` 投影。注意: 此处 snapshot 中的 `section_id` 来自 `_build_bond_risk_evidence_record` 中的 anchor 投影逻辑，但 bond_risk_evidence 的 anchor 在 snapshot 记录中显示为 `§2`（来自其他 anchor），而非 `derived:nav`。这是因为 snapshot 的 `_build_bond_risk_evidence_record` 使用 `_first_traceable_anchor` 选择锚点，而 bond_risk_evidence 字段的 anchors 元组中可能包含多个锚点（包括 annual_report 的 §2 锚点和 derived 锚点）。`_first_traceable_anchor` 优先返回 `annual_report` 锚点。

  **补充验证**: 实现 evidence 的直接 extractor provenance 确认 `extractor_anchor source_kind=derived`、`section_id=derived:nav`、`row_locator=metric:max_drawdown:A:2024-01-01:2024-12-31`。snapshot 中显示 `§2` 是因为该记录还有其他年报锚点存在（七组中其他组的锚点），`_first_traceable_anchor` 返回了首个 `annual_report` 锚点。这不影响 `drawdown_stress` 组的 satisfied 状态——结构化字段 `bond_risk_satisfied_groups` 已正确包含 `drawdown_stress`。snapshot 的锚点投影只用于 traceability 辅助，不影响 score/quality gate 的结构化判断。

### score.json

- `score_applicability_issues: []`——无 `bond_risk_evidence_missing`。
- 剩余 issues: FQ2（turnover_rate、holder_structure、share_change）、FQ2F（P1 字段失败）、FQ0（未配置 golden）、FQ4（缺失率 28.6%）。均与 bond_risk_evidence 无关。

### quality_gate.json

- `status: "warn"`，`issue_count: 6`。
- 无 `reason="bond_risk_evidence_missing"` 的 FQ2F issue。
- 剩余 issues 与 score.json 一致: turnover_rate、holder_structure、share_change 的 FQ2 警告，P1 字段失败的 FQ2F，FQ0 未配置，FQ4 缺失率。

## Scope Compliance

| 检查项 | 状态 |
|---|---|
| 未修改 `extraction_score.py` | ✓ |
| 未修改 `quality_gate.py` | ✓ |
| 未修改 golden fixtures | ✓ |
| 未修改 score threshold/policy | ✓ |
| 未修改 FQ0-FQ6 语义 | ✓ |
| 未修改 snapshot schema（无新增字段） | ✓ |
| 未使用 `extra_payload` | ✓ |
| 未直接调用 CSRC/source/cache/stock-sdk | ✓ |
| 未混合 A/C/E/F | ✓ |
| 未实现 volatility | ✓ |
| 未修改 disallowed production files | ✓ |
| ruff 全量通过 | ✓（evidence 记录） |
| pytest 938 passed, coverage 92.42% | ✓（evidence 记录） |

## Residual Low Risks

1. **CSRC EID endpoint availability**: 外部 source 无 SLA；`unavailable` 保持 `drawdown_stress` weak/missing，score 自然阻断。已正确处理。
2. **CSRC EID source scoped to 006597 family**: 当前 hardcoded 常量；metric 对其他基金族需单独 gate。已知限制。
3. **`source_query_params` 混合 HTTP params 和 request context**: 预已存在问题，非本 gate 引入。future provenance cleanup。
4. **Accumulated NAV 不等同于 total-return index**: 已接受限制，不 relabel。
5. **snapshot 锚点投影**: 当 bond_risk_evidence 同时有 annual_report 和 derived 锚点时，snapshot 的 `section_id` 显示 `§2` 而非 `derived:nav`。这不影响结构化字段正确性，但 reviewer 如需验证 derived provenance 需查看 extractor 内部 anchors 而非 snapshot 投影字段。可通过后续 snapshot schema 扩展支持多锚点投影（非本 gate 范围）。

## Verdict

**accepted**

实现与 accepted plan 完全一致。10 个 review focus 均无阻断 finding。contract extension 安全（MiMo plan review finding 01 已正确修复）、data boundary 隔离、share-class 分离、period 无泄漏、fail-closed 完整、provenance 完备、score/quality gate/golden 未被弱化。测试覆盖 happy path 和 failure path。docs 与实现对齐且不 overclaim。real 006597 run 产出 `bond_risk_contract_status="satisfied"`、`score_applicability_issues=[]`、quality gate 无 `bond_risk_evidence_missing` FQ2F。
