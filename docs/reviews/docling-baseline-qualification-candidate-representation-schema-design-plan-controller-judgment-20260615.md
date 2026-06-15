# Docling Baseline Qualification Candidate Representation Schema Design Plan Controller Judgment - 2026-06-15

Gate: `Candidate Representation Schema / Design Plan Review Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes review for the candidate representation schema/design plan.

Reviewed plan:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-review-mimo-20260615.md`

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`

## 3. Controller Disposition

| Review point | Source | Disposition | Reason |
|---|---|---|---|
| No over-promotion of Docling structural coverage. | DS + MiMo | ACCEPT | Reviews confirmed the plan keeps structural coverage separate from source truth, field correctness, baseline qualification, parser replacement and readiness. |
| Three candidate routes represented. | DS + MiMo | ACCEPT | Plan covers `docling_pdf_candidate`, `pdfplumber_pdf_candidate` and `eid_xbrl_html_render_candidate` with route-specific locator differences. |
| Production boundaries preserved. | DS + MiMo | ACCEPT | Plan does not modify public `EvidenceAnchor`, `FundDocumentRepository`, production parser, source policy, Service/UI/Host/renderer/quality gate. |
| Next gate sequencing. | DS + MiMo | ACCEPT | Next gate is no-live implementation planning, not production implementation or parser replacement. |

## 4. Accepted Plan Facts

The accepted plan may be used as input for the next planning gate. It accepts only:

- candidate-internal route-neutral schema planning;
- route-specific locator preservation;
- internal candidate-to-`EvidenceAnchor.note` mapping planning;
- baseline qualification criteria as future acceptance criteria, not current qualification;
- future no-live implementation planning.

It does not accept:

- production parser replacement;
- public `EvidenceAnchor` schema change;
- `FundDocumentRepository` behavior change;
- source policy change;
- non-EID fallback;
- field correctness/source truth/taxonomy/readiness/release claims.

## 5. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Existing candidate models are Docling-first and do not yet support all three route kinds. | Accepted residual | Candidate Representation Schema No-live Implementation Planning Gate. |
| Candidate heading filtering and section tree semantics remain undefined. | Accepted residual | Candidate schema/design implementation planning and locator stability evidence. |
| Field-family correctness remains unproven. | Deferred | Field-family correctness pilot after candidate schema implementation/evidence. |
| Production integration remains out of scope. | Deferred | Separate production integration planning after schema/evidence acceptance. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No readiness/release/PR claim. |

## 6. Validation

Required checkpoint validation:

```text
git diff --check
git status --short
git status --branch --short
```

## 7. Final Verdict

`VERDICT: ACCEPT_SCHEMA_DESIGN_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`

Next recommended gate:

`Candidate Representation Schema No-live Implementation Planning Gate`

Do not proceed directly to production implementation, parser replacement, field correctness promotion, readiness, release or PR.
