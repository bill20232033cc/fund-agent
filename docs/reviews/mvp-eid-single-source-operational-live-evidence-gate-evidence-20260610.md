# EID Single Source Operational Live Evidence Gate - Evidence

## Verdict

`accepted_live_success`.

One controlled live EID acquisition succeeded through `FundDocumentRepository`.

## Scope

- Fund: `004393`
- Report year: `2024`
- Document kind: `annual_report`
- Source policy: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`
- Live command count: 1

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
await repository.load_annual_report("004393", 2024, force_refresh=True)
...
PY
```

The command used temporary cache directories and printed only safe scalar metadata, counts and hash values.

## Exit Code

`0`

## Safe Output Summary

```json
{
  "status": "accepted_live_success",
  "key": {
    "fund_code": "004393",
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
    "fund_code": "004393",
    "fund_id": "1618",
    "report_year": 2024,
    "report_code": "FB010010",
    "report_desp": "年度报告",
    "report_name": "安信企业价值优选混合型证券投资基金2024年年度报告",
    "report_send_date": "2025-03-28",
    "source_url": "http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248088",
    "upload_info_id": "1248088",
    "upload_info_detail_id": "1285356",
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
    "raw_text_chars": 66889,
    "sections": 8,
    "tables": 100
  },
  "pdf_integrity": {
    "exists": true,
    "magic": "%PDF-",
    "size_bytes": 841826,
    "sha256": "bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf"
  },
  "workspace_retention": "temporary cache directory only; no PDF content retained in artifact"
}
```

## Acceptance Matrix

| Check | Result | Evidence |
|---|---|---|
| FDR boundary | `PASS` | command called `FundDocumentRepository.load_annual_report("004393", 2024, force_refresh=True)` |
| EID-only source | `PASS` | `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` |
| No fallback | `PASS` | `fallback_used=false`, `primary_failure_category=null` |
| Identity | `PASS` | report key and metadata align to `004393 / 2024 / annual_report`; EID `fund_id=1618`; `upload_info_id=1248088` |
| Integrity | `PASS` | PDF exists, magic `%PDF-`, SHA256 `bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf` |
| Parser viability | `PASS` | `raw_text_chars=66889`, `sections=8`, `tables=100` |
| Cache policy | `PASS` | temporary forced acquisition has `pdf_cache_hit=false`, `parsed_cache_hit=false`, `source_metadata_present=true` |
| Safe retention | `PASS` | no PDF bytes, raw text or extracted report text retained in this artifact |

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

This gate proves one bounded live EID acquisition path for `004393 / 2024` through `FundDocumentRepository`.

It does not prove:

- all five small-golden rows;
- all EID failure branches in live conditions;
- extractor correctness;
- fixture projection;
- golden/readiness promotion;
- production report generation;
- provider / LLM behavior.
