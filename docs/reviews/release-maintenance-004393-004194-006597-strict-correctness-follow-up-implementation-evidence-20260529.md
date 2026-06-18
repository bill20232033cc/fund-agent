# 004393 / 004194 / 006597 Strict Correctness Follow-up Implementation Evidence

Date: 2026-05-29

Role: AgentCodex implementation/evidence worker; not controller.

## Verdict

**BLOCKED with reason.**

The 006597 public CLI rerun produced strict correctness output, but it triggered the accepted stop condition: same-fund 006597 has `unavailable` field-level records that require a separate manual evidence confirmation gate. This worker did not perform manual verification, did not edit the golden answer, did not edit fixtures, did not edit manifests, did not run promotion, and did not change code.

## Inputs

- Accepted plan: `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md`
- Plan reviews:
  - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md` - PASS
  - `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md` - PASS
- 006597 rerun score: `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json`
- 006597 rerun golden set: `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/golden_set.json`
- Golden answer used for rerun: `reports/golden-answers/golden-answer.json`

## 006597 Rerun Result

Command already executed before this evidence artifact:

```bash
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json --output-dir reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529
```

Machine result:

| Field | Value |
|---|---:|
| correctness.status | `available` |
| golden_answer_path | `reports/golden-answers/golden-answer.json` |
| total_records | 150 |
| comparable_records | 9 |
| matched_records | 9 |
| mismatched_records | 0 |
| unavailable_records | 141 |
| coverage_scope | `partially_covered` |
| covered_fund_codes | `006597` |

Same-fund 006597 summary:

| Status | Count |
|---|---:|
| match | 9 |
| unavailable | 11 |

Matched same-fund fields:

- `basic_identity.fund_name`
- `basic_identity.fund_code`
- `basic_identity.management_company`
- `basic_identity.custodian`
- `basic_identity.inception_date`
- `benchmark.benchmark_name`
- `classified_fund_type.fund_type`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`

Same-fund unavailable fields requiring later manual field review:

- `product_profile.investment_objective`
- `product_profile.style_positioning`
- `manager_strategy_text.strategy_summary`
- `manager_strategy_text.market_outlook`
- `manager_alignment.manager_holding`
- `manager_alignment.employee_holding`
- `holder_structure.institutional_holder`
- `holder_structure.individual_holder`
- `share_change.beginning_share`
- `share_change.ending_share`
- `share_change.net_change`

Machine reason for each unavailable row: snapshot did not explicitly expose the golden sub-field, so the row does not enter the correctness denominator.

## Fund Decisions

| Fund | Decision | Fixture state | Promotion allowed | Reason |
|---|---|---|---:|---|
| `004393` | `not_minimum_v1_promotion_prep_by_default` | `absent` | false | Strict correctness remains partial by default: 9/150 comparable, 9 matched, 0 mismatched, 141 unavailable. |
| `004194` | `index_profile_only_candidate_not_full_fixture_ready` | `absent` | false | Machine match is limited to five `index_profile.*` records; this is not full fixture readiness. |
| `006597` | `blocked_pending_same_fund_unavailable_field_review` | `absent` | false | Rerun is configured and available, but same-fund 006597 has 11 unavailable fields requiring separate manual field-level review. |

006597 bond blocker is closed as resolved context only. It is not an active blocker in this follow-up and is not used as promotion evidence.

## Non-mutation Statement

This evidence artifact and its paired machine-readable JSON are control-plane review artifacts only:

- `promotion_manifest=false`
- `not_promotion_manifest=true`
- `runtime_consumed=false`
- `promotion_allowed=false`

No golden answer, fixture manifest, residual manifest, code, tests, or promotion state was changed by this worker.
