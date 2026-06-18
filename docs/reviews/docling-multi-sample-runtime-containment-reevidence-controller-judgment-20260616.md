# Docling Multi-sample Runtime Containment Re-evidence Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Runtime Containment Re-evidence Gate`
Controller role: evidence disposition and closeout
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the bounded no-live S4/S5/S6 Docling runtime/cache/cost containment re-evidence gate.

It does not authorize live/network/EID/FDR/PDF/source acquisition, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, `FundDocumentRepository` behavior change, source policy change, `EvidenceAnchor` schema change, CHAPTER_CONTRACT change, Service/Host/UI/renderer/quality gate integration, push, merge or PR.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth and gate scope |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-controller-judgment-20260616.md` | Accepted execution plan judgment |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-20260616.md` | Accepted execution plan |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-20260616.md` | Evidence artifact |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-review-ds-20260616.md` | AgentDS scoped evidence review |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-review-mimo-20260616.md` | AgentMiMo scoped evidence review |
| `reports/docling-runtime-containment/20260616/runtime-summary.json` | Runtime summary |
| `reports/docling-runtime-containment/20260616/manifests/*.json` | Single-sample manifests |
| `reports/docling-runtime-containment/20260616/outputs/*.json` | Isolated Docling candidate outputs |
| `reports/docling-runtime-containment/20260616/logs/*.txt` | Per-sample stdout/stderr/exit-code logs |

## 3. Accepted Runtime Facts

| Fact | Controller disposition |
| --- | --- |
| S4 `006597 / 2024` ran through the candidate Docling export harness with exit code `0`, `real 45.94s`, input hash match, output JSON hash `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307`, empty route failures and bbox/page/table-cell locator metrics present. | `ACCEPT_CANDIDATE_RUNTIME_FACT` |
| S5 `017641 / 2024` ran through the candidate Docling export harness with exit code `0`, `real 85.80s`, input hash match, output JSON hash `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7`, empty route failures and bbox/page/table-cell locator metrics present. | `ACCEPT_CANDIDATE_RUNTIME_FACT` |
| S6 `110020 / 2024` ran through the candidate Docling export harness with exit code `0`, `real 87.34s`, input hash match, output JSON hash `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb`, empty route failures and bbox/page/table-cell locator metrics present. | `ACCEPT_CANDIDATE_RUNTIME_FACT` |
| All three runs used isolated output root `reports/docling-runtime-containment/20260616/outputs`, local `cache/docling-artifacts`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, default socket blocking and no `--docling-no-socket-block`. | `ACCEPT_CONTAINMENT_FACT` |
| Log/output scan found no runtime `docling_network_attempt_blocked`, `docling_model_artifact_unavailable`, `socket access blocked`, `snapshot_download`, `huggingface`, `modelscope` or remote model-download evidence; only expected `not_raw_xml_download_proof` blocked-claim strings appeared in output JSON. | `ACCEPT_NO_RUNTIME_DOWNLOAD_FAILURE_EVIDENCE` |
| Evidence remains candidate-only: `candidate_status`, `field_correctness_status` and `source_truth_status` remain `not_proven`; `production_parser_replacement_status` remains `not_authorized`; release/readiness remains `NOT_READY`. | `ACCEPT_BOUNDARY` |

## 4. Review Finding Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Evidence Section 1 wording could be read as a double negative because `The gate does not claim:` preceded negative labels. | DS-F1 | `ACCEPT_CLOSED` | Evidence artifact now states `The gate explicitly states these non-proof boundaries:`. |
| Evidence Section 1 non-proof labels are semantically correct. | MiMo-F1 | `ACCEPT` | The wording was improved for clarity; no substantive evidence defect. |
| `runtime-summary.json` uses `pass_candidate_only_not_ready` while the artifact verdict uses the full verdict token. | MiMo-F2 | `ACCEPT_AS_NONBLOCKING` | Summary value and artifact verdict are semantically aligned; no schema is production-facing. |

## 5. Accepted / Rejected / Residual Table

| Claim | Decision | Reason |
| --- | --- | --- |
| Accept S4/S5/S6 bounded runtime/cache/cost containment evidence for candidate Docling route. | `ACCEPT` | All three samples satisfy the accepted plan's pass criteria. |
| Proceed to `Docling Full-document Coverage Evidence Gate`. | `ACCEPT_WITH_BOUNDARY` | Runtime containment blocker is closed for S4/S5/S6; next gate must remain evidence-only and `NOT_READY`. |
| Treat Docling as a production baseline. | `REJECT` | Baseline disposition still requires full-document coverage, EvidenceAnchor mapping, comparative quality and cost/performance disposition. |
| Treat Docling output as source truth or full field correctness proof. | `REJECT` | Candidate-only output; correctness/source truth remains not proven. |
| Replace production parser or change repository behavior. | `REJECT` | No production behavior change was authorized or made. |
| Move release/readiness from `NOT_READY`. | `REJECT` | This evidence is not readiness/release proof. |

## 6. Validation

Commands run across the evidence and closeout:

```text
git status --short
git status --branch --short
git diff --check
shasum -a 256 <S4/S5/S6 accepted input PDFs>
du -sh cache/docling-artifacts
python -m json.tool reports/docling-runtime-containment/20260616/manifests/*.json
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /usr/bin/time -p uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <S4/S5/S6 single-sample manifest> --workspace-root . --output-root reports/docling-runtime-containment/20260616/outputs --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts --allow-overwrite
python -m json.tool reports/docling-runtime-containment/20260616/outputs/*.json
jq '{fund_code, document_year, candidate_status, field_correctness_status, source_truth_status, production_parser_replacement_status, route_failures: .failure_taxonomy.route_failures, summary_metrics}' reports/docling-runtime-containment/20260616/outputs/*.json
shasum -a 256 reports/docling-runtime-containment/20260616/outputs/*.json
rg -n "docling_network_attempt_blocked|docling_model_artifact_unavailable|socket access blocked|snapshot_download|huggingface|modelscope|download" reports/docling-runtime-containment/20260616/logs reports/docling-runtime-containment/20260616/outputs
python -m json.tool reports/docling-runtime-containment/20260616/runtime-summary.json
jq -e '.overall_result == "pass_candidate_only_not_ready" and all(.samples[]; .command_exit_code == 0 and .route_failures == [] and .has_bbox == true and .has_page_number == true and .has_table_cell_locator == true and .runtime_containment_status == "pass_candidate_only_not_ready")' reports/docling-runtime-containment/20260616/runtime-summary.json
tmux-cli status
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command} #{pane_title}'
tmux-cli send -p agents:0.2 /clear
tmux-cli send -p agents:0.3 /clear
tmux-cli send -p agents:0.2 <DS scoped evidence review prompt>
tmux-cli send -p agents:0.3 <MiMo scoped evidence review prompt>
tmux capture-pane -p -t agents:0.2 -S -500
tmux capture-pane -p -t agents:0.3 -S -700
```

`git diff --check` passed. No live/source acquisition/provider/LLM/readiness/release/PR command was run.

## 7. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| Full-document coverage and paragraph/table completeness beyond locator metrics | open | baseline qualification owner | `Docling Full-document Coverage Evidence Gate` |
| EvidenceAnchor mapping from Docling candidate locators | open | documents/schema owner | future EvidenceAnchor mapping gate |
| Comparative quality against pdfplumber / EID HTML route | open | baseline qualification owner | future comparative correctness / route disposition gate |
| Production model artifact provenance | open | production integration owner | separate provenance gate before dependency promotion |
| Runtime cost threshold calibration | open | baseline qualification owner | future performance/cache/cost disposition gate |

## 8. Next Gate Recommendation

Recommended next gate:

```text
Docling Full-document Coverage Evidence Gate
```

Purpose:

- evaluate full-document coverage for S1/S4/S5/S6 candidate Docling outputs;
- measure section/table/paragraph coverage and obvious completeness gaps;
- preserve candidate-only and `NOT_READY`;
- avoid baseline promotion, production parser replacement, source-truth claim, readiness/release claim and repository behavior changes.

## 9. Final Verdict

```text
VERDICT: ACCEPT_MULTI_SAMPLE_RUNTIME_CONTAINMENT_READY_FOR_FULL_DOCUMENT_COVERAGE_GATE_NOT_READY
```
