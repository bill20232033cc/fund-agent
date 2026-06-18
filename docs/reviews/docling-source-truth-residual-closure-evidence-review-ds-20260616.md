# Docling Source-truth Residual Closure Evidence Review (AgentDS)

## Scope

- Mode: role-scoped evidence review (not full gateflow)
- Gate: `Docling Source-truth Residual Closure No-live Evidence Gate`
- Assigned role: review worker only, AgentDS
- Review target: evidence matrix + evidence document
- Output file: `docs/reviews/docling-source-truth-residual-closure-evidence-review-ds-20260616.md`
- Included scope: residual_closure_matrix.json, evidence document, source_truth_matrix.json, helper implementation, controller judgment
- Excluded scope: full gateflow restart, plan review, implementation review, controller judgment review

## Findings

未发现实质性问题。

## Validation Checks

### 1. Row Count and Set Correctness

- Source truth matrix: 72 total rows, 55 `source_body_match`, 17 residual (15 `ambiguous_source_body_match` + 1 `source_body_mismatch` + 1 `semantic_assignment_residual`)
- Residual closure matrix: exactly 17 rows
- Fact ID sets are identical between the two matrices, covering S1 (F002, F015, F020), S4 (S4-F001, S4-F002, S4-F015), S5 (S5-F018, S5-F019, S5-F023, S5-F032), S6 (S6-F035 through S6-F038, S6-F041, S6-F049, S6-F050)

### 2. No-Live Guard Semantics

- Evidence document `## No-live Repository Guard` section explicitly documents access path: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only
- States no direct PDF/cache/source-helper access, no Docling conversion, no live/source acquisition, no provider/LLM/analyze commands
- All 4 repository load entries (S1, S4, S5, S6) carry `force_refresh_false: true`, `network_socket_guard: "blocked"`, and `repository_access_only_via_fund_document_repository: true`
- All 17 rows carry identical guard flags in both `guard_flags` and `repository_reference_bundle_status.guard_flags`

### 3. Three-Layer Closure (No Value-Equality-Alone)

- All 10 closed rows (`disambiguated_source_body_match`) carry three non-trivial statuses:
  - `source_layer_status: same_source_reference_loaded`
  - `processed_layer_status: locator_context_available`
  - `fund_layer_status: semantic_rule_satisfied`
- Each closed row has `matched_reference_origin` set to `fund_document_repository_parsed_table`
- Each closed row has specific `matched_row_label_path`, `matched_column_header_path`, and `matched_table_context` entries proving semantic rule satisfaction
- No row is closed solely by normalized text match; all require section_id, row labels, table context, and semantic guard checks per `FIELD_RULES`

### 4. S5-F023 Acceptance

- `source_layer_status: same_source_reference_loaded` — same-source repository reference was loaded
- `matched_reference_origin: fund_document_repository_parsed_table`, `matched_repository_source_name: eid` — same-source proof with traceable origin
- `matched_row_label_path: ["投资目标"]`, `matched_table_context: ["投资目标", "…"]` — semantic context matches `FIELD_RULES["investment_objective"]` requirements: `expected_section_id="§2"`, `required_row_label_any=("投资目标",)`, `semantic_guard="投资目标"`
- `fund_layer_status: semantic_rule_satisfied` — all semantic rule checks passed
- `current_disposition` was `source_body_mismatch` (no match in original source_truth_matrix processing); helper found the match in repository reference bundles via `_source_matches` → `_reference_matches` substring-in-normalized-text check, narrowed by semantic rule

### 5. S6-F041 Preservation

- `closure_disposition: semantic_assignment_residual` — correctly preserved as residual
- `fund_layer_status: semantic_rule_rejected` — benchmark semantic rule rejected
- `original_residual_reason: "benchmark semantics requires benchmark-labeled source context; shared investment-objective candidate locator is insufficient"` — consistent with `FIELD_RULES["benchmark"]` which has `rejected_row_label_any=("投资目标",)` and `semantic_guard="业绩比较基准"`
- No `matched_row_label_path` or `matched_table_context` entries — semantic match was not found

