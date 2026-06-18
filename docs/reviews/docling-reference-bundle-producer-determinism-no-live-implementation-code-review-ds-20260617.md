# Docling Reference Bundle Producer Determinism No-live Implementation Code Review DS - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism No-live Implementation Gate`
Role: code review worker (DS)
Status: `CODE_REVIEW_PASS_NOT_READY`
Verdict: `CODE_REVIEW_PASS_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Approved plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
- Controller acceptance: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-acceptance-controller-judgment-20260617.md`
- Implementation evidence: `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md`
- Review target: `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- Review target: `tests/fund/documents/test_docling_source_truth_residual_closure.py`

## Review Scope

Per gateflow handoff: code review worker only. Review criteria as specified in the handoff instruction. No controller action, no edit, no fix, no commit, no push, no PR, no release, no closeout.

## Slice-by-Slice Verification

### Slice 1 — Deterministic Diagnostic Models

`PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"` added at source:106.

Deterministic helpers added:

- `_diagnostic_normalized_text` (source:1925–1939): null→"", `re.sub(r"\s+", " ", text).strip()`. Matches plan contract exactly.
- `_normalized_text_hash` (source:1908–1922): `hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()` via `_diagnostic_normalized_text`. Matches plan.
- `_raw_text_excerpt` (source:1942–1957): truncates at `_RAW_TEXT_EXCERPT_CODEPOINT_LIMIT=200` code points, appends `...` when truncated, max 203 code points. Matches plan.
- `_bundle_content_fingerprint` (source:1886–1905): `json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")` → `sha256.hexdigest()`. Exact match to plan serialization spec.
- `_cell_sort_key` (source:1720–1746): `(sample_id, fund_code, document_year, page_number, table_id, row_index, column_index, normalized_text_hash)`. Matches plan.
- `_text_span_sort_key` (source:1749–1774): `(sample_id, fund_code, document_year, page_number, section_id, context_label, normalized_text_hash)`. Matches plan.
- `_match_sort_key` (source:1696–1717): delegates to cell/span sort key with `"cell"`/`"text_span"` prefix. Determistic.

All helpers are file-read free, repository-free, source-helper-free, candidate-only. Confirmed by `test_pure_helper_boundary_does_not_read_or_call_repository` (test:2334–2359) which monkeypatches `builtins.open` to assert failure on any file read.

### Slice 2 — Bundle Diagnostic Summary

`_bundle_diagnostic_summary` (source:1095–1165) added and wired into `RepositoryReferenceBundle.to_dict()` (source:439).

Bundle-level diagnostics emitted:

- `producer_contract_version` — companion metadata, NOT in fingerprint
- `producer_input_mode` — `raw_legacy_v1` or `pre_enriched_v2`, in fingerprint
- `cell_count`, `text_span_count` — in fingerprint
- `table_count` (source:1795–1819) — unique `(fund_code, document_year, source, section, table_id)` tuples
- `section_count` (source:1822–1841) — unique diagnostic section_ids
- `table_family_counts` — from cell.table_family Counter, in fingerprint
- `section_inference_counts` — per-section occurrence count across cells+spans, in fingerprint
- `section_inference_reason_counts` — `explicit_section_id` vs `missing_section_id`, in fingerprint
- `row_hierarchy_role_counts` — from cell.row_hierarchy_role Counter, in fingerprint
- `text_semantic_context_counts` — from span.semantic_context_label Counter, in fingerprint
- `bundle_content_fingerprint` — SHA256 of fingerprint_payload per plan spec; None when `diagnostic_payload_available=false`
- `diagnostic_payload_available` — companion metadata, NOT in fingerprint

Fingerprint payload (source:1131–1148) contains only the 12 fields listed in plan §Bundle-level contract hash-participating content. Companion metadata fields are emitted in the return dict (source:1149–1165) but excluded from `fingerprint_payload`.

`_producer_input_mode` (source:1777–1792): returns `raw_legacy_v1` when `reference_bundle_schema_version == "repository_reference_bundle.v1"`, else `pre_enriched_v2`. Correct.

