# Plan Review: Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Plan

Date: 2026-06-14

Reviewer: AgentMiMo / independent plan reviewer

Reviewed target: `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-procodex-20260613.md`

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`

## 1. Scope

Adversarial review of the proposed no-live fix plan for the Chapter 3 provider-before `ValueError` / `code_bug` path.

Review focus:

- Whether the proposed candidate code path is directly supported by repo facts and accepted evidence.
- Whether the red-test-first stop condition is sufficient to avoid speculative fix.
- Whether the minimal write set is properly constrained.
- Whether the plan preserves EID single-source no-fallback and NOT_READY.
- Whether the plan avoids scope creep into annual-period LLM route, repair budget calibration, provider default changes, Docling, source fallback, live/provider commands and external state.
- Whether proposed tests are sufficient to prove the no-live pre-tool ValueError path and safe diagnostic projection.

## 2. Evidence Reviewed

Control and disposition evidence:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-diagnostic-disposition-20260613.md`
- `docs/reviews/workspace-scope-artifact-disposition-closeout-20260613.md`

Source/test evidence (read to verify plan claims):

- `fund_agent/agent/runner.py` lines 290-346, 585-619, 897-952, 1389-1471
- `fund_agent/services/agent_bridge.py` lines 659-696
- `fund_agent/services/chapter_orchestrator.py` lines 1043-1102, 2606-2714
- `tests/agent/test_runner.py` lines 167-194

## 3. Findings

### 01-未修复-低-`_exception_task` 空 traces 行为变更缺少回归覆盖

- **位置**: Section 5 Proposed Minimal Fix, "Adjust `_exception_task(...)` so zero-trace pre-tool exceptions do not create a synthetic attempt record"
- **问题类型**: 测试缺口
- **当前写法**: Plan 要求修改 `_exception_task(...)` 在 `traces == ()` 时保持 `attempts == previous_attempts`，不创建 synthetic `ChapterAttempt`。Test A 验证 `task.attempts == ()`，但没有显式回归测试验证现有 `traces != ()` 路径行为不变。
- **反例/失败场景**: 修改 `_exception_task` 的 traces 判断条件时，如果条件写宽了（如 `len(traces) <= 1`），可能影响现有 writer tool exception 路径（`traces == (writer_trace,)`），导致现有 test_chapter_3_value_error 测试回归。
- **为什么有问题**: 当前 `_exception_task` 有三个调用点：line 339（writer tool，traces 非空）、line 418（programmatic audit，traces 非空）、line 466（LLM audit，traces 非空）。新调用点将是第一个传 `traces=()` 的。修改条件时必须精确只拦截 `traces == ()`。
- **直接证据**: `runner.py:927-940` 当前逻辑使用 `len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"` 判断。修改需确保此条件不受影响。
- **影响**: 低。现有三个调用点都传非空 traces，修改 `traces == ()` 分支不影响它们。但如果实现 agent 写出 `if not traces:` 之类的宽条件，会改变 writer tool 异常路径的 attempts 构造行为。
- **建议改法和验证点**: 在 plan 中明确 `_exception_task` 修改仅在 `len(traces) == 0` 时短路返回 `previous_attempts`，保持其他条件不变。V3 已包含现有三个测试的回归验证，但建议在 plan 文本中显式标注此约束。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 02-未修复-低-Test A monkeypatch 注入点存在不确定性

