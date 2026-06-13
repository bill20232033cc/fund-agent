# Implementation Review: Fixture Promotion State Year-aware Schema / Parser

Date: 2026-06-13

Reviewer: AgentMiMo (implementation review worker)

Gate: `Fixture Promotion State Year-aware Schema / Parser Implementation Gate`

## Verdict

**PASS**

## 1. Scope Verification

### Diff Scope

Diff stat:

```text
fund_agent/fund/README.md                     |   2 +-
fund_agent/fund/golden_readiness_preflight.py | 159 +++++++++++++--
tests/README.md                               |   4 +-
tests/fund/test_golden_readiness_preflight.py | 277 +++++++++++++++++++++++++-
4 files changed, 424 insertions(+), 18(-)
```

Disposition: `PASS` — exactly the allowed write set.

### Boundary Confirmation

- Did not edit golden-answer files, fixture files, promotion state manifest content, `docs/design.md`, control docs, root README, pyproject or `.gitignore`.
- Did not run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR commands.
- Release/readiness remains `NOT_READY`.

## 2. Contract Compliance

### 2.1 Schema Version

`FIXTURE_PROMOTION_STATE_SCHEMA_VERSION = "fund-agent.fixture-promotion-state.year-aware.v1"` — matches accepted contract exactly.

### 2.2 Exact Promotion Identity Key

`_load_year_aware_fixture_promotion_states()` builds `states: dict[tuple[str, int], PromotionState]` keyed by `(fund_code, report_year)`. `_derive_fixture_promotion_state()` looks up via `fixture_states.fund_year_states.get((artifact.fund_code, artifact.report_year))`. Matches accepted contract.

### 2.3 Required `promotion_identity == "fund_year"` with Fail-closed

`_load_year_aware_fixture_promotion_states()` line 1342-1343:

```python
if promotion_identity != "fund_year":
    raise ValueError("fixture promotion entry promotion_identity 必须是 fund_year")
```

Fail-closed confirmed.

### 2.4 Duplicate `(fund_code, report_year)` Raises `ValueError`

Lines 1348-1352:

```python
key = (fund_code, report_year)
if key in states:
    raise ValueError(
        f"fixture promotion entry duplicate identity: {fund_code}/{report_year}"
    )
```

Fail-closed confirmed.

### 2.5 Unknown Top-level and Entry Fields Raise `ValueError`

Top-level: `_reject_unknown_keys(payload, {"schema_version", "accepted_as_of", "source_artifacts", "entries"}, ...)` at line 1299-1303.

Entry-level: `_reject_unknown_keys(entry, {"fund_code", "report_year", "promotion_state", "promotion_identity", "evidence_artifacts"}, ...)` at lines 1320-1328.

Fail-closed confirmed.

### 2.6 Legacy Fund-code-only Diagnostic-only

`_load_fixture_promotion_states()` routes legacy `entries` without `report_year` and legacy `{fund_code: state}` mappings to `FixturePromotionStates(fund_year_states={}, legacy_fund_states=states)`. `_derive_fixture_promotion_state()` checks `legacy_state` only after exact year lookup fails, returning `fixture_promotion_legacy_fund_only` blocker with `promotion_state="unknown"`. Matches accepted contract.

### 2.7 State/Blocker Mapping Table

| Condition | Expected | Actual | Match |
|---|---|---|---|
| Exact `promoted_fixture` | state=`promoted_fixture`, blocker=none | Lines 1947-1948: returns no blocker | YES |
| Exact `not_promoted` | state=`not_promoted`, blocker=`fixture_promotion_absent` | Lines 1949-1964: returns `fixture_promotion_absent` blocker | YES |
| Exact `unknown` | state=`unknown`, blocker=`fixture_promotion_unknown` | Lines 1965-1980: returns `fixture_promotion_unknown` blocker | YES |
| Exact missing + legacy exists | state=`legacy_fund_only`, `promotion_state=unknown`, blocker=`fixture_promotion_legacy_fund_only` | Lines 1981-1998: returns `legacy_fund_only` state, `unknown` promotion_state, `fixture_promotion_legacy_fund_only` blocker | YES |
| Exact missing + no legacy | state=`unknown`, blocker=`fixture_promotion_unknown` | Lines 1999-2013: returns `unknown` state and `fixture_promotion_unknown` blocker | YES |

All five rows match accepted contract exactly.

### 2.8 No `DEFAULT_REPORT_YEAR` Mapping

`_derive_fixture_promotion_state()` uses `artifact.report_year` directly in the lookup key, never falls back to `DEFAULT_REPORT_YEAR` for legacy state promotion. Confirmed.

## 3. Non-interference Check

### 3.1 Strict Golden Coverage

`_derive_strict_golden_coverage()` is unchanged (confirmed by diff — no modification to that function). The evidence artifact also states it was not changed.

