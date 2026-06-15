# Docling Baseline Qualification Full Representation Export Harness Implementation Controller Judgment - 2026-06-15

Gate: `Candidate Representation Export Harness No-live Implementation Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the candidate-only representation export harness implementation gate.

It accepts a no-live harness implementation. It does not accept Docling conversion evidence, pdfplumber full export evidence, EID HTML render discovery, field correctness, source truth, taxonomy compatibility, production parser replacement, `FundDocumentRepository` behavior change, source policy change, readiness, release, PR, push or merge.

## 2. Artifacts Reviewed

- Implementation evidence: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-evidence-20260615.md`
- DS implementation review: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-review-ds-20260615.md`
- MiMo implementation review: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-review-mimo-20260615.md`
- DS targeted re-review: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-rereview-ds-20260615.md`
- MiMo targeted re-review: `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-rereview-mimo-20260615.md`
- Accepted plan judgment: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Implementation Facts

| Fact | Controller disposition |
|---|---|
| `fund_agent/fund/documents/candidates/representation_export.py` defines candidate-only manifest, route/mode enums, path/hash validation, envelope builders, blocked-result generation, injectable route-handler export and CLI validation/write-blocked entrypoint. | ACCEPT |
| Route kinds are closed to `docling_pdf_candidate`, `pdfplumber_pdf_candidate` and `eid_xbrl_html_render_candidate`. | ACCEPT |
| Output envelope preserves `not_proven` source truth, field correctness and taxonomy status, plus `not_authorized` parser replacement status. | ACCEPT |
| Manifest validation rejects production-shaped `cache/pdf`, absolute paths and parent traversal. | ACCEPT |
| Existing S1 representation JSON can be validated through `reference_existing_json` without rewrite. | ACCEPT |
| Blocked JSON can represent missing EID HTML render route without raw XML, field correctness, taxonomy, source truth or readiness claims. | ACCEPT |
| Candidate internals remain outside `fund_agent.fund.documents.__all__`. | ACCEPT |
| `fund_agent/fund/README.md` documents the candidate-only boundary and non-proof status. | ACCEPT |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Path boundary checks could be bypassed with `..` traversal. | DS / MiMo initial reviews | ACCEPT_AS_BLOCKING | Fixed by rejecting absolute paths and any `..` component before output/cache/reference checks. |
| Traversal regression tests were missing. | DS / MiMo initial reviews | ACCEPT_AS_BLOCKING | Added output traversal and input-to-`cache/pdf` traversal tests. |
| Lack of built-in Docling/pdfplumber handlers. | DS / MiMo initial reviews | ACCEPT_AS_RESIDUAL_NOT_BLOCKING | This gate is the candidate harness slice. Real conversion/export remains a later reviewed handler/evidence gate. |
| Path-boundary blocker closed. | DS / MiMo targeted re-reviews | ACCEPT | Both targeted re-reviews returned `PASS`. |

No unresolved blocking finding remains.

## 5. Blocked Claims

The following remain blocked:

- Docling can process S4/S5/S6;
- pdfplumber full representation can process S4/S5/S6;
- EID HTML render exists for S4/S5/S6;
- Docling is a baseline;
- any representation route is source truth;
- any extracted field is correct;
- raw XML / raw XBRL direct download;
- taxonomy compatibility;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- release/readiness/PR readiness.

## 6. Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Built-in Docling/pdfplumber conversion handlers are not implemented. | open | Fund documents candidate owner / controller | Next gate must decide between a reviewed handler implementation or a controller-approved Python API injection evidence path. |
| S4/S5/S6 EID HTML render URLs remain unaccepted. | open | EID HTML evidence owner / controller | Use blocked JSON by default or open bounded EID HTML discovery gate. |
| S2/S3 provenance/hash residuals remain. | open | Source provenance owner / controller | Separate provenance resolution gate. |
| Control docs lag latest accepted gate chain. | open | Controller | Scoped control sync gate. |

## 7. Validation

Commands accepted:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
16 passed
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

## 8. Next Gate

Primary next gate:

`Full Representation Export Handler / Evidence Routing Decision Gate`

Purpose:

- decide whether to implement built-in Docling/pdfplumber route handlers before export evidence, or allow a tightly bounded evidence gate to inject reviewed route handlers through the accepted Python API;
- preserve the accepted candidate-only harness boundary;
- keep S4/S5/S6 EID HTML render as blocked JSON unless separate bounded discovery is opened;
- keep release/readiness as `NOT_READY`.

Do not proceed directly to production integration, field correctness validation, baseline qualification closeout, readiness or PR.

## 9. Final Verdict

`VERDICT: ACCEPT_IMPLEMENTATION_READY_FOR_HANDLER_OR_EVIDENCE_ROUTING_DECISION_GATE_NOT_READY`
