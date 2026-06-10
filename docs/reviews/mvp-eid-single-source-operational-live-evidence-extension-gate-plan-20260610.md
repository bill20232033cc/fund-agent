# EID Single Source Operational Live Evidence Extension Gate - Plan

## Gate

- Gate: `EID Single Source Operational Live Evidence Extension Gate`
- Classification: `heavy`
- User authorization: option `1` after accepted checkpoint `6237f08`
- Objective: extend bounded live EID evidence beyond `004393 / 2024` to the remaining accepted small-golden source-identity rows, while preserving EID-only, no-fallback, FundDocumentRepository-only boundaries.

## Controller Startup Judgment

Current control truth permits this gate because `docs/implementation-control.md` lists "extend live EID evidence to additional rows only if separately authorized" as a valid next entry after the accepted `004393 / 2024` live proof. The user's `1` is treated as that separate authorization.

This gate does not reopen source policy design. Current implemented policy remains:

- `selected_source=eid`
- `mode=single_source_only`
- `fallback_enabled=false`
- Eastmoney, fund-company official website/CDN, CNINFO and other non-EID routes are deferred candidates or historical evidence-intake routes only.

## Current Truth

- EID single-source no-live implementation is current code fact.
- `004393 / 2024` has one accepted live EID/FDR acquisition proof.
- Other small-golden rows and live failure branches remain unproven.
- Production annual-report access must go through `FundDocumentRepository`.
- UI, Service, Host, renderer and quality gate must not directly call EID source, downloader, PDF cache, parser helper or source adapters.

## Authorized Live Scope

Authorized only for this gate:

- EID network access needed by the default EID source.
- PDF download needed by EID source integrity validation.
- `FundDocumentRepository.load_annual_report()` live acquisition for the fixed rows below.

Fixed row set:

| fund_code | report_year | document_kind | prior docs-only identity status |
|---|---:|---|---|
| `004194` | 2024 | `annual_report` | `matched_without_hash` |
| `006597` | 2024 | `annual_report` | `matched_without_hash` |
| `110020` | 2024 | `annual_report` | `matched_without_hash` |
| `017641` | 2024 | `annual_report` | `matched_without_hash` |

Still forbidden:

- fallback invocation;
- Eastmoney / fund-company / CNINFO source use;
- provider / LLM / endpoint probe;
- extractor correctness work;
- fixture projection;
- golden/readiness promotion;
- source code, tests, provider/default/runtime/budget/config changes;
- PR/push/merge/mark-ready.

## Command Shape

The live command must:

- instantiate `EidAnnualReportSource` with a temporary PDF cache directory;
- instantiate `AnnualReportSourceOrchestrator` with exactly one source: that EID source;
- instantiate `AnnualReportPdfAdapter` with that orchestrator;
- instantiate `FundDocumentRepository` with that adapter;
- override the repository document cache to a temporary document cache directory;
- call `repository.load_annual_report(fund_code, 2024, force_refresh=True)` for each fixed row;
- print only safe scalar metadata, counts, hashes and categorized exceptions;
- retain no PDF bytes, raw text or full parsed report text in the artifact.

The command must not:

- call `FundDataExtractor`;
- call `analyze`, `checklist`, renderer, Service, Host or UI;
- instantiate or import `EastmoneyAnnualReportSource`;
- construct `AnnualReportSourceOrchestrator` with more than one source;
- persist PDF contents in review artifacts.

## Row-Level Outcome Rules

Each row can end in one of:

- `accepted_live_success`
- `blocked_not_found`
- `blocked_unavailable`
- `blocked_schema_drift`
- `blocked_identity_mismatch`
- `blocked_integrity_error`
- `blocked_environment`

Continuation rules:

- `accepted_live_success`: record scalar evidence and continue.
- `blocked_not_found`: record row residual and continue to the next row, because this is a row-level EID discovery miss and does not authorize fallback.
- `blocked_unavailable`: stop the gate, because environmental/service availability may make later rows misleading.
- `blocked_environment`: stop the gate. This is a gate-local artifact category for unexpected environment/runtime exceptions only; it does not change the AGENTS.md annual-report source failure taxonomy and must not be written as source-policy metadata.
- `blocked_schema_drift`: stop the gate, because the EID contract may have drifted.
- `blocked_identity_mismatch`: stop the gate, because fail-closed identity behavior must be investigated before further live acquisition.
- `blocked_integrity_error`: stop the gate, because PDF integrity failure must remain fail-closed.
- unexpected exception or attempt to use non-EID source: stop the gate.

If all attempted rows end as `blocked_not_found`, the gate can close with `accepted_live_no_additional_success_with_row_residuals` only if the evidence artifact explicitly states the aggregate ambiguity: the result cannot by itself distinguish true row-level absence from a potential EID schema-drift path misclassified as `not_found`. That outcome must not be treated as proof that the four annual reports are absent from EID, and it must preserve an owner for a separate schema-drift diagnostic gate if reviewers need more evidence.

## Acceptance Matrix

| Check | Accepted evidence |
|---|---|
| FDR boundary | each attempted row calls `FundDocumentRepository.load_annual_report(fund_code, 2024, force_refresh=True)` |
| EID-only source | success metadata has `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false` |
| No fallback | success metadata has `fallback_used=false`, `primary_failure_category=None`; failure rows have no fallback success |
| Identity | success report key and metadata align to attempted `fund_code / 2024 / annual_report` |
| Integrity/parser viability | success rows have PDF magic `%PDF-`, SHA256, non-empty text, section count and table count |
| Failure classification | terminal rows preserve EID failure category without retrying another source |
| Safe retention | evidence artifact stores scalar metadata, counts, hash and exception category only, not raw PDF or full report text |

## Evidence Artifact

Write:

- `docs/reviews/mvp-eid-single-source-operational-live-evidence-extension-gate-evidence-20260610.md`

The artifact must include:

- exact command shape;
- exit code;
- safe stdout/stderr summary;
- per-row outcome table;
- source metadata scalar values for successful rows;
- report key for successful rows;
- section/table counts for successful rows;
- per-row failure category for blocked rows;
- original exception type and classification rationale for blocked rows;
- aggregate ambiguity statement if all rows are `blocked_not_found`;
- controller classification;
- explicit statement that no fallback/provider/extractor/golden/readiness action was run.

## Validation

Before live command:

- `git status --short`

After live command:

- `git status --short`
- `git diff --check`
- `git diff --name-only`

No pytest is required unless tracked source/test files are changed. This gate should not change source/test files.

## Review Routing

Two independent plan reviews:

- AgentDS: adversarial review for source-policy, FDR boundary, failure-classification and scope drift.
- AgentMiMo: adversarial review for live authorization boundary, row continuation rules, evidence retention and overreach.

Two independent evidence reviews after the live command:

- AgentDS: verify the evidence artifact matches the plan and no fallback/source bypass occurred.
- AgentMiMo: verify row-level outcomes, safe retention and no unauthorized scope expansion.

## Stop Conditions

Stop immediately and record blocker if:

- any command attempts a non-EID source;
- the command needs code/config/runtime changes;
- EID returns `schema_drift`, `identity_mismatch`, `integrity_error` or `unavailable`;
- repository boundary cannot be used without direct source/downloader calls from higher layers;
- workspace tracked source/test/config files change;
- user authorization scope becomes ambiguous.
