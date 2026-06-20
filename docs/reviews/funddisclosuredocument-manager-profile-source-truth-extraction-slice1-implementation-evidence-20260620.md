# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 1 Implementation Evidence

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 1 Direct Route / Admission Guard Skeleton`
- Role: AgentCodex implementation worker only
- Verdict: `IMPLEMENTATION_SLICE1_COMPLETE`
- Evidence artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice1-implementation-evidence-20260620.md`

## Exact Slice Objective

Route exactly `manager_profile.v1` through existing source-truth admission when `source_truth_extraction_allowed` is true, but return a direct-route missing skeleton only. The skeleton suppresses `manager_profile.v1` candidate evidence on proof-positive direct route, including when no direct value is found.

No value extraction was implemented for `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, or `holdings_snapshot`.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice1-implementation-evidence-20260620.md`

## Implementation Summary

- Added local `manager_profile_source_truth: FundFieldFamilyResult | None` in `_field_families_for_intermediate()`.
- When existing source-truth admission allows direct extraction and content intermediate is present, `_field_families_for_intermediate()` now calls `_extract_manager_profile_source_truth(content_intermediate, source_provenance, context)`.
- `manager_profile_evidence` is set to `()` when `manager_profile_source_truth` is present; otherwise it keeps existing `_select_manager_profile_candidate_evidence(intermediate)` behavior.
- Field-family construction now returns `manager_profile_source_truth` only for `family_id == "manager_profile.v1"` and non-None.
- Added `_extract_manager_profile_source_truth()` skeleton returning:
  - `field_family_id="manager_profile.v1"`
  - `status="missing"`
  - `extraction_mode="missing"`
  - `value={}`
  - `anchors=()`
  - one local `field_family_missing` gap
  - `candidate_evidence=()`
- `_validate_source_truth_admission()` was not modified.
- `product_essence.v1` and `return_attribution.v1` direct extraction behavior was preserved.

## Tests Added / Updated

- `test_manager_profile_source_truth_route_suppresses_candidate_evidence`
  - Proves proof-positive direct route returns public missing skeleton and suppresses `manager_profile.v1.candidate_evidence == ()`.
  - Also asserts `current_stage.v1` and `core_risk.v1` remain public missing with no value or anchors when the fixture includes holdings-related source text.
- `test_manager_profile_source_truth_requires_proof_even_when_candidate_boundary_none`
  - Proves `candidate_boundary=None` without source-truth proof is not sufficient.
  - Confirms proof-missing path keeps S6-D candidate evidence and appends `source_truth_admission_missing`.
- `test_manager_profile_source_truth_rejects_base_admission_invalid_paths`
  - Proves base admission failures such as missing `source_provenance` and `schema_drift` still block before field-family direct route.
- `test_manager_profile_source_truth_candidate_boundary_remains_blocked`
  - Proves candidate-boundary input remains `blocked`, public missing, and candidate-only rather than direct source truth.

## Validation Commands And Outputs

```text
$ uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
collected 139 items
tests/fund/processors/test_fund_disclosure_processor.py ................ [ 11%]
........................................................................ [ 63%]
...................................................                      [100%]
139 passed in 0.98s
```

```text
$ uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
$ git diff --check
<no output>
```

## Required Confirmations

- Candidate evidence is suppressed on proof-positive direct-route missing: confirmed by `test_manager_profile_source_truth_route_suppresses_candidate_evidence`, which asserts `manager_profile.v1.candidate_evidence == ()`.
- Proof-missing / candidate-only path still keeps candidate evidence and public missing: confirmed by `test_manager_profile_source_truth_requires_proof_even_when_candidate_boundary_none`, which asserts candidate evidence remains present, public `value == {}`, `anchors == ()`, and gaps include `candidate_only_not_source_truth` plus `source_truth_admission_missing`.
- Candidate-boundary blocked behavior is preserved: confirmed by `test_manager_profile_source_truth_candidate_boundary_remains_blocked`.
- Base admission invalid paths are preserved: confirmed by `test_manager_profile_source_truth_rejects_base_admission_invalid_paths`.
- `current_stage.v1` and `core_risk.v1` public missing / no leakage is preserved in the direct-route fixture.

## Residual Risks And Owners

- Real `manager_profile.v1` value extraction remains unimplemented: covered by later approved slices in this work unit.
- `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, and `holdings_snapshot` field correctness remains unproven: covered by later approved slices and future evidence worker.
- `holdings_snapshot` semantic overlap with `current_stage.v1` / `core_risk.v1` remains unresolved: owned by future `current_stage.v1` / `core_risk.v1` source-truth planning gates.
- Broader holdings shapes, manager tenure normalization, and manager alignment judgment remain out of scope: owned by future refinement gates.
- Design doc / README synchronization is not performed in this implementation-only slice because the allowed write set excludes those files.

## Stop Confirmation

No commit, push, PR, mark-ready, merge, external state mutation, unrelated cleanup, artifact disposition, or next gate action was performed.
