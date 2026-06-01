# CSRC EID and stock-sdk NAV Source Evaluation Gate — Evidence

日期：2026-05-28

角色：AgentCodex evidence worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Accepted plan：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`

Recommended decision：

- CSRC EID：`accepted-primary-candidate`
- stock-sdk：`evidence-only`（not runtime / not typed secondary source as-is）

## Step Self-Check

- Current gate / role：本 artifact 只产出 E1-E4 source evidence；不启动 gateflow，不 implement、commit、push、PR、merge、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、前序 NAV adjusted-basis source identity controller judgment / evidence、accepted plan、`nav_models.py`、`nav_repository.py`、`nav_data.py`。
- Scope boundary：只新增本 evidence artifact；未改 production code/tests、dependency files、score、snapshot、quality gate、golden fixture、drawdown metric、Host/Agent/dayu。
- Evidence boundary：CSRC EID 和 stock-sdk smoke 都是 evidence-only；stock-sdk 使用 `/tmp` 解包 / Node 直接加载包产物，没有修改项目 `pyproject.toml`、`package.json` 或 lockfile。
- Stop condition check：source smoke 全部可分类；未遇到不可分类 source failure。

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
- This evidence slice adds only `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md`.

## Truth Source Summary

- Current architecture remains `UI -> Service -> Host -> Agent`; NAV source/repository candidates belong only under Agent-layer Fund data boundary.
- Current production `FundNavRepository.load_nav_series()` still normalizes only Akshare `单位净值走势` into `raw_unit_nav`, `requested_code_only`, and `strong_drawdown_evidence_eligible=False`.
- Current typed model taxonomy can represent `nav_type="accumulated_nav"` and `adjusted_basis="accumulated_nav"`, and must fail closed on `schema_drift`, `identity_mismatch`, `integrity_error`, `adjustment_basis_unknown`, `missing_date_range`, `insufficient_records`, `not_found`, `unavailable`.
- Prior accepted evidence already accepts Eastmoney / 天天基金 `Data_ACWorthTrend` / `累计净值走势` as future `accumulated_nav` candidate for A/C/E and F source-inception-forward windows; `LJSYLZS` remains `adjustment_basis_unknown`.
- This gate does not解除 `drawdown_stress` blocker and does not decide max drawdown / volatility suitability.

## Commands Run

CSRC EID smoke:

```text
python - <<'PY'
# urllib standard-library GET/POST only.
# GET /fund/disclose/index.html
# GET /fund/js_new/index.js?ver=0.3
# POST /fund/disclose/validate_fund.do with cFundCode values:
#   国泰利享中短债债券, 006597, 006598, 014217, 022176, 5755
# GET /fund/disclose/fund_detail_search.do?cFundCode=5755
# GET /fund/disclose/list_net_daily.do?reportType=FB040&fundCode=006597
# GET /fund/disclose/list_net_classification.do?reportType=FB040&fundCode=006597&classification=<A/C/E/F classification>
# GET classification pages with limit/start pagination.
PY
```

stock-sdk inspection / smoke:

```text
npm view stock-sdk version license repository homepage dist.tarball dependencies peerDependencies engines --json
npm view stock-sdk versions --json
npm view stock-sdk readme --json
npm view stock-sdk main module types exports files bin --json
npm view stock-sdk dist.integrity dist.shasum gitHead time --json
tmp=$(mktemp -d /tmp/stock-sdk.XXXXXX) && cd "$tmp" && npm pack stock-sdk@1.10.0 --silent && tar -xzf stock-sdk-1.10.0.tgz
rg -n "getFundNavHistory|getFundDividendList|Data_ACWorthTrend|fund.eastmoney" /tmp/stock-sdk.../package
node --input-type=module - <<'NODE'
# imports /tmp package/dist/index.js, calls getFundNavHistory for 006597/006598/014217/022176
# calls getFundDividendList({ year: 2023, page: 'all', code: '014217' })
NODE
```

Annual-report reconciliation:

```text
uv run python - <<'PY'
from fund_agent.fund.documents import FundDocumentRepository
# await FundDocumentRepository().load_annual_report("006597", 2025)
PY
```

No annual-report PDF/cache direct reads were used.

## E1 — CSRC EID Evidence

### Public Search / Internal ID

CSRC EID index JS exposes the public search flow:

- Search function posts to `/fund/disclose/validate_fund.do?t=<random>`.
- POST body uses explicit `cFundCode=<user input>`.
- Successful result redirects to `/fund/disclose/fund_detail_search.do?cFundCode=<data.fundId>&rnd=<random>`.

Observed search results:

| Input | Response | Interpretation |
|---|---|---|
| `国泰利享中短债债券` | `{"fundId":5755,"isSuccess":true}` | fund family maps to EID internal ID `5755` |
| `006597` | `{"fundId":5755,"isSuccess":true}` | A class maps to internal ID `5755` |
| `006598` | `{"fundId":5755,"isSuccess":true}` | C class maps to internal ID `5755` |
| `014217` | `{"fundId":5755,"isSuccess":true}` | E class maps to internal ID `5755` |
| `022176` | `{"isSuccess":false}` | F class direct public-search mapping missing |
| `国泰利享中短债债券F` | `{"isSuccess":false}` | F class name direct public-search mapping missing |
| `5755` | `{"isSuccess":false}` | `5755` is not a public code; it is internal ID |

Interpretation:

- User-supplied candidate `cFundCode=5755` is verified through CSRC public search for product name and A/C/E share codes.
- F class is not searchable directly by code/name, but the official `5755` detail page contains the F share class `022176` and F classification history link. This is a CSRC search-index limitation, not a detail-page identity mismatch.

### Detail Page / Share-Class Granularity

Verified URL:

```text
http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=5755&rnd=<random>
```

The page is machine-readable HTML and contains:

- Title identity：`国泰利享中短债债券(006597)`.
- A class：`净值日报国泰利享中短债债券A(006597)`.
- C class：`净值日报国泰利享中短债债券C(006598)`.
- E class：`净值日报国泰利享中短债债券E(014217)`.
- F class：`净值日报国泰利享中短债债券F(022176)`.
- Columns：`估值日期`, `单位净值`, `累计净值`, `基金资产净值`, `备注`.
- More links per share class:
  - A：`../disclose/list_net_classification.do?reportType=FB040&fundCode=006597&classification=2030-1010`
  - C：`../disclose/list_net_classification.do?reportType=FB040&fundCode=006597&classification=2030-1020`
  - E：`../disclose/list_net_classification.do?reportType=FB040&fundCode=006597&classification=2030-1040`
  - F：`../disclose/list_net_classification.do?reportType=FB040&fundCode=006597&classification=2030-1050`

Granularity:

- CSRC EID uses product/fundCode `006597` plus `classification` to expose share-class-level rows.
- Row fields include main fund code, returned share-class code, share-class name, unit NAV, accumulated NAV, asset NAV, valuation date, remark.
- A/C/E/F can be kept separate. This satisfies the plan's share-class separation requirement despite the F search-index gap.

### Pagination / Record Counts / Date Ranges

Classification pages expose stable HTML pagination:

```text
/fund/disclose/list_net_classification.do?1=1&fundCode=006597&classification=<classification>&limit=20&start=<offset>
```

Pagination examples:

- E class page shows `第 1 页 / 共50页`, `记录：1-20 / 共994条`, last page start `980`.
- A/C pages show `共91页`, `共1809条`.
- F page shows `共20页`, `共398条`.

Observed per-class samples:

| Share class | Code | Classification | Rows | First / earliest checked | Latest checked | Latest unit / accumulated | Notes |
|---|---:|---:|---:|---|---|---|---|
| A | 006597 | `2030-1010` | 1809 | 2018-12-07 | 2026-05-28 | `1.2275 / 1.2275` | earliest two rows have blank accumulated NAV |
| C | 006598 | `2030-1020` | 1809 | 2018-12-07 | 2026-05-28 | `1.2094 / 1.2094` | earliest two rows have blank accumulated NAV |
| E | 014217 | `2030-1040` | 994 | 2022-04-25 | 2026-05-28 | `1.2033 / 1.2113` | full source-inception window has accumulated NAV |
| F | 022176 | `2030-1050` | 398 | inferred from total rows; sampled latest through 2026-03-02 | 2026-05-28 | `1.2273 / 1.2273` | source-inception-forward only; pre-2024-10-08 remains missing_date_range by prior evidence |

A/C earliest-row caveat:

- A 2018-12-14 and 2018-12-07 rows have unit NAV but blank accumulated NAV.
- C 2018-12-14 and 2018-12-07 rows have unit NAV but blank accumulated NAV.
- From 2018-12-18 onward, A/C accumulated NAV is populated and equals unit NAV in sampled rows.
- This is not a blocker for recent date windows, but future adapter must classify requests that require blank accumulated rows as `missing_date_range` or `schema_drift` / `integrity_error` depending on explicit window semantics.

### E-Class Distribution Cross-Check

CSRC EID E-class rows around the known 2023 distribution:

| Date | Unit NAV | Accumulated NAV | Difference |
|---|---:|---:|---:|
| 2023-01-10 | 1.1332 | 1.1332 | 0.0000 |
| 2023-01-11 | 1.1252 | 1.1332 | 0.0080 |
| 2023-01-12 | 1.1254 | 1.1334 | 0.0080 |
| 2023-01-13 | 1.1256 | 1.1336 | 0.0080 |

Annual report via `FundDocumentRepository.load_annual_report("006597", 2025)`:

- Metadata source：`eid`.
- Source URL：`http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1450363`.
- Metadata fund_id：`5755`.
- Report name：`国泰利享中短债债券型证券投资基金2025年年度报告`.
- §2 maps share classes and codes：A `006597`, C `006598`, E `014217`, F `022176`.
- §3.3 records E class 2023 distribution：每 10 份 `0.080`, cash `7,273,431.12`, reinvested `1,871,517.43`, total `9,144,948.55`; A/C no distribution in past three years; F no distribution since added.
- §3.1 records E-class year-end NAV values including `2025年末 1.1967`.

Interpretation:

- CSRC EID accumulated NAV behaves as additive `accumulated_nav` around the known E-class distribution.
- Evidence proves `adjustment_basis="accumulated_nav"`, not `dividend_adjusted_nav` and not `total_return`.

### CSRC EID Failure Classification

| Condition | Classification |
|---|---|
| F code `022176` direct public search fails while official detail page contains F | not a terminal failure; record as search-index limitation |
| Product/detail page not found for name/A/C/E search | would be `not_found` |
| Cannot parse detail/list HTML schema or pagination | would be `schema_drift` |
| Product-level data cannot split share classes | would be `identity_mismatch`; not observed |
| Earliest A/C rows with blank accumulated NAV requested by explicit window | future adapter should fail closed as `missing_date_range` or `schema_drift` / `integrity_error` depending on requested contract |

Recommended CSRC EID disposition：`accepted-primary-candidate`.

## E2 — stock-sdk Evidence

### Package / License / Dependency Model

NPM metadata:

- Package：`stock-sdk`
- Version：`1.10.0`
- Repository：`git+https://github.com/chengzuopeng/stock-sdk.git`
- Homepage：`https://stock-sdk.linkdiary.cn`
- License：`ISC`
- Engines：`node >=18.0.0`
- Dependencies：none reported by `npm view`; package describes itself as zero-dependency.
- Main/module/types：`./dist/index.cjs`, `./dist/index.js`, `./dist/index.d.ts`.
- Published：`2026-05-27T11:44:28.633Z`
- gitHead：`fd41063a30a36e9dc7908df9cdc1f15bdb1818f4`

