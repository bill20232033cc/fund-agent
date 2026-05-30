# MVP Gate 4 Slice 4C CLI --use-llm implementation review (MiMo)

日期：2026-05-30
角色：review worker
Gate：`MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate`

## Verdict

**PASS**

无 blocking、critical 或 medium findings。实现与 plan、plan decision controller amendments、Slice 4B controller judgment 和 evidence artifact 完全一致。

## Findings

无。

## Non-blocking observations

### O1. `_build_llm_clients_or_fail()` 返回类型 `NoReturn` 与 Slice 4D 演进

`fund_agent/ui/cli.py:774` 函数签名为 `def _build_llm_clients_or_fail() -> NoReturn`，当前实现始终抛出 `LLMProviderUnavailableError`，`NoReturn` 类型正确。当 Slice 4D provider construction 接受后，该函数将实际返回 `ChapterOrchestratorLLMClients`，签名需同步修改为非 `NoReturn` 返回类型。此为预期演进，不阻断当前 slice。

### O2. `LLMProviderUnavailableError` 消息常量与测试断言方式

`fund_agent/ui/cli.py:66` 定义 `LLM_PROVIDER_UNAVAILABLE_MESSAGE = "LLM provider 未配置/未实现"` 为模块级常量。`tests/ui/test_cli.py:933` 使用 `assert "LLM provider 未配置/未实现" in result.stderr` 硬编码字符串匹配。若后续修改常量值但忘记同步测试，测试仍可能通过（子串匹配）。风险极低，因为该常量的唯一用途就是此 fail-closed 路径。

## Validation performed

```text
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
$ uv run pytest tests/ui/test_cli.py -q
46 passed in 0.72s
```

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
51 passed in 0.48s
```

```text
$ uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1064 passed in 4.96s
Required test coverage of 50% reached. Total coverage: 91.74%
```

```text
$ rg -n "dayu|extra_payload|openai|anthropic|httpx" fund_agent/ui/cli.py
(no output)
```

```text
$ git diff --check
clean
```

## Review checklist

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 不传 `--use-llm` 时 deterministic analyze 行为不变 | PASS | `test_analyze_cli_calls_service_and_prints_report` 断言 `analyze_called=True`、`analyze_with_llm_called=False` |
| `--use-llm` 在 Service 调用前 fail-closed | PASS | `_build_llm_clients_or_fail()` 始终抛出；test 断言 `last_request is None`、`analyze_called=False` |
| fail-closed stdout 为空 | PASS | test 断言 `result.stdout == ""` |
| fail-closed stderr 消息清晰 | PASS | test 断言 `"LLM provider 未配置/未实现" in result.stderr` |
| fail-closed exit code 为 1 | PASS | test 断言 `result.exit_code == 1` |
| `checklist` 不接受 `--use-llm` | PASS | `test_checklist_cli_rejects_use_llm_option` 断言 exit != 0、`checklist_called=False`、option_names 不含 `--use-llm` |
| 无 fake writer/auditor client 注入生产 CLI | PASS | `_build_llm_clients_or_fail()` 始终抛出，不返回 client |
| 无 provider SDK / openai / anthropic / httpx 导入 | PASS | `rg` 无匹配 |
| 无 dayu / extra_payload 导入 | PASS | `rg` 无匹配 |
| 无 Host/Agent/dayu 变更 | PASS | diff 只涉及 `cli.py`、`test_cli.py`、`README.md`、`tests/README.md` |
| 无 Fund primitive / final judgment / quality / golden / score / snapshot 变更 | PASS | diff 不涉及 |
| help 文档包含 `--use-llm` | PASS | `test_analyze_cli_help_documents_auto_valuation_and_opt_out` 断言 |
| boundary imports 静态检查 | PASS | `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` |
| Service 上游测试无回归 | PASS | 51 passed |
| 全量测试无回归 | PASS | 1064 passed, 91.74% coverage |
| ruff 无 lint 问题 | PASS | clean |
| git diff --check 无 whitespace 问题 | PASS | clean |

## Residual risk

- Slice 4D production LLM provider construction 仍为 residual / future gate。`--use-llm` 当前生产路径始终 fail-closed。
- `--use-llm` 是可见 CLI 入口，用户可尝试使用但会收到明确的失败消息。
