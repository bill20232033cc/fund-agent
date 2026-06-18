# Docling Runtime Local Artifact / No-model-download Containment Proof Evidence - 2026-06-14

Status: `EVIDENCE_STOPPED_NOT_READY`
Gate: `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`
Role: role-scoped evidence worker; not controller; no full workflow started
Final verdict: `VERDICT: CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY`

## Scope

This artifact tests only whether the installed local Docling runtime has either:

1. accepted local artifacts for the model-backed layout/table stages; or
2. a no-model configuration/bypass for those stages sufficient to permit a later socket-blocked Docling conversion gate.

No conversion was executed because containment was not proven. This gate did not run EID HTTP, repository/FDR PDF acquisition, PDF body reads, pdfplumber, Docling conversion, provider/LLM, analyze/checklist, readiness/release/PR/push/merge commands, dependency install, code changes, cache cleanup, or production parser integration.

Release/readiness remains `NOT_READY`. This artifact does not claim source truth, raw XML availability, field correctness, taxonomy compatibility, parser replacement, `FundDocumentRepository` behavior change, or readiness.

## Commands

Executed commands:

```text
git branch --show-current
git status --short
sed -n '1,260p' AGENTS.md
sed -n '1,260p' docs/design.md
rg -n "Docling|docling|runtime containment|model|parser replacement|raw XML|taxonomy|readiness|NOT_READY" docs/design.md
sed -n '650,682p' docs/design.md
sed -n '1,260p' docs/current-startup-packet.md
sed -n '1,280p' docs/implementation-control.md
sed -n '1,260p' docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md
sed -n '1,320p' docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md
sed -n '320,520p' docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md
find .venv/lib/python3.11/site-packages -maxdepth 3 -type d -name 'docling*' -print
rg -n "artifacts_path|model_path|repo_id|download|snapshot_download|from_pretrained|LayoutModel|TableFormer|StandardPdfPipeline|PdfPipelineOptions|do_table_structure|do_ocr" .venv/lib/python3.11/site-packages/docling .venv/lib/python3.11/site-packages/docling_ibm_models
find .venv/lib/python3.11/site-packages -maxdepth 5 -type f \( -name '*.onnx' -o -name '*.safetensors' -o -name '*.pt' -o -name '*.pth' -o -name '*.bin' -o -name 'model.*' -o -name '*.json' \) -print
find .venv/lib/python3.11/site-packages/docling .venv/lib/python3.11/site-packages/docling_ibm_models -maxdepth 4 -type f -print
rg -n "artifacts_path|model_path|repo_id|download|snapshot_download|from_pretrained|local_files_only" .venv/lib/python3.11/site-packages/docling .venv/lib/python3.11/site-packages/docling_ibm_models
rg -n "do_table_structure|TableFormer|TableStructure|do_ocr|LayoutModel|ReadingOrder|PagePreprocessing|PageAssemble" .venv/lib/python3.11/site-packages/docling/pipeline .venv/lib/python3.11/site-packages/docling/models .venv/lib/python3.11/site-packages/docling/datamodel .venv/lib/python3.11/site-packages/docling_ibm_models
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/pipeline/standard_pdf_pipeline.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/datamodel/pipeline_options.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/datamodel/stage_model_specs.py
sed -n '260,620p' .venv/lib/python3.11/site-packages/docling/datamodel/pipeline_options.py
sed -n '260,620p' .venv/lib/python3.11/site-packages/docling/pipeline/standard_pdf_pipeline.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/factories/layout_factory.py
sed -n '1,280p' .venv/lib/python3.11/site-packages/docling/models/factories/table_factory.py
sed -n '620,1040p' .venv/lib/python3.11/site-packages/docling/datamodel/pipeline_options.py
sed -n '1,300p' .venv/lib/python3.11/site-packages/docling/models/factories/base_factory.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/plugins/defaults.py
sed -n '1040,1380p' .venv/lib/python3.11/site-packages/docling/datamodel/pipeline_options.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/stages/layout/layout_model.py
sed -n '1,280p' .venv/lib/python3.11/site-packages/docling/models/stages/layout/layout_object_detection_model.py
sed -n '1,320p' .venv/lib/python3.11/site-packages/docling/models/stages/table_structure/table_structure_model.py
sed -n '1380,1680p' .venv/lib/python3.11/site-packages/docling/datamodel/pipeline_options.py
sed -n '620,980p' .venv/lib/python3.11/site-packages/docling/pipeline/standard_pdf_pipeline.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/base_table_model.py
sed -n '1,220p' .venv/lib/python3.11/site-packages/docling/models/base_layout_model.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/utils/hf_model_download.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/datamodel/layout_model_specs.py
sed -n '1,240p' .venv/lib/python3.11/site-packages/docling/models/inference_engines/object_detection/factory.py
rg -n "force_backend_text|do_table_structure|do_ocr|layout_options|artifacts_path|download_models|snapshot_download|enabled" .venv/lib/python3.11/site-packages/docling/pipeline .venv/lib/python3.11/site-packages/docling/models .venv/lib/python3.11/site-packages/docling/datamodel
sed -n '1,320p' .venv/lib/python3.11/site-packages/docling/models/stages/page_assemble/page_assemble_model.py
sed -n '1,260p' .venv/lib/python3.11/site-packages/docling/models/stages/reading_order/readingorder_model.py
uv run python -c "<local Docling package/options introspection only>"
find .venv/lib/python3.11/site-packages/docling .venv/lib/python3.11/site-packages/docling_ibm_models -maxdepth 10 -type f \( -name '*.onnx' -o -name '*.safetensors' -o -name '*.pt' -o -name '*.pth' -o -name '*.bin' -o -name '*.ckpt' -o -name '*.json' \) -print
find .venv/lib/python3.11/site-packages/docling .venv/lib/python3.11/site-packages/docling_ibm_models -maxdepth 10 -type d \( -name '*docling-layout*' -o -name '*docling-models*' -o -name '*tableformer*' -o -name '*layout*' -o -name '*model_artifacts*' \) -print
find .venv/lib/python3.11/site-packages/rapidocr/models -maxdepth 1 -type f -print
rg -n "docling|Docling|rapidocr|huggingface|model" pyproject.toml uv.lock AGENTS.md docs/current-startup-packet.md docs/implementation-control.md docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md
sed -n '1,220p' .venv/lib/python3.11/site-packages/docling/models/stages/table_structure/table_structure_model_v2.py
sed -n '1,220p' .venv/lib/python3.11/site-packages/docling/models/stages/table_structure/table_structure_model_granite_vision.py
```

