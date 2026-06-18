# Manual Evidence Intake: 017641 2024 Annual Report Source Identity

## Gate Metadata

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Scope: docs-only evidence intake.
- Fund code: `017641`.
- Report year: `2024`.
- Document kind: `annual_report`.
- Evidence provider: `user_provided`.
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-017641-20260609-source-payload.json`.
- Source payload SHA256: `853cf6b2f5c388897d76e08015527b91c9c8d4c08e58a1d79ab935c5823007d0`.

## Boundary Statement

This artifact only records user-provided official locator/id/metadata/checksum. It does not verify the URLs, open the URLs, read a PDF, hash a PDF, call `FundDocumentRepository`, use fallback, use akshare/EID tooling, run network commands, or run live LLM/provider probes.

No PDF SHA256 was provided for this row. The `user_provided_pdf_sha256` field is therefore recorded as `not_provided`.

## User-Provided Source Identity Fields

| Field | Recorded value |
|---|---|
| `fund_code` | `017641` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `official_search_url` | `http://eid.csrc.gov.cn/fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=017641` |
| `official_fund_detail_url` | `unknown` |
| `official_document_url` | `https://www.cifm.com/fund/017641/announce/202503/W020250331321243719367.pdf` |
| `official_document_id` | `cifm:W020250331321243719367` |
| `official_announcement_id` | `unknown` |
| `source_document_title` | `摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告` |
| `source_publisher` | `摩根基金管理（中国）有限公司` |
| `source_registry` | `摩根基金官网 / CIFM；EID search locator provided, EID document id unknown` |
| `publication_date` | `2025-03-31` |
| `fund_name` | `摩根标普500指数型发起式证券投资基金(QDII)` |
| `share_class.target` | `人民币A` |
| `share_class.target_code` | `017641` |
| `share_class.other_classes` | `人民币C=019305` |
| `user_provided_pdf_sha256` | `not_provided` |

## User-Provided Identity Anchors

| Anchor | User-provided source | User-provided evidence |
|---|---|---|
| `registry_metadata` | `摩根基金官网 PDF / announcement path` | `公告标题=摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告；公告路径日期=202503` |
| `pdf_title_page` | `official PDF title page` | `标题=摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告；基金管理人=摩根基金管理（中国）有限公司` |
| `pdf_profile` | `§2 基金简介 / 2.1 基金基本情况` | `基金主代码=017641；基金名称=摩根标普500指数型发起式证券投资基金(QDII)；下属分级基金交易代码 人民币A=017641，人民币C=019305` |

## Intake Assessment Before Review

| Check | Result |
|---|---|
| Official locator/id present | PASS: `official_document_url` and `official_document_id=cifm:W020250331321243719367` are present. |
| Fund code present | PASS: `017641` is present in user-provided profile anchor. |
| Report year present | PASS: `2024` is present in title and gate field. |
| Document kind annual report | PASS: `document_kind=annual_report` and title says `2024年年度报告`. |
| Publisher present | PASS: `摩根基金管理（中国）有限公司`. |
| Publication date present | PASS: `2025-03-31`. |
| Share class present | PASS: target class `人民币A=017641`, other class `人民币C=019305`. |
| PDF SHA256 | DEFERRED: user did not provide PDF SHA256. This does not block manual identity intake because official locator/id is present, but it cannot prove PDF bytes. |
| Fallback used | PASS: no fallback used or invoked in this docs-only intake. |
| Source/PDF/network access | PASS: none performed. |
| Exact/numeric correctness | BLOCKED: no row-field exact/numeric assertions accepted. |
| Fixture projection | BLOCKED: no fixture change or projection in this gate. |

## Preliminary Row Decision

`017641 / 2024` is ready for independent review as a user-provided manual source identity candidate.

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

- This artifact does not externally verify EID/CIFM metadata or PDF content.
- This artifact does not retain PDF bytes or extracted PDF text.
- This artifact does not create retained minimal field excerpts.
- EID document id remains unknown in user-provided metadata.
- QDII row remains not promotion-ready; this evidence does not change golden/readiness or promotion state.
- PDF byte identity is not proved because no user-provided PDF SHA256 was supplied.
- Exact/numeric extractor correctness remains blocked until a later row-field gate accepts field-specific anchors and expected values.
- Existing small golden fixture rows remain unchanged in this gate.
