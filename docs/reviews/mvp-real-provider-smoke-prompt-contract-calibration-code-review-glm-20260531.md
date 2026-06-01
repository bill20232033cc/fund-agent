# MVP real provider smoke prompt-contract calibration — code review (GLM)

日期：2026-05-31

Gate：MVP real provider smoke acceptance rerun with prompt-contract calibration
Role：code review worker

## Self-check

- Current gate / role：只做 code review，不启动完整 gateflow，不改代码，不 commit/push/PR。
- Source of truth：approved plan、plan fix、controller judgment、implementation evidence。
- Scope boundary：只 review allowed-file implementation；未修改 control docs、design、template、golden、fixtures、score、quality gate、Host/Agent/dayu。
- Verified commands：未亲自运行验证命令（review worker 不改代码也不运行 smoke）；review 依据代码阅读、测试断言分析和 controller evidence 文件。

## Scope verification

Changed files 全部在 allowed list 内：

| File | Allowed | Status |
|---|---|---|
| `fund_agent/fund/chapter_writer.py` | yes | reviewed |
| `fund_agent/fund/chapter_auditor.py` | yes | reviewed |
| `fund_agent/services/chapter_orchestrator.py` | yes | reviewed |
| `fund_agent/services/llm_provider.py` | yes | reviewed |
| `fund_agent/ui/cli.py` | yes | reviewed |
| `tests/fund/test_chapter_writer.py` | yes | reviewed |
| `tests/fund/test_chapter_auditor.py` | yes | reviewed |
| `tests/services/test_chapter_orchestrator.py` | yes | reviewed |
| `tests/services/test_llm_provider.py` | yes | reviewed |
| `tests/ui/test_cli.py` | yes | reviewed |
| `fund_agent/config/llm.py` | yes | reviewed |

**No scope violations detected.** 未发现对 `docs/design.md`、`docs/implementation-control.md`、`AGENTS.md`、golden/fixtures/score/quality gate、Host/Agent/dayu 的编辑。

## Findings

### Blocking findings

**None.**

### Non-blocking findings

#### N1 — Controller smoke evidence stderr/diagnostic 不一致（informational）

Controller evidence 目录下 `controller-real-provider-006597-2024.stderr` 报告 `orchestration_status=blocked`、`first_failed_chapter_id=1`、`first_failed_stop_reason=llm_contract_violation`；而同目录 `controller-real-provider-006597-2024-diagnostic.json` 显示 `orchestration_status=partial`、chapter 1 `status=accepted`、chapter 2 `status=blocked`/`stop_reason=llm_contract_violation`。

两个 evidence 文件的章节状态矩阵不匹配，说明它们可能来自不同时间的 controller rerun。这不是代码 bug（`_first_failed_chapter_summary` 正确跳过 accepted 章节），但会导致 reviewer 如果仅看部分 evidence 就误判当前状态。

**建议**：controller 在 closeout 时确认所有 evidence 文件来自同一次 rerun，或在 evidence 中标注 rerun 序号/时间戳。

#### N2 — `_sanitize_text` redacts "prompt" 可能误伤审计 issue message（informational）

`chapter_orchestrator.py:1638` 的 `_sanitize_text` 把 `"prompt"` 替换为 `"[redacted]"`。如果审计 issue message 包含 "prompt contract" 或 "prompt calibration" 等合法诊断文本，会被脱敏。在 `llm_provider.py:595` 同样存在，但 provider 层处理的是完整 prompt 文本，redact "prompt" 是合理的。

orchestrator 层的 `_sanitize_text` 主要用于审计 issue message 和 repair correction，redact "prompt" 可能降低 repair 上下文的可读性。当前影响有限（repair correction mapping 用的是硬编码确定性文本，不含 "prompt"），但若未来 issue message 命中该词会导致 repair context 信息损失。

**建议**：后续 gate 考虑在 orchestrator 层的 sanitize 中移除 `"prompt"`，改用更精确的敏感词（如 `"writer user prompt"` 或 `"system prompt text"`）。

#### N3 — `_is_fact_gap_issue` 基于文本 heuristic（informational）

