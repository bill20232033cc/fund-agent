# MVP programmatic audit L1 calibration — code review

日期：2026-05-31

Reviewer：MiMo (Gateflow code reviewer)

Gate：`MVP programmatic audit L1 calibration gate`

Review scope：workspace diff (`git diff HEAD`)，implementation evidence，plan/reviews，previous gate judgment。

## Verdict

**PASS**

---

## Review checklist

### 1. L1 taxonomy/diagnostic 只新增，不放松 `_audit_numerical_closure` 或 L1 anchor proximity

**PASS.** `chapter_auditor.py` diff 不触碰 `_audit_numerical_closure`（`git diff HEAD -- fund_agent/fund/chapter_auditor.py | grep _audit_numerical_closure` 无命中）。auditor 的 L1 规则逻辑、正则 `_NUMERICAL_CLOSURE_RE` / `_NUMERIC_TEXT_RE`、以及 `5行` anchor proximity 阈值均未修改。

新增内容仅：
- `_ASSERTED_FACET_RE_TEMPLATE` 常量（facet 断言 regex）。
- `_required_output_marker()` / `_facet_asserted()` helper。
- `_audit_contract_markers()` 改用 exact marker 匹配。
- `_audit_non_asserted_facets()` 从手动窗口扫描改为 regex 匹配。
- LLM audit prompt 加强行协议约束。
- `_parse_llm_audit_response()` 改 `line.split("|")` 要求恰好 3 段。

L1 anchor proximity 语义完整保留。

### 2. Slice 3 确实 skipped，unsafe L1 cases 仍 fail-closed

**PASS.** 实现证据记录 Slice 3 skipped（无 overstrict evidence）。代码确认：
- `_audit_numerical_closure()` 未修改。
- 新增 auditor tests 验证 unsafe L1 cases 仍 fail-closed：
  - `test_programmatic_audit_blocks_l1_a_minus_c_without_nearby_anchor_marker` — A-C 百分比缺邻近 anchor 仍触发 L1。
  - `test_programmatic_audit_blocks_l1_missing_wording_with_concrete_unanchored_percentage` — "数据不足" 包裹具体无锚点闭环百分比仍触发 L1。
- Safe cases 不被误杀：
  - `test_programmatic_audit_allows_l1_formula_framework_without_concrete_percentage` — 纯框架说明不触发 L1。
  - `test_programmatic_audit_allows_l1_formula_with_nearby_anchor_marker` — 有邻近 anchor 不触发 L1。

### 3. `_SUBCATEGORY_PRECEDENCE` 插入位置安全，不掩盖 candidate_facet / forbidden

**PASS.** `chapter_orchestrator.py:139-148` 实际 precedence：

```
response_length_incomplete > invalid_marker > unknown_anchor > missing_required_marker >
missing_structure > candidate_facet_assertion > forbidden_phrase > l1_numerical_closure > code_bug_other
```

`l1_numerical_closure` 位于 `candidate_facet_assertion` 和 `forbidden_phrase` **之后**、`code_bug_other` 之前。这保证：
- 候选 facet 断言（交易安全）优先于 L1。
- 禁用措辞（交易安全）优先于 L1。
- L1 优先于泛化 fallback `code_bug_other`。

`_primary_subcategory()` 遍历 `_SUBCATEGORY_PRECEDENCE` 顺序返回首个命中计数 > 0 的子类，逻辑正确。

### 4. `_required_correction_from_issue` 的 L1 guidance 安全，不鼓励编造数值

**PASS.** `chapter_orchestrator.py:2056-2061` L1 修正项：

> "修复模板第2章 R=A+B-C 数字闭环：公式/百分比闭合断言必须在同一句或上下2行内放入 allowed anchor marker；若没有同源事实支撑 R、A、B、C 或 A-C 数值关系，删除具体数值闭合断言，改写为未披露/数据不足/下一步最小验证问题；不得编造 Alpha、Beta、Cost 或 R 数值。"

指令明确：
- 有同源事实 → 必须放 anchor marker（强化锚定）。
- 无同源事实 → 删除数值断言，写缺口（不鼓励编造）。
- 明确禁止编造 Alpha/Beta/Cost/R 数值。

Writer prompt 中的 L1 anchor rule（`chapter_writer.py` diff）也一致：`不得编造 R、A、B、C 或 A-C 数值`。

### 5. CLI / service taxonomy 一致，failed stdout empty / no fallback