Commands intentionally not executed:

```text
Docling conversion
socket-blocked conversion subprocess
EID HTTP
FundDocumentRepository/FDR PDF acquisition
PDF body read
pdfplumber parser run
provider/LLM/analyze/checklist/readiness/release/PR/push/merge commands
dependency install
cache cleanup/delete/move/archive
```

Preflight:

```text
branch=feat/mvp-llm-incomplete-run-artifacts
existing_dirty_state=AGENTS.md, README.md, docs/current-startup-packet.md, docs/design.md, docs/implementation-control.md modified; many pre-existing untracked artifacts
scope_handling=this gate writes only docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md and ignores unrelated dirty/untracked state
```

## Inputs

Read in the requested order:

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/current-startup-packet.md`
4. `docs/implementation-control.md`
5. `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md`
6. `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md`

Control facts accepted for this evidence gate:

| Input | Relevant accepted/control fact |
|---|---|
| `AGENTS.md` | Production annual-report access must remain behind `FundDocumentRepository`; parser internals cannot be directly exposed to Service/UI/Host/renderer/quality gate. |
| `docs/design.md` | Docling is only a future parallel parser benchmark / next-generation document representation candidate; Docling output is not fact truth and cannot replace self-owned extractor/EvidenceAnchor/fail-closed flow. |
| `docs/current-startup-packet.md` | Current active gate is `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`; containment must be proven before conversion. |
| `docs/implementation-control.md` | Current mainline permits only proof or fail-closed on accepted local artifacts or no-model bypass for layout/table stages before any conversion; release/readiness remains `NOT_READY`. |
| Setup evidence controller judgment | Docling `2.93.0` installed/importable, `do_ocr=False` configurable, but visible layout/table model-backed paths were the accepted blocker. |
| Setup evidence | Previous gate stopped before conversion because layout had `docling-project/docling-layout-heron`, empty `model_path`, `artifacts_path=None`; table structure defaulted to `TableFormerMode.ACCURATE`; RapidOCR files were residual only. |

## Local Package/Artifact Inventory

Installed package directories observed:

```text
.venv/lib/python3.11/site-packages/docling
.venv/lib/python3.11/site-packages/docling-2.93.0.dist-info
.venv/lib/python3.11/site-packages/docling_slim-2.93.0.dist-info
.venv/lib/python3.11/site-packages/docling_core
.venv/lib/python3.11/site-packages/docling_core-2.75.0.dist-info
.venv/lib/python3.11/site-packages/docling_parse
.venv/lib/python3.11/site-packages/docling_parse-5.11.0.dist-info
.venv/lib/python3.11/site-packages/docling_ibm_models
.venv/lib/python3.11/site-packages/docling_ibm_models-3.13.2.dist-info
```

Local introspection output:

```text
docling_version=2.93.0
docling_slim_version=2.93.0
docling_ibm_models_version=3.13.2
artifacts_path=None
do_ocr=False
do_table_structure=False
force_backend_text=True
layout_options_type=LayoutOptions
layout_kind=docling_layout_default
layout_model_name=docling_layout_heron
layout_repo_id=docling-project/docling-layout-heron
layout_revision=main
layout_model_path=''
table_options_type=TableStructureOptions
table_kind=docling_tableformer
table_mode=TableFormerMode.ACCURATE
enable_remote_services=False
allow_external_plugins=False
accelerator_device=auto
rapidocr_models_exists=True
```

Artifact file inventory:

| Inventory check | Result | Containment implication |
|---|---|---|
| `.venv/lib/python3.11/site-packages/docling` / `docling_ibm_models` files matching `*.onnx`, `*.safetensors`, `*.pt`, `*.pth`, `*.bin`, `*.ckpt`, `*.json` at maxdepth 10 | no output | No bundled Docling layout/table weight/config artifact was observed in these installed package directories. |
| Docling/docling_ibm_models directories matching layout/table names | source-code directories only: `docling/models/stages/layout`, `docling_ibm_models/tableformer_v2`, `docling_ibm_models/tableformer`, `docling_ibm_models/layoutmodel` | These are package code directories, not accepted model artifact roots. |
| `.venv/lib/python3.11/site-packages/rapidocr/models` | residual OCR `.onnx`, `.pth`, and dictionary files exist | Classified only as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`; not layout/table containment proof. |

