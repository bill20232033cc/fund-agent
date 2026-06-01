# Source Provenance Primary Failure Category Propagation Design Plan

> Date: 2026-05-27
> Role: AgentCodex planning worker
> Gate: `source provenance primary-failure-category propagation design gate`
> Latest accepted checkpoint: `722cc6c docs: accept source provenance evidence classification`
> Scope: design / implementation plan artifact only. No source code, tests, `docs/design.md`, `docs/implementation-control.md`, evidence reruns, commit, push, PR, or next-gate entry is authorized in this planning step.

## Startup Packet Replay

| Item | Current state |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `source provenance bounded evidence classification accepted locally` |
| Next entry point | `source provenance primary-failure-category propagation design gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | `722cc6c docs: accept source provenance evidence classification` |
| Truth sources | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts |
| Evidence-chain only | `docs/reviews/`; `docs/archive/implementation-control-history-20260525.md` |

Startup Packet constraints replayed:

- Current truth is limited to `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / current gate, and accepted artifacts.
- Architecture remains `UI -> Service -> Host -> Agent`; the current deterministic production path is still Service calling `fund_agent/fund` Agent-layer fund capability directly.
- No independent Host/Agent gate is open. Do not create `fund_agent/host` or `fund_agent/agent`; any future Host must use `dayu.host`, and any future Agent execution kernel must use `dayu.engine`.
- This gate is design/plan/review first. It may decide whether and how to persist or publicly project repository primary failure category into public source provenance outputs.
- Durable baseline/golden promotion remains blocked. `110020`, `017641`, FOF, bond baseline-blocking, and reviewed-fact blockers remain open.

`init-agents` note: the skill instructions were read. Because this handoff explicitly assigns the current process as a role-scoped planning worker, not controller, this artifact does not dispatch tmux review workers or enter another gate. A later controller can use this plan as the handoff basis.

## First Principles

Fallback eligibility is a property of the repository source strategy decision, not a property of any later successful artifact.

The only same-source evidence for whether fallback was eligible is the primary source failure category captured when `FundDocumentRepository` tries the primary annual-report source and decides whether a fallback source is allowed. Successful PDF extraction, populated structured fields, score output, quality status, renderer output, or source name alone are all downstream or indirect signals. They can prove that some later path ran, but they cannot prove why fallback was permitted.

Therefore the public classification rule must be:

- `fallback_used=true` plus repository primary failure category `not_found` or `unavailable` means public fallback classification may be `eligible`.
- `fallback_used=true` plus repository primary failure category `schema_drift`, `identity_mismatch`, or `integrity_error` means public fallback classification must be `fail_closed`, even if a fallback-backed extraction later succeeds.
- `fallback_used=true` plus missing public primary failure category remains `unknown_public_metadata_absent`.
- `fallback_used=false` remains `not_applicable` for fallback eligibility.

This design deliberately treats missing category as durable absence, not a recoverable inference problem. Recovery requires the repository metadata owner to persist the category at the source-decision boundary.

## Current Code Facts

