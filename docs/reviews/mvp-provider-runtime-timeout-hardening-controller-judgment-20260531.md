# MVP provider runtime timeout hardening controller judgment

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening gate`

角色：phaseflow controller，不是 implementation worker。

## Judgment

**Accepted locally as timeout-hardening implementation; real-provider smoke remains blocked.**

本 gate 的 provider runtime timeout hardening 已本地接受：实现、测试、review 和 controller 复跑证明 `--use-llm` 路径现在可以对 provider timeout 做有界重试、保留脱敏诊断，并在未完成时 fail-closed 到首个失败章节摘要。它没有让 `006597 / 2024` 生成完整 0-7 章，因此不能标记 real-provider smoke accepted。

当前最小 blocker：`MVP real provider smoke acceptance gate` 仍 blocked。最新 controller CLI 复跑为 `provider_runtime / llm_timeout`；补充 service-level 复跑观察到第 1 章 `llm_contract_violation`。这两个都不是 provider config/auth 问题，下一最小入口应回到 writer prompt/contract calibration 或 provider timeout budget tuning，不能回退到 deterministic fallback。

## Evidence

| Evidence | Result |
|---|---|
| Plan | `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md` |
| Plan judgment | `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-controller-judgment-20260531.md` |
| Implementation evidence | `docs/reviews/mvp-provider-runtime-timeout-hardening-implementation-evidence-20260531.md` |
| Code review GLM | `docs/reviews/mvp-provider-runtime-timeout-hardening-code-review-glm-20260531.md` — PASS |
| Code re-review MiMo | `docs/reviews/mvp-provider-runtime-timeout-hardening-code-rereview-mimo-20260531.md` — PASS |
| Initial MiMo review | `docs/reviews/mvp-provider-runtime-timeout-hardening-code-review-mimo-20260531.md` — scope finding superseded after controller clarified pre-existing Gate A/control dirty worktree |
| Controller real provider CLI stdout | `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.stdout` — empty |
| Controller real provider CLI stderr | `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.stderr` — safe first failed summary |
| Controller real provider exit code | `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.exitcode` — `1` |
| Controller diagnostic JSON | `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024-diagnostic.json` |

Controller CLI stderr summary:

```text
LLM 分析未完成：orchestration_status=blocked, final_assembly_status=incomplete, ..., first_failed_chapter_id=1, first_failed_status=failed, first_failed_stop_reason=llm_timeout
```

补充 service-level rerun（未保存 prompt、draft 或 provider body）观察：

```text
orchestration_status=blocked
final_assembly_status=incomplete
chapter 1 status=blocked stop_reason=llm_contract_violation attempt_count=1
chapter 2-6 status=skipped stop_reason=dependency_missing
```

## Validation Matrix

| Validation | Result |
|---|---|
| `uv run ruff check .` | PASS per implementation evidence and MiMo re-review |
| Targeted pytest for config/provider/orchestrator/service/CLI | PASS, `157 passed` per implementation evidence and MiMo re-review |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1151 passed`, coverage `91.82%` per implementation evidence |
| Missing-config `--use-llm` smoke | PASS, exit `1`, stdout empty, fail-closed before Service |
| Deterministic `analyze 006597 / 2024` smoke | PASS, exit `0` |
| Deterministic `checklist 006597 / 2024` smoke | PASS, exit `0` |
| Controller real provider `006597 / 2024 --use-llm` smoke | FAIL-CLOSED, exit `1`, no deterministic fallback, first failed chapter classified as `llm_timeout` |
| Secret leak check | PASS for new gate artifacts by inspection; no API key, Authorization header, full provider response, prompt or draft stored |

## Review Finding Disposition

| Finding | Disposition |
|---|---|
| MiMo B-1/B-2/B-3 initial scope violations | Superseded. Findings described pre-existing Gate A/control-doc dirty worktree, not provider-timeout allowed-file implementation. Controller requested re-review with explicit scope. |
| MiMo re-review | Accepted PASS. Allowed-file implementation has no blocking finding. |
| GLM F1 orchestrator sanitizer list shorter than provider sanitizer | Non-blocking residual. Current diagnostic paths do not leak prompt/draft/body; future shared sanitizer extraction may consolidate lists. |
| GLM F2 string-based exception type mapping | Accepted as deliberate boundary tradeoff. It avoids orchestrator importing provider exception classes and remains fail-closed on unknown subclasses. |
| GLM F3 run-level vs attempt-level diagnostic placement | Accepted as current data model. Downstream must inspect both `ChapterRunResult.runtime_diagnostics` and attempt diagnostics. |

## Accepted Implementation Facts

- `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` is typed config with default `2` and bounds `1..3`.
- `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` is typed config with default `1.0` and bounds `0..30`.
- Provider timeout is the only retryable provider runtime condition.
- Rate limit, malformed response, network errors and non-2xx HTTP errors do not retry.
- Provider diagnostics are provider-local and secret-safe; Service orchestrator enriches them with chapter identity.
- Fund writer/auditor Protocol request/response contracts are not extended by provider diagnostics.
- CLI incomplete LLM result prints only safe orchestration/final assembly status plus first failed chapter id/status/stop reason.
- Default deterministic `analyze` and `checklist` behavior remains unchanged.

## Blocker And Next Entry

`MVP real provider smoke acceptance gate` remains **blocked**:

- Required acceptance was complete `0-7` chapters with evidence anchors and chapter audit status.
- Actual controller smoke still exits `1`, stdout empty, final assembly incomplete.
- Failure is now precise enough to continue: `provider_runtime / llm_timeout` in CLI rerun, with additional `prompt_contract / llm_contract_violation` observed in service-level rerun.

Next smallest gate:

`MVP real provider smoke acceptance rerun with prompt-contract calibration`

Minimum entry criteria:

1. Use current timeout hardening; do not revisit provider auth/config unless env loading itself fails.
2. Rerun `fund-analysis analyze 006597 --report-year 2024 --use-llm` once and capture safe summaries.
3. If first failed stop reason is `llm_contract_violation`, inspect writer parser category and prompt/required marker mismatch without storing full draft.
4. If first failed stop reason is `llm_timeout`, decide whether to tune typed timeout budget within current bounds or create a provider runtime budget gate.
5. Do not relax evidence, ITEM_RULE, candidate facet, transaction advice or E2 deferred safety boundaries.

## External State

No push, PR update, merge, release, mark-ready, request-reviewer or external state mutation was performed.
