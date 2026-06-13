# Controlled Live Provider/LLM Evidence Execution

Date: 2026-06-13

Gate: `Controlled Live Provider/LLM Evidence Execution Gate`

Status: `EXECUTION_EVIDENCE_WITH_PLAN_BLOCKER_READY_FOR_REVIEW_NOT_READY`

Release/readiness: `NOT_READY`

## Scope

This gate executed the exact controlled live Route C command authorized by the
user after the accepted plan checkpoint `b6853e3`.

This gate did not modify source, tests, runtime behavior, manifest,
golden-answer content, fixtures, README or design truth. It did not run
additional live/provider/LLM/network/PDF/FDR/source/analyze/checklist/
readiness/release/PR commands. It did not push, merge, open PR, mark ready,
cleanup, archive or ignore files.

## Accepted Plan Boundary

| Boundary | Execution result |
|---|---|
| Sample | `004393 / 2025` |
| CLI route | `fund-analysis analyze` |
| LLM mode | explicit opt-in `--use-llm` Route C |
| Quality gate policy | `--dev-override --quality-gate-policy warn` |
| Valuation state | `unavailable` |
| Progress | `--no-llm-progress` |
| Timeout attempts | `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1` |
| Timeout backoff | `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0` |
| Max output chars | `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000` |
| Source policy | EID single-source/no fallback preserved as required; no source fallback claim accepted from this artifact |

## Executed Command

Exactly one live command was run:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

No second live command was run.

## Execution Result

| Field | Value |
|---|---:|
| `start_utc` | `2026-06-13T10:05:33Z` |
| `end_utc` | `2026-06-13T10:08:05Z` |
| `elapsed_seconds` | `152` |
| `exit_code` | `1` |
| `timed_out` | `0` |
| `stdout_lines` | `0` |
| `stdout_bytes` | `0` |
| `stderr_lines` | `2` |
| `stderr_bytes` | `1232` |

The command failed closed with empty stdout. No final accepted report body was
retained in this evidence artifact.

## Capped Stderr Summary

The capped stderr summary contained two safe diagnostic lines:

- incomplete diagnostic artifact path:
  `reports/llm-runs/004393-2025-20260613T100803Z-host_run_36d7fd95448d4c5/manifest.json`
- incomplete LLM analysis summary:
  `orchestration_status=partial`, `final_assembly_status=incomplete`,
  `first_failed_chapter_id=3`, `first_failed_status=failed`,
  `first_failed_stop_reason=llm_exception`,
  `first_failed_category=code_bug`,
  `first_failed_runtime_operation=writer`,
  `first_failed_provider_attempts=0/unknown`,
  `first_failed_provider_runtime_category=unknown`,
  `host_status=failed`,
  `timeout_classification=none`,
  `error_type=_LLMIncompleteHostRunError`,
  `elapsed_ms=148385`.

The chapter matrix in stderr was:

```text
1:accepted/none/unknown/unknown;
2:accepted/none/unknown/unknown;
3:failed/llm_exception/code_bug/unknown;
4:accepted/none/unknown/unknown;
5:accepted/none/unknown/unknown;
6:accepted/none/unknown/unknown
```

## Runtime Artifact Metadata

Only these safe metadata files were read:

- `reports/llm-runs/004393-2025-20260613T100803Z-host_run_36d7fd95448d4c5/manifest.json`
- `reports/llm-runs/004393-2025-20260613T100803Z-host_run_36d7fd95448d4c5/summary.json`

Chapter writer/auditor Markdown files and chapter JSON bodies were not read.
The runtime artifact remains local untracked evidence residue; it is not source
truth, release evidence or readiness proof.

Manifest metadata:

