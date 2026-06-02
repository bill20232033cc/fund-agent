# MVP multi-year annual evidence scope design

## Worker Self-Check

- Role: scoped design specialist only, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`.
- Scope: design/review only. This artifact designs five-year annual report evidence scope and contract boundaries.
- Allowed output file: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`.
- Files intentionally not edited: source code, tests, `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, README, reports, retained artifacts.
- Actions intentionally not taken: no implementation, no commit, no push, no PR, no provider runtime budget change, no score-loop wiring, no quarterly/prospectus/fund-contract scope, no direct template truth replacement.
- Source-of-truth discipline: current facts below are limited to the required read set and local code. Proposed types and flows are future design only unless explicitly described as current code facts.

## Current Facts

1. Current production annual report access is centralized through `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)`. The repository validates fund code/year, hides local PDF paths from callers, manages parsed/PDF cache provenance internally, and returns a `ParsedAnnualReport`. Service/UI/Host/renderer/quality gate must not call PDF cache, download helpers, or concrete annual-report sources directly.

2. Current `AnnualReportSourceMetadata` records source name, fund identity fields, report year, report type fields, `fallback_used`, and `primary_failure_category`. The closed failure taxonomy is `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. Existing guardrails allow fallback only for `not_found` and `unavailable`; `schema_drift`, `identity_mismatch`, and `integrity_error` must fail closed.

3. Current `FundDataExtractor.extract(fund_code, report_year, force_refresh=...)` loads exactly one annual report through the repository, then builds one `StructuredFundDataBundle` for that report year. NAV failures can degrade to unavailable, but annual report repository/extractor failures propagate unless handled by a future boundary.

4. Current `StructuredFundDataBundle` is single-year. It contains one `fund_code`, one `report_year`, one set of extracted fields, one `nav_data`, one `source_provenance`, and no year-indexed annual evidence collection.

5. Current `ChapterFactProvider.project()` / `project_chapter_facts()` consume an in-memory single-year `StructuredFundDataBundle` and template truth APIs. They do not read annual reports, repositories, PDF/cache/source helpers, parsers, LLM, Service, Host, or dayu.

6. Current `chapter_fact_projection.v1` public chapter ids remain `0-7`. Chapter 5 currently receives a synthetic missing fact with `source_field_name="cross_period_comparison"`, `missing_reason="cross_period_comparison_missing"`, and detail saying the current input is a single-period `StructuredFundDataBundle` and must not fake cross-period comparison.

7. Current `ReportEvidenceBundle` is also projected from one `StructuredFundDataBundle`. It records one `report_year`, `source_documents`, `facts`, `evidence_anchors`, `data_gaps`, and derived quality/review state, but it does not load documents and does not represent a five-year annual evidence corpus. Current `ReportEvidenceProjectionContext` is also single-year shaped: it carries one `source_failure_category`, one `document_identity_status`, and one `fallback_used` flag.

8. Current `ReportDataGap` is the existing typed gap truth for report evidence. It already carries gap kind, failure category, reason code, chapter refs, fallback flags, required wording, and blocked claim ids. This gate must not create a third unrelated gap truth source.

9. Current deterministic `analyze/checklist` and provider-backed `analyze --use-llm` behavior are unchanged by this gate. Current Agent runner/tool-loop is not implemented; current Host runtime governance is process-local and business-agnostic.

## Accepted Prior Inputs

1. The template typed contract redesign gate is accepted only as future design. It accepts typed `ChapterContract`, derived `EvidenceAvailability`, evidence-conditional Ch3 `must_not_cover`, `RequiredOutputItem.when_evidence_missing`, Ch0 consuming Ch7 with fail-closed body readiness, and per-chapter `audit_focus` for bounded semantic audit only. It explicitly keeps public chapter ids `0-7`.

2. The same gate accepts `EvidenceAvailability` as a derived supplemental view over same-source `ChapterFactProjection`, not a replacement unless a later gate accepts that replacement. It also recognizes future year-tier/data-tier availability such as `1Y/3Y/5Y` and `available_report_years`, but does not implement it.

