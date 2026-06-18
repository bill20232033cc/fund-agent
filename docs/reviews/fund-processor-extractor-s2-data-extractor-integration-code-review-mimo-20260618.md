# Fund Processor/Extractor S2 DataExtractor Integration — Code Review (AgentMiMo)

> Date: 2026-06-18
> Role: AgentMiMo independent code reviewer
> Gate: S2 code review gate
> Status: review complete

## Verdict

PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY

实现正确接入 S1 `FundProcessorRegistry` / `ActiveFundAnnualProcessor`，active_fund 路径完全走 processor output，fail-closed 语义完整，non-active direct legacy path 行为保留，测试充分覆盖 marker attribution 和 registry fail-closed。存在两个非阻塞发现。不得据此声明 readiness/release/parser replacement。

## Review Focus Findings

### Finding 1 — nonblocking — core_risk.v1 fallback condition narrowing

**File:** `fund_agent/fund/data_extractor.py:542`

**Issue:** Plan 要求 `product_essence.v1` 投影出的 `risk_characteristic_text` 字段 `extraction_mode == "missing"` 且 `core_risk.v1` 同名字段有 public value 时做 fallback。实现条件为 `risk_characteristic_text.value is None`，省略了 `extraction_mode` 检查。

**Impact:** 当前 `_field_from_family` 在 value 为 None 时总是设 `extraction_mode="missing"`，所以两个条件等价。但如果未来 `_field_from_family` 语义变化（如 value=None 但 extraction_mode 非 missing），此条件可能产生非预期 fallback。当前无运行时影响。

**Severity:** nonblocking — 当前等价行为正确，可作为后续 S3 hardening 关注点。

### Finding 2 — nonblocking — _field_from_family 返回类型 `ExtractedField[Any]` 与 StructuredFundDataBundle 字段类型不精确

**File:** `fund_agent/fund/data_extractor.py:474-503`

**Issue:** `_field_from_family` 返回 `ExtractedField[Any]`，传入 `StructuredFundDataBundle` 各字段（如 `ExtractedField[dict[str, object]]`）时需 `# type: ignore[arg-type]`。类型安全性依赖 processor 输出值的实际运行时类型。

**Impact:** 运行时无影响。processor output schema 版本化契约确保值类型正确。`# type: ignore` 注释是 S2 bridge 的合理 trade-off。后续可引入泛型约束改善。

**Severity:** nonblocking — 类型擦除不影响运行时正确性。

## Review Focus Verification Matrix

### 1. Implementation matches accepted S2 plan exactly

**PASS.** 逐项核实：

- ✅ Constructor injection: `processor_registry` 可选参数，默认 `FundProcessorRegistry.create_default()`，仅保存不触发 I/O
- ✅ Active fund processor path: `dispatch_key` 构造使用确定性静态 `source_kind="annual_report"`，不从 candidate/fallback 派生
- ✅ Registry resolve → processor.extract → contract_status check → bundle projection
- ✅ Non-active fund `_extract_bundle_direct_legacy_path()` 封装原有逻辑
- ✅ Exact write set 守护：仅 `data_extractor.py` 和 `test_data_extractor.py` 被修改
- ✅ 禁止路径未触碰（verified via `git diff --name-only HEAD`）

### 2. Active_fund path uses FundProcessorRegistry / processor output, no silent fallback

**PASS.** 三重证明：

- ✅ `test_active_fund_uses_processor_path_with_marker_values` — 注入 `_MarkerActiveFundProcessor` 返回独特 marker 值，bundle 14 个字段全部匹配 marker 而非 direct extractor
- ✅ `test_active_fund_unsupported_registry_fails_closed` — `_NeverSupportProcessor.supports()` 返回 False，`resolve()` 抛出 `UnsupportedFundProcessorError`
- ✅ `result.contract_status in ("unsupported", "blocked")` → `RuntimeError`，无 fallback 到 direct path

### 3. Bundle projection preserves field semantics

**PASS.** 逐项核实：

- ✅ **Field values**: `_field_from_family` 正确从 `FundFieldFamilyResult.value[field_name]` 投影
- ✅ **Anchors**: 使用 family-level `FundFieldFamilyResult.anchors`，missing 字段用空 anchors
- ✅ **Missing semantics**: family absent → `"field_family_absent:{field_name}"`；field not in family → `"field_not_in_family:{family_id}:{field_name}"`；`extraction_mode="missing"`
- ✅ **tracking_error**: `_tracking_error_for_fund_type()` 对非指数基金返回 missing，marker test 验证 `"非指数基金不适用跟踪误差"`
- ✅ **source_provenance**: 从 `project_public_source_provenance(report.metadata.source)` 投影，不暴露 None
- ✅ **index_profile**: 来自 `profile_result.index_profile`（S2 residual，记录在 implementation evidence）
- ✅ **bond_risk_evidence**: active fund 继续调用 `extract_bond_risk_evidence()`，返回 `not_applicable_non_bond_fund`（existing test 通过）
- ✅ **core_risk.v1 fallback**: 仅 `risk_characteristic_text` 可从 core_risk fallback，`current_stage.v1` 不投影

