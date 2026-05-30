# NAV Typed Contract Slice 1a Code Review

日期：2026-05-28

Reviewer：AgentMiMo (code review agent)

Gate classification：`heavy`

Work unit：NAV repository/source adapter typed contract implementation gate

Slice：1a — Typed Models And Pure Contract Tests

## Review Scope

Reviewed files：

- `fund_agent/fund/data/nav_models.py`（新增）
- `fund_agent/fund/data/__init__.py`（修改）
- `tests/fund/data/test_nav_repository_contract.py`（新增）

参考文件：

- `AGENTS.md`
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`（Slice 1a 部分）
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-evidence-20260528.md`

## Independent Validation

```
uv run pytest tests/fund/data/test_nav_repository_contract.py -q
→ 11 passed in 0.03s ✓

uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py
→ All checks passed! ✓
```

## Conclusion

**accepted-with-required-fixes**

Implementation 正确、完整、符合 approved plan Slice 1a 设计意图。有一项 required fix：缺少 `identity_mismatch` fail-closed 路径的显式测试。

## Findings

### [P0] Missing identity_mismatch Fail-Closed Test

- File: `tests/fund/data/test_nav_repository_contract.py`
- Severity: required-fix
- Category: test-gap
- Plan reference: Slice 1a Exact changes §6："fake source returned identity mismatch 时 raise `NavDataContractError(category='identity_mismatch')`"

`_validate_identity()`（nav_models.py:435）正确实现了 `identity_status == "identity_mismatch"` 时抛出 `NavDataContractError(category="identity_mismatch")` 的逻辑。但测试文件没有覆盖该路径。现有 `test_record_share_class_mismatch_raises_integrity_error` 只测 record-level share_class mismatch，不测 identity-level mismatch。

建议新增测试：

```python
def test_identity_mismatch_raises_identity_mismatch() -> None:
    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(identity_status="identity_mismatch")
    assert exc_info.value.category == "identity_mismatch"
```

### [P1] Coverage Gap: "unknown" identity_status Path

- File: `fund_agent/fund/data/nav_models.py:546-547`
- Severity: advisory
- Category: coverage-gap

`_apply_strong_drawdown_eligibility` 的 `elif series.identity_status != "verified"` 分支覆盖 `identity_status="unknown"` 场景（添加通用 reason），但无测试验证该路径。非阻塞，但建议后续补充。

### [P2] test_record_share_class_mismatch 依赖 helper 默认兼容性

- File: `tests/fund/data/test_nav_repository_contract.py:334-337`
- Severity: advisory
- Category: test-fragility

`test_record_share_class_mismatch_raises_integrity_error` 使用 `_nav_record(share_class="C")`，依赖 `_nav_record` 的默认 `nav_type="adjusted_nav"` / `adjusted_basis="dividend_adjusted_nav"` 与 series-level 兼容。当前正确，但如果 `_nav_record` 默认值变化，该测试会在 share_class 校验前因 `schema_drift` 失败。建议测试中显式传入 nav_type/adjusted_basis。

## Scope Compliance

| 检查项 | 结果 |
|---|---|
| 只实现 Slice 1a，未越界 | 通过。未修改 nav_data.py、nav_repository.py、extractor、snapshot、score、quality gate |
| dataclass invariants fail-closed | 通过。empty records→not_found、record_count mismatch→integrity_error、duplicate dates→integrity_error、share_class mismatch→integrity_error、nav_type/adjusted_basis mismatch→integrity_error、adjusted_basis unknown→adjustment_basis_unknown、nav_type unknown→schema_drift、identity_mismatch→identity_mismatch |
| NavType/AdjustmentBasis 兼容矩阵 | 通过。unit_nav→raw_unit_nav、accumulated_nav→accumulated_nav、adjusted_nav→dividend_adjusted_nav、total_return_index→total_return、unknown→空集(schema_drift) |
| verified 与 reason 语义 | 通过。verified identity + raw_unit_nav 正确降级为 not strong eligible；requested_code_only 正确添加 reason 并降级；identity_mismatch 正确 fail-closed |
| raw_payload 不参与业务等价 | 通过。field(compare=False) + test_raw_payload_is_diagnostics_only_and_not_equality_bypass 验证 |
| 中文 docstring | 通过。所有类、函数、测试函数均有中文 docstring |
| 类型注解 | 通过。Literal domain、frozen/slotted dataclass、InitVar 使用正确 |
| public re-export | 通过。__init__.py re-export 12 个 nav_models public symbol，不暴露内部类型 |
| 无 extra_payload | 通过。所有 dataclass 使用显式 kw_only 参数 |
| drawdown_stress blocker | 未解除。implementation 正确保留了 strong_drawdown_evidence_eligible=False 语义 |

## Invariants Detail

| Invariant | category | 实现位置 | 测试覆盖 |
|---|---|---|---|
| empty records | `not_found` | nav_models.py:380-386 | implicit（validator 路径） |
| record_count mismatch | `integrity_error` | nav_models.py:387-393 | test_record_count_mismatch_raises_integrity_error ✓ |
| duplicate dates | `integrity_error` | nav_models.py:395-404 | test_duplicate_record_date_raises_integrity_error ✓ |
| share_class mismatch | `integrity_error` | nav_models.py:406-412 | test_record_share_class_mismatch_raises_integrity_error ✓ |
| nav_type/adjusted_basis mismatch | `integrity_error` | nav_models.py:413-419 | implicit（validator 路径） |
| adjusted_basis="unknown" | `adjustment_basis_unknown` | nav_models.py:337-343 | test_adjusted_basis_unknown_raises_adjustment_basis_unknown ✓ |
| nav_type="unknown" | `schema_drift` | nav_models.py:344-350 | implicit（empty frozenset 路径） |
| illegal combination | `schema_drift` | nav_models.py:352-359 | test_illegal_nav_type_adjustment_basis_combination_raises_schema_drift ✓ |
| identity_mismatch | `identity_mismatch` | nav_models.py:435-441 | **缺失（P0）** |
| requested_code_only not strong eligible | override to False | nav_models.py:542-545 | test_requested_code_only_is_not_strong_drawdown_eligible ✓ |
| raw_unit_nav not strong eligible | override to False | nav_models.py:549-552 | test_raw_unit_nav_is_not_strong_drawdown_eligible ✓ |
| unchecked completeness | override to "unchecked" | nav_models.py:497-499 | test_nav_series_success_path_normalizes_contract_fields ✓ |
| complete_enough | override to "complete_enough" | nav_models.py:525 | test_explicit_constraints_mark_complete_enough_when_satisfied ✓ |

## Self-Check

- Review scope：只审了 Slice 1a allowed files。未审 nav_data.py、nav_repository.py 或其他模块。
- Finding severity 分类：P0=required-fix（缺显式测试），P1/P2=advisory。
- 未建议解除 drawdown_stress blocker、改 FQ0-FQ6 或改 snapshot/score/quality gate schema。
- 结论与 findings 一致：implementation 正确但缺一项必测路径，结论为 accepted-with-required-fixes。
