# Release Maintenance Engineering Baseline Alignment Controller Judgment - 2026-05-23

## Scope

本裁决覆盖当前 `release maintenance documentation / engineering-baseline alignment` gate：

- `docs/design.md` 将规则权威、架构边界、P19 温度计事实和 Dayu 参考吸收范围对齐到 `AGENTS.md`。
- `docs/implementation-control.md` 将当前 release-maintenance 状态、候选后续工作和 residual risk 回写到总控。
- `pyproject.toml` / `uv.lock` 将项目工程基线切换到 setuptools + PEP 621 元数据、显式依赖和 test/dev 可选依赖分组。
- `docs/reviews/release-maintenance-engineering-baseline-build-fix-handoff-20260523.md` 记录 setuptools blocker 的 specialist handoff。

## Controller Decision

Accepted locally.

基于 `AGENTS.md` 的硬约束和 `docs/design.md` 的设计目标，当前最小正确动作不是引入 Dayu runtime，而是吸收其可迁移工程纪律：
Python 版本、打包后端、依赖声明、工具配置和分层边界检查。该 gate 不改变基金分析主链路、不新增 Host/Engine/tool loop，也不改变
Fund Capability 的年报仓库、审计、模板或温度计计算行为。

## Accepted Fix

Worker 修复了 setuptools/PEP 639 blocker：`pyproject.toml` 已保留 `license = "MIT"`，并移除旧式
`License :: OSI Approved :: MIT License` classifier。该修复符合最小变更原则，因为 license expression 已是当前 metadata 真源，
旧 classifier 只会导致 setuptools build/editable install fail-closed。

## Validation

Passed:

- `uv lock --check`
- `uv run python -c "import fund_agent; import pandas; print('ok')"`
- `ruff check fund_agent tests`
- `git diff --check docs/design.md docs/implementation-control.md pyproject.toml uv.lock docs/reviews/release-maintenance-engineering-baseline-build-fix-handoff-20260523.md docs/reviews/release-maintenance-engineering-baseline-alignment-controller-judgment-20260523.md`

Known failing validation:

- `pytest tests/test_repo_hygiene.py -q` -> `1 failed, 2 passed`
- Failure root cause: current worktree has `LICENSE` deleted, so `tests/test_repo_hygiene.py::test_license_and_package_metadata_are_declared`
  raises `FileNotFoundError` for `/Users/maomao/fund-agent/LICENSE`.
- Controller did not restore `LICENSE` because the deletion predates this gate's accepted write scope and must not be reverted without explicit user authorization.

## Boundary Check

- UI/Application/Runtime/Service/Engine/Capability boundary: documented as design truth; no source boundary change in this gate.
- Fund documents access boundary: untouched; no direct production PDF/cache/source access introduced outside `FundDocumentRepository`.
- Annual-report fallback taxonomy: untouched and remains covered by prior P1 source-taxonomy confirmation.
- Explicit parameters vs `extra_payload`: untouched; no new API parameter path.
- Dayu runtime: not introduced.

## Residuals

- `RR-20`: deterministic CLI still directly calls Service; future selected work should add a thin Application use-case facade without changing Fund Capability behavior.
- `RR-21`: engineering baseline is accepted, but repo hygiene remains blocked until the current `LICENSE` deletion is restored or explicitly confirmed.
- Push/PR/external actions remain unauthorized.
