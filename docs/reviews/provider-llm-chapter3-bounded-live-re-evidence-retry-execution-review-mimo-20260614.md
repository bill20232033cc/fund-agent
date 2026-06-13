# Review: Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Execution

Reviewer: AgentMiMo
Date: 2026-06-14
Target: `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-execution-20260614.md`

## Verdict

**PASS_WITH_FINDINGS**

## Findings

### F1 — Retry did not actually execute; artifact is pre-fix evidence reuse [SEVERITY: HIGH]

The preflight section explicitly states:

> "No second live command was run before or during this retry gate."

Yet the execution result section presents `exit_code=1`, `stderr_lines=2`, and the full error diagnostic as if they were from this retry. The inspected artifact `created_at` is `2026-06-13T17:35:13.011460Z` (filesystem `Jun 14 01:35` local). The Chapter 3 no-live fix was accepted at checkpoint `76df5ba` before this retry gate opened. Therefore the inspected artifact reflects pre-fix behavior, not post-fix behavior.

The artifact's own accepted fact "Chapter 3 failed with `llm_exception` / `code_bug` / `ValueError`" (line 237) is accepted as pre-fix evidence only. It cannot serve as post-fix evidence because no command was re-executed under the fixed code.

**Impact**: The artifact cannot prove or disprove whether the fix at `76df5ba` resolves the Chapter 3 `ValueError`. A Post-retry Ready-state Disposition Gate is premature; a no-live code-bug root-cause/fix verification gate is required first.

### F2 — Preflight `find` date pattern mismatch with artifact naming [SEVERITY: LOW]

The preflight `find` searched for `004393-2025-20260614*` but the artifact directory name uses UTC date `20260613T173513Z`. The find correctly returned no output because the local-date prefix `20260614` does not match the UTC-date directory name `20260613T...`. This is a naming-convention gap, not a safety failure, but future preflights should account for UTC/local date divergence in artifact directory names.

### F3 — No new 2026-06-14 runtime artifact was created [SEVERITY: MEDIUM]

Because no command was executed, no new runtime artifact with a 2026-06-14 creation timestamp exists. The `reports/llm-runs/` listing confirms only two `004393-2025-*` artifacts, both with `created_at` on 2026-06-13 (UTC). This reinforces F1: the retry produced no new execution evidence.

## Accepted Facts

| Fact | Basis |
|---|---|
| Preflight checks passed: no leftover `fund-analysis`/`uv` process, no visible partial `004393-2025-*` artifact from 2026-06-14 (by local-date pattern), clean `git diff --check`. | Preflight section, consistent with controller judgment preconditions. |
| The exact `004393 / 2025` Route C command matrix is correctly recorded and matches the accepted plan. | Section 4 command boundary matches `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md` exactly. |
| The inspected artifact is a valid `llm_incomplete_run_diagnostic` with `schema_version=llm_incomplete_run_artifact_manifest.v1`. | Manifest metadata, section 6. |
| Chapter 3 `stop_reason=llm_exception`, `category=code_bug`, `terminal_issue_class=ValueError`, `terminal_runtime_operation=writer`, `provider_attempt_count=0` in the inspected artifact. | Summary safe diagnostic metadata, section 8. |
| Runtime safe metadata records `max_output_chars=12000` for the first-failed chapter. | Summary safe diagnostic, section 8. |
| `NOT_READY` is preserved throughout the artifact. | Sections 1, 10, 11, 13. |
| EID single-source/no-fallback is preserved. | Section 9 redaction checks; no `fallback_used=true`, `fallback_enabled=true`, Eastmoney/CNINFO/fund-company access observed. |
| Stop conditions are correctly evaluated. | Section 10; all 16 conditions PASS based on inspected artifact metadata. |

## Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| Provider readiness is proven. | REJECT | No provider attempt occurred; `provider_attempt_count=0`. |
| LLM content quality is accepted. | REJECT | No content body was reviewed or accepted. |
| Release/readiness is improved. | REJECT | `NOT_READY` preserved. |
| Source policy or fallback was authorized. | REJECT | EID single-source/no-fallback remains current policy. |
| 401/403 provider-response classification is closed. | REJECT | No provider response was observed. |
| The retry proves post-fix Chapter 3 behavior. | REJECT | No command was executed during this retry gate; inspected artifact is pre-fix evidence. |

## Redaction and Safe Metadata

Redaction boundary is correctly respected. Only safe scalar/policy metadata was read from `manifest.json` and `summary.json`. No raw prompts, provider payloads, credentials, PDF/cache bodies, source bodies or accepted final report bodies were retained. The `redaction_policy.forbidden_categories` entries for `raw_provider_payloads` and `cookies_and_passwords` are safe policy names, not sensitive values.

## Review Question Answers

**Q1. Did retry follow preflight and exact command boundary?**

Partial. Preflight checks are correct and consistent with controller judgment preconditions. The exact command matrix is correctly recorded. However, no command was actually executed during this retry gate (F1), so the command boundary was recorded but not exercised.

**Q2. Are accepted facts supported: exit 1 fail-closed, Chapter 3 llm_exception/code_bug/ValueError, provider_attempt_count 0, runtime max_output_chars 12000?**

Yes, all are supported by the inspected artifact's safe metadata. However, these facts reflect pre-fix behavior, not post-fix behavior (F1).

**Q3. Are source/fallback/readiness/provider-readiness claims correctly rejected?**

Yes. All overclaims are correctly rejected with appropriate reasoning.

**Q4. Are redaction and safe metadata boundaries respected?**

Yes. Only safe scalar/policy metadata was retained. No sensitive values were accepted.

**Q5. Is next entry Post-retry Ready-state Disposition Gate appropriate?**

No. Because no command was executed during this retry, the artifact cannot serve as post-fix evidence. The next gate should be a **no-live code-bug root-cause/fix verification gate** that either:
- Re-executes the command under the fixed code to produce post-fix evidence, or
- Uses no-live test evidence to verify the fix at `76df5ba` resolves the Chapter 3 `ValueError`.

A Post-retry Ready-state Disposition Gate is only appropriate after post-fix execution evidence exists.

## Required Amendments

1. **AMEND**: The artifact must clearly distinguish between "this retry did not execute a command" and "the execution result shown is from the prior (pre-fix) run." Currently the execution result section presents pre-fix evidence without this qualification, which could mislead readers into thinking the retry produced these results.

2. **AMEND**: The "Interpretation" subsection (section 8) must note that the inspected artifact predates the Chapter 3 fix at `76df5ba` and therefore reflects pre-fix behavior only.

3. **AMEND**: The next entry should route to a no-live code-bug root-cause/fix verification gate, not a Post-retry Ready-state Disposition Gate, because no post-fix execution evidence exists.

## Recommended Controller Disposition

Route to **Provider/LLM Chapter 3 No-live Code-bug Fix Verification Gate** before any ready-state disposition. The verification gate should either:
- Confirm via no-live tests that the fix at `76df5ba` resolves the Chapter 3 `ValueError` (preferred, avoids live execution), or
- If live re-execution is required, authorize a fresh bounded live retry under the fixed code as a separate gate.

The current artifact is valid as pre-fix evidence and preflight checklist evidence, but it is not valid as post-fix behavioral evidence.
