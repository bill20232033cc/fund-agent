# MVP writer marker syntax repair code review (MiMo)

日期：2026-05-31

Gate：`MVP writer marker syntax repair gate`

角色：Gateflow code reviewer，不是 implementation worker。

## Review scope

Review target：workspace diff on branch `codex/local-reconciliation`，gate 实现变更。

Source of truth read：
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Gate plan：`docs/reviews/mvp-writer-marker-syntax-repair-plan-20260531.md`
- Plan review (MiMo)：`docs/reviews/mvp-writer-marker-syntax-repair-plan-review-mimo-20260531.md`
- Implementation evidence：`docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`
- 上一 gate controller judgment：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md`
- 变更代码：`fund_agent/fund/chapter_writer.py`、`tests/fund/test_chapter_writer.py`、`tests/services/test_chapter_orchestrator.py`、`tests/ui/test_cli.py`
- 不变代码（回归确认）：`fund_agent/services/chapter_orchestrator.py`、`fund_agent/ui/cli.py`、`tests/config/test_llm_config.py`、`tests/services/test_llm_provider.py`

## Review focus areas

### 1. Parser / allowed missing reasons / regex 未放宽

**PASS。**

- `_MISSING_MARKER_RE`（`chapter_writer.py:54`）保持 `r"<!-- missing:([a-z_]+) -->"`，未修改。
- `_invalid_marker_issues()`（`chapter_writer.py:927-959`）逻辑不变：扫描 `_COMMENT_RE` 匹配，payload 包含 `missing` 且不满足 `_MISSING_MARKER_RE.fullmatch()` 时产生 `writer:invalid_missing_marker`。
- `_parse_missing_markers()`（`chapter_writer.py:1067-1099`）逻辑不变：只接受 `_SUPPORTED_MISSING_REASONS` 交集 `chapter.missing_reasons`；未知 reason 产生 `writer:unknown_missing_reason`。
- `ChapterFactMissingReason` closed set 未扩展。
- `chapter.missing_reasons` 仍来自 Gate 1 投影的 chapter-scoped allowed set。

### 2. Prompt guidance 是否避免 Markdown code-span 污染

**PASS。**

旧 prompt（已被删除）：
```python
"声明缺口必须使用 allowed missing marker：`<!-- missing:<reason> -->`；"
"可用缺口原因：" + _json_text(chapter.missing_reasons),
```

新 prompt 由 `_missing_marker_contract_prompt()`（`chapter_writer.py:803-842`）生成，包含：

- `MISSING_MARKER_CONTRACT:` 稳定标题（非 code-span）
- `ALLOWED_MISSING_REASONS:` token list 紧邻 marker guidance
- `MISSING_MARKER_EXACT_FORM:` 标题和 `<!-- missing:{reason} -->` plain text（无反引号）
- `MISSING_MARKER_RULES:` 包含：
  - 替换 `{reason}` 规则
  - 禁止输出 placeholder（`{reason}`, `<reason>`）
  - 禁止冒号周围空格
  - 禁止大小写/翻译/全角冒号
  - 禁止反引号或 code fence 包裹
  - 禁止 marker 内加入中文说明/JSON/Markdown bullet/额外标签

当 `chapter.missing_reasons` 为空时，prompt 明确禁止输出 missing marker，但仍允许"未披露 / 数据不足 / 下一步最小验证问题"表达缺口。

旧 prompt 的 code-span 和 JSON-only 方式已完全移除（测试 `test_writer_prompt_contains_missing_marker_exact_contract_near_allowed_reasons` 断言 `"可用缺口原因：" not in prompt.user_prompt` 和 `"allowed missing marker：`<!-- missing:<reason> -->`" not in prompt.user_prompt`）。

### 3. Invalid missing marker 仍 fail-closed 并归类 invalid_marker

**PASS。**

- Writer 层：`_invalid_marker_issues()` 不变，`writer:invalid_missing_marker` issue 的 reason 仍为 `llm_contract_violation`。
- Orchestrator 层：`_INVALID_MARKER_PREFIXES`（`chapter_orchestrator.py:130-135`）包含 `"writer:invalid_missing_marker"`，`_writer_prompt_contract_diagnostic()` 用 `sum(prefix_counts.get(prefix, 0) for prefix in _INVALID_MARKER_PREFIXES)` 统计 `invalid_marker_count`。
- 测试 `test_writer_rejects_invalid_missing_marker_syntax`（`test_chapter_writer.py:474-509`）覆盖 4 种污染形态（空格/大小写/全角冒号/placeholder），全部断言 `stop_reason == "llm_contract_violation"` 和 `issue.issue_id.startswith("writer:invalid_missing_marker")`。
- 测试 `test_writer_missing_marker_issues_count_as_invalid_marker_without_raw_suffix`（`test_chapter_orchestrator.py:701-731`）覆盖 `writer:invalid_missing_marker` 和 `writer:unknown_missing_reason` 均归类为 `failure_subcategory=invalid_marker`，且 prefix 不包含 raw suffix。

### 4. candidate_facet_assertion 仍 blocked

**PASS。**

- `candidate_facet_assertion_count` 在 `_writer_prompt_contract_diagnostic()` 中固定为 `0`（writer 层不产生该 issue）。
- `_audit_prompt_contract_diagnostic()` 正确统计 audit 层 `candidate_facet_assertion_count`。
- 测试 `test_programmatic_candidate_facet_assertion_is_counted_not_accepted`（`test_chapter_orchestrator.py:746-766`）验证 candidate facet 仍阻断且 subcategory 为 `candidate_facet_assertion`。
- 本 gate 未修改任何 candidate facet 相关逻辑。

### 5. CLI / serialization / secret safety 未回退

**PASS。**

- `_llm_incomplete_message()`（`cli.py:807-832`）和 `_first_failed_chapter_summary()`（`cli.py:835-868`）未变更。
- `_sanitize_text()`（`chapter_orchestrator.py:2086-2105`）仍对 `Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`、`api_key`、`sk-`、`prompt` 做 `[redacted]` 替换。
- `serialize_chapter_prompt_contract_diagnostics()`（`chapter_orchestrator.py:603-630`）仍只输出标量/计数，不输出 prompt/draft/raw response。
- 测试 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`（`test_cli.py:1398-1441`）断言 stderr 排除 `Authorization`、`Bearer`、`sk-`、`system_prompt`、`user_prompt`、`draft_markdown`、`provider_response`。
- 测试 `test_sanitized_prompt_contract_serialization_excludes_raw_payloads`（`test_chapter_orchestrator.py:866-888`）断言序列化输出排除 10 种敏感关键词。
- 测试 `test_unexpected_exception_records_code_bug_diagnostic_without_secret`（`test_chapter_orchestrator.py:945-964`）验证含 secret 的异常消息被脱敏。

