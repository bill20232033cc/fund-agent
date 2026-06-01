# MVP LLM writer/auditor contract hardening code review

日期：2026-05-31

角色：AgentMiMo independent code reviewer，不 controller、不 implementation worker。

Review target：当前 uncommitted workspace changes，Gate A implementation only。

Primary artifacts：
- Approved plan：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
- Controller judgment：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-controller-judgment-20260531.md`
- Implementation evidence：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md`

## Verdict

**PASS**

无 blocking findings。实现正确覆盖 approved plan 的 Slice A-D，fail-closed 语义完整，secret hygiene 保持，测试覆盖充分。

## Findings

### F-001 [INFO] `_facet_asserted` regex 可能对否定句误杀

- 严重级别：INFO
- 文件：`fund_agent/fund/chapter_auditor.py:761-775`
- 证据：`_ASSERTED_FACET_RE_TEMPLATE = r"(?:本基金|这只基金|该基金|基金)?\s*(?:是|为|属于|定位为|可判定为)\s*{facet}"` 不含否定词锚定。文本 `本基金不是主动权益基金（价值风格）` 会在位置 4 匹配到 `是主动权益基金`，触发 blocking。
- 影响：MVP 低风险。writer prompt 明确要求使用推荐写法 `候选/未断言信息：<facet> 仅为候选标签...`，该写法在 assertion verb 后使用 `该 facet` 占位而非实际 facet 文案，不会命中 regex。误杀优于漏杀。
- 残余风险：若真实 provider 在否定句中重复实际 facet 文案，会触发 false positive blocking。后续 polish gate 可考虑增加否定词前瞻 `(?<!不)` 或窗口内否定检测。
- 建议：记录为后续 polish gate 的已知限制，当前不阻断。

### F-002 [INFO] `_provider_runtime_stop_reason` 使用 type name 字符串匹配而非 isinstance

- 严重级别：INFO
- 文件：`fund_agent/services/chapter_orchestrator.py:826-838`
- 证据：`if type_name == "LLMProviderTimeoutError":` 等条件使用字符串匹配。若有人子类化这些异常，type name 会不同导致 fallback 到 `llm_exception`。
- 影响：当前代码库无子类化场景，orchestrator 不直接 import provider exceptions（保持解耦），设计合理。
- 建议：可接受。若后续需要更精确匹配，可在 `LLMProviderRuntimeError` 上增加 `category` 属性。

### F-003 [INFO] `_sanitize_text` 将 `prompt` 列为敏感词可能过度脱敏

- 严重级别：INFO
- 文件：`fund_agent/services/chapter_orchestrator.py:1098-1107`
- 证据：`for sensitive in ("Authorization", "Bearer", "FUND_AGENT_LLM_API_KEY", "api_key", "sk-", "prompt"):` 将 `prompt` 作为敏感词替换为 `[redacted]`。
- 影响：correction message 中若包含 "writer prompt" 或 "auditor prompt" 等合法上下文会被脱敏。例如 "按 auditor 行协议修复" 不含 "prompt" 所以不受影响；但 "the prompt was malformed" 会被脱敏。
- 建议：可接受。correction messages 由确定性映射生成，当前已知 patterns 不含独立 "prompt" 词。后续若需保留可缩小匹配范围为 `api_key` / `sk-` 前缀。

### F-004 [INFO] real provider smoke 未在当前环境执行