### 3.2 Golden Answer / Fixture Content / Source Policy

No edits to golden answer files, fixture files, or source policy modules.

### 3.3 Readiness/Release State

Release/readiness remains `NOT_READY`. No readiness/release commands were run.

## 4. Test Quality

### 4.1 Value-level Assertions

All six new tests use value-level assertions:

- `test_preflight_accepts_year_aware_fixture_promotion_matching_year`: asserts `fixture_promotion_state == "promoted_fixture"`, `promotion_state == "promoted_fixture"`, and absence of all three fixture promotion blocker codes.
- `test_preflight_rejects_fixture_promotion_wrong_year`: asserts `fixture_promotion_state == "unknown"`, `promotion_state == "unknown"`, and presence of `fixture_promotion_unknown` blocker.
- `test_preflight_blocks_legacy_fund_code_only_fixture_promotion`: asserts `fixture_promotion_state == "legacy_fund_only"`, `promotion_state == "unknown"`, and presence of `fixture_promotion_legacy_fund_only` blocker.
- `test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry`: asserts `pytest.raises(ValueError, match="duplicate identity")`.
- `test_preflight_rejects_year_aware_fixture_promotion_unknown_field`: asserts `pytest.raises(ValueError, match="未知字段")`.
- `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity`: asserts `pytest.raises(ValueError, match="promotion_identity")`.

All assertions check concrete values, not file-existence or string-presence heuristics.

### 4.2 Coverage Matrix

| Scenario | Test | Value-level? |
|---|---|---|
| Matching year | `test_preflight_accepts_year_aware_fixture_promotion_matching_year` | YES |
| Wrong year | `test_preflight_rejects_fixture_promotion_wrong_year` | YES |
| Legacy fund-code-only | `test_preflight_blocks_legacy_fund_code_only_fixture_promotion` | YES |
| Duplicate identity | `test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry` | YES |
| Unknown field | `test_preflight_rejects_year_aware_fixture_promotion_unknown_field` | YES |
| Wrong identity | `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity` | YES |

All six required scenarios from the review checklist are covered.

### 4.3 Validation

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
# 22 passed in 0.79s

uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py
# All checks passed!
```

Both pass. Independent verification confirms evidence artifact claims.

## 5. README Update Assessment

### `fund_agent/fund/README.md`

Added one sentence documenting year-aware promotion identity and legacy fail-closed behavior. Accurately reflects implementation. No over-claim.

### `tests/README.md`

Updated test description to include new year-aware fixture promotion test scenarios. Added value-level assertion testing convention. Accurately reflects implementation.

## 6. Finding Table

| Finding | Severity | Evidence | Recommendation |
|---|---|---|---|
| Implementation matches accepted contract exactly across all 8 contract items | info | Diff analysis vs controller judgment §4 | No action needed |
| All 6 required test scenarios covered with value-level assertions | info | Test file analysis | No action needed |
| `_load_fixture_promotion_states()` return type changed from `dict[str, PromotionState] | None` to `FixturePromotionStates | None` | info | Diff line 1233; all internal callers updated | No action needed; this is an internal function, not a public API |
| Legacy `entries` format still accepted as diagnostic-only input | info | Lines 1256-1270; test `test_preflight_blocks_legacy_fund_code_only_fixture_promotion` | Confirmed fail-closed |
| `FixturePromotionStates` dataclass has clear `fund_year_states` / `legacy_fund_states` separation | info | Lines 62-71 | Clean design; supports future tracked manifest |

## 7. Accepted Items

| Item | Disposition |
|---|---|
| Exact `(fund_code, report_year)` promotion identity | ACCEPT |
| Required `promotion_identity == "fund_year"` validation | ACCEPT |
| Duplicate identity fail-closed | ACCEPT |
| Unknown field fail-closed | ACCEPT |
| Wrong identity fail-closed | ACCEPT |
| Legacy fund-code-only diagnostic-only | ACCEPT |
| State/blocker mapping for all five conditions | ACCEPT |
| No `DEFAULT_REPORT_YEAR` mapping from legacy to year-aware proof | ACCEPT |
| Strict golden coverage unchanged | ACCEPT |
| Release/readiness remains `NOT_READY` | ACCEPT |

## 8. Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Fixture promotion content write | REJECT | Out of scope for this gate |
| Golden-answer content edits | REJECT | Out of scope |
| Readiness/release/PR claim | DEFER | Release/readiness remains `NOT_READY` |

## 9. Residuals

| Residual | Owner |
|---|---|
| No fixture promotion content was created or promoted | Golden/readiness owner |
| No readiness/release command was run | Release owner |
| `FixturePromotionStates` is currently internal; if a future gate exposes it as public API, a new contract gate is required | Fund API owner |

## 10. Next Step

Recommended next entry:

```text
Fixture Promotion State Year-aware Schema / Parser Implementation Controller Judgment
```
