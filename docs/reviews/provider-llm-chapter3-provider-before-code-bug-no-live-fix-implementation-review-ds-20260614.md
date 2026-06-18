# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Review (DS)

Date: 2026-06-14

Reviewer: AgentDS (independent implementation reviewer)

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope

- **Mode**: role-scoped worker handoff — independent implementation review of current unstaged diff.
- **Branch**: `feat/mvp-llm-incomplete-run-artifacts`
- **Review target**: Current unstaged implementation diff in:
  - `fund_agent/agent/runner.py`
  - `tests/agent/test_runner.py`
  - `tests/services/test_chapter_orchestrator.py`
- **Evidence artifact**: `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md`
- **Accepted plan**: `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md` (verdict `ACCEPT_PLAN_WITH_MANDATORY_AMENDMENTS`)
- **Included scope**:
  - Red-test-first evidence review
  - Source implementation correctness against plan and mandatory amendments
  - `_exception_task()` empty-traces guard correctness and non-empty trace behavior preservation
  - All 4 `_exception_task` call-site regression analysis
  - Test coverage of pre-tool ValueError and Service/orchestrator safe diagnostic projection
  - Scope boundary compliance (no Service/Bridge/Orchestrator/Fund writer/source/provider/repair-budget/annual-period LLM changes)
  - EID single-source/no-fallback and `NOT_READY` preservation
- **Excluded scope**:
  - Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands
  - Source/test/runtime behavior edits
  - Stage, commit, push, PR, delete, archive, cleanup or ignore actions
- **Parallel review coverage**: 无

## 2. Evidence Reviewed

- `AGENTS.md` — execution rule truth source
- `docs/current-startup-packet.md` — current gate scope and constraints
- `docs/implementation-control.md` — control truth
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md` — accepted plan with mandatory amendments
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md` — implementation evidence from AgentCodex
- `git diff -- fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py` — full unstaged diff
- Source files at relevant line ranges:
  - `fund_agent/agent/runner.py:290-520` — `_run_single_chapter` full implementation
  - `fund_agent/agent/runner.py:907-962` — `_exception_task` full implementation
  - `fund_agent/agent/runner.py:1112-1133` — `_typed_required_output_items` definition
  - `tests/agent/test_runner.py:185-243` — new red test
  - `tests/services/test_chapter_orchestrator.py:1640-1708` — new orchestrator projection test

## 3. Findings

未发现实质性问题。

### 逐项审查记录

**3.1 Red-test-first compliance**

证据 `§3` 记录了 pre-fix 执行结果：

```
FAILED tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool
ValueError: Authorization Bearer sk-secret prompt raw
```

失败位置在 `runner.py:615`（`_writer_input` 调用链中 `_typed_required_output_items` 的 monkeypatch 注入点），exception 在 writer tool 调用之前逃逸。满足 controller amendment #1（red test first，pre-fix 必须 fail）。

**3.2 Monkeypatch injection point**

测试使用 `monkeypatch.setattr(runner_module, "_typed_required_output_items", ...)`（agent 测试）和 `monkeypatch.setattr("fund_agent.agent.runner._typed_required_output_items", ...)`（orchestrator 测试）。注入函数签名 `(chapter_id: int, *, policy: object) -> tuple[object, ...]` 与实际 `_typed_required_output_items(chapter_id: int, *, policy: AgentRunPolicy) -> tuple[RequiredOutputItem, ...]` 兼容。注入位置在 `_writer_input` → `build_chapter_writer_input` 的参数构造路径上（`runner.py:625`），与实际 `ValueError` 逃逸路径一致。满足 controller amendment #2。

**3.3 `_exception_task()` empty-traces guard**

实现精确匹配 controller amendment #3：

```python
# runner.py:939 — 实际实现
if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"):
```

完整追踪 `_exception_task` 的 4 个调用点：

| 调用点 (行号) | traces 内容 | `len(traces)` | 命中分支 | 行为变化 |
|---|---|---|---|---|
| 317 (新增 pre-tool) | `()` | 0 | `len(traces)==0` → `previous_attempts` | **新增**：不记录 ChapterAttempt |
| 349 (writer tool 异常) | `(writer_trace,)` | 1, tool=`fund.write_chapter` | 原条件 → `previous_attempts` | **无变化** |
| 428 (programmatic audit 异常) | `(writer_trace, prog_trace)` | 2 | else → 创建 ChapterAttempt | **无变化** |
| 476 (LLM audit 异常) | `(writer_trace, [prog_trace,] llm_trace)` | 2 或 3 | else → 创建 ChapterAttempt | **无变化** |

调用点 349、428、476 的行为与改动前完全一致。新增调用点 317 的 `traces=()` 在改动前不存在任何调用方，不构成回归。满足 controller amendment #4。

**3.4 `_chapter_title()` 范围边界**

`_chapter_title(projection, chapter_id)`（`runner.py:305`）仍在 try/except 块外部。若 `_chapter_title` 本身抛出异常，仍会逃逸。这是 controller finding #5 明确接受的 residual。满足 controller amendment #5。

**3.5 非空 trace 行为保留验证**

对 writer tool 异常路径（line 349）：`traces=(writer_execution.trace,)`，`len(traces)==1`，`traces[0].request.tool_name == "fund.write_chapter"` → `current_attempts = previous_attempts`。与改动前行为完全一致。

对 auditor 异常路径（lines 428/476）：`len(traces) >= 2` → 走 else 分支 → 创建 `ChapterAttempt(attempt_index=..., tool_traces=traces, ...)`。与改动前行为完全一致。

