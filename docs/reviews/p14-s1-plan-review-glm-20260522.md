# P14-S1 Plan Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan 是可实施的，核心决策（FQ2 conditional P1、不扩展 ExtractionMode、comparable scalar-only 子字段、001548 golden-only、stop condition 守卫）均正确且与 AGENTS.md / design.md / implementation-control.md / post-P13 planning 16 条必答约束一致。

两个 low-severity finding 不阻断实施，但应在 implementation 前明确写入 plan 或由 implementer 在 slice 内处理。

## Evidence Used

### Code Facts Verified

| Claim in plan | Verified | Evidence |
|---|---|---|
| `COMPARABLE_SUB_FIELDS_BY_FIELD` 不含 `index_profile` / `tracking_error` | ✅ | `extraction_snapshot.py:47-60` 仅含 `basic_identity`, `benchmark`, `nav_benchmark_performance`, `classified_fund_type` |
| `FIELD_PRIORITY_BY_NAME` 不含这两个字段 | ✅ | `extraction_score.py:40-55` 无 `index_profile` / `tracking_error` 条目 |
| `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]` | ✅ | `extractors/models.py:10` |
| `001548` 在 `reports/golden-answers/golden-answer.json` 和 `docs/code_20260519.csv` 中 | ✅ | JSON 含 6 只基金包括 001548；CSV 含 `天弘上证50ETF联接A,001548,国内股票类` |
| `510300` 不在 CSV / strict golden 中 | ✅ | CSV 无 510300；golden-answer.json 不含 510300 |
| `510300` 在 `test_p1_sample_matrix.py` 中已有 tracking_error 断言 | ✅ | line 15: `_SAMPLE_FUNDS` 含 `("510300", "宽基指数")`；line 276: `tracking_error.extraction_mode == "direct"` |
| `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt` 存在 | ✅ | 637 bytes, 15 行, 含 §1/§2 但无 §3 |
| `161725` 不在 sample matrix 中 | ✅ | 仅在 `test_profile.py` 中使用 |
| `_comparable_values_for_field(field_name, extracted_field.value)` 传入 dataclass 会 `.get()` 失败 | ✅ | `extraction_snapshot.py:829` 传 `extracted_field.value`；`1032` 调 `value.get(sub_field)`；dataclass 无 `.get()` |
| `_sub_field_value` 调 `extracted_field.value.get(value_key)` 对 dataclass 同样失败 | ✅ | `golden_prefill.py:304-327` |
| `SnapshotRecord` 每条记录携带 `classified_fund_type` | ✅ | `extraction_snapshot.py:178`；`_unique_optional_text(records, "classified_fund_type")` 可从单条记录获取 |

### Dataclass Field Verification

Plan 选择的 comparable sub-fields 全部验证为标量类型：

**`IndexProfileValue`**（`extractors/models.py:88-130`，13 字段）：

| Plan 选定子字段 | 类型 | 标量 |
|---|---|---|
| `benchmark_text` | `str \| None` | ✅ |
| `benchmark_identity_status` | `Literal[...]` | ✅ |
| `benchmark_index_name` | `str \| None` | ✅ |
| `benchmark_index_code` | `str \| None` | ✅ |
| `methodology_availability` | `Literal[...]` | ✅ |
| `constituents_availability` | `Literal[...]` | ✅ |
| `source_tier` | `Literal[...]` | ✅ |

Plan 排除的嵌套字段 `benchmark_component_text: tuple[str, ...]` 和 `missing_reasons: tuple[str, ...]` 会被 `_comparable_scalar` 的 `isinstance(value, (..., tuple, ...))` 过滤。排除决策正确。

**`TrackingErrorValue`**（`extractors/models.py:133-177`，19 字段）：

| Plan 选定子字段 | 类型 | 标量 |
|---|---|---|
| `value_text` | `str` | ✅ |
| `period_label` | `str` | ✅ |
| `annualized` | `bool` | ✅（转文本） |
| `source_type` | `Literal[...]` | ✅ |
| `calculation_method` | `Literal[...]` | ✅ |
| `benchmark_identity_status` | `Literal[...]` | ✅ |
| `benchmark_index_name` | `str \| None` | ✅ |
| `benchmark_index_code` | `str \| None` | ✅ |
| `frequency` | `Literal[...]` | ✅ |
| `input_period_complete` | `bool` | ✅（转文本） |

排除 `value: Decimal` 的决策正确：`value_text` 保留披露原文，避免 Decimal 格式化漂移。排除 `fund_series_source`, `index_series_source`, `observation_count`, `annualization_factor` 正确——这些字段属于 calculated series 范围。

## Findings

### F1 — LOW：Bool 子字段 comparable 文本序列化应在 plan 中显式说明