### 4. Non-active/unclassified direct legacy path preserves current behavior

**PASS.**

- ✅ `_extract_bundle_direct_legacy_path()` 完整复制原有编排逻辑：`extract_performance()` → `extract_manager_ownership()` → `extract_holdings_share_change()` → drawdown → bond_risk_evidence → `StructuredFundDataBundle`
- ✅ `test_index_fund_direct_path_smoke_test` — index_fund 走 direct path，验证 classified_fund_type 和 tracking_error
- ✅ Bond drawdown typed NAV: `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes` 通过
- ✅ NAV degradation: `test_data_extractor_degrades_nav_failure_without_blocking_annual_report` 通过
- ✅ Repository failure: `test_data_extractor_does_not_mask_repository_failure` 通过
- ✅ Source provenance: 3 个 provenance 测试全部通过

### 5. Tests sufficient

**PASS.**

- ✅ Marker processor attribution: `_MarkerActiveFundProcessor` 注入返回独特 marker，验证 14 个 bundle 字段
- ✅ Unsupported registry fail-closed: `_NeverSupportProcessor` → `UnsupportedFundProcessorError`
- ✅ Index fund direct path smoke test
- ✅ 25 个既有测试全部通过（NAV failure、repo failure、bond drawdown、source provenance 等）
- ✅ 总计 28 passed in 0.41s

### 6. Type errors, runtime bugs, edge cases, public contract drift

**PASS (with nonblocking findings).**

- ✅ `# type: ignore[arg-type]` 注释标注了 S2 bridge 的类型擦除，运行时无影响
- ✅ `profile_result: Any` 类型注解合理（S2 temporary bridge）
- ✅ `_field_from_family` 对 family absent 和 field not in family 都返回正确的 missing field
- ✅ `FundFieldFamilyResult` value 类型为 `dict[str, object]`，`.get()` 调用安全
- ✅ `ruff check` 通过，`git diff --check` 通过
- ⚠️ Finding 1: core_risk.v1 fallback condition narrowing（nonblocking）
- ⚠️ Finding 2: ExtractedField[Any] type erasure（nonblocking）

### 7. No forbidden paths modified, no candidate/parser boundaries crossed

**PASS.**

- ✅ `git diff --name-only HEAD` 仅显示 `fund_agent/fund/data_extractor.py` 和 `tests/fund/test_data_extractor.py`
- ✅ 未触碰 `fund_agent/fund/documents/**`、`fund_agent/service/**`、`fund_agent/host/**`、`fund_agent/agent/**`、`fund_agent/render/**`、`fund_agent/quality/**`、`docs/design.md`、`docs/implementation-control.md`
- ✅ `dispatch_key.source_kind` 使用确定性静态值 `"annual_report"`，不从 candidate status 派生
- ✅ `candidate_boundary=None`（S2 生产路径不使用 candidate boundary）

## Commands Inspected/Run

```
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
# All checks passed!

uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py -v
# 28 passed in 0.41s

git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
# (no output — no whitespace errors)

git diff --name-only HEAD
# fund_agent/fund/data_extractor.py
# tests/fund/test_data_extractor.py

git diff fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
# Full diff reviewed (553 insertions, 31 deletions)
```

## Residual Risk Section

### Residuals Carried Forward (unchanged from implementation evidence)

- Non-active fund processors (index, enhanced_index, bond, QDII, FOF) 未实现
- `index_profile` 仍来自 bootstrap `extract_profile()`；S1 processor field families 不覆盖
- Active path 内存在临时 in-memory profile extraction 重复（bootstrap 分类 + processor 内部分类）；可由 S3 precomputed extraction context 消除
- `current_stage.v1` 和 `core_risk.v1` 的非 fallback 字段不进入 bundle projection
- 未实现 `FundDisclosureDocument` / Docling candidate / pdfplumber candidate / EID XBRL HTML render candidate 的生产路径

### New Residual from Review

- core_risk.v1 fallback 条件可由 `value is None` 加强为显式 `extraction_mode == "missing"` 检查（非阻塞，S3 可处理）
- `_field_from_family` 返回 `ExtractedField[Any]` 的类型擦除可由泛型约束改善（非阻塞）

### No-claim Boundary

不声明 source truth、full field correctness、golden promotion、release readiness 或 parser replacement。
