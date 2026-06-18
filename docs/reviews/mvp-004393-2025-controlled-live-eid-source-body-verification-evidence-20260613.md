# 004393 / 2025 Controlled Live EID Source-body Verification Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Controlled Live EID Source-body Verification Sub-slice`

Status: `EVIDENCE_READY_FOR_REVIEW`

## 1. Scope

This evidence verifies only the seven accepted candidate rows from
`docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-controller-judgment-20260613.md`
against the `004393 / 2025` annual-report body.

User authorization for the bounded live sub-slice was received in-chat before
the repository command was executed.

This evidence did not edit tracked golden answer content, did not promote
fixtures, did not change source/tests/runtime behavior, did not run provider,
LLM, analyze, checklist, readiness, release or PR commands, and did not use
Eastmoney, fund-company official site, CNINFO or fallback expansion.

## 2. Source Path

Access path:

```text
FundDocumentRepository().load_annual_report("004393", 2025)
```

Repository metadata:

| Metadata field | Value |
|---|---|
| `source.source` | `eid` |
| `source.selected_source` | `eid` |
| `source.source_mode` | `single_source_only` |
| `source.fallback_enabled` | `false` |
| `source.fallback_used` | `false` |
| `source.report_year` | `2025` |
| `source.report_code` | `FB010010` |
| `source.report_desp` | `年度报告` |
| `source.report_name` | `安信企业价值优选混合型证券投资基金2025年年度报告` |
| `source.upload_info_id` | `1447922` |
| `source.upload_info_detail_id` | `1494773` |
| `source.report_send_date` | `2026-03-27` |
| `cache.parsed_cache_hit` | `true` |
| `cache.pdf_cache_hit` | `false` |
| `cache.source_metadata_present` | `true` |
| `cache.cache_schema_version` | `1` |

The repository call returned an EID single-source/no-fallback parsed report.
Although the live sub-slice was authorized, this execution hit the parsed report
cache and did not require a fresh PDF fetch.

## 3. Verification Method

The verification script:

1. loaded the report through `FundDocumentRepository`;
2. checked the seven candidate expected values only;
3. searched parsed report tables for the row-local label and expected value;
4. compared values after whitespace normalization to handle PDF line wrapping;
5. recorded page/table/row coordinates from `ParsedTable`.

An initial helper run produced two false negatives because the script failed to
normalize PDF line breaks correctly. The corrected verification run is the
accepted evidence below.

Corrected command class:

```text
uv run python -c "<load FundDocumentRepository; compare 7 candidate rows with whitespace normalization>"
```

## 4. Row Verification Matrix

| Row | Expected value | Source-body match | Disposition |
|---|---|---|---|
| `basic_identity.fund_name` | `安信企业价值优选混合型证券投资基金` | page 5 table 0 headers: `基金名称` / `安信企业价值优选混合型证券投资基金` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.fund_code` | `004393` | page 5 table 0 row 1: `基金主代码` / `004393` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.management_company` | `安信基金管理有限责任公司` | page 5 table 0 row 4: `基金管理人` / `安信基金管理有限责任公司` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.custodian` | `中国银行股份有限公司` | page 5 table 0 row 5: `基金托管人` / `中国银行股份有限公司` | `PASS_SOURCE_BODY_VERIFIED` |
| `basic_identity.inception_date` | `2022年8月8日` | page 5 table 0 row 3: `基金合同生效日` / `2022年8月8日` | `PASS_SOURCE_BODY_VERIFIED` |
| `product_profile.investment_objective` | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。` | page 5 table 1 headers: `投资目标` / `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争\n实现基金资产的长期稳健增值。` | `PASS_SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` |
| `benchmark.benchmark_name` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%` | page 5 table 1 row 1: `业绩比较基准` / `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+\n中债综合（全价）指数收益率×20%` | `PASS_SOURCE_BODY_VERIFIED_WITH_WHITESPACE_NORMALIZATION` |

Summary:

```text
verified_rows=7
passed_rows=7
failed_rows=0
rejected_fee_rows_verified=0
```

## 5. Explicit Non-verification

The two fee rows remain rejected for this route and were not verified here:

- `fee_schedule.management_fee`
- `fee_schedule.custody_fee`

No `turnover_rate` row was verified or added. Current accepted applicability
truth keeps `turnover_rate` non-applicable for this 2025 annual-report route.

## 6. Boundary Confirmation

This evidence did not perform or authorize:

- tracked golden answer content edits;
- fixture promotion edits;
- source/test/runtime behavior changes;
- provider, LLM, analyze, checklist, readiness, release or PR commands;
- Eastmoney, fund-company official site, CNINFO or source fallback expansion;
- cleanup, archive, push, merge or external-state actions.

## 7. Next Entry Recommendation

Recommended next entry after review/controller acceptance:

```text
004393 / 2025 Tracked Golden Content Write Planning Gate
```

The next gate must remain planning-only unless separately authorized for
implementation. It may use the seven `PASS_SOURCE_BODY_VERIFIED` rows as
source-body-verified candidates, but must still avoid fixture promotion,
readiness/release claims and PR external-state actions.
