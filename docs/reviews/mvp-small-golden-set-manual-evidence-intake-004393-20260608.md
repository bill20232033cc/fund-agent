# Manual Evidence Intake: 004393 2024 Annual Report Source Identity

## Gate Metadata

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Scope: docs-only evidence intake.
- Fund code: `004393`.
- Report year: `2024`.
- Document kind: `annual_report`.
- Evidence provider: `user_provided`.
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-20260608-source-payload.json`.
- Source payload SHA256: `3926f237f48cfae0e59b92769039c655e0ba09692d7fb3535288a365e7d8c4d3`.

## Boundary Statement

This artifact only records user-provided official locator/id/metadata/checksum. It does not verify the URLs, open the URLs, read a PDF, hash a PDF, call `FundDocumentRepository`, use fallback, use akshare/EID tooling, run network commands, or run live LLM/provider probes.

The user-provided PDF SHA256 below is recorded as user-provided metadata. It was not computed by this agent.

## User-Provided Source Identity Fields

| Field | Recorded value |
|---|---|
| `fund_code` | `004393` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `official_search_url` | `http://eid.csrc.gov.cn/fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=004393` |
| `official_fund_detail_url` | `http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=1618&rnd=0.602227203698933` |
| `official_document_url` | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248088` |
| `official_document_id` | `instanceid=1248088` |
| `official_announcement_id` | `unknown` |
| `source_document_title` | `安信企业价值优选混合型证券投资基金2024年年度报告` |
| `source_publisher` | `安信基金管理有限责任公司` |
| `source_registry` | `中国证监会基金电子披露网站 / EID` |
| `publication_date` | `2025-03-28` |
| `fund_name` | `安信企业价值优选混合型证券投资基金` |
| `share_class.target` | `A` |
| `share_class.target_code` | `004393` |
| `share_class.other_classes` | `C=020964` |
| `user_provided_pdf_sha256` | `bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf` |

## User-Provided Identity Anchors

| Anchor | User-provided source | User-provided evidence |
|---|---|---|
| `registry_metadata` | `EID search/detail page` | `fundCode=004393；reportType=FB010；公告标题=安信企业价值优选混合型证券投资基金2024年年度报告；披露日期=2025-03-28；document instanceid=1248088` |
| `pdf_title_page` | `official PDF title page` | `标题=安信企业价值优选混合型证券投资基金2024年年度报告；基金管理人=安信基金管理有限责任公司；报告送出日期=2025-03-28` |
| `pdf_profile` | `§2 基金简介 / 基金产品概况` | `基金主代码=004393；下属分级基金交易代码 A=004393；C=020964` |

## Intake Assessment Before Review

| Check | Result |
|---|---|
| Official locator/id present | PASS: `official_document_url` and `official_document_id=instanceid=1248088` are present. |
| Fund code present | PASS: `004393` is present in user-provided registry metadata and profile anchor. |
| Report year present | PASS: `2024` is present in title and gate field. |
| Document kind annual report | PASS: `document_kind=annual_report` and title says `2024年年度报告`. |
| Publisher present | PASS: `安信基金管理有限责任公司`. |
| Publication date present | PASS: `2025-03-28`. |
| Share class present | PASS: target class `A=004393`, other class `C=020964`. |
| Fallback used | PASS: no fallback used or invoked in this docs-only intake. |
| Source/PDF/network access | PASS: none performed. |
| Exact/numeric correctness | BLOCKED: no row-field exact/numeric assertions accepted. |
| Fixture projection | BLOCKED: no fixture change or projection in this gate. |

## Preliminary Row Decision

`004393 / 2024` is ready for independent review as a user-provided manual source identity candidate.

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
- Exact/numeric extractor correctness remains blocked until a later row-field gate accepts field-specific anchors and expected values.
- Existing small golden fixture rows remain unchanged in this gate.
