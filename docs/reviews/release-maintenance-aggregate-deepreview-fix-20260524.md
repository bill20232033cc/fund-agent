# Release Maintenance Aggregate Deepreview Fix 2026-05-24

## Scope

本次只修复 controller accepted findings：

- RM-AGG-C2：清理当前 source-facing docstring/comment 中把 `fund_agent/fund` 表述为 `Capability` / `Fund Capability` 层的旧口径。
- RM-AGG-C3：为 `fund_agent/ui/cli.py` 的 `_echo_checklist_result` 参数补充 `FundChecklistResult` 类型注解，并移除 `no-untyped-def` ignore。

未修改历史 review artifact、implementation-control archive 历史文字、README、design/control、测试夹具、golden 数据、依赖、lockfile、行为代码或公开 API。

## Changes

- 将 `fund_agent/fund/**/*.py` 当前源码注释/docstring 中的架构级旧术语替换为当前口径：
  - `Agent 层基金能力`
  - `基金领域能力`
  - `Agent 层基金能力 data 层`
  - `Agent 层基金能力 analysis 层`
- 将 `fund_agent/config/paths.py` 模块 docstring 中 `Fund Capability` 复用表述改为 `Agent 层基金能力` 复用。
- 在 `fund_agent/ui/cli.py` 中通过 `fund_agent.services` 导入 `FundChecklistResult`，并把 `_echo_checklist_result(result)` 改为 `_echo_checklist_result(result: FundChecklistResult)`。

## Capability Occurrences

`rg -n "Capability|Fund Capability" fund_agent` 无输出。

因此当前 source 下没有需要保留并解释的 `Capability` / `Fund Capability` occurrence。

## Validation

- `rg -n "Capability|Fund Capability" fund_agent`：通过，无输出。
- `uv run ruff check fund_agent/fund fund_agent/config/paths.py fund_agent/ui/cli.py`：通过，`All checks passed!`。
- `uv run pytest tests/ui/test_cli.py::test_checklist_cli_calls_service_and_prints_summary tests/services/test_fund_analysis_service.py::test_fund_analysis_service_checklist_returns_shared_core_without_rendering`：通过，`2 passed`。
- `git diff --check`：通过，无输出。

## Residual Risk

本次改动为源码注释/docstring 与 CLI 私有 helper 类型注解修复，不改变运行时行为。残余风险主要是历史文档和 archive 中仍存在旧 Capability 口径；按本 gate 范围这些属于历史证据，未修改。
