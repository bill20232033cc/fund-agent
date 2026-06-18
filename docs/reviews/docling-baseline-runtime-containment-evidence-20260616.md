# Docling Baseline Runtime Containment Evidence - 2026-06-16

Gate: `Docling Baseline Runtime Containment Evidence Gate`
Role: evidence worker fallback
Release/readiness: `NOT_READY`

## 1. Scope

This evidence gate evaluates whether the accepted Docling candidate route has enough runtime/cache/cost containment evidence to proceed in the baseline qualification flow.

This gate is evidence-only. It does not run Docling conversion, EID/FDR/source acquisition, PDF download, pdfplumber export, provider/LLM routes, `analyze`, `checklist`, golden, readiness, release, PR, push or merge commands. It does not modify source, tests, runtime behavior, `FundDocumentRepository`, parser behavior, source policy, `EvidenceAnchor`, `CHAPTER_CONTRACT`, Service, Host, UI, renderer or quality gate.

Initial subagent spawn was not available and returned `agent thread limit reached`, so the first evidence artifact was produced by controller fallback. After user correction, real tmux handoffs were sent to AgentDS and AgentMiMo; their reviews are recorded in separate review artifacts. No ProCodex review is claimed for this artifact.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and NOT_READY guardrails |
| `docs/implementation-control.md` | Control truth and current gate scope |
| `docs/design.md` Docling candidate sections | Candidate-layer design boundary |
| `docs/reviews/docling-baseline-qualification-plan-20260615.md` | Accepted baseline qualification plan |
| `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md` | Accepted Gate A runtime containment thresholds |
| `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md` | Prior blocked runtime setup evidence |
| `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-controller-judgment-20260614.md` | Prior no-download blocker judgment |
| `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` | Route A local artifact conversion evidence |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md` | Accepted multi-sample selected-fact correctness expansion |
| `reports/docling-route-a/artifact-manifest.json` | Local Docling model artifact inventory |
| `reports/docling-route-a/004393_2025_docling_summary.json` | Single-sample conversion runtime summary |
| `reports/representation-json/004393_2025_docling_full.json` | S1 Docling full representation JSON |
| `reports/representation-json/006597_2024_docling_full.json` | S4 Docling full representation JSON |
| `reports/representation-json/017641_2024_docling_full.json` | S5 Docling full representation JSON |
| `reports/representation-json/110020_2024_docling_full.json` | S6 Docling full representation JSON |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Accepted selected-fact expansion JSON |

## 3. Runtime Containment Criteria

The accepted baseline qualification plan requires Gate A to prove, for active samples:

- explicit local `artifacts_path`;
- offline/no-hidden-download posture;
- socket-blocked conversion process;
- recorded Docling/package configuration;
- output hash and parseable JSON artifact;
- no source acquisition or non-EID read during conversion;
- no production parser replacement or readiness claim.

This artifact distinguishes three evidence levels:

| Level | Meaning |
| --- | --- |
| `runtime_containment_proven` | A sample has accepted conversion runtime metadata with socket blocking, explicit local artifacts path and output hashes. |
| `representation_artifact_available_runtime_log_missing` | A sample has a Docling representation JSON but lacks accepted conversion runtime metadata. |
| `not_proven` | No accepted representation or runtime evidence exists. |

## 4. Accepted Runtime Evidence

### 4.1 Local Model Artifact Inventory

`reports/docling-route-a/artifact-manifest.json` records repo-local artifact root `cache/docling-artifacts`.

| Artifact folder | Revision | Files | Bytes |
| --- | --- | ---: | ---: |
| `docling-project--docling-layout-heron` | `8f39ad3c0b4c58e9c2d2c84a38465abf757272d8` | 6 | 171,764,371 |
| `docling-project--docling-models` | `fc0f2d45e2218ea24bce5045f58a389aed16dc23` | 8 | 358,236,323 |

Local size observations:

```text
cache/docling-artifacts: 505M
reports/docling-route-a: 5.3M
reports/representation-json: 33M
```

Disposition: accepted as repo-local artifact inventory for candidate evidence. It is not model provenance acceptance for production use.

### 4.2 S1 Runtime Summary

`reports/docling-route-a/004393_2025_docling_summary.json` records:

| Field | Value |
| --- | --- |
| status | `success` |
| elapsed_seconds | `63.483` |
| pdf_size | `832089` |
| artifacts_path | `/Users/maomao/fund-agent/cache/docling-artifacts` |
| do_ocr | `false` |
| do_table_structure | `true` |
| socket_blocked | `true` |
| page_count | `65` |
| table_count | `95` |
| markdown_chars | `152718` |

Hashes:

| File | SHA256 |
| --- | --- |
| `reports/docling-route-a/artifact-manifest.json` | `a452d29d8de9dc74fcea1566397fe647e62b15aa5c7c7a832caa0a9102912bbd` |
| `reports/docling-route-a/004393_2025_docling_summary.json` | `cb8ac76d78792afdb9ca3526cfaa5a2bcbe05dfc1d737935873e71c5588af758` |
| `reports/representation-json/004393_2025_docling_full.json` | `069282b22d7926e93743cc12a8538e43eaf262aa165376d872552a76efac0e49` |

Disposition: S1 `004393 / 2025` has accepted local runtime containment input from Route A: explicit local artifact root, socket-blocked conversion, no OCR, table structure enabled, successful output and output hashes.

## 5. Multi-sample Representation Artifact Status

The following Docling full representation JSON files are available and parseable as local candidate artifacts:

| Sample | File | Pages | Headings | Sections | Paragraphs | Tables | Cells | bbox | page no. | table locator |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| S1 `004393 / 2025` | `reports/representation-json/004393_2025_docling_full.json` | 65 | 213 | 13 | 457 | 95 | 3,493 | true | true | true |
| S4 `006597 / 2024` | `reports/representation-json/006597_2024_docling_full.json` | 70 | 229 | 229 | 737 | 96 | 2,759 | true | true | true |
| S5 `017641 / 2024` | `reports/representation-json/017641_2024_docling_full.json` | 110 | 208 | 208 | 856 | 121 | 7,060 | true | true | true |
| S6 `110020 / 2024` | `reports/representation-json/110020_2024_docling_full.json` | 84 | 222 | 222 | 840 | 124 | 5,940 | true | true | true |

Hashes:

| File | SHA256 |
| --- | --- |
| `reports/representation-json/006597_2024_docling_full.json` | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` |
| `reports/representation-json/017641_2024_docling_full.json` | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` |
| `reports/representation-json/110020_2024_docling_full.json` | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | `ddea0a101b3f084478c369f7822ef338154157ccdf584a2c10970a4a330932e0` |

Disposition: S4/S5/S6 have useful full representation JSONs and accepted selected-fact correctness expansion input, but these JSONs do not themselves prove the conversion runtime posture. They do not contain accepted socket-block/offline/model-download runtime logs equivalent to S1.

## 6. Runtime Containment Matrix

| Sample | Representation JSON | Runtime log | Socket-block proven | Explicit local artifacts path proven | Cost metric | Runtime containment disposition |
| --- | --- | --- | --- | --- | --- | --- |
| S1 `004393 / 2025` | yes | yes | yes | yes | `63.483s`, `832089` bytes PDF, `65` pages | `runtime_containment_proven_for_single_sample` |
| S4 `006597 / 2024` | yes | no accepted per-sample conversion log found | not proven | not proven | not proven | `representation_artifact_available_runtime_log_missing` |
| S5 `017641 / 2024` | yes | no accepted per-sample conversion log found | not proven | not proven | not proven | `representation_artifact_available_runtime_log_missing` |
| S6 `110020 / 2024` | yes | no accepted per-sample conversion log found | not proven | not proven | not proven | `representation_artifact_available_runtime_log_missing` |

## 7. Cost / Cache Observations

Accepted observations:

- Repo-local Docling artifacts currently occupy approximately `505M`.
- S1 conversion took `63.483s` on CPU with `do_ocr=false` and `do_table_structure=true`.
- S1 generated a `4.6M` full representation JSON plus Route A summary/Markdown/quality artifacts.
- S4/S5/S6 representation JSONs are `2.4M`, `4.8M` and `4.2M` respectively, but their conversion elapsed time and runtime containment logs are not accepted in this gate.

Disposition: the cache/cost profile is measurable but incomplete for a baseline candidate. The evidence is sufficient to plan a bounded multi-sample runtime re-evidence gate, not sufficient to pass full Gate A for the active matrix.

## 8. Blocked Claims

The following claims remain blocked:

- Docling runtime containment is proven for the full active sample matrix.
- S4/S5/S6 conversion ran with socket blocking.
- S4/S5/S6 conversion used explicit local `cache/docling-artifacts`.
- S4/S5/S6 conversion avoided hidden model download.
- S4/S5/S6 conversion cost/elapsed time is accepted.
- Docling is source truth.
- Docling field correctness is fully proven.
- Docling is production parser replacement.
- Docling is readiness/release/PR proof.
- Model artifact provenance is production-accepted.

## 9. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| Multi-sample runtime logs missing for S4/S5/S6 | blocking for Gate A pass | evidence worker / controller | Bounded no-live multi-sample runtime containment re-evidence gate |
| Model artifact production provenance not accepted | residual | controller / future design owner | Separate model artifact provenance acceptance if production use is considered |
| Initial subagent spawn unavailable | residual history | controller | Real tmux DS/MiMo reviews were later obtained; keep this as channel-history only |
| Runtime cost threshold not calibrated | residual | baseline qualification owner | Measure per-page/per-table elapsed time in bounded runtime re-evidence |

## 10. Validation

Commands run:

```text
git branch --show-current
git status --short
sed -n '1,120p' docs/current-startup-packet.md
sed -n '1,220p' docs/implementation-control.md
sed -n '1,220p' AGENTS.md
sed -n '1,220p' docs/reviews/docling-baseline-qualification-plan-20260615.md
sed -n '1,220p' docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md
sed -n '1,260p' docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md
sed -n '1,260p' docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md
sed -n '1,260p' docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-controller-judgment-20260614.md
sed -n '1,260p' docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-controller-judgment-20260616.md
find reports/docling-route-a -maxdepth 2 -type f -print
find reports/representation-json -maxdepth 2 -type f -print
jq '.' reports/docling-route-a/artifact-manifest.json
jq '.' reports/docling-route-a/004393_2025_docling_summary.json
jq '.summary_metrics, .metadata.conversion_summary? // empty' reports/representation-json/004393_2025_docling_full.json
jq '.summary_metrics, .blocked_claims, .candidate_status, .source_truth_status, .field_correctness_status, .production_parser_replacement_status' reports/representation-json/006597_2024_docling_full.json reports/representation-json/017641_2024_docling_full.json reports/representation-json/110020_2024_docling_full.json
shasum -a 256 reports/docling-route-a/artifact-manifest.json reports/docling-route-a/004393_2025_docling_summary.json reports/representation-json/004393_2025_docling_full.json reports/representation-json/006597_2024_docling_full.json reports/representation-json/017641_2024_docling_full.json reports/representation-json/110020_2024_docling_full.json reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
du -sh cache/docling-artifacts reports/docling-route-a reports/representation-json
```

No live/source acquisition, Docling conversion, provider/LLM, analyze/checklist/golden/readiness/release/PR command was run.

## 11. Evidence Verdict

```text
VERDICT: PARTIAL_RUNTIME_CONTAINMENT_EVIDENCE_BLOCKED_FOR_FULL_MATRIX_NOT_READY
```

Conclusion:

- S1 `004393 / 2025` has accepted single-sample runtime containment evidence from Route A.
- S4/S5/S6 have representation artifacts and selected-fact correctness evidence, but lack accepted per-sample runtime containment logs.
- The correct next gate is a bounded no-live multi-sample runtime containment re-evidence gate, not full-document coverage or baseline disposition.
