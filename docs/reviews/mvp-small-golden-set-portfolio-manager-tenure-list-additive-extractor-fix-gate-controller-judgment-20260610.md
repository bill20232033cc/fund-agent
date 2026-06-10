# MVP Small Golden Set Portfolio Manager Tenure List Additive Extractor Fix Gate Controller Judgment

## Gate

- Gate: `portfolio_manager_tenure_list.v1 additive extractor fix gate`
- Classification: `standard`
- Date: 2026-06-10
- Role: controller judgment
- Status: accepted locally, pending checkpoint commit

## Inputs Reviewed

- Accepted plan checkpoint: `025d375`
- Plan: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-plan-20260610.md`
- Plan review: `docs/reviews/plan-review-20260610-131917.md`
- Plan re-review: `docs/reviews/plan-review-20260610-132022.md`
- Plan controller judgment: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-plan-controller-judgment-20260610.md`
- Implementation evidence: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-implementation-evidence-20260610.md`
- Code review: `docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-code-review-20260610-132540.md`

## Controller Verdict

Accepted.

The implementation satisfies the accepted additive extractor fix scope for `portfolio_manager_tenure_list.v1`. It makes the accepted same-source manager roster test pass while preserving source/fallback/provider/runtime/config/golden/readiness boundaries.

## Accepted Current Fact

`extract_manager_ownership()` now exposes `portfolio_managers` as `portfolio_manager_tenure_list.v1` when the parsed report has:

- a numbered `§4` heading containing both `基金经理` and `简介`;
- a manager roster table with semantic headers for name, role and start date.

The field returns ordered manager rows with row-level source anchors. This is current extractor surface only. It is not yet integrated into `StructuredFundDataBundle`, snapshot, renderer, quality gate, report evidence, chapter facts, checklist or Service.

## Review Finding Judgment

Code review verdict: PASS with zero blocking findings.

No fix/re-review loop is required.

## Validation Accepted

| Command | Accepted Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_manager_ownership.py -q` | `10 passed` |
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | `21 passed, 3 xfailed` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | `42 passed, 3 xfailed` |
| `uv run pytest tests/fund/extractors/test_manager_ownership.py tests/fund/test_data_extractor.py -q` | `20 passed` |
| `uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py` | `All checks passed!` |
| `git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md fund_agent/fund/README.md docs/reviews/mvp-small-golden-set-portfolio-manager-tenure-list-additive-extractor-fix-gate-implementation-evidence-20260610.md` | passed |

## Boundary Confirmation

- No PDF read.
- No repository/source/cache/fallback/network/live EID/FDR action.
- No provider, live LLM, runtime budget or config change.
- No small-golden fixture mutation or projection.
- No golden/readiness promotion.
- No source orchestration, parser model, score-loop, quality gate, renderer, chapter facts, evidence availability, report evidence, checklist or Service integration.
- No adjacent future contract work.

## Residual Risk

`ParsedTable` still has no parser-level section ownership metadata. The accepted current mitigation is the numbered `§4` manager-roster heading guard. Parser-level table section ownership remains future work.

## Next Entry

Recommended next entry is one of:

- same-source failing risk test gate for `risk_characteristic_text.v1`;
- same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1`;
- same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`;
- separate downstream integration planning for `portfolio_managers` into bundle/snapshot/report surfaces, if separately authorized.

Do not enter fixture projection, golden/readiness promotion, live source acquisition, fallback, provider/runtime/config changes, release, PR, merge or mark-ready without separate authorization.
