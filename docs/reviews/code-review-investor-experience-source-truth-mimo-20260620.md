# Code Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Metadata

- Role: AgentMiMo code reviewer
- Gate: Code Review Gate
- Work unit: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction
- Branch: `funddisclosure-investor-experience-source-truth`
- Base commit: `1bf4187` (accepted plan)
- Review date: 2026-06-20
- Verdict: **CODE_REVIEW_PASS**

## Scope Verification

Changed files match expected set exactly:

| File | Expected | Actual |
|---|---|---|
| `fund_agent/fund/processors/fund_disclosure_processor.py` | Yes | Yes |
| `tests/fund/processors/test_fund_disclosure_processor.py` | Yes | Yes |
| `tests/fund/test_data_extractor.py` | Yes | Yes |
| `fund_agent/fund/README.md` | Yes | Yes |
| `docs/design.md` | Yes | Yes |

No changes to `contracts.py`, `data_extractor.py`, `extractors/**`, `documents/**`, `services/**`, `ui/**`, `host/**`, `agent/**`, or any forbidden module.

## Contract Compliance

### Exact scope: investor_experience.v1 only

- [x] Public `investor_experience.v1.value` limited to `schema_version`, `investor_return`, `holder_structure`, `share_change`
- [x] `subscription_redemption` and `income_distribution` remain candidate-only; never emitted as public subvalues
- [x] `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` constant contains exactly three keys

### Proof-positive only; fail-closed on all other paths

- [x] Proof-positive direct route returns `candidate_evidence=()` for `investor_experience.v1`
- [x] Direct-route missing returns `candidate_evidence=()`, `status="missing"`, `value={}`, `anchors=()`
- [x] Proof-missing preserves candidate-only public missing with `source_truth_admission_missing` gap
- [x] Proof-invalid preserves candidate-only public missing with `source_truth_admission_invalid` gap
- [x] Candidate-boundary blocks direct route, preserves public missing
- [x] Missing provenance / non-empty `failure_class` fail closed

### current_stage.v1 and core_risk.v1 non-interference

- [x] Their candidate selectors remain unconditional (not gated on investor_experience source truth)
- [x] Investor direct-route suppression does not clear their existing candidate evidence

### No forbidden expansions

- [x] No parser replacement
- [x] No `EvidenceSourceKind` or public `EvidenceAnchor` expansion
- [x] No Service/UI/Host/renderer/quality-gate consumption changes
- [x] No live/provider/LLM claims
- [x] No real-report correctness, golden/readiness, release, or PR mutation claims

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 174 passed in 0.54s |
| `uv run pytest tests/fund/test_data_extractor.py -k "disclosure_source_truth_investor_experience or disclosure_candidate_only_investor_experience"` | 2 passed, 37 deselected in 0.39s |
| `uv run ruff check ...` | All checks passed |
| `git diff --check` | Passed (no whitespace errors) |

## Implementation Fidelity to Plan

### Constants and dataclass (Plan §4, §5, §7 Slice 1)

All 14 constants match the plan specification exactly:

- `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL`: 3 keys
- `_INVESTOR_RETURN_DIRECT_LABELS`: 3 labels
- `_INVESTOR_RETURN_ESTIMATED_LABELS`: 3 labels
- `_INVESTOR_RETURN_UNAVAILABLE_TOKENS`: 5 tokens
- `_HOLDER_STRUCTURE_INSTITUTIONAL_LABELS`: 4 labels
- `_HOLDER_STRUCTURE_INDIVIDUAL_LABELS`: 4 labels
- `_HOLDER_STRUCTURE_GUARD_LABELS`: 4 labels
- `_HOLDER_STRUCTURE_PLACEHOLDERS`: 6 values
- `_SHARE_CHANGE_BEGINNING_LABELS`: 3 labels
- `_SHARE_CHANGE_ENDING_LABELS`: 3 labels
- `_SHARE_CHANGE_NET_LABELS`: 2 labels
- `_SHARE_CHANGE_TABLE_GUARD_LABELS`: 3 labels
- `_SHARE_CHANGE_LABEL_COLUMN_TOKENS`: label tokens including row labels
- `_SHARE_CHANGE_VALUE_PATTERN`: numeric regex

`_InvestorExperienceValueCandidate` dataclass: `frozen=True, slots=True`, fields match plan.

### _field_families_for_intermediate integration (Plan §6)

Four surgical edits match plan exactly:

1. Local `investor_experience_source_truth` variable added
2. Direct extractor called under `source_truth_extraction_allowed and content_intermediate is not None` guard
3. Candidate selector suppressed when direct result present
4. Direct result returned for `family_id == "investor_experience.v1"` when present

### Helper function inventory (Plan §7 Slice 1)

All 8 required top-level helpers and 22+ sub-helpers present. Function signatures and return types match plan specification.

### Source selection rules (Plan §5)

- investor_return: paragraph + table extraction, direct/estimated label precedence, unavailable wording rejection, ambiguity resolution
- holder_structure: institutional/individual side independence, guard context requirement, placeholder filtering
- share_change: table-only, label-column exclusion, single_value_column / fund_code_header_match selection, Decimal net_change calculation, column_header_path aggregation

## Test Coverage

### Required tests (Plan §7 Slice 2): 17/18 present

