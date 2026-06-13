# Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Execution — DS Review

Date: 2026-06-14

Reviewer: AgentDS

Target: `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-execution-20260614.md`

Gate: `Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Gate`

Release/readiness: `NOT_READY`

## 1. Scope and Constraints

This review covers the five review questions assigned to DS for the bounded live retry execution artifact. It does not read chapter body Markdown/JSON, raw prompts, provider payloads, credentials, raw PDF/cache/source bodies or accepted final report bodies. It does not modify source, tests, control docs or design docs.

## 2. Review Questions

### RQ1: Did retry follow preflight and exact command boundary?

**Verdict: PASS**

Preflight (§3):

| Check | Result | Assessment |
|---|---|---|
| `pgrep -x fund-analysis` | exit `1` | No leftover process. |
| `pgrep -x uv` | exit `1` | No leftover process. |
| `find reports/llm-runs -maxdepth 1 -type d -name '004393-2025-20260614*'` | no output | No visible partial 2026-06-14 local-date runtime artifact. |
| `git diff --check` | exit `0`; no output | Working tree clean. |

These checks match the preflight requirements from the worker-channel controller judgment (`docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-worker-channel-controller-judgment-20260614.md` §5): verify no leftover `fund-analysis`/`uv` process, no visible partial `004393-2025-*` runtime artifact from 2026-06-14, and clean `git diff --check`.

The `find` check uses `-maxdepth 1` and the narrow glob `004393-2025-20260614*`. The controller judgment requirement says "no visible partial `004393-2025-*` runtime artifact from 2026-06-14". The glob is time-scoped to the current date rather than all possible `004393-2025-*` artifacts. This is a reasonable bounded check: the concern was new partial artifacts from the current date, and existing prior-date artifacts are known accepted residue. No material gap.

Command boundary (§4): the executed command matches the exact authorized command from `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md` §4 line 74, character for character. All env prefix values match: timeouts at 60s, max attempts 1, backoff 0, max output chars 12000. CLI args match: `004393`, `--report-year 2025`, `--use-llm`, `--dev-override`, `--quality-gate-policy warn`, `--valuation-state unavailable`, `--no-llm-progress`.

Stop-condition disposition (§10): all 17 stop conditions recorded PASS. No second live command was run. Sample identity is exact `004393 / 2025`.

One observation: the runtime artifact path inspected in §6 is `004393-2025-20260613T173513Z-*`. The retry ran on 2026-06-14 but the artifact directory uses `20260613` in its name. This is consistent with UTC timestamp naming (2026-06-14 ~01:35 local China time ≈ 2026-06-13 17:35 UTC). No finding against correctness; the artifact could note the timezone basis for completeness but this does not affect evidence validity.

### RQ2: Are accepted facts supported?

**Verdict: PASS**

Four fact claims are verified:

| Fact | Source in target | Evidence type | Assessment |
|---|---|---|---|
| exit `1` fail-closed | §5: `exit_code: 1`, stdout empty, host failed | Direct command observation | Supported. |
| Chapter 3 `llm_exception` / `code_bug` / `ValueError` | §5 safe stderr: `first_failed_stop_reason=llm_exception`, `first_failed_category=code_bug`; §8: `terminal_issue_class=ValueError` | Safe runtime diagnostic from `summary.json` | Supported. |
| `provider_attempt_count` = `0` | §8: `provider_attempt_count: 0`, `provider_runtime_categories: []` | Safe runtime diagnostic from `summary.json` | Supported. |
| runtime `max_output_chars` = `12000` | §8: `max_output_chars: 12000`; §5 safe stderr: `first_failed_max_output_chars=12000` | Safe runtime diagnostic from `summary.json`; also in stderr summary | Supported. This closes the prior blocker residual where runtime metadata `max_output_chars=null` was observed before the no-live fix at `76df5ba`. |

The safe stderr summary (§5) and safe runtime diagnostic (§8) are internally consistent: both show Chapter 3 failed with the same stop reason, category, provider attempt count, and max_output_chars. The chapter matrix (§7) is also consistent: Chapter 3 `failed` with 0 attempts.

The artifact correctly limits Chapter 1/2/4/5/6 acceptance to "safe chapter matrix metadata only; not content-quality acceptance" (§11 `ACCEPT_WITH_SCOPE_LIMIT`). This is appropriate given only `manifest.json` and `summary.json` were read.

### RQ3: Are source/fallback/readiness/provider-readiness claims correctly rejected?

**Verdict: PASS**

The artifact explicitly rejects all five overclaim categories (§11):

