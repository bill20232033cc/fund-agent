# MVP provider runtime timeout follow-up controller judgment

日期：2026-05-31

角色：Gateflow controller，不是 implementation worker。

## Verdict

**Blocked with precise next entry.**

本 gate 的代码与诊断能力本地接受；真实 provider smoke 仍未 accepted。当前最小 blocker 不再是 provider config/auth，也不应通过继续拉长 timeout 解决。证据显示：

- 默认 60s x2 provider 预算下，service-level safe diagnostic 可复现 chapter 1 auditor `llm_timeout`。
- Bounded 120s x2 provider 预算下，CLI 和 service-level safe diagnostic 均越过 timeout，失败转为 chapter 1 auditor `audit_rule_too_strict` / `repair_budget_exhausted`。
- 两个真实 provider CLI smoke 都 exit `1`、stdout empty、final assembly incomplete、无 deterministic fallback。

下一最小 gate：`MVP chapter 1 auditor rule calibration gate`，聚焦区分当前 `audit_rule_too_strict` 是 LLM audit 规则过严、auditor prompt/protocol 校准不足，还是 writer 输出真实不合格。不得放松证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics 或 L1/C2 安全边界。

## Source Artifacts

- Plan: `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- Plan reviews: `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-glm-20260531.md`
- Plan re-reviews: `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-rereview-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-rereview-glm-20260531.md`
- Implementation evidence: `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md`
- Code reviews: `docs/reviews/mvp-provider-runtime-timeout-follow-up-code-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-timeout-follow-up-code-review-glm-20260531.md`
- Smoke evidence directory: `reports/mvp-local-acceptance/20260531-provider-runtime-timeout-follow-up/`

## Accepted Local Implementation

- Provider runtime diagnostics now include safe prompt/runtime cost scalar fields:
  - `system_prompt_chars`
  - `user_prompt_chars`
  - `approx_prompt_tokens`
  - `allowed_fact_count`
  - `allowed_anchor_count`
  - `max_output_chars`
- `serialize_chapter_runtime_diagnostics()` emits only allowlisted scalar fields and intentionally omits `message`, `model_name`, prompt text, draft text, raw provider response and raw audit response.
- CLI incomplete `--use-llm` stderr now includes first failed runtime summary:
  - operation
  - observed/max provider attempts
  - provider runtime category
  - max elapsed ms
  - prompt chars
  - approximate prompt tokens
- Timeout retry remains timeout-only and bounded; non-timeout provider errors are not retried.
- Default deterministic `analyze` and `checklist` behavior remains unchanged.

## Reviews

MiMo code review verdict: **PASS**.

GLM code review verdict: **PASS**.

Residuals were non-blocking:

- `ChapterLLMRuntimeDiagnostic` still has `message` / `model_name` fields, but serializer and CLI do not output them.
- Provider and orchestrator each have a local `_sanitize_text()` helper; current allowlist prevents leakage.
- A cosmetic dictionary indentation issue was noted; tests and ruff pass.
- Real provider smoke remained controller responsibility and was run after review.

## Validation

| Check | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1189 passed`, coverage `91.88%` |
| Targeted provider/orchestrator/CLI tests | PASS, `143 passed` |
| Deterministic `fund-analysis analyze 006597 --report-year 2024` | PASS, exit `0` |
| Deterministic `fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0` |
| Missing config `--use-llm` smoke | PASS fail-closed, exit `1`, stdout empty, stderr `missing FUND_AGENT_LLM_PROVIDER` |
| Real provider default `006597 / 2024 --use-llm` CLI | FAIL-CLOSED, exit `1`, stdout empty, no fallback |
| Real provider bounded `120s x2` CLI | FAIL-CLOSED, exit `1`, stdout empty, no fallback |
| Secret leak scan over gate reports/reviews/control paths | PASS, no API key / Authorization header / bearer token / raw prompt assignment pattern found |

