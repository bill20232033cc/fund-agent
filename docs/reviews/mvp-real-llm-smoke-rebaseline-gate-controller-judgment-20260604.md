# MVP Real LLM Smoke Re-baseline Gate Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM smoke re-baseline gate`
- Gate classification: `heavy`
- Controller role: judge evidence and independent reviews only; no specialist implementation, no live provider retry, no provider/runtime/default/budget change.
- Plan checkpoint: `4fd5b5b`
- Control sync checkpoint before evidence: `6b649a9`
- Evidence artifact: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`
- Evidence reviews:
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-review-ds-20260604.md`
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-review-mimo-20260604.md`

## 2. Direct Evidence Reviewed

The evidence artifact records a secret-safe presence-only preflight:

- `FUND_AGENT_LLM_PROVIDER` present: `false`
- `FUND_AGENT_LLM_MODEL` present: `false`
- `FUND_AGENT_LLM_BASE_URL` present: `false`
- API key env var checked: `FUND_AGENT_LLM_API_KEY`
- API key present: `false`
- Required env/config all present: `false`
- Optional runtime env variables explicitly set: all `false`

The evidence artifact records:

- Preflight classification: `environment_blocked`
- Local non-live safety validation: not run due to `environment_blocked`
- Reviewed live smoke command `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`: not run
- Retained `reports/llm-runs/` artifact: none
- Secret/redaction scan over the evidence artifact: PASS
- Git integrity: no tracked source/test/config/runtime/design/control/startup diff during specialist evidence execution; only the allowed evidence artifact was added

## 3. Independent Review Findings

AgentDS review verdict:

- Evidence artifact correctness: PASS
- Gate outcome: BLOCKED by `environment_blocked`
- Blocking findings against evidence artifact: 0
- Non-blocking observations: A2/A6 wording could more explicitly separate artifact correctness from gate outcome.

AgentMiMo review verdict:

- Evidence artifact correctness: PASS
- Gate outcome: BLOCKED by `environment_blocked`
- Blocking findings against evidence artifact: 0
- Non-blocking residual: A3-A6/A8 classification wording conflates not-evaluated live-smoke criteria with gate-level blocker.

Controller accepts both non-blocking presentation observations as residual wording only. They do not require evidence rewrite because the blocker classification, owner and stop condition are explicit and same-source.

## 4. Verifier Matrix

| Criterion | Direct evidence | Validation command / artifact | Judgment |
|---|---|---|---|
| A1. Plan scope and forbidden-scope safety | Specialist evidence wrote only the allowed evidence artifact and changed no source/test/config/runtime behavior. | `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md` §3, §9, §11; DS/MiMo evidence reviews | PASS |
| A2. Env/config presence preflight is secret-safe | Presence-only preflight printed booleans and env var names only; required provider/model/base-url/key are absent. | Evidence §4; redaction scan evidence §7 | BLOCKED: `environment_blocked` |
| A3. Reviewed real-smoke command is singular and scoped | The reviewed command is recorded but correctly not run after A2 hard stop; no alternate live probe was run. | Evidence §6 | BLOCKED: not evaluated because A2 stopped live smoke |
| A4. Incomplete fail-closed and stdout safety | No live smoke ran; no stdout was produced; no partial report was emitted. | Evidence §6, §9 | BLOCKED: not evaluated because A2 stopped live smoke |
| A5. Accepted report safety if smoke succeeds | No accepted report exists from this gate because live smoke did not run. | Evidence §6 | BLOCKED: not evaluated because A2 stopped live smoke |
| A6. Safe diagnostic matrix and no secret leakage | Artifact redaction scan passed; runtime matrix does not exist because live smoke did not run. | Evidence §7; DS/MiMo reviews | BLOCKED for runtime evidence; artifact redaction PASS |
| A7. Direct evidence integrity | Pre/post git branch/status/diff recorded; no tracked diff from evidence execution. | Evidence §3, §11 | PASS |
| A8. Provider timeout/block classification preserves current semantics | Provider smoke did not run; no timeout/default/budget/runtime behavior was changed. | Evidence §6, §9 | BLOCKED: not evaluated because A2 stopped live smoke |
| A9. Boundary guardrails | No Dayu runtime, Agent runtime, multi-year runtime, direct PDF/cache/source-helper read, `extra_payload`, golden/readiness, PR/push/release, deterministic fallback or stdout partial report occurred. | Evidence §9; DS/MiMo reviews | PASS |

## 5. Controller Judgment

Evidence artifact correctness is accepted.

The gate is not accepted. `Real LLM smoke re-baseline gate` is blocked at evidence stage by `environment_blocked` because required LLM provider/model/base-url/API-key presence is absent. The accepted plan required a secret-safe preflight before any real smoke and allowed exactly one reviewed live smoke only if preflight and local safety were safe. Running live smoke without required env/config would violate the plan; substituting historical retained artifacts would violate the direct-evidence requirement.

Controller classification:

- Blocker ID: `B1`
- Classification: `environment_blocked`
- Owner: controller / environment owner
- Current gate status: blocked, not accepted
- Next entry point: configure the required LLM env/config in a secret-safe way, then rerun the same `Real LLM smoke re-baseline gate` evidence execution from the preflight step under the accepted plan/controller judgment. Do not enter `Chapter acceptance calibration gate` before the smoke evidence, independent reviews, controller judgment and accepted checkpoint complete.

## 6. Stop Conditions

Stop now. Do not proceed to the next phase gate.

Forbidden until the blocker is resolved and this gate is accepted:

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
| Required LLM env/config absent | `environment_blocked` blocker | Controller / environment owner | Provide provider/model/base-url/API-key presence without printing secret values, then rerun same gate evidence execution. |
| A2/A3-A6/A8 wording separates gate blocker from artifact correctness imperfectly | Non-blocking presentation residual | Controller | Preserve distinction in control/startup and future evidence instructions; no evidence rewrite required. |
