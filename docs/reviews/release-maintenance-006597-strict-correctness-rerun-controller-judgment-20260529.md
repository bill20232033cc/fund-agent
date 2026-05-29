# 006597 Strict Correctness Rerun Controller Judgment

日期：2026-05-29

角色：Phaseflow / Gateflow controller。本文只做 controller 裁决和状态固化，不是 promotion manifest，不修改 golden fixture / golden-answer JSON，不授权 push、PR、merge、release、golden promotion 或 fixture promotion。

## Scope

Gate：`006597 strict correctness rerun / same-fund unavailable field review gate`

Gate classification：`heavy`。原因：本 gate 影响 strict golden correctness、fixture promotion-prep eligibility、minimum golden v1 readiness 和 release maintenance roadmap Track 1；本次实现限定为 rerun evidence / docs / review artifact，不改生产代码、golden、manifest 或 FQ 语义。

Accepted plan commit：`15cf863`

Accepted plan artifact：

- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md`

Accepted plan reviews：

- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-review-mimo-20260529.md`：`PASS_WITH_FINDINGS`
- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-review-glm-20260529.md`：`PASS_WITH_FINDINGS`

Implementation / evidence artifact：

- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-20260529.md`

Implementation reviews：

- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-review-mimo-20260529.md`：`PASS`
- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-review-glm-20260529.md`：`PASS`

Rerun outputs：

- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json`
- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.md`
- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/golden_set.json`
- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json`
- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.md`

The report outputs are generated evidence only and are gitignored in the current workspace. They are not tracked fixtures and not promotion artifacts.

## Accepted Decision

Controller accepts the evidence outcome:

`decision=blocked_pending_same_fund_unavailable_field_review`

The rerun successfully consumed `reports/golden-answers/golden-answer.json` and produced a configured strict correctness score for `006597 / 2024`. It did not cleanly pass.

Accepted correctness summary:

| Field | Value |
|---|---:|
| `coverage_scope` | `partially_covered` |
| `total_records` | 150 |
| `comparable_records` | 9 |
| `matched_records` | 9 |
| `mismatched_records` | 0 |
| `unavailable_records` | 141 |
| `skipped_records` | 29 |
| `accuracy_rate` | 1.0 |
| same-fund `006597` unavailable | 11 |
| cross-fund unavailable | 130 |

The 130 cross-fund unavailable rows are not a 006597 same-fund failure. The blocker is the 11 same-fund unavailable rows.

Accepted same-fund breakdown:

- Matched rows：9
- Mismatched rows：0
- Unavailable rows：11

Matched rows are the currently comparable `006597` P0 rows:

- `basic_identity.fund_name`
- `basic_identity.fund_code`
- `basic_identity.management_company`
- `basic_identity.custodian`
- `basic_identity.inception_date`
- `benchmark.benchmark_name`
- `classified_fund_type.fund_type`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`

Unavailable same-fund rows:

- P0：`manager_strategy_text.strategy_summary`
- P0：`manager_strategy_text.market_outlook`
- P1：`product_profile.investment_objective`
- P1：`product_profile.style_positioning`
- P1：`manager_alignment.manager_holding`
- P1：`manager_alignment.employee_holding`
- P1：`holder_structure.institutional_holder`
- P1：`holder_structure.individual_holder`
- P1：`share_change.beginning_share`
- P1：`share_change.ending_share`
- P1：`share_change.net_change`

Because two P0 `manager_strategy_text` rows are same-fund unavailable, `006597` is not a minimum v1 promotion-prep candidate after this gate. `clean_pass=false`, `promotion_prep_candidate=false`, and `promoted=false`.

`fee_schedule` is P0 by `docs/design.md` §7.3 but has no current 006597 golden-answer row. Therefore even a hypothetical clean pass over the current 20 006597 rows would not prove full P0 coverage.

## Fixture / Promotion State

Controller accepts the conservative state:

| Field | Value |
|---|---|
| `fixture_state` | `absent` |
| `promotion_allowed` | `false` |
| `promotion_manifest` | `false` |
| `blocks_minimum_v1` | `true` |
| `blocks_full_v1` | `true` |

The accepted fixture promotion state manifest was not modified. It may still list `strict_golden_not_configured` as a blocker because manifest/preflight consumption was out of scope for this rerun gate. This rerun is evidence for future control-plane reconciliation; it is not itself a manifest mutation or promotion.

