# Controller Judgment: risk_characteristic_text.v1 additive extractor fix gate plan

## Decision

`AUTHORIZED_WITH_BOUNDARIES`.

The plan is accepted for local implementation. This is a `heavy` gate because it adds a public Fund extractor output field.

## Accepted Inputs

- Plan: `docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-145801.md`
- Accepted failing-test implementation checkpoint: `4d01617`
- Current control sync checkpoint: `d1cd1ed`

## Controller Rationale

The current control truth lists `risk_characteristic_text.v1` additive extractor fix as the first valid next entry. The accepted same-source failing test proves a dedicated risk-characteristic surface is absent. The plan keeps the fix inside Fund profile extraction, requires explicit risk-characteristic labels, and forbids using `product_profile.style_positioning` as the acceptance surface.

## Boundaries

Allowed implementation files:

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-*.md`

Forbidden in this gate:

- downstream bundle/snapshot/report/quality/chapter/checklist/Service/Host/Agent runtime integration;
- FDR/PDF/cache/source helper/network/fallback/provider/live LLM;
- fixture projection, golden/readiness promotion, source/provider/runtime/config behavior changes;
- bond or target ETF row-shape work.

## Required Validation

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-*.md docs/reviews/plan-review-20260610-145801.md
```

Expected small-golden family result: `43 passed, 2 xfailed`.

## Step Self-Check

- Current gate / role: controller accepting plan for heavy additive risk extractor fix.
- Source of truth: live startup/control docs, accepted failing test, plan, plan review.
- Scope boundary: Fund profile extractor + focused tests/docs only; unrelated untracked residue remains out of scope.
- Stop conditions: any need for downstream integration, source/network/provider/fallback/golden/readiness work, or indirect `基金类型` risk parsing blocks acceptance.
- Evidence and validation: implementation evidence and code review required before accepted implementation checkpoint.
- Next action: create accepted plan commit, then implement the authorized slice.
