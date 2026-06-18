# Fund Processor/Extractor S2 DataExtractor Integration — Implementation Evidence

> Date: 2026-06-18
> Role: AgentDS implementation worker
> Gate: S2 implementation gate
> Status: implementation complete, tests pass, stop condition met

## Verdict

S2_IMPLEMENTATION_COMPLETE_NOT_READY

S2 DataExtractor Integration 已实现：`FundDataExtractor.extract()` 在 active_fund 时通过 processor registry 路径走 `ActiveFundAnnualProcessor`，非 active fund 保留 direct legacy path。不得据此声明 readiness/release/parser replacement。

## Files Changed

- `fund_agent/fund/data_extractor.py` — 新增 processor registry injection、active_fund processor 路径、bundle projection helpers、direct legacy path helper
- `tests/fund/test_data_extractor.py` — 新增 marker processor proof test、unsupported registry fail-closed test、index_fund direct path smoke test；更新 anchor assertion 以适配 family-level anchors

No other files were modified.

## Implementation Summary

### Constructor Injection

`FundDataExtractor.__init__()` 新增可选参数 `processor_registry`，默认值为 `FundProcessorRegistry.create_default()`。仅在构造函数中保存，不触发 I/O。

### Active Fund Processor Path

`FundDataExtractor.extract()` 在 `classified_fund_type == "active_fund"` 时调用 `_extract_active_fund_via_processor()`：

1. 构造 `FundProcessorDispatchKey(fund_type="active_fund", report_type="annual_report", intermediate_kind="parsed_annual_report.v1", source_kind="annual_report", ...)`
2. 通过 `self._processor_registry.resolve(dispatch_key)` 获取 processor
3. 构造 `FundProcessorInput` 并调用 `processor.extract()`
4. 若 `result.contract_status in ("unsupported", "blocked")` 则抛出 `RuntimeError` fail-closed
5. 调用 `_active_processor_result_to_bundle()` 投影 `StructuredFundDataBundle`

Bootstrap 分类仍通过 `extract_profile(report)` → `_classified_fund_type()` 完成（S2 temporary bridge）。

### Bundle Projection Rules

新增 helpers：
- `_field_family_by_id()` — 按 field_family_id 索引字段族
- `_field_from_family()` — 从字段族 value 投影单个 `ExtractedField`，缺失时返回 `extraction_mode="missing"`
- `_active_processor_result_to_bundle()` — 完整投影逻辑

投影映射：

| Field Family | Bundle Fields |
|---|---|
| `product_essence.v1` | `basic_identity`, `product_profile`, `benchmark`, `risk_characteristic_text` |
| `return_attribution.v1` | `fee_schedule`, `nav_benchmark_performance`, `tracking_error`（经 `_tracking_error_for_fund_type()`） |
| `manager_profile.v1` | `portfolio_managers`, `turnover_rate`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot` |
| `investor_experience.v1` | `investor_return`, `holder_structure`, `share_change` |
| `core_risk.v1` | 仅 `risk_characteristic_text` fallback（当 `product_essence.v1` 同名字段缺失且有 public value 时） |
| `current_stage.v1` | informational/redundant — 不投影 |

不来自 processor 的字段：
- `index_profile` — 来自 bootstrap `profile_result.index_profile`（S2 residual）
- `bond_risk_evidence` — 继续调用 `extract_bond_risk_evidence()`；active fund 返回 `not_applicable_non_bond_fund`
- `nav_data` — 继续通过 `_load_nav_data_or_unavailable()` 加载
- `source_provenance` — 继续从 `ParsedAnnualReport.metadata.source` 投影

每个从 family 投影出的 `ExtractedField` 使用 `FundFieldFamilyResult.anchors`（family-level anchors），缺失字段返回 `extraction_mode="missing"` 且 note 包含 source family/gap 信息。

### Non-active Fund Direct Legacy Path

`_extract_bundle_direct_legacy_path()` 封装原有 direct extractor 编排逻辑，用于：
- `index_fund`、`enhanced_index`、`bond_fund`、`qdii_fund`、`fof_fund`
- unclassified fund type

行为与 S2 前完全一致。

### Fail-closed Behavior

- **Registry 无 processor**：`UnsupportedFundProcessorError` 向上传播，不 fallback
- **Processor result unsupported/blocked**：抛出 `RuntimeError`，不 fallback
- **`processor.extract()` 意外异常**：自然向上传播，不吞掉
- **Repository failure**：保持向上抛出
- **NAV provider failure**：保持 `nav_unavailable` 降级
- **Bond drawdown typed NAV failure**：保持 weak/missing evidence 语义

## Tests Run

```
uv run pytest tests/fund/processors/test_registry.py \
  tests/fund/processors/test_active_annual_processor.py \
  tests/fund/test_data_extractor.py -v

============================== 28 passed in 0.46s ==============================
```

### New Focused Tests

1. **`test_active_fund_uses_processor_path_with_marker_values`** — 注入返回已知 marker 值的自定义 `_MarkerActiveFundProcessor`，验证 bundle 字段包含 marker 值而非 direct extractor 结果。证明 fields 来自 processor 路径。

2. **`test_active_fund_unsupported_registry_fails_closed`** — 注入只含 `_NeverSupportProcessor` 的 registry，验证 active fund extract 抛出 `UnsupportedFundProcessorError`。

3. **`test_index_fund_direct_path_smoke_test`** — 指数基金走 direct legacy path，验证返回完整 bundle 且分类正确。

### Existing Tests Preserved

所有现有 25 个测试继续通过，包括：
- NAV failure degradation
- Repository failure propagation
- Non-bond bond risk evidence does not scan groups
- Bond fund typed NAV drawdown behavior
- Source provenance projection (primary, fallback, missing category)
- Registry and processor unit tests

### Static Analysis

```
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
All checks passed!

git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py \
  fund_agent/fund/README.md docs/reviews/...implementation-evidence-20260618.md
(no output — no whitespace errors)
```

## Residuals Carried Forward

- Non-active fund processors（index、enhanced_index、bond、QDII、FOF）未实现
- `index_profile` 仍来自 bootstrap `extract_profile()`；S1 processor field families 不覆盖
- Active path 内存在临时 in-memory profile extraction 重复（bootstrap 分类 + processor 内部分类）；可由 S3 precomputed extraction context 消除
- `current_stage.v1` 和 `core_risk.v1` 的非 fallback 字段不进入 bundle projection
- 未实现 `FundDisclosureDocument` / Docling candidate / pdfplumber candidate / EID XBRL HTML render candidate 的生产路径
- 不声明 source truth、full field correctness、golden promotion、release readiness

## Git Status

```
 M fund_agent/fund/data_extractor.py
 M tests/fund/test_data_extractor.py
?? docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md
```

## Stop Condition

Implementation worker stopped after:
1. Code and tests within exact write set
2. All focused tests and static checks passed and recorded
3. Implementation evidence artifact written
4. `git status --short` captured

No commit, push, PR, merge, or readiness action was taken.
