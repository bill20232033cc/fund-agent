# MVP Gate 4 Slice 4B Service analyze_with_llm implementation review — MiMo

日期：2026-05-30

角色：review worker。只覆盖当前未合并 Slice 4B diff；不修改源码、不 commit、不 push、不 PR。

## Verdict

**PASS**

Slice 4B 实现满足 plan contract、controller amendments 和 review lens 全部要求。无阻断发现。

## Review scope

Diff 文件（纯新增，0 删除）：
- `fund_agent/services/fund_analysis_service.py` — +124 行
- `fund_agent/services/__init__.py` — +2 行（export `FundLLMAnalysisResult`）
- `tests/services/test_fund_analysis_service_llm.py` — 新增
- `tests/README.md` — +2 行（test location 和 quick-command 追加）

## Findings

无阻断或中等发现。

## Non-blocking observations

### O1. `FundLLMAnalysisResult` 缺少 `__all__` 显式 tuple 声明

`FundLLMAnalysisResult` 已正确通过 `__init__.py` 导出，但 `fund_analysis_service.py` 模块级没有 `__all__`。这不是 Slice 4B 引入的问题（既有模块也没有 `__all__`），仅记录一致性观察。不阻断。

### O2. `analyze_with_llm()` 没有 `command_source` 覆盖测试

当前 `analyze_with_llm()` 内部 `replace(request, command_source="analyze")` 硬编码为 `"analyze"`。测试中使用的 `_developer_request()` 默认 `command_source="analyze"`，因此覆盖了正常路径。如果未来调用方传入 `command_source="checklist"`，该值会被静默覆盖。这是 plan 要求的行为（Slice 4B 固定为 analyze），但没有显式测试该覆盖语义。不阻断。

### O3. 测试中 `_FakeChapterLLMClient` 和 `_FakeAuditLLMClient` 仅在测试文件内定义

符合 plan 要求"fake writer/auditor 只在测试内定义"。实现正确，仅确认。

## Validation performed

| 验证项 | 命令 | 结果 |
|--------|------|------|
| Lint | `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py` | All checks passed! |
| Slice 4B 测试 | `uv run pytest tests/services/test_fund_analysis_service_llm.py -q` | 7 passed |
| 相关回归 | `uv run pytest tests/services/test_fund_analysis_service.py tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q` | 75 passed |
| 全量覆盖率 | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | 1061 passed, 91.73% |
| Whitespace | `git diff --check` | clean |
| 静态边界 | `rg -n "dayu\|extra_payload\|openai\|anthropic\|pdf\|cache\|source helper\|download" fund_agent/services/fund_analysis_service.py` | 仅 docstring 中 `extra_payload` 反面提及，无越界导入 |
| `analyze/checklist` 未修改 | `git diff` grep `def analyze` / `def checklist` | diff 中无 analyze/checklist 签名变更 |

## Review lens checklist

| Lens | 结论 | 证据 |
|------|------|------|
| `analyze_with_llm` 复用 `_run_analysis_core` | ✅ | L617: `core_result = await self._run_analysis_core(replace(request, command_source="analyze"))` |
| `QualityGateBlockedError` 传播 | ✅ | 测试 `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration` 验证 writer/auditor 未被调用 |
| `QualityGateNotRunBlockedError` 传播 | ✅ | 测试 `test_analyze_with_llm_propagates_quality_gate_not_run_before_extraction` 验证 extractor 未被调用 |
| Gate 3 orchestration 始终调用 | ✅ | L626: `orchestrate_chapters(orchestration_input, llm_clients=llm_clients)` |
| Gate 4 assembler 始终调用 | ✅ | L630: `assemble_final_chapters(FinalChapterAssemblyInput(...))` |
| 不回退确定性报告 | ✅ | `report_markdown` property fail-closed: raise ValueError when None |
| `llm_clients` keyword-only | ✅ | L589: `*, llm_clients: ChapterOrchestratorLLMClients` |
| 无 `extra_payload` | ✅ | diff 中无 extra_payload 使用 |
| 无 CLI 变更 | ✅ | diff 不含 `cli.py` |
| 无 provider 构造 | ✅ | 无 openai/anthropic/httpx 导入 |
| 无 Host/Agent/dayu | ✅ | 静态扫描通过 |
| 无 repository/PDF/cache/source helper | ✅ | 导入边界测试 + 静态扫描 |
| 无 final judgment 语义变更 | ✅ | `FinalJudgmentDecision` 只消费不修改 |
| 无 quality gate/FQ 语义变更 | ✅ | 只传播不修改 |
| 无 golden/score/snapshot 变更 | ✅ | diff 不含相关文件 |
| 无 Fund primitive 变更 | ✅ | diff 不含 `fund_agent/fund/` |
| `analyze()` 不变 | ✅ | diff 无 analyze 签名/逻辑变更 |
| `checklist()` 不变 | ✅ | diff 无 checklist 签名/逻辑变更 |
| 测试覆盖 accepted path | ✅ | `test_analyze_with_llm_returns_accepted_final_assembly_and_report_markdown` |
| 测试覆盖 deterministic 不受影响 | ✅ | `test_deterministic_analyze_does_not_call_llm_orchestrator_path` + `test_deterministic_checklist_does_not_call_llm_orchestrator_path` |
| 测试覆盖 missing client fail-closed | ✅ | `test_missing_writer_or_auditor_blocks_without_deterministic_fallback` |
| 测试覆盖 import 边界 | ✅ | `test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries` |

## Residual risk

- Slice 4C CLI `--use-llm` 和 Slice 4D production provider construction 未实现，`--use-llm` 路径当前 fail-closed。
- `FundLLMAnalysisResult.report_markdown` 的 ValueError 消息包含 orchestration_status/assembly_status/issues，对调试友好，但 CLI 层尚未消费该异常（Slice 4C 职责）。
- `analyze_with_llm()` 中 `_run_analysis_core` 异常（包括底层 extractor 异常）会直接传播到调用方，不被 Service 层额外包装。这是正确行为，但调用方（CLI）需要在 Slice 4C 中处理这些异常。
