# Docling Multi-sample Runtime Containment Re-evidence - 2026-06-16

Gate: `Docling Multi-sample Runtime Containment Re-evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This evidence gate executed the accepted bounded no-live plan for S4/S5/S6 Docling runtime/cache/cost containment.

The gate did not run live/network/EID/FDR/PDF/source acquisition, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, and did not modify source, tests, runtime behavior, `FundDocumentRepository`, parser behavior, source policy, `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate.

The gate explicitly states these non-proof boundaries:

- `not_source_truth`
- `not_full_field_correctness`
- `not_production_parser_replacement`
- `not_readiness_proof`
- `no_repository_behavior_change`
- `no_service_host_ui_renderer_quality_gate_integration`

## 2. Evidence Inputs

| Input | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-controller-judgment-20260616.md` | Accepted plan controller judgment |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-20260616.md` | Accepted execution plan |
| `reports/docling-runtime-containment/20260616/manifests/*.json` | New single-sample execution manifests |
| `reports/docling-runtime-containment/20260616/outputs/*.json` | New isolated candidate Docling outputs |
| `reports/docling-runtime-containment/20260616/logs/*.txt` | New stdout/stderr/exit-code logs |
| `reports/docling-runtime-containment/20260616/runtime-summary.json` | Evidence summary |

## 3. Commands Run

Preflight and input checks:

```text
git status --short
git status --branch --short
git diff --check
shasum -a 256 cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf
du -sh cache/docling-artifacts
python -m json.tool reports/docling-runtime-containment/20260616/manifests/S4_006597_2024_docling_runtime_manifest.json
python -m json.tool reports/docling-runtime-containment/20260616/manifests/S5_017641_2024_docling_runtime_manifest.json
python -m json.tool reports/docling-runtime-containment/20260616/manifests/S6_110020_2024_docling_runtime_manifest.json
```

Per-sample conversion command shape:

```text
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /usr/bin/time -p uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <single-sample-manifest> --workspace-root . --output-root reports/docling-runtime-containment/20260616/outputs --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts --allow-overwrite > reports/docling-runtime-containment/20260616/logs/<sample>.stdout.txt 2> reports/docling-runtime-containment/20260616/logs/<sample>.stderr.txt
```

The command was run once each for:

- `reports/docling-runtime-containment/20260616/manifests/S4_006597_2024_docling_runtime_manifest.json`
- `reports/docling-runtime-containment/20260616/manifests/S5_017641_2024_docling_runtime_manifest.json`
- `reports/docling-runtime-containment/20260616/manifests/S6_110020_2024_docling_runtime_manifest.json`

Post-run validation:

```text
python -m json.tool reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json
python -m json.tool reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json
python -m json.tool reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json
jq '{fund_code, document_year, candidate_status, field_correctness_status, source_truth_status, production_parser_replacement_status, route_failures: .failure_taxonomy.route_failures, summary_metrics}' reports/docling-runtime-containment/20260616/outputs/*.json
shasum -a 256 reports/docling-runtime-containment/20260616/outputs/*.json
rg -n "docling_network_attempt_blocked|docling_model_artifact_unavailable|socket access blocked|snapshot_download|huggingface|modelscope|download" reports/docling-runtime-containment/20260616/logs reports/docling-runtime-containment/20260616/outputs
python -m json.tool reports/docling-runtime-containment/20260616/runtime-summary.json
jq -e '.overall_result == "pass_candidate_only_not_ready" and all(.samples[]; .command_exit_code == 0 and .route_failures == [] and .has_bbox == true and .has_page_number == true and .has_table_cell_locator == true and .runtime_containment_status == "pass_candidate_only_not_ready")' reports/docling-runtime-containment/20260616/runtime-summary.json
git diff --check
```

## 4. Sample Runtime Matrix

