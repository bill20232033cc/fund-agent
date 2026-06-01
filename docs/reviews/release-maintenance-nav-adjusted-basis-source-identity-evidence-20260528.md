# NAV Adjusted-Basis Source Identity Gate — E1/E2 Evidence

日期：2026-05-28

角色：evidence worker，非 controller，非 implementation worker。

Work unit：`NAV adjusted-basis source identity gate`

Accepted plan：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`

Recommended decision：`partial-acceptance-with-blocked-classes`

## Step Self-Check

- Current gate / role：本 artifact 只产出 E1/E2 source evidence 和 decision recommendation；不启动 gateflow，不 implement、commit、push、PR、merge、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、前序 NAV controller judgments、accepted plan、`nav_models.py`、`nav_repository.py`、`nav_data.py`。
- Scope boundary：只新增本 evidence artifact；不改 plan/review、production code/tests、score、snapshot、quality gate、golden fixture、bond extractor、Host/Agent/dayu。
- Evidence boundary：E1 JS smoke 只解析 `fS_code` / `fS_name` 和变量存在性；未解析或记录 JS 数值变量内容。E2 数值 cross-check 使用 Akshare public API DataFrame 与 `FundDocumentRepository` 年报证据。
- Stop condition check：source smoke 全部成功且可分类；未遇到不可分类 source failure。

## Preflight

Commands：

```text
git branch --show-current
git status --short
```

Observed：

- Branch：`codex/local-reconciliation`
- Pre-existing dirty scope：
  - `?? --help`
  - `?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
  - `?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md`
  - `?? docs/reviews/repo-review-20260526-231040.md`
  - `?? docs/reviews/repo-review-20260527-215953.md`
  - `?? docs/reviews/repo-review-20260527-225303.md`
  - `?? docs/tmux-agent-memory-store.md`
- This evidence slice adds only `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`.

## Source Truth Summary

Current repository truth：

- `FundNavRepository.load_nav_series()` is the future typed boundary for path metrics; it consumes `FundNavDataAdapter.load_raw_nav_source()` and returns `FundNavSeries`.
- Current production normalization is still hard-coded to `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, `strong_drawdown_evidence_eligible=False`.
- Current typed models can carry source identity and basis through `NavSourceMetadata`, `ShareClassMapping`, and `FundNavSeries`; likely no new field is needed for a single accepted accumulated-nav series per call.
- Current model taxonomy has `insufficient_records` and `missing_date_range`; evidence-level `insufficient_history` must map to one of those before implementation.

Prior accepted annual-report facts：

- 006597 2025 annual report §3.3 proves E class had a 2023 distribution: every 10 shares `0.080`, cash `7,273,431.12`, reinvested `1,871,517.43`, total `9,144,948.55`.
- 006597 2025 annual report §3.1 E-class year-end fund share NAV is `1.1967`.

## Commands Run

E1/E2 smoke command：

```text
uv run python - <<'PY'
# Calls:
# - ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
# - ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
# - ak.fund_open_fund_info_em(symbol=code, indicator="累计收益率走势", period="成立来")
# - HTTP GET https://fund.eastmoney.com/pingzhongdata/{code}.js
# JS parsing scope: fS_code / fS_name values and Data_* variable presence only.
PY
```

Akshare source inspection command：

```text
uv run python - <<'PY'
import inspect, akshare as ak
print(ak.__version__)
print(inspect.signature(ak.fund_open_fund_info_em))
print(inspect.getdoc(ak.fund_open_fund_info_em))
print(inspect.getsource(ak.fund_open_fund_info_em))
PY
```

Annual-report evidence command：

```text
uv run python - <<'PY'
from fund_agent.fund.documents import FundDocumentRepository
# load_annual_report("006597", 2025), then inspect §3 text and parsed tables.
PY
```

No direct PDF/cache file reads were used for annual-report evidence.

## E1 Smoke Matrix

Akshare version：`1.18.60`

`ak.fund_open_fund_info_em` signature：

```text
(symbol: str = '710001', indicator: str = '单位净值走势', period: str = '成立来') -> pandas.DataFrame
```

Akshare source inspection facts：

- `单位净值走势` executes `Data_netWorthTrend` and returns columns `净值日期`, `单位净值`, `日增长率`.
- `累计净值走势` executes `Data_ACWorthTrend` and returns columns `净值日期`, `累计净值`.
- `累计收益率走势` calls Eastmoney `https://api.fund.eastmoney.com/pinzhong/LJSYLZS` and returns columns `日期`, `累计收益率`.
- Akshare docstring/source maps fields to provider variables/API but does not define dividend / total-return semantics. It is not sufficient by itself to prove adjusted basis.

