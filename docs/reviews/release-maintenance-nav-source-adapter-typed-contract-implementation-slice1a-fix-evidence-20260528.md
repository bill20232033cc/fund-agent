# NAV Source Adapter Typed Contract Implementation Slice 1a Fix Evidence

## Scope

- Work unit: NAV repository/source adapter typed contract implementation gate.
- Current gate: Slice 1a code review fix.
- Role: fix worker; no controller action, no new gateflow, no commit, no push, no PR.
- Accepted findings fixed: AgentMiMo required finding and AgentDS F1-F4.
- Not fixed by controller instruction: AgentDS F5-F6.

## Files Changed

- `fund_agent/fund/data/nav_models.py`
- `tests/fund/data/test_nav_repository_contract.py`
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-fix-evidence-20260528.md`

## Findings Closed

- AgentMiMo required finding / DS F2: added `test_identity_mismatch_raises_identity_mismatch`, directly asserting `identity_status="identity_mismatch"` raises `NavDataContractError` with `category == "identity_mismatch"`.
- DS F3: added `test_empty_records_raises_not_found`, directly constructing `FundNavSeries(records=())` without the `_nav_series` helper so empty tuple is not converted to default records.
- DS F4: added `test_nav_type_unknown_raises_schema_drift`, directly asserting `nav_type="unknown"` raises `category == "schema_drift"`.
- DS F1: added a nearby comment in `_validate_record_shape` explaining that record-level share_class mismatch is classified as `integrity_error` because the source/share mapping identity is already series-level, while mixed record share classes corrupt one series' internal integrity.
- Optional low-risk focus fix: updated `test_record_share_class_mismatch_raises_integrity_error` to pass matching `nav_type="adjusted_nav"` and `adjusted_basis="dividend_adjusted_nav"` explicitly, keeping the test focused on share_class mismatch.

## Validation Outputs

```text
$ uv run pytest tests/fund/data/test_nav_repository_contract.py -q
..............                                                           [100%]
14 passed in 0.05s
```

```text
$ uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py
All checks passed!
```

## Residuals

- F5 and F6 remain intentionally unchanged per controller instruction.
- Slice 1a remains pure typed model and contract tests only; no adapter, repository, extractor, snapshot, score, quality gate, README, design, implementation-control, golden, or drawdown metric changes were made.
- `drawdown_stress` blocker remains unresolved; this fix does not promote NAV data to strong drawdown evidence.
