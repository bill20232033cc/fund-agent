# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Fix Evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Fix`
Role: plan fix worker only
Verdict: `HANDOFF_READY_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Accepted review artifact: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-ds-20260617.md`
- Target plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`

## Changed Files

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix-evidence-20260617.md`

No code or test files were modified.

## Fixes

| Finding | Status | Plan change |
|---|---|---|
| `F-DS-P1` | fixed | Defined `_row_primary_label(cell)` exactly as the last non-empty stripped `row_label_path` element; parent/child/top-level predicates must consume only that primary label. |
| `F-DS-P2` | fixed | Defined semantic precedence: `context_label` > `heading_path` > `raw_text`; local investment-objective context rejects benchmark inference; cross-layer benchmark/objective conflict fails closed. |
| `F-DS-P3` | fixed | Specified delimiter-aware raw prefix detection with Chinese/ASCII colon, pipe/full-width pipe, whitespace, and leading whitespace handling. |
| `F-DS-P4` | fixed | Added required positive test for benchmark classification from `heading_path` when `context_label` is generic/non-conflicting. |
| `F-DS-P5` | fixed | Rewrote the v1 enrichment wiring sample to avoid assuming nonexistent `_enrich_share_period_contexts()`; existing inline share/period logic remains default. |
| `F-DS-P6` | fixed | Clarified integer `row_index` gaps are comparable; only missing, non-integer, duplicated row identity, or otherwise non-comparable order fails closed. |

## Boundary Confirmation

- Preserves `NOT_READY`.
- Preserves `source_truth_status=not_proven`.
- No source truth acceptance.
- No baseline promotion.
- No parser replacement.
- No full correctness/readiness claim.
- No live/network/provider/LLM/analyze/checklist/golden command.
- No code/test change.
- No commit/stage/push/PR.

## Validation

Required validation:

```text
git diff --check -- docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix-evidence-20260617.md
```

Result: pass - exit 0, no output.

## Self-check

pass - all six accepted DS findings are addressed without broadening implementation scope or changing source truth, baseline, parser, or readiness status.
