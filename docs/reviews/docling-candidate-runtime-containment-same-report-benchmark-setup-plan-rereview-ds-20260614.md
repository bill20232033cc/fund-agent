# Docling Candidate Runtime Containment And Same-report Benchmark Setup Plan Re-review (DS) — 2026-06-14

Status: REREVIEW_COMPLETE
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate`
Reviewer: AgentDS (plan review worker, targeted re-review)
Prior review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-ds-20260614.md`
Plan under review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`

## Verdict

**PASS**

All four findings from the prior DS review (F1–F4) are closed. No new findings.

## Closure Table

| ID | Prior Severity | Status | Evidence of Closure |
|---|---|---|---|
| F1 | MEDIUM | **CLOSED** | §7 Stage C0 expanded from checking only `do_ocr` + table structure options to: "inspect all visible Docling `PdfPipelineOptions` and format options that may trigger model initialization, model artifact lookup, table-structure model use, layout model use, OCR, accelerator/device selection, remote artifact retrieval or network access" and "explicitly record whether any non-OCR pipeline stage appears to require model artifacts or network access." The C0 surface now covers the full pipeline option space, not just the OCR flag. |
| F2 | LOW | **CLOSED** | §7 Stage C1 now requires: "runs Docling conversion, if later allowed, in a subprocess that blocks Python socket connects during the conversion phase" and "sets offline/fail-closed environment variables where supported by the dependency stack, such as model-hub offline flags." §12 allowed commands now gate Docling conversion behind "conversion-phase socket blocking" and "only if C0/C1 prove no unaccepted model download path." The containment mechanism is now concrete: subprocess + socket blocking + offline env vars, not an unspecified wrapper. |
| F3 | LOW | **CLOSED** | §7 Stage C1 now requires: "classifies any conversion that succeeds only because of residual model files from the prior boundary incident as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`, not as proof that Docling is self-contained." This is a binding classification requirement — the evidence worker cannot silently depend on residual models or treat their presence as containment proof. |
| F4 | INFO | **CLOSED** | §8 Forbidden list now includes: "evidence worker invention of new production types, classes, modules, schemas, repository APIs, comparison schemas, or code artifacts." §12 Forbidden list now includes: "new production types/classes/modules/schemas/repository APIs/comparison schema artifacts." The prohibition is explicit in two sections and covers the full artifact surface. |

## Residuals

- **`rereview_C0_introspection_bound`**: C0 introspection is bounded by what is "visible" through Python import/introspection. If Docling `2.93.0` triggers model download through a non-public internal path (C extension, lazy import, indirect dependency), C0 alone cannot detect it. The C1 socket-blocking subprocess provides a second containment layer that catches what C0 misses. This is a defense-in-depth design, not a gap.
- **`rereview_socket_blocking_implementation`**: The plan specifies "blocks Python socket connects" as a requirement but delegates the exact mechanism to the evidence worker (e.g., `socket.socket` monkeypatch, `HTTP_PROXY` override, or OS-level network namespace). This is acceptable — the requirement is reviewable and the evidence gate must prove the mechanism worked before advancing to C2.

## Recommendation

Proceed to controller judgment. All four prior findings are addressed with concrete, reviewable amendments. The two informational residuals are inherent to any containment-by-introspection design and are mitigated by the dual-layer C0+C1 strategy.