`chapter_orchestrator.py:1379` 通过在 `issue_id + message + repair_hint` 拼接文本中搜索 `"needs_more_facts"` 和 `"fact_gap"` 来判断是否为 fact gap issue。这是 heuristic 而非 typed 分类。

当前 bounded：`needs_more_facts` 来自 `ChapterAuditRepairHint` Literal，不会意外出现。但若 LLM auditor 返回的 message 文本恰好包含这些字符串，可能误分类。实际风险低（plan 要求 `audit_rule_too_strict` 检查同时排除 `needs_more_facts` repair hint 和 fact-gap 类 issue，heuristic 只在 LLM issue 侧生效）。

**建议**：后续 gate 考虑在 `ChapterAuditIssue` 增加 typed `failure_category_hint` 字段替代文本 heuristic。

## Review detail by check area

### 1. Writer prompt — 降低认知负担且不放松 parser/safety

**PASS。**

- Prompt 结构（`chapter_writer.py:408-446`）：输出协议放在最前（`"先遵守输出协议，后写内容："`），编号化、可复制。
- 固定三段（`chapter_writer.py:422-423`）：`### 结论要点 / ### 详细情况 / ### 证据与出处`，通过 `REQUIRED_BODY_SECTION_HEADINGS` 常量引用。
- Required output marker（`chapter_writer.py:424-425`）：`<!-- required_output:<exact required output item> -->` exact marker 语法在 prompt 中明确给出。
- Anchor marker（`chapter_writer.py:426-427`）：`<!-- anchor:<anchor_id> -->`，明确 allowed anchor set 是允许集合不是全量要求。
- Missing marker（`chapter_writer.py:428-429`）：`<!-- missing:<reason> -->`，缺口表达要求未披露/数据不足/下一步验证问题。
- Non-asserted facet（`chapter_writer.py:433-436`）：固定句式 `候选/未断言信息：<facet> 仅为候选标签...`，禁止断言形式 `是/为/属于/定位为/可判定为`。
- 长度防护（`chapter_writer.py:430-431`）：`max_output_chars` 硬上限，`response_too_long` fail-closed（`chapter_writer.py:824-831`）。
- Incomplete finish reason（`chapter_writer.py:64-66`，`816-823`）：`INCOMPLETE_FINISH_REASONS` 包含 `length`、`max_tokens`、`content_filter`，触发 `response_incomplete` blocked。
- Parser 未放松（`chapter_writer.py:830-854`）：有 issue 时 `draft` 为 `None`，不截断、不自动补 marker、不部分接受。
- 测试覆盖（`test_chapter_writer.py`）：empty response、too long、incomplete finish、missing structure、missing marker、unknown anchor、unknown missing reason、forbidden phrase、invalid marker spacing、non-asserted facet、repair context 渲染均有断言。

### 2. Auditor line protocol parse failure fail-closed

**PASS。**

- System prompt（`chapter_auditor.py:836-837`）：短硬句 `"只能返回固定行协议，禁止 Markdown、JSON、编号列表、解释性前缀或总结句。"`。
- User prompt（`chapter_auditor.py:839-848`）：唯一 pass 格式放在最前 `PASS|chapter|no issues`，非 pass 只允许三段 `BLOCKING|REVIEWABLE|INFO|<location>|<message>`。
- Parser（`chapter_auditor.py:857-902`）：
  - 空响应 → `_llm_parse_failure`（line 872-873）。
  - `PASS|chapter|no issues` 之外混入任何文本 → parse failure（line 874 只有精确匹配 `("PASS|chapter|no issues",)` 才 pass）。
  - 非 3 段 → parse failure（line 885-886）。
  - location/message 为空或 severity 不在 allowlist → parse failure（line 888-889）。
