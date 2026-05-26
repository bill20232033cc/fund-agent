# Code Review

## Scope

- Mode: current changes (uncommitted workspace + untracked files on `codex/local-reconciliation`)
- Branch: `codex/local-reconciliation`
- Base: `main` (latest accepted checkpoint: `315c9ef docs: accept source provenance implementation plan`)
- Output file: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-review-mimo-20260527.md`
- Included scope:
  - New: `fund_agent/fund/source_provenance.py` (untracked)
  - Modified: `fund_agent/fund/data_extractor.py`, `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/README.md`
  - New: `tests/fund/test_source_provenance.py` (untracked)
  - Modified: `tests/fund/test_data_extractor.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_extraction_score.py`, `tests/services/test_extraction_score_service.py`, `tests/README.md`
- Excluded scope: renderer, FQ0-FQ6, default CLI/Host/Agent/dayu, FundDocumentRepository source strategy, source helper/downloader/cache/PDF, golden/baseline, report_evidence.py, report_quality_validation.py
- Parallel review coverage: 无
- Plan: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-plan-20260527.md`

## Findings

### 1-未修复-低-Source Provenance summary note always shown when any errors exist, even partial-failure funds

- **入口/函数**: `_source_provenance_summary_lines()` in `fund_agent/fund/extraction_snapshot.py`
- **文件(行号)**: `extraction_snapshot.py:1071-1078` (unstaged diff offset)
- **输入场景**: A fund that fails on some fields but still produces snapshot records for other fields (partial failure). `errors` is non-empty, but all funds in `errors` may also have records in `records`.
- **实际分支**: `if errors:` is truthy whenever `errors` is non-empty, regardless of whether any fund was completely omitted from `records`.
- **预期行为**: Note should ideally distinguish "some failed funds still have records" from "some failed funds were completely omitted." The current note says "Failed funds without snapshot records are omitted," which is factually correct but always shown when any error exists.
- **实际行为**: The note `_Failed funds without snapshot records are omitted from Source Provenance v1._` is appended whenever `errors` is non-empty. If all funds in `errors` actually have at least one record in `records`, the note still appears but no fund is actually omitted.
- **直接证据**: `extraction_snapshot.py:1071` — `if errors:` unconditionally emits the note. The `first_records_by_fund` dict only includes funds with records, so the table itself is correct; only the note is over-inclusive.
- **影响**: Cosmetic / informational only. The Source Provenance table itself is correct. The note may cause a reader to expect omitted funds when none are actually omitted.
- **建议改法和验证点**: Optionally check `error_fund_codes - record_fund_codes` to determine if any fund was actually omitted before emitting the note. Low priority.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 2-未通过-无实质问题-Projection correctness verified

PublicSourceProvenance projection logic in `source_provenance.py` is correct:

- `fallback_used=true` + `primary_failure_category=None` → `unknown_public_metadata_absent`, `incomplete`, never `eligible`. Confirmed at line 161-170.
- Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) → `fail_closed`, `incomplete`. Confirmed at line 150-160.
- Eligible categories (`not_found`, `unavailable`) → `eligible`, `complete`. Confirmed at line 139-149.
- `fallback_used=false` → `not_applicable` regardless of source name. Confirmed at line 127-137.
- Source name alone (`eastmoney`) does not imply fallback. Confirmed by test `test_eastmoney_source_name_alone_does_not_imply_fallback`.
- `source_metadata=None` → safe default `not_applicable`. Confirmed at line 123-124.

### 3-未通过-无实质问题-Boundary compliance verified

- `source_provenance.py` imports only from `fund_agent.fund.documents.models.AnnualReportSourceMetadata`. No access to `sources.py`, downloader, cache, PDF, or source helper internals.
- `data_extractor.py` change is additive: one new field on `StructuredFundDataBundle` with safe default factory, one explicit projection call in `extract()`. No change to repository, extractor, or nav provider logic.
- `extraction_snapshot.py` changes are additive: 8 new fields on `SnapshotRecord`, one summary table helper. No change to `SNAPSHOT_FIELD_ORDER`, field counts, selected fund logic, or errors JSONL semantics.
- No renderer, FQ0-FQ6, CLI, Host, Agent, dayu, golden, or baseline scope drift detected.

### 4-未通过-无实质问题-StructuredFundDataBundle default factory verified

