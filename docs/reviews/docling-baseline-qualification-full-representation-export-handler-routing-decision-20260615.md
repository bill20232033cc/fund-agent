# Docling Baseline Qualification Full Representation Export Handler Routing Decision - 2026-06-15

Gate: `Full Representation Export Handler / Evidence Routing Decision Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This gate decides how to move from the accepted candidate representation export harness to reproducible full representation export evidence.

It does not implement handlers, run Docling conversion, run pdfplumber export, run EID HTML discovery, parse PDF bodies, call `FundDocumentRepository`, run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, change source policy, change production parser behavior or claim readiness.

## 2. Evidence Reviewed

- Rules: `AGENTS.md`
- Design truth: `docs/design.md`
- Control docs: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- Accepted implementation judgment: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`
- Accepted plan judgment: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-controller-judgment-20260615.md`
- Current harness implementation: `fund_agent/fund/documents/candidates/representation_export.py`

## 3. Current Accepted Facts

| Fact | Status |
|---|---|
| Candidate export harness exists and is accepted. | accepted code fact |
| Harness supports manifest validation, candidate envelope, blocked JSON and injectable route handlers. | accepted code fact |
| Harness does not include built-in Docling/pdfplumber conversion handlers. | accepted residual |
| S1 `004393 / 2025` has accepted full JSON route artifacts. | accepted evidence fact |
| S4/S5/S6 have accepted staged EID PDF artifacts. | accepted evidence fact |
| S4/S5/S6 EID HTML render URLs are not accepted. | open residual |
| S2/S3 provenance/hash residuals remain. | deferred residual |
| Release/readiness remains `NOT_READY`. | binding |

## 4. Options Considered

| Option | Decision | Reason |
|---|---|---|
| A. Proceed directly to evidence gate with ad hoc Python handler injection. | REJECT | This would reintroduce one-off scripts and make the evidence hard to reproduce or review. It also risks bypassing the accepted command/module entrypoint requirement from DS review. |
| B. Implement built-in candidate route handlers first. | ACCEPT | This creates a stable, reviewable execution surface for Docling/pdfplumber full representation export and keeps later evidence from inventing parsing logic. |
| C. Pause Docling route and return to XBRL HTML only. | REJECT | The current product question is Docling baseline qualification; accepted evidence already shows Docling has strong full-document representation signal for S1. |
| D. Promote staged PDFs into `cache/pdf` before handler work. | REJECT_FOR_NOW | Current harness can consume explicit staged paths as candidate-evidence inputs. Cache promotion is only needed if a future implementation proves explicit staged paths cannot work safely. |
| E. Open S4/S5/S6 EID HTML render discovery first. | DEFER | EID HTML does not consume staged PDFs. It can be represented as blocked JSON in the first export evidence and reopened separately if tri-route evidence is required. |

## 5. Controller Decision

Choose Option B:

`Built-in Candidate Representation Route Handler Planning Gate`

Rationale:

- It is the shortest reproducible route to full export evidence.
- It keeps Docling/pdfplumber logic inside Fund documents candidate internals.
- It avoids temporary evidence scripts that future reviewers cannot regenerate.
- It preserves the current production parser and repository boundary.
- It lets S4/S5/S6 use the accepted staged EID PDFs without writing `cache/pdf`.

## 6. Binding Constraints For Next Gate

Next gate is planning-only.

Allowed planning targets:

```text
fund_agent/fund/documents/candidates/representation_handlers.py
fund_agent/fund/documents/candidates/representation_export.py
tests/fund/documents/test_candidate_representation_handlers.py
tests/fund/documents/test_candidate_representation_export.py
fund_agent/fund/README.md
docs/reviews/<gate artifacts>
```

Planning must decide:

- exact built-in handler API;
- whether Docling and pdfplumber handlers live in one module or separate modules;
- how to keep handler invocation inside candidate internals;
- whether handler implementation may import Docling/pdfplumber directly or should lazy-import inside handler functions;
- how to enforce no network / no model download expectations for Docling;
- how to represent S4/S5/S6 EID HTML render as blocked JSON unless a later discovery gate accepts URLs;
- exact manifest entries for S1 reference JSON and S4/S5/S6 first-wave PDF routes;
- output overwrite policy for `reports/representation-json/*`;
- no-live tests using tiny fixtures / mocks, not full annual-report conversion;
- evidence gate commands after handler acceptance.

Forbidden in next planning gate:

- running Docling conversion;
- running pdfplumber full export;
- reading PDF bodies;
- running live/network/EID/FDR commands;
- writing `reports/representation-json/*`;
- writing or reading production-shaped `cache/pdf` as candidate input;
- modifying `FundDocumentRepository`, sources, cache, Service, UI, Host, renderer, quality gate or extractor behavior;
- declaring Docling baseline, source truth, field correctness, taxonomy compatibility or readiness.

## 7. Expected Handler Implementation Direction

The next implementation plan should prefer:

- lazy imports for optional parser dependencies;
- deterministic conversion functions that accept an already accepted manifest entry and return a candidate envelope payload;
- explicit runtime containment flags and failure taxonomy for Docling;
- pdfplumber handler that operates only on the accepted candidate PDF path and emits representation metrics, not business facts;
- blocked EID HTML handler for samples without accepted render URL;
- tests with fake/minimal parser outputs and path/hash checks, not large real PDFs.

The plan must not require implementation workers to design field-correctness comparison, EvidenceAnchor production schema, CHAPTER_CONTRACT consumption, Service integration or readiness criteria.

## 8. Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Built-in handler plan not written. | open | planning worker / controller | `Built-in Candidate Representation Route Handler Planning Gate`. |
| S4/S5/S6 EID HTML render URLs unaccepted. | open | EID HTML evidence owner | Deferred bounded discovery gate; blocked JSON is acceptable before then. |
| S2/S3 provenance/hash residuals. | deferred | source provenance owner | Separate provenance resolution gate. |
| Control docs lag current accepted gate chain. | open | controller | Scoped control sync gate after handler planning or before longer execution. |
| Full representation export evidence not run. | open | evidence owner | Only after handler implementation acceptance. |

## 9. Final Verdict

`VERDICT: ROUTE_TO_BUILT_IN_HANDLER_PLANNING_NOT_READY`