3. The same gate rejects direct five-year raw PDF/text injection into LLM prompts, provider budget changes, score-loop wiring, quality gate changes, final judgment changes, golden/readiness changes, Ch2 split, and public chapter count changes.

4. The internalized Agent engine/tool-loop contract execution gate is accepted only as future design. It accepts future Agent ownership of `AgentReportRun`, `ChapterTask`, task graph, tool loop, attempt ledger, `ToolRegistry`, `ToolTrace`, repair policy, and `FinalAssemblyReadiness`. Service keeps use case, `ExecutionContract`, quality policy, report strategy, first-MVP provider construction/runtime ceilings, and final product fail-closed mapping. Fund owns domain tools, `ChapterContract`, `ChapterFactProjection`, derived `EvidenceAvailability`, programmatic-first audit, bounded semantic audit adapter, and `RepairSemantics`.

5. The same Agent gate clarifies that `EvidenceAvailability` is precomputed typed input, not a ToolRegistry tool; Service-constructed writer/auditor clients are explicit per-run typed fields, not tools and not `extra_payload`.

## First-Principles Problem

The current single-year evidence path is safe but incomplete for template Chapter 5. A single `StructuredFundDataBundle` can support current-year product identity, performance, manager, investor experience, risk, and final judgment inputs, but it cannot prove "current stage and key changes" because change is a relation across years. The current system correctly marks that gap as `cross_period_comparison_missing`.

The future Agent needs bounded multi-year annual evidence so it can answer cross-year questions without inventing changes from a single year and without pushing raw PDF text into prompts. The core problem is therefore not "load more PDFs into context"; it is "declare, load, summarize, anchor, and degrade a bounded annual-report corpus through typed contracts while preserving same-fund identity and repository fallback semantics."

The safe MVP answer is a typed annual evidence scope that:

- caps the corpus at target year plus up to four prior annual reports;
- loads each annual report only through `FundDocumentRepository`;
- turns each available year into typed extracted facts/summaries and anchors;
- records missing years and failure categories explicitly;
- lets Chapter 5 use cross-year derived facts only when the typed annual evidence is sufficient;
- keeps Chapter 0 and Chapter 7 fail-closed on accepted body chapters;
- never injects raw five-year PDF text into LLM prompts.

## Proposed Future Design

### 1. Annual Evidence Scope

MVP annual scope is:

- `target_year`: the requested report year and the only required year for the current-year report.
- `prior_years`: up to four immediately preceding annual report years. MVP deterministic order is most-recent first for request planning and presentation summaries, while cross-year calculations may internally sort ascending when computing deltas as long as anchor ids and source years remain explicit.
- `max_years`: default `5` and absolute cap `5`; valid request value range is `1..5`.
- `same_fund_identity`: every loaded annual report must match the requested `fund_code` and report year through repository/source metadata and parsed document key. `fund_id` consistency is compared only within the same source when `fund_id` is present across years; same-source inconsistency is `identity_mismatch` for the affected year. Cross-source `fund_id` comparison is not required for MVP.
- `availability_bound`: if a prior annual report is not available or temporarily unavailable, the corpus records an availability gap instead of pretending five years exist.
- `public_chapter_ids`: remain `0-7`. Chapter 5 receives cross-year evidence inside chapter id `5`, not by adding new public chapters.

The accepted MVP scope is annual reports only. It does not include quarterly reports, interim reports, prospectus, fund contract, fact sheets, third-party pages, or raw PDF snippets beyond typed summaries and anchors.

### 2. Service Scope Declaration And Request Validation

Service may declare what annual evidence is needed, but must not load documents or touch repository/cache/source helper internals. Future Service-owned request/contract shape should be explicit and typed, for example:

```python
AnnualEvidenceScopeRequest(
    fund_code: str,
    target_year: int,
    required_years: tuple[int, ...],
    optional_years: tuple[int, ...],
    max_years: int,
    force_refresh: bool,
    degradation_policy: Literal["current_year_required_prior_years_optional"],
)
```