`_sorted_cells` and `_sorted_text_spans` sort via the plan-specified sort keys before hash extraction. Hash order in fingerprint is deterministic.

### Slice 3 — Row-level Diagnostic Payload

`ResidualClosureResultRow.diagnostic_payload` field added (source:496) as `Mapping[str, object] | None`.

Three diagnostic payload constructors:

1. `_selected_match_diagnostic_payload` (source:1168–1189): for closed rows and semantic-equivalent duplicate rows. Emits `diagnostic_kind="selected_reference_match"`, `normalized_candidate_hash`, and `selected_reference_diagnostic` from `_match_diagnostic`.

2. `_source_absent_diagnostic_payload` (source:1192–1215): for `source_body_mismatch` rows. Emits `diagnostic_kind="candidate_search_no_source_match"`, searched cell/span counts, and bounded `candidate_search_diagnostics` via `_bounded_reference_diagnostics` (source:1257–1290). Limited to `_ROW_DIAGNOSTIC_CANDIDATE_LIMIT=20` per category.

3. `_semantic_residual_diagnostic_payload` (source:1218–1254): for `semantic_assignment_residual` rows. Sorts source matches by deterministic `_match_sort_key`, limits to 20, and includes per-match `rejection_categories` via `_semantic_rejection_categories` (source:1293–1494).

Cell-level diagnostic fields (source:1540–1579): all 19 fields from plan §Cell-level diagnostic contract present, including `normalized_text_hash` and `raw_text_excerpt`.

Text-span diagnostic fields (source:1582–1610): all 8 fields from plan §Text-span diagnostic contract present.

`diagnostic_payload_available` in result row `to_dict()` (source:511): `True` when `diagnostic_payload is not None`.

All diagnostics derived from already-loaded bundle; no repository reload, no PDF/cache/source-helper access.

## Closure Semantics Verification

FIELD_RULES (source:613–729) unchanged from prior accepted state. No rule relaxed.

`_match_satisfies_rule` (source:966–1064) unchanged. No predicate made more permissive.

`_close_row` (source:775–887) adds diagnostic payload pass-through to `_result()` calls. Closure disposition logic unchanged.

`_processed_status` (source:890–926) unchanged. Candidate metadata guards intact.

### S6-F041 — Benchmark Guard

Verified via test matrix:

| Test | Scenario | Expected | Actual |
|------|----------|----------|--------|
| test:1465 | investment objective cell context | `semantic_assignment_residual` | PASS |
| test:1490 | benchmark semantic text span | `disambiguated_source_body_match` | PASS |
| test:1490 | investment_objective text span | `semantic_assignment_residual` | PASS |
| test:1529 | diagnostic shows `required_text_semantic_context_absent` | PASS | PASS |
| test:1644 | investment objective raw text mentions benchmark | `semantic_assignment_residual` | PASS |
| test:1670 | ambiguous benchmark+objective labels | `semantic_assignment_residual` | PASS |
| test:1696 | benchmark label outside §2 | `semantic_assignment_residual` | PASS |
| test:1723 | context_label objective overrides heading benchmark | `semantic_assignment_residual` | PASS |

S6-F041 remains residual on investment-objective text. Closes only with benchmark semantic context. Fail-closed as planned.

### S6-F049 / S6-F050 — Portfolio Hierarchy

Verified via test matrix:

| Test | Scenario | Expected | Actual |
|------|----------|----------|--------|
| test:982 | v2 identical values without hierarchy | both `semantic_assignment_residual` | PASS |
| test:1099 | v1 enrichment with hierarchy proven | both `disambiguated_source_body_match` | PASS |
| test:1148 | v1 stock child without equity parent | `semantic_assignment_residual` | PASS |
| test:1268 | v1 neighbor labels don't prove hierarchy | `semantic_assignment_residual` | PASS |
| test:1295 | v1 detail row breaks parent-child bridge | `semantic_assignment_residual` | PASS |
| test:1335 | v1 new top-level asset resets parent scope | `semantic_assignment_residual` | PASS |
| test:2069 | equity_amount only closes aggregate, not child/detail | PASS | PASS |
| test:2124 | stock_amount only closes child under equity parent | PASS | PASS |

