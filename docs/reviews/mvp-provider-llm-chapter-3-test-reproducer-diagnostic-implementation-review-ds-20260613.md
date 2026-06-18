# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation — DS Review

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

Role: AgentDS review worker only. 未修改 source/tests/runtime 行为。

Review basis: diff for the six allowed files and the accepted plan, controller judgment, and implementation evidence artifacts.

## Verdict

**PASS_WITH_FINDINGS**

Implementation correctly executes accepted S1/S2/S3/S4 plan and Pass A/Pass B controller sequencing. Two low-severity findings; no blocker.

---

## Findings

### F1-LOW — orchestrator test 未直接断言 `diagnostic.message` 脱敏结果

- **入口/函数**: `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap`
- **文件(行号)**: `tests/services/test_chapter_orchestrator.py` (line ~1637)
- **输入场景**: 测试用 `ValueError("Authorization Bearer sk-secret prompt raw")` 作为第3章 writer 异常
- **实际分支**: `_exception_runtime_diagnostics` → `_safe_exception_message` → `_sanitize_text` 脱敏路径
- **预期行为**: `diagnostic.message` 不应包含 `Authorization`、`Bearer`、`sk-secret`、`prompt raw` 等密钥子串
- **实际行为**: 测试只在 `serialize_chapter_runtime_diagnostics` 的字符串化 payload 上断言 secret 不存在（line ~1638: `text = str(payload); assert "Authorization" not in text`）；未直接断言 `diagnostic.message` 的脱敏效果。同文件中 `test_unexpected_exception_records_code_bug_diagnostic_without_secret` 确实直接断言了 `diagnostic.message`（line ~1586），但新测试未复制该模式。
- **直接证据**:
  - orchestrator test line ~1634–1638 只检查 `str(payload)` 不含 secret
  - 对比已有测试 `test_unexpected_exception_records_code_bug_diagnostic_without_secret` 在 line ~1585–1586 直接断言 `diagnostic.message`
- **影响**: `_sanitize_text` 脱敏在当前输入上可以通过（关键词匹配），但如果序列化路径改变导致 message 字段被单独暴露（而 str(payload) 整体断言仍在），可能漏检。当前风险低——message 字段始终在序列化输出内，str(payload) 断言覆盖了它。
- **建议改法和验证点**: 在 `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap` 中为第一个 diagnostic 增加 `assert "Authorization" not in (diagnostics[0].get("message") or "")` 或等效直接断言，不依赖序列化包装。
- **修复风险**: 低
- **严重程度**: 低

### F2-LOW — `_execution_request` 测试 helper 接受 plan 未列出的 `typed_template_path` 扩展

- **入口/函数**: `_execution_request` (test helper)
- **文件(行号)**: `tests/services/test_fund_analysis_service_llm.py` (line ~1376, ~1388)
- **输入场景**: 新测试传入 `ChapterOrchestrationPolicy(..., typed_template_path="typed_template_contract")`，`_execution_request` 将其填入 `ExecutionContract` 和 `FundLLMExecutionRequest`
- **实际分支**: helper 修改了两处：contract 构造增加 `typed_template_path=chapter_policy.typed_template_path`，execution request 构造增加 `typed_template_path=runtime_plan.typed_template_path`
- **预期行为**: plan S1.6 说 "Use existing `_FakeExtractor`, `_bundle`, `_FakeChapterLLMClient`, `_FakeAuditLLMClient`, `_execution_request()` and `FundAnalysisService`"——暗示使用已有 helper，不修改它
- **实际行为**: helper 被扩展了两个字段以满足新测试需求。对其他通过 `_execution_request()` 构造的测试（它们不传 `typed_template_path`），修改后合约和请求可能收到 `None`（若 `chapter_policy.typed_template_path` 为 None）或默认值（若有），不会破坏现有测试。
- **直接证据**: diff 中 `_execution_request` 函数末尾增加两行 `typed_template_path=...`
- **影响**: 测试 infrastructure 变化，非生产代码。现有 128 个测试全部通过证明没有破坏。但偏离了 plan 的 "use existing" 措辞，未在 implementation evidence 中作为 deviation 记录。
- **建议改法和验证点**: controller 可接受此 deviation 为 `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL`（与 MiMo/DS 对 `_FakeExtractor`/`_FakeChapterLLMClient` 的 disposition 一致）。implementation evidence 应记录此偏差。
- **修复风险**: 低
- **严重程度**: 低