Boundary rules:

- `target_year` is required and must be a valid annual report year accepted by the same validation policy as the repository-facing year.
- `required_years` must contain `target_year` for MVP. A request that omits `target_year` from `required_years` fails at request construction; historical-only analysis is out of this MVP scope.
- `required_years` and `optional_years` must be disjoint. Any overlap fails at request construction rather than being silently deduplicated.
- `max_years` is an absolute cap in the closed range `1..5`. If `len(required_years) > max_years`, construction fails. If `len(required_years) + len(optional_years) > max_years`, optional years are truncated from the most distant year first until the cap is satisfied.
- `optional_years` should contain prior years up to `target_year - 4`, bounded by `max_years`; implementation must reject optional years after `target_year` for this MVP.
- Deterministic year order is required. The canonical request order is `target_year`, then prior years descending by year. Any implementation that accepts caller-supplied tuples must normalize to this order before loading and before deriving stable ids.
- `force_refresh` is a typed policy forwarded across Service into the Fund capability call; Service must not translate it into cache or PDF operations.
- MVP `force_refresh` applies uniformly to all requested years if present. More granular per-year refresh is deferred; it must not be hidden in `extra_payload`.
- Service may include this request in a future `ExecutionContract` / `AgentReportRun` input because it is a business scope declaration.
- Service must not call `FundDocumentRepository`, PDF cache, concrete source orchestrator, downloader, parser helper, or local filesystem paths directly.
- No scope parameter may be hidden in `extra_payload`.

### 3. Fund Loading Boundary

Fund/Agent domain capability should own annual evidence loading. The future loader should call:

```python
FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=force_refresh)
```

once per requested annual report year. It should not bypass the repository, should not read cached PDFs directly, and should not call concrete source/download helpers from Service/UI/Host/renderer/quality gate.

Failure handling:

- Required current year `not_found` or `unavailable`: run cannot produce current-year report evidence and should fail closed or return a typed blocked result according to the surrounding Service/Agent contract.
- Optional prior year `not_found` or `unavailable`: record a year-level availability gap/degradation if the chapter contract allows degraded cross-year reasoning.
- Current target year `schema_drift`, `identity_mismatch`, or `integrity_error`: block report evidence for the run. Current-year fail-closed still prevents current-year report evidence because the canonical report cannot be trusted.
- Optional prior year `schema_drift`, `identity_mismatch`, or `integrity_error`: fail closed for that year's evidence only, mark the year `failed_closed`, and disallow any cross-year claim whose requirement depends on that year. This does not kill the current-year report unless the failed prior year is explicitly required by a future contract.
- Repository fallback remains internal to the repository/source orchestration. If fallback succeeds, metadata such as `fallback_used=True` and `primary_failure_category` must be retained in the resulting source document record.
- If all optional prior years are missing/unavailable but current year is valid, current-year chapters may continue where their contracts allow one-year evidence; Chapter 5 must declare that cross-period comparison is unavailable and avoid cross-year change claims.
- Multi-year loading may use concurrency only after an implementation gate proves repository/cache/source adapters are safe under concurrent access and without changing provider/runtime budgets. Sequential loading is acceptable for correctness-first MVP planning.

### 4. Future Typed Evidence Bundle Shape

Future design may introduce an annual evidence corpus or bundle without changing current `StructuredFundDataBundle` facts prematurely. The safest boundary is an additive wrapper:

