# Docling Reference Bundle Enrichment No-live Implementation Code Review - AgentMiMo - 2026-06-17

Gate: `Docling Reference Bundle Enrichment No-live Implementation Gate`
Role: AgentMiMo code review worker only.
Verdict: `PASS_WITH_FINDINGS`
Release/readiness: `NOT_READY`

## Reviewed Artifacts

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-evidence-20260617.md`

## Accepted Plan / Judgment

- `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-field-spec-plan-controller-judgment-20260617.md`

## Findings

### F1 - Low - `reference_generation_status` lacks literal coercion in `_coerce_bundle()`

**File/line:** `source_truth_residual_closure.py:1171-1173`

**Issue:** `_coerce_bundle()` applies `str()` to `reference_generation_status` without `_coerce_literal()`. The `ReferenceGenerationStatus` literal type only allows `"available"` and `"blocked_reference_unavailable"`, but any arbitrary string (e.g. `"typo"`) passes through and is accepted by the dataclass field's `str` type annotation.

**Counterexample / failure mode:** A payload with `{"reference_generation_status": "typo"}` would be coerced to `"typo"`. The guard at line 791 (`bundle.reference_generation_status != "available"`) would still block it, so it is fail-closed. However, the literal contract is not enforced at the coercion boundary, violating the plan's coercion spec: "missing/invalid literal fields become default."

**Why it matters:** Inconsistent with the coercion pattern applied to all other literal fields (`enrichment_status`, `table_family`, `share_class_context`, etc.). If a future guard checks for a specific status string rather than `!= "available"`, the lack of coercion could silently accept invalid state.

**Suggested fix:** Replace line 1171-1173 with:

```python
reference_generation_status=_coerce_literal(  # type: ignore[arg-type]
    value.get("reference_generation_status"),
    ("available", "blocked_reference_unavailable"),
    "available",
),
```

**Severity:** Low - fail-closed in current code, but inconsistent with coercion contract.

### F2 - Low - Missing `_enrich_reference_bundle_contexts()` call in `close_source_truth_residuals()`

**File/line:** `source_truth_residual_closure.py:714-750`

**Issue:** The function `_enrich_reference_bundle_contexts()` (lines 1894-1923) exists and derives table-family, share-class, and period-context for bundle cells, but it is never called by the public entry point `close_source_truth_residuals()`. The entry point only calls `_coerce_reference_bundles()` which does not run enrichment.

**Counterexample / failure mode:** All test fixtures explicitly provide `table_family`, `share_class_context`, `period_context`, etc. as constructor arguments in `_cell()`. If a real payload arrives with raw/flat fields only (no enrichment step upstream), `_match_satisfies_rule()` would see `table_family="unknown"`, `share_class_context="unknown"`, `period_context="unknown"` and all target rules would fail closed. The helper would be inert without upstream enrichment.

**Why it matters:** The plan specifies that table-family classification, share-class derivation, and period-context derivation are part of the helper's responsibility (Slices 1-2). The code exists but is orphaned. This means the helper cannot function as a standalone residual closure path without an external enrichment call.

**Suggested fix:** Add enrichment to `close_source_truth_residuals()` after `_coerce_reference_bundles()`:

```python
bundles = {
    key: _enrich_reference_bundle_contexts(bundle)
    for key, bundle in bundles.items()
}
```

Or document that upstream is required to call enrichment before passing bundles. Given that this is a candidate-only no-live gate and the helper is currently exercised only through in-memory fixtures, this is acceptable as a residual for the next gate.

**Severity:** Low - all tests pass because fixtures pre-populate enriched fields; the helper is currently consumed only through controlled test paths. This is a design residual, not a correctness bug in current code.

## Open Questions

None.

## Residual Risks

1. The helper's enrichment derivation (`_enrich_reference_bundle_contexts`) is implemented but not wired into the public entry point. Future integration must either wire it in or require upstream enrichment.
2. `reference_generation_status` coercion does not enforce the literal contract, though current guard logic is fail-closed.
3. All validation evidence comes from in-memory fixtures; no real document or repository payload has been tested.
4. Source truth, baseline disposition, parser replacement, full field correctness, and release readiness remain unproven.

## Validation Checks

| Check | Result |
|---|---|
| Tests pass (`uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py`) | 56 passed in 0.71s |
| Whitespace check (`git diff --check`) | passed, no output |
| Literal aliases match plan spec | all 8 aliases present and correct |
| Dataclass fields match plan spec | all new fields present with correct types and defaults |
| `to_dict()` emits all new fields | confirmed |
| `_coerce_literal()` used for all literal fields except `reference_generation_status` | confirmed |
| `_coerce_cell()` does not infer `table_family` | confirmed - line 1234 uses `_coerce_literal` default `"unknown"` |
| `_coerce_bundle()` does not infer `enrichment_status` from cells | confirmed - line 1177 uses `_coerce_literal` default `"not_enriched"` |
| `_classify_table_family()` is deterministic | confirmed - priority signal scanning with conflict resolution |
| New table-family fields take precedence over legacy `required_table_family_any` | confirmed - lines 1017-1028 |
| Legacy raw context cannot override new-field rejection | confirmed - rejection check at line 958 precedes legacy fallback |
| S6-F041 fail-closed without benchmark label | confirmed - `required_text_semantic_context="benchmark"` at line 709 |
| S6-F049/S6-F050 fail-closed without proven hierarchy | confirmed - `rejected_row_hierarchy_roles=("child","unknown")` at line 648 for equity; `required_row_hierarchy_role="child"` and `required_parent_row_label_any=("权益投资",)` at lines 663-664 for stock |
| `bounded_neighbor_row_labels` not used for positive closure | confirmed - not consumed in `_match_satisfies_rule()` |
| Pure-helper boundary preserved | confirmed - test at line 1312 blocks `open()` and verifies no `FundDocumentRepository` import |
| No live/network/source/provider/LLM/analyze/checklist/golden/readiness/release behavior | confirmed - no suspicious imports or external calls |
| No direct PDF/cache/source-helper/repository calls | confirmed |
| No Service/UI/Host/renderer/quality-gate changes | confirmed |

## Final Verdict

**PASS_WITH_FINDINGS**

Two low-severity findings identified:

1. `reference_generation_status` lacks `_coerce_literal()` enforcement (F1) - fail-closed in current code but inconsistent with coercion contract.
2. `_enrich_reference_bundle_contexts()` is implemented but not wired into the public entry point (F2) - tests pass because fixtures pre-populate enriched fields; this is a design residual for the next gate.

No blocking findings. Implementation conforms to the accepted field-spec plan and controller judgment. All 56 tests pass. Pure-helper boundary and NOT_READY guard flags are preserved. The two findings are non-blocking residual items that should be tracked for the next gate.

Blocking findings count: 0

## Self-check

pass - review reproduced validation (56 tests pass, git diff --check clean), cross-checked contracts against accepted plan, verified scope boundary (candidate-only, NOT_READY, no live behavior), and confirmed no blocking correctness issues in the implementation.