- Programmatic audit 优先于 LLM audit（`chapter_auditor.py:429-430`）：programmatic blocked 或 llm blocked → status `"blocked"`；programmatic fail 或 llm fail → status `"fail"`。LLM PASS 不能覆盖 programmatic blocked/fail。
- Parse failure 不被当 pass（`chapter_auditor.py:924-933`）：返回 `status="blocked"`、issue_id `"llm:parse_failure"`、repair_hint `"regenerate"`。
- 测试覆盖（`test_chapter_auditor.py`）：free text parse failure、extra separator parse failure、Markdown/explanatory prefix parse failure、audit LLM unavailable blocked、audit PASS + programmatic pass accepted、REVIEWABLE issue prevents acceptance。

### 3. Repair/regenerate bounded

**PASS。**

- `max_repair_attempts` 默认 `1`（`chapter_orchestrator.py:190`），固定不变。
- 每章最大 writer attempts = `1 + max_repair_attempts`（while loop 在 `chapter_orchestrator.py:746-890`，`attempt_index` 递增，`remaining_budget = max_repair_attempts - attempt_index` 在 `_decide_repair` 中检查）。
- Regenerate 输入包含上一轮失败摘要（`chapter_orchestrator.py:1506-1530`）：`attempt_index`、`previous_issue_ids`、sanitized `previous_messages`、`required_corrections`。
- Required corrections 是确定性映射（`chapter_orchestrator.py:1556-1584`）：P1→补结构、C2 required output→补 marker、C2 facet→改写为候选、E1→只使用 allowed anchor、llm:parse_failure→按行协议修复。
- Previous messages 经 `_sanitize_text` 脱敏限长（`chapter_orchestrator.py:1528`，max 180 chars）。
- Timeout 不进入 repair loop（`chapter_orchestrator.py:749-758`）：writer exception 直接返回 `_exception_result`，不调用 audit。
- 测试覆盖（`test_chapter_orchestrator.py`）：repair budget exhausted（`max_repair_attempts=0` 不重试）、regenerate 携带 repair context（`previous_issue_ids`/`previous_messages`/`required_corrections`）、timeout diagnostic enriched 不 regenerate（`len(writer.requests) == 1`）。

### 4. ChapterFailureCategory 新增 llm_timeout/audit_rule_too_strict

**PASS。**

- `ChapterFailureCategory` Literal（`chapter_orchestrator.py:79-87`）：包含 `provider_runtime`、`llm_timeout`、`prompt_contract`、`audit_parse`、`audit_rule_too_strict`、`fact_gap`、`code_bug`。与 plan Section 7.4 taxonomy 完全一致。
- Timeout 独立分类：
  - `_chapter_failure_category_from_exception`（`chapter_orchestrator.py:1204-1221`）：通过 `_provider_runtime_category_from_exception` 映射 timeout → `llm_timeout`，非 timeout → `provider_runtime`，未知 → `code_bug`。
  - `_chapter_failure_category_from_provider_runtime`（`chapter_orchestrator.py:1224-1241`）：timeout → `llm_timeout`，其他 → `provider_runtime`。
  - `_chapter_failure_category_from_stop_reason`（`chapter_orchestrator.py:1244-1275`）：`llm_timeout` → `llm_timeout`，`llm_*` prefix → `provider_runtime`。
- `audit_rule_too_strict` 四条件（`chapter_orchestrator.py:1340-1363` `_is_audit_rule_too_strict`）：
  1. `programmatic.status == "pass"`（line 1353）
  2. `llm.status in ("fail", "blocked")` 且 `llm.issues` 非空（line 1354-1357）
  3. 无 `LLM_UNAVAILABLE` issue（line 1359-1360）
  4. 无 `llm:parse_failure` issue（line 1361-1362）
  5. 无 fact gap issue（line 1363，`_is_fact_gap_issue` 检查 `needs_more_facts`/`fact_gap`）
  - Programmatic fail 仍走 `prompt_contract` 或 `fact_gap`（`chapter_orchestrator.py:1335-1336`），不被 LLM audit 覆盖。

### 5. ChapterRunResult.failure_category 填充一致性 / CLI 读取路径

**PASS。**