| Area | Current fact | Consequence |
|---|---|---|
| Source taxonomy | `fund_agent/fund/documents/sources.py` currently defines `AnnualReportSourceFailureCategory` with `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. | The taxonomy is correct, but the later implementation should move the type owner to `fund_agent/fund/documents/models.py` next to `AnnualReportSourceName` so metadata and source orchestration share one import-safe public model type. |
| Fallback strategy | `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()` allows fallback only after `not_found` / `unavailable`; fail-closed categories raise `AnnualReportSourceFallbackBlockedError`. | Strategy semantics are already correct and must not be changed by this gate. |
| Successful fallback metadata | `_mark_fallback_used()` currently writes only `fallback_used=True` into `AnnualReportSourceMetadata`. | Public output cannot distinguish eligible fallback from unknown because the primary category is lost before metadata persistence. |
| Public metadata model | `AnnualReportSourceMetadata` currently stores source identity fields and `fallback_used`; it has no primary failure category field. | It does not currently have enough state for public provenance classification. |
| Public projection | `fund_agent/fund/source_provenance.py` can already project eligible/fail-closed/unknown when an explicit `primary_failure_category` is provided, but production calls do not pass one. | Minimal implementation should source the category from `AnnualReportSourceMetadata`, not from downstream callers. |
| Structured bundle | `StructuredFundDataBundle.source_provenance` already has a safe `not_applicable` default and production population from `ParsedAnnualReport.metadata.source`. | Preserve this boundary; only make projection consume richer metadata. |
| Snapshot output | `snapshot.jsonl` already emits the eight additive source provenance fields and `summary.md` emits a `Source Provenance` table. | Keep output schema stable; change field values only when public metadata now contains the category. |
| Score / quality | Existing score tests assert additive provenance does not change score output; quality output cannot prove fallback eligibility. | Add no score policy or FQ0-FQ6 behavior changes. |

## Public Contract

Recommended contract: **persist the repository primary failure category as optional source metadata and project it through the existing public provenance fields.**

### Source Metadata Owner

`fund_agent/fund/documents/models.py::AnnualReportSourceMetadata` should own the durable optional field:

```text
primary_failure_category: AnnualReportSourceFailureCategory | None
```

Field meaning:

- Present only when a source-chain success used fallback because an earlier primary source failed.
- Value is the primary source failure category that caused the fallback attempt to be allowed or, for defensive malformed historical states, the category attached to a fallback-backed result.
- Absent for primary-source success, old cache rows, tests/fixtures that did not model provenance, and any metadata path where the repository did not observe a primary failure.
- It must not store raw exception messages, source helper payloads, cache paths, PDF paths, or private source internals.

The metadata field is owned by the document repository/source layer because that is the only layer where the fallback decision and source failure category are logically and temporally adjacent.

### Projection

`fund_agent/fund/source_provenance.py::project_public_source_provenance()` should prefer the category found on `AnnualReportSourceMetadata`.

Recommended function shape:

```text
project_public_source_provenance(
    source_metadata: AnnualReportSourceMetadata | None,
    *,
    primary_failure_category: PrimaryFailureCategory | None = None,
) -> PublicSourceProvenance
```

Compatibility behavior:

- Keep the explicit keyword argument as a test/development override if it already exists.
- Use exact precedence:

  ```text
  effective_category = (
      source_metadata.primary_failure_category
      if source_metadata is not None and source_metadata.primary_failure_category is not None
      else primary_failure_category
  )
  ```

- Metadata non-`None` category wins over the keyword argument. Metadata `None` category falls back to the keyword argument only for test/development override compatibility.
- If metadata lacks the field, behavior remains exactly as today: `fallback_used=true` maps to `unknown_public_metadata_absent`.
- Invalid/deserialized unknown category values should normalize to `None` and therefore remain unknown; do not emit a new public enum value without a schema gate.

Projection precedence truth table:

| `source_metadata` | `source_metadata.primary_failure_category` | kwarg `primary_failure_category` | `effective_category` | Required test |
|---|---|---|---|---|
| `None` | N/A | `not_found` | `not_found` | kwarg fallback remains available for pure projection tests. |
| present | `None` | `unavailable` | `unavailable` | metadata missing category may use test/development override. |
| present | `schema_drift` | `not_found` | `schema_drift` | metadata wins; kwarg cannot recover fail-closed metadata. |
| present | `not_found` | `identity_mismatch` | `not_found` | metadata wins; kwarg cannot make eligible metadata fail-closed. |
| present | `None` | `None` | `None` | missing category remains `unknown_public_metadata_absent` when fallback was used. |

Classification rules remain the existing public contract:

| Input state | Public output |
|---|---|
| `source_metadata is None` | `fallback_used=false`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`, reason `source_metadata_absent_no_fallback_evidence` |
| `fallback_used=false` | `primary_failure_category=null`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`, reason `primary_source_success_no_fallback` |
| `fallback_used=true`, category missing | `primary_failure_category=null`, `fallback_eligibility=unknown_public_metadata_absent`, `source_provenance_status=incomplete`, reason `fallback_used_primary_failure_category_absent` |
| `fallback_used=true`, category `not_found` / `unavailable` | `primary_failure_category=<category>`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, reason `fallback_used_primary_failure_category_eligible` |
| `fallback_used=true`, category `schema_drift` / `identity_mismatch` / `integrity_error` | `primary_failure_category=<category>`, `fallback_eligibility=fail_closed`, `source_provenance_status=incomplete`, reason `fallback_used_primary_failure_category_fail_closed` |

### Bundle And Public Outputs

`StructuredFundDataBundle.source_provenance` remains the only public provenance object that snapshot code consumes.

Production flow after implementation:

```text
AnnualReportSourceOrchestrator
  -> AnnualReportSourceResult.metadata.primary_failure_category
  -> FundDocumentRepository / parsed report metadata
  -> FundDataExtractor.extract()
  -> project_public_source_provenance(report.metadata.source)
  -> StructuredFundDataBundle.source_provenance
  -> extraction_snapshot.SnapshotRecord additive provenance fields
  -> snapshot.jsonl and summary.md Source Provenance table