```python
AnnualEvidenceBundle(
    fund_code: str,
    target_year: int,
    max_years: int,
    current_year: StructuredFundDataBundle,
    years: Mapping[int, AnnualYearEvidence],
    source_documents: tuple[ReportSourceDocument, ...],
    anchors: tuple[ReportEvidenceAnchor | ChapterEvidenceAnchor, ...],
    data_gaps: tuple[ReportDataGap, ...],
    availability: EvidenceAvailability,
    cross_year_facts: tuple[CrossYearDerivedFact, ...],
    degradation: AnnualEvidenceDegradation,
    fallback_summary: AnnualEvidenceFallbackSummary,
)

AnnualYearEvidence(
    year: int,
    status: Literal["available", "missing", "unavailable", "failed_closed"],
    bundle: StructuredFundDataBundle | None,
    source_document_ids: tuple[str, ...],
    anchor_ids: tuple[str, ...],
    failure_category: AnnualReportSourceFailureCategory | None,
    fallback_used: bool,
    primary_failure_category: AnnualReportSourceFailureCategory | None,
    identity_status: DocumentIdentityStatus,
    data_gaps: tuple[ReportDataGap, ...],
    source_year_anchor_ids: tuple[str, ...],
)

AnnualEvidenceFallbackSummary(
    fallback_years: tuple[int, ...],
    fallback_year_count: int,
    primary_failure_categories: Mapping[int, AnnualReportSourceFailureCategory],
)
```

This shape is future design, not current code. Its intent is to keep the current-year bundle first-class while adding year-indexed annual evidence summaries. Implementation may choose names differently, but the contract must preserve these semantics:

- one canonical current-year bundle;
- one year-indexed availability record per requested year;
- source documents and anchors tied to fund code, report year, document identity, and repository/source metadata;
- explicit data gaps for missing or degraded years;
- cross-year derived facts computed from typed year summaries, not raw text;
- degradation semantics that tell writers/auditors what claims are disallowed.
- `ReportDataGap` is reused or extended for annual evidence gaps in MVP. `AnnualEvidenceGap` may be a local alias or typed specialization over `ReportDataGap`, but it must serialize into the same gap truth and must not create a third unrelated source of gap semantics.
- The current single-year `ReportEvidenceProjectionContext` must not be stretched into a misleading bundle-wide field. Multi-year projection needs per-year `source_failure_category`, `fallback_used`, `primary_failure_category`, and `document_identity_status`, with bundle-level summaries derived from those per-year fields.
- Current `DocumentIdentityStatus` mapping for MVP: successful same-fund annual reports map to `verified_annual_report`; optional year fail-closed source failures map to `mismatch` for `identity_mismatch` and `source_failed` for `schema_drift` / `integrity_error` / source failure states; unavailable or missing optional years map to `source_failed` with a `ReportDataGap`. Future statuses such as `same_fund_verified` and `cross_year_ambiguous` are acceptable future additions but not required before MVP implementation.

### 5. Cross-Year Derived Facts

Cross-year facts should be derived only from available typed yearly evidence. Examples of allowed future derived facts:

- fee schedule changes across years;
- turnover rate trend across available years;
- holdings concentration or industry allocation change where extracted facts and anchors exist;
- share change and holder structure trend;
- manager tenure/manager statement continuity where current extractors support it;
- annual performance/benchmark relation across available yearly bundles, subject to the same evidence and calculation audit rules as current Chapter 2.

Examples of disallowed future derived facts:

- style stability or manager consistency inferred from raw prose without typed anchors;
- cross-year causal claims not supported by public annual reports;
- five-year summaries that mix missing years into averages without gaps;
- claims from optional prior years after `schema_drift`, `identity_mismatch`, or `integrity_error`.

Conceptual shape:

```python
CrossYearDerivedFact(
    fact_id: str,
    requirement_key: str,
    fact_category: str,
    source_years: tuple[int, ...],
    source_year_anchor_ids: tuple[str, ...],
    source_fact_ids: tuple[str, ...],
    value: object,
    status: Literal["available", "degraded", "blocked"],
    data_gap_refs: tuple[str, ...],
    fallback_provenance: AnnualEvidenceFallbackSummary | None,
)
```

Every `CrossYearDerivedFact` must trace to its `source_years` and `source_year_anchor_ids`. A derived fact with no source-year anchors is not eligible for writer/auditor consumption. If any source year used repository fallback, the derived fact must carry a fallback provenance caveat so Chapter 5, Chapter 2, and auditors can avoid overstating confidence.

