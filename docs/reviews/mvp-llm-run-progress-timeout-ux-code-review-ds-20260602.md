# Code Review

## Scope

- Mode: current changes
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Review target: unstaged implementation diff for MVP LLM run progress and timeout UX gate
- Output file: `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md`
- Included scope: `fund_agent/host/runtime.py`, `fund_agent/host/__init__.py`, `fund_agent/services/fund_analysis_service.py`, `fund_agent/ui/cli.py`, `tests/host/test_runtime_runner.py`, `tests/services/test_fund_analysis_service_llm.py`, `tests/ui/test_cli.py`, `README.md`, `fund_agent/host/README.md`, `tests/README.md`, implementation evidence
- Excluded scope: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, provider config/runtime budget, artifact schema, score/golden/readiness files
- Parallel review coverage: 无

## Findings

### 1-BLOCKING-高-quality gate 异常路径导致 `UnboundLocalError` 破坏 terminal progress 和错误信息

- **入口/函数**: `analyze()` 命令函数，`fund_agent/ui/cli.py:786-794`
- **文件(行号)**: `fund_agent/ui/cli.py:786-794`
- **输入场景**: `analyze --use-llm --llm-progress` 且 quality gate 在 block 策略下产生 `QualityGateBlockedError`，或 quality gate 未运行产生 `QualityGateNotRunBlockedError`
- **实际分支**: `_run_llm_analysis_in_host()` 内部 catch 了 quality gate 异常，存入 `quality_gate_exception` nonlocal 后 `raise`，Host runner 捕获该异常返回 `HostRunResult(status=FAILED)`，然后 `_run_llm_analysis_in_host()` 在 `cli.py:1424-1425` 检测到 `quality_gate_exception is not None` 并重新 `raise quality_gate_exception`
- **预期行为**: 按 accepted plan 要求："If `_run_llm_analysis_in_host()` re-raises an existing quality-gate exception before returning a result, preserve existing quality-gate stderr and exit code without inventing a fake terminal line." 即不调用 `emit_terminal`，让已有的 quality gate except handler 处理
- **实际行为**: `reporter.emit_terminal(host_result)` 在 `cli.py:794` 被执行，但 `host_result` 从未被赋值（因为 `host_result = _run_llm_analysis_in_host(...)` 右侧 raise 导致赋值未完成），触发 `UnboundLocalError`，被外层 `except Exception as exc:` (line 825) 捕获，输出错误的 `"分析失败：local variable 'host_result' referenced before assignment"` 而非正确的 quality gate 阻断信息
- **直接证据**:
  - `cli.py:786-794`: `host_result` 在 try 块内赋值，若 `_run_llm_analysis_in_host()` raise，`host_result` 未绑定
  - `cli.py:1418-1425`: `host_result = HostRuntimeRunner().run_sync(...)` 成功返回，但随后 `raise quality_gate_exception` 使函数 raise 而非 return
  - `cli.py:817-822`: quality gate except handler 可以正确处理，但 `UnboundLocalError` 在到达这些 handler 之前就已触发
- **影响**: quality gate 阻断路径的错误信息被替换为无意义的 `UnboundLocalError` 信息；terminal progress 行未被正确抑制（违反了 plan 中 "without inventing a fake terminal line" 的要求）
- **建议改法和验证点**:
  修改 `_run_llm_analysis_in_host()` 使其在 quality gate 异常路径上也返回 `host_result` 而非 re-raise，由调用方按 `host_result` 结果和额外信息决定处理方式。或调整 CLI 调用结构，在 `try/finally` 之外用独立 try/except 捕获 quality gate 异常，并在 except 分支中跳过 `emit_terminal`。
  需要新增测试：`test_analyze_cli_use_llm_progress_quality_gate_block_preserves_error`，验证 quality gate block + `--llm-progress` 时 exit code 仍为 2，stderr 包含正确的 quality gate 阻断信息，不出现 `UnboundLocalError` 或无意义的 terminal progress。
- **修复风险（低）**: 修改范围仅限于 `_run_llm_analysis_in_host()` 的异常传播策略或 CLI 调用结构，不影响 Host runner、progress reporter、Service 或其他路径
- **严重程度（高）**: 虽然 quality gate 阻断在生产中不是高频路径（需要精选池 CSV 中有该基金且 gate 策略为 block），但一旦触发会导致错误的用户可见错误信息，且违反了 accepted plan 中明确记录的契约

