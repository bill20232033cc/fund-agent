# MVP writer prompt contract diagnostic narrowing code review (MiMo)

日期：2026-05-31

审阅者角色：Gateflow code reviewer，不是 implementation worker。

审阅对象：workspace diff（`codex/local-reconciliation` branch），对照 gate plan、MiMo/GLM plan review、implementation evidence。

## Review scope

读取了以下文件：

- `AGENTS.md`（规则真源）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-20260531.md`（gate plan）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-mimo-20260531.md`（MiMo plan review）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-glm-20260531.md`（GLM plan review）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-implementation-evidence-20260531.md`（implementation evidence）
- `fund_agent/fund/chapter_writer.py`（workspace diff + 当前文件）
- `fund_agent/services/chapter_orchestrator.py`（workspace diff + 当前文件）
- `fund_agent/ui/cli.py`（workspace diff + 当前文件）
- `tests/fund/test_chapter_writer.py`（workspace diff）
- `tests/services/test_chapter_orchestrator.py`（workspace diff）
- `tests/ui/test_cli.py`（workspace diff）

注意：workspace diff 混有前序 accepted gate 改动（如 `ChapterRepairContext`、prompt 结构强化、`_repair_context_from_audit` 等）。以下 review 只按本 gate plan/evidence 判断新增风险，不重新审计前序 accepted gate 已接受的内容。

## 结论

**PASS**

实现正确执行了 plan 的最小脱敏诊断扩展。taxonomy/precedence 正确，issue_id_prefix_counts 剥离了 raw suffix，CLI 只输出 scalar，serialization 不含 prompt/draft/raw response/API key。tests 覆盖充分。以下按 review 重点逐项说明。

## 1. 实现是否只做脱敏诊断扩展和 failure_subcategory

**通过。**

### 本 gate 新增内容

| 变更 | 文件 | 是否属于 plan scope |
|---|---|---|
| `ChapterWriteResult` 新增 `response_chars`、`finish_reason`、`max_output_chars` 标量 | `chapter_writer.py` | ✓ Slice A |
| `_blocked_result` 传递标量 | `chapter_writer.py` | ✓ Slice A |
| `write_chapter` 传递标量到 blocked/drafted 结果 | `chapter_writer.py` | ✓ Slice A |
| `INCOMPLETE_FINISH_REASONS` 常量 | `chapter_writer.py` | ✓ Slice A |
| `_draft_from_llm_response` 新增 `response_incomplete` 检查 | `chapter_writer.py` | ✓ 诊断收窄所需 |
| `_required_structure_issues` 新增函数 | `chapter_writer.py` | ✓ 诊断收窄所需 |
| `_required_output_marker_issues` 新增函数 | `chapter_writer.py` | ✓ 诊断收窄所需 |
| `ChapterFailureCategory` / `ChapterFailureSubcategory` 类型 | `chapter_orchestrator.py` | ✓ Slice A |
| `ChapterPromptContractDiagnostic` dataclass | `chapter_orchestrator.py` | ✓ Slice A |
| `ChapterLLMRuntimeDiagnostic` dataclass | `chapter_orchestrator.py` | ✓ Slice A |
| `_primary_subcategory` 优先级选择 | `chapter_orchestrator.py` | ✓ Slice A |
| `_writer_prompt_contract_diagnostic` / `_audit_prompt_contract_diagnostic` | `chapter_orchestrator.py` | ✓ Slice A |
| `_writer_issue_id_prefix` / `_audit_issue_id_prefix` 剥离函数 | `chapter_orchestrator.py` | ✓ Slice A |
| `_writer_response_length_incomplete_count` | `chapter_orchestrator.py` | ✓ Slice A |
| `_is_candidate_facet_assertion_issue` / `_is_forbidden_phrase_issue` | `chapter_orchestrator.py` | ✓ Slice A |
| `_chapter_failure_category_from_*` 映射族 | `chapter_orchestrator.py` | ✓ Slice A |
| `_provider_runtime_stop_reason` / `_provider_runtime_category_from_exception` | `chapter_orchestrator.py` | ✓ 诊断收窄所需 |
| `_exception_result` 重构为精确 stop_reason + runtime_diagnostics | `chapter_orchestrator.py` | ✓ 诊断收窄所需 |
| `_enrich_provider_diagnostic` / `_exception_runtime_diagnostics` | `chapter_orchestrator.py` | ✓ 诊断收窄所需 |
| `serialize_chapter_prompt_contract_diagnostics` 序列化 helper | `chapter_orchestrator.py` | ✓ Slice C |
| `_first_failed_diagnostic` / `_chapter_diagnostic_row` | `chapter_orchestrator.py` | ✓ Slice C |
| `_first_failed_chapter_summary` CLI stderr 扩展 | `cli.py` | ✓ Slice B |
| `ChapterRunResult` 新增 `failure_category`、`failure_subcategory`、`prompt_contract_diagnostics`、`runtime_diagnostics` | `chapter_orchestrator.py` | ✓ Slice A |