API surface from `dist/index.d.ts`:

- `getFundDividendList(options?: FundDividendListOptions): Promise<FundDividendListResult>`
- `getFundNavHistory(code: string): Promise<FundNavHistory>`
- `FundNavPoint` fields：`date`, `timestamp`, `nav`, `accNav`, `dailyReturn`, `unitMoney`.
- `FundDividend` fields：`code`, `name`, `equityRecordDate`, `exDividendDate`, `dividendPerShare`, `payDate`, `raw`.

Provider lineage from package d.ts / bundled source:

- `getFundNavHistory` doc states source is `fund.eastmoney.com/pingzhongdata/{code}.js`.
- Bundled source requests `https://fund.eastmoney.com/pingzhongdata/{code}.js` and parses `fS_code`, `fS_name`, `Data_netWorthTrend`, `Data_ACWorthTrend`.
- `getFundDividendList` uses `https://fund.eastmoney.com/Data/funddataIndex_Interface.aspx` and fields `pageinfo`, `jjfh_data`.

Interpretation:

- stock-sdk is not an independent source; it is a JavaScript client over the same Eastmoney / 天天基金 lineage already accepted in the prior gate.
- License is permissive and package is lightweight, but introducing Node runtime into production would still require a separate architecture/implementation gate. No dependency was added in this evidence gate.

