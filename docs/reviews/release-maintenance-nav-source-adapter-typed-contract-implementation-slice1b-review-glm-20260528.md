# NAV Source Adapter Typed Contract Implementation — Slice 1b Code Review (GLM)

日期：2026-05-28

角色：code review agent (GLM)

Gate：`NAV repository/source adapter typed contract implementation gate`

Slice：1b — Adapter Metadata, Repository Normalization, Integration Tests

审查范围：`fund_agent/fund/data/nav_data.py`、`fund_agent/fund/data/nav_repository.py`、`fund_agent/fund/data/__init__.py`、`tests/fund/data/test_nav_data.py`、`tests/fund/data/test_nav_repository_contract.py`

Plan artifact：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`

Plan fix artifact：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md`

Evidence artifact：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1b-evidence-20260528.md`

Validation：32 passed；ruff clean。Controller 已 rerun 确认。

## Findings

### F1 — Low：`_parse_decimal` 静默剥离 `%` 符号存在语义风险

- **文件**：`fund_agent/fund/data/nav_repository.py:504`
- **描述**：`_parse_decimal` 使用 `str(raw_value).strip().replace("%", "")`。若 source schema 变更使日增长率或净值带 `%` 后缀（如 `"1.5%"`），该函数会将 `"1.5%"` 解析为 `Decimal("1.5")` 而非 `Decimal("0.015")`，且不触发 `schema_drift`。当前 Akshare 返回的数值不带 `%`，因此不存在活跃 bug，但静默剥离会掩盖 schema 变化。
- **建议**：在后续 slice 或 source adapter 增强时，可考虑检测 `%` 存在后 raise `schema_drift`，或在 docstring 中明确标注此行为仅适用于已知不带 `%` 的 source 格式。当前不阻断。
- **Severity**：Low。当前 source 格式已知且稳定，无活跃错误。

### F2 — Informational：`_validate_returned_identity` 未校验 fund_name 冲突

- **文件**：`fund_agent/fund/data/nav_repository.py:558-589`
- **描述**：`_validate_returned_identity` 只检查 `returned_fund_code != requested_fund_code`，不检查 `returned_fund_name` 冲突。Plan taxonomy 表述为「source-returned code/name 与请求冲突 → identity_mismatch」。当前 Akshare NAV 记录不包含基金名称字段，因此不存在活跃风险。`_extract_identity` 会提取 `returned_fund_name` 并写入 `NavSourceMetadata`，但不参与冲突校验。
- **建议**：未来 source 若返回 fund_name 且语义可靠，应补充 name-level identity 校验。当前可接受。
- **Severity**：Informational。当前 source 不返回 fund_name。

### F3 — Informational：测试导入私有 `_RawNavSourceResult`

- **文件**：`tests/fund/data/test_nav_repository_contract.py:26`
- **描述**：`from fund_agent.fund.data.nav_data import _RawNavSourceResult` 直接导入私有 DTO 构造 fake adapter 返回值。这是 repository 边界测试的标准做法，但不改变 `_RawNavSourceResult` 是内部 DTO 的事实。若该 DTO shape 变更，测试需同步修改。
- **建议**：可接受。Plan 明确要求 `_RawNavSourceResult` 不进入 `data/__init__.py` public re-export，当前实现满足此约束。
- **Severity**：Informational。测试与内部 DTO 的耦合是预期行为。

### F4 — Informational：`minimum_records < 1` 使用 `schema_drift` 分类

- **文件**：`fund_agent/fund/data/nav_repository.py:114-120`
- **描述**：当 `minimum_records` 小于 1 时，实现抛出 `NavDataContractError(category="schema_drift")`。Plan 建议「ValueError 只用于纯调用方空参，contract error 用于 source/identity 语义」。`minimum_records < 1` 是纯调用方参数校验，使用 `ValueError` 可能更精确，但 `schema_drift` 也能表达语义。
- **建议**：不阻断。分类语义不影响 fail-closed 正确性。
- **Severity**：Informational。

## Review Focus Checklist

| # | Focus Area | Status | Notes |
|---|---|---|---|
| 1 | `load_nav_data` backward compat / cache hit `source="nav_cache"` | ✅ Pass | `load_nav_data()` cache hit 仍返回 `NavDataResult(source="nav_cache", cached=True)`。`_load_cached_sync` 内部委托 `_load_cached_with_metadata` 但公开返回类型 `NavPayload \| None` 不变。旧测试无需修改。新测试 `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata` 显式验证 `legacy_result.source == "nav_cache"`。 |
| 2 | 私有 cache metadata / `_RawNavSourceResult` 不被 public re-export | ✅ Pass | `_NavCacheEntry`、`_RawNavSourceResult`、`load_raw_nav_source` 均不在 `data/__init__.py` 的 `__all__` 或 import 中。`load_raw_nav_source` 是 `FundNavDataAdapter` 实例方法，不作为模块级 public symbol。 |
| 3 | `FundNavRepository` 边界：显式参数、无 extra_payload/kwargs、无 source 直连 | ✅ Pass | `load_nav_series` 签名只有 `fund_code, *, share_class, start_date, end_date, minimum_records, force_refresh`。`test_load_nav_series_signature_has_no_extra_payload_or_kwargs` 验证所有参数均为 `POSITIONAL_OR_KEYWORD` 或 `KEYWORD_ONLY`。无 Akshare/SQLite/web/cache helper 直接调用。 |
| 4 | 归一化正确性：中文列、日期排序、无 silent dedupe、必需列、Decimal 解析、非法增长率 | ✅ Pass | 必需列 `净值日期`、`单位净值` 通过 `_required_column` 校验。可选列 `日增长率` 缺失返回 `None`，存在但非法 raise `schema_drift`。records 按 date 升序排序。重复 date 在 `FundNavSeries.__post_init__` 的 `_validate_record_shape` 中检测，归类 `integrity_error`。非正 NAV 归类 `integrity_error`。 |
| 5 | 当前 source 标记为 `raw_unit_nav` / `requested_code_only` / not strong eligible | ✅ Pass | `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, `strong_drawdown_evidence_eligible=False`。ineligibility reason 包含 "raw_unit_nav" 和 "source-returned identity 未验证"。无 adjusted 或 total-return claim。 |
| 6 | Fail-closed taxonomy 与 plan 一致 | ✅ Pass | 全部 8 种 taxonomy category 均有对应实现和测试：`unavailable`(source exception) → `not_found`(empty) → `schema_drift`(missing column/invalid date/invalid growth rate) → `integrity_error`(nonpositive NAV/duplicate date) → `identity_mismatch`(code conflict) → `missing_date_range`(date range shortfall) → `insufficient_records`(minimum_records)。`adjustment_basis_unknown` 在 model 层 Slice 1a 测试覆盖。 |
| 7 | 测试覆盖成功和失败路径，无脆弱测试 | ✅ Pass | 14 个 Slice 1b 集成测试覆盖全部 repository 路径。`_FakeRawNavAdapter` 不伪装 Akshare 行为，只返回已知 fixture records。无依赖网络/SQLite/真实 source 的测试。 |
| 8 | Scope：无 extractor/snapshot/score/quality gate/golden/README 变更 | ✅ Pass | `git diff` 确认变更仅限 `nav_data.py`、`nav_repository.py`（新增）、`__init__.py`、`test_nav_data.py`、`test_nav_repository_contract.py`。 |

## Conclusion

**accepted**

实现与 plan 完全对齐。四个 finding 均为 Low 或 Informational，无阻断问题。

- Fail-closed taxonomy 全部类别有对应实现和测试覆盖。
- 旧 `load_nav_data()` backward compatibility 通过显式测试验证。
- `FundNavRepository` 边界严格遵守显式参数约束，无 `extra_payload` / `**kwargs`。
- 当前 source 明确标记为 `raw_unit_nav` / `not_adjusted` / not strong eligible，无 adjusted 或 total-return claim。
- Scope 严格限制在 data 层内部，未触碰 extractor、snapshot、score、quality gate、golden、README 或 design doc。