### 前序 gate 已 accepted 的内容（不重新审计）

- `ChapterRepairContext` dataclass 和 `_repair_context_from_audit`
- writer prompt 结构强化（输出协议、required output marker 指引、candidate facet 禁止断言措辞）
- `_prompt_required_output_payload` / `_repair_context_prompt`
- `REQUIRED_BODY_SECTION_HEADINGS` / `REQUIRED_OUTPUT_MARKER_PREFIX` 常量
- `ChapterLLMRequest.repair_context` / `ChapterWriterInput.repair_context`

### 是否做了 prompt 修复或 safety contract 放松

**否。** 实现未修改 parser acceptance 行为、未放松 anchor/ITEM_RULE/candidate facet/forbidden phrase/missing semantics 边界、未新增 deterministic fallback、未让 `--use-llm` partial result 输出报告。新的 stop reason（`missing_required_structure` 等）是更精确的分类，不改变哪些输出被阻断。

## 2. Taxonomy/precedence 是否正确

**通过。**

### 子类映射验证

| Writer issue reason / prefix | Plan subcategory | 实现映射 | 正确 |
|---|---|---|---|
| `missing_required_structure` | `missing_structure` | ✓ `reason_counts.get("missing_required_structure")` | ✓ |
| `missing_required_output_marker` | `missing_required_marker` | ✓ `reason_counts.get("missing_required_output_marker")` | ✓ |
| `unknown_anchor` | `unknown_anchor` | ✓ `reason_counts + prefix_counts` 取 max | ✓ |
| `writer:invalid_anchor_marker:*` | `invalid_marker` | ✓ `_INVALID_MARKER_PREFIXES` | ✓ |
| `writer:invalid_missing_marker:*` | `invalid_marker` | ✓ `_INVALID_MARKER_PREFIXES` | ✓ |
| `writer:unknown_missing_reason:*` | `invalid_marker` | ✓ `_INVALID_MARKER_PREFIXES` | ✓ |
| `writer:evidence_line_without_anchor_marker` | `invalid_marker` | ✓ `_INVALID_MARKER_PREFIXES` | ✓ |
| `writer:forbidden_phrase:*` | `forbidden_phrase` | ✓ `_FORBIDDEN_PHRASE_PREFIX` | ✓ |
| `response_too_long` | `response_length_incomplete` | ✓ `_writer_response_length_incomplete_count` | ✓ |
| `response_incomplete` | `response_length_incomplete` | ✓ `_writer_response_length_incomplete_count` | ✓ |
| `llm_contract_violation`（无具体 issue） | `code_bug_other` | ✓ fallback | ✓ |

Audit 侧：

| Audit 来源 | Plan subcategory | 实现映射 | 正确 |
|---|---|---|---|
| programmatic C2 candidate facet | `candidate_facet_assertion` | ✓ `_is_candidate_facet_assertion_issue` | ✓ |
| programmatic C1 forbidden phrase | `forbidden_phrase` | ✓ `_is_forbidden_phrase_issue` | ✓ |

### Primary selection order 验证

`_SUBCATEGORY_PRECEDENCE` 定义为：

```python
("response_length_incomplete", "invalid_marker", "unknown_anchor",
 "missing_required_marker", "missing_structure", "candidate_facet_assertion",
 "forbidden_phrase", "code_bug_other")
```

与 plan 第 88-96 行定义一致。✓

### Accepted 章节 subcategory 为 None

`_run_single_chapter` 在 accepted 路径设置 `failure_category=None`，`failure_subcategory` 默认 `None`。✓ 测试 `test_accepted_chapter_has_no_prompt_contract_subcategory` 验证。✓