- `ChapterRunResult.failure_category`（`chapter_orchestrator.py:340`）：可选字段，`ChapterFailureCategory | None`。
- 填充路径全覆盖：
  - Writer blocked（line 789-790）：`_chapter_failure_category_from_writer_result`
  - Audit not accepted（line 889）：`_chapter_failure_category_from_audit_result`
  - Exception（line 950）：`_chapter_failure_category_from_exception`
  - Global blocked（line 698）：`_chapter_failure_category_from_stop_reason`
  - Accepted（line 841）：`failure_category=None`
  - Skipped/fail_fast（line 1883）：`failure_category="fact_gap"`
- CLI `_first_failed_chapter_summary`（`cli.py:835-864`）：用 `getattr(chapter_result, "failure_category", None)` 直接从 `ChapterRunResult` 顶层字段读取。不遍历 `attempts`、`runtime_diagnostics` 或 provider diagnostics。当 `failure_category is None` 时 fallback 到 `"unknown"`。
- CLI stdout 在 LLM 未完成时保持 empty（`cli.py:269-271`：`if use_llm and result.final_assembly_result.report_markdown is None` → stderr only，`typer.echo(result.report_markdown)` 在 if 块之后，此时 report_markdown 为 None 会 raise）。
- 测试覆盖（`test_cli.py`）：timeout fail-closed stderr 包含 `llm_timeout`、`first_failed_chapter_id=2`、`first_failed_category=llm_timeout`，stdout 为空，无 deterministic fallback。`_FakeChapterRunResult` 携带 `failure_category` 字段。

### 6. 验证矩阵和 controller 真实 provider evidence

**PASS with caveat (N1)。**

Implementation evidence 报告的验证矩阵全部 PASS：
- `ruff check`：PASS
- Targeted pytest（170 tests）：PASS
- Full coverage gate（1154 tests, 91.80%）：PASS
- Deterministic analyze/checklist smoke：PASS
- Missing-config `--use-llm` fail-closed：PASS
- Real provider smoke：BLOCKED（provider env absent in implementation shell）

Controller smoke evidence（`reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`）：
- `diagnostic.json` 显示 chapter 1 `accepted`（相比之前 gate 的 `llm_timeout`，这是实质性改善），chapter 2 `blocked`/`llm_contract_violation`/`prompt_contract`，chapter 3-6 `skipped`/`dependency_missing`/`fact_gap`。
- `orchestration_status=partial`（diagnostic.json），对比之前 gate 的 `blocked`，也是改善。
- `first_failed_category=prompt_contract` 精确指向 writer prompt contract 问题，不是泛化 `provider_runtime`。
- stderr 与 diagnostic.json 存在不一致（N1），建议 controller 统一 evidence。

结论：taxonomy 分类正确，失败未被包装成 pass。下一步入口明确为 writer prompt contract calibration follow-up（chapter 2 的 `llm_contract_violation`）。

### 7. Secret hygiene

**PASS。**

- `llm_provider.py`：Authorization header 在 `_complete` 中发送（line 225）但不在 diagnostic 中记录。`_sanitize_text`（line 568-598）redact `Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`、`api_key`、`sk-`、`prompt`、`writer user`、`draft markdown`。
- `chapter_orchestrator.py`：`_sanitize_text`（line 1623-1642）redact `Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`、`api_key`、`sk-`、`prompt`。
- `chapter_orchestrator.py:1383-1396`：`_safe_exception_message` 用 `_sanitize_text` 处理异常消息。
- `llm_provider.py`：`_safe_http_error_message`（line 528-545）只包含 status_code 和 request_id，不包含 response body。
- Controller smoke stderr：只包含 status/category 摘要，无 secret。
- Controller diagnostic.json：只包含结构化状态数据（chapter_id/status/stop_reason/failure_category/attempt_count），无 API key、prompt body、draft body 或 provider response。
- Implementation evidence secret scan：PASS（only safe policy-label hits）。
- CLI timeout test（`test_cli.py:1429-1430`）：断言 `Authorization`、`Bearer` 不在 stderr。
- Orchestrator code_bug test（`test_chapter_orchestrator.py:702-704`）：断言 `Authorization`、`Bearer`、`sk-` 不在 diagnostic message。

未发现 API key、Authorization header、完整 prompt、draft 或 provider response 被记录到 evidence/diagnostic/CLI 输出。

