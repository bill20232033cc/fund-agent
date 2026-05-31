# MVP real provider smoke prompt-contract calibration code review

日期：2026-05-31

Gate：`MVP real provider smoke acceptance rerun with prompt-contract calibration`

Role：code review worker，不是 controller、implementation worker 或 planning worker。

## Self-check

- Source of truth：approved plan、plan fix、controller judgment、implementation evidence、controller smoke evidence（`reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024.*`）。
- Scope boundary：只 review allowed implementation files；不改代码、不 commit/push/PR。
- Verification：亲自运行全部验证命令（见下方 Validation）。

## Findings

按 severity 排序。无 blocking findings。

### F1 — Implementation evidence real-provider chapter matrix stop reason 非代码级 Literal（non-blocking / evidence-clarity）

**Severity**：non-blocking

**File**：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`，chapter matrix 表。

**Observation**：real-provider smoke evidence 的 chapter matrix 记录 `stop_reason=provider_config_missing_in_validation_shell`。该值不在 `ChapterRunStopReason` Literal 内，也不是代码执行后从 `ChapterRunResult.stop_reason` 读取的——因为 real provider smoke 未实际运行，章节从未进入 orchestrator。implementation worker 在 evidence 中直接填写了"验证 shell 缺 provider env"的诊断状态，而非代码级 stop reason。

**Impact**：evidence 合规性口径偏差，不影响代码安全。controller judgment 要求 smoke evidence 使用代码级字段值。此处 evidence 章节矩阵的 stop reason 不来自代码输出，而是 implementation worker 手动标注的环境状态。

**Recommendation**：controller closeout 时可要求 evidence 在无法运行 real provider smoke 时，chapter matrix 留空或标注 `not_run`，不要使用非 Literal 值作为 stop reason。

### F2 — Implementation evidence first_failed_category 与 controller smoke evidence 不一致（non-blocking / evidence-discrepancy）

**Severity**：non-blocking

**File**：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md` vs `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024.stdout`。

**Observation**：
- Implementation evidence：`first_failed_category=provider_runtime`（因为 real provider smoke 未运行，implementation worker 用 env-missing 作为 fallback）。
- Controller smoke evidence：`first_failed_category=prompt_contract`（controller 已运行真实 smoke，所有章节 `llm_contract_violation`）。

两份 evidence 对同一 gate 的 real provider smoke 给出不同 category。Implementation evidence 的 category 是"env 缺失"的代理分类，controller smoke 的 category 是真实 provider 输出的分类。

**Impact**：不影响代码安全。controller 可能需要在 closeout 时以 controller smoke evidence 为准，或要求 implementation worker 在 env 不可用时不在 chapter matrix 中填写非代码值。

**Recommendation**：controller closeout 时以 controller smoke evidence（`prompt_contract`）为权威。

### F3 — `audit_parse` condition 3 在 `_is_audit_rule_too_strict` 中通过 `llm.issues` 检查而非独立 parse-failure flag（non-blocking / defense-in-depth）

**Severity**：non-blocking

**File**：`fund_agent/services/chapter_orchestrator.py:1357-1363`

**Observation**：plan Section 7.4 要求 `audit_rule_too_strict` 条件 3 为"不存在 `llm:parse_failure`"。代码实现为：

```python
if any(issue.issue_id == "llm:parse_failure" for issue in audit_result.llm.issues):
    return False
```

这依赖 `_parse_llm_audit_response` 在 parse failure 时生成 `issue_id="llm:parse_failure"` 的 issue。如果未来 auditor 模块改变 issue id 命名，此处检查会静默失效，`audit_parse` 可能被误分类为 `audit_rule_too_strict`。

**Impact**：当前代码正确。风险是跨模块紧耦合——auditor issue id 命名变更会影响 orchestrator 分类。

**Recommendation**：可接受当前实现。如果后续 auditor 模块重构，应同步检查此处。不属于 blocking finding。

### F4 — `_sanitize_text` 在 `chapter_orchestrator.py` 和 `llm_provider.py` 中有两份实现（non-blocking / minor duplication）

**Severity**：non-blocking

**File**：`fund_agent/services/chapter_orchestrator.py:1623-1642`、`fund_agent/services/llm_provider.py:568-598`

**Observation**：两个模块各有 `_sanitize_text` 函数，逻辑相似（单行化、redact 敏感词、限长）。orchestrator 版 redact 列表较短（6 项），provider 版较长（8 项，含 `writer user` 和 `draft markdown`）。

