# MVP Gate 4 Slice 4C CLI --use-llm Implementation Review (GLM)

日期：2026-05-30
角色：GLM review worker（不是 controller，不是 implementation worker）
Gate：`MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate`
分类：`heavy`

## Verdict

**PASS**

Slice 4C 实现严格遵循 accepted plan 和 plan decision controller amendments。CLI 默认 `analyze` 路径逐行等价未变；`--use-llm` 在 provider construction 未 accepted 前于 Service 调用之前 fail-closed（exit 1、stdout 空、stderr 清晰、不输出确定性 Markdown、不回退、不注入 fake client）；`checklist` 不接受该 flag；无 forbidden runtime import、无 `extra_payload`、无 Service/Fund/final judgment/quality gate/golden/score/snapshot 变更。

## Findings

无 blocking、critical 或 medium findings。

### Non-blocking observations

#### O1. `_build_llm_clients_or_fail()` 返回类型 `NoReturn` 将在 Slice 4D 后变更

`cli.py:774` — `_build_llm_clients_or_fail()` 当前声明 `-> NoReturn`（始终 raise）。Slice 4D provider construction accepted 后，此函数应改为返回 `ChapterOrchestratorLLMClients` 并在 CLI 调用 `analyze_with_llm()` 时作为参数注入。当前签名是正确且充分的最小 fail-closed 表达；未来签名变更是 Slice 4D 的责任，不阻塞本 slice。

#### O2. 测试 `_FakeService.analyze_with_llm()` 存在但生产路径永不调用

`test_cli.py` 中 `_FakeService` 新增了 `analyze_with_llm()` 方法和 `analyze_with_llm_called` 标志。当前生产 CLI fail-closed 路径在 Service 构造之前就已 raise，因此该方法不会被调用。该设计为 Slice 4D 提供了现成测试桩，是合理的 forward-compatible 准备。

## Validation performed

### Lint

```text
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

### CLI tests

```text
$ uv run pytest tests/ui/test_cli.py -q
46 passed in 1.09s
```

### Gate 3/4 service regression

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
51 passed in 0.47s
```

### Fund-layer regression

```text
$ uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
51 passed in 0.43s
```

### Static boundary check

```text
$ rg -n "dayu|extra_payload|openai|anthropic|httpx|provider_sdk|pdf_cache|download_annual_report|annual_report_source" fund_agent/ui/cli.py
(no output — clean)
```

### Whitespace check

```text
$ git diff --check
(no output — clean)
```

### Full regression (from evidence artifact)

Evidence artifact 已记录全局 1064 passed、91.74% coverage、`--cov-fail-under=50` 通过。Review worker 确认范围与 timing 一致。

## Review lens checklist

| Lens | Result | Evidence |
|------|--------|----------|
| `analyze` without `--use-llm` deterministic and unchanged | PASS | `use_llm=False`（默认）不触发 `_build_llm_clients_or_fail()`，直接调用 `FundAnalysisService().analyze(request)`，与 pre-diff 代码路径逐行等价。测试断言 `analyze_called=True`、`analyze_with_llm_called=False`。 |
| `analyze --use-llm` fail-closed before Service call | PASS | `cli.py:247-248` — `use_llm=True` 时 `_build_llm_clients_or_fail()` 立即 raise `LLMProviderUnavailableError`；`cli.py:250-252` catch 后 stderr 输出消息、exit 1。`asyncio.run(FundAnalysisService().analyze(request))` 不执行。 |
| fail-closed stdout empty | PASS | 测试断言 `result.stdout == ""`。raise 后 `typer.echo(result.report_markdown)` 不可达。 |
| fail-closed stderr clear message | PASS | 测试断言 `"LLM provider 未配置/未实现" in result.stderr`。 |
| fail-closed exit 1 | PASS | 测试断言 `result.exit_code == 1`。 |
| checklist must not accept `--use-llm` | PASS | `checklist` 函数无该参数；测试断言 Typer 拒绝、`checklist_called=False`、`--use-llm not in option_names`。 |
| No fake writer/auditor clients in production CLI | PASS | 生产 CLI 不构造 `ChapterOrchestratorLLMClients`、不调用 `analyze_with_llm()`。fail-closed 发生在任何 client 构造之前。 |
| No provider SDK / openai / anthropic / httpx / Host / Agent / dayu | PASS | 静态检查 clean；`test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` 断言 9 项 forbidden term 不出现。 |
| No Service internals / Fund primitives / final judgment / quality gate / golden / score / snapshot changes | PASS | Diff 仅修改 `cli.py`（UI 层）、`test_cli.py`、`README.md`、`tests/README.md`。无 Service/Fund 文件变更。 |
| No `extra_payload` | PASS | Diff 中无该词。 |
| Tests adequately cover default analyze | PASS | `test_analyze_cli_calls_service_and_prints_report` 增加断言 `analyze_called=True`、`analyze_with_llm_called=False`。 |
| Tests cover fail-closed `--use-llm` | PASS | `test_analyze_cli_use_llm_fails_closed_before_service` 覆盖 exit 1、stdout 空、stderr 消息、无 deterministic markdown、Service 未调用。 |
| Tests cover checklist unknown option | PASS | `test_checklist_cli_rejects_use_llm_option` 覆盖 exit != 0、Typer 拒绝、Service 未调用。 |
| Tests cover help text | PASS | `test_analyze_cli_help_documents_auto_valuation_and_opt_out` 增加断言 `--use-llm` 在 help 和 Click params 中。 |
| Boundary imports test | PASS | `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` 新增，覆盖 9 项 forbidden import term。 |
| Quality gate deterministic behavior unchanged | PASS | `LLMProviderUnavailableError` catch 在 `QualityGateNotRunBlockedError`/`QualityGateBlockedError` catch 之前，但默认 `use_llm=False` 从不触发前者；后者路径逐行等价于 pre-diff。 |

## Residual risk

- Slice 4D production LLM provider construction remains residual / future gate。
- `--use-llm` 当前是可见 opt-in 入口但在 provider construction accepted 前生产 CLI 必须继续 fail-closed。
- Chapter 0/7 LLM polish、LLM audit、Evidence Confirm/E2 source verification、Host/Agent/dayu integration 仍按 Route C 后续 gate 处理。
- `_build_llm_clients_or_fail()` 签名 `-> NoReturn` 需在 Slice 4D 后变更为返回 typed clients。

## Scope confirmation

- 本 review 不修改源代码。
- 未 commit、push、PR、merge、release、promotion 或清理 untracked files。
- Review artifact 仅写入 `docs/reviews/`。
