# EID Single Source Operational Implementation Planning Gate Plan

Date: 2026-06-10

Gate: `EID Single Source Operational Implementation Planning Gate`

Classification: `heavy`

Role: planning worker only

Deliverable status: code-generation-ready plan; no source, test, README, design/control, live source, fallback, provider, stage, commit, push or PR action performed in this gate.

## 1. Goal

Implement the accepted annual-report source policy as code in a later implementation gate:

- `selected_source=eid`
- `mode=single_source_only`
- `fallback_enabled=false`

The implementation must make EID the only production annual-report PDF source behind `FundDocumentRepository`. Eastmoney, fund-company website/CDN, CNINFO and other non-EID routes remain deferred candidates / historical evidence-intake routes only. They must not be default production fallback.

## 2. Non-goals

- No live EID/network/PDF/FDR acquisition during implementation acceptance.
- No Eastmoney, fund-company website/CDN, CNINFO or multi-source fallback production behavior.
- No extractor, renderer, quality gate, golden/readiness, fixture projection, score-loop, provider/runtime/default/config, Host/Agent runtime expansion, dayu runtime or `extra_payload` change.
- No direct source/downloader/cache/parser calls from UI, Service, Host, renderer or quality gate.
- No use of `fund_agent/tools/` or `scripts/claude_mimo_simple.py` as architecture truth, implementation input, validation input or evidence.

## 3. Current EID Implementation Inventory

Current facts from read-only inspection:

| Area | Current implementation | Required change |
|---|---|---|
| Public annual-report access | `FundDocumentRepository.load_annual_report()` is the public repository boundary and returns `ParsedAnnualReport`, not a PDF path. | Preserve this as the only production access boundary. |
| Adapter | `AnnualReportPdfAdapter` delegates PDF acquisition to `AnnualReportSourceOrchestrator`, then parses local PDF via parser helpers. | Preserve adapter boundary; default orchestrator must become EID-only. |
| EID source | `EidAnnualReportSource` already calls `validate_fund.do`, `advanced_search_report.do`, then `instance_show_pdf_id.do`, validates Content-Type and `%PDF-`, writes atomically, and returns `AnnualReportSourceMetadata`. | Reuse this source as the selected source; harden metadata/policy markers and tests. |
| Current default source orchestration | `AnnualReportSourceOrchestrator(None)` currently defaults to `(EidAnnualReportSource, EastmoneyAnnualReportSource)` and allows fallback after `not_found` / `unavailable`. | Replace production default with exactly one EID source; terminalize `not_found` / `unavailable` in single-source mode. |
| Failure taxonomy | Existing categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. Orchestrator fail-closes schema/mismatch/integrity but fallback-allows not_found/unavailable when more sources exist. | Keep five categories; no category allows production fallback under this gate. |
| Eastmoney wrapper | Existing wrapper maps `FileNotFoundError` to `not_found` and `httpx.HTTPError` / `OSError` / `ValueError` to `unavailable`; repo review found the `ValueError` path can mask PDF integrity failure. | Do not fix or promote Eastmoney in this gate; remove it from production default and mark only as deferred future fallback-candidate risk. |
| Source metadata | `AnnualReportSourceMetadata` persists source URL, fund identity/report fields, upload ids, `fallback_used`, and `primary_failure_category`. Cache stores metadata JSON in `documents.source_metadata_json` and parsed payload metadata. | Add explicit single-source policy metadata and reject non-EID/fallback/unknown-source cache hits for production EID-only loads. |
| Cache behavior | Repository can reuse parsed report cache or PDF cache even when source metadata is missing, Eastmoney, or fallback-backed. | Change repository cache admissibility so production EID-only reads do not consume legacy unknown/Eastmoney/fallback cache entries. |
| Existing tests | EID no-live tests use `httpx.MockTransport`; fallback tests currently assert fallback after `not_found` / `unavailable`; repository tests assert fallback metadata persistence and legacy no-metadata cache reuse. | Update tests to assert EID-only default, terminal failures, cache rejection for non-EID/unknown/fallback metadata, and no live/network dependencies. |

## 4. EID Discovery Contract

Production discovery is EID-only and exact-code-only for this implementation gate.

Required call sequence inside `EidAnnualReportSource.fetch_annual_report_pdf()`:

