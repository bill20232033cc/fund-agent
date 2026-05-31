# MVP writer prompt contract diagnostic narrowing code review (GLM)

日期：2026-05-31

审阅者角色：Gateflow code reviewer（GLM），不是 implementation worker。

审阅对象：`MVP writer prompt contract diagnostic narrowing gate` workspace 实现。

## Review scope

读取了以下文件：

- `AGENTS.md`（规则真源）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-20260531.md`（本 gate plan）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-mimo-20260531.md`（MiMo plan review）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-glm-20260531.md`（GLM plan review）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-implementation-evidence-20260531.md`（实现证据）
- `fund_agent/fund/chapter_writer.py`（writer primitive，全文）
- `fund_agent/services/chapter_orchestrator.py`（orchestrator，全文 + diff）
- `fund_agent/ui/cli.py`（CLI 入口，全文 + diff）
- `tests/services/test_chapter_orchestrator.py`（orchestrator 测试，全文）
- `tests/ui/test_cli.py`（CLI 测试，全文）

## 结论

**PASS**

实现严格遵循 plan 三 slice 设计，只做脱敏诊断扩展和 `failure_subcategory`，不做 prompt 修复或 safety contract 放松。安全边界完整，taxonomy 和 precedence 正确，敏感信息保护充分。以下为逐项分析和非阻塞观察。

## 1. 实现范围——只做脱敏诊断，不做 prompt 修复或 safety contract 放松

**通过。**

workspace diff 混有前序 accepted gate（prompt-contract calibration）的改动，包括 `ChapterLLMRuntimeDiagnostic`、`ChapterFailureCategory`、provider runtime 异常映射、write-audit-repair loop 等。这些不属于本 gate plan scope，是已接受的历史实现。本 gate 新增的核心改动为：

- `ChapterPromptContractDiagnostic` dataclass（`chapter_orchestrator.py:195-239`）：纯加法 typed 诊断结构。
- `ChapterFailureSubcategory` Literal（`chapter_orchestrator.py:88-97`）：8 个子类枚举。
- `_SUBCATEGORY_PRECEDENCE`（`chapter_orchestrator.py:137-146`）：固定优先级元组。
- `_INVALID_MARKER_PREFIXES`、`_FORBIDDEN_PHRASE_PREFIX`（`chapter_orchestrator.py:130-136`）：用于安全分类。
- `_writer_prompt_contract_diagnostic()`（`chapter_orchestrator.py:1471-1530`）：从 writer 失败派生子类。
- `_audit_prompt_contract_diagnostic()`（`chapter_orchestrator.py:1533-1588`）：从 audit 失败派生子类。
- `_primary_subcategory()`（`chapter_orchestrator.py:1591-1635`）：按固定优先级选择主子类。
- `_writer_issue_id_prefix()`（`chapter_orchestrator.py:1677-1695`）：剥离 raw suffix。
- `serialize_chapter_prompt_contract_diagnostics()`（`chapter_orchestrator.py:603-630`）：安全序列化。
- CLI `_first_failed_chapter_summary()`（`cli.py:835-868`）：只输出 scalar。

未修改 writer prompt 文本、parser acceptance 行为、auditor 安全规则、证据锚点、ITEM_RULE、candidate facet 断言阻断、forbidden phrase 阻断、missing semantics、deterministic fallback 或 provider config/auth。

## 2. Taxonomy / Precedence 正确性

**通过。**

逐条对照 plan taxonomy 与实现：

| Plan subcategory | 代码 `_SUBCATEGORY_PRECEDENCE` | 映射正确 |
|---|---|---|
| `response_length_incomplete` | 第 1 | ✓ |
| `invalid_marker` | 第 2 | ✓ |
| `unknown_anchor` | 第 3 | ✓ |
| `missing_required_marker` | 第 4 | ✓ |
| `missing_structure` | 第 5 | ✓ |
| `candidate_facet_assertion` | 第 6 | ✓ |
| `forbidden_phrase` | 第 7 | ✓ |
| `code_bug_other` | 第 8（兜底） | ✓ |

