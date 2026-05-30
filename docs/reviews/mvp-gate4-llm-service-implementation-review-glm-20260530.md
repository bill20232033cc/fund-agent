# MVP Gate 4 Slice 4B Service analyze_with_llm implementation review (GLM)

日期：2026-05-30
角色：review worker (AgentGLM)
Gate：`MVP Gate 4 Slice 4B: Service analyze_with_llm implementation gate`
分类：`heavy`

## Verdict

**PASS**

实现正确满足 Slice 4B 全部审查 lens 要求。`analyze_with_llm()` 忠实复用 `_run_analysis_core()`，quality gate 异常传播完整，Gate 3/4 编排串联正确，无确定性回退，无越界修改。测试覆盖 accepted 路径、deterministic 路径不受影响、missing client fail-closed、quality gate block/not-run 传播和导入边界。

## Findings

无 BLOCKING 或 CRITICAL 级别发现。

### MEDIUM

无。

### LOW / Non-blocking

#### L1. FundLLMAnalysisResult 不携带中间分析产物

- **文件**: `fund_agent/services/fund_analysis_service.py:291-335`
- **事实**: `FundLLMAnalysisResult` 只保留 `structured_data`、`final_judgment_decision`、`llm_orchestration_result`、`final_assembly_result`、`quality_gate_result` 和 `quality_gate_not_run_reason`。不携带 `rabc_attribution`、`consistency_result`、`investor_experience`、`risk_check_result`、`stress_test_result`、`checklist_result`、`valuation_state_resolution` 或 `current_stage`。
- **评估**: Plan 明确允许最小实现路径"更小实现可不嵌套完整 FundAnalysisResult，但必须保留 deterministic core 中的 structured_data, final_judgment_decision, quality_gate_result, quality_gate_not_run_reason"。当前实现保留的字段覆盖 plan 最低要求。中间产物仍在 `_run_analysis_core` 内正确计算并用于派生 `final_judgment_decision`，未丢失计算链路。
- **风险**: 如果后续 CLI `--use-llm` 需要展示 checklist 或 R=A+B-C 中间结果，需扩展 result 类型。当前不影响 Slice 4B scope。

#### L2. orchestrate_chapters / assemble_final_chapters 为同步函数

- **文件**: `fund_agent/services/fund_analysis_service.py:626-638`
- **事实**: `orchestrate_chapters()` 和 `assemble_final_chapters()` 是同步函数（非 async）。`analyze_with_llm` 标记为 `async` 仅因 `_run_analysis_core` 调用了 `self._extractor.extract()` 异步协议。
- **评估**: 当前 Gate 3/4 实现不涉及网络 I/O，同步签名合理。若后续 Gate 3 writer/auditor 改为异步 LLM 调用，需调整此处集成。
- **风险**: 低。这是后续 Gate 5 或 provider 集成时的问题，当前不影响正确性。

## Correctness and Contract Verification

| 合约要求 | 验证结果 | 依据 |
|---|---|---|
| 复用 `_run_analysis_core()` | PASS | `fund_analysis_service.py:617-619` 调用 `self._run_analysis_core(replace(request, command_source="analyze"))` |
| `QualityGateBlockedError` 传播 | PASS | `_run_analysis_core` 内部 line 751-753 抛出，在 `analyze_with_llm` 中未被 catch；测试 `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration` 验证 writer/auditor 未被调用 |
| `QualityGateNotRunBlockedError` 传播 | PASS | `_run_analysis_core` 内部 line 750 抛出；测试 `test_analyze_with_llm_propagates_quality_gate_not_run_before_extraction` 验证 extractor 和 writer/auditor 未被调用 |
| 调用 Gate 3 orchestration | PASS | `fund_analysis_service.py:626-629` 调用 `orchestrate_chapters(orchestration_input, llm_clients=llm_clients)` |
| 总是调用 Gate 4 assembler | PASS | `fund_analysis_service.py:630-638` 无论 orchestration accepted/partial/blocked 都调用 `assemble_final_chapters()` |
| 不回退确定性报告 | PASS | `analyze_with_llm` 内无 `render_template_report`、`analyze()` 或 `FundAnalysisResult` 构造；测试 `test_missing_writer_or_auditor_blocks_without_deterministic_fallback` 验证 blocked orchestration 返回 incomplete assembly 而非 deterministic markdown |
| `llm_clients` keyword-only | PASS | `fund_analysis_service.py:589` 签名 `*, llm_clients: ChapterOrchestratorLLMClients` |
| 无 `extra_payload` | PASS | docstring 显式声明，grep 搜索无业务参数传递 |
| `report_markdown` fail-closed | PASS | `FundLLMAnalysisResult.report_markdown` 在 `report_markdown is None` 时抛出 `ValueError`；测试 line 243-244 验证 |

## Scope Boundary Verification