| # | Test | Status |
|---|---|---|
| 1 | `test_..._route_suppresses_candidate_evidence` | Present |
| 2 | `test_..._requires_proof_even_when_candidate_boundary_none` | Present |
| 3 | `test_..._rejects_base_admission_invalid_paths` | Present |
| 4 | `test_..._candidate_boundary_remains_blocked` | Present |
| 5 | `test_..._extracts_exact_value_shape` | Present |
| 6 | `test_..._estimated_investor_return_only` | Present |
| 7 | `test_..._estimated_investor_return_conflict_omits_value` | Present |
| 8 | `test_..._investor_return_paragraph_requires_label_value_pattern` | Present |
| 9 | `test_..._holder_structure_filters_placeholder_values` | Present |
| 10 | `test_..._partial_when_required_groups_missing` | Present |
| 11 | `test_..._missing_when_no_allowed_public_labels` | Present |
| 12 | `test_..._ambiguous_duplicate_omits_conflicting_value` | Present |
| 13 | `test_..._share_change_excludes_label_column` | Present |
| 14 | `test_..._share_change_selects_single_value_column` | **Missing** (see finding F1) |
| 15 | `test_..._share_change_selects_exact_fund_code_column` | Present |
| 16 | `test_..._share_change_rejects_ambiguous_share_class_columns` | Present |
| 17 | `test_..._share_change_calculates_net_change` | Present |
| 18 | `test_..._does_not_populate_stage_or_risk` | Present |

### Facade regression tests (Plan §7 Slice 3): 2/2 present

- `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle`: proof-positive -> bundle projection with `extraction_mode="direct"`, non-empty values, annual-report anchors
- `test_explicit_disclosure_candidate_only_investor_experience_stays_missing`: proof-missing -> bundle fields stay `None` with empty anchors

### Contract coverage matrix

| Path | Test coverage |
|---|---|
| Proof-positive, all 3 subvalues | `extracts_exact_value_shape` |
| Proof-positive, partial | `partial_when_required_groups_missing` |
| Proof-positive, direct-route missing | `route_suppresses_candidate_evidence` |
| Proof-positive, candidate-only content | `missing_when_no_allowed_public_labels` |
| Proof-missing | `requires_proof_even_when_candidate_boundary_none` |
| Proof-invalid (provenance) | `rejects_base_admission_invalid_paths` |
| Proof-invalid (failure_class) | `rejects_base_admission_invalid_paths` |
| Candidate-boundary | `candidate_boundary_remains_blocked` |
| Ambiguous direct return | `ambiguous_duplicate_omits_conflicting_value` |
| Ambiguous estimated return | `estimated_investor_return_conflict_omits_value` |
| Ambiguous share_change column | `share_change_rejects_ambiguous_share_class_columns` |
| Estimated-only return | `estimated_investor_return_only` |
| Paragraph label/value pattern | `investor_return_paragraph_requires_label_value_pattern` |
| Placeholder filtering | `holder_structure_filters_placeholder_values` |
| Label column exclusion | `share_change_excludes_label_column` |
| Fund code header match | `share_change_selects_exact_fund_code_column` |
| Net change calculation | `share_change_calculates_net_change` |
| Stage/risk non-interference | `does_not_populate_stage_or_risk` |

## Findings

### F1 [LOW] Missing dedicated `share_change_selects_single_value_column` test

- File: `tests/fund/processors/test_fund_disclosure_processor.py`
- Plan §7 Slice 2 required a dedicated `test_investor_experience_source_truth_share_change_selects_single_value_column` test
- The test is absent from the diff
- **Mitigating factor**: `test_..._share_change_excludes_label_column` explicitly asserts `share_class_selection_reason == "single_value_column"` and sets up a table with exactly one label column and one value column, implicitly covering the single-value-column selection path
- **Severity**: LOW — the contract is proven by an existing test with explicit assertion; the missing test would be a more isolated variant of the same path
- **Recommendation**: add the dedicated test in a follow-up for plan completeness; no blocking concern

### No blocking findings.

## Observations

1. **Dead code** in `_collect_investor_return_table_candidates`: `if row_index < 0: break` is unreachable since `row_index` comes from `dict[int, ...]` keys (non-negative). Harmless, no action required.

2. **`_normalize_match_text` for fund_code_header_match**: collapses all whitespace to empty string, which is correct for the intended semantic of matching fund codes that should not contain spaces.

3. **Table unavailable wording check**: implementation checks individual cells for unavailable wording rather than row-aggregated text. This is a reasonable interpretation since table values occupy specific cells, and unavailable wording typically appears in the value cell itself.

## Documentation Accuracy

- `fund_agent/fund/README.md`: correctly states investor_experience.v1 covers `investor_return`, `holder_structure`, `share_change`; subscription_redemption/income_distribution stay candidate-only; current_stage.v1/core_risk.v1 remain unimplemented
- `docs/design.md`: v2.31 correctly updated with current code facts only; no premature claims

## Verdict

**CODE_REVIEW_PASS**

No blocking findings. One low-severity observation (F1) about a missing dedicated test that is implicitly covered by an existing test with explicit assertions. Implementation faithfully follows the accepted plan across all contract dimensions: scope, proof semantics, candidate suppression, non-interference, and forbidden expansion boundaries.
