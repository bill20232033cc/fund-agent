# MVP LLM acceptance volatility and diagnostic evidence reconciliation design plan — DS review

## Reviewer Self-Check

- Role: AgentDS, independent plan reviewer only, not controller.
- Gate under review: `MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`.
- Classification: `heavy`.
- Actions not taken: no source, test, config, runtime, provider, or plan edits.
- Same-source evidence inspected: default retained run `c83e8c1adcc846a` summary.json + chapter-02.json; 120s retained run `4b7dddc60d084e7` summary.json + chapter-02.json. No writer/auditor markdown files opened.

## Same-Source Verification

Before reviewing the plan's claims, I independently verified the Ch2 attribution gap by comparing chapter-02.json across both retained runs:

Default run `c83e8c1adcc846a` chapter-02.json:
- `stop_reason=llm_timeout`, `failure_category=llm_timeout`
- `chapter_runtime_diagnostics` has two rows, both with `provider_runtime_category=timeout`, `timeout_seconds=60.0`, `timeout_budget_kind=auditor`, `error_type=ReadTimeout`, `approx_prompt_tokens=758`
- Attempts array has `attempt_index=0` with matching timeout runtime_diagnostics rows; no repair_decision
- **Consistent**: terminal classification matches serialized diagnostics

120s run `4b7dddc60d084e7` chapter-02.json:
- `stop_reason=llm_timeout`, `failure_category=llm_timeout`
- `issues`: contains `LLMProviderTimeoutError`
- `chapter_runtime_diagnostics` has ONE row: `finish_reason=stop`, `response_chars=22`, `chapter_failure_category=prompt_contract`, NO timeout scalars (no `timeout_seconds`, `timeout_budget_kind`, `provider_runtime_category`, `error_type`)
- Attempts array has `attempt_index=0` with `repair_decision.action=regenerate` on `programmatic:L1`, same non-timeout runtime diagnostic row
- `attempt_count=1` — the regenerate step's auditor call timed out before it could be recorded as attempt_index=1
- **Inconsistent**: terminal `llm_timeout` classification exists, but serialized runtime diagnostics contain only prior audit repair state, no timeout scalar

The plan's claim of a diagnostic attribution gap is **same-source confirmed**. The gap is real: the 120s artifact simultaneously reports chapter-level `llm_timeout` and auditor `finish_reason=stop` with `chapter_failure_category=prompt_contract` at the diagnostic row level.

## Findings

### Finding 1 — NON-BLOCKING: 全量回归测试未列入 completion evidence

**Severity**: non-blocking

当前 plan 的 validation commands 只跑两个 service test 文件加 CLI `llm and diagnostic` 过滤：

```
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py
uv run pytest tests/ui/test_cli.py -k "llm and diagnostic"
```

`heavy` gate 修改 retained artifact serializer 的公共 schema（新增 `diagnostic_consistency_status` 等字段），应该跑全量 pytest 确保没有意外 regress 其他 serializer consumer（如 CLI summary 输出、manifest、已有 artifact 兼容性）。

**建议**: completion evidence 增加 `uv run pytest` 全量回归，或至少说明为什么全量不必要。

### Finding 2 — NON-BLOCKING: `attempts[]` 层级的 runtime diagnostic lineage 未被 plan 覆盖

**Severity**: non-blocking

Plan 聚焦在 `chapter_runtime_diagnostics`（即 summary.json 的 `runtime_diagnostics.chapter_runtime_matrix` 和 chapter JSON 顶层的 `chapter_runtime_diagnostics`），但 chapter JSON 内 `attempts[].runtime_diagnostics` 同样存在 lineage 问题——120s run 的 Ch2 attempt 0 的 `runtime_diagnostics` 里的 auditor row 也是 `finish_reason=stop` / `chapter_failure_category=prompt_contract`，没有 timeout scalar。

如果 Slice 1 只修 `chapter_runtime_diagnostics` 层级而不处理 `attempts[].runtime_diagnostics`，attribution gap 会在 attempt 级别残留，未来按 attempt 查询证据的人仍会看到不一致。