The `006597` bond risk evidence blocker remains closed as resolved context only. It does not override strict correctness / fixture readiness blockers.

## Review Finding Disposition

Plan review findings:

- MiMo F1：old follow-up score predicted 9 matched P0 and 11 same-fund unavailable rows.
  - Disposition：accepted as non-blocking predictor only.
  - Controller decision：current judgment relies on the new 006597-specific rerun output, not the old untracked multi-fund follow-up artifacts.

- MiMo F2：this rerun is the first configured strict correctness run for 006597 and may resolve the `strict_golden_not_configured` evidence gap.
  - Disposition：accepted as evidence note.
  - Controller decision：do not update preflight or manifests in this gate; route control-plane reconciliation to a future manifest/preflight lifecycle gate or Track 1 readiness decision.

- GLM F1：`fee_schedule` is P0 but has no current 006597 golden rows.
  - Disposition：accepted as explicit coverage limitation.
  - Controller decision：recorded in evidence and this judgment; clean pass over current rows would still not prove full P0 coverage.

Implementation evidence reviews:

- MiMo：`PASS`, no findings.
- GLM：`PASS`, no findings.

## Residuals

| Residual | Owner | Next gate | Blocks minimum v1 | Blocks full v1 |
|---|---|---|---:|---:|
| `manager_strategy_text.strategy_summary` unavailable | future 006597 extractor projection owner | `006597 extractor projection gate` | true | true |
| `manager_strategy_text.market_outlook` unavailable | future 006597 extractor projection owner | `006597 extractor projection gate` | true | true |
| 9 P1 same-fund unavailable rows | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true until controller explicitly scopes them out | true |
| `fee_schedule` P0 has no current 006597 golden rows | future 006597 golden coverage owner | `006597 P0 fee_schedule fact-freeze / golden coverage gate` | true for full P0 coverage | true |
| Manifest/preflight still reflect older `strict_golden_not_configured` blocker | artifact / manifest lifecycle owner | control-plane reconciliation or minimum v1 readiness decision gate | true until reconciled | true |

No residual authorizes runtime fix, golden edit, manifest mutation, fixture promotion, release readiness, or external GitHub mutation.

## Validation

Accepted validation:

- `uv run fund-analysis extraction-score ... --golden-answer-path reports/golden-answers/golden-answer.json --output-dir reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529` exited 0.
- `uv run fund-analysis quality-gate --score-path reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json --output-dir reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529` exited 0.
- `python -m json.tool` passed for the new score JSON and quality gate JSON.
- `git diff --check` passed for the evidence artifact.
- Forbidden diff over golden answers, manifests, runtime code, tests, scripts, `pyproject.toml`, `uv.lock`, `docs/implementation-control.md`, and `docs/design.md` produced no output.
- `git status --short` for the new report output directories produced no output because those generated reports are ignored; they remain local generated evidence, not tracked fixtures.

Full `ruff` / `pytest` were not run because this gate did not modify Python, tests, runtime behavior, snapshot projection, extractor, score semantics, quality gate semantics, preflight consumption, or manifests. The only executable actions were existing CLI rerun commands plus docs/evidence output.

Controller will run `git diff --check` again after this judgment and the control-doc update before committing the accepted local checkpoint.

## Controller Self-Check

- Current role：controller；this judgment and control-doc update are allowed controller work.
- Source of truth：`AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted 006597 plan/reviews, rerun evidence, MiMo / GLM evidence reviews.
- Scope boundary：Track 1 006597 strict correctness evidence only; no code, fixtures, golden-answer JSON, manifests, preflight mutation, QDII/FOF/110020/004393/004194, Host/Agent/dayu, PR/push/merge/release/promotion.
- Stop conditions：same-fund unavailable exists, so this gate ends blocked-with-reason rather than attempting fixes.
- Next action：minimal update to `docs/implementation-control.md`; commit accepted local checkpoint for evidence/judgment only.

## Final Judgment

`006597` strict correctness rerun is accepted as configured evidence, but the gate outcome is blocked-with-reason. `006597` remains not promotion-prep-ready and not promoted. `fixture_state=absent` and `promotion_allowed=false` remain unchanged.

Next minimum Track 1 entry：`006597 same-fund unavailable field review / extractor projection gate` for the two P0 `manager_strategy_text` unavailable rows and the P1 unavailable ledger. The later `minimum v1 promotion-prep readiness decision` should not run as accepted-ready until this blocker is resolved or explicitly scoped by a separate controller decision.
