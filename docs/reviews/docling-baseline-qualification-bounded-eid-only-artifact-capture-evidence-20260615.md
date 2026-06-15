# Docling Baseline Qualification Bounded EID-only Artifact Capture Evidence - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records staged EID-only PDF capture evidence for required Docling baseline qualification samples S4/S5/S6.

This gate captured PDFs only into:

```text
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/
```

This gate did not write to `cache/pdf/`, did not overwrite the existing S4 cache file, did not run `FundDocumentRepository`, did not run Docling conversion, did not run pdfplumber export, did not run production analyzer/checklist, did not run provider/LLM/golden/readiness/release/PR/push/merge commands, and did not change source policy or production behavior.

Direct official EID HTTP access in this artifact is an evidence-only staging exception accepted by `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-controller-judgment-20260615.md`. It does not change the production rule that annual-report access goes through `FundDocumentRepository`.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-controller-judgment-20260615.md`

## 3. Preflight

```text
git branch --show-current
feat/mvp-llm-incomplete-run-artifacts

git status --short
 M AGENTS.md
?? .mimocode/
?? docs/audit/
?? docs/code-wiki-and-audit-report-20260613.md
?? docs/dayu-agent-architect-gap-analysis-20260613.md
?? docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
?? docs/dayu-fund-agent-mvp-gap-discussion-summary-20260613.md
?? docs/learning-roadmap.md
?? docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
?? docs/next-development-phaseflow.md
?? docs/reviews/annual-report-docling-parser-discussion-summary-20260613.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-controller-judgment-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-ds-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-mimo-20260614.md
?? docs/reviews/audit-disposition-phaseflow-reconciliation-controller-judgment-20260610.md
?? docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md
?? docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-controller-judgment-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-ds-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-mimo-20260614.md
?? docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md
?? docs/reviews/mvp-post-eid-artifact-disposition-controller-judgment-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-inventory-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-review-ds-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-startup-judgment-20260609.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-controller-judgment-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-ds-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-mimo-20260606.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-evidence-20260608.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-mimo-review-20260608.md
?? docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260609.md
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/plan-review-20260609-071706.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-ds-20260614.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-mimo-20260614.md
?? docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/reviews/repo-review-20260609-130307.md
?? docs/reviews/repo-review-20260609-165959.md
?? docs/reviews/repo-review-20260611-231358.md
?? docs/reviews/workspace-ownership-reconciliation-20260531.md
?? docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md
?? docs/tmux-agent-memory-store.md
?? reports/docling-route-a/
?? reports/live-evidence/
?? reports/manual-llm-smoke/
?? reports/representation-json/
?? reviews/
?? scripts/claude_mimo_simple.py
?? scripts/review-artifact.sh
?? 基金年报/
?? 定性分析模板.md
```

Existing staging directory check before capture:

```text
find cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf -maxdepth 1 -type f -print
find: cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf: No such file or directory
```

Existing S4 production-shaped cache file before/after capture:

```text
cache/pdf/006597_2024_annual_report_eid.pdf|size=792928|mtime=May 29 05:51:59 2026
```

This confirms the existing S4 `cache/pdf` file was not overwritten by this gate.

## 4. Accepted Metadata Inputs

| Sample | Fund/year | Upload id | Fund short name | Metadata classification |
|---|---|---:|---|---|
| S4 | `006597 / 2024` | `1253099` | `国泰利享中短债债券` | `eid_metadata_matched_no_download` |
| S5 | `017641 / 2024` | `1256369` | `摩根标普500指数发起式(QDII)` | `eid_metadata_matched_no_download` |
| S6 | `110020 / 2024` | `1249587` | `易方达沪深300ETF联接` | `eid_metadata_matched_no_download` |

## 5. Capture Directory And Non-overwrite Policy

Staging directory:

```text
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/
```

Capture implementation:

- used Node `fetch` as an equivalent official HTTP client;
- used `redirect=follow`;
- used `timeout_ms=120000` per attempt;
- allowed max two attempts per URL;
- wrote to `.incomplete` temporary files in the same staging directory;
- renamed `.incomplete` to final staged path only after status/content-type/PDF magic/SHA-256 checks passed;
- left no `.incomplete` files after successful capture.

No headers, raw response dumps or debug payloads were written outside the evidence artifact and staging directory.

## 6. Request / Response Matrix

| Sample | Requested URL | Final URL | Host | Attempts | HTTP | Content-Type | Content-Length | Classification |
|---|---|---|---|---:|---:|---|---|---|
| S4 | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1253099` | same | `eid.csrc.gov.cn` | 1 | 200 | `application/pdf` | null | `eid_artifact_captured_staged` |
| S5 | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1256369` | same | `eid.csrc.gov.cn` | 1 | 200 | `application/pdf` | null | `eid_artifact_captured_staged` |
| S6 | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1249587` | same | `eid.csrc.gov.cn` | 1 | 200 | `application/pdf` | null | `eid_artifact_captured_staged` |

