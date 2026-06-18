# Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence Gate`.

Accepted implementation checkpoint:

- `6cd5ac5`
- `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- Verdict: `ACCEPT_IMPLEMENTATION_NOT_READY`

This evidence tests the exact `004393 / 2025` Route C live/provider path after the no-live item 01 template fix. It does not claim release readiness, MVP readiness, LLM path readiness, content quality, provider acceptance, PR readiness or source-policy change.

## Guardrails

- EID remains the only operational annual-report source path.
- No Eastmoney, fund-company website, CNINFO, source fallback or provider fallback was introduced.
- No source/PDF/cache body was read.
- No chapter writer Markdown, auditor feedback Markdown, raw prompt, provider payload or source document body was read.
- Only safe runtime metadata was read from:
  - `manifest.json`
  - `summary.json`
  - `chapters/chapter-02.json`
  - `chapters/chapter-03.json`
- Release/readiness remains `NOT_READY`.

## Preflight

Commands run before live execution:

```bash
git status --branch --short
git status --short
git diff --check
pgrep -x fund-analysis
pgrep -x uv
find reports/llm-runs -maxdepth 1 -type d -name '004393-2025-*' -print | tail -n 10
```

Preflight facts:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`, ahead of origin.
- Existing unrelated tracked diffs remained in `AGENTS.md`, `README.md`, `docs/design.md`; they were not staged or modified by this gate.
- Existing untracked historical/review/report residue remained visible and was not cleaned, moved, deleted, archived, staged or promoted.
- `git diff --check` passed with no output.
- No active `fund-analysis` process was found.
- No active `uv` process was found.
- Existing `004393-2025-*` LLM run artifacts before this command were historical and not treated as current evidence.

## Live Command

Command:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Exit code: `1`.

CLI output:

```text
LLM incomplete diagnostic artifacts: reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/manifest.json
LLM 分析未完成：orchestration_status=partial, final_assembly_status=incomplete, issues=orchestration_not_accepted, chapter_not_accepted, missing_accepted_draft, missing_accepted_conclusion, chapter_not_accepted, missing_accepted_draft, missing_accepted_conclusion, chapter7_readiness_blocked, first_failed_chapter_id=2, first_failed_status=failed, first_failed_stop_reason=repair_budget_exhausted, first_failed_category=prompt_contract, first_failed_subcategory=l1_numerical_closure, first_failed_runtime_operation=auditor, first_failed_provider_attempts=0/unknown, first_failed_provider_runtime_category=unknown, first_failed_elapsed_ms_max=unknown, first_failed_prompt_chars=unknown, first_failed_approx_prompt_tokens=unknown, first_failed_timeout_root_cause_hint=unknown, first_failed_max_output_chars=unknown, chapter_matrix=1:accepted/none/unknown/unknown;2:failed/repair_budget_exhausted/prompt_contract/l1_numerical_closure;3:blocked/missing_required_facts/fact_gap/unknown;4:accepted/none/unknown/unknown;5:accepted/none/unknown/unknown;6:accepted/none/unknown/unknown; LLM Host run 未完成：run_id=host_run_3870105453bd4f26; status=failed; timeout_classification=none; cancel_reason=none; error_type=_LLMIncompleteHostRunError; elapsed_ms=285604
```

## Runtime Artifact

Manifest path:

```text
reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/manifest.json
```

Safe metadata facts from `manifest.json`:

- `artifact_kind`: `llm_incomplete_run_diagnostic`
- `schema_version`: `llm_incomplete_run_artifact_manifest.v1`
- `fund_code`: `004393`
- `report_year`: `2025`
- `run_id`: `host_run_3870105453bd4f26`
- `orchestration_status`: `partial`
- `final_assembly_status`: `incomplete`
- `chapter_count`: `6`
- `summary_file`: `summary.json`
- `redaction_policy.policy_id`: `llm_incomplete_artifact_redaction.v1`
- `retention_policy`: `manual_local_cleanup`
- `trigger`: `use_llm_incomplete`
- `created_at`: `2026-06-13T19:06:05.370012Z`

## Accepted Runtime Facts

Safe metadata facts from `summary.json`:

- `orchestration_status`: `partial`
- `final_assembly_status`: `incomplete`
- first failed chapter:
  - `chapter_id`: `2`
  - `status`: `failed`
  - `stop_reason`: `repair_budget_exhausted`
  - `failure_category`: `prompt_contract`
  - `failure_subcategory`: `l1_numerical_closure`
  - `attempt_count`: `2`
- chapter matrix:
  - Chapter 1: `accepted`, `attempt_count=2`
  - Chapter 2: `failed`, `repair_budget_exhausted`, `prompt_contract`, `l1_numerical_closure`, `attempt_count=2`
  - Chapter 3: `blocked`, `missing_required_facts`, `fact_gap`, `attempt_count=1`
  - Chapter 4: `accepted`, `attempt_count=1`
  - Chapter 5: `accepted`, `attempt_count=1`
  - Chapter 6: `accepted`, `attempt_count=1`
- final assembly blocked because orchestration was not accepted, Chapter 2 was failed, Chapter 3 was blocked, and Chapter 7 requires Chapters 1-6 accepted with accepted draft/conclusion.

Safe metadata facts from `chapters/chapter-03.json`:

- `chapter_id`: `3`
- `status`: `blocked`
- `accepted`: `false`
- `stop_reason`: `missing_required_facts`
- `failure_category`: `fact_gap`
- `terminal_stop_reason`: `missing_required_facts`
- `terminal_failure_category`: `fact_gap`
- `terminal_issue_class`: `null`
- `diagnostic_consistency_status`: `consistent`
- issue:
  - `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01`

Safe metadata facts from `chapters/chapter-02.json`:

- `chapter_id`: `2`
- `status`: `failed`
- `accepted`: `false`
- `stop_reason`: `repair_budget_exhausted`
- `failure_category`: `prompt_contract`
- `failure_subcategory`: `l1_numerical_closure`
- `terminal_stop_reason`: `repair_budget_exhausted`
- `diagnostic_consistency_status`: `consistent`
- issue:
  - `2:repair_budget_exhausted:programmatic:L1:line:26:02ea024a63`
- prompt-contract diagnostics show `programmatic:L1` with `l1_numerical_closure_count=1` for attempts `0` and `1`.

## Disposition

| Question | Evidence | Disposition |
| --- | --- | --- |
| Did the item 01 fix remove the provider-before `ValueError` / `code_bug` failure for Chapter 3? | Chapter 3 is now `blocked/missing_required_facts/fact_gap`, terminal issue class is `null`, issue is `required_output_block:ch3.required_output.item_01`. | ACCEPTED: the prior Chapter 3 provider-before code-bug is not reproduced by this live run. |
| Did Chapter 3 become accepted? | Chapter 3 remains `blocked`, accepted draft/conclusion are absent. | NOT ACCEPTED: this is expected fail-closed fact-gap behavior, not content acceptance. |
| Did the whole LLM run complete? | Exit code `1`, orchestration `partial`, final assembly `incomplete`. | NOT ACCEPTED: Route C full completion remains unproven. |
| What is the strongest current runtime blocker after the item 01 fix? | First failed chapter is Chapter 2 with `repair_budget_exhausted`, `prompt_contract`, `l1_numerical_closure`. | ACCEPTED as next root-cause candidate. |
| Does this prove release/readiness? | No; final assembly incomplete and Chapter 2/3 not accepted. | REJECT readiness claim; release/readiness remains `NOT_READY`. |

## Residuals

| Residual | Disposition |
| --- | --- |
| Chapter 2 fails with `prompt_contract/l1_numerical_closure` after repair budget exhaustion. | Next no-live root-cause planning/evidence candidate. |
| Chapter 3 is now a fact-gap block, not accepted content. | Accepted fail-closed behavior for this gate; any product decision about rendering a Chapter 3 evidence gap would require a separate template/product policy gate. |
| Runtime diagnostics still include several `max_output_chars=null` / provider runtime metadata unknown fields for auditor/programmatic phases. | Deferred diagnostic-quality residual unless a future gate targets runtime metadata completeness. |
| Full LLM completion, content quality, additional samples and readiness remain unproven. | Preserve `NOT_READY`. |

## Verdict

VERDICT: ACCEPT_LIVE_ITEM01_FIX_CONFIRMED_NEW_BLOCKER_CHAPTER2_NOT_READY

Recommended next gate:

`Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Planning Gate`
