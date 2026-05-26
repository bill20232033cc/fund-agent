# Source Provenance Public Output Implementation Plan

> Date: 2026-05-27
> Role: AgentCodex planner
> Gate: `source provenance public-output implementation gate`
> Latest accepted checkpoint: `918f65d docs: accept source provenance design`
> Scope: implementation planning handoff only. No source code, tests, `docs/design.md`, `docs/implementation-control.md`, extraction evidence, commit, push, or PR changes are authorized in this planning step.

## Startup Packet Replay

| Item | Current state |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `coverage replacement / source provenance design accepted locally` |
| Next entry point | `source provenance public-output implementation gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | `918f65d docs: accept source provenance design` |
| Truth sources | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts |
| Evidence-chain only | `docs/reviews/`; `docs/archive/implementation-control-history-20260525.md` |

Allowed implementation scope after this plan is accepted:

- Add an additive public provenance projection owned by `fund_agent/fund`.
- Thread existing repository source metadata from `ParsedAnnualReport.metadata.source` through the already public extraction data path.
- Add source provenance fields to public extraction snapshot JSONL records and summary shape.
- Optionally expose the same projected provenance in report-evidence source document records if the change remains additive and does not change existing review-status semantics.
- Preserve score-compatible readers by treating missing provenance keys as legacy-compatible, conservative unknown metadata.
- Add focused unit/service tests only around projection, snapshot public output shape, report-evidence compatibility if touched, and no-regression boundaries.

Forbidden scope:

- No `FundDocumentRepository` source strategy change.
- No source helper, downloader, cache, source adapter, PDF direct access, or fallback eligibility rewrite.
- No renderer changes.
- No FQ0-FQ6 threshold or quality-gate policy changes.
- No default `fund-analysis analyze` / `checklist` behavior change.
- No Host/Agent/dayu package creation or execution-kernel work.
- No golden/baseline promotion.
- No fund-type, extractor, source-search, replacement-candidate, or document identity logic changes unless implementation proves unavoidable; if unavoidable, stop for controller decision before code.

## Accepted Design Constraints

The accepted design in `docs/design.md` section 6.1 requires public extraction snapshot / summary / score-compatible outputs to expose additive source provenance so maintainers can judge fallback-backed rows from public artifacts. The minimum stable fields are:

| Field | Stable domain / rule |
|---|---|
| `source_provenance_schema_version` | Constant string, initially `repository_source_provenance.v1`. |
| `source_strategy` | Constant public strategy label, initially `primary_then_fallback`; descriptive only. |
| `resolved_source_name` | Public source name from repository metadata: `eid`, `eastmoney`, or `null` when absent. |
| `fallback_used` | Boolean copied from repository metadata when available; absent metadata maps to `false` only when no fallback is evidenced. |
| `primary_failure_category` | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, or `null`. Current metadata does not expose this category, so fallback-backed rows must normally emit `null`. |
| `fallback_eligibility` | `eligible`, `fail_closed`, `not_applicable`, or `unknown_public_metadata_absent`. |
| `source_provenance_status` | `complete`, `incomplete`, or `not_applicable`. |
| `source_provenance_reason` | Short deterministic reason string; no raw exception dumps. |

Conservative rules:

- `fallback_used=true` plus missing, `null`, or unavailable `primary_failure_category` maps to `fallback_eligibility="unknown_public_metadata_absent"` and `source_provenance_status="incomplete"`.
- `fallback_used=true` plus `primary_failure_category in {"not_found", "unavailable"}` maps to `fallback_eligibility="eligible"` and `source_provenance_status="complete"`.
- `fallback_used=true` plus `primary_failure_category in {"schema_drift", "identity_mismatch", "integrity_error"}` maps to `fallback_eligibility="fail_closed"` and must remain non-clean even if downstream extraction or scoring succeeds.
- `fallback_used=false` and no primary failure maps to `fallback_eligibility="not_applicable"`, `source_provenance_status="not_applicable"`, and `primary_failure_category=null`.
- `source_provenance_status="not_applicable"` requires `fallback_eligibility="not_applicable"` and `fallback_used=false`.
- Missing legacy keys in old JSONL / score inputs must stay compatible and classify as conservative unknown/incomplete only when a consumer needs provenance accounting.
- If `AnnualReportSourceFailure.category` is not available at the public boundary, preserve unknown; do not infer from `resolved_source_name`, cache hit, successful extraction, report title, or source helper behavior.

## Code Inspection Findings

| Area | Current code fact | Planning consequence |
|---|---|---|
| Repository metadata | `fund_agent/fund/documents/models.py` has `AnnualReportSourceMetadata(source, source_url, ..., fallback_used)` but no primary failure category. | Public projection must preserve `primary_failure_category=null` for fallback-backed rows unless a later accepted gate extends metadata. |
| Source failures | `fund_agent/fund/documents/sources.py` defines `AnnualReportSourceFailure.category` and fail-closed taxonomy internally. | Do not reach into `sources.py` or source helper internals from Service/public output. |
| Extractor boundary | `FundDataExtractor.extract()` loads `ParsedAnnualReport`, then returns `StructuredFundDataBundle` without carrying `report.metadata.source`. | Minimal threading point is `StructuredFundDataBundle`: add a public/projection-ready provenance field or source metadata field populated from `report.metadata.source`. |
| Snapshot output | `fund_agent/fund/extraction_snapshot.py` serializes each `SnapshotRecord` via `asdict(record)` to `snapshot.jsonl`; summary is generated from records. | Add fields to `SnapshotRecord` only if all records get deterministic values; summary can aggregate per-fund provenance from records. |
| Score compatibility | `fund_agent/fund/extraction_score.py` consumes snapshot records mostly through required field helpers and ignores unknown extra keys. | Additive snapshot keys should not change scoring; add explicit legacy/missing-key tests. |
| Report evidence | `fund_agent/fund/report_evidence.py` already has `source_failure_category`, `fallback_allowed`, and `fallback_used`, but context is caller-provided and not derived from repository metadata. | Do not change review-status or scoring-ready semantics in this slice. If adding public provenance here, keep it additive and derive only from the same projection. |
| Report quality validation | `fund_agent/fund/report_quality_validation.py` already fail-closes `schema_drift`, `identity_mismatch`, `integrity_error` and treats unknown upstream failure as non-ready. | Existing semantics align with new public projection; tests should ensure new fields do not bypass these checks. |
| Service | `fund_agent/services/extraction_snapshot_service.py` only validates request and delegates to Fund. | Service should not access documents/source internals; it may remain unchanged unless tests need public output orchestration assertions. |

## Implementation Slice

Recommended minimal slice: **Fund-owned projection + DataBundle threading + snapshot public output**.

1. Add a Fund-level pure projection module.

   Suggested file: `fund_agent/fund/source_provenance.py`.

   Suggested public types:

   - `PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION: Final[str] = "repository_source_provenance.v1"`
   - `SourceStrategy = Literal["primary_then_fallback"]`
   - `ResolvedSourceName = Literal["eid", "eastmoney"]`
   - `PrimaryFailureCategory = Literal["not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error"]`
   - `FallbackEligibility = Literal["eligible", "fail_closed", "not_applicable", "unknown_public_metadata_absent"]`
   - `SourceProvenanceStatus = Literal["complete", "incomplete", "not_applicable"]`
   - `PublicSourceProvenance` frozen slotted dataclass with the eight accepted fields.

   `SourceStrategy` intentionally has a single Literal value in v1. It documents the current public strategy label without opening a policy surface for source ordering, fallback qualification, or repository behavior.

   Suggested functions:

   - `project_public_source_provenance(source_metadata: AnnualReportSourceMetadata | None, *, primary_failure_category: PrimaryFailureCategory | None = None) -> PublicSourceProvenance`
   - `source_provenance_to_dict(provenance: PublicSourceProvenance) -> dict[str, object]`
   - `default_public_source_provenance() -> PublicSourceProvenance`

   Rules:

   - Accept only explicit `primary_failure_category`; never import or inspect `AnnualReportSourceFailure`.
   - If `source_metadata is None`, emit `resolved_source_name=None`, `fallback_used=False`, `primary_failure_category=None`, `fallback_eligibility="not_applicable"`, `source_provenance_status="not_applicable"`, reason such as `source_metadata_absent_no_fallback_evidence`.
   - If `source_metadata.fallback_used is False`, emit not-applicable even when `resolved_source_name` is `eid` or `eastmoney`; do not infer fallback from source name alone.
   - If `source_metadata.fallback_used is True` and category is `None`, emit `unknown_public_metadata_absent` / `incomplete`.

2. Thread provenance through the structured bundle.

   Modify: `fund_agent/fund/data_extractor.py`.

   Preferred low-risk shape:

   - Add `source_provenance: PublicSourceProvenance` to `StructuredFundDataBundle`.
   - Use `field(default_factory=default_public_source_provenance)` so existing fixtures and call sites that are not testing provenance get a safe `NOT_APPLICABLE` public provenance by default. Do not expose `None` as the bundle value.
   - In `FundDataExtractor.extract()`, call `project_public_source_provenance(report.metadata.source)`.
   - Production `FundDataExtractor.extract()` must always explicitly populate the projected value from `ParsedAnnualReport.metadata.source`; the default factory is for tests, fakes, and non-provenance constructors only.
   - Do not add `AnnualReportSourceMetadata` itself to the public bundle unless tests show downstream code needs raw metadata. A projected dataclass is safer because it prevents Service/snapshot code from depending on repository internals.
   - Update only provenance-focused fake bundle builders to pass explicit provenance. Other fixtures should rely on the safe default rather than broad constructor edits.

   Stop condition:

   - If the default-field strategy cannot be implemented cleanly, requires `None`, or changes behavior for existing non-provenance tests, stop and return to controller. Do not silently introduce nullable provenance semantics that hide fallback-backed unknowns.

3. Add source provenance to snapshot records.

   Modify: `fund_agent/fund/extraction_snapshot.py`.

   Suggested `SnapshotRecord` additive fields:

   - `source_provenance_schema_version: str`
   - `source_strategy: str`
   - `resolved_source_name: str | None`
   - `fallback_used: bool`
   - `primary_failure_category: str | None`
   - `fallback_eligibility: str`
   - `source_provenance_status: str`
   - `source_provenance_reason: str`

   Implementation rule:

   - `SnapshotRecord` may define `NOT_APPLICABLE`-compatible defaults for the eight additive fields, but production snapshot creation must go through `build_snapshot_records(...)` / `_snapshot_record(...)`, where values are fully populated from `bundle.source_provenance`.
   - `_snapshot_record(...)` should copy values from `bundle.source_provenance` into every field-level record, so public JSONL consumers can classify each row without joining another file.
   - Legacy JSONL compatibility is handled by downstream score readers ignoring extra keys and tolerating missing provenance keys; it is not handled by emitting partial or nullable bundle provenance.
   - `write_snapshot_summary(...)` should add a separate `## Source Provenance` section with exactly these columns:

     `fund_code`, `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`.

     For not-applicable rows, print `resolved_source_name` as a null-equivalent stable token such as `null`, `fallback_used` as `false`, `fallback_eligibility` as `not_applicable`, and `source_provenance_status` as `not_applicable`. Aggregate from the first snapshot record per succeeded fund. Failed funds without snapshot records are omitted in v1, and the section must include a short note that failed-fund provenance is out of scope for v1.
   - Do not change `SNAPSHOT_FIELD_ORDER`, field counts, selected fund logic, or errors JSONL semantics.

