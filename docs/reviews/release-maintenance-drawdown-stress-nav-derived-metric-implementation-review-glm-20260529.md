# Drawdown Stress NAV-Derived Metric Implementation — Deep Review (GLM)

日期：2026-05-29

角色：code review worker only。未编辑文件、未 commit、未 push、未建 PR、未 merge、未 release、未 golden promotion、未运行破坏性命令。

Gate：`drawdown_stress NAV-derived metric contract / implementation gate`

---

## 0. 审查范围与方法

### 0.1 规则真源

- `AGENTS.md` 是唯一权威入口；`docs/design.md` 是设计真源；`docs/implementation-control.md` 是实施总控。
- 用中文回答。

### 0.2 审查对象

- Implementation diff：`git diff HEAD` 相对于 accepted plan commit `41485d5` 的全部未提交变更。
- Accepted plan：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- Plan reviews / rereviews：GLM / MiMo 各两份，全部读取。
- Implementation evidence：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-evidence-20260529.md`
- Required truth sources：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`，全部读取。
- Production files：`nav_metrics.py`（新文件，全文阅读）、`data_extractor.py`、`models.py`、`bond_risk_evidence.py`、`extraction_snapshot.py`、`data/__init__.py`、`docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md`。
- Test files：`test_nav_metrics.py`（新文件，全文阅读）、`test_data_extractor.py`、`test_bond_risk_evidence.py`、`test_extraction_snapshot.py`、`test_quality_gate.py`。
- Real run artifacts：snapshot.jsonl、score.json、quality_gate.json，全部读取并验证断言。
- 排除项：`--help`、旧 repo-review/comprehensive audit docs、`docs/tmux-agent-memory-store.md`、`reviews/`。

### 0.3 审查方法

逐项对照 10 个审查焦点，对 implementation diff 做深度 code review。对每个焦点验证：(1) 实现是否与 accepted plan 一致；(2) 公式/逻辑是否正确；(3) 是否存在安全/正确性/数据边界风险；(4) 测试覆盖是否充分。Real run artifacts 交叉验证 implementation evidence 的断言。

---

## 1. Findings

### Finding L1: summary 文本硬编码 "2024" 年份

严重度：低

位置：`fund_agent/fund/extractors/bond_risk_evidence.py` — `_derived_drawdown_metric_group()` 函数

```python
summary="CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤",
```

该 `summary` 使用硬编码 "2024" 而非 `drawdown_metric.period_start.year` 或 `report.key.year`。同一函数的 `period_label` 已正确使用 `drawdown_metric.period_start.isoformat()` / `drawdown_metric.period_end.isoformat()` 做动态拼接，但 summary 遗漏。

影响：当前生产范围仅为 006597/A 2024 年报，硬编码值与实际运行一致。若后续扩展到其他年报年度，summary 会显示错误年份。`period_label` 和 `metric_value` 不受影响，不会导致回撤数值或评分判断出错。

建议修复：将 `"2024"` 替换为 `f"{drawdown_metric.period_start.year}"` 或 `f"{report.key.year}"`。单行改动，无测试影响。

Plan 合规：Plan Slice 2 要求 `_extract_drawdown_stress` 接受可选 `NavMaxDrawdownMetric`，但未显式规定 summary 是否必须动态。这是实现细节遗漏，非 plan 违反。

### Finding I1: anchor note 缺少 series_record_count

严重度：信息（低）

位置：`fund_agent/fund/extractors/bond_risk_evidence.py` — `_derived_nav_metric_anchor_draft()` 函数

Plan 建议的 anchor note 包含 `series_record_count=<series.record_count>`，实现只包含 `record_count=<period_record_count>`，未区分 full series count 和 period-filtered count。

影响：Real smoke 中 full series 有 1807 条记录，period-filtered 有 243 条。当前 note 的 `record_count=243` 明确表示期间过滤后的数量，语义清晰。Full series count 可通过 `date_range_start`/`date_range_end` 推断。不构成正确性问题。

建议：作为后续 provenance 增强可补加，不阻塞当前 gate。

### Finding I2: identity_status 独立拒绝路径缺少专属测试

严重度：信息（低）

位置：`tests/fund/data/test_nav_metrics.py`

