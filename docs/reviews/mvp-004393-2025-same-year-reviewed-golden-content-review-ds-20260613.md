# DS Review - 004393 / 2025 Same-year Reviewed Golden Content Evidence

Date: 2026-06-13

Reviewer role: DS

Gate: `004393 / 2025 Same-year Reviewed Golden Content Evidence Gate`

Verdict: `PASS_WITH_FINDINGS`

## Findings

| ID | Severity | Row or scope | Evidence | Recommendation |
|---|---|---|---|---|
| DS-F1 | Medium | `fee_schedule.management_fee`, `fee_schedule.custody_fee` | `docs/golden-answer-template.md` marks `fee_schedule` as skipped for `004393`; `docs/golden-answer-instructions.md` also lists `fee_schedule` as a skipped row family. | Do not accept these two fee rows in this gate. If fee fields should enter the comparable golden contract, open a separate contract/schema or source-owner clarification gate. |
| DS-F2 | Medium | Fee row source locators | The accepted plan requires source to prefer `§<section> page-<page>` and table evidence to carry table/row locator; fee rows only cite `年报2025 §5 management_fee` / `年报2025 §5 custody_fee`. | Reject or defer the fee rows until stable locators are provided. |
| DS-F3 | Low | All accepted candidate rows | Candidate artifact supplies locators and values but no row-local excerpt; plan says product smoke output cannot supply row truth and direct annual-report body was not read in this gate. | Candidate rows may be accepted only as candidates; do not upgrade them to primary-source or strict golden truth. |

## Row Dispositions

| Row | Disposition | Reason |
|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE` | Field is in the current comparable contract; source locator is specific enough for candidate status. |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE` | Field is in contract; value matches fund identity; locator is acceptable for candidate status. |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE` | Field is in contract; same §2 table locator can support candidate status. |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE` | Field is in contract; same §2 table locator can support candidate status. |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE` | Field is in contract; date value and locator are plausible for candidate status. |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE` | Field is in contract; `medium` confidence is reasonable because the long text span requires boundary judgment. |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE` | Field is in contract; locator points to §2 table; formula exactness remains a later verification point. |
| `fee_schedule.management_fee` | `REJECT` | Current accepted template/instructions mark `fee_schedule` as skipped, and locator specificity is insufficient. |
| `fee_schedule.custody_fee` | `REJECT` | Current accepted template/instructions mark `fee_schedule` as skipped, and locator specificity is insufficient. |

## Residuals

- Seven rows may proceed only as accepted candidate rows.
- Two fee rows are excluded from this gate's accepted candidate set.
- Tracked golden content write, fixture promotion and release/readiness remain separate gates.
