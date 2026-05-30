# CSRC EID and stock-sdk NAV Source Evaluation Gate — Controller Judgment

日期：2026-05-28

角色：Gateflow controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

## Verdict

**Accepted local evidence.**

Controller decisions：

- CSRC EID：`accepted-primary-candidate`
- stock-sdk：`evidence-only`

本 gate 只裁决 source identity / accumulated NAV source candidacy，不实现 runtime adapter，不实现 max drawdown / volatility，不解除 `drawdown_stress` blocker，不修改 score、snapshot、quality gate、golden fixture 或生产 Python 路径。

## Preflight And Scope

Gate 开始前已先运行：

```text
git branch --show-current
git status --short
```

结果：

- Branch：`codex/local-reconciliation`
- Tracked dirty：无
- Dirty scope：仅既有无关 untracked 文件；本 gate 新增 plan / review / evidence / judgment artifacts。

本 gate 使用 tmux multi-agent flow：

- Codex：planning worker、planning fix worker、evidence worker。
- DS / GLM：plan review、plan re-review、evidence review。
- MiMo：未用于本轮，因为本轮 review 派发和完成时不在 00:00-08:00 review window。

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md` |
| Plan review: DS | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-review-ds-20260528.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-review-glm-20260528.md` |
| Plan re-review: DS | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-rereview-ds-20260528.md` |
| Plan re-review: GLM | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-rereview-glm-20260528.md` |
| Evidence | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md` |
| Evidence review: DS | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-review-ds-20260528.md` |
| Evidence review: GLM | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-review-glm-20260528.md` |

Accepted plan commit：

```text
0868183 gateflow: accept plan for CSRC EID stock-sdk NAV source evaluation
```

## Controller Decision

### CSRC EID

CSRC EID is accepted as a future primary `accumulated_nav` source candidate.

Accepted source metadata：

- `source_name`：`csrc_eid`
- Provider：`eid.csrc.gov.cn`
- Verified internal ID：`5755`
- Public search proof：
  - `国泰利享中短债债券` -> `fundId=5755`
  - `006597` -> `fundId=5755`
  - `006598` -> `fundId=5755`
  - `014217` -> `fundId=5755`
  - `022176` direct search missing, but F share class is present in the verified detail page and classification links.
- Detail page：`fund_detail_search.do?cFundCode=5755`
- NAV rows：machine-readable HTML with `估值日期`, `单位净值`, `累计净值`, `基金资产净值`, `备注`.
- Share-class separation：product fundCode `006597` plus classification IDs:
  - A `006597`: `2030-1010`
  - C `006598`: `2030-1020`
  - E `014217`: `2030-1040`
  - F `022176`: `2030-1050`
- Accepted `adjustment_basis`：`accumulated_nav`
- Not accepted：`dividend_adjusted_nav`, `total_return`.

Per-share coverage：

| Code | Class | Date range / rows | Decision |
|---:|---|---|---|
| `006597` | A | 1809 rows, 2018-12-07 to 2026-05-28; earliest blank accumulated rows caveat | accepted for complete accumulated-nav windows |
| `006598` | C | 1809 rows, 2018-12-07 to 2026-05-28; earliest blank accumulated rows caveat | accepted for complete accumulated-nav windows |
| `014217` | E | 994 rows, 2022-04-25 to 2026-05-28 | accepted; exact distribution cross-check |
| `022176` | F | 398 rows, source-inception-forward | accepted for source-inception-forward windows; pre-inception windows remain `missing_date_range` |

E-class proof anchor：

- `FundDocumentRepository.load_annual_report("006597", 2025)` confirms E-class 2023 distribution every 10 shares `0.080`.
- CSRC EID E-class rows show `accumulated_nav - unit_nav` changed from `0.0000` to `0.0080` on `2023-01-11`, matching every-share distribution amount.

### stock-sdk

stock-sdk is accepted only as `evidence-only`.

Accepted facts：

- Package：`stock-sdk@1.10.0`
- Repository：`git+https://github.com/chengzuopeng/stock-sdk.git`
- License：`ISC`
- Runtime：Node `>=18.0.0`
- Dependencies：none reported by npm metadata.
- `getFundDividendList` correctly returns 014217 E-class 2023 dividend metadata matching annual-report §3.3.

Rejected runtime / typed source reasons：