`test_calculate_max_drawdown_rejects_raw_unit_or_ineligible_series` 同时修改 `nav_type`、`adjusted_basis` 和 `strong_drawdown_evidence_eligible`，不独立测试 `identity_status != "verified"` 的拒绝。在真实 CSRC EID path 中，raw_unit_nav 系列 `identity_status` 为 `requested_code_only`（非 verified），因此该测试间接覆盖了 identity 检查。但若存在 `accumulated_nav/accumulated_nav/strong_eligible=True` 但 `identity_status != "verified"` 的边界组合（理论上不应出现在 typed contract 中），缺乏专属测试。

影响：当前 typed contract 不产生该组合。不构成安全缺口。

建议：作为后续测试增强可补加，不阻塞当前 gate。

---

## 2. 逐焦点审查结果

### Focus 1: 最大回撤公式正确性

通过。

- 算法：标准 running-peak max drawdown。`drawdown = nav_value / peak_value - 1`。负数表示损失，零表示无回撤。
- 验证测试 `[1.00, 1.10, 1.05, 1.20, 1.08]` → `-0.10`，peak=1.20，trough=1.08。手动推演确认正确。
- 单调路径：`[1.00, 1.01, 1.02]` → `0`，peak/trough 均为首条记录。正确。
- 平局处理：`drawdown < max_drawdown`（严格小于）保留最早谷值。正确。
- 期间过滤：`_period_records()` 按 `period_start <= date <= period_end` inclusive 过滤后按日期升序排序。正确。
- 独立最小记录检查：`_validate_period_records()` 在 period-filtered 结果上独立检查，不依赖 repository 的 full-series `minimum_records`。测试 `test_period_filtered_records_are_checked_independently` 使用 2023 年 30 条记录、2024 年 0 条记录验证。正确。
- 重复日期：`integrity_error` fail-closed。正确。
- 非正 NAV：`integrity_error` fail-closed。正确。
- Real 006597 结果：`-0.0010059518819683125157179982` ≈ `-0.10%`，peak 2024-09-26 / 1.1929，trough 2024-10-09 / 1.1917，243 条期间记录。数值合理，与 fixture 测试一致。

### Focus 2: contract extension 安全性

通过。

- `quantitative_derived` 加入 `BondRiskEvidenceStrength` / `_BOND_RISK_EVIDENCE_STRENGTHS` / `_BOND_RISK_ACCEPTED_STRENGTHS`。
- `derived_metric` 加入 `BondRiskEvidenceMeasurementKind` / `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS`。
- Validator 新增规则：`strength="quantitative_derived"` 必须伴随 `measurement_kind="derived_metric"`；违反者抛出 `ValueError`。
- 测试 `test_quantitative_derived_drawdown_requires_derived_metric_kind` 验证 good case 和 bad case（`actual_metric` / `actual_exposure` / `risk_disclosure` 均被拒绝）。
- Additive Literal 扩展未破坏现有值。schema 保持 `bond_risk_evidence.v1`。

### Focus 3: data boundary

通过。

- `bond_risk_evidence.py` 不导入任何 source / cache / repository 模块。只接收预计算的 `NavMaxDrawdownMetric` 和 `NavDataContractError`。
- `nav_metrics.py` 只消费 `FundNavSeries` typed contract，不读取外部 source / cache / 年报文件。
- `FundDataExtractor` 通过 `_NavSeriesRepository` Protocol 隔离 typed repository。Constructor 注入，默认 `FundNavRepository()`。
- Repository 调用使用显式参数：`fund_code`、`share_class="A"`、`start_date`、`end_date`、`minimum_records=30`、`force_refresh`。无 `extra_payload` / `**kwargs`。
- 非 `bond_fund` 不调用 typed repository。测试 `test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups` 验证 typed repository 注入 `RuntimeError("must not call")` 后仍正常完成。

### Focus 4: share-class boundary

通过。

- Production 使用常量 `_BOND_DRAWDOWN_SHARE_CLASS = "A"`。
- `_load_drawdown_metric_for_bond_fund()` 调用 `load_nav_series(fund_code, share_class="A", ...)`。
- 测试 `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes` 验证 typed repository 只收到一次调用 `("006597", "A", date(2024,1,1), date(2024,12,31), 30, ...)`。
- Real smoke 中 C/E/F 仅用于独立验证 source path 可达，不进入 drawdown_stress metric_value。
- F class 因 source 起始日期 `2024-10-08` 无法覆盖 2024 全年，正确 fail-closed。

