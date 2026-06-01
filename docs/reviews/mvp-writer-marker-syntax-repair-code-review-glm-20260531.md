# MVP writer marker syntax repair code review (GLM)

日期：2026-05-31

Reviewer：GLM（code reviewer，不是 implementation worker）

Gate：`MVP writer marker syntax repair gate`

## 审查范围

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-writer-marker-syntax-repair-plan-20260531.md`（gate plan）
- `docs/reviews/mvp-writer-marker-syntax-repair-plan-review-glm-20260531.md`（GLM plan review）
- `docs/reviews/mvp-writer-marker-syntax-repair-plan-review-mimo-20260531.md`（MiMo plan review）
- `docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`（implementation evidence）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md`（上一 gate controller judgment）
- `fund_agent/fund/chapter_writer.py`（writer 实现，含 prompt 构造和 marker parser）
- `fund_agent/services/chapter_orchestrator.py`（Service 层编排和诊断）
- `fund_agent/ui/cli.py`（CLI 入口）
- `tests/fund/test_chapter_writer.py`（writer 测试）
- `tests/services/test_chapter_orchestrator.py`（orchestrator 测试）
- `tests/ui/test_cli.py`（CLI 测试）
- workspace diff（`git diff HEAD`）

未运行真实 provider，未修改代码。

## 结论

**PASS** — 无 blocking findings。

实现严格对齐 plan，只修改了 prompt guidance 文本构造，未触碰 parser regex、allowed missing reasons closed set、candidate facet、CLI/serialization/secret safety。测试覆盖了 plan 要求的所有场景。以下为逐项审查结果。

---

## 1. 是否只做 marker syntax prompt repair，没有放宽 `_MISSING_MARKER_RE`、`_invalid_marker_issues`、`_parse_missing_markers`、allowed missing reasons

**只做 prompt repair。**

核心变更为新增 `_missing_marker_contract_prompt()` 函数（`chapter_writer.py:803-842`），该函数替代了旧的内联 Markdown code-span guidance。函数签名接收 `missing_reasons: tuple[ChapterFactMissingReason, ...]`，返回 prompt contract 文本片段。

经代码验证：

- `_MISSING_MARKER_RE = r"<!-- missing:([a-z_]+) -->"`（`chapter_writer.py:54`）—— regex 未变。
- `_invalid_marker_issues()`（`chapter_writer.py:927-959`）—— 扫描逻辑未变：遍历 `_COMMENT_RE` 匹配，对 payload 含 `"missing"` 且不满足 `_MISSING_MARKER_RE.fullmatch()` 的 comment 产生 `writer:invalid_missing_marker:<offset>` / `llm_contract_violation`。
- `_parse_missing_markers()`（`chapter_writer.py:1067-1099`）—— closed-set 校验未变：先检查 `_SUPPORTED_MISSING_REASONS`（从 `ChapterFactMissingReason` Literal 提取的 `frozenset`），再检查 `allowed`（来自 `chapter.missing_reasons`），两层 fail-closed。
- `ChapterFactMissingReason` 枚举未修改。
- `_SUPPORTED_MISSING_REASONS` frozenset 未修改。

diff 中涉及以上符号的行均为 unchanged context lines（diff 上下文），无实质修改。

`build_chapter_prompt()`（`chapter_writer.py:434`）调用 `_missing_marker_contract_prompt(chapter.missing_reasons)` 替换了旧的两行内联 guidance：

```python
# 已移除（旧）
"写作要求：每条证据行前后必须包含对应 HTML marker；格式为 "
"`<!-- anchor:<anchor_id> -->`。声明缺口必须使用 `<!-- missing:<reason> -->`；",
"可用缺口原因：" + _json_text(chapter.missing_reasons),
```

替换为新的 contract block 调用。这是唯一的 prompt repair 变更。

## 2. Prompt guidance 是否避免 Markdown code-span 污染，并包含 allowed reasons token list、禁止规则

**避免了 code-span 污染，包含所有要求元素。**

`_missing_marker_contract_prompt()` 的非空分支（`chapter_writer.py:828-842`）输出：