### 2-未修复-低-`_handle_phase_completed` 的 phase 匹配逻辑在 phase 值触发 `_progress_scalar` ValueError 时会错误地保持旧状态

- **入口/函数**: `_LLMProgressReporter._handle_phase_completed()`, `fund_agent/ui/cli.py:469-503`
- **文件(行号)**: `fund_agent/ui/cli.py:489`
- **输入场景**: `phase_completed` 事件的 diagnostics 中包含的 `phase` 值经过 `_progress_scalar()` 处理时触发 `ValueError`（例如 phase 值包含 forbidden 片段）
- **实际分支**: `_progress_scalar(phase)` (line 489) 抛出 `ValueError` → 传播到 `_handle_event()` → 传播到 `handle_event()` → 被 `except Exception` 捕获 → `_mark_sink_failed()` 被调用
- **预期行为**: sink 失败后 phase 状态被清除，heartbeat 被关闭，符合 fail-safe 行为
- **实际行为**: 实际上 `_mark_sink_failed()` 确实会清除状态并设置 `_sink_failed=True`，后续 heartbeat 会被抑制。但该 `ValueError` 发生前，`_progress_scalar(phase)` 已经被调用了一次用于比较 (line 489)，如果前一个 phase_started 的 phase 值本身非法（也触发 ValueError），当前 sink_failed 状态不会影响已完成的状态清除。这是正确的 fail-safe 行为。
- **直接证据**: `cli.py:489`: `if self._current_phase == _progress_scalar(phase):` — 异常在比较时触发，传播到上层 handler → `_mark_sink_failed()`。但在此之前的状态更新（lines 490-494）不会执行，这并不影响安全性，因为 sink failed 已标记。
- **影响**: 无实际影响；sink 正确地标记为 failed，heartbeat 被停止
- **建议改法和验证点**: 无需修复。当前行为是 fail-safe 的。但如果追求代码健壮性，可以在 `_handle_phase_completed` 中将 `_progress_scalar(phase)` 调用移到 try/except 外部统一处理
- **修复风险（低）**: 无
- **严重程度（低）**: 实际不影响行为；列为低优先级仅供参考

## Open Questions

1. quality gate block 路径 + progress 启用时是否应该在 Host runner 返回 FAILED 结果后仍输出 terminal progress 行？Plan 说 "without inventing a fake terminal line"，但 Host runner 确实返回了合法的终态结果。当前实现的问题是尝试输出 terminal 但因 `host_result` 未绑定而崩溃。如果修复了 Finding 1，应该输出 `run_terminal event=run_failed` 还是跳过？建议按 plan 原文跳过 terminal progress，仅保留现有 quality gate stderr 输出。

## Residual Risk

- quality gate + progress 路径无测试覆盖（plan 要求但未实现对应的测试）
- `_LLMProgressReporter` 未测试 `enabled=False` 时各方法的 no-op 行为（现有测试通过 monkeypatch 模拟 disabled 场景的集成测试覆盖了主要路径）
- 多个 phase 快速交替时（如同一 phase 的 started/completed 之间出现另一个 phase 的 started），heartbeat 可能短暂显示无 phase 状态（当前因为 Host runner 是同步的，phase 事件严格顺序，实际不会发生）
- `_heartbeat_tick` 在 `_heartbeat_loop` 中被调用时，如果 `_safe_echo` 抛出异常，异常在 `_heartbeat_tick` 内部被捕获并标记 sink_failed。但 `_heartbeat_loop` 的对 `_stop_event.wait()` 的调用不受影响，线程会在最多 1 秒内退出。daemon 线程确保进程退出时被清理

## Verdict

**PASS with 1 blocking finding**

Finding 1 (quality gate 异常路径导致 `UnboundLocalError`) 必须在 merge 前修复。其他方面（Host boundary、secret safety、progress stderr-only、deterministic 不变性、heartbeat lifecycle、fail-closed、event_sink 通用性、测试覆盖）均符合 accepted plan 要求且实现正确。
