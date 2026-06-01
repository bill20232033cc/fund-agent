# MVP Gate 4 Slice 4D2 Implementation Review (GLM)

日期：2026-05-30
角色：review agent（GLM）
Gate：`MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate`
分类：`heavy`

## Verdict

**PASS**

未发现 blocking finding。实现严格遵循 plan §10/§12 4D2、plan decision A1-A8 和 4D1 controller judgment 残余约束。所有 9 条审查 lens 均通过。

## Review Inputs

- Plan：`docs/reviews/mvp-gate4-provider-construction-plan-20260530.md` §10、§12 4D2
- Plan decision：`docs/reviews/mvp-gate4-provider-construction-plan-decision-20260530.md` A1-A8
- 4D1 controller judgment：`docs/reviews/mvp-gate4-provider-construction-4d1-controller-judgment-20260530.md`
- Implementation evidence：`docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md`
- Diff files：`fund_agent/ui/cli.py`、`tests/ui/test_cli.py`
- Source of truth：`AGENTS.md`、`docs/design.md` §5.4.1、`docs/current-startup-packet.md`

## Lens-by-Lens Findings

### Lens 1: 4D2 是否严格按 plan

| Plan 要求 | 实现状态 | 证据 |
|---|---|---|
| `_build_llm_clients_or_fail()` 返回 `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)` | ✅ | `cli.py:784-804`：签名返回 `tuple[ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy]`，调用 `load_llm_provider_config_from_env()` → `build_chapter_llm_clients(config)` → `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)` |
| `use_llm` 成功时调用 `analyze_with_llm`，不调用 deterministic `analyze` | ✅ | `cli.py:243-253`：`if use_llm:` 分支只调用 `analyze_with_llm(request, llm_clients=..., chapter_policy=...)`；`else:` 分支调用 `analyze(request)`。测试 `test_analyze_cli_use_llm_configured_calls_llm_service_and_prints_report` 断言 `analyze_called is False` 且 `analyze_with_llm_called is True` |

### Lens 2: Missing/invalid config 与 construction error

| 要求 | 实现状态 | 证据 |
|---|---|---|
| exit 1 | ✅ | `cli.py:254-259`：两个 catch 块均 `raise typer.Exit(code=1)` |
| stderr 分类清晰 | ✅ | Config error → `"LLM provider 配置错误：{exc}"`；Construction error → `"LLM provider 构造失败：{exc}"` |
| stdout empty | ✅ | 测试 `test_analyze_cli_use_llm_missing_config_fails_before_service` 和 `test_analyze_cli_use_llm_construction_error_fails_before_service` 均断言 `result.stdout == ""` |
| Service 不被调用 | ✅ | 同上测试断言 `analyze_called is False` 且 `analyze_with_llm_called is False` |

### Lens 3: LLM final assembly incomplete

| 要求 | 实现状态 | 证据 |
|---|---|---|
| exit 1 | ✅ | `cli.py:269-271`：`raise typer.Exit(code=1)` |
| stderr 以 `LLM 分析未完成：` 开头 | ✅ | `_llm_incomplete_message()` 返回 `"LLM 分析未完成：" + ...`；测试断言 `"LLM 分析未完成：" in result.stderr` |
| stdout empty | ✅ | 测试 `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` 断言 `result.stdout == ""` |
| 无 deterministic fallback | ✅ | 测试断言 `"# 0. 投资要点概览" not in result.output`（确定性报告标志内容不存在） |

### Lens 4: QualityGateBlockedError / QualityGateNotRunBlockedError

| 要求 | 实现状态 | 证据 |
|---|---|---|
| 仍 exit 2 | ✅ | `cli.py:260-265`：两个 catch 块均 `raise typer.Exit(code=2)` |
| LLM path 不吞掉 | ✅ | 新增 `_FakeLLMBlockedAnalysisService` 和 `_FakeLLMNotRunBlockedAnalysisService` 的 `analyze_with_llm()` 直接抛出 `QualityGateBlockedError` / `QualityGateNotRunBlockedError`；`analyze()` 方法抛出 `AssertionError("deterministic analyze must not be called")` 确保不回退 |
| 测试覆盖 | ✅ | `test_analyze_cli_use_llm_structured_quality_gate_block` 和 `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` 均断言 exit code 2、stdout empty、stderr 包含阻断信息 |

### Lens 5: Default analyze path 隔离

