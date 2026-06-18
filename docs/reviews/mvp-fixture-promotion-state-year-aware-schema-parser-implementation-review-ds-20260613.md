# DS Implementation Review: Fixture Promotion State Year-aware Schema / Parser

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Implementation Gate`

Role: AgentDS — implementation review worker

Reviewed artifacts:

- 4-file uncommitted diff: `golden_readiness_preflight.py`, `test_golden_readiness_preflight.py`, `fund_agent/fund/README.md`, `tests/README.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-evidence-20260613.md`
- Accepted contract: `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-controller-judgment-20260613.md` §4

Verdict: **PASS**

## 1. Contract Compliance

| Contract item (§4) | Implementation check | Verdict |
|---|---|---|
| Schema version `fund-agent.fixture-promotion-state.year-aware.v1` | `FIXTURE_PROMOTION_STATE_SCHEMA_VERSION` constant, used as gate in `_load_fixture_promotion_states()` | `PASS` |
| Exact identity `(fund_code, report_year)` | `FixturePromotionStates.fund_year_states: Mapping[tuple[str, int], PromotionState]` | `PASS` |
| `promotion_identity == "fund_year"` required, fail-closed wrong identity | `if promotion_identity != "fund_year": raise ValueError(...)` at L1342-1343 | `PASS` |
| Duplicate `(fund_code, report_year)` raises `ValueError` | `if key in states: raise ValueError(... duplicate identity ...)` at L1349-1352 | `PASS` |
| Unknown top-level fields raise `ValueError` | `_reject_unknown_keys(payload, {"schema_version", "accepted_as_of", "source_artifacts", "entries"}, ...)` at L1299-1303 | `PASS` |
| Unknown entry fields raise `ValueError` | `_reject_unknown_keys(entry, {"fund_code", "report_year", "promotion_state", "promotion_identity", "evidence_artifacts"}, ...)` at L1320-1329 | `PASS` |
| Legacy fund-code-only diagnostic-only, cannot satisfy year-specific proof | Legacy formats (`{fund_code: state}` dict and `entries` list without `report_year`) routed to `legacy_fund_states`; `_derive_fixture_promotion_state()` checks `fund_year_states` first, then `legacy_fund_states` only as fallback → `fixture_promotion_legacy_fund_only` blocker | `PASS` |
| No `DEFAULT_REPORT_YEAR` for legacy→year-aware promotion | `DEFAULT_REPORT_YEAR` is never referenced in `_load_fixture_promotion_states()`, `_load_year_aware_fixture_promotion_states()`, or `_derive_fixture_promotion_state()` | `PASS` |

### State/Blocker Mapping Verification

| Condition | Expected `state` | Expected `promotion_state` | Expected blocker | Code match |
|---|---|---|---|---|
| Exact key `promoted_fixture` | `promoted_fixture` | `promoted_fixture` | none | L1947-1948: returns `_PromotionStateSummary("promoted_fixture", "promoted_fixture")` — no blockers tuple | `PASS` |
| Exact key `not_promoted` | `not_promoted` | `not_promoted` | `fixture_promotion_absent` | L1949-1963: returns `("not_promoted", "not_promoted")` with `fixture_promotion_absent` blocker | `PASS` |
| Exact key `unknown` | `unknown` | `unknown` | `fixture_promotion_unknown` | L1965-1980: returns `("unknown", "unknown")` with `fixture_promotion_unknown` blocker | `PASS` |
| Exact key missing, legacy exists | `legacy_fund_only` | `unknown` | `fixture_promotion_legacy_fund_only` | L1981-1998: returns `("legacy_fund_only", "unknown")` with `fixture_promotion_legacy_fund_only` blocker | `PASS` |
| Exact key missing, no legacy | `unknown` | `unknown` | `fixture_promotion_unknown` | L1999-2013: returns `("unknown", "unknown")` with `fixture_promotion_unknown` blocker | `PASS` |

## 2. Scope Boundary Check

| Boundary | Check | Verdict |
|---|---|---|
| Strict golden coverage unchanged | `_derive_strict_golden_coverage()` not in diff | `PASS` |
| Golden answer content unchanged | No golden answer file in diff | `PASS` |
| Fixture content unchanged | No fixture file created or edited | `PASS` |
| Source policy unchanged | No source/provider/fallback code changed | `PASS` |
| Release/readiness unclaimed | Evidence §6: `NOT_READY` | `PASS` |
| No live/network/PDF/FDR/provider/LLM commands | Evidence §1: explicitly scoped out | `PASS` |
| Diff within accepted write set | Only 4 files: `golden_readiness_preflight.py`, `test_golden_readiness_preflight.py`, `fund_agent/fund/README.md`, `tests/README.md` | `PASS` |
| Caller check: `_load_fixture_promotion_states()` return type change | Private function (`_` prefix), only caller is `run_golden_readiness_preflight()` at L591; no external import or call site observed | `PASS` |

## 3. Test Quality

### New Tests (6 added)

| Test | Coverage target | Assertion type | Verdict |
|---|---|---|---|
| `test_preflight_accepts_year_aware_fixture_promotion_matching_year` | `(004393, 2025)` matches → promoted | Value-level: `fixture_promotion_state`, `promotion_state`, absence of specific blocker codes | `PASS` |
| `test_preflight_rejects_fixture_promotion_wrong_year` | `(004393, 2024)` promoted but artifact year=2025 → blocked | Value-level: `state="unknown"`, `promotion_state="unknown"`, `fixture_promotion_unknown` blocker present | `PASS` |
| `test_preflight_blocks_legacy_fund_code_only_fixture_promotion` | legacy `{"004393": "promoted_fixture"}` → fail-closed | Value-level: `state="legacy_fund_only"`, `promotion_state="unknown"`, `fixture_promotion_legacy_fund_only` blocker present | `PASS` |
| `test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry` | Duplicate `(004393, 2025)` → `ValueError` | Exception type + message match: `pytest.raises(ValueError, match="duplicate identity")` | `PASS` |
| `test_preflight_rejects_year_aware_fixture_promotion_unknown_field` | Entry with `extra_payload` → `ValueError` | Exception type + message match: `pytest.raises(ValueError, match="未知字段")` | `PASS` |
| `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity` | `promotion_identity="fund_code_only"` → `ValueError` | Exception type + message match: `pytest.raises(ValueError, match="promotion_identity")` | `PASS` |

### Existing Test Regression

All 16 existing tests continue to pass. Key regression-sensitive tests:

- `test_preflight_blocks_fixture_promotion_absence`: unchanged behavior (no manifest → `fixture_promotion_absent`)
- `test_preflight_blocks_strict_golden_absence_and_fund_miss`: unchanged (`_derive_strict_golden_coverage()` untouched)
- `test_preflight_marks_006597_bond_blocker_resolved_not_blocker`: unchanged

### Test Helper Changes

`_run_single_artifact()`: added `fixture_promotion_state_path` parameter with default `None`. Existing callers not providing this parameter get `None` → identical behavior to prior hardcoded `None`. No regression risk.

### Legacy `promoted_fixture` Can't Prove `004393 / 2025`

Confirmed by `test_preflight_blocks_legacy_fund_code_only_fixture_promotion`: a legacy `{"004393": "promoted_fixture"}` manifest with `report_year=2025` artifact produces `fixture_promotion_state="legacy_fund_only"`, `promotion_state="unknown"`, and `fixture_promotion_legacy_fund_only` blocker. Legacy promotion cannot satisfy `004393 / 2025`-specific proof.

## 4. README Accuracy

| README | Change | Accuracy |
|---|---|---|
| `fund_agent/fund/README.md` L295 | Added: year-aware `(fund_code, report_year)` identity, legacy diagnostic-only, `fixture_promotion_legacy_fund_only` blocker | Matches implementation |
| `tests/README.md` L30 | Updated test description to include new coverage categories: year-aware matching-year pass, wrong-year block, legacy fail-closed, duplicate/unknown-field rejection | Matches implementation |
| `tests/README.md` L214 | Added testing convention: value-level `(fund_code, report_year)` identity assertions, legacy fail-closed blocker rule | Matches implementation |

No stale terminology or dual口径 observed.

## 5. Validation Credibility

| Command | Reported output | Credibility |
|---|---|---|
| `uv run pytest tests/fund/test_golden_readiness_preflight.py -q` | 22 passed in 0.90s | Plausible: 16 existing + 6 new = 22 tests | `PASS` |
| `uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py` | All checks passed! | Consistent with diff scope | `PASS` |
| `git diff --check` | no output | No whitespace errors | `PASS` |

Test count arithmetic (16 + 6 = 22) is internally consistent. Command outputs are consistent with the diff scope — only parser/schema, derivation, tests, and README changed; no structural or import changes that would cascade.

## 6. Findings

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| F1 | Legacy `entries` format (without `report_year`) does not validate unknown entry fields | `info` | `_load_fixture_promotion_states()` L1256-1270: reads `fund_code`/`promotion_state` from legacy entries but does not call `_reject_unknown_keys`. Pre-existing behavior; not introduced by this diff. | Accept as-is. Legacy is diagnostic-only; strict validation is only required for year-aware schema. If legacy format evolves, add `_reject_unknown_keys` in a separate gate. |
| F2 | `_run_single_artifact` test helper's new `fixture_promotion_state_path` parameter is not exercised by existing tests | `info` | All 16 existing tests call `_run_single_artifact` without the new parameter → defaults to `None` → identical to prior hardcoded `None`. | Accept as-is. The default-`None` design preserves backward compatibility. No action needed. |

## 7. Accepted / Rejected / Deferred

| Item | Disposition |
|---|---|
| Year-aware parser/schema implementation | `ACCEPT` — fully compliant with contract §4 |
| `FixturePromotionStates` dataclass with `fund_year_states` + `legacy_fund_states` | `ACCEPT` |
| `_load_year_aware_fixture_promotion_states()` with fail-closed validation | `ACCEPT` |
| `_derive_fixture_promotion_state()` year-aware first, legacy fallback | `ACCEPT` |
| 6 new value-level tests covering matching/wrong year, legacy, duplicate, unknown field, wrong identity | `ACCEPT` |
| README updates reflecting year-aware identity and legacy fail-closed | `ACCEPT` |
| Legacy `promoted_fixture` not serving as `004393 / 2025`-specific proof | `ACCEPT` |
| Strict golden coverage, golden answer, fixture content, source policy unchanged | `ACCEPT_CONFIRMED` |
| Release/readiness remains `NOT_READY` | `ACCEPT_CONFIRMED` |
| Fixture promotion content creation/write | `DEFER` — out of scope for this parser/schema gate |
| Readiness/release/PR claim | `DEFER` — requires separate authorization |

## 8. Residuals

| Residual | Owner | Destination |
|---|---|---|
| No fixture promotion content was created | Golden/readiness owner | Future fixture promotion/content gate |
| `DEFAULT_REPORT_YEAR` still used in `_entry()` (static manifest) and `_load_strict_golden_coverage()` (golden answer fallback) — separate from fixture promotion | Respective owners | Out of scope for this gate |
| Legacy `entries` format unknown-field validation gap | Future schema gate owner | Address only if legacy format evolves |

## 9. Verdict Justification

`PASS`: The implementation strictly follows every element of the accepted contract in controller judgment §4. All six new tests are value-level assertions covering the required failure modes. No regression in 16 existing tests. Diff stays within the accepted 4-file write set. No accidental modification to strict golden coverage, golden answer content, fixture content, source policy, or readiness/release state. Validation outputs (22/22 pytest, ruff clean, diff whitespace clean) are internally consistent and credible.
