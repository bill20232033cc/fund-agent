# Docling Multi-sample Same-source Reference Availability Proof Plan Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Same-source Reference Availability Proof Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_WITH_DS_AMENDMENTS_APPLIED_READY_FOR_ARTIFACT_ONLY_EVIDENCE_GATE_NOT_READY`

## Scope

This judgment accepts the plan for a bounded, no-live reference-availability evidence gate for S4/S5/S6.

It does not authorize implementation, production parser replacement, `FundDocumentRepository` behavior change, source policy change, `EvidenceAnchor` schema change, Service/UI/Host/renderer/quality-gate integration, Docling baseline promotion, source-truth claim, full field-correctness claim, readiness/release claim, PR, push, or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Execution constraints and FundDocumentRepository/source-boundary rules |
| `docs/current-startup-packet.md` | Current active gate and accepted Docling blocked-evidence fact |
| `docs/implementation-control.md` | Current control truth and `NOT_READY` guardrails |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md` | Accepted prior blocked evidence judgment |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Prior evidence input for S4/S5/S6 blocked status |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Prior machine-readable evidence input |
| `docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-20260616.md` | Plan under review |
| `docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-review-ds-tmux-20260616.md` | DS plan review |

## Accepted Facts

- Current production annual-report source policy remains EID single-source/no-fallback for this route.
- S1 `004393 / 2025` remains the only accepted bounded correctness pilot in this Docling line.
- S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` have candidate JSON artifacts from the prior gate, but candidate artifacts are not same-source reference proof and are not field-correctness proof.
- The next evidence worker may first check only accepted evidence-chain artifacts for same-source reference availability.
- `FundDocumentRepository(force_refresh=False)` is not automatically no-live. Without prior parsed-cache metadata proof, attempting it can cross into PDF cache lookup, acquisition, or parsing.

## Review Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS F1-F4 | ACCEPT | Same-source proof semantics, candidate-output exclusion, Route A scope, and repository semantics are accepted. |
| DS F5 / A1 | ACCEPT_APPLIED | Plan now explicitly records Route B pre-execution proof circularity and requires `blocked_repository_route_requires_authorization` unless exact prior parsed-cache metadata proof or separate metadata-only authorization exists. |
| DS F6 / A2 | ACCEPT_APPLIED | Plan now explicitly forbids inspecting, serializing, diffing, comparing, or using parsed report body content; only `metadata.source` envelope fields may be recorded if separately authorized. |
| DS F10 / A3 | ACCEPT_APPLIED | Plan now marks `shasum` over accepted reference artifacts as conditional and not applicable when no artifact path exists. |
| MiMo review | DEFERRED_REVIEW_CHANNEL_RESIDUAL | MiMo pane remained blocked in a prior interactive approval prompt after `escape`, `interrupt`, and `/clear`; no MiMo review is counted for this gate. |

## Binding Amendments

The accepted plan is binding only with these amendments applied:

1. Route A must run first and may use only accepted same-source reference artifacts in the reviewed evidence chain.
2. Candidate Docling/pdfplumber JSON, untracked residue, cache internals, direct PDF paths, source helpers, and source adapters are not reference proof.
3. Route B is not authorized by this judgment.
4. If a later controller/user decision authorizes metadata-only cache inspection, the worker may access only `metadata.source` envelope fields and must not inspect parsed report body content.
5. Evidence must preserve `NOT_READY`, not source truth, not field correctness, not full correctness, and not parser replacement.

## Validation

Commands run by controller:

```text
git branch --show-current
git status --short
tmux-cli status
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command} #{pane_title}'
git diff --check -- docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-20260616.md
```

Plan worker validation:

```text
git diff --check -- docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-20260616.md
```

Result: PASS, no output.

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| MiMo reviewer unavailable | Controller / future gate | Do not count MiMo review for this gate. Re-attempt only after pane is clean. |
| Route B cache metadata proof unresolved | Future controller decision | Requires a separate Cache Metadata Contract Gate or explicit bounded metadata-only authorization. |
| S4/S5/S6 same-source references may remain unavailable | Evidence worker | Artifact-only evidence gate should record sample-specific blocked status rather than invent a reference route. |

## Next Gate

Proceed to:

```text
Docling Multi-sample Same-source Reference Availability Artifact-only Evidence Gate
```

Allowed next-gate action:

- Write one evidence artifact that evaluates Route A only.
- Do not attempt Route B/FDR/cache metadata inspection unless separately authorized.
- If no accepted same-source reference artifacts exist for S4/S5/S6, write `BLOCKED_NO_NO_LIVE_REFERENCE_PROOF_NOT_READY` with per-sample blockers.

## Final Verdict

```text
VERDICT: ACCEPT_WITH_DS_AMENDMENTS_APPLIED_READY_FOR_ARTIFACT_ONLY_EVIDENCE_GATE_NOT_READY
```
