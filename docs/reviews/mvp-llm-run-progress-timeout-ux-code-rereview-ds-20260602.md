# Code Review (Re-review)

## Scope

- Mode: current changes (re-review of DS F1 fix only)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Prior review: `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md`
- Controller judgment: `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-controller-judgment-20260602.md`
- Fix evidence: `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-fix-evidence-20260602.md`
- Output file: `docs/reviews/mvp-llm-run-progress-timeout-ux-code-rereview-ds-20260602.md`
- Re-review target: DS F1 fix + regression check for no new scope violations
- Changed files in fix: `fund_agent/ui/cli.py`, `tests/ui/test_cli.py`, fix evidence artifact
- Parallel review coverage: 无

## DS F1 Fix Verification

### Fix implementation (`cli.py:786-797`)

原始代码（有 bug）：
```python
try:
    reporter.start()
    host_result = _run_llm_analysis_in_host(...)
finally:
    reporter.stop()
reporter.emit_terminal(host_result)  # UnboundLocalError on quality gate re-raise
```

修复后代码：
```python
host_result: HostRunResult | None = None
try:
    reporter.start()
    host_result = _run_llm_analysis_in_host(...)
finally:
    reporter.stop()
if host_result is None:
    raise RuntimeError("LLM Host run did not return a result")
reporter.emit_terminal(host_result)
```

**执行路径分析：**

| 路径 | `_run_llm_analysis_in_host()` 行为 | `host_result` 值 | 是否到达 `emit_terminal` | 终态处理 |
|---|---|---|---|---|
| 成功 | 返回 `HostRunResult(SUCCEEDED)` | 实际结果 | 是 | terminal progress 正常输出 |
| Incomplete | 返回 `HostRunResult(FAILED), operation_result=incomplete` | 实际结果 | 是 | terminal progress 正常输出 |
| Host 失败 | 返回 `HostRunResult(FAILED)` | 实际结果 | 是 | terminal progress 正常输出 |
| Quality gate block | raise `QualityGateBlockedError` | `None`（保持预初始化值） | 否，异常传播到外层 `except` | quality gate stderr 输出，exit 2 |
| Quality gate not-run | raise `QualityGateNotRunBlockedError` | `None`（保持预初始化值） | 否，异常传播到外层 `except` | quality gate not-run stderr 输出，exit 2 |

**验证结论：DS F1 已正确修复。**

关键保障：
- `host_result` 预初始化为 `None`，在 quality gate re-raise 时不会 `UnboundLocalError`
- quality gate 异常从内部 `try` 传播到外部 `except QualityGateBlockedError` / `except QualityGateNotRunBlockedError`，绕过了 `emit_terminal` 和 `host_result is None` 检查
- `reporter.stop()` 在 `finally` 中仍然执行，heartbeat 线程被正确停止
- 正常路径（成功/incomplete/Host 失败）下 `host_result` 被赋值为实际结果，正常通过 `None` 检查并执行 `emit_terminal`

### 新增测试覆盖

**`test_analyze_cli_use_llm_progress_quality_gate_block_preserves_error`** (`tests/ui/test_cli.py:3068`)：
- 使用 `_FakeLLMBlockedAnalysisService`（`analyze_with_llm_execution()` raise `QualityGateBlockedError`）
- `--use-llm --llm-progress`
- 断言：exit 2, stdout 空, `质量 gate 阻断报告输出` 存在, `quality_gate_status: block` 存在, `run_started` 存在, `run_terminal` 不存在, 无 `UnboundLocalError`, 无 `分析失败：`, 无 `LLM Host run 未完成`

**`test_analyze_cli_use_llm_progress_quality_gate_not_run_preserves_error`** (`tests/ui/test_cli.py:3171`)：
- 使用 `_FakeLLMNotRunBlockedAnalysisService`（`analyze_with_llm_execution()` raise `QualityGateNotRunBlockedError`）
- `--use-llm --llm-progress`
- 断言：exit 2, stdout 空, `质量 gate 阻断报告输出` 存在, `quality_gate_status: not_run` 存在, `run_started` 存在, `run_terminal` 不存在, 无 `UnboundLocalError`, 无 `分析失败：`, 无 `LLM Host run 未完成`

两个测试均正确覆盖了 **block** 和 **not-run** 两种 quality gate 阻断路径 + progress 启用的场景，断言项完整匹配 controller judgment 中列出的所有要求。

预现有测试 `test_analyze_cli_structured_quality_gate_not_run_block` (line 3110) 和 `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` (line 3137) 继续覆盖无 progress 场景的 quality gate 路径，未被修改。

## Regression Verification

### Host event_sink 语义

`fund_agent/host/runtime.py` 未被 fix 修改。`_commit_event` 的语义不变：
- 构造安全事件 → 追加到 `events` → 调用 sink → 返回事件
- Sink 异常记录到 `event_sink_errors` 后原样 raise
- Host 的 broad `except` 在 line 533 检查 `event_sink_errors[-1] is exc` 做 identity check 避免误吞

### 非目标区域

fix evidence 确认以下区域未被修改：
- 无 provider timeout/retry/backoff budget 变化
- 无 artifact schema 变化
- 无 chapter acceptance/auditor 逻辑变化
- 无 score/golden/readiness 变化
- 无 `docs/design.md` / `docs/implementation-control.md` / `docs/current-startup-packet.md` 更新

### 测试验证

Controller 提供的 rerun 结果：
- `tests/ui/test_cli.py`：72 passed（+2 新测试）
- 全量 targeted：191 passed（189 + 2 新测试）
- `ruff check .`：All checks passed

### `_run_llm_analysis_in_host()` 未变

质量 gate 异常 catch/re-raise 模式保持不变（`cli.py:1416-1419` catch, `cli.py:1427-1428` re-raise），Host runner 调用方式不变，`event_sink` 传递方式不变。

## Findings

未发现实质性问题。

DS F1 已正确修复，质量 gate block 和 not-run 路径 + `--use-llm --llm-progress` 不再产生 `UnboundLocalError`。新增测试覆盖充分，无回归风险。

## Open Questions

无。

## Residual Risk

- `run_started` progress 行会在 quality gate 阻断前由 Host 发出，属于正常的 Host 生命周期行为，不是 fake terminal line
- Fake 测试中的 `_FakeLLMBlockedAnalysisService` 直接在 `analyze_with_llm_execution()` 中 raise，不经过 Service 的 `_record_host_phase_started(phase="analysis_core")`。这意味着测试中 `phase_started phase=analysis_core` 不会出现在 quality gate 路径上。这与生产行为一致（生产路径下 quality gate 阻断发生在 `_run_analysis_core()` 内，在 `analysis_core` phase started 之后，但 `analysis_core` phase completed 不会出现）。测试不要求 `phase_started` 出现是合理的——quality gate 阻断先于 phase 记录的可能性也存在（如 `_check_pool_membership_before_extraction` 提前阻断）

## Verdict

**PASS**

DS F1 已修复，无新阻塞发现。原有其他审查项（Host boundary、secret safety、progress stderr-only、deterministic 不变性、heartbeat lifecycle、fail-closed）在首次审查中已确认正确，本次 fix 未触及这些区域。