1. Normalize request `fund_code` to exactly six digits; invalid format is `identity_mismatch`.
2. POST `EID_VALIDATE_FUND_PATH` with `cFundCode=<fund_code>`.
3. Validate response:
   - `isSuccess is True` and non-empty `fundId` -> continue.
   - `isSuccess is False` -> `not_found`.
   - missing/non-object/non-JSON/invalid `fundId` -> `schema_drift`.
4. GET `EID_ADVANCED_SEARCH_REPORT_PATH` with `aoData` containing:
   - `reportType=FB010`
   - `reportYear=<year>`
   - `fundCode=<fund_code>`
   - no fund-short-name fallback in this gate.
5. Parse `aaData` list. Missing/non-list/non-object candidate rows are `schema_drift`.
6. Select exactly one valid annual-report candidate. Empty valid set is `not_found` only when there are no contradictory candidates; contradictory candidate rows are `identity_mismatch`; multiple valid candidates are `schema_drift`.
7. Build PDF URL with `instance_show_pdf_id.do?instanceid=<uploadInfoId>`.

Deferred: EID internal short-name discovery, share-class reconciliation, corrected CSV mapping, QDII/FOF special paths, quarterly/interim/prospectus documents. These require a separate design/identity gate.

## 5. EID Identity Validation Contract

The selected EID candidate must match all fields before any PDF download is trusted:

| Field | Required value / relation | Failure category |
|---|---|---|
| `fundCode` | exact request fund code | `identity_mismatch` |
| `fundId` | exact `validate_fund.do` `fundId` | `identity_mismatch` |
| `reportYear` | exact request year | `identity_mismatch` |
| `reportCode` | `FB010010` | `identity_mismatch` |
| `reportDesp` | `年度报告` | `identity_mismatch` |
| `tableName` | `PDF` | `identity_mismatch` |
| `reportName` | must not be annual-report abstract / summary | `identity_mismatch` |
| `attachFileName` / `attachFilePath` | unsupported in this gate; must be absent/empty | `schema_drift` |
| `uploadInfoId` / `uploadInfoDetailId` | non-empty strings | `schema_drift` |

Identity validation must happen before `_build_eid_metadata()` and before PDF cache write. No caller outside `fund_agent/fund/documents` may override identity status.

## 6. EID PDF Integrity Contract

PDF integrity is fail-closed:

- HTTP status:
  - 5xx, timeout, transport error, retry exhaustion -> `unavailable`.
  - non-200 -> `unavailable` unless a future reviewed EID response contract proves a stable not-found status.
- Response Content-Type:
  - normalized media type must equal `application/pdf`; otherwise `integrity_error`.
- Response body:
  - must start with `%PDF-`; otherwise `integrity_error`.
- Cached EID PDF:
  - must exist, be at least `%PDF-` length, and start with `%PDF-`.
  - invalid cached PDF is not trusted; it may be unlinked and refetched through EID only.
- Write:
  - write via temp file + fsync + atomic replace.
  - write failure is local unavailable/infrastructure failure, not identity/schema success.

No HTML body, redirect landing page, JSON error page, empty body or non-PDF file may be classified as `unavailable` after a 200 response with non-PDF content. It is `integrity_error`.

## 7. Source Metadata Schema

Implementation must keep metadata safe, structured and cache-persisted.

Required successful EID metadata fields:

| Field | Required value |
|---|---|
| `source` | `eid` |
| `source_url` | EID PDF URL containing `instanceid=<uploadInfoId>` |
| `fund_code` | exact EID candidate/request fund code |
| `fund_id` | exact validate/search fund id |
| `report_year` | request year |
| `report_code` | `FB010010` |
| `report_desp` | `年度报告` |
| `report_name` | optional EID report name; must not be summary |
| `upload_info_id` | EID announcement instance id |
| `upload_info_detail_id` | EID detail id |
| `table_name` | `PDF` |
| `report_send_date` | optional source date |
| `operation_upload_type` | optional source upload type |
| `corrections_num` | optional integer |
| `fallback_used` | `False` |
| `primary_failure_category` | `None` |
| `selected_source` | `eid` |
| `source_mode` | `single_source_only` |
| `fallback_enabled` | `False` |
| `discovery_contract_version` | `eid_annual_report_discovery.v1` |

