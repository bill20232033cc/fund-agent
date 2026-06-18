# Controller Judgment: 004393 / 2025 Tracked Golden Content Write Implementation

Date: 2026-06-13

Gate: `004393 / 2025 Tracked Golden Content Write Implementation Gate`

Implementation evidence:
`docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md`

Review inputs:

- `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-review-ds-20260613.md`
- `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-review-mimo-20260613.md`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## 1. Controller Scope

This judgment accepts the tracked golden content write implementation for
`004393 / 2025`.

This judgment accepts only the seven source-body-verified rows written through
the reviewed Markdown and generated JSON path. It does not promote fixtures, it
does not claim release/readiness, and it does not authorize PR, push, merge,
provider, LLM, analyze, checklist, live, fallback or source-policy changes.

Release/readiness remains `NOT_READY`.

## 2. Accepted Implementation Facts

| Fact | Disposition | Basis |
|---|---|---|
| Implementation followed the accepted S1-S3 sequence: reviewed Markdown write, generated JSON, implementation evidence. | `ACCEPT` | Implementation evidence; DS review verdict `PASS`; MiMo review verdict `PASS` |
| The new reviewed Markdown block is for `004393 / 2025`, includes `report_year: 2025`, and is placed after the existing `004393 / 2024` block before the next fund heading. | `ACCEPT` | `reports/golden-answers/golden-answer-prefill-reviewed.md`; implementation evidence §4-5; MiMo F1-F3 |
| Exactly seven active rows were written for `004393 / 2025`. | `ACCEPT` | Implementation evidence §4; DS §4; MiMo F2 |
| `fee_schedule.management_fee`, `fee_schedule.custody_fee`, `turnover_rate`, skipped rows and deferred rows were not added for `004393 / 2025`. | `ACCEPT` | DS §4; MiMo F4-F5; controller parse check |
| `golden-build` regenerated `reports/golden-answers/golden-answer.json` with `funds=12`, `records=157`, `skipped=29`. | `ACCEPT` | Implementation evidence §3 and §5; DS §5; MiMo F8-F9 |
| Baseline skipped count was `29`; post-write skipped count remains `29`. | `ACCEPT` | Implementation evidence §3; DS §5; MiMo F8 |
| Non-target Markdown and loader-semantic JSON preservation checks passed. | `ACCEPT` | Implementation evidence §5; DS §3 and §8; MiMo F6-F7 |
| Targeted tests, ruff and diff whitespace checks passed. | `ACCEPT` | Implementation evidence §5; MiMo F10-F12; controller rerun |

## 3. Accepted Rows

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| `basic_identity` | `fund_name` | `安信企业价值优选混合型证券投资基金` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_name` |
| `basic_identity` | `fund_code` | `004393` | `high` | `年报2025 §2 page-5 page-5-table-0 fund_code` |
| `basic_identity` | `management_company` | `安信基金管理有限责任公司` | `high` | `年报2025 §2 page-5 page-5-table-0 management_company` |
| `basic_identity` | `custodian` | `中国银行股份有限公司` | `high` | `年报2025 §2 page-5 page-5-table-0 custodian` |
| `basic_identity` | `inception_date` | `2022年8月8日` | `high` | `年报2025 §2 page-5 page-5-table-0 inception_date` |
| `product_profile` | `investment_objective` | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。` | `medium` | `年报2025 §2 page-5 page-5-table-1 investment_objective` |
| `benchmark` | `benchmark_name` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%` | `high` | `年报2025 §2 page-5 page-5-table-1 benchmark` |

These seven rows are now accepted tracked golden content for `004393 / 2025`
within the reviewed Markdown/generated JSON contract.

## 4. Review Finding Disposition

| Finding | Source | Controller disposition | Follow-up |
|---|---|---|---|
| No blocking implementation findings. | DS / MiMo | `ACCEPT` | No fix or re-review required. |
| Implementation evidence lacks an explicit "Next Gate Recommendation" section. | DS non-blocking observation | `ACCEPT_AS_NONBLOCKING` | Controller judgment and control sync provide next entry. No implementation fix required. |
| Source-body verification used parsed cache, not fresh-fetch proof. | DS / MiMo residual | `ACCEPTED_RESIDUAL` | Preserve provenance context; fresh-fetch proof remains a separate gate only if requested. |
| Fixture promotion remains unresolved and year-blind. | DS / MiMo residual | `ACCEPTED_RESIDUAL` | Separate fixture promotion design/evidence gate. |
| Release/readiness remains unproven. | DS / MiMo residual | `ACCEPTED_RESIDUAL_NOT_READY` | Separate readiness/evidence rollup gate. |

## 5. Validation

Controller verified or accepted the following validation matrix:

```text
uv run python -c "<parse reviewed Markdown and generated JSON; assert 004393/2025 has 7 rows and 0 skipped; assert total skipped remains 29>"
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
git diff --check
git diff --name-only
```

Observed results:

```text
controller_parse_ok md_funds=12 md_records=157 md_skipped=29 json_funds=12 json_records=157 json_skipped=29
34 passed
All checks passed!
git diff --check: clean
tracked diff: reports/golden-answers/golden-answer-prefill-reviewed.md, reports/golden-answers/golden-answer.json
```

## 6. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Fixture promotion remains unresolved because the current promotion path is not yet proven year-aware for `004393 / 2025`. | Fixture/golden owner | Separate fixture promotion design/evidence gate |
| This write does not prove strict golden coverage/readiness pass or release readiness. | Release / quality owner | Separate non-live readiness/evidence gate |
| Source-body verification provenance records `parsed_cache_hit=true`, not fresh-fetch proof. | Evidence owner | Preserve as provenance; fresh-fetch proof only under separate authorization |
| Fee rows remain rejected for this route. | Golden contract/source owner | Separate fee-row clarification gate if needed |
| `turnover_rate` remains non-applicable for this 2025 route. | Quality/scoring owner | Separate applicability gate only if policy changes |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup only |

## 7. Accepted Checkpoint And Next Entry

Accepted checkpoint to create:

```text
gateflow: accept 004393 tracked golden content write
```

After checkpoint, the recommended next entry is:

```text
004393 / 2025 Fixture Promotion State / Strict Golden Coverage Evidence Planning Gate
```

Purpose of the next entry:

- determine whether the current fixture promotion path can safely express
  `004393 / 2025` year-specific strict golden truth;
- plan coverage/readiness evidence without promoting fixtures by default;
- keep release/readiness `NOT_READY` unless a later evidence gate proves
  otherwise.

Deferred entries:

- controlled fresh-fetch EID source-body proof;
- fee-row clarification;
- turnover policy changes;
- release/readiness rollup;
- PR/release external-state gate.

## 8. Boundary Confirmation

This judgment did not perform or authorize:

- fixture promotion;
- source/test/runtime behavior changes;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- source fallback, Eastmoney, fund-company official site or CNINFO expansion;
- cleanup, archive, push, merge or external-state actions.
