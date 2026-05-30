# NAV Repository / Source Adapter Typed Contract Implementation Plan — Re-Review

日期：2026-05-28

Reviewer：MiMo

Fix artifact：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md`

Updated plan：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`

## Conclusion

**accepted**

## Required Fixes Final Status

### F1 — `identity_status="requested_code_only"` strong eligibility constraint

**Status：已修复**

Updated plan §Typed Models FundNavSeries validator (line 191) 现在写：

> `identity_status != "verified"` 时 `strong_drawdown_evidence_eligible=False`；其中 `requested_code_only` 的 reason 必须说明 source-returned identity 未验证，`identity_mismatch` 必须 fail-closed。

Future Consumer Rule (line 455) 也强化为三条件缺一不可：

> `identity_status == "verified"`、`strong_drawdown_evidence_eligible is True`、`adjusted_basis in {"dividend_adjusted_nav", "total_return"}` 或后续 accepted set。三条件缺一不可；`raw_unit_nav` 和 `requested_code_only` 默认拒绝。

这比原 review 建议的修复更完整：不仅在 validator 层面约束，还在 consumer rule 层面形成三重门控。即使未来有新 source adapter 返回非 `raw_unit_nav` basis，`requested_code_only` 仍然无法成为 strong evidence。

### F2 — 日期去重验证归属

**Status：已修复**

修复在三处显式声明：

1. §Typed Models FundNavSeries validator (line 188)：`records` 中 `date` 不得重复；重复 date 归类为 `integrity_error`。
2. §Raw Akshare Normalization rules (line 245)：Parsed records 必须按 date 形成唯一序列；重复 date 不做 silent dedupe，直接归类为 `integrity_error` fail-closed。
3. §Fail-Closed Taxonomy (line 264)：NAV 值非正、records 日期重复导致路径不可用、排序无法稳定 → `integrity_error` → fail-closed。

Slice 1a (line 304) 和 Slice 1b (line 367) 测试也都明确覆盖 duplicate dates raise `integrity_error`。

归属清晰：repository normalization 阶段检测并归类，validator 兜底校验，fail-closed taxonomy 表格有对应行。

## Advisory Status

5 个 advisory 均未引入新 blocker：

- **F3**（NavType/AdjustmentBasis 语义重叠）：plan 新增兼容矩阵 (line 164-173)，非法组合 `schema_drift` fail-closed。清晰可执行。
- **F4**（RawNavSourceResult 与 Slice 1 实现路径不一致）：`_RawNavSourceResult` 明确为 adapter-private (line 202-214)，`_NavCacheEntry` 和 `_load_cached_with_metadata` 签名明确 (line 219-236)。歧义消除。
- **F5**（NavDataContractError 与 AnnualReportSourceFailure 关系）：line 162 明确类型独立、名称语义对齐。
- **F6**（`_load_cached_sync` 变更兼容性）：新 `_load_cached_with_metadata` + 旧 `_load_cached_sync` 内部委托 (line 235-236)，旧 `load_nav_data()` cache hit 行为不变 (line 236)。
- **F7**（NavSourceMetadata.failure_category 成功时语义）：line 178 明确成功 series 中必须为 `None`。

## Additional Improvements Noted

Fix artifact 额外引入了以下改进，均不引入新 blocker：

- Slice 拆分为 1a（pure models）+ 1b（adapter + repository）+ 2（docs/smoke），更利于独立 review。
- `FundNavRecord` 增加 `share_class` 字段，validator 校验 record-level 与 series-level 一致。
- `raw_payload` docstring 明确仅供 diagnostics/debugging，production consumer 不得读取。
- 新增模块单文件覆盖率目标 ≥80% 的 implementation reporting 要求。
- Residual risks 补充单一 `FundNavSeries` 只表达一种 NAV type/basis/share class。

## Self-Check

- [x] 读取了 fix artifact
- [x] 读取了更新后的 plan artifact
- [x] 核验 F1 修复：`identity_status != "verified"` 约束 + Future Consumer Rule 三条件
- [x] 核验 F2 修复：validator + normalization rules + fail-closed taxonomy 三处显式声明
- [x] 确认 5 个 advisory 未引入新 blocker
- [x] 结论为 `accepted`
- [x] 未修改除 re-review artifact 外的任何文件
- [x] 未启动 `$gateflow` / `/gateflow`，未 implementation、fix、commit、push、PR、merge
