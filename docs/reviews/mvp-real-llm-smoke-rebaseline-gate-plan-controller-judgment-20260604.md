# MVP Real LLM Smoke Re-baseline Gate Plan Controller Judgment

## 1. Controller Context

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM smoke re-baseline gate`
- Gate classification: `heavy`
- Rule truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Previous accepted gate: `Template truth validation gate`
- Previous gate checkpoint: `c907258`
- Previous control sync checkpoint: `e11f5a3`
- Plan artifact: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
- Plan reviews:
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-review-ds-20260604.md`
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-review-mimo-20260604.md`

Controller role check: this judgment is controller work. It accepts or rejects the
plan only. It does not authorize source/test/config/runtime behavior changes,
provider default/runtime/budget changes, Agent runtime implementation, multi-year
runtime, score-loop, golden/readiness, PR, push, release, or external-state actions.

## 2. Judgment

Verdict: **ACCEPT PLAN**

The `Real LLM smoke re-baseline gate` plan is accepted locally.

Both independent plan reviews returned `PASS` with zero blocking findings. The plan
correctly limits the current stage to planning and defines a later evidence protocol
that may run exactly one reviewed real-smoke command only after this plan has review,
controller judgment, and an accepted local checkpoint.

Basis:

- The plan preserves the accepted `Template truth validation gate` facts and does not
  reuse historical retained runs as current smoke evidence.
- The plan classifies this gate as `heavy`, which is appropriate because real provider
  smoke evidence affects subsequent chapter acceptance calibration sequencing and
  must preserve fail-closed/no-fallback/stdout safety semantics.
- The plan's verifier matrix A1-A9 covers plan scope, secret-safe preflight, exactly
  one reviewed smoke command, incomplete fail-closed behavior, accepted-report safety,
  safe diagnostics/redaction, direct evidence integrity, provider timeout/block
  classification, and boundary guardrails.
- The plan explicitly forbids provider default/runtime/budget changes, Agent runtime,
  multi-year runtime, score-loop, golden/readiness, PR/push/release, direct Dayu
  runtime dependency, direct PDF/cache/source-helper access, and `extra_payload`
  business parameters.
- The plan requires current direct evidence from the future smoke execution and
  prohibits old logs, old retained artifacts, old reviews, or aggregate history from
  substituting for the current run.

Based on `docs/design.md` and first principles, accepting this plan is the current
best practice because the next risk is not template truth but the current provider
backed `--use-llm` baseline. The plan constrains that evidence collection tightly
enough to observe the current state without changing runtime defaults or weakening
safety semantics.

## 3. Review Finding Disposition

### DS Finding 1: Preflight provider/model value boundary is conservative

Disposition: **Accepted as non-blocking residual for evidence execution**

Controller decision: no plan fix required. The evidence step must keep the accepted
presence-only preflight unless the controller explicitly changes the evidence
handoff. In the next evidence step, provider/model/base URL/key handling must remain
secret-safe; base URL values, API keys, Authorization headers, and raw config dumps
must not be written.

Rationale: conservative presence-only reporting may reduce diagnostics, but it
protects secrets and does not block evidence collection.

### DS Finding 2: Temporary capture file lifecycle after secret detection is implicit

Disposition: **Accepted as non-blocking residual; promoted to evidence-step requirement**

Controller decision: the evidence execution handoff must require deletion or
quarantine of temporary capture files if secret/raw prompt/raw response content is
detected. Such files must not be committed or referenced as accepted evidence.

Rationale: the plan already treats detected secret/raw content as a blocker. The
controller adds lifecycle handling for local capture files.

### DS Finding 3: Local non-live validation gating semantics are deferred to controller

Disposition: **Accepted as controller-owned evidence-step classification**

Controller decision: no plan fix required. During evidence execution, failures in
`test_llm_run_artifacts.py`, `test_llm_provider.py`, `test_cli.py`, or Service LLM
boundary tests should be treated as likely harness/safety blockers until controller
review classifies otherwise. The evidence owner must not run live smoke over failed
safety-relevant local validation without controller approval.

Rationale: the plan already prevents bypassing local validation failures. Controller
judgment at evidence time can apply differential relevance based on actual failing
tests.

### MiMo Review

Disposition: **PASS with no findings**

Controller decision: MiMo found no blocking or non-blocking findings. No plan fix is
required.

## 4. Accepted Plan Verifier

The accepted evidence-stage verifier is the plan's A1-A9 matrix, with these
controller additions:

| Area | Controller requirement for evidence step |
| --- | --- |
| Secret-safe preflight | Keep presence-only reporting unless separately authorized; never print API key, Authorization, base URL value, or raw config |
| Temporary capture files | If secret/raw prompt/raw provider response/raw audit response is detected, classify blocker and delete/quarantine local temp captures; do not commit them |
| Local validation failures | Do not run live smoke over failed safety-relevant local validation without controller judgment |
| Live command scope | Exactly one reviewed command is allowed after evidence handoff: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`; no provider/runtime/default overrides |
| Outcome handling | Timeout/block/incomplete is valid baseline evidence only if fail-closed, stdout-safe, retained artifact-safe, and no deterministic fallback |

## 5. Stop Conditions For Next Step

Stop before live smoke if:

- Required provider env/config presence is absent.
- Any secret-safe preflight would require printing secret values, base URL values, raw
  config, or Authorization headers.
- Safety-relevant local non-live validation fails and controller has not explicitly
  classified it as unrelated to smoke evidence safety.
- The evidence command requires provider default/runtime/budget changes, timeout
  overrides, model/endpoint changes, repair-budget changes, prompt/debug overrides,
  or more than one live smoke command.
- Any step would modify source/test/config/runtime behavior, quality gate semantics,
  provider defaults, golden/readiness state, Agent runtime, multi-year runtime,
  score-loop, PR/push/release, or external state.

## 6. Accepted Checkpoint Requirements

The plan checkpoint may include only:

- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-review-ds-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-review-mimo-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-controller-judgment-20260604.md`

It must not include source/test/config/runtime behavior changes, control/startup
sync edits, design edits, template edits, live provider artifacts, retained smoke
artifacts, or unrelated untracked files.

## 7. Next Entry Point

After this plan checkpoint and control/startup sync, continue within the same gate to:

`Real LLM smoke re-baseline evidence execution`

The evidence step must be delegated as specialist evidence collection. It must start
with secret-safe preflight and local validation as directed by this judgment. A live
real LLM smoke command is allowed only if preflight and safety checks pass. This
judgment does not authorize chapter acceptance calibration, provider runtime/default
changes, Agent runtime implementation, multi-year runtime, score-loop, golden/readiness,
PR, push, or release.