### 6. Deterministic analyze/checklist 和 missing-config fail-closed 不变

**PASS。**

- `test_llm_config.py` 全量通过，无变更。
- `test_llm_provider.py` 全量通过，无变更。
- `test_cli.py` 中 `test_analyze_cli_use_llm_missing_config_fails_before_service` 断言 exit 1、stdout 空、stderr 包含 `"missing FUND_AGENT_LLM_PROVIDER"`、Service 未被调用。
- Implementation evidence 记录 `fund-analysis analyze 006597 --report-year 2024` exit 0、`fund-analysis checklist 006597 --report-year 2024` exit 0、isolated missing-config `--use-llm` exit 1 fail-closed。

### 7. Tests / validation 是否充分

**PASS。**

Writer prompt tests（`test_chapter_writer.py`）：
- `test_writer_prompt_contains_missing_marker_exact_contract_near_allowed_reasons`：覆盖 explicit contract、allowed reasons、exact form、所有禁止规则、旧 code-span 已移除。
- `test_writer_prompt_without_missing_reasons_forbids_missing_marker`：覆盖空 allowed reasons 禁止 missing marker。
- `test_writer_prompt_requires_body_sections_and_required_output_markers`：覆盖固定结构和 required output marker guidance。

Writer parser tests（`test_chapter_writer.py`）：
- `test_writer_rejects_invalid_missing_marker_syntax`（parametrized 4 种形态）：空格、大小写、全角冒号、placeholder 未替换。
- `test_writer_parses_valid_anchor_and_missing_markers`：合法 exact marker 仍 accepted。
- `test_writer_rejects_unknown_missing_reason_marker`：未知 reason 仍 blocked。

