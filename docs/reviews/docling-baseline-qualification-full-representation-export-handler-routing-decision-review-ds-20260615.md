# Docling Baseline Qualification Full Representation Export Handler Routing Decision Review - DS - 2026-06-15

Verdict: `PASS`

Review target:

- `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-20260615.md`

Context checked:

- `AGENTS.md`
- `docs/design.md` Docling / `FundDisclosureDocument` / EID HTML render relevant sections
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`

## Findings

| ID | Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|---|
| None | none | The decision routes to `Built-in Candidate Representation Route Handler Planning Gate` instead of direct evidence injection, keeps the next gate planning-only, forbids Docling/pdfplumber execution, PDF body reads, live/network/EID/FDR commands, production source/cache/repository changes, and source truth / field correctness / taxonomy / readiness claims. This matches the implementation controller judgment, which left built-in handlers as the primary open residual and required a handler-or-evidence routing decision before evidence execution. | Proceed to the planned handler planning gate under the listed constraints. | no |

## Review Notes

- Routing to built-in handler planning is the safer next gate than evidence-time handler injection. The accepted harness already supports injectable handlers, but the controller decision correctly rejects ad hoc evidence injection because it would make full export evidence harder to reproduce and review.
- Candidate-only and `NOT_READY` are preserved. The decision explicitly states that it does not run handlers, conversion, PDF parsing, FDR, provider/LLM, readiness/release/PR, source policy changes, production parser behavior changes, or readiness claims.
- The decision remains consistent with `docs/design.md`: Docling is still only a future parallel benchmark / document representation candidate; EID HTML render remains `eid_xbrl_html_render_candidate`, not raw XML/source truth/taxonomy proof; production source policy remains EID single-source with no fallback.
- The next planning worker has enough constraints to produce an implementation-ready handler plan: candidate-internal file targets, lazy import question, no network/model-download expectations, S4/S5/S6 EID HTML blocked handling, manifest entries, overwrite policy, no-live tests, and post-acceptance evidence commands are all called out.

## Residuals

- Built-in Docling/pdfplumber handlers are still unimplemented and must remain candidate-only until separately planned, reviewed, implemented, and evidenced.
- S4/S5/S6 EID HTML render URLs remain unaccepted; blocked JSON remains the correct default unless a separate bounded discovery gate is opened.
- S2/S3 provenance/hash residuals and control-doc lag remain outside this routing decision review.

## Final Recommendation

Accept the routing decision and proceed to `Built-in Candidate Representation Route Handler Planning Gate`.
