# MVP Service ExecutionContract boundary hardening Slice 1 code review

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Review target: Implementation Slice 1 - Service ExecutionContract Types
Role: Gateflow-governed code review worker, not controller
Reviewed files:

- `fund_agent/services/execution_contract.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_execution_contract.py`

## Findings

### 001-未修复-[中]-开放参数袋负向测试在 future annotations 下失效

- **入口/函数**: `test_new_dataclasses_and_public_signatures_exclude_open_business_bags()` / `_is_open_business_bag()`
- **文件(行号)**: `tests/services/test_execution_contract.py:366`、`tests/services/test_execution_contract.py:370`、`tests/services/test_execution_contract.py:486`
- **输入场景**: `fund_agent/services/execution_contract.py` 使用 `from __future__ import annotations`，后续有人在新增 contract/request/policy dataclass 字段时写入 `dict[str, Any]` 或 `Mapping[str, Any]`。
- **实际分支**: 测试通过 `dataclasses.fields(public_object)` 读取 `field.type`，再把该值传给 `typing.get_origin()` / `typing.get_args()` 判断开放业务参数袋。
- **预期行为**: Slice 1 plan 要求新增 Service contract 测试真实断言 dataclass fields 和 public signatures 不含 `extra_payload`、`**kwargs`、`dict[str, Any]` 或 `Mapping[str, Any]`；因此在 future annotations 场景下也必须能识别开放映射类型。
- **实际行为**: dataclass `Field.type` 在当前模块里是字符串，`get_origin("dict[str, Any]")` 返回 `None`，所以 `dict[str, Any]` / `Mapping[str, Any]` 字段会逃过 `_is_open_business_bag()`。当前 targeted test 仍显示 `19 passed`，但它不能证明 plan 要求的负向保护真实有效。
- **直接证据**:
  - 目标模块启用了 postponed annotations：`fund_agent/services/execution_contract.py:9`。
  - 当前运行时检查显示新增 dataclass 字段注解均为字符串，例如 `FundLLMRuntimePlan [('chapter_policy', 'ChapterOrchestrationPolicy', 'str'), ..., ('host_timeout_seconds', 'int', 'str')]`，`FundLLMExecutionRequest [('contract', 'FundLLMExecutionContract', 'str'), ..., ('llm_clients', 'ChapterOrchestratorLLMClients', 'str')]`。
  - 复现同类失败：对字符串注解 `"dict[str, Any]"` 调用 `get_origin()` / `get_args()` 得到 `None` / `()`，不会触发 `_is_open_business_bag()`。
  - `typing.get_type_hints(FundLLMRuntimePlan)` 当前还会因 TYPE_CHECKING-only 名称 `ChapterOrchestrationPolicy` 未进入 runtime globals 而 `NameError`，说明不能简单依赖现有 helper 已解析真实类型。
- **影响**: Slice 1 最关键的边界回归保护之一没有生效。实现目前没有发现实际开放业务参数袋，但后续 slice 或维护改动可以把 `dict[str, Any]` / `Mapping[str, Any]` 加进 contract/request/policy dataclass 而不被该测试拦截，违反 approved plan 的 extra_payload/open-bag 禁令。
- **建议改法和验证点**: 修正测试 guard，使它同时覆盖字符串注解和可解析注解。可选做法是对 `field.type` / parameter annotation 为 `str` 的情况做文本级拒绝，至少覆盖 `dict[str, Any]`、`Mapping[str, Any]`、`typing.Mapping[str, Any]`；或在测试中用 `typing.get_type_hints(..., globalns=...)` 注入 `ChapterOrchestrationPolicy`、`FinalAssemblyPolicy`、`ChapterOrchestratorLLMClients`、`FundAnalysisDeveloperOverrides` 等 TYPE_CHECKING-only 名称后再判定。建议加入一个测试专用样本或 monkeypatch，证明 `dict[str, Any]` 字符串注解会被 guard 拒绝。验证命令：`uv run pytest tests/services/test_execution_contract.py -q`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中
- **blocking**: yes

## Scope And Boundary Notes

- Slice 1 scope: reviewed diff only touches allowed files; no CLI/Service execution method/Host/provider env hookup was introduced in the reviewed diff.
- `FundLLMExecutionContract`: current fields are limited to fund identity, report mode, opt-in mode, normalized business input and quality declaration; reviewed fields do not include provider clients, Host lifecycle, runtime-only policies, or diagnostic display toggles.
- `FundLLMRuntimePlan` / `FundLLMExecutionRequest`: current docstrings identify them as Service-internal and hold runtime-only plan/client fields outside the stable contract.
- `derive_host_timeout_seconds`: current implementation follows the approved formula `max(1, (writer + auditor + repair) * attempts * chapter_count)` and validates positive `chapter_count`; provider budget validation rejects nonpositive provider timeouts and attempts.
- `normalize_fund_llm_analysis_input`: current implementation preserves deterministic request business fields and normalizes `command_source` to `analyze`; no provider/runtime semantics were added.

## Validation

- `uv run pytest tests/services/test_execution_contract.py -q` -> passed, `19 passed in 0.65s`.
- Additional runtime annotation inspection confirmed the test gap described in finding 001.

## Verdict

Code review verdict: not accepted due to 1 blocking finding.