### Provider timeout 不误归 prompt_contract

`_provider_runtime_stop_reason` 将 timeout 映射为 `"llm_timeout"`，`_chapter_failure_category_from_stop_reason` 将 `"llm_timeout"` 映射为 `"llm_timeout"`（非 `"prompt_contract"`）。✓ 测试 `test_provider_timeout_has_no_prompt_contract_subcategory` 验证。✓

## 3. issue_id_prefix_counts 是否剥离 raw suffix

**通过。**

### Writer issue id prefix 提取

`_writer_issue_id_prefix` 逻辑：

```python
if not issue_id.startswith("writer:"):
    return issue_id.split(":", 1)[0]  # e.g. "missing_required_structure" → "missing_required_structure"
parts = issue_id.split(":")
if len(parts) >= 2:
    return ":".join(parts[:2])  # e.g. "writer:unknown_anchor:XXX" → "writer:unknown_anchor"
return issue_id
```

- `writer:unknown_anchor:<anchor_id>` → `writer:unknown_anchor` ✓（raw anchor id 剥离）
- `writer:missing_required_output_marker:<index>` → `writer:missing_required_output_marker` ✓
- `writer:missing_required_structure:<heading>` → `writer:missing_required_structure` ✓
- `writer:forbidden_phrase:<phrase>` → `writer:forbidden_phrase` ✓（raw phrase 剥离）
- `writer:invalid_anchor_marker:<marker>` → `writer:invalid_anchor_marker` ✓
- `writer:unknown_missing_reason:<reason>` → `writer:unknown_missing_reason` ✓（raw reason 剥离）

### Audit issue id prefix 提取

`_audit_issue_id_prefix` 逻辑：

```python
parts = issue_id.split(":")
if parts[0] == "programmatic" and len(parts) >= 2:
    return ":".join(parts[:2])  # "programmatic:C1:phrase:abcdef" → "programmatic:C1"
if parts[0] == "llm" and len(parts) >= 3:
    return ":".join(parts[:3])  # "llm:C2:hash" → "llm:C2:hash"
return parts[0]
```

- `programmatic:C1:phrase:<hash>` → `programmatic:C1` ✓（raw hash 剥离）
- `programmatic:C2:facet:<facet_text>` → `programmatic:C2` ✓（raw facet text 剥离）

### 测试验证

- `test_writer_diagnostic_prefix_counts_strip_raw_suffixes`：验证 `writer:unknown_anchor` prefix，不含 raw anchor id。✓
- `test_writer_forbidden_phrase_subcategory_remains_blocked`：验证 `writer:forbidden_phrase` prefix，不含 raw phrase。✓
- `test_writer_unknown_missing_reason_counts_as_invalid_marker_without_raw_suffix`：验证不含 raw reason。✓
- `test_programmatic_candidate_facet_assertion_is_counted_not_accepted`：验证不含 facet text。✓
- `test_sanitized_prompt_contract_serialization_excludes_raw_payloads`：验证序列化输出不含敏感文本。✓

## 4. CLI 是否只输出 scalar，不泄露 prompt/draft/provider response

**通过。**

`_first_failed_chapter_summary` 输出的字段：

- `first_failed_chapter_id=<int>` — scalar
- `first_failed_status=<enum>` — scalar
- `first_failed_stop_reason=<enum>` — scalar
- `first_failed_category=<enum>` — scalar
- `first_failed_subcategory=<enum>` — scalar

使用 `getattr` 安全访问，不读取 prompt/draft/raw_response 字段。✓

测试 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证 stderr 不含 `Authorization`、`Bearer`、report markdown。✓

## 5. Serialization 是否不含 prompt/draft/raw response/API key/Auth header

**通过。**

`serialize_chapter_prompt_contract_diagnostics` 输出的 payload 字段：

```python
{
    "schema_version": str,
    "fund_code": str,
    "report_year": int,
    "orchestration_status": str,
    "first_failed": {chapter_id, phase, attempt_index, category, subcategory},
    "chapter_phase_matrix": [{
        chapter_id, status, stop_reason, failure_category, failure_subcategory,
        attempt_count, phases: [{schema_version, chapter_id, phase, attempt_index,
        primary_subcategory, issue_reason_counts, issue_id_prefix_counts,
        required_structure_missing_count, required_output_missing_count,
        unknown_anchor_count, invalid_marker_count, forbidden_phrase_count,
        candidate_facet_assertion_count, response_length_incomplete_count,
        response_chars, max_output_chars, finish_reason, accepted_draft_present}]
    }]
}
```