`TrackingErrorValue.annualized`（`bool`）和 `input_period_complete`（`bool`）被选入 comparable sub-fields。`_comparable_scalar` 对 bool 值执行 `str(value)`，产出 Python 原生 `"True"` / `"False"`（首字母大写）。Golden answer 比对、测试断言和 golden prefill 底稿必须对齐此表示。

Plan Slice A 提到"including bool values as deterministic text via existing scalar conversion"，但没有明确输出格式。Implementer 和 golden answer 作者需要知道确切字符串。

**Required change in plan：**

Slice A 测试期望断言中增加显式说明：

```text
bool comparable sub-fields serialize as str(True)="True" and str(False)="False".
Golden answer expected_value for bool sub-fields must match this exact representation.
```

### F2 — LOW：Slice D 应显式说明 enhanced-index fixture builder 需要 §3 内容

现有 `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt`（161725）只含 §1/§2。Plan Slice D 提议在 `test_p1_sample_matrix.py` 中增加 `161725` enhanced_index case，且包含 tracking_error 断言。但 tracking_error 提取依赖 §3 年报表现数据。

Plan 说"Build report text by extending the current `_build_report()` or adding a specific enhanced-index fixture builder"，但没有明确指出 fixture 必须包含 §3。

**Required change in plan：**

Slice D 增加显式要求：

```text
The enhanced-index fixture builder for 161725 must include:
- §1/§2: for fund type classification (指数型 + 基金名称含"增强") and index_profile extraction
- §3: for tracking_error direct-disclosure extraction (e.g. "报告期年化跟踪误差：1.23%")
```

## Positive Observations

1. **`SnapshotRecord.classified_fund_type` 验证通过**：每条 snapshot 记录携带 `classified_fund_type`（line 178），plan 提出的 `_is_non_applicable_index_quality_record(record)` 可直接通过 `record.get("classified_fund_type")` 获取基金类型，不需要额外的 fund-type mapping 步骤。`score_snapshot_records()` 的 per-record 过滤是可行的。

2. **Stop condition 设计合理**：Slice C 对 golden production row 设置了"如果 001548 当前 extractor 输出不匹配 proposed values，stop before editing production golden files"。这是正确的 fail-safe 设计。

3. **FQ2 条件化适用性矩阵完整**：`index_fund` / `enhanced_index` 适用；`active_fund` / `bond_fund` / `qdii_fund` / `fof_fund` 排除；`classified_fund_type` 缺失/未知时保守计入。这防止了分类失败的静默隐藏。

4. **`_comparable_values_for_field` dataclass gap 正确识别**：Plan 准确定位了 `extraction_snapshot.py:829` 传 `extracted_field.value`（dataclass）给期望 dict 的函数，以及 `golden_prefill.py` 的 `value.get()` 调用。提出的 `_value_mapping` helper 方案可行。

5. **16 条必答约束全覆盖**：denominator 定义、字段范围、FQ2 priority、comparable sub-fields、golden correctness、适用性矩阵、ExtractionMode 决策、缺失/冲突语义、质量门控边界、fixture 策略、validation / exit criteria、behavior assertions、source boundary、failure taxonomy、docs decision、positive acceptance criteria 均有明确回答。

## Boundary Check

| Boundary / constraint | Plan compliance |
|---|---|
| FundDocumentRepository only | ✅ 无直接 PDF/cache/source 访问 |
| No Dayu runtime | ✅ 无 Host/Engine/tool loop 依赖 |
| No LLM / Evidence Confirm | ✅ 纯确定性质量机制 |
| No RR-13 / repo-audit | ✅ 明确排除 |
| No calculated tracking error | ✅ 无 time series 计算 |
| No source adapter | ✅ 无外部指数序列 |
| No methodology / constituents extraction | ✅ 子字段排除设计正确 |
| No QDII subtype redesign | ✅ 只认 index_fund / enhanced_index 适用 |
| Fund Capability ownership | ✅ 所有改动在 fund/ 层 |
| Deterministic MVP | ✅ 无非确定性引入 |

## Residual Risk Assessment

Plan 的 residual 表覆盖完整。重点确认：

- `tracking_error` production golden for `001548` 的 stop-condition risk 由 Slice C 的 fail-safe 守卫。Owner 正确。
- FQ2 conditional filtering 对 unknown fund type 的保守处理在 plan 中有明确 state transition。风险可控。
- `001548` index profile expected values 的 stop-condition risk 与 golden production 同理。

## Required Changes Summary

| Finding | Severity | Required change | Where in plan |
|---|---|---|---|
| F1 | LOW | 明确 bool 子字段序列化为 `"True"` / `"False"` | Slice A 测试期望 |
| F2 | LOW | 明确 enhanced-index fixture builder 必须含 §3 | Slice D fixture 要求 |

两个 finding 均不阻断实施。Controller 可选择在 plan review judgment 中注明"implementer 必须在 Slice A/D 中体现"，或要求 plan revision 后再进入 implementation。