| Sample | Fund | Year | Exit | Real seconds | PDF bytes | Pages | Tables | Table cells | Output bytes | Output SHA256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| S4 | `006597` | 2024 | 0 | 45.94 | 792928 | 70 | 96 | 2759 | 2465451 | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` |
| S5 | `017641` | 2024 | 0 | 85.80 | 2970819 | 110 | 121 | 7060 | 5077159 | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` |
| S6 | `110020` | 2024 | 0 | 87.34 | 2639303 | 84 | 124 | 5940 | 4414725 | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` |

All three samples used:

- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `--docling-artifacts-path cache/docling-artifacts`
- default socket blocking from `representation_handlers.py`
- no `--docling-no-socket-block`
- isolated `--output-root reports/docling-runtime-containment/20260616/outputs`

## 5. Hash And Output Validation

| Sample | Input hash status | Output JSON status | Output route failures | Locator metrics |
| --- | --- | --- | --- | --- |
| S4 | matched `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` | parseable | `[]` | bbox/page/table-cell locator all true |
| S5 | matched `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` | parseable | `[]` | bbox/page/table-cell locator all true |
| S6 | matched `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` | parseable | `[]` | bbox/page/table-cell locator all true |

## 6. Route Failure Inspection

For all three isolated outputs:

```text
failure_taxonomy.route_failures == []
candidate_status == "not_proven"
field_correctness_status == "not_proven"
source_truth_status == "not_proven"
production_parser_replacement_status == "not_authorized"
```

The log/output scan for:

```text
docling_network_attempt_blocked
docling_model_artifact_unavailable
socket access blocked
snapshot_download
huggingface
modelscope
download
```

returned only the expected output blocked-claim string `not_raw_xml_download_proof`. It did not find a runtime network-attempt failure, missing local model artifact failure, or remote model download log.

## 7. Cost / Cache Metrics

| Metric | Result |
| --- | --- |
| Local Docling artifact directory | `cache/docling-artifacts` |
| Local artifact directory size | `505M` |
| Evidence output directory size | `11M` |
| S4 elapsed time | `45.94s` |
| S5 elapsed time | `85.80s` |
| S6 elapsed time | `87.34s` |

These are runtime/cost evidence for the bounded candidate samples only. They are not a production performance SLA or a release-readiness claim.

## 8. Blocked Claims

| Claim | Status |
| --- | --- |
| Docling output is source truth | `BLOCKED_NOT_PROVEN` |
| Docling output is full field correctness proof | `BLOCKED_NOT_PROVEN` |
| Docling replaces the production parser | `BLOCKED_NOT_AUTHORIZED` |
| Docling is a production baseline | `BLOCKED_NOT_AUTHORIZED` |
| Docling evidence proves readiness/release | `BLOCKED_NOT_READY` |
| Raw XML / XBRL instance direct download is proven | `BLOCKED_NOT_PROVEN` |
| Taxonomy/schemaRef cross-year compatibility is proven | `BLOCKED_NOT_PROVEN` |
| EvidenceAnchor mapping is accepted | `BLOCKED_NOT_PROVEN` |

## 9. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| Full-document coverage and paragraph/table completeness beyond locator metrics | open | baseline qualification owner | `Docling Full-document Coverage Evidence Gate` |
| EvidenceAnchor mapping from Docling candidate locators | open | documents/schema owner | future EvidenceAnchor mapping gate |
| Comparative quality against pdfplumber/EID HTML route after runtime containment | open | baseline qualification owner | comparative correctness / route disposition gate |
| Production model artifact provenance | open | production integration owner | separate provenance gate before dependency promotion |
| Runtime cost threshold calibration | open | baseline qualification owner | future performance/cache/cost disposition gate |

## 10. Validation

Validation results:

| Check | Result |
| --- | --- |
| Manifest JSON parse | PASS |
| Input PDF hashes | PASS |
| All conversion exit codes | PASS |
| Output JSON parse | PASS |
| Route failures empty | PASS |
| bbox/page/table-cell locator metrics | PASS |
| Candidate-only non-proof statuses | PASS |
| Log scan for network/model-download failure strings | PASS_WITH_EXPECTED_BLOCKED_CLAIM_MATCH |
| `runtime-summary.json` parse and assertion | PASS |
| `git diff --check` | PASS |

## 11. Verdict

```text
VERDICT: ACCEPT_MULTI_SAMPLE_RUNTIME_CONTAINMENT_READY_FOR_FULL_DOCUMENT_COVERAGE_GATE_NOT_READY
```