### Focus 5: period

通过。

- `date(report_year, 1, 1)` 至 `date(report_year, 12, 31)` inclusive，基于 `report_year` 动态生成。
- `_period_records()` 二次过滤，不依赖 repository 的 `start_date`/`end_date` 窗口裁剪。
- Real smoke 243 条交易日记录落在 2024-01-01..2024-12-31 内。
- 无 trailing future 泄漏。

### Focus 6: derived anchor / provenance

通过（含 I1 备注）。

- `EvidenceAnchor.source_kind="derived"`，`section_id="derived:nav"`，`page_number=None`，`table_id=None`。
- Row locator：`metric:max_drawdown:A:2024-01-01:2024-12-31`。
- Anchor note 包含 21 项 key=value provenance 条目：source / source_name / source_id / source_url / source_query_params / retrieved_at / fund_code / share_class / date_range / record_count / nav_type / adjusted_basis / dividend_adjustment_status / identity_status / calculation_method / peak_date / peak_value / trough_date / trough_value / max_drawdown_ratio。
- `_stable_query_params()` 按 key 排序序列化，确保确定性输出。
- `_build_group_anchors()` 新增 `source_kind` 分支：`section_id.startswith("derived:")` 使用 `"derived"`，否则 `"annual_report"`。不影响现有 annual-report anchor 路径。
- Snapshot 投影：`_first_traceable_anchor()` 优先返回 `source_kind="annual_report"` 的锚点，不存在时返回首个可用锚点。改动窄且向后兼容。测试 `test_build_snapshot_records_projects_derived_bond_risk_anchor_when_no_annual_anchor` 验证 derived-only 场景。已有 annual-report anchor 的场景不受影响。
- Real smoke 确认 snapshot `bond_risk_contract_status="satisfied"`，drawdown_stress 出现在 `bond_risk_satisfied_groups`。

### Focus 7: failure behavior

通过。

- `_load_drawdown_metric_for_bond_fund()` 捕获 `NavDataContractError` 和通用 `Exception`，返回 `(None, error)`。不向上传播。
- 非 `bond_fund` 返回 `(None, None)`，不触发 typed repository 调用。
- 当 `drawdown_metric_error` 非空时，`_extract_drawdown_stress()` 将错误分类映射为 `na_reason`（如 `drawdown_nav_unavailable`），保持 weak/missing 状态。
- 测试 `test_nav_metric_error_keeps_drawdown_control_text_weak` 验证 `unavailable` 错误不提升控制意图文本。
- 测试 `test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak` 验证 `adjustment_basis_unknown` 错误保持回撤组 weak。
- NAV source 或指标失败不改变 extraction_score / quality gate 逻辑；score 仍按结构化 satisfied groups 自然派生 issues。

### Focus 8: score / quality gate / golden 未弱化

通过。

- `extraction_score.py` 未修改。Plan 明确禁止 score threshold / policy / FQ 语义变更，实现遵守。
- `quality_gate.py` / `quality_gate_integration.py` 未修改。
- Golden fixtures 未修改。
- Real run score：`score_applicability_issues` 为空，无 `bond_risk_evidence_missing`。
- Real run quality gate：6 个 issues 中无 `bond_risk_evidence_missing`。FQ2F 来自其他 P1 failed fields（turnover_rate / holder_structure / share_change）。
- Plan 要求的回归测试：已有 `test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group` 覆盖 drawdown_stress 仍为唯一未满足组时 score 继续发出 blocker。Implementation evidence 确认该测试仍通过。

### Focus 9: 测试覆盖

通过（含 I2 备注）。

| 测试文件 | 新增测试数 | 覆盖路径 |
|---|---|---|
| `test_nav_metrics.py` | 6 | 公式、单调零、期间独立检查、重复日期、非正 NAV、raw-unit 拒绝 |
| `test_bond_risk_evidence.py` | 3 | 派生 accepted + provenance、contract 拒绝错误 kind、错误保持 weak |
| `test_data_extractor.py` | 2 | A-share typed 调用、NAV 错误降级 |
| `test_extraction_snapshot.py` | 1 | derived-only anchor 投影 |
| `test_quality_gate.py` | 1 | 七组满足时无 FQ2F bond_risk issue |

