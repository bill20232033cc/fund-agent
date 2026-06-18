# MVP Small Golden Set Portfolio Manager Tenure List Additive Extractor Fix Gate Plan Controller Judgment

## Gate

- Gate: `portfolio_manager_tenure_list.v1 additive extractor fix gate`
- Classification: `standard`
- Date: 2026-06-10
- Role: controller judgment
- Status: accepted locally, pending checkpoint commit

## Inputs Reviewed

- Plan: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-131917.md`
- Plan re-review: `docs/reviews/plan-review-20260610-132022.md`
- Current control truth: `docs/implementation-control.md`
- Current startup packet: `docs/current-startup-packet.md`
- Previous gate judgment: `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-controller-judgment-20260610.md`

## Controller Verdict

Accepted for implementation.

The plan is sufficiently scoped and code-generation-ready after re-review. It authorizes only an additive manager roster output surface for `extract_manager_ownership()` and its focused tests. It does not authorize downstream report/scoring/quality integration, source acquisition, fallback, provider/runtime/config changes, fixture projection, golden/readiness promotion, live commands, PR/release/merge/mark-ready, or adjacent future contracts.

## Review Finding Judgment

### F1: fabricated section anchors for tables without section metadata

- Review status: accepted as blocking in initial plan review.
- Plan fix: accepted.
- Re-review status: pass-with-risks.
- Judgment: resolved for this gate.

Reason: the plan now requires current-model direct extraction to fail closed unless `§4` text contains a manager-roster heading such as `4.1.2 基金经理简介` or an accepted equivalent containing both `基金经理` and `简介`. It also requires a negative unit test for a manager-shaped table without the `§4` manager-roster heading.

## Authorized Implementation Boundary

Allowed implementation files:

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- implementation/review artifacts under `docs/reviews/`

Optional only if needed and narrowly current-fact-only:

- `fund_agent/fund/README.md`

## Required Validation

Implementation must run:

```bash
uv run pytest tests/fund/extractors/test_manager_ownership.py -q
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md
```

Expected result:

- manager unit tests pass;
- small-golden extractor correctness reaches `21 passed, 3 xfailed`;
- small-golden family reaches `42 passed, 3 xfailed`;
- remaining xfails are only other not-yet-implemented future contracts.

## Stop Conditions

Implementation must stop if it needs to:

- read PDF, invoke repository/source/cache/fallback/network/live EID/FDR/provider/LLM;
- modify source orchestration, parser model, runtime budget, config, score-loop, quality gate, renderer, chapter facts, evidence availability, report evidence, checklist or Service;
- mutate small-golden fixtures or project fixture fields;
- relax accepted same-source assertions;
- hard-code fixture table indexes;
- emit direct `§4` anchors without section metadata or the `§4` manager-roster heading guard.

## Residual Risk

Parser-level table section ownership remains absent from `ParsedTable`. The accepted implementation mitigation is a local `§4` manager-roster heading guard. Parser-level section ownership is future work and is not authorized in this gate.

## Next Step

Proceed to implementation under the accepted plan.
