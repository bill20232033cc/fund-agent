# Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence

Date: 2026-06-14

Role: AgentController / evidence owner

Gate: `Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence Gate`

Verdict: `LIVE_FAIL_CLOSED_CHAPTER2_L1_STILL_REPRODUCES_NOT_READY`

## Scope

This artifact records one controlled live/provider sample after the accepted no-live Chapter 2 L1 prompt-contract strengthening at checkpoint `ee65f69`.

The gate only asks whether the strengthened Chapter 2 prompt avoids the previously observed live Chapter 2 L1 repair-budget exhaustion for exact sample `004393 / 2025`.

This artifact does not claim release readiness, MVP readiness, LLM path readiness, general live acceptance or content correctness.

Release/readiness remains `NOT_READY`.

EID annual-report acquisition remains single-source/no-fallback. This gate does not authorize Eastmoney, fund-company/CDN, CNINFO or other fallback routes.

## Command

Executed command:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Result:

- Exit code: `1`.
- Stdout: empty.
- Stderr reported incomplete diagnostic artifacts at `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/manifest.json`.
- Host run id from manifest/summary: `host_run_9dbb1b5be0e54cdb`.
- Host elapsed: `234223 ms`.

## Evidence Read Boundary

Read:

- `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/manifest.json`
- `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/summary.json`
- `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/chapters/chapter-03.json`
- `reports/llm-runs/004393-2025-20260613T221455Z-host_run_9dbb1b5be0e54cd/chapters/chapter-05.json`

Not read:

- writer Markdown bodies
- auditor feedback Markdown bodies
- repair Markdown bodies
- raw prompts
- provider request/response payloads
- source/PDF/cache body
- final report body

## Accepted Live Metadata Facts

Overall run:

- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- first failed chapter: `2`
- first failed status: `failed`
- first failed stop reason: `repair_budget_exhausted`
- first failed category: `prompt_contract`
- first failed subcategory: `l1_numerical_closure`
- first failed runtime operation: `auditor`
- first failed provider attempt count from runtime summary: `0`

Chapter matrix:

| Chapter | Status | Stop reason | Failure category | Failure subcategory | Attempt count |
|---|---|---|---|---|---|
| 1 | `accepted` | `none` | null | null | 1 |
| 2 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `l1_numerical_closure` | 2 |
| 3 | `blocked` | `missing_required_output_marker` | `prompt_contract` | `missing_required_marker` | 1 |
| 4 | `accepted` | `none` | null | null | 1 |
| 5 | `accepted` | `none` | null | null | 1 |
| 6 | `accepted` | `none` | null | null | 1 |

Chapter 2 prompt-contract diagnostic phases:

| Attempt | Phase | Issue prefix counts | L1 count | Required output missing | Response chars |
|---|---|---|---|---|---|
| 0 | `programmatic_audit` | `programmatic:L1=1` | 1 | 0 | 22 |
| 1 | `programmatic_audit` | `programmatic:L1=2` | 2 | 0 | 22 |

Chapter 3 prompt-contract diagnostic:

- status: `blocked`
- stop reason: `missing_required_output_marker`
- category/subcategory: `prompt_contract` / `missing_required_marker`
- issue prefix: `writer:required_output_gap_missing=1`
- reason count: `missing_required_output_marker=1`
- `max_output_chars=12000`

Chapter 5:

- status: `accepted`
- stop reason: `none`
- category/subcategory: null

## Comparison To Previous Accepted Evidence

Compared with the accepted Chapter 3 policy post-fix bounded live evidence at checkpoint `2f8dce9`:

- Chapter 2 remained the first failed chapter with the same terminal classification: `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.
- The strengthened Chapter 2 prompt contract did not resolve the live sample.
- Chapter 5 moved from a previous residual blocker to `accepted` in this sample, but this is single-sample live metadata only and not a readiness claim.
- Chapter 3 no longer shows the previous accepted state in this sample; it is now blocked on `missing_required_output_marker`. Because Chapter 2 is still first failed, Chapter 3 must be handled as a separate residual after Chapter 2 disposition, not as proof against the Chapter 2 result.

## Disposition

The post-fix bounded live sample is valid fail-closed evidence.

It does not accept the Chapter 2 L1 fix as live-confirmed. Instead, it proves that the exact `004393 / 2025` live sample still reproduces Chapter 2 L1 repair-budget exhaustion after the no-live prompt-contract strengthening.

Accepted classification:

`CHAPTER2_L1_LIVE_PERSISTENT_FAILURE_AFTER_PROMPT_STRENGTHENING`

This should route to a no-code disposition/root-cause planning gate before any further implementation. The next gate should decide whether the residual points to:

- live model noncompliance with prompt contract;
- insufficient structured facts/anchors for the desired numeric closure;
- auditor/repair instruction mismatch still not captured by current no-live tests;
- current one-repair budget being insufficient for live output;
- or a product decision to render a deterministic gap/minimum-verification path rather than repeatedly trying to produce concrete Chapter 2 numeric closure.

## Residuals

| Residual | Status | Next handling |
|---|---|---|
| Chapter 2 L1 still fails live after prompt strengthening | Blocking for LLM completion | No-code disposition/root-cause planning gate |
| Chapter 3 missing required marker in this sample | Residual | Separate disposition after Chapter 2 route is chosen |
| Chapter 5 prior forbidden-phrase blocker | Not reproduced in this sample | Keep as residual until explicitly dispositioned |
| Live content quality | Unproven | Deferred |
| Release/readiness | `NOT_READY` | Preserved |

## Recommended Next Gate

`Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

Purpose:

- Do not implement immediately.
- Reconcile no-live implementation acceptance with live persistent failure.
- Decide whether the next action is additional no-live diagnostic evidence, deterministic gap rendering, repair budget calibration planning, or a narrower code fix plan.
- Preserve `NOT_READY`.

## Final Verdict

`VERDICT: LIVE_FAIL_CLOSED_CHAPTER2_L1_STILL_REPRODUCES_NOT_READY`
