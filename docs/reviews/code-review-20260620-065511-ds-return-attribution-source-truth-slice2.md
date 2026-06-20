# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Slice 2 Code Review

## Gate Metadata

- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate - Slice 2`
- Review target: Slice 2 value extraction diff (`fund_disclosure_processor.py`, test file, evidence doc)
- Reviewer: AgentDS (review-only; no code/modify/commit/push/PR)
- Classification: `heavy`
- Accepted references: plan, plan controller judgment, Slice 1 controller judgment, Slice 2 evidence
- Verdict: `PASS`

---

## Scope Verification

- [x] Only Slice 2 value extraction: `_extract_return_attribution_source_truth` and field-specific helpers
- [x] Public value shape only `schema_version`, `nav_benchmark_performance`, `fee_schedule`, `tracking_error`
- [x] `TrackingErrorValue` construction supplies all required fields with correct direct-disclosure semantics
- [x] NAV/benchmark same-row deterministic, fee parsing fail-closed
- [x] Tracking error target/control/limit contexts rejected via `_RETURN_ATTRIBUTION_TRACKING_ERROR_REJECT_CONTEXT`
- [x] Missing/partial/accepted status and `extraction_mode` correct; direct route keeps `candidate_evidence == ()`
- [x] No unauthorized schema expansion, source policy/repository/facade/docs changes, other field families, parser replacement, upper-layer consumption, readiness/release claim, or live/network commands

---

## Findings

### Finding 1 — Tracking error cell matching includes table-level context (INFO, not blocking)

**File**: `fund_agent/fund/processors/fund_disclosure_processor.py:1144`

`_collect_return_attribution_tracking_error_candidates` uses `_return_attribution_cell_context_text(table, cell)` to construct matching context for tracking error. This context includes `table.heading_text`, `table.table_caption_or_nearby_heading`, and the full table heading path. A percent-value cell whose own row/column labels do not reference tracking error could still be matched if the parent table heading mentions tracking error labels.

The risk is low because:
1. FDD tracking error tables are typically single-purpose.
2. `_return_attribution_tracking_error_rejected` still applies to the full context.
3. Conflict resolution (`_resolve_return_attribution_candidate`) catches duplicate candidates.
4. The cell-level `value_text` must still be a parseable percent, which is strongly correlated with actual tracking error values in a tracking error table.

This is a design choice consistent with the plan's label matching requirements; the broader context helps catch cases where the tracking error label appears in a merged header rather than the cell's immediate row/column path.

### Finding 2 — Ambiguous path and partial top-level gap can both fire (INFO, not blocking)

**File**: `fund_agent/fund/processors/fund_disclosure_processor.py:1868–1925`

When `nav_benchmark_performance` is ambiguous (multiple same-row pairs), `_select_return_attribution_nav_benchmark_values` adds it to `ambiguous_paths` and returns empty `{}`. Then `_return_attribution_source_truth_gaps` generates both:
- `ambiguous_table_or_locator` gap with `source_field_path="nav_benchmark_performance"`
- `field_family_partial` gap for `nav_benchmark_performance` (since it's absent from the value dict)

This double-reports the same underlying cause. Not a contract violation — the ambiguity gap explains *why*, and the partial gap states *what* is missing — but the redundancy is notable. The gap API accepts it; the call semantic is slightly noisy.

### Finding 3 — No table-cell-specific tracking error rejection test (MINOR, non-blocking)

The rejection test `test_return_attribution_source_truth_rejects_tracking_error_target_context` (line 1929) tests only paragraph-level rejection. Table-cell-level tracking error rejection uses the same `_return_attribution_tracking_error_rejected` function (line 1147) on the combined context, so behavior is consistent across sources. However, a focused table-cell rejection test would close a test coverage gap for the table path's context assembly (`_return_attribution_cell_context_text`).

### Finding 4 — Redundant candidate_evidence assignment preserved from Slice 1 (INFO, non-blocking, previously accepted)

**File**: `fund_agent/fund/processors/fund_disclosure_processor.py:778–781`

```python
return_attribution_evidence = _select_return_attribution_candidate_evidence(intermediate)
return_attribution_evidence = (
    () if return_attribution_source_truth is not None else return_attribution_evidence
)
```

The first assignment on line 778 is unconditionally overwritten on line 779. This was noted in the Slice 1 AgentMiMo review and accepted as non-blocking. No behavioral effect.

---

## Validation Reviewed

### Public Value Shape

- [x] Top-level keys: only `schema_version`, `nav_benchmark_performance`, `fee_schedule`, `tracking_error` — verified at `_build_return_attribution_value:1699–1726`
- [x] `schema_version` is `"return_attribution.v1"`
- [x] `nav_benchmark_performance` contains only `nav_growth_rate` and `benchmark_return_rate`
- [x] `fee_schedule` contains only `management_fee` and `custody_fee`; one-side-as-None allowed for partial
- [x] `tracking_error` is `TrackingErrorValue` instance (not bare string)

### TrackingErrorValue Construction

- [x] `value`: Decimal ratio via `_return_attribution_percent_ratio` — line 1629
- [x] `value_text`: percent text via `_return_attribution_percent_text` — line 1608
- [x] `unit`: `"ratio"`
- [x] `period_label`: human-readable from row label/heading/paragraph context — `_return_attribution_cell_period_label:1277`, `_return_attribution_paragraph_period_label:1480`
- [x] `period_start`: `None`, `period_end`: `None` — unavailable for direct disclosure
- [x] `annualized`: True when `"年化"` in context text
- [x] `source_type`: `"direct_disclosure"`
- [x] `calculation_method`: `"disclosed"`
- [x] `benchmark_identity_status`: `"missing"` — no benchmark identity from FDD direct disclosure
- [x] `benchmark_index_name`: `None`, `benchmark_index_code`: `None`
- [x] `fund_series_source`: `None`, `index_series_source`: `None`
- [x] `observation_count`: `None`
- [x] `frequency`: `"annual_report_period"` — matches controller judgment: `frequency` uses this, `period_label` is human-readable
- [x] `annualization_factor`: `None`
- [x] `input_period_complete`: `True` — direct disclosure has no partial-period concern
- [x] `provenance_note`: disclaims series/benchmark/stddev derivation — line 1549

### NAV/Benchmark Same-Row Determinism

- [x] NAV and benchmark values paired within same table by `row_index` — `_select_return_attribution_nav_benchmark_values:1008–1064`
- [x] Missing either side → subvalue omitted (fail closed)
- [x] Multiple same-row pairs → `ambiguous_paths.add("nav_benchmark_performance")`, returns `{}` (fail closed)
- [x] Only stable locators accepted; unstable table/cell skipped
- [x] Generic cell texts (labels themselves) rejected via percent parsing

### Fee Parsing Determinism

- [x] Table cells: label match via `_match_return_attribution_fee_cell_output_path`, percent value required — `_collect_return_attribution_fee_candidates:1067–1114`
- [x] Paragraph fallback: explicit label-starting text with percent — `_return_attribution_fee_paragraph_candidate:1378–1423`
- [x] Label-only or non-percent cells rejected
- [x] Sales service fee excluded from public value (candidate-only)
- [x] Duplicate conflicting values → omission with ambiguity gap

### Tracking Error Target/Control/Limit Rejection

- [x] Rejected tokens: `目标`, `控制`, `不超过`, `力争`, `偏离度绝对值` — `_RETURN_ATTRIBUTION_TRACKING_ERROR_REJECT_CONTEXT:165–171`
- [x] Table path: context assembled via `_return_attribution_cell_context_text` → `_return_attribution_tracking_error_rejected`
- [x] Paragraph path: same rejection check on paragraph text — `_return_attribution_tracking_error_paragraph_candidate:1450`
- [x] Normalization via `_normalize_match_text` removes whitespace for token matching

### Status / extraction_mode

- [x] `accepted` when all three top-level present — `_return_attribution_status:1941`
- [x] `partial` when at least one present but not all — line 1944
- [x] `missing` when none present — line 1945
- [x] `extraction_mode="direct"` for `accepted` and `partial` — `_extract_return_attribution_source_truth:941`
- [x] `extraction_mode="missing"` for `missing`
- [x] `candidate_evidence == ()` in all direct routes — line 945

### Gap Behavior

- [x] `field_family_missing` when no allowed value formed — `_return_attribution_source_truth_gaps:1903`
- [x] `field_family_partial` for each missing required top-level — line 1915
- [x] `ambiguous_table_or_locator` for duplicate conflicting paths — line 1889
- [x] Result-level gaps untouched for field-local gaps

### Anchor Behavior

- [x] `source_kind` is `"annual_report"` on all public anchors
- [x] `document_year` from dispatch context
- [x] `page_number` is `None` (no page-level source-truth mapping for FDD)
- [x] `row_locator` includes `field=<output_path>` with stable table/cell or paragraph identity
- [x] Anchors deduped via `_dedupe_anchors`
- [x] Only emitted output paths produce anchors

### Boundary Preservation

- [x] No `EvidenceSourceKind` expansion
- [x] No `EvidenceAnchor` field expansion
- [x] No other field family (manager_profile, investor_experience, current_stage, core_risk) source-truth extraction
- [x] No parser replacement
- [x] No `FundDocumentRepository` / source policy / fallback / cache / PDF change
- [x] No Service/UI/Host/renderer/quality-gate change
- [x] No live/network/PDF/FDR/Docling conversion/pdfplumber export/LLM command
- [x] No readiness/release claim

### Test Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
133 passed in 0.87s

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!

git diff --check
PASS: no output
```

