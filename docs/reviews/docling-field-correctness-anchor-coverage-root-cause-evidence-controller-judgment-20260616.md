# Docling Field Correctness Anchor Coverage Root-cause Evidence Controller Judgment - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage Root-cause Evidence Review Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the review/controller step for the root-cause evidence artifact:

- `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md`
- `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json`

This judgment does not authorize production parser replacement, production `EvidenceAnchor` admission, source acquisition, source policy changes, baseline promotion, Service/Host/UI/renderer/quality-gate/provider/LLM route changes, readiness, release, PR, push, merge, or the next implementation gate.

## 2. Evidence Reviewed

| Artifact | Role | Disposition |
| --- | --- | --- |
| `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-plan-20260616.md` | accepted root-cause evidence plan | accepted as scope boundary |
| `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md` | root-cause evidence artifact | accepted |
| `reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json` | root-cause evidence matrix | accepted |
| `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-review-ds-20260616.md` | AgentDS independent review | `REVIEW_PASS_NOT_READY`, accepted |
| `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-review-mimo-20260616.md` | AgentMiMo independent review | `REVIEW_PASS_NOT_READY`, accepted |

## 3. Accepted Facts

The controller accepts the following facts as no-live candidate-internal root-cause evidence only:

| Fact | Accepted value |
| --- | ---: |
| Missing-anchor rows represented | `28 / 28` |
| Missing-anchor rows by sample | S1=`3`, S4=`11`, S6=`14` |
| Missing-anchor rows by family | `expense_costs=6`, `fund_identity_profile=10`, `performance_indicators=6`, `product_contract_profile=6` |
| Parent table exists | `28 / 28` |
| Candidate cell exists | `28 / 28` |
| Rows mapped when calling current helper directly | `0 / 28` |
| Rows blocked by current helper | `28 / 28` |
| Dominant repair surface | `section_context_mapping_rule` |
| Repair surface coverage | `28 / 28` |
| `duplicate_section_heading` | `16 / 28` |
| `missing_section_context` | `12 / 28` |

No row is accepted as belonging to:

- `table_cell_locator_normalization`
- `reference_to_anchor_join_logic`
- `reference_artifact_scope`
- `reduced_scope_controller_decision`

The accepted root cause is therefore:

```text
section_context_mapping_rule
```

for all `28 / 28` missing-anchor reviewed facts.

## 4. Review Disposition

AgentDS review is accepted with verdict:

```text
REVIEW_PASS_NOT_READY
```

AgentMiMo review is accepted with verdict:

```text
REVIEW_PASS_NOT_READY
```

No blocking review finding remains.

DS residuals are classified as non-blocking for this gate:

| Residual | Controller disposition |
| --- | --- |
| S6-F040 and S6-F041 share the same candidate cell locator | Accepted as next-planning caution. It does not invalidate the evidence that the current helper blocks both rows at `section_context_mapping_rule`. The next planning gate should verify whether the reference-side `benchmark` assignment is correct before including S6-F041 in an implementation success target. |
| Startup/control packet staleness | Accepted as control-sync follow-up. It does not change root-cause evidence validity. |
| Broader blocked candidate population in positive controls | Accepted as scope caution. It supports that section-context blocking is systemic, but this gate only accepts the reviewed `28 / 28` missing-anchor rows. |

MiMo residuals are classified as non-blocking for this gate:

| Residual | Controller disposition |
| --- | --- |
| S5 has zero missing-anchor reviewed facts but many blocked candidate cells overall | Accepted. S5 remains a reviewed-fact positive control, not a proof that all candidate cells map. |
| No live PDF/FDR/Docling execution | Accepted as inherent to the no-live evidence scope. If candidate envelopes change, this evidence must be regenerated or revalidated. |

## 5. Boundary Guardrails

This judgment accepts only a candidate-internal root-cause classification.

It does not prove:

- source truth;
- full field correctness;
- production parser replacement readiness;
- production `EvidenceAnchor` admission;
- Docling baseline or golden promotion;
- release readiness;
- PR readiness.

The earlier comparative result remains bounded:

- selected Docling reviewed values matched accepted same-source references for `72 / 72` reviewed facts;
- selected reviewed-fact anchor coverage remained `44 / 72`;
- the missing `28 / 72` anchor rows are now classified as blocked by `section_context_mapping_rule`.

Candidate status remains:

```text
candidate_field_correctness_status_remains=not_proven
```

## 6. Controller Decision

The root-cause evidence artifact and matrix are accepted.

The accepted next local gate, if separately authorized by the user, is:

```text
Docling Field Correctness Anchor Coverage No-live Implementation Planning Gate
```

The next planning gate must be limited to section-context mapping behavior and must preserve fail-closed semantics. It must not modify public `EvidenceAnchor`, production parser replacement policy, source policy, Service/Host/UI/renderer/quality gate behavior, readiness, release, PR, push, or merge state.

The next planning gate should explicitly decide:

1. Whether S6-F041 remains in the implementation success target after verifying its reference-side `benchmark` assignment.
2. Whether the first implementation target is exactly `72 / 72` reviewed-fact anchor coverage or a narrower incremental improvement over `44 / 72`.
3. How S5 positive-control behavior is protected while changing section-context mapping rules.
4. Whether broader blocked candidate-cell populations are out of scope or tracked as a separate follow-up.

## 7. Final Verdict

```text
VERDICT: ACCEPT_ROOT_CAUSE_SECTION_CONTEXT_MAPPING_RULE_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY
```
