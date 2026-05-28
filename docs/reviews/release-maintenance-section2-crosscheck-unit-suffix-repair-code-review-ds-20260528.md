# Section2 Crosscheck Unit Suffix Repair Code Review DS

> Date: 2026-05-28
> Gate: code review
> Work unit: section2 crosscheck unit suffix repair gate
> Reviewer: DS
> Role: code review worker, not controller

## Gate / Reviewed Target / Conclusion

- **Gate**: code review
- **Reviewed target**:
  - Plan: `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-plan-20260528.md`
  - Implementation: `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-implementation-20260528.md`
  - Diff target: `fund_agent/fund/extractors/bond_risk_evidence.py`, `tests/fund/extractors/test_bond_risk_evidence.py`
- **Review scope**: only the current gate increment:
  - `_DECIMAL_UNIT_SUFFIXES = ("份",)`
  - `_parse_plain_decimal()` terminal suffix stripping
  - unit suffix regression tests
  - regression confirmation that prior §10 unlabeled alignment / §2 cross-check skeleton remains fail-closed
- **Conclusion**: PASS

## Findings

No findings.

## Direct Evidence

- `fund_agent/fund/extractors/bond_risk_evidence.py:42` defines `_DECIMAL_UNIT_SUFFIXES: Final[tuple[str, ...]] = ("份",)`, so the implementation whitelists only the terminal `份` unit suffix.
- `fund_agent/fund/extractors/bond_risk_evidence.py:2331-2335` compacts text, removes commas, and strips only a matching terminal suffix from `_DECIMAL_UNIT_SUFFIXES`; it does not broadly delete arbitrary non-numeric characters.
- `fund_agent/fund/extractors/bond_risk_evidence.py:2340-2345` still rejects `%` and returns `None` on `InvalidOperation`, preserving fail-closed parsing for non-numeric values after suffix stripping.
- Local parse probe result:
  - `_parse_share_decimal("5,711,224,267\n.09份") == Decimal("5711224267.09")`
  - `_parse_share_decimal("5,711,224,267.09") == Decimal("5711224267.09")`
  - `_parse_share_decimal("N/A份") is None`
  - `_parse_share_decimal("abc份") is None`
- `fund_agent/fund/extractors/bond_risk_evidence.py:1621-1636` still requires §2 cross-check only for `_SHARE_CHANGE_ALIGNMENT_UNLABELED`; missing cross-check returns `share_class_ending_cross_check_missing`, and mismatch returns the validator result.
- `fund_agent/fund/extractors/bond_risk_evidence.py:1795-1855` still reads §2 profile rows from an independent table and excludes the current §10 table by `(page_number, table_index)`, preventing unlabeled §10 self-certification.
- `fund_agent/fund/extractors/bond_risk_evidence.py:1924-1947` still compares each §10 class ending value against the §2 cross-check value and fails closed on missing or mismatched classes.
- `tests/fund/extractors/test_bond_risk_evidence.py:676-701` covers real newline + `份` cells and asserts accepted redemption share pressure.
- `tests/fund/extractors/test_bond_risk_evidence.py:704-731` covers invalid `N/A份` fail-closed parsing and missing cross-check acceptance prevention.
- `tests/fund/extractors/test_bond_risk_evidence.py:631-673` keeps the clean numeric unlabeled §10 / §2 cross-check path accepted.
- `tests/fund/extractors/test_bond_risk_evidence.py:876-919` keeps missing and mismatched unlabeled cross-check paths fail-closed.

## Validation

```bash
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
```

Result: passed (`All checks passed!`)

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
```

Result: passed (`58 passed in 0.76s`)

```bash
uv run python -c 'from fund_agent.fund.extractors import bond_risk_evidence as m; print(m._parse_share_decimal("5,711,224,267\n.09份")); print(m._parse_share_decimal("5,711,224,267.09")); print(m._parse_share_decimal("N/A份")); print(m._parse_share_decimal("abc份"))'
```

Result: `5711224267.09`, `5711224267.09`, `None`, `None`

## Hard Constraint Check

- Only terminal `份` suffix is stripped via whitelist: PASS.
- `N/A份` / `abc份` remain fail-closed: PASS.
- Unlabeled §10 columns still require independent §2 cross-check: PASS.
- No reviewed evidence of score policy / quality gate / schema / drawdown / credit_risk / Service/UI/Host/Agent/dayu / golden/release changes in this gate increment: PASS.
- Tests cover real newline + `份`, clean numeric, invalid suffix fail-closed, missing cross-check fail-closed, and mismatch cross-check fail-closed: PASS.

## Open Questions / Residual Risk

- Real 006597/2024 extraction snapshot was not run by this reviewer; implementation artifact already records it as outside the worker's required validation commands.
- The full `git diff` contains prior gate changes in the same files. This review intentionally scoped findings to the specified unit suffix repair increment and only sanity-checked that the prior §10 unlabeled alignment / §2 cross-check skeleton remains intact.

## Controller Decision Status

- Placeholder: pending controller disposition.

## Worker Self-Check

- Current gate / role: code review worker; did not start gateflow and did not act as controller.
- Scope boundary: reviewed only the specified increment and regression surface; did not modify source, tests, score policy, quality gate, schema, Service/UI/Host/Agent/dayu, golden, release, git state, PR, push, or merge.
- Evidence and validation: required artifacts/diff were read; targeted ruff, pytest, and parse probe passed.
- Completion signal: durable review artifact written at `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-code-review-ds-20260528.md`.

