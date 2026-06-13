# Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence Gate`.

Role: AgentController evidence collector.

This artifact records one controlled post-fix Route C live command for exact `004393 / 2025` after the Chapter 2 L1 no-live fix accepted at `842362d`.

This gate does not change source/tests/runtime behavior, source policy, provider defaults, repair budget, readiness/release/PR state or fallback policy. It does not claim release-ready, MVP-ready or LLM-path-ready.

Release/readiness remains `NOT_READY`. Annual-report access remains EID single-source/no-fallback.

## Command

```text
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Result:

- Exit code: `1`
- Runtime artifact: `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
- Stdout excerpt: none accepted as report output.
- Stderr/control output reported incomplete LLM run and first failed chapter 3.

## Safe Metadata Read

Only safe metadata files were read:

- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-03.json`

Not read:

- writer draft Markdown
- repair Markdown
- auditor feedback Markdown
- raw prompts
- provider payloads or provider responses
- source/cache/PDF bodies
- final report body

## Accepted Runtime Facts

Manifest safe metadata:

- `schema_version=llm_incomplete_run_artifact_manifest.v1`
- `run_id=host_run_4a531cbe94604e47`
- `fund_code=004393`
- `report_year=2025`
- `orchestration_status=partial`
- `final_assembly_status=incomplete`

Summary safe metadata:

- `schema_version=llm_incomplete_run_summary.v1`
- `fund_code=004393`
- `report_year=2025`
- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- `first_failed.chapter_id=3`
- `first_failed.status=blocked`
- `first_failed.stop_reason=missing_required_facts`
- `first_failed.failure_category=fact_gap`
- `first_failed.failure_subcategory=null`
- `first_failed.attempt_count=1`

Chapter matrix:

| Chapter | Status | Stop reason | Failure category | Failure subcategory | Attempt count |
| --- | --- | --- | --- | --- | --- |
| 1 | accepted | none | null | null | 1 |
| 2 | accepted | none | null | l1_numerical_closure | 2 |
| 3 | blocked | missing_required_facts | fact_gap | null | 1 |
| 4 | accepted | none | null | null | 1 |
| 5 | accepted | none | null | null | 1 |
| 6 | accepted | none | null | null | 1 |

Chapter 2 safe metadata:

- `status=accepted`
- `stop_reason=none`
- `failure_category=null`
- `failure_subcategory=l1_numerical_closure`
- `diagnostic_consistency_status=consistent`
- `issues_count=0`
- Prompt-contract diagnostics still record an earlier `phase=programmatic_audit` row with `issue_id_prefix_counts["programmatic:L1"]=1` and `l1_numerical_closure_count=1`, but the final chapter status is accepted.
- Runtime diagnostics are safe scalar/null fields only; provider attempt index/max-attempt fields are null.

Chapter 3 safe metadata:

- `status=blocked`
- `stop_reason=missing_required_facts`
- `failure_category=fact_gap`
- `failure_subcategory=null`
- `diagnostic_consistency_status=consistent`
- `provider_attempt_count=null`
- `issues_safe=["3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01"]`
- Runtime operation is `writer`; provider attempt index/max-attempt fields are null.

## Disposition

| Item | Decision | Basis |
| --- | --- | --- |
| Chapter 2 L1 post-fix behavior | ACCEPT_AS_LIVE_IMPROVEMENT_EVIDENCE | Chapter 2 status is now `accepted` after two attempts; no terminal Chapter 2 `repair_budget_exhausted` blocker remains in this run. |
| Chapter 2 full content correctness | NOT_CLAIMED | This gate read only safe metadata, not accepted draft/report body. |
| Chapter 3 item 01 fact-gap blocker | ACCEPT_AS_CURRENT_NEXT_BLOCKER | First failed chapter is now Chapter 3 `missing_required_facts` / `fact_gap`, matching the previous known fact-gap residual. |
| Provider/LLM full completion | REJECT_AS_NOT_PROVEN | Command exit is `1`; final assembly is incomplete. |
| Release/readiness | NOT_READY | Single live evidence does not prove readiness. |

## Residuals

- Full Route C LLM report completion remains unproven.
- Chapter 3 item 01 remains a fact-gap blocker.
- Live provider adherence is only proven for this single sample and this metadata-level outcome.
- H4/H5 diagnostic serialization/projection residuals remain future scope.
- Chapter repair budget calibration remains future scope.
- Release/readiness remains `NOT_READY`.

## Next Gate Recommendation

Proceed to:

`Provider/LLM Chapter 3 Item 01 Fact-gap Disposition Gate`

That next gate should decide whether Chapter 3 item 01 fact-gap remains an accepted residual, needs no-live data/projection diagnostics, or requires a narrow template/required-output policy adjustment. It must not reintroduce provider/source fallback or claim readiness.

## Final Verdict

VERDICT: ACCEPT_LIVE_CHAPTER2_L1_FIX_CONFIRMED_CHAPTER3_FACT_GAP_NOT_READY
