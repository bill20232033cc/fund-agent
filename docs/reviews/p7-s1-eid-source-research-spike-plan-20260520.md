# P7-S1 EID Source Research Spike Plan - 2026-05-20

## Verdict

EID / 证监会资本市场统一信息披露平台可以作为 P7 公募基金年报主源的第一候选。

推荐进入下一 gate：

```text
P7-S2 document repository source abstraction plan/review
```

P7-S2/P7-S3 的实现边界应保持在 Fund Capability 内部：所有上层读取仍只通过 `FundDocumentRepository.load_annual_report(...)`，EID 作为 primary source，Eastmoney/akshare 作为 fallback，巨潮不作为公募基金年报主源。

## Inputs

- `docs/design.md`
- `docs/implementation-control-p4.md`
- `docs/reviews/annual-report-source-strategy-reconciliation-20260520.md`
- `docs/reviews/post-p6-follow-up-planning-20260520.md`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/pdf/downloader.py`
- EID public endpoints checked on 2026-05-20.

## Problem Statement

Current annual report download is behind the right repository boundary, but the concrete source is still Eastmoney/akshare:

- `FundDocumentRepository.load_annual_report(...)` is the only public document loading entry.
- `AnnualReportPdfAdapter` delegates download to `fund_agent.fund.pdf.downloader._download_annual_report_pdf`.
- `_download_annual_report_pdf` calls `akshare.fund_announcement_report_em(symbol=fund_code)`, selects a title containing `年度报告` and not `摘要`, then downloads from `https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf`.

This is acceptable as a fallback, but not ideal as the primary source for evidence audit. P7 should move the primary annual report acquisition path to the official EID public disclosure platform while preserving the current repository boundary.

## Official Entry Check

### Browser Entry

Checked:

```text
http://eid.csrc.gov.cn/fund
http://eid.csrc.gov.cn/fund/disclose/index.html
```

Observed facts:

- `/fund` returns HTTP 200 with a short HTML entry.
- `/fund/disclose/index.html` returns HTTP 200 and page title `公募基金-资本市场统一信息披露平台`.
- The page contains navigation for `公募基金` / `公告信息` / `主体信息` and uses `/fund/js_new/index.js?ver=0.3`.
- The footer identifies the organizer and owner as 中国证券监督管理委员会.

### Index Public Data

Checked:

```text
GET http://eid.csrc.gov.cn/fund/disclose/indexPublicData.json
```

Observed response groups include:

- `yearReportList`
- `seasonReportList`
- `qSReportList`
- `fAReportList`
- `noticeReportList`
- `isShowPdfYear`
- `isShowPdfSeason`

Sample annual report item:

```json
{
  "fundcode": "012854",
  "fundidStr": "10652",
  "fundshortName": "英大中证ESG120策略指数",
  "idStr": "1462687",
  "newString": "英大中证ESG120策略指数证券投资基金2025年年度报告",
  "operationUploadType": "9090-1010",
  "reportCode": "FB010010",
  "reportSendDate": "2026-03-31",
  "reportTypereportDesp": "年度报告",
  "reportYear": "2025",
  "tableName": "PDF",
  "uploadInfoDetailId": "1510462",
  "correctionsNum": 0
}
```

This endpoint is useful for homepage sanity checks but should not be the primary lookup path because it only returns recent homepage subsets, not a bounded query by fund code/year.

## Query Flow

### Fund Code To Fund ID

Checked:

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
form: cFundCode=012854
```

Observed response:

```json
{"fundId":10652,"isSuccess":true}
```

