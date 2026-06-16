# Docling Source-truth Residual Closure Plan Controller Judgment - 2026-06-16

Gate: `Docling Source-truth Residual Closure Planning Controller Judgment`
Role: controller
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Inputs Reviewed

Plan:

- `docs/reviews/docling-source-truth-residual-closure-plan-20260616.md`

Review loop:

- `docs/reviews/plan-review-20260616-222825.md`
- `docs/reviews/plan-review-20260616-224804.md`

Accepted upstream artifacts:

- `docs/reviews/fund-disclosure-processor-contract-design-controller-judgment-20260616.md`
- `docs/reviews/docling-baseline-support-source-truth-evidence-controller-judgment-20260616.md`
- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`

## 2. Controller Decision

Accept the plan for a no-live implementation gate.

Accepted scope:

- target only the 17 residual rows from `source_truth_matrix.json`;
- implement a candidate-internal residual closure helper under `fund_agent/fund/documents/candidates/`;
- add focused tests under `tests/fund/documents/`;
- keep pure helper access file-free, repository-free, Docling-free and source-helper-free;
- let only the later evidence wrapper build `RepositoryReferenceBundle` through `FundDocumentRepository.load_annual_report(..., force_refresh=False)` under cache-only/no-live guard semantics;
- classify every row through source / processed / fund statuses;
- preserve residuals when proof is incomplete.

## 3. Review Finding Disposition

| Finding | Source | Controller disposition |
| --- | --- | --- |
| F1: `repository_reference_rows` lacked a schema and would force implementation worker to redesign source-reference contract. | `docs/reviews/plan-review-20260616-222825.md` | Accepted and fixed. Plan sections 5.4 and 5.5 now define repository reference row/bundle contracts and pure-helper vs evidence-wrapper ownership. |

Re-review result:

```text
docs/reviews/plan-review-20260616-224804.md -> pass-with-risks
```

Controller accepts the residual risk because the plan explicitly requires fail-closed handling when repository table semantics are insufficient.

## 4. Binding Implementation Constraints

Implementation worker must preserve these constraints:

- Do not modify `FundDocumentRepository`, production parser behavior, public `EvidenceAnchor` schema, Service, UI, Host, renderer or quality gate.
- Do not read PDF files, parser cache bodies, source-helper bodies or source adapter outputs directly.
- Do not run live/network/EID/provider/LLM/analyze commands.
- Do not run Docling conversion.
- Do not treat candidate JSON, parser agreement or previous `source_excerpt_samples` as source truth.
- Do not close `S5-F023 / investment_objective` unless same-source repository body proof exists.
- Do not close `S6-F041 / benchmark` unless benchmark-labeled source context exists.
- Do not force `17 / 17` closure. Partial closure with explicit residuals is acceptable.

## 5. Accepted Risk

| Risk | Accepted handling |
| --- | --- |
| Current `ParsedTable` only exposes `page_number`, `table_index`, `headers` and `rows`, not full row-label path, column-header path, caption or table family. | Implementation may derive conservative reference context only when deterministic. Otherwise rows must remain `locator_context_insufficient`, `semantic_rule_unresolved`, `blocked_reference_unavailable` or another explicit residual/blocker. |
| S1 expense duplicate may remain unresolved even with table context. | Keep as `semantic_equivalent_duplicate_residual` if total/vendor rows cannot be separated under accepted source evidence. |

## 6. Next Entry Point

Next gate:

```text
Docling Source-truth Residual Closure No-live Implementation Gate
```

Required implementation outputs:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` or equivalent candidate-internal helper;
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`;
- implementation evidence artifact under `docs/reviews/`;
- validation with focused pytest and `git diff --check`.

The implementation gate should not generate final evidence matrix unless the worker can do so without crossing the accepted boundaries. If matrix generation is deferred, the JSON validation belongs to the later evidence gate.

## 7. Not Accepted

This judgment does not accept:

- source-truth residual closure evidence;
- Docling baseline qualification;
- full field correctness;
- parser replacement;
- source policy changes;
- release readiness;
- PR readiness.

## 8. Validation To Run Before Local Checkpoint

Required sanity check:

```bash
git diff --check
```

## 9. Verdict

```text
VERDICT: ACCEPT_DOCLING_SOURCE_TRUTH_RESIDUAL_CLOSURE_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY
```
