# Docling Reference Bundle Field-spec Plan Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Field-spec Planning Gate`
Role: controller judgment
Verdict: `ACCEPT_FIELD_SPEC_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Artifacts

- Plan: `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`
- AgentDS review: `docs/reviews/docling-reference-bundle-field-spec-plan-review-ds-20260617.md`
- AgentMiMo review: `docs/reviews/docling-reference-bundle-field-spec-plan-review-mimo-20260617.md`
- AgentDS re-review: `docs/reviews/docling-reference-bundle-field-spec-plan-rereview-ds-20260617.md`
- AgentMiMo re-review: `docs/reviews/docling-reference-bundle-field-spec-plan-rereview-mimo-20260617.md`

## Judgment

Accepted as the field-level implementation plan for the next candidate-only
Docling reference-bundle enrichment and semantic-rule predicate implementation
gate.

The plan resolves the binding amendments from
`docs/reviews/docling-semantic-residual-rule-design-controller-judgment-20260617.md`:

- exact reference-bundle field names, types, defaults, serialization and
  coercion behavior;
- table-family classification labels, deterministic input signals,
  conflict handling and fail-closed behavior;
- row hierarchy encoding and parent/child predicate consumption;
- share-class and period-context proof sources and canonical variants;
- diagnostic scope kept optional/future;
- partial enrichment behavior with missing required context failing closed.

The plan remains candidate-only and does not authorize production parser
replacement, source truth acceptance, baseline promotion, full field
correctness, release readiness, PR readiness, live/source acquisition,
provider/LLM/analyze/checklist/golden commands, direct PDF/cache/source-helper
access, or Service/UI/Host/renderer/quality-gate parser access.

## Review Disposition

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentDS | `PASS_WITH_FINDINGS` | `PASS` | Accepted; DS-P1 through DS-P5 were fixed and no blocking findings remain. |
| AgentMiMo | `PASS_WITH_FINDINGS` | `PASS` | Accepted; all five prior findings were fixed and no new blockers were introduced. |

The accepted fix clarified:

- `row_hierarchy_path` deterministic default behavior;
- `column_header_band_path` consumer semantics for share-class and period context;
- table-family conflict handling and per-cell coercion boundaries;
- `bounded_neighbor_row_labels` as diagnostic/negative-disambiguation context only;
- precedence between new table-family fields and legacy `required_table_family_any`;
- `ResidualClosureRule` as Python-only constant configuration for this gate;
- `_coerce_bundle()` missing `enrichment_status` behavior;
- `_has_share_class_context()` replacement/wrapper path;
- backward compatibility for existing `_cell()` / `_bundle()` test fixtures.

## Accepted Next Implementation Scope

The next gate may plan or execute a no-live implementation slice limited to:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- directly related evidence/review artifacts for that implementation gate

The implementation must preserve the pure-helper boundary: no file reads, no
`FundDocumentRepository` calls inside the helper, no Docling conversion, no
source-helper imports, no live/network/provider/LLM/analyze/checklist/golden
commands, and no production `EvidenceAnchor` admission.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Candidate reference-bundle enrichment and predicate implementation not yet performed. | Fund documents candidate internals implementation owner | `Docling Reference Bundle Enrichment No-live Implementation Gate` |
| Seven semantic residual rows remain unclosed until implementation and evidence prove closure or preserve residuals. | Fund documents candidate evidence owner | Later no-live residual closure re-evidence gate |
| Source truth, full field correctness, baseline disposition, production parser replacement and readiness remain unproven. | Future baseline disposition / readiness owners | Separate reviewed gates only |

## Validation

Controller observed:

```text
git diff --check -- docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md docs/reviews/docling-reference-bundle-field-spec-plan-review-ds-20260617.md docs/reviews/docling-reference-bundle-field-spec-plan-review-mimo-20260617.md docs/reviews/docling-reference-bundle-field-spec-plan-rereview-ds-20260617.md docs/reviews/docling-reference-bundle-field-spec-plan-rereview-mimo-20260617.md
```

The command completed successfully with no output.

## Next Gate

Recommended next gate:

```text
Docling Reference Bundle Enrichment No-live Implementation Gate
```

Purpose: implement the accepted candidate-only reference-bundle field model,
serialization/coercion behavior, table-family classification, row hierarchy,
share/period predicates and benchmark context checks under no-live boundaries,
with focused tests. Do not run residual closure re-evidence or claim baseline
qualification until a later evidence gate is explicitly opened.
