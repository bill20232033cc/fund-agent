# MVP Future Live Provider Calibration Evidence Gate — Live Rerun Evidence Review (MiMo)

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Classification: `heavy`
- Role: independent evidence reviewer only; not controller, not evidence executor, not implementation/fix worker
- Evidence artifact under review: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-20260605.md`
- Accepted plan: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- Prior controller judgment: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-controller-judgment-20260605.md`
- Review artifact write path: this file only

## 2. Sources Read

- `AGENTS.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-controller-judgment-20260605.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-20260605.md`
- `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/manifest.json`
- `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/chapters/chapter-01.json`
- `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/chapters/chapter-03.json`
- `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/chapters/chapter-06.json`

## 3. Retained Artifact Verification

Reviewer independently read the retained artifact at `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/` to verify the evidence artifact's factual claims.

### 3.1 Manifest Verification

| Field | Evidence claim | Manifest value | Match |
|---|---|---|---|
| artifact_kind | `llm_incomplete_run_diagnostic` | `llm_incomplete_run_diagnostic` | YES |
| schema_version | `llm_incomplete_run_artifact_manifest.v1` | `llm_incomplete_run_artifact_manifest.v1` | YES |
| fund/year | `006597 / 2024` | `006597 / 2024` | YES |
| chapter_count | `6` | `6` | YES |
| final_assembly_status | `incomplete` | `incomplete` | YES |
| orchestration_status | `blocked` | `blocked` | YES |
| redaction_applied | `false` | `false` | YES |
| run_id | `host_run_bd4ba477cecf42c9` | `host_run_bd4ba477cecf42c9` | YES |

### 3.2 Chapter Matrix Spot-Check

Reviewer read chapters 1, 3, and 6 directly. All three confirm:

- `status`: `failed`
- `stop_reason`: `llm_network_error`
- `failure_category`: `provider_runtime`
- `terminal_issue_class`: `ConnectError`
- `provider_runtime_category`: `network`
- `timeout_root_cause_hint`: `non_timeout_provider_runtime`
- `operation`: `writer`
- `accepted`: `false`
- `accepted_conclusion_present`: `false`

These match the evidence artifact's chapter matrix table. No chapter has an accepted draft or conclusion.

### 3.3 Stderr Safe Summary Verification

The evidence artifact's stderr summary matches the prior controller judgment's documented command authorization (`uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`). The stderr reports `orchestration_status=blocked`, `final_assembly_status=incomplete`, all six chapters `failed/llm_network_error/provider_runtime`, and `error_type=_LLMIncompleteHostRunError`. No secrets or raw prompts appear in the safe summary.

## 4. Plan Sequence Compliance

| Step | Plan requirement | Evidence | Result |
|---|---|---|---|
| 1 | Git/scope preflight | Section 3 records branch, status, diff | PASS |
| 2 | Presence-only readiness | Section 4 ran the exact command from plan Section 5.2 | PASS |
| 3 | Stop if readiness fails | Readiness passed; stop condition not reached | PASS |
| 4 | Exactly one live command | Section 5.1; command count = 1 | PASS |
| 5 | No overrides | Section 5.1; no --llm-progress, timeout, model, endpoint, etc. | PASS |
| 6 | Retained artifact parsed | Section 6; same-run artifact from the single command | PASS |
| 7 | Redaction scan | Section 7; rg scan found only policy-text matches | PASS |
| 8 | Verifier matrix | Section 8; A1-A9 | See Section 6 below |
| 9 | Outcome classification | Section 9 | BLOCKING FINDING — see Section 6 |

## 5. Verifier Matrix Review

| ID | Evidence verdict | Reviewer verdict | Notes |
|---|---|---|---|
| A1 | PASS | PASS | Plan accepted; evidence ran after prior controller judgment |
| A2 | PASS | PASS | Presence-only output has booleans and safe field names only; no values, no HTTP |
| A3 | PASS | PASS | Exactly 1 live command; no probe, retry, fallback, or second command |
| A4 | PASS | PASS | No overrides; git diff empty before execution; no source/config/runtime change |
| A5 | PASS | PASS | Exit 1, stdout 0 bytes, stderr safe summary, no deterministic fallback, no partial stdout |
| A6 | PASS | PASS | Retained artifact path matches stderr output; manifest and chapter files verified by reviewer |
| A7 | PASS | PASS | Redaction scan found only policy-text and redaction-policy label matches |
| A8 | PASS | PASS | No source/test/config/control/startup/runtime/quality/golden/Agent/score-loop edits |
| A9 | PASS | **BLOCKING** | Evidence claims PASS but the classification itself is wrong — see Finding 1 |

