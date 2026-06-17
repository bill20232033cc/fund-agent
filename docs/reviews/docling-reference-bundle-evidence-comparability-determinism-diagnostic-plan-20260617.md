# Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Plan - 2026-06-17
Status: DRAFT_FOR_REVIEW

Gate: `Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Planning Gate`
Role: planning worker only
Planned next gate type: no-live diagnostic evidence gate
Implementation context: accepted commit `7f1d0f6`

## Goal

Design the next no-live diagnostic gate to isolate why the re-evidence result regressed from the prior accepted checkpoint before any further residual-closure re-evidence is attempted.

First-principles motivation: a residual-closure result is meaningful only when the input representation construction is comparable and deterministic. If two checkpoints feed different raw legacy reference bundles into the same closure helper, row closures can change because of wrapper construction drift rather than because the accepted helper improved or regressed. The next gate must therefore answer whether the evidence wrapper/reference bundle producer changed cell counts, text span construction, section inference, row labels, column headers, or table context in a way that makes the two closure matrices non-comparable.

## Non-goals

- No Docling baseline promotion.
- No source truth acceptance.
- No parser replacement.
- No full field correctness claim.
- No readiness, release, PR, golden, or quality-gate claim.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release commands.
- No source/test/runtime/control/design/README edits in the diagnostic evidence gate.
- No direct PDF/cache/source-helper access.
- No attempt to force closure counts back to `13/4` or improve residual closure inside this diagnostic gate.

## Current Accepted Facts

- Prior accepted checkpoint: `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`.
- Prior result: `17` rows total, `13` closed, `4` residual.
- Current re-evidence artifact: `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`.
- Current result: `17` rows total, `10` closed, `7` residual.
- Delta: `-3` closed rows versus prior.
- Current verdict is valid blocked/regression evidence: `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`.
- Regression rows versus prior:
  - `S1 F015 sales_service_fee_C_current_year`: prior `disambiguated_source_body_match`; current `semantic_assignment_residual`.
  - `S5 S5-F023 investment_objective`: prior `disambiguated_source_body_match`; current `source_body_mismatch`.
  - `S6 S6-F035 fund_name`: prior `disambiguated_source_body_match`; current `semantic_assignment_residual`.
- Target seven current status: `2/7` closed, `5/7` residual.
- Target seven prior status: `3/7` closed, `4/7` residual.
- `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY` remain binding.

## Diagnostic Questions

The diagnostic evidence gate must answer these questions without changing closure behavior:

1. Are the two evidence matrices comparable at the repository load aggregate level?
   - Compare `cell_reference_count`, `text_span_count`, `table_count`, `section_count`, metadata flags, `parsed_cache_hit`, and source mode per sample.
   - Current count drift already visible from committed artifacts:
     - `S1`: prior cells/text spans `3201/8`; current `3247/6`.
     - `S4`: prior `2529/8`; current `2561/6`.
     - `S5`: prior `6739/6`; current `6805/6`.
     - `S6`: prior `5665/8`; current `5633/6`.
2. Did section inference drift?
   - Compare `section_inference_counts` per sample, including `unknown`, `§2`, `§7`, `§8`, `§10`.
   - Compare `section_inference_reason_counts` per sample.
   - Flag any sample where a section count differs, even if closure rows are unchanged.
3. Did row-level matched context drift for closed/regressed rows?
   - Compare `closure_disposition`, `source_layer_status`, `fund_layer_status`, `matched_row_label_path`, `matched_column_header_path`, and `matched_table_context` for all 17 rows.
   - For the three regression rows, explicitly show prior matched context versus current empty/unresolved context:
     - `F015`: prior matched row `当期发生的基金应支付的销售服务费 > 安信基金`; current no matched context.
     - `S5-F023`: prior matched row `投资目标`, column `table_header`; current source text absent.
     - `S6-F035`: prior matched row `基金名称`, column `table_header`; current no matched context.
4. Did text span construction drift?
   - Compare `text_span_count` by sample.
   - For text-backed rows such as `S5-F023`, `S6-F035`, and `S6-F041`, determine whether current `same_source_text_absent` is explainable by wrapper text span slicing, label selection, normalization, or section assignment.
   - If the committed matrices cannot expose raw text span contents, record that limitation and stop before repository reload unless explicitly authorized.
5. Did raw legacy v1 bundle schema or enrichment boundary drift?
   - Confirm both matrices report `reference_bundle_schema_version=repository_reference_bundle.v1(raw legacy; helper enrichment delegated)`.
   - Confirm neither wrapper prefilled v2 hierarchy/semantic fields.
   - Confirm current helper file hash and accepted implementation commit context.