```

Snapshot JSONL behavior:

- Keep the existing eight additive fields unchanged:
  `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`.
- Every field-level record for the same bundle should copy the same public provenance values.
- For old metadata, `primary_failure_category` stays `null` and fallback-backed rows stay `unknown_public_metadata_absent`.

Summary behavior:

- Keep the existing separate `## Source Provenance` table.
- Recommended later minor addition: include `primary_failure_category` in the table only if an accepted implementation plan chooses to revise summary shape. It is not necessary for machine classification because JSONL already carries the field.
- If the table shape is kept unchanged, tests must still assert the summary classification changes through `fallback_eligibility`, `source_provenance_status`, and `source_provenance_reason`.

## Minimal Data Model Extension

`AnnualReportSourceMetadata` currently does **not** have enough state.

Minimal extension:

- Add optional `primary_failure_category` to `AnnualReportSourceMetadata`.
- Move `AnnualReportSourceFailureCategory` from `fund_agent/fund/documents/sources.py` to `fund_agent/fund/documents/models.py`, next to `AnnualReportSourceName`. `sources.py` must import the type from `models.py`; `models.py` must not import from `sources.py`. Do not create a local duplicate alias in either module.
- Add the field to `to_dict()` with exact key `"primary_failure_category"`, and update `from_dict()` to read the same key.
- Validate/normalize through `_normalize_failure_category()` following the existing `_normalize_source_name()` pattern so only the five accepted categories survive deserialization.
- Preserve old metadata compatibility: missing key deserializes as `None`; existing cache rows and parsed reports remain readable.
- Do not bump public source provenance schema version for this value-populating change because the public field already exists. Cache schema version bump is not required if the deserializer tolerates missing field; a bump may be considered only if maintainers want to force cache refresh for evidence reruns. This plan recommends no automatic cache invalidation.

Minimal source-chain write:

- Change `_mark_fallback_used()` to this exact signature:

  ```text
  _mark_fallback_used(
      result: AnnualReportSourceResult,
      *,
      primary_failure_category: AnnualReportSourceFailureCategory | None = None,
  ) -> AnnualReportSourceResult
  ```

  It should set both `fallback_used=True` and `primary_failure_category=<first/primary failure category>` when a category is provided.
- In `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()`, when `failures` is non-empty and a later source succeeds, pass `failures[0].category` into the metadata replacement.
- Preserve fail-closed behavior: code paths for `schema_drift`, `identity_mismatch`, and `integrity_error` still raise before fallback success. Tests may construct metadata with fail-closed categories defensively, but production source-chain should not create a successful fallback after fail-closed primary failure.

Why first failure:

- Current v1 public strategy is `primary_then_fallback`; the bounded case of interest is the primary source failure before fallback success.
- Multi-source chains beyond primary + fallback are out of scope. If introduced later, open a provenance-chain schema gate instead of overloading `primary_failure_category`.

## Implementation Files For Later Gate

Implementation files:

- `fund_agent/fund/documents/models.py`
  - Move/own `AnnualReportSourceFailureCategory` here next to `AnnualReportSourceName`.
  - Add `primary_failure_category: AnnualReportSourceFailureCategory | None = None` to `AnnualReportSourceMetadata`.
  - Update docstring, dataclass field, `to_dict()` key `"primary_failure_category"`, `from_dict()`, and `_normalize_failure_category()` following `_normalize_source_name()` style.
  - Do not import `sources.py`; keep models import-safe for cache/repository users.
- `fund_agent/fund/documents/sources.py`
  - Import `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models`.
  - Remove the local `AnnualReportSourceFailureCategory` alias.
  - Update `_mark_fallback_used(result, *, primary_failure_category: AnnualReportSourceFailureCategory | None = None)` to preserve the primary failure category in metadata.
  - Update `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()` success-after-failure path to pass `failures[0].category`.
  - Do not alter `_FALLBACK_ELIGIBLE_CATEGORIES`, exception mapping, source ordering, downloader, source helpers, or fail-closed raises.
- `fund_agent/fund/source_provenance.py`
  - Compute `effective_category = source_metadata.primary_failure_category if source_metadata is not None and source_metadata.primary_failure_category is not None else primary_failure_category`.
  - Use `effective_category` for eligible/fail-closed/unknown classification.
  - Keep stable public enums and reason codes.
  - Keep missing category as `unknown_public_metadata_absent`.
- `fund_agent/fund/data_extractor.py`
  - Ideally no code change if projection reads metadata. If touched, only keep the existing `project_public_source_provenance(report.metadata.source)` production call.
- `fund_agent/fund/extraction_snapshot.py`
  - Ideally no code change because fields already exist. If summary includes category later, change only the `Source Provenance` table and tests.

Tests:

- `tests/fund/documents/test_annual_report_sources.py`
  - `AnnualReportSourceOrchestrator` fallback success after `not_found` stores `primary_failure_category="not_found"`.
  - `AnnualReportSourceOrchestrator` fallback success after `unavailable` stores `primary_failure_category="unavailable"`.
  - Fail-closed categories still raise `AnnualReportSourceFallbackBlockedError`; no fallback source is called and no successful metadata is produced.
- `tests/fund/documents/test_cache.py`
  - `AnnualReportSourceMetadata.to_dict()` / `from_dict()` round-trips the new field.
  - `to_dict()` includes the exact `"primary_failure_category"` key.
  - Old metadata JSON without the field deserializes with `primary_failure_category is None`.
  - Unknown/invalid category in cached JSON degrades to `None` or makes source metadata unavailable according to current cache error policy; prefer degrade-to-`None` for compatibility.
- import-safety verification
  - A focused test or lint-level import check should import `AnnualReportSourceMetadata`, `AnnualReportSourceName`, and `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models` without importing `fund_agent.fund.documents.sources`.
  - `sources.py` may import the model type; `models.py` must remain independent of source orchestration classes and exceptions.
- `tests/fund/documents/test_repository.py`
  - Repository round-trip preserves metadata `primary_failure_category` through PDF/parsed cache paths if existing tests cover metadata persistence.
- `tests/fund/test_source_provenance.py`
  - Metadata-owned eligible categories classify as `eligible`.
  - Metadata-owned fail-closed categories classify as `fail_closed`.
  - Fallback with missing metadata category remains `unknown_public_metadata_absent`.
  - Metadata-owned category wins over kwarg: metadata `schema_drift` plus kwarg `not_found` stays `fail_closed`.
  - Kwarg fallback still works when metadata category is `None`: metadata fallback row with kwarg `unavailable` classifies `eligible`.