### `getFundNavHistory` Smoke

Command used `/tmp/stock-sdk.../package/dist/index.js` directly without project dependency mutation.

Observed result:

| Code | Returned name | Count | First item | Last item | 2023-01-11 item |
|---:|---|---:|---|---|---|
| 006597 | 国泰利享中短债债券A | 1810 | `2018-12-02 nav=1 accNav=1` | `2026-05-27 nav=1.2275 accNav=1.2275` | `nav=1.1353 accNav=1.1353` |
| 006598 | 国泰利享中短债债券C | 1810 | `2018-12-02 nav=1 accNav=1` | `2026-05-27 nav=1.2094 accNav=1.2094` | `nav=1.1261 accNav=1.1261` |
| 014217 | 国泰利享中短债债券E | 994 | `2022-04-24 nav=1.119 accNav=1.119` | `2026-05-27 nav=1.2033 accNav=1.2113` | `nav=1.1254 accNav=1.1334` |
| 022176 | 国泰利享中短债债券F | 398 | `2024-10-07 nav=1.1924 accNav=1.1924` | `2026-05-27 nav=1.2273 accNav=1.2273` | n/a |

Critical date-normalization issue:

- CSRC EID and prior Akshare evidence place latest 2026-05-28 values at 2026-05-28, but stock-sdk returns the same values dated 2026-05-27.
- CSRC EID E-class 2023-01-12 values are `1.1254 / 1.1334`; stock-sdk returns those values under `date="2023-01-11"`.
- CSRC EID E-class 2023-01-11 values are `1.1252 / 1.1332`; stock-sdk does not align those values to `date="2023-01-11"`.
- The bundled source computes `date` via `new Date(timestamp).toISOString().slice(0,10)`, which appears to convert Eastmoney local-market timestamps into UTC calendar dates and shift displayed dates by one day.