所有值为 str/int/bool/dict[str,int]/None，不含 prompt、draft、raw response、API key 或 Auth header。✓

`runtime_diagnostics` 不包含在序列化 payload 中（只包含 `prompt_contract_diagnostics`）。✓

测试 `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` 验证不含 `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、`accepted_draft.markdown`、`Authorization`、`Bearer`、`sk-`。✓

## 6. Deterministic analyze/checklist、missing-config fail-closed 行为是否保持

**通过。**

- Implementation evidence 记录：`uv run fund-analysis analyze 006597 --report-year 2024` exit 0 ✓
- Implementation evidence 记录：`uv run fund-analysis checklist 006597 --report-year 2024` exit 0 ✓
- Implementation evidence 记录：isolated missing-config `--use-llm` exit 1，stdout empty，stderr `missing FUND_AGENT_LLM_PROVIDER` ✓
- `_draft_from_llm_response` 的检查顺序不变：empty → incomplete → too_long → invalid_marker → structure → required_output → anchor → missing → evidence_line → forbidden_phrase。✓
- 新增的 `_required_structure_issues` 和 `_required_output_marker_issues` 只在 `_draft_from_llm_response` 中增加额外 issue，不改变已有 issue 的生成逻辑。✓

## 7. Tests 是否覆盖足够

**通过。**

### Writer tests（`test_chapter_writer.py`）

| 测试 | 覆盖内容 |
|---|---|
| `test_writer_prompt_requires_body_sections_and_required_output_markers` | prompt 包含固定结构和 marker 指引 |
| `test_writer_blocks_incomplete_finish_reason_without_accepting_partial_text` | `response_incomplete` 阻断（length/content_filter） |
| `test_writer_blocks_missing_required_body_section_before_audit` | `missing_required_structure` 阻断 |
| `test_writer_blocks_missing_required_output_marker_before_audit` | `missing_required_output_marker` 阻断 |
| `test_repair_context_is_rendered_into_writer_prompt_without_extra_payload` | repair context 进入 prompt |
| `test_llm_request_carries_typed_repair_context` | LLM request 携带 repair context |

已有测试更新：

- `test_writer_rejects_response_over_max_output_chars_without_truncation`：stop_reason 从 `llm_contract_violation` 更新为 `response_too_long` ✓
- `test_writer_rejects_unknown_anchor_reference`：stop_reason 从 `llm_contract_violation` 更新为 `unknown_anchor` ✓
- `_valid_chapter_markdown` helper 更新为包含 required_output marker ✓

### Orchestrator tests（`test_chapter_orchestrator.py`）

| 测试 | 覆盖内容 |
|---|---|
| `test_provider_runtime_exceptions_map_to_precise_stop_reason` | timeout/rate_limit/malformed/network → 精确 stop reason |
| `test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate` | timeout 诊断补齐 + 不 regenerate |
| `test_writer_prompt_contract_blocked_records_diagnostic_category` | writer blocked → prompt_contract + subcategory |
| `test_writer_prompt_contract_subcategory_mapping` (parametrize) | 5 个 stop_reason → subcategory 映射 |
| `test_writer_diagnostic_prefix_counts_strip_raw_suffixes` | prefix 剥离 raw suffix |
| `test_writer_forbidden_phrase_subcategory_remains_blocked` | forbidden_phrase 阻断 + 诊断 |
| `test_writer_unknown_missing_reason_counts_as_invalid_marker_without_raw_suffix` | unknown missing reason → invalid_marker |
| `test_accepted_chapter_has_no_prompt_contract_subcategory` | accepted → None |
| `test_programmatic_candidate_facet_assertion_is_counted_not_accepted` | candidate facet 计数不接受 |
| `test_programmatic_forbidden_phrase_is_counted_not_accepted` | audit forbidden phrase 诊断 |
| `test_provider_timeout_has_no_prompt_contract_subcategory` | timeout → 无 prompt-contract subcategory |
| `test_unmapped_writer_contract_issue_is_code_bug_other` | unmapped → code_bug_other |
| `test_candidate_facet_precedence_beats_forbidden_phrase_only_by_plan_order` | precedence 验证 |
| `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` | 序列化安全 |
| `test_audit_parse_failure_records_audit_parse_diagnostic` | audit_parse 分类 |
| `test_parseable_llm_audit_failure_after_programmatic_pass_is_audit_rule_too_strict` | audit_rule_too_strict 分类 |
| `test_needs_more_facts_records_fact_gap_diagnostic` | fact_gap 分类 |
| `test_unexpected_exception_records_code_bug_diagnostic_without_secret` | code_bug + 脱敏 |
| `test_llm_unavailable_audit_is_not_audit_rule_too_strict` | LLM_UNAVAILABLE 不误归 |
| `test_regenerate_request_contains_previous_failure_context` | regenerate 携带 repair context |
| `test_required_corrections_are_deterministic_for_known_issue_patterns` | deterministic correction |
| `test_required_corrections_sanitize_unknown_issue_message` | correction 脱敏 |
| `test_repairable_audit_failure_retries_and_second_pass_accepts` (updated) | repair context 进入第二轮 |
| `test_repair_budget_exhausted_returns_failed_stop_reason` (updated) | 使用显式 audit fixture |
| `test_max_repair_attempts_zero_does_not_retry_after_audit_failure` (updated) | 使用显式 audit fixture |
| `test_fail_fast_false_continues_and_returns_partial` (updated) | 使用显式 audit fixture |
| `test_h2_conclusion_extraction_stops_before_next_h2` (updated) | H2 不再作为 accepted 结构 |
| `test_fallback_conclusion_uses_first_three_non_empty_lines` (updated) | 固定结论 heading 优先 |

### CLI tests（`test_cli.py`）

| 测试 | 覆盖内容 |
|---|---|
| `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | timeout fail-closed + stderr scalar + 脱敏 |

