# Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate Plan Review - MiMo - 2026-06-14

Status: REVIEW_COMPLETE
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate`
Reviewer: AgentMiMo
Plan artifact: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`

## 1. Verdict

```text
PASS_WITH_FINDINGS
```

## 2. Review Focus Verification

| # | Focus | Verdict | Evidence |
|---|---|---|---|
| 1 | Primary ordinary non-REIT sample is `004393 / 安信企业价值优选混合A` | PASS | §1: `fund_code=004393, fund_name=安信企业价值优选混合A, preferred report year=2025`; §6 Sample Matrix: A1 = `004393 / 2025` as preferred ordinary non-REIT benchmark; fallback years 2024/2023/2022 only if 2025 blocked |
| 2 | Local `基金年报/` PDFs remain user-owned candidates, not source truth | PASS | §4: "These files are user-owned data artifact candidates. They are not current source truth and must not be body-read unless a later evidence gate records explicit user authorization"; §8 route priority 3: "local file only if a later evidence gate explicitly authorizes local user-owned PDF access and records why the route remains repository-compatible" |
| 3 | Docling runtime containment required before any convert; no dependency install / model download / uncontrolled network | PASS | §7 Stage C0: import/inspect only, do not call convert; C1: no-network/no-download containment plan; C2: bounded conversion only after C0/C1 pass; §12 Forbidden: "dependency installation", "Docling/OCR runtime model download"; §13 Stop: "Docling conversion requires OCR model download, model initialization network, dependency installation or uncontrolled runtime side effects" |
| 4 | `do_ocr=False` or equivalent no-OCR path reduces OCR model download risk | PASS | §5: `PdfPipelineOptions.do_ocr` default `True` observed; §7 C1: "sets PdfPipelineOptions.do_ocr=False for text-native annual reports"; §13 Stop: "Docling cannot be configured with do_ocr=False or equivalent no-OCR bounded path" |
| 5 | All PDF access within Fund documents / FundDocumentRepository ownership | PASS | §8: three-route priority (FDR/adapter → cache with metadata → local only with explicit authorization); Forbidden: "direct arbitrary PDF path parsing without repository-compatible ownership", "direct body read of 基金年报/*.pdf in planning" |
| 6 | EID HTML render kept as `eid_xbrl_html_render_candidate`, not called raw XBRL | PASS | §1: "eid_xbrl_html_render_candidate" explicitly listed as route 1; §3 Non-goals: "Do not claim raw XML direct download, raw XBRL instance availability"; no section calls HTML render "raw XBRL" or "raw XML" |
| 7 | Avoids field correctness, taxonomy, source truth, parser replacement, readiness/release claims | PASS | §3 Non-goals: full prohibition list; §12 Forbidden: "field correctness comparison", "taxonomy proof", "raw XML endpoint probing", "source fallback invocation"; §13 Stop: evidence needing "field correctness, raw XML or taxonomy claims" |
| 8 | Allowed commands / stop conditions sufficient for next evidence gate without schema invention | PASS | §12: explicit allowed and forbidden command lists; §13: 10 stop conditions covering containment, identity, auth, domain, source, behavior, correctness and workspace state; §11: all allowed verdicts end with `_NOT_READY` |

## 3. Findings

| id | severity | finding | evidence | recommendation |
|---|---|---|---|---|
| F1 | medium | `do_ocr=False` may not be sufficient to prevent all model downloads. Docling's `DocumentConverter` pipeline may also require layout detection models and table structure models beyond OCR. The plan's §7 C1 only specifies `do_ocr=False` as the containment mechanism, but does not inspect or constrain `PdfPipelineOptions` layout/table model download behavior. Prior evidence (§11 in same-report evidence) shows the conversion triggered RapidOCR model downloads, but the plan does not verify whether `do_ocr=False` alone would have prevented that download or whether layout/table models would still be fetched. | §7 C1: "sets PdfPipelineOptions.do_ocr=False for text-native annual reports"; §5 only records `do_ocr` default; no inspection of layout/table model options | Evidence gate C0 must inspect all `PdfPipelineOptions` model-related flags (not just `do_ocr`), and C1 must define containment for layout/table model downloads as well. If Docling still attempts model download with `do_ocr=False`, the stop condition in §13 must trigger. |
| F2 | medium | §5 records RapidOCR model files in `.venv/lib/python3.11/site-packages/rapidocr/models` as residue. The plan does not specify whether residual layout/table structure model files may also exist from the prior incident, or whether the evidence worker should inventory all Docling-related model caches (not just RapidOCR). §7 C1 "records whether existing model files are present" is too narrow. | §5: only RapidOCR models mentioned; §7 C1: "records whether existing model files are present" without specifying full inventory scope | Evidence gate must inventory all Docling-related model caches under `.venv/` (RapidOCR, layout, table structure, any `docling` or `docling_core` model directories) before conversion, and record whether they are sufficient for fully offline conversion or whether additional downloads would be triggered. |
| F3 | low | §9 and §10 use "EID HTML render" as shorthand while §1 uses the full classification `eid_xbrl_html_render_candidate`. The comparison metrics table header says "EID HTML render" rather than the formal candidate label. This is internally consistent with the plan's established classification but could drift in future evidence artifacts. | §1 uses `eid_xbrl_html_render_candidate`; §10 table header uses "EID HTML render" | Acceptable for readability. Evidence gate should restate the formal `eid_xbrl_html_render_candidate` classification in its scope section. |

## 4. Residuals

| Residual | Status | Notes |
|---|---|---|
| `tier_a_ordinary_annual_not_available` | Addressed | Plan selects `004393` ordinary non-REIT annual as primary sample; prior evidence only had REIT samples |
| `docling_runtime_uncontained` | Addressed | Plan defines C0/C1/C2 containment stages; evidence gate must execute them |
| `raw_xml_not_proven` | Retained | Plan does not claim raw XML; no change |
| `field_correctness_not_proven` | Retained | Plan explicitly forbids field correctness claims; no change |
| `taxonomy_compatibility_not_proven` | Retained | Plan explicitly forbids taxonomy claims; no change |
| `not_source_truth` | Retained | Plan explicitly preserves NOT_READY and source truth boundary; no change |
| RapidOCR residual model files in `.venv` | Retained | F2: plan records presence but does not prescribe action; evidence worker must document |
| Startup packet sync | Noted | `docs/current-startup-packet.md` §2 "Current active gate" still references `Same-report Document Representation Quality Comparison Planning Gate`; controller must sync after plan acceptance |

## 5. Boundary Compliance

- No source/test/runtime behavior changes proposed.
- No live EID/network/PDF/FDR/parser/Docling/analyze/checklist/readiness/release/PR/push/merge commands.
- No stage/commit actions.
- Plan is planning-only, consistent with gate classification `standard`.

## 6. Recommendation

Plan is handoff-ready for controller judgment. All 8 review focus areas pass. Three low-severity findings are noted but do not block acceptance. The evidence gate must address F1 by specifying a concrete network-blocking enforcement mechanism before running any Docling conversion.

```text
artifact path: docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-review-mimo-20260614.md
verdict: PASS_WITH_FINDINGS
primary benchmark sample: 004393 / 安信企业价值优选混合A / 2025 annual
non-goals preserved: yes
findings: 3 low
residuals: 7 retained, 1 startup packet sync noted
recommendation: accept plan; evidence gate must specify network-blocking enforcement mechanism
```
