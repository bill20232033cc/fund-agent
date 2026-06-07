# MVP Agent Engine Design Slice E Implementation Code Review (AgentDS)

## 审查范围

仅审查当前未提交 Slice E 实现变更（git diff HEAD），对照已接受的 Slice E plan 和 controller
约束。不触发 live LLM、provider、endpoint/DNS/curl/socket probe，不修改代码、control doc
或外部状态。

## 审查方法

逐文件阅读 + 对照 plan scope/constraint 逐项 check + adversarial failure pass
（边界违规、静默行为回退、安全泄漏、类型擦除、测试缺口）。

## 总体结论

**有条件通过，1 个 P0 阻断项（无关入口点泄入 pyproject.toml），2 个 P1 回归风险
（repair phase event 丢失 + 旧 orchestrator 死代码留存），若干 P2 标注问题。**

---

## 变更清单逐项审查

| 文件 | 变更性质 | 审查结论 |
|---|---|---|
| `fund_agent/agent/contracts.py` | 新文件，Agent 契约 dataclasses | PASS |
| `fund_agent/agent/tools.py` | 新文件，Fund tool adapters + ToolTrace | PASS |
| `fund_agent/agent/repair.py` | 新文件，Agent repair policy | PASS |
| `fund_agent/agent/runner.py` | 新文件，Agent body runner | PASS（附 P2 标注）|
| `fund_agent/services/agent_bridge.py` | 新文件，Service→Agent bridge | PASS（附 P1 标注）|
| `fund_agent/services/chapter_orchestrator.py` | 修改：编排入口切换到 Agent bridge | **P1** 死代码留存 |
| `fund_agent/README.md` | 文档同步 | PASS |
| `fund_agent/agent/README.md` | 新文件，Agent 包开发手册 | PASS |
| `tests/README.md` | 测试目录同步 | PASS |
| `pyproject.toml` | 新增 `claude-mimo` 入口点 | **P0 阻断** |
| `tests/agent/*.py` | 5 个新测试文件 | PASS（附 P2 标注）|

---

## P0 阻断（必须在 accept 前解决）

### P0-1: `pyproject.toml` 泄入无关入口点 `claude-mimo`

**位置**: `pyproject.toml` line 71

```toml
claude-mimo = "fund_agent.tools.claude_mimo:app"
```

**问题**: `claude-mimo` 是一个独立的 tools 模块入口点，与 Slice E Agent Engine
实现完全无关。该模块 (`fund_agent/tools/claude_mimo.py`) 在本次 diff 的 4
个已修改文件中均未出现，但通过 `pyproject.toml` 变更被连带引入 staged area。

**风险**:
- 如果 `fund_agent/tools/claude_mimo.py` 不存在或不可导入，`uv sync` 后的 CLI
  entry point 注册会失败。
- 即便文件存在，此变更超出了 Slice E controller 授权范围（gate scope =
  Agent engine contracts/tools/repair/runner/bridge/README），是一次未经 gate
  review 的侧面入口点注册。

**建议**: 从本次变更中移除该行；如果 `claude-mimo` 需要独立入口点，应在独立
gate 中走完整 plan/review/accept 流程。

---

## P1 高优先级（应在 accept 前修复或记录为 explicit residual）

### P1-1: Repair phase event 丢失（bridge 不回放 repair 阶段事件）

**位置**: `fund_agent/services/agent_bridge.py` `_phase_from_tool_name()` (line 186-203)

```python
def _phase_from_tool_name(tool_name: str) -> str | None:
    if tool_name == "fund.write_chapter":
        return "writer"
    if tool_name == "fund.audit_chapter_llm":
        return "auditor"
    return None
```