Happy path 和 failure path 均有覆盖。Provenance completeness 通过 token-level 断言逐项验证（21 项）。

### Focus 10: docs alignment

通过。

- `docs/design.md`：更新三段，准确描述最大回撤实现、A 类年度期间、派生锚点、fail-closed 行为、volatility/golden 非目标。无过度声明。
- `fund_agent/fund/README.md`：更新 `data/` 分层描述和 FundDataExtractor 行为描述。准确。
- `tests/README.md`：新增 `test_nav_metrics.py` 条目，更新 `test_data_extractor.py` / `test_extraction_snapshot.py` / `test_extraction_score.py` / `test_quality_gate.py` 描述。准确。

---

## 3. Real Run Artifacts 验证

| 断言 | 结果 |
|---|---|
| snapshot `bond_risk_contract_status="satisfied"` | 确认 |
| `bond_risk_satisfied_groups` 包含全部七组含 `drawdown_stress` | 确认 |
| `bond_risk_weak_groups` / `missing_groups` / `ambiguous_groups` 为空 | 确认 |
| score `score_applicability_issues` 无 `bond_risk_evidence_missing` | 确认（issues 为空） |
| quality gate 无 FQ2F `bond_risk_evidence_missing` | 确认 |
| quality gate 剩余 warnings 非本 gate 引入 | 确认（FQ2 turnover/holder/share + FQ2F P1 fails + FQ0 + FQ4） |

---

## 4. Plan 合规总结

| Plan 要求 | 状态 |
|---|---|
| Slice 1: metric helper + fail-closed | 完全实现 |
| Slice 2: contract extension + derived anchor | 完全实现（含 L1） |
| Slice 3: extractor wiring + A-share only | 完全实现 |
| Slice 4: snapshot/score/quality natural path | 完整实现 |
| Slice 5: docs + real evidence | 完全实现 |
| 不修改 score policy / quality gate / golden | 确认 |
| 不在 extractor 内执行 IO | 确认 |
| 不混合 A/C/E/F | 确认 |
| 不实现 volatility | 确认 |
| 弱文本不提升为定量 | 确认 |
| 失败不阻断年报抽取 | 确认 |
| `extraction_snapshot.py` 变更有充分理由 | 确认 |
| `extraction_score.py` 未修改 | 确认 |
| Full validation: ruff all passed, 938 pytest passed, 92.42% coverage | 确认 |

---

## 5. Residual Low Risks

1. **CSRC EID endpoint availability**：外部 source，无 SLA。Source `unavailable` 时 drawdown_stress 保持 weak/missing，score 自然阻断。已通过 fail-closed 测试覆盖。
2. **source_query_params 混合 HTTP params 与 request context**：pre-existing，本 gate 不清理。Anchor note 序列化确定性已通过 `_stable_query_params()` 保证。
3. **F class无法覆盖完整 2024 年度**：source 起始于 2024-10-08，minimum_records 检查正确 fail-closed。F 不用于 006597/A 证据。
4. **CSRC source 当前 scoped 到 006597 家族常量**：metric 对其他基金代码未做通用化验证。后续扩展需独立 gate。
5. **accumulated NAV max drawdown 不等于 total-return index drawdown**：当前 gate 明确不声称 dividend-adjusted / total-return basis。

---

## 6. Verdict

**Accepted / Pass**

无阻塞性发现。一个低严重度硬编码年份问题（L1），可在后续维护中修复。实现严格遵守 accepted plan 全部 slices 和 data boundary 约束，real run artifacts 完全匹配预期断言，测试覆盖充分，score / quality gate / golden 未被弱化。

---

## 7. Self-Check

pass。

- 角色合规：仅做 code review，未编辑代码、未 commit、未 push、未建 PR、未运行破坏性命令。
- 审查范围：仅覆盖 implementation diff 和 real run artifacts，排除无关 untracked 文件。
- Findings 排序：按严重度从高到低。无 P0/P1。
- Verdict 明确：Accepted / Pass。
