# MVP provider runtime timeout follow-up plan re-review — MiMo

Gate: `MVP provider runtime timeout follow-up gate`
Role: plan re-reviewer
Date: 2026-05-31
Reviewed artifact: `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
Original review: `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-mimo-20260531.md`

## Conclusion

**PASS**

Blocking finding MIMO-P1 已在 plan 中修复。Runtime serializer 现在明确禁止输出通用 `message` 字段，CLI summary 也不输出 message，测试要求覆盖负断言。Plan 仍聚焦 chapter 1 `llm_timeout`，未回退到 provider config/auth，未扩大 retry，未混修 C2，未放松 evidence/ITEM_RULE/candidate facet/L1/default deterministic。Plan handoff-ready。

---

## Blocking finding verification

| Finding ID | Original verdict | Plan fix location | Verification |
|---|---|---|---|
| MIMO-P1 | blocking (高) | §5.1 line 76-77, §5.2 line 99, §7 Slice 1 assertions, §9 evidence exclusion, §10 code review gates | **FIXED** — 见下方逐项验证 |

### MIMO-P1 逐项验证

**1. Runtime serializer 禁止输出通用 `message`**

Plan §5.1 line 76-77:

> "Do not include the generic `message` field in the runtime serializer. Existing `ChapterLLMRuntimeDiagnostic.message` can be provider-local safe text in some cases, but it can also be built from writer/auditor/programmatic issue text or LLM audit line messages. For this gate, precise timeout classification must rely on allowlisted scalar fields only."

代码事实确认：`_writer_runtime_diagnostic()` (line 1243) 以 `"; ".join(_writer_issue_messages(writer_result))` 构造 message；`_audit_runtime_diagnostic()` (line 1289) 以 `"; ".join(_audit_issue_messages(audit_result))` 构造 message。这些来源不是 provider scalar，plan 正确识别了风险并禁止序列化该字段。

§5.1 最后一段还明确：未来 gate 如需文本摘要，必须单独添加 allowlisted enum/fixed-summary field 并有测试证明 writer/auditor/programmatic issue messages 不能流入。

**2. CLI summary 不输出 message**

Plan §5.2 line 99:

> "The CLI summary must not print runtime diagnostic `message` or any writer/auditor/programmatic issue text."

CLI 只输出 plan 列出的 safe scalar fields：`first_failed_runtime_operation`、`first_failed_provider_attempts`、`first_failed_provider_runtime_category`、`first_failed_elapsed_ms_max`。

**3. 测试要求覆盖 writer/auditor/programmatic/raw audit canary 负断言**

Plan §7 Slice 1 acceptance assertions (line 186):

> "Omits generic diagnostic `message` even when a diagnostic carries text that contains writer issue text, auditor LLM line text, programmatic issue text, raw audit sentinel text, prompt/draft/body-like strings or secret-like strings."

Plan §7 Slice 2 acceptance assertions (line 199):

> "No deterministic fallback and no secret/prompt/body/raw audit/draft-derived message leakage."

Plan §8 test plan (line 240):

> "content-level negative assertion over diagnostic JSON/stderr: injected sentinel strings representing `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, raw audit text, provider body, writer/auditor issue text, Authorization/Bearer/key-like values must be absent."

**4. Evidence 排除**

Plan §9 (line 272):

> "generic runtime diagnostic `message`, writer issue message, auditor LLM issue message, programmatic issue message, provider body text or draft-derived snippets."

**5. Code review gates**

Plan §10 (line 287):

> "Runtime serializer and CLI summary do not output diagnostic `message`; tests include negative canary strings for writer/auditor/programmatic/raw audit text."

---

## Scope / constraints re-verification

| Criterion | Status |
|---|---|
| 聚焦 chapter 1 `llm_timeout`，不回到 provider config/auth | PASS — §1, §3, §5.4 |
| retry 保持 timeout-only、有界 `1..3` | PASS — §5.3 |
| 不引入并发或 provider fallback | PASS — §3, §5.3 |
| 不放松 writer/auditor/evidence/C2/L1/candidate facet/ITEM_RULE/quality/golden/default deterministic | PASS — §3 |
| 不记录 API key/Authorization/prompt/draft/provider response/raw audit response | PASS — §3, §9 |
| 不改 PR/push/merge/release | PASS — §3 |
| C2 作为 timeout-free 后的 secondary diagnostic，不在本 gate 修复 | PASS — §5.5 |
| 不改 golden/fixtures/score/quality gate/final judgment | PASS — §3 |

---

## Positive checks

- Plan 对 `ChapterLLMRuntimeDiagnostic.message` 的风险分析准确：正确区分了 provider-local safe message（来自 llm_provider.py 的固定文案或 status/request-id 摘要）和 Service 层 writer/auditor diagnostic 复用同一字段的非标量文本。
- §5.1 最后一段的 "future gate" 约定合理，防止后续 gate 默认恢复 message 输出。
- §5.4 failure taxonomy 不复用 prompt-contract subcategory 来表达 timeout，避免语义混淆。
- §5.3 timeout budget 决策使用现有 config knobs，不新增 provider config 变量。
- Implementation slices 划分合理：slice 1 (serializer) → slice 2 (CLI) → slice 3 (evidence script)，顺序依赖正确。

---

## Open Questions

无。

---

## Residual Risks

- 真实 provider 在 bounded smoke 下仍可能 timeout，这是 Gate B acceptance 风险，不是本 plan blocker。controller judgment 需按计划输出唯一主 blocker 和下一最小入口。
- 若 timeout-free rerun 到达 chapter 3 C2，应按 `MVP programmatic audit C2 calibration gate` 单独处理。

---

## Reviewer Self-Check

- 当前角色：Gateflow plan re-reviewer（MiMo），不是 implementation worker。
- 本 review 只新增指定 review artifact；未修改 plan 或代码。
- finding 验证绑定到 plan 具体行号和代码事实（line 1243, 1289），不是风格意见。
- conclusion 使用 `PASS`，因为 blocking finding MIMO-P1 已在 plan 中修复。
- output path 使用本机系统时钟生成的 timestamp（`20260531-081249`）。