```text
MISSING_MARKER_CONTRACT:
ALLOWED_MISSING_REASONS: field_missing, ...
MISSING_MARKER_EXACT_FORM:
<!-- missing:{reason} -->
MISSING_MARKER_RULES:
- Replace {reason} with exactly one token from ALLOWED_MISSING_REASONS.
- Do not output {reason}, <reason>, or any placeholder.
- Do not add spaces around the colon.
- Do not change case, translate missing, or use a fullwidth colon.
- Do not wrap the marker in backticks or code fences.
- Do not add Chinese explanation, JSON, Markdown bullet text, or extra labels inside the marker.
```

逐项确认：

| Plan 要求 | 实现 | 覆盖 |
|---|---|---|
| 避免 Markdown code-span | `<!-- missing:{reason} -->` 不在反引号中 | ✅ |
| allowed reasons token list 紧邻 marker block | `ALLOWED_MISSING_REASONS:` 紧接 `MISSING_MARKER_EXACT_FORM:` | ✅ |
| placeholder 替换规则 | `Replace {reason} with exactly one token from ALLOWED_MISSING_REASONS.` | ✅ |
| 禁止输出 placeholder | `Do not output {reason}, <reason>, or any placeholder.` | ✅ |
| 禁止空格污染 | `Do not add spaces around the colon.` | ✅ |
| 禁止大小写/翻译/全角冒号 | `Do not change case, translate missing, or use a fullwidth colon.` | ✅ |
| 禁止反引号/code fence | `Do not wrap the marker in backticks or code fences.` | ✅ |
| 禁止 marker 内加入说明/JSON/标签 | `Do not add Chinese explanation, JSON, Markdown bullet text, or extra labels inside the marker.` | ✅ |
| 空 allowed reasons 禁止 marker | 空分支输出 `ALLOWED_MISSING_REASONS: none` + `Do not output any missing marker in this chapter.` | ✅ |

测试验证（`test_chapter_writer.py`）：

- `test_writer_prompt_contains_missing_marker_exact_contract_near_allowed_reasons`（line 177-208）：断言所有上述元素存在，且旧 code-span 模式 `可用缺口原因：` 和 `` `allowed missing marker：`<!-- missing:<reason> -->` `` 不在 prompt 中。
- `test_writer_prompt_without_missing_reasons_forbids_missing_marker`（line 211-233）：断言空 reasons 时 `MISSING_MARKER_EXACT_FORM:` 不出现，禁止 marker 语句出现。

## 3. Invalid missing marker 仍 fail-closed 并归类 invalid_marker

**仍 fail-closed。**

Parser 路径完全未变：

1. `_invalid_marker_issues()` 对所有 HTML comment 中的 `missing` 关键词做 regex 校验。
2. `_parse_missing_markers()` 做 closed-set + chapter allowed set 双层校验。
3. 两者均产生 `llm_contract_violation` stop reason。

测试验证：

- `test_writer_rejects_invalid_missing_marker_syntax`（`test_chapter_writer.py:474-509`）：parametrized 4 种污染形态（spacing、case、fullwidth colon、placeholder），全部断言 `status == "blocked"`、`stop_reason == "llm_contract_violation"`、`draft is None`、`issue_id.startswith("writer:invalid_missing_marker")`。
- `test_writer_missing_marker_issues_count_as_invalid_marker_without_raw_suffix`（`test_chapter_orchestrator.py:701-731`）：parametrized unknown_reason 和 spacing 污染，断言 `failure_subcategory == "invalid_marker"`、`invalid_marker_count == 1`、raw suffix 不在 `issue_id_prefix_counts`。

## 4. candidate_facet_assertion 仍 blocked

**仍 blocked。**

`build_chapter_prompt()` 中 candidate facet 相关 prompt 行未修改（`chapter_writer.py:438-442`）。`_draft_from_llm_response()` 中无 candidate facet 相关 parser 变更。

测试验证：

- `test_programmatic_candidate_facet_assertion_is_counted_not_accepted`（`test_chapter_orchestrator.py:746-766`）：断言 `status == "failed"`、`failure_subcategory == "candidate_facet_assertion"`、`candidate_facet_assertion_count > 0`。

## 5. CLI/serialization/secret safety 未回退

**未回退。**

CLI 测试验证：

- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`（`test_cli.py:1398-1441`）：断言 `exit_code == 1`、`stdout == ""`、stderr 包含 safe scalars（`first_failed_chapter_id`、`first_failed_stop_reason`、`first_failed_category`），且 `Authorization`、`Bearer`、`sk-`、`system_prompt`、`user_prompt`、`draft_markdown`、`provider_response` 不在 stderr。

