# Controller Judgment: Fixture Promotion State Year-aware Schema / Parser Planning

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Planning Gate`

Plan:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-20260613.md`

Review inputs:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-review-ds-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-review-mimo-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-rereview-ds-20260613.md`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## 1. Controller Scope

This judgment accepts the amended plan for a narrow year-aware fixture
promotion schema/parser implementation gate.

This judgment does not implement code, does not promote fixtures, does not edit
golden-answer content, does not run readiness/release commands, and does not
claim release/readiness.

Release/readiness remains `NOT_READY`.

## 2. Accepted Plan Facts

| Fact | Disposition | Basis |
|---|---|---|
| The planning gate is docs-only and did not authorize implementation. | `ACCEPT` | Plan §2/§14; DS F1; MiMo F1 |
| Strict golden coverage is already year-aware for the current tracked JSON surface and needs no implementation in this work unit. | `ACCEPT` | Evidence checkpoint `aaf7922`; Plan §3/§4; DS F2; MiMo F2 |
| Fixture promotion remains fund-code-only and cannot prove `004393 / 2025`-specific promotion. | `ACCEPT` | Evidence checkpoint `aaf7922`; Plan §3/§4 |
| Implementation is required before any later gate may treat fixture promotion as year-specific proof. | `ACCEPT` | Plan §4; DS F2; MiMo F11 |
| Controller may still defer implementation only if downstream readiness explicitly excludes fixture promotion proof and preserves `NOT_READY`. | `ACCEPT_AS_DEFER_ROUTE` | Plan §4 |
| The implementation scope is limited to fixture promotion parser/schema, targeted tests and triggered READMEs. | `ACCEPT` | Plan §5/§8/§10; DS F7; MiMo F7/F9 |

## 3. Review Finding Disposition

| Finding | Source | Controller disposition | Follow-up |
|---|---|---|---|
| MiMo passed the plan with no amendments. | MiMo | `ACCEPT` | No action. |
| DS Amendment A: `promotion_identity` needs explicit disposition. | DS F3 | `ACCEPT_WITH_AMENDMENT_A1` | Keep `promotion_identity` as required, add rationale and wrong-identity test. Completed in amended plan; DS re-review PASS. |
| DS Amendment B: row derivation contract must specify output `state`, `promotion_state` and blocker. | DS F4 | `ACCEPT_WITH_AMENDMENT` | Completed in amended plan; DS re-review PASS. |
| DS Amendment C: type-reference changes must be enumerated. | DS F5 | `ACCEPT_WITH_AMENDMENT` | Completed in amended plan; DS re-review PASS. |
| Public contract risk is bounded but must be verified before implementation changes old parser return shape. | DS F10; MiMo F4/F12 | `ACCEPT_AS_IMPLEMENTATION_STOP_CONDITION` | Implementation worker must check for callers outside `run_golden_readiness_preflight()` before changing parser return type. |
| `DEFAULT_REPORT_YEAR` must not be used to promote legacy fund-code-only fixture state. | DS F11; MiMo F6 | `ACCEPT` | Keep exact `(fund_code, report_year)` lookup and legacy fail-closed behavior. |

## 4. Accepted Implementation Contract For Next Gate

The next implementation gate is allowed to implement only this contract:

- year-aware manifest schema version:
  `fund-agent.fixture-promotion-state.year-aware.v1`;
- exact promotion identity key: `(fund_code, report_year)`;
- required entry field `promotion_identity == "fund_year"` with fail-closed
  wrong-identity validation;
- duplicate `(fund_code, report_year)` entries raise `ValueError`;
- unknown top-level and entry fields raise `ValueError`;
- legacy fund-code-only manifests remain diagnostic-only and cannot satisfy
  year-specific promotion proof;
- exact year `promoted_fixture` can pass; exact year `not_promoted` or
  `unknown` blocks; legacy-only state blocks as
  `fixture_promotion_legacy_fund_only`;
- no `DEFAULT_REPORT_YEAR` mapping from legacy promotion state to year-aware
  proof.

Accepted state/blocker mapping for row derivation:

| Condition | `state` output | `promotion_state` output | Blocker |
|---|---|---|---|
| Exact key is `promoted_fixture` | `promoted_fixture` | `promoted_fixture` | none |
| Exact key is `not_promoted` | `not_promoted` | `not_promoted` | `fixture_promotion_absent` |
| Exact key is `unknown` | `unknown` | `unknown` | `fixture_promotion_unknown` |
| Exact key missing and legacy fund-code state exists | `legacy_fund_only` | `unknown` | `fixture_promotion_legacy_fund_only` |
| Exact key missing and no legacy state exists | `unknown` | `unknown` | `fixture_promotion_unknown` |

## 5. Accepted Next Gate

Recommended next mainline entry:

```text
Fixture Promotion State Year-aware Schema / Parser Implementation Gate
```

Allowed implementation write set:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `fund_agent/fund/README.md` only if triggered by the source change
- `tests/README.md` only if triggered by the test change
- implementation evidence artifact under `docs/reviews/`

Expected review artifacts after implementation:

- DS review under `docs/reviews/`
- MiMo review under `docs/reviews/`
- controller judgment under `docs/reviews/`

Validation commands for the implementation gate:

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py
```

Do not run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release
commands in the implementation gate.

## 6. Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Strict golden coverage implementation | `REJECT_AS_UNNEEDED_NOW` | Already accepted as year-aware for current tracked JSON surface. |
| Treating legacy fund-code-only `promoted_fixture` as year-specific proof | `REJECT` | Violates accepted identity contract. |
| Fixture promotion content write or promotion action | `REJECT` | Next gate is parser/schema implementation only. |
| Golden-answer content edits | `REJECT` | Out of scope. |
| Readiness/release/PR claim | `DEFER` | Release/readiness remains `NOT_READY`; external state requires separate authorization. |
| Defer route that excludes fixture promotion proof | `DEFER_AS_ALLOWED_ALTERNATIVE` | Available only if controller later decides not to implement promotion-state proof before readiness; this judgment recommends implementation. |

## 7. Accepted Checkpoint

This plan gate is accepted as a local checkpoint once these files are committed
together:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-review-ds-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-review-mimo-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-rereview-ds-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-controller-judgment-20260613.md`

Expected checkpoint message:

```text
gateflow: accept fixture promotion year-aware parser plan
```

## 8. Boundary Confirmation

This judgment did not perform or authorize:

- source, test or runtime behavior changes;
- golden-answer, fixture or promotion-state content edits;
- fixture promotion;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- cleanup, deletion, archive, push, merge or external-state actions.