**Impact**：不一致的 redact 列表可能导致 orchestrator 层 diagnostic 遗漏某些敏感词。当前无安全风险，因为 orchestrator 层处理的文本通常不含 `writer user` / `draft markdown`。

**Recommendation**：非 blocking。如果后续统一 redact 策略，可提取为共享 helper。

## Verification commands（reviewer 亲自运行）

| Command | Result | Notes |
|---|---|---|
| `uv run ruff check .` | PASS | All checks passed |
| `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_provider.py tests/ui/test_cli.py -q` | PASS | 170 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS | 1154 passed, total coverage 91.80% |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS | exit 0 |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS | exit 0 |
| Secret leak scan | PASS | only safe policy-label hits in evidence doc |

## Checklist review per plan requirements

### 1. Writer prompt：降低认知负担且不放松 parser/safety

**Verdict**：PASS。

- Writer prompt 前置 5 条编号化输出协议（`先遵守输出协议，后写内容：`），降低了模型认知负担。
- 固定三段结构（`### 结论要点` / `### 详细情况` / `### 证据与出处`）在 prompt 和 parser 两侧均有强制检查。
- `required_output` exact marker 格式在 prompt 中以 `` `<!-- required_output:<exact required output item> -->` `` 显式示出，且 required_output_items payload 已带 exact marker。
- Anchor marker 限定为 allowed anchor set，prompt 明确"required_anchor_ids 是允许集合，不要求全量使用"。
- Missing marker 限定为 allowed missing reason。
- `non_asserted_facets` 有固定句式（`候选/未断言信息：<facet> 仅为候选标签...`）和禁止断言形式（`是/为/属于/定位为/可判定为`）。
- Parser 仍 fail-closed：`response_too_long`、`response_incomplete`（含 `length`/`max_tokens`/`content_filter`）、`missing_required_structure`、`missing_required_output_marker`、`unknown_anchor`、`llm_empty_response` 均阻断。
- 未引入自动补 marker、截断或修正文案。

### 2. Auditor line protocol parse failure：fail-closed

**Verdict**：PASS。

- `_parse_llm_audit_response` 改为 `line.split("|")`（非 `split("|", 2)`），严格要求恰好三段。额外分隔符（如 `BLOCKING|chapter|reason|extra`）触发 parse failure blocked。
- 空响应、`PASS|chapter|no issues` 以外混入文本、severity 不在 allowlist、location/message 为空——均为 parse failure blocked。
- Parse failure issue id 为 `llm:parse_failure`，分类为 `audit_parse`，不被 `audit_rule_too_strict` 覆盖。
- Programmatic audit blocked 不被 LLM PASS 覆盖：`_is_audit_rule_too_strict` 首先检查 `programmatic.status != "pass"`，programmatic fail 时返回 `False`，分类为 `prompt_contract`。
- `_audit_contract_markers` 修正为 `_required_output_marker(item) not in markdown`（原来 `item not in markdown` 是裸文案匹配，现在是 exact marker 匹配）。
- `_audit_non_asserted_facets` 重构为 regex `_ASSERTED_FACET_RE_TEMPLATE`，匹配 `是/为/属于/定位为/可判定为` 断言形式。候选说明（`候选/未断言信息：...`）不命中 regex，不会被误杀。

### 3. Repair/regenerate bounded；previous issue 进入 regenerate

**Verdict**：PASS。

- `ChapterRepairContext` dataclass 包含 `attempt_index`、`previous_issue_ids`、`previous_messages`、`required_corrections`。
- `_repair_context_from_audit` 从审计结果构造 typed context，`_sanitize_text` 限长 180 字符。
- `_required_corrections_from_issues` 按确定性映射生成修正项（structure→补齐段落、C2→补 marker、E1→anchor、`llm:parse_failure`→行协议、facet→候选改写）。
- `_repair_context_prompt` 渲染为 prompt 片段，含 `attempt_index`、issue ids、messages、corrections。
- `max_repair_attempts` 默认 1，每章最大 writer attempts = 2（1 + 1）。Budget 耗尽返回 `repair_budget_exhausted`。
- Timeout 异常在 `_run_single_chapter` 中 `except Exception` 后直接 `_exception_result` 返回，不进入 repair loop。
- `ChapterLLMRequest` 携带 typed `repair_context`。

### 4. ChapterFailureCategory 正确新增 `llm_timeout` / `audit_rule_too_strict`

**Verdict**：PASS。