### A Class: 006597

| Source | Indicator | Columns | Rows | First date | Last date | Samples |
|---|---|---|---:|---|---|---|
| `ak.fund_open_fund_info_em` | `单位净值走势` | `净值日期`, `单位净值`, `日增长率` | 1809 | 2018-12-03 | 2026-05-27 | first `1.0`; last `1.2275` |
| `ak.fund_open_fund_info_em` | `累计净值走势` | `净值日期`, `累计净值` | 1809 | 2018-12-03 | 2026-05-27 | first `1.0`; last `1.2275` |
| `ak.fund_open_fund_info_em` | `累计收益率走势`, `period="成立来"` | `日期`, `累计收益率` | 202 | 2018-12-03 | 2026-05-28 | first `0.0`; last `22.75` |
| Eastmoney JS | `pingzhongdata/006597.js` | identity + variable presence only | n/a | n/a | n/a | `fS_code="006597"`, `fS_name="国泰利享中短债债券A"`; `Data_netWorthTrend`, `Data_ACWorthTrend`, `Data_grandTotal` present |

Provider page cross-check：天天基金 006597 page displays A-class identity, current `单位净值` / `累计净值`, a table with `日期 单位净值 累计净值 日增长率`, and says inception-to-date dividend count is `0` and split count is `0`: <https://fund.eastmoney.com/006597.html>.

### C Class: 006598

| Source | Indicator | Columns | Rows | First date | Last date | Samples |
|---|---|---|---:|---|---|---|
| `ak.fund_open_fund_info_em` | `单位净值走势` | `净值日期`, `单位净值`, `日增长率` | 1809 | 2018-12-03 | 2026-05-27 | first `1.0`; last `1.2094` |
| `ak.fund_open_fund_info_em` | `累计净值走势` | `净值日期`, `累计净值` | 1809 | 2018-12-03 | 2026-05-27 | first `1.0`; last `1.2094` |
| `ak.fund_open_fund_info_em` | `累计收益率走势`, `period="成立来"` | `日期`, `累计收益率` | 202 | 2018-12-03 | 2026-05-28 | first `0.0`; last `20.94` |
| Eastmoney JS | `pingzhongdata/006598.js` | identity + variable presence only | n/a | n/a | n/a | `fS_code="006598"`, `fS_name="国泰利享中短债债券C"`; `Data_netWorthTrend`, `Data_ACWorthTrend`, `Data_grandTotal` present |

Provider page cross-check：天天基金 006598 page displays C-class table `日期 单位净值 累计净值 日增长率`; current rows have unit NAV equal to accumulated NAV, and inception-to-date dividend count is `0`, split count `0`: <https://fund.eastmoney.com/006598.html>.

### E Class: 014217

| Source | Indicator | Columns | Rows | First date | Last date | Samples |
|---|---|---|---:|---|---|---|
| `ak.fund_open_fund_info_em` | `单位净值走势` | `净值日期`, `单位净值`, `日增长率` | 994 | 2022-04-25 | 2026-05-28 | first `1.119`; last `1.2033` |
| `ak.fund_open_fund_info_em` | `累计净值走势` | `净值日期`, `累计净值` | 994 | 2022-04-25 | 2026-05-28 | first `1.119`; last `1.2113` |
| `ak.fund_open_fund_info_em` | `累计收益率走势`, `period="成立来"` | `日期`, `累计收益率` | 250 | 2022-04-25 | 2026-05-28 | first `0.0`; last `8.30` |
| Eastmoney JS | `pingzhongdata/014217.js` | identity + variable presence only | n/a | n/a | n/a | `fS_code="014217"`, `fS_name="国泰利享中短债债券E"`; `Data_netWorthTrend`, `Data_ACWorthTrend`, `Data_grandTotal` present |

Provider page cross-check：天天基金 014217 page displays E-class identity, current `单位净值=1.2033`, `累计净值=1.2113`, `成立来=8.30%`, and a table with `日期 单位净值 累计净值 日增长率`; it also records inception-to-date dividend count `1` and `2023-01-11 每份派现金 0.0080 元`: <https://fund.eastmoney.com/014217.html>.

