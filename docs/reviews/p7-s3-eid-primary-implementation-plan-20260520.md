# P7-S3 EID Primary Implementation Plan - 2026-05-20

## Verdict

Implement EID / 证监会资本市场统一信息披露平台 as the primary `AnnualReportSource` behind the P7-S2 source abstraction.

Production source order after P7-S3:

```text
EID primary -> Eastmoney/akshare fallback
```

`FundDocumentRepository.load_annual_report(...)` remains the only public annual-report read entry. Service/UI/Engine/CLI must not know EID, Eastmoney, akshare, URLs, report codes, or source priority.

## Inputs

- `docs/reviews/p7-s1-eid-source-research-spike-plan-20260520.md`
- `docs/reviews/p7-s2-document-repository-source-abstraction-plan-20260520.md`
- `docs/implementation-control-p4.md`
- `docs/design.md`
- current code after `eb39877`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/pdf/downloader.py`
- `tests/fund/documents/test_annual_report_sources.py`

## Problem Statement

P7-S2 created the internal source protocol and orchestrator, but production still defaults to Eastmoney/akshare. P7-S3 should add a deterministic EID source implementation and make it the default primary source while preserving Eastmoney/akshare as fallback.

The slice must solve only source acquisition:

- locate a fund on EID by fund code
- locate the requested annual report by fund code and year
- validate structured metadata fail-closed
- download the PDF
- verify PDF content type and magic bytes
- return `AnnualReportSourceResult` with EID metadata

It must not change parsing, extraction, audit, template rendering, score, quality gate, Service, UI, Engine, CLI, or cache schema unless a tiny compatibility-safe addition is strictly necessary.

## Owned Files

Allowed implementation files:

| File | Action |
|---|---|
| `fund_agent/fund/documents/sources.py` | Add EID source implementation, EID helpers, metadata field extensions, default source order |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | Only if constructor/default orchestration wiring needs a docstring or import adjustment |
| `fund_agent/fund/documents/repository.py` | Avoid changes; only private docstring/typing if necessary |
| `tests/fund/documents/test_annual_report_sources.py` | Add fake-network EID tests using `004393` fixture |
| `fund_agent/fund/README.md` | Update current source behavior after implementation |
| `tests/README.md` | Update source test description if needed |
| `docs/reviews/p7-s3-implementation-20260520.md` | Implementation artifact |

Do not modify control docs.

## Non-goals

P7-S3 does not:

- Add live EID network tests.
- Add Service/UI/Engine/CLI source awareness.
- Add or use `extra_payload`.
- Change `FundDocumentRepository.load_annual_report(...)` public signature.
- Change repository parsed report cache behavior.
- Persist source metadata in cache schema unless implementation proves it is strictly necessary.
- Change PDF parser, section locator, extractor, audit, renderer, score, or quality gate behavior.
- Implement Evidence Confirm, LLM audit, ITEM_RULE renderer/audit integration, or quality-gate source checks.
- Use 巨潮 as public-fund annual-report source.
- Rely on natural-language title matching without structured `reportCode/reportYear/fundCode` checks.

## EID Endpoint Contract

Base URL:

```text
http://eid.csrc.gov.cn/fund
```

Use a single `httpx.AsyncClient` session per EID source call so cookies from the platform can be preserved across metadata and PDF requests.

### 1. Fund Code Validation

Endpoint:

```text
POST /fund/disclose/validate_fund.do
form:
  cFundCode=<fund_code>
```

Fixture:

```text
cFundCode=004393
```

Expected mocked response:

```json
{"fundId":1618,"isSuccess":true}
```

Required parser behavior:

- Response must be JSON object.
- `isSuccess` must be `true`.
- `fundId` must be present and convertible to non-empty string.
- If `isSuccess` is false for a syntactically valid fund code, classify as `AnnualReportSourceNotFoundError`.
- Non-JSON, missing `isSuccess`, missing `fundId`, or invalid field types are `AnnualReportSourceSchemaError`.
- HTTP 5xx, timeout, connection errors, and rate-limit-like transient errors are `AnnualReportSourceUnavailableError`.

### 2. Annual Report Search

Endpoint:

```text
GET /fund/disclose/advanced_search_report.do
query:
  aoData=<json array encoded as one query parameter>
