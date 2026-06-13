# Provider/LLM Chapter 3 Required-output Policy Post-fix Bounded Live Re-evidence

Date: 2026-06-14

Role: evidence worker / controller-recorded

Gate: `Provider/LLM Chapter 3 Required-output Policy Post-fix Bounded Live Re-evidence Gate`

Verdict: `LIVE_FAIL_CLOSED_CHAPTER3_ACCEPTED_NEW_BLOCKERS_NOT_READY`

## Scope

This gate verifies the accepted no-live policy implementation checkpoint `1b9cd00` against one bounded live Route C sample:

- fund code: `004393`
- report year: `2025`
- path: explicit `--use-llm`
- sample count: one

The only accepted purpose is to determine whether Chapter 3 item 01 now degrades to an evidence gap without reproducing the provider-before `ValueError` / `code_bug` failure.

## Non-goals

- No release-ready, MVP-ready or LLM path ready claim.
- No source acquisition policy change.
- No Eastmoney, CNINFO, fund-company or other fallback reintroduction.
- No provider default, repair budget, annual-period LLM route or Docling change.
- No source/PDF/body/provider payload/final report body read.
- No PR, push, merge or external-state action.

Release/readiness remains `NOT_READY`.

## Inputs

| Input | Use |
|---|---|
| `AGENTS.md` | Rule truth and source/readiness boundaries. |
| `docs/current-startup-packet.md` | Current gate and no-fallback/readiness guardrails. |
| `docs/implementation-control.md` | Control truth and accepted checkpoint chain. |
| `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-controller-judgment-20260614.md` | Accepted no-live implementation checkpoint `1b9cd00`. |

## Command

Authorized live command:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Result:

| Field | Value |
|---|---|
| Exit code | `1` |
| Runtime | `251843 ms` |
| Artifact root | `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/` |
| Manifest | `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/manifest.json` |
| Summary | `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json` |

The command failed closed with incomplete final assembly. This is valid bounded live evidence, not completion/readiness evidence.

## Safe Metadata Reviewed

Only safe runtime metadata was read:

- `manifest.json`
- `summary.json`
- `chapters/chapter-02.json`
- `chapters/chapter-03.json`
- `chapters/chapter-05.json`

The following files were not read as evidence:

- writer Markdown
- auditor feedback Markdown
- repair Markdown
- raw prompts
- raw provider payloads
- source/PDF/cache body
- final report body

## Accepted Live Facts

| Fact | Evidence |
|---|---|
| Route C live command did not complete final assembly. | `orchestration_status=partial`; `final_assembly_status=incomplete`; exit code `1`. |
| Chapter 3 is no longer the current failed chapter. | `summary.json` chapter matrix: Chapter 3 `status=accepted`, `stop_reason=none`; `chapters/chapter-03.json` has `status=accepted`, `issues=[]`. |
| The prior Chapter 3 item 01 provider-before `ValueError` / `code_bug` is not reproduced in this run. | Chapter 3 accepted; no Chapter 3 failure category/subcategory appears in safe metadata. |
| Current first failed chapter is Chapter 2. | `summary.json.first_failed.chapter_id=2`; category `prompt_contract`; subcategory `l1_numerical_closure`; stop reason `repair_budget_exhausted`. |
| Chapter 2 failure remains fail-closed. | `chapters/chapter-02.json`: `status=failed`, `stop_reason=repair_budget_exhausted`, issues `programmatic:L1`. |
| Chapter 5 is an additional blocked chapter after Chapter 2. | `chapters/chapter-05.json`: `status=blocked`, `stop_reason=llm_contract_violation`, category `audit_parse`, subcategory `forbidden_phrase`. |
| Final report assembly correctly remains blocked. | `summary.json.final_assembly_issues` includes Chapter 2 missing accepted draft/conclusion, Chapter 5 missing accepted draft/conclusion and Chapter 7 readiness blocked. |
| Redaction was applied. | `summary.json`: `redaction_applied=true`, `redaction_count=1`. |

## Chapter Matrix

| Chapter | Status | Stop reason | Category | Subcategory | Attempts |
|---|---:|---|---|---|---:|
| 1 | `accepted` | `none` |  |  | 1 |
| 2 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `l1_numerical_closure` | 2 |
| 3 | `accepted` | `none` |  |  | 1 |
| 4 | `accepted` | `none` |  |  | 1 |
| 5 | `blocked` | `llm_contract_violation` | `audit_parse` | `forbidden_phrase` | 2 |
| 6 | `accepted` | `none` |  |  | 1 |

## Disposition

| Item | Disposition | Basis |
|---|---|---|
| Chapter 3 required-output policy implementation | `CONFIRMED_BY_SINGLE_BOUNDED_LIVE_SAMPLE` | Chapter 3 accepted in safe live metadata after checkpoint `1b9cd00`. |
| Provider/LLM full completion | `REJECT_AS_UNPROVEN` | Exit code `1`; final assembly incomplete. |
| Release/readiness | `NOT_READY` | This gate is single-sample fail-closed evidence only. |
| Chapter 2 L1 numerical closure | `RESIDUAL_BLOCKER` | First failed chapter remains Chapter 2 `prompt_contract/l1_numerical_closure`. |
| Chapter 5 forbidden phrase | `RESIDUAL_BLOCKER` | Additional blocked chapter after Chapter 2. |
| Source/fallback policy | `UNCHANGED` | No source expansion or fallback policy change was made; EID single-source/no-fallback remains current control truth. |

## Residuals

| Residual | Owner | Next gate |
|---|---|---|
| Chapter 2 `prompt_contract/l1_numerical_closure` still fails after repair budget exhaustion in live Route C. | Agent/Fund chapter contract owner + controller | `Provider/LLM Chapter 2 L1 Numerical Closure Live-regression Disposition Gate` |
| Chapter 5 `audit_parse/forbidden_phrase` blocks later in the same live run. | Agent/Fund writer/audit policy owner + controller | Deferred until Chapter 2 blocker is dispositioned or a separate Chapter 5 gate is opened. |
| Provider/LLM full report completion remains unproven. | Provider/LLM route owner + controller | Future bounded live evidence after blockers close. |
| Release/readiness remains unproven. | Release owner + controller | Release-readiness gate only after bounded live completion evidence and residual disposition. |

## Validation

Commands run in this gate:

```bash
git diff --check
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
find reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab -maxdepth 3 -type f | sort
jq safe metadata reads for manifest.json, summary.json, chapters/chapter-02.json, chapters/chapter-03.json and chapters/chapter-05.json
```

`git diff --check` passed before the live command. The live command exited `1` fail-closed.

## Final Verdict

`LIVE_FAIL_CLOSED_CHAPTER3_ACCEPTED_NEW_BLOCKERS_NOT_READY`

Next entry recommendation:

```text
Provider/LLM Chapter 2 L1 Numerical Closure Live-regression Disposition Gate
```

This next gate should decide whether the current Chapter 2 live regression is already covered by accepted Chapter 2 evidence, requires no-live diagnostic evidence, or requires a narrow no-live fix plan. It must not claim readiness.
