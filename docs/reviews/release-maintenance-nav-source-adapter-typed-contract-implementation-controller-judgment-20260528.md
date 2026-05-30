# NAV Repository / Source Adapter Typed Contract Implementation — Controller Judgment

日期：2026-05-28 19:42 CST

Gate：`NAV repository/source adapter typed contract implementation gate`

角色：Gateflow controller

结论：`accepted local validation`

## Controller Decision

本 gate 接受 Fund data 层 typed NAV repository/source adapter contract implementation。

已实现内容：

- `FundNavSeries` / `FundNavRecord` / `NavSourceMetadata` / `ShareClassMapping` typed contract。
- `FundNavDataAdapter.load_raw_nav_source()` adapter boundary，保留 cache origin metadata。
- `FundNavRepository.load_nav_series()` typed repository boundary。
- 当前 Akshare / 天天基金 `单位净值走势` 路径明确标记为 `raw_unit_nav`、`unit_nav`、`not_adjusted`、`requested_code_only`，且 `strong_drawdown_evidence_eligible=False`。
- Fail-closed taxonomy、provenance、share-class mapping、explicit params / no `extra_payload` tests。
- Design / Fund README / tests README 当前事实同步。

未实现内容：

- 不解除 `006597 / 2024` 的 `drawdown_stress` blocker。
- 不实现 max drawdown / volatility / stress metric。
- 不声明 adjusted NAV、cumulative NAV、dividend-adjusted NAV、total-return basis 或 verified source identity。
- 不修改 bond extractor、snapshot、score、quality gate、golden fixture、Host/Agent/dayu、release、PR 或 promotion。

## Accepted Commits

- Plan accepted：`09f0f13`
- Slice 1a typed models：`69394fb`
- Slice 1b adapter metadata / repository normalization：`1bf7f59`
- Slice 2 docs / real smoke evidence：`094609d`
- Aggregate deepreview：`63c1dbd`

## Accepted Artifacts

- Plan：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`
- Plan fix：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md`
- Plan reviews / rereviews：DS + MiMo artifacts under `docs/reviews/`
- Slice 1a evidence / review / fix / rereview artifacts
- Slice 1b evidence / DS review / GLM review artifacts
- Slice 2 evidence / DS review / GLM review artifacts
- Aggregate deepreview:
  - `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-aggregate-deepreview-ds-20260528.md`
  - `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-aggregate-deepreview-glm-20260528.md`

## Validation

Focused validations passed during slices:

- `uv run pytest tests/fund/data/test_nav_repository_contract.py -q`
- `uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py`
- `uv run pytest tests/fund/data/test_nav_data.py tests/fund/data/test_nav_repository_contract.py -q`
- `uv run ruff check fund_agent/fund/data tests/fund/data`

Final full validation passed:

- `uv run ruff check .` -> pass
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` -> `893 passed`, total coverage `92.40%`

Real `006597` typed NAV smoke passed through `FundNavRepository.load_nav_series("006597", minimum_records=30)`:

- `records=1809`
- `share_class="A"`
- `nav_type="unit_nav"`
- `adjusted_basis="raw_unit_nav"`
- `dividend_adjustment_status="not_adjusted"`
- `identity_status="requested_code_only"`
- `strong_drawdown_evidence_eligible=false`
- `source="nav_cache"`
- `origin_source="akshare"`

## Review Disposition

DS and GLM aggregate deepreview both returned `accepted`.

Non-blocking residuals accepted:

- `_RAW_UNIT_NAV_INELIGIBILITY_REASON` in repository is currently overwritten by model validator reason generation; behavior is correct, optional cleanup can be deferred.
- Some defensive caller-error branches have no dedicated tests; core fail-closed taxonomy and primary paths are covered and project coverage remains above gate.
- `_raise_contract_error` is duplicated privately in `nav_models.py` and `nav_repository.py`; acceptable until repetition grows.

No accepted finding requires a fix in this gate.

## Residuals

- `006597 / 2024` still has `bond_risk_evidence_missing.baseline_blocking=true` due to `drawdown_stress`.
- Current typed NAV path is reachable but remains raw-unit-only and source identity is `requested_code_only`; it cannot be consumed as strong drawdown evidence.
- Future `drawdown_stress` implementation must first obtain accepted adjusted / dividend-adjusted / total-return basis and verified identity, or remain fail-closed.
- Golden corpus v1 remains blocked; no promotion occurred.

## Next Entry Point

`drawdown_stress NAV-derived metric implementation gate` or narrower `NAV adjusted-basis source identity gate`.

Minimum requirement for the next gate:

- Consume only `FundNavRepository.load_nav_series()`.
- Require explicit `fund_code`, `share_class`, `start_date`, `end_date`, `minimum_records`; do not use `extra_payload`.
- Refuse `raw_unit_nav` and `requested_code_only` as strong drawdown evidence.
- Require accepted adjusted / dividend-adjusted / total-return basis and verified source/share-class identity before producing quantitative `drawdown_stress`.
- Keep annual-report “控制回撤” text weak qualitative unless a separate accepted contract changes the rule.
