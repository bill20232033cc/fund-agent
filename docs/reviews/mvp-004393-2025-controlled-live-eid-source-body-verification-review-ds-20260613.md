# DS Review: 004393 / 2025 Controlled Live EID Source-body Verification Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Controlled Live EID Source-body Verification Sub-slice`

Reviewer role: DS evidence reviewer

Verdict: `PASS_WITH_FINDINGS`

## 1. Scope

This review assesses the evidence artifact
`docs/reviews/mvp-004393-2025-controlled-live-eid-source-body-verification-evidence-20260613.md`
against the four review lenses defined by the current gate.

It does not authorize live EID/network/PDF/FDR/provider/LLM/analyze/checklist/
readiness/release/PR commands, source/test/golden/control doc edits, commit,
push, or entry into another gate.

## 2. Lens-by-lens Assessment

### Lens 1: Is the live/repository access evidence within the user-authorized bounded sub-slice?

**PASS.**

The evidence states user authorization was received in-chat. Access was bounded to
`FundDocumentRepository().load_annual_report("004393", 2025)` — a single fund,
single year, single call. Only the seven controller-accepted candidate rows were
verified. No provider, LLM, analyze, checklist, readiness, release, PR, or
fallback-expansion commands were run. The two fee rows were explicitly excluded
from verification. The boundary matches the accepted sub-slice.

Observation: `parsed_cache_hit=true` means this was de facto a warm-cache
execution, not a fresh live EID fetch. The evidence acknowledges this
transparently. Under the user's live authorization this is not a violation — a
cache hit on a `load_annual_report()` call that COULD have gone live is still a
repository-bounded live-sub-slice execution.

### Lens 2: Does metadata support EID single-source, no fallback, report_year 2025, fund_code 004393?

**PASS.**

Repository metadata:

| Contract field | Required | Evidence value | Match |
|---|---|---|---|
| source | `eid` | `eid` | ✓ |
| selected_source | `eid` | `eid` | ✓ |
| source_mode | `single_source_only` | `single_source_only` | ✓ |
| fallback_enabled | `false` | `false` | ✓ |
| fallback_used | `false` | `false` | ✓ |
| report_year | 2025 | 2025 | ✓ |
| fund_code | 004393 | present in load call parameter; report_name resolves to 安信企业价值优选混合 | ✓ |
| report_code | FB010010 | FB010010 (annual report) | ✓ |

Fund identity is confirmed by report_name containing the expected fund name
(`安信企业价值优选混合型证券投资基金`). Fund code is present in the load
parameter and further confirmed by the row-level match of `fund_code=004393`
in table 0 row 1. Single-source/no-fallback contract is satisfied.

### Lens 3: Are exactly the seven accepted candidate rows verified, and are the two fee rows still excluded?

**PASS.**

Controller-accepted rows (7) — all verified:

| Row | Controller disposition | Evidence disposition |
|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED` |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `PASS_SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` |

Controller-rejected rows (2) — excluded:

| Row | Controller disposition | Evidence status |
|---|---|---|
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | Not verified (correctly excluded) |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | Not verified (correctly excluded) |

Summary: `verified_rows=7, passed_rows=7, failed_rows=0, rejected_fee_rows_verified=0`.

No `turnover_rate` row was added or verified — consistent with the accepted
regulatory applicability truth.

### Lens 4: Are row-level page/table/row locators and whitespace-normalized long-text matches sufficient for source-body verified candidate status?

**PASS_WITH_FINDINGS.**

Row-by-row locator assessment:

| Row | Locator | Label match | Value match | Sufficient? |
|---|---|---|---|---|
| `fund_name` | p5 t0 headers | `基金名称` ✓ | exact match | Yes |
| `fund_code` | p5 t0 r1 | `基金主代码` → `基金代码` is acceptable | `004393` | Yes |
| `management_company` | p5 t0 r4 | `基金管理人` ✓ | exact match | Yes |
| `custodian` | p5 t0 r5 | `基金托管人` ✓ | exact match | Yes |
| `inception_date` | p5 t0 r3 | `基金合同生效日` → `成立日期` is acceptable | `2022年8月8日` | Yes |
| `investment_objective` | p5 t1 headers | `投资目标` ✓ | whitespace-normalized match | Yes |
| `benchmark.benchmark_name` | p5 t1 r1 | `业绩比较基准` ✓ | whitespace-normalized match | Yes |

All seven rows have page/table/row coordinates from `ParsedTable`. The five
`basic_identity` rows are on page 5 table 0 (the basic-info table). The
`product_profile` and `benchmark` rows are on page 5 table 1 (the product-profile
table). This is structurally plausible for §2.1 of the annual report.

Whitespace normalization (collapsing embedded `\n` introduced by PDF line wrapping)
is a legitimate text-extraction normalization for long-text fields. Both
`investment_objective` and `benchmark.benchmark_name` show `\n` breaks in the
source body at positions consistent with PDF line wrapping, not content divergence.

Findings recorded below.

## 3. Findings

| ID | Severity | Finding | Evidence basis |
|---|---|---|---|
| DS-F1 | LOW | Execution was de facto a warm-cache probe, not a fresh live EID fetch (`parsed_cache_hit=true`, `pdf_cache_hit=false`). The live authorization path was not exercised because the repository returned cached parsed content. | Metadata §2 |
| DS-F2 | LOW | Row locators use `ParsedTable` internal indices (`table 0`, `table 1`) rather than formal annual-report table numbers or section references. This reduces locator stability if parsing internals change. | Verification matrix §4 |
| DS-F3 | LOW | The verification script is described but not fully reproduced. The evidence states an "initial helper run produced two false negatives" and a "corrected verification run" was used. The exact normalization rules (e.g., `\n` → space vs `\n` → empty) and the corrected script are not recorded, limiting independent reproduction. | Evidence §3 |
| DS-F4 | INFO | All seven verified rows map to page 5 only. This is structurally plausible (page 5 typically carries §2.1 basic info), but means the verification surface is a single page of the annual report. No cross-page or cross-section consistency check was performed. | Verification matrix §4 |

## 4. Row Disposition After DS Review

| Row | Prior controller disposition | DS review disposition | Reasoning |
|---|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED` | Exact match against p5 t0 header label `基金名称`. |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED` | Exact match `004393` at p5 t0 r1 label `基金主代码`. |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED` | Exact match at p5 t0 r4 label `基金管理人`. |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED` | Exact match at p5 t0 r5 label `基金托管人`. |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED` | Exact match at p5 t0 r3 label `基金合同生效日`. |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` | Whitespace-normalized match at p5 t1 header label `投资目标`. Prior `MEDIUM_CONFIDENCE` residual is now resolved by actual body verification. |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | `SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` | Whitespace-normalized match at p5 t1 r1 label `业绩比较基准`. Formula exactness (characters, spaces, operator ordering) matches after normalization. |
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | `EXCLUDED` (no change) | Not verified. |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | `EXCLUDED` (no change) | Not verified. |

## 5. Residuals

| Residual | Owner | Severity | Destination |
|---|---|---|---|
| Two rows passed with whitespace normalization; normalization rules are implicit. | Evidence owner | LOW | Future source-body verification gates should specify normalization contract (e.g., collapse `\n` → space, trim trailing, preserve CJK). |
| Verification script not fully reproduced. | Evidence owner | LOW | If independent reproduction is required, the corrected script should be recorded in a follow-up artifact. |
| `ParsedTable` internal indices used as locators. | Fund documents owner | LOW | Future gates may want formal annual-report table/section references for locator stability. |

## 6. Next Entry Recommendation

Seven rows are source-body verified with adequate locators and value matches.
The prior `SOURCE_BODY_RESIDUAL` and `MEDIUM_CONFIDENCE` dispositions are
resolved by actual body verification.

Recommended next entry:

```text
004393 / 2025 Tracked Golden Content Write Planning Gate
```

The next gate may treat the seven rows as source-body-verified candidates
(5 at plain `SOURCE_BODY_VERIFIED`, 2 at `SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION`)
and may decide whether these seven rows can be written to tracked golden content
with source-body verification provenance recorded in the write artifact.

Constraints for the next gate:
- Must remain planning-only unless separately authorized for implementation.
- Must not authorize fixture promotion, readiness/release claims, or PR actions.
- The two fee rows remain excluded.
- No `turnover_rate` row.

## 7. Boundary Confirmation

This review did not perform or authorize:
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR commands;
- source/test/golden/control doc edits;
- local PDF/data directory inspection;
- commit, stage, push, PR, or entry into another gate.