adversarial pass：考虑 `len(traces) == 1` 但 `tool_name != "fund.write_chapter"` 的边界情况。当前所有调用点均不存在此情况（唯一 `len(traces)==1` 的调用点是 writer tool 异常，tool_name 即为 `fund.write_chapter`）。若将来新增调用点传入非 writer 的单 trace，会走 else 分支创建 ChapterAttempt，行为正确。

**3.6 敏感文本泄露检查**

两个新测试均注入 `ValueError("Authorization Bearer sk-secret prompt raw")` 并验证敏感文本不出现在序列化输出中：

- Agent 测试 (`test_runner.py:239-243`)：验证 `task.blocked_reasons` repr 不含 `Authorization`/`Bearer`/`sk-secret`/`prompt raw`
- Orchestrator 测试 (`test_chapter_orchestrator.py:1704-1708`)：验证 `serialize_chapter_runtime_diagnostics` 完整 payload str 不含上述敏感文本

诊断字段 `error_type` 仅输出 `"ValueError"`（类型名，不含消息体）。`blocked_reasons` 格式为 `f"{chapter_id}:{terminal}:{type(exception).__name__}"`，只含类型名。安全诊断投影成立。

**3.7 Scope boundary compliance**

diff 只涉及三个授权文件：`fund_agent/agent/runner.py`、`tests/agent/test_runner.py`、`tests/services/test_chapter_orchestrator.py`。

确认未触碰：
- Service 层：`fund_agent/services/` 无变更
- Bridge：`fund_agent/bridge/` 无变更
- Orchestrator 实现：`fund_agent/services/chapter_orchestrator.py` 无变更（仅测试文件新增测试）
- Fund writer：`fund_agent/fund/` 无变更
- Source/provider/repair-budget/annual-period：全无变更
- EID single-source/no-fallback：全无变更
- `NOT_READY`：全无变更

**3.8 `attempt_index` 初始化顺序**

`attempt_index = 0`（`runner.py:307`）已移至 try/except 块之前，确保 pre-tool 异常时 `_exception_task(..., attempt_index=attempt_index, ...)` 中的 `attempt_index` 为已初始化的 `0` 而非未定义。正确。

**3.9 `previous_attempts=tuple(attempts)` 在 pre-tool 路径**

pre-tool 路径中 `attempts: list[ChapterAttempt] = []` 刚初始化，`tuple(attempts)` 为 `()`。测试断言 `task.attempts == ()` — 确认无 ChapterAttempt 记录。这正确反映了 provider attempt 未发生的事实。

## 4. Validation Reviewed or Run

### 4.1 Evidence 记录的验证（已采信）

| ID | Command | Evidence result |
|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | `1 passed in 0.85s` |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | `1 passed in 0.45s` |
| V3 | regression: 3 existing tests | `3 passed in 0.44s` |

### 4.2 独立重新验证（本次审查执行）

| ID | Command | Result |
|---|---|---|
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | `123 passed in 1.01s` |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | `All checks passed!` |
| V6 | `git diff --check` | Passed (no output) |

V4 覆盖完整 focused suite（123 tests），包括：
- `tests/agent/test_runner.py`：agent body runner 的全部测试
- `tests/services/test_chapter_orchestrator.py`：orchestrator 投射的全部测试
- `tests/services/test_fund_analysis_service_llm.py`：Service LLM 执行路径的全部测试

V5 确认无 ruff 违规。V6 确认无空白字符错误。

## 5. Verdict Table

| 审查项 | 结果 |
|---|---|
| 实现匹配 accepted plan | PASS |
| Red-test-first 证据充分 | PASS |
| `_exception_task` empty-traces guard 精确匹配 mandatory amendment | PASS |
| 非空 trace 行为完整保留（4 个调用点逐一验证） | PASS |
| 测试证明 pre-tool ValueError → `code_bug` 分类 | PASS |
| 测试证明 Service/orchestrator 安全诊断投射 | PASS |
| 无 Service/Bridge/Orchestrator/Fund writer 变更 | PASS |
| 无 source/provider/repair-budget/annual-period LLM 变更 | PASS |
| EID single-source/no-fallback 保留 | PASS |
| `NOT_READY` 保留 | PASS |
| 测试回归（123 passed） | PASS |
| 静态检查（ruff） | PASS |
| 空白字符检查（git diff --check） | PASS |
| 缺失测试 | 未发现 |
| 不安全诊断 | 未发现 |
| Scope expansion | 未发现 |

## 6. Residuals

| Residual | Status |
|---|---|
| `_chapter_title()` 异常仍可逃逸 | Accepted residual（controller finding #5）；不在本 gate 范围内 |
| 其他异常类型（非 ValueError）pre-tool 行为仅由 `except Exception` 兜底覆盖 | 低风险：fail-closed 语义成立；`_failure_category_from_exception` 和 `_terminal_from_exception` 对所有异常类型均有定义 |
| Exact live `004393 / 2025` Route C full completion | Deferred（单独 live re-evidence gate） |
| LLM content quality | Deferred |
| 401/403 provider-response classification | Deferred |
| Annual-period LLM route | Deferred |
| Chapter repair budget calibration | Deferred |
| Release/readiness | `NOT_READY` |

## 7. Final Verdict

**PASS**

实现完全匹配 `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md` 的 accepted plan 和全部 5 项 mandatory amendments。red-test-first 有充分的 pre-fix 失败证据。`_exception_task()` 的 4 个调用点逐一追踪验证，非空 trace 行为无回归。测试覆盖 pre-tool ValueError 分类和 orchestrator 安全诊断投射，敏感文本确认不泄露。Scope 严格限定在 3 个授权文件，无 Service/Bridge/Orchestrator/Fund writer/source/provider/repair-budget/annual-period LLM 变更。EID single-source/no-fallback 和 `NOT_READY` 完整保留。全部验证命令（focused suite 123 passed、ruff、git diff --check）通过。