| Field | Value |
|---|---|
| `artifact_kind` | `llm_incomplete_run_diagnostic` |
| `schema_version` | `llm_incomplete_run_artifact_manifest.v1` |
| `cli_command` | `analyze --use-llm` |
| `fund_code` | `004393` |
| `report_year` | `2025` |
| `run_id` | `host_run_36d7fd95448d4c58` |
| `orchestration_status` | `partial` |
| `final_assembly_status` | `incomplete` |
| `trigger` | `use_llm_incomplete` |
| `redaction_policy.policy_id` | `llm_incomplete_artifact_redaction.v1` |
| `redaction_applied` | `false` |
| `redaction_count` | `0` |
| `retention_policy` | `manual_local_cleanup` |

Allowed redaction-policy metadata listed these forbidden categories:

- `secret_headers`
- `provider_credentials`
- `prompt_request_payloads`
- `raw_provider_payloads`
- `cookies_and_passwords`

These are safe policy category names, not retained sensitive values.

## Chapter Matrix

| Chapter | Status | Attempt count | Stop reason | Failure category | Accepted draft | Accepted conclusion |
|---:|---|---:|---|---|---|---|
| 1 | `accepted` | 1 | `none` | - | true | true |
| 2 | `accepted` | 1 | `none` | - | true | true |
| 3 | `failed` | 0 | `llm_exception` | `code_bug` | false | false |
| 4 | `accepted` | 1 | `none` | - | true | true |
| 5 | `accepted` | 1 | `none` | - | true | true |
| 6 | `accepted` | 1 | `none` | - | true | true |

Final assembly blockers:

- `orchestration_not_accepted`
- `chapter_not_accepted` for chapter 3
- `missing_accepted_draft` for chapter 3
- `missing_accepted_conclusion` for chapter 3
- `chapter7_readiness_blocked`

## First Failed Diagnostic

| Field | Value |
|---|---|
| `chapter_id` | `3` |
| `status` | `failed` |
| `stop_reason` | `llm_exception` |
| `category` | `code_bug` |
| `terminal_issue_class` | `ValueError` |
| `provider_attempt_count` | `0` |
| `provider_runtime_categories` | `[]` |
| `timeout_seconds` | `null` |
| `timeout_max_attempts` | `null` |
| `timeout_backoff_seconds` | `null` |
| `max_output_chars` | `null` |
| `diagnostic_consistency_status` | `missing_terminal_runtime_diagnostic` |

Interpretation:

- The command exercised the explicit `--use-llm` Route C path.
- The run did not complete a full accepted report.
- The terminal failure was fail-closed before chapter 3 provider attempt metadata
  was available.
- The exact command forced `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`, but runtime
  safe metadata did not prove `max_output_chars=12000` because the first failed
  chapter stopped with pre-provider `code_bug` metadata where `max_output_chars`
  is `null`.
- This is not provider readiness proof and not LLM content acceptance.

## Redaction And Source-policy Checks

Safe metadata search over `manifest.json` and `summary.json` found only allowed
policy/scalar metadata matches:

- `raw_provider_payloads` inside `redaction_policy.forbidden_categories`;
- `cookies_and_passwords` inside `redaction_policy.forbidden_categories`;
- `approx_prompt_tokens: null`;
- `system_prompt_chars: null`;
- `user_prompt_chars: null`.

No retained sensitive value was accepted from these metadata files.

Search for source fallback/source expansion terms over `manifest.json` and
`summary.json` found only `repair_timeout_fallback_used: null`, which is
provider timeout diagnostic metadata and not annual-report source fallback.

No safe metadata evidence showed:

- `fallback_used=true`;
- `fallback_enabled=true`;
- Eastmoney/CNINFO/fund-company source access;
- direct PDF/cache/source helper access from provider/LLM path.

## Stop-condition Disposition

