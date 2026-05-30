# Source Provenance Public Output Implementation Evidence

> Date: 2026-05-27
> Worker: AgentCodex
> Scope: accepted source provenance public-output implementation slice only
> Checkpoint entering implementation: `315c9ef docs: accept source provenance implementation plan`

## Scope Replay

Implemented only the accepted additive slice:

- Added Fund-owned deterministic public source provenance projection.
- Threaded projected provenance through `StructuredFundDataBundle` with a safe not-applicable default factory.
- Populated production `FundDataExtractor.extract()` provenance from `ParsedAnnualReport.metadata.source`.
- Added eight additive provenance fields to snapshot records / JSONL.
- Added separate `## Source Provenance` summary table with the accepted v1 columns.
- Added focused tests for projection, extractor threading, snapshot output, score no-change compatibility, and service fixture compatibility.

No changes were made to `FundDocumentRepository` source strategy, `documents/sources.py`, source helpers, downloader/cache/PDF access, renderer, FQ0-FQ6 policy, default analyze/checklist behavior, Host/Agent/dayu, fund type logic, golden/baseline fixtures, replacement candidates, or bounded 110020/017641 evidence runs.

## Files Changed

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/services/test_extraction_score_service.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Implementation Notes

- `PublicSourceProvenance` exposes stable v1 fields and Literal domains.
- `default_public_source_provenance()` returns `fallback_used=false`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`, and reason `source_metadata_absent_no_fallback_evidence`.
- Production fallback rows with `fallback_used=true` and no public `primary_failure_category` project to `fallback_eligibility=unknown_public_metadata_absent` and `source_provenance_status=incomplete`; no inference is made from `resolved_source_name`.
- Snapshot summary aggregates the first record per succeeded fund. Failed funds without snapshot records are omitted from the v1 table and documented with a short note.
- Score output remains compatible: top-level `score.json` keys and FQ0-FQ6 gate-sensitive structures are unchanged by additive provenance keys.

## Validation

Focused implementation tests:

```text
uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
67 passed in 0.72s
```

Adjacent compatibility tests:

```text
uv run pytest tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_quality_gate_service.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
112 passed in 0.76s
```

Static / whitespace:

```text
uv run ruff check .
All checks passed!

git diff --check
passed
```

## Residual / Stop-Condition Risk

- Expected residual: current repository public metadata does not persist `primary_failure_category`, so fallback-backed production rows normally remain `unknown_public_metadata_absent` / `incomplete`.
- No stop condition was hit.
- Existing unrelated untracked docs were present before evidence writing and were not modified by this implementation.