### 6. EvidenceAvailability Integration

Future `EvidenceAvailability` may include annual evidence tiers:

```python
EvidenceAvailability(
    available_report_years: tuple[int, ...],
    requested_report_years: tuple[int, ...],
    requirement_availability: Mapping[str, RequirementAvailability],
    data_tier_availability: Mapping[Literal["1Y", "3Y", "5Y"], AvailabilityStatus],
    year_availability: Mapping[int, AnnualYearAvailability],
    unavailable_requirements: tuple[str, ...],
    data_gaps: tuple[str, ...],
)

RequirementAvailability(
    requirement_key: Literal[
        "fee_trend",
        "turnover_trend",
        "holdings_trend",
        "manager_continuity",
        "performance_series",
    ] | str,
    status_by_tier: Mapping[Literal["1Y", "3Y", "5Y"], AvailabilityStatus],
    source_years_by_tier: Mapping[Literal["1Y", "3Y", "5Y"], tuple[int, ...]],
    blocked_years_by_tier: Mapping[Literal["1Y", "3Y", "5Y"], tuple[int, ...]],
    data_gap_refs: tuple[str, ...],
)
```

Semantics:

- `1Y` is available only when target year current evidence is available and identity-verified.
- `3Y` is available only when `requirement_availability[requirement].status_by_tier["3Y"]` is available for the relevant requirement, not merely when three calendar years were requested.
- `5Y` is available only when `requirement_availability[requirement].status_by_tier["5Y"]` is available with same-fund identity and typed anchors for that requirement.
- Availability is requirement-sensitive. For example, `fee_trend` may be available across more years than `holdings_trend` if holdings extraction failed or was not reviewed for a prior year. `turnover_trend`, `manager_continuity`, and `performance_series` may each have different source years and blocked years.
- Coarse `data_tier_availability` for `1Y` / `3Y` / `5Y` is a derived summary over `requirement_availability`, not an independent truth source. Consumers must inspect the requirement key before making a claim.
- `EvidenceAvailability` remains derived by Fund/Agent from typed annual evidence and `ChapterFactProjection`/annual summaries. It is not a ToolRegistry tool and not Service-constructed from prompt text.

### 7. Template And Agent Feed

Future template/Agent integration should follow these rules:

- Chapter ids remain `0-7`.
- Chapter 5 may use `cross_year_facts` only when `EvidenceAvailability` shows enough typed annual evidence for the specific claim. Otherwise it must keep an explicit degraded output, replacing the current synthetic `cross_period_comparison_missing` with a more precise year-level gap.
- Chapter 3 may use cross-period style/holdings/turnover evidence only when the evidence-conditional `must_not_cover` preconditions are satisfied. Missing or partial annual evidence must preserve cautious wording and next minimum verification question.
- Chapter 2 can use annual performance/cost breakdown inside public chapter id `2`; this does not authorize a public Ch2 split. If `performance_series` availability is partial, Chapter 2 must degrade the table to available anchored years or mark unavailable rows explicitly; it must not synthesize a five-year R=A+B-C table from missing years.
- Chapter 0 consumes Chapter 7 and accepted body chapters. It must not summarize unavailable cross-year conclusions as if they were accepted facts.
- Chapter 7 remains fail-closed on accepted body chapter readiness and final judgment consistency. It must not turn partial prior-year availability into a stronger final judgment.
- Agent/tool-loop consumes typed `AnnualEvidenceBundle`, `EvidenceAvailability`, `ChapterFactProjection`, and `CrossYearDerivedFact` inputs. It must not consume raw PDFs or raw five-year extracted text in prompts.
- `ChapterFactProvider` extension must be explicit before implementation. Acceptable MVP options are either an additive multi-year projection provider that consumes `AnnualEvidenceBundle`, or an extension of `ChapterFactProjection` that adds Chapter 5 cross-year facts while preserving public chapter ids `0-7`. The existing single-year synthetic `cross_period_comparison_missing` may be replaced or supplemented only through typed year-level gaps and `CrossYearDerivedFact` entries.
- Prior-year extraction should prefer annual-report-only summaries. It should avoid repeated NAV loading and bond drawdown calculations for every prior year unless a later gate explicitly requires multi-year NAV or drawdown evidence. Current-year NAV/drawdown behavior remains unchanged.