## Test coverage assessment

测试覆盖了 plan Section 9 所有 required assertions：

| Required assertion | Test location | Status |
|---|---|---|
| Writer prompt includes fixed headings, markers, anchor/missing syntax, candidate-only facet, length budget | `test_chapter_writer.py:test_writer_prompt_requires_body_sections_and_required_output_markers` | covered |
| Writer parser fail-closes missing structure | `test_chapter_writer.py:test_writer_blocks_missing_required_body_section_before_audit` | covered |
| Writer parser fail-closes missing required marker | `test_chapter_writer.py:test_writer_blocks_missing_required_output_marker_before_audit` | covered |
| Writer parser fail-closes candidate facet assertion | `test_chapter_auditor.py:test_programmatic_audit_blocks_non_asserted_facet_as_asserted_fact` | covered |
| Auditor line protocol accepts only exact pass or valid severity | `test_chapter_auditor.py:test_llm_audit_fake_pass_combines_with_programmatic_pass`, `test_llm_audit_line_with_extra_separator_is_parse_failure` | covered |
| Auditor parse failure blocked, cannot become pass | `test_chapter_auditor.py:test_llm_audit_parse_failure_is_blocked` | covered |
| Programmatic blocking not overridden by LLM PASS | `test_chapter_auditor.py:test_audit_blocks_when_llm_required_but_unavailable`（结构验证 programmatic→llm 顺序） | covered |
| Orchestrator regenerate includes previous issue ids/messages/corrections | `test_chapter_orchestrator.py:test_regenerate_request_contains_previous_failure_context` | covered |
| Orchestrator max repair bounded | `test_chapter_orchestrator.py:test_repair_budget_exhausted_returns_failed_stop_reason`, `test_max_repair_attempts_zero_does_not_retry_after_audit_failure` | covered |
| Timeout maps to llm_timeout | `test_chapter_orchestrator.py:test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate` | covered |
| ChapterRunResult.failure_category filled for all paths | `test_chapter_orchestrator.py:test_writer_prompt_contract_blocked_records_diagnostic_category`, `test_audit_parse_failure_records_audit_parse_diagnostic`, `test_parseable_llm_audit_failure_after_programmatic_pass_is_audit_rule_too_strict`, `test_needs_more_facts_records_fact_gap_diagnostic`, `test_unexpected_exception_records_code_bug_diagnostic_without_secret` | covered |
| Parse failure maps to audit_parse | `test_chapter_orchestrator.py:test_audit_parse_failure_records_audit_parse_diagnostic` | covered |
| Fact gaps map to fact_gap | `test_chapter_orchestrator.py:test_needs_more_facts_records_fact_gap_diagnostic` | covered |
| audit_rule_too_strict four conditions | `test_chapter_orchestrator.py:test_parseable_llm_audit_failure_after_programmatic_pass_is_audit_rule_too_strict`, `test_llm_unavailable_audit_is_not_audit_rule_too_strict` | covered |
| CLI --use-llm fail-closed: stdout empty, no deterministic fallback | `test_cli.py:test_analyze_cli_use_llm_incomplete_result_exits_without_fallback`, `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | covered |
| Missing config fails before Service | `test_cli.py:test_analyze_cli_use_llm_missing_config_fails_before_service` | covered |
| CLI timeout stderr includes llm_timeout | `test_cli.py:test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | covered |

## Overall verdict

**PASS。**

无 blocking findings。Implementation 完整实现了 plan 的 5 个 slice，failure taxonomy 正确，CLI 读取路径正确，secret hygiene 合规，测试覆盖充分。

3 个 non-blocking findings（N1 controller evidence 不一致、N2 sanitize "prompt" 可能误伤、N3 fact gap heuristic）均不影响当前 gate 的安全性和正确性，建议后续 gate 按优先级处理。

Controller smoke 显示 chapter 1 从 `llm_timeout` 改善为 `accepted`，验证了 prompt-contract calibration 的有效性。Chapter 2 仍 `llm_contract_violation`/`prompt_contract`，下一最小入口明确。
