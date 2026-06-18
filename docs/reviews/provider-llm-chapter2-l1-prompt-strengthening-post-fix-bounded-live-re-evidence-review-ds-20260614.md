# Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence — DS Review

Date: 2026-06-14

Role: AgentDS review worker

Gate: `Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-20260614.md`

Verdict: `PASS`

## Scope

This review cross-checks the evidence artifact against safe metadata only (manifest, summary, chapter-02, chapter-03, chapter-05 JSON files). No writer/auditor/repair Markdown bodies, raw prompts, provider payloads, source/PDF/cache body, or final report body were read.

## Evidence Read

| Source | Use |
|---|---|
| `AGENTS.md` | Execution rules, fail-closed semantics, source policy |
| `docs/current-startup-packet.md` | Current gate scope, accepted checkpoints |
| `docs/implementation-control.md` | Control truth, implementation scope |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-controller-judgment-20260614.md` | Prior gate verdict and next gate recommendation |
| `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-20260614.md` | Review target |
| `manifest.json` | Run-level metadata |
| `summary.json` | Chapter matrix, first_failed, runtime diagnostics |
| `chapter-02.json` | Chapter 2 attempt-level diagnostics |
| `chapter-03.json` | Chapter 3 diagnostics |
| `chapter-05.json` | Chapter 5 status |

## Cross-check Results

### 1. Fidelity to safe metadata

Every metadata claim in the evidence artifact was verified against the safe JSON files.

**Overall run facts — manifest.json:**

| Evidence claim | JSON source | Match |
|---|---|---|
| `orchestration_status=partial` | `manifest.orchestration_status: "partial"` | YES |
| `final_assembly_status=incomplete` | `manifest.final_assembly_status: "incomplete"` | YES |
| `run_id: host_run_9dbb1b5be0e54cdb` | `manifest.run_id: "host_run_9dbb1b5be0e54cdb"` | YES |

**First failed — summary.json `first_failed` block:**

| Evidence claim | JSON source | Match |
|---|---|---|
| chapter_id: `2` | `first_failed.chapter_id: 2` | YES |
| status: `failed` | `first_failed.status: "failed"` | YES |
| stop_reason: `repair_budget_exhausted` | `first_failed.stop_reason: "repair_budget_exhausted"` | YES |
| failure_category: `prompt_contract` | `first_failed.failure_category: "prompt_contract"` | YES |
| failure_subcategory: `l1_numerical_closure` | `first_failed.failure_subcategory: "l1_numerical_closure"` | YES |
| attempt_count: `2` | `first_failed.attempt_count: 2` | YES |

**First failed runtime — summary.json `runtime_diagnostics.first_failed`:**

| Evidence claim | JSON source | Match |
|---|---|---|
| runtime_operation: `auditor` | `first_failed.runtime_operation: "auditor"` | YES |
| provider_attempt_count: `0` | `first_failed.provider_attempt_count: 0` | YES |

**Chapter matrix — summary.json `chapter_matrix`:**

| Ch | Evidence (status/stop/category/subcategory/attempts) | JSON | Match |
|---|---|---|---|
| 1 | `accepted` / `none` / null / null / 1 | `accepted` / `none` / null / null / 1 | YES |
| 2 | `failed` / `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` / 2 | `failed` / `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` / 2 | YES |
| 3 | `blocked` / `missing_required_output_marker` / `prompt_contract` / `missing_required_marker` / 1 | `blocked` / `missing_required_output_marker` / `prompt_contract` / `missing_required_marker` / 1 | YES |
| 4 | `accepted` / `none` / null / null / 1 | `accepted` / `none` / null / null / 1 | YES |
| 5 | `accepted` / `none` / null / null / 1 | `accepted` / `none` / null / null / 1 | YES |
| 6 | `accepted` / `none` / null / null / 1 | `accepted` / `none` / null / null / 1 | YES |

**Chapter 2 attempt-level L1 counts — `chapter-02.json` `chapter_prompt_contract_diagnostics` and `summary.json` `prompt_contract_diagnostics.chapter_phase_matrix[1]`:**

| Evidence claim | JSON source(s) | Match |
|---|---|---|
| Attempt 0: phase `programmatic_audit`, `programmatic:L1=1`, L1 count=1, required_output_missing=0, response_chars=22 | `chapter-02.json` diagnostics[0] and `summary.json` phases[0]: phase `programmatic_audit`, prefix `programmatic:L1: 1`, l1_count `1`, missing `0`, chars `22` | YES |
| Attempt 1: phase `programmatic_audit`, `programmatic:L1=2`, L1 count=2, required_output_missing=0, response_chars=22 | `chapter-02.json` diagnostics[1] and `summary.json` phases[1]: phase `programmatic_audit`, prefix `programmatic:L1: 2`, l1_count `2`, missing `0`, chars `22` | YES |

**Chapter 3 diagnostics — `chapter-03.json` and `summary.json`:**

| Evidence claim | JSON source | Match |
|---|---|---|
| status: `blocked` | `chapter-03.status: "blocked"` | YES |
| stop_reason: `missing_required_output_marker` | `chapter-03.stop_reason: "missing_required_output_marker"` | YES |
| category/subcategory: `prompt_contract` / `missing_required_marker` | `chapter-03.failure_category: "prompt_contract"`, `failure_subcategory: "missing_required_marker"` | YES |
| issue_prefix: `writer:required_output_gap_missing=1` | `chapter-03` diagnostics[0] prefix `writer:required_output_gap_missing: 1` | YES |
| reason_count: `missing_required_output_marker=1` | `chapter-03` diagnostics[0] reason_counts `missing_required_output_marker: 1` | YES |
| `max_output_chars=12000` | `chapter-03` diagnostics[0] `max_output_chars: 12000` | YES |

**Chapter 5 — `chapter-05.json`:**

| Evidence claim | JSON source | Match |
|---|---|---|
| status: `accepted` | `chapter-05.status: "accepted"` | YES |
| stop_reason: `none` | `chapter-05.stop_reason: "none"` | YES |
| category/subcategory: null | `chapter-05.failure_category: null`, `failure_subcategory: null` | YES |

**Unverifiable from safe metadata:**

- Host elapsed `234223 ms`: this value comes from stderr output of the live command. It is not present in the safe metadata JSON files (manifest, summary, or chapter artifacts). It does not affect any material conclusion.

### 2. Exit code 1 / fail-closed classification

The evidence artifact correctly classifies exit code 1 as fail-closed. The command exited with code 1, produced empty stdout, and generated incomplete diagnostic artifacts. No deterministic fallback was triggered, no report content was produced, and the system correctly halted at the first failed chapter (Chapter 2) with `repair_budget_exhausted`. The final assembly status `incomplete` confirms no partial report was emitted.

This is consistent with `AGENTS.md` fail-closed semantics: the `--use-llm` path is explicit opt-in and fail-closed, with no deterministic fallback.

### 3. Chapter 2 first failed classification

The evidence artifact correctly reports Chapter 2 as the first failed chapter with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`. This is verified in:

- `summary.json` `first_failed` block (chapter_id 2, status failed, stop_reason repair_budget_exhausted, category prompt_contract, subcategory l1_numerical_closure)
- `summary.json` `prompt_contract_diagnostics.first_failed` (chapter_id 2, category prompt_contract, subcategory l1_numerical_closure, phase programmatic_audit)
- `summary.json` `runtime_diagnostics.first_failed` (chapter_id 2, category prompt_contract, subcategory l1_numerical_closure, operation auditor, provider_attempt_count 0)
- `chapter-02.json` top-level status `failed`, stop_reason `repair_budget_exhausted`, failure_category `prompt_contract`, failure_subcategory `l1_numerical_closure`

The classification is internally consistent across all three diagnostic payloads (chapter_matrix, prompt_contract_diagnostics, runtime_diagnostics) and the chapter-level artifact.

### 4. Attempt-level L1 counts

The evidence artifact correctly reports:

- Attempt 0: L1 count = 1 (`programmatic:L1=1` in issue_id_prefix_counts, `l1_numerical_closure_count=1`)
- Attempt 1: L1 count = 2 (`programmatic:L1=2` in issue_id_prefix_counts, `l1_numerical_closure_count=2`)

Both are confirmed in `chapter-02.json` `chapter_prompt_contract_diagnostics` and `summary.json` `prompt_contract_diagnostics.chapter_phase_matrix[1].phases`. The evidence artifact's table format is a faithful transcription.

Note: L1 count increased from 1 to 2 across attempts, indicating the repair attempt produced worse L1 compliance, not better. This is accurately reported and is consistent with the `repair_budget_exhausted` terminal state.

### 5. NOT_READY preservation

The evidence artifact explicitly preserves `NOT_READY` in three locations:

- Line 19: "Release/readiness remains `NOT_READY`."
- Line 141 (residuals table): "Release/readiness | `NOT_READY` | Preserved"
- Final verdict: `LIVE_FAIL_CLOSED_CHAPTER2_L1_STILL_REPRODUCES_NOT_READY`

The `NOT_READY` suffix in the verdict string matches the convention established by prior controller judgments. The evidence artifact does not claim release readiness, MVP readiness, LLM path readiness, or general live acceptance.

### 6. Recommended next gate

The evidence artifact recommends: `Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

This recommendation is appropriate given the live evidence. The strengthened Chapter 2 prompt contract did not resolve the live Chapter 2 L1 failure. The recommended gate:

- Correctly routes to a **no-code** disposition gate ("Do not implement immediately")
- Correctly identifies the core tension: "Reconcile no-live implementation acceptance with live persistent failure"
- Correctly enumerates possible root causes (live model noncompliance, insufficient structured facts, auditor/repair mismatch, insufficient repair budget, deterministic gap rendering path)
- Correctly preserves `NOT_READY`

The recommendation is consistent with the prior controller judgment at `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-controller-judgment-20260614.md`, which deferred "Live model behavior after strengthened Chapter 2 prompt" to this gate and listed "Repair budget calibration" as a separate deferred entry.

No rewrite is needed.

## Findings

未发现实质性问题。

The evidence artifact is faithful to all safe metadata. Every numerical claim and classification was verified against manifest.json, summary.json, chapter-02.json, chapter-03.json, and chapter-05.json. All cross-checks passed.

## Open Questions

无。

## Residual Risk

- Host elapsed time `234223 ms` could not be verified from safe metadata JSON (not present in manifest/summary/chapter artifacts). It is non-material to the gate conclusion.
- Chapter 3 `blocked` status in this run differs from the prior accepted state at checkpoint `2f8dce9`. The evidence artifact correctly notes this but defers it as a separate residual after Chapter 2 disposition. The Chapter 3 metadata is accurately reported.
- Chapter 5 moved from prior residual blocker to `accepted` in this single sample. This is accurately reported as single-sample metadata only with no readiness claim.

## Verdict

`PASS`