Implementation detail:

- Additive metadata fields can be added to `AnnualReportSourceMetadata` without changing the SQLite schema because source metadata is JSON payload.
- `from_dict()` must tolerate legacy payloads but policy validation must treat missing `selected_source/source_mode/fallback_enabled` as not admissible for production cache reuse unless an implementation worker explicitly proves a safe migration path in review.
- Do not store raw response body, prompt, secret, auth header, cookies or full PDF bytes in metadata.

## 8. Repository / Cache Persistence Boundaries

`FundDocumentRepository` remains the only production annual-report read boundary.

Required cache policy:

1. Parsed report cache hit is usable only when `report.metadata.source` satisfies current EID-only policy:
   - `source == "eid"`
   - `fallback_used is False`
   - `primary_failure_category is None`
   - `selected_source == "eid"`
   - `source_mode == "single_source_only"`
   - `fallback_enabled is False`
2. PDF cache entry is usable only when its `source_metadata` satisfies the same policy.
3. Legacy parsed/PDF cache with missing metadata, Eastmoney metadata, fallback metadata, or unknown source-policy metadata must be treated as stale for production EID-only loads. It may remain on disk; implementation must not delete unrelated cache files as part of acceptance.
4. `force_refresh=True` bypasses parsed and PDF cache as it does today, and fetches from EID only.
5. Parsed report save must persist the same source metadata that came from the EID PDF fetch result.
6. The repository must not expose local PDF paths to UI/Service/Host/renderer/quality gate beyond existing internal metadata; callers continue consuming `ParsedAnnualReport`.

No migration script is required for this gate. Stale legacy cache is ignored by policy rather than rewritten in bulk.

## 9. Failure Category Matrix

Single-source mode terminal behavior:

| Failure | Meaning | Terminal? | Fallback? | Expected exception surface |
|---|---|---:|---:|---|
| `not_found` | EID validly says fund/report absent, or exact annual report has no candidate | Yes | No | `AnnualReportSourceNotFoundError` |
| `unavailable` | EID/network/timeout/5xx/local transient write infrastructure failure | Yes | No | `AnnualReportSourceUnavailableError` or aggregate with only EID failure if the implementation keeps aggregate type |
| `schema_drift` | EID JSON/candidate shape violates contract | Yes | No | fail-closed typed source error, preserving original cause |
| `identity_mismatch` | Candidate contradicts requested fund/year/report identity | Yes | No | fail-closed typed source error, preserving original cause |
| `integrity_error` | EID PDF response/cache/write content is not a valid PDF contract | Yes | No | fail-closed typed source error, preserving original cause |

Implementation may introduce `AnnualReportSourceFailClosedError` to replace fallback-specific wrapping for schema/mismatch/integrity. If it keeps `AnnualReportSourceFallbackBlockedError` temporarily, docs/tests must make clear that no fallback exists and the name is legacy; preferred implementation is a new fail-closed exception with `failure.source`, `failure.category`, and `__cause__`.

## 10. Allowed Files

Future implementation gate may touch only these files unless a controller explicitly amends the plan after review:

- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py` only if docstring/default-source wording needs alignment
- `fund_agent/fund/documents/cache.py` only if metadata serialization helpers need additive support; no SQLite table migration expected
- `tests/fund/documents/test_annual_report_sources.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/documents/test_cache.py`
- `fund_agent/fund/README.md` after code/tests are accepted, to document current Fund documents source policy
- `tests/README.md` if test taxonomy/run instructions change
- `docs/design.md` and `docs/implementation-control.md` only in the documentation/control sync slice after implementation and reviews are accepted
- New review/evidence artifacts under `docs/reviews/` for implementation/review/closeout

## 11. Forbidden Files / Paths

Forbidden in the implementation gate:

- `fund_agent/tools/`
- `scripts/claude_mimo_simple.py`
- `fund_agent/ui/`
- `fund_agent/services/`
- `fund_agent/host/`
- `fund_agent/agent/` except no changes expected and not authorized by this plan
- `fund_agent/fund/extractors/`
- `fund_agent/fund/pdf/parser.py`
- `fund_agent/fund/pdf/downloader.py` unless controller explicitly accepts a separate Eastmoney/downloader integrity gate
- `render/`
- `reports/`
- `reviews/`
- `docs/fund-analysis-template-draft.md`
- golden answers, fixtures, snapshots, score artifacts, release artifacts, provider config/default/runtime files
- README files outside the allowed docs above

Forbidden actions:

- live EID/network/PDF/FDR/fallback/provider/curl/DNS/socket/probe/smoke
- invoking `FundDocumentRepository.load_annual_report()` against real sources
- fallback invocation
- staging, committing, pushing, opening PR, merge, mark-ready, release
- importing, executing or reading source-like residue paths
- introducing `dayu-agent`, `dayu.host`, `dayu.engine` production dependency
- adding `extra_payload` for explicit business/source parameters

## 12. Implementation Slices

### Slice 1: EID-only source policy and terminal orchestration

Objective: make production default source orchestration exactly EID single-source.

Allowed files: `fund_agent/fund/documents/sources.py`, `tests/fund/documents/test_annual_report_sources.py`.

Required changes:

- Change `AnnualReportSourceOrchestrator(None)` default from EID + Eastmoney to exactly one `EidAnnualReportSource(config=self.config)`.
- Enforce single-source invariant for production path:
  - either reject `sources` tuples with length other than 1, or introduce an explicit test-only/migration-only helper that cannot be reached by default production adapter.
  - preferred: `AnnualReportSourceOrchestrator((source,))` only; `AnnualReportSourceOrchestrator(())` and multi-source tuples raise `ValueError`.
- Remove fallback success marking from production path. Successful EID result must keep `fallback_used=False` and `primary_failure_category=None`.
- Make `not_found` and `unavailable` terminal when EID fails.
- Make schema/mismatch/integrity terminal fail-closed, preserving source/category/cause.
- Keep `EastmoneyAnnualReportSource` only as an unused deferred candidate if deletion is too broad; it must not be reachable from default production adapter.

No-live tests:

- Update `test_orchestrator_rejects_empty_sources_but_none_uses_default` to assert:
  - `None` default has exactly one source;
  - that source is `EidAnnualReportSource`;
  - no `EastmoneyAnnualReportSource` exists in default sources.
- Replace fallback tests with terminal tests:
  - EID `AnnualReportSourceUnavailableError` does not call a second source and raises terminal unavailable.
  - EID `AnnualReportSourceNotFoundError` does not call a second source and raises terminal not-found.
  - multi-source constructor is rejected, if this strategy is selected.
- Preserve tests that schema/mismatch/integrity fail closed, updated to the new exception surface if needed.

Completion signal:

- No default production code path constructs Eastmoney fallback.
- No test asserts successful fallback in current production source policy.

Stop condition:

- If a reviewer requires retaining multi-source injection for no-live unit tests, implementation must prove it is impossible to reach from `AnnualReportPdfAdapter()` default production path and must document the residual as test-only. Controller must decide before acceptance.

### Slice 2: Source metadata schema hardening

Objective: make successful EID metadata explicitly prove single-source policy.

Allowed files: `fund_agent/fund/documents/models.py`, `fund_agent/fund/documents/sources.py`, `tests/fund/documents/test_cache.py`, `tests/fund/documents/test_annual_report_sources.py`.

Required changes:

- Extend `AnnualReportSourceMetadata` with additive safe fields:
  - `selected_source: Literal["eid"] | None`
  - `source_mode: Literal["single_source_only"] | None`
  - `fallback_enabled: bool | None`
  - `discovery_contract_version: str | None`
- Serialize/deserialize the fields in `to_dict()` / `from_dict()`.
- `_build_eid_metadata()` must populate:
  - `selected_source="eid"`
  - `source_mode="single_source_only"`
  - `fallback_enabled=False`
  - `discovery_contract_version="eid_annual_report_discovery.v1"`
- Keep legacy deserialization tolerant; do not bulk-migrate cache.

No-live tests:

- EID happy path asserts all new metadata fields.
- Cache metadata round-trip asserts new fields survive `to_dict()` / `from_dict()`.
- Legacy metadata payload without new fields deserializes without crashing but leaves fields as `None`.
- Unknown `source_mode` / malformed `fallback_enabled` behavior must be explicit; preferred fail-closed for invalid typed values in direct metadata constructors, tolerant-to-None for legacy JSON.

Completion signal:

- Fresh EID fetch metadata carries enough information to distinguish current EID-only policy from old EID/Eastmoney/fallback metadata.

### Slice 3: Repository/cache admissibility for EID-only policy

Objective: prevent production loads from consuming old Eastmoney/fallback/unknown-source cache.

Allowed files: `fund_agent/fund/documents/repository.py`, `tests/fund/documents/test_repository.py`; `fund_agent/fund/documents/cache.py` only if helper placement requires it.

Required changes:

- Add a small policy helper, preferably module-private in `repository.py`:
  - `_is_current_eid_single_source_metadata(metadata: AnnualReportSourceMetadata | None) -> bool`
- The helper returns `True` only for:
  - source `eid`;
  - `fallback_used is False`;
  - `primary_failure_category is None`;
  - `selected_source == "eid"`;
  - `source_mode == "single_source_only"`;
  - `fallback_enabled is False`.
- Before returning a parsed report cache hit, check `cached_report.metadata.source` with this helper. If false, ignore parsed cache and proceed to PDF cache/fetch.
- Before reusing a PDF cache entry, check `pdf_entry.source_metadata` with this helper. If false, ignore PDF cache and fetch via EID.
- Do not delete stale cache entries by default; do not rewrite unrelated cache.
- Fresh fetch must still record source metadata and save parsed report as today.

No-live tests:

- Parsed cache with current EID policy metadata is reused.
- Parsed cache with legacy missing metadata is ignored and fresh EID metadata-aware loader is called.
- Parsed cache with Eastmoney/fallback metadata is ignored and fresh EID metadata-aware loader is called.
- PDF cache with current EID policy metadata is reused.
- PDF cache with missing/Eastmoney/fallback metadata is ignored and fresh EID metadata-aware loader is called.
- `force_refresh=True` still bypasses all cache and overwrites metadata.
- Concurrent metadata tests still prove no cross-attach.

Completion signal:

- A production `FundDocumentRepository.load_annual_report()` cannot silently return old Eastmoney/fallback/unknown-source parsed/PDF cache content under EID-only policy.

### Slice 4: Adapter/default wiring and boundary regressions

Objective: prove the default repository path reaches EID-only source through existing boundaries and no upper layer bypass is introduced.

Allowed files: `fund_agent/fund/documents/adapters/annual_report_pdf.py` if wording needs alignment, `tests/fund/documents/test_repository.py`, `tests/fund/documents/test_annual_report_sources.py`.

Required changes:

- If `AnnualReportPdfAdapter` docstring says "current default sources", update wording to "current default EID source" without changing public API.
- Add/adjust no-live regression that default `AnnualReportPdfAdapter()` owns an `AnnualReportSourceOrchestrator` whose default source set is EID-only. Use object inspection only; do not fetch.
- Add/adjust repository boundary regression to keep return type `ParsedAnnualReport` and no PDF path exposure.

No-live tests:

- Object construction of default adapter/repository does not touch network.
- Default orchestrator source inventory is EID-only.
- Existing repository "returns ParsedAnnualReport without path exposure" still passes.

Completion signal:

- Source policy is enforced behind `FundDocumentRepository`; UI/Service/Host/renderer/quality gate remain unchanged.

### Slice 5: Documentation and control sync after accepted implementation

Objective: update docs only after code/tests/reviews prove the implementation.

Allowed files: `fund_agent/fund/README.md`, `tests/README.md` if needed, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` if controller requires startup mirror update, and implementation evidence/review artifacts under `docs/reviews/`.

