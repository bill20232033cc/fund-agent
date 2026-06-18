# Fixture Promotion State Year-aware Schema / Parser Implementation Evidence

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Implementation Gate`

Role: implementation evidence

Status: `IMPLEMENTATION_READY_FOR_REVIEW`

Accepted plan:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-controller-judgment-20260613.md`

## 1. Scope

Allowed implementation write set used:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- this implementation evidence artifact

This implementation did not edit golden-answer files, fixture files, promotion
state manifest content, `docs/design.md`, control docs, root README, pyproject
or `.gitignore`.

This implementation did not run live/network/PDF/FDR/provider/LLM/analyze/
checklist/readiness/release/PR commands.

Release/readiness remains `NOT_READY`.

## 2. Implementation Summary

### Parser / Schema

Implemented in `fund_agent/fund/golden_readiness_preflight.py`:

- added `FIXTURE_PROMOTION_STATE_SCHEMA_VERSION =
  "fund-agent.fixture-promotion-state.year-aware.v1"`;
- added `FixturePromotionStates` with explicit:
  - `fund_year_states: Mapping[tuple[str, int], PromotionState]`;
  - `legacy_fund_states: Mapping[str, PromotionState]`;
- changed `_load_fixture_promotion_states()` to return
  `FixturePromotionStates | None`;
- added `_load_year_aware_fixture_promotion_states()` for the accepted
  year-aware schema;
- year-aware schema rejects:
  - unknown top-level fields;
  - unknown entry fields;
  - missing or non-integer `report_year`;
  - invalid `promotion_state`;
  - `promotion_identity != "fund_year"`;
  - duplicate `(fund_code, report_year)` identities;
- legacy `entries` without `report_year` and legacy top-level
  `{fund_code: state}` mappings are still accepted, but only into
  `legacy_fund_states`.

### Row Derivation

Updated `_derive_fixture_promotion_state()`:

- non-digit rows remain `not_applicable`;
- no manifest or no parsed states still emits `fixture_promotion_absent`;
- exact `(artifact.fund_code, artifact.report_year)` lookup is checked before
  any legacy state;
- exact `promoted_fixture` returns promoted with no fixture blocker;
- exact `not_promoted` returns `fixture_promotion_absent`;
- exact `unknown` returns `fixture_promotion_unknown`;
- legacy fund-code-only state returns:
  - `fixture_promotion_state="legacy_fund_only"`;
  - `promotion_state="unknown"`;
  - blocker `fixture_promotion_legacy_fund_only`;
- missing exact year with no legacy state returns `fixture_promotion_unknown`;
- `_derive_strict_golden_coverage()` was not changed.

### Tests

Updated `tests/fund/test_golden_readiness_preflight.py` with value-level tests
for:

- matching-year year-aware promotion pass;
- wrong-year year-aware promotion block;
- legacy fund-code-only promotion fail-closed;
- duplicate `(fund_code, report_year)` rejection;
- unknown entry field rejection;
- wrong `promotion_identity` rejection.

### Docs

Updated:

- `fund_agent/fund/README.md` to document year-aware promotion identity and
  legacy fail-closed behavior;
- `tests/README.md` to document the new value-level readiness parser test
  coverage and testing convention.

## 3. Validation

Command:

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
```

Observed output:

```text
......................                                                   [100%]
22 passed in 0.90s
```

Disposition: `PASS`

Command:

```bash
uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py
```

Observed output:

```text
All checks passed!
```

Disposition: `PASS`

Command:

```bash
git diff --check
```

Observed output:

```text
<no output>
```

Disposition: `PASS`

## 4. Diff Scope

Command:

```bash
git diff --name-only
```

Observed output:

```text
fund_agent/fund/README.md
fund_agent/fund/golden_readiness_preflight.py
tests/README.md
tests/fund/test_golden_readiness_preflight.py
```

Disposition: `PASS_WITHIN_ACCEPTED_WRITE_SET`

## 5. Finding Table

| Finding | Disposition | Evidence |
|---|---|---|
| Fixture promotion parser is now capable of year-aware identity. | `IMPLEMENTED` | `FixturePromotionStates.fund_year_states`; `_load_year_aware_fixture_promotion_states()` |
| Legacy fund-code-only promotion no longer satisfies year-specific proof. | `IMPLEMENTED_FAIL_CLOSED` | `legacy_fund_states`; `fixture_promotion_legacy_fund_only` test |
| Wrong-year promotion does not pass as target-year proof. | `IMPLEMENTED_FAIL_CLOSED` | `test_preflight_rejects_fixture_promotion_wrong_year` |
| Duplicate fund/year identity fails closed. | `IMPLEMENTED_FAIL_CLOSED` | duplicate identity test |
| Unknown fields and wrong `promotion_identity` fail closed. | `IMPLEMENTED_FAIL_CLOSED` | unknown field and wrong identity tests |
| Strict golden coverage implementation was not changed. | `CONFIRMED` | diff scope; implementation contract |
| Release/readiness remains unclaimed. | `NOT_READY` | gate boundary |

## 6. Residuals

| Residual | Owner | Destination |
|---|---|---|
| No fixture promotion content was created or promoted. | Golden/readiness owner | Future fixture promotion/content gate only if authorized |
| No readiness/release command was run. | Release owner | Future readiness rollup after accepted review/controller judgment |
| Existing historical untracked residue remains outside this gate. | Artifact owners | Existing disposition routes |

## 7. Next Step

Recommended next step:

```text
Fixture Promotion State Year-aware Schema / Parser Implementation Review Gate
```

Required review:

- DS implementation review;
- MiMo implementation review;
- controller judgment.

Do not enter readiness/release/PR or fixture promotion from this evidence
artifact.