- `getFundNavHistory` provider lineage is Eastmoney `pingzhongdata/{code}.js`; it does not improve source provenance over the already accepted Eastmoney/Akshare path.
- `getFundNavHistory` has a date-normalization `integrity_error`: values align with CSRC/Eastmoney after a one-day offset, but the exposed `date` field is shifted. `date` is part of typed NAV record identity, so this output cannot be consumed as runtime typed series as-is.
- It must not be added as a project runtime dependency or subprocess adapter without a later architecture / implementation gate and a fix or bypass for the date issue.

## Review Disposition

Plan review:

- DS initially required two fixes:
  - Add explicit `getFundDividendList` evaluation steps.
  - Do not assume `cFundCode=5755`; first locate CSRC EID internal ID through public search.
- Codex planning fix addressed both and also added non-blocking improvements.
- DS and GLM re-review both accepted.

Evidence review:

- DS accepted with non-blocking findings:
  - stock-sdk date computation source location not pinned to exact file/line.
  - A/C earliest blank accumulated rows were not fully enumerated.
  - §3.1 year-end NAV reconciliation was not systemically executed.
  - stock-sdk +1 row count discrepancy was not explained.
  - stock-sdk date-shift wording could be more precise.
- GLM accepted with non-blocking findings:
  - stock-sdk row count discrepancy not explicitly explained.
  - A/C blank accumulated NAV date set not fully listed.
  - `dividendPerShare` precision appears as `0.008` vs `0.0080`.
  - shared `retrieved_at` timestamp is evidence-session level.

Controller accepts these as future adapter implementation residuals, not blockers to source disposition.

## Residuals

Future CSRC EID adapter constraints:

- Adapter must bind public search / validated internal ID / classification links before fetching rows.
- Adapter must keep A/C/E/F separated and must not treat product-level rows as share-class NAV.
- Adapter must implement full pagination and fail closed on pagination gaps, duplicate dates, bad decimals, missing accumulated NAV, and HTML schema drift.
- A/C earliest blank accumulated NAV rows must be handled with explicit requested-window semantics.
- F direct-search gap must be handled through verified detail-page classification only; if classification cannot be verified, fail closed.
- CSRC EID HTML endpoints are not versioned APIs; parser must treat schema change as `schema_drift`.

Future stock-sdk disposition:

- Keep as evidence-only unless a later gate proves date handling is fixed and decides a Node/subprocess/runtime dependency boundary.
- `getFundDividendList` may be useful for independent cross-checks, but does not make stock-sdk a primary source.
- If using stock-sdk JSON numeric values in any future diagnostic, convert through Decimal-safe string paths where possible.

`drawdown_stress` blocker remains:

- Runtime typed NAV path is still raw-unit-only.
- No CSRC EID adapter has been implemented.
- No drawdown metric contract has accepted accumulated NAV as a metric input.
- Latest `006597 / 2024` score remains blocked by `drawdown_stress`.

## Validation

Run / reviewed:

- `git branch --show-current`
- `git status --short`
- CSRC EID public search, detail page, classification pages, pagination and E-class distribution-window smoke
- `npm view stock-sdk ...`
- temporary `/tmp` `npm pack` / Node smoke for stock-sdk
- `FundDocumentRepository.load_annual_report("006597", 2025)`
- DS / GLM plan review and re-review
- DS / GLM evidence review

Not run:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- extraction snapshot / score / quality gate

Reason：this gate changed only `docs/reviews/` evidence/control artifacts and did not modify Python, tests, schema, runtime behavior, score, snapshot, quality gate, or golden fixtures.

## Next Entry Point

Next minimal gate：

```text
CSRC EID accumulated NAV adapter normalization implementation gate
```

Objective：

- Implement a Fund data source adapter / repository path that fetches CSRC EID accumulated NAV through the typed NAV boundary.
- Normalize `source_name`, `source_url`, `retrieved_at`, internal ID, classification ID, share-class identity, date range, record count, `unit_nav`, `accumulated_nav`, `adjustment_basis="accumulated_nav"`, and fail-closed categories into `FundNavSeries`, `NavSourceMetadata`, and `ShareClassMapping`.
- Keep current raw unit NAV path explicitly not strong evidence.
- Do not implement drawdown metric or unblock `drawdown_stress` in that adapter gate.

Non-goal：

- No drawdown metric, score policy, snapshot, quality gate, golden fixture, release, PR, push, merge, or promotion work.
