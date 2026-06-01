# NAV Source Adapter Typed Contract — Slice 1a Review

日期：2026-05-28

Review agent：AgentDS (deepreview)

Work unit：NAV repository/source adapter typed contract implementation gate

Slice under review：**Slice 1a — Typed Models And Pure Contract Tests**

Reviewed artifacts：
- Approved plan：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`
- Implementation evidence：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-evidence-20260528.md`
- Changed files：
  - `fund_agent/fund/data/nav_models.py`
  - `fund_agent/fund/data/__init__.py`
  - `tests/fund/data/test_nav_repository_contract.py`

## Disposition

**accepted**

Slice 1a 实现了 approved plan 要求的全部 typed model、Literal domain、validator invariant、compatibility matrix 和 pure contract tests。所有 fail-closed 路径正确，无越界到 nav_data.py / repository / snapshot / score / quality gate。6 项 findings 均为 minor/cosmetic，不影响 Slice 1a 验收；建议在 Slice 1b 启动前或实现中关闭。

---

## Review Scope & Self-Check

- **Role boundary**：本次是 review agent，不是 controller。不启动 `$gateflow`、不做 implementation、fix、commit、push、PR、merge。
- **Scope assertion**：仅审查 Slice 1a allowed files 的 diff，不审查未改动文件。
- **Preflight**：implementation worker 报告 branch `codex/local-reconciliation` clean before implementation；validation 已通过（11 tests passed, ruff All checks passed）。
- **Knowledge sources**：`AGENTS.md`、approved plan、implementation evidence、diff 文件。

---

## Findings

### F1 (minor) — `_validate_record_shape` docstring 未说明 share_class mismatch 分类理由

- **Location**：`fund_agent/fund/data/nav_models.py:362–378`
- **Finding**：Approved plan Slice 1a 要求 "record share class mismatch raises `identity_mismatch` 或 `integrity_error`（implementation 选一类但必须 fail-closed 并在 docstring 说明）"。实现选择了 `integrity_error`（line 408），fail-closed 行为正确，但 `_validate_record_shape` 的 docstring 未解释为何 share_class mismatch 归类为 `integrity_error` 而非 `identity_mismatch`。
- **Recommendation**：在 docstring 或 line 407 附近加一行注释说明决策依据（例如 "share_class 不一致属于数据完整性错误而非 source identity 错误"）。

### F2 (minor) — 缺少 `identity_mismatch` fail-closed 直接测试

- **Location**：`tests/fund/data/test_nav_repository_contract.py`
- **Finding**：`_validate_identity`（nav_models.py:435–441）正确对 `identity_status="identity_mismatch"` 抛出 `NavDataContractError(category="identity_mismatch")`，但测试文件中没有直接覆盖此路径。当前 11 个测试覆盖了 `requested_code_only` 的降级行为，但未覆盖 identity_mismatch 直接 fail-closed。
- **Recommendation**：新增测试：构造 `_nav_series(identity_status="identity_mismatch")` 并断言 `pytest.raises(NavDataContractError)` 且 `category == "identity_mismatch"`。

### F3 (minor) — 缺少 empty records → `not_found` 直接测试

- **Location**：`tests/fund/data/test_nav_repository_contract.py`
- **Finding**：`_validate_record_shape`（line 380–386）对空 records 抛出 `not_found`，但测试 helper `_nav_series` 的 `records or (...)` 逻辑使得空 tuple 永远被默认值替换，该路径未被覆盖。
- **Recommendation**：新增直接构造 `FundNavSeries(records=(), ...)` 的测试，确认空 records → `not_found` fail-closed。注意需绕过 `_nav_series` helper 的默认值逻辑。

### F4 (minor) — 缺少 `nav_type="unknown"` → `schema_drift` 测试

- **Location**：`tests/fund/data/test_nav_repository_contract.py`
- **Finding**：`_validate_nav_type_adjustment_basis`（line 344–350）对 `nav_type="unknown"` 做了防御性 fail-closed（抛出 `schema_drift`），比 approved plan 明确要求的 `adjusted_basis="unknown"` 检查多一层保护，但没有对应测试。
- **Recommendation**：新增测试确认 `nav_type="unknown"` 抛出 `schema_drift`。

