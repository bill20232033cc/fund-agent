# NAV Source Adapter Typed Contract — Slice 1a Re-Review

日期：2026-05-28

Re-review agent：AgentMiMo (code review agent)

Work unit：NAV repository/source adapter typed contract implementation gate

Gate：Slice 1a re-review after accepted code review fixes

## Disposition

**accepted**

全部 7 项 re-review 验证标准通过。Accepted findings 已关闭，fix 未引入回归或越界。

---

## Verification Matrix

### 1. identity_mismatch 直接测试

- **标准**：identity mismatch direct test exists and asserts category identity_mismatch。
- **证据**：`tests/fund/data/test_nav_repository_contract.py:385-401`
  - `test_identity_mismatch_raises_identity_mismatch` 构造 `identity_status="identity_mismatch"` 的 series。
  - 断言 `exc_info.value.category == "identity_mismatch"`。
- **判定**：通过。

### 2. empty records 直接测试

- **标准**：empty records direct test exists and asserts category not_found without helper default substitution。
- **证据**：`tests/fund/data/test_nav_repository_contract.py:321-353`
  - `test_empty_records_raises_not_found` 直接构造 `FundNavSeries(records=(), ...)`，不使用 `_nav_series` helper，确保空 tuple 不被默认记录替换。
  - 断言 `exc_info.value.category == "not_found"`。
- **判定**：通过。

### 3. nav_type unknown 直接测试

- **标准**：nav type unknown direct test exists and asserts category schema_drift。
- **证据**：`tests/fund/data/test_nav_repository_contract.py:427-447`
  - `test_nav_type_unknown_raises_schema_drift` 构造 `nav_type="unknown"` 的 series。
  - 断言 `exc_info.value.category == "schema_drift"`。
- **判定**：通过。

### 4. share_class mismatch integrity_error 注释

- **标准**：share class mismatch integrity_error rationale comment is present and coherent。
- **证据**：`fund_agent/fund/data/nav_models.py:406-408`
  - 注释内容："series identity 已在 source/share mapping 层表达；单条记录份额串线代表同一 series 内部数据完整性破坏，因此归类为 integrity_error。"
  - 理由清晰：identity 在 mapping 层处理，record-level share_class 不一致属于 series 内部完整性问题，不归为 identity_mismatch。
- **判定**：通过。

### 5. share_class mismatch 测试聚焦性

- **标准**：share class mismatch test remains focused with explicit nav_type and adjusted_basis。
- **证据**：`tests/fund/data/test_nav_repository_contract.py:369-382`
  - `test_record_share_class_mismatch_raises_integrity_error` 显式传入 `nav_type="adjusted_nav"` 和 `adjusted_basis="dividend_adjusted_nav"` 给 `_nav_record`。
  - 测试只关注 share_class="C" vs series share_class="A" 的 mismatch，不依赖 helper 默认值隐式兼容。
- **判定**：通过。

### 6. 变更范围

- **标准**：No changes outside allowed Slice 1a files and fix evidence。
- **证据**：fix evidence 记录的变更文件：
  - `fund_agent/fund/data/nav_models.py`（允许）
  - `tests/fund/data/test_nav_repository_contract.py`（允许）
  - `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-fix-evidence-20260528.md`（fix evidence 文档）
- **验证**：`__init__.py` 处于 git modified 状态，但属于原始 Slice 1a 实现阶段的 re-export 变更，fix 步骤未修改。无越界文件。
- **判定**：通过。

### 7. 验证结果可信度

- **标准**：Focused validation evidence is credible: pytest 14 passed and ruff all checks passed。
- **证据**：
  - `uv run pytest tests/fund/data/test_nav_repository_contract.py -q` → 14 passed in 0.05s
  - `uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py` → All checks passed!
- **说明**：从原始 Slice 1a 的 11 tests 增长到 14 tests，新增 3 个测试对应 AgentMiMo P0（identity_mismatch）、AgentDS F3（empty records）、AgentDS F4（nav_type unknown）。
- **判定**：通过。

---

## __init__.py Re-export 核对

`fund_agent/fund/data/__init__.py` re-export 12 个 nav_models public symbols：

`AdjustmentBasis`, `DividendAdjustmentStatus`, `FundNavRecord`, `FundNavSeries`, `NavCompletenessStatus`, `NavContractError`, `NavDataContractError`, `NavFailureCategory`, `NavIdentityStatus`, `NavSourceMetadata`, `NavType`, `ShareClassMapping`

与 `nav_models.py.__all__` 完全一致。未暴露内部类型。

---

## Non-Goal Preservation

确认以下各项未被 fix 触及：

- `drawdown_stress` blocker 未解除。
- `nav_data.py` 未修改。
- `FundDataExtractor`、snapshot、score、quality gate、FQ0-FQ6 未修改。
- golden/baseline fixtures 未修改。
- Host/Agent/dayu package 未创建。
- docs/design.md、README、implementation-control.md 未修改。

---

## Summary

Slice 1a fix 步骤正确关闭了 AgentMiMo 的 P0 required finding 和 AgentDS 的 F1-F4。3 个新增测试覆盖了 identity_mismatch、empty records、nav_type unknown 的 fail-closed 路径，share_class mismatch 测试增加了显式参数聚焦性，integrity_error 分类注释清晰合理。14 tests passed，ruff all checks passed，无回归，无越界。
