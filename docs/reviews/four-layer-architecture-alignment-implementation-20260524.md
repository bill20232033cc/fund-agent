# Four-Layer Architecture Alignment Implementation

## Gate

- Work unit: release maintenance four-layer architecture alignment
- Branch: `codex/checklist-host-engine-design`
- Date: 2026-05-24
- Status: completed locally

## Scope

This implementation aligns the repository with the current `AGENTS.md` source of truth:

```text
UI -> Service -> Host -> Agent
```

## Implemented Changes

- Removed the historical six-layer Application facade:
  - deleted `fund_agent/application/__init__.py`
  - deleted `fund_agent/application/use_cases.py`
  - deleted `tests/application/test_use_cases.py`
- Updated `fund_agent/ui/cli.py` so the UI imports and invokes Service layer entry points directly.
- Updated UI and config boundary tests so UI is allowed to depend on `fund_agent.services`, while remaining forbidden from directly importing `fund_agent.fund`.
- Updated Service docstrings from old Application/Capability wording to Service / Agent-layer fund capability wording.
- Restored root `LICENSE` to satisfy repo hygiene and keep `pyproject.toml` `license = "MIT"` aligned with the release-readiness test.
- Added `pythonpath = ["."]` to `[tool.pytest.ini_options]` so full-suite collection can import repository-local `tests` and `scripts` modules consistently under `uv run pytest`.
- Updated design/control/README documentation to:
  - use `UI -> Service -> Host -> Agent` as the target architecture;
  - state that future Host work must use `dayu.host`;
  - state that future Agent execution/tool-loop work must use `dayu.engine`;
  - keep current deterministic production flow as UI -> Service -> `fund_agent/fund`;
  - describe `fund-analysis checklist` as a real Service use case sharing the `analyze` core;
  - record current Quality Gate and `derive_final_judgment()` behavior.

## Non-Goals

- Did not create placeholder `fund_agent/host` or `fund_agent/agent` packages.
- Did not add `dayu.host` or `dayu.engine` dependencies to `pyproject.toml`.
- Did not change fund analysis rules, annual-report source orchestration, renderer output, quality gate rules, or thermometer calculation behavior.
- Did not push, create a PR, modify external issues, or touch RR-13 source CSV.

## Validation

```bash
uv run pytest -q
# 614 passed

uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
# 614 passed, total coverage 91.94%

uv run ruff check .
# All checks passed

uv lock --check
# Resolved 75 packages

uv run python -c "import fund_agent; import pandas; print('ok')"
# ok

git diff --check
# passed
```

Focused regression scans:

```bash
rg -n "fund_agent\\.application|fund_agent/application|tests/application|FundAnalysisUseCase|ThermometerUseCase|ExtractionSnapshotUseCase|ExtractionScoreUseCase|GoldenPrefillUseCase|GoldenAnswerUseCase|QualityGateUseCase|UseCase" fund_agent tests README.md docs/design.md docs/implementation-control.md pyproject.toml
# no matches

rg -n 'UI CLI 只依赖 Application|Application 层入口|禁止 UI 直接导入 Service|checklist.*占位|占位命令|仍是占位|repo hygiene 测试仍因|LICENSE.*已删除|当前工作区 `LICENSE` 已删除' docs/design.md docs/implementation-control.md README.md fund_agent/README.md fund_agent/config/README.md fund_agent/fund/README.md tests/README.md tests/config/test_paths.py
# no matches
```

## Residual Risks

- Host and Agent generic execution packages remain intentionally unimplemented. Future work must enter a separate gate with concrete session/run/tool-loop requirements and explicit `dayu.host` / `dayu.engine` dependency decisions.
- Historical review artifacts still mention older six-layer attempts as past decisions; current design/control documents mark those paths as superseded.
- Current deterministic Service path still directly calls `fund_agent/fund` public ability because Host/Agent dispatch is not yet a production requirement.

## Completion Signal

The four-layer architecture alignment is locally complete and ready for local acceptance. No external action has been taken.
