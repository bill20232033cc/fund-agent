# NAV Source Adapter Typed Contract — Slice 1a Re-Review

日期：2026-05-28

Re-review agent：AgentDS (deepreview re-review)

Work unit：NAV repository/source adapter typed contract implementation gate

Re-review target：Slice 1a fix evidence after accepted code review findings

Reviewed artifacts：
- Approved plan：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`
- Original implementation evidence：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-evidence-20260528.md`
- AgentMiMo review：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-review-mimo-20260528.md`
- AgentDS review：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-review-ds-20260528.md`
- Fix evidence：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-fix-evidence-20260528.md`
- Changed files：
  - `fund_agent/fund/data/nav_models.py`
  - `tests/fund/data/test_nav_repository_contract.py`

## Disposition

**accepted**

所有 7 项 re-review 检查点全部通过。AgentMiMo required finding 和 AgentDS F1–F4 均已正确关闭，修复未引入回归或越界变更。

---

## Re-Review Scope & Self-Check

- **Role boundary**：本次是 re-review agent，不是 controller。不 implementation、fix、commit、push、PR、merge、release、golden promotion。
- **Re-review scope**：仅验证已接受 findings 是否关闭、修复是否引入回归或 scope creep。不重新审查已 accepted 的代码质量或设计决策。
- **Preflight**：branch `codex/local-reconciliation`；fix evidence 报告 fix 前 worktree clean。

---

## Verification Matrix

### 1. identity_mismatch 直接测试存在且断言 category identity_mismatch

- **位置**：`tests/fund/data/test_nav_repository_contract.py:385–401`
- **测试名**：`test_identity_mismatch_raises_identity_mismatch`
- **验证**：使用 `_nav_series(identity_status="identity_mismatch")` 构造，`pytest.raises(NavDataContractError)` 捕获，`assert exc_info.value.category == "identity_mismatch"`
- **结论**：✅ 通过。关闭 AgentMiMo P0 / DS F2。

### 2. empty records 直接测试存在且断言 category not_found，不经 helper 默认值替换

- **位置**：`tests/fund/data/test_nav_repository_contract.py:321–353`
- **测试名**：`test_empty_records_raises_not_found`
- **验证**：直接构造 `FundNavSeries(records=(), ...)` 而非通过 `_nav_series` helper（helper 的 `records or (...)` 逻辑会用默认记录替换空 tuple）。断言 `exc_info.value.category == "not_found"`。
- **结论**：✅ 通过。关闭 DS F3。

### 3. nav_type unknown 直接测试存在且断言 category schema_drift

- **位置**：`tests/fund/data/test_nav_repository_contract.py:427–447`
- **测试名**：`test_nav_type_unknown_raises_schema_drift`
- **验证**：构造 `nav_type="unknown"` + `adjusted_basis="raw_unit_nav"`，断言 `exc_info.value.category == "schema_drift"`。
- **结论**：✅ 通过。关闭 DS F4。

### 4. share_class mismatch integrity_error 理由注释存在且合理

- **位置**：`fund_agent/fund/data/nav_models.py:407–408`
- **注释内容**：
  ```
  # series identity 已在 source/share mapping 层表达；单条记录份额串线代表
  # 同一 series 内部数据完整性破坏，因此归类为 integrity_error。
  ```
- **合理性**：注释明确区分了 series-level identity（在 source/share mapping 层表达）与 record-level share_class mismatch（同一 series 内部数据完整性破坏），逻辑自洽，与 `identity_mismatch` 的语义边界清晰。
- **结论**：✅ 通过。关闭 DS F1。

### 5. share_class mismatch 测试保持聚焦，显式传入 nav_type 和 adjusted_basis

- **位置**：`tests/fund/data/test_nav_repository_contract.py:356–382`
- **测试名**：`test_record_share_class_mismatch_raises_integrity_error`
- **验证**：
  - `_nav_series` 层级显式传入 `nav_type="adjusted_nav"`, `adjusted_basis="dividend_adjusted_nav"`
  - `_nav_record` 层级同样显式传入 `nav_type="adjusted_nav"`, `adjusted_basis="dividend_adjusted_nav"` 及 `share_class="C"`
  - 测试不再依赖 helper 默认值的兼容性，即使 `_nav_record` 默认值未来变化也不会导致 share_class 校验前因 `schema_drift` 误失败
- **结论**：✅ 通过。关闭 MiMo P2（advisory）。

### 6. 未超出 Slice 1a 允许文件和 fix evidence 范围

- **Slice 1a 允许文件**（plan）：`nav_models.py`、`__init__.py`、`test_nav_repository_contract.py`
- **Fix 实际改动文件**：`nav_models.py`、`test_nav_repository_contract.py`、fix evidence artifact（新 review 产物，非代码变更）
- **未触碰文件确认**：`nav_data.py`、`nav_repository.py`（不存在）、`FundDataExtractor`、snapshot、score、quality gate、bond extractor、golden fixture、README、design.md、implementation-control.md
- **结论**：✅ 通过。无越界变更。

### 7. 聚焦验证证据可信：pytest 14 passed，ruff all checks passed

- **Fix evidence 报告**：
  ```
  uv run pytest tests/fund/data/test_nav_repository_contract.py -q
  14 passed in 0.05s

  uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py
  All checks passed!
  ```
- **测试数量变化**：11 → 14（+3：identity_mismatch、empty_records、nav_type_unknown），与关闭的 findings 一致
- **结论**：✅ 通过。验证证据可信，无回归。

---

## Regression Check

对原有 11 个测试逐一确认未被修改破坏：

| 原测试 | fix 后状态 |
|---|---|
| `test_nav_series_success_path_normalizes_contract_fields` | 未修改，继续通过 |
| `test_nav_source_metadata_failure_category_defaults_to_none` | 未修改，继续通过 |
| `test_requested_code_only_is_not_strong_drawdown_eligible` | 未修改，继续通过 |
| `test_raw_unit_nav_is_not_strong_drawdown_eligible` | 未修改，继续通过 |
| `test_illegal_nav_type_adjustment_basis_combination_raises_schema_drift` | 未修改，继续通过 |
| `test_duplicate_record_date_raises_integrity_error` | 未修改，继续通过 |
| `test_record_share_class_mismatch_raises_integrity_error` | 修改（增加显式参数），继续通过 |
| `test_adjusted_basis_unknown_raises_adjustment_basis_unknown` | 未修改，继续通过 |
| `test_record_count_mismatch_raises_integrity_error` | 未修改，继续通过 |
| `test_explicit_constraints_mark_complete_enough_when_satisfied` | 未修改，继续通过 |
| `test_raw_payload_is_diagnostics_only_and_not_equality_bypass` | 未修改，继续通过 |

`test_record_share_class_mismatch_raises_integrity_error` 的唯一变更是将隐式依赖 helper 默认值的参数改为显式传入，断言逻辑不变，属于降低测试脆弱性的正向改进。无回归。

---

## Scope Creep Check

| 检查项 | 结果 |
|---|---|
| 是否新增了超出 Slice 1a 的模块或文件 | 否 |
| 是否修改了 `nav_data.py` | 否 |
| 是否新增了 repository IO | 否 |
| 是否调用了 akshare / SQLite / cache | 否 |
| 是否触碰了 extractor / snapshot / score / quality gate | 否 |
| 是否新增了 docs/design.md / README / control doc 变更 | 否（fix evidence 是 review artifact，非文档同步） |
| 是否改变了 fail-closed taxonomy 语义 | 否 |
| 是否解除或弱化了 `drawdown_stress` blocker | 否 |

---

## Residual Risks

- DS F5（raw_unit_nav ineligibility reason 措辞）和 F6（NavType 包含 "unknown" 防御性扩展）按 controller 指令 intentionally unchanged，不构成 blocking。
- 单文件覆盖率具体数值仍未在 evidence 中报告；14 个测试覆盖了所有 module-level validator 函数和 fail-closed 路径，但建议 Slice 1b evidence 提供 `--cov=fund_agent.fund.data.nav_models` 数值。
- `drawdown_stress blocker remains unresolved`，本 re-review 确认 fix 未改变此状态。

---

## Summary

Slice 1a fix 正确关闭了 AgentMiMo required finding（P0）和 AgentDS F1–F4 共 5 项 findings。新增 3 个测试覆盖了此前缺失的 identity_mismatch、empty records、nav_type unknown fail-closed 路径。share_class mismatch 注释说明了 integrity_error 归类理由，对应测试显式化了参数不再依赖 helper 默认值兼容性。所有原有测试无回归，无越界变更，ruff 全通过。

结论：**accepted**。Slice 1a 可以进入 controller acceptance gate，具备 Slice 1b 启动条件。
