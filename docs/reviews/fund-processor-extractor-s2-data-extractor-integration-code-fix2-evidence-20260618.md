# Fund Processor/Extractor S2 DataExtractor Integration — Code Fix2 Evidence

**Date:** 2026-06-18
**Gate:** S2 code fix gate, round 2
**Re-review artifact:** `fund-processor-extractor-s2-data-extractor-integration-code-rereview-codex-20260618.md`
**Worker:** AgentDS fix worker

## Accepted Blocking Finding

Repository/report mismatch still mixes request NAV data with report evidence.

## Exact Fix

### `fund_agent/fund/data_extractor.py` — identity validation gate (line 308–312)

After `repository.load_annual_report()` and before `_load_nav_data_or_unavailable()`, inserted:

```python
if report.key.fund_code != fund_code or report.key.year != report_year:
    raise RuntimeError(
        f"Report identity mismatch: requested {fund_code}/{report_year}, "
        f"loaded {report.key.fund_code}/{report.key.year}"
    )
```

This guarantees:
- If `report.key.fund_code != fund_code` → fail closed, NAV provider never called.
- If `report.key.year != report_year` → fail closed, NAV provider never called.
- No fallback to direct path.

### `tests/fund/test_data_extractor.py` — test replacement (line 879–900)

Replaced `test_active_fund_bundle_uses_report_identity_not_request_identity` (which previously asserted success when report fund_code="110011" ≠ request "999999") with `test_data_extractor_rejects_report_identity_mismatch_before_nav`:

```python
async def test_data_extractor_rejects_report_identity_mismatch_before_nav() -> None:
    repository = _FakeRepository(_annual_report())   # report.key.fund_code = "110011"
    nav_provider = _RecordingNavProvider()
    registry = FundProcessorRegistry()
    registry.register(_MarkerActiveFundProcessor)
    extractor = FundDataExtractor(
        repository=repository,
        nav_provider=nav_provider,
        processor_registry=registry,
    )

    with pytest.raises(RuntimeError, match="Report identity mismatch"):
        await extractor.extract("999999", 2024)       # request fund_code = "999999"

    assert nav_provider.calls == []                    # NAV provider never called
```

Processor result mismatch test (`test_active_fund_processor_mismatched_identity_fails_closed`) preserved unchanged.

## Command Results

### Tests — 30 passed, 0 failed

```
tests/fund/processors/test_registry.py::test_registry_resolves_priority_descending PASSED
tests/fund/processors/test_registry.py::test_registry_keeps_stable_tie_order PASSED
tests/fund/processors/test_registry.py::test_registry_first_supported_wins PASSED
tests/fund/processors/test_registry.py::test_registry_unsupported_context_fail_closed PASSED
tests/fund/processors/test_registry.py::test_registry_create_default_resolves_active_annual_processor PASSED
tests/fund/processors/test_registry.py::test_dispatch_key_rejects_invalid_values_and_has_no_extra_payload PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_outputs_six_non_missing_field_families PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_mapping_table_covers_emitted_value_fields PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_keeps_mapping_gaps_on_field_family_only PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_emits_field_family_missing_when_whole_family_missing PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_projects_public_provenance_and_public_anchors PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_makes_no_candidate_proof_or_readiness_claims PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_does_not_import_or_call_source_access_boundaries PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_fail_closed_on_wrong_intermediate_type PASSED
tests/fund/processors/test_active_annual_processor.py::test_active_processor_unsupported_dispatch_gap_attribution PASSED
tests/fund/test_data_extractor.py::test_data_extractor_degrades_nav_failure_without_blocking_annual_report PASSED
tests/fund/test_data_extractor.py::test_data_extractor_does_not_mask_repository_failure PASSED
tests/fund/test_data_extractor.py::test_structured_bundle_default_source_provenance_is_not_none PASSED
tests/fund/test_data_extractor.py::test_data_extractor_returns_bundle_with_bond_risk_evidence PASSED
tests/fund/test_data_extractor.py::test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups PASSED
tests/fund/test_data_extractor.py::test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes PASSED
tests/fund/test_data_extractor.py::test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak PASSED
tests/fund/test_data_extractor.py::test_data_extractor_projects_primary_source_metadata PASSED
tests/fund/test_data_extractor.py::test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent PASSED
tests/fund/test_data_extractor.py::test_data_extractor_projects_metadata_primary_failure_category PASSED
tests/fund/test_data_extractor.py::test_active_fund_uses_processor_path_with_marker_values PASSED
tests/fund/test_data_extractor.py::test_active_fund_unsupported_registry_fails_closed PASSED
tests/fund/test_data_extractor.py::test_active_fund_processor_mismatched_identity_fails_closed PASSED
tests/fund/test_data_extractor.py::test_data_extractor_rejects_report_identity_mismatch_before_nav PASSED
tests/fund/test_data_extractor.py::test_index_fund_direct_path_smoke_test PASSED

============================== 30 passed in 0.56s ==============================
```

### Ruff check — all passed

```
All checks passed!
```

### git diff --check — no whitespace errors

(no output)

## Git Status

```
 M fund_agent/fund/README.md
 M fund_agent/fund/data_extractor.py
 M tests/fund/test_data_extractor.py
?? docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix2-evidence-20260618.md
 (plus untracked residue — not in scope)
```

## Verification Summary

| Check | Result |
|---|---|
| Report identity validated before NAV provider call | PASS |
| Mismatch raises RuntimeError with "Report identity mismatch" | PASS |
| NAV provider not called on mismatch (`nav_provider.calls == []`) | PASS |
| Repository failure still propagated (no masking) | PASS |
| Processor result identity mismatch test preserved | PASS |
| All 30 tests pass | PASS |
| Ruff check clean | PASS |
| git diff --check clean | PASS |
| No commit/push/PR/merge | CONFIRMED |
