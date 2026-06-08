# Manual Evidence Intake: 004194 2024 Annual Report Source Identity

## Gate Metadata

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Scope: docs-only evidence intake.
- Fund code: `004194`.
- Report year: `2024`.
- Document kind: `annual_report`.
- Evidence provider: `user_provided`.
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004194-20260609-source-payload.json`.
- Source payload SHA256: `3db311f49cb6528eafc565edc18cc9504bc7ed2917479d2cc58ea0779f7e87d3`.

## Boundary Statement

This artifact only records user-provided official locator/id/metadata/checksum. It does not verify the URLs, open the URLs, read a PDF, hash a PDF, call `FundDocumentRepository`, use fallback, use akshare/EID tooling, run network commands, or run live LLM/provider probes.

No PDF SHA256 was provided for this row. The `user_provided_pdf_sha256` field is therefore recorded as `not_provided`.

## User-Provided Source Identity Fields

| Field | Recorded value |
|---|---|
| `fund_code` | `004194` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `official_search_url` | `http://eid.csrc.gov.cn/fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=004194` |
| `official_fund_detail_url` | `http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=1488&rnd=0.41437996451709624` |
| `official_document_url` | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248907` |
| `official_document_id` | `instanceid=1248907` |
| `official_announcement_id` | `unknown` |
| `source_document_title` | `招商中证1000 指数增强型证券投资基金2024 年年度报告` |
| `source_publisher` | `招商基金管理有限公司` |
| `source_registry` | `中国证监会基金电子披露网站 / EID` |
| `publication_date` | `2025-03-28` |
| `fund_name` | `招商中证1000指数增强型证券投资基金` |
| `share_class.target` | `A` |
| `share_class.target_code` | `004194` |
| `share_class.other_classes` | `C=004195` |
| `user_provided_pdf_sha256` | `not_provided` |

## User-Provided Identity Anchors

| Anchor | User-provided source | User-provided evidence |
|---|---|---|
| `registry_metadata` | `EID search/detail page` | `fundCode=004194；reportType=FB010；公告标题=招商中证1000 指数增强型证券投资基金2024 年年度报告；披露日期=2025-03-28；document instanceid=1248907` |
| `pdf_title_page` | `official PDF title page` | `标题=招商中证1000 指数增强型证券投资基金2024 年年度报告；基金管理人=招商基金管理有限公司；报告送出日期=2025-03-28` |
| `pdf_profile` | `§2 基金简介 / 基金产品概况` | `基金主代码=004194；下属分级基金交易代码 A=004194；C=004195` |

## Intake Assessment Before Review

| Check | Result |
|---|---|
| Official locator/id present | PASS: `official_document_url` and `official_document_id=instanceid=1248907` are present. |
| Fund code present | PASS: `004194` is present in user-provided registry metadata and profile anchor. |
| Report year present | PASS: `2024` is present in title and gate field. |
| Document kind annual report | PASS: `document_kind=annual_report` and title says `2024 年年度报告`. |
| Publisher present | PASS: `招商基金管理有限公司`. |
| Publication date present | PASS: `2025-03-28`. |
| Share class present | PASS: target class `A=004194`, other class `C=004195`. |
| PDF SHA256 | DEFERRED: user did not provide PDF SHA256. This does not block manual identity intake because official locator/id is present, but it cannot prove PDF bytes. |
| Fallback used | PASS: no fallback used or invoked in this docs-only intake. |
| Source/PDF/network access | PASS: none performed. |
| Exact/numeric correctness | BLOCKED: no row-field exact/numeric assertions accepted. |
| Fixture projection | BLOCKED: no fixture change or projection in this gate. |

## Preliminary Row Decision

`004194 / 2024` is ready for independent review as a user-provided manual source identity candidate.

Preliminary status before review:

- `identity_status`: `matched`.
- `identity_review_status`: `pending_review`.
- `source_boundary`: `manual_review`.
- `source_failure_category`: `none`.
- `fallback_allowed`: `false`.
- `fallback_used`: `false`.
- `exact_numeric_correctness_allowed`: `false`.
- `fixture_projection_allowed_in_this_gate`: `false`.

## Residuals

- This artifact does not externally verify EID metadata or PDF content.
- This artifact does not retain PDF bytes or extracted PDF text.
- This artifact does not create retained minimal field excerpts.
- PDF byte identity is not proved because no user-provided PDF SHA256 was supplied.
- Exact/numeric extractor correctness remains blocked until a later row-field gate accepts field-specific anchors and expected values.
- Existing small golden fixture rows remain unchanged in this gate.
