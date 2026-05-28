# Drawdown Stress NAV-Derived Metric Implementation Plan Review — MiMo

日期：2026-05-29

角色：plan review worker only。不实施、不 commit、不 push、不 PR、不 merge。

## Reviewed Target

`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`

## Scope

对 drawdown_stress NAV-derived metric 实施计划进行对抗性审查，覆盖 10 个审查焦点：

1. max drawdown alone 作为最小 accepted metric 的充分性
2. 006597/A 作为 main evidence、不混合 A/C/E/F 的正确性
3. 2024-01-01..2024-12-31 作为 006597/2024 证据期间的正确性
4. 公式/fail-closed 设计对重复、缺失、不足、不可用等场景的处理
5. **关键：additive enum extension 在 bond_risk_evidence.v1 中无 schema version bump 是否可接受**
6. derived anchors 的 section_id/source_kind 与现有 validator/snapshot/report 语义的兼容性
7. 数据边界：只消费 FundNavRepository.load_nav_series() 的正确性
8. 测试是否足以证明 score 自然停止发出 bond_risk_evidence_missing
9. 允许文件范围是否合理
10. blocking vs non-blocking findings 分类

## Assumptions Tested

1. `BondRiskEvidenceStrength` 和 `BondRiskEvidenceMeasurementKind` 的 Literal extension 不破坏现有 validator 逻辑。
2. `_build_group_anchors()` 当前硬编码 `source_kind="annual_report"`；plan 的 `section_id.startswith("derived:")` 行为变更是安全的。
3. `_validate_bond_risk_status_strength()` 的 `accepted` 分支仅检查 strength ∈ accepted set，不额外检查 measurement_kind。
4. `FundNavRepository.load_nav_series()` 返回完整 series 而非窗口裁剪 series，metric helper 必须二次过滤。
5. CSRC EID 006597/A 2024 年报期间有足够交易日记录（≥30）。
6. `NavDataContractError` taxonomy 足以覆盖所有 metric helper fail-closed 场景。
7. 同步 `extract_bond_risk_evidence()` 加 optional drawdown metric 参数不会破坏现有调用方。

## Findings

### 01-未修复-中-accepted status + quantitative_derived + 非 derived_metric measurement_kind 未被 validator 拦截

- **位置**: Core Decisions #1, Contract Extension, Tests #9
- **问题类型**: 契约缺失
- **当前写法**: plan 扩展 `_BOND_RISK_ACCEPTED_STRENGTHS` 包含 `quantitative_derived`，扩展 `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS` 包含 `derived_metric`，并在 `_validate_bond_risk_status_strength()` 中允许 `status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="derived_metric"`。
- **反例/失败场景**: 当前 `_validate_bond_risk_status_strength()` 的 `accepted` 分支只检查 `strength ∈ accepted_set`（`bond_risk_evidence.py:285`），**不检查 measurement_kind**。扩展后，`status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"` 也会通过验证——这个组合语义不一致（派生指标不应声称 actual_metric）。
- **为什么有问题**: 任何 combination 都能通过 validator，削弱了 `quantitative_derived` / `derived_metric` 的语义区分价值。implementation worker 可能构造出语义矛盾的 record 且测试不拦截。
- **直接证据**: `bond_risk_evidence.py:272-299`——`_validate_bond_risk_status_strength()` 的 `accepted` 分支仅检查 strength，不检查 measurement_kind。plan 的 contract extension 描述未提及此约束。
- **影响**: implementation worker 可能生成 `quantitative_derived + actual_metric` 的 record，reviewer 需要额外人工检查。
- **建议改法和验证点**: 在 `_validate_bond_risk_status_strength()` 中为 `quantitative_derived` 增加 measurement_kind 约束：当 `strength="quantitative_derived"` 时，`measurement_kind` 必须为 `"derived_metric"`。在 test #9 中增加 reject case：`status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"` 应被拒绝。
- **修复风险（低/中/高）**: 低——只增加一行 if 条件和一个 test case。
- **严重程度（低/中/高/严重）**: 中——不影响 happy path 但削弱了 contract 的防御价值。

### 02-未修复-低-period 后记录数不足时 repository 与 helper 双重 minimum_records 检查的语义差异

- **位置**: Core Decisions #3, Fail-Closed Behavior table, Data Boundary
- **问题类型**: 契约缺失
- **当前写法**: plan 的 fail-closed 表列出 "period-filtered records < 30 → reject; na_reason=drawdown_period_insufficient_records"。同时 Slice 3 要求 repository 调用传 `minimum_records=30`。
- **反例/失败场景**: `FundNavRepository.load_nav_series()` 的 `minimum_records` 检查在 `FundNavSeries.__post_init__` 中执行（`nav_models.py:523`），校验的是**全 series 记录数**，不是 period-filtered 记录数。如果全 series 有 200 条但 period-filtered 后只有 25 条，repository 不会拒绝（200 ≥ 30），但 helper 必须拒绝（25 < 30）。plan 的 fail-closed 表正确描述了 helper 行为，但 Slice 3 的 repository 调用传 `minimum_records=30` 是冗余的——它检查的是不同维度。
- **为什么有问题**: 不会导致错误，但 implementation worker 可能困惑于两个 `minimum_records` 的语义差异，甚至在 helper 中省略 period-filtered 检查。
- **直接证据**: `nav_models.py:523`——`if minimum_records is not None and len(records) < minimum_records`——检查的是全 series `len(records)`。plan Slice 3 要求 `minimum_records=30` 传给 repository。
- **影响**: 低——不会导致错误行为，但可能造成 implementation 困惑。
- **建议改法和验证点**: 在 plan 中明确注释 repository 的 `minimum_records` 是 early sanity check，metric helper 的 `minimum_records` 是 period-filtered 后的 final check。两者独立，helper 不依赖 repository 的检查结果。在 test 中覆盖：repository 返回 ≥30 条全 series 但 period-filtered 后 <30 条的场景。
- **修复风险（低/中/高）**: 低——只增加注释和一个 test case。
- **严重程度（低/中/严重）**: 低——语义清晰度问题，不影响正确性。