No accepted `artifacts_path` was configured or proven. No Docling layout/table local artifact root was accepted in this gate.

## Model-backed Stage Analysis

Observed standard PDF stages from `docling/pipeline/standard_pdf_pipeline.py`:

```text
preprocess -> ocr -> layout -> table -> assemble -> reading_order
```

Key source-level facts:

| Stage | Source evidence | Containment implication |
|---|---|---|
| OCR | `StandardPdfPipeline._make_ocr_model(... enabled=self.pipeline_options.do_ocr ...)` | `do_ocr=False` disables OCR execution, but OCR was not the blocking stage. |
| Layout | `_init_models()` always creates `self.layout_model = layout_factory.create_instance(...)`; `BaseLayoutModel.__call__()` has no `enabled` pass-through field. | Standard PDF layout is not disabled by `do_ocr=False`, `do_table_structure=False`, or `force_backend_text=True`. |
| Table | `_init_models()` creates `self.table_model = table_factory.create_instance(... enabled=self.pipeline_options.do_table_structure ...)`; `BaseTableStructureModel.__call__()` yields pages unchanged when `enabled=False`. | `do_table_structure=False` can bypass table-structure model execution, but it does not bypass layout. |
| Assemble | `PageAssembleModel.__call__()` asserts `page.predictions.layout is not None` and builds body/table/figure/text elements from layout clusters. | Standard output assembly depends on layout predictions. |
| Reading order | `ReadingOrderModel` consumes assembled elements and builds the `DoclingDocument`. | Reading order is downstream of layout/assembly; it is not a replacement for layout. |

