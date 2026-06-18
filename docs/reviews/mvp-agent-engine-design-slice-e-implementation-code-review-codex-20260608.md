# MVP Agent Engine Design Slice E Implementation Code Review (AgentCodex)

## Verdict

**PASS_WITH_RESIDUALS**

未发现 Slice E 范围内的 P0/P1 implementation code defect。DS review 后两个 P1 修复有同路径证据：

- repair Host phase event 回放已在 `fund_agent/services/agent_bridge.py:147-195` 实现，并由 `tests/agent/test_service_bridge.py:115-170` 覆盖。
- 旧 `chapter_orchestrator` direct execution dead code 已删除；当前 `orchestrate_chapters()` 在 `fund_agent/services/chapter_orchestrator.py:674-681` 只委托 `run_agent_chapter_orchestration_bridge()`，未再保留旧 `_run_single_chapter()` / Host phase wrapper / provider exception wrapper。

## Findings

### P0

无。

### P1

无。

### P2-1: `chapter_orchestrator` 模块 docstring 仍描述为“不接入 Host/Agent/dayu”

- 位置：`fund_agent/services/chapter_orchestrator.py:3-6`
- 证据：同一模块当前保留 `host_context: HostRunContext | None` 参数（`fund_agent/services/chapter_orchestrator.py:637`），并在 `fund_agent/services/chapter_orchestrator.py:674-681` 委托 `agent_bridge` 执行 Agent body runner。
- 问题：这是文档口径 drift，不是执行缺陷；但它会误导后续 reviewer/worker 以为 `chapter_orchestrator` 仍完全不接入 Agent/Host，从而降低边界审查效率。
- 建议：把模块 docstring 改为“Service 入口负责输入解析、早期 fail-closed 和委托 Agent bridge；Host cancel/deadline 仅透传到 bridge 翻译”，与 README 当前口径对齐。

### P2-2: evidence artifact 的汇总测试计数不是最新最终总数

- 位置：`docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md:85-98`
- 证据：evidence 记录 `162 passed` / `38 passed`；本次 reviewer 复跑同一 no-live 矩阵后为 `163 passed`，其中 `tests/agent` 为 39 个用例。差异来自 DS P1 follow-up 后新增的 repair phase event bridge 测试，evidence 在 `docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md:106-115` 另有 focused closure validation。
- 问题：不影响实现正确性，但 accepted evidence 的“Final validation”表述容易被误读为 P1 修复后的全量最终矩阵。
- 建议：后续 checkpoint 前可补一行 reviewer rerun 或更新最终汇总计数；不需要改代码。

## Constraint Checks

| 检查项 | 结论 | 证据 |
|---|---|---|
| Agent 包不导入 Host/Service | PASS | 静态扫描 `fund_agent/agent` 未发现 `fund_agent.host` / `fund_agent.services` import；测试覆盖 `tests/agent/test_contracts.py:240-263`、`tests/agent/test_tool_adapters.py:269-292`、`tests/agent/test_runner.py:290-303`。 |
| Service bridge 是 Host cancel/deadline 到 Agent 的翻译边界 | PASS | `fund_agent/services/agent_bridge.py:235-309` 把 `HostRunContext` 翻译为 `AgentSchedulerInterruption`；Agent 只消费 checker。 |
| ToolTrace 只保存安全标量 | PASS | forbidden metadata key 在 `fund_agent/agent/contracts.py:42-89` 校验，`to_safe_dict()` 在 `fund_agent/agent/contracts.py:241-267` 只输出 allowlisted scalar；工具适配层只记录 prompt/raw response 长度、issue id、状态和 error type，见 `fund_agent/agent/tools.py:151-188`、`244-303`、`306-340`、`377-402`。 |
| 不泄漏 prompt/draft/raw response/fact values/secret/header/model/base_url/provider config | PASS | 当前 trace 不输出这些 payload；测试 `tests/agent/test_tool_adapters.py:89-157`、`187-218`、`221-267`、`343-373` 覆盖。 |
| Agent repair 无 hidden retry | PASS | `AgentRepairPolicy.hidden_retry_allowed=True` fail-closed，见 `fund_agent/agent/contracts.py:270-301`；测试 `tests/agent/test_contracts.py:119-134`。 |
| patch/regenerate 显式 ledger | PASS | `decide_repair()` 将 `patch`/`regenerate` 映射为预算内 regenerate，见 `fund_agent/agent/repair.py:126-134`；runner 在 `fund_agent/agent/runner.py:491-517` 记录 repair decision 后再进入下一 attempt；测试 `tests/agent/test_runner.py:189-213`。 |
| needs_more_facts 不 source-probe | PASS | `fund_agent/agent/repair.py:102-109` 直接终止；测试 `tests/agent/test_repair_policy.py:32-47`、`tests/agent/test_runner.py:165-187`。 |
| Service bridge 保持 accepted conclusions / runtime diagnostics / prompt diagnostics / final assembly readiness | PASS | 投影逻辑在 `fund_agent/services/agent_bridge.py:69-93`、`312-349`、`509-643`；Service 集成测试与 final assembly 测试均通过。 |
| DS P1 repair Host phase event replay | PASS | `fund_agent/services/agent_bridge.py:147-195` 和 `tests/agent/test_service_bridge.py:115-170`。 |
| DS P1 old direct execution dead code deletion | PASS | `rg` 未在 `chapter_orchestrator.py` 找到旧 `_run_single_chapter` / `_raise_if_host_cancelled` / `_host_phase_started` / `_host_phase_completed` / `_provider_runtime_stop_reason`。 |
| no live provider / no network probe | PASS | 只运行本地 no-live pytest/ruff/diff-check；未运行 `--use-llm`、provider readiness、endpoint/DNS/curl/socket probe。 |

## Validation Evidence

本次 reviewer 执行：

```text
uv run pytest tests/agent tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py
163 passed in 1.01s
```

```text
uv run ruff check fund_agent/agent fund_agent/services/agent_bridge.py fund_agent/services/chapter_orchestrator.py tests/agent
All checks passed!
```

```text
git diff --check -- fund_agent/agent fund_agent/services/agent_bridge.py fund_agent/services/chapter_orchestrator.py tests/agent fund_agent/agent/README.md fund_agent/README.md tests/README.md docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md
PASS
```

静态检查：

```text
rg -n "fund_agent\.(host|services)|dayu|httpx|requests|socket|curl|FUND_AGENT|base_url|api_key|authorization|provider" fund_agent/agent
```

结果只命中文档/枚举/forbidden-key 文本和 provider-runtime 分类字符串，未发现 Agent 包反向 import、网络库或 provider config 读取。

## Residuals

- `pyproject.toml:71` 的 `claude-mimo = "fund_agent.tools.claude_mimo:app"` 是当前 workspace dirty change，但按用户约束视为接手前 unrelated change；未计入 Slice E implementation defect。它仍需要独立 owner/controller disposition，避免 accepted checkpoint 混入非 Slice E 入口点变更。
- `fund_agent/services/agent_bridge.py:502-505` 仍把 `blocked_scheduler_interrupted` / `blocked_internal_code_bug` 投影为既有 `llm_exception` stop reason。这保持当前 `ChapterRunStopReason` public contract，不作为本 Slice 阻断；若要区分 Host cancel/deadline，应另开 public contract slice。
- Agent runner typed path 由 Service orchestrator 既有测试覆盖，Agent 包自身 focused 测试主要覆盖默认 runner path；当前 no-live 集成矩阵通过，后续可补一个 `AgentRunPolicy(typed_template_path="typed_template_contract")` 的直接 runner 用例降低定位成本。
