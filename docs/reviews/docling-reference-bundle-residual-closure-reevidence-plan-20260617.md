# Docling Reference Bundle Residual Closure Re-evidence Plan - 2026-06-17

Gate: `Docling Reference Bundle Residual Closure Re-evidence Planning Gate`
Role: planning worker only
Target artifact: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-20260617.md`
Status: `PLAN_NOT_READY`
Release/readiness: `NOT_READY`
Verdict: `RESIDUAL_CLOSURE_REEVIDENCE_PLAN_NOT_READY`

## Goal / Motivation / Success Signal

Goal: plan exactly one future no-live evidence gate that reruns Docling reference-bundle residual-closure re-evidence with producer diagnostics present, so closure-count movement can be classified only after sample identity, row identity, repository metadata, producer counts, `bundle_content_fingerprint`, and `producer_contract_version` are proven comparable.

Motivation: current accepted producer determinism evidence proves the reference-bundle producer can emit stable diagnostics and a deterministic `bundle_content_fingerprint`, but the existing real-artifact residual-closure matrices were produced before those diagnostics were available. Therefore the observed movement from prior `13 closed / 4 residual` to current `10 closed / 7 residual` is blocked evidence, not interpretable improvement or regression.

Success signal for this planning gate:

- The future evidence gate has an exact write set, exact input scope, JSON schema, comparability rules, verdict taxonomy, validation commands, stop conditions, and completion report format.
- The plan is code-generation-ready for an evidence worker without requiring them to invent scope, schema, row identity rules, or verdict semantics.
- The plan preserves `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY`.

## Non-goals / Scope Boundary

This planning gate does not:

- generate re-evidence JSON;
- explain the `13 / 4` vs `10 / 7` closure-count delta;
- run live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- access PDF/cache/source-helper directly;
- perform fresh fetch, repository reload, or source acquisition;
- modify code, tests, README, `docs/design.md`, `docs/implementation-control.md`, reports, or other review artifacts.

The future evidence gate must not claim:

- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness;
- golden readiness;
- release readiness;
- PR readiness.

## Direct Evidence Basis

Design/control guardrails:

- `docs/design.md` keeps production parsing as `pdfplumber -> raw_text / tables -> locate_sections -> ParsedAnnualReport -> 自研 extractor -> EvidenceAnchor / CHAPTER_CONTRACT / 审计 / 报告生成`.
- `docs/design.md` states Docling / document middle layers must stay inside `FundDocumentRepository` / Fund documents boundaries and cannot be used directly by Service, UI, Host, renderer, quality gate, or LLM prompt.
- `docs/design.md` states Docling output is candidate / benchmark artifact only, not fund fact source truth.
- `docs/implementation-control.md` Current Truth Guardrails keep current Docling evidence as candidate-layer evidence only and explicitly reject source truth, full field correctness, parser replacement, readiness, and release claims.

Accepted producer determinism evidence:

- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-controller-judgment-20260617.md` accepts `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"`, deterministic bundle diagnostics, `bundle_content_fingerprint`, row-level diagnostic payloads, and the fail-closed locks for S6-F041, S6-F049, and S6-F050.
- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md` and its controller judgment accept that same logical synthetic no-live input repeats to the same fingerprint, reordered cells keep the same fingerprint, hash-participating content perturbation changes the fingerprint, companion metadata-only mutation does not change the fingerprint, and blocked reference generation emits `diagnostic_payload_available=false` plus `bundle_content_fingerprint=null`.
- The same accepted evidence states prior `13 / 4` and current `10 / 7` residual-closure matrices must not be reinterpreted without producer diagnostics, and current `10 / 7` remains blocked evidence.

Existing real-artifact matrices:

- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` records `17` rows with `13` `disambiguated_source_body_match` and `4` `semantic_assignment_residual`, verdict `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`, `candidate_only=true`, and `source_truth_status=not_proven`.
- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json` records `17` rows with `10` `disambiguated_source_body_match`, `5` `semantic_assignment_residual`, and `2` `source_body_mismatch`; it records `delta_vs_previous_closed_rows=-3` and verdict `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`.
- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json` records regression rows `F015`, `S5-F023`, `S6-F035`, count drift for S1/S4/S5/S6, section inference drift for S1/S4/S5/S6, and verdict `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`.
- In both existing residual-closure row summaries, `diagnostic_payload_available` is absent/null at row level. That prevents current evidence from comparing row-level producer diagnostics or bundle fingerprints.