4. Preserve score-compatible output.

   Inspect/modify only if tests fail: `fund_agent/fund/extraction_score.py`.

   Expected result:

   - No production scoring logic change is needed because extra snapshot keys should be ignored.
   - Add tests proving old snapshot rows without provenance keys still score/parse as before.
   - Score-compatible means deterministic no-change for `score.json` key set and all FQ0-FQ6 gate-sensitive output. Add explicit assertions comparing the `score.json` top-level keys and gate-consumed fields before/after additive snapshot provenance.
   - If a future summary of provenance in `score.json` is desired, defer it; this gate asks for score-compatible public output, not new scoring policy.

5. Optional report-evidence additive projection only if bounded.

   Candidate files: `fund_agent/fund/report_evidence.py`, `fund_agent/fund/report_quality_validation.py`, `tests/fund/test_report_evidence.py`, `tests/fund/test_report_quality_validation.py`.

   Default recommendation: do not touch this in the first implementation slice unless plan review requires it. Current report-evidence `source_failure_category` is caller-provided and enforces different scoring-ready semantics. Mixing repository public provenance into it risks changing baseline review logic.

   If touched, only add a nested `source_provenance` or equivalent fields to `ReportSourceDocument` as additive metadata, with validation limited to enum shape and not used to derive `review_status`, `fallback_allowed`, or `source_failure_category`.

