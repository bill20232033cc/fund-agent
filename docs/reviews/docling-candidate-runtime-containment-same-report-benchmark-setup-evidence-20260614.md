# Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence - 2026-06-14

Status: `EVIDENCE_STOPPED_NOT_READY`
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate`
Role: role-scoped evidence worker; not controller; no full workflow started
Final verdict: `VERDICT: DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY`

## 1. Scope

This artifact records bounded evidence for the selected ordinary non-REIT sample:

```text
fund_code=004393
fund_name=安信企业价值优选混合A
preferred_report_year=2025
fallback_years=2024, 2023, 2022 only if 2025 identity or route discovery is blocked
```

The gate was required to perform Docling C0/C1 runtime containment checks before any official EID route discovery, Fund documents PDF acquisition, current pdfplumber parser execution, or Docling conversion.

Containment was not proven. Therefore no EID HTTP request, repository PDF acquisition, pdfplumber parser run, or Docling conversion was executed.

This artifact is evidence only. It does not implement parser code, add a Docling adapter, install dependencies, change `FundDocumentRepository`, invoke fallback sources, read local PDF bodies, run provider/LLM/analyze/checklist/readiness/release/PR commands, or claim source truth/readiness.

Readiness remains `NOT_READY`.

## 2. Inputs Reviewed

Read in the requested source-of-truth order:

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/current-startup-packet.md`
4. `docs/implementation-control.md`
5. `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`
6. `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-controller-judgment-20260614.md`
7. `docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md`

Commands executed:

```text
git status --branch --short
git status --short
find 基金年报 -maxdepth 1 -type f -name '*安信企业价值优选混合型证券投资基金*年度报告.pdf' -print
uv run python -c '<bounded Docling import/version/options introspection>'
uv run python -c '<bounded Docling no-OCR options and RapidOCR residual-file introspection>'
```

Commands intentionally not executed because containment was not proven:

```text
bounded official EID HTTP GET/HEAD to eid.csrc.gov.cn URLs only
repository-bounded EID single-source PDF metadata/path acquisition for 004393 selected year
current pdfplumber parser execution through Fund documents boundary
Docling conversion with do_ocr=false and conversion-phase socket blocking
```

Preflight status:

```text
branch=feat/mvp-llm-incomplete-run-artifacts
branch_state=ahead origin by 142 commits
existing_dirty_state=AGENTS.md, README.md, docs/current-startup-packet.md, docs/design.md, docs/implementation-control.md modified; many pre-existing untracked artifacts
scope_handling=this gate writes only this evidence artifact and ignores unrelated dirty/untracked state
```

## 3. Sample Selection And Identity Matrix

Primary sample selection:

| Priority | fund_code | fund_name | year | intended role | status |
|---|---|---|---:|---|---|
| A1 | `004393` | `安信企业价值优选混合A` | 2025 | preferred ordinary non-REIT annual sample | not reached because Docling containment failed before route discovery |
| A2 | `004393` | `安信企业价值优选混合A` | 2024 | fallback only if 2025 identity/route blocked | not reached |
| A3 | `004393` | `安信企业价值优选混合A` | 2023 | fallback only if A1/A2 blocked | not reached |
| A4 | `004393` | `安信企业价值优选混合A` | 2022 | fallback only if A1-A3 blocked | not reached |

Local user-owned PDF filename inventory:

```text
基金年报/安信企业价值优选混合型证券投资基金2024年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2025年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2023年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2022年年度报告.pdf
```

Identity classification:

| route | identity status | evidence boundary |
|---|---|---|
| local PDF filenames | `identity_partly_matched_local_candidate_only` | filename inventory only; no body read; not source truth |
| official EID HTML render | `not_attempted_after_containment_block` | no EID HTTP request executed |
| FundDocumentRepository PDF | `not_attempted_after_containment_block` | no repository PDF acquisition executed |
| Docling candidate | `blocked_before_conversion` | no conversion executed |

No sample reached `identity_match_ordinary_non_reit_annual`.

## 4. Docling Runtime Containment Checks

### C0 Import And Visible Options Introspection

Observed Docling version:

```text
docling_version=2.93.0
```

Observed `PdfPipelineOptions` defaults and relevant fields:

