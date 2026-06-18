# Docling Baseline Qualification Full Representation Export Handler Routing Decision Controller Judgment - 2026-06-15

Gate: `Full Representation Export Handler / Evidence Routing Decision Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the routing decision gate between the accepted candidate representation export harness and the next full-export work.

This judgment is decision-only. It does not implement handlers, run Docling conversion, run pdfplumber export, run EID HTML discovery, parse PDF bodies, call `FundDocumentRepository`, run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, change source policy, change production parser behavior, push or merge.

## 2. Artifacts Reviewed

- Routing decision: `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-20260615.md`
- DS review: `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-review-ds-20260615.md`
- MiMo review: `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-review-mimo-20260615.md`
- Accepted implementation judgment: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Decision

Controller accepts:

`ROUTE_TO_BUILT_IN_HANDLER_PLANNING_NOT_READY`

Meaning:

- the next gate is `Built-in Candidate Representation Route Handler Planning Gate`;
- direct evidence-time ad hoc Python handler injection is rejected;
- full representation export evidence must not proceed until handler planning and implementation are separately accepted;
- release/readiness remains `NOT_READY`.

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Routing to built-in handler planning is safer and more reproducible than direct evidence injection. | DS / MiMo | ACCEPT | Closed. |
| Decision preserves candidate-only status and `NOT_READY`. | DS / MiMo | ACCEPT | Closed. |
| Decision avoids production repository/source/cache behavior changes. | DS / MiMo | ACCEPT | Closed. |
| Decision preserves EID single-source/no fallback. | DS / MiMo | ACCEPT | Closed. |
| Decision avoids source truth, field correctness, taxonomy and readiness claims. | DS / MiMo | ACCEPT | Closed. |
| Decision gives enough constraints for the next planning worker. | DS / MiMo | ACCEPT | Closed. |

No blocking findings remain.

## 5. Blocked Claims

The following remain blocked:

- Docling can process S4/S5/S6;
- pdfplumber full representation can process S4/S5/S6;
- EID HTML render exists for S4/S5/S6;
- Docling is a baseline;
- any route is source truth;
- field correctness is proven;
- raw XML / raw XBRL direct download is proven;
- taxonomy compatibility is proven;
- `FundDocumentRepository` behavior can change;
- production parser replacement is authorized;
- readiness/release/PR readiness.

## 6. Binding Constraints For Next Gate

Next gate:

`Built-in Candidate Representation Route Handler Planning Gate`

The planning worker must define:

- exact handler module and API;
- whether handlers are in one module or split modules;
- lazy import policy for Docling and pdfplumber;
- no-network/no-model-download containment expectations for Docling;
- how pdfplumber consumes accepted candidate PDF paths without `cache/pdf` mutation;
- how S4/S5/S6 EID HTML render becomes blocked JSON unless a separate bounded discovery gate accepts render URLs;
- exact S1/S4/S5/S6 manifest entries;
- output overwrite policy for `reports/representation-json/*`;
- no-live tests with fake/minimal parser outputs;
- later evidence command matrix.

The next gate must not:

- run Docling conversion;
- run pdfplumber export;
- read PDF bodies;
- run live/network/EID/FDR commands;
- write `reports/representation-json/*`;
- write or read production-shaped `cache/pdf` as candidate input;
- modify `FundDocumentRepository`, sources, cache, Service, UI, Host, renderer, quality gate or extractor behavior;
- declare baseline, source truth, field correctness, taxonomy compatibility or readiness.

## 7. Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Built-in handler plan not written. | open | planning worker / controller | Immediate next gate. |
| Built-in Docling/pdfplumber handlers unimplemented. | open | implementation owner / controller | After planning/review acceptance only. |
| S4/S5/S6 EID HTML render URLs unaccepted. | open | EID HTML evidence owner | Deferred bounded discovery gate or blocked JSON. |
| S2/S3 provenance/hash residuals. | deferred | source provenance owner | Separate provenance resolution gate. |
| Control docs lag current accepted gate chain. | open | controller | Scoped control sync gate before longer execution or closeout. |

## 8. Validation

Required validation:

```text
git diff --check
```

Controller result: passed.

## 9. Final Verdict

`VERDICT: ACCEPT_ROUTING_DECISION_READY_FOR_BUILT_IN_HANDLER_PLANNING_GATE_NOT_READY`
