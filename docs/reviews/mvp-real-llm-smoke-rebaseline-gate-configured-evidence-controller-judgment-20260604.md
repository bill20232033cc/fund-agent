# MVP Real LLM Smoke Re-baseline Gate Configured Evidence Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM smoke re-baseline gate`
- Gate classification: `heavy`
- Controller role: judge configured evidence and independent reviews only; no implementation, no live provider retry, no provider/runtime/default/budget change.
- Plan checkpoint: `4fd5b5b`
- Prior environment-blocked evidence: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`
- Configured evidence artifact: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`
- Configured evidence controller decision: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-decision-20260604.md`
- Configured evidence reviews:
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-review-ds-20260604.md`
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-review-mimo-20260604.md`
- Retained artifact: `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/manifest.json`

## 2. Direct Evidence Reviewed

The configured evidence records:

- Required provider/model/base-url/API-key presence is now present in the current shell.
- Optional runtime env overrides are absent.
- Local non-live safety validation passed: `306 passed`.
- The first configured live smoke attempt was operator-interrupted after approximately `900s`, before the derived Host deadline of approximately `2160s`; that attempt is correctly classified as inconclusive and superseded.
- A controller decision then authorized exactly one replacement attempt of the same reviewed command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

The replacement attempt records:

- Exit code: `1`
- Stdout: empty
- Stderr: safe fail-closed summary present
- Deterministic fallback: not run
- Accepted full report: not produced
- Orchestration status: `blocked`
- Final assembly status: `incomplete`
- Host run status: `failed`
- Host timeout classification: `none`
- Retained artifact path: `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/manifest.json`

Retained summary direct evidence:

- All six body chapters failed with `failure_category=llm_timeout` and `stop_reason=llm_timeout`.
- First failed chapter: chapter 1, auditor operation, `ReadTimeout`, provider runtime category `timeout`, `2/2` attempts, timeout `60.0s`, approx `1074` prompt tokens, timeout root-cause hint `small_prompt_provider_timeout`.
- Chapters 1 and 6 reached auditor timeout after one writer draft attempt.
- Chapters 2, 3, 4 and 5 failed at writer timeout.
- No chapter had accepted draft or accepted conclusion.
- Final assembly issues block chapter 7 readiness because chapters 1-6 are not accepted.

Redaction evidence:

- Review/evidence artifact scan found no secret-like value, URL value, Authorization value or Bearer value.
- Retained artifact scan found no API key, base URL, Authorization, Bearer, raw prompt, raw provider response, raw audit response, message body or request headers.
- Writer draft markdown files were not promoted into the evidence artifact; only safe scalar summaries from manifest/summary JSON were used.

## 3. Independent Review Findings

AgentMiMo review verdict:

- Evidence artifact correctness: PASS
- Replacement command singular/scoped and authorized: PASS
- Fail-closed / no deterministic fallback / stdout empty: PASS
- Retained artifact supports `provider_runtime_residual` / all-chapters `llm_timeout`: PASS
- Chapter ids and boundary guardrails preserved: PASS
- Redaction and raw-payload constraints satisfied: PASS
- Gate outcome recommendation: accept evidence correctness; keep gate blocked by `B3 provider_runtime_residual_all_chapters_llm_timeout`.

AgentDS review verdict:

- Evidence artifact correctness: PASS
- A1-A9 mapping correctness: PASS
- Secret-safe preflight and redaction scan adequacy: PASS
- Direct evidence integrity and no historical substitution: PASS
- Residual classification `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL`: PASS
- Stop condition `no Chapter acceptance calibration`: PASS
- Non-blocking observation: `attempt_count=0` for chapters 2-5 may confuse readers because provider attempts are recorded separately in runtime diagnostics.

Controller accepts the AgentDS non-blocking observation as documentation nuance only. The evidence artifact already includes provider attempt details in retained runtime diagnostics and scalar summary.

## 4. Verifier Matrix Judgment

| Criterion | Judgment | Basis |
|---|---|---|
| A1. Plan scope and forbidden-scope safety | PASS | Configured evidence stayed within controller-authorized evidence scope; no source/test/config/runtime behavior changed. |
| A2. Env/config presence preflight is secret-safe | PASS | Initial and replacement preflights record booleans and env var names only; no secret/config values printed. |
| A3. Reviewed real-smoke command is singular and scoped | PASS | One replacement command was authorized and run: same fund/year/`--use-llm`, no provider/runtime/default overrides. |
| A4. Incomplete fail-closed and stdout safety | PASS | Replacement smoke naturally exited `1`, stdout empty, safe stderr summary present, retained artifact present, no deterministic fallback. |
| A5. Accepted report safety if smoke succeeds | NOT_APPLICABLE | Smoke did not succeed and no accepted report was produced. |
| A6. Safe diagnostic matrix and no secret leakage | PASS | CLI/retained artifact provide safe chapter/runtime matrix; redaction scans passed. |
| A7. Direct evidence integrity | PASS | Replacement evidence uses same-run retained artifact `host_run_b52b779e7e9a43c`; historical artifacts are not substituted. |
| A8. Provider timeout/block classification preserves current semantics | PASS_WITH_RESIDUAL | Same-run evidence classifies all chapters as provider `ReadTimeout` / `llm_timeout`; no timeout/default/budget changes were made. |
| A9. Boundary guardrails | PASS | No Dayu runtime dependency, Agent runtime, multi-year runtime, direct PDF/cache/source-helper read, `extra_payload`, golden/readiness, PR/push/release or deterministic fallback action occurred. |

## 5. Controller Judgment

Configured evidence artifact correctness is accepted.

The gate is not accepted as complete. It remains blocked at evidence stage with direct provider-runtime residual:

- Blocker ID: `B3`
- Classification: `provider_runtime_residual_all_chapters_llm_timeout`
- Gate outcome: `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL`
- Owner: future provider runtime residual disposition / calibration owner

`B1 environment_blocked` is resolved. Required LLM env/config presence exists in the current shell.

`B2 operator_interrupted_before_derived_host_deadline` is superseded by the controller-authorized replacement attempt and should not be reopened.

This gate now has direct current smoke evidence:

- fail-closed behavior preserved;
- stdout empty on incomplete;
- no deterministic fallback;
- retained incomplete artifact produced;
- all six body chapters blocked by provider runtime `llm_timeout`.

The next entry is not Chapter acceptance calibration. No chapter produced accepted draft/conclusion; there is no content acceptance surface to calibrate. The next scoped gate must be provider runtime residual disposition/calibration or provider endpoint/runtime policy decision.

## 6. Stop Conditions

Stop now. Do not proceed to the next phase gate.

Forbidden until a future controller gate authorizes it:

- Chapter acceptance calibration
- Provider default/runtime/budget changes
- Additional live provider probes or alternate smoke commands
- Agent runtime implementation
- Multi-year evidence runtime implementation
- Score-loop work
- Golden/readiness/snapshot/strict-correctness/release-readiness work
- PR/push/release external state changes

## 7. Residuals

| Residual | Classification | Owner | Next action |
|---|---|---|---|
| All chapters fail with provider `ReadTimeout` / `llm_timeout` | `provider_runtime_residual_all_chapters_llm_timeout` blocker | Provider runtime residual disposition / calibration owner | Decide provider endpoint/runtime policy or calibration strategy in a new scoped gate; do not change defaults in this gate. |
| `attempt_count` semantics may confuse readers | Non-blocking documentation nuance | Controller / future artifact schema owner | Keep scalar provider attempts in runtime diagnostics; no evidence rewrite required. |
