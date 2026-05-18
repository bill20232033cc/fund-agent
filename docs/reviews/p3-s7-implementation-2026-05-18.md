# P3-S7 Implementation - Coverage Gate

## Verdict

Implemented.

P3-S7 establishes a reproducible coverage gate for the current fund-agent test matrix and verifies that total coverage is above the 50% target.

## Scope

- Added `pytest-cov>=7.1` to the `dev` optional dependency group in `pyproject.toml`.
- Updated `tests/README.md` with the coverage gate command:

```bash
pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

## Validation

Executed:

```bash
.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Result:

```text
115 passed
Required test coverage of 50% reached. Total coverage: 90.07%
```

## Boundary Check

- No production code changed.
- Coverage measurement covers `fund_agent` package code.
- The gate keeps deterministic test scope and avoids real network/PDF smoke behavior.

## Residual Risk

Coverage is a breadth signal, not a substitute for semantic review. The real PDF/network smoke path remains outside this deterministic coverage gate.