### 03-未修复-低-Slice 4 测试中 extraction_snapshot.py 和 extraction_score.py 的修改边界未明确

- **位置**: Slices #4, Tests File Scope
- **问题类型**: 切片过粗
- **当前写法**: Slice 4 允许修改 `tests/fund/test_extraction_snapshot.py`、`tests/fund/test_extraction_score.py`、`tests/fund/test_quality_gate.py`，并允许 `fund_agent/fund/extraction_snapshot.py` 仅当 derived anchors 需要 source_kind-aware first-anchor selection 时。
- **反例/失败场景**: `extraction_snapshot.py` 当前在 bond_risk_evidence 的 snapshot record 生成中，将 anchors 投影到 snapshot 字段。如果 `EvidenceAnchor.source_kind` 从 `"annual_report"` 变为 `"derived"`，snapshot 投影逻辑是否会正确处理？plan 说 "snapshot only projects the first anchor/ref into section_id/page/table/row_id"——这是对的，但 implementation worker 需要验证 snapshot 投影逻辑不假设 `source_kind="annual_report"`。
- **为什么有问题**: 如果 snapshot 投影逻辑硬编码了 `source_kind` 假设，derived anchors 可能被错误投影或跳过。
- **直接证据**: `extraction_snapshot.py:45`——`("risk", "bond_risk_evidence")` 在 `SNAPSHOT_FIELD_ORDER` 中；snapshot 投影逻辑需要读取 `EvidenceAnchor` 字段。
- **影响**: 低——snapshot 投影逻辑大概率只读 `section_id`/`page_number`/`table_id`/`row_locator`，不检查 `source_kind`。但需要 implementation worker 验证。
- **建议改法和验证点**: 在 Slice 4 的 stop condition 中增加：如果 snapshot 投影逻辑对 `source_kind` 有假设，停止并报告 controller。
- **修复风险（低/中/高）**: 低——增加一行 stop condition。
- **严重程度（低/中/严重）**: 低——大概率不需要修改 snapshot 代码。

### 04-未修复-低-real CSRC EID smoke 命令中 force_refresh=True 的缓存影响

- **位置**: Validation Commands, Slice 5
- **问题类型**: 其它
- **当前写法**: real smoke 命令使用 `force_refresh=True`，real 006597 extraction 也使用 `--force-refresh`。
- **反例/失败场景**: CSRC EID endpoint 没有 SLA（plan Residual Risks 已承认）。如果 endpoint 在 implementation worker 运行时不可用，real smoke 会失败。plan 已将此归类为 residual risk，正确。
- **为什么有问题**: 不是 plan 设计问题，而是运行时风险。
- **直接证据**: plan Residual Risks: "CSRC EID endpoint has no SLA; source unavailable should keep blocker rather than accepting weak data."
- **影响**: 低——plan 已正确处理为 residual。
- **建议改法和验证点**: 无需修改。implementation worker 应在 real smoke 失败时报告为 validation residual，不 paper over。
- **修复风险（低/中/高）**: 低。
- **严重程度（低/中/严重）**: 低——已归类为 residual。

## Open Questions

无。所有 10 个审查焦点已通过 evidence-based 分析覆盖。

## Residual Risks

| Residual | Owner / tracking destination |
|---|---|
| CSRC EID endpoint has no SLA | 本 gate residual；source unavailable 应保持 blocker |
| volatility 不在本 gate 实现 | 后续独立 gate |
| CSRC EID source scoped to 006597 family constants | future NAV source generalization gate |
| `source_query_params` mixes HTTP params and request context | future NAV provenance cleanup gate |
| accumulated_nav 不等同于 total-return index | accepted limitation，不 relabel |

## Reviewer Self-Check

- [x] reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] findings 均 evidence-based、adversarial、可执行，无 style/nit/speculation
- [x] open questions、residual risks 与 findings 分开
- [x] conclusion 只能是 `pass`、`pass-with-risks` 或 `fail`
- [x] output path 使用本机系统时钟生成的 timestamp，匹配 artifact path 格式

## Conclusion

**pass-with-risks**

Plan 整体设计扎实：

- **Contract extension 安全**：`quantitative_derived` / `derived_metric` 的 additive Literal extension 不改变 dataclass 字段形状，不破坏 snapshot schema，不弱化 FQ0-FQ6。`_validate_bond_risk_status_strength()` 的 `accepted` 分支仅检查 strength ∈ accepted set，新增值通过 frozenset 扩展自然被接受。score / quality gate 消费的是结构化 `satisfied_group_ids`，不依赖具体 strength/measurement_kind 值。
- **Data boundary 正确**：只消费 `FundNavRepository.load_nav_series()`，不直接访问 CSRC EID / Akshare / stock-sdk / cache。
- **Fail-closed 完整**：覆盖所有 source failure、metric input failure 和 calculation failure 场景。
- **Slicing 合理**：5 个 slice 从纯 data → contract → wiring → integration → docs，依赖正确。
- **006597/A 不混合正确**：A/C/E/F 份额分离，不构造 product-level NAV。

唯一需要 implementation 前修复的 finding 是 #01：`quantitative_derived` + `非 derived_metric measurement_kind` 的 validator 约束缺失。修复成本低（一行 if + 一个 test case），不影响 plan 整体结构。其余 findings 为低严重度，implementation worker 可按 plan 直接推进。