| 要求 | 实现状态 | 证据 |
|---|---|---|
| 不读取 LLM env | ✅ | `test_analyze_cli_default_product_request` monkeypatch `load_llm_provider_config_from_env` → `_forbid_llm_config`（触发 `AssertionError("default analyze must not read LLM config")`） |
| 不构造 provider | ✅ | 同测试 monkeypatch `build_chapter_llm_clients` → `_forbid_llm_clients`（触发 `AssertionError("default analyze must not construct LLM clients")`） |
| 不改变既有输出 | ✅ | 测试断言 `result.exit_code == 0`、`analyze_called is True`、`analyze_with_llm_called is False`、`last_request.mode == "product"` |

### Lens 6: checklist --use-llm

| 要求 | 实现状态 | 证据 |
|---|---|---|
| 仍是 Typer unknown option | ✅ | `checklist` 命令签名无 `--use-llm` 参数；既有测试 `test_checklist_cli_rejects_use_llm_option`（line 1800）验证 Typer 拒绝该选项，4D2 未修改 `checklist` 命令 |

### Lens 7: UI import boundary

| 要求 | 实现状态 | 证据 |
|---|---|---|
| CLI 不 import `fund_agent.fund.*` | ✅ | `grep` 结果：cli.py 无 `fund_agent.fund` import |
| CLI 不 import Host/dayu | ✅ | `grep` 结果：无 Host/dayu import |
| CLI 不 import provider SDK/httpx | ✅ | `grep` 结果：无 httpx/provider SDK import |
| CLI 不使用 extra_payload | ✅ | `grep` 结果：无 extra_payload |
| 只允许 config/Service public APIs | ✅ | Import 来源：`fund_agent.config.llm`（A6 授权直接 import）+ `fund_agent.services`（public `__init__.py`）+ `fund_agent.config.paths` |
| 既有 import boundary test 通过 | ✅ | `test_cli_module_imports_service_but_not_agent_internals` 未修改，仍检查 `"dayu", "extra_payload", "httpx"` 等禁止项 |

### Lens 8: Tests 充分性

| 测试路径 | 覆盖 | 证据 |
|---|---|---|
| Missing config → exit 1, stdout empty, no Service call | ✅ | `test_analyze_cli_use_llm_missing_config_fails_before_service` |
| Configured accepted → calls `analyze_with_llm()`, prints LLM report | ✅ | `test_analyze_cli_use_llm_configured_calls_llm_service_and_prints_report`；额外验证 `chapter_policy.max_output_chars == _FakeLLMConfig.max_output_chars` |
| Construction error → exit 1, no Service call | ✅ | `test_analyze_cli_use_llm_construction_error_fails_before_service` |
| Incomplete result → exit 1, no fallback | ✅ | `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` |
| Quality gate blocked (LLM) → exit 2 | ✅ | `test_analyze_cli_use_llm_structured_quality_gate_block` |
| Quality gate not-run (LLM) → exit 2 | ✅ | `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` |
| Default path isolation | ✅ | `test_analyze_cli_default_product_request` + `_forbid_llm_config` / `_forbid_llm_clients` |
| checklist --use-llm invalid | ✅ | `test_checklist_cli_rejects_use_llm_option`（4C 遗留，未修改） |
| No live network / real key | ✅ | 所有 CLI LLM 测试使用 monkeypatch 替换 config/factory；无真实 API key、endpoint 或 live transport |

### Lens 9: A8 compliance（未同步 design/control）

| 要求 | 实现状态 | 证据 |
|---|---|---|
| 4D2 不把 provider-backed path 写入 design/control docs | ✅ | `git diff` scope 只包含 `cli.py` 和 `test_cli.py`；evidence 文件为 review artifact，不是 design/control truth |

## Non-blocking Findings

### N1. Provider runtime errors 通过 generic Exception handler

`cli.py:266-268` 的 `except Exception` 会捕获 `LLMProviderRuntimeError` 及其子类（`RateLimitError`、`MalformedResponseError`），输出 `"分析失败：{exc}"`。

**为什么 non-blocking**：plan §11.2 明确 Service orchestrator 在 writer/auditor 层捕获 provider runtime errors 并映射为 `llm_exception` stop reason，最终表现为 incomplete final assembly（`report_markdown is None`）。因此正常路径下 provider runtime error 不会泄漏到 CLI。若 Service 未来有未捕获的 provider error 泄漏，generic handler 仍能 fail-closed（exit 1 + stderr + stdout empty），只是消息不如 config/construction 那样分类。