Required P7-S1 selected-fund sample:

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
form: cFundCode=004393
```

Observed response:

```json
{"fundId":1618,"isSuccess":true}
```

Observed JS path in `/fund/js_new/index.js?ver=0.3`:

```text
$.post("/fund/disclose/validate_fund.do", {"cFundCode": value}, ...)
location.href = "/fund/disclose/fund_detail_search.do?cFundCode=" + data.fundId
```

Implementation implication:

- `cFundCode` is the explicit request field.
- `fundId` is the platform-specific fund identity.
- If `isSuccess != true`, fail closed for EID and let fallback policy decide whether Eastmoney/akshare can be tried.
- Do not infer `fundId` from page URLs without validation.

### Fund Detail Pages

Checked:

```text
GET http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=10652
GET http://eid.csrc.gov.cn/fund/disclose/fund_detail.do?fundId=10652
```

Observed facts:

- Both return a fund detail HTML page for `英大中证ESG120策略指数(012854)`.
- The detail page includes grouped sections:
  - `季度报告`, link `advanced_search.html?queryType=1&reportType=FB030&fundCode=012854`
  - `中期/年度报告`, link `advanced_search.html?queryType=1&reportType=FB010&fundCode=012854`
  - `临时公告`
- Annual report rows contain `instance_show_pdf_id.do?instanceid=...` links, e.g. `instanceid=1462687` for the 2025 annual report.

Implementation implication:

- Detail HTML can be used as a secondary cross-check or diagnostic source.
- The deterministic implementation should prefer the JSON-backed advanced-search endpoint because it exposes structured `reportCode`, `reportYear`, `uploadInfoId`, `uploadInfoDetailId`, `tableName`, and correction fields.

### Report Type Metadata

Checked:

```text
POST http://eid.csrc.gov.cn/fund/disclose/upload_inforeport_query.do
```

Observed useful metadata:

```json
{
  "reportTypeList": [
    {"FB": "【基金运作信息披露】"},
    {"FB010": "&nbsp&nbsp【年度报告】"},
    {"FB010010": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp年度报告"},
    {"FB020": "&nbsp&nbsp【中期报告】"},
    {"FB020010": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp中期报告"},
    {"FB030": "&nbsp&nbsp【季度报告】"},
    {"FB030010": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp第一季度报告"},
    {"FB030020": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp第二季度报告"},
    {"FB030030": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp第三季度报告"},
    {"FB030040": "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp第四季度报告"},
    {"FB060": "&nbsp&nbsp【清算报告】"},
    {"FC": "【基金临时信息披露】"}
  ],
  "yearList": ["2026", "2025", "2024", "...", "1997"]
}
```

Implementation implication:

- Annual report classification should use `reportType=FB010` plus row-level `reportCode=FB010010` and `reportDesp=年度报告`.
- Mid-year reports are `FB020`, quarterly reports are `FB030`, liquidation reports are `FB060`, temporary announcements are `FC*`.
- Do not select annual reports by title substring alone.

### Advanced Report Search

Page JS:

```text
GET /fund/disclose/advanced_search.html?queryType=1&reportType=FB010&fundCode=012854
loads /fund/disclose/report_query.html
loads /fund/js/report_query.js?ver=1.1
DataTables source: ../disclose/advanced_search_report.do
```

Checked request:

```text
GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do
query:
  aoData=[
    {"name":"iDisplayStart","value":0},
    {"name":"iDisplayLength","value":20},
    {"name":"fundType","value":""},
    {"name":"reportType","value":"FB010"},
    {"name":"reportYear","value":"2025"},
    {"name":"fundCompanyShortName","value":""},
    {"name":"fundCode","value":"012854"},
    {"name":"fundShortName","value":""},
    {"name":"startUploadDate","value":""},
    {"name":"endUploadDate","value":""}
  ]
```

Observed annual response:

```json
{
  "iTotalRecords": 1,
  "iTotalDisplayRecords": 1,
  "sEcho": 1,
  "aaData": [
    {
      "reportName": "英大中证ESG120策略指数证券投资基金2025年年度报告",
      "reportYear": "2025",
      "reportDesp": "年度报告",
      "reportCode": "FB010010",
      "createTime": "2026年03月31日",
      "uploadDate": "2026-03-31",
      "reportSendDate": "2026-03-31",
      "uploadInfoId": 1462687,
      "uploadInfoDetailId": 1510462,
      "fundId": 10652,
      "fundCode": "012854",
      "fundShortName": "英大中证ESG120策略指数",
      "fundSign": "9010-1020",
      "tableName": "PDF",
      "operationUploadType": "9090-1010",
      "organName": "英大",
      "correctionsNum": 0,
      "attachFileName": "",
      "isShowInfo": "1"
    }
  ]
}
```

Required P7-S1 selected-fund sample:

```text
GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do
query:
  aoData=[
    {"name":"iDisplayStart","value":0},
    {"name":"iDisplayLength","value":20},
    {"name":"fundType","value":""},
    {"name":"reportType","value":"FB010"},
    {"name":"reportYear","value":"2024"},
    {"name":"fundCompanyShortName","value":""},
    {"name":"fundCode","value":"004393"},
    {"name":"fundShortName","value":""},
    {"name":"startUploadDate","value":""},
    {"name":"endUploadDate","value":""}
  ]
```

Observed selected-fund annual response fields:

```json
{
  "iTotalRecords": 1,
  "aaData": [
    {
      "fundCode": "004393",
      "fundId": 1618,
      "reportYear": "2024",
      "reportDesp": "年度报告",
      "reportCode": "FB010010",
      "uploadInfoId": 1248088,
      "uploadInfoDetailId": 1285356,
      "tableName": "PDF"
    }
  ]
}
```

This is the concrete P7-S2/P7-S3 mocked fixture target: `004393` + `2024` resolves through EID to `fundId=1618`, annual report `uploadInfoId=1248088`, `uploadInfoDetailId=1285356`, `tableName=PDF`, `reportDesp=年度报告`.

Checked quarterly contrast:

```text
reportType=FB030
reportYear=2026
fundCode=012854
```

Observed quarterly response:

```json
{
  "aaData": [
    {
      "reportName": "英大中证ESG120策略指数证券投资基金2026年第1季度报告",
      "reportYear": "2026",
      "reportDesp": "第一季度报告",
      "reportCode": "FB030010",
      "uploadInfoId": 1481089,
      "uploadInfoDetailId": 1529866,
      "fundId": 10652,
      "fundCode": "012854",
      "tableName": "PDF"
    }
  ]
}
```

Implementation implication:

- The P7-S3 source locator should query `advanced_search_report.do` with explicit `fundCode`, `reportType=FB010`, and `reportYear=<requested year>`.
- The response parser should require exactly one selected annual report after filtering, or apply deterministic tie-breaks only for correction semantics.
- It must validate:
  - `fundCode == requested fund_code`
  - `str(reportYear) == str(requested year)`
  - `reportCode == "FB010010"` or at minimum starts with `FB010` and `reportDesp == "年度报告"`
  - `tableName == "PDF"` for the current PDF pipeline
  - `uploadInfoId` / `instanceid` is present
  - `reportName` does not contain `摘要`

### PDF Link

Checked:

```text
HEAD http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1462687
```

Observed response:

```text
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: inline;filename=...
Set-Cookie: acw_tc=...
Set-Cookie: tgw_l7_route=...
```

Required P7-S1 selected-fund PDF sample:

```text
HEAD http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248088
```

Observed response:

```text
HTTP/1.1 200 OK
Content-Type: application/pdf
```

Observed JS link construction:

```text
../disclose/instance_show_pdf_id.do?instanceid=<uploadInfoId>
../disclose/instance_show_pdf_id.do?instanceid=<uploadInfoId>&uploadInfoDetailId=<uploadInfoDetailId>
../disclose/fund_attach_detail.html?... only when attachFileName and attachFilePath are present
```

Implementation implication:

- For normal PDF rows with empty attachment fields, construct:

```text
http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=<uploadInfoId>
```

- Preserve `uploadInfoDetailId` in metadata and include it in the URL only when needed for corrected rows or attachment detail handling.
- Verify downloaded content with response `Content-Type` and first bytes `%PDF-`.

## Available Metadata

The following fields are available and should be captured in source metadata:

| Field | Source | Use |
|---|---|---|
| `fundId` / `fundidStr` | validate/detail/list | EID platform fund identity |
| `fundCode` / `fundcode` | list | requested fund code validation |
| `fundShortName` / `fundshortName` | list | diagnostics only |
| `reportName` / `newString` | list | diagnostics and title sanity |
| `reportYear` | list | fail-closed year validation |
| `reportCode` | list | annual vs quarterly vs temporary classification |
| `reportDesp` / `reportTypereportDesp` | list | human-readable report type validation |
| `reportSendDate` | list | source metadata and sorting |
| `uploadDate` / `createTime` | advanced list | diagnostics and correction sorting |
| `uploadInfoId` / `idStr` | advanced/index list | `instanceid` for PDF link |
| `uploadInfoDetailId` | list | correction/attachment metadata |
| `tableName` | list | PDF vs XBRL/html path selection |
| `operationUploadType` | list | correction semantics |
| `correctionsNum` | list | correction semantics |
| `attachFileName` / `attachFilePath` | list | attachment-detail alternative path |
| `organName` | advanced list | diagnostics |

P7-S3 should persist enough of this metadata with the cached PDF or parsed report to make later Evidence Confirm and source debugging possible. Minimum recommended fields:

```text
source=eid
source_url
fund_code
fund_id
report_year
report_code
report_desp
report_name
report_send_date
upload_info_id
upload_info_detail_id
table_name
operation_upload_type
corrections_num
fallback_used=false
```

## Fail-Closed Rules

P7-S3 must fail closed for EID primary lookup when:

- `validate_fund.do` returns non-JSON, `isSuccess != true`, or missing `fundId`.
- `advanced_search_report.do` returns non-JSON, `success == false`, or missing `aaData`.
- No candidate remains after deterministic annual-report filters.
- More than one non-correction candidate remains for the same `fundCode/reportYear/reportCode`.
- Candidate `reportYear` differs from requested year.
- Candidate `fundCode` differs from requested fund code.
- Candidate `reportCode` is not annual report (`FB010010` or accepted `FB010*` annual code).
- Candidate `reportDesp` is not `年度报告`.
- Candidate `reportName` contains `摘要`.
- Candidate `tableName` is not `PDF` and no current PDF path can be resolved.
- PDF endpoint does not return HTTP 200.
- Response content is not a PDF by header and magic-byte validation.

Fallback policy:

- EID not-found or fail-closed source mismatch may fall back to Eastmoney/akshare only if the error is classified as source-unavailable / no-official-hit, not if EID returns a contradictory official candidate for a different year or fund code.
- Fallback must be explicit in metadata. It must never silently cache a fallback PDF as if it came from EID.

## Timeout, Retry, Rate Limit, Schema Drift

Recommended P7-S2/P7-S3 source behavior:

- Per-request timeout: bounded and explicit, e.g. 10 seconds for metadata endpoints and 60 seconds for PDF download.
- Retries: small fixed count, e.g. 2 attempts for transient network/5xx/timeouts; no infinite retry.
- Backoff: short exponential or fixed backoff with jitter inside the source adapter.
- Rate limit: serialize or bound concurrent EID requests in repository/source adapter; default conservative concurrency is 1-2 for EID.
- Headers: send a normal `User-Agent`; preserve redirects and cookies within one `httpx.AsyncClient` session.
- Schema drift: parse only required fields through a typed internal model; missing required fields raise a source schema error and fail closed.
- Encoding: do not depend on `Content-Disposition` filename decoding for correctness; use metadata and configured filename.
- Observability: log source, fund code, year, endpoint, status code, selected `uploadInfoId`, and fallback reason without logging full PDF bytes.

## P7-S2 Implementation Boundary

P7-S2 should introduce the internal source abstraction, not full EID implementation.

Recommended scope:

- Add an internal `AnnualReportSource` protocol under `fund_agent/fund/documents` or `fund_agent/fund/documents/adapters`.
- Keep `FundDocumentRepository.load_annual_report(fund_code, year, *, force_refresh=False)` unchanged.
- Keep Service, Engine, UI, CLI unchanged.
- Let `AnnualReportPdfAdapter.fetch_pdf_path(...)` delegate to a source orchestrator rather than directly to `_download_annual_report_pdf`.
- Source order should be explicit in adapter configuration: EID primary, Eastmoney/akshare fallback.
- Introduce internal source metadata models if needed, but do not put explicit source parameters into `extra_payload`.
- Existing `fund_agent/fund/pdf/downloader.py` can remain as Eastmoney/akshare fallback implementation until P7-S3 replaces or wraps it.

Acceptance signal:

- Unit tests prove source priority, fallback order, timeout propagation, year fail-closed behavior, and unchanged repository public signature using fake sources only.
- No upper-layer imports of EID or source-specific classes.

## P7-S3 Implementation Boundary

P7-S3 should implement EID primary source behind the P7-S2 abstraction.

Recommended scope:

- Implement EID metadata client:
  - `validate_fund.do`
  - `advanced_search_report.do`
  - PDF URL construction via `instance_show_pdf_id.do`
- Implement deterministic annual-report candidate filtering.
- Implement PDF download through the same cache path used by repository parsing.
- Preserve Eastmoney/akshare fallback.
- Do not add document filesystem reads outside the repository path.
- Do not add Service/UI/Engine/CLI behavior changes.
- Do not use real EID in tests.

Acceptance signal:

- With mocked EID metadata and PDF responses, EID hit wins.
- EID miss or transient error falls back to Eastmoney/akshare and records fallback metadata.
- EID wrong-year/wrong-fund/wrong-report-type candidate fails closed.
- PDF bytes are validated before cache record.
- `FundDocumentRepository.load_annual_report(...)` remains the only public read path.

## Test Strategy

All P7-S2/P7-S3 tests must mock network. They must not depend on live EID availability.

Recommended focused tests:

- `validate_fund.do` success maps `fund_code -> fundId`.
- `validate_fund.do` failure raises EID not-found / fallback-eligible error.
- `advanced_search_report.do` annual item is parsed into a source candidate.
- quarterly `FB030` item is rejected for annual-report lookup.
- `reportYear` mismatch is rejected and does not silently use a different year.
- `fundCode` mismatch is rejected.
- title containing `摘要` is rejected.
- duplicate candidates fail closed unless correction selection rules are explicitly implemented and tested.
- PDF endpoint must return `application/pdf` and `%PDF-` bytes.
- EID timeout/5xx retries are bounded.
- source orchestrator uses EID before Eastmoney/akshare.
- fallback metadata is preserved.
- repository callers still use `FundDocumentRepository` and fake loaders; no real PDF/network in unit tests.

## Non-goals

P7-S1/P7-S2/P7-S3 should not:

- Parse fund reports directly from arbitrary filesystem paths.
- Let Service/UI/Engine/CLI import or know EID, Eastmoney, akshare, or URL details.
- Put explicit parameters into `extra_payload`.
- Use real EID network in automated tests.
- Introduce LLM audit, Evidence Confirm, CHAPTER_CONTRACT changes, ITEM_RULE renderer/audit integration, or quality gate behavior changes.
- Make 巨潮 a public-fund annual-report primary source.
- Trust title substring matching without structured `reportCode/reportYear/fundCode` checks.

## Risks And Owners

| Risk | Owner | Mitigation |
|---|---|---|
| EID endpoint schema drift | Capability / documents | Typed parser, required-field validation, fail closed, fallback only when safe |
| EID anti-bot/rate limiting/cookies | Capability / documents | Bounded concurrency, normal User-Agent, session cookies, conservative retries |
| Wrong-year caching | Capability / documents | Validate `reportYear` before download and before cache record |
| Corrected reports ambiguity | Capability / documents | Fail closed until deterministic correction-selection rules are implemented |
| Attachment-detail path | Capability / documents | Treat as unsupported or separate tested path; do not assume normal PDF path |
| PDF filename encoding | Capability / documents | Ignore filename for identity; use explicit cache filename and metadata |
| Current design doc still says 巨潮 | Future design/docs update | Update only when implementation changes source behavior |
| Fallback masking official mismatch | Capability / documents | Differentiate unavailable/not-found from contradictory official metadata |

## Rollback

P7-S2 rollback should be simple because the public repository API remains unchanged:

- Restore `AnnualReportPdfAdapter` to direct `_download_annual_report_pdf` delegation.
- Keep existing Eastmoney/akshare helper as fallback-compatible code.
- Remove or disable EID source orchestrator behind adapter configuration.

P7-S3 rollback should disable EID primary and keep Eastmoney/akshare fallback active, without touching Service/UI/Engine/CLI.

## Recommended Next Gate

Proceed to:

```text
P7-S2 document repository source abstraction plan/review
```

P7-S2 should be code-generation-ready and focus on source adapter boundaries, metadata model, fallback semantics, and mocked tests. P7-S3 should then implement the EID client using the verified endpoint chain.
