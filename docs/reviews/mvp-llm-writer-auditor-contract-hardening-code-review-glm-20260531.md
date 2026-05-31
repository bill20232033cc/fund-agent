# MVP LLM writer/auditor contract hardening code review (GLM)

日期：2026-05-31
角色：AgentGLM 独立 code reviewer，非 controller、非 implementation worker。
Gate：`MVP LLM writer/auditor contract hardening gate`
Approved plan：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
Implementation evidence：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md`

## Verdict

**PASS** — 无阻断性发现。实现与 approved plan 一致，fail-closed 语义正确，安全边界未放松，秘密卫生保持。

## Blocking findings

无。

## Non-blocking findings

### N-1 (info)：控制面文档与 implementation workspace 共存

- 严重程度：info
- 文件：`docs/current-startup-packet.md`、`docs/implementation-control.md`
- 证据：git diff 显示两个文件有未提交修改，内容为 gate 状态从 "MVP Gate 4 draft PR gate" 转移到 "MVP provider auth/config verification gate"。Plan section 7 明确禁止 implementation worker 编辑这两个文件。Implementation evidence 声称 "prohibited files untouched by this worker"。
- 判断：diff 内容是 gate 状态转移叙事更新，属于 controller closeout 操作，非 implementation worker 代码变更。两文件变更不涉及运行时契约或安全边界。未提交 workspace 中共存不影响本次 code review 的 pass 判定，但 controller closeout 应在独立 commit 或明确的 handoff 中完成，以便 attribution 清晰。
- 建议：controller 可选择将控制面更新拆到独立 commit，或在 closeout judgment 中显式接受共存。

### N-2 (info)：`_provider_runtime_stop_reason` 使用 `type(exc).__name__` 字符串比较

- 严重程度：info
- 文件：`fund_agent/services/chapter_orchestrator.py:834`
- 证据：函数通过 `type(exc).__name__ == "LLMProviderTimeoutError"` 等字符串匹配分类异常，而非 `isinstance` 检查。测试 `test_provider_runtime_exceptions_map_to_precise_stop_reason` 覆盖四种 typed 异常。
- 判断：此设计避免了 Service 层 import provider 层异常类（维护层边界）。在当前 provider 异常类不使用子类化的前提下行为正确。若后续引入子类化，`type().__name__` 将不匹配父类名，fallback 到 `llm_exception`——仍是 fail-closed 安全行为。MVP 可接受。
- 建议：后续 gate 可考虑在 provider 层提供稳定 category 属性或注册表，替代字符串比较。

### N-3 (info)：`_sanitize_text` 对 "prompt" 一词过度脱敏

- 严重程度：info
- 文件：`fund_agent/services/chapter_orchestrator.py:1101`
- 证据：脱敏列表包含 `"prompt"`，会将与 LLM prompt 无关的 "prompt" 文本替换为 `[redacted]`。测试 `test_required_corrections_sanitize_unknown_issue_message` 验证了 `Authorization`、`Bearer`、`sk-` 的脱敏，但未覆盖 "prompt" 误杀场景。
- 判断：保守策略倾向于过度脱敏而非泄漏，安全方向正确。实际 repair context 消息中 "prompt" 出现概率低，且映射到 `[redacted]` 不影响修复指导的语义。
- 建议：后续可区分独立词 "prompt" 与嵌入模式（如 "api_key" 前缀），减少误杀。

### N-4 (info)：`_required_correction_from_issue` E1 映射条件过宽

- 严重程度：info
- 文件：`fund_agent/services/chapter_orchestrator.py:1043`
- 证据：E1 correction 触发条件为 `issue.rule_code == "E1" or "anchor" in message.lower() or "锚点" in message`，即任何包含 "anchor" 或 "锚点" 的消息（无论 rule_code）都映射到 anchor 修正项。
- 判断：映射目标是安全修正（"只使用 allowed anchor marker"），不会产生危险的修复指导。但可能让非 anchor 类 issue 收到不精确的 correction，增加 regenerate prompt 噪音。测试 `test_required_corrections_are_deterministic_for_known_issue_patterns` 覆盖了 E1 正确映射。
- 建议：后续可收紧条件为 `issue.rule_code == "E1"` 或添加 `issue.location` 辅助判断。

## Verification by review focus area

### 1. Writer protocol and parser

**结论：正确。**

- `REQUIRED_BODY_SECTION_HEADINGS` 定义三个固定段落（`chapter_writer.py:58-62`）。
- `REQUIRED_OUTPUT_MARKER_PREFIX` 定义 exact marker 前缀（`chapter_writer.py:63`）。
- `INCOMPLETE_FINISH_REASONS` 包含 `length`、`max_tokens`、`content_filter`（`chapter_writer.py:64-66`），命名统一使用 `response_incomplete`，不将 `content_filter` 误称 truncation（对应 GLM N-1 fix）。
- `_draft_from_llm_response` 检查顺序正确：空响应 → finish_reason 不完整 → 超长 → marker 格式 → required section headings → required output markers → anchor/missing parsing → evidence line and forbidden phrases（`chapter_writer.py:800-833`）。遇到不完整 finish_reason 时 `return None` 且不解析部分文本，不做 free-text 猜测。
- `_required_structure_issues`（`chapter_writer.py:884-911`）：只检查第 1-6 章，缺失时生成 `missing_required_structure` stop reason。
- `_required_output_marker_issues`（`chapter_writer.py:914-939`）：以 exact marker `<!-- required_output:<item> -->` 匹配，非裸 item text。
- `_unknown_anchor_issue`（`chapter_writer.py:1073-1095`）：stop reason 为 `unknown_anchor`，保留 bond_risk_evidence 专门 message。
- 测试覆盖：`test_writer_blocks_missing_required_body_section_before_audit`、`test_writer_blocks_missing_required_output_marker_before_audit`、`test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text`（覆盖 `length` 和 `content_filter` 两种 finish reason）、`test_writer_rejects_unknown_anchor_reference`。

### 2. Non-asserted candidate facets

**结论：正确。**

- `_audit_non_asserted_facets`（`chapter_auditor.py:618-646`）：循环迭代 `non_asserted_facets`（unique facet text），每个 facet 最多产生一条 issue。断言检测使用 `_ASSERTED_FACET_RE_TEMPLATE`（`chapter_auditor.py:134`）匹配 `是/为/属于/定位为/可判定为` 五种断言动词。
- 去重策略：自然去重——循环粒度是 `non_asserted_facets` 中的 unique facet text，而非 markdown 中的每个断言出现位置。测试 `test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet` 验证同一 facet 多处断言只产生一条 issue 且仍 blocking。
- 候选 disclaimer 通过：`test_non_asserted_facet_candidate_disclaimer_passes` 验证 "候选/未断言信息：<facet> 仅为候选标签..." 不被误杀。断言模板不匹配 "候选/未断言" 前缀的文本。
- asserted candidate facet 仍 blocking：`test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact` 验证 "这只基金是主动权益基金（价值风格）" 触发 C2。

### 3. Auditor line protocol

**结论：正确。**

- Programmatic `_audit_contract_markers`（`chapter_auditor.py:536-554`）：使用 `_required_output_marker(item)` 构造 exact marker，通过 `marker not in markdown` 检查。裸 item text 不能通过。测试 `test_programmatic_audit_requires_required_output_marker_not_bare_item_text` 移除 marker 但保留裸文案，验证 C2 仍触发。
- LLM audit prompt（`chapter_auditor.py:835-849`）：明确指定唯一 pass 格式 `PASS|chapter|no issues`、三种 severity 行格式、location/message 非空要求、禁止额外文本，含 pass 和 blocking 示例。测试 `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol` 验证 prompt 内容。
- `_parse_llm_audit_response`（`chapter_auditor.py:857-902`）：`lines == ("PASS|chapter|no issues",)` 精确匹配。非 pass 行要求 `split("|", 2)` 产生 3 部分、severity 在允许集合内、location 和 message 非空。任何违反触发 `_llm_parse_failure`。测试 `test_llm_audit_blocks_markdown_or_explanatory_prefix` 验证解释性前缀 "审计结果：\nPASS|chapter|no issues" 被正确 parse failure。
- Parse failure 语义：`_llm_parse_failure` 返回 `status="blocked"`、`accepted=False`、issue id 包含 `llm:parse_failure`，message 包含行协议修复提示。测试 `test_llm_audit_parse_failure_is_blocked` 验证 status=blocked 且 message 包含 "PASS|chapter|no issues"。

### 4. Repair/regenerate

**结论：正确。**

- `ChapterRepairContext`（`chapter_writer.py:127-141`）：frozen dataclass，显式 typed fields（`attempt_index`、`previous_issue_ids`、`previous_messages`、`required_corrections`），无 `extra_payload`。测试 `test_repair_context_is_rendered_into_writer_prompt_without_extra_payload` 验证 `ChapterLLMRequest.__dataclass_fields__` 不包含 `extra_payload`。
- `ChapterWriterInput.repair_context`（`chapter_writer.py:205`）：默认 `None`，初始 attempt 不携带。
- Regenerate 重新构造 writer input（`chapter_orchestrator.py:762-773`）：调用 `_repair_context_from_audit` 从上一轮 audit result 派生 context，包含 issue ids、脱敏 messages、deterministic corrections。测试 `test_regenerate_request_contains_previous_failure_context` 验证第二轮 request 的 repair context 包含 previous_issue_ids、previous_messages 和 required_corrections。
- `_required_corrections_from_issues`（`chapter_orchestrator.py:996-1047`）：确定性映射覆盖 P1 结构段落、C2 required output、C2 candidate facet、E1 anchor、`llm:parse_failure`。未知规则使用 `_sanitize_text` fallback（脱敏 `Authorization`/`Bearer`/`sk-`/`prompt`/换行，限长 180 字符）。测试 `test_required_corrections_are_deterministic_for_known_issue_patterns` 和 `test_required_corrections_sanitize_unknown_issue_message` 完整覆盖。
- Max attempts bounded：`ChapterOrchestrationPolicy.max_repair_attempts` 控制，默认 1。测试 `test_max_repair_attempts_zero_does_not_retry_after_audit_failure` 和 `test_repair_budget_exhausted_returns_failed_stop_reason` 验证边界。

### 5. Provider runtime classification

**结论：正确。**

- `LLMProviderTimeoutError`、`LLMProviderNetworkError`（`llm_provider.py:62-67`）：新增 typed subclasses。
- `_complete`（`llm_provider.py:186-189`）：`httpx.TimeoutException` → `LLMProviderTimeoutError`，`httpx.TransportError` → `LLMProviderNetworkError`（排除已捕获的 timeout）。
- `_provider_runtime_stop_reason`（`chapter_orchestrator.py:821-843`）：映射 timeout → `llm_timeout`、rate limit → `llm_rate_limited`、malformed → `llm_malformed_response`、network → `llm_network_error`、unknown → `llm_exception`。
- Issue message 不含 secret：`_safe_exception_message` 调用 `_sanitize_text` 脱敏。测试 `test_provider_runtime_exceptions_map_to_precise_stop_reason` 验证四种 typed 异常精确映射且 issues 不含 `Authorization`/`Bearer`。
- Provider 层测试：`test_timeout_maps_to_typed_error_without_prompt_or_key` 和 `test_network_error_maps_to_typed_error_without_prompt_or_key` 验证 typed error 且不泄漏 prompt/key。

### 6. Scope boundary check

**结论：通过。**

- 无 golden/fixtures/score/quality gate/snapshot/promotion state 变更。
- 无 dayu/Host/Agent 文件变更。
- 无 PR/push/merge/release 操作。
- Deterministic `analyze`/`checklist` 默认行为未改变（writer prompt 变更仅影响 `--use-llm` 路径的 LLM 输出协议，不影响 deterministic renderer）。
- Import boundary 测试：`test_writer_does_not_import_repository_source_service_dayu_or_openai`、`test_auditor_does_not_import_repository_source_service_dayu_or_openai`、`test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries` 均通过。
- 控制面文档（N-1）为 gate 状态更新，非运行时代码。
- `fund_agent/fund/README.md` 变更合理：writer/auditor public contract 变更需要同步开发手册。

### 7. Tests and safety boundaries

**结论：正确。**

- 测试 helper `_valid_chapter_markdown`（writer test）、`_valid_markdown`（auditor test）、`_valid_markdown_from_parts`（orchestrator test）均已更新，包含 required output markers 和固定结构段落。
- Stop reason mapping 测试 `test_every_writer_stop_reason_maps_to_exact_run_reason` 覆盖全部 13 个 writer stop reason（排除 `none`），与 `ChapterWriteStopReason.__args__` 精确对齐。
- Fail-closed 路径覆盖：missing config exit 1（`test_analyze_cli_use_llm_missing_config_fails_before_service`）、timeout fail-closed（`test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`）、incomplete result no fallback（`test_analyze_cli_use_llm_incomplete_result_exits_without_fallback`）。
- 安全边界未放松：交易建议仍被阻断（`test_writer_rejects_forbidden_trading_advice`）、ITEM_RULE 删除段落仍被阻断（`test_programmatic_audit_fails_deleted_item_rule_section`）、E2 deferred 未改变、证据锚点要求未放松。

## Test gap summary

- Real provider smoke 未在 implementation worker 环境运行（因缺少 LLM env），属于已知 residual risk，由下一 gate `MVP real provider smoke acceptance gate` 负责。
- `max_tokens` finish reason 未在 `test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text` 参数化中单独测试，但 `INCOMPLETE_FINISH_REASONS` frozenset 包含该值，且代码路径统一处理所有 `INCOMPLETE_FINISH_REASONS` 成员。
- `_sanitize_text` 的 "prompt" 误杀场景未被正面测试覆盖（N-3）。

## Self-check

Self-check: pass

- 只执行了读取操作（源码、测试、文档、diff），未修改任何文件（review artifact 除外）。
- 未运行破坏性命令、未 commit/push/PR。
- Review artifact 未包含 API key、Authorization header、完整 provider response 或完整 writer draft。
- Verdict 基于代码证据和测试覆盖，非推测。