### F Class: 022176

| Source | Indicator | Columns | Rows | First date | Last date | Samples |
|---|---|---|---:|---|---|---|
| `ak.fund_open_fund_info_em` | `单位净值走势` | `净值日期`, `单位净值`, `日增长率` | 398 | 2024-10-08 | 2026-05-28 | first `1.1924`; last `1.2273` |
| `ak.fund_open_fund_info_em` | `累计净值走势` | `净值日期`, `累计净值` | 398 | 2024-10-08 | 2026-05-28 | first `1.1924`; last `1.2273` |
| `ak.fund_open_fund_info_em` | `累计收益率走势`, `period="成立来"` | `日期`, `累计收益率` | 398 | 2024-10-08 | 2026-05-28 | first `0.0`; last `2.93` |
| Eastmoney JS | `pingzhongdata/022176.js` | identity + variable presence only | n/a | n/a | n/a | `fS_code="022176"`, `fS_name="国泰利享中短债债券F"`; `Data_netWorthTrend`, `Data_ACWorthTrend`, `Data_grandTotal` present |

Provider page cross-check：天天基金 022176 page displays F-class table `日期 单位净值 累计净值 日增长率`; current rows have unit NAV equal to accumulated NAV, inception-to-date dividend count is `0`, split count `0`, but history starts at 2024-10-08: <https://fund.eastmoney.com/022176.html>.

## E2 Semantics Proof Attempt

### Source-Owned Semantics Found

Akshare source-owned / provider-owned mapping：

- Akshare maps `累计净值走势` to Eastmoney JS variable `Data_ACWorthTrend`.
- Akshare maps `累计收益率走势` to Eastmoney API `LJSYLZS`.
- This proves source endpoint / variable lineage, but not dividend semantics.

Eastmoney / 天天基金 provider page evidence：

- Fund pages display `单位净值`, `累计净值`, `成立来` return, a historical table headed `日期 单位净值 累计净值 日增长率`, and per-class dividend/split count.
- For 014217 E, provider page gives exact dividend date and amount: `2023-01-11 每份派现金 0.0080 元`.
- For 006597 A, 006598 C and 022176 F, provider pages report dividend count `0`, split count `0`.

Provider help page evidence：

- 天天基金帮助中心 states fund dividends distribute part of returns in cash or converted fund shares, and that the distributed amount was originally part of fund share NAV.
- The same page gives cash-dividend and reinvestment-share calculation formulas, including use of the equity registration date NAV: <https://fundtest.eastmoney.com/help/question_250.html>.

Official annual-report evidence via `FundDocumentRepository`：

- `FundDocumentRepository.load_annual_report("006597", 2025)` returned source `eid`, report name `国泰利享中短债债券型证券投资基金2025年年度报告`, instance `1450363`.
- §3.3 / parsed table page 17 records:
  - A class：past three years no profit distribution.
  - C class：past three years no profit distribution.
  - E class：2023 every 10 shares `0.080`, cash `7,273,431.12`, reinvested `1,871,517.43`, total `9,144,948.55`; 2024/2025 none.
  - F class：no profit distribution since the share class was added.
- §2 / parsed table page 5 maps share classes and codes: A `006597`, C `006598`, E `014217`, F `022176`.

### What Was Not Proven

- No provider document was found that explicitly defines `Data_ACWorthTrend` as formula `unit NAV + accumulated cash distributions`.
- No provider document was found that explicitly defines `LJSYLZS` as a total-return index or dividend-reinvested return series.
- Therefore `累计收益率走势` / `LJSYLZS` remains `adjustment_basis_unknown` for strong evidence. Its lower-frequency row counts (202 / 202 / 250 for A/C/E) also make future path-metric suitability unresolved.

### E-Class Distribution Cross-Check

Source anchors：

- Official annual report through `FundDocumentRepository`: E class had 2023 distribution every 10 shares `0.080`, equivalent to every share `0.0080`.
- Provider page exact date: 014217 E `2023-01-11 每份派现金 0.0080 元`.
- Akshare accumulated/unit series from the same provider source.

Akshare cross-check observations for 014217 E:

| Date | Unit NAV | Accumulated NAV | Difference |
|---|---:|---:|---:|
| 2023-01-03 | 1.1319 | 1.1319 | 0.0000 |
| 2023-01-04 | 1.1323 | 1.1323 | 0.0000 |
| 2023-01-05 | 1.1326 | 1.1326 | 0.0000 |
| 2023-01-06 | 1.1327 | 1.1327 | 0.0000 |
| 2023-01-09 | 1.1332 | 1.1332 | 0.0000 |
| 2023-01-10 | 1.1332 | 1.1332 | 0.0000 |
| 2023-01-11 | 1.1252 | 1.1332 | 0.0080 |
| 2023-01-12 | 1.1254 | 1.1334 | 0.0080 |
| 2023-12-31 | 1.1566 | 1.1646 | 0.0080 |

Interpretation：

- The unit-vs-accumulated difference changes from `0.0000` to `0.0080` exactly on the provider page dividend date.
- The difference matches the annual report distribution amount per share: every 10 shares `0.080` equals every share `0.0080`.
- This supports accepting Eastmoney/Akshare `累计净值走势` as an `accumulated_nav` source candidate for E-class source/basis identity.
- This does not prove dividend-reinvested NAV or total-return basis. It proves additive accumulated NAV behavior around the known cash distribution.

## Candidate Disposition Matrix

### `单位净值走势` / `Data_netWorthTrend`

| Class | Code | Identity status if JS identity is integrated | nav_type | adjusted_basis | dividend_adjustment_status | Failure / status |
|---|---:|---|---|---|---|---|
| A | 006597 | `verified` | `unit_nav` | `raw_unit_nav` | `not_adjusted` | Not strong evidence |
| C | 006598 | `verified` | `unit_nav` | `raw_unit_nav` | `not_adjusted` | Not strong evidence |
| E | 014217 | `verified` | `unit_nav` | `raw_unit_nav` | `not_adjusted` | Not strong evidence; E has known distribution |
| F | 022176 | `verified` | `unit_nav` | `raw_unit_nav` | `not_adjusted` | Not strong evidence |

`raw_unit_nav` remains blocked for strong drawdown evidence even when identity is verified.

### `累计净值走势` / `Data_ACWorthTrend`

| Class | Code | Identity status if JS identity is integrated | nav_type | adjusted_basis | dividend_adjustment_status | Evidence-level history status | Recommendation |
|---|---:|---|---|---|---|---|---|
| A | 006597 | `verified` | `accumulated_nav` | `accumulated_nav` | `adjusted` for cash distributions; no distribution observed | none | Accept as source/basis candidate; source page and annual report say no distributions, so accumulated equals unit NAV for the observed range |
| C | 006598 | `verified` | `accumulated_nav` | `accumulated_nav` | `adjusted` for cash distributions; no distribution observed | none | Accept as source/basis candidate; source page and annual report say no distributions, so accumulated equals unit NAV for the observed range |
| E | 014217 | `verified` | `accumulated_nav` | `accumulated_nav` | `adjusted` for cash distributions additively | none | Accept as source/basis candidate; exact-date cross-check matches 0.0080 per-share distribution |
| F | 022176 | `verified` | `accumulated_nav` | `accumulated_nav` | `adjusted` for cash distributions; no distribution observed | `insufficient_history` for 2023 and any pre-2024-10-08 window; model mapping `missing_date_range` | Block for historical windows before inception; accept only for source-inception-forward basis candidate |

Important limitation：`accumulated_nav` is not a dividend-reinvested total-return path. Future drawdown suitability still needs a separate reviewed metric contract / implementation gate.

### `累计收益率走势` / `LJSYLZS`

| Class | Code | Identity status if JS identity is integrated | nav_type | adjusted_basis | dividend_adjustment_status | Failure / status |
|---|---:|---|---|---|---|---|
| A | 006597 | `verified` | `unknown` | `unknown` | `unknown` | `adjustment_basis_unknown`; row count 202 vs 1809 daily NAV rows |
| C | 006598 | `verified` | `unknown` | `unknown` | `unknown` | `adjustment_basis_unknown`; row count 202 vs 1809 daily NAV rows |
| E | 014217 | `verified` | `unknown` | `unknown` | `unknown` | `adjustment_basis_unknown`; row count 250 vs 994 daily NAV rows |
| F | 022176 | `verified` | `unknown` | `unknown` | `unknown` | `adjustment_basis_unknown`; source-inception-forward rows 398 but no total-return semantics proof |