**建议**：若 4D3 或后续 gate 发现 runtime error 泄漏为高频场景，可新增 `except LLMProviderRuntimeError` 专有 catch。当前不阻塞。

### N2. Exception catch blocks 覆盖 if/else 两个分支

`LLMProviderConfigError` 和 `LLMProviderConstructionError` 的 catch blocks 位于 `try` 顶层，覆盖 `if use_llm:` 和 `else:` 两个分支。在 `else:` 分支中这些异常不可能被触发（`_build_llm_clients_or_fail()` 不被调用）。

**为什么 non-blocking**：逻辑安全，dead catch 不影响行为。将 catch blocks 移入 `if use_llm:` 分支内需要更深的嵌套或提取子函数，降低可读性。当前结构保持所有 exception handling 在同一缩进层级，是合理的 CLI 代码风格。

### N3. `_llm_incomplete_message` 参数无类型注解

`cli.py:807` 使用 `# type: ignore[no-untyped-def]`。`getattr` 访问模式允许函数同时接受真实 `FundLLMAnalysisResult` 和测试替身。

**为什么 non-blocking**：CLI display helper 不属于公共 API 或 Service contract；`getattr` 提供的鸭子类型兼容性在 CLI 层是合理的工程选择。

## Validation Reviewed

以下验证由 implementation evidence 报告，本次 review 未重新执行（review agent 不是 execution worker）：

- `uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py` → passed
- `uv run pytest tests/ui/test_cli.py -q` → 51 passed
- `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py -q` → 74 passed
- `uv run ruff check .` → passed
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` → 1106 passed, coverage 91.76%
- `git diff --check` → passed

以下由本次 review 独立验证：

- CLI import boundary：`grep` 确认无 `fund_agent.fund.*`、Host/dayu、httpx、extra_payload import
- Test import boundary：确认 test 文件中 `fund_agent.fund.*` import 为测试构造所需（`QualityGateIssue`、`ThermometerHistoryCache` 等），不影响 CLI import boundary test
- `analyze_with_llm` 签名：确认接受 `chapter_policy: ChapterOrchestrationPolicy | None = None`，CLI 传递了该参数
- `FundLLMAnalysisResult.report_markdown` property：确认在 `report_markdown is None` 时 raise `ValueError`，CLI 先检查 `result.final_assembly_result.report_markdown is None` 避免触发 property
- `ChapterOrchestrationPolicy` 默认 `max_output_chars=12000`：确认 A3 无需 pre-work
- `LLMProviderConfigError`（`fund_agent/config/llm.py`）和 `LLMProviderConstructionError`（`fund_agent/services/llm_provider.py`）分属不同模块，catch 顺序正确
- `checklist --use-llm` 测试（line 1800）确认仍存在且未被修改

## Scope Check

### 已发现项

- Scope 严格限制在 `fund_agent/ui/cli.py` 和 `tests/ui/test_cli.py`，加 evidence artifact
- 临时 `LLMProviderUnavailableError` 和 `LLM_PROVIDER_UNAVAILABLE_MESSAGE` 已移除（A5）
- `_build_llm_clients_or_fail()` 从 `NoReturn` 改为 `tuple[ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy]`（A5）
- 直接 import `fund_agent.config.llm`（A6 授权）

### 未发现越界项

- 未修改 Service/Fund/orchestrator internals
- 未修改 quality gate 语义
- 未修改 Gate 2/3/4 contract
- 未修改 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`（A8 遵守）
- 未修改 README、README.config、tests/README
- 未引入 Host/Agent/dayu
- 未引入 live provider smoke
- 未使用 `extra_payload`
- 未修改 final judgment 派生逻辑
- 未修改 golden/score/snapshot/promotion

## Residual Risks

| 风险 | 归属 | 说明 |
|---|---|---|
| 4D3 docs/control sync | 4D3 gate | provider-backed CLI path accepted 后仍需同步 design/startup/control docs |
| Provider runtime error 消息分类 | 未来 gate | 当前 generic handler 足够 fail-closed，但消息不如 config/construction 分类清晰 |
| `_llm_incomplete_message` 无类型注解 | future cleanup | CLI display helper 鸭子类型可接受，未来若类型系统收严可考虑 Protocol |
