# Provider/LLM Chapter 3 Post-fix Bounded Live Re-evidence

Date: 2026-06-14 local / 2026-06-13 UTC artifact timestamp

## Scope

This evidence belongs to `Provider/LLM Chapter 3 Post-fix Bounded Live Re-evidence Gate`.

Accepted prerequisite checkpoint:

- `2bced82 fix: handle chapter 3 missing typed availability`
- Controller judgment: `docs/reviews/provider-llm-chapter3-fund-writer-missing-availability-no-live-patch-implementation-controller-judgment-20260614.md`

This gate only re-runs one bounded `004393 / 2025` Route C live command after the accepted no-live Fund writer patch. It does not change source policy, provider defaults, repair budget, annual-period LLM route, Docling scope, readiness, release or PR state.

## Guardrails

- EID remains the single operational source path.
- No Eastmoney, fund-company website, CNINFO or other fallback was introduced.
- No PDF/source/cache body was read for this evidence.
- No writer markdown, raw prompt, provider payload or chapter body content was read.
- `release/readiness` remains `NOT_READY`.

## Preflight

Commands:

```bash
pgrep -x fund-analysis
pgrep -x uv
find reports/llm-runs -maxdepth 1 -type d -name '004393-2025-20260614*' -print
git diff --check
```

Observed result:

- No running `fund-analysis` process.
- No running `uv` process.
- No visible current-date partial runtime artifact matching `004393-2025-20260614*`.
- `git diff --check` passed with no output.

## Live Command

Command:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Observed result:

- Exit code: `1`
- Runtime artifact: `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/manifest.json`
- Summary artifact: `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/summary.json`
- Chapter 3 metadata artifact: `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/chapters/chapter-03.json`
- Host run id: `host_run_c1b20382568e4ae0`
- Elapsed ms from CLI diagnostic: `188648`

CLI diagnostic summary:

- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- `first_failed_chapter_id=3`
- `first_failed_status=failed`
- `first_failed_stop_reason=llm_exception`
- `first_failed_category=code_bug`
- `first_failed_runtime_operation=writer`
- `first_failed_provider_attempts=0/unknown`
- `first_failed_runtime_category=unknown`
- `first_failed_max_output_chars=12000`
- `chapter_matrix=1:accepted;2:accepted;3:failed;4:accepted;5:accepted;6:accepted`

## Safe Metadata Reviewed

Read:

- `manifest.json` safe top-level metadata.
- `summary.json` structured run summary.
- `chapter-03.json` structured Chapter 3 diagnostic metadata.

Not read:

- `chapters/*-writer.md`
- `chapters/*-auditor-feedback.md`
- raw prompts
- provider payloads
- source/PDF/cache bodies

## Accepted Evidence Facts

1. The post-fix bounded live command still fails closed.
2. Chapter 3 remains the first failed chapter.
3. Chapter 3 still fails at writer operation before provider execution.
4. Provider attempt count remains `0`.
5. Runtime diagnostic records `error_type=ValueError`, `failure_category=code_bug`, `stop_reason=llm_exception`.
6. `max_output_chars=12000` is present in the Chapter 3 runtime diagnostic, so this is not the prior null-cap metadata residual.
7. Chapters 1, 2, 4, 5 and 6 reached accepted state in this run; final assembly remains blocked because Chapter 3 is not accepted.

## Evidence Limits

This live evidence proves that the accepted Fund writer missing-availability patch did not complete the Chapter 3 Route C path for `004393 / 2025`.

This live evidence does not prove:

- provider availability or provider response quality;
- LLM content quality;
- final report readiness;
- release readiness;
- source fallback behavior;
- annual-period LLM route viability.

Because provider attempts remain `0`, the current failure remains a provider-before code/diagnostic problem, not provider runtime evidence.

## Residuals

| Residual | Classification | Owner / next action |
| --- | --- | --- |
| Chapter 3 still fails writer-before-provider with `ValueError` after `2bced82` | Open blocker | No-live root-cause evidence gate should inspect code/typed diagnostic path and reproduce the exact remaining `ValueError` without live/provider commands |
| Provider availability for Chapter 3 | Not evaluated | Deferred until Chapter 3 reaches provider attempt > 0 |
| LLM report content quality | Not evaluated | Deferred until accepted draft/conclusion exists for Chapter 3 |
| Release/readiness | Not ready | Preserve `NOT_READY` |

## Verdict

VERDICT: LIVE_FAIL_CLOSED_STILL_PROVIDER_BEFORE_CODE_BUG_NOT_READY

Recommended next gate:

`Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`