**建议**: plan 应明确 `diagnostic_consistency_status` 是否同时应用于 `attempts[].runtime_diagnostics`，或说明为何 attempt 级别不需要。

### Finding 3 — NON-BLOCKING: `_first_failed_runtime_diagnostic()` 匹配逻辑变更的 CLI 回归未显式要求

**Severity**: non-blocking

Plan 第 3 点说 `_first_failed_runtime_diagnostic()` 在 `stop_reason=llm_timeout` 时应 prefer `provider_runtime_category=timeout` 或 `timeout_budget_kind != None` 的 row，不再 blindly 取第一条。这个变更会影响 summary.json 的 `first_failed` 字段和 CLI stderr 的 first failed chapter 输出。

Expected tests 包含了 `diagnostic_consistency_status` 的几个场景，但没有显式要求 CLI first-failed 输出的 before/after 对比——比如 default run 的 Ch2 first-failed 是否仍然正确显示 auditor timeout scalars，120s run 的 first-failed 是否从 Ch1 `audit_rule_too_strict` 保持不变（因为 consistent timeout row 不存在，不应强行把 Ch2 提升为 first-failed 并附上不存在的 timeout scalars）。

**建议**: Expected tests 增加一条：default retained run 的 Ch2 first-failed 序列化后 `timeout_budget_kind=auditor` 和 `provider_attempt_count=2` 保持不变；120s run 的 Ch1 first-failed 不因匹配逻辑改变而被错误替换。

### Finding 4 — NON-BLOCKING: Slice 4 `audit_focus` design gate 与已接受 future architecture 的边界需提前声明

**Severity**: non-blocking（不是当前 Slice 1 的实现问题，但影响 ordering 合理性）

Plan 把 Slice 4 `audit_focus` design gate 排在 volatility matrix（Slice 3）之后。已接受的 `MVP fund report template typed contract redesign gate` 已把 per-chapter `audit_focus` 作为 accepted future design，且明确 "per-chapter `audit_focus` for bounded semantic audit only"。Slice 4 如果重新设计 `audit_focus`，必须显式引用已接受的 template redesign gate 的 `audit_focus` 定义，不能独立重新发明语义或范围，否则会与已接受的 design-only future architecture 冲突。

**建议**: Slice 4 摘要里加一句 "must conform to the already-accepted `audit_focus` semantics in the template typed contract redesign gate"。

## Positive Confirmation（逐个对照 5 个 review focus）

### Focus 1: Ch2 attribution gap 同源证据充分性

**PASS**。我独立对比了两个 retained run 的 chapter-02.json，确认：
- default run 的 Ch2 runtime diagnostics 有两行完整 timeout scalar（`timeout_seconds=60.0`, `timeout_budget_kind=auditor`, `error_type=ReadTimeout`），与 `stop_reason=llm_timeout` 一致。
- 120s run 的 Ch2 runtime diagnostics 只有一行 auditor `finish_reason=stop` / `response_chars=22` / `chapter_failure_category=prompt_contract`，没有 timeout scalar，与顶层的 `stop_reason=llm_timeout` 矛盾。

Plan 将此标记为 "diagnostic attribution gap" 而非 "proven provider-budget root cause"，没有过度推断。推理链完整：同一个 retained chapter file 同时暴露 terminal timeout classification 和 non-timeout diagnostic row → serialization/lineage 必须先修才能跑更多 live probe。

### Focus 2: 正确阻止继续 provider timeout default tuning、PASS-only、split-audit、Ch3 implementation

**PASS**。

- Provider timeout default tuning: explicit non-goal + stop condition "Stop if implementation would change … provider default behavior"
- PASS-only: 放入 "Deferred Probes"，明确 "Do not run now"，且需要 controller-authorized evidence gate
- Split-audit: 排在 PASS-only 之后，"requires a separate design gate after `audit_focus` design"
- Ch3 implementation: "Do not start Ch3 calibration implementation until steps 1-4 have made runtime/audit/anchor volatility legible"

Ordering 合理：先修诊断基础设施，再做 provider endpoint disposition，然后 volatility matrix，最后才考虑 audit_focus 和 PASS-only。