## First-principles Judgment

Closure count is an aggregate derived from three layers: source availability, processed locator context, and fund semantic rule evaluation. A count delta is only meaningful if the compared runs consumed the same sample identities, same row identities, same repository source metadata, and materially comparable producer inputs.

The accepted producer diagnostics create the missing comparability instrument, but only prospectively. They do not retroactively attach fingerprints to old real-artifact matrices. Therefore the next correct gate is not to interpret `13 / 4` vs `10 / 7`; it is to rerun residual-closure re-evidence with producer diagnostics and make comparability the first decision.

If fingerprints, counts, source metadata, or row identities drift, the only defensible conclusion is blocked non-comparable evidence. In that state, declaring helper improvement or regression would use indirect evidence and would violate the same-source/root-cause rule.

## Future Evidence Gate

Recommended gate name:

`Docling Reference Bundle Residual Closure Re-evidence Gate`

Future role:

evidence worker only.

### Exact Allowed Write Set

The future evidence gate may write only:

- `reports/docling-reference-bundle-residual-closure-reevidence/20260617/residual_closure_matrix.json`
- `docs/reviews/docling-reference-bundle-residual-closure-reevidence-20260617.md`

No other files may be written. In particular, the future gate must not modify code, tests, README, `docs/design.md`, `docs/implementation-control.md`, reports outside the write set, or existing review artifacts.

### Exact Input Scope

The future evidence gate input is exactly the same 17 residual rows already present in the prior/current matrices:

| sample_id | fact_id | field_name |
|---|---|---|
| S1 | F002 | `fund_code` |
| S1 | F015 | `sales_service_fee_C_current_year` |
| S1 | F020 | `manager_holding_range_A` |
| S4 | S4-F001 | `fund_name` |
| S4 | S4-F002 | `fund_code` |
| S4 | S4-F015 | `fixed_income_investment_amount` |
| S5 | S5-F018 | `fund_name` |
| S5 | S5-F019 | `fund_code` |
| S5 | S5-F023 | `investment_objective` |
| S5 | S5-F032 | `equity_investment_amount` |
| S6 | S6-F035 | `fund_name` |
| S6 | S6-F036 | `fund_code` |
| S6 | S6-F037 | `manager` |
| S6 | S6-F038 | `custodian` |
| S6 | S6-F041 | `benchmark` |
| S6 | S6-F049 | `equity_investment_amount` |
| S6 | S6-F050 | `stock_investment_amount` |

The target seven are the current blocked/residual rows from the `10 / 7` matrix:

- `F015`
- `S5-F023`
- `S5-F032`
- `S6-F035`
- `S6-F041`
- `S6-F049`
- `S6-F050`

The future evidence gate must explicitly cover the regression rows:

- `F015`
- `S5-F023`
- `S6-F035`

The future evidence gate must explicitly preserve these fail-closed locks:

- `S6-F041`: benchmark must remain fail-closed unless benchmark semantic context is proven; investment-objective text is insufficient.
- `S6-F049`: equity aggregate must remain fail-closed unless row hierarchy proves aggregate semantics; value equality alone is insufficient.
- `S6-F050`: stock child row must remain fail-closed unless parent/child hierarchy proves stock-child semantics; value equality alone is insufficient.

### Future Evidence JSON Schema

Top-level required fields:

- `schema_version`: exactly `docling_reference_bundle_residual_closure_reevidence.v1`.
- `gate`: exactly `Docling Reference Bundle Residual Closure Re-evidence Gate`.
- `no_live`: `true`.
- `candidate_only`: `true`.
- `source_truth_status`: exactly `not_proven`.
- `producer_contract_version`: exactly `docling_reference_bundle_producer_contract.v1`.
- `verdict`: one of the verdict taxonomy below; every allowed verdict ends with `NOT_READY`.
- `input_artifacts`: paths of consumed accepted artifacts/matrices.
- `summary`: aggregate row counts and disposition counts.
- `comparability`: comparability decision object.
- `samples`: sample-level diagnostics.
- `rows`: exactly 17 row-level results.
- `non_claims`: booleans explicitly keeping source truth, baseline promotion, parser replacement, full field correctness, golden readiness, release readiness, and PR readiness false.

Each `samples[]` item must include:

- `sample_id`
- `fund_code`
- `document_year`
- `repository_source_name`
- `source_mode`
- `fallback_used`
- `metadata_ok`
- `metadata_reason`
- `reference_generation_status`
- `producer_contract_version`
- `producer_input_mode`
- `diagnostic_payload_available`
- `diagnostic_payload_unavailable_reason` when `diagnostic_payload_available=false`
- `bundle_content_fingerprint`
- `cell_count`
- `text_span_count`
- `table_count`
- `section_count`
- `table_family_counts`
- `section_inference_counts`
- `section_inference_reason_counts`
- `row_hierarchy_role_counts`
- `text_semantic_context_counts`

Each `rows[]` item must include:

- `row_key`: stable key formatted as `<sample_id>/<fact_id>/<field_name>`.
- `sample_id`
- `fact_id`
- `field_name`
- `fund_code`
- `document_year`
- `current_disposition`
- `prior_disposition`
- `closure_disposition`
- `source_layer_status`
- `processed_layer_status`
- `fund_layer_status`
- `source_truth_status`: exactly `not_proven`.
- `candidate_only`: `true`.
- `matched_context`: object containing selected `reference_kind`, `section_id`, `table_id`, `row_index`, `column_index`, `row_label_path`, `column_header_path`, `table_context`, `table_family`, `row_hierarchy_path`, `row_hierarchy_role`, `share_class_context`, `period_context`, `semantic_context_label`, and `normalized_text_hash` when a match exists.
- `diagnostic_payload_available`
- `diagnostic_payload_unavailable_reason` when `diagnostic_payload_available=false`
- `diagnostic_payload` when available, using the implemented helper payloads:
  - `selected_reference_match`
  - `candidate_search_no_source_match`
  - semantic residual diagnostics with considered match diagnostics and rejection categories.

### Comparability Rules

The future evidence gate must evaluate comparability before interpreting any closure-count delta.

Required comparison order:

1. sample identity: exact sample set, `fund_code`, and `document_year`;
2. row identity: exact 17 `row_key` set and no duplicate row keys;
3. repository metadata: `repository_source_name`, `source_mode`, `fallback_used`, `metadata_ok`, and `metadata_reason`;
4. producer diagnostics availability: every available sample must have `diagnostic_payload_available=true`; blocked samples must include unavailable reason and cannot be used for delta interpretation;
5. producer counts: `cell_count`, `text_span_count`, `table_count`, `section_count`, and section/table/semantic count maps;
6. `bundle_content_fingerprint`;
7. `producer_contract_version`;
8. row-level matched diagnostic payloads for the target seven and the three regression rows.

Only if all required comparability checks pass may the evidence report discuss the closure-count delta. Any drift in fingerprint, counts, source metadata, producer contract version, sample identity, or row identity must force verdict `BLOCKED_NON_COMPARABLE_NOT_READY` and must not be described as helper improvement or helper regression.

### Verdict Taxonomy

All future verdicts remain `NOT_READY`:

- `COMPARABLE_PARTIAL_NOT_READY`: all comparability checks passed; at least one row remains residual/blocked; evidence may describe the current row dispositions but still cannot claim source truth, full field correctness, baseline promotion, golden/readiness/release/PR readiness, or parser replacement.
- `BLOCKED_NON_COMPARABLE_NOT_READY`: any fingerprint/count/source metadata/sample identity/row identity/producer contract drift exists; evidence must not interpret helper improvement or regression.
- `DIAGNOSTIC_MISSING_NOT_READY`: required sample-level or row-level producer diagnostics are missing without a precise unavailable reason; evidence must stop before delta interpretation.