`_primary_subcategory()`（`chapter_orchestrator.py:1630-1635`）遍历 `_SUBCATEGORY_PRECEDENCE` 跳过 `code_bug_other`，按计数 > 0 返回首个命中子类；全部无命中时返回 `code_bug_other`。逻辑正确、确定性、无歧义。

### accepted 章节 subcategory 为 None

`ChapterRunResult.failure_subcategory` 默认 `None`（`chapter_orchestrator.py:422`）。accepted 章节的 `ChapterRunResult` 构造处未设置 `failure_subcategory`（`chapter_orchestrator.py:954-964`），保持 `None`。**正确。**

### provider timeout 不误归 prompt_contract

`_exception_result()` 不设置 `prompt_contract_diagnostics`（`chapter_orchestrator.py:1072-1083`），`failure_subcategory` 保持 `None`。`_chapter_failure_category_from_exception()` 将 timeout 映射为 `llm_timeout` 而非 `prompt_contract`。**正确。**

测试覆盖：`test_provider_timeout_has_no_prompt_contract_subcategory` 验证 timeout 结果 `failure_subcategory is None`、`prompt_contract_diagnostics == ()`。

## 3. issue_id_prefix_counts 剥离 raw suffix

**通过。**

`_writer_issue_id_prefix()`（`chapter_orchestrator.py:1677-1695`）：

```python
if not issue_id.startswith("writer:"):
    return issue_id.split(":", 1)[0]
parts = issue_id.split(":")
if len(parts) >= 2:
    return ":".join(parts[:2])
return issue_id
```

验证关键 case：

- `writer:unknown_anchor:actual-anchor-id` → `writer:unknown_anchor`（剥离 raw anchor id）
- `writer:invalid_anchor_marker:123` → `writer:invalid_anchor_marker`（剥离位置）
- `writer:forbidden_phrase:0` → `writer:forbidden_phrase`（剥离 phrase index）
- `writer:unknown_missing_reason:unknown_reason` → `writer:unknown_missing_reason`（剥离 raw reason）
- `writer:llm_contract_violation` → `writer:llm_contract_violation`（无 suffix 时保持）
- 非 `writer:` 前缀 → 只保留第一段

**满足 plan 要求：** 不得包含 raw anchor id、missing reason value、facet text、forbidden phrase text、required output item text 或 message snippets。

`_audit_issue_id_prefix()`（`chapter_orchestrator.py:1718-1738`）对 programmatic/llm audit issue id 同理剥离。

测试覆盖：
- `test_writer_diagnostic_prefix_counts_strip_raw_suffixes` 验证 `issue_id_prefix_counts == {"writer:unknown_anchor": 1}`，不包含 raw anchor。
- `test_writer_forbidden_phrase_subcategory_remains_blocked` 验证 `"建议买入" not in str(diagnostic.issue_id_prefix_counts)`。
- `test_writer_unknown_missing_reason_counts_as_invalid_marker_without_raw_suffix` 验证 raw reason 不出现。

## 4. CLI 只输出 scalar，不泄露敏感信息

**通过。**

`_first_failed_chapter_summary()`（`cli.py:835-868`）只输出 5 个 `key=value` 标量：`first_failed_chapter_id`、`first_failed_status`、`first_failed_stop_reason`、`first_failed_category`、`first_failed_subcategory`。使用 `getattr()` 防御性读取，缺失时输出 `"unknown"`。

**不包含：** prompt 文本、draft markdown、provider response、issue message、anchor id、facet text、forbidden phrase。

测试覆盖：
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证 stderr 包含 `first_failed_subcategory=unknown` 且不包含 `Authorization`、`Bearer`。
- `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` 验证 stdout 为空。

## 5. Serialization 不含 full prompt / draft / raw response / API key / Auth header

