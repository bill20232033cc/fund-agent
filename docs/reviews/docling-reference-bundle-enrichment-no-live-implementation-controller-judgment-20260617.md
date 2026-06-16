# Docling Reference Bundle Enrichment No-live Implementation Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Enrichment No-live Implementation Gate`
Role: controller judgment
Verdict: `ACCEPT_IMPLEMENTATION_READY_FOR_NO_LIVE_RESIDUAL_CLOSURE_REEVIDENCE_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Artifacts

- Implementation evidence: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-evidence-20260617.md`
- Fix evidence: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-fix-evidence-20260617.md`
- AgentDS code review: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-code-review-ds-20260617.md`
- AgentMiMo code review: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-code-review-mimo-20260617.md`
- AgentDS re-review: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-rereview-ds-20260617.md`
- AgentMiMo re-review: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-rereview-mimo-20260617.md`

## Judgment

Accepted as the candidate-only no-live implementation of the previously
accepted Docling reference-bundle field spec.

The implementation adds the reference-bundle v2 field model, deterministic
literal coercion, serialization, table-family classification, share-class and
period-context predicates, row-hierarchy predicates, benchmark semantic-context
checks, and focused target-row rules for the scoped semantic residual rows.

The accepted fix also closes the two actionable non-blocking review findings:

- `reference_generation_status` now uses literal coercion. Missing or invalid
  values default to `available`; `blocked_reference_unavailable` remains a
  valid fail-closed state.
- `close_source_truth_residuals()` now runs `_enrich_reference_bundle_contexts()`
  after repository-reference coercion, so raw legacy v1 bundle payloads can be
  enriched in memory before closure.

The controller accepts the v1-only enrichment guard as the intended boundary:
legacy/raw `repository_reference_bundle.v1` payloads may be enriched by this
helper; `repository_reference_bundle.v2` payloads are treated as already
enriched and are not overwritten. Invalid v2 enrichment literals therefore
remain fail-closed rather than being repaired by this helper.

## Review Disposition

| Reviewer | Initial verdict | Accepted findings | Re-review verdict | Controller disposition |
|---|---|---:|---|---|
| AgentDS | `PASS` | 1 Low actionable finding plus Info items | `PASS` | Accepted. The enrichment entrypoint finding is fixed; remaining DS items are non-blocking residuals. |
| AgentMiMo | `PASS_WITH_FINDINGS` | 2 Low findings | `PASS` | Accepted. Both findings are fixed and no new blocking finding remains. |

AgentDS re-review raised one new Info item: the fix evidence did not explicitly
record the v1-only enrichment guard. This controller judgment records that
boundary and treats the Info item as closed for this gate.

## Accepted Scope

Accepted changed implementation files:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

Accepted behavior:

- pure in-memory helper behavior only;
- no file reads or writes inside the helper;
- no `FundDocumentRepository` invocation inside the helper;
- no direct PDF/cache/source-helper access;
- no live/network/provider/LLM/analyze/checklist/golden commands;
- no Service/UI/Host/renderer/quality-gate parser path changes;
- no production `EvidenceAnchor` admission.

## Validation

Controller observed:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result:

```text
60 passed in 0.64s
```

Controller also observed:

```text
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-evidence-20260617.md docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-fix-evidence-20260617.md docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-code-review-ds-20260617.md docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-code-review-mimo-20260617.md docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-rereview-ds-20260617.md docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-rereview-mimo-20260617.md
```

Result: command completed successfully with no output.

## Non-goals Preserved

This accepted implementation does not prove:

- source truth acceptance;
- Docling baseline qualification;
- production parser replacement;
- full field correctness;
- release readiness;
- PR readiness;
- real-document residual closure rates;
- golden-set readiness.

`source_truth_status` remains `not_proven`; Docling remains candidate-only and
`NOT_READY`.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Real residual-row closure impact has not been re-measured. | Fund documents candidate evidence owner | No-live residual closure re-evidence gate. |
| `_period_context_from_text` has known composite-label ambiguity such as prior comparable period plus period-end wording. | Fund documents candidate implementation owner | Only fix if re-evidence produces a concrete failing row. |
| `_cell_has_required_text_semantic_context` only maps benchmark semantics today. | Fund documents candidate implementation owner | Extend only when a scoped row requires additional text semantic labels. |
| v2 bundle enrichment quality is assumed upstream and not repaired here. | Future reference-bundle producer owner | Validate in the producer/evidence gate before any baseline decision. |
| Source truth, baseline disposition, parser replacement and readiness remain unproven. | Future baseline disposition/readiness owners | Separate reviewed heavy gates only. |

## Next Gate

Recommended next gate:

```text
Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Gate
```

Purpose: run the accepted no-live helper against the scoped residual rows and
accepted repository-reference payloads, measure which rows close, which remain
residual, and why. The next gate may produce evidence for residual closure
impact only; it still must not promote Docling to baseline, accept production
source truth, replace the parser, or claim readiness.
