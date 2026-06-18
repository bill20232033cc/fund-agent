# Docling Baseline Qualification Plan Controller Judgment

Date: 2026-06-15

Gate: `Docling Baseline Qualification Planning Gate`

Role: controller

Verdict: `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_ACQUISITION_STATUS_PLANNING_GATE_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the plan gate for proving whether Docling can qualify as a baseline candidate for annual-report document representation.

Accepted plan:

- `docs/reviews/docling-baseline-qualification-plan-20260615.md`

Reviews:

- DS initial review: `docs/reviews/docling-baseline-qualification-plan-review-ds-20260615.md`
- MiMo initial review: `docs/reviews/docling-baseline-qualification-plan-review-mimo-20260615.md`
- DS targeted re-review: `docs/reviews/docling-baseline-qualification-plan-rereview-ds-20260615.md`
- MiMo targeted re-review: `docs/reviews/docling-baseline-qualification-plan-rereview-mimo-20260615.md`

This judgment does not authorize implementation, Docling conversion, live/network/EID/FDR/PDF download, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, source/test/runtime behavior changes, production parser replacement, `FundDocumentRepository` behavior change, source policy change, raw XML claim, field correctness claim, source-truth claim, taxonomy compatibility claim, readiness claim, stage, commit, push or PR.

## 2. Accepted Plan Facts

| Plan fact | Controller disposition |
|---|---|
| The plan distinguishes `baseline candidate` from `production baseline`; production baseline cannot be declared by this plan or by single-sample representation evidence. | ACCEPT |
| Docling remains candidate-only and must not be treated as source truth, field correctness proof, raw XML/XBRL proof, taxonomy proof, readiness proof or parser replacement. | ACCEPT |
| The minimum qualification matrix is six fund/year profiles, but only S1 currently has accepted same-report Docling/pdfplumber/EID HTML representation JSONs. | ACCEPT |
| Gate 0 is now a required prerequisite family before runtime/coverage evidence: sample status, bounded EID-only acquisition where needed, pdfplumber exports, field-reference establishment and EID HTML availability classification. | ACCEPT |
| Gate D now separates D1 identity/structural comparison from D2 true field correctness. D2 may score only sample/field-family pairs with accepted same-report reviewed/golden reference facts. | ACCEPT |
| The dependency chain is explicit: acquisition status planning -> bounded EID-only acquisition if needed -> pdfplumber export if needed -> reference-fact acquisition -> runner planning if needed -> Gates A-E evidence -> Gate F disposition. | ACCEPT |
| Verdict criteria preserve `NOT_READY` and include baseline-candidate, hybrid-primary, auxiliary-candidate and rejected outcomes. | ACCEPT |
| Current production source policy remains EID single-source/no-fallback; no Eastmoney, CNINFO, fund-company website or other fallback is reintroduced. | ACCEPT |
| All future implementation or evidence work must remain inside the Fund documents / `FundDocumentRepository` boundary; Service/UI/Host/renderer/quality gate must not directly consume Docling/PDF/parser artifacts. | ACCEPT |

## 3. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| S2-S6 field correctness reference facts undefined; Gate D would be untestable. | DS-F1 / MiMo-P2 | ACCEPT_AS_REQUIRED_FIX | CLOSED by Gate 0D, D1/D2 separation and D2 accepted-reference-only scoring. |
| S2-S6 local artifacts and pdfplumber baseline prerequisites unproven. | DS-F2 / MiMo-P1 | ACCEPT_AS_REQUIRED_FIX | CLOSED by Gate 0A/0B/0C and explicit S1 versus S2-S6 availability table. |
| EID-only sample acquisition dependency chain was hidden. | MiMo-P3 | ACCEPT_AS_REQUIRED_FIX | CLOSED by explicit Section 11 dependency chain. |
| Gate A auxiliary verdict mapping was ambiguous. | DS-F3 | ACCEPT_AS_REQUIRED_FIX | CLOSED by mapping isolated fail-closed conversion failure to auxiliary candidate and unclassified or repeated failure to rejected. |
| Performance threshold needed calibration path. | MiMo-P4 | ACCEPT_AS_NONBLOCKING_FIX | CLOSED by Gate E calibration from Gate A logs. |
| Page parity threshold was too binary. | MiMo-P5 | ACCEPT_AS_NONBLOCKING_FIX | CLOSED by route-difference classification and blocker only for unexplained missing source pages. |
| Hybrid routing semantics were underspecified. | MiMo-P6 | ACCEPT_AS_NONBLOCKING_FIX | CLOSED by minimum route semantics and deferral to later hybrid routing design if needed. |
| EID HTML availability for S2-S6 unclassified. | DS-F5 | ACCEPT_AS_RESIDUAL | Handled by Gate 0E before Gate D. |
| Table-count threshold band still needs evidence judgment. | DS-F4 | ACCEPT_AS_RESIDUAL | Deferred to Gate B evidence; taxonomy classification is required. |

Both targeted re-reviews returned `PASS_CLOSURE`; no blocking finding remains.

## 4. Binding Amendments For Next Gate

The next gate must preserve these binding amendments:

1. Do not run Docling conversion, EID acquisition, pdfplumber export or manual reference review inside the acquisition-status planning gate.
2. Classify S1-S6 artifact status explicitly:
   - accepted local artifact;
   - needs bounded EID-only acquisition;
   - needs replacement;
   - out of scope.
3. Classify pdfplumber full representation export status for every active sample.
4. Classify reviewed/golden reference fact coverage by sample and field family.
5. Classify EID HTML render availability by sample, without running live discovery unless a later bounded live evidence gate is explicitly opened.
6. Keep true field correctness separate from route agreement. Route agreement may prioritize review but cannot become source truth.
7. Keep all work candidate-only and `NOT_READY`.

## 5. Blocked Claims

The following claims remain blocked:

- Docling is production baseline;
- Docling is source truth;
- Docling field correctness is proven;
- raw XML / raw XBRL direct download is proven;
- taxonomy compatibility is proven;
- `FundDocumentRepository` behavior can change;
- Service/UI/Host/renderer/quality gate can directly consume Docling/PDF/parser artifacts;
- production parser replacement;
- readiness/release/PR readiness.

## 6. Next Gate

Recommended next gate:

```text
Docling Baseline Qualification Acquisition Status Planning Gate
```

Purpose:

- inventory S1-S6 artifact availability;
- identify which samples require bounded EID-only acquisition execution;
- identify missing pdfplumber full representation exports;
- identify missing same-report reviewed/golden reference facts by field family;
- identify EID HTML render availability status;
- produce a dependency-resolved execution plan for Gate 0 without running acquisition, conversion or field review.

This is planning-only. It should stop before any live/network/PDF/Docling conversion command unless a later controller/user explicitly authorizes a bounded evidence execution gate.

## 7. Deferred Entries

- Bounded EID-only Sample Acquisition Execution Gate.
- Pdfplumber Full Representation Export Planning/Execution Gate.
- Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate.
- Docling/pdfplumber Runner Planning Gate.
- Docling Baseline Runtime Containment Evidence Gate.
- Docling Full-document Coverage Evidence Gate.
- Docling EvidenceAnchor Mapping Evidence Gate.
- Docling Field Correctness Comparative Evidence Gate.
- Docling Performance / Cache / Cost Evidence Gate.
- Docling Baseline Disposition Controller Judgment.
- Any production repository integration, parser replacement, source-kind/schema change, readiness/release/PR gate.

## 8. Validation

Controller validation:

```text
git diff --check
```

Result: passed before this judgment was written.

## 9. Final Verdict

`VERDICT: ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_ACQUISITION_STATUS_PLANNING_GATE_NOT_READY`