---

## Boundary Checks

### Source Policy Preservation

| 检查项 | 结果 |
|---|---|
| EID `single_source_only` 未修改 | PASS — changed files 中无 `selected_source`、`source_mode`、`single_source_only` 引用 |
| `fallback_enabled=false` 未修改 | PASS — changed files 中无 `fallback_enabled` 引用 |
| Eastmoney 未进入当前路径 | PASS — changed files 中无 `eastmoney` 引用 |
| fund-company/CDN 未进入当前路径 | PASS — changed files 中无 `fund.company`、`cdn` 引用 |
| CNINFO 未进入当前路径 | PASS — changed files 中无 `cninfo` 引用 |
| fallback invocation 未引入 | PASS — 无 fallback 调用链变化 |

### No Live/Provider/LLM/Network Commands

| 检查项 | 结果 |
|---|---|
| 无 live/provider/LLM/network/PDF/FDR 命令 | PASS — diff 仅含代码和测试修改 |
| 无 source/cache/analyze/checklist 命令 | PASS |
| 无 readiness/release/PR/push/merge 命令 | PASS |
| 无 memory probing | PASS |

### Safe Diagnostic Behavior

| 检查项 | 证据 |
|---|---|
| pre-provider ValueError → `llm_exception` / `code_bug` | `agent_bridge.py:533-534`: `blocked_internal_code_bug` → `"llm_exception"`; `agent_bridge.py:714-715`: `task.failure_category` 透传 `"code_bug"` |
| provider attempt count = 0 | `chapter_orchestrator.py:1088`: fallback diagnostic 设 `provider_attempt_index=None`; Agent test 断言 `task.attempts == ()` |
| `provider_runtime_category` = None | `chapter_orchestrator.py:1271-1281`: `_provider_runtime_category_from_exception` 对 `ValueError` 返回 `None` |
| `max_output_chars` 作为安全标量传播 | `agent_bridge.py:76` → `_service_chapter_result_from_task` → `_runtime_diagnostics_from_task` → `_exception_runtime_diagnostics(..., max_output_chars=max_output_chars)` → `chapter_orchestrator.py:1099` |
| provider diagnostics cap 不被覆盖 | `chapter_orchestrator.py:1070-1080`: provider diagnostics 分支不传 `max_output_chars`，由 provider adapter 自身的 cap 保留 |
| `terminal_runtime_diagnostic` 对 code_bug 正确选择 | `chapter_orchestrator.py:2614-2617`: `_is_code_bug_runtime_diagnostic` 优先于 provider-runtime fallback（line 2618-2620） |
| `diagnostic_matches_terminal` 对 code_bug 正确匹配 | `chapter_orchestrator.py:2684-2686`: 同优先级 |
| 无 raw exception/prompt/provider/secret 泄漏 | `chapter_orchestrator.py:1818`: `_safe_exception_message` → `_sanitize_text` redacts Authorization/Bearer/sk-/prompt/api_key; 限长 180 chars |

### No `llm_exception` in Provider Runtime Category Mapping

| 检查项 | 结果 |
|---|---|
| `_RUNTIME_STOP_REASON_CATEGORY` 不含 `llm_exception` | PASS — 仅含 `llm_timeout`/`llm_rate_limited`/`llm_malformed_response`/`llm_network_error` (chapter_orchestrator.py:190-197) |
| `_is_code_bug_runtime_diagnostic` 要求 `provider_runtime_category is None` | PASS — 确保 code_bug 和 provider runtime 分类互斥 (chapter_orchestrator.py:2713) |

### `_is_code_bug_runtime_diagnostic` 四条件完备性

函数 (chapter_orchestrator.py:2691-2714) 要求:
1. `result.stop_reason == "llm_exception"` ✓
2. `result.failure_category == "code_bug"` ✓
3. `diagnostic.chapter_failure_category == "code_bug"` ✓
4. `diagnostic.provider_runtime_category is None` ✓

四个条件一起确保只在 stop reason、failure category 和 diagnostic 三方一致指向 pre-provider code bug 时才匹配。若任何一个条件不满足（如 provider runtime diagnostic 被标为 code_bug，或 code_bug 场景下仍有 provider category），匹配失败并 fallback 到现有 provider-runtime 搜索。设计审慎。