Key tests verified:
- `test_return_attribution_source_truth_extracts_exact_value_shape` — full shape, all 3 subvalues, 5 anchors, source_kind assertion
- `test_return_attribution_source_truth_partial_when_required_groups_missing` — partial + field_family_partial gaps
- `test_return_attribution_source_truth_missing_when_no_allowed_labels` — missing + field_family_missing + candidate_evidence=()
- `test_return_attribution_source_truth_fee_schedule_one_side_is_partial` — one-sided fee as partial
- `test_return_attribution_source_truth_nav_requires_both_sides_same_row` — parametrized: missing NAV or different-row
- `test_return_attribution_source_truth_tracking_error_actual_disclosure_value` — TrackingErrorValue all fields
- `test_return_attribution_source_truth_rejects_tracking_error_target_context` — target/control rejection
- Slice 1 guard tests still pass (proof-missing, candidate-boundary, base-admission-invalid paths)
- S6-C candidate-only tests still pass

---

## Required Fixes

None.

---

## Residual Risks

1. **Real-report field correctness unproven**: synthetic FDD stubs are used; actual FDD content from real annual reports may not match label patterns, table structures, or paragraph text conventions assumed here. Owner: future evidence gate.
2. **Tracking error table-cell false matches**: table-heading-level `_return_attribution_mentions_tracking_error` could match percent cells from non-tracking-error rows in a tracking-error-themed table. Low probability in practice; conflict resolution mitigates. Owner: later field-specific evidence/refinement gate if needed.
3. **FDD protocols may lack stable locator labeling**: table heading text, row labels, and cell id conventions in production FDD may differ from stubs. Owner: future evidence gate.
4. **Multi-table NAV/benchmark**: `_select_return_attribution_nav_benchmark_values` correctly rejects ambiguous pairs across tables, but a single-table scenario with only one pair but ambiguous period context would still be accepted. This is intended wait-for-evidence behavior.
5. **`manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` remain missing** for FDD source-truth direct extraction. Owner: separate future gates.
6. **Docs/design/README sync, facade regression**: not implemented in this slice by user instruction. Owner: later Slice 4 if authorized.

---

## Final Recommendation

**CODE_REVIEW_PASS_NOT_READY**

The Slice 2 implementation correctly constructs public `return_attribution.v1` value from proof-positive FDD content. The value shape, `TrackingErrorValue` construction, fail-closed rules, status/`extraction_mode` semantics, gap behavior, anchor construction, and scope boundaries all conform to the accepted plan and controller clarifications. No blocking findings.
