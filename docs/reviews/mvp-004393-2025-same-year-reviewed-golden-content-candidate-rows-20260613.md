# 004393 / 2025 Same-year Reviewed Golden Content Candidate Rows

Date: 2026-06-13

Source status: `CANDIDATE_ROWS_FOR_REVIEW_NOT_ACCEPTED`

Gate: `004393 / 2025 Candidate Row Source Preparation Gate`

## Boundary

This artifact is a candidate-row source package only. It does not accept rows as
strict golden truth, does not edit tracked golden content, does not promote
fixtures, does not prove release readiness and does not authorize PR or external
state changes.

The rows below are derived from already accepted single-sample live output
locators and visible 2025 annual-report source lines. The live output remains
product/evidence material, not row truth. The next evidence gate must review
each row independently before any later tracked content write can be proposed.

## Source Inputs Read

| Source | Use in this gate | Disposition |
|---|---|---|
| `docs/current-startup-packet.md` | Current gate and boundary truth | `repo/control truth` |
| `docs/implementation-control.md` | Active gate, accepted input and non-goals | `repo/control truth` |
| `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-20260613.md` | Candidate row contract | `accepted plan truth` |
| `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-controller-judgment-20260613.md` | Conditional next-entry truth | `accepted controller truth` |
| `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/stdout.md` | Candidate locator/value source lines only | `accepted single-sample live output; not row truth` |
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Field/sub-field shape reference only | `2024 corpus; not 2025 row truth` |

## Candidate Rows

## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2025
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 安信企业价值优选混合型证券投资基金 | high | 年报2025 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 004393 | high | 年报2025 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 安信基金管理有限责任公司 | high | 年报2025 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 中国银行股份有限公司 | high | 年报2025 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2022年8月8日 | high | 年报2025 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。 | medium | 年报2025 §2 page-5 page-5-table-1 investment_objective |
| benchmark | benchmark_name | 沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20% | high | 年报2025 §2 page-5 page-5-table-1 benchmark |
| fee_schedule | management_fee | 1.20% | high | 年报2025 §5 management_fee |
| fee_schedule | custody_fee | 0.20% | high | 年报2025 §5 custody_fee |

## Candidate Shape Check

- Explicit fund block: `PASS`; heading is `004393 安信企业价值优选混合A（国内股票类）`.
- Explicit report year metadata: `PASS`; fenced `golden-answer-metadata` declares `report_year: 2025`.
- Five-column reviewed Markdown table: `PASS`; table columns are `field`, `sub_field`, `expected_value`, `confidence`, `source`.
- Candidate row count: `PASS`; 9 candidate rows are present.
- Duplicate candidate identity: `PASS`; no duplicate `(004393, 2025, field, sub_field)` identity is present.
- Tracked golden content write: `PASS`; this artifact is under `docs/reviews/`; no `reports/golden-answers/` file is edited.

## Deferred / Excluded Candidate Lines

- `classified_fund_type.fund_type`: `DEFER_NOT_READ`; current output says `active_fund`, but the same output also says fund category is undisclosed and classification is derived. Evidence gate should decide whether this row can be accepted under direct 2025 source rules.
- `nav_benchmark_performance.nav_growth_rate`: `DEFER_NOT_READ`; current appendix line names the table/row locator but does not expose the exact percentage value in the visible source-line snippet.
- `nav_benchmark_performance.benchmark_return_rate`: `DEFER_NOT_READ`; current appendix line names the table/row locator but does not expose the exact percentage value in the visible source-line snippet.
- `share_change.beginning_share` / `ending_share` / `net_change`: `DEFER_NOT_READ`; product output contains values, but the visible appendix source line only identifies the table and row family. Needs row-local review before candidate inclusion.
- `manager_alignment.manager_holding` / `employee_holding`: `DEFER_NOT_READ`; product output contains long table text; row-local exactness should be reviewed in the evidence gate or a source-owner clarification pass before inclusion.
- `turnover_rate`: `DEFER_NOT_DISCLOSED`; current accepted applicability truth says 2025 and earlier annual reports do not disclose turnover rate; it is non-applicable for scoring and not a candidate golden row here.

## Next Gate Recommendation

Because this artifact exists, contains candidate rows and follows the reviewed
Markdown `report_year: 2025` shape, the next mainline entry should be:

```text
004393 / 2025 Same-year Reviewed Golden Content Evidence Gate
```

The evidence gate must still treat every row above as unaccepted until reviewed
and judged row-by-row.
