# Docling Multi-sample Runtime Containment Re-evidence Plan - 2026-06-16

Gate: `Docling Multi-sample Runtime Containment Re-evidence Planning Gate`
Role: planning worker fallback
Release/readiness: `NOT_READY`

## 1. Scope

This plan defines the next bounded evidence gate for proving runtime/cache/cost containment for Docling samples S4/S5/S6.

This planning gate does not run Docling conversion, does not acquire source/PDF artifacts, does not run live/network/EID/FDR commands, does not run pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, and does not modify source, tests, runtime behavior, `FundDocumentRepository`, parser behavior, source policy, `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate.

The plan exists because S4/S5/S6 Docling representation JSON files already exist, but their original conversion runs do not have accepted per-sample logs proving socket blocking, explicit local artifact use, offline flags, no hidden model download and elapsed-time cost.

## 2. Goal

The next evidence gate must answer one narrow question:

```text
Can S4/S5/S6 Docling conversion be re-run from accepted local EID-controlled PDF artifacts with explicit local Docling model artifacts, socket blocking, offline environment flags, stable output hashes and per-sample runtime/cost metrics?
```

The evidence gate must not answer:

- whether Docling is a production baseline;
- whether Docling output is source truth;
- whether Docling field correctness is fully proven;
- whether Docling should replace the production parser;
- whether release/readiness can move from `NOT_READY`.

## 3. Direct Evidence Inputs

| Input | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth and current gate scope |
| `docs/reviews/docling-baseline-runtime-containment-evidence-controller-judgment-20260616.md` | Current blocker and next-gate source |
| `docs/reviews/docling-baseline-runtime-containment-evidence-review-ds-20260616.md` | DS review, including S4/S5/S6 causal-gap residual |
| `docs/reviews/docling-baseline-runtime-containment-evidence-review-mimo-20260616.md` | MiMo PASS review |
| `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md` | Gate A runtime containment threshold source |
| `reports/representation-json/full-representation-export-manifest-20260615.json` | Existing sample/input/output route manifest. Metadata input only; do not pass this full manifest to the harness command. Evidence worker must create the single-sample manifests in Section 7. |
| `reports/docling-route-a/artifact-manifest.json` | Existing local Docling artifact inventory |

## 4. Sample Matrix

Only S4/S5/S6 are in scope. S1 `004393 / 2025` already has accepted single-sample runtime containment evidence and must not be re-run in this gate.

| Sample | Fund code | Year | Input PDF | Accepted input SHA256 | Output path for re-evidence |
| --- | --- | ---: | --- | --- | --- |
| S4 | `006597` | 2024 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf` | `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` | `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` |
| S5 | `017641` | 2024 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf` | `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` | `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` |
| S6 | `110020` | 2024 | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf` | `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` | `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` |

The evidence gate must verify the PDF SHA256 before conversion. Any mismatch is `BLOCKED_INPUT_HASH_MISMATCH_NOT_READY`.

## 5. Runner Decision

Use the existing Fund documents candidate export harness:

```text
python module: fund_agent.fund.documents.candidates.representation_export
mode: --run-built-in-handlers
route: docling_pdf_candidate
docling_artifacts_path: cache/docling-artifacts
socket block: enabled by default; do not pass --docling-no-socket-block
```

Rationale:

