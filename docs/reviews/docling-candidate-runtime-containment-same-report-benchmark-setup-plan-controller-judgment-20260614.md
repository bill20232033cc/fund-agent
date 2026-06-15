# Docling Candidate Runtime Containment And Same-report Benchmark Setup Plan Controller Judgment - 2026-06-14

Status: ACCEPTED_NOT_READY
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate`
Controller: AgentController
Plan artifact: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`

## 1. Scope

This judgment accepts a planning artifact only. It does not authorize implementation, production parser changes, dependency installation, Docling adapter work, repository behavior change, fallback/source expansion, provider/LLM work, readiness/release/PR action, or field correctness/taxonomy/source-truth claims.

The primary future benchmark sample is:

```text
fund_code=004393
fund_name=安信企业价值优选混合A
preferred_year=2025
fallback_years=2024, 2023, 2022 only if 2025 identity or route discovery is blocked
```

Release/readiness remains `NOT_READY`.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-ds-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-mimo-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-rereview-ds-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-rereview-mimo-20260614.md`

## 3. Review Summary

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentDS | `PASS_WITH_FINDINGS` | `PASS` | Accept. All DS findings closed by plan amendments. |
| AgentMiMo | `PASS_WITH_FINDINGS` | `PASS_WITH_RESIDUALS` | Accept. All MiMo plan findings closed; startup/control sync remains controller residual. |

## 4. Findings Disposition

| Finding | Source | Disposition | Controller rationale |
|---|---|---|---|
| `do_ocr=False` alone may not prevent non-OCR model downloads. | DS-F1 / MiMo-F1 | `ACCEPTED_CLOSED` | Plan now requires inspection of all visible Docling PDF pipeline/format options that may trigger model initialization, artifact lookup, table/layout model use, OCR, accelerator/device selection, remote artifact retrieval or network access. |
| Containment enforcement mechanism was underspecified. | DS-F2 / MiMo-F1 | `ACCEPTED_CLOSED` | Plan now requires conversion-phase socket blocking in a subprocess plus offline/fail-closed environment flags where supported; Docling conversion remains forbidden until C0/C1 prove no unaccepted model download path. |
| Residual RapidOCR model files could create false offline proof. | DS-F3 / MiMo-F2 | `ACCEPTED_CLOSED` | Plan now requires classification `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` for any conversion that succeeds only because of residual files from the prior boundary incident. |
| Evidence worker could invent schema/code artifacts. | DS-F4 | `ACCEPTED_CLOSED` | Plan now explicitly forbids new production types, classes, modules, schemas, repository APIs, comparison schema artifacts and code artifacts. |
| Candidate label could drift from formal `eid_xbrl_html_render_candidate`. | MiMo-F3 | `ACCEPTED_CLOSED` | Plan retains formal source classification and requires future evidence artifact to restate it. |
| Startup packet still names prior active gate. | MiMo residual | `ACCEPTED_CONTROLLER_SYNC_RESIDUAL` | This is not a plan blocker. It must be handled by scoped control sync after plan acceptance. |

## 5. Accepted Plan Requirements

The next evidence gate must preserve these binding requirements:

- primary sample is `004393 / 安信企业价值优选混合A`, preferred year `2025`;
- local `基金年报/` PDFs remain user-owned data artifact candidates, not source truth;
- all production annual-report/PDF access remains inside Fund documents / `FundDocumentRepository` ownership;
- `eid_xbrl_html_render_candidate` remains candidate render classification, not raw XML or raw XBRL instance;
- Docling handling must run C0 import/introspection before any conversion;
- Docling conversion may run only after C0/C1 prove no unaccepted model download path and must use conversion-phase socket blocking;
- residual RapidOCR model files must be recorded and cannot prove offline containment;
- no field correctness, raw XML, taxonomy compatibility, source truth, parser replacement, readiness, release or PR claim is allowed.

## 6. Residuals

| Residual | Owner | Next handling |
|---|---|---|
| `docling_runtime_containment_unproven` | Evidence worker / controller | Prove or fail closed in the next evidence gate. |
| `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` | Evidence worker / controller | Record residual model presence and ensure it is not used as self-contained proof. |
| `004393_eid_html_render_identity_unproven` | Evidence worker / controller | Discover official EID HTML render for selected year or stop with identity/route blocker. |
| Startup/control docs still reference prior planning gate | Controller | Scoped control sync after this judgment. |
| Release/readiness | Release owner / controller | Remains `NOT_READY`. |

## 7. Verdict

```text
VERDICT: ACCEPT_WITH_REVIEW_FIXES_READY_FOR_EVIDENCE_GATE_NOT_READY
```

Next gate:

```text
Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate
```

Do not automatically enter design or implementation. Do not stage, commit, push or create PR from this judgment.