| Rejected claim | Disposition | Assessment |
|---|---|---|
| Provider readiness is proven | REJECT | Correct. Run did not complete; first failure has provider attempt count 0. |
| LLM content quality is accepted | REJECT | Correct. No content body was reviewed or accepted. |
| Release/readiness is accepted | REJECT | Correct. `NOT_READY` preserved. |
| Source policy changed or fallback authorized | REJECT | Correct. EID single-source/no fallback remains current policy. |
| 401/403 provider-response classification is closed | REJECT | Correct. No provider response classification was observed. |

The artifact's posture is consistent throughout:
- §1: "not provider readiness proof, LLM content quality acceptance, release readiness or PR readiness"
- §9: safe metadata search found no `fallback_used=true`, `fallback_enabled=true`, Eastmoney/CNINFO/fund-company source access, or direct PDF/cache/source helper access
- §13: verdict `LIVE_FAIL_CLOSED_BOUNDED_NOT_READY`

The guardrail language in §9 correctly distinguishes between safe policy/scalar metadata terms (which are allowed in redaction policy descriptions and negative assertions) and actual source access or fallback invocation (which would be violations). No unexpected source access was observed.

### RQ4: Are redaction and safe metadata boundaries respected?

**Verdict: PASS**

The artifact respects all redaction boundaries from the plan:

- §2: explicit declaration that no raw prompt, provider request/response body, credential, header, token, raw report body, chapter content body, raw source body or accepted final report body was read or retained.
- §6: only `manifest.json` and `summary.json` were read. Chapter writer/auditor Markdown files and chapter JSON bodies were not read.
- §9: the safe metadata search enumerated only allowed policy/scalar fields:
  - `raw_provider_payloads` and `cookies_and_passwords` as `redaction_policy.forbidden_categories` names (policy metadata, not actual values)
  - `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens` as safe scalar/null fields
  - `repair_timeout_fallback_used: null` as provider timeout diagnostic (not annual-report source fallback)
- §9: "No retained sensitive value was accepted from these metadata files."
- §5 safe stderr summary: contains only diagnostic scalar fields and paths. The incomplete diagnostic artifact path is a safe filesystem path, not body content. The LLM analysis summary fields are all scalar status/metadata.

The artifact correctly applies the plan's distinction (§9 of the plan) between:
- Sensitive value-bearing fields (API keys, raw prompts, raw provider payloads, raw PDF/cache/source bodies) — none retained
- Safe scalar/policy metadata (`redaction_policy.forbidden_categories`, `system_prompt_chars`, `max_output_chars`, provider/runtime category names, timeout scalars) — allowed

No `SENSITIVE_DATA_LEAK` or `UNEXPECTED_SOURCE_ACCESS` condition was triggered.

### RQ5: Is next entry Post-retry Ready-state Disposition Gate appropriate, or should it route to another no-live code-bug root-cause/fix gate?

**Verdict: PASS_WITH_FINDINGS**

The proposed NEXT_ENTRY is `Provider/LLM Chapter 3 Post-retry Ready-state Disposition Gate`.

This is a reasonable immediate next step. Rationale:

1. The retry gate's scope was specifically to re-run the bounded live command after the permission approval blocker was resolved. That scope is fulfilled: the command was executed, evidence was collected, and the result is recorded.

2. A ready-state disposition gate is the standard mechanism for closing a gate and routing the next action. It allows the controller to assess what changed (max_output_chars metadata gap resolved), what didn't change (Chapter 3 code_bug persists), and what the appropriate next gate should be.

3. The disposition gate does not inherently close the Chapter 3 code_bug issue — it can (and should) route to further action.

**Finding F1 (MEDIUM): Next entry rationale underspecified.**

The artifact does not address the relationship between the proposed disposition gate and the unresolved Chapter 3 code_bug. Specifically:

- The no-live fix at `76df5ba` addressed diagnostic propagation (adding `_exception_task()` guard and `max_output_chars` lineage) but did not fix the underlying `ValueError`.
- The root-cause evidence at `4a7c191` classified the strongest finding as `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`, which the fix partially addressed (diagnostic propagation improved) but the `ValueError` root cause remains open.
- Two live runs now confirm the same failure: Chapter 3 `llm_exception` / `code_bug` / `ValueError` at provider attempt count 0.

The artifact's residuals table (§12) lists "Chapter 3 Route C code-bug failure after no-live fix" with next handling "Separate no-live root-cause evidence/fix gate; live retry no longer blocked by output-cap metadata proof." This is correct. But the NEXT_ENTRY field (§13) is the disposition gate — not the root-cause gate. The artifact should explain that the disposition gate is the routing mechanism and that one of its expected outcomes is to sequence the root-cause/fix gate.

