# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Implementation Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate`
Role: controller judgment only
Verdict: `ACCEPT_IMPLEMENTATION_READY_FOR_NO_LIVE_REEVIDENCE_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Inputs

- Accepted plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- Plan controller judgment: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-controller-judgment-20260617.md`
- Accepted plan commit: `a4f2803`

## Accepted Implementation Artifacts

- Implementation code: `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- Implementation tests: `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- Implementation evidence: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`
- DS code review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-code-review-ds-20260617.md`
- MiMo code review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-code-review-mimo-20260617.md`

## Controller Decision

The implementation is accepted for local no-live re-evidence.

Accepted scope:

- raw legacy v1 `_enrich_reference_bundle_contexts()` now derives deterministic candidate-only row hierarchy and text semantic context;
- v2 bundles remain non-overwritten;
- `FIELD_RULES` were not expanded;
- `其中：普通股` remains residual for positive `stock_investment_amount` closure;
- no source truth, baseline, parser, readiness, live/source/PDF/cache/helper, Service/UI/Host/renderer/quality-gate boundary was crossed.

This judgment does not accept Docling as a baseline, does not accept source truth, and does not prove full field correctness. Any changed residual count must be measured in a separate no-live re-evidence gate.

## Validation

Controller independently reran:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result:

```text
80 passed in 0.82s
```

Controller independently reran:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -k "hierarchy or benchmark or raw_legacy or neighbor"
```

Result:

```text
28 passed, 52 deselected in 0.61s
```

Controller independently ran:

```text
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md
```

Result: pass - exit 0, no output.

## Review Disposition

AgentDS review verdict: `PASS`; blocking findings: 0.

Accepted DS findings:

- F-DS-I1 `_is_stock_child_label` accepts labels such as `其中：股票投资`: accepted as Info residual; no known false-positive scenario.
- F-DS-I2 context benchmark + heading objective cross-layer conflict lacks a dedicated test: accepted as Info residual; implementation fail-closes to `unknown`.
- F-DS-I3 context benchmark + raw objective prefix conflict lacks a dedicated test: accepted as Info residual; implementation fail-closes to `unknown`.
- F-DS-I4 `_is_equity_parent_label` substring matching accepts variants such as `权益投资合计`: accepted as Info residual; future re-evidence should decide whether to narrow.

AgentMiMo review verdict: `PASS_WITH_FINDINGS`; blocking findings: 0.

Accepted MiMo findings:

- F1 `_is_detail_or_geography_row` does not cover every possible detail label: accepted as Low residual. Future re-evidence should trigger a follow-up only if a real false closure appears.
- F2 `_is_equity_parent_label` substring matching may over-match: accepted as Info residual, same class as DS F-DS-I4.
- F3 context ambiguity test uses a compound label string: accepted as Info; no current behavioral risk.
- F4 heading-path internal benchmark/objective conflict has no dedicated test: accepted as Info and already accepted in the plan re-review as fail-closed residual.

No fix gate is required for this implementation gate.

## Boundary Guardrails

This accepted implementation preserves:

- `NOT_READY`;
- `candidate_only=true`;
- `source_truth_status=not_proven`;
- no source truth acceptance;
- no Docling baseline promotion;
- no parser replacement;
- no full field correctness claim;
- no release readiness, PR readiness, or golden readiness;
- no live/network/provider/LLM/analyze/checklist/golden commands;
- no direct PDF/cache/source-helper access;
- no `FundDocumentRepository` call;
- no Service/UI/Host/renderer/quality-gate change;
- no evidence-wrapper v2 prefill solution.

README files were not updated in this gate because the accepted implementation plan and controller judgment limited the write set to private candidate helper code, focused tests, and implementation evidence; there is no public usage or package-level developer contract change in this gate.

## Next Gate

Next gate:

`Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Gate`

Purpose:

- rerun the accepted 17-row residual closure matrix using the updated helper;
- compare against the prior accepted checkpoint of 13 closed / 4 residual;
- preserve `source_truth_status=not_proven`;
- classify any remaining residuals without claiming baseline/source truth/readiness.

## Self-check

Current gate is implementation acceptance. Controller has verified branch, worktree scope, implementation evidence, DS/MiMo reviews, and validation commands. Review findings are non-blocking and already bounded as residuals. The accepted checkpoint is ready for local commit and then no-live re-evidence.
