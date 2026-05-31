# MVP real provider smoke prompt-contract calibration plan fix

日期：2026-05-31

角色：Gateflow planning specialist。本文是同一 planning task 的 plan-fix artifact，只记录 controller finding decisions 的文档修正；未进入 implementation，未修改运行时代码，未 commit、push、PR 或 release。

## 1. Self-check

- Current gate / role：当前仍是 `MVP real provider smoke acceptance rerun with prompt-contract calibration` 的 planning handoff；我是 planning worker，不是 controller、implementation worker 或 reviewer。
- Source of truth：依据用户提供的 controller finding decisions 修正 `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`。
- Scope boundary：只修改原 plan artifact，并新增本文 plan-fix artifact。
- Prohibited actions：未改 runtime code、tests、control docs、golden、fixtures、score、quality gate、Host/Agent/dayu、PR 状态。
- Handoff status：原 plan 已按 accepted findings 修正，仍为 handoff-ready。

## 2. Finding disposition

| Finding | Controller decision | Fix applied |
|---|---|---|
| GLM F1 | accepted | 原 plan Section 7.4 明确选择方案 A：`llm_timeout` 是代码级独立 `ChapterFailureCategory` 成员；timeout provider diagnostics / exception category 返回 `llm_timeout`；rate limit / malformed / network / http_error 仍归 `provider_runtime`；smoke/CLI 优先显示 `first_failed_category=llm_timeout`。 |
| GLM F2 | accepted with amendment | 原 plan Section 7.4 / Slice D 明确选择方案 A：`ChapterRunResult` 增加可选 `failure_category` 字段，由 writer blocked、audit blocked/failed、exception/result construction 等路径填入；CLI 从 `ChapterRunResult.failure_category` 直接输出，不遍历 attempts/runtime diagnostics/provider diagnostics；stdout 继续 empty/no fallback。 |
| GLM F3 | accepted | 原 plan Section 7.4 明确 `audit_rule_too_strict` 条件：programmatic audit accepted/pass；LLM audit 是可解析 fail/blocked/reviewable issue；无 `llm:parse_failure`；无 `needs_more_facts` 或 fact-gap issue。programmatic fail 仍按 `prompt_contract` / `fact_gap`，不被 LLM 覆盖；taxonomy 要求加入 Literal。 |
| GLM F4 | accepted | 原 plan Section 7.2 item 10 已从错误引用 7.5 改为引用 7.4 taxonomy。 |
| MiMo F1 | accepted | 原 plan Section 7.1 expected writer failure categories 已补充 `llm_empty_response` -> `prompt_contract`。 |
| MiMo F2 | accepted | 原 plan Section 7.4 明确 taxonomy 是代码级 `ChapterFailureCategory` 扩展，不是仅 evidence/reporting 层；新增 Literal 值至少包含 `llm_timeout` 和 `audit_rule_too_strict`。 |

## 3. Updated implementation requirements

Implementation worker 必须按修正后的原 plan 执行以下硬要求：

- `ChapterFailureCategory` Literal 至少新增 `llm_timeout` 和 `audit_rule_too_strict`。
- `llm_timeout` 不再归入泛化 `provider_runtime` category；timeout stop reason、provider diagnostic enrichment、exception result construction 和 smoke evidence 都优先输出 `llm_timeout`。
- 非 timeout provider failures 仍归 `provider_runtime`，包括 rate limit、malformed response、network、HTTP error 和已知 provider runtime 非 timeout。
- `ChapterRunResult.failure_category` 是 CLI `first_failed_category` 的唯一读取来源。
- CLI 不得遍历 nested diagnostics 来推导 category，不得输出 prompt、draft、provider response，不得 fallback 到 deterministic report。
- `audit_rule_too_strict` 只能在 programmatic pass 且 LLM audit 可解析失败时使用；任何 parse failure 都是 `audit_parse`，任何 programmatic fail 都不能被 LLM audit 覆盖。

## 4. Handoff readiness

Status：handoff-ready。

Blocking Questions For Controller：None。

Plan artifact updated：

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`

Plan-fix artifact:

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-fix-20260531.md`
