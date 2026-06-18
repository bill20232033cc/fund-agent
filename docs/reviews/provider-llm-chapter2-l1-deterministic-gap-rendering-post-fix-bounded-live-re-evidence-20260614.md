# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Post-fix Bounded Live Re-evidence

Date: 2026-06-14

Role: AgentController live evidence executor

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Post-fix Bounded Live Re-evidence Gate`

Verdict: `LIVE_CHAPTER2_ACCEPTED_NEW_BLOCKER_CHAPTER6_INVALID_MARKER_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact records one bounded live/provider re-evidence command for exact `004393 / 2025` after the accepted no-live Chapter 2 deterministic gap rendering implementation at checkpoint `a4726da`.

The gate only evaluates safe runtime metadata. It does not claim release readiness, MVP readiness, LLM path readiness, LLM content quality, provider quality or broader sample acceptance.

EID source policy remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Command

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Exit code: `1`

Stdout: empty

Stderr safe diagnostic:

```text
LLM incomplete diagnostic artifacts: reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/manifest.json
LLM 分析未完成：orchestration_status=partial, final_assembly_status=incomplete, issues=orchestration_not_accepted, chapter_not_accepted, missing_accepted_draft, missing_accepted_conclusion, chapter7_readiness_blocked, first_failed_chapter_id=6, first_failed_status=blocked, first_failed_stop_reason=llm_contract_violation, first_failed_category=prompt_contract, first_failed_subcategory=invalid_marker, first_failed_runtime_operation=writer, first_failed_provider_attempts=0/unknown, first_failed_provider_runtime_category=unknown, first_failed_elapsed_ms_max=unknown, first_failed_prompt_chars=unknown, first_failed_approx_prompt_tokens=unknown, first_failed_timeout_root_cause_hint=unknown, first_failed_max_output_chars=unknown, chapter_matrix=1:accepted/none/unknown/unknown;2:accepted/none/unknown/l1_numerical_closure;3:accepted/none/unknown/unknown;4:accepted/none/unknown/unknown;5:accepted/none/unknown/unknown;6:blocked/llm_contract_violation/prompt_contract/invalid_marker; LLM Host run 未完成：run_id=host_run_8bbf668bcf7644ec; status=failed; timeout_classification=none; cancel_reason=none; error_type=_LLMIncompleteHostRunError; elapsed_ms=241702
```

## 3. Artifact Boundary

Metadata files inspected:

- `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/manifest.json`
- `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/summary.json`
- `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/chapters/chapter-06.json`

Explicitly not read:

- writer markdown bodies
- auditor feedback markdown bodies
- repair markdown bodies
- prompt bodies
- provider request/response payloads
- PDF/source/cache bodies
- final report body

The artifact directory contains writer/auditor/repair markdown files, but they were not opened for this evidence.

## 4. Safe Metadata Facts

| Field | Value |
|---|---|
| `fund_code` | `004393` |
| `report_year` | `2025` |
| `run_id` | `host_run_8bbf668bcf7644ec` |
| command exit code | `1` |
| `orchestration_status` | `partial` |
| `final_assembly_status` | `incomplete` |
| first failed chapter | `6` |
| first failed status | `blocked` |
| first failed stop reason | `llm_contract_violation` |
| first failed category | `prompt_contract` |
| first failed subcategory | `invalid_marker` |
| first failed runtime operation | `writer` |
| first failed provider attempts | `0/unknown` from stderr; `0` in summary runtime diagnostics for first failed |
| host status | `failed` from stderr |
| timeout classification | `none` from stderr |
| cancel reason | `none` from stderr |
| elapsed | `241702 ms` from stderr |

## 5. Chapter Matrix

| Chapter | Status | Stop reason | Failure category | Failure subcategory | Attempt count | Accepted draft/conclusion in summary |
|---|---|---|---|---|---:|---|
| 1 | `accepted` | `none` | null | null | 1 | yes / yes |
| 2 | `accepted` | `none` | null | `l1_numerical_closure` residual metadata | 2 | yes / yes |
| 3 | `accepted` | `none` | null | null | 1 | yes / yes |
| 4 | `accepted` | `none` | null | null | 1 | yes / yes |
| 5 | `accepted` | `none` | null | null | 1 | yes / yes |
| 6 | `blocked` | `llm_contract_violation` | `prompt_contract` | `invalid_marker` | 1 | no / no |

Chapter 2 prompt-contract diagnostics still record a prior attempt-level `l1_numerical_closure` phase, but the chapter terminal status is `accepted` with `stop_reason=none`. Therefore the post-fix live evidence no longer has Chapter 2 as the first failed blocker.

## 6. Final Assembly Issues

Accepted safe metadata final assembly blockers:

- `final_assembly:orchestration_not_accepted`
- `final_assembly:chapter_6:not_accepted`
- `final_assembly:chapter_6:missing_accepted_draft`
- `final_assembly:chapter_6:missing_accepted_conclusion`
- `final_assembly:chapter_7:readiness_blocked`

The final assembly remains incomplete because Chapter 6 is blocked and Chapter 7 requires chapters 1-6 accepted with accepted draft/conclusion.

## 7. Disposition

| Question | Disposition |
|---|---|
| Did the exact `004393 / 2025` live sample still first-fail Chapter 2 L1 after deterministic gap rendering implementation? | No. Chapter 2 is accepted in safe metadata. |
| Did the command complete a full LLM report? | No. Exit code `1`; orchestration is `partial`; final assembly is `incomplete`. |
| What is the new first failed blocker? | Chapter 6 `llm_contract_violation` / `prompt_contract` / `invalid_marker`. |
| Does this prove LLM path readiness? | No. `NOT_READY` preserved. |
| Does this change EID source policy? | No. EID remains single-source/no-fallback. |

## 8. Residuals

| Residual | Disposition |
|---|---|
| Chapter 6 invalid marker blocks completion. | New primary live blocker candidate; needs separate disposition/root-cause gate. |
| Chapter 2 accepted only as single exact live sample. | Do not generalize to broader live stability. |
| Chapter 2 still has attempt-level L1 diagnostic metadata before terminal acceptance. | Accepted as non-terminal metadata; can be monitored in future evidence. |
| Final assembly incomplete. | `NOT_READY`; no readiness/release claim. |
| Live LLM content quality was not reviewed. | Deferred. |

## 9. Verdict

`VERDICT: LIVE_CHAPTER2_ACCEPTED_NEW_BLOCKER_CHAPTER6_INVALID_MARKER_NOT_READY`

Recommended next gate:

```text
Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate
```