- `tests/fund/test_data_extractor.py`
  - Fake repository returning `ParsedAnnualReport.metadata.source` with fallback category produces bundle `source_provenance.primary_failure_category` and eligible classification.
  - Existing default bundle provenance remains `not_applicable`.
- `tests/fund/test_extraction_snapshot.py`
  - Snapshot JSONL copies metadata-derived `primary_failure_category` to every row.
  - Summary classification row reflects eligible/fail-closed/unknown without relying on score.
- `tests/fund/test_extraction_score.py`
  - `score.json` and FQ0-FQ6 gate-sensitive outputs remain unchanged when only provenance values change.
  - Legacy snapshot rows without provenance keys remain score-compatible if current readers support that path.
- `tests/ui/test_cli.py` or service tests only if the later implementation modifies CLI/service-visible behavior. Default recommendation: no CLI/service code change, so no new CLI behavior tests beyond no-change coverage if already present.

Documentation updates after implementation approval:

- `fund_agent/fund/README.md`: update the public source provenance note to state `primary_failure_category` is populated only when repository metadata persisted the primary source failure category; old metadata remains unknown.
- `docs/design.md`: update section 6.1 current design to say `AnnualReportSourceMetadata` now records optional `primary_failure_category` and the public projection consumes it.
- `docs/implementation-control.md`: only the controller should update Startup Packet/current gate ledger after plan/review/implementation acceptance.
- `tests/README.md`: update provenance/document cache test descriptions if test coverage changes.
- Root `README.md`: not required unless public CLI command shape or user workflow text changes. This plan recommends no root README update.

## Negative Tests Required

The later implementation gate must include negative tests for these exact risks:

| Risk | Required assertion |
|---|---|
| Missing category becomes falsely eligible | `AnnualReportSourceMetadata(source="eastmoney", fallback_used=True, primary_failure_category=None)` still projects `fallback_eligibility="unknown_public_metadata_absent"` and `source_provenance_status="incomplete"`. |
| Fail-closed recovered by fallback success | Metadata with `fallback_used=True` and `primary_failure_category in {"schema_drift", "identity_mismatch", "integrity_error"}` projects `fallback_eligibility="fail_closed"` even if bundle/snapshot fields are otherwise populated. |
| Source chain fail-closed regression | A primary `schema_drift`, `identity_mismatch`, or `integrity_error` prevents fallback source invocation and raises `AnnualReportSourceFallbackBlockedError`. |
| Eligible inferred from success | Successful extraction, score completion, or quality `warn` / `pass` cannot change `unknown_public_metadata_absent` to `eligible` when the public category is absent. |
| Eligible inferred from source name | `source="eastmoney"` with `fallback_used=False` remains `not_applicable`; `source="eastmoney"` with `fallback_used=True` and no category remains unknown. |
| Old metadata compatibility | Old JSON/cache metadata without `primary_failure_category` remains readable and projects unknown only when fallback was used. |
| FQ0-FQ6 no change | Adding/populating source provenance changes no field score, fund score, correctness, quality gate status, issue severity, or FQ0-FQ6 outputs. |
| Renderer/default behavior no change | Default `fund-analysis analyze`, `fund-analysis checklist`, renderer output, and report-writing behavior remain unchanged unless a later accepted plan explicitly expands scope. |

## Bounded Evidence Rerun Expectations

Do not run evidence in this design gate.

After implementation, code review, and controller acceptance, a bounded evidence gate may rerun only the accepted public CLI path for:

- `110020` / 2024
- `017641` / 2024

Expected command family, with new run ids chosen by the controller:

```bash
uv run fund-analysis extraction-snapshot --run-id <new-run-id> --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/<new-run-id>
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/<new-run-id>/snapshot.jsonl --errors-path reports/extraction-snapshots/<new-run-id>/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/<new-run-id>
uv run fund-analysis quality-gate --score-path reports/scoring-runs/<new-run-id>/score.json --output-dir reports/quality-gate-runs/<new-run-id>
```

Repeat for `017641` with its own run id.

Classification expectations:

- If public snapshot JSONL shows `fallback_used=true`, `primary_failure_category in {"not_found", "unavailable"}`, and `fallback_eligibility="eligible"`, then provenance is no longer the blocker. The row still needs public quality output to avoid `quality_blocked_after_provenance`.
- If public snapshot JSONL still shows `primary_failure_category=null`, terminal state remains `provenance_unknown_public_metadata_absent`.
- If public snapshot JSONL shows a fail-closed category, terminal state is `provenance_fail_closed` regardless of extraction/score/quality success.
- Every rerun row must record `promotion_disposition=not_promoted` unless a separate later gate explicitly authorizes durable baseline/golden promotion.
- Generated `reports/` outputs remain ignored scratch evidence unless a later controller explicitly promotes a small tracked summary artifact.

## Verifier Matrix

| Verifier | Command / check | Required result |
|---|---|---|
| Source metadata unit tests | `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q` | Fallback eligible categories persist; fail-closed source chain remains blocked; old metadata remains compatible. |
| Public projection tests | `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py -q` | Metadata-derived categories classify deterministically; missing category remains unknown. |
| Snapshot output tests | `uv run pytest tests/fund/test_extraction_snapshot.py -q` | JSONL has stable eight provenance fields and category values are copied to all rows; summary remains deterministic. |
| Score no-change tests | `uv run pytest tests/fund/test_extraction_score.py -q` | Additive/populated provenance does not change score or FQ0-FQ6-sensitive outputs. |
| Adjacent quality tests | `uv run pytest tests/fund/test_report_quality_validation.py tests/fund/test_report_writing_audit.py -q` | Existing fallback/fail-closed and report audit behavior remain unchanged. |
| UI/CLI no-change smoke | `uv run pytest tests/ui/test_cli.py -q` only if touched or if implementation plan wants broad guard | No default analyze/checklist/render behavior change. |
| Lint | `uv run ruff check fund_agent/fund tests/fund` | No lint regressions in touched areas. |
| Whitespace | `git diff --check` | Clean. |

## Stop Conditions

Stop and return to controller before implementation or before continuing implementation if any of these occur:

- The source category cannot be captured at `AnnualReportSourceOrchestrator` / `AnnualReportSourceMetadata` without changing source ordering, fallback eligibility, downloader behavior, source helper semantics, PDF/cache internals, or repository public entrypoint semantics.
- Implementing the field requires direct source helper, PDF, cache, or filesystem inspection from Service, renderer, quality gate, or public evidence scripts.
- Existing fail-closed categories could be masked by fallback success.
- Public classification would depend on extraction success, score success, quality status, renderer output, report text, source name alone, or cache hit status.
- Old metadata/cache rows cannot be read without forced destructive cache clearing.
- FQ0-FQ6, default `analyze` / `checklist`, renderer, report-writing, Host/Agent/dayu, baseline/golden fixture, or source strategy changes become necessary.
- Bounded evidence for `110020` / `017641` is requested before implementation review and controller acceptance.

## Non-Goals

- No source strategy change.
- No fallback eligibility rewrite.
- No direct source helper, PDF, cache, private exception, or filesystem inspection from public classification.
- No baseline/golden promotion or fixture update.
- No durable corpus denominator change.
- No Host/Agent/dayu package or runtime work.
- No renderer change.
- No FQ0-FQ6 policy, score semantics, or quality-gate policy change.
- No default `fund-analysis analyze` / `fund-analysis checklist` behavior change.
- No source replacement probing.
- No fund-type taxonomy, FOF coverage, bond residual, or `006597` work.

## Recommendation

Proceed, after review, with the smallest implementation slice: add optional `primary_failure_category` to `AnnualReportSourceMetadata`, set it only in the repository source-chain success-after-primary-failure path, and let the existing public provenance projection and snapshot fields expose it. This keeps fallback eligibility evidence logically/data-source aligned with the repository decision and avoids any inference from downstream extraction, scoring, or quality outputs.