**通过。**

`serialize_chapter_prompt_contract_diagnostics()`（`chapter_orchestrator.py:603-630`）构造的 payload 包含：
- `schema_version`、`fund_code`、`report_year`、`orchestration_status`（字符串/整数）
- `first_failed`：通过 `_first_failed_diagnostic()` 读取 `chapter_id`、`phase`、`attempt_index`、`category`、`subcategory`
- `chapter_phase_matrix`：通过 `_chapter_diagnostic_row()` 读取 `chapter_id`、`status`、`stop_reason`、`failure_category`、`failure_subcategory`、`attempt_count`、`phases`

`_prompt_contract_diagnostic_payload()`（`chapter_orchestrator.py:2377-2411`）只输出 `ChapterPromptContractDiagnostic` 的字段，全部为字符串、整数和布尔值。

**不包含：** `accepted_draft`、`accepted_conclusion`、`prompt`（`ChapterWriterPrompt`）、`markdown`（`ChapterDraft.markdown`）、`raw_response`（`ChapterLLMResponse.text`）、API key、Authorization header。

`_sanitize_text()`（`chapter_orchestrator.py:2086-2105`）在 runtime diagnostic message 中清除 `Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`、`api_key`、`sk-`、`prompt`。

测试覆盖：
- `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` 验证 payload 不包含 `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、`accepted_draft.markdown`、`### 结论要点`、`Authorization`、`Bearer`、`sk-`。

## 6. Deterministic analyze/checklist 行为保持

**通过。**

本 gate 新增代码全部在 `--use-llm` 路径内：

- `ChapterPromptContractDiagnostic`、`ChapterFailureSubcategory`、`_writer_prompt_contract_diagnostic()` 等只在 writer/auditor blocked 路径中构造。
- CLI `_first_failed_chapter_summary()` 只在 `_llm_incomplete_message()` 中调用，该函数只在 `use_llm=True` 且 `report_markdown is None` 时触发。
- 默认 `analyze` 和 `checklist` 命令的代码路径未改变。

Evidence 验证：`deterministic-analyze` exit 0、stdout 24636 bytes；`deterministic-checklist` exit 0、stdout 1544 bytes。**行为不变。**

### Missing-config fail-closed

`missing-config-use-llm` 测试（evidence）验证 exit 1、stdout empty、stderr 包含 `missing FUND_AGENT_LLM_PROVIDER`。CLI 测试 `test_analyze_cli_use_llm_missing_config_fails_before_service` 同样验证。**正确。**

## 7. Tests 覆盖充分性

**通过。**

### Orchestrator 测试（`test_chapter_orchestrator.py`）

本 gate 新增/修改的测试：

| 测试 | 覆盖 |
|---|---|
| `test_writer_prompt_contract_blocked_records_diagnostic_category` | writer blocked → `prompt_contract` + `missing_required_marker` |
| `test_writer_prompt_contract_subcategory_mapping`（parametrize 5 case） | 5 个子类正向映射 |
| `test_writer_diagnostic_prefix_counts_strip_raw_suffixes` | prefix 剥离不含 raw suffix |
| `test_writer_forbidden_phrase_subcategory_remains_blocked` | forbidden phrase 只计数仍阻断 |
| `test_writer_unknown_missing_reason_counts_as_invalid_marker_without_raw_suffix` | unknown missing reason → invalid_marker |
| `test_accepted_chapter_has_no_prompt_contract_subcategory` | accepted 章节无 subcategory |
| `test_programmatic_candidate_facet_assertion_is_counted_not_accepted` | candidate facet 只计数仍阻断 |
| `test_programmatic_forbidden_phrase_is_counted_not_accepted` | audit forbidden phrase 只计数 |
| `test_provider_timeout_has_no_prompt_contract_subcategory` | timeout 不产生 prompt-contract subcategory |
| `test_unmapped_writer_contract_issue_is_code_bug_other` | 无可分类 issue → `code_bug_other` |
| `test_candidate_facet_precedence_beats_forbidden_phrase_only_by_plan_order` | precedence 验证 |
| `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` | 序列化脱敏 |