- `source_provenance: PublicSourceProvenance = field(default_factory=default_public_source_provenance)` at `data_extractor.py:121-123`.
- Default returns `not_applicable`, `fallback_used=False`, `source_provenance_status="not_applicable"`.
- Production `extract()` explicitly calls `project_public_source_provenance(report.metadata.source)` at `data_extractor.py:210`.
- Test `test_structured_bundle_default_source_provenance_is_not_none` confirms safe default never `None`.

### 5-未通过-无实质问题-SnapshotRecord/JSONL and summary output verified

- All 8 provenance fields added to `SnapshotRecord` as final fields (after `note`), preserving existing field order.
- `_snapshot_record()` copies all 8 values from `bundle.source_provenance` at `extraction_snapshot.py:1050-1057`.
- Summary table has correct 6 columns: `fund_code`, `resolved_source_name`, `fallback_used`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`.
- `null` formatting for `None`, `true`/`false` for booleans — deterministic.
- Failed-fund omission note present. Table sorted by `fund_code` — deterministic.
- Test `test_run_snapshot_summary_highlights_duplicates_and_continues_failures` verifies table presence, column headers, row content, omission note, and that failed fund 000001 is excluded from the provenance section.

### 6-未通过-无实质问题-Score compatibility tests verified

- `test_source_provenance_keys_do_not_change_score_outputs`: Compares `score_snapshot_records`, `score_fund_records`, `derive_fund_quality_records`, `derive_field_applicability_decisions`, `derive_score_applicability_issues` with and without provenance fields. Asserts equality.
- `test_run_extraction_score_output_ignores_additive_source_provenance`: Full `run_extraction_score` end-to-end with legacy vs provenance JSONL. Asserts `score.json` top-level key set (`_SCORE_JSON_TOP_LEVEL_KEYS`) and all gate-sensitive keys identical.
- `test_run_extraction_score_writes_score_outputs`: Asserts `set(score_payload) == _SCORE_JSON_TOP_LEVEL_KEYS` — key set stability.
- Legacy `_snapshot_record()` without `include_source_provenance=True` produces records without provenance keys, confirming backward compatibility.

### 7-未通过-无实质问题-Test/doc coverage and README sync verified

- `test_source_provenance.py`: 7 tests covering default, primary, fallback-unknown, eligible, fail-closed, source-name-no-infer, and dict serialization.
- `test_data_extractor.py`: 4 new tests covering default provenance, primary projection, fallback-unknown projection, and NAV degradation not affecting provenance.
- `test_extraction_snapshot.py`: 3 new tests covering provenance fields in schema, identical provenance across rows, and summary table with omission note.
- `test_extraction_score.py`: 2 new tests for legacy/additive compatibility at record and end-to-end levels.
- `fund_agent/fund/README.md` updated: additive provenance fields documented, Source Provenance summary table documented.
- `tests/README.md` updated: `test_source_provenance.py` entry added, existing entries updated for provenance coverage.

## Open Questions

无。

## Residual Risk

- `test_extraction_score_service.py` change (adding `field_applicability_decisions` and `score_applicability_issues` to fixture) is a compatibility fix for the committed `extraction_score.py` changes, not a source provenance change. Adjacent compatibility, not a gap.
- Report-evidence provenance projection (`report_evidence.py`) deferred per plan. Current `source_failure_category` is caller-provided and enforces different semantics; mixing repository public provenance would risk changing baseline review logic. Correctly deferred.
- No CLI end-to-end test exercises the Source Provenance table in a full `fund-analysis extraction-snapshot` run. The snapshot unit tests cover the table construction; a CLI integration test would add confidence but is not strictly required for this additive gate.

## Conclusion

**PASS**

Implementation correctly follows the accepted plan. All eight source provenance fields are projected from `AnnualReportSourceMetadata` through `StructuredFundDataBundle` to `SnapshotRecord` JSONL and summary output. Conservative fail-closed rules are correctly enforced: `fallback_used=true` with missing category maps to `unknown_public_metadata_absent` (never eligible), fail-closed categories never become clean, and source name alone does not imply fallback. Boundary compliance is clean: no source helper/downloader/cache/PDF access, no repository/renderer/FQ0-FQ6/CLI scope drift. Score compatibility is explicitly tested at both record and end-to-end levels. One low-severity cosmetic finding: the summary omission note is shown whenever any error exists, even if no fund is actually omitted from the table.
