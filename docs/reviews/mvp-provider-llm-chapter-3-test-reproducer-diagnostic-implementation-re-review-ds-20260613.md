# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation — DS Re-review

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

Role: AgentDS re-review worker only. Targeted follow-up on F1/F2 fixes only. 未修改 source/tests/runtime 行为。

Review basis:
- Prior DS review: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-ds-20260613.md`
- Diff: `tests/services/test_chapter_orchestrator.py` (F1 fix)
- Current implementation evidence: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md` (F2 fix)

## Verdict

**PASS**

F1 closed. F2 closed. No new blocker.

---

## Finding Disposition

### F1-LOW — orchestrator test 未直接断言 `diagnostic.message` 脱敏结果 → CLOSED

**Fix evidence** (`tests/services/test_chapter_orchestrator.py`, diff lines +25–+29):

```python
diagnostic_message = diagnostics[0].get("message")  # type: ignore[union-attr]
assert "Authorization" not in (diagnostic_message or "")
assert "Bearer" not in (diagnostic_message or "")
assert "sk-secret" not in (diagnostic_message or "")
assert "prompt raw" not in (diagnostic_message or "")
```

新增的四行直接断言与已有测试 `test_unexpected_exception_records_code_bug_diagnostic_without_secret` 的模式一致。断言在 `str(payload)` 整体检查之前，提供 message 字段级别的脱敏验证。`(diagnostic_message or "")` 的 None-safety 处理正确——若 message 缺失则退化为空字符串，不会因 NoneType 而漏检。

现有的 `str(payload)` 断言保留在下方（lines +38–+41），提供双层覆盖。

**结论**: 修复精确、最小、与已有测试模式一致。F1 关闭。

### F2-LOW — `_execution_request` typed_template_path helper 扩展未记录 → CLOSED

**Fix evidence** (`docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`, lines 144–149):

> `_execution_request()` in `tests/services/test_fund_analysis_service_llm.py` was narrowly extended to thread `typed_template_path` consistently when a test passes an explicit `ChapterOrchestrationPolicy`. This is an accepted nonblocking test helper deviation only; it is not production behavior and does not change Service runtime request construction.

Implementation evidence 现在明确记录：
- 变更范围：`_execution_request()` 中的窄扩展
- 性质：test helper deviation only，非 production 行为
- 影响：不改变 Service runtime request construction

措辞与 DS review 建议的 `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL` disposition 一致，且与 controller 在 planning gate 中对同类 fixture/helper 问题的处理风格一致。

**结论**: 修复符合推荐处置。F2 关闭。

---

## Boundary Re-check

F1/F2 修复未引入对以下内容的变更，原 review 的 boundary checks 仍有效：

- 无 source policy 变更（`_execution_request` 是 test-only helper）
- 无 live/provider/LLM/network 命令
- 无 `llm_exception` 被加入 `_RUNTIME_STOP_REASON_CATEGORY`
- `_is_code_bug_runtime_diagnostic` 四条件不变
- `NOT_READY` 保留

orchestrator test 修改仅新增四个 `diagnostic_message` 断言；implementation evidence 修改仅新增一段 deviation 记录。二者均不改变生产代码行为。

---

## Residual Risk

F1、F2 关闭后，原 DS review residual risk 表无变化。

---

## Open Questions

无。