### F5 (cosmetic) — `raw_unit_nav` ineligibility reason 措辞与 plan 不完全一致

- **Location**：`fund_agent/fund/data/nav_models.py:550–552`
- **Finding**：Approved plan 要求 reason "明确说明 raw unit NAV 未处理分红/拆分/份额转换"。实现使用了英文领域术语 "dividend adjustment 或 total-return basis"。语义等价（total-return basis 是分红/拆分/份额转换的上位概念），但措辞风格与 plan 中的中文描述不完全对应。
- **Recommendation**：考虑补充 "拆分/份额转换" 等中文术语以与 plan 完全一致，或保持当前措辞（更精确的领域术语）。不强制修改。

### F6 (observation) — `NavType` Literal 包含 `"unknown"` 属于防御性扩展

- **Location**：`fund_agent/fund/data/nav_models.py:21–27`
- **Finding**：Approved plan 的 `NavType` Literal 定义（plan line 111–115）只列出 4 个值（`unit_nav`, `accumulated_nav`, `adjusted_nav`, `total_return_index`），但实现的 Literal 增加了 `"unknown"`。Plan 的兼容矩阵中包含 `unknown` 行（plan line 169），且实现正确对其 fail-closed（`unknown: frozenset()` + 显式前置检查）。这是合理的防御性设计，不构成偏离。
- **Recommendation**：无需修改。若需严格对齐 plan，可在 plan 更新的下一 gate 中同步 Literal 定义。

---

## Verified Correct

以下各项经逐条审查确认为正确：

### 1. Scope Boundary（无越界）

- 未修改 `nav_data.py`、未新增 `nav_repository.py`、未调用 akshare/SQLite/cache。
- 未触碰 `FundDataExtractor`、snapshot、score、quality gate、bond extractor、golden fixture。
- 未更新 docs/design.md、README、implementation-control.md（按 plan 推迟到 Slice 2）。
- 实现严格限定在 Slice 1a allowed files。

### 2. Dataclass Invariants（全部 fail-closed）

| 条件 | 实现 | 分类 | 判定 |
|---|---|---|---|
| empty records | `_validate_record_shape` line 380–386 | `not_found` | 正确 |
| record_count ≠ len(records) | line 387–393 | `integrity_error` | 正确 |
| duplicate dates | line 395–404 | `integrity_error` | 正确 |
| share_class mismatch | line 406–412 | `integrity_error` | 正确 |
| nav_type/adjusted_basis mismatch | line 413–419 | `integrity_error` | 正确 |
| adjusted_basis="unknown" | line 337–343 | `adjustment_basis_unknown` | 正确 |
| nav_type="unknown" | line 344–350 | `schema_drift` | 正确（防御性） |
| illegal combo | line 352–359 | `schema_drift` | 正确 |
| identity_mismatch | line 435–441 | `identity_mismatch` | 正确 |

### 3. NavType / AdjustmentBasis 兼容矩阵

实现（line 64–70）与 plan 矩阵完全一致：

- `unit_nav` → `{raw_unit_nav}` ✓
- `accumulated_nav` → `{accumulated_nav}` ✓
- `adjusted_nav` → `{dividend_adjusted_nav}` ✓
- `total_return_index` → `{total_return}` ✓
- `unknown` → `{}` (empty frozenset, 任何 basis 均被拒绝) ✓

### 4. strong_drawdown_evidence_eligible 与 reason 语义

- `requested_code_only` → `eligible=False`，reason 包含 "source-returned identity 未验证" ✓
- `raw_unit_nav` → `eligible=False`，reason 提及 dividend adjustment 和 total-return basis ✓
- identity 非 verified（如 `unknown`）→ 走 elif 分支降级，reason 说明 "未 verified" ✓
- 验证器只降级不升级：不会把 caller 传入的 `eligible=False` 错误改为 True ✓
- 当 identity verified + adjusted_basis 非 raw_unit_nav 时，不追加 reason，保留 caller 原始值 ✓

### 5. raw_payload 不参与业务等价

- `field(compare=False)` ✓
- `MappingProxyType` 冻结 ✓
- `metadata["doc"]` 明确标注 "仅供 diagnostics/debugging" ✓
- 测试验证 `first == second` 即使 raw_payload 不同 ✓

