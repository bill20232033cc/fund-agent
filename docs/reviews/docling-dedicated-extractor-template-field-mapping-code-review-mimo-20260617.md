# Docling Dedicated Extractor Template-field Mapping Code Review — AgentMiMo 2026-06-17

Gate: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
Role: AgentMiMo code reviewer
Reviewed files:
- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`

## Verdict

`CODE_REVIEW_PASS_NOT_READY`

## Candidate-only / source_truth_status / not_proven Boundaries

PASS.

- `CandidateTemplateField.__post_init__` enforces `candidate_only is True` and `source_truth_status == "not_proven"` at construction time. Any violation raises `ValueError` before the object can be returned.
- `DoclingTemplateFieldExtractionResult.__post_init__` applies the same guard at the result envelope level.
- `_validate_document` rejects inputs whose `candidate_status`, `field_correctness_status`, or `source_truth_status` are not `"not_proven"`, or whose `production_parser_replacement_status` is not `"not_authorized"`.
- `_extract_single_field` hardcodes `candidate_only=True, source_truth_status="not_proven"` in both the direct and missing return paths.

No code path can produce a candidate field or result that escapes the proof boundary.

## No Production EvidenceAnchor Promotion

PASS.

- `CandidateTemplateFieldAnchor` is a standalone dataclass with explicit `source_kind: CandidateTemplateSourceKind` (Literal `"annual_report"`). It does not inherit from, wrap, or convert to `EvidenceAnchor`.
- No import of `EvidenceAnchor` or any production anchor type exists in the module.
- Anchor `note` fields consistently prefix `"candidate_only:"` to prevent downstream misinterpretation.

## No FundDataExtractor Integration or Parser Replacement

PASS.

- No import of `FundDataExtractor`, `FundDocumentRepository`, or any production report/parser module.
- No `__init__.py` re-export added.
- The module is self-contained and unreachable from production report generation.

## Exact One Field Per DEFAULT Path / Missing Semantics

PASS.

- `extract_docling_template_fields` iterates `target_field_paths` via a generator comprehension, calling `_extract_single_field` once per path. No early return or skip.
- When `_match_field` returns `None`, `_missing_field` produces an explicit `CandidateTemplateField` with `extraction_mode="missing"`, `value=None`, `anchors=()`.
- `_missing_note_for` distinguishes deferred fields (specific note codes like `"docling_template_field_deferred_manager_strategy_text"`) from general missing (`"docling_template_field_missing:{field_path}"`).
- Test `test_docling_template_field_extractor_emits_one_candidate_field_per_default_path` asserts `len(result.fields) == len(DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS)` and exact set equality.

No field can be silently dropped or duplicated.

## Field Matching Correctness and Fail-Closed Behavior

PASS.

Matching is deterministic, section-scoped, and fail-closed:

| Field group | Strategy | Correctness notes |
|---|---|---|
| `_PROFILE_LABELS` (8 fields) | Table key-value + text fallback, §2 only | Label cell matched by text or `row_label_path`; value cell is first non-empty non-label cell in same row. Empty values skipped. |
| `_FEE_LABELS` (2 fields) | Table key-value + text fallback, §7 only | Same as profile. |
| `_PERFORMANCE_LABELS` (2 fields) | Column header + row label intersection, §3 only | Requires both `column_header_path` contains label AND `row_label_path` contains period indicator (`"过去一年"` etc). Prevents column-only false positives. |
| `tracking_error.value_text` | Text block, §3/§4 | Reject keywords (`控制在`, `力争`, `目标` etc) filter target/narrative text. Accept keywords (`实际`, `报告期` etc) require actual disclosure. Percent pattern extracted only after both filters pass. |
| `portfolio_managers` | Table row scan, §4 | Header row excluded (`name in {"姓名", "基金经理"}`). Each manager gets anchor. Returns structured dict with `schema_version`. |
| `turnover_rate` | Table key-value + text fallback, §8 | Shares section with holdings but dispatched before `holdings_snapshot.*` prefix check — correct precedence. |
| `manager_alignment.*` | Table key-value + text fallback, §10 | Isolated section. |
| `holdings_snapshot.*` | Row context labels + column header scan, §8 | `_holding_required_labels` disambiguates stock/bond/target-fund rows within same section. First matching row returned. |

All matchers return `None` on miss — no exception, no partial result. `_extract_single_field` treats `None` as missing.

### Minor observation (non-blocking)

`_match_holding_row` returns only the **first** matching row per field path. For `holdings_snapshot.top_holdings` this means a single stock row, not the full top-N list. This is consistent with the plan's "first row candidate" scope but means downstream integration must handle the `{"rows": (single_row,)}` structure as a candidate hint, not a complete holdings snapshot. The evidence document acknowledges this as residual.

## Test Coverage for Current Slice

PASS. 7 tests, all passing:

| Test | Coverage |
|---|---|
| `test_..._emits_one_candidate_field_per_default_path` | Structural invariant: one field per path, correct schema/status |
| `test_..._maps_profile_fee_and_performance_fields` | 12 profile/fee/performance field values |
| `test_..._maps_tracking_manager_and_holding_fields` | tracking_error, portfolio_managers, manager_alignment, 3 holdings types |
| `test_..._emits_explicit_missing_for_deferred_paths` | 4 deferred fields: extraction_mode, value, anchors, note, missing_field_paths |
| `test_..._rejects_non_docling_source` | PDFPLUMBER source rejected |
| `test_..._rejects_status_claims` | source_truth_status="accepted" rejected |
| `test_..._rejects_tracking_error_target_text` | "力争将跟踪误差控制在 4.00%以内" correctly missed |

Coverage is sufficient for the candidate-only slice. Acknowledged gaps (real annual report data, numeric normalization, multi-year semantics, QDII/FOF) are documented as residual risks.

## Summary

Implementation is structurally correct. Candidate-only boundaries are enforced at every construction and validation point. No production types are imported or produced. Field matching is deterministic, section-scoped, and fail-closed. Every DEFAULT path produces exactly one candidate field with explicit missing semantics for unmatched/deferred paths. Test coverage validates the invariants required by this gate.

`CODE_REVIEW_PASS_NOT_READY`
