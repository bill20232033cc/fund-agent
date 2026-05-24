# Release Maintenance Slice D Controller Judgment — CI Coverage Gate

## Scope

- Source finding: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` Slice D.
- Handoff: `docs/reviews/release-maintenance-slice-d-ci-coverage-gate-handoff-20260523.md`.
- Worker: implemented a focused CI coverage gate patch.

## Accepted Changes

- `.github/workflows/ci.yml`
  - Replaces bare `uv run pytest -q` with `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`.
- `tests/test_repo_hygiene.py`
  - Adds a shared expected CI coverage command constant.
  - Asserts coverage collection, terminal missing report, and explicit `--cov-fail-under=50`.
- `README.md` and `tests/README.md`
  - Align release readiness and CI documentation with the enforced coverage command.

## Controller Verification

```bash
uv run pytest tests/test_repo_hygiene.py -q
```

Result: `3 passed in 0.02s`.

```bash
uv run ruff check tests/test_repo_hygiene.py
```

Result: `All checks passed!`.

```bash
git diff --check -- .github/workflows/ci.yml tests/test_repo_hygiene.py tests/README.md README.md
```

Result: passed.

## Judgment

Slice D is accepted. CI now enforces the existing documented 50% coverage baseline through `pytest-cov`, and the repo hygiene test will fail if the workflow returns to bare pytest.

## Residual Risk

The threshold remains the historical `50%` baseline. Raising it requires a separate coverage-improvement phase so the target is supported by actual missing-line analysis instead of a policy-only change.