6. Is the count/context drift caused by wrapper construction or helper logic?
   - Prefer JSON-only evidence: if repository load counts, section inference, text spans, or matched context differ before helper semantics, classify as wrapper/reference-bundle construction drift.
   - Only if JSON artifacts are insufficient should the later evidence gate request repository-mediated annual report object access through `FundDocumentRepository.load_annual_report(..., force_refresh=False)` with socket guard.

## Allowed Evidence Inputs

The diagnostic evidence gate should read only these committed files first:

- `AGENTS.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-controller-judgment-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md`
- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-controller-judgment-20260617.md`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` for helper hash/API context only; no code changes.

If, and only if, committed JSON artifacts cannot isolate the producer drift, the next gate may propose a separate follow-up evidence gate that loads annual report objects via `FundDocumentRepository.load_annual_report(..., force_refresh=False)` under a `socket.socket.connect/connect_ex` guard. That follow-up must still avoid direct PDF/cache/source-helper access.

## Planned Output Artifacts

Future evidence gate write set should be limited to:

- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`

No source, tests, runtime, control, design, README, baseline, golden, or PR artifacts should be written.

## Proposed Diagnostic Matrix Schema

`comparability_matrix.json` should include:

- `schema_version`: `docling_reference_bundle_comparability_diagnostic.v1`
- `gate`: diagnostic gate name.
- `candidate_only`: `true`
- `not_source_truth`: `true`
- `not_baseline_promotion`: `true`
- `not_parser_replacement`: `true`
- `not_full_field_correctness`: `true`
- `not_release_readiness`: `true`
- `not_ready`: `true`
- `inputs`: path and sha256 for current matrix, prior matrix, current report, controller judgment, helper file.
- `comparison_basis`: `committed_json_artifacts_only` unless a later approved gate explicitly loads repository objects.
- `repository_load_comparison`: per sample prior/current/delta for:
  - `cell_reference_count`
  - `text_span_count`
  - `table_count`
  - `section_count`
  - metadata fields
  - `section_inference_counts`
  - `section_inference_reason_counts`
- `row_comparison`: all 17 rows with prior/current:
  - `sample_id`
  - `fact_id`
  - `field_name`
  - `closure_disposition`
  - `source_layer_status`
  - `processed_layer_status`
  - `fund_layer_status`
  - `matched_row_label_path`
  - `matched_column_header_path`
  - `matched_table_context`
  - `source_truth_status`
  - `regression_flag`
  - `comparability_class`
- `target_seven_comparison`: focused table for `F015`, `F020`, `S4-F015`, `S5-F032`, `S6-F041`, `S6-F049`, `S6-F050`.
- `regression_rows`: exactly `F015`, `S5-F023`, `S6-F035` unless evidence changes during review.
- `diagnostic_findings`: machine-readable findings such as:
  - `repository_load_count_drift`
  - `section_inference_drift`
  - `text_span_count_drift`
  - `matched_context_drift`
  - `source_layer_status_drift`
  - `json_artifacts_insufficient_for_root_cause`
- `summary`:
  - `rows_total`
  - `regression_rows_total`
  - `samples_with_count_drift`
  - `samples_with_section_inference_drift`
  - `target_seven_prior_closed`
  - `target_seven_current_closed`
  - `verdict`

Suggested diagnostic verdict tokens:

- `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_HELPER_DRIFT_SUSPECTED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_INSUFFICIENT_JSON_EVIDENCE_BLOCKED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_NO_DRIFT_FOUND_BLOCKED_NOT_READY`

## Evidence Report Requirements

`docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md` must include:

- Inputs and sha256 hashes.
- Commands run.
- Explicit statement that comparison used committed JSON artifacts first.
- No-live/source boundary confirmation.
- Summary table comparing prior `13/4` and current `10/7`.
- Per-sample repository load comparison table.
- Per-sample section inference comparison table.
- Per-row comparison table for all 17 rows.
- Focused regression table for `F015`, `S5-F023`, `S6-F035`.
- Focused target seven comparison.
- Classification of whether each observed drift is wrapper/reference-bundle construction drift, helper behavior drift, or insufficient evidence.
- Explicit statement that current `10/7` artifact remains valid blocked/regression evidence and is not overwritten by this diagnostic.
- Validation results.
- Final verdict token.
- Self-check.

## Implementation Steps for Future Evidence Worker

1. Read all allowed input files.
2. Compute sha256 for each input.
3. Load current and prior matrices as JSON.
4. Assert both matrices have `rows_total=17`; if not, stop with `COMPARABILITY_DIAGNOSTIC_INSUFFICIENT_JSON_EVIDENCE_BLOCKED_NOT_READY`.
5. Build a row index keyed by `(sample_id, fact_id, field_name)` for both matrices.
6. Build `repository_load_comparison` keyed by `sample_id`.
7. For every sample, compute deltas for counts and exact diff objects for `section_inference_counts` and `section_inference_reason_counts`.
8. Build `row_comparison` for all 17 rows:
   - mark `regression_flag=true` when prior closed and current not closed;
   - mark `improvement_flag=true` only if current closed and prior not closed;
   - compare matched row/header/table context arrays exactly;
   - preserve `source_truth_status=not_proven`.
9. Build a focused diagnostic record for `F015`, `S5-F023`, and `S6-F035`.
10. Build a focused target seven comparison.
11. Classify drift:
   - If repository load counts, section inference counts, text span counts, or matched context differ while helper commit is fixed, classify as `wrapper_or_reference_bundle_construction_drift`.
   - If counts/context are identical but closure differs, classify as `helper_behavior_or_rule_path_drift_suspected`.
   - If raw bundle fields needed to determine root cause are absent from committed JSON, classify as `json_artifacts_insufficient_for_root_cause` and stop before repository reload.
12. Write `comparability_matrix.json`.
13. Write markdown evidence report.
14. Run validation commands only.
15. Stop and report paths, verdict, regression rows count, and whether further repository-mediated diagnostic authorization is needed.

## Allowed Commands for Future Evidence Gate

Read-only commands:

```text
sed -n '...' <allowed-input>
jq '...' <allowed-json>
rg '...' <allowed-inputs>
```

No-live artifact generation:

```text
uv run python -B - <<'PY' ... PY
```

Validation:

```text
python -m json.tool reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
jq -e '.candidate_only == true and .not_source_truth == true and .not_ready == true and (.row_comparison | length == 17)' reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
jq -e '.summary.regression_rows_total == 3' reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
git diff --check -- reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md
```

Forbidden commands remain forbidden even if they look useful:

- repository acquisition unless explicitly authorized in a later gate;
- live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- direct PDF/cache/source-helper access;
- stage/commit/push/PR.

## Review Gates

After the diagnostic evidence artifacts are written:

1. AgentDS evidence review:
   - Check JSON/report consistency.
   - Check that count/context drift conclusions are supported by committed matrix fields.
   - Check no source truth/baseline/readiness claims slipped in.
2. AgentMiMo evidence review:
   - Challenge comparability classification.
   - Confirm regression rows and target seven summaries match current/prior artifacts.
   - Confirm no unauthorized repository/PDF/cache/source-helper access.
3. Controller judgment:
   - Accept as diagnostic evidence, or block for artifact inconsistency.
   - Decide whether the next gate should be a wrapper determinism implementation gate, a repository-mediated diagnostic gate, or a residual-closure re-evidence retry.

## Stop Conditions

The future evidence worker must stop without widening scope if any of these occur:

- The committed JSON artifacts do not contain enough data to attribute root cause.
- A repository reload appears necessary.
- Any direct PDF/cache/source-helper access would be needed.
- Any live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR command would be needed.
- Any code/test/runtime/control/design/README change appears necessary.
- Any result would be interpreted as Docling baseline promotion, source truth acceptance, parser replacement, full correctness, or readiness.
- The two matrices cannot be aligned to the same 17 residual rows.

## Completion Report Format

The future evidence worker final response should be concise and include:

- Artifact paths written.
- Diagnostic verdict token.
- Prior/current closure counts: `13/4` versus `10/7`.
- Regression rows count and IDs.
- Whether wrapper/reference-bundle construction drift was identified.
- Whether repository-mediated follow-up is blocked/needed.
- Validation command results.
- Boundary confirmation: candidate-only, `source_truth_status=not_proven`, `NOT_READY`, no stage/commit/push/PR.

## Residual Risks

- Current and prior matrices expose aggregate counts and matched contexts, but may not expose full raw cell/text span payloads. That may be enough to identify non-comparability but not enough to prove the exact producer line that caused drift.
- `text_span_count` and section inference drift can indicate wrapper construction drift, but exact raw span slicing may require a separately authorized repository-mediated diagnostic.
- A successful comparability diagnostic does not close any residual row; it only decides whether another re-evidence run would be meaningful.

Final planning verdict: `HANDOFF_READY_NOT_READY`