## 7. File Integrity Matrix

| Sample | Staging path | Byte size | PDF magic | SHA-256 |
|---|---|---:|---|---|
| S4 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf` | 792928 | `%PDF-` | `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` |
| S5 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf` | 2970819 | `%PDF-` | `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` |
| S6 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf` | 2639303 | `%PDF-` | `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` |

Independent file checks:

```text
stat -f '%N|size=%z|mtime=%Sm' cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf

cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf|size=792928|mtime=Jun 15 16:18:03 2026
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf|size=2970819|mtime=Jun 15 16:18:04 2026
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf|size=2639303|mtime=Jun 15 16:18:06 2026
```

```text
shasum -a 256 cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf

85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982  cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf
33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c  cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf
307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790  cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf
```

```text
head -c 5 <each staged PDF>
%PDF-
%PDF-
%PDF-
```

Incomplete-file check:

```text
find cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf -maxdepth 1 -name '*.incomplete' -print
<no output>
```

## 8. Staging Artifact Manifest

| Sample | Artifact path | Intended downstream status |
|---|---|---|
| S4 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf` | staged EID-controlled PDF; not promoted to `cache/pdf` |
| S5 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf` | staged EID-controlled PDF; not promoted to `cache/pdf` |
| S6 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf` | staged EID-controlled PDF; not promoted to `cache/pdf` |

## 9. Blocked Proofs And Residuals

The following remain explicitly not proven:

- `not_field_correctness_proof`: no table or narrative values were compared.
- `not_docling_baseline_proof`: no Docling conversion or representation quality evidence was run.
- `not_pdfplumber_export_proof`: no pdfplumber export or parser command was run.
- `not_source_truth`: staged PDF bytes plus EID metadata do not prove fund facts.
- `not_production_cache_promotion`: staged PDFs were not copied or promoted to `cache/pdf`.
- `not_repository_behavior_change`: `FundDocumentRepository` was not executed or changed.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_fallback`: no CNINFO, fund-company, Eastmoney, akshare or local non-EID fallback was used.

Residuals:

| Residual | Status | Next handling |
|---|---|---|
| Staged PDFs are not production-shaped cache entries. | open | Route to `EID Staged PDF Cache Promotion Planning Gate` only if production-shaped cache is needed. |
| Representation export has not been run on staged PDFs. | open | Route to `Full Representation Export Planning Gate` after controller decides staged path vs promotion path. |
| S3 hash gap remains. | accepted residual | Carry to later export planning or artifact-capture expansion if needed. |
| Control docs lag behind latest accepted gate chain. | open | Scoped control sync after evidence closeout. |

## 10. Validation

```text
git diff --check
passed
```

## 11. Final Classification

Per-sample:

- S4 `006597 / 2024`: `eid_artifact_captured_staged`
- S5 `017641 / 2024`: `eid_artifact_captured_staged`
- S6 `110020 / 2024`: `eid_artifact_captured_staged`

Whole gate:

`ALL_REQUIRED_EID_ARTIFACTS_CAPTURED_STAGED_NOT_READY`