| Stop condition | Result |
|---|---|
| Command differs from accepted exact command | PASS |
| More than one live command was run | PASS |
| Sample differs from `004393 / 2025` | PASS |
| Provider attempts exceed `1` | PASS; first failed provider attempt count was `0` |
| Provider retry/backoff occurs | PASS; no provider retry was observed in safe first-failed metadata |
| `max_output_chars` metadata is not exactly `12000` | NOT_PROVEN_BY_RUNTIME_METADATA; exact command forced `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`, but first-failed safe metadata is `null` after pre-provider chapter 3 `code_bug`; controller must accept this only as a residual/blocker, not full plan satisfaction |
| Execution timeout exceeded | PASS; elapsed `152s`, no wrapper timeout |
| Deterministic fallback occurs | PASS; stdout empty and final assembly incomplete |
| `--use-llm` absent | PASS |
| `--dev-override` absent with `--quality-gate-policy warn` | PASS |
| `fallback_used=true` | PASS; not observed in safe metadata |
| `fallback_enabled=true` | PASS; not observed in safe metadata |
| Eastmoney/CNINFO/fund-company access appears | PASS; not observed in safe metadata |
| Credential/header/token/raw prompt/raw provider/raw PDF/cache/source body retained | PASS for read safe metadata; chapter bodies were not read |
| Accepted final report body retained | PASS; stdout empty and no report body retained |
| Release/readiness/PR readiness claim | PASS; `NOT_READY` preserved |

## Accepted / Rejected / Residual Facts

| Fact or claim | Disposition | Reason |
|---|---|---|
| Exact accepted live Route C command was executed once. | ACCEPT | Command boundary and execution stats. |
| The command failed closed with exit code `1`. | ACCEPT | stdout empty, host failed/incomplete diagnostic. |
| The run produced local incomplete diagnostic metadata. | ACCEPT | manifest/summary metadata only. |
| Chapters 1, 2, 4, 5 and 6 reached accepted status in this run. | ACCEPT_WITH_SCOPE_LIMIT | Safe chapter matrix metadata only; not content-quality acceptance. |
| Chapter 3 failed with `llm_exception` / `code_bug` / `ValueError`. | ACCEPT | Safe runtime diagnostic metadata. |
| Exact command forced `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`. | ACCEPT_COMMAND_FACT | Command boundary. |
| Runtime safe metadata proves `max_output_chars=12000`. | REJECT | First-failed runtime metadata recorded `max_output_chars=null`. |
| Provider readiness is proven. | REJECT | Run did not complete; first failure has provider attempt count `0`; one sample cannot prove readiness. |
| LLM content quality is accepted. | REJECT | No content body was reviewed or accepted. |
| Release/readiness is accepted. | REJECT | `NOT_READY` preserved. |
| Source policy changed or fallback was authorized. | REJECT | EID single-source/no fallback remains current policy. |
| 401/403 provider-response classification is closed. | REJECT | No 401/403 response classification was observed. |

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Chapter 3 Route C code-bug failure (`ValueError`, `llm_exception`) | Provider/LLM Route C owner + controller | Separate no-live root-cause planning/evidence gate before any repeat live execution. |
| Runtime `max_output_chars=12000` metadata remains unproven in the failed run. | Provider/LLM Route C owner + controller | Treat as tied to the pre-provider chapter 3 failure unless no-live root cause proves otherwise. |
| Live provider/LLM full report completion remains unproven. | Runtime/provider owner | Deferred until code-bug residual is dispositioned. |
| LLM content quality/chapter acceptance remains unaccepted. | Provider/runtime + chapter owners | Separate content-quality gate only after a complete accepted run exists. |
| 401/403 provider-response classification remains unproven. | Provider/runtime owner | Optional no-live mock classification gate. |
| Release/readiness remains unproven. | Release owner/controller | Separate readiness/release gate only. |
| PR/push/merge/mark-ready remains external state. | User/controller | Separate explicit authorization only. |

## Next Entry Recommendation

Recommended next entry:

`Provider/LLM Chapter 3 Code-bug Root-cause Planning Gate`

Purpose: determine, without live execution, why chapter 3 failed before provider
attempt metadata was available and whether a narrow code/test fix is needed.

Do not repeat live provider/LLM execution until the chapter 3 code-bug residual
has a reviewed disposition.

If controller accepts this evidence, synchronize `docs/current-startup-packet.md`
and `docs/implementation-control.md` to this no-live Chapter 3 root-cause
planning next entry while preserving `NOT_READY`, EID single-source/no fallback
and no-repeat-live execution.