## Boundary Mapping

| Layer | Accepted future responsibility | Explicit boundary |
|---|---|---|
| UI | Express user intent such as target year and explicit refresh option through Service request fields | No repository, PDF/cache/source helper, Agent/Fund internals |
| Service | Declare annual evidence scope, build use-case/ExecutionContract semantics, choose report/quality strategy, pass typed request to Host/Agent or current transition Fund public API | No document loading, no cache/PDF/source helper access, no raw PDF prompt assembly, no `extra_payload` business params |
| Host | Lifecycle, deadline, cancel, terminal state, safe diagnostics/events | Does not inspect fund code/year/scope semantics, does not load documents |
| Agent | Own run/task/tool-loop in future implementation and consume typed annual evidence inputs | No direct dayu runtime dependency; no raw PDF prompt injection |
| Fund | Load annual reports through `FundDocumentRepository`, extract typed yearly bundles/summaries, derive annual evidence availability, gaps, anchors, cross-year facts, and audit semantics | No Service-owned source strategy bypass; no silent fail-open for fail-closed categories |
| Renderer / quality gate | Consume typed report/evidence outputs only if a later implementation gate wires them | No repository/PDF/cache/source helper access |

## Non-Goals And Rejections

- No implementation in this gate.
- No loading code, extractors, Agent runtime, provider runtime, or score-loop changes.
- No quarterly reports or interim reports.
- No prospectus or fund contract evidence scope.
- No raw five-year PDF text or raw five-year parsed text sent to LLM.
- No direct template truth replacement and no edit to `docs/fund-analysis-template-draft.md`.
- No public chapter id changes, no Ch2 split, no `0+9` / `0+10`.
- No new annual-report source strategy and no direct Eastmoney/EID API calls outside existing repository/source orchestration.
- No cache/PDF helper APIs exposed to Service/UI/Host/renderer/quality gate.
- No provider budget tuning or timeout attribution change.
- No chapter generation score-loop or golden/readiness mutation.
- No final judgment taxonomy change.

## Missing Years And Failure Semantics

| Situation | MVP design response |
|---|---|
| Target year available and identity-verified | Build current-year bundle; current-year chapters may proceed subject to existing contracts |
| Target year `not_found` / `unavailable` | Current-year report evidence is blocked; Service/Agent must return a typed blocked/fail-closed result |
| Target year `schema_drift` / `identity_mismatch` / `integrity_error` | Current-year report evidence is blocked; no fallback masking or generic missing-year downgrade |
| Optional prior year `not_found` | Record year-level `ReportDataGap` missing gap; requirement_availability degrades for requirements needing that year |
| Optional prior year `unavailable` | Record year-level `ReportDataGap` unavailable gap; requirement_availability degrades for requirements needing that year |
| Optional prior year `schema_drift` | Mark that year `failed_closed`; disallow dependent cross-year claims; current-year report may continue if no current-year impact and no future contract makes that year required |
| Optional prior year `identity_mismatch` | Mark that year `failed_closed`; same-source identity for that year's evidence is broken; disallow dependent cross-year claims; current-year report may continue under the same isolation rule |
| Optional prior year `integrity_error` | Mark that year `failed_closed`; do not use corrupted evidence; disallow dependent cross-year claims; current-year report may continue under the same isolation rule |
| Repository fallback succeeds for any year | Preserve per-year source/fallback metadata, include year in `fallback_years`, increment `fallback_year_count`, and retain `primary_failure_category` |
| Cross-year fact uses fallback year | Carry fallback provenance caveat in the `CrossYearDerivedFact`; do not block solely because fallback was used |
| All prior years missing/unavailable | Current-year report evidence may remain available, but Chapter 5 must not make cross-year change claims |
| Partial prior years available | Allow only claims whose `requirement_availability` tier and source-year anchors are satisfied; all other claims degrade |