**PASS.**
- CLI `_first_failed_chapter_summary()` 从 `chapter_result.failure_category` / `failure_subcategory` 直接读取，与 service 层 `ChapterRunResult` 字段一致。
- 测试 `test_analyze_cli_use_llm_l1_subcategory_matches_service_summary` 验证：`first_failed_category=prompt_contract`、`first_failed_subcategory=l1_numerical_closure`，stdout 为空，不回退 deterministic。
- 测试 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证：timeout 分类 `first_failed_category=llm_timeout`，stdout 为空，不回退。
- 测试 `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback`（已有）继续验证 incomplete 场景。

### 6. Serialization / secret safety

**PASS.**
- `serialize_chapter_prompt_contract_diagnostics()` 只输出标量、计数和枚举值，不输出 prompt/draft/provider response。
- `_sanitize_text()` 在 orchestrator 和 llm_provider 中均实现：折叠空白、redact `Authorization`/`Bearer`/`sk-`/`api_key`/`prompt` 等敏感字段、限长 180 字符。
- `_safe_exception_message()` 通过 `_sanitize_text()` 包装。
- Provider diagnostics (`ChapterLLMRuntimeDiagnostic`) 不含 prompt body、API key 或 response content。
- `_audit_prompt_contract_diagnostic()` 只保存 prefix counts，不保存 line suffix 或 draft 文本。
- 测试 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证 stderr 不含 `Authorization`/`Bearer`/`sk-`/`system_prompt`/`user_prompt`/`draft_markdown`/`provider_response`。

### 7. Deterministic analyze / checklist / missing-config 不变

**PASS.** 实现证据记录：
- `fund-analysis analyze 006597 --report-year 2024` exit 0，deterministic 默认不变。
- `fund-analysis checklist 006597 --report-year 2024` exit 0，checklist 不变。
- isolated missing-config `--use-llm` fail-closed exit 1，stdout bytes 0。
- `1186 passed`，coverage 91.85%。

### 8. Scope 不碰 forbidden files

**PASS.** Changed files（除 docs/reviews evidence 外）：
- `fund_agent/services/chapter_orchestrator.py` — 在 scope 内。
- `fund_agent/fund/chapter_writer.py` — 在 scope 内。
- `fund_agent/fund/chapter_auditor.py` — 在 scope 内（只改 facet/contract marker/helper/prompt）。
- `fund_agent/services/llm_provider.py` — provider runtime diagnostics + timeout retry，未碰 config/auth golden。
- `fund_agent/config/llm.py` — 新增 timeout_max_attempts / timeout_backoff_seconds 配置，未修改已有字段。
- `fund_agent/ui/cli.py` — 只新增 `_first_failed_chapter_summary()`，未改退出码机制。
- Tests — 对应测试文件。

未修改：golden fixtures、score、quality gate、final judgment、Host/Agent/dayu、PR 状态。

---

## Non-blocking observations

**O1.** `_primary_subcategory()` line 1648 `return "code_bug_other" if not has_any_counter else "code_bug_other"` 两个分支返回相同值，可简化为 `return "code_bug_other"`。不影响正确性。

**O2.** `llm_provider.py` 新增 `timeout_max_attempts` retry 循环仅对 `httpx.TimeoutException` 重试，`TransportError` / HTTP error / malformed 仍立即抛出。这是合理的 — timeout 是唯一适合重试的 transient 错误。

**O3.** `_parse_llm_audit_response()` 改 `line.split("|")` 要求恰好 3 段，这意味着 message 内含 `|` 会被判为 parse failure。这对 LLM 输出是更安全的约束（防止注入额外字段），但可能增加 parse failure 率。已有 `test_llm_audit_line_with_extra_separator_is_parse_failure` 覆盖。

---

## 结论

**PASS.** 实现严格遵循已批准 plan，只新增 `l1_numerical_closure` taxonomy/diagnostic 和 L1 repair guidance，未放松 `_audit_numerical_closure` 或 L1 anchor proximity。Slice 3 确实 skipped，unsafe L1 cases 保持 fail-closed。`_SUBCATEGORY_PRECEDENCE` 插入位置安全（低于 candidate_facet/forbidden，高于 code_bug_other）。L1 修正指令明确禁止编造数值。CLI/service taxonomy 一致。Serialization 不含 secret。Deterministic 路径不变。Scope 不碰 forbidden files。无 blocking finding。