**问题**: 旧 `chapter_orchestrator._run_single_chapter()` 在 regenerate 路径中
显式记录了 `_host_phase_started(host_context, phase="repair", ...)` 和对应的
`_host_phase_completed` (旧文件 line 1259-1288)。Agent bridge 的
`_record_agent_phase_events()` 通过 ToolTrace 回放 phase events，但 Agent
runner 内 repair decision 不产生独立 ToolTrace——repair 是通过重入 writer
实现的——因此 bridge 层不会产生任何 `phase="repair"` 的 Host event。

**影响**: 现有 Host event consumer（production diagnostics、monitoring、phase
timeline reconstructor）可能依赖 `phase="repair"` 事件来区分首写与修复重写。
缺少此事件会导致：
- 无法区分首次写入耗时与修复写入耗时
- 修复次数无法从 Host event stream 中重建

**建议**: 方案 A——在 bridge `_record_agent_phase_events()` 中，当 Agent attempt
的 repair_decision 非 None 且 action 为 "regenerate" 时，补录 `phase="repair"`
事件。方案 B——如果认为 repair phase event 不是 Host 层关注点，在
implementation evidence 或 residual 中显式记录此行为变更及接受依据。

### P1-2: `chapter_orchestrator.py` 残留大量死代码

**位置**: `fund_agent/services/chapter_orchestrator.py` lines 1044-1500+

**问题**: `orchestrate_chapters()` 函数已切换到 `run_agent_chapter_orchestration_bridge()`
委托路径，但旧实现 `_run_single_chapter()` 及其辅助函数全部保留在文件中：
- `_run_single_chapter` (line 1044-1304, ~260 行)
- `_exception_result` (line 1307-1368, ~60 行)
- `_raise_if_host_cancelled` (line 1371-1386)
- `_host_phase_started` / `_host_phase_completed` (line 1389-1424)
- `_provider_runtime_stop_reason` (line 1427-1449)
- `_exception_runtime_diagnostics` (line 1452+)
- 以及更多未列的旧 helper

这些函数已没有任何调用方。它们的存在:
- 增加代码库维护负担（阅读者可能误以为双路径并存）
- 可能导致后续开发者错误地回退到旧路径
- 类型检查器（mypy/pyright）会分析但不会标记为 dead code

**建议**: 删除所有已不再调用的旧实现函数。如果担心回滚需求，应从 git
history 恢复而非保留在 HEAD 中。

---

## P2 建议修复（不阻止 accept，但建议在后续迭代中处理）

### P2-1: `_terminal_from_writer_stop_reason` 在两个模块中重复定义

**位置**:
- `fund_agent/agent/tools.py` line 439-475
- `fund_agent/agent/runner.py` line 1113-1147

两处实现完全一致（相同 mapping logic）。runner.py 中的版本被 `_run_single_chapter`
内部使用，tools.py 中的版本被 tool adapter 使用。但从模块边界看，这是 agent
层的内部重复，应该只保留一份。

**建议**: 从 tools.py 移除，统一使用 runner.py 中的定义，或者提取到 contracts.py
作为公共映射函数。

### P2-2: `_service_stop_reason_from_task` 中 scheduler interrupted 映射为 `"llm_exception"`

**位置**: `fund_agent/services/agent_bridge.py` line 473-474

```python
if task.terminal_state == "blocked_scheduler_interrupted":
    return "llm_exception"
```

**问题**: `blocked_scheduler_interrupted` 表示 Host cancel 或 deadline exceeded，
这与 LLM provider 异常（`llm_exception`）是两类完全不同的失败模式。将 scheduler
中断映射为 `llm_exception` 会：
- 使 Service diagnostics 的上游消费者无法区分"系统被取消"与"LLM provider 崩溃"
- Host cancel 的语义被静默覆盖

**现状**: 测试 `test_service_bridge_translates_host_cancel_to_agent_interruption`
(line 71-106) 显式断言 `row.stop_reason == "llm_exception"`，说明这是当前
有意为之的行为。