## Residual Risks

1. Identity continuity across fund share classes, fund name changes, fund mergers, or converted products needs an implementation-time rule. MVP should require same `fund_code`; same-source `fund_id` mismatch is `identity_mismatch` for the affected year; cross-source `fund_id` comparison is explicitly out of scope.

2. Extractor reuse across multiple years may expose historical schema differences in annual reports. This is a source/contract issue, not a prompt issue; fail-closed categories must stay intact.

3. The future `AnnualEvidenceBundle` could duplicate `ReportEvidenceBundle` and `ChapterFactProjection` if implemented as a parallel truth source. The safer implementation slice should make it an additive wrapper over current-year bundle plus year summaries, with one canonical source for fact/anchor ids and `ReportDataGap` as the reusable gap truth.

4. Requirement-sensitive availability is more precise than coarse `1Y/3Y/5Y` flags. Implementation must make `requirement_availability` the source of truth and keep coarse tiers as derived summaries only.

5. Provider prompt budget may be affected by adding annual evidence summaries. This gate deliberately does not tune provider budget; future implementation must keep summaries bounded and use typed facts rather than raw text.

6. Chapter 5 contract needs explicit degrade wording and audit rules in a later typed contract implementation gate. Without that, writers may still over-claim from partial annual evidence.

7. Cross-year derived fact algorithms need per-fact tests and same-source anchor checks. Trend calculations should not be accepted without `source_years`, `source_year_anchor_ids`, and gap-aware denominators.

8. ChapterFactProvider extension needs a concrete implementation contract before coding. The accepted design only authorizes typed additions inside existing public chapter ids, not public chapter expansion or raw evidence injection.

9. Multi-year repository concurrency and per-year refresh controls may become performance needs. They remain deferred unless a later planning gate proves they are required and safe; this gate keeps provider budget and source strategy unchanged.

## Future Implementation Planning Slices

1. Scope contract slice: add typed `AnnualEvidenceScopeRequest` / policy types at the Service boundary and tests proving `target_year` required, required/optional disjointness, `max_years` range `1..5`, optional truncation from most distant first, deterministic year order, no `extra_payload`, and no repository access from Service.

2. Fund annual loader slice: implement a Fund-layer loader that iterates requested years through `FundDocumentRepository.load_annual_report()` and returns year-level availability records with fallback/failure metadata, same-`fund_code` validation, same-source `fund_id` consistency checks when present, and isolated optional-prior-year fail-closed semantics.

3. Yearly extraction slice: produce per-year `StructuredFundDataBundle` or narrower `AnnualYearEvidenceSummary` from parsed annual reports, reusing current annual-report extractors where valid and avoiding repeated prior-year NAV/drawdown work unless a later gate requires it.

4. Bundle/projection slice: introduce `AnnualEvidenceBundle` or equivalent additive wrapper, preserving current-year bundle, source/anchor/gap semantics, `ReportDataGap` reuse, per-year projection context fields, bundle-level `fallback_years` / `fallback_year_count`, and a canonical anchor id namespace.

5. Availability slice: derive `EvidenceAvailability` with `requirement_availability` from typed annual evidence, then derive coarse `1Y` / `3Y` / `5Y` summaries from that mapping rather than asserting them independently.

6. Cross-year facts slice: compute a minimal set of Chapter 5 facts with explicit `source_years`, `source_year_anchor_ids`, fallback provenance caveats, and gaps, starting with low-risk fields such as fee, turnover, share change, and holdings concentration where extraction support exists.

7. ChapterFactProvider and writer/auditor slice: define the ChapterFactProvider / ChapterFactProjection extension contract, update Chapter 5 writer/auditor contracts to consume typed cross-year facts and preserve degraded wording, and do not broaden public chapter ids.

8. Agent integration slice: pass typed annual evidence inputs into future Agent task graph without raw PDFs and without turning `EvidenceAvailability` into a tool.

