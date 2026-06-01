# MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration Validation Evidence

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: Gateflow controller validation evidence, not implementation worker evidence.
- Date: 2026-05-31
- Report directory: `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/`

## Summary

The implementation is locally valid, but the real provider smoke is still blocked.

The same-source CLI and Service diagnostics prove that compact writer payloads reduced the former chapter 2 / 6 large writer prompts below the large-prompt threshold. The remaining blocker is small-prompt provider runtime timeout: every body chapter writer timed out under the bounded default budget.

## Commands And Results

| Check | Command / artifact | Result |
|---|---|---|
| Ruff | `uv run ruff check .` | PASS; `ruff.exitcode=0`; stdout `All checks passed!` |
| Full pytest | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS; `pytest.exitcode=0`; `1206 passed`, total coverage `91.82%` |
| Deterministic analyze | `uv run fund-analysis analyze 006597 --report-year 2024` | PASS; `deterministic-analyze.exitcode=0` |
| Deterministic checklist | `uv run fund-analysis checklist 006597 --report-year 2024` | PASS; `deterministic-checklist.exitcode=0` |
| Missing-config `--use-llm` | env-unset `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | PASS fail-closed; `missing-config-use-llm.exitcode=1`; stderr `missing FUND_AGENT_LLM_PROVIDER` |
| Real provider CLI | `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | BLOCKED; `real-provider-cli.exitcode=1`; stdout empty; stderr safe summary only |
| Service diagnostic JSON | same provider config, `prompt_payload_mode=compact` | Emitted `service-diagnostic.json`; no complete report |

## Real Provider CLI Evidence

Artifact:

- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/real-provider-cli.stdout`
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/real-provider-cli.stderr`
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/real-provider-cli.exitcode`

CLI result:

- Exit code: `1`
- stdout: empty
- deterministic fallback observed: no
- orchestration status: `partial`
- final assembly status: `incomplete`
- first failed chapter: `2`
- first failed operation: `writer`
- first failed category: `llm_timeout`
- first failed provider attempts: `2/2`
- first failed runtime category: `timeout`
- first failed prompt chars: `6360`
- first failed approximate prompt tokens: `1590`
- first failed timeout hint: `small_prompt_provider_timeout`
- all-chapter CLI matrix: chapter 1 accepted; chapters 2-6 failed `llm_timeout`

The CLI path is the real user command and uses compact writer payload mode in `fund_agent/ui/cli.py`.

## Service Diagnostic Evidence

Artifact:

- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/service-diagnostic.json`

Top-level result:

- `prompt_payload_mode=compact`
- `orchestration_status=blocked`
- `final_assembly_status=incomplete`
- `report_markdown_present=false`
- `generated_chapter_ids=[1,2,3,4,5,6]`
- `skipped_chapter_ids=[]`
- `accepted_chapter_ids=[]`
- deterministic fallback observed: false

Per-chapter runtime matrix:

| Chapter | Status | Stop reason | Operation | Attempts | Max elapsed ms | Approx tokens | User prompt chars | Timeout hint |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | failed | `llm_timeout` | writer | 2 | 60094 | 2109 | 8346 | `small_prompt_provider_timeout` |
| 2 | failed | `llm_timeout` | writer | 2 | 60029 | 1590 | 6273 | `small_prompt_provider_timeout` |
| 3 | failed | `llm_timeout` | writer | 2 | 60065 | 2575 | 10213 | `small_prompt_provider_timeout` |
| 4 | failed | `llm_timeout` | writer | 2 | 60091 | 1274 | 5006 | `small_prompt_provider_timeout` |
| 5 | failed | `llm_timeout` | writer | 2 | 79066 | 2518 | 9985 | `small_prompt_provider_timeout` |
| 6 | failed | `llm_timeout` | writer | 2 | 60027 | 2110 | 8350 | `small_prompt_provider_timeout` |

All rows use `timeout_seconds=60.0`, `provider_max_attempts=2`, and `timeout_budget_kind=writer_initial`.

## Prompt-Cost Before / After

Baseline source:

- `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`

Current source:

- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/service-diagnostic.json`

| Chapter | Before operation | Before approx tokens | Before user chars | After operation | After approx tokens | After user chars | After hint |
|---:|---|---:|---:|---|---:|---:|---|
| 2 | writer | 26086 | 104256 | writer | 1590 | 6273 | `small_prompt_provider_timeout` |
| 6 | writer | 29078 | 116223 | writer | 2110 | 8350 | `small_prompt_provider_timeout` |

Current prompt-cost component examples:

- Chapter 2 components: protocol `1521`, contract `463`, must_answer `160`, must_not_cover `72`, required_output `447`, facts `2293`, anchors `1284`, repair_context `26`.
- Chapter 2 large raw fact `structured.nav_data` had `value_chars=98093` but serialized compact fact row `serialized_fact_chars=523`.
- Chapter 6 components: protocol `1565`, contract `397`, must_answer `157`, must_not_cover `139`, required_output `204`, facts `3741`, anchors `2114`, repair_context `26`.

Conclusion: the former large chapter 2 / 6 writer prompt cost was materially reduced. The remaining timeout is no longer explainable as `large_writer_prompt_cost`.

## Secret And Payload Safety

Scans:

- Exact current API key byte match under the current report directory: `exact_key_hits=0`.
- Generic scan for `Authorization`, `Bearer `, `sk-`, `provider response`, `raw_response`, `draft_markdown`, `system_prompt`, `user_prompt` in the current report directory found only safe scalar field names such as `system_prompt_chars` and `user_prompt_chars`.

No API key, Authorization header, full prompt, full draft, full provider response or raw audit response was recorded in the current gate artifacts.

## Root-Cause Classification

Rejected:

- `large_writer_prompt_cost`: rejected for current smoke because compact mode reduced chapter 2 from `26086` to `1590` approximate tokens and chapter 6 from `29078` to `2110`.
- `prompt_cost_regression`: rejected; current ch2/ch6 cost decreased materially versus previous diagnostic.
- `prompt_contract`: no marker / required-output / candidate-facet contract failure appears in the current first failing rows.
- `audit_rule_calibration`: no current row reached audit; failures are writer provider timeouts.
- `fact_gap`: no current evidence of missing facts causing fail-closed; failures occur at provider runtime writer calls.
- `code_bug`: no code-path error evidence; ruff, full pytest, deterministic analyze/checklist and missing-config fail-closed pass.

Accepted:

- Primary blocker: `provider_runtime_timeout_small_prompt`.
- More specific next-entry framing: provider endpoint/runtime budget calibration for small prompts, because all current writer prompts are below `3000` approximate tokens yet time out after bounded `60s x2` attempts.

## Residual Risk

The provider health check can return HTTP 200 for a tiny request, but full report generation still times out for small prompt writer calls. That distinction means the next gate should not revisit provider config/auth. It should compare bounded operation-specific budgets and provider endpoint behavior using safe elapsed/attempt diagnostics, while keeping no deterministic fallback and no audit/evidence relaxation.