**建议**: 新增专用 stop reason（如 `"host_cancelled"` 或
`"scheduler_interrupted"`）并更新相关测试断言。此变更涉及
`ChapterRunStopReason` Literal 类型扩展，属于 public contract 变更，建议
在独立 slice 中处理。

### P2-3: Agent runner 测试未覆盖 typed_template_contract path

**位置**: `tests/agent/test_runner.py`

所有 runner 测试使用默认 `AgentRunPolicy()`，其
`typed_template_path="legacy_contract"`。没有测试覆盖
`typed_template_path="typed_template_contract"` 路径中
`_typed_chapter_contract()` / `_typed_required_output_items()` 的调用行为。

**风险**: 如果 typed contract path 的 wiring 存在 bug（例如
`_typed_required_output_items` 返回空元组但 typed path 实际已启用），
当前测试无法发现。

**建议**: 增加至少一个 typed_template_contract path 的 runner 测试。

### P2-4: `_writer_input` 中多处 `# type: ignore[arg-type]` 注解

**位置**: `fund_agent/agent/runner.py` lines 558-562

```python
repair_context=repair_context,  # type: ignore[arg-type]
prompt_payload_mode=policy.prompt_payload_mode,  # type: ignore[arg-type]
...
    else None,  # type: ignore[arg-type]
```

3 处 type: ignore 表明 Agent runner 和 Fund writer input 之间的类型不完全
对齐。虽然通过了测试，但这些 ignore 会抑制未来类型漂移的检测。

**建议**: 在 Fund writer 层为这些参数声明显式 Protocol/Union 类型，消除
Agent 层的 type: ignore。

### P2-5: `_HostInterruptionChecker` 中的 `cancel_if_deadline_exceeded()` 有副作用

**位置**: `fund_agent/services/agent_bridge.py` line 248

```python
exceeded = self.host_context.cancel_if_deadline_exceeded()
```

此调用**会修改** Host cancellation token 的状态（如果 deadline 已超过则将其标记为
cancelled）。类名 `_HostInterruptionChecker` 暗示这是一个只读检查器，但实际上
它有写副作用。

**建议**: 将类重命名为 `_HostInterruptionTranslator`，或在 docstring 中明确
标注"本调用会 side-effect Host context（将过期 deadline 转为 cancel 状态）"。

---

## 约束合规检查

| 约束 | 状态 | 证据 |
|---|---|---|
| Agent 包不导入 `fund_agent.host` | **PASS** | AST 测试 `test_agent_contracts_do_not_import_host_or_service` 验证；人工确认 |
| Agent 包不导入 `fund_agent.services` | **PASS** | 同上 |
| ToolTrace 不序列化 prompt/draft/raw response/secret/headers/model/base_url/provider config | **PASS** | `_FORBIDDEN_SAFE_METADATA_KEYS` frozenset (20 key) + `to_safe_dict()` allowlist + test |
| `derive_evidence_availability` 不是 ToolRegistry tool | **PASS** | `test_supported_tool_names_exclude_run_level_evidence_availability` 断言 |
| Service 保留 provider 构造、用例、Host 翻译、diagnostics、final assembly | **PASS** | `agent_bridge.py` / `chapter_orchestrator.py` 分工确认 |
| Host 保持业务不透明 | **PASS** | `_HostInterruptionChecker` 只访问 cancel/deadline，不触及基金语义 |
| No live LLM / provider readiness / endpoint probe | **PASS** | 无此类调用 |
| Agent repair 不隐藏 retry | **PASS** | `AgentRepairPolicy.hidden_retry_allowed` 固定 `False` |
| patch 和 regenerate 都映射为整章重写 | **PASS** | `decide_repair()` line 127-133 |

## 测试质量评估

5 个新测试文件，38 个用例全部通过：

- `test_contracts.py` (6 tests): 覆盖 ToolTrace 安全序列化、metadata key 拦截、
  hidden retry 禁止、scheduler interruption 契约、frozen dataclass、import
  边界。**质量: 好**。
