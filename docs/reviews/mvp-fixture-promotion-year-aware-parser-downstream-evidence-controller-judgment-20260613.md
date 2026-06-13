# Fixture Promotion Year-aware Parser Downstream Evidence Controller Judgment

Date: 2026-06-13

Gate: `Fixture Promotion Year-aware Parser Downstream Evidence Gate`

Controller verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## Controller Scope

This judgment accepts only the downstream, non-live evidence for year-aware
fixture promotion consumption. It does not accept fixture promotion content,
does not create an accepted fixture promotion state manifest, does not modify
golden-answer content, does not change source/tests/runtime behavior, does not
run live/provider/LLM/analyze/checklist/readiness/release/PR commands and does
not change release/readiness state.

Release/readiness remains `NOT_READY`.

## Inputs Reviewed

- Rule truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Accepted implementation judgment:
  `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md`
- Evidence:
  `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-20260613.md`
- DS review:
  `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-review-ds-20260613.md`
- MiMo review:
  `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-review-mimo-20260613.md`

## Validation Considered

Evidence artifact validation:

- `git status --branch --short`
- `git diff --name-only`
- `git diff --check`
- Temporary local Python API run calling
  `fund_agent.fund.golden_readiness_preflight.run_golden_readiness_preflight()`
- `uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion -q`

Review validation:

- DS review reports `git diff --check` passed and targeted pytest result
  `3 passed in 0.68s`.
- MiMo review reports `git diff --check` passed and targeted pytest result
  `3 passed in 0.67s`.

## Accepted Facts

| Fact | Disposition | Basis |
|---|---|---|
| Downstream preflight rows consume exact year-aware fixture promotion state. | ACCEPT | Evidence API run, targeted pytest, DS review and MiMo review. |
| Exact `004393 / 2025` year-aware promotion can produce `fixture_promotion_state=promoted_fixture`, `promotion_state=promoted_fixture` and no fixture promotion blocker in the local downstream row. | ACCEPT | Evidence case `matching_year_promoted` and targeted test `test_preflight_accepts_year_aware_fixture_promotion_matching_year`. |
| A year-aware `004393 / 2024` promotion entry cannot satisfy a `004393 / 2025` row. | ACCEPT | Evidence case `wrong_year_promoted` and targeted test `test_preflight_rejects_fixture_promotion_wrong_year`. |
| Legacy fund-code-only promotion state cannot prove `004393 / 2025` promotion. | ACCEPT | Evidence case `legacy_fund_only_promoted` and targeted test `test_preflight_blocks_legacy_fund_code_only_fixture_promotion`. |
| This gate proves release/readiness. | REJECT | Gate scope is downstream evidence only; no readiness/release command or content promotion occurred. |
| This gate creates accepted fixture promotion content or manifest. | REJECT | Evidence and both reviews explicitly state no fixture promotion content/manifest was created. |

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS-role review | `PASS_WITH_RESIDUALS` | ACCEPT. Residuals are non-blocking for this evidence gate and remain blockers for promotion/readiness claims. |
| MiMo-role review | `PASS_WITH_RESIDUALS` | ACCEPT. Low auditability note about elided inline API script is accepted as non-blocking because targeted tests and code-level review independently cover the same semantics. |

## Residuals

| Residual | Owner | Next handling | Blocks |
|---|---|---|---|
| No accepted fixture promotion state manifest/content exists from this gate. | Fixture promotion owner / controller | Decide in `Fixture Promotion Content / Promotion-state Manifest Planning Gate`. | Fixture-promotion-content claim and any readiness claim that depends on accepted promotion content. |
| Release/readiness remains unproven. | Release owner / controller | Future release-readiness rollup only after accepted content/promotion decisions. | Release/readiness claim. |
| Existing untracked residue remains outside this gate. | Controller / artifact owners | Artifact-specific disposition gates only; no cleanup here. | Cleanliness/readiness claim, not this evidence acceptance. |
| Future evidence artifacts should include complete local scripts or rely on named tests instead of elided snippets. | Controller / future evidence workers | Process-quality note for future evidence gates. | Non-blocking for this gate. |

## Controller Decision

The evidence gate is accepted with residuals. The accepted downstream fact is
limited to row-level consumption and fail-closed routing:

- exact `(fund_code, report_year)` is required for year-aware fixture promotion
  proof;
- wrong-year entries do not cross-apply;
- legacy fund-code-only state is diagnostic-only and routes to
  `fixture_promotion_legacy_fund_only`;
- release/readiness remains `NOT_READY`.

## Next Entry

Recommended next mainline entry:

`Fixture Promotion Content / Promotion-state Manifest Planning Gate`

Purpose: decide whether the project should create a reviewed, year-aware fixture
promotion manifest/content path for `004393 / 2025`, or explicitly defer that
work and route the remaining blocker to release/readiness residual handling.

Deferred entries:

- fixture promotion content implementation, unless the planning gate accepts it;
- readiness/release rollup;
- live/provider/LLM/analyze/checklist/readiness/release/PR actions;
- artifact cleanup/archive/ignore disposition.