## Real Provider Evidence

### Default Provider Budget

CLI evidence:

- `real-provider-default.exitcode`: `1`
- `real-provider-default.stdout`: `0` bytes
- `real-provider-default.stderr`: safe incomplete summary only
- First failed CLI summary in that run:
  - chapter `1`
  - status `failed`
  - stop reason `repair_budget_exhausted`
  - category `audit_rule_too_strict`
  - runtime operation `auditor`
  - provider attempts unknown in CLI summary because this path was not a provider exception

Service safe diagnostic in a separate default-budget run:

- `real-provider-default-safe-diagnostics.json`
- final assembly: `incomplete`
- report present: `false`
- first failed:
  - chapter `1`
  - category `llm_timeout`
  - operation `auditor`
  - provider runtime categories: `["timeout"]`
  - provider attempts: `2/2`
  - elapsed per attempt: about `60003 ms` and `60029 ms`
  - system prompt chars: `54`
  - user prompt chars: `3270`
  - approximate prompt tokens: `831`
  - allowed facts: `5`
  - allowed anchors: `13`

Controller interpretation: default provider budget can still timeout at chapter 1 auditor, and now the timeout location and prompt/runtime cost are safely observable.

### Bounded Provider Budget

Bounded validation env:

- `FUND_AGENT_LLM_TIMEOUT_SECONDS=120`
- `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=2`
- `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=2`

CLI evidence:

- `real-provider-bounded-120x2.exitcode`: `1`
- `real-provider-bounded-120x2.stdout`: `0` bytes
- `real-provider-bounded-120x2.stderr`: safe incomplete summary only
- First failed CLI summary:
  - chapter `1`
  - status `failed`
  - stop reason `repair_budget_exhausted`
  - category `audit_rule_too_strict`
  - subcategory `unknown`
  - runtime operation `auditor`

Service safe diagnostic:

- `real-provider-bounded-120x2-safe-diagnostics.json`
- final assembly: `incomplete`
- report present: `false`
- first failed:
  - chapter `1`
  - category `audit_rule_too_strict`
  - status `failed`
  - stop reason `repair_budget_exhausted`
  - operation `auditor`
  - attempt count `2`
  - runtime diagnostics have `finish_reason=stop`
  - response chars: `151` and `255`
  - provider timeout categories: none
- chapters `2-6` skipped due to dependency after chapter 1 failed.

Controller interpretation: bounded runtime budget moves the primary observed blocker from transport timeout to auditor rule calibration. Continuing to increase timeout would mask the real next issue and make smoke runs expensive without producing accepted chapters.

## Safety Decision

No pass was claimed for the real provider smoke. The report was not generated, chapters `0-7` were not accepted, and stdout stayed empty for both provider runs.

The current `audit_rule_too_strict` classification is a fail-closed category, not an acceptance override. The next gate must calibrate the chapter 1 auditor behavior with secret-safe issue taxonomy and same-source evidence. It must not weaken:

- evidence anchor requirements
- ITEM_RULE enforcement
- candidate facet non-assertion rules
- trade recommendation bans
- E2 deferred handling
- missing semantics
- L1/C2 safety boundaries

## Next Entry

Start `MVP chapter 1 auditor rule calibration gate`.

Minimum goal:

1. Add safe auditor failure diagnostics that expose issue ids / rule codes / severity counts and repair hints without raw audit response or draft text.
2. Determine whether chapter 1 `audit_rule_too_strict` is:
   - `audit_rule_too_strict` true false positive,
   - `audit_parse`,
   - `prompt_contract`,
   - `fact_gap`,
   - `code_bug`, or
   - writer output genuinely non-compliant.
3. If and only if same-source evidence shows auditor rule overreach, calibrate the auditor prompt/parser or rule mapping without weakening safety boundaries.
4. Rerun real provider smoke for `006597 / 2024 --use-llm` under bounded provider settings before any acceptance claim.
