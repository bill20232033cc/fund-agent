# Docling Baseline Qualification Full Representation Export Plan Controller Judgment - 2026-06-15

Gate: `Full Representation Export Planning Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the full representation export planning gate for Docling baseline qualification.

It accepts the plan only. It does not authorize Docling conversion, pdfplumber export, EID HTML discovery, PDF body parsing, provider/LLM, analyzer/checklist, golden, readiness, release, PR, push, merge, production parser replacement, `FundDocumentRepository` behavior change, source policy change, cache promotion or public consumer integration.

## 2. Artifacts Reviewed

- Plan: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-20260615.md`
- DS-role review: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-review-ds-20260615.md`
- MiMo-role review: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-review-mimo-20260615.md`
- Parent controller judgment: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Plan Decisions

| Decision | Controller disposition | Reason |
|---|---|---|
| Do not proceed directly to ad hoc full export evidence. | ACCEPT | Current repo has accepted S1 JSON artifacts but no tracked reproducible export harness. |
| Route next to `Candidate Representation Export Harness No-live Implementation Gate`. | ACCEPT | A candidate-only harness prevents one-off scripts and gives implementation/review a stable contract. |
| Keep implementation inside `fund_agent/fund/documents/candidates/`. | ACCEPT | This is the correct Fund documents candidate boundary and does not expose parser/source behavior to Service/UI/Host/renderer/quality gate. |
| Treat S1 as existing reference JSON only. | ACCEPT | S1 already has accepted Docling/pdfplumber/EID HTML full JSON artifacts. |
| Use S4/S5/S6 staged EID PDFs as required first-wave PDF-route inputs. | ACCEPT_WITH_BOUNDARY_AMENDMENT | Accepted staged paths may be consumed only by the Fund documents candidate harness in this evidence chain. They are not a production document-access pattern or `FundDocumentRepository` replacement. |
| Defer S2/S3 until provenance/hash resolution or explicit controller decision. | ACCEPT | Prevents silently promoting local candidates with residual provenance gaps. |
| Default S4/S5/S6 EID HTML render output to blocked JSON unless a separate bounded discovery gate accepts render URLs. | ACCEPT | EID HTML render cannot be inferred from staged PDF paths or `uploadInfoId`; it does not consume PDF. |
| Preserve `NOT_READY` and candidate-only status. | ACCEPT | Representation completeness is not field correctness, source truth, taxonomy proof, baseline qualification or release/readiness proof. |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Explicit staged paths are an exception-shaped diagnostic route. | DS-role review | ACCEPT_AS_BINDING_AMENDMENT | The accepted implementation/evidence gates must state that staged paths are only Fund documents candidate-harness inputs and cannot become production API, Service/UI/Host inputs or `FundDocumentRepository` replacement. |
| Full export evidence gate needs an explicit command/module entrypoint before execution. | DS-role review | ACCEPT_AS_BINDING_AMENDMENT | The implementation gate must define the accepted harness entrypoint, input manifest path and output directory. Controller must not open export evidence until this is present. |
| No blocking issue found; plan can proceed to no-live implementation. | MiMo-role review | ACCEPT | Closed. |

No unresolved blocking finding remains.

## 5. Blocked Claims

The following claims remain blocked:

- Docling is a production baseline;
- Docling output is source truth;
- pdfplumber full JSON is a production `FundDisclosureDocument` schema;
- EID HTML render is raw XML / raw XBRL instance truth;
- raw XML direct download is proven;
- field correctness is proven;
- taxonomy compatibility is proven;
- S2/S3 are accepted baseline qualification samples;
- S4/S5/S6 EID HTML render is available;
- staged PDFs are production cache entries;
- production parser replacement is authorized;
- `FundDocumentRepository` behavior can change;
- release/readiness/PR readiness.

## 6. Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Candidate export harness not implemented. | Fund documents candidate owner / controller | `Candidate Representation Export Harness No-live Implementation Gate`. |
| Harness command/module entrypoint not yet accepted. | Implementation owner / controller | Must be defined and reviewed in implementation gate before evidence execution. |
| Explicit staged path consumption remains a candidate-evidence exception. | Controller / implementation reviewer | Re-check during implementation and evidence review. |
| S2/S3 provenance/hash residuals. | Controller / source provenance owner | Deferred `S2/S3 Local Cache Provenance Resolution Gate` or explicit controller decision. |
| S4/S5/S6 EID HTML render availability. | EID HTML evidence owner / controller | Deferred bounded discovery gate; blocked JSON is acceptable until then. |
| Control docs lag the latest accepted gate chain. | Controller | Scoped control sync gate after accepted checkpoint or before a longer implementation run. |

## 7. Next Gate

Primary next gate:

`Candidate Representation Export Harness No-live Implementation Gate`

Binding constraints for that gate:

- write only the plan-accepted implementation/test/evidence files unless review requires a scoped amendment;
- keep candidate internals out of `fund_agent.fund.documents` public exports;
- define an explicit accepted command or module entrypoint;
- define an explicit input manifest path contract and allowed output directory;
- do not run Docling conversion in unit tests;
- do not run live/network/provider/LLM/analyzer/checklist/golden/readiness/release/PR commands;
- do not write `cache/pdf/` or modify production cache/repository/source behavior;
- preserve EID single-source/no fallback and `NOT_READY`.

Deferred gates:

- `Full Representation Export Evidence Gate`
- `S2/S3 Local Cache Provenance Resolution Gate`
- `S4/S5/S6 EID HTML Render Discovery Gate`
- `EID Staged PDF Cache Promotion Planning Gate`
- `Field Correctness Validation Gate`
- `FundDisclosureDocument Production Schema / Repository Integration Planning Gate`
- readiness/release/PR gates

## 8. Validation

Required validation after writing this judgment:

```text
git diff --check
```

Controller result: passed.

## 9. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_CANDIDATE_REPRESENTATION_EXPORT_HARNESS_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`
