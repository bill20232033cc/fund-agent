# MVP Small Golden Set Row-field Extractor Correctness Test Gate Implementation Evidence

## Gate

- Gate: `row-field extractor correctness test gate after accepted retained excerpts`
- Role: implementation worker
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Date: 2026-06-09

## Source Of Truth

- Execution rules: `AGENTS.md`
- Control packet: `docs/current-startup-packet.md`
- Control truth: `docs/implementation-control.md`
- Design truth: `docs/design.md`
- Accepted oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

## Scope Boundary

- Changed:
  - `tests/fund/test_small_golden_set_extractor_correctness.py`
  - `tests/README.md`
  - `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-implementation-evidence-20260609.md`
- Not changed:
  - No extractor code.
  - No accepted retained excerpt JSON.
  - No synthetic fixture projection.
  - No provider/default/runtime/budget/config.
  - No startup packet or implementation-control update.
  - No stage, commit, push or PR.

## Implementation

- Added retained-excerpt row-field correctness tests that load only `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` as the correctness oracle.
- Added oracle boundary assertions:
  - exactly five accepted rows: `004393`, `004194`, `006597`, `110020`, `017641`;
  - year is `2024` and document kind is `annual_report`;
  - each row contains exactly the accepted field groups;
  - each field group contains non-empty `expected`, `anchor` and short `excerpt`;
  - access boundary records no network, FDR live acquisition, fallback, extractor modification, fixture projection, exact/numeric acceptance or golden/readiness promotion;
  - retention boundary records no full PDF and no full page text retained.
- Added explicit exclusion test for `tests/fixtures/fund/small_golden_set/**/expected_fields.json`: all rows remain `fixture_source_kind=synthetic`, `source_identity.status=unmatched_synthetic`, `exact_numeric_correctness_allowed=false`, `promotion_allowed=false` and `fallback_invocation=prohibited`.
- Added passing row-field assertions for current extractor-consumable fields using minimal `ParsedAnnualReport` / `ParsedTable` objects built only from accepted oracle fields:
  - profile extractor: `fund_code`, `fund_name`, `fund_scale` from `target_share_units` / `total_share_units` when present, `benchmark_text`, `management_fee`, `custody_fee`;
  - performance extractor: one-year target-share NAV growth and one-year benchmark return for all five rows;
  - performance extractor: `110020` annual tracking error when present.
- Added strict xfail records for same-source fields that exist in the oracle but do not yet have a current row-field consumer in this test shape: `manager`, `holdings`, `risk`.
- Updated `tests/README.md` with the new test entry and retained-excerpt correctness boundary.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `13 passed, 3 xfailed in 0.76s`.

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `34 passed, 3 xfailed in 0.54s`.

```bash
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
```

Result: `All checks passed!`.

## Same-source Failing / Blocked Extractor Gaps

- `manager`: accepted oracle has manager expected values, anchor and excerpt, but current row-field correctness test does not have a direct extractor consumer shape for fund manager rows.
- `holdings`: accepted oracle has holdings expected values, anchor and excerpt, but current holdings extractor support is table-shape specific and does not cover all accepted row variants in this gate without a later extractor fix/design gate.
- `risk`: accepted oracle has risk expected text, anchor and excerpt, but current extractor does not expose a dedicated row-field risk output for exact correctness.

These gaps are recorded as `pytest.mark.xfail(strict=True)` in `tests/fund/test_small_golden_set_extractor_correctness.py`. They are same-source blocked evidence, not extractor fixes.

## Residual Risks

- Current passing tests prove correctness only for fields the current extractor can directly consume from the accepted retained excerpt oracle: identity, share-unit scale when present, benchmark, management/custody fee, one-year return fields and the accepted 110020 tracking-error field.
- The test builds minimal parsed report/table objects from oracle fields; it does not prove production PDF parser table-shape fidelity. That remains outside this gate because PDF access and FDR/live acquisition are explicitly unauthorized.
- Manager, holdings and risk require a later extractor fix or row-shape design gate before they can become default passing correctness assertions.

## Self-check

- Current role remains implementation worker, not controller.
- Touched files are limited to the allowed files for this gate.
- No extractor, accepted JSON, PDF, FDR, network, fallback, provider/config, promotion, staging, commit, push or PR action was performed.
- Artifact, validation and residual risks are recorded here; stop condition is satisfied after final diff check.
