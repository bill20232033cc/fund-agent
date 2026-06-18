# Controller Judgment: 004393 / 2025 Controlled Live EID Source-body Verification

Date: 2026-06-13

Gate: `004393 / 2025 Controlled Live EID Source-body Verification Sub-slice`

Evidence:
`docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-evidence-20260613.md`

Review inputs:

- `docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-review-mimo-20260613.md`
- `docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-review-ds-20260613.md`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## 1. Controller Scope

This judgment accepts only the bounded source-body verification result for seven
previously accepted candidate rows for `004393 / 2025`.

It does not authorize tracked golden answer content edits, fixture promotion,
provider/LLM/analyze/checklist/readiness/release/PR commands, cleanup, push,
merge, or external-state actions.

Release/readiness remains `NOT_READY`.

## 2. Accepted Source Path Facts

| Fact | Controller disposition | Basis |
|---|---|---|
| User authorized the bounded live sub-slice before the repository command. | `ACCEPT` | In-chat authorization and evidence scope |
| Access used `FundDocumentRepository().load_annual_report("004393", 2025)`. | `ACCEPT` | Evidence §2; MiMo and DS reviews |
| Returned source metadata is EID single-source/no-fallback. | `ACCEPT` | `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false` |
| Returned report identity is `004393 / 2025` annual report. | `ACCEPT` | `report_year=2025`, `report_code=FB010010`, row-local `fund_code=004393`, report name |
| Execution hit parsed report cache. | `ACCEPT_WITH_RESIDUAL` | `cache.parsed_cache_hit=true`; this is acceptable for source-body verification after authorization but is not fresh-fetch evidence |

## 3. Row Disposition

| Row | Prior disposition | Source-body verification result | Controller disposition |
|---|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 0 headers exact match | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE` |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 0 row 1 exact match | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE` |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 0 row 4 exact match | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE` |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 0 row 5 exact match | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE` |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 0 row 3 exact match | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE` |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | page 5 table 1 headers match after PDF whitespace normalization | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE_WITH_WHITESPACE_NORMALIZATION` |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | page 5 table 1 row 1 match after PDF whitespace normalization | `ACCEPT_SOURCE_BODY_VERIFIED_CANDIDATE_WITH_WHITESPACE_NORMALIZATION` |
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | not verified | `EXCLUDED_NO_CHANGE` |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | not verified | `EXCLUDED_NO_CHANGE` |

No `turnover_rate` row is added or verified.

## 4. Review Finding Disposition

| Finding | Source | Controller disposition | Rationale |
|---|---|---|---|
| Evidence is within the bounded authorized repository sub-slice. | MiMo / DS | `ACCEPT` | Scope was single fund/year and seven rows only. |
| Metadata supports EID single-source/no-fallback. | MiMo / DS | `ACCEPT` | Required source fields are present and no fallback was used. |
| Seven rows are verified and two fee rows remain excluded. | MiMo / DS | `ACCEPT` | Row count and exclusion match prior controller judgment. |
| DS-F1 / MiMo F02: execution hit parsed cache, not a fresh live fetch or fresh PDF re-parse. | DS / MiMo | `ACCEPT_AS_RESIDUAL_NOT_BLOCKING` | The gate purpose is source-body verification through repository after live authorization, not proof of fresh network fetch. Cache-origin context must be carried into downstream write planning. |
| DS-F2: locators use `ParsedTable` internal indices rather than formal annual-report table numbers. | DS | `ACCEPT_AS_LOW_RESIDUAL` | Page/table/row coordinates are sufficient for candidate write planning, but future stable locator work may need formal table numbering. |
| DS-F3 / MiMo F01: corrected verification script is summarized but not fully reproduced. | DS / MiMo | `ACCEPT_AS_LOW_RESIDUAL` | The evidence records the comparison method and row results. Future evidence gates should include the exact normalization rule or script when reproducibility is required. |
| DS-F4: all seven rows are on page 5. | DS | `ACCEPT_AS_INFO` | This is structurally expected for §2 fund profile/basic information and does not imply an evidence gap for these rows. |

## 5. Accepted Result

The seven candidate rows are accepted as source-body-verified candidates for
future tracked golden content write planning.

They are not yet accepted as tracked strict golden truth because no tracked
golden write implementation has been planned, reviewed, implemented or accepted.

## 6. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Seven rows are source-body-verified candidates but not tracked strict golden truth. | Golden content owner | `004393 / 2025 Tracked Golden Content Write Planning Gate` |
| Verification used parsed cache, not a fresh PDF fetch/re-parse. | Evidence owner | Carry as context in write planning; do not claim fresh-fetch proof |
| Two long-text rows rely on whitespace normalization for PDF line wrapping. | Golden content/evidence owner | Write planning should preserve this provenance note |
| ParsedTable internal locators are sufficient for current planning but not formal annual-report table numbers. | Fund documents owner | Future locator stability gate if needed |
| Two fee rows remain excluded. | Golden contract/source owner | Separate fee-row clarification gate if needed |
| Fixture promotion remains unresolved and year-blind. | Fixture promotion owner | Separate fixture promotion design/evidence gate |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup only |

## 7. Next Entry

Recommended next entry:

```text
004393 / 2025 Tracked Golden Content Write Planning Gate
```

Required constraints:

- planning-only unless the user separately authorizes implementation;
- may use exactly the seven source-body-verified candidate rows;
- must exclude the two fee rows unless a separate clarification gate accepts
  them;
- must not promote fixtures, claim readiness/release, push, PR, merge or change
  external state.

## 8. Boundary Confirmation

This judgment did not perform or authorize:

- tracked golden answer content edits;
- fixture promotion edits;
- source/test/runtime behavior changes;
- provider, LLM, analyze, checklist, readiness, release or PR commands;
- Eastmoney, fund-company official site, CNINFO or source fallback expansion;
- cleanup, archive, push, merge or external-state actions.