Required timing:

- Do not edit docs/design/control before implementation evidence and code review pass.
- After code review acceptance, update `docs/design.md` from "EID single-source accepted target / not implemented code fact" to current code fact, with exact current scope:
  - EID-only annual-report PDF source behind `FundDocumentRepository`;
  - no Eastmoney/fund-company/CNINFO fallback;
  - no live proof accepted unless a later live gate runs;
  - no extractor/renderer/quality/golden/provider/Host/Agent runtime change.
- Update `docs/implementation-control.md` current gate/residual rows:
  - mark implementation accepted only after local accepted checkpoint;
  - keep live EID proof residual unauthorized until separate live gate;
  - keep Eastmoney integrity finding as deferred future fallback-candidate risk.
- Update `fund_agent/fund/README.md` documents section to describe current EID-only production source policy.
- Update `tests/README.md` only if new no-live source-policy test grouping or command guidance changes existing test manual.

No-live validation:

- `git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md`
- targeted docs grep checks listed in §14.

Completion signal:

- Docs distinguish current code fact, future live proof, and deferred source candidates without presenting live EID acquisition as accepted.

## 13. No-live Tests Per Slice

| Slice | Test files | Required assertions |
|---|---|---|
| S1 | `tests/fund/documents/test_annual_report_sources.py` | default sources are EID-only; multi-source fallback not production-reachable; not_found/unavailable terminal; schema/mismatch/integrity fail-closed |
| S2 | `tests/fund/documents/test_annual_report_sources.py`, `tests/fund/documents/test_cache.py` | EID metadata carries source policy; metadata JSON round trip; legacy metadata tolerated but not policy-admissible |
| S3 | `tests/fund/documents/test_repository.py` | parsed/PDF cache admissibility rejects missing/Eastmoney/fallback metadata; accepts current EID metadata; force_refresh and concurrency remain correct |
| S4 | `tests/fund/documents/test_repository.py`, `tests/fund/documents/test_annual_report_sources.py` | default adapter/repository construction remains no-live and points to EID-only source; repository boundary preserved |
| S5 | docs grep / diff checks | design/control/readme truth updated only after implementation accepted; no future/live proof written as current fact |