- `ChapterFailureCategory` Literal 包含全部 7 个值：`provider_runtime`、`llm_timeout`、`prompt_contract`、`audit_parse`、`audit_rule_too_strict`、`fact_gap`、`code_bug`。
- `_chapter_failure_category_from_provider_runtime`：`timeout` → `llm_timeout`，其他 → `provider_runtime`。
- `_chapter_failure_category_from_exception`：先映射 provider category，非 provider 返回 `code_bug`。
- `_chapter_failure_category_from_audit_result`：parse failure → `audit_parse`；needs_more_facts → `fact_gap`；`_is_audit_rule_too_strict` → `audit_rule_too_strict`；fail/blocked → `prompt_contract`；兜底 `code_bug`。
- `_is_audit_rule_too_strict` 四条件：programmatic pass ✓、LLM fail/blocked with issues ✓、无 `llm:parse_failure` ✓、无 fact-gap issue ✓。
- `_chapter_failure_category_from_stop_reason`：`llm_timeout` → `llm_timeout`；`llm_empty_response`/`llm_contract_violation`/等 → `prompt_contract`；其他 `llm_*` → `provider_runtime`。

### 5. `ChapterRunResult.failure_category` 所有 failed/blocked/skipped 路径填充一致

**Verdict**：PASS。

- Writer blocked：`failure_category=_chapter_failure_category_from_writer_result(writer_result)` ✓
- Audit result 不 accepted：`failure_category=_chapter_failure_category_from_audit_result(audit_result)` ✓
- Exception：`failure_category=_chapter_failure_category_from_exception(exc)` ✓
- Global blocked：`failure_category=_chapter_failure_category_from_stop_reason(stop_reason)` ✓
- Skipped：`failure_category="fact_gap"` ✓
- Accepted：`failure_category=None` ✓
- CLI `_first_failed_chapter_summary` 只读 `ChapterRunResult.failure_category`，不遍历 attempts 或 diagnostics ✓

### 6. Controller smoke evidence 不把失败包装成 pass

**Verdict**：PASS。

- Controller smoke evidence（`controller-real-provider-006597-2024.exitcode`）：exit 1。
- stdout：`LLM 分析未完成：orchestration_status=blocked, ...first_failed_category=prompt_contract`。
- 所有 6 章 `chapter_not_accepted`、`missing_accepted_draft`、`missing_accepted_conclusion`。
- 没有章节被标记为 accepted。没有 deterministic fallback。失败如实报告。

### 7. Secret hygiene

**Verdict**：PASS。

- Implementation evidence 未记录 API key、Authorization header、完整 prompt、draft 或 provider response。
- Secret scan 仅有 evidence 文档中的 policy-label 命中（如 `API key/header/full prompt/full draft/full provider response stored：no`），无实际 secret 值。
- `_sanitize_text` 在 orchestrator 和 provider 两层均 redact `Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`、`api_key`、`sk-`、`prompt`。
- Provider diagnostic 不含 `chapter_id`、`fund_code`、`report_year`（provider 层记录为 `None`，由 orchestrator enrich）。
- CLI stderr 不输出 prompt、draft 或 provider response。

## Scope violation check

- Implementation worker 只修改了 approved plan allowed files。
- Pre-existing dirty worktree 文件（`docs/current-startup-packet.md`、`docs/implementation-control.md`、`fund_agent/config/llm.py` 等）的 dirty 状态为 pre-existing，与本 gate 无关，不构成 scope violation。
- 未发现本 gate scope 外的修改。

## Conclusion

**PASS。无 blocking findings。**

Implementation 正确实现了 plan 的全部 contract decisions：
- Writer prompt 降低认知负担，parser 保持 fail-closed。
- Auditor line protocol 严格三段解析，parse failure blocked 且分类为 `audit_parse`。
- Repair/regenerate bounded，typed repair context 携带 previous issues 和 deterministic corrections。
- `ChapterFailureCategory` 新增 `llm_timeout` 和 `audit_rule_too_strict`，分类逻辑正确。
- `ChapterRunResult.failure_category` 在所有 failed/blocked/skipped 路径一致填充。
- CLI 只从顶层 `failure_category` 读取，不遍历 nested diagnostics。
- Secret hygiene 通过。

4 个 non-blocking findings 涉及 evidence 口径和 minor code duplication，不影响代码安全或功能正确性。

## Residual risks

- Real provider smoke 仍可能返回 `prompt_contract`（controller smoke evidence 已证实）；后续需 writer prompt 进一步校准。
- `_is_audit_rule_too_strict` 依赖 auditor issue id 命名稳定性，跨模块重构时需同步检查。
