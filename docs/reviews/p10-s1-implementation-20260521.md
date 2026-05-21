# P10-S1 Repo Hygiene / Release Readiness Implementation

- **Date**: 2026-05-21
- **Gate**: `P10-S1 implementation`
- **Plan**: `docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`
- **Controller judgment**: `docs/reviews/p10-s1-plan-review-controller-judgment-20260521.md`

## Holder Confirmation

The implementation blocker was cleared by maintainer confirmation in chat:

- MIT copyright holder: `bill20232033cc`

## Implemented Scope

- Added root MIT `LICENSE` using the confirmed holder string.
- Added `[project].license = "MIT"` to `pyproject.toml`.
- Added GitHub Actions CI at `.github/workflows/ci.yml` for Python 3.11 with:
  - `uv sync --extra dev --frozen`
  - `uv run ruff check .`
  - `uv run pytest -q`
- Tightened `.gitignore` for local test/build artifacts, generated report outputs, runtime caches, and `docs/*.docx`.
- Added static repository path defaults in `fund_agent/config/paths.py`.
- Migrated UI / Service / Fund Capability default path aliases to `fund_agent.config.paths`.
- Kept `fund_agent.ui.cli.DEFAULT_QUALITY_GATE_SCORE` CLI-local as the historical P4 score fixture path.
- Kept `fund_agent/config/__init__.py` without path re-exports.
- Updated README, developer README, config README, and test README for current repo hygiene and path policy.
- Added repo hygiene and path migration guard tests.
- Updated `golden-build` default input to the reviewed Markdown fixture path:
  `reports/golden-answers/golden-answer-prefill-reviewed.md`.

## Validation

Passed:

```bash
uv run pytest tests/test_repo_hygiene.py tests/config/test_paths.py -q
uv run pytest tests/test_repo_hygiene.py tests/config/test_paths.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate_integration.py tests/fund/test_golden_answer.py tests/fund/documents tests/fund/pdf tests/fund/data -q
uv run ruff check .
uv run pytest -q
git diff --check
uv lock --check
git check-ignore "docs/fund-agent_仓库级综合审核报告_2026-05-21.docx"
```

Observed final full-suite result:

- `388 passed`

## Worktree Notes

- `docs/fund-agent_仓库级综合审核报告_2026-05-21.docx` remains local and ignored by `.gitignore`.
- `docs/reviews/code-review-p8-s3-ds-20260521.md` remains a durable review artifact for inclusion.
- Existing pre-implementation worktree changes in `docs/implementation-control.md` and P10 plan/review artifacts were not reverted.
