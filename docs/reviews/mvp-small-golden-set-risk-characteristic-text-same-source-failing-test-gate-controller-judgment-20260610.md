# Controller Judgment: risk_characteristic_text.v1 same-source failing test gate plan

## Decision

`AUTHORIZED_WITH_BOUNDARIES`.

The plan is accepted for local implementation. This is a test-only `standard` gate.

## Accepted Inputs

- Plan: `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-141151.md`
- Current startup packet: `docs/current-startup-packet.md`
- Control truth: `docs/implementation-control.md`
- Accepted oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

## Controller Rationale

The next-entry condition is satisfied: `risk_characteristic_text.v1` is an accepted future row-shape contract and still lacks a dedicated same-source failing test. The existing generic `risk` unsupported-field xfail does not specify the future output surface and could allow an implementation to conflate risk-characteristic text with `product_profile.style_positioning`.

The accepted plan fixes that by requiring a named strict xfail over all five accepted rows and by asserting a dedicated `profile.risk_characteristic_text` output shape. The test is expected to fail today because current production code does not expose that field.

## Boundaries

Allowed files before implementation checkpoint:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-*.md`

Forbidden in this gate:

- production extractor changes;
- `ProfileExtractionResult` schema changes;
- using `style_positioning` as passing risk evidence;
- bundle/snapshot/renderer/quality gate/report/chapter/checklist/Service/Host integration;
- PDF, `FundDocumentRepository`, cache/source helper, fallback, network, provider/live LLM, fixture projection, golden/readiness promotion or runtime/config/source behavior changes.

## Required Validation

Implementation must run:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-plan-20260610.md docs/reviews/plan-review-20260610-141151.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-controller-judgment-20260610.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-implementation-evidence-20260610.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-code-review-20260610-*.md
```

Expected focused result: `21 passed, 3 xfailed`; the new risk test must remain xfailed and must not XPASS.

## Step Self-Check

- Current gate / role: controller accepting plan for same-source risk failing-test gate.
- Source of truth: live startup/control docs, accepted retained oracle, plan and plan review.
- Scope boundary: tests/docs only; unrelated untracked files remain out of scope.
- Stop conditions: any production code change, XPASS, network/source/provider/fallback requirement or validation failure blocks implementation acceptance.
- Evidence and validation: implementation evidence plus code review required before accepted implementation checkpoint.
- Next action: create accepted plan commit, then implement the authorized test-only slice.