- **位置**: Section 6 Test A, "Use `monkeypatch` to patch `fund_agent.agent.runner._typed_required_output_items` or another narrow `_writer_input(...)` dependency"
- **问题类型**: 不可直接实施
- **当前写法**: Plan 建议 monkeypatch `_typed_required_output_items` 或 "another narrow dependency" 来注入 `ValueError`。
- **反例/失败场景**: `_writer_input(...)` 内部调用 `build_chapter_writer_input(...)`，该函数也可能对 Chapter 3 抛出 `ValueError`。如果实现 agent 选择了错误的注入点（如 patch `build_chapter_writer_input` 但签名不匹配），可能导致测试构造困难。
- **为什么有问题**: Plan 用 "or another narrow dependency" 留了不确定性，implementation agent 需要自行判断最佳注入点。这不会导致 plan 失败，但会增加实现时的试错成本。
- **直接证据**: `runner.py:609-619` 显示 `_writer_input` 调用 `build_chapter_writer_input(...)` 传入多个参数，其中 `_typed_required_output_items(chapter_id, policy=policy)` 是最窄的无副作用依赖。
- **影响**: 低。不影响 plan 可行性，但 implementation agent 可能需要额外时间确定注入点。
- **建议改法和验证点**: 将 "or another narrow dependency" 收敛为明确推荐 `_typed_required_output_items`，因为它是纯函数、无副作用、签名简单，且 plan 已在 Test B 中使用相同注入点。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

无 material findings。

## 4. Verdict Table

| 维度 | 评估 | 说明 |
|---|---|---|
| 候选代码路径直接证据 | PASS | `_run_single_chapter()` line 307 在 `attempt_index` 初始化（line 314）和 `write_chapter_tool` 调用（line 326）之前调用 `_writer_input()`，该函数 docstring 明确标注 `Raises: ValueError`。代码事实直接支持。 |
| Red-test-first 止损条件 | PASS | Section 10 明确要求 Test A 必须先以 escaped ValueError 失败，否则停止并报告 `NEED_MORE_NO_LIVE_EVIDENCE`。条件充分。 |
| 最小写集约束 | PASS | 仅允许修改 `runner.py`、`test_runner.py`、`test_chapter_orchestrator.py`。明确禁止修改 Service、Bridge、Orchestrator、chapter_writer、provider defaults、config。 |
| EID 单源无降级 / NOT_READY | PASS | Section 8 明确 preserve EID single-source/no-fallback、fail-closed、NOT_READY。无降级路径引入。 |
| 范围规避 | PASS | 明确排除 annual-period LLM route、repair budget calibration、provider defaults、Docling、source fallback、live/provider commands、external state。 |
| 测试充分性 | PASS（附低风险修正建议） | Test A 证明 pre-tool ValueError 不逃逸且分类正确；Test B 证明 Service/orchestrator 诊断投影安全。V3 覆盖现有回归。 |
| `_exception_task` 行为变更安全性 | PASS（附低风险修正建议） | 现有三个调用点都传非空 traces，`traces == ()` 分支仅影响新路径。但 plan 文本可更精确。 |
| 诊断投影路径 | PASS | `_runtime_diagnostics_from_task` 在 `task.attempts == ()` 时正确路由到 `_exception_runtime_diagnostics`，产出 `provider_attempt_index=None`、`max_output_chars=12000` 的安全诊断。 |

## 5. Required Amendments

无 required amendments。

两个低风险 finding 建议在 implementation gate 执行时注意，不阻塞 plan approval。

## 6. Residuals

| Residual | Status | Tracking |
|---|---|---|
| 精确 live `004393 / 2025` Route C 完整执行仍未证明 | Deferred | no-live fix acceptance 后单独授权的 bounded live re-evidence gate |
| LLM 内容质量仍未证明 | Deferred | 未来 content-quality/readiness gate |
| 401/403 provider-response 分类仍未证明 | Deferred | 未来 provider-response negative evidence gate |
| Annual-period LLM route 仍未设计 | Deferred | 单独 annual-period LLM route design gate |
| Chapter repair budget 仍未校准 | Deferred | 单独 repair budget calibration gate |
| 全局 pre-run `ValueError` 路径不在本次窄修复范围 | Deferred | 如 controller 需要全局 fail-closed 语义则单独规划 |
| Release/readiness 保持 `NOT_READY` | Accepted residual | Release/readiness gate only |

## 7. Final Verdict

**PASS**

Plan 的候选代码路径有直接代码事实支持，red-test-first 止损条件充分，最小写集正确约束，EID 单源/NOT_READY 不受影响，范围规避完整，测试足以证明目标行为。两个低风险 finding 不阻塞 implementation gate 进入。