| 边界约束 | 验证结果 | 依据 |
|---|---|---|
| 不修改 CLI | PASS | diff 不含 `fund_agent/ui/cli.py` |
| 不构造 provider | PASS | 无 `openai`/`anthropic`/`httpx` 导入；LLM clients 通过 keyword-only 参数注入 |
| 不引入 Host/Agent/dayu | PASS | grep 边界检查通过；导入边界测试通过 |
| 不修改 quality/FQ/golden/score/snapshot | PASS | diff 不含 `quality_gate.py`、`golden_*.py`、`extraction_score.py`、`extraction_snapshot.py` |
| 不修改 Fund primitives | PASS | diff 不含 `fund_agent/fund/` 下任何文件 |
| 不修改 final judgment 语义 | PASS | `derive_final_judgment()` 未被修改；`analyze_with_llm` 只消费 `core_result.final_judgment_decision` |
| 不新增 repository/PDF/cache/source 直连 | PASS | 导入边界测试 `test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries` 通过；仅允许已有 `fund_agent.fund.data_extractor` transition import |
| `analyze()` 行为不变 | PASS | 测试 `test_deterministic_analyze_does_not_call_llm_orchestrator_path` 验证 |
| `checklist()` 行为不变 | PASS | 测试 `test_deterministic_checklist_does_not_call_llm_orchestrator_path` 验证 |

## Changed Files Audit

| 文件 | 状态 | 是否允许 |
|---|---|---|
| `fund_agent/services/fund_analysis_service.py` | modified (+124 行) | 允许 — 新增 `FundLLMAnalysisResult` dataclass 和 `analyze_with_llm()` method + Gate 3/4 imports |
| `fund_agent/services/__init__.py` | modified (+2 行) | 允许 — 导出 `FundLLMAnalysisResult` |
| `tests/services/test_fund_analysis_service_llm.py` | new untracked | 允许 — Slice 4B 新增测试文件 |
| `tests/README.md` | modified (+2 行) | 允许 — 新增测试文件说明 |

无越界文件修改。`git diff --check` clean。

## Test Adequacy

| 测试场景 | 覆盖 | 测试函数 |
|---|---|---|
| accepted 路径：fake extractor + fake writer/auditor -> accepted final assembly + report_markdown | PASS | `test_analyze_with_llm_returns_accepted_final_assembly_and_report_markdown` |
| deterministic `analyze()` 不调用 LLM | PASS | `test_deterministic_analyze_does_not_call_llm_orchestrator_path` |
| deterministic `checklist()` 不调用 LLM | PASS | `test_deterministic_checklist_does_not_call_llm_orchestrator_path` |
| missing auditor client -> blocked/incomplete，不回退 deterministic | PASS | `test_missing_writer_or_auditor_blocks_without_deterministic_fallback` |
| quality gate block 在 Gate 3 前传播 | PASS | `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration` |
| quality gate not-run 在 extraction 前传播 | PASS | `test_analyze_with_llm_propagates_quality_gate_not_run_before_extraction` |
| 导入边界：无 repository/PDF/cache/source/Host/dayu | PASS | `test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries` |

共 7 个测试。全部通过。

## Validation Performed

```text
$ uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py
All checks passed!
```

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_fund_analysis_service.py tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py -q
82 passed in 0.92s
```

```text
$ uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
51 passed in 0.46s
```

```text
$ git diff --check
(clean)
```

```text
$ rg -n "dayu|extra_payload|openai|anthropic|pdf|cache|source.helper|download" fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py
命中项均为既有 thermometer_cache_dir 参数、extra_payload 否定性 docstring 和已有 cache_dir 参数名；无新增越界导入。
```

```text
$ git diff --name-only
fund_agent/services/__init__.py
fund_agent/services/fund_analysis_service.py
tests/README.md
```

```text
$ git diff --stat
3 files changed, 128 insertions
```

## Residual Risk

1. **FundLLMAnalysisResult 中间产物不可达**: 如后续 CLI 需要展示 checklist 或 R=A+B-C 结果，需扩展 result 类型。当前不影响 Slice 4B。
2. **Gate 3/4 同步 vs 异步**: `orchestrate_chapters` 和 `assemble_final_chapters` 当前为同步函数。若后续 Gate 5 引入异步 LLM 调度，此处集成需调整。
3. **Slice 4C CLI `--use-llm` 依赖 4D**: 当前 `analyze_with_llm` 需要显式注入 `llm_clients`，CLI 层在 provider 构造未完成前必须 fail-closed。这属于 4C/4D scope，不影响 4B 正确性。
4. **无 `command_source="analyze_with_llm"` 选项**: `analyze_with_llm` 使用 `command_source="analyze"` 进入 `_run_analysis_core`。quality gate run id 将使用 "analyze" 前缀。这与 plan 一致（plan 要求 `replace(request, command_source="analyze")`），但若后续需要区分 LLM 与 deterministic 的 quality gate run id，需新增 command_source 值。