```

Required `aoData` encoding:

```json
[
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

Implementation detail:

- Build the array with `json.dumps(..., ensure_ascii=False, separators=(",", ":"))`.
- Pass it as a normal `params={"aoData": encoded}` value to `httpx`, not by manual string concatenation.
- `reportType` is always `FB010`.
- `reportYear` is the requested year converted to string.
- `fundCode` is the normalized 6-digit fund code.
- `iDisplayLength=20` is enough for exact fund/year query; if more candidates appear, filtering/tie-break rules below must decide.

Fixture response fields for `004393`, `2024`:

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

Required response parser:

- Response must be JSON object.
- If response has `success == false`, classify as `AnnualReportSourceUnavailableError` when it looks service-side/transient; otherwise `AnnualReportSourceSchemaError` unless a clear no-data signal is present.
- `aaData` must exist and be a list.
- Each candidate row must be parsed through a typed internal dataclass, e.g. `_EidAnnualReportCandidate`.
- Required row fields:
  - `fundCode`
  - `fundId`
  - `reportYear`
  - `reportDesp`
  - `reportCode`
  - `uploadInfoId`
  - `uploadInfoDetailId`
  - `tableName`
- Optional metadata row fields:
  - `reportName`
  - `reportSendDate`
  - `uploadDate`
  - `createTime`
  - `operationUploadType`
  - `correctionsNum`
  - `attachFileName`
  - `attachFilePath`
  - `organName`

## Annual Report Filters

Filtering must be deterministic and fail closed:

1. `fundCode == requested fund_code`
2. `str(reportYear) == str(requested year)`
3. `reportCode == "FB010010"` for P7-S3
4. `reportDesp == "年度报告"`
5. `tableName == "PDF"`
6. `uploadInfoId` is present and non-empty
7. `reportName` must not contain `摘要` when `reportName` is present
8. attachment path handling:
   - if `attachFileName` or `attachFilePath` is present and non-empty, P7-S3 should fail with `AnnualReportSourceSchemaError` or explicit unsupported-attachment error; do not guess `fund_attach_detail.html`

Final candidate selection:

- No candidates after filtering -> `AnnualReportSourceNotFoundError`.
- Exactly one candidate -> select it.
- More than one candidate -> fail closed with `AnnualReportSourceSchemaError` unless P7-S3 implements and tests a deterministic correction rule.
- Do not silently pick first row.
- Do not select quarterly (`FB030`), mid-year (`FB020`), liquidation (`FB060`), temporary (`FC*`), or title-only annual-looking rows.

Mismatch vs not-found:

- If `aaData` contains rows for the requested query but they contradict requested `fundCode`, `reportYear`, annual `reportCode`, or PDF `tableName`, classify as `AnnualReportSourceMismatchError` or `AnnualReportSourceSchemaError` and stop fallback.
- If `aaData` is empty for the exact valid query, classify as `AnnualReportSourceNotFoundError` and allow fallback.

## PDF Download

Endpoint:

```text
GET /fund/disclose/instance_show_pdf_id.do?instanceid=<uploadInfoId>
```

Fixture:

```text
GET /fund/disclose/instance_show_pdf_id.do?instanceid=1248088
```

Expected mocked response:

```text
HTTP 200
Content-Type: application/pdf
body starts with %PDF-
```

Validation rules:

- HTTP status must be 200.
- `Content-Type` must include `application/pdf` after lowercasing and ignoring parameters.
- Body must start with bytes `%PDF-`.
- Non-200/5xx/timeouts are `AnnualReportSourceUnavailableError`.
- 200 with HTML, JSON, empty body, non-PDF content-type, or missing `%PDF-` is `AnnualReportSourceSchemaError`.
- Do not rely on `Content-Disposition` filename decoding for identity.

PDF cache path:

- Use a deterministic filename under the existing raw PDF cache directory:

```text
cache/pdf/<fund_code>_<year>_annual_report_eid.pdf
```

- Reuse the existing `_download_pdf(...)` helper only if it can support content validation cleanly. If not, implement an EID-specific private `_download_eid_pdf(...)` in `sources.py`.
- If implementing `_download_eid_pdf(...)`, keep writes inside `cache/pdf`; create directories with `asyncio.to_thread`.
- `force_refresh=False` and file exists:
  - source may return the existing file without network PDF download after metadata lookup, but repository-level cache normally prevents source calls when PDF path is already cached.
- `force_refresh=True`:
  - EID source must re-fetch PDF and overwrite the deterministic cache file after validation.

## Timeout, Retry, Session, User-Agent

Use `AnnualReportSourceConfig` from P7-S2:

- `metadata_timeout_seconds`: for `validate_fund.do` and `advanced_search_report.do`
- `pdf_timeout_seconds`: for PDF download
- `retry_attempts`: transient retry count
- `max_concurrency`: keep as config boundary; do not add global async semaphore unless implementation needs it

HTTP client:

- Use `httpx.AsyncClient(follow_redirects=True, headers=...)` as the shared session holder.
- Use one client per `fetch_annual_report_pdf(...)` call so cookies (`acw_tc`, `tgw_l7_route`) can be retained across requests.
- Apply timeouts at request level, not only at client level:
  - `validate_fund.do` request passes `timeout=config.metadata_timeout_seconds`
  - `advanced_search_report.do` request passes `timeout=config.metadata_timeout_seconds`
  - `instance_show_pdf_id.do` PDF request passes `timeout=config.pdf_timeout_seconds`
- Do not rely on one `AsyncClient(timeout=...)` value for both metadata and PDF requests; that would erase the distinction between metadata and PDF timeout policy.
- Use a normal browser-like `User-Agent`, consistent with existing downloader style.
- Do not put source settings in CLI args, Service request objects, or `extra_payload`.

Retries:

- Retry transient `httpx.TimeoutException`, `httpx.TransportError`, and HTTP 5xx up to `retry_attempts`.
- Do not retry schema/mismatch/not-found errors.
- Keep backoff simple and bounded; if adding sleep, use tiny async sleep and make tests avoid real waiting by setting retry attempts to 1 or injecting a no-op sleep helper.
- If all retry attempts for a request fail transiently, raise `AnnualReportSourceUnavailableError`.

## Metadata Returned

Extend `AnnualReportSourceMetadata` minimally if needed to carry P7-S1 EID fields:

```text
source="eid"
source_url=<pdf url>
fund_code="004393"
fund_id="1618"
report_year=2024
report_code="FB010010"
report_desp="年度报告"
report_name=<optional>
upload_info_id="1248088"
upload_info_detail_id="1285356"
table_name="PDF"
report_send_date=<optional extension>
operation_upload_type=<optional extension>
corrections_num=<optional extension>
fallback_used=false
```

Rules:

- Metadata is returned in `AnnualReportSourceResult`.
- Metadata persistence in SQLite/parsed report is not required in P7-S3.
- If EID fails and Eastmoney succeeds, orchestrator must return Eastmoney metadata with `fallback_used=True`.
- Do not silently label fallback PDFs as EID.

## Default Source Order

Current P7-S2 default:

```text
AnnualReportSourceOrchestrator(None) -> Eastmoney only
```

P7-S3 target default:

```text
AnnualReportSourceOrchestrator(None) -> EidAnnualReportSource(), EastmoneyAnnualReportSource()
```

Keep explicit empty tuple behavior:

```python
AnnualReportSourceOrchestrator(())  # raises ValueError
```

Tests must update the default-source assertion accordingly.

## Cache And `force_refresh`

Repository behavior remains unchanged:

- `force_refresh=False`
  - parsed report cache hit stops before source.
  - cached PDF path hit stops before source and goes straight to parse.
  - source runs only if both parsed and PDF cache miss.
- `force_refresh=True`
  - repository skips parsed report and PDF path cache.
  - adapter calls orchestrator with `force_refresh=True`.
  - EID source must re-fetch metadata and PDF.

P7-S3 should not add source metadata persistence to the documents SQLite schema unless implementation proves it is necessary for correctness. Returning metadata through `AnnualReportSourceResult` is sufficient for this slice.

## File-Level Implementation Plan

### 1. Extend `sources.py` constants and metadata

Add constants:

```python
EID_BASE_URL = "http://eid.csrc.gov.cn/fund"
EID_VALIDATE_FUND_PATH = "/fund/disclose/validate_fund.do"
EID_ADVANCED_SEARCH_REPORT_PATH = "/fund/disclose/advanced_search_report.do"
EID_PDF_PATH = "/fund/disclose/instance_show_pdf_id.do"
EID_ANNUAL_REPORT_TYPE = "FB010"
EID_ANNUAL_REPORT_CODE = "FB010010"
EID_ANNUAL_REPORT_DESP = "年度报告"
PDF_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF-"
```

Extend `AnnualReportSourceMetadata` with optional fields only if needed:

- `report_send_date`
- `operation_upload_type`
- `corrections_num`

Keep field additions backward-compatible because dataclass defaults are optional.

### 2. Add typed EID helper dataclasses

Recommended private dataclasses:

```python
@dataclass(frozen=True, slots=True)
class _EidValidatedFund:
    fund_id: str

@dataclass(frozen=True, slots=True)
class _EidAnnualReportCandidate:
    fund_code: str
    fund_id: str
    report_year: int
    report_desp: str
    report_code: str
    upload_info_id: str
    upload_info_detail_id: str
    table_name: str
    report_name: str | None = None
    report_send_date: str | None = None
    operation_upload_type: str | None = None
    corrections_num: int | None = None
    attach_file_name: str | None = None
    attach_file_path: str | None = None
```

Add private parsing helpers with Chinese docstrings:

- `_parse_eid_validate_response(payload)`
- `_build_eid_ao_data(fund_code, year)`
- `_parse_eid_search_response(payload)`
- `_parse_eid_candidate(payload)`
- `_select_eid_annual_report_candidate(candidates, fund_code, year)`
- `_build_eid_pdf_url(base_url, upload_info_id)`
- `_validate_pdf_response(response)`

No nested functions.

### 3. Implement `EidAnnualReportSource`

Constructor:

```python
class EidAnnualReportSource:
    name: AnnualReportSourceName = "eid"

    def __init__(
        self,
        *,
        base_url: str = EID_BASE_URL,
        cache_dir: Path | None = None,
        config: AnnualReportSourceConfig | None = None,
        client_factory: Callable[..., httpx.AsyncClient] | None = None,
    ) -> None: ...
```

Notes:

- `client_factory` exists only for fake-network tests.
- If typing an async context manager factory is too noisy, accept a simple callable returning `httpx.AsyncClient`.
- Default cache directory should match existing `cache/pdf` behavior, using the constant from `fund_agent.fund.pdf.downloader` if reasonable.

`fetch_annual_report_pdf(...)` sequence:

1. create one `httpx.AsyncClient`
2. POST validate fund
3. GET advanced search report with `aoData`
4. select candidate
5. build PDF URL
6. if `force_refresh=False` and deterministic EID cache file exists, return it with metadata after metadata validation
7. GET PDF
8. validate content type and `%PDF-`
9. write bytes to deterministic file
10. return `AnnualReportSourceResult`

### 4. Update orchestrator default

Change default source tuple from:

```python
(EastmoneyAnnualReportSource(),)
```

to:

```python
(EidAnnualReportSource(config=config), EastmoneyAnnualReportSource())
```

Be careful with constructor order:

- `AnnualReportSourceOrchestrator(None, config=custom_config)` should pass the same config to `EidAnnualReportSource`.
- `AnnualReportSourceOrchestrator(())` must still raise `ValueError`.

### 5. Keep adapter/repository/cache/parser stable

No behavior changes required outside default source order.

Only update `annual_report_pdf.py` docstring if it still says current default source is Eastmoney-only.

## Fake-Network Test Plan

All tests use fake network. No live EID, Eastmoney, akshare, or real PDF download.

Use `httpx.MockTransport` or an injected fake async client/request helper. Prefer `httpx.MockTransport` for URL, method, params, body, headers, and cookie/session behavior. Use an injectable fake client/request helper where request-level timeout assertions are needed, because `MockTransport` alone may not expose the `timeout=` value passed to `client.get(...)` / `client.post(...)`.

Fixtures:

- fund code: `004393`
- year: `2024`
- validate response: `{"fundId":1618,"isSuccess":true}`
- search response row:
  - `fundCode="004393"`
  - `fundId=1618`
  - `reportYear="2024"`
  - `reportDesp="年度报告"`
  - `reportCode="FB010010"`
  - `uploadInfoId=1248088`
  - `uploadInfoDetailId=1285356`
  - `tableName="PDF"`
- PDF response:
  - status 200
  - `Content-Type: application/pdf`
  - body starts `%PDF-`

Required tests in `tests/fund/documents/test_annual_report_sources.py`:

1. `test_eid_source_fetches_004393_annual_report_with_validated_metadata`
   - validates `validate_fund.do`, `advanced_search_report.do`, and `instance_show_pdf_id.do` are called
   - asserts `aoData` contains `reportType=FB010`, `reportYear=2024`, `fundCode=004393`
   - asserts PDF file is written and metadata contains EID fields

2. `test_eid_source_validate_fund_false_is_not_found`
   - validate response `{"isSuccess":false}`
   - raises `AnnualReportSourceNotFoundError`

3. `test_eid_source_validate_schema_error_fails_closed`
   - missing `fundId` with `isSuccess=true`
   - raises `AnnualReportSourceSchemaError`

4. `test_eid_source_search_empty_is_not_found`
   - `aaData=[]`
   - raises `AnnualReportSourceNotFoundError`

5. `test_eid_source_rejects_wrong_year_candidate`
   - row `reportYear="2023"` for request `2024`
   - raises `AnnualReportSourceMismatchError` or `AnnualReportSourceSchemaError`
   - orchestrator should not fall back when tested through orchestrator

6. `test_eid_source_rejects_quarterly_candidate`
   - row `reportCode="FB030010"` / `reportDesp="第一季度报告"`
   - raises fail-closed mismatch/schema error

7. `test_eid_source_rejects_non_pdf_table_name`
   - `tableName="HTML"` or `XBRL`
   - raises fail-closed mismatch/schema error

8. `test_eid_source_rejects_abstract_title`
   - `reportName` contains `摘要`
   - raises fail-closed mismatch/schema error

9. `test_eid_source_rejects_duplicate_candidates`
   - two valid annual PDF candidates
   - raises `AnnualReportSourceSchemaError`

10. `test_eid_source_pdf_content_type_must_be_pdf`
    - response `text/html`
    - raises `AnnualReportSourceSchemaError`

11. `test_eid_source_pdf_magic_bytes_must_be_pdf`
    - `Content-Type: application/pdf`, body starts `<html`
    - raises `AnnualReportSourceSchemaError`

12. `test_eid_source_transient_http_error_is_unavailable`
    - metadata or PDF request returns 500 or raises timeout
    - raises `AnnualReportSourceUnavailableError`

13. `test_default_orchestrator_uses_eid_then_eastmoney`
    - `AnnualReportSourceOrchestrator(None)` now has EID first and Eastmoney second
    - `AnnualReportSourceOrchestrator(())` still raises `ValueError`

14. `test_orchestrator_falls_back_to_eastmoney_after_eid_not_found`
    - fake EID source not-found, fake Eastmoney success
    - metadata `fallback_used=True`

15. `test_orchestrator_does_not_fallback_after_eid_mismatch`
    - fake EID mismatch, fake Eastmoney success
    - mismatch raised and fallback not called

16. `test_eid_source_force_refresh_overwrites_cached_pdf`
    - precreate deterministic EID PDF path
    - `force_refresh=True` writes new bytes

17. `test_eid_source_without_force_refresh_reuses_existing_pdf_after_metadata_validation`
    - precreate deterministic EID PDF path
    - metadata endpoints called
    - PDF endpoint not called
    - returned path is existing PDF

18. `test_eid_source_uses_distinct_request_level_timeouts`
    - inject a fake async client/request helper that records each call's `timeout` argument
    - assert `validate_fund.do` uses `metadata_timeout_seconds`
    - assert `advanced_search_report.do` uses `metadata_timeout_seconds`
    - assert `instance_show_pdf_id.do` uses `pdf_timeout_seconds`
    - keep one logical client/session for all three calls so cookie-preserving behavior remains compatible with request-level timeout policy

Update existing P7-S2 tests for default source order. Keep fake tests isolated and deterministic.

## README Sync

P7-S3 changes current behavior in `fund_agent/fund/`, so update:

- `fund_agent/fund/README.md`
- `tests/README.md`

README should say current behavior after implementation:

- document repository remains the only public annual-report read entry
- documents layer internally uses EID primary and Eastmoney/akshare fallback
- Service/UI/Engine/CLI remain source-unaware
- tests use fake network and do not call live EID

Do not describe unimplemented cache metadata persistence or future Evidence Confirm behavior as current behavior.

## Acceptance Commands

Implementation should run:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_annual_report_sources.py -q
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

No command should require live EID.

## Risks

| Risk | Mitigation |
|---|---|
| EID schema drift | typed required-field parser, schema errors fail closed, fake tests pin fields |
| Official mismatch hidden by fallback | mismatch/schema errors stop fallback |
| EID temporary outage blocks otherwise available reports | unavailable/not-found categories allow orchestrator fallback only for eligible errors |
| PDF endpoint returns HTML challenge page | validate content type and `%PDF-` bytes |
| Cookie/routing behavior differs across requests | use one `httpx.AsyncClient` session per source call |
| Retry tests become slow | inject config with low retry attempts; avoid real sleep or use no-op sleep helper |
| Cache metadata overreach | do not persist source metadata in P7-S3 |
| Source leaks upward | keep implementation in `fund_agent/fund/documents`; no Service/UI/Engine/CLI imports |

## Rollback

Rollback should be narrow:

1. Remove or stop wiring `EidAnnualReportSource`.
2. Restore orchestrator default to `(EastmoneyAnnualReportSource(),)`.
3. Keep P7-S2 source abstraction intact.
4. No cache schema rollback should be needed because P7-S3 should not migrate cache metadata.

## Ready For Implementation

P7-S3 is ready for implementation after plan review acceptance. The implementation owner should stop at EID primary source acquisition and fake-network tests; source metadata persistence and Evidence Confirm integration remain later slices.