- 严重级别：INFO
- 文件：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md:64-67`
- 证据：implementation evidence 记录 `real-provider-smoke-006597-2024` 未执行，因 worker 环境缺 `FUND_AGENT_LLM_PROVIDER`。`real-provider-smoke` 命令因 missing config exit code `1`。
- 影响：contract hardening 的代码正确性由 fake client tests 覆盖；真实 provider 行为验证推迟到下一 gate `MVP real provider smoke acceptance gate`。这是 approved plan 允许的。
- 建议：controller 应在有 LLM env 的环境重跑 real provider smoke 作为下一 gate 前置验证。

## Checklist verification

### 1. Writer protocol and parser

- [PASS] `REQUIRED_BODY_SECTION_HEADINGS` 固定为 `### 结论要点` / `### 详细情况` / `### 证据与出处`（`chapter_writer.py:58-62`）
- [PASS] `REQUIRED_OUTPUT_MARKER_PREFIX = "<!-- required_output:"`（`chapter_writer.py:63`）
- [PASS] `_required_output_marker()` 生成 exact marker `<!-- required_output:<item> -->`（`chapter_writer.py:942-953`）
- [PASS] `_required_structure_issues()` 对 chapter 1-6 检查三个固定段落，缺任一产生 `missing_required_structure` stop reason（`chapter_writer.py:884-910`）
- [PASS] `_required_output_marker_issues()` 检查 exact marker，不接受裸 item text（`chapter_writer.py:914-938`）
- [PASS] `INCOMPLETE_FINISH_REASONS = frozenset(("length", "max_tokens", "content_filter"))` 在空响应检查之后、超长检查之前拦截（`chapter_writer.py:808-815`）
- [PASS] `_unknown_anchor_issue()` reason 从 `llm_contract_violation` 改为 `unknown_anchor`（`chapter_writer.py:1089`）
- [PASS] `_draft_from_llm_response()` 顺序：空响应 → incomplete finish_reason → 超长 → marker 格式 → 结构段落 → required output marker → anchor/missing → evidence/forbidden（`chapter_writer.py:802-846`）
- [PASS] 测试覆盖：`test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text` 覆盖 `length` 和 `content_filter`；`test_writer_blocks_missing_required_body_section_before_audit`；`test_writer_blocks_missing_required_output_marker_before_audit`

### 2. non_asserted candidate facets

- [PASS] `_facet_asserted()` 使用 regex 匹配断言动词 `是|为|属于|定位为|可判定为`（`chapter_auditor.py:761-775`）
- [PASS] 候选/未断言 disclaimer 包含 `不能写成本基金属于该 facet`（使用 `该 facet` 占位）不会命中 regex（`test_non_asserted_facet_candidate_disclaimer_passes`）
- [PASS] 同一 facet 多次断言只报告一次但仍 blocking（`test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet`，assert `len(facet_issues) == 1` 且 `result.status == "fail"`）
- [PASS] asserted fact 仍被阻断（existing `test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact`）
- [PASS] 无 candidate facet 变成 asserted

### 3. Auditor line protocol

- [PASS] `_audit_contract_markers()` 改为检查 exact marker `_required_output_marker(item) not in markdown`，不检查裸 item text（`chapter_auditor.py:550-553`）
- [PASS] LLM audit prompt 明确 `PASS|chapter|no issues` 为唯一 pass 格式（`chapter_auditor.py:835-851`）
- [PASS] LLM audit prompt 明确 `BLOCKING|<location>|<message>` 等行格式，禁止 Markdown/JSON/解释性前缀（`chapter_auditor.py:835-851`）
- [PASS] `_llm_parse_failure()` message 包含行协议修复提示（`chapter_auditor.py:926-928`）
- [PASS] 测试覆盖：`test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol`；`test_llm_audit_blocks_markdown_or_explanatory_prefix`；`test_llm_audit_parse_failure_is_blocked` 断言 message 含 `PASS|chapter|no issues`
- [PASS] `_valid_markdown()` helper 更新为包含 required output markers（`test_chapter_auditor.py:672-675`）

### 4. Repair/regenerate

- [PASS] `ChapterRepairContext` 是 `frozen=True, slots=True, kw_only=True` dataclass（`chapter_writer.py:124-139`）
- [PASS] 字段：`attempt_index: int`、`previous_issue_ids: tuple[str, ...]`、`previous_messages: tuple[str, ...]`、`required_corrections: tuple[str, ...]`
- [PASS] `ChapterWriterInput.repair_context: ChapterRepairContext | None = None`（`chapter_writer.py:202`）
- [PASS] `ChapterLLMRequest.repair_context: ChapterRepairContext | None = None`（`chapter_writer.py:121`）
- [PASS] `build_chapter_prompt()` 存在 repair context 时追加 attempt_index、issue ids、messages、required corrections（`chapter_writer.py:750-763`）
- [PASS] `_llm_request_from_prompt()` 传递 repair_context（`chapter_writer.py:734`）
- [PASS] orchestrator regenerate 时重建 writer_input 携带 `_repair_context_from_audit()`（`chapter_orchestrator.py:762-772`）
- [PASS] `_required_corrections_from_issues()` 使用确定性映射：P1 结构 → C2 required output → C2 facet → E1 anchor → llm:parse_failure → fallback sanitize（`chapter_orchestrator.py:1042-1068`）
- [PASS] `_sanitize_text()` 去换行、限长 180 chars、替换敏感词（`chapter_orchestrator.py:1098-1107`）
- [PASS] 无 `extra_payload` 引入
- [PASS] `max_repair_attempts` 保持 bounded（existing `ChapterOrchestrationPolicy.max_repair_attempts`）
- [PASS] 测试覆盖：`test_repair_context_is_rendered_into_writer_prompt_without_extra_payload`；`test_llm_request_carries_typed_repair_context`；`test_regenerate_request_contains_previous_failure_context`；`test_required_corrections_are_deterministic_for_known_issue_patterns`；`test_required_corrections_sanitize_unknown_issue_message`

