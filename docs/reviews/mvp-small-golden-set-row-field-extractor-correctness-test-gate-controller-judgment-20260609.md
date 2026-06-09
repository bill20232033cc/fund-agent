# MVP Small Golden Set Row-field Extractor Correctness Test Gate Controller Judgment

## Gate

- Gate: `row-field extractor correctness test gate after accepted retained excerpts`
- Classification: `standard`
- Date: 2026-06-09
- Controller: AgentController

## Judgment

Accepted locally.

The gate added retained-excerpt-driven row-field extractor correctness tests without changing extractor code, accepted oracle data, fixture projection, source acquisition, provider/runtime/config, fallback or golden/readiness promotion. The tests use `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` as the only correctness oracle and explicitly keep synthetic/unmatched fixtures out of correctness.

## Accepted Scope

- Test artifact: `tests/fund/test_small_golden_set_extractor_correctness.py`
- Test documentation update: `tests/README.md`
- Implementation evidence: `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-implementation-evidence-20260609.md`

The passing assertions cover current extractor-consumable same-source row fields:

- `identity`: `fund_code`, `fund_name`
- `scale`: `fund_scale` from `target_share_units` or `total_share_units`
- `benchmark`: `benchmark_text`
- `fee`: `management_fee`, `custody_fee`
- `return`: one-year target-share NAV growth and benchmark return
- `return`: `110020` annual tracking error when present

`manager`, `holdings` and `risk` remain same-source blocked gaps recorded as strict xfail markers. They are not accepted as passing extractor correctness and do not authorize extractor fixes by themselves.

## Review Judgment

- Chandrasekhar review: PASS / no blocking findings.
- Carver review: found one valid blocking issue: `scale` was incorrectly classified as an xfail gap despite current profile extractor support.
- Controller judgment on Carver finding: accepted.
- Targeted fix: `scale` was removed from `SAME_SOURCE_UNSUPPORTED_FIELDS`, `fund_scale` passing assertion was added, and implementation evidence was updated.
- Carver targeted re-review: finding fixed.
- Chandrasekhar final current-state re-review: PASS / no blocking findings.
- AgentDS final review artifact: `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-review-ds-20260609.md`, PASS / no blocking findings.
- AgentMiMo final review artifact: `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-review-mimo-20260609.md`, PASS / no blocking findings.

The DS/MiMo tmux panes initially retained stale `PR #22` UI residue after `/clear`; the user explicitly authorized DS/MiMo handoff despite that pane residue. Their final review artifacts are accepted as the current gate's independent review evidence.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `13 passed, 3 xfailed`.

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `34 passed, 3 xfailed`.

```bash
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
```

Result: `All checks passed!`.

```bash
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-implementation-evidence-20260609.md
```

Result: PASS.

## Boundary

No PDF read, network access, `FundDocumentRepository` live acquisition, fallback invocation, live LLM, endpoint/provider probe, provider/default/runtime/budget/config change, extractor modification, fixture projection, golden/readiness promotion, release, merge or PR state change occurred.

The untracked `docs/reviews/repo-review-20260609-130307.md` was produced as an unrelated side artifact and is not accepted by this gate.

## Next Entry Point

Open a `row-field extractor gap decision gate for retained manager / holdings / risk fields` or a separately authorized non-extractor phase.

The next extractor-facing gate must first decide whether to turn `manager`, `holdings` and `risk` into field-specific same-source failing extractor-path tests, adjust row-shape design, or defer them. Do not modify extractor code until a reviewed gate accepts the field-specific failing tests and root-cause boundary. Fixture projection, golden/readiness promotion, FDR/PDF/network acquisition, fallback, live LLM, provider/runtime/config changes, Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, release, merge and mark-ready remain unauthorized.