## 14. No-live Validation Matrix

Implementation acceptance must run no-live commands only:

| Validation | Command | Expected result |
|---|---|---|
| Source policy tests | `uv run pytest tests/fund/documents/test_annual_report_sources.py -q` | pass; no live network because tests use fake sources / `httpx.MockTransport` |
| Repository/cache tests | `uv run pytest tests/fund/documents/test_repository.py tests/fund/documents/test_cache.py -q` | pass; temp cache only |
| Boundary regressions | `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py tests/fund/documents/test_cache.py tests/fund/test_source_provenance.py tests/fund/test_report_quality_validation.py -q` | pass |
| Broader local regression | `uv run pytest tests/fund tests/services tests/ui -q` | pass or documented unrelated failure with direct evidence |
| Lint | `uv run ruff check fund_agent tests` | pass |
| Whitespace | `git diff --check` | pass |
| Forbidden path audit | `git diff --name-only` | must not include `fund_agent/tools/` or `scripts/claude_mimo_simple.py` |
| No fallback wording in current docs | `rg -n "Eastmoney.*production fallback|fallback_enabled=true|primary_then_fallback" docs/design.md docs/implementation-control.md fund_agent/fund/README.md` | no current-production claims after docs sync |

Forbidden validation:

- `fund-analysis analyze ...` against real source
- `FundDocumentRepository.load_annual_report()` with default real source
- curl/DNS/socket/browser/network/PDF live smoke
- fallback invocation
- provider/LLM commands

## 15. Direct Evidence Matrix

| Claim | Direct evidence used for this plan |
|---|---|
| `FundDocumentRepository` is the annual-report access boundary | `AGENTS.md:75-79`; `fund_agent/fund/documents/repository.py:1-5`; `docs/design.md:1087-1096` |
| UI/Service/Host/renderer/quality gate must not call source/cache/downloader helpers | `AGENTS.md:77`; `docs/design.md:51-59` |
| Current accepted policy is EID single source, fallback disabled | `docs/current-startup-packet.md:18-22`; `docs/design.md:5-6`; `docs/design.md:1096-1106`; `docs/reviews/mvp-eid-single-source-operational-implementation-planning-gate-startup-judgment-20260610.md:15-29` |
| Current code still defaults to EID + Eastmoney fallback | `fund_agent/fund/documents/sources.py:570-594`; `tests/fund/documents/test_annual_report_sources.py:396-417` |
| Existing fallback behavior allows not_found/unavailable fallback | `fund_agent/fund/documents/sources.py:622-660`; `fund_agent/fund/documents/sources.py:685-699`; `tests/fund/documents/test_annual_report_sources.py:953-1009` |
| Existing EID source already has discovery/identity/PDF integrity primitives | `fund_agent/fund/documents/sources.py:31-39`; `fund_agent/fund/documents/sources.py:356-412`; `fund_agent/fund/documents/sources.py:940-1174`; `tests/fund/documents/test_annual_report_sources.py:419-924` |
| Source metadata currently persists source/fallback fields but lacks explicit source policy markers | `fund_agent/fund/documents/models.py:24-129`; `fund_agent/fund/documents/cache.py:96-139`; `tests/fund/documents/test_cache.py` metadata tests |
| Repository currently can reuse cached parsed/PDF metadata | `fund_agent/fund/documents/repository.py:322-385`; `tests/fund/documents/test_repository.py:585-1051` |
| Eastmoney integrity misclassification is deferred, not current production fallback scope | `docs/reviews/repo-review-20260609-165959.md:18-38`; `docs/implementation-control.md:590-598`; startup judgment `20260610.md:25-29` |
| Source-like residue is explicitly ignored | startup judgment `20260610.md:32-40` |

