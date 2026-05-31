# MVP Real Provider Smoke Independent Body Matrix Evidence

## Gate / Role

- Gate: `MVP real provider smoke acceptance rerun with independent body chapter matrix`
- Role: Gateflow controller diagnostic evidence, not implementation.
- Date: 2026-05-31.
- Scope: validation and diagnosis only; no runtime, prompt, audit-rule, quality-gate, score, golden, Host/Agent/dayu, PR, push, merge or release change.

## Direct Inputs

- Command under acceptance:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

- CLI raw files:
  - `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/real-provider-cli.stdout`
  - `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/real-provider-cli.stderr`
  - `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/real-provider-cli.exit`
- Service-level safe diagnostic:
  - `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`
  - `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.exit`

No artifact stores API key, Authorization header, full prompt, draft markdown, raw provider response or raw audit response.

## Validation Summary

| Check | Result |
|---|---|
| deterministic analyze `006597 / 2024` | PASS, exit `0` |
| deterministic checklist `006597 / 2024` | PASS, exit `0` |
| missing-config `--use-llm` | PASS, exit `1`, stdout empty, clear missing-provider error |
| real provider CLI smoke | BLOCKED, exit `1`, stdout empty |
| deterministic fallback observed | `false` |
| secret leak scan over gate report files | PASS |

## CLI Smoke Result

- Exit code: `1`
- Stdout bytes: `0`
- Stderr bytes: `1057`
- CLI stderr summary:
  - `orchestration_status=partial`
  - `final_assembly_status=incomplete`
  - `first_failed_chapter_id=3`
  - `first_failed_status=failed`
  - `first_failed_stop_reason=llm_timeout`
  - `first_failed_category=llm_timeout`
  - `first_failed_runtime_operation=auditor`
  - `first_failed_provider_attempts=2/2`
  - `first_failed_provider_runtime_category=timeout`
  - `first_failed_elapsed_ms_max=60028`
  - `first_failed_prompt_chars=4277`
  - `first_failed_approx_prompt_tokens=1070`
  - `chapter_matrix=1:accepted/none/unknown/unknown;2:accepted/none/unknown/unknown;3:failed/llm_timeout/llm_timeout/unknown;4:failed/llm_timeout/llm_timeout/unknown;5:failed/llm_timeout/llm_timeout/unknown;6:failed/llm_timeout/llm_timeout/unknown`

CLI smoke proves the independent body chapter gate changed behavior: chapters 2-6 are no longer synthetic `dependency_missing`; all requested body chapter rows are visible.

## Service Diagnostic Result

The service-level diagnostic rerun was used because CLI stderr intentionally emits only a compact safe summary and does not include full per-chapter provider attempt detail.

- Diagnostic exit code: `0`
- `orchestration_status`: `partial`
- `final_assembly_status`: `incomplete`
- `report_markdown_present`: `false`
- `deterministic_fallback_observed`: `false`
- `generated_chapter_ids`: `[1, 2, 3, 4, 5, 6]`
- `skipped_chapter_ids`: `[]`
- `accepted_chapter_ids`: `[4]`

## Per-Chapter Matrix

| Chapter | Write status | Audit status | Repair attempts/actions | Stop reason | Failure category | Failure subcategory | Provider operation / attempts | Max elapsed ms | Prompt chars / approx tokens |
|---|---|---|---|---|---|---|---|---:|---|
| 1 | none completed | none | `0` / none | `llm_timeout` | `llm_timeout` | `null` | writer `2/2`, timeout | `60081` | system `87`, user `8719`, approx `2202` |
| 2 | none completed | none | `0` / none | `llm_timeout` | `llm_timeout` | `null` | writer `2/2`, timeout | `60080` | system `87`, user `104256`, approx `26086` |
| 3 | drafted | none completed | `0` / none | `llm_timeout` | `llm_timeout` | `null` | auditor `2/2`, timeout | `60060` | system `54`, user `4131`, approx `1047` |
| 4 | drafted | accepted | `0` / none | `none` | `null` | `null` | no runtime timeout diagnostic recorded | n/a | n/a |
| 5 | drafted | none completed | `0` / none | `llm_timeout` | `llm_timeout` | `null` | auditor `2/2`, timeout | `60030` | system `54`, user `3878`, approx `983` |
| 6 | none completed | none | `0` / none | `llm_timeout` | `llm_timeout` | `null` | writer `2/2`, timeout | `60087` | system `87`, user `116223`, approx `29078` |

Notes:

- `attempt_count=0` for chapters 1, 2 and 6 means the provider timed out in writer before a `ChapterAttemptRecord` could be created.
- `attempt_count=1` with `audit_status=null` for chapters 3 and 5 means writer drafted, then auditor timed out before audit result.
- Chapter 4 accepted in the service diagnostic rerun; the CLI smoke and service diagnostic are separate live-provider runs and may differ by chapter outcome.

## Blocker Classification

Primary blocker: `provider_runtime_timeout`.

Rationale:

- Both CLI and service diagnostic reached the real provider and returned no deterministic fallback.
- Provider auth/config is not the blocker.
- Failure rows are explicit `llm_timeout` with provider runtime category `timeout`.
- The independent body matrix is complete enough to prove chapters 1-6 are no longer hidden behind synthetic dependency skips.
- The largest observed writer prompt sizes are very high for chapters 2 and 6: approximately `26086` and `29078` prompt tokens by the current heuristic. That is direct runtime-cost evidence, not a root-cause assumption.

## Acceptance Decision

Gate B smoke is **blocked**, not pass:

- No complete 0-7 report was produced.
- No evidence anchors or chapter audit status are available in a final report because `final_assembly_status=incomplete`.
- `report_markdown_present=false`.
- `deterministic_fallback_observed=false`, which is correct fail-closed behavior.
- Partial body chapter matrix is diagnostic only and was not treated as accepted report.

## Next Smallest Entry Point

`MVP provider runtime budget and prompt-cost calibration gate`

Minimum scope:

- Do not revisit provider config/auth.
- Do not relax evidence, ITEM_RULE, candidate facet, transaction advice, E2 deferred or audit safety boundaries.
- Use the existing safe diagnostics to decide whether to:
  - reduce extreme writer prompt cost for chapters 2 and 6;
  - add bounded per-chapter runtime budget controls;
  - add progress/phase observability for long real-provider smoke;
  - preserve final assembly fail-closed behavior.

No code fix was made in this gate.
