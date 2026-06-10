# EID Single Source Operational Live Evidence Extension Gate - Evidence

## Verdict

`accepted_live_extension_completed`.

Four controlled live EID acquisitions succeeded through `FundDocumentRepository`. No fallback or non-EID source was invoked.

## Scope

| fund_code | report_year | document_kind | outcome |
|---|---:|---|---|
| `004194` | 2024 | `annual_report` | `accepted_live_success` |
| `006597` | 2024 | `annual_report` | `accepted_live_success` |
| `110020` | 2024 | `annual_report` | `accepted_live_success` |
| `017641` | 2024 | `annual_report` | `accepted_live_success` |

Source policy:

- `selected_source=eid`
- `mode=single_source_only`
- `fallback_enabled=false`

## Command

Command form:

```text
uv run python - <<'PY'
...
EidAnnualReportSource(cache_dir=<temporary pdf cache>, config=AnnualReportSourceConfig(...))
AnnualReportSourceOrchestrator((eid_source,))
AnnualReportPdfAdapter(source_orchestrator=orchestrator)
repository = FundDocumentRepository(adapter)
repository._cache = AnnualReportDocumentCache(<temporary document cache>)
await repository.load_annual_report(fund_code, 2024, force_refresh=True)
...
PY
```

The command used temporary cache directories and printed only safe scalar metadata, counts and hash values. It did not retain PDF bytes, raw text or full parsed report text in this artifact.

## Exit Code

`0`

## Safe Output Summary

### `004194 / 2024`

```json
{
  "status": "accepted_live_success",
  "key": {
    "fund_code": "004194",
    "year": 2024,
    "document_kind": "annual_report"
  },
  "source_metadata": {
    "source": "eid",
    "selected_source": "eid",
    "source_mode": "single_source_only",
    "fallback_enabled": false,
    "fallback_used": false,
    "primary_failure_category": null,
    "fund_code": "004194",
    "fund_id": "1488",
    "report_year": 2024,
    "report_code": "FB010010",
    "report_desp": "年度报告",
    "report_name": "招商中证1000指数增强型证券投资基金2024年年度报告",
    "report_send_date": "2025-03-28",
    "source_url": "http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248907",
    "upload_info_id": "1248907",
    "upload_info_detail_id": "1286201",
    "table_name": "PDF",
    "operation_upload_type": "9090-1010",
    "corrections_num": 0,
    "discovery_contract_version": "eid_annual_report_discovery.v1"
  },
  "cache": {
    "pdf_cache_hit": false,
    "parsed_cache_hit": false,
    "source_metadata_present": true,
    "cache_schema_version": 1
  },
  "parsed_counts": {
    "raw_text_chars": 83236,
    "sections": 8,
    "tables": 100
  },
  "pdf_integrity": {
    "magic": "%PDF-",
    "size_bytes": 852514,
    "sha256": "c5b8efd8a4d57265e5ce34ff4a7426a259da19401638f859467b2ee76bb9d976"
  }
}
```

### `006597 / 2024`

```json
{
  "status": "accepted_live_success",
  "key": {
    "fund_code": "006597",
    "year": 2024,
    "document_kind": "annual_report"
  },
  "source_metadata": {
    "source": "eid",
    "selected_source": "eid",
    "source_mode": "single_source_only",
    "fallback_enabled": false,
    "fallback_used": false,
    "primary_failure_category": null,
    "fund_code": "006597",
    "fund_id": "5755",
    "report_year": 2024,
    "report_code": "FB010010",
    "report_desp": "年度报告",
    "report_name": "国泰利享中短债债券型证券投资基金2024年年度报告",
    "report_send_date": "2025-03-29",
    "source_url": "http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1253099",
    "upload_info_id": "1253099",
    "upload_info_detail_id": "1290497",
    "table_name": "PDF",
    "operation_upload_type": "9090-1010",
    "corrections_num": 0,
    "discovery_contract_version": "eid_annual_report_discovery.v1"
  },
  "cache": {
    "pdf_cache_hit": false,
    "parsed_cache_hit": false,
    "source_metadata_present": true,
    "cache_schema_version": 1
  },
  "parsed_counts": {
    "raw_text_chars": 61510,
    "sections": 8,
    "tables": 85
  },
  "pdf_integrity": {
    "magic": "%PDF-",
    "size_bytes": 792928,
    "sha256": "85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982"
  }
}
```

### `110020 / 2024`

