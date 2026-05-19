# P4-S1 Code Review — AgentGLM

> **Reviewer**: AgentGLM
> **Date**: 2026-05-19
> **Gate**: `P4-S1 code review`
> **Scope**: Selected Fund Extraction Snapshot + Quality Gate MVP
> **Design doc**: `docs/design.md`
> **Control docs**: `docs/implementation-control.md`, `docs/implementation-control-p4.md`
> **Implementation artifact**: `docs/reviews/p4-s1-implementation-20260519.md`

---

## Review Criteria

1. P4-S1 must implement Selected Fund Extraction Snapshot + Quality Gate MVP only. It must not fix 004393 classifier or expand extractor logic.
2. Snapshot core must be in Capability layer `fund_agent/fund`. UI must depend on Service/Application, not Capability.
3. Annual report access must go through `FundDataExtractor.extract(...)` or `FundDocumentRepository` only. No direct PDF/cache reads in upper layers.
4. Explicit params only: `fund_code`, `report_year`, `source_csv`, `run_id`, `output_dir`, `force_refresh`, `sample_per_category`, `limit`. No `extra_payload`.
5. Snapshot schema must contain required fields from control doc section 4.5 and `field_group`/`field_name` mapping.
6. Failure continuation, `errors.jsonl`, duplicate 016492 summary marking, and 004393 known failure capture must be correct.
7. Tests must avoid real network/PDF and cover CSV validation, schema, duplicate summary, failure continuation, Service/UI boundary.

---

## Findings

### F1 — INFO: `_path_for_output` uses CWD-relative instead of repo-root-relative

- **Severity**: INFO
- **File**: `fund_agent/fund/extraction_snapshot.py:1149-1152`
- **Evidence**:

```python
def _path_for_output(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
```

The control doc section 4.5 says "`source_csv` 使用相对 repo root 的路径". The implementation uses `Path.cwd()` to compute relative paths. When the CLI is run from the repo root (the default), behavior matches the control doc. When run from another directory, the recorded `source_csv` in snapshot records would differ.

- **Recommendation**: Accept as-is for P4-S1. The CLI default `source_csv` is already a relative path (`docs/code_20260519.csv`), and `_path_for_output` would keep it as-is when CWD matches repo root.

### F2 — INFO: `_KNOWN_FAILURE_004393_NOTE` is hardcoded for a single fund code

- **Severity**: INFO
- **File**: `fund_agent/fund/extraction_snapshot.py:43`, line `621`, line `1046`
- **Evidence**:

```python
_KNOWN_FAILURE_004393_NOTE: Final[str] = "known_failure:P4-S1 当前记录 004393 被误判为 index_fund 的真实输出，不在本 slice 修正。"
```

```python
if selected_fund.fund_code == "004393" and classified_fund_type == "index_fund" and field_name == "classified_fund_type":
    notes.append(_KNOWN_FAILURE_004393_NOTE)
```

The known failure note is only triggered for `fund_code == "004393"`. This is the exact known failure case documented in the control doc section 1. The classifier fix is deferred to P4-S3.

- **Recommendation**: Accept as-is for P4-S1 scope. P4-S3 will address the underlying classifier, at which point this hardcoding can be removed or generalized to a data-driven known-failure registry.

### F3 — INFO: Duplicate fund codes are not deduplicated before extraction

- **Severity**: INFO
- **File**: `fund_agent/fund/extraction_snapshot.py:314-317` (explicit selection), `669-677` (category sampling)
- **Evidence**:

```python
if fund_code:
    selected = [fund for fund in funds if fund.fund_code == fund_code]
```

When `016492` appears twice in the CSV and is selected (by explicit code or by category sampling reaching that row), both occurrences are processed. This produces duplicate snapshot records and a redundant extraction call.

The control doc section 2 says "P4-S1 允许重复但 summary 必须标红". The summary correctly marks `016492` with `<mark>016492</mark>` and the duplicate does not block the run.

- **Recommendation**: Accept as-is for P4-S1. If P4-S2 or later slices require deduplicated snapshot records, a `seen_codes` filter can be added to `select_snapshot_funds`.

### F4 — LOW: `SnapshotExtractor` Protocol duplicates `_FundDataExtractor` Protocol signature

- **Severity**: LOW
- **Files**: `fund_agent/fund/extraction_snapshot.py:46-72` vs `fund_agent/services/fund_analysis_service.py:39-66`
- **Evidence**: Both files define a Protocol with identical `extract()` signature:

```python
async def extract(self, fund_code: str, report_year: int, *, force_refresh: bool = False) -> StructuredFundDataBundle:
```

Python's structural subtyping means `FundDataExtractor` satisfies both Protocols. The duplication is not a correctness issue, but it means any future signature change must be updated in two places.

- **Recommendation**: No action for P4-S1. Could be consolidated into a shared Protocol in `fund_agent.fund.data_extractor` if Protocol reuse becomes a maintenance concern.