### 6. Guard Flags

All 17 rows carry identical guard flags on both row-level `guard_flags` and `repository_reference_bundle_status.guard_flags`:

| Flag | Value |
|------|-------|
| `candidate_only` | `true` |
| `not_source_truth` | `true` |
| `not_baseline_promotion` | `true` |
| `not_parser_replacement` | `true` |
| `not_full_field_correctness` | `true` |
| `not_release_readiness` | `true` |
| `force_refresh_false` | `true` |
| `network_socket_guard` | `"blocked"` |
| `repository_access_only_via_fund_document_repository` | `true` |

Matrix-level flags (`candidate_only`, `not_baseline_promotion`, `not_full_field_correctness`, `not_parser_replacement`, `not_raw_pdf_bbox_truth`, `not_release_readiness`) are all `true`.

### 7. Summary Counts Internal Consistency

| Field | Summary Value | Manual Count | Match |
|-------|--------------|--------------|-------|
| `rows_total` | 17 | 17 | ✓ |
| `closed_rows_total` | 10 | 10 | ✓ |
| `residual_rows_total` | 7 | 7 | ✓ |
| `closure_dispositions.disambiguated_source_body_match` | 10 | 10 | ✓ |
| `closure_dispositions.semantic_assignment_residual` | 7 | 7 | ✓ |
| `source_layer_statuses.same_source_reference_loaded` | 17 | 17 | ✓ |
| `processed_layer_statuses.locator_context_available` | 17 | 17 | ✓ |
| `fund_layer_statuses.semantic_rule_satisfied` | 10 | 10 | ✓ |
| `fund_layer_statuses.semantic_rule_rejected` | 7 | 7 | ✓ |
| `s5_f023_closed_with_same_source_proof` | `true` | confirmed | ✓ |
| `s6_f041_preserved_residual` | `true` | confirmed | ✓ |

### 8. Input Artifact Hash

- `source_truth_matrix_artifact.path`: `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`
- `source_truth_matrix_artifact.sha256` in matrix: `a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`
- Actual `sha256sum` of file: `a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`
- Match confirmed

### 9. Evidence Document ↔ Matrix Row Consistency

All 17 rows in the evidence document per-row table were cross-checked against the matrix JSON. All `source_layer_status`, `processed_layer_status`, `fund_layer_status`, `closure_disposition`, and `closure_reason` values are identical between the evidence document table and the matrix rows. No discrepancies found.

### 10. Helper Contract Boundary

The helper (`source_truth_residual_closure.py`) module docstring states it does not read files, call `FundDocumentRepository`, call Docling, call source helpers, or construct production `EvidenceAnchor`. The evidence document states repository access happened separately via `FundDocumentRepository.load_annual_report(..., force_refresh=False)` under no-live guard semantics before invoking the helper. This boundary was respected.

## Verdict

**PASS**

## Open Questions

无。

## Residual Risk

- The helper's `_reference_matches` function uses substring matching (`candidate in normalized_text`), which could in principle produce false-positive matches for very short candidate values. This risk is mitigated by the three-layer semantic rule check that narrows matches by section, row labels, column headers, table context, and semantic guard. No instance of false-positive closure was observed in this 17-row matrix.
- The 7 residual rows (F015, F020, S4-F015, S5-F032, S6-F041, S6-F049, S6-F050) remain blocked on fund semantic context. Their `same_source_reference_loaded` / `locator_context_available` status confirms the data is present but the semantic rules cannot yet resolve the correct assignment. This is expected under the current candidate-only scope.
- This evidence review does not cover the repository reference bundle construction step (how cells/text_spans were extracted from the cache). That step belongs to a prior gate; only its outputs are consumed here.
