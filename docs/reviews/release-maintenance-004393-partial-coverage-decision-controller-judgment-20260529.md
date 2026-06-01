# 004393 Partial Coverage Decision — Controller Judgment

日期：2026-05-29

角色：Phaseflow / Gateflow controller。

## Verdict

**Accepted local validation.**

本 gate 接受 `004393 / 2024` partial strict correctness coverage 的 docs-only decision。当前 `004393` 不进入 minimum golden v1 promotion-prep；fixture state 保持 `absent`，`promotion_allowed=false`。本 gate 没有修改 production code、tests、runtime、reports、score、quality gate、snapshot、preflight、JSON manifests、golden answer、golden fixtures、README、PR、push、merge、release 或 promotion state。

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md` |
| Plan reviews | `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-review-mimo-20260529.md`; `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-review-glm-20260529.md` |
| Decision artifact | `docs/reviews/release-maintenance-004393-partial-coverage-decision-20260529.md` |
| Implementation evidence | `docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-evidence-20260529.md` |
| Implementation reviews | `docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-review-mimo-20260529.md`; `docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-review-glm-20260529.md` |

Accepted plan commit: `60be50f gateflow: accept plan for 004393 partial coverage decision`.

## Controller Decision

| Key | Decision |
|---|---|
| `decision` | `reject_partial_coverage_for_minimum_v1_promotion_prep` |
| `fund_code` / `report_year` | `004393 / 2024` |
| `minimum_v1_promotion_prep_ready` | `false` |
| `fixture_state_after_gate` | `absent` |
| `promotion_allowed` | `false` |
| P0 required before future minimum v1 promotion-prep | `manager_strategy_text.strategy_summary`; `manager_strategy_text.market_outlook` |
| P0 disposition | `needs_extractor_projection_gate` |
| P1 disposition | `defer_from_minimum_v1` for current minimum-v1 decision; remains full-v1 / future coverage residual |
| Missing cause | `snapshot_comparable_projection_gap` |
| Fact freeze required now | `false` |
| Next gate | `004194 P0 coverage or index_profile-only fixture decision gate` in the overnight route; 004393 follow-up owner is future `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate` |

The accepted evidence shows `004393` has score-wide strict correctness `total_records=150`, `comparable_records=9`, `matched_records=9`, `mismatched_records=0`, `unavailable_records=141`. Same-fund 004393 coverage is P0 `9/11` comparable and P1 `0/10` comparable. The nine matched rows are exposed P0 rows only: `basic_identity.*`, `benchmark.benchmark_name`, `classified_fund_type.fund_type`, and `nav_benchmark_performance.*`.

The two missing P0 rows are mandatory before future minimum v1 promotion-prep because `docs/design.md` §7.3 classifies `manager_strategy_text` as P0 and the golden rows already exist. Treating current partial coverage as promotion-prep-ready would assume correctness for reviewed fields that are not in the snapshot comparable contract.

The ten P1 rows are not accepted as ready. They are conservatively deferred from the minimum-v1 decision and remain owned by future full-v1 / coverage policy gates. `turnover_rate` remains a quality warning outside the current 004393 strict golden row set.

## Finding Judgments

| Review observation | Judgment | Reason |
|---|---|---|
| MiMo plan review PASS | accepted | Verified score counts, priority mapping, missing cause, P0 mandatory fields, P1 deferral, forbidden file boundaries, and validation matrix. |
| GLM plan review PASS | accepted | Independently verified the same field counts and conservative default with no findings. |
| MiMo implementation review PASS | accepted | Verified decision/evidence artifacts implement the accepted plan with no forbidden file changes. |
| GLM implementation review PASS | accepted | Independently verified decision encoding, field disposition, fact-freeze decision, next gate, and scope compliance. |

No accepted findings require fix or re-review.

## Validation

Controller verification:

```text
git diff --check -- docs/reviews/release-maintenance-004393-partial-coverage-decision-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-evidence-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-review-mimo-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-review-glm-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md docs/implementation-control.md
```

Result: passed, no output.

```text
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json
```

Result: passed, no output.

`ruff` / `pytest` are not required because this gate is docs-only and did not modify Python runtime, tests, reports, score policy, quality gate semantics, snapshot projection, golden answer, fixtures, manifests, CLI, renderer, Service/UI, Host/Agent/dayu, or preflight runtime consumption.

## Guardrails Preserved

- No golden promotion.
- No fixture promotion.
- No `promotion_allowed=true`.
- No golden answer / golden fixture modification.
- No score / quality gate / FQ0-FQ6 semantic change.
- No partial coverage treated as full readiness.
- No QDII probing, FOF taxonomy, `004194`, `006597`, `110020`, or `017641` scope work in this gate.
- No Host/Agent/dayu implementation.
- No PR, push, merge, release, or external-state mutation.

## Next Entry Point

Continue the overnight route with:

1. `004194 P0 coverage or index_profile-only fixture decision gate`.
2. `006597 same-fund unavailable field review` if existing untracked evidence is accepted, otherwise `006597 strict correctness rerun with reports/golden-answers/golden-answer.json`.
3. `minimum v1 promotion-prep readiness decision`.

The 004393-specific future implementation gate is `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate`; it is not authorized by this gate.