## Exact Files to Inspect / Modify

Implementation files:

- Add: `fund_agent/fund/source_provenance.py`
- Modify: `fund_agent/fund/data_extractor.py`
- Modify: `fund_agent/fund/extraction_snapshot.py`
- Inspect, modify only if needed for compatibility tests: `fund_agent/fund/extraction_score.py`
- Inspect, avoid modifying in first slice unless review requires: `fund_agent/fund/report_evidence.py`
- Inspect, avoid modifying in first slice unless report-evidence shape changes: `fund_agent/fund/report_quality_validation.py`
- Documentation sync after tests if public output shape changes: `fund_agent/fund/README.md`, `tests/README.md`

Tests:

- Add: `tests/fund/test_source_provenance.py`
- Modify: `tests/fund/test_data_extractor.py`
- Modify: `tests/fund/test_extraction_snapshot.py`
- Modify: `tests/services/test_extraction_snapshot_service.py` only if request/result shape changes; expected no change.
- Modify: `tests/fund/test_extraction_score.py` for legacy missing-key compatibility.
- Modify only if optional report-evidence slice is touched: `tests/fund/test_report_evidence.py`, `tests/fund/test_report_quality_validation.py`.
- Run adjacent no-regression tests: `tests/fund/test_quality_gate.py`, `tests/fund/test_quality_gate_integration.py`, `tests/services/test_extraction_score_service.py`, `tests/services/test_quality_gate_service.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py`.