| option | observed value | containment implication |
|---|---|---|
| `do_ocr` | default `True`; can be configured `False` | no-OCR path exists, but this alone is insufficient |
| `do_table_structure` | default `True` | table model path remains active unless separately disabled/proven local |
| `table_structure_options.mode` | `TableFormerMode.ACCURATE` | visible model-backed table-structure stage; no local artifact proof accepted |
| `layout_options.model_spec.name` | `docling_layout_heron` | visible layout model stage |
| `layout_options.model_spec.repo_id` | `docling-project/docling-layout-heron` | visible remote model repository identifier |
| `layout_options.model_spec.revision` | `main` | visible model revision |
| `layout_options.model_spec.model_path` | empty string | no explicit accepted local model path |
| `artifacts_path` | `None` | no explicit accepted local artifact directory |
| `enable_remote_services` | `False` | remote services disabled, but not proof that model artifacts cannot be fetched |
| `allow_external_plugins` | `False` | external plugins disabled |
| `accelerator_options.device` | default `auto` | device selection not pinned; not itself a network proof |
| `picture_classification_options.model_spec.repo_id` | `docling-project/DocumentFigureClassifier-v2.5` | disabled by `do_picture_classification=False`, but visible model option exists |
| `picture_description_options.model_spec.default_repo_id` | `HuggingFaceTB/SmolVLM-256M-Instruct` | disabled by `do_picture_description=False`, but visible model option exists |
| `code_formula_options.model_spec.default_repo_id` | `docling-project/CodeFormulaV2` | disabled by `do_code_enrichment=False` and `do_formula_enrichment=False`, but visible model option exists |
| `chart_extraction_options.model` | `granite-vision-v4` | disabled by `do_chart_extraction=False`, but visible model option exists |

No conversion was run.

### C1 No-network / No-download Containment Assessment

Configured no-OCR introspection:

```text
configured_do_ocr=False
configured_do_table_structure=True
configured_artifacts_path=None
configured_enable_remote_services=False
configured_allow_external_plugins=False
configured_accelerator_device=auto
layout_model_name=docling_layout_heron
layout_model_repo_id=docling-project/docling-layout-heron
layout_model_revision=main
layout_model_path=
table_mode=TableFormerMode.ACCURATE
table_do_cell_matching=True
ocr_option_type=OcrAutoOptions
ocr_force_full_page=False
```

Containment conclusion:

```text
C0_C1_CONTAINMENT_STATUS=blocked
```

Reason:

- `do_ocr=False` is configurable, but the visible standard PDF pipeline still has a model-backed layout stage with `repo_id=docling-project/docling-layout-heron`, `revision=main`, and no accepted local `model_path` or `artifacts_path`.
- Default table-structure extraction remains enabled with `TableFormerMode.ACCURATE`; this gate did not prove that the table stage is local-only or network-impossible.
- The options surface exposes additional remote model specs for picture classification, picture description, code/formula enrichment and chart extraction. Their corresponding feature toggles are false in the default/introspected path, so they are not the primary blocker, but they confirm that the options surface includes model-backed stages.
- `enable_remote_services=False` and `allow_external_plugins=False` are useful guardrails, but they do not prove that model artifact lookup/download cannot occur inside model-backed local stages.
- No accepted offline artifact directory was configured or proven.

Residual model files from the prior boundary incident:

```text
rapidocr_models_dir=.venv/lib/python3.11/site-packages/rapidocr/models
rapidocr_models_exists=True
rapidocr_models_files=[
  ch_PP-OCRv4_det_infer.onnx,
  ch_PP-OCRv4_det_mobile.pth,
  ch_PP-OCRv4_rec_infer.onnx,
  ch_PP-OCRv4_rec_mobile.pth,
  ch_ppocr_mobile_v2.0_cls_infer.onnx,
  ch_ptocr_mobile_v2.0_cls_mobile.pth,
  ppocr_keys_v1.txt,
  ppocrv5_dict.txt
]
classification=DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED
```

Because containment was not proven before conversion, the gate stopped before any conversion-phase socket-blocked Docling run. A socket-blocking wrapper would be necessary in a later gate, but it cannot substitute for the missing C0/C1 proof here.

## 5. Official EID HTML Render Discovery For 004393

Status: `not_attempted_after_containment_block`.

No official EID HTTP GET/HEAD request was executed. The plan requires first proving Docling containment before proceeding to same-report setup facts. Since C0/C1 failed, EID HTML render discovery for `004393 / 2025` and fallback years remains unproven.

Current classification remains:

```text
eid_xbrl_html_render_candidate=not_discovered_for_004393_in_this_gate
not_raw_xml
not_source_truth
not_field_correctness_proof
not_taxonomy_proof
```

## 6. FundDocumentRepository/PDF Ownership Proof

Status: `not_attempted_after_containment_block`.

No repository-bounded EID single-source PDF metadata/path acquisition was executed. No PDF body was read. No current pdfplumber parser execution was run.

Ownership proof remains blocked for this gate:

| proof | status |
|---|---|
| `selected_source=eid` for `004393 / selected_year` | not observed in this gate |
| `source_mode=single_source_only` | not observed in this gate |
| `fallback_enabled=false` / `fallback_used=false` | not observed in this gate |
| repository-produced PDF path | not acquired |
| PDF hash/content identity | not computed |
| local `基金年报/` file as source truth | forbidden; not used |

## 7. Route Availability Matrix

| route | status | evidence |
|---|---|---|
| `eid_xbrl_html_render_candidate` | `not_attempted_after_containment_block` | no official EID URL fetched in this gate |
| `pdfplumber_current` | `not_attempted_after_containment_block` | no Fund documents PDF acquisition or parser execution |
| `docling_candidate` | `blocked_before_conversion` | C0/C1 could not prove no unaccepted model download path |
| local PDF filenames | `candidate_inventory_only` | four annual-report filenames observed; no body read; not source truth |

No tri-route comparable same-report setup exists.