Orchestrator tests（`test_chapter_orchestrator.py`）：
- `test_writer_missing_marker_issues_count_as_invalid_marker_without_raw_suffix`：invalid marker 和 unknown reason 均归 `invalid_marker`，prefix 不含 raw suffix。
- `test_programmatic_candidate_facet_assertion_is_counted_not_accepted`：candidate facet 仍 blocked。
- `test_sanitized_prompt_contract_serialization_excludes_raw_payloads`：脱敏序列化不含敏感信息。
- `test_accepted_chapter_has_no_prompt_contract_subcategory`：accepted 章节无 failure_subcategory。

CLI tests（`test_cli.py`）：
- `test_analyze_cli_use_llm_missing_config_fails_before_service`：missing config fail-closed。
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`：timeout fail-closed 且脱敏。

Validation matrix（implementation evidence）：
- `ruff check .` PASS
- `pytest` 200 passed（gate 相关）、1176 passed（全量），coverage 91.84%
- deterministic `analyze`/`checklist` exit 0
- isolated missing-config `--use-llm` exit 1 fail-closed
- `git diff --check` PASS

## Scope compliance

**PASS。**

变更文件符合 plan allowed files：
- `fund_agent/fund/chapter_writer.py`（prompt guidance + 新 parser checks）
- `tests/fund/test_chapter_writer.py`（新 prompt/parser tests）
- `tests/services/test_chapter_orchestrator.py`（新 orchestrator regression tests）
- `tests/ui/test_cli.py`（CLI secret safety tests 已存在，未新增变更）
- `docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`

未变更的受保护边界：
- `chapter_orchestrator.py`：无 diff（除前序 gate 已 accepted 的变更）
- `cli.py`：无 diff
- `_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()`：逻辑不变
- `ChapterFactMissingReason`：closed set 不变
- Golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态：未触及

## Non-blocking observations

1. **新增 `_required_structure_issues()` 和 `_required_output_marker_issues()` 超出 strict marker syntax repair scope**。Plan Slice A 要求"保持 `_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()` 行为不变"，但 implementation 额外新增了两个 parser check 函数。这两个函数是 writer prompt contract 加固的合理延伸（确保模型遵守固定结构和 required output marker），且不放宽任何安全边界，不阻塞本 gate。后续 gate 可评估是否需要更精确的 scope 控制。

2. **`ChapterWriteStopReason` Literal 扩展了 5 个新值**（`missing_required_structure`、`missing_required_output_marker`、`unknown_anchor`、`response_too_long`、`response_incomplete`）。这些是前序 gate 已设计但未实现的 stop reason，本 gate 补齐。不改变安全语义，不阻塞。

3. **`unknown_anchor` stop reason 从 `llm_contract_violation` 改为独立 stop reason**（`chapter_writer.py:1170`）。这是更精确的分类，orchestrator 的 `_WRITER_STOP_REASON_MAPPING` 已有对应映射。不改变 fail-closed 语义。

## 结论

**PASS。**

Implementation 严格对齐 gate plan：只修改 writer prompt guidance（从 Markdown code-span 改为 explicit contract block with allowed reasons token list），不放宽 `_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()` 或 `ChapterFactMissingReason`；invalid missing marker 仍 fail-closed 并归类 `invalid_marker`；`candidate_facet_assertion` 未被触及；CLI/serialization/secret safety 未回退；deterministic analyze/checklist 和 missing-config fail-closed 不变。测试覆盖充分（prompt contract、invalid marker 4 种污染形态、orchestrator subcategory、CLI secret safety）。新增的 `_required_structure_issues()` 和 `_required_output_marker_issues()` 属于合理的 prompt contract 加固延伸，不阻塞本 gate。
