# Controller Judgment: bond_top_holding_row.v1 same-source failing test gate plan

## Decision

`AUTHORIZED_WITH_BOUNDARIES`.

The plan is accepted for local implementation. This is a test/docs-only `standard` gate.

## Accepted Inputs

- Plan: `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-152453.md`
- Current control sync checkpoint: `6aa2dea`
- Accepted retained oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

## Controller Rationale

Current control truth lists same-source failing `006597` bond holding test gate as the first valid next entry. The accepted row-shape decision requires a dedicated `bond_top_holding_row.v1` contract before any extractor fix and forbids using stock `top_holdings`, bond risk evidence, or fabricated rank values for the first test.

The plan satisfies that boundary by creating a named strict xfail using only retained oracle fields and a minimal `§8.6` parsed table.

## Boundaries

Allowed files before implementation checkpoint:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-*.md`

Forbidden in this gate:

- production extractor changes;
- downstream bundle/snapshot/report/quality/chapter/checklist/Service/Host/Agent runtime integration;
- PDF/FDR/cache/source helper/network/fallback/provider/live LLM;
- fixture projection, golden/readiness promotion, source/provider/runtime/config behavior changes;
- target ETF implementation or extractor fix work.

## Required Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-bond-top-holding-row-same-source-failing-test-gate-*.md docs/reviews/plan-review-20260610-152453.md
```

Expected small-golden family result: `43 passed, 2 xfailed`; the bond test must remain xfailed and must not XPASS.

## Step Self-Check

- Current gate / role: controller accepting plan for same-source bond holding failing-test gate.
- Source of truth: live startup/control/design docs, accepted retained oracle, plan, plan review.
- Scope boundary: tests/docs only; unrelated untracked residue remains out of scope.
- Stop conditions: any production extractor change, XPASS, target ETF weakening, or PDF/source/network/provider requirement blocks acceptance.
- Evidence and validation: implementation evidence and code review required before accepted implementation checkpoint.
- Next action: create accepted plan commit, then implement the authorized test-only slice.