覆盖了 plan 要求的所有维度：8 个子类映射、accepted 为 None、provider timeout 不误归、unmapped → code_bug_other、precedence 优先级、prefix 剥离、序列化脱敏、candidate facet 只计数、forbidden phrase 只计数。

### CLI 测试（`test_cli.py`）

| 测试 | 覆盖 |
|---|---|
| `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | timeout fail-closed + scalar 输出 + 敏感信息排除 |
| `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` | incomplete fail-closed + 无 deterministic fallback |

`_FakeChapterRunResult` 新增 `failure_subcategory` 字段，`_TimeoutLLMService` 使用 `failure_subcategory=None` 模拟 timeout 场景。覆盖充分。

### 缺失覆盖观察（非阻塞）

- `response_incomplete`（`finish_reason` in INCOMPLETE_FINISH_REASONS）在 parametrize 中未单独覆盖，但 `_writer_response_length_incomplete_count()` 逻辑简单（`reason_counts.get("response_incomplete", 0) + finish_reason 检查 + chars > max 检查`），且 `test_writer_prompt_contract_subcategory_mapping` 覆盖了 `response_too_long`，间接覆盖了 length 路径。
- `_is_candidate_facet_assertion_issue()` 使用文本匹配（`"候选 facet" in text and "断言" in text`），GLM plan review O2 指出的窄 helper 选择已落实为语义匹配，但依赖 audit issue message 包含关键词。如果 auditor 改变 message 措辞，可能失效。当前实现与 plan reviewer 的"在 evidence artifact 中注明选择"一致。**可接受。**

## Minor observations（非阻塞）

### O1. `_primary_subcategory` 的 `code_bug_other` 双路径

`_primary_subcategory()`（`chapter_orchestrator.py:1635`）无论 `has_any_counter` 为 True 或 False，都返回 `"code_bug_other"`。这意味着即使有 issue 计数但不命中前 7 类（理论上不可能，因为所有 writer issue 都映射到了前 7 类），也会返回 `code_bug_other`。当前 writer issue id 全覆盖，这不是问题。但如果未来新增 issue id 格式，该兜底行为是正确的安全网。

### O2. CLI stderr 中 `first_failed_subcategory=unknown`

当 `failure_subcategory` 为 `None`（如 timeout、code_bug 等非 prompt-contract 失败）时，CLI 输出 `first_failed_subcategory=unknown`（`cli.py:859-860`）。这是预期行为——`"unknown"` 是 CLI 的安全 fallback，不是 prompt-contract 子类。

## Safety boundaries checklist

| 安全边界 | 保持 | 验证 |
|---|---|---|
| Evidence anchors fail-closed | ✓ | writer parser 未改 |
| ITEM_RULE deletion fail-closed | ✓ | writer parser 未改 |
| Candidate facet non-asserted | ✓ | `candidate_facet_assertion_count` 只计数，测试验证仍阻断 |
| Trading advice blocked | ✓ | `forbidden_phrase_count` 只计数，测试验证仍阻断 |
| E2 deferred | ✓ | 本 gate 不实现 Evidence Confirm |
| Missing semantics strict | ✓ | missing marker 逻辑未改 |
| No deterministic fallback | ✓ | CLI `--use-llm` incomplete 仍 exit 1 |
| Default deterministic unchanged | ✓ | evidence 验证 analyze/checklist exit 0 |

## Blocking Findings

无。

## Verdict

**PASS** — 实现严格遵循 plan，只做脱敏诊断扩展和 `failure_subcategory`，安全边界完整，taxonomy 和 precedence 正确，敏感信息保护充分，测试覆盖充分。非阻塞观察不影响 gate accept。
