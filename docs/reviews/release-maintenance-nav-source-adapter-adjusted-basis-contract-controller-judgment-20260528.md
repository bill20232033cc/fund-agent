# NAV Repository / Source Adapter Adjusted-Basis Contract — Controller Judgment

日期：2026-05-28 14:25 CST

Gate：`NAV repository/source adapter adjusted-basis contract and primer gate`

角色：Gateflow controller

结论：`accepted blocked-with-contract-gap`

## Controller Decision

本 gate 接受 `fund NAV / share-class / adjusted-basis primer` 与 NAV source adapter contract 方向，但不进入 production implementation，不解除 `006597 / 2024` 的 `drawdown_stress` blocker。

当前可接受结论：

- `drawdown_stress` quantitative evidence 可以作为未来 NAV-derived evidence 的候选方向。
- 未来实现必须通过 Agent/Fund 层 NAV repository/source adapter 统一边界消费 typed NAV series。
- 当前 `FundNavDataAdapter.load_nav_data("006597")` 只能证明 raw `单位净值走势` rows 可达，不能证明 share class、adjusted basis、dividend adjustment status、source-returned identity、provenance 或 fail-closed failure taxonomy。
- 因此当前 adapter 不满足 future `drawdown_stress` strong quantitative evidence contract。

## Accepted Artifacts

- Primer：`docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-primer-20260528.md`
- Contract plan：`docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-plan-20260528.md`
- Contract evidence：`docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-evidence-20260528.md`
- DS review：`docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-plan-review-ds-20260528.md`
- GLM review：`docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-plan-review-glm-20260528.md`

Both independent reviews returned `accepted`.

## Verified Facts

- Preflight branch：`codex/local-reconciliation`
- Dirty scope：no tracked dirty files; current gate added only docs/reviews artifacts.
- Latest 006597 score remains blocked only by `drawdown_stress`.
- `credit_risk` and `redemption_share_pressure` accepted repair state did not regress.
- `FundDocumentRepository` successfully loaded 006597 annual reports:
  - 2024 source `eid`, instance `1253099`, report name `国泰利享中短债债券型证券投资基金2024年年度报告`
  - 2025 source `eid`, instance `1450363`, report name `国泰利享中短债债券型证券投资基金2025年年度报告`
- 006597 2025 annual report §3.1 E-class year-end fund share NAV is `1.1967`.
- The earlier handoff value `1.1744` is not a 2025 annual report §3.1 year-end value and is not accepted as this gate truth.
- 006597 2025 annual report §3.3 proves E class had a 2023 distribution: every 10 shares `0.080`, cash `7,273,431.12`, reinvested `1,871,517.43`, total `9,144,948.55`.
- `FundNavDataAdapter.load_nav_data("006597")` public smoke returns 1809 records with keys `净值日期`, `单位净值`, `日增长率`; it does not expose share class, NAV type, adjustment basis, dividend adjustment status, identity status, failure category, source URL/source ID, or retrieved/cache-updated provenance.

## Contract Accepted For Next Gate

Next implementation should define typed NAV data at the Agent/Fund data boundary:

- `NavType`: unit NAV, accumulated NAV, adjusted NAV, total-return index or equivalent.
- `AdjustmentBasis`: `raw_unit_nav`, `accumulated_nav`, `dividend_adjusted_nav`, `total_return`, `unknown` or equivalent.
- Independent `dividend_adjustment_status` metadata is preferred over hiding distribution handling inside `adjustment_basis`.
- Required provenance: source name, source URL or source ID, retrieved/cache updated time, requested fund code, source-returned identity, share-class mapping, date range, record count, NAV type, adjustment basis, identity status, failure category, completeness status.
- Failure taxonomy must preserve fail-closed behavior:
  - `not_found` / `unavailable`: retry or eligible fallback.
  - `schema_drift` / `identity_mismatch` / `integrity_error` / `adjustment_basis_unknown` / insufficient history for path metrics: fail-closed.
- A/C/E/F share classes must not be mixed into a single product-level NAV series.
- `006597` may default to A class only if mapping is explicit and evidence-backed; C/E/F require explicit share-class code or share-class request.

## Drawdown Evidence Boundary

For future `drawdown_stress`:

- `total_return` or `dividend_adjusted_nav` is the preferred strong-evidence basis.
- `accumulated_nav` may be candidate evidence only if provider semantics and drawdown suitability are proven.
- `raw_unit_nav` is weak/blocked by default and may be limited-use only when the target period is proven free of distributions/splits/conversions and identity/basis are verified.
- E-class raw unit NAV across the 2023 distribution period cannot be strong drawdown evidence.
- Annual report §3.2 interval net value growth and standard deviation are useful disclosure evidence, but do not replace a daily/periodic path for max drawdown.

## Validation

No production code, schema, score policy, quality gate, golden fixture, or runtime path changed.

Executed / reviewed:

- `git branch --show-current`
- `git status --short`
- `FundDocumentRepository.load_annual_report("006597", 2024/2025)` smoke
- `FundNavDataAdapter.load_nav_data("006597")` public smoke
- Independent DS and GLM reviews with their own repository/adapter smoke

Not run:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`

Reason: this gate produced docs/reviews control artifacts only and did not modify Python, tests, schema, score, quality gate, or runtime behavior.

## Residuals

- `006597 / 2024` remains `bond_risk_evidence_missing.baseline_blocking=true`, with `missing_evidence_groups=["drawdown_stress"]`.
- Current adapter does not meet the accepted NAV contract.
- `NavType` and `AdjustmentBasis` overlap must be resolved or intentionally retained in the next implementation gate.
- NAV mapping evidence type must avoid a bad dependency direction from data layer to extractor layer.
- Golden corpus v1 remains blocked; no promotion occurred.

## Next Entry Point

`NAV repository/source adapter typed contract implementation gate`

Minimum next gate objective:

- Implement typed NAV series result/record/metadata at the Fund data boundary.
- Mark current Akshare `单位净值走势` as explicit raw unit NAV and not eligible for strong drawdown evidence by default.
- Expose origin source/cache metadata through public adapter results.
- Establish share-class mapping and fail-closed taxonomy.
- Keep `drawdown_stress` blocker intact until a later drawdown implementation gate consumes an accepted adjusted-basis contract.