No PASS/READY verdict is allowed in this gate.

### Future Commands / Validation

Future required validation commands:

```text
python -m json.tool reports/docling-reference-bundle-residual-closure-reevidence/20260617/residual_closure_matrix.json
```

Expected assertion: JSON parses successfully.

```text
python - <<'PY'
... assert schema_version, no_live, candidate_only, source_truth_status, producer_contract_version, exact 17 row keys, target seven coverage, regression row coverage, fail-closed lock rows, non_claims, sample diagnostics, row diagnostics, and verdict taxonomy ...
PY
```

Expected assertion: all schema, scope, comparability, and non-claim assertions pass.

```text
git diff --check -- reports/docling-reference-bundle-residual-closure-reevidence/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-residual-closure-reevidence-20260617.md
```

Expected assertion: no whitespace errors.

Optional focused no-live validation may be referenced, but must not become a current planning-gate command requirement:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -q
uv run ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Optional validation is only for future evidence worker confidence if they need to prove the existing helper still emits diagnostics. It does not authorize implementation changes.

## Residual Risks

- Producer diagnostics prove comparability mechanics, not source truth or field correctness.
- Real-artifact rerun may expose fingerprint/count drift. That is a valid blocked outcome and must not be repaired inside the evidence gate.
- If a target-seven row changes disposition, the report may record the row-level result only after comparability passes.
- S6-F041, S6-F049, and S6-F050 remain intentionally fail-closed locks unless their exact semantic/hierarchy prerequisites are proven by diagnostics.
- Existing `13 / 4` and `10 / 7` matrices remain historical inputs, not sufficient proof for root-cause attribution.

## Stop Conditions

The future evidence worker must stop and emit a `NOT_READY` verdict if any of the following occurs:

- any write outside the exact allowed write set is needed;
- live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR command would be needed;
- PDF/cache/source-helper direct access, fresh fetch, or repository reload would be needed;
- exact 17-row input scope cannot be reconstructed from accepted artifacts;
- target seven or regression rows cannot be explicitly represented;
- any required sample-level producer diagnostic is missing without unavailable reason;
- any row-level diagnostic payload is missing for a row whose disposition is interpreted;
- sample identity, row identity, source metadata, counts, fingerprint, or producer contract version drift prevents comparability;
- the evidence would need to claim source truth, parser replacement, baseline promotion, full field correctness, golden/readiness/release/PR readiness.

## Completion Report Format

The future evidence report must end with:

```text
Artifact paths:
- reports/docling-reference-bundle-residual-closure-reevidence/20260617/residual_closure_matrix.json
- docs/reviews/docling-reference-bundle-residual-closure-reevidence-20260617.md

Validation:
- python -m json.tool ...: PASS|FAIL
- JSON assertions: PASS|FAIL
- git diff --check ...: PASS|FAIL
- optional focused no-live validation, if run: PASS|FAIL|NOT_RUN

Comparability:
- sample identity: PASS|FAIL
- row identity: PASS|FAIL
- repository metadata: PASS|FAIL
- producer diagnostics availability: PASS|FAIL
- counts: PASS|FAIL
- bundle_content_fingerprint: PASS|FAIL
- producer_contract_version: PASS|FAIL

Verdict: `<COMPARABLE_PARTIAL_NOT_READY|BLOCKED_NON_COMPARABLE_NOT_READY|DIAGNOSTIC_MISSING_NOT_READY>`
Release/readiness: `NOT_READY`
```

## No Over-design Judgment

This plan intentionally does not add:

- production CLI;
- evidence wrapper CLI;
- source truth or golden promotion mechanism;
- baseline promotion mechanism;
- parser replacement path;
- repository/source policy changes;
- helper closure semantic changes;
- live/source access;
- README/control/design synchronization.

The only planned expansion is a bounded evidence JSON/report schema that consumes already accepted residual rows and already implemented producer diagnostics. That is the minimum necessary step before any closure-count delta can be interpreted.

VERDICT: `RESIDUAL_CLOSURE_REEVIDENCE_PLAN_NOT_READY`