Layout model-backed path:

| Source evidence | Observed behavior |
|---|---|
| `PipelineOptions.artifacts_path` field description | If `None`, models are fetched from remote sources on first use; offline operation requires pre-downloaded artifacts. |
| `LayoutModel.__init__()` | If `artifacts_path is None`, it sets `artifacts_path = self.download_models(layout_model_config=layout_model_config) / model_path`. |
| `LayoutModel.download_models()` | Calls `download_hf_model(repo_id=layout_model_config.repo_id, revision=layout_model_config.revision, ...)`. |
| `download_hf_model()` | Calls `huggingface_hub.snapshot_download(...)`. |
| `LayoutModelConfig` defaults | `DOCLING_LAYOUT_HERON` has `repo_id="docling-project/docling-layout-heron"`, `revision="main"`, `model_path=""`. |

Table model-backed paths:

| Table option/model | Source evidence | Containment implication |
|---|---|---|
| `TableStructureModel` / TableFormer v1 | If enabled and `artifacts_path is None`, calls `download_models()` for `docling-project/docling-models`, revision `v2.3.0`, then uses `model_artifacts/tableformer/{accurate|fast}`. | Default table mode remains model-backed unless `do_table_structure=False` is used. No accepted local artifact was proven. |
| `TableStructureModelV2` | If enabled and `artifacts_path is None`, calls `download_models()` for `docling-project/TableFormerV2`, then `from_pretrained(model_path)` and tokenizer load. | Alternative table option is also model-backed. |
| `GraniteVisionTableStructureModel` | If enabled and artifact folder is missing, logs that artifacts will be downloaded, and `download_models()` uses `ibm-granite/granite-vision-4.1-4b`. | Alternative table option is VLM/model-backed and not a no-model bypass. |

Guardrail assessment:

| Guardrail | Observed value | Disposition |
|---|---:|---|
| `enable_remote_services` | `False` | Prevents remote service/API model calls in configured branches; does not disable HuggingFace artifact lookup/download for local model stages. |
| `allow_external_plugins` | `False` | Prevents non-Docling plugin loading; does not prove local model artifacts or no-download behavior. |
| `accelerator_options.device` | `auto` | Not pinned. It is not itself a network path, but it is not containment proof. |
| `artifacts_path` | `None` | Blocking for accepted local artifact proof. |

## No-model Bypass Analysis

Tested/configured no-model surface by local introspection:

```text
PdfPipelineOptions(do_ocr=False, do_table_structure=False, force_backend_text=True)
```

Result:

| Option | Effect | No-model proof status |
|---|---|---|
| `do_ocr=False` | Disables OCR model execution. | Accepted as OCR bypass only; not sufficient because layout remains model-backed. |
| `do_table_structure=False` | `BaseTableStructureModel.__call__()` yields pages unchanged when disabled. | Accepted as table-structure execution bypass for the configured standard PDF path; not sufficient because layout remains model-backed and required by assembly. |
| `force_backend_text=True` | Documented as using PDF backend native text instead of layout model text detection. | Not accepted as layout bypass: standard pipeline still initializes and executes layout, and `PageAssembleModel` requires `page.predictions.layout`. |
| `layout_options.skip_cell_assignment` / `keep_empty_clusters` / `create_orphan_clusters` | Tuning fields on layout output behavior. | Not layout disable switches. |

No `do_layout=False`, `enabled=False`, local-only layout backend, or source-observed rules-only layout replacement was found in the standard PDF pipeline path inspected in this gate.

Therefore a no-model Docling standard PDF conversion path was not proven. At best, table-structure execution can be disabled, but layout remains model-backed and unresolved.

## Socket-blocked Conversion Eligibility Decision

Decision:

```text
socket_blocked_conversion_eligible=false
```

Rationale:

- The current gate required accepted local artifacts or a no-model bypass before any conversion.
- No accepted Docling layout artifact root was configured or proven.
- Source code shows `artifacts_path=None` leads layout model initialization to `download_hf_model()` and then `huggingface_hub.snapshot_download()`.
- The standard PDF pipeline has no observed layout-disable switch, and output assembly requires layout predictions.
- Table structure can be disabled, but that only removes the table model blocker; it does not remove the layout blocker.
- A socket-blocked conversion subprocess would test runtime network denial, but it cannot substitute for the missing accepted local artifact/no-model proof required before conversion.

No Docling conversion was executed.

## Blocked/Accepted Proofs

| Proof | Status | Evidence |
|---|---|---|
| Docling installed/importable | Accepted local package fact | `docling_version=2.93.0`; `docling_slim_version=2.93.0`; `docling_ibm_models_version=3.13.2`. |
| OCR no-model bypass | Accepted only for OCR stage | `do_ocr=False` configurable and observed. |
| Table-structure bypass | Accepted only for table-structure execution in configured standard PDF path | `do_table_structure=False` and `BaseTableStructureModel.__call__()` pass-through when disabled. |
| Layout no-model bypass | Blocked | No `do_layout`/layout disable switch observed; layout model is always created in `StandardPdfPipeline._init_models()`; `BaseLayoutModel` lacks enabled pass-through. |
| Accepted local layout artifact | Blocked | `artifacts_path=None`; `layout_repo_id=docling-project/docling-layout-heron`; no bundled layout weights/config artifact observed under `.venv` Docling package dirs. |
| Accepted local table artifact | Not needed if table disabled; otherwise blocked | Default TableFormer path downloads `docling-project/docling-models` when enabled and no local artifact path is supplied. |
| No-download containment for standard PDF conversion | Blocked | Layout path remains model-backed with `snapshot_download()` path when artifacts are missing/unspecified. |
| Socket-blocked conversion gate eligibility | Blocked | Conversion would violate current gate stop condition because containment is not proven. |
| RapidOCR residual as accepted containment artifact | Rejected | Residual files remain `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`. |

## Residuals

| Residual | Status | Next handling |
|---|---|---|
| `docling_layout_local_artifact_unproven` | blocking | A later gate would need an explicit accepted `artifacts_path` containing the required layout repo folder/files, with provenance and no-download behavior proven before conversion. |
| `docling_layout_no_model_bypass_unproven` | blocking | A later gate would need a source-supported standard PDF path that does not instantiate/execute model-backed layout, or a separately accepted non-standard path. |
| `docling_table_artifact_unproven_if_enabled` | retained | If `do_table_structure=True`, table artifacts must be accepted or the table model path remains blocked. |
| `docling_table_bypass_only_partial` | retained | `do_table_structure=False` bypasses table structure but reduces table reconstruction and does not solve layout containment. |
| `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` | retained | RapidOCR files exist but are not accepted as Docling layout/table artifacts. |
| `socket_blocked_conversion_not_authorized` | blocking | Do not run conversion until local artifact/no-model containment is accepted. |
| `same_report_comparison_not_reopened` | retained | No EID HTML discovery, FDR PDF ownership proof, pdfplumber run, or Docling conversion was attempted. |
| `not_raw_xml_download_proof` | retained | This gate did not probe raw XML and does not alter prior HTML render candidate classification. |
| `not_field_correctness_proof` | retained | No field/value correctness comparison performed. |
| `not_taxonomy_compatibility_proof` | retained | No taxonomy/schemaRef/contextRef/unitRef proof performed. |
| `not_source_truth` | retained | No candidate route promoted to source truth. |
| `not_readiness_proof` | retained | Release/readiness remains `NOT_READY`. |

## Final Verdict

```text
VERDICT: CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY
```

Rationale:

- The installed Docling runtime is present, but the standard PDF path still requires a model-backed layout stage.
- `do_ocr=False` and `do_table_structure=False` can bypass OCR and table-structure execution, but they do not bypass layout.
- The inspected standard PDF layout path has remote HuggingFace repo metadata and calls `snapshot_download()` when `artifacts_path=None`.
- No accepted local layout/table artifact root was configured or proven in repo or `.venv` package evidence.
- Therefore a later socket-blocked conversion gate is not eligible from this artifact.

Completion status:

```text
artifact_path=docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md
verdict=CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY
release_readiness=NOT_READY
```
