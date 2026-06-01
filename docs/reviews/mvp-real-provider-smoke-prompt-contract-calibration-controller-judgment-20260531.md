# MVP real provider smoke prompt-contract calibration controller judgment

日期：2026-05-31

Gate：`MVP real provider smoke acceptance rerun with prompt-contract calibration`

角色：Gateflow controller，不是 implementation worker。

## Judgment

**Implementation accepted locally; real-provider smoke acceptance remains blocked.**

本 gate 已完成 plan / review / plan fix / re-review / implementation / code review / controller rerun。实现本身通过两份 code review，无 blocking findings。真实 provider 路径比上一 gate 更接近可接受报告：controller service-level rerun 中第 1 章 accepted，编排状态从 blocked 改为 partial；但完整 0-7 章仍未生成，最终总装仍 incomplete。

主 blocker：`prompt_contract`。

定位：真实 provider writer 输出仍触发 `llm_contract_violation`。controller CLI rerun 的 first failed 是 chapter 1 / writer contract；controller service-level diagnostic rerun 的 chapter 1 accepted，但 chapter 2 blocked with `llm_contract_violation` / `prompt_contract`。两次 rerun 共同说明 provider/auth 与 timeout 已不是主阻断，剩余阻断集中在真实模型 writer 输出未稳定满足 required marker / anchor / missing / candidate facet / length contract。

下一最小入口：

`MVP writer prompt contract diagnostic narrowing gate`

该入口应只做 secret-safe writer contract failure diagnostics：不保存完整 prompt、完整 draft 或 provider response，只记录失败子类（missing marker、unknown anchor、candidate facet assertion、response length/incomplete、forbidden phrase 等）和最小 prompt/parser 修正入口。

## Evidence

| Evidence | Result |
|---|---|
| Plan | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md` |
| Plan fix | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-fix-20260531.md` |
| Plan reviews | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-review-glm-20260531.md` |
| Plan re-review | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-rereview-glm-20260531.md` |
| Plan controller judgment | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-controller-judgment-20260531.md` |
| Implementation evidence | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md` |
| Code reviews | `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-code-review-glm-20260531.md` |
| Controller CLI smoke stdout | `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024.stdout` — empty |
| Controller CLI smoke stderr | `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024.stderr` |
| Controller CLI smoke exit code | `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024.exitcode` — `1` |
| Controller service diagnostic | `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024-diagnostic.json` |

## Validation

| Validation | Result |
|---|---|
| `uv run ruff check .` | PASS, per implementation evidence and MiMo code review |
| Targeted pytest writer/auditor/orchestrator/provider/CLI | PASS, `170 passed`, per implementation evidence and MiMo code review |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1154 passed`, coverage `91.80%` |
| deterministic analyze `006597 / 2024` | PASS, exit `0` |
| deterministic checklist `006597 / 2024` | PASS, exit `0` |
| missing-config `--use-llm` | PASS, exit `1`, stdout empty |
| controller real provider CLI smoke | FAIL-CLOSED, exit `1`, stdout empty, no deterministic fallback, first failed category `prompt_contract` |
| controller real provider service diagnostic | FAIL-CLOSED, orchestration `partial`, chapter 1 accepted, chapter 2 blocked `prompt_contract` |
| secret leak scan | PASS; no API key, Authorization header, full prompt, full draft or full provider response found in new controller artifacts |

## Controller Smoke Summary

CLI rerun:

```text
exit_code=1
stdout_bytes=0
first_failed_chapter_id=1
first_failed_status=blocked
first_failed_stop_reason=llm_contract_violation
first_failed_category=prompt_contract
```

Service-level diagnostic rerun:

| Chapter | Status | Stop reason | Category | Attempt count |
|---|---|---|---|---|
| 1 | accepted | none | none | 1 |
| 2 | blocked | llm_contract_violation | prompt_contract | 1 |
| 3 | skipped | dependency_missing | fact_gap | 0 |
| 4 | skipped | dependency_missing | fact_gap | 0 |
| 5 | skipped | dependency_missing | fact_gap | 0 |
| 6 | skipped | dependency_missing | fact_gap | 0 |

The two controller reruns are different live-provider attempts and should not be merged as a single run. The common, actionable blocker is writer `prompt_contract`.

## Review Finding Disposition

| Finding | Decision |
|---|---|
| MiMo code review F1/F2 evidence mismatch from implementation worker env absence | accepted as evidence-clarity residual; controller smoke evidence supersedes implementation-worker skipped-env evidence |
| MiMo F3 parse failure issue id coupling | deferred to future auditor refactor if issue ids change |
| MiMo F4 duplicated sanitizer helpers | deferred; current secret hygiene evidence is clean |
| GLM N1 controller evidence inconsistency | accepted as live-provider rerun variability; judgment explicitly distinguishes CLI rerun and service diagnostic rerun |
| GLM N2 sanitizer redacts `prompt` broadly | deferred to future sanitizer cleanup |
| GLM N3 fact-gap heuristic | deferred to future typed audit issue category gate |

None of the non-blocking findings requires a fix before this gate judgment.

## Accepted Implementation Facts

- Writer prompt is front-loaded with a shorter output contract and explicit marker syntax.
- Auditor parser now requires exactly three line-protocol fields for non-pass lines.
- Parse failure remains fail-closed and maps to `audit_parse`.
- Repair/regenerate remains bounded and carries sanitized previous issue context.
- `ChapterFailureCategory` now includes `llm_timeout` and `audit_rule_too_strict`.
- `ChapterRunResult.failure_category` is populated and used by CLI `first_failed_category`.
- CLI incomplete LLM path still emits stderr only and does not deterministic-fallback.
- Default deterministic analyze/checklist behavior is unchanged.

## Acceptance Decision

Pass criteria were not met:

- No complete 0-7 chapter report was generated.
- Final assembly remains incomplete.
- Real provider smoke still exits `1`.

Blocked criteria are met:

- Provider config/auth is not the blocker.
- Timeout is not the current main blocker.
- Failure is classified as `prompt_contract`.
- Chapter/phase are localized to writer output contract: chapter 1 in one CLI rerun, chapter 2 in service diagnostic rerun.
- Next smallest entry is identified.

## Next Minimal Gate

`MVP writer prompt contract diagnostic narrowing gate`

Minimum scope:

1. Rerun real provider with current code once.
2. Without storing full prompt/draft/provider response, extract only writer blocked issue ids / stop reason / marker-category counters.
3. Classify prompt contract failure into one unique subcategory: missing structure, missing required marker, unknown anchor, invalid marker, candidate facet assertion, forbidden phrase, response length/incomplete, or other code bug.
4. If subcategory is stable and fixable, plan the smallest writer prompt/parser correction.
5. Preserve evidence, ITEM_RULE, candidate facet, transaction advice, E2 deferred, missing semantics and no-fallback safety boundaries.

## External State

No push, PR update, merge, release, mark-ready, reviewer request, external comment or external state change was performed.
