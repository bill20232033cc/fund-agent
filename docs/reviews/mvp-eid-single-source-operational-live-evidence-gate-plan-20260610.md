# EID Single Source Operational Live Evidence Gate - Plan

## Gate

- Gate: `EID Single Source Operational Live Evidence Gate`
- Classification: `heavy`
- User authorization: option `1` after accepted no-live implementation checkpoint `0b9fe0b`
- Objective: verify that the current EID single-source production path can perform one controlled live acquisition through `FundDocumentRepository` without fallback or upper-layer bypass.

## Current Truth

- EID single-source no-live implementation is current code fact.
- Current source policy is `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney, fund-company official website/CDN and CNINFO are deferred candidates only.
- Production annual-report access must go through `FundDocumentRepository`.
- UI, Service, Host, renderer and quality gate must not call source/downloader/cache helpers directly.

## Live Authorization Boundary

Authorized only for this gate:

- EID network access needed by the default EID source.
- PDF download needed by EID source integrity validation.
- `FundDocumentRepository().load_annual_report()` live acquisition for the selected row.

Still forbidden:

- fallback invocation;
- Eastmoney / fund-company / CNINFO source use;
- provider / LLM / endpoint probe;
- extractor correctness work;
- fixture projection;
- golden/readiness promotion;
- source code, tests, provider/default/runtime/budget/config changes;
- PR/push/merge/mark-ready.

## Selected Live Row

Primary row:

- `fund_code=004393`
- `report_year=2024`
- `document_kind=annual_report`

Reason:

- This row has accepted docs-only EID manual evidence and a known EID source identity record.
- It is sufficient for a first live path smoke and avoids expanding into all five small-golden rows.

Optional fallback row for diagnostic only:

- none.

If `004393/2024` fails with `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, or `integrity_error`, record the exact failure category and stop. Do not try another source or another row without a new controller decision.

## Command Shape

The live command must:

- instantiate `EidAnnualReportSource` with a temporary PDF cache directory;
- instantiate `AnnualReportSourceOrchestrator` with exactly that one EID source;
- instantiate `AnnualReportPdfAdapter` with that orchestrator;
- instantiate `FundDocumentRepository` with that adapter;
- monkeypatch repository document cache creation to use a temporary document cache directory;
- call `repository.load_annual_report("004393", 2024, force_refresh=True)`;
- print only safe scalar metadata and counts.

The command must not:

- call `FundDataExtractor`;
- call `analyze`, `checklist`, renderer, Service, Host or UI;
- call `AnnualReportSourceOrchestrator` with more than one source;
- instantiate or import `EastmoneyAnnualReportSource`;
- persist PDF contents in review artifacts.

## Acceptance Matrix

| Check | Accepted evidence |
|---|---|
| FDR boundary | live command calls `FundDocumentRepository.load_annual_report()` |
| EID-only source | metadata has `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` |
| No fallback | metadata has `fallback_used=false`, `primary_failure_category=None` |
| Identity | report key is `004393 / 2024 / annual_report`; metadata fund code/year align |
| Integrity/parser viability | command returns parsed report with non-empty `raw_text`, section count and table count |
| Cache policy | returned `metadata.cache.source_metadata_present=true`; first forced acquisition has `pdf_cache_hit=false`, `parsed_cache_hit=false` |
| Safe retention | evidence artifact stores scalar metadata, section/table counts and exception category only, not raw PDF or full report text |

## Failure Classification

Acceptable terminal outcomes:

- `accepted_live_success`
- `blocked_not_found`
- `blocked_unavailable`
- `blocked_schema_drift`
- `blocked_identity_mismatch`
- `blocked_integrity_error`
- `blocked_environment`

Any failure must preserve source/failure category. It must not be relabeled as a generic success or hidden behind fallback.

## Evidence Artifact

Write:

- `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-evidence-20260610.md`

The artifact must include:

- exact command;
- exit code;
- safe stdout/stderr summary;
- source metadata scalar values;
- report key;
- section/table counts;
- controller classification;
- explicit statement that no fallback/provider/extractor/golden/readiness action was run.

## Validation

Before live command:

- `git status --short`

After live command:

- `git status --short`
- `git diff --check`

No pytest is required unless the live command or docs artifact changes tracked source/test files.

## Stop Conditions

Stop immediately and record blocker if:

- live command attempts a non-EID source;
- live command requires code changes;
- EID returns `schema_drift`, `identity_mismatch`, or `integrity_error`;
- EID is unavailable or times out;
- repository boundary cannot be used without directly calling source/downloader from higher layers;
- user authorization scope becomes ambiguous.