Orchestrator serialization 测试验证：

- `test_sanitized_prompt_contract_serialization_excludes_raw_payloads`（`test_chapter_orchestrator.py:866-888`）：断言 `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、`provider_response`、`accepted_draft.markdown`、`### 结论要点`、`Authorization`、`Bearer`、`sk-` 不在序列化 payload 中。

## 6. Deterministic analyze/checklist 和 missing-config fail-closed 不变

**不变。**

Implementation evidence 记录：

- `uv run fund-analysis analyze 006597 --report-year 2024` → PASS, exit 0
- `uv run fund-analysis checklist 006597 --report-year 2024` → PASS, exit 0
- isolated missing-config `--use-llm` → PASS fail-closed, exit 1, stdout empty

Prompt repair 只改变 LLM prompt 文本，不影响确定性路径。`build_chapter_prompt()` 在 `mode="llm"` 和 `mode="prompt_only"` 路径都会构造 prompt，但 deterministic analyze/checklist 不调用 writer，不经过此路径。

## 7. Tests/validation 是否充分

**充分。**

| 测试场景 | 测试文件 | 覆盖 |
|---|---|---|
| prompt 包含 MISSING_MARKER_CONTRACT block + allowed reasons token list | `test_chapter_writer.py:177-208` | ✅ |
| prompt 包含所有禁止规则（placeholder、spacing、case、translation、backtick、code fence） | 同上 | ✅ |
| prompt 旧 code-span 模式已移除 | 同上 | ✅ |
| 空 allowed reasons 禁止 missing marker | `test_chapter_writer.py:211-233` | ✅ |
| 4 种污染形态仍 fail-closed（spacing、case、fullwidth、placeholder） | `test_chapter_writer.py:474-509` | ✅ |
| unknown reason 仍 blocked | `test_chapter_writer.py:684-705`（已有，保持） | ✅ |
| valid exact missing marker 仍 accepted | `test_chapter_writer.py:423-448`（已有，保持） | ✅ |
| orchestrator invalid_marker subcategory 归类 + raw suffix 剥离 | `test_chapter_orchestrator.py:701-731` | ✅ |
| candidate facet assertion 仍 blocked | `test_chapter_orchestrator.py:746-766`（已有，保持） | ✅ |
| serialized diagnostics 排除 raw payload | `test_chapter_orchestrator.py:866-888`（已有，保持） | ✅ |
| CLI fail-closed stdout empty + safe scalars + no secret | `test_cli.py:1398-1441`（已有，保持） | ✅ |

## Non-blocking observations

1. **`{reason}` 占位符在 prompt 文本中是字面量**。`_missing_marker_contract_prompt()` 使用普通字符串拼接（`"\n".join(...)`），`{reason}` 不会被 Python 格式化引擎替换。这是正确的——占位符意在让 LLM 看到 exact form 模板。无需改为 `<REASON>` 等替代形式。

2. **`Do not output {reason}, <reason>, or any placeholder.`** 同时禁止了花括号和尖括号两种 placeholder 形式。这是合理的——旧 guidance 使用 `<reason>`（尖括号），新 guidance 使用 `{reason}`（花括号）作为 exact form 占位符，两者都应被禁止出现在输出中。

3. **测试断言粒度适当**。`test_writer_prompt_contains_missing_marker_exact_contract_near_allowed_reasons` 使用 `assert "KEY_PHRASE" in prompt.user_prompt` 而非全文本精确匹配，允许后续小幅 prompt 调整不需同步修改测试。符合 GLM plan review 的 non-blocking observation #5 建议。

---

**审查完毕。结论：PASS。无 blocking findings。**

📢 Code review 完成，结论 PASS，实现严格对齐 plan 且安全边界完整保持。