## 16. Rollback

Rollback after implementation should be simple and local:

- Revert the implementation commit(s) for `fund_agent/fund/documents/*`, tests and docs.
- No cache migration is performed, so rollback does not require cache schema downgrade.
- Any stale cache ignored by the implementation remains untouched on disk.
- If docs/control were updated in Slice 5, rollback must also restore design/control wording to "accepted target / not implemented code fact".

Do not delete cache directories, reports, untracked residue or user files as rollback.

## 17. Residual Risk

| Risk | Disposition |
|---|---|
| No live EID proof | Intentional residual. Optional live gate requires separate user authorization. No implementation acceptance may claim live success. |
| Legacy cache ignored may cause first post-implementation run to fetch EID again | Accepted operational consequence of single-source integrity; no bulk migration. |
| Some share-class codes may not match EID exact fundCode | Deferred to EID identity/discovery follow-up; this implementation remains exact-code fail-closed. |
| Eastmoney wrapper integrity bug remains in code if class is retained | Deferred future source-candidate/fallback risk only; not production-reachable under EID-only default. |
| Existing exception names may mention fallback if not replaced | Prefer new fail-closed exception. If retained for minimal churn, must be documented as legacy naming and reviewed as non-blocking only if no production fallback exists. |
| Metadata schema is additive and cache JSON-tolerant | Accepted. Policy admissibility, not JSON deserialization, is the security boundary. |

## 18. Design / Control Update Points

Do not update `docs/design.md` or `docs/implementation-control.md` in the planning gate.

Future implementation gate:

1. Plan accepted + implementation starts: no design/control update yet.
2. Code + no-live tests pass: still no design/control update until review.
3. Code review/re-review accepted: update `docs/design.md`, `docs/implementation-control.md`, and if controller requires, `docs/current-startup-packet.md`.
4. Local accepted checkpoint created: control doc can state EID single-source is current code fact and live proof remains residual.
5. Optional live gate later: only after explicit user authorization may live evidence update control/design with live operational status.

## 19. Optional Live EID Smoke Gate

This is not part of implementation acceptance.

Status: deferred; requires separate user authorization.

Allowed only after:

- implementation slices S1-S5 accepted;
- controller opens a separate live evidence gate;
- user explicitly authorizes live EID/network/PDF/FDR action;
- test target fund/year and cache policy are specified;
- no fallback and no provider/LLM probes are bundled.

Minimal live smoke candidate after authorization:

- one fund/year only;
- route through `FundDocumentRepository` or a controller-approved narrower source probe, not UI/Service/Host/renderer/quality gate bypass;
- record source metadata, PDF integrity result, cache behavior and terminal failure category;
- never invoke Eastmoney/fund-company/CNINFO fallback.

## 20. Completion Report Format For Implementation Worker

Implementation worker must report:

- changed files;
- slice IDs completed;
- no-live validation commands and results;
- direct evidence that default production source is EID-only;
- direct evidence that non-EID/unknown/fallback cache entries are not consumed;
- docs update status;
- residual risks with owner/destination;
- confirmation: no live EID/network/PDF/FDR/fallback/provider probe, no source-like residue use, no stage/commit/push/PR.
