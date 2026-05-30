# NAV Source Adapter Typed Contract — Aggregate Deep Review (GLM)

日期：2026-05-28

Reviewer：GLM（aggregate reviewer）

Role：aggregate reviewer only。不做实现、修复、commit、push、PR、merge、release 或 golden promotion。

Scope：base commit `449feba`，diff `449feba...HEAD`。27 files changed, +5304 / -10。

## Conclusion

**accepted**

实现完整满足 plan 全部三条 slice 契约，fail-closed taxonomy 覆盖全部 8 类失败场景，legacy `load_nav_data()` 兼容性无回归，`drawdown_stress` blocker 未解除。发现 3 条 informational findings，无需 blocking fix。

## Findings

### F-1 [informational] repository pre-set ineligibility reason 被 validator 覆写

`nav_repository.py` 在构造 `FundNavSeries` 时预填 `strong_drawdown_ineligibility_reason=_RAW_UNIT_NAV_INELIGIBILITY_REASON`。但 `FundNavSeries.__post_init__` 调用 `_apply_strong_drawdown_eligibility`，该函数会根据 `identity_status` 和 `adjusted_basis` 重新计算 reasons 并用 `object.__setattr__` 覆写。因此预填值永远不会出现在最终 series 中——它是死代码。不影响正确性（validator 始终产出正确 reason），但可能误导阅读者以为 repository 端控制了 reason 文案。

建议：后续可将预填改为 `None` 或移除该常量，依赖 validator 单一真源。不阻塞 accept。

### F-2 [informational] `_raise_contract_error` 在 nav_models.py 和 nav_repository.py 双重定义

两个模块各自定义了签名完全相同的模块级私有 `_raise_contract_error` 函数。功能无差别，可考虑在 `nav_models.py` 中保留一份并在 `nav_repository.py` 中 import。不阻塞 accept——两者都是模块私有，无 public 依赖。

### F-3 [informational] `_RAW_UNIT_NAV_INELIGIBILITY_REASON` 混用中英文

`_RAW_UNIT_NAV_INELIGIBILITY_REASON` 前半句英文、后半句中文。而 `nav_models.py` 中 validator 生成的 reasons 全部以中文为主。由于该值被 validator 覆写（见 F-1），实际上不会出现在运行时 series 中。不阻塞 accept。

## Contract Coherency

### Models (`nav_models.py`)

- `NavType` / `AdjustmentBasis` / `DividendAdjustmentStatus` / `NavIdentityStatus` / `NavCompletenessStatus` / `NavFailureCategory` Literal 域与 plan 完全一致。
- `_ALLOWED_ADJUSTMENT_BASIS_BY_NAV_TYPE` 兼容矩阵：`unit_nav → {raw_unit_nav}`、`accumulated_nav → {accumulated_nav}`、`adjusted_nav → {dividend_adjusted_nav}`、`total_return_index → {total_return}`、`unknown → ∅`。与 plan 设计表逐行核对无误。
- `NavDataContractError` 含 `category`、`message`、`source`、`fund_code`、`cause` 五字段，`__slots__` 优化，满足 plan 要求。
- `NavContractError = NavDataContractError` 别名在 `__init__.py` 正确 re-export。
- `NavSourceMetadata.failure_category: NavFailureCategory | None`，成功 series 默认 `None`。正确。
- `ShareClassMapping.mapping_evidence: tuple[str, ...]`，不依赖 extractor 类型。正确。
- `FundNavRecord.raw_payload` 通过 `MappingProxyType` 冻结，`compare=False` 阻断等价判断绕过。正确。
- `FundNavSeries.__post_init__` 验证链：`_validate_nav_type_adjustment_basis → _validate_record_shape → _validate_identity → _apply_date_range_defaults → _apply_completeness_status → _apply_strong_drawdown_eligibility`。顺序合理，每步或 fail-closed 或规范化，无遗漏。
- `adjusted_basis="unknown"` → `adjustment_basis_unknown` fail-closed。正确。
- `nav_type="unknown"` → `schema_drift` fail-closed。正确。
- `identity_status="identity_mismatch"` → `identity_mismatch` fail-closed。正确。
- `requested_code_only` 和 `raw_unit_nav` 均导致 `strong_drawdown_evidence_eligible=False`。正确。

### Adapter (`nav_data.py`)