Failure classification:

- `getFundNavHistory` source identity is verified through `fS_code` / `fS_name`.
- Unit and accumulated NAV values are present and line up with Eastmoney/CSRC values after a one-day display offset.
- Because the public API's `date` field is part of the typed NAV record identity, the observed one-day date shift is an `integrity_error` for runtime typed contract use as-is.

### `getFundDividendList` Smoke

Command:

```text
sdk.getFundDividendList({ year: 2023, page: "all", code: "014217" })
```

Observed result:

```json
{
  "totalPages": 62,
  "pageSize": 100,
  "currentPage": -1,
  "count": 1,
  "first": {
    "code": "014217",
    "name": "国泰利享中短债债券E",
    "equityRecordDate": "2023-01-11",
    "exDividendDate": "2023-01-11",
    "dividendPerShare": 0.008,
    "payDate": "2023-01-12",
    "raw": ["014217", "国泰利享中短债债券E", "2023-01-11", "2023-01-11", "0.008", "2023-01-12", ""]
  }
}
```

Cross-check:

- stock-sdk dividend list matches annual report §3.3 every 10 shares `0.080` = every share `0.0080`.
- It also matches provider/Eastmoney accepted event date `2023-01-11`.
- stock-sdk `getFundNavHistory` values prove a `0.0080` accumulated-minus-unit gap, but the date field is shifted, so NAV-history event-level date alignment remains unsafe as runtime typed evidence.

### stock-sdk Disposition

Recommended decision：`evidence-only`.

Reasons:

- Positive：license is permissive, package is lightweight, API exists, provider lineage is transparent, dividend list cross-check is useful, and NAV values include unit + accumulated fields.
- Negative：underlying provider is Eastmoney, so stock-sdk does not improve source provenance over the prior accepted Eastmoney/Akshare evidence.
- Blocking for runtime：`getFundNavHistory` exposes a date-normalization `integrity_error`; typed NAV consumers cannot use the returned `date` field as-is.
- Runtime dependency / subprocess adapter would require a separate architecture/implementation gate and a fix or bypass for stock-sdk's date normalization.

## E3 — Cross-Source Reconciliation

### Source Availability

| Source | NAV rows? | Identity status | Reconciliation status |
|---|---:|---|---|
| CSRC EID | yes | verified for A/C/E/F through product ID + classification rows | executed |
| stock-sdk getFundNavHistory | yes | verified code/name but date integrity failure | values inspected; not accepted as typed series |
| Eastmoney/Akshare accepted evidence | yes | verified by prior gate | used as reference |
| Annual report via FundDocumentRepository | n/a | official EID annual report metadata fund_id `5755` | used as anchor |

### Numeric Reconciliation

CSRC EID vs prior Eastmoney/Akshare:

- A/C/E/F row counts and latest values align with prior Eastmoney/Akshare evidence.
- E-class distribution cross-check matches exactly:
  - Annual report §3.3：every 10 shares `0.080`.
  - CSRC EID：`accumulated_nav - unit_nav` changes from `0.0000` to `0.0080` on 2023-01-11.
  - Prior Eastmoney/Akshare：same event-level behavior accepted.

stock-sdk vs CSRC/Eastmoney:

- Values align after date offset, but exposed `date` does not align.
- Because date is a required typed key for path metrics, stock-sdk cannot be accepted as runtime candidate without fixing or bypassing date conversion.

### Basis Decision

- CSRC EID：accepted only as `adjustment_basis="accumulated_nav"`.
- stock-sdk：its provider basis is Eastmoney `Data_ACWorthTrend`, but API output has `integrity_error`; use as evidence-only/cross-check, not typed source.
- `dividend_adjusted_nav` and `total_return` are not proven by either new source.
- Raw unit NAV remains blocked for strong drawdown evidence.

## E4 — Source Disposition Matrix

### CSRC EID

| Code | Share class | source_name | source_url/provider | retrieved_at | date_range | record_count | unit_nav | accumulated_nav | adjustment_basis | identity_status | failure_category |
|---:|---|---|---|---|---|---:|---|---|---|---|---|
| 006597 | A | `csrc_eid` | `eid.csrc.gov.cn` detail ID `5755`, classification `2030-1010` | 2026-05-28T15:45:54Z | 2018-12-07 to 2026-05-28, with earliest blank accumulated rows caveat | 1809 | present | present except earliest blank rows | `accumulated_nav` for complete rows/windows | `verified` | null for complete windows; earliest blank rows require fail-closed window handling |
| 006598 | C | `csrc_eid` | `eid.csrc.gov.cn` detail ID `5755`, classification `2030-1020` | 2026-05-28T15:45:54Z | 2018-12-07 to 2026-05-28, with earliest blank accumulated rows caveat | 1809 | present | present except earliest blank rows | `accumulated_nav` for complete rows/windows | `verified` | null for complete windows; earliest blank rows require fail-closed window handling |
| 014217 | E | `csrc_eid` | `eid.csrc.gov.cn` detail ID `5755`, classification `2030-1040` | 2026-05-28T15:45:54Z | 2022-04-25 to 2026-05-28 | 994 | present | present | `accumulated_nav` | `verified` | null |
| 022176 | F | `csrc_eid` | `eid.csrc.gov.cn` detail ID `5755`, classification `2030-1050` | 2026-05-28T15:45:54Z | source-inception-forward, latest 2026-05-28; total rows 398 | 398 | present | present | `accumulated_nav` for source-inception-forward windows | `verified` through detail page; direct public search missing | null for source-inception-forward; pre-inception windows `missing_date_range` |

CSRC EID decision：`accepted-primary-candidate`.

Controller constraints to carry forward:

- Future adapter must bind public search/validated internal ID and share-class classification links.
- Future adapter must fail closed on F direct-search gap only if it cannot verify F through detail/classification page.
- Future adapter must handle A/C earliest blank accumulated NAV rows with explicit requested-date logic.

### stock-sdk

| Code | Share class | source_name | source_url/provider | retrieved_at | date_range | record_count | unit_nav | accumulated_nav | adjustment_basis | identity_status | failure_category |
|---:|---|---|---|---|---|---:|---|---|---|---|---|
| 006597 | A | `stock_sdk` | Eastmoney `pingzhongdata/006597.js`; stock-sdk `1.10.0` | 2026-05-28T15:45:54Z | API reports 2018-12-02 to 2026-05-27 | 1810 | `nav` present | `accNav` present | provider candidate `accumulated_nav`, API not accepted | `verified` code/name | `integrity_error` due one-day date shift |
| 006598 | C | `stock_sdk` | Eastmoney `pingzhongdata/006598.js`; stock-sdk `1.10.0` | 2026-05-28T15:45:54Z | API reports 2018-12-02 to 2026-05-27 | 1810 | `nav` present | `accNav` present | provider candidate `accumulated_nav`, API not accepted | `verified` code/name | `integrity_error` due one-day date shift |
| 014217 | E | `stock_sdk` | Eastmoney `pingzhongdata/014217.js`; stock-sdk `1.10.0` | 2026-05-28T15:45:54Z | API reports 2022-04-24 to 2026-05-27 | 994 | `nav` present | `accNav` present | provider candidate `accumulated_nav`, API not accepted | `verified` code/name | `integrity_error` due one-day date shift |
| 022176 | F | `stock_sdk` | Eastmoney `pingzhongdata/022176.js`; stock-sdk `1.10.0` | 2026-05-28T15:45:54Z | API reports 2024-10-07 to 2026-05-27 | 398 | `nav` present | `accNav` present | provider candidate `accumulated_nav`, API not accepted | `verified` code/name | `integrity_error` due one-day date shift; pre-inception windows remain `missing_date_range` |

