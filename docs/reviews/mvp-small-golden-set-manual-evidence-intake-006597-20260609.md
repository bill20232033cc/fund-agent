# Manual Evidence Intake: 006597 2024 Annual Report Source Identity

## Gate Metadata

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Scope: docs-only evidence intake.
- Fund code: `006597`.
- Report year: `2024`.
- Document kind: `annual_report`.
- Evidence provider: `user_provided`.
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-006597-20260609-source-payload.json`.
- Source payload SHA256: `c982303b16e212eb3661c9585f910f59d4bd59d8715a63100673075214419b33`.

## Boundary Statement

This artifact only records user-provided official locator/id/metadata/checksum. It does not verify the URLs, open the URLs, read a PDF, hash a PDF, call `FundDocumentRepository`, use fallback, use akshare/EID tooling, run network commands, or run live LLM/provider probes.

No PDF SHA256 was provided for this row. The `user_provided_pdf_sha256` field is therefore recorded as `not_provided`.

## User-Provided Source Identity Fields

| Field | Recorded value |
|---|---|
| `fund_code` | `006597` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `official_search_url` | `http://eid.csrc.gov.cn/fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=006597` |
| `official_fund_detail_url` | `unknown` |
| `official_document_url` | `https://static.cninfo.com.cn/finalpage/2025-03-29/1222957988.PDF` |
| `official_document_id` | `cninfo:1222957988` |
| `official_announcement_id` | `unknown` |
| `source_document_title` | `国泰利享中短债债券型证券投资基金2024年年度报告` |
| `source_publisher` | `国泰基金管理有限公司` |
| `source_registry` | `巨潮资讯 / CNINFO；EID search locator provided, EID document id unknown` |
| `publication_date` | `2025-03-29` |
| `fund_name` | `国泰利享中短债债券型证券投资基金` |
| `share_class.target` | `A` |
| `share_class.target_code` | `006597` |
| `share_class.other_classes` | `C=006598`; `E=014217`; `F=022176` |
| `user_provided_pdf_sha256` | `not_provided` |

## User-Provided Identity Anchors

| Anchor | User-provided source | User-provided evidence |
|---|---|---|
| `registry_metadata` | `CNINFO PDF metadata/search result` | `公告标题=国泰利享中短债债券型证券投资基金2024年年度报告；PDF id=1222957988；披露日期/报告送出日期=2025-03-29` |
| `pdf_title_page` | `official PDF title page` | `标题=国泰利享中短债债券型证券投资基金2024年年度报告；基金管理人=国泰基金管理有限公司；报告送出日期=2025-03-29` |
| `pdf_profile` | `§2 基金简介 / 2.1 基金基本情况` | `基金主代码=006597；基金名称=国泰利享中短债债券型证券投资基金；下属分级基金交易代码 A=006597，C=006598，E=014217，F=022176` |

## Intake Assessment Before Review

| Check | Result |
|---|---|
| Official locator/id present | PASS: `official_document_url` and `official_document_id=cninfo:1222957988` are present. |
| Fund code present | PASS: `006597` is present in user-provided profile anchor. |
| Report year present | PASS: `2024` is present in title and gate field. |
| Document kind annual report | PASS: `document_kind=annual_report` and title says `2024年年度报告`. |
| Publisher present | PASS: `国泰基金管理有限公司`. |
| Publication date present | PASS: `2025-03-29`. |
| Share class present | PASS: target class `A=006597`; other classes `C=006598`, `E=014217`, `F=022176`. |
| PDF SHA256 | DEFERRED: user did not provide PDF SHA256. This does not block manual identity intake because official locator/id is present, but it cannot prove PDF bytes. |
| Fallback used | PASS: no fallback used or invoked in this docs-only intake. |
| Source/PDF/network access | PASS: none performed. |
| Exact/numeric correctness | BLOCKED: no row-field exact/numeric assertions accepted. |
| Fixture projection | BLOCKED: no fixture change or projection in this gate. |

## Preliminary Row Decision

`006597 / 2024` is ready for independent review as a user-provided manual source identity candidate.

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

- This artifact does not externally verify CNINFO/EID metadata or PDF content.
- This artifact does not retain PDF bytes or extracted PDF text.
- This artifact does not create retained minimal field excerpts.
- EID document id remains unknown in user-provided metadata.
- PDF byte identity is not proved because no user-provided PDF SHA256 was supplied.
- Exact/numeric extractor correctness remains blocked until a later row-field gate accepts field-specific anchors and expected values.
- Existing small golden fixture rows remain unchanged in this gate.
