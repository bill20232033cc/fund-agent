# Minimum V1 Promotion-Prep Readiness Decision

日期：2026-05-29

角色：minimum v1 promotion-prep readiness decision gate planning / decision worker。

本文是 docs-only decision artifact。它不执行 promotion，不修改 `docs/implementation-control.md`、`docs/design.md`、golden answer、golden fixtures、reports、manifests、runtime code、tests、score、quality gate、preflight output、PR、push、merge 或 release state。

## Scope And Guardrails

Gate：`minimum v1 promotion-prep readiness decision gate`

Gate classification：`heavy`。原因：本裁决影响 minimum golden v1 readiness、fixture candidacy、promotion-prep route 和后续控制面入口；本次实际工作仅允许写入本 Markdown artifact。

本 gate 的问题是：在 Track 1 已接受的 `004393`、`004194`、`006597` fund-level controller judgments 之后，是否有任何基金可以进入 minimum v1 promotion-prep。

硬边界：

- 不做 golden promotion、fixture promotion 或 release readiness。
- 不设置 `promotion_allowed=true`。
- 不修改 golden-answer JSON、golden fixtures、residual manifest、fixture promotion state manifest、preflight output、snapshot、score、quality gate 或 runtime。
- 不改变 FQ0-FQ6、score policy、quality gate severity、final judgment 或 report semantics。
- 不进入 QDII、FOF、`110020`、Host/Agent/dayu、source generalization 或 unrelated fund work。
- 不 stage、commit、push、PR、merge、release、promote 或 delete files。

## Evidence Freeze

本裁决冻结到以下已接受证据：

| Evidence | Use |
|---|---|
| `AGENTS.md` | gate 分类、真源、禁止 promotion / release / GitHub mutation 和模块边界纪律 |
| `docs/design.md` §7.3 / §7.4 | P0/P1 字段优先级、strict correctness、quality gate 阻断语义 |
| `docs/implementation-control.md` Startup Packet | 当前 Track 1 accepted state 和 next entry point |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` | minimum golden v1 readiness route 仍 active；006597 bond blocker closed 但 strict correctness / fixture candidacy 未解决 |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | 004393 / 004194 / 006597 初始 promotion-prep 均未 accepted，全部 `fixture_state=absent`、`promotion_allowed=false` |
| `docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md` | 004393 partial coverage rejected for minimum v1 promotion-prep |
| `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md` | 004194 full fixture blocked；only bounded `index_profile` diagnostic candidate |
| `docs/reviews/release-maintenance-006597-strict-correctness-rerun-controller-judgment-20260529.md` | 006597 configured strict correctness rerun accepted blocked-with-reason |
| `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md` | historical preflight state remains BLOCK and non-promotion |
| `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | control-plane residual disposition only, `promotion_allowed=false` |
| `docs/reviews/fixture-promotion-state-manifest-20260529.json` | control-plane fixture state evidence only, all relevant Track 1 rows remain absent / false |

Preflight and the two manifests may lag the accepted 006597 rerun wording because the 006597 rerun gate intentionally did not mutate them. That lag is not repaired here; it is routed to a separate control-plane lifecycle gate if needed.

## Overall Decision

| Field | Decision |
|---|---|
| `overall_readiness` | `not_ready` |
| `decision` | `blocked_with_reason` |
| `minimum_v1_promotion_prep_ready` | `false` |
| `any_fund_can_enter_promotion_prep_now` | `false` |
| `fixture_state_change` | none |
| `promotion_allowed_change` | none |
| `preflight_manifest_update_now` | `false` |
| `promotion_allowed` | `false` for all Track 1 funds |

No Track 1 fund can enter promotion-prep now. The conservative default is required because each accepted fund-level judgment still has a blocking strict correctness, P0 coverage, or fixture candidacy gap.

## Per-Fund Candidate State

| Fund | Accepted state | Promotion-prep candidate now | Blocking reason | Fixture state | Promotion allowed |
|---|---|---:|---|---|---|
| `004393 / 2024` | `reject_partial_coverage_for_minimum_v1_promotion_prep` | no | P0 `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook` are missing from comparable snapshot coverage; same-fund P0 coverage is only `9/11`, P1 coverage `0/10`. | `absent` | `false` |
| `004194 / 2024` | `index_profile_only_candidate_not_full_fixture_ready` | no | P0 strict correctness coverage is `0`; exactly five matched `index_profile.*` rows validate only bounded benchmark-context diagnostics. | `absent` | `false` |
| `006597 / 2024` | `blocked_pending_same_fund_unavailable_field_review` | no | Configured strict correctness rerun has `9` matched, `0` mismatch, `11` same-fund unavailable; unavailable P0 rows include `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook`. | `absent` | `false` |

`004194` may still be referenced as a bounded diagnostic / specialized `index_profile` candidate, but that is not minimum v1 promotion-prep and not full fixture readiness.

## 006597 Bond Blocker Status

The `006597` bond risk evidence blocker remains closed as resolved context through the accepted NAV-derived drawdown metric route. That closure only resolves the prior bond-risk evidence issue.

It does not override strict correctness readiness. The accepted 006597 rerun is configured with `reports/golden-answers/golden-answer.json`, but it is blocked because same-fund unavailable rows remain. Therefore:

- `bond_risk_evidence_missing=closed`
- `strict_correctness_clean_pass=false`
- `promotion_prep_candidate=false`
- `fixture_state=absent`
- `promotion_allowed=false`

The strict correctness blocker remains the active minimum route blocker.

## Blockers And Next Gates

| Blocker | Fund / scope | Owner | Next gate | Blocks minimum v1 | Blocks full v1 |
|---|---|---|---|---:|---:|
| P0 `manager_strategy_text.strategy_summary` unavailable / not comparable | `006597` | future 006597 extractor projection owner | `006597 same-fund unavailable field review / extractor projection gate` | true | true |
| P0 `manager_strategy_text.market_outlook` unavailable / not comparable | `006597` | future 006597 extractor projection owner | `006597 same-fund unavailable field review / extractor projection gate` | true | true |
| 9 same-fund P1 unavailable rows | `006597` | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true until explicitly scoped out | true |
| P0 `fee_schedule` has no current 006597 golden rows | `006597` | future 006597 golden coverage owner | `006597 P0 fee_schedule fact-freeze / golden coverage gate` | true for full P0 proof | true |
| P0 `manager_strategy_text.strategy_summary` / `market_outlook` partial coverage gap | `004393` | future 004393 extractor projection owner | `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate` | true | true |
| P0 strict correctness coverage equals `0` | `004194` | future 004194 P0 golden coverage owner | `004194 P0 golden row fact-freeze / strict correctness expansion gate` | true | true |
| `tracking_error` production golden rows lack reviewed direct observed disclosure evidence | `004194` / future index coverage | P15 / tracking-error evidence owner | `P15 direct observed disclosure evidence gate` | false for current diagnostic-only scope | true |
| Fixture state absent for Track 1 funds | `004393`, `004194`, `006597` | future fixture promotion lifecycle owner | separate fixture promotion-prep / promotion gate after blockers close | true | true |

## Next Minimum Entry Point

The next minimum entry point is:

`006597 same-fund unavailable field review / extractor projection gate`

Rationale：`006597` is the smallest currently active Track 1 blocker after the configured strict correctness rerun. It already has a current rerun ledger with `0` mismatch and a finite same-fund unavailable ledger. The next gate should address the two P0 `manager_strategy_text` unavailable rows and disposition the nine P1 unavailable rows without guessing fixes.

After that gate is accepted, revisit this readiness decision. The `004393` P0 `manager_strategy_text` projection gap and `004194` P0 golden coverage path remain future blockers, but they are not the immediate next entry if prioritizing the smallest active blocker.

## Manifest And Preflight Disposition

No preflight or manifest update is authorized now.

The tracked residual disposition manifest and fixture promotion state manifest remain control-plane evidence, not promotion manifests. They continue to support conservative state:

- `fixture_state=absent` for `004393`, `004194`, and `006597`.
- `promotion_allowed=false` for `004393`, `004194`, and `006597`.
- `promotion_manifest=false`.

If the project wants those artifacts to reflect the accepted 006597 rerun wording instead of the earlier `strict_golden_not_configured` wording, that must be a separate control-plane lifecycle gate with its own review and validation. This decision artifact does not mutate them.

## Final Accepted Decision Candidate

```text
decision=blocked_with_reason
overall_readiness=not_ready
minimum_v1_promotion_prep_ready=false
any_fund_can_enter_promotion_prep_now=false
004393_candidate_state=not_candidate_partial_coverage_rejected
004194_candidate_state=index_profile_only_diagnostic_not_promotion_prep
006597_candidate_state=blocked_pending_same_fund_unavailable_field_review
fixture_state_after_gate=absent_for_all_track1_funds
promotion_allowed=false
promotion_manifest=false
preflight_manifest_update_now=false
next_minimum_entry_point=006597_same_fund_unavailable_field_review_extractor_projection_gate
```

## Non-Goals / Forbidden Changes

This gate explicitly does not:

- promote any fixture or golden answer row;
- edit `reports/golden-answers/golden-answer.json`;
- edit golden fixtures, snapshots, score outputs, quality gate outputs, reports, preflight outputs or manifests;
- update `docs/implementation-control.md` or `docs/design.md`;
- change runtime code, tests, scripts, package metadata, `pyproject.toml` or `uv.lock`;
- change FQ / score / quality semantics;
- enter QDII, FOF, `110020`, Host/Agent/dayu, PR, push, merge, release or promotion work.

## Validation

Required validation for this docs-only decision:

```text
git diff --check -- docs/reviews/release-maintenance-minimum-v1-promotion-prep-readiness-decision-20260529.md
```

Expected result：passed, no output.

Forbidden diff check:

```text
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json docs/implementation-control.md docs/design.md reports/golden-answers
```

Expected result：passed, no output.

`ruff` / `pytest` are not required because this gate is docs-only and does not modify Python, tests, runtime behavior, extractor projection, score semantics, quality gate semantics, preflight consumption, manifests, reports or golden fixtures.

## Self-Check

Self-check：pass. This artifact encodes `not_ready / blocked_with_reason`, preserves all forbidden boundaries, and records no promotion or state mutation.