- `representation_export.py` is explicitly candidate-only and internal to Fund documents.
- `representation_handlers.py` sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` in `_docling_environment()`.
- The handler blocks sockets when `docling_socket_block=True`.
- The handler maps network attempts to `docling_network_attempt_blocked`.
- The handler maps missing/unavailable local model artifacts to `docling_model_artifact_unavailable`.

Do not write a new production runner, parser adapter, repository method or Service/Host/UI command for this evidence gate.

## 6. Evidence Artifact Layout

The evidence gate may create only these new scoped artifacts:

```text
reports/docling-runtime-containment/20260616/manifests/S4_006597_2024_docling_runtime_manifest.json
reports/docling-runtime-containment/20260616/manifests/S5_017641_2024_docling_runtime_manifest.json
reports/docling-runtime-containment/20260616/manifests/S6_110020_2024_docling_runtime_manifest.json
reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json
reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json
reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json
reports/docling-runtime-containment/20260616/logs/S4_006597_2024.stdout.txt
reports/docling-runtime-containment/20260616/logs/S4_006597_2024.stderr.txt
reports/docling-runtime-containment/20260616/logs/S5_017641_2024.stdout.txt
reports/docling-runtime-containment/20260616/logs/S5_017641_2024.stderr.txt
reports/docling-runtime-containment/20260616/logs/S6_110020_2024.stdout.txt
reports/docling-runtime-containment/20260616/logs/S6_110020_2024.stderr.txt
reports/docling-runtime-containment/20260616/runtime-summary.json
docs/reviews/docling-multi-sample-runtime-containment-reevidence-20260616.md
```

Forbidden output locations:

- `reports/representation-json/*` existing accepted JSON files;
- `cache/pdf/*`;
- production repository cache internals;
- source/test/runtime directories.

## 7. Manifest Template

Each per-sample manifest must use `candidate_representation_export_manifest.v1` and exactly one `docling_pdf_candidate` entry.

Example for S4:

```json
{
  "schema_version": "candidate_representation_export_manifest.v1",
  "entries": [
    {
      "sample_id": "S4",
      "fund_code": "006597",
      "document_year": 2024,
      "route": "docling_pdf_candidate",
      "mode": "handled",
      "input_artifact_path": "cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf",
      "accepted_input_sha256": "85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982",
      "provenance_judgment_path": "docs/reviews/docling-baseline-qualification-staged-eid-artifact-capture-evidence-20260615.md",
      "output_path": "reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json",
      "report_type": "annual_report"
    }
  ]
}
```

S5/S6 must use the paths and hashes in Section 4.

## 8. Allowed Evidence Commands

The evidence worker may run only these command families:

```text
git branch --show-current
git status --short
python -m json.tool <manifest-or-output-json>
shasum -a 256 <input-pdf-or-output-json>
jq <read-only assertions over evidence JSON>
du -sh cache/docling-artifacts reports/docling-runtime-containment/20260616
uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <single-sample-manifest> --workspace-root . --output-root reports/docling-runtime-containment/20260616/outputs --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts --allow-overwrite
git diff --check
```

For every `representation_export` command, `--output-root reports/docling-runtime-containment/20260616/outputs` is mandatory. The harness default output root is `reports/representation-json`; omitting `--output-root` would either fail output-path validation or risk confusing the evidence route with accepted representation artifacts.

For each conversion, the worker must wrap the command with elapsed-time capture. Recommended form:

```text
/usr/bin/time -p uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <single-sample-manifest> --workspace-root . --output-root reports/docling-runtime-containment/20260616/outputs --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts --allow-overwrite
```

The worker must redirect stdout/stderr into the scoped `logs/` files and preserve the exit code in `runtime-summary.json`. When using `/usr/bin/time -p`, parse the line shaped `real <seconds>` from the timing stderr stream or combined stderr log and copy that numeric value into `elapsed_seconds`. If the timing line is absent, classify the sample as `BLOCKED_RUNTIME_METRICS_INCOMPLETE_NOT_READY`.

## 9. Forbidden Commands And Actions

Forbidden:

- live/network/EID/FDR/source acquisition;
- any non-EID fallback;
- `--docling-no-socket-block`;
- dependency installation;
- production `FundDocumentRepository` behavior changes;
- writing to existing accepted `reports/representation-json/*` files;
- pdfplumber export;
- provider/LLM;
- `fund-analysis analyze`, `checklist`, golden, readiness, release, PR, push, merge;
- source/test/runtime code edits.

If the evidence worker needs a new script, source-code helper, dependency, broader output schema, live source acquisition or production integration to complete the task, the evidence gate must stop as `BLOCKED_NEEDS_SEPARATE_IMPLEMENTATION_OR_AUTHORIZATION_NOT_READY`.

## 10. Required Runtime Summary

The evidence gate must write `reports/docling-runtime-containment/20260616/runtime-summary.json` with at least:

```json
{
  "schema_version": "docling_runtime_containment_reevidence.v1",
  "candidate_only": true,
  "not_source_truth": true,
  "not_full_field_correctness": true,
  "not_production_parser_replacement": true,
  "not_readiness_proof": true,
  "samples": [
    {
      "sample_id": "S4",
      "fund_code": "006597",
      "document_year": 2024,
      "input_pdf": "...",
      "input_sha256_expected": "...",
      "input_sha256_actual": "...",
      "command_exit_code": 0,
      "elapsed_seconds": null,
      "artifacts_path": "cache/docling-artifacts",
      "hf_hub_offline": "1",
      "transformers_offline": "1",
      "socket_block_expected": true,
      "route_failures": [],
      "output_json": "...",
      "output_sha256": "...",
      "page_count": null,
      "heading_count": null,
      "table_count": null,
      "table_cell_count": null,
      "has_bbox": null,
      "has_page_number": null,
      "has_table_cell_locator": null,
      "runtime_containment_status": "pass_or_blocked"
    }
  ],
  "overall_result": "pass_or_blocked_not_ready"
}
```

Use numeric values where observed. `elapsed_seconds` must come from `/usr/bin/time -p` stderr or equivalent preserved timing output.

## 11. Pass / Block Criteria

### Pass for one sample

A sample may pass only if all conditions hold:

- input PDF hash matches the accepted hash;
- command exit code is `0`;
- output JSON exists and parses;
- `failure_taxonomy.route_failures` is empty;
- summary metrics show `page_count > 0`, `table_count > 0`, `has_bbox=true`, `has_page_number=true`, `has_table_cell_locator=true`;
- runtime logs show elapsed seconds;
- command did not use `--docling-no-socket-block`;
- evidence records explicit `cache/docling-artifacts` use;
- evidence preserves candidate-only status.

S4/S5/S6 are annual-report samples expected to contain table structure. If any sample unexpectedly has no tables or no table-cell locator in the candidate output, the evidence worker must record the concrete metrics and block this gate for that sample instead of weakening the pass criterion.

### Full gate pass

The evidence gate may return:

```text
VERDICT: ACCEPT_MULTI_SAMPLE_RUNTIME_CONTAINMENT_READY_FOR_FULL_DOCUMENT_COVERAGE_GATE_NOT_READY
```

only if S4/S5/S6 all pass.

### Block outcomes

Use these exact blocked outcomes when applicable:

| Condition | Required result |
| --- | --- |
| Input hash mismatch | `BLOCKED_INPUT_HASH_MISMATCH_NOT_READY` |
| Any network/socket attempt mapped to route failure | `BLOCKED_NETWORK_ATTEMPT_NOT_READY` |
| Local model artifacts unavailable | `BLOCKED_LOCAL_MODEL_ARTIFACT_UNAVAILABLE_NOT_READY` |
| Conversion command nonzero exit | `BLOCKED_CONVERSION_COMMAND_FAILED_NOT_READY` |
| Output JSON missing or invalid | `BLOCKED_OUTPUT_JSON_INVALID_NOT_READY` |
| Route failures present | `BLOCKED_ROUTE_FAILURE_NOT_READY` |
| Metrics missing or zero where required | `BLOCKED_RUNTIME_METRICS_INCOMPLETE_NOT_READY` |
| Need source acquisition, code change or dependency install | `BLOCKED_NEEDS_SEPARATE_IMPLEMENTATION_OR_AUTHORIZATION_NOT_READY` |

If one sample blocks, the evidence gate must not hide it by aggregating only successful samples.

## 12. Evidence Artifact Minimum Structure

The evidence artifact `docs/reviews/docling-multi-sample-runtime-containment-reevidence-20260616.md` must include:

1. Scope
2. Evidence Inputs
3. Commands Run
4. Sample Runtime Matrix
5. Hash And Output Validation
6. Route Failure Inspection
7. Cost / Cache Metrics
8. Blocked Claims
9. Residuals
10. Validation
11. Verdict

It must explicitly state:

- `not_source_truth`;
- `not_full_field_correctness`;
- `not_production_parser_replacement`;
- `not_readiness_proof`;
- `no_repository_behavior_change`;
- `no_service_host_ui_renderer_quality_gate_integration`.

## 13. Review Gate

After evidence execution, controller must send real tmux handoffs to AgentDS and AgentMiMo unless the user explicitly cancels or the panes are unavailable after discovery/clear verification.

Review focus:

- whether every active sample has real runtime containment logs;
- whether representation JSON existence is still kept separate from runtime proof;
- whether any output overwrote accepted `reports/representation-json/*`;
- whether any forbidden source/live/provider/readiness command was run;
- whether blocked outcomes are correctly classified;
- whether `NOT_READY` and candidate-only boundaries are preserved.

## 14. Controller Closeout

Controller must classify:

- `ACCEPT_MULTI_SAMPLE_RUNTIME_CONTAINMENT_READY_FOR_FULL_DOCUMENT_COVERAGE_GATE_NOT_READY`;
- `ACCEPT_PARTIAL_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY`;
- `REJECT_EVIDENCE_NEEDS_FIX_NOT_READY`;
- `BLOCKED_NEEDS_SEPARATE_AUTHORIZATION_NOT_READY`.

Controller must stop after closeout/control sync. Do not automatically enter full-document coverage unless the evidence gate passes and control docs are synced.

## 15. Validation For This Planning Gate

Planning gate validation:

```text
git diff --check
git status --short
```

## 16. Final Planning Verdict

```text
VERDICT: PLAN_READY_FOR_MULTI_SAMPLE_RUNTIME_CONTAINMENT_REEVIDENCE_REVIEW_NOT_READY
```