---

## Validation Reviewed

Implementation evidence (`docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`) 报告:

| 验证命令 | 报告结果 |
|---|---|
| `pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime` | 1 passed |
| `pytest tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic` | 1 passed |
| `pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap` | 1 passed |
| `pytest tests/services/test_llm_run_artifacts.py::test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage` | 1 passed |
| focused suite (4 files) | 129 passed |
| ruff check (allowed source + test surface) | All checks passed |
| `git diff --check` | passed |

Reviewer 未重新运行这些命令（no-live gate 约束），但通过静态代码走读确认实现与报告一致。

---

## Evidence Note: Legacy Execution Helper Path

Implementation evidence 记录:

> the Service reproducer uses the existing legacy execution helper path because the typed path can block before the Chapter 3 writer call on current fixture inputs. Typed policy cap propagation is covered by S2 bridge/orchestrator tests.

**DS assessment**: 可接受。理由：

1. Service 测试调用真实的 `service.analyze_with_llm_execution()` ——这是生产环境使用的同一个 public API。测试未走不同的代码路径。
2. "legacy" 指测试使用 `_execution_request()` helper 构造 `FundLLMExecutionRequest`——该 helper 是此测试文件中所有 Service execution 测试的标准 fixture pattern。它不在 production code path 中。
3. `max_output_chars` 通过 Service → bridge → orchestrator → diagnostic 的 typed propagation 由 S2 orchestrator 测试 (`test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap`) 独立验证：诊断构造、序列化和 artifact 写入的正确性。
4. 两项测试覆盖互补：Service 测试证明 fail-closed **编排行为**（blocked/incomplete/no fallback），orchestrator 测试证明 typed cap 的**诊断序列化**。
5. controller 已在 planning gate 中将 fixture/helper 可用性问题 disposition 为 `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL`。

没有由此产生的 finding。

---

## Test Meaningfulness Assessment

| 测试 | 证明什么 | 有意义？ |
|---|---|---|
| `test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime` | Agent 层将 pre-provider ValueError 分类为 `blocked_internal_code_bug` / `code_bug`，且不泄露 secrets | 是——验证了 Agent 分类契约 |
| `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic` | Service execution path 将 Agent code bug 投影为 `llm_exception`/`code_bug`，final assembly incomplete，无确定性回退 | 是——验证了 Service fail-closed 编排 |
| `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap` | serializer 输出 `max_output_chars`、零次 provider attempt、terminal diagnostic present/consistent | 是——验证了安全标量序列化 |
| `test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage` | artifact writer 在 `summary.json`、runtime matrix、chapter-03.json 中保留安全诊断 lineage，不含 canary/secrets | 是——验证了 artifact redaction |

四个测试均证明真实的失败行为，非实现 artifact 的 trivial 断言。每个测试 follow arrange-act-assert 模式，使用 fake/fixture 以保持 no-live。

---

## Open Questions

无。

---

## Residual Risk

| 风险 | 严重程度 | 处置 |
|---|---|---|
| `_sanitize_text` 脱敏是关键词级别的，非语义级别——不匹配关键词的新 secret 格式不会被脱敏 | 低 | 已有行为；message 限制为 180 chars 缓解暴露面。非本次变更引入。 |
| Service reproducer 测试在 `analyze_with_llm_execution` 内部走的精确代码路径可能异于 live 命令路径（live 命令可能走 typed Host/Agent bridge，测试可能走 in-process orchestration） | 低 | 两种路径共用相同 orchestrator 和 serializer；bridge/orchestrator 测试覆盖 typed cap propagation。controller 已将 fixture 问题 disposition 为 `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL`。 |
| 当前 fixture 使用 `fund_code="110011"` 和 `report_year=2024`，与 `004393 / 2025` 不同 | 低 | 计划已接受此约束——本 gate 为 no-live，不能读取 source body。future diagnostic gate 可解决。 |
| 未验证完整 `fund-analysis analyze --use-llm` CLI 路径 | 中 | 已延期；不在本 gate 范围内。live provider/LLM 命令被明确禁止。 |

---

## NOT_READY Preservation

Release/readiness 仍为 `NOT_READY`。本实现是 no-live diagnostic/test 覆盖，不证明 live provider/LLM 完成、LLM 内容质量、401/403 provider-response 分类、PR state 或 release state。
