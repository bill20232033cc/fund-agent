# Docling Source-truth Residual Closure No-live Implementation Code Review - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Implementation Gate`
Role: code review worker
Reviewer: AgentMiMo

## Findings

### F1 (Observation) — `candidate_documents` parameter accepted but unused

`close_source_truth_residuals` accepts `candidate_documents: Mapping[str, CandidateRepresentationDocument] | None = None` but immediately discards it at line 516:

```python
_ = candidate_documents or {}
```

The plan (section 5.2) states the helper must "consume already loaded JSON-like payloads or already projected candidate documents" and the `ResidualClosureInputRow` docstring says "current helper 只做 candidate metadata guard." However, the candidate metadata guard in `_processed_status` only inspects `row.candidate_anchor` — it never uses `candidate_documents`.

This is not a bug: the guard works correctly from anchor metadata alone. But the unused parameter creates a misleading API surface suggesting candidate-document-level validation that does not exist. If the evidence wrapper calls this function with `candidate_documents`, that argument has no effect.

**Severity**: observation — no behavioral impact.

### F2 (Observation) — `manager_holding_range_A` field rule has no dedicated test

The plan (section 6) requires testing identity, portfolio, benchmark, investment-objective, expense-duplicate, boundary, guard-flag, pure-helper-boundary, and missing-reference tests. The implementation evidence claims coverage for "manager/custodian disambiguation" but does not claim coverage for `manager_holding_range_A`. The `FIELD_RULES` dict includes a `manager_holding_range_A` rule (lines 463-469) with `share_class_context="A"`, `expected_section_id="§10"`, and `required_table_family_any`. No test exercises this rule.

The plan does not explicitly require a dedicated `manager_holding_range_A` test, so this is not a plan violation. However, the share-class-context logic (`_has_share_class_context`) and the §10 table-family guard are only tested through the `sales_service_fee_C_current_year` test, which uses `share_class_context="C"`.

**Severity**: observation — test gap, not a plan violation.

### F3 (Observation) — Unused imports `field` and `Any`

Line 15 imports `field` from `dataclasses` and line 16 imports `Any` from `typing`. Neither is used anywhere in the module. This is cosmetic but violates the project's general cleanliness expectation.

**Severity**: observation — no behavioral impact.

## Review Focus Findings

### 1. Bugs or contract violations in candidate-only helper

No bugs found. The helper correctly:
- Filters residual rows by excluding `row_disposition == "source_body_match"` (line 994).
- Applies three-layer status classification (source/processed/fund) per plan section 5.8.
- Requires all three layers (`same_source_reference_loaded`, `locator_context_available`, `semantic_rule_satisfied`) for `disambiguated_source_body_match` closure.
- Returns explicit residual/blocker dispositions for every other combination.

### 2. Direct file/PDF/cache/source-helper/FundDocumentRepository/Docling access

**PASS** — No forbidden access. Imports are limited to standard library (`re`, `Counter`, `Mapping`, `dataclass`, `Literal`) and internal candidate modules (`normalize_text`, `CandidateRepresentationDocument`). No `open()`, `Path`, `os`, `FundDocumentRepository`, `Docling`, `EvidenceAnchor`, `load_annual_report`, or source-helper references found. Module is not exported from public `fund_agent.fund.documents` package.

### 3. repository_source_name, processor route identity, and EvidenceAnchor.source_kind separation

**PASS** — Three distinct boundary fields are preserved:
- `matched_repository_source_name`: sourced from `RepositoryReferenceCell.repository_source_name` or `RepositoryReferenceTextSpan.repository_source_name` (line 1105-1122).
- `candidate_processor_source_kind`: sourced from `candidate_anchor["candidate_source_kind"]` or `candidate_anchor["processor_source_kind"]` (line 1099-1102).
- `evidence_anchor_source_kind`: hardcoded to `"annual_report"` (line 307).

Test `test_boundary_fields_keep_repository_processor_and_anchor_kind_separate` asserts all three are distinct.

### 4. S5-F023 and S6-F041 cannot be incorrectly closed without required proof

**PASS** —
- S5-F023 (`investment_objective`): When no same-source reference text matches, returns `source_body_mismatch` with `same_source_text_absent`. Test `test_investment_objective_without_same_source_body_stays_mismatch` confirms.
- S6-F041 (`benchmark`): Rule has `rejected_row_label_any=("投资目标",)` and `semantic_guard="业绩比较基准"`. When the only matching reference has `row_label_path=("投资目标",)`, `_match_satisfies_rule` returns `False` (rejection by `rejected_row_label_any`), yielding `semantic_assignment_residual` with `semantic_rule_rejected`. Test `test_benchmark_guard_keeps_investment_objective_context_residual` confirms.