S6-F049/S6-F050 cannot close by value equality alone. Hierarchy must be proven. Fail-closed as planned.

### Other Regression Guards

- `test:1375`: v2 bundle with unknown hierarchy is NOT repaired by v1 enrichment. PASS.
- `test:1208`: `其中：普通股` not in current stock FIELD_RULES, remains residual. PASS.
- `test:1750`: `bounded_neighbor_row_labels` do not prove positive hierarchy. PASS.
- `test:1440`: new `rejected_table_families` takes precedence over legacy `required_table_family_any`. PASS.
- `test:859`: ambiguous table family resolves to `unknown`. PASS.
- `test:687`: invalid literals become `unknown` and fail target predicates. PASS.
- `test:1793`: `locator_context_conflict` blocks closure. PASS.

## Boundary Confirmation

- `candidate_only=true` preserved in output matrix (source:553). Verified by test:2276.
- `source_truth_status=not_proven` preserved in output rows (source:494). Verified by test:2276.
- `NOT_READY` flags preserved: `not_baseline_promotion`, `not_parser_replacement`, `not_release_readiness`, `not_full_field_correctness`, `not_raw_pdf_bbox_truth` all `True` (source:548–552). Verified by test:2276.
- No source truth acceptance claim.
- No Docling baseline promotion.
- No parser replacement claim.
- No full field correctness claim.
- No golden/readiness/release/PR claim.
- No live/network/provider/LLM access added.
- No direct PDF/cache/source-helper access added. Verified by test:2334.
- No repository reload. `FundDocumentRepository` and `load_annual_report` absent from module. Verified by test:2334.
- No evidence wrapper, production CLI, or future-slice implementation.

## Test Coverage Assessment

89 tests pass. Coverage spans all required categories:

1. **Determinism** (4 tests):
   - `test:364` — producer diagnostics emit with correct fingerprint
   - `test:426` — fingerprint stable under input order variation
   - `test:479` — fingerprint changes when hash-participating content changes
   - `test:479` — companion-only metadata changes do NOT affect fingerprint

2. **Boundary** (4 tests):
   - `test:510` — normalization, hash, and excerpt upper bound (203 code points)
   - `test:528` — missing bundle diagnostics don't infer comparability
   - `test:2334` — pure helper boundary (monkeypatched open)
   - `test:2276` — output guard flags preserved

3. **Diagnostic sufficiency** (5+ tests):
   - `test:1529` — S6-F041 benchmark_label_absent diagnostic
   - `test:1775` — S6-F035 unknown hierarchy rejection diagnostic
   - `test:1823` — S5-F023 source_absent search diagnostic
   - `test:1946` — F015 share/period rejection diagnostic
   - `test:1858` — unresolved expense duplicate emits diagnostic

4. **Regression guards** (20+ tests):
   - S6-F041 benchmark guards: 8 tests (see above)
   - S6-F049/S6-F050 portfolio hierarchy: 8 tests (see above)
   - Table family classifier: 2 tests
   - Literal coercion: 1 test
   - Share/period derivation: 1 test
   - And more

## Findings

Finding count: 0.

No contract drift, no bugs, no missing tests, no type-safety issues, no overbroad changes, no scope violations identified.

## Completion Report

- **Artifact path**: `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-code-review-ds-20260617.md`
- **Verdict**: `CODE_REVIEW_PASS_NOT_READY`
- **Finding count**: 0
- **Boundary confirmation**: 
  - `candidate_only=true` preserved
  - `source_truth_status=not_proven` preserved
  - `NOT_READY` preserved
  - No source truth acceptance
  - No baseline promotion
  - No parser replacement
  - No release/readiness/PR/golden claim
  - No live/network/provider/LLM access
  - No direct PDF/cache/source-helper access
  - No repository reload
- **Closure semantics**: unchanged. S6-F041, S6-F049, S6-F050 remain fail-closed as planned.
- **Producer contract version**: `docling_reference_bundle_producer_contract.v1` bound.
- **Implementation follows**: accepted plan slices 1–3 only. Future evidence wrapper/CLI not implemented.
- **Self-check**: pass.