已有测试更新：

- `test_analyze_cli_use_llm_missing_config_fails_before_service`：显式清理 env vars ✓

### 覆盖率

Implementation evidence 记录：1169 passed，total coverage 91.83%。✓

## Minor observations（非 blocking）

### O1. `_primary_subcategory` 的 `has_any_counter` 参数不影响结果

`_primary_subcategory` 最后一行：

```python
return "code_bug_other" if not has_any_counter else "code_bug_other"
```

两个分支返回相同值。`has_any_counter` 参数不影响任何执行路径。这不是 bug——当所有计数为 0 时，无论 `has_any_counter` 为 True 迌是 False，都应返回 `code_bug_other`（对应 plan 的"no issue counters despite llm_contract_violation"）。但条件表达式可以简化为 `return "code_bug_other"`。建议后续清理时简化。

### O2. `_audit_runtime_diagnostic` 存储 `len(raw_response)` 为 response_chars

`_audit_runtime_diagnostic` 中：

```python
response_chars=len(audit_result.llm.raw_response) if audit_result.llm.raw_response else None,
```

存储的是 raw_response 的**长度**（int），不是 raw_response 内容。`serialize_chapter_prompt_contract_diagnostics` 不序列化 `runtime_diagnostics`。安全，但 `response_chars` 字段名可能被误解为包含响应内容。当前实现符合 plan 要求。

### O3. `_candidate_facet_assertion` 仅在 audit 阶段出现

Plan 已注明此点（MiMo plan review O1）。实现正确：`_writer_prompt_contract_diagnostic` 将 `candidate_facet_assertion_count` 固定为 0（writer 阶段不检测），`_audit_prompt_contract_diagnostic` 从 audit issues 推导。时序正确。

### O4. README 未更新

Implementation evidence 记录"No README update was made"。workspace git status 显示 `fund_agent/config/README.md` 和 `fund_agent/fund/README.md` 有变更，但这些变更可能来自前序 gate 或独立的文档同步。本 gate 的诊断扩展是内部 Service 层变更，不改变用户命令或公共接口，不强制要求 README 更新。

## Blocking Findings

无。

## Verdict

**PASS** — 实现正确执行了 plan 的最小脱敏诊断扩展。taxonomy/precedence 正确，issue_id_prefix_counts 剥离了 raw suffix，CLI 只输出 scalar，serialization 不含 prompt/draft/raw response/API key。tests 覆盖充分。4 个 minor observations 均为非阻塞建议。
