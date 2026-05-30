# Section2 Crosscheck Unit Suffix Repair Code Review - MiMo

> Date: 2026-05-28
> Reviewer: MiMo
> Gate: code review
> Work unit: section2 crosscheck unit suffix repair gate
> Reviewed target:
> - `fund_agent/fund/extractors/bond_risk_evidence.py`
> - `tests/fund/extractors/test_bond_risk_evidence.py`
> - current `git diff -- fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`

## Conclusion

PASS

No blocking findings.

## Findings

No findings.

## Direct Evidence

- `_parse_plain_decimal()` compacts text and removes commas before suffix handling, then strips only configured terminal suffixes from `_DECIMAL_UNIT_SUFFIXES = ("份",)` before `Decimal(normalized)`. The implementation does not delete arbitrary non-numeric text and still returns `None` on `InvalidOperation`.
- Dash behavior remains unchanged: `_parse_share_decimal()` passes `dash_as_zero=True`, while `_parse_plain_decimal()` defaults `dash_as_zero=False`.
- Percentage behavior remains unchanged because values containing `%` are rejected before Decimal parsing.
- §2 profile ending-share cross-check remains independent from §10: `_share_class_ending_cross_check_from_profile_tables()` skips the current §10 table by `(page_number, table_index)` identity before looking for the §2 same-table name/code/ending rows.
- `test_redemption_share_pressure_aligns_real_profile_unit_suffix_newline_values` models real 006597 §2 cells including `5,711,224,267\n.09份`, `4,760,029,01\n5.27份`, `25,795,859.1\n2份`, and `52,531,021.8\n4份`, then asserts `redemption_share_pressure` is accepted.
- `test_redemption_share_pressure_keeps_invalid_unit_suffix_value_fail_closed` asserts `N/A份` is not parsed and the extractor remains ambiguous with `share_class_ending_cross_check_missing`.
- Existing fail-closed coverage still asserts missing §2 cross-check, §2/§10 mismatch, and §10 self-certification attempts are not accepted.

## Validation

```bash
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
```

Result: passed (`All checks passed!`)

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
```

Result: passed (`58 passed in 0.47s`)

```bash
uv run python -c "from fund_agent.fund.extractors import bond_risk_evidence as m; print(m._parse_share_decimal('5,711,224,267\n.09份')); print(m._parse_share_decimal('N/A份')); print(m._parse_share_decimal('abc份')); print(m._parse_share_decimal('80.00%')); print(m._parse_share_decimal('-')); print(m._parse_plain_decimal('-'));"
```

Result:

```text
5711224267.09
None
None
None
0
None
```

## Open Questions / Residual Risk

- No blocking open questions.
- Real 006597/2024 end-to-end extraction snapshot was not run in this review pass; implementation artifact already records it as outside the worker's required validation. The targeted parser and extractor tests cover the unit-suffix failure mode.
- Workspace contains pre-existing dirty/untracked artifacts from prior gates. This review did not classify or dispose of unrelated files.

## Scope Check

- No schema, score, quality-gate, drawdown, credit_risk, Service/UI/Host/Agent/dayu, golden, release, PR, push, merge, or closeout behavior was reviewed as accepted scope for this gate.
- Review remained limited to terminal `份` suffix parsing and §2/§10 cross-check tests.

## Controller Decision Status

Pending controller disposition.

## Worker Self-Check

- Current gate / role: code review specialist; not controller.
- Source of truth: `AGENTS.md`, approved plan artifact, implementation artifact, and current target diff were read.
- Scope boundary: only reviewed the assigned two files and this review artifact; no production/test code edits, no commit, no push, no PR.
- Stop conditions: none found.
- Completion signal: durable review artifact written with PASS and no blocking findings.