9. Documentation/control sync slice: only after implementation acceptance, update design/control/README truth docs as current facts.

## Acceptance Criteria For This Design Gate

- The artifact distinguishes current code facts from future design.
- MVP annual scope is target year plus up to four prior annual reports, bounded by availability and same fund identity.
- `AnnualEvidenceScopeRequest` validation is explicit: `target_year` required, required/optional disjoint, `max_years` cap `1..5`, deterministic year order, invalid overlap/target omission fail at construction, optional years truncate from most distant first when needed.
- Service declares scope through explicit typed fields and does not cross into repository/PDF/cache/source helper access.
- Fund loading goes through `FundDocumentRepository.load_annual_report(year)` for every annual report.
- Missing optional years degrade only for `not_found` / `unavailable`; optional prior year `schema_drift` / `identity_mismatch` / `integrity_error` fail closed for that year's evidence and block dependent cross-year claims without killing the current-year report unless current year or a future required prior year is affected.
- Requirement-sensitive `requirement_availability` is the truth for `fee_trend`, `turnover_trend`, `holdings_trend`, `manager_continuity`, `performance_series`, and similar categories; coarse `1Y` / `3Y` / `5Y` is derived only.
- The future evidence bundle shape includes current-year bundle, year-indexed annual evidence, source documents, anchors, data gaps, per-year availability, cross-year derived facts, and explicit degradation semantics.
- The future evidence bundle preserves per-year source failure/fallback fields, bundle-level `fallback_years`, and `ReportDataGap` reuse.
- Cross-year derived facts include `source_years` and `source_year_anchor_ids`.
- Template/Agent feed preserves public chapter ids `0-7`, keeps Chapter 0/7 fail-closed on accepted body chapters, and consumes typed evidence rather than raw PDFs.
- Quarterly reports, prospectus/fund contract, provider budget, score-loop, Ch2 split, public chapter count changes, implementation, new source strategy, and direct cache/PDF APIs are explicitly deferred or rejected.

## Next Handoff

Controller should send this artifact to independent design reviewers. If accepted, the next implementation planning gate should start from the planning slices above and must not combine implementation with provider budget, score-loop, quarterly reports, or template public structure changes.

Suggested reviewer focus:

- whether `AnnualEvidenceScopeRequest` stays Service-safe and explicit;
- whether Fund loading preserves repository-only access and fallback taxonomy;
- whether `AnnualEvidenceBundle` avoids becoming a parallel truth source;
- whether Chapter 5 degradation semantics are strong enough to prevent cross-year over-claiming;
- whether the design leaks raw PDF/text or provider-budget concerns into this scope gate.

## Validation

- `rg -n "Worker Self-Check|Current Facts|Accepted Prior Inputs|Proposed Future Design|Boundary Mapping|Non-Goals|Residual Risks|Acceptance Criteria|Next Handoff|Secret Safety|raw five-year PDF|quarterly|score-loop|FundDocumentRepository|AnnualEvidenceScopeRequest|AnnualEvidenceBundle|schema_drift|identity_mismatch|integrity_error|chapter ids remain|0-7" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. Required sections, repository boundary, failure taxonomy, chapter id boundary, raw PDF rejection, quarterly rejection, score-loop deferral, and future bundle/request concepts are present.
- `rg -n "requirement_availability|fallback_years|source_year_anchor_ids|ReportDataGap|target_year|max_years|identity_mismatch" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md` — pass. Review-fix terms are present in the revised design and fix evidence artifacts.
- Readability self-check via `sed -n '1,260p' docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. The artifact separates current facts, accepted prior inputs, future design, boundary mapping, non-goals, failure semantics, residual risks, acceptance criteria, and handoff; proposed types are labeled future design.
- `git diff --check -- docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md` — pass after review-fix update.
- `git status --short -- docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md` — pass. Only the allowed design and fix evidence files are shown in this path-limited status.

## Secret Safety

This artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
