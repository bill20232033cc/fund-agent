# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Fix 2 Evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Fix 2`
Role: plan fix worker only
Verdict: `HANDOFF_READY_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Accepted review artifact: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-mimo-20260617.md`
- Accepted re-review artifact: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-rereview-ds-20260617.md`
- Target plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`

## Changed Files

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix2-evidence-20260617.md`

No code or test files were modified.

## Fixes

| Finding | Status | Disposition |
|---|---|---|
| MiMo `F1` | fixed | Removed `其中：普通股` from positive `stock_investment_amount` closure requirements and examples. Positive stock closure is now limited to `其中：股票` / `其中:股票` under current `FIELD_RULES`. Added a negative test requiring `其中：普通股` to remain residual for stock closure. |
| MiMo `F2` | clarified | Kept conservative top-level boundary behavior; ambiguous parent scope remains fail-closed. No scope expansion was introduced. |
| MiMo `F3` | clarified | The plan already states `_enrich_share_period_contexts()` extraction is optional and the default is to keep existing inline share/period logic. No further implementation requirement was added. |

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
git diff --check -- docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix2-evidence-20260617.md
```

Result: pass - exit 0, no output.

## Self-check

pass - MiMo F1 is fixed without authorizing FIELD_RULES expansion, broadening implementation scope, or changing source truth, baseline, parser, or readiness status.
