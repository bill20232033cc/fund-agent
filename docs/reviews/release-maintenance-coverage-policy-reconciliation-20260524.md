# Release Maintenance Coverage Policy Reconciliation

> Date: 2026-05-24
> Branch: `codex/coverage-policy-reconciliation`
> Work unit: document-only coverage policy reconciliation
> Result: accepted locally

## Scope

本次只关闭仓库级 residual：`Coverage policy reconciliation`。

根因是两套覆盖率口径没有显式区分：

- `AGENTS.md` 要求“单文件测试覆盖率目标为 ≥80%”。
- CI、README 和测试手册当前执行 `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`，这是项目全局覆盖率自动阻断 gate。

## Decision

保留当前 CI 全局 `--cov-fail-under=50`，不在本 gate 直接提高阈值。

理由：

- 当前仓库历史上 P3-S7 设定的是全局覆盖率 gate，用来防止发布测试面过窄。
- 单文件 ≥80% 是新增或大幅修改模块的评审目标，更适合在 code review、controller judgment 和 residual risk 中按变更范围裁决。
- 直接提高全局 CI 阈值会把未做缺口评估的历史模块变成脆弱阻断，不能证明新增代码质量真正改善。

## Changes

- `AGENTS.md` 保留单文件 ≥80% 标准，并明确这是新增或大幅修改模块的评审目标；暂未达到时必须在 review / residual risk 中说明。
- `README.md` 在本地验证和仓库产物策略中说明 CI 全局 50% 与单文件 80% 目标的关系。
- `tests/README.md` 将“覆盖率 gate”改写为自动阻断阈值，并补充单文件目标的执行方式。
- `docs/design.md` 在工程基线和 plan review 检查中加入覆盖率策略要求。
- `docs/implementation-control.md` 更新 Startup Packet、候选表、Active Gate Ledger 和状态日志。

## Non-Goals

- 不修改 `.github/workflows/ci.yml`。
- 不修改 `pyproject.toml`。
- 不提高或降低当前 CI coverage threshold。
- 不新增测试，也不把文档口径改动伪装成真实覆盖率提升。

## Validation

- `rg -n "单文件测试覆盖率目标|--cov-fail-under=50|单文件覆盖率 ≥80%|coverage policy reconciliation|覆盖率策略" AGENTS.md README.md tests/README.md docs/design.md docs/implementation-control.md docs/reviews/release-maintenance-coverage-policy-reconciliation-20260524.md`
- `git diff --check`

Both checks passed. Full test suite was not run because no code, config, runtime behavior, tests, or CI workflow changed.
