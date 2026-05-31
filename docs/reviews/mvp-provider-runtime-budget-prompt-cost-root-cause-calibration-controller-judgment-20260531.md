# MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration Controller Judgment

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: Gateflow controller.
- Date: 2026-05-31
- Classification: `heavy`
- Judgment: **blocked with root cause narrowed and implementation locally accepted**

## Decision

This gate is accepted as a local diagnostic / runtime-cost hardening gate, but the real provider smoke is not accepted.

The implementation safely added prompt-cost diagnostics, compact writer payload mode for explicit CLI `--use-llm`, operation-specific timeout config, timeout-only bounded retry diagnostics and root-cause hints. Reviews and validation pass.

The real provider acceptance remains blocked because compact small writer prompts still time out under the current bounded budget.

## Evidence

Primary artifacts:

- Plan: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md`
- Plan reviews: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-ds-20260531.md`
- Implementation evidence: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-implementation-evidence-20260531.md`
- Code reviews: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-code-review-ds-20260531.md`
- Deep review: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-deepreview-20260531.md`
- Validation evidence: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-validation-evidence-20260531.md`
- Runtime evidence directory: `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/`

Validation:

- `uv run ruff check .`: PASS
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: PASS, `1206 passed`, total coverage `91.82%`
- deterministic `fund-analysis analyze 006597 --report-year 2024`: PASS
- deterministic `fund-analysis checklist 006597 --report-year 2024`: PASS
- missing-config `--use-llm`: PASS fail-closed, exit `1`
- real provider `fund-analysis analyze 006597 --report-year 2024 --use-llm`: BLOCKED, exit `1`, stdout empty
- secret scan: exact current API key hits `0`; no Authorization header, full prompt, full draft or full provider response in current report artifacts

## Current Real Provider Result

CLI:

- `real-provider-cli.exitcode=1`
- stdout empty
- no deterministic fallback
- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- first failed: chapter 2 writer `llm_timeout`
- first failed prompt scale: `6360` chars / approx `1590` tokens
- first failed hint: `small_prompt_provider_timeout`

Service diagnostic:

- `prompt_payload_mode=compact`
- `orchestration_status=blocked`
- `final_assembly_status=incomplete`
- `report_markdown_present=false`
- `generated_chapter_ids=[1,2,3,4,5,6]`
- `skipped_chapter_ids=[]`
- `accepted_chapter_ids=[]`

Per-chapter Service matrix:

| Chapter | Status | Stop reason | Operation | Attempts | Approx tokens | Timeout hint |
|---:|---|---|---|---:|---:|---|
| 1 | failed | `llm_timeout` | writer | 2 | 2109 | `small_prompt_provider_timeout` |
| 2 | failed | `llm_timeout` | writer | 2 | 1590 | `small_prompt_provider_timeout` |
| 3 | failed | `llm_timeout` | writer | 2 | 2575 | `small_prompt_provider_timeout` |
| 4 | failed | `llm_timeout` | writer | 2 | 1274 | `small_prompt_provider_timeout` |
| 5 | failed | `llm_timeout` | writer | 2 | 2518 | `small_prompt_provider_timeout` |
| 6 | failed | `llm_timeout` | writer | 2 | 2110 | `small_prompt_provider_timeout` |

## Prompt-Cost Calibration Decision

The former large-prompt blocker for chapters 2 and 6 is resolved for the current explicit `--use-llm` path:

| Chapter | Before approx tokens | After approx tokens | Decision |
|---:|---:|---:|---|
| 2 | 26086 | 1590 | no longer `large_writer_prompt_cost` |
| 6 | 29078 | 2110 | no longer `large_writer_prompt_cost` |

Current chapter 2 / 6 timeout cannot be attributed to large writer prompt cost. The current blocker is small-prompt provider runtime timeout.

## Root-Cause Classification

Accepted primary blocker:

- `provider_runtime_timeout_small_prompt`

Rejected classifications:

- `provider_runtime_timeout_large_prompt`: rejected by current compact prompt costs.
- `prompt_cost_regression`: rejected because ch2/ch6 costs decreased materially.
- `prompt_contract`: no current contract failure; writer provider call times out before parser/auditor.
- `audit_rule_calibration`: no current row reaches audit.
- `fact_gap`: no current fact-gap failure evidence.
- `code_bug`: local tests pass and diagnostics are internally consistent.
- `provider_config` / `provider_auth`: rejected by prior provider verification and current real provider calls reaching runtime timeout.

## Safety Boundary

No audit, evidence, ITEM_RULE, candidate facet, missing semantics, E2 deferred, transaction-advice or final assembly boundary was relaxed. Partial matrices remain diagnostic only. Deterministic analyze/checklist remain unchanged.

## Next Smallest Entry Point

Start `MVP provider endpoint small-prompt runtime budget calibration gate`.

Minimum scope:

1. Do not revisit provider config/auth unless env loading fails.
2. Run bounded experiments with operation-specific timeout values, for example writer timeout `120s`, max attempts `2`, backoff `2s`; do not use unlimited retry.
3. Capture same-source Service diagnostics for 006597 / 2024 with prompt chars, approximate tokens, timeout seconds, attempts, elapsed ms and operation.
4. Determine whether small prompts complete under a bounded writer budget or whether the endpoint/model runtime is still timing out.
5. If small prompts still time out under a reasonable bounded budget, classify as `provider_endpoint_runtime` and stop; do not keep slimming already-small prompts or relax audit/evidence rules.

The next gate may include a separate follow-up for chapter 3 C2 only after writer timeout no longer prevents reaching audit.