Dividend API:

| Code | source_name | source_url/provider | Date | Amount | Identity | Failure |
|---:|---|---|---|---:|---|---|
| 014217 | `stock_sdk` | Eastmoney `funddataIndex_Interface.aspx` | equity/ex-dividend `2023-01-11`, pay `2023-01-12` | `0.008` per share | `verified` | null for dividend record |

stock-sdk decision：`evidence-only`.

## Recommended Controller Decisions

1. Accept CSRC EID as a future primary `accumulated_nav` source candidate, subject to a later adapter normalization implementation gate.
2. Do not accept stock-sdk as runtime dependency, subprocess adapter, or typed secondary source as-is. Keep it evidence-only because `getFundNavHistory` has a date-normalization `integrity_error`.
3. Preserve prior Eastmoney/Akshare `Data_ACWorthTrend` acceptance. stock-sdk does not provide independent provenance because it wraps the same provider endpoint.
4. Do not解除 `drawdown_stress` blocker. This gate supplies source identity / semantics evidence only.
5. Do not classify either source as `dividend_adjusted_nav` or `total_return`; accepted basis is only `accumulated_nav`.

## Non-Goals Preserved

- No production code/tests were modified.
- No project dependency files were modified.
- No adapter, drawdown metric, max drawdown, volatility, score, snapshot, quality gate, golden fixture, Host/Agent/dayu, release, PR, push, merge, or promotion change occurred.
- Annual-report evidence used only `FundDocumentRepository`.
- Raw unit NAV remains not strong evidence.

## Validation

Run / inspected:

- `git branch --show-current`
- `git status --short`
- CSRC EID public search POST `/fund/disclose/validate_fund.do`.
- CSRC EID detail page and per-share classification history pages.
- CSRC EID pagination and E-class 2023-01-11 distribution-window rows.
- `npm view stock-sdk ...`
- Temporary `/tmp` npm pack/extract for `stock-sdk@1.10.0`.
- Node smoke for `getFundNavHistory` and `getFundDividendList`.
- `uv run python` `FundDocumentRepository.load_annual_report("006597", 2025)`.

Not run:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- snapshot / score / quality gate.

Reason：this is an evidence-only docs/reviews gate and did not modify production Python, tests, schema, runtime behavior, score, snapshot, quality gate, or golden fixtures.

## Completion Report

```text
Self-check: pass
Artifact path: docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md
CSRC EID decision: accepted-primary-candidate
stock-sdk decision: evidence-only
Accepted adjustment_basis: accumulated_nav
Rejected/blocked bases: raw_unit_nav, adjustment_basis_unknown, dividend_adjusted_nav, total_return
Per-code coverage:
- 006597 A: CSRC verified, 1809 rows, accumulated_nav candidate; stock-sdk verified but NAV date integrity_error
- 006598 C: CSRC verified, 1809 rows, accumulated_nav candidate; stock-sdk verified but NAV date integrity_error
- 014217 E: CSRC verified, 994 rows, exact 2023-01-11 distribution cross-check; stock-sdk dividend list matches but NAV date integrity_error
- 022176 F: CSRC verified through detail/classification page, 398 rows source-inception-forward; direct CSRC search missing; stock-sdk verified but NAV date integrity_error
Provider/license/runtime disposition:
- CSRC EID: official, machine-readable, primary candidate with adapter caveats
- stock-sdk: Eastmoney wrapper, ISC, Node >=18, zero dependency, evidence-only due date normalization integrity_error
Annual report reconciliation: §2 share-class mapping, §3.1 E NAV, §3.3 E distribution via FundDocumentRepository
Validation: evidence-only commands listed above
Residual risks / controller decisions needed: CSRC adapter pagination/window handling; stock-sdk date bug disposition; no drawdown metric decision
Non-goals preserved: no code/tests, no drawdown blocker解除, no metric, no score/snapshot/quality/golden, no dependency, no PR/push/release
```
