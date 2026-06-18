# MVP Small Golden Set / Extractor Correctness Slice C Option 2 Implementation Evidence

## Scope

Role: implementation/evidence worker only.

Gate: `small golden set extractor correctness implementation gate`, Slice C Option 2 parser/fixture mechanics mini-slice.

This mini-slice is offline only. It validates local fixture parsing, metadata normalization, explicit unsupported/unavailable/deferred status propagation and fail-closed boundaries for the five synthetic small golden rows. It does not claim source truth, annual-report correctness, exact/numeric extractor correctness, matched identity, golden/readiness promotion or quality gate acceptance.

## Changed Files

- `tests/fund/test_small_golden_set_parser_mechanics.py`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md`

No production code, fixture JSON, extractor, provider/runtime/config, reports/golden, control doc, design doc, startup packet, README or quality gate file was changed.

## Mechanics Covered

- Fixture row boundary:
  - exact five directories are required: `004393_2024`, `110020_2024`, `004194_2024`, `006597_2024`, `017641_2024`.
  - every parsed row must use `report_year=2024`.
- Fail-closed metadata:
  - `promotion_allowed=false`
  - `fallback_invocation=prohibited`
  - `fixture_source_kind=synthetic`
  - `source_identity.status=unmatched_synthetic`
  - `source_identity.matched_source_document=false`
  - `source_identity.fallback_used=false`
  - `exact_numeric_correctness_allowed=false`
- Assertion boundary:
  - no field group may use `exact`, `normalized_text` or `numeric_percent`.
  - all current field groups remain `assertion_kind=availability_status`.
- Slice A status preservation:
  - each fixture field status is checked against the Slice A manifest status.
  - `017641 holdings=unavailable` is preserved.
  - `017641 risk=deferred_policy` is preserved.
- Parser mechanics helper behavior:
  - synthetic/unmatched fields with manifest status `expected` degrade to explicit `parser_status=unavailable` with reason `unsupported_unmatched_synthetic_fixture`.
  - fixture `unavailable` propagates as `parser_status=unavailable`.
  - fixture `deferred_policy` propagates as `parser_status=deferred_policy`.
  - helper output is forbidden from using silent success statuses such as `expected`, `success` or `matched`.
- Import boundary:
  - the new test file imports only standard library modules and reads only local review/fixture JSON files.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py -q
```

Result:

```text
.....................                                                    [100%]
21 passed in 0.04s
```

```bash
uv run ruff check tests/fund/test_small_golden_set_parser_mechanics.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- tests/fund/test_small_golden_set_parser_mechanics.py docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md
```

Result: passed with no output.

## Residuals

- Exact/numeric extractor correctness remains blocked because all five rows are synthetic/unmatched and have no matched annual-report source identity.
- No row is eligible for promotion, readiness, quality gate scoring, source truth acceptance or extractor root-cause claims.
- Future extractor correctness work still requires a separate accepted plan with matched same-source fixture evidence.
