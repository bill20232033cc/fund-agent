# MVP Service ExecutionContract boundary hardening Slice 1 code re-review

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Review target: Implementation Slice 1 - Service ExecutionContract Types
Source review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-review-20260601.md`
Role: Gateflow-governed code re-review worker, not controller

## Finding Status Mapping

### 001-已修复-[中]-开放参数袋负向测试在 future annotations 下失效

- **Source finding**: `001-未修复-[中]-开放参数袋负向测试在 future annotations 下失效`
- **Final title status**: `已修复`
- **复核范围**: 仅复核 controller-accepted finding 001 及其测试修复；未启动 `/gateflow` 或 `$gateflow`，未修改生产代码，未 commit/push/PR。

## Evidence And Validation

- `tests/services/test_execution_contract.py:379` 新增聚焦回归测试 `test_open_business_bag_guard_detects_future_annotation_strings()`，参数化覆盖 `dict[str, Any]`、`Mapping[str, Any]`、`typing.Mapping[str, Any]`，并额外覆盖带引号的 `"dict[str, Any]"` 字符串注解形态。
- `tests/services/test_execution_contract.py:501` 的 `_is_open_business_bag()` 现在先分支处理 `str` 注解，再走 `typing.get_origin()` / `typing.get_args()` 的原有真实类型判断。
- `tests/services/test_execution_contract.py:527` 的 `_is_open_business_bag_annotation_text()` 会去除外层引号和空格，并显式拒绝 `dict[str,Any]`、`Mapping[str,Any]`、`typing.Mapping[str,Any]`，因此可覆盖 `from __future__ import annotations` 导致的字符串注解。
- 只读复现旧 guard 行为：用旧逻辑对 `dict[str, Any]`、`Mapping[str, Any]`、`typing.Mapping[str, Any]` 字符串调用 `get_origin()` / `get_args()` 后均返回未命中，结果为 `False`；因此新增回归测试会在旧 guard 下失败。
- 变更保持在 Slice 1 测试边界内：本次 fix 复核目标是 `tests/services/test_execution_contract.py` 的测试 guard；未发现为修复该 finding 而改变生产行为。

Validation command:

```text
uv run pytest tests/services/test_execution_contract.py -q
```

Result:

```text
23 passed in 0.59s
```

该结果可信：命令在当前工作区直接重跑，覆盖新增字符串注解回归用例和现有 ExecutionContract 边界测试。

## Verdict

Code re-review verdict: accepted with no blocking findings