## 8. Section Structure Comparison

No section structure comparison was performed.

Reason:

```text
docling_runtime_containment_unproven
```

The prior accepted same-report evidence remains the only comparison input: REIT annual EID HTML render samples exposed visible navigation labels, while current pdfplumber on `180605 / 2025` collapsed section indexing to one `§1` section. That prior evidence is not an ordinary non-REIT `004393` same-report comparison and cannot be promoted here.

## 9. Table Structure Comparison

No table structure comparison was performed.

Reason:

```text
docling_runtime_containment_unproven
```

The current gate did not fetch EID HTML, acquire repository PDF, run pdfplumber, or run Docling conversion. No table-route winner or route-strength claim is supported.

## 10. Locator Comparison

No locator comparison was performed.

Blocked locator shapes:

| route | locator status |
|---|---|
| EID HTML render | no render URL, section anchor, table ordinal, row/column path discovered for `004393` |
| pdfplumber current | no repository PDF page/table locator observed for `004393` |
| Docling candidate | no element path, page span, bbox, table id, row/column/cell path observed |

## 11. Narrative/Text Block Comparison

No narrative/text block comparison was performed.

No official HTML paragraphs, repository PDF text slices, pdfplumber section text, or Docling text blocks were produced in this gate.

## 12. Performance And Runtime Side Effects

Measured/observed runtime facts:

| command family | result | side effects |
|---|---|---|
| `git status --branch --short` / `git status --short` | completed | read-only |
| local PDF filename `find` | completed | read-only filename inventory |
| Docling import/options introspection | completed | imported installed Python packages; no conversion |
| Docling no-OCR/residual introspection | completed | inspected option values and RapidOCR residual model directory; no conversion |

No dependency installation was attempted.
No Docling conversion was attempted.
No socket-blocked conversion subprocess was attempted.
No official EID network request was attempted.
No arbitrary network request was attempted.
No production source/test/runtime file was modified.
No cache or parser output was intentionally written by this gate.

Potential side-effect caveat:

```text
Importing Docling for introspection may initialize Python package metadata, but no parser/converter execution or model-download path was invoked in this gate.
```

## 13. Blocked Proofs And Residuals

| residual | status | next handling |
|---|---|---|
| `docling_runtime_containment_unproven` | blocking | requires a later containment gate proving local artifacts or disabling/proving model-backed stages before conversion |
| `layout_model_remote_repo_visible` | blocking | `docling-project/docling-layout-heron` visible with empty `model_path` and `artifacts_path=None` |
| `table_structure_model_path_unproven` | blocking | default `do_table_structure=True` with `TableFormerMode.ACCURATE`; no local-only proof |
| `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` | retained | RapidOCR model files exist but cannot prove self-contained setup |
| `004393_eid_html_render_identity_unproven` | retained | no official EID route discovery attempted |
| `004393_fdr_pdf_ownership_unproven` | retained | no repository PDF acquisition attempted |
| `same_report_tri_route_comparison_unproven` | retained | no route produced comparable evidence |
| `not_raw_xml_download_proof` | retained | HTML render route was not probed and prior HTML evidence is not raw XML proof |
| `not_field_correctness_proof` | retained | no field/value correctness comparison performed |
| `not_taxonomy_compatibility_proof` | retained | no taxonomy proof performed |
| `not_source_truth` | retained | no candidate route promoted to source truth |
| `not_readiness_proof` | retained | readiness remains `NOT_READY` |

## 14. Next Gate Recommendation

Recommended next gate:

```text
Docling Runtime Local Artifact / No-model-download Containment Proof Gate
```

Minimum objective:

- Identify the exact Docling standard PDF stages required for text-native annual-report conversion.
- Prove accepted local artifacts for layout/table stages, or configure/justify a no-model path that disables or bypasses those stages.
- Pin accelerator/device and artifact path behavior where needed.
- Run conversion only in a subprocess with conversion-phase socket blocking.
- Treat any success dependent on residual RapidOCR files as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`.

Do not proceed to EID HTML render discovery, repository PDF acquisition, pdfplumber comparison, Docling conversion, source design, parser adapter implementation, production integration, readiness/release, PR or fallback expansion until containment is accepted.

## 15. Final Verdict

```text
VERDICT: DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY
```

Rationale:

- Docling `2.93.0` is installed and `PdfPipelineOptions(do_ocr=False)` is configurable.
- However, no-OCR configuration still leaves visible model-backed layout/table stages without accepted local artifact proof.
- `layout_options.model_spec.repo_id=docling-project/docling-layout-heron`, `model_path=''`, and `artifacts_path=None` prevent a no-download proof.
- Default table structure remains enabled with `TableFormerMode.ACCURATE`, and no local-only proof was established.
- RapidOCR model files exist from the prior boundary incident and are explicitly classified as residual, not promoted setup.
- Therefore conversion was not allowed, and same-report setup/comparison did not proceed.

Completion status:

```text
Self-check: pass
artifact_path=docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md
verdict=DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY
git_diff_check=passed
release_readiness=NOT_READY
```