### 5. Provider runtime classification

- [PASS] `LLMProviderTimeoutError(LLMProviderRuntimeError)` 新增（`llm_provider.py:62-63`）
- [PASS] `LLMProviderNetworkError(LLMProviderRuntimeError)` 新增（`llm_provider.py:66-67`）
- [PASS] `httpx.TimeoutException` → `LLMProviderTimeoutError`（`llm_provider.py:187`）
- [PASS] `httpx.TransportError` → `LLMProviderNetworkError`（`llm_provider.py:189`）
- [PASS] `_provider_runtime_stop_reason()` 映射：timeout → `llm_timeout`，rate limit → `llm_rate_limited`，malformed → `llm_malformed_response`，network → `llm_network_error`，unknown → `llm_exception`（`chapter_orchestrator.py:826-838`）
- [PASS] `_exception_result()` 使用 `_provider_runtime_stop_reason()` 替代硬编码 `llm_exception`（`chapter_orchestrator.py:808`）
- [PASS] issue message 使用 `_safe_exception_message()` 脱敏（`chapter_orchestrator.py:817`）
- [PASS] 测试覆盖：`test_provider_runtime_exceptions_map_to_precise_stop_reason` 覆盖四种异常类型；`test_timeout_maps_to_typed_error_without_prompt_or_key`；`test_network_error_maps_to_typed_error_without_prompt_or_key`

### 6. Non-goal compliance

- [PASS] 无 golden/fixtures/score/quality gate/snapshot/promotion state 变更
- [PASS] 无 dayu/Host/Agent 变更
- [PASS] 无 PR/release 变更
- [PASS] deterministic default analyze/checklist 行为未改变（evidence 记录 `1127 passed` full coverage）
- [PASS] 无 `docs/fund-analysis-template-draft.md`、`docs/design.md`、`docs/implementation-control.md` 变更
- [PASS] `fund_agent/fund/README.md` 更新了 writer/auditor public contract 描述，与代码一致

### 7. Secret hygiene

- [PASS] `_safe_exception_message()` 脱敏 Authorization/Bearer/API key/sk-/prompt
- [PASS] `_sanitize_text()` 脱敏并限长
- [PASS] `_llm_parse_failure()` message 不含完整 provider response
- [PASS] implementation evidence 不含 API key、Authorization header、完整 provider response
- [PASS] 测试中断言 `"Authorization" not in` 和 `"Bearer" not in`

## Residual test/smoke gaps

1. Real provider smoke `real-provider-smoke-006597-2024` 未在当前环境执行，因 worker 缺 LLM env。由下一 gate `MVP real provider smoke acceptance gate` 覆盖。
2. `_facet_asserted` regex 对否定句（如 `本基金不是<facet>`）可能误杀，但推荐 disclaimer 写法规避了此问题。后续 polish gate 可增加否定词检测。
3. `_provider_runtime_stop_reason` 使用 type name 字符串匹配，当前无子类化风险，后续可考虑增加 `category` 属性。

## Scope compliance

- Allowed files touched：`chapter_writer.py`、`chapter_auditor.py`、`chapter_orchestrator.py`、`llm_provider.py`、对应测试文件、`test_cli.py`、`fund_agent/fund/README.md`
- Prohibited files untouched：`docs/design.md`、`docs/implementation-control.md`、`docs/fund-analysis-template-draft.md`、golden/fixtures/score/quality gate、Host/Agent/dayu
- No commit/push/PR/merge/release

## Test results

- `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_provider.py tests/ui/test_cli.py -q`：**155 passed**
- Full coverage：**1127 passed, 91.77%**
- `uv run ruff check .`：PASS
- `git diff --check`：PASS