### Focus 3: Ch1/Ch4 volatility、Ch5 writer timeout、Ch6 unknown_anchor 分类正确性

**PASS**。

| Chapter | Plan 分类 | 同源验证 |
|---|---|---|
| Ch1 | `audit_rule_too_strict` / acceptance volatility | ✅ 120s run Ch1 chapter JSON：`failure_category=audit_rule_too_strict`，issue class 指向 unsupported anchor/fact 和 `non_asserted_facet_boundary`，无 provider timeout 字段 |
| Ch4 | `audit_rule_too_strict` / acceptance volatility | ✅ 120s run summary matrix：`failure_category=audit_rule_too_strict`，无 provider runtime 字段 |
| Ch5 | writer endpoint/runtime evidence under unchanged writer budget | ✅ 120s run Ch5 runtime rows：`operation=writer`, `timeout_budget_kind=writer_initial`, `timeout_seconds=60.0`, `error_type=ReadTimeout`。Plan 明确分离 Ch5 writer timeout 和 Ch2 auditor budget |
| Ch6 | typed anchor/evidence contract (`unknown_anchor`)，非 provider runtime | ✅ 120s run Ch6：`stop_reason=unknown_anchor`, `failure_category=prompt_contract`, `failure_subcategory=unknown_anchor`, prompt diagnostic 显示 `writer:unknown_anchor=1`, `phase=writer_parse`。正确归入 prompt/anchor contract family |

Plan 对 volatility 的处理正确：记录为 evidence volatility 而不是 weaken blocker（"An accepted chapter in one live run does not invalidate a later fail-closed audit issue"）。

### Focus 4: 下一 gate 推荐 typed diagnostic serialization repair 的时机与范围

**PASS，附 Finding 1-3 的 non-blocking 意见**。

时机恰当：在 serialization 不可信的情况下跑更多 live provider probe 会产生误导性证据。先修 diagnostic contract 再跑 provider endpoint disposition 是正确顺序。

范围受控：
- Allowed files 只有 4 个文件（2 source + 2 test），不碰 provider、auditor、config、template、Host、Agent
- Non-goals 明确：no provider call, no timeout default change, no auditor rule change, no prompt/body/raw response persistence, no deterministic fallback
- 新增字段全是 scalar allowlisted values，无 prompt/draft/raw response
- 安全字段白名单和禁止字段黑名单完整

Plan 说 "do not change chapter acceptance behavior; only expose the inconsistency" ——这是关键安全约束。

Tests 覆盖了 5 个关键场景（consistent timeout, missing terminal diagnostic, audit_rule_too_strict, unknown_anchor, secret safety）。

### Focus 5: 边界、fail-closed、secret safety、no deterministic fallback

**PASS**。

- UI→Service→Host→Agent 边界：只改 Service 层 serializer（`chapter_orchestrator.py`, `llm_run_artifacts.py`），不跨层。Host 保持 business-agnostic，Agent/Fund 层不动。
- Fail-closed：所有 stop conditions 保持 fail-closed（exit 1, stdout empty）。Non-goals 明确 no deterministic fallback。
- Secret safety：Safe Evidence Fields 白名单和 Forbidden 黑名单完整覆盖 API key、Authorization header、Bearer token、base URL、model value、raw prompt、draft、provider response、audit response、report body、PDF text。
- No deterministic fallback：在 non-goals 和 stop conditions 中多次确认。

## Overall Judgment

**PASS — no blocking findings.**

Plan 基于同源证据正确识别了 Ch2 diagnostic attribution gap，未过度推断。正确阻止了 provider timeout default tuning、PASS-only、split-audit 和 Ch3 implementation 的过早启动。Ch1/Ch4/Ch5/Ch6 均分入正确的 failure family。下一 gate（typed diagnostic serialization repair）时机和范围合理。边界、fail-closed、secret safety 约束全部满足。

4 个 non-blocking findings 建议在 controller judgment 或 implementation gate 中处理，不阻止 plan acceptance。

## Review Artifact

`docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-review-ds-20260603.md`