### F5 — INFO: Failed fund rows in summary include raw error message

- **Severity**: INFO
- **File**: `fund_agent/fund/extraction_snapshot.py:615-618`
- **Evidence**:

```python
lines.append(
    "| "
    f"{fund.fund_code} | {fund.fund_name} | {fund.app_category} | failed |  | "
    f"{error.error_type}: {error.error_message} |"
)
```

Production errors could produce verbose messages in the summary Markdown table. However, `errors.jsonl` provides the complete structured error detail, and the summary is intended for human scanning.

- **Recommendation**: Accept as-is for P4-S1. If summary readability becomes an issue with real errors, consider truncating `error_message` in the table and pointing to `errors.jsonl`.

---

## Criteria Verification

### C1: Scope limited to Selected Fund Extraction Snapshot + Quality Gate MVP — PASS

The implementation only adds snapshot recording capability. It does not modify the classifier, any extractor, or the template/analysis pipeline. The only change to existing files (`fund_analysis_service.py`, `__init__.py`, `cli.py`, READMEs) is additive integration and documentation.

**Evidence**: No changes to `fund_agent/fund/extractors/*`, `fund_agent/fund/fund_type.py`, `fund_agent/fund/analysis/*`, or `fund_agent/fund/template/*`.

### C2: Snapshot core in Capability layer; UI depends on Service, not Capability — PASS

- Snapshot core: `fund_agent/fund/extraction_snapshot.py` (Capability layer) ✅
- Service: `fund_agent/services/extraction_snapshot_service.py` imports from Capability ✅
- CLI: `fund_agent/ui/cli.py` imports `ExtractionSnapshotRequest` and `ExtractionSnapshotService` from `fund_agent.services` (line 18-19), not from Capability ✅

**Evidence**: `cli.py` line 16-24:

```python
from fund_agent.services import (
    ExtractionSnapshotRequest,
    ExtractionSnapshotService,
    ...
)
```

### C3: Annual report access through `FundDataExtractor.extract(...)` only — PASS

`run_extraction_snapshot` line 387:

```python
bundle = await active_extractor.extract(fund.fund_code, report_year, force_refresh=force_refresh)
```

No direct reads of `fund_agent/fund/pdf/*`, `cache/pdf/*`, or local PDF files in any upper layer.

### C4: Explicit params only, no `extra_payload` — PASS

`ExtractionSnapshotRequest` dataclass fields (line 31-38):

```python
fund_code: str | None
report_year: int
source_csv: Path
run_id: str
output_dir: Path | None
force_refresh: bool
sample_per_category: int = 1
limit: int | None = None
```

All 8 params are explicit. No `extra_payload`, no implicit CWD dependency for core logic. CLI constructs the request directly (line 176-189).

### C5: Snapshot schema matches control doc section 4.5 — PASS

`SnapshotRecord` dataclass contains all 19 required fields:

| Control doc field | SnapshotRecord attribute | Type |
|---|---|---|
| `run_id` | `run_id` | `str` |
| `extraction_timestamp` | `extraction_timestamp` | `str` |
| `source_csv` | `source_csv` | `str` |
| `fund_code` | `fund_code` | `str` |
| `fund_name` | `fund_name` | `str` |
| `app_category` | `app_category` | `str` |
| `report_year` | `report_year` | `int` |
| `classified_fund_type` | `classified_fund_type` | `str \| None` |
| `classification_basis` | `classification_basis` | `tuple[str, ...]` |
| `field_name` | `field_name` | `str` |
| `field_group` | `field_group` | `str` |
| `extraction_mode` | `extraction_mode` | `str` |
| `value_present` | `value_present` | `bool` |
| `anchor_present` | `anchor_present` | `bool` |
| `section_id` | `section_id` | `str \| None` |
| `page` | `page` | `int \| None` |
| `table_id` | `table_id` | `str \| None` |
| `row_id` | `row_id` | `str \| None` |
| `note` | `note` | `str \| None` |

`SNAPSHOT_FIELD_ORDER` has exactly 14 entries matching the control doc's `field_group`/`field_name` mapping in section 4.5, in the same order.

All 14 `field_name` values correspond to attributes on `StructuredFundDataBundle`:
- `basic_identity`, `product_profile`, `benchmark`, `fee_schedule` (from `ProfileExtractionResult`)
- `classified_fund_type` (derived from `basic_identity.value["classified_fund_type"]`)
- `nav_benchmark_performance`, `investor_return` (from `PerformanceExtractionResult`)
- `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holder_structure` (from `ManagerOwnershipExtractionResult`)
- `holdings_snapshot`, `share_change` (from `HoldingsShareChangeExtractionResult`)
- `nav_data` (from `NavDataResult`)

### C6: Failure continuation, errors.jsonl, duplicate marking, 004393 known failure — PASS

