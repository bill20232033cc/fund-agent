# MVP Real LLM Smoke Re-baseline Gate Evidence

## 1. Scope

- Role: AgentCodex specialist evidence execution.
- Phase: `MVP typed-template-to-agent report generation stabilization phase`.
- Gate: `Gate 2 Real LLM smoke re-baseline gate`.
- Plan accepted checkpoint: `4fd5b5b`.
- Control sync checkpoint: `6b649a9`.
- Plan artifact: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`.
- Controller judgment: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-controller-judgment-20260604.md`.
- Allowed write path: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`.
- Allowed runtime output path: local ignored `reports/llm-runs/` retained artifact only if the reviewed smoke reaches incomplete/fail-closed path.
- Scope boundary: evidence collection only; no feature implementation, review, commit, push, PR, provider default/runtime/budget change, Agent runtime, multi-year runtime, score-loop, golden/readiness, strict correctness rerun or release readiness.

## 2. Required Context Read

Read before evidence execution:

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/design.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-controller-judgment-20260604.md`

Key current facts confirmed:

- Current gate next entry is evidence execution with secret-safe preflight, local safety validation, then exactly one reviewed live smoke command only if safe.
- Current `--use-llm` path is explicit opt-in provider-backed fail-closed execution; incomplete/blocked runs must not fall back to deterministic markdown and must not print partial reports to stdout.
- Provider/runtime defaults, public chapter ids `0-7`, quality gate semantics, deterministic default `analyze/checklist`, Agent runtime, multi-year runtime, score-loop, golden/readiness and release/PR state are not in scope.
- Production annual-report access must continue through `FundDocumentRepository`; Service/UI/Host/renderer/quality gate must not call PDF cache, source helpers or download helpers directly.

## 3. Pre Git Integrity

- Command: `git branch --show-current`
  - Exit code: `0`
  - Result: `feat/mvp-llm-incomplete-run-artifacts`
- Command: `git status --short`
  - Exit code: `0`
  - Safe summary: pre-existing untracked files only; no tracked modifications.
  - Pre-existing untracked entries observed:
    - `docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-ds-20260603.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-mimo-20260603.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md`
    - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md`
    - `docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md`
    - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md`
    - `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
    - `docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md`
    - `docs/reviews/repo-review-20260526-231040.md`
    - `docs/reviews/repo-review-20260527-215953.md`
    - `docs/reviews/repo-review-20260527-225303.md`
    - `docs/reviews/workspace-ownership-reconciliation-20260531.md`
    - `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md`
    - `docs/tmux-agent-memory-store.md`
    - `reports/manual-llm-smoke/`
    - `reviews/`
    - `定性分析模板.md`
- Command: `git diff --name-only`
  - Exit code: `0`
  - Result: empty.

## 4. Secret-safe Env/Config Presence Preflight

Command run:

```bash
uv run python -c '<presence-only env preflight>'
```

Exit code: `0`.

Presence-only results:

| Field | Result |
|---|---|
| `FUND_AGENT_LLM_PROVIDER` present | `false` |
| `FUND_AGENT_LLM_MODEL` present | `false` |
| `FUND_AGENT_LLM_BASE_URL` present | `false` |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` override present | `false` |
| API key env var name checked | `FUND_AGENT_LLM_API_KEY` |
| API key present | `false` |
| Required env/config all present | `false` |

Optional runtime env explicitly set:

| Env var | explicitly_set |
|---|---|
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` | `false` |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | `false` |

Secret-safe statement:

- No API key value was printed.
- No base URL value was printed.
- No Authorization header, raw config dump, shell environment dump, raw prompt, draft, raw provider response, raw audit response or request headers were printed.
- No endpoint reachability check, HTTP request or provider call was performed.

Preflight classification: `environment_blocked`.

Stop reason: required LLM provider/model/base-url/key presence is absent. Per handoff and controller stop conditions, evidence execution stopped after Step 1. Local non-live validation and live smoke were not run.

## 5. Local Non-live Safety Validation

Not run due to Step 1 `environment_blocked` stop condition.

Planned commands explicitly not run:

1. `uv run pytest tests/services/test_llm_run_artifacts.py -q`
2. `uv run pytest tests/ui/test_cli.py -q`
3. `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q`
4. `uv run pytest tests/services/test_chapter_orchestrator.py -q`
5. `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q`
6. `uv run pytest tests/services/test_llm_provider.py -q`

Local validation result: `not_run_environment_blocked`.

## 6. Exactly-one Reviewed Live Smoke

Reviewed command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Execution status: not run.

Reason: Step 1 preflight classified this run as `environment_blocked`; running live smoke without required env/config presence would violate the accepted plan and controller stop conditions.

Smoke result:

- Live smoke run: `false`
- Exit code: not applicable.
- Stdout status: not applicable; no live command stdout was produced.
- Stderr safe summary: not applicable.
- Retained artifact path: none; no `reports/llm-runs/` artifact was produced by this evidence step.
- Orchestration status: not evaluated.
- Final assembly status: not evaluated.
- Per-chapter matrix: not evaluated.
- Failure category/subcategory: `environment_blocked` before live execution.
- Deterministic fallback: not run; no fallback command was executed.

## 7. Secret / Redaction Scan

Classification: `PASS` for this evidence artifact; no retained runtime artifact exists for this evidence step.

Scan scope:

- This evidence artifact.
- Retained artifact summaries: none, because live smoke was not run and no retained `reports/llm-runs/` artifact was produced by this evidence step.

Scan command:

```bash
uv run python -c '<secret/redaction scan over evidence artifact>'
```

Exit code: `0`.

Safe scan summary:

| Check | Result |
|---|---|
| `sk-` secret-like value | `false` |
| Authorization header value-like line | `false` |
| Bearer token value-like string | `false` |
| API key assignment value-like field | `false` |
| Configured key env var value present | `false` |
| Base URL value-like string | `false` |
| Raw prompt / raw provider response / raw audit response / message body / full request headers value detected | `false` |
| Blocking secret or raw payload value hit | `false` |

Policy-term note: terms such as raw prompt, raw provider response, raw audit response, message body and full request headers appear only as forbidden-scope / scan checklist labels in this artifact. No raw payload body or secret value was present.

## 8. A1-A9 Acceptance Criteria Mapping

| Criterion | Status | Evidence / reason |
|---|---|---|
| A1. Plan scope and forbidden-scope safety | `PASS` | Evidence execution stayed within specialist scope and did not modify source/test/config/runtime behavior. |
| A2. Env/config presence preflight is secret-safe | `BLOCKER` | Presence-only preflight was secret-safe, but required provider/model/base-url/key presence is absent; classified `environment_blocked`. |
| A3. Reviewed real-smoke command is singular and scoped | `BLOCKER` | Live smoke was correctly not run because A2 blocked. No alternate live command or probe was run. |
| A4. Incomplete fail-closed and stdout safety | `BLOCKER` | Not evaluated because live smoke was not run after A2 hard stop. |
| A5. Accepted report safety if smoke succeeds | `BLOCKER` | Not evaluated because live smoke was not run after A2 hard stop. |
| A6. Safe diagnostic matrix and no secret leakage | `BLOCKER` | Runtime matrix not available because live smoke was not run; artifact redaction scan passed with no blocking secret/raw payload value hit. |
| A7. Direct evidence integrity | `PASS` | Pre/post git branch/status/diff recorded. |
| A8. Provider timeout/block classification preserves current semantics | `BLOCKER` | Not evaluated because provider smoke was not run; no runtime/default/budget changes were made. |
| A9. Boundary guardrails | `PASS` | No Dayu runtime dependency, Agent runtime, multi-year runtime, direct PDF/cache/source-helper read, `extra_payload` business parameter, public id, provider default, quality gate, golden/readiness, external state, PR/push/release or deterministic fallback action was introduced. |

Single blocking finding: `B1 environment_blocked` caused A2 and all live-smoke-dependent criteria to remain blocked/not evaluable.

## 9. A8/A9 Forbidden-scope Checklist

| Forbidden scope | Result |
|---|---|
| No provider default/runtime/budget change | `PASS` |
| No timeout/attempt/backoff/model/endpoint/provider/max-output/repair-budget override | `PASS` |
| No Agent runtime implementation | `PASS` |
| No multi-year runtime | `PASS` |
| No score-loop | `PASS` |
| No golden/readiness | `PASS` |
| No snapshot refresh | `PASS` |
| No strict correctness rerun | `PASS` |
| No release readiness | `PASS` |
| No PR/push/release | `PASS` |
| No external state command | `PASS` |
| No dayu runtime dependency | `PASS` |
| No direct PDF/cache/source helper read | `PASS` |
| Production annual-report access only through `FundDocumentRepository` | `PASS` (no production annual-report access occurred) |
| No `extra_payload` business params | `PASS` |
| Public chapter ids remain `0-7` | `PASS` |
| No auditor/quality gate/fail-closed relaxation | `PASS` |
| No deterministic fallback on incomplete | `PASS` (no live execution occurred) |
| No partial report to stdout | `PASS` (no live execution occurred) |

## 10. Blocking Findings And Residual Owners

Blocking findings count: `1`.

| ID | Classification | Finding | Owner |
|---|---|---|---|
| B1 | `environment_blocked` | Required LLM env/config presence is absent: provider/model/base-url/key are not present. | Controller / environment owner |

Residuals:

- No provider runtime residual was observed because live smoke was not run.
- No content contract residual was observed because live smoke was not run.
- No code contract blocker was observed in this evidence step.
- No secret redaction blocker was observed.

## 11. Post Git Integrity

- Command: `git branch --show-current`
  - Exit code: `0`
  - Result: `feat/mvp-llm-incomplete-run-artifacts`
- Command: `git status --short`
  - Exit code: `0`
  - Safe summary: post status contains the newly added allowed evidence artifact plus the same pre-existing unrelated untracked entries recorded in pre-git integrity.
  - Newly added allowed path:
    - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`
  - Runtime retained artifact from this evidence step: none.
- Command: `git diff --name-only`
  - Exit code: `0`
  - Result: empty. No tracked source/test/config/runtime/design/control/startup diff exists.

Allowed-write conclusion:

- This evidence step wrote only `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`.
- It produced no new `reports/llm-runs/` retained artifact because live smoke was not run.
- It did not modify `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, plan/review/controller artifacts, source, test, config or runtime behavior.
