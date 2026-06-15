# Docling Multi-sample Field-family Correctness Expansion Plan Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Planning Gate`
Controller role: plan review disposition and accepted plan checkpoint
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the plan review/fix/re-review loop for
`docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md`.

The gate remains planning-only. It does not execute evidence collection, Docling conversion,
PDF/FDR loading, EID/live acquisition, provider/LLM routes, golden/readiness/release commands,
source/test/runtime changes, PR creation, push, or merge.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source, especially repository-bound document access |
| `docs/current-startup-packet.md` | Current control packet and NOT_READY guardrails |
| `docs/implementation-control.md` | Current implementation control truth |
| `docs/reviews/docling-baseline-qualification-review-provenance-remediation-controller-judgment-20260615.md` | Accepted provenance remediation and valid tmux review basis |
| `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md` | Accepted 004393 bounded pilot fact |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Amended plan under judgment |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-review-ds-tmux-20260615.md` | DS plan review |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-review-mimo-tmux-20260615.md` | MiMo plan review |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-rereview-ds-tmux-20260616.md` | DS targeted A1 re-review |

## 3. Finding Disposition

| Finding | Source | Controller disposition | Reason |
| --- | --- | --- | --- |
| DS A1: reference-load availability was ambiguous and could trigger unauthorized live acquisition or skip valid no-live references. | DS review | `ACCEPT_WITH_REWRITE` | The risk is valid. The original DS repair suggestion to check expected cache/PDF paths is rewritten because `AGENTS.md` requires fund document access through `FundDocumentRepository` and forbids direct filesystem document access. The amended plan now requires an accepted same-source reference artifact or `FundDocumentRepository` with no-refresh/no-live intent and `force_refresh=False`; otherwise the sample is `blocked_reference_unavailable` with reason `no_no_live_reference_proof`. |
| DS advisory: candidate JSON path/hash verification should be explicitly sequenced. | DS review | `ACCEPT` | The amended plan now verifies candidate JSON existence and SHA-256 hashes before fact selection and records `blocked_missing_candidate_input` / `blocked_candidate_hash_mismatch` stop states. |
| MiMo F01: definition of "reviewed" around blocked families could be more explicit. | MiMo review | `ACCEPTED_RESIDUAL` | MiMo classified this as low risk with no required amendment. Existing per-sample blocked thresholds and evidence summary requirements are sufficient for this planning gate. |
| MiMo F02: S4/S5/S6 reference availability depends on no-live repository/reference availability. | MiMo review | `ACCEPTED_RESIDUAL_AFTER_A1_FIX` | The same risk is covered by accepted DS A1 rewrite and DS targeted re-review closure. |
| MiMo F03: `product_contract_profile` long-text `partial_match` uses reviewer judgment. | MiMo review | `ACCEPTED_RESIDUAL` | The plan confines `partial_match` to this family and requires bounded excerpts with no contradiction. Broader text-match calibration belongs to future evidence disposition, not this plan gate. |

## 4. Re-review Result

DS targeted re-review verdict:

```text
A1_CLOSED_READY_FOR_CONTROLLER_ACCEPTANCE_NOT_READY
```

Controller accepts that A1 is closed. The closure preserves the repository boundary by avoiding
direct source helper, cache internal, direct PDF path, `force_refresh=True`, or source/cache
implementation inspection requirements.

## 5. Accepted Plan Summary

The accepted plan defines a bounded multi-sample evidence gate for Docling candidate-layer
field-family correctness expansion:

- Required control sample: `004393 / 2025`.
- Expansion candidates: `006597 / 2024`, `017641 / 2024`, `110020 / 2024`, only when existing candidate artifacts and no-live same-source reference proof are available.
- Field families: `fund_identity_profile`, `product_contract_profile`, `performance_indicators`, `expense_costs`, `portfolio_structure`, `manager_alignment`.
- Correctness principle: Docling candidate facts must be compared to same-source annual-report references, not to parser-vs-parser agreement.
- Candidate status remains `not_proven`; this is not source truth, not full field correctness, not production parser replacement, and not readiness proof.
- EID HTML remains blocked/deferred for this Docling expansion gate.
- Production boundaries remain unchanged: no `FundDocumentRepository`, parser, source policy, `EvidenceAnchor`, Service, Host, UI, renderer, quality gate, LLM route, test, or runtime mutation.

## 6. Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| Repository metadata proof mechanism is abstract and must be recorded precisely in the evidence artifact. | Future evidence worker | Accepted residual; do not inspect repository internals or direct cache paths to compensate. |
| S4/S5/S6 may be blocked if no accepted same-source reference artifact or no-live repository metadata proof exists. | Future evidence worker / controller | Evidence gate should return `blocked_not_ready` or partial result instead of triggering live acquisition. |
| Current matrix is bounded to four samples and two report years. | Controller | Broader baseline qualification requires a future expansion gate. |
| Long-text partial matching remains judgment-dependent for `product_contract_profile`. | Evidence reviewer | Evidence artifact must include bounded excerpts and review notes. |

## 7. Final Verdict

```text
VERDICT: ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_EVIDENCE_GATE_NOT_READY
```

Next recommended gate:

```text
Docling Multi-sample Field-family Correctness Expansion Evidence Gate
```

Do not proceed directly to implementation. Evidence execution must remain no-live unless a later gate explicitly authorizes live acquisition.