**Recommended amendment:** Add a sentence or brief note in §13 clarifying that the disposition gate is expected to route to a no-live Chapter 3 code-bug root-cause investigation/fix gate as a primary follow-up, given the diagnostic-only fix at `76df5ba` did not resolve the underlying ValueError and two live runs now confirm the same pre-provider failure.

## 3. Additional Findings

**Finding F2 (LOW): Artifact timestamp is explainable but not contextualized.**

§6 reads runtime metadata from `004393-2025-20260613T173513Z-*`. The retry ran on 2026-06-14. The manifest `created_at` is `2026-06-13T17:35:13.011460Z`. The `20260613` in the path and the UTC `created_at` are self-consistent with each other but the artifact does not explain the date offset relative to the 2026-06-14 execution date. This is not a correctness issue (UTC vs local time explains it), but readers unfamiliar with the timezone convention may question whether the metadata belongs to this retry or a prior run. A brief note in §6 would improve traceability.

No other findings.

## 4. Accepted Facts

| # | Fact | Basis |
|---|---|---|
| AF1 | Preflight checks passed: no leftover process, no visible 2026-06-14 partial artifact, clean `git diff --check`. | §3 preflight results. |
| AF2 | Exact authorized Route C command was executed once for `004393 / 2025`. | §4 command boundary; §10 stop conditions. |
| AF3 | Command failed closed with exit `1`, empty stdout, incomplete final assembly. | §5 execution result. |
| AF4 | Chapter 3 failed with `llm_exception` / `code_bug` / `ValueError`. | §5 safe stderr; §8 safe runtime diagnostic. |
| AF5 | Provider attempt count for first failed chapter is `0`. | §8 safe runtime diagnostic. |
| AF6 | Runtime `max_output_chars` is `12000` in first-failed diagnostic metadata. | §8; prior blocker residual resolved. |
| AF7 | No fallback invocation, source expansion, or sensitive retention was observed in safe metadata. | §9 redaction/source-policy checks. |
| AF8 | Only `manifest.json` and `summary.json` were read; no chapter body or raw payload was accessed. | §6 safe metadata inspection. |
| AF9 | EID single-source/no-fallback policy preserved; `NOT_READY` preserved. | §1, §10, §11, §13. |
| AF10 | No code, tests, docs, source policy, provider defaults, repair budget, annual-period LLM route, Docling, readiness, release or PR state was changed. | §1 scope declaration; consistent with gate boundary. |

## 5. Required Amendments

| # | Severity | Finding | Required change |
|---|---|---|---|
| A1 | MEDIUM | F1: NEXT_ENTRY rationale underspecified relative to unresolved Chapter 3 code_bug. | In §13, add a sentence stating that the Post-retry Ready-state Disposition Gate is expected to route to a no-live Chapter 3 code-bug root-cause investigation/fix gate, given two live runs confirm the same pre-provider failure and the diagnostic-only fix did not resolve the underlying ValueError. |
| A2 | LOW | F2: Artifact timestamp not contextualized. | In §6, add a brief note that the `20260613` path component and `2026-06-13T17:35:13Z` created_at are in UTC and are consistent with a 2026-06-14 local-time execution. Optional. |

## 6. Final Verdict

**VERDICT: PASS_WITH_FINDINGS**

The execution artifact correctly records a bounded live retry that followed the preflight and command boundary from the worker-channel controller judgment and the accepted live evidence plan. All four core facts (exit 1, Chapter 3 code_bug, provider attempt count 0, max_output_chars 12000) are supported by safe runtime metadata. Source/fallback/readiness/provider-readiness claims are correctly rejected. Redaction and safe metadata boundaries are respected. EID single-source/no-fallback and `NOT_READY` are preserved.

Two non-blocking findings: the NEXT_ENTRY rationale should clarify that the disposition gate is expected to route to a no-live root-cause/fix gate (F1/MEDIUM), and the artifact timestamp could be briefly contextualized (F2/LOW). Neither finding affects the evidence validity or the fail-closed posture.

## 7. Recommended Controller Disposition

1. Accept the execution artifact as bounded live retry evidence with the two amendments above (A1 required, A2 optional).
2. Accept that the retry resolved the `max_output_chars` metadata blocker residual but did not change the Chapter 3 code_bug status.
3. Route the Post-retry Ready-state Disposition Gate to sequence a no-live Chapter 3 code-bug root-cause investigation/fix gate as the primary follow-up, rather than treating the code_bug as a closed or deferred residual.
4. Keep release/readiness as `NOT_READY`.
5. Do not authorize further live retries until the root cause of the Chapter 3 pre-provider ValueError is identified and fixed in a no-live gate.