**Failure continuation**: `run_extraction_snapshot` lines 385-407. Per-fund try/except catches all exceptions, records to `errors.jsonl` via `_append_jsonl`, appends to `error_records`, and `continue`s.

**errors.jsonl**: Written per-error at line 406. Schema is `SnapshotErrorRecord` with `run_id`, `extraction_timestamp`, `source_csv`, `fund_code`, `fund_name`, `app_category`, `report_year`, `error_type`, `error_message`.

**Duplicate 016492 marking**: `validate_selected_fund_pool` line 279-280 detects duplicates. `write_snapshot_summary` lines 574-576 renders `<mark>016492</mark>`. `has_blocking_errors` correctly returns `False` for duplicates only (line 119), so duplicates don't block the run.

**004393 known failure**: `_record_note` lines 1046-1047 appends `_KNOWN_FAILURE_004393_NOTE` when `fund_code == "004393"` and `classified_fund_type == "index_fund"`. Summary Fund Results table also adds the note at line 621. The classification is **recorded as-is**, not overwritten or corrected.

### C7: Tests avoid real network/PDF and cover required scenarios — PASS

| Scenario | Test | Network/PDF |
|---|---|---|
| CSV validation (missing, bad code, duplicates) | `test_selected_fund_csv_validation_flags_missing_bad_code_and_duplicates` | No — inline CSV |
| Snapshot schema (all 19 fields, all 14 field_name) | `test_build_snapshot_records_contains_required_schema_and_all_fields` | No — `_build_bundle` helper |
| Duplicate summary marking | `test_run_snapshot_summary_highlights_duplicates_and_continues_failures` | No — `_FakeExtractor` |
| Failure continuation + errors.jsonl | Same as above | No — `_FakeExtractor` with injected `RuntimeError` |
| 004393 known failure capture | `test_004393_known_failure_classification_is_captured` | No — `_FakeExtractor` |
| Service boundary (explicit params) | `test_extraction_snapshot_service_delegates_explicit_params` | No — `monkeypatch` |
| Service validation (invalid fund_code) | `test_extraction_snapshot_service_rejects_invalid_fund_code` | No — no extractor call |
| CLI boundary (thin entry) | `test_extraction_snapshot_cli_is_thin_capability_entry` | No — `_FakeExtractionSnapshotService` |
| Real CSV smoke | `test_selected_funds_smoke.py` (4 tests) | No — dry-run only |

All tests use fake extractors, monkeypatched services, or inline CSV fixtures. No test triggers real PDF download, network access, or cache writes.

---

## Adversarial Failure Pass

### AF1: What if `FundDataExtractor.extract()` returns a bundle with `basic_identity.value = None`?

`_extract_classified_fund_type` line 715: `value = bundle.basic_identity.value or {}` — safely handles `None`, returns `None` for `classified_fund_type`. The snapshot record would have `classified_fund_type=None`, `extraction_mode="missing"`, `value_present=False`. Correct. ✅

### AF2: What if `classification_basis` is an unexpected type (e.g., int)?

`_extract_classification_basis` lines 739-743: handles `None`, `str`, `Sequence`, and falls through to `str()` for anything else. Returns a `tuple[str, ...]` in all cases. Correct. ✅

### AF3: What if an `ExtractedField` has `extraction_mode` not in the known set?

`_normalize_extraction_mode` line 981: any unrecognized mode falls through to `"missing"`. Defensive. ✅

### AF4: What if snapshot output directory creation fails (permissions)?

`run_extraction_snapshot` line 370: `resolved_output_dir.mkdir(parents=True, exist_ok=True)` would raise `OSError`, which propagates to the caller. The function's docstring documents `OSError` in the Raises section. Correct. ✅

### AF5: What if `_append_jsonl` fails mid-run (disk full)?

`_append_jsonl` opens files in append mode per-line. A write failure on one fund's records would propagate as `OSError` from the per-fund loop, caught by the outer try/except at line 392. The error would be recorded in `error_records` but NOT in `errors.jsonl` (since the write itself failed). The summary would still be written after the loop. This is a narrow edge case — partial data loss is acceptable for P4-S1 MVP. Not blocking.

---

## Verdict

**PASS**

No blocking or high-severity findings. P4-S1 correctly implements the Selected Fund Extraction Snapshot + Quality Gate MVP within the specified scope:

- Layering is clean: Capability → Service → UI dependency direction is correct.
- Annual report access is uniformly mediated through `FundDataExtractor.extract(...)`.
- Snapshot schema exactly matches the control doc section 4.5 field specification.
- Failure continuation, duplicate marking, and 004393 known failure capture all work correctly.
- Test coverage avoids real network/PDF and covers all review criteria.
- No scope creep into classifier fixes or extractor expansion.

Five info/low findings documented above. None warrant blocking the slice.