### 5. Source / processed / fund statuses and closure_disposition coherence

**PASS** — All output paths through `_close_row` (lines 533-637) and `_result` (lines 999-1047) set all three status fields consistently:
- `blocked_candidate_metadata_violation` → `blocked_reference_unavailable` / `candidate_metadata_violation` / `semantic_rule_unresolved`
- `blocked_rule_missing` → `blocked_reference_unavailable` / (processed from `_processed_status`) / `semantic_rule_missing`
- `blocked_reference_unavailable` (no bundle or generation blocked) → `blocked_reference_unavailable` / (processed) / `semantic_rule_unresolved`
- `blocked_reference_unavailable` (metadata violation) → `metadata_violation` / (processed) / `semantic_rule_unresolved`
- `source_body_mismatch` → `same_source_text_absent` / (processed) / `semantic_rule_unresolved`
- `blocked_locator_unavailable` → `same_source_reference_loaded` / (processed) / `semantic_rule_unresolved`
- `semantic_assignment_residual` → `same_source_reference_loaded` / (processed) / `semantic_rule_rejected` or `semantic_rule_unresolved`
- `semantic_equivalent_duplicate_residual` → `same_source_reference_loaded` / (processed) / `semantic_rule_unresolved`
- `disambiguated_source_body_match` → `same_source_reference_loaded` / (processed) / `semantic_rule_satisfied`

Fail-closed behavior: any missing bundle, missing metadata, insufficient locator, or unresolved semantics prevents `disambiguated_source_body_match`.

### 6. Test coverage vs accepted plan requirements

All 13 plan-required test assertions are covered:

| Plan requirement | Test | Status |
| --- | --- | --- |
| identity code disambiguation | `test_identity_code_disambiguates_main_code_from_trading_code` | PASS |
| identity name disambiguation | `test_identity_name_closes_only_on_labeled_profile_row` | PASS |
| manager/custodian disambiguation | `test_manager_and_custodian_close_on_labeled_profile_rows` | PASS |
| portfolio parent/child split | `test_portfolio_parent_child_split_uses_row_label_not_value_only` | PASS |
| fixed-income hierarchy rejection | `test_fixed_income_rejects_fair_value_hierarchy_and_accepts_portfolio_row` | PASS |
| benchmark semantic guard | `test_benchmark_guard_keeps_investment_objective_context_residual` | PASS |
| investment-objective mismatch | `test_investment_objective_without_same_source_body_stays_mismatch` | PASS |
| unresolved duplicate | `test_unresolved_expense_duplicate_remains_semantic_equivalent_residual` | PASS |
| boundary fields | `test_boundary_fields_keep_repository_processor_and_anchor_kind_separate` | PASS |
| guard flags | `test_output_guard_flags_are_preserved` | PASS |
| pure helper boundary | `test_pure_helper_boundary_does_not_read_or_call_repository` | PASS |
| missing reference bundle | `test_missing_reference_bundle_blocks_reference_layer` | PASS |
| candidate boundary guard | `test_candidate_boundary_guard_rejects_truth_claims` | PASS (additional) |

### 7. Implementation claims baseline/source truth/parser replacement/readiness

**PASS** — Implementation evidence (`docs/reviews/docling-source-truth-residual-closure-no-live-implementation-evidence-20260616.md`) states:
- `Readiness: NOT_READY`
- `Non-readiness Statement`: "No baseline qualification, no parser replacement, no source policy change, no release readiness, no PR readiness and no full field correctness are claimed."
- Guard flags in `SourceTruthResidualClosureMatrix`: all six non-proof guards are `True`.

## Adversarial Failure Pass

- Substring over-match: `_reference_matches` uses `candidate in normalized_text` substring matching. Short values (e.g., "004393") could match longer strings. Mitigated by semantic rules (row label, column header, table context) that constrain which matches are accepted. Not a false-closure risk under current field rules.
- Empty bundle: `_source_matches` returns empty tuple for empty bundle, correctly yielding `source_body_mismatch`.
- `reference_generation_status` string coercion: `_coerce_bundle` accepts any string via `str(value.get(...))`, not validated against `ReferenceGenerationStatus` literal at runtime. Type system provides compile-time guard only.

## Validation

```bash
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result: 13 passed in 0.71s

```bash
git diff --check
```

Result: clean (no output)

## Conclusion

```text
PASS_WITH_FINDINGS
```

Implementation correctly follows the accepted plan and controller judgment boundaries. Three observations (F1-F3) are non-blocking: unused `candidate_documents` parameter, missing `manager_holding_range_A` dedicated test, and unused imports. No contract violations, no boundary breaches, no incorrect closures, and no readiness/baseline/replacement claims found.
