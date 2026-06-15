# Docling Candidate Runtime Containment And Same-report Benchmark Setup Plan Review (DS) — 2026-06-14

Status: REVIEW_COMPLETE
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate`
Reviewer: AgentDS (plan review worker)
Plan under review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`

## Verdict

**PASS_WITH_FINDINGS**

The plan correctly selects `004393 / 安信企业价值优选混合A` as the primary ordinary non-REIT sample, keeps local PDFs as user-owned candidates, requires Docling runtime containment before any convert, preserves FundDocumentRepository ownership, maintains `eid_xbrl_html_render_candidate` terminology, and explicitly excludes field correctness, taxonomy, source truth, parser replacement, and readiness claims. Three addressable findings and one informational observation are recorded below; none block plan acceptance.

## Findings Table

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F1 | MEDIUM | `do_ocr=False` sufficiency unverified — the plan assumes `PdfPipelineOptions.do_ocr=False` gates all model downloads, but Docling non-OCR pipeline stages (layout analysis, table structure, reading order) may independently trigger model downloads from external sources | Plan §7 Stage C1: "sets `PdfPipelineOptions.do_ocr=False` for text-native annual reports; avoids OCR path by default." Prior evidence artifact §11 records that `DocumentConverter().convert(...)` initiated RapidOCR model downloads — it does not prove the downloads were OCR-path–specific versus triggered by a different pipeline stage. Plan §5 confirms `PdfPipelineOptions.do_ocr` default is `True` but does not inspect other `PdfPipelineOptions` flags (e.g. `accelerator_device`, `table_structure_options.do_table_structure`, layout model paths) that could also cause network access | Add an explicit C0 check: the evidence worker must inspect all `PdfPipelineOptions` fields that may trigger external network/model access (not just `do_ocr`), and must confirm through Docling source/config introspection that `do_ocr=False` plus any other required flags are sufficient to guarantee no-network/no-download conversion before advancing to C2. If this cannot be confirmed through introspection alone, stop with `DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY` |
| F2 | LOW | Containment enforcement mechanism unspecified — the plan delegates containment to a "local command wrapper" that the evidence worker must define, without specifying the enforcement mechanism | Plan §7 Stage C1: "The evidence worker must define a local command wrapper that: sets `PdfPipelineOptions.do_ocr=False`… fails closed if Docling attempts network/model download." The plan provides no mechanism for detecting or intercepting a network attempt (e.g. `--no-network` flag, `HTTP_PROXY` override, filesystem sandbox, subprocess isolation). A wrapper that only sets `do_ocr=False` in Python code cannot detect or prevent an unexpected socket call from a C extension or third-party library | Either: (a) add to §12 a requirement that the C1 wrapper must set `PdfPipelineOptions.do_ocr=False` AND apply at least one network-interception guard (e.g. `HTTP_PROXY=http://127.0.0.1:9`, `--no-network` flag if Docling exposes one, or a pre-conversion environment audit); or (b) accept that C0 introspection must prove network impossibility before C1 proceeds, making the C1 wrapper a belt-and-suspenders confirmation rather than the primary containment layer |
| F3 | LOW | Residual RapidOCR model files from prior boundary incident are noted but not dispositioned for the containment check | Plan §5: "RapidOCR model files now exist in `.venv/lib/python3.11/site-packages/rapidocr/models` — observed residue from prior boundary incident; not promoted as accepted setup." If these residual files exist and Docling discovers them at runtime, the conversion could succeed without network access, producing a false-negative containment check (the models are present, so no download is triggered, but the models were never accepted as contained setup) | Add to §7 Stage C0 or C1: the evidence worker must record whether residual RapidOCR model files are present in the environment, and must classify any conversion that uses these residual files as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` rather than as contained evidence. Do not use residual model presence as proof that Docling is self-contained |
| F4 | INFO | No explicit guard against the evidence worker inventing schema or creating code artifacts — the plan's allowed commands (§12) and stop conditions (§13) are comprehensive for what is *forbidden*, but do not explicitly state that the evidence worker must not create new types, classes, modules, or schema definitions | Plan §3 non-goals includes "Do not implement parser code" and "Do not add a Docling adapter," and §12 lists forbidden operations, but neither section explicitly forbids creating comparison schema types, inline class definitions, or evidence-format inventions. The AGENTS.md boundary rules and the plan's own "planning-only" classification provide implicit protection | In controller judgment or plan amendment, consider adding to §3 non-goals or §12 forbidden: "Do not invent new types, classes, modules, comparison schema, evidence format, or code artifacts; the evidence artifact is a Markdown document only." This makes the constraint explicit for the evidence worker without changing the plan architecture |

## Residuals

- **`do_ocr_sufficiency_unverified`**: F1. If Docling's table structure or layout stages also require model downloads, the plan's current C1 wrapper (which only sets `do_ocr=False`) would not prevent them. The controller should decide whether to require full pipeline-option introspection in C0, or to accept `do_ocr=False` as the first containment layer and let the evidence gate discover additional requirements.
- **`containment_enforcement_gap`**: F2. The plan assumes a Python-level option flag is sufficient to prevent network access from a library that includes compiled extensions (ONNX Runtime, RapidOCR). The controller should decide the acceptable containment standard: pure Python flag, environment-level network guard, or a combination.
- **`rapidocr_residual_models`**: F3. The residual models are a pre-existing environment state. If the controller accepts C0/C1 containment as sufficient even with residual models present, the evidence artifact must clearly record this as a containment caveat.
- **`no_explicit_schema_guard`**: F4. Informational only. The plan's framing as a "handoff-ready evidence plan" and its explicit non-goals provide reasonable protection. The controller may optionally add an explicit guard.

## What the Plan Gets Right

1. **Sample selection**: `004393 / 安信企业价值优选混合A` correctly identified as primary ordinary non-REIT sample (A1), with `004393 / 2024–2022` as fallback years only if 2025 identity is blocked (§6). The plan requires `identity_match_status=identity_match_ordinary_non_reit_annual` before issuing any route-strength verdict, preventing the REIT-only limitation of the prior evidence gate.

2. **Local PDF ownership**: `基金年报/` PDFs are explicitly classified as "user-owned data artifact candidates" (§4), forbidden from body-read in planning (§3 non-goals), and gated behind explicit later authorization (§8 route 3). They are never treated as source truth.

3. **Docling containment ordering**: Stage C0 (introspection only, no convert) → Stage C1 (containment plan) → Stage C2 (bounded convert only after C0/C1 pass). This is the correct ordering. The `DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY` stop verdict is correctly specified.

4. **FundDocumentRepository boundary**: Section 8 correctly routes all PDF access through repository ownership: (1) FDR/FundDocumentRepository EID path, (2) existing cache with EID metadata, (3) local files only with explicit authorization. Direct PDF path parsing is explicitly forbidden.

5. **Terminology consistency**: `eid_xbrl_html_render_candidate` is used throughout; "raw XBRL," "raw XML," and "XBRL instance" claims are explicitly forbidden (§3, §9, §13).

6. **Scope discipline**: The plan explicitly excludes field correctness, taxonomy, source truth, parser replacement, fallback invocation, repository behavior changes, readiness, release, and PR (§3). Comparison is scoped to "representation quality, not value correctness" (§10).

7. **Stop conditions**: Section 13 covers the critical failure modes: model download, `do_ocr=False` unavailability, identity mismatch, local-filename-only identity, auth/captcha requirements, domain redirects, fallback source requirements, and production behavior changes.

8. **Allowed commands**: Section 12 correctly gates the evidence gate into two tiers (allowed without conversion, allowed only after containment confirmation), and explicitly forbids dependency installation, model download, and arbitrary network.

## Recommendation

Accept the plan with F1–F3 addressed via controller amendments or deferred to the evidence gate's C0/C1 stages. F4 is informational and optional.

The plan's architecture — sample selection, containment ordering, repository boundary, terminology, and scope discipline — is sound. The three actionable findings are all addressable within the plan's existing C0/C1 framework without restructuring. None rises to FAIL.