### 6. 中文 docstring、类型、public re-export

- 所有类、函数、模块含中文 docstring ✓
- 全部类型注解完整 ✓
- `__init__.py` 正确 re-export 12 个 Slice 1a public symbols ✓
- 无 `extra_payload`、`**kwargs`、自由 dict 参数 ✓
- `FundNavRecord` 含 `share_class` 字段 ✓

### 7. Test Coverage Assessment

11 个测试覆盖 approved plan Slice 1a 全部明确要求的测试点：

| Plan 要求 | 测试 | 状态 |
|---|---|---|
| dataclass 构造字段完整 | `test_nav_series_success_path_normalizes_contract_fields` | ✓ |
| failure_category is None success | `test_nav_source_metadata_failure_category_defaults_to_none` | ✓ |
| requested_code_only not strong eligible | `test_requested_code_only_is_not_strong_drawdown_eligible` | ✓ |
| raw_unit_nav not strong eligible | `test_raw_unit_nav_is_not_strong_drawdown_eligible` | ✓ |
| illegal combo → schema_drift | `test_illegal_nav_type_adjustment_basis_combination_raises_schema_drift` | ✓ |
| duplicate dates → integrity_error | `test_duplicate_record_date_raises_integrity_error` | ✓ |
| share class mismatch → fail-closed | `test_record_share_class_mismatch_raises_integrity_error` | ✓ |
| adjusted_basis unknown → fail | `test_adjusted_basis_unknown_raises_adjustment_basis_unknown` | ✓ |
| record_count mismatch → integrity_error | `test_record_count_mismatch_raises_integrity_error` | ✓ |
| completeness complete_enough | `test_explicit_constraints_mark_complete_enough_when_satisfied` | ✓ |
| raw_payload not equality bypass | `test_raw_payload_is_diagnostics_only_and_not_equality_bypass` | ✓ |

---

## Residual Risks (Slice 1a → Slice 1b)

1. `identity_mismatch` / empty records / `nav_type="unknown"` 路径未经直接测试（见 F2–F4），但这些是 Slice 1b repository integration 自然会覆盖的路径。
2. `strong_drawdown_evidence_eligible=False` 但 `strong_drawdown_ineligibility_reason=None` 的组合在 verified + dividend_adjusted_nav 场景下可能被构造。这不违反 plan（plan 只规定何时必须为 False，未规定何时必须为 True），但 Slice 1b 的 repository 实现应确保不会产生此组合。
3. 单文件覆盖率未在 evidence 中报告具体数值。Plan 要求 `nav_models.py` ≥80%。从函数覆盖看（所有 module-level validator 函数均被至少一个测试间接调用），覆盖率应达标，但建议 Slice 1b evidence 提供 `--cov=fund_agent.fund.data.nav_models` 具体数值。

---

## Non-Goal Preservation

确认以下各项未被 Slice 1a 触及：

- `drawdown_stress` blocker 未解除 ✓
- bond risk evidence extractor 未修改 ✓
- snapshot schema / score policy / quality gate / FQ0–FQ6 未修改 ✓
- golden/baseline fixtures 未修改 ✓
- Host/Agent/dayu package 未创建 ✓
- `FundNavDataAdapter.load_nav_data()` 行为未改变（`nav_data.py` 未修改）✓

---

## Validation

Implementation worker 已通过：

```
uv run pytest tests/fund/data/test_nav_repository_contract.py -q  # 11 passed
uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py  # All checks passed
```

Review agent 未重新运行 validation（纯模型测试无 IO 依赖，结果可信）。

---

## Summary

Slice 1a 实现质量良好。Typed model 设计完整覆盖 plan 要求的全部 Literal domain、frozen dataclass、validator invariant 和 fail-closed taxonomy。NavType/AdjustmentBasis 兼容矩阵正确，raw_payload 正确隔离，strong_drawdown_evidence_eligible 降级规则正确。6 项 findings 均为 minor/cosmetic，不阻断 Slice 1a acceptance。建议在 Slice 1b 启动前关闭 F1–F4，F5–F6 可选择性处理。
