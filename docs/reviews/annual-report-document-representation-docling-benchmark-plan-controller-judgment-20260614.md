# Annual-report Document Representation / Docling Benchmark Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Annual-report Document Representation / Docling Benchmark Planning Gate`

Verdict: `ACCEPT_WITH_BINDING_AMENDMENTS_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment evaluates the planning artifact and independent DS/MiMo reviews for the annual-report document representation / Docling benchmark route.

This judgment does not authorize live/provider/network/PDF/FDR commands, production parser replacement, Docling production dependency, source fallback, annual-period LLM route, repair-budget change, readiness/release/PR state change, or direct Service/UI/Host/renderer/quality-gate parser access.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- Plan: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md`
- DS review: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-ds-20260614.md`
- MiMo review: `docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-mimo-20260614.md`
- Route closeout: `docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md`

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run for this judgment.

## 3. Accepted Plan Facts

| Fact | Decision | Basis |
|---|---|---|
| The plan keeps Docling as a bounded benchmark candidate, not production parser. | ACCEPT | Plan §§1, 3, 7, 8; DS/MiMo PASS |
| The plan keeps document intermediates below fact truth; project-owned extractor / projection / EvidenceAnchor remains required. | ACCEPT | Plan §§2, 5, 7; `AGENTS.md`; `docs/design.md` |
| The plan preserves EID single-source/no-fallback policy. | ACCEPT | Plan §§2, 3, 4, 6, 7, 9; reviews |
| The plan preserves `NOT_READY`. | ACCEPT | Plan header, §§2, 10; reviews |
| The plan is planning-only and does not smuggle live/provider/PDF/FDR/readiness/PR work. | ACCEPT | Plan §3; DS/MiMo smuggled-work checks |
| The candidate `FundDisclosureDocument` schema is explicitly future/candidate-only. | ACCEPT | Plan §7; `docs/design.md` |

## 4. Findings Disposition

| Finding | Source | Decision | Controller rationale |
|---|---|---|---|
| Tier A source-identity metadata vs PDF body authorization is not split enough. | DS F1, MiMo F1 | ACCEPT_WITH_REWRITE | Next implementation/evidence gate must split Tier A into A1 metadata-only identity anchoring and A2 explicit FDR/PDF body access. Source-identity acceptance does not imply body-read authorization. |
| Tier B fund-type panel lacks deterministic selection heuristic. | DS F2 | ACCEPT_WITH_REWRITE | Slice 0 must predeclare candidate fund codes by fund type, minimum required types, substitution/skip rules and how `not_found` / `unavailable` becomes benchmark gap evidence. |
| Paragraph dimension may overclaim if body text cannot be committed. | DS F3, MiMo F3 | ACCEPT_WITH_REWRITE | Later evidence must use structural metrics and bounded/redacted excerpts only when explicitly authorized; no raw body text or full report body may be committed. |
| `benchmark-unavailable` is vague. | DS F4 | ACCEPT_WITH_REWRITE | Later metrics must use concrete per-sample fields such as `parser_status=unavailable`, `unavailable_reason` and dimension-level `skipped`. |
| Docling optional import mechanism is underspecified. | DS F5 | ACCEPT_WITH_REWRITE | Later implementation plan must prefer adapter-construction-time optional import and must not add Docling to default/production dependency groups without a separate dependency gate. |
| Docling/pdfplumber version reproducibility needs explicit contract. | DS F6 | ACCEPT_WITH_REWRITE | Later benchmark metadata must record parser package/version, adapter version, options hash and normalized schema version; version changes require re-running both parser paths. |
| Candidate schema text retention policy needs clearer cross-reference to artifact policy. | MiMo F2 | ACCEPT_WITH_REWRITE | Later schema plan/tests must mark raw body retention as off-by-default for committed fixtures. |
| Slice-specific coverage target not stated. | MiMo F5 | DEFER_TO_IMPLEMENTATION_PLAN | Apply existing `AGENTS.md` test policy in the next implementation gate; no planning blocker. |

No reviewer finding is rejected. No finding blocks accepting the plan, but DS F1/F2 are binding amendments before any evidence or implementation work may proceed.

## 5. Binding Amendments For Next Gate

The next gate may proceed only with these amendments in scope:

1. Split sample authorization:
   - Tier A1: metadata-only sample identity anchoring using already accepted source-identity facts.
   - Tier A2: parser benchmark body access, requiring explicit authorization and a no-live/non-live boundary decision before FDR/PDF body access.
2. Define Tier B selection:
   - predeclare candidate fund codes and fund types;
   - require at least one active equity fund and one bond fund if available under accepted source policy;
   - treat unavailable types as benchmark gaps, not fallback triggers or planning failures.
3. Keep Slice 0 and Slice 1 first:
   - Slice 0: sample manifest / artifact policy / benchmark authorization manifest;
   - Slice 1: candidate schema types/tests only;
   - defer Docling adapter, parser execution, comparator metrics and evidence execution until after Slice 0/1 are accepted.
4. Preserve all hard boundaries:
   - no live/provider/network/PDF/FDR commands unless a later gate explicitly authorizes the exact command class;
   - no production Docling/parser replacement;
   - no source fallback expansion;
   - no annual-period LLM route;
   - no readiness/release/PR claim.

## 6. Next Gate Recommendation

Proceed to:

```text
Annual-report Document Representation Sample Manifest And Candidate Schema No-live Implementation Gate
```

Scope of the next gate:

- implementation only for Slice 0 and Slice 1 from the accepted plan;
- no parser execution;
- no Docling adapter implementation unless separately planned after Slice 0/1;
- no live/provider/network/PDF/FDR commands;
- no report/PDF body inspection;
- no readiness/release/PR state.

## 7. Final Verdict

VERDICT: ACCEPT_WITH_BINDING_AMENDMENTS_NOT_READY

The planning gate is accepted. The route remains `NOT_READY`. The next gate is a no-live implementation gate limited to sample manifest/artifact policy and candidate schema foundations, with DS F1/F2 binding amendments applied before any evidence benchmark execution.
