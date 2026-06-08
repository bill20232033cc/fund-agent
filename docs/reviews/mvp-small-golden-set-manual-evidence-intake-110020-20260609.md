# Manual Evidence Intake: 110020 2024 Annual Report Source Identity

## Gate Metadata

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Scope: docs-only evidence intake.
- Fund code: `110020`.
- Report year: `2024`.
- Document kind: `annual_report`.
- Evidence provider: `user_provided`.
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-110020-20260609-source-payload.json`.
- Source payload SHA256: `898b29082998b9849dbba35d0436d7810b3f1ee2e6c9886b605555af9d1800d0`.

## Boundary Statement

This artifact only records user-provided official locator/id/metadata/checksum. It does not verify the URLs, open the URLs, read a PDF, hash a PDF, call `FundDocumentRepository`, use fallback, use akshare/EID tooling, run network commands, or run live LLM/provider probes.

No PDF SHA256 was provided for this row. The `user_provided_pdf_sha256` field is therefore recorded as `not_provided`.

## User-Provided Source Identity Fields

| Field | Recorded value |
|---|---|
| `fund_code` | `110020` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `official_search_url` | `http://eid.csrc.gov.cn/fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=110020` |
| `official_fund_detail_url` | `unknown` |
| `official_document_url` | `https://cdn.efunds.com.cn/owch/data/bulletin/20250331/%E6%98%93%E6%96%B9%E8%BE%BE%E6%B2%AA%E6%B7%B1300%E4%BA%A4%E6%98%93%E5%9E%8B%E5%BC%80%E6%94%BE%E5%BC%8F%E6%8C%87%E6%95%B0%E5%8F%91%E8%B5%B7%E5%BC%8F%E8%AF%81%E5%88%B8%E6%8A%95%E8%B5%84%E5%9F%BA%E9%87%91%E8%81%94%E6%8E%A5%E5%9F%BA%E9%87%912024%E5%B9%B4%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A.pdf` |
| `official_document_id` | `efunds-bulletin-20250331-annual-report-110020` |
| `official_announcement_id` | `unknown` |
| `source_document_title` | `易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告` |
| `source_publisher` | `易方达基金管理有限公司` |
| `source_registry` | `易方达基金官网 CDN；EID search locator provided, EID document id unknown` |
| `publication_date` | `2025-03-31` |
| `fund_name` | `易方达沪深300交易型开放式指数发起式证券投资基金联接基金` |
| `share_class.target` | `A` |
| `share_class.target_code` | `110020` |
| `share_class.other_classes` | `C=007339`; `Y=022928` |
| `user_provided_pdf_sha256` | `not_provided` |

## User-Provided Identity Anchors

| Anchor | User-provided source | User-provided evidence |
|---|---|---|
| `registry_metadata` | `易方达基金官网 PDF / bulletin path` | `公告标题=易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告；公告路径日期=20250331` |
| `pdf_title_page` | `official PDF title page` | `标题=易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告；基金管理人=易方达基金管理有限公司` |
| `pdf_profile` | `§2 基金简介 / 2.1 基金基本情况` | `基金主代码=110020；基金名称=易方达沪深300交易型开放式指数发起式证券投资基金联接基金；下属分级基金交易代码 A=110020，C=007339，Y=022928` |

## Intake Assessment Before Review

| Check | Result |
|---|---|
| Official locator/id present | PASS: `official_document_url` and `official_document_id=efunds-bulletin-20250331-annual-report-110020` are present. |
| Fund code present | PASS: `110020` is present in user-provided profile anchor. |
| Report year present | PASS: `2024` is present in title and gate field. |
| Document kind annual report | PASS: `document_kind=annual_report` and title says `2024年年度报告`. |
| Publisher present | PASS: `易方达基金管理有限公司`. |
| Publication date present | PASS: `2025-03-31`. |
| Share class present | PASS: target class `A=110020`; other classes `C=007339`, `Y=022928`. |
| PDF SHA256 | DEFERRED: user did not provide PDF SHA256. This does not block manual identity intake because official locator/id is present, but it cannot prove PDF bytes. |
| Fallback used | PASS: no fallback used or invoked in this docs-only intake. |
| Source/PDF/network access | PASS: none performed. |
| Exact/numeric correctness | BLOCKED: no row-field exact/numeric assertions accepted. |
| Fixture projection | BLOCKED: no fixture change or projection in this gate. |

## Preliminary Row Decision

`110020 / 2024` is ready for independent review as a user-provided manual source identity candidate.

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

- This artifact does not externally verify EID/Efunds metadata or PDF content.
- This artifact does not retain PDF bytes or extracted PDF text.
- This artifact does not create retained minimal field excerpts.
- EID document id remains unknown in user-provided metadata.
- `Y=022928` class was added from 2024-12-13 per user-provided note; future field-level assertions must distinguish share-class columns.
- PDF byte identity is not proved because no user-provided PDF SHA256 was supplied.
- Exact/numeric extractor correctness remains blocked until a later row-field gate accepts field-specific anchors and expected values.
- Existing small golden fixture rows remain unchanged in this gate.
