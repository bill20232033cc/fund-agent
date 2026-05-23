# PR Fix Artifact — PR 12 CI Help Width

## Gate

- Current gate: PR fix
- Work unit: repo-deepreview-audit-type-guards
- PR: https://github.com/bill20232033cc/fund-agent/pull/12
- Source failure: GitHub Actions job `77480848328`

## Accepted Finding Status

### 1-已修复-CI help output depends on runner terminal width

- Source: CI failure in `tests/ui/test_cli.py::test_analyze_cli_help_documents_auto_valuation_and_opt_out`.
- Failure:
  - GitHub runner did not include full `--thermometer-cache-dir` text in Rich/Typer help output.
  - Local reproduction showed `COLUMNS=60` hides the long option while `COLUMNS>=80` includes it.
- Fix:
  - Updated the help-output test to assert user-facing valuation help text from rendered help output.
  - Verified `--thermometer-cache-dir` through Typer/Click command metadata instead of Rich table output, because GitHub Actions can truncate or fold long option names differently from local runs.
- Rationale:
  - This is a test determinism fix only. CLI behavior and production code did not change.

## Changed Files

- `tests/ui/test_cli.py`
- `docs/reviews/pr-fix-12-ci-help-width-20260523.md`

## Validation

- `COLUMNS=40 uv run pytest tests/ui/test_cli.py::test_analyze_cli_help_documents_auto_valuation_and_opt_out -q`
  - Result: `1 passed in 0.44s`
- `uv run pytest -q`
  - Result: `549 passed in 1.16s`
- `uv run ruff check .`
  - Result: `All checks passed!`

## Residual Risks

- None for this fix. The test now pins its own help rendering width.