- `test_tool_adapters.py` (7 tests): 覆盖 4 个工具 adapter、异常 trace 安全、
  import 边界。**质量: 好**。
- `test_repair_policy.py` (5 tests): 覆盖 patch/regenerate 映射、needs_more_facts
  终止、预算耗尽、LLM unavailable、repair context 脱敏。**质量: 好**。
- `test_runner.py` (7 tests): 覆盖全章 accepted、单章 writer blocked 不跳过后章、
  provider timeout 分类、未知异常 code_bug 分类、needs_more_facts 终止不探查、
  修复预算耗尽记录每次 attempt、cancel/deadline 中断。**质量: 好**（缺 typed
  template path 测试，见 P2-3）。
- `test_service_bridge.py` (3 tests): 覆盖 accepted/partial/cancelled 三类
  bridge 投影。**质量: 基本够用**（3 个用例对 bridge 投影逻辑来说偏少）。

## Adversarial Failure Pass

对以下 adversarial 场景做了走查：

1. **ToolTrace metadata 注入攻击**: `_normalize_safe_metadata` 使用
   `key.lower() in _FORBIDDEN_SAFE_METADATA_KEYS` 检查。大小写不敏感匹配，
   覆盖 `Authorization`/`authorization`/`AUTHORIZATION` 等变体。**PASS**。

2. **`response_chars` 泄漏 raw response 长度**: LLM 审计工具的
   `response_chars` 来自 `len(audit_result.raw_response)` (tools.py line 293)。
   这是合法的标量信息（长度不泄漏内容），但需确保 future 不通过
   `response_chars` 通道发送内容文本。当前实现安全。**PASS**。

3. **Agent runner 无限循环**: `_run_single_chapter` while True 循环的唯一
   continue 路径是 `decision.action == "regenerate"`，且受
   `repair_policy.max_content_repair_attempts` 限制。每次 loop 都 increment
   `attempt_index`，`remaining_budget` 递减。当 `remaining_budget <= 0` 时
   `decide_repair` 返回 `action="stop"`。循环必然终止。**PASS**。

4. **Bridge 中 `fund_agent.host` 导入**: `agent_bridge.py` 导入了
   `HostRunContext`。这是**允许的**——bridge 属于 Service 层，Service 层有权
   导入 Host。Agent 包本身（`fund_agent/agent/`）不导入 Host。**PASS**。

5. **Orchestrator 仍然导入 `HostRunContext`**: `chapter_orchestrator.py` line
   48: `from fund_agent.host import HostRunContext`。这是 Service 层导入 Host，
   合规。但 `orchestrate_chapters()` 不再直接使用 `host_context` 做章节级
   cancel 检查——旧代码中 `_raise_if_host_cancelled(host_context)` 被移除，
   现在 Host cancel/deadline 只通过 Agent bridge 的 `_HostInterruptionChecker`
   在 Agent phase 边界（before_chapter/before_writer/after_tool_call/
   between_writer_and_auditor/before_repair_decision）生效。这意味着 cancel
   检测频率从旧实现的"每次 phase 边界 + 每次 writer/auditor 调用前"降为
   仅 Agent phase 边界。**PASS（行为变更，但 Agent phase 边界仍然覆盖关键点）**。

## 残留风险总结

| 风险 | 严重度 | Owner |
|---|---|---|
| pyproject.toml 无关入口点泄入 | P0 | 需在 accept 前修复 |
| Repair phase Host event 丢失 | P1 | 本 gate 修复或记录为 explicit residual |
| 旧 orchestrator 死代码留存 | P1 | 本 gate 清理 |
| Scheduler interrupted → llm_exception 映射不准 | P2 | 后续 slice |
| 缺 typed template path runner 测试 | P2 | 后续 slice |
| 多处 type: ignore 抑制类型检查 | P2 | 后续 slice |

## 审查人

AgentDS (Claude Opus 4.7) — 2026-06-08