Reason：no source-owned semantics found that defines `LJSYLZS` as total-return or dividend-reinvested path. Do not accept from field name alone.

## Recommended Decision

Recommended terminal result：`partial-acceptance-with-blocked-classes`

Accepted source/basis candidate：

- Source：Eastmoney / 天天基金, accessed through Akshare `fund_open_fund_info_em` plus same-provider JS identity metadata.
- Exact source endpoint/function：
  - data function: `ak.fund_open_fund_info_em(symbol=<code>, indicator="累计净值走势")`
  - identity URL: `https://fund.eastmoney.com/pingzhongdata/{code}.js`
- Source identity proof：
  - `fS_code` equals requested code for 006597 / 006598 / 014217 / 022176.
  - `fS_name` includes exact share-class suffix A / C / E / F.
- Accepted `nav_type`：`accumulated_nav`
- Accepted `adjusted_basis`：`accumulated_nav`
- Accepted `dividend_adjustment_status`：`adjusted` for cash distributions additively; not total-return reinvestment.
- Share classes covered：
  - A `006597`: accepted source/basis identity candidate.
  - C `006598`: accepted source/basis identity candidate.
  - E `014217`: accepted source/basis identity candidate with exact dividend-date cross-check.
  - F `022176`: accepted only for source-inception-forward candidate windows.
- Insufficient classes/windows：
  - F `022176` is `insufficient_history` for 2023 and any window before 2024-10-08; map to current model `missing_date_range`.
  - `LJSYLZS` / `累计收益率走势` is blocked for all classes as `adjustment_basis_unknown`.

Why not `accepted-source-basis-candidate` for all：

- F class cannot cover 2023 or pre-inception windows.
- `累计收益率走势` / `LJSYLZS` lacks source-owned total-return semantics proof.
- `accumulated_nav` still requires a future metric suitability decision before any drawdown implementation.

Why not `blocked-with-source-gap`：

- Source identity is verified for all four codes through same-provider `fS_code` / `fS_name`.
- `累计净值走势` behavior for E class incorporates the exact 0.0080 per-share distribution on 2023-01-11, matching both provider dividend metadata and annual report distribution amount.

## Non-Goals Preserved

- `drawdown_stress` blocker remains unchanged.
- `raw_unit_nav` remains not strong evidence.
- No max drawdown or volatility was implemented.
- No production code/tests were modified.
- No score, snapshot, quality gate, golden fixture, bond extractor, Host/Agent/dayu, QDII/FOF/110020, release, PR, push or merge state changed.
- No extractor direct source dependency was introduced.

## Validation

Run / inspected：

- `git branch --show-current`
- `git status --short`
- `uv run python` Akshare/source smoke for all A/C/E/F classes and three indicators.
- `uv run python` Akshare source inspection for `fund_open_fund_info_em`.
- `uv run python` `FundDocumentRepository.load_annual_report("006597", 2025)` §3 / parsed table inspection.
- Public provider pages:
  - <https://fund.eastmoney.com/006597.html>
  - <https://fund.eastmoney.com/006598.html>
  - <https://fund.eastmoney.com/014217.html>
  - <https://fund.eastmoney.com/022176.html>
  - <https://fundtest.eastmoney.com/help/question_250.html>

Not run：

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`

Reason：this slice added only a docs/reviews evidence artifact and did not modify Python, tests, schema, score, quality gate, runtime behavior or production source path.

## Next Minimal Gate

If controller accepts this evidence, the next minimal gate should be a source adapter normalization implementation plan, not drawdown metric implementation:

- Add a source adapter path that can fetch `累计净值走势` and same-provider source identity metadata.
- Normalize identity into `NavSourceMetadata.returned_fund_code` / `returned_fund_name` and `ShareClassMapping`.
- Emit `nav_type="accumulated_nav"`, `adjusted_basis="accumulated_nav"`, and explicit `dividend_adjustment_status`.
- Fail closed on `identity_mismatch`, `schema_drift`, `adjustment_basis_unknown`, `missing_date_range`, or `insufficient_records`.
- Keep `drawdown_stress` unresolved until a later metric contract and implementation gate accepts how accumulated NAV may be consumed.