## Test Plan

Projection unit tests in `tests/fund/test_source_provenance.py`:

- Primary success / no metadata fallback evidence:
  - `source_metadata=None` returns not-applicable, fallback false, category null.
  - EID metadata with `fallback_used=False` returns not-applicable.
- Fallback metadata gap:
  - Eastmoney metadata with `fallback_used=True` and no category returns `unknown_public_metadata_absent`, status `incomplete`, category null, never eligible.
- Eligible mapping:
  - Explicit fake categories `not_found` and `unavailable` with `fallback_used=True` return `eligible`, status `complete`.
- Fail-closed mapping:
  - Explicit fake categories `schema_drift`, `identity_mismatch`, `integrity_error` with `fallback_used=True` return `fail_closed`, status `incomplete` or equivalent non-clean status, never eligible.
- Not-applicable consistency:
  - Every `source_provenance_status="not_applicable"` fixture asserts `fallback_eligibility="not_applicable"` and `fallback_used is False`.
- Do not infer:
  - `source="eastmoney"` with `fallback_used=False` remains not-applicable; source name alone does not imply fallback.

Data extractor tests in `tests/fund/test_data_extractor.py`:

- Constructing `StructuredFundDataBundle` without explicit provenance yields the safe `NOT_APPLICABLE` default object, never `None`.
- Fake repository returns `ParsedAnnualReport.metadata.source=AnnualReportSourceMetadata(source="eid", fallback_used=False)` and bundle carries not-applicable public provenance.
- Fake repository returns `source="eastmoney", fallback_used=True` and bundle carries `unknown_public_metadata_absent`.
- NAV unavailable downgrade remains unchanged and does not affect source provenance.

Snapshot tests in `tests/fund/test_extraction_snapshot.py`:

- `build_snapshot_records()` required schema test includes the eight additive fields.
- All records for a fund carry identical provenance copied from the bundle.
- Snapshot records built through the production `build_snapshot_records()` / `_snapshot_record()` path are fully populated from `bundle.source_provenance`; dataclass defaults, if present, are only `NOT_APPLICABLE`-compatible safety defaults.
- JSONL public shape contains provenance fields.
- Summary contains a separate `## Source Provenance` table with exactly `fund_code`, `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`.
- Summary prints not-applicable rows consistently as `resolved_source_name=null`, `fallback_used=false`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`, with deterministic reason text.
- Failed funds without records are omitted from the v1 Source Provenance table and the summary includes a note that failed-fund provenance is out of scope for v1.
- Summary changes do not alter selected count, record count, field order, errors JSONL, or known 004393 note behavior.

Score compatibility tests in `tests/fund/test_extraction_score.py`:

- Existing snapshot rows without provenance keys still parse and score unchanged.
- Snapshot rows with provenance keys produce the same field/fund scores as identical rows without those keys.
- `score.json` top-level key set remains unchanged.
- FQ0-FQ6 gate-sensitive output remains unchanged: no new required provenance keys, no changed status aggregation, no changed `field_scores`, `fund_scores`, `fund_quality`, `field_applicability_decisions`, `score_applicability_issues`, `failed_funds`, `golden_set`, or `correctness` semantics from additive provenance alone.

Optional report-evidence tests only if touched:

- `ReportSourceDocument` additive provenance fields serialize through `asdict` without changing existing `source_failure_category`, `fallback_allowed`, `fallback_used`, or `review_status`.
- Existing fail-closed and unknown-upstream validation remains unchanged.

No-regression tests:

- Renderer tests are not modified; run a representative subset only if optional report-evidence changes touch dataclass constructor call sites.
- `tests/services/test_fund_analysis_service.py` and `tests/ui/test_cli.py` should prove default `analyze` / `checklist` behavior is unchanged.

## Validation Commands

Focused implementation tests:

```bash
uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
```

Adjacent compatibility tests:

```bash
uv run pytest tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_quality_gate_service.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Optional if report-evidence shape is touched:

```bash
uv run pytest tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py tests/fund/template/test_renderer.py
```

Static and whitespace checks:

```bash
uv run ruff check .
git diff --check
```

Bounded CLI evidence:

- Do not run extraction evidence during implementation planning.
- After implementation and review acceptance only, run bounded public CLI evidence for `110020 --report-year 2024` and `017641 --report-year 2024` under ignored report paths.
- Evidence classification must use only public provenance fields. If both remain `unknown_public_metadata_absent`, the rows stay excluded from clean denominator.

## Risk Matrix

| Risk | Severity | Trigger | Mitigation |
|---|---|---|---|
| Metadata gap is misread as eligible fallback | High | `fallback_used=true` but category missing | Projection hard-codes `unknown_public_metadata_absent`; tests assert never eligible. |
| Service or snapshot reaches into source internals | High | Import from `documents/sources.py` or downloader/cache helpers outside Fund projection boundary | Projection consumes only `AnnualReportSourceMetadata` or explicit category parameter; Service remains delegate-only. |
| Bundle provenance field causes broad fixture churn | Low | Many tests construct `StructuredFundDataBundle` directly | Use `field(default_factory=default_public_source_provenance)` so non-provenance fixtures keep safe not-applicable behavior; only provenance-focused tests pass explicit values. |
| Snapshot additive keys break score readers | Medium | Score code assumes exact key set | Add legacy and additive-key compatibility tests; avoid changing scoring policy. |
| `score.json` shape changes accidentally | High | Provenance is propagated into score output or FQ0-FQ6 gate inputs | Assert `score.json` top-level key set and gate-sensitive sections remain unchanged. |
| Report-evidence semantics accidentally change | High | Reusing public provenance to derive `source_failure_category` / `fallback_allowed` | Keep report-evidence out of first slice unless explicitly required; if touched, additive only. |
| Summary output becomes noisy or gate-sensitive | Low | Summary starts implying baseline eligibility | Use deterministic terse status/reason; do not mention promotion readiness. |
| Fail-closed source categories become hidden by downstream success | High | Score/quality gate passes despite provenance fail-closed | Projection preserves `fail_closed`; future evidence gate must classify from provenance, not downstream success. |

## Stop Conditions

Stop and return to controller before implementation if any of the following occurs:

- The implementation needs to modify `FundDocumentRepository`, `documents/sources.py`, downloader/cache/source adapter behavior, or fallback eligibility decisions.
- Public provenance cannot be derived from `ParsedAnnualReport.metadata.source` without reading private cache/PDF/source-helper internals.
- A real `AnnualReportSourceFailure.category` must be threaded through persistent metadata to meet acceptance. That is a separate source metadata schema gate, not this public-output slice.
- `StructuredFundDataBundle.source_provenance` cannot use a safe `NOT_APPLICABLE` default factory cleanly, requires exposing `None`, or changes behavior for fixtures that do not test provenance.
- `fund_type`, extractor logic, renderer, FQ0-FQ6, `analyze`, `checklist`, Host/Agent/dayu, golden/baseline promotion, or replacement-candidate selection becomes necessary.
- Tests show snapshot additive keys alter scoring, `score.json` key set, quality gate, CLI defaults, or renderer behavior beyond public-output metadata shape.
- Existing design/control truth conflicts with the code-level plan; update requires controller-approved design/control gate first.

## Recommended Implementation Slice

Implement one narrow slice:

1. `fund_agent/fund/source_provenance.py` with deterministic public projection and unit tests.
2. `StructuredFundDataBundle.source_provenance` with a safe not-applicable default factory; production `FundDataExtractor.extract()` explicitly populates it from `ParsedAnnualReport.metadata.source`.
3. Add the eight public provenance fields to `SnapshotRecord` and JSONL through the production `build_snapshot_records()` / `_snapshot_record()` path.
4. Add a separate `## Source Provenance` summary table with the exact v1 columns and failed-fund out-of-scope note.
5. Add compatibility tests proving `score.json` key set, FQ0-FQ6 gate-sensitive output, and default CLI/service behavior do not require or reinterpret provenance.

Defer report-evidence public provenance until the snapshot path is accepted, unless plan review explicitly requires it in the same gate.