```json
{
  "status": "accepted_live_success",
  "key": {
    "fund_code": "110020",
    "year": 2024,
    "document_kind": "annual_report"
  },
  "source_metadata": {
    "source": "eid",
    "selected_source": "eid",
    "source_mode": "single_source_only",
    "fallback_enabled": false,
    "fallback_used": false,
    "primary_failure_category": null,
    "fund_code": "110020",
    "fund_id": "2855",
    "report_year": 2024,
    "report_code": "FB010010",
    "report_desp": "年度报告",
    "report_name": "易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告",
    "report_send_date": "2025-03-31",
    "source_url": "http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1249587",
    "upload_info_id": "1249587",
    "upload_info_detail_id": "1286903",
    "table_name": "PDF",
    "operation_upload_type": "9090-1010",
    "corrections_num": 0,
    "discovery_contract_version": "eid_annual_report_discovery.v1"
  },
  "cache": {
    "pdf_cache_hit": false,
    "parsed_cache_hit": false,
    "source_metadata_present": true,
    "cache_schema_version": 1
  },
  "parsed_counts": {
    "raw_text_chars": 85681,
    "sections": 8,
    "tables": 118
  },
  "pdf_integrity": {
    "magic": "%PDF-",
    "size_bytes": 2639303,
    "sha256": "307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790"
  }
}
```

### `017641 / 2024`

```json
{
  "status": "accepted_live_success",
  "key": {
    "fund_code": "017641",
    "year": 2024,
    "document_kind": "annual_report"
  },
  "source_metadata": {
    "source": "eid",
    "selected_source": "eid",
    "source_mode": "single_source_only",
    "fallback_enabled": false,
    "fallback_used": false,
    "primary_failure_category": null,
    "fund_code": "017641",
    "fund_id": "12471",
    "report_year": 2024,
    "report_code": "FB010010",
    "report_desp": "年度报告",
    "report_name": "摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告",
    "report_send_date": "2025-03-31",
    "source_url": "http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1256369",
    "upload_info_id": "1256369",
    "upload_info_detail_id": "1293857",
    "table_name": "PDF",
    "operation_upload_type": "9090-1010",
    "corrections_num": 0,
    "discovery_contract_version": "eid_annual_report_discovery.v1"
  },
  "cache": {
    "pdf_cache_hit": false,
    "parsed_cache_hit": false,
    "source_metadata_present": true,
    "cache_schema_version": 1
  },
  "parsed_counts": {
    "raw_text_chars": 97453,
    "sections": 6,
    "tables": 114
  },
  "pdf_integrity": {
    "magic": "%PDF-",
    "size_bytes": 2970819,
    "sha256": "33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c"
  }
}
```

## Acceptance Matrix

| Check | Result | Evidence |
|---|---|---|
| FDR boundary | `PASS` | command called `FundDocumentRepository.load_annual_report(fund_code, 2024, force_refresh=True)` for each fixed row |
| EID-only source | `PASS` | every success row has `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` |
| No fallback | `PASS` | every success row has `fallback_used=false`, `primary_failure_category=null`; no fallback source was constructed or invoked |
| Identity | `PASS` | every report key and metadata aligns to the attempted `fund_code / 2024 / annual_report` |
| Integrity | `PASS` | every PDF has magic `%PDF-` and a SHA256 hash |
| Parser viability | `PASS` | every row has non-empty text and parsed section/table counts |
| Cache policy | `PASS` | every forced acquisition has `pdf_cache_hit=false`, `parsed_cache_hit=false`, `source_metadata_present=true` |
| Safe retention | `PASS` | no PDF bytes, raw text or full parsed report text retained in this artifact |

## Blocked Row Classification

No row was blocked. No exception type, failure category, aggregate all-not-found ambiguity or schema-drift residual was produced.

## Post-Live Workspace Check

Commands:

```text
git status --short
git diff --check
git diff --name-only
```

Results:

- `git status --short`: unchanged unrelated untracked residue plus this gate's untracked review artifacts only.
- `git diff --check`: passed.
- `git diff --name-only`: empty; no tracked source/test/control diff was created by the live command.

## Forbidden Actions Check

Not performed:

- fallback invocation;
- Eastmoney / fund-company / CNINFO source use;
- extractor or `FundDataExtractor`;
- CLI `analyze` / `checklist`;
- Service / Host / UI / renderer / quality gate;
- provider / LLM / endpoint probe;
- fixture projection;
- golden/readiness promotion;
- source code, tests, config, runtime or budget changes;
- PR/push/merge/mark-ready.

## Controller Classification

This gate extends accepted live EID evidence to the remaining four small-golden rows.

It proves:

- all five small-golden rows now have a bounded live EID/FDR acquisition success when combined with prior accepted `004393 / 2024` proof;
- EID metadata, PDF integrity and parser viability for the four additional rows;
- no fallback was needed or used for these successful rows.

It does not prove:

- live EID failure branches;
- extractor correctness beyond already accepted no-live tests;
- fixture projection;
- golden/readiness promotion;
- production report generation;
- provider / LLM behavior.