- `_NavCacheEntry` 和 `_RawNavSourceResult` 为私有 DTO，不出现在 `__init__.py`。验证通过。
- `_load_cached_with_metadata` 查询 `payload_json`、`source`、`updated_at` 三列。旧 `_load_cached_sync` 委托后只返回 `records`。旧 `load_nav_data()` cache hit 仍返回 `NavDataResult(source="nav_cache", cached=True)`。兼容性完整。
- `load_raw_nav_source` cache hit 时 `source="nav_cache"` 但 `origin_source` 来自 `_NavCacheEntry.source`（即 `"akshare"`），`cache_updated_at` 来自缓存行。provenance 正确。
- `_save_cached_sync` 新增 `updated_at: str | None = None`，默认 `_utc_timestamp()`。旧 `load_nav_data()` 只传两参数，第三参数走默认，行为不变。正确。

### Repository (`nav_repository.py`)

- `FundNavRepository.__init__` 接受 `source_adapter: FundNavDataAdapter | None`，默认构造 adapter。正确。
- `load_nav_series` 签名：`(self, fund_code: str, *, share_class, start_date, end_date, minimum_records, force_refresh)`。全部显式参数，无 `extra_payload`/`kwargs`。已通过 `inspect.signature` 测试锁定。
- Fund code 校验：6 位数字，否则 `identity_mismatch` fail-closed。正确。
- Share class 校验：`None` 默认 `"A"`，非空时 `strip().upper().isalnum()`，否则 `identity_mismatch`。正确。
- Source adapter 异常包装：catch `NavDataContractError` 直接 reraise，其余 `Exception` 包装为 `unavailable` 保留 cause。正确。
- Identity 验证：`_extract_identity` 从 raw records 按候选 key 提取 returned code/name。冲突时 `identity_mismatch` fail-closed。无 identity 时通过（`requested_code_only` 在 series 级表达）。正确。
- Raw record normalization：`_normalize_raw_record` 校验 `Mapping` 类型、必需 `净值日期`/`单位净值`、可选 `日增长率`、Decimal 解析、非正 NAV → `integrity_error`、日期排序去重。与 plan normalization rules 完全一致。
- Series-level fixed values：`nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`identity_status="requested_code_only"`、`strong_drawdown_evidence_eligible=False`。与 plan 完全一致。

### Public Exports (`__init__.py`)

新增 re-export：`AdjustmentBasis`、`DividendAdjustmentStatus`、`FundNavRecord`、`FundNavRepository`、`FundNavSeries`、`NavCompletenessStatus`、`NavContractError`、`NavDataContractError`、`NavFailureCategory`、`NavIdentityStatus`、`NavSourceMetadata`、`NavType`、`ShareClassMapping`。未 re-export `_RawNavSourceResult` 和 `_NavCacheEntry`。`__all__` 已同步更新。正确。

## Fail-Closed Taxonomy Verification

| 场景 | plan 要求 category | 实现 category | 测试覆盖 |
|---|---|---|---|
| fund_code 非法 | `identity_mismatch` | `identity_mismatch` | 无独立测试，但 `_normalize_fund_code` 路径被 repository 集成测试隐式覆盖 |
| source 异常 | `unavailable` | `unavailable` | `test_repository_unavailable_cause_preserved` |
| 空 records | `not_found` | `not_found` | `test_repository_empty_records_raises_not_found`、`test_empty_records_raises_not_found` |
| 缺列/不可解析 | `schema_drift` | `schema_drift` | `test_repository_missing_date_column_raises_schema_drift`、`test_repository_missing_nav_column_raises_schema_drift`、`test_repository_invalid_date_raises_schema_drift`、`test_repository_invalid_growth_rate_raises_schema_drift` |
| NAV 非正/日期重复/计数不匹配 | `integrity_error` | `integrity_error` | `test_repository_nonpositive_nav_raises_integrity_error`、`test_repository_duplicate_raw_date_raises_integrity_error`、`test_duplicate_record_date_raises_integrity_error`、`test_record_count_mismatch_raises_integrity_error` |
| source-returned code 冲突 | `identity_mismatch` | `identity_mismatch` | `test_repository_identity_mismatch_raises`、`test_identity_mismatch_raises_identity_mismatch` |
| adjusted_basis unknown | `adjustment_basis_unknown` | `adjustment_basis_unknown` | `test_adjusted_basis_unknown_raises_adjustment_basis_unknown` |
| 日期范围不足 | `missing_date_range` | `missing_date_range` | `test_repository_missing_date_range_raises` |
| minimum_records 不足 | `insufficient_records` | `insufficient_records` | `test_repository_insufficient_records_raises` |

8/8 失败类别全部覆盖。`schema_drift`/`identity_mismatch`/`integrity_error`/`adjustment_basis_unknown` 不允许 fallback 静默掩盖——实现中这些类别直接 `raise`，无 fallback 路径。正确。

注：`fund_code` 空值/非 6 位数字的 `_normalize_fund_code` 路径无独立单元测试。建议后续补测。不阻塞 accept——该路径在真实调用中必经 `load_nav_series` 入口，且 `minimum_records < 1` 和 `start_date > end_date` 等前置校验有独立测试。

## raw_unit_nav Evidence Strength

实现正确地做了以下三层防护：

1. **Repository 硬编码**：`FundNavRepository.load_nav_series()` 构造 series 时固定 `strong_drawdown_evidence_eligible=False`。
2. **Validator 覆核**：`_apply_strong_drawdown_eligibility` 检测到 `adjusted_basis == "raw_unit_nav"` 后追加 reason 并强制 `False`。即使构造时误传 `True` 也会被覆写。
3. **Identity 双重阻断**：`requested_code_only` 同样导致 `False`。当前路径同时命中两条 ineligibility reason。

raw unit NAV 不证明分红调整、累计净值或 total-return basis。实现与 plan、design.md、README 表述一致。

## requested_code_only Identity

`_extract_identity` 从 raw records 中按候选 key 提取 returned code/name。当前 Akshare `单位净值走势` 路径不返回 identity 字段，因此 `returned_fund_code` / `returned_fund_name` 均为 `None`，`_validate_returned_identity` 在 `None` 时直接 return（不触发 mismatch）。Repository 构造 `identity_status="requested_code_only"` 和 `ShareClassMapping.mapping_status="requested_code_default_a"`。正确。

## Provenance

Cache hit 时 `source="nav_cache"` 但 `origin_source` 来自 `_NavCacheEntry.source`（`"akshare"`），`cache_updated_at` 来自缓存行 `updated_at`。`retrieved_at` 为 `None`（cache hit 无新抓取时间）。`load_raw_nav_source` 返回的 `_RawNavSourceResult` 完整暴露 6 字段 metadata。测试 `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata` 验证了 cache hit 后 origin source 可追溯。正确。

## Legacy `load_nav_data()` Compatibility

- `_load_cached_sync` 改为委托 `_load_cached_with_metadata().records`，返回类型仍为 `NavPayload | None`。旧 `load_nav_data()` 行为不变。
- `_save_cached_sync` 新增 `updated_at` 默认参数，旧调用只传两参数，走默认 `_utc_timestamp()`。行为不变。
- 旧 cache 测试（`test_nav_data_adapter_cache_reuse`、`test_nav_data_adapter_force_refresh_bypasses_cache`）仍在 diff 中保留且未修改断言。
- 新增测试 `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata` 验证旧入口仍返回 `source="nav_cache"` 和 `cached=True`。
- `NavDataResult` 无字段变更。`FundDataExtractor` 和 `_NavDataProvider` Protocol 未被修改。正确。

## Explicit Params / No extra_payload/kwargs

`inspect.signature` 测试锁定 `load_nav_series` 全部参数为 `POSITIONAL_OR_KEYWORD` 或 `KEYWORD_ONLY`。grep 确认 `nav_repository.py` 和 `nav_models.py` 无 `extra_payload`、`kwargs`、`**kwargs`。正确。

## No Extractor/Snapshot/Score/Quality/Golden Changes

`git diff 449feba...HEAD --name-only | grep -E '(extractor|snapshot|score|quality|golden)'` 返回空。无变更。正确。

## drawdown_stress Blocker

Evidence artifact 明确声明 `drawdown_stress blocker remains unresolved`。`design.md`、`README.md`、`tests/README.md` 均未声称解除 blocker。实现中 `strong_drawdown_evidence_eligible=False` 保证了 raw unit NAV 不能被 drawdown consumer 消费为强证据。正确。

## Validation Status

- Full ruff：pass（`All checks passed!`）
- Full pytest：893 passed, coverage 92.40%（evidence artifact 确认）
- Real 006597 smoke：`fund_code="006597"`, `adjusted_basis="raw_unit_nav"`, `nav_type="unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, `strong_drawdown_evidence_eligible=false`, `origin_source="akshare"`, `cached=true`。全部与 plan 预期一致。

## Review Focus Checklist

| 关注点 | 状态 |
|---|---|
| contract coherency（models/repository/adapter/export） | 通过 |
| raw_unit_nav not strong evidence | 通过 |
| requested_code_only identity | 通过 |
| fail-closed taxonomy 8/8 覆盖 | 通过 |
| provenance cache hit 保留 origin_source | 通过 |
| legacy load_nav_data 兼容 | 通过 |
| explicit params, no extra_payload/kwargs | 通过 |
| no extractor/snapshot/score/quality/golden changes | 通过 |
| drawdown_stress blocker remains | 通过 |
