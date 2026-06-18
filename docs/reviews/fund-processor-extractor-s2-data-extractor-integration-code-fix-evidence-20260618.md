# Fund Processor/Extractor S2 DataExtractor Integration — Code Fix Evidence

> Date: 2026-06-18
> Role: AgentDS fix worker
> Gate: S2 code fix gate
> Status: fix complete, all validation passed

## Verdict

S2_CODE_FIX_COMPLETE_NOT_READY

所有 4 项 controller accepted findings 已处置：2 项 blocking 已修复，2 项 nonblocking 已按指示处理。不得据此声明 readiness/release/commit/push/PR。

## Findings Fixed

### Finding 1 — blocking — identity drift (Codex #1)

**Files:** `fund_agent/fund/data_extractor.py`, `tests/fund/test_data_extractor.py`

**Root cause:** `_active_processor_result_to_bundle()` 使用外层请求参数 `fund_code`/`report_year` 写入 bundle 顶层身份，而非已加载年报或 processor result 的身份。当 repository 或 processor 返回与请求不一致的身份时，bundle 会输出请求身份 + 其他基金证据的静默串联。

**Fixes applied:**

1. 新增 `_validate_processor_result_identity()` 函数（`data_extractor.py` 行 506-547）：逐字段校验 `result.fund_code`、`result.report_year`、`result.fund_type`、`result.report_type`、`result.input_intermediate_kind` 与 `dispatch_key` 一致；任一不匹配抛出 `RuntimeError` fail-closed。

2. `_extract_active_fund_via_processor()` 内：
   - `_load_drawdown_metric_for_bond_fund()` 调用改为使用 `report.key.fund_code` / `report.key.year`（而非外层 `fund_code`/`report_year`）
   - contract_status 检查后立即调用 `_validate_processor_result_identity(result, dispatch_key)`
   - `_active_processor_result_to_bundle()` 调用移除 `fund_code`/`report_year` 参数

3. `_active_processor_result_to_bundle()` 签名移除 `fund_code`/`report_year` 参数，bundle 顶层身份使用 `result.fund_code` / `result.report_year`（已通过身份校验的 processor 结果身份）。

4. 新增测试：
   - `test_active_fund_processor_mismatched_identity_fails_closed` — `_MismatchedIdentityProcessor` 返回 `fund_code="999999"`，验证 active path 抛出 `RuntimeError("Processor result identity mismatch")` 而非静默输出错误 bundle
   - `test_active_fund_bundle_uses_report_identity_not_request_identity` — repository 返回 `fund_code="110011"` 年报但请求参数为 `"999999"`，验证 `bundle.fund_code == "110011"`（来自已加载年报/processor identity）

### Finding 2 — blocking — Fund README stale (Codex #2)

**File:** `fund_agent/fund/README.md`

**Changes:**

- 行 77 区域：原「该 processor 尚未接入 `FundDataExtractor.extract()` 默认生产 facade」更新为明确 S2 已接入：active fund annual 路径通过 `FundProcessorRegistry` / `ActiveFundAnnualProcessor` 投影 bundle；非 active/unclassified 保留 S2 residual direct legacy path
- 行 111 区域：`FundDataExtractor.extract()` 描述更新为反映 S2 行为 — active fund 已覆盖字段来自 processor 输出而非窄 extractor 透传

### Finding 3 — nonblocking — core_risk fallback condition (Codex #3 / MiMo #1)

**File:** `fund_agent/fund/data_extractor.py`（`_active_processor_result_to_bundle` 内）

**Change:** fallback 条件从 `risk_characteristic_text.value is None and core_risk is not None` 加强为 `risk_characteristic_text.extraction_mode == "missing" and risk_characteristic_text.value is None and core_risk is not None`。

当前 `_field_from_family()` 对 value=None 总是设 `extraction_mode="missing"`，二者等价；加强后即使未来 `_field_from_family` 语义变化（value=None 但 extraction_mode 非 missing），fallback 也不会误触发。

### Finding 4 — nonblocking — ExtractedField[Any] type erasure (Codex #4 / MiMo #2)

**Disposition:** no required fix per controller instruction. Recorded as nonblocking residual.

`_field_from_family()` 返回 `ExtractedField[Any]`，传入 `StructuredFundDataBundle` 各字段时需 `# type: ignore[arg-type]`。运行时无影响：processor output schema 版本化契约确保值类型正确。后续可由泛型约束改善。

## Residuals

- Non-active fund processors (index, enhanced_index, bond, QDII, FOF) 未实现
- `index_profile` 仍来自 bootstrap `extract_profile()`（S2 residual）
- Active path 内存在临时 in-memory profile extraction 重复（bootstrap 分类 + processor 内部分类）
- `current_stage.v1` 和 `core_risk.v1` 的非 fallback 字段不进入 bundle projection
- `_field_from_family` 返回 `ExtractedField[Any]` 的类型擦除（nonblocking，S3 可改善）
- 未实现 `FundDisclosureDocument` / Docling candidate / pdfplumber candidate / EID XBRL HTML render candidate 的生产路径

## Files Changed

- `fund_agent/fund/data_extractor.py` — 新增 `_validate_processor_result_identity()`，修复 identity drift，加强 core_risk fallback 条件
- `tests/fund/test_data_extractor.py` — 新增 `_MismatchedIdentityProcessor`、`test_active_fund_processor_mismatched_identity_fails_closed`、`test_active_fund_bundle_uses_report_identity_not_request_identity`
- `fund_agent/fund/README.md` — 更新 S2 active fund processor 路径和 `FundDataExtractor.extract()` 行为描述

## Validation

### Test Results

```
uv run pytest tests/fund/processors/test_registry.py \
  tests/fund/processors/test_active_annual_processor.py \
  tests/fund/test_data_extractor.py -v

============================== 30 passed in 0.80s ==============================
```

30 passed (28 existing + 2 new identity drift tests)，0 failed。

### Static Analysis

```
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
All checks passed!
```

### Whitespace Check

```
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py \
  fund_agent/fund/README.md \
  docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md \
  docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix-evidence-20260618.md
(no output — no whitespace errors)
```

## Git Status

```
 M fund_agent/fund/README.md
 M fund_agent/fund/data_extractor.py
 M tests/fund/test_data_extractor.py
?? docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix-evidence-20260618.md
```

## Stop Condition

Fix worker stopped after:
1. All 4 accepted findings addressed within allow write set
2. All tests pass (30/30)
3. Static analysis and whitespace checks pass
4. Evidence artifact written

No commit, push, PR, merge, or readiness action was taken.
