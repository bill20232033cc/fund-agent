# NAV Repository / Source Adapter Typed Contract Implementation Plan Fix

日期：2026-05-28

角色：planning/fix agent

Gate：`NAV repository/source adapter typed contract implementation gate`

Fix target：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`

Review artifacts：

- MiMo：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-review-mimo-20260528.md`
- DS：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-review-ds-20260528.md`

## Worker Self-Check

- Current gate / role：当前是 `plan fix`；我是 planning/fix agent，不是 controller。
- Scope：只修改 plan artifact，并新增本 fix artifact；不改代码，不改 review artifacts。
- Non-goals：不启动 `$gateflow` / `/gateflow`，不 implementation、commit、push、PR、merge。
- Source of truth：已读取 MiMo review、DS review 和当前 plan artifact。
- Completion signal：accepted fixes 全部写回 plan，advisory 纳入 implementation notes / residual risks，输出本 fix artifact。

## Fix Status

| Finding | Controller disposition | Fix status | Plan changes |
|---|---|---|---|
| MiMo F1 | accepted fix | fixed | `FundNavSeries` validator 规则改为 `identity_status != "verified"` 时 `strong_drawdown_evidence_eligible=False`；`requested_code_only` reason 必须说明 source-returned identity 未验证。Future Consumer Rule 也要求 `identity_status == "verified"`。 |
| MiMo F2 | accepted fix | fixed | 在 typed model validator 和 Raw Akshare normalization rules 中明确 records date 不得重复；重复 date 不 silent dedupe，归类 `integrity_error` fail-closed。 |
| DS F1 | accepted fix | fixed | 原 Slice 1 拆为 Slice 1a typed models + pure contract tests，Slice 1b adapter metadata + repository normalization + integration tests；docs/design/smoke 保持为 Slice 2，并显式依赖前序 slices。 |
| DS F2 | accepted fix | fixed | 选择 DS 推荐 option A：保留 `NavType` 和 `AdjustmentBasis`，新增语义解释和兼容矩阵；非法组合归类 `schema_drift` fail-closed。 |
| DS F3 / MiMo F7 | accepted fix | fixed | `NavSourceMetadata.failure_category` 明确为 `NavFailureCategory | None`；成功 series 中必须为 `None`。 |
| DS F6 | accepted fix | fixed | 明确 cache metadata 签名：新增 `_NavCacheEntry`、`_load_cached_with_metadata(fund_code) -> _NavCacheEntry | None`；旧 `_load_cached_sync() -> NavPayload | None` 内部只取 records；`load_raw_nav_source()` 使用 metadata；旧 `load_nav_data()` cache hit 继续 `source="nav_cache"`。 |

## Advisory Incorporated

- `FundNavRecord` 增加 `share_class` 字段；validator 校验 record-level `share_class` 与 series-level 一致。
- Future Consumer Rule 强化为三条件：`identity_status == "verified"`、`strong_drawdown_evidence_eligible is True`、`adjusted_basis` 属于 accepted adjusted/total-return set。
- 明确 `NavFailureCategory` 与 documents 层 `AnnualReportSourceFailure` 类型独立，只保持名称语义对齐。
- 明确 `completeness_status`：未传约束为 `unchecked`；通过 date/minimum constraints 后为 `complete_enough`；不通过 fail-closed。
- 明确 `raw_payload` 只用于 diagnostics/debugging，future drawdown consumer 不得读取。
- Slice 1a / 1b 增加新增模块单文件覆盖率目标 ≥80% 的 implementation reporting 要求。
- Residual risks 明确真实 006597 smoke 是 implementation evidence，不进入 CI。
- Residual risks 补充单一 `FundNavSeries` 只表达一种 NAV type/basis/share class；多类型 source 未来需拆分 series 或另开 `FundNavBundle` gate。

## Change Summary

- Strengthened typed NAV model invariants around identity, date uniqueness, share class consistency, basis/type compatibility, and source failure metadata.
- Replaced ambiguous cache metadata wording with exact adapter-private method signatures.
- Reworked implementation sequence into smaller, reviewable slices:
  - Slice 1a: pure typed models and contract tests.
  - Slice 1b: adapter metadata, repository normalization, integration tests.
  - Slice 2: docs/design sync and real 006597 smoke evidence.
- Tightened future consumer boundary so later drawdown work cannot accept raw unit NAV, unverified identity, `raw_payload`, source-specific adapter calls, SQLite cache, snapshot JSONL, or `extra_payload`.

## Residual Risks

- The implementation gate still only establishes typed contract and raw-unit-only normalization; it does not create strong drawdown evidence.
- `drawdown_stress` blocker remains unresolved by design.
- Current source identity remains `requested_code_only` unless future source adapter can verify returned identity.
- Cache provenance remains limited to existing SQLite `source` / `updated_at`; richer source URL/ID/version metadata requires future schema work.

## Re-Review Readiness

Ready for re-review：yes.

No blocking questions remain for plan re-review.