## 6. Findings

### Finding 1 — Outcome Classification Mismatch [BLOCKING]

**Severity**: blocking

**Evidence**: The evidence artifact (Section 9) classifies the outcome as `provider_runtime_residual_narrowed`. The retained artifact shows all six chapters failed with the identical non-timeout error (`ConnectError` / `llm_network_error` / `provider_runtime_category: network` / `timeout_root_cause_hint: non_timeout_provider_runtime`). No chapter has an accepted draft or conclusion.

**Plan reference**: Accepted plan Section 6 defines two relevant classifications:

- **6.3 `provider_runtime_residual_narrowed`**: requires "only a subset of chapters or operations times out; other chapters produce accepted conclusions or non-timeout blockers." This definition requires a MIX of outcomes — some accepted, some failed with different failure modes.
- **6.4 `provider_runtime_error_non_timeout`**: requires "the retained artifact or stderr safe summary reports provider runtime failures other than timeout, including `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, HTTP error, malformed response or rate limiting."

**Analysis**: The observed outcome is uniform failure across all six chapters with `llm_network_error` / `ConnectError` — a non-timeout provider runtime error. There are zero accepted conclusions and zero timeout-based failures. This matches Section 6.4 (`provider_runtime_error_non_timeout`), not Section 6.3 (`provider_runtime_residual_narrowed`).

The evidence artifact's own Section 9 text acknowledges this: "all six body chapters failed at the writer operation with `ConnectError` / `llm_network_error` and provider runtime category `network`. This is a current live provider runtime residual, but it is not the prior `ReadTimeout` / `llm_timeout` shape." Despite this accurate description, the classification label chosen does not match the plan taxonomy.

**Impact**: The classification mismatch means A9 (clear next residual classification) is incorrectly marked PASS. The "next entry point" recommendation in the evidence artifact is reasonable in substance but references the wrong classification taxonomy, which could cause the controller to route to the wrong residual owner (Section 6.3 owner vs Section 6.4 owner per plan Section 11).

**Required fix**: The evidence artifact must reclassify the outcome from `provider_runtime_residual_narrowed` to `provider_runtime_error_non_timeout`. The next entry point text should then reference the correct residual owner: "provider runtime operator / future calibration controller" per plan Section 11, with the specific guidance: "stop and hand controller a same-run non-timeout provider residual. Do not classify it as endpoint availability, do not retry, and do not change provider/default/runtime/budget in this gate."

### Finding 2 — Informational: A9 Verder Discrepancy [NON-BLOCKING]

**Severity**: non-blocking (informational)

The A9 row in the verifier matrix states "Outcome classification is based only on current readiness output and same-run retained artifact evidence, not historical runtime inference" and marks it PASS. The methodology is correct (same-run evidence only, no historical substitution), but the classification result derived from that evidence is wrong (Finding 1). Once Finding 1 is fixed, A9 becomes a clean PASS.

## 7. Residual Risk

If the classification is corrected to `provider_runtime_error_non_timeout`, the residual risk is:

- The provider endpoint is unreachable from this execution shell (ConnectError, not ReadTimeout).
- This is a different failure shape from the prior `ReadTimeout` / `llm_timeout` residual, confirming the residual has narrowed from "timeout" to "network connectivity."
- No chapter acceptance calibration is possible because no chapter produced an accepted draft or conclusion.
- The system's fail-closed semantics remain intact: exit 1, stdout empty, no fallback, incomplete assembly.

## 8. Review Verdict

**VERDICT: FINDINGS — BLOCKING**

One blocking finding (Finding 1: outcome classification mismatch). The evidence artifact's factual claims are all verified correct against the retained artifact. The only issue is the outcome classification label and its downstream routing implications.

**Required action**: Evidence executor must reclassify the outcome from `provider_runtime_residual_narrowed` to `provider_runtime_error_non_timeout` and update the next entry point text accordingly. No re-execution of the live command is needed; the retained artifact evidence is sufficient.

After the classification fix, the evidence artifact should be re-reviewed (or accepted by controller with the correction noted) before the controller issues a judgment.
