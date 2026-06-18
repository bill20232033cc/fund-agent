# MVP Real LLM Smoke Re-baseline Gate Configured Evidence Review (AgentDS)

## 1. Review Scope

- Role: AgentDS independent evidence reviewer.
- Reviewed artifacts:
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`
  - `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-decision-20260604.md`
  - `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` (manifest.json, summary.json, chapter JSONs)
- This review does not modify evidence, source, test, config, control docs, retained artifacts, commits, provider/runtime/defaults, or run live provider.

## 2. Review Lens

Per controller instruction:

1. A1-A9 mapping correctness.
2. Secret-safe preflight and redaction scan adequacy.
3. Direct-evidence integrity and no historical substitution.
4. Correct residual classification: BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL rather than environment_blocked or content calibration.
5. Stop condition: no Chapter acceptance calibration yet.

## 3. A1-A9 Mapping Correctness

Each criterion independently verified against direct evidence and retained artifacts:

| Criterion | Evidence claim | Reviewer verdict | Basis |
|---|---|---|---|
| A1. Plan scope and forbidden-scope safety | PASS | PASS | Evidence stayed within controller authorization. No source/test/config/runtime change. Forbidden-scope checklist (section 11) is complete and each item independently verifiable. |
| A2. Env/config presence preflight is secret-safe | PASS | PASS | Both preflights (initial §4 and replacement §15) report only boolean presence and env var names. No base URL, provider/model name, API key value, or raw config dump printed. Verified by reviewer against the artifact text. |
| A3. Reviewed real-smoke command is singular and scoped | PASS | PASS | Replacement command count = 1, same fund/year/command, no overrides. Controller authorization explicitly limited to one replacement attempt. |
| A4. Incomplete fail-closed and stdout safety | PASS | PASS | Exit code 1, stdout empty, safe stderr summary present. Retained artifact created. No deterministic fallback. Verified against section 16 execution facts. |
| A5. Accepted report safety if smoke succeeds | NOT_APPLICABLE | NOT_APPLICABLE | Smoke failed; no report produced. Classification is correct. |
| A6. Safe diagnostic matrix and no secret leakage | PASS | PASS | CLI and retained artifact provide safe chapter/runtime matrix. Redaction scan (section 18) verified by reviewer with independent rg scan of retained artifacts — zero secret/credential/token matches. |
| A7. Direct evidence integrity | PASS | PASS | Branch/status/diff, command facts, retained artifact path, manifest/summary recorded. All section 19 A7 evidence is same-run, not historical. |
| A8. Provider timeout/block classification preserves current semantics | PASS_WITH_RESIDUAL | PASS_WITH_RESIDUAL | Verified: every chapter in summary.json has error_type=ReadTimeout, provider_runtime_category=timeout. No runtime/default/budget change. Classification accurately reflects same-run direct evidence. |
| A9. Boundary guardrails | PASS | PASS | No Dayu dependency, Agent runtime, multi-year runtime, PDF/cache/source-helper read, extra_payload, provider default, quality gate, golden/readiness, PR/push/release, or deterministic fallback introduced. Verified against forbidden-scope checklist and retained artifact contents. |

**A1-A9 mapping verdict: PASS.** All criteria correctly classified. No misclassification found.

## 4. Secret-Safe Preflight and Redaction Scan Adequacy

### Preflight adequacy

Both initial (§4) and replacement (§15) preflights:
- Use presence-only booleans.
- Print only env var names (`FUND_AGENT_LLM_API_KEY`), never values.
- Explicitly confirm no base URL, provider/model, API key value, Authorization header, raw config/env dump, raw prompt, or raw provider/audit response was printed.
- Explicitly state no endpoint reachability check or HTTP request was performed.

Reviewer independently confirmed: the evidence artifact text contains no secret-like values, no base URLs, no provider/model identifiers, and no raw provider payloads. The preflight `python -c '<presence-only env preflight>'` command itself is redacted in the artifact — the inline Python is replaced with a placeholder, which is an additional safety measure.

### Redaction scan adequacy

Evidence section 18 scan scope covers:
1. The evidence artifact itself.
2. The controller decision artifact.
3. The retained artifact directory.

Reviewer performed independent rg scan of `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` for secret-like patterns (API key, Authorization, Bearer, token, base URL). Result: zero matches.

Redaction in retained artifacts: `manifest.json` declares `redaction_applied: false`, `redaction_count: 0`. This means the runtime itself found nothing requiring redaction at write time. The reviewer's independent scan confirms this — no secret material is present in the retained JSONs or writer markdown files.

**Redaction verdict: PASS.** Preflights are secret-safe, redaction scans are adequate, and independent reviewer scan confirms zero secret material.

## 5. Direct-Evidence Integrity and No Historical Substitution

Evidence section 8 explicitly excludes historical retained artifacts from 2026-06-02 and 2026-06-03 from current direct evidence. The evidence artifact:
- Records branch `feat/mvp-llm-incomplete-run-artifacts` as the execution branch.
- Uses only the replacement attempt's retained artifact (`006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c`) for runtime evidence.
- Cross-references controller decision artifact for authorization chain.
- Records both the inconclusive first attempt (§7) and the replacement attempt (§16) transparently, with B2 explicitly superseded.

Reviewer verified cross-consistency between evidence artifact claims and retained `summary.json`:

| Evidence claim (§16-17) | summary.json | Match |
|---|---|---|
| orchestration_status=blocked | orchestration_status=blocked | YES |
| final_assembly_status=incomplete | final_assembly_status=incomplete | YES |
| first_failed_chapter_id=1 | first_failed.chapter_id=1 | YES |
| first_failed_stop_reason=llm_timeout | first_failed.stop_reason=llm_timeout | YES |
| first_failed_runtime_operation=auditor | runtime_diagnostics.first_failed.runtime_operation=auditor | YES |
| first_failed_provider_attempts=2/2 | first_failed.provider_attempt_count=2, provider_max_attempts=2 | YES |
| first_failed_approx_prompt_tokens=1074 | approx_prompt_tokens=1074 | YES |
| Chapter matrix all-6-llm_timeout | All 6 chapters failure_category=llm_timeout | YES |
| Chapter 2-5 terminal operation=writer | Chapters 2-5 terminal_runtime_operation=writer | YES |
| Chapter 1 & 6 terminal operation=auditor | Chapters 1 & 6 terminal_runtime_operation=auditor | YES |

**Direct-evidence integrity verdict: PASS.** No historical substitution detected. All evidence claims are traceable to same-run retained artifacts.

## 6. Residual Classification Correctness

### Current classification

Evidence section 20: `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL`.

### Why not `environment_blocked`

Both preflights confirm all required env/config present. B1 is explicitly resolved (§12). No environment blocker remains.

### Why not `content_calibration` or `Chapter acceptance calibration`

No chapter reached accepted status. `orchestration_status=blocked`, `final_assembly_status=incomplete`. All 6 chapters have `failure_category=llm_timeout`. The failure is at the provider runtime level (ReadTimeout), not at the content quality level. The `small_prompt_provider_timeout` hint across all chapters — including prompts as small as ~946 tokens (chapter 6 auditor) — further indicates provider-side timeout, not prompt-size or content issue.

### Why `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL` is correct

- The replacement smoke naturally failed closed (exit 1, empty stdout, safe stderr).
- Every chapter failed with `ReadTimeout` from the provider after exhausting 2/2 attempts.
- First failed is chapter 1 auditor: ~1074 prompt tokens, 60s timeout, 2 attempts exhausted.
- The failure is same-run, same-provider, direct evidence — not environment, not operator interruption, not content calibration.
- B3 (§20) correctly captures this as `provider_runtime_residual_all_chapters_llm_timeout`.

### One observation (non-blocking)

The `attempt_count` field in the chapter matrix (section 17) uses internal semantics where `attempt_count` represents `chapter-level attempts that reached audit`, not `total provider attempts`. Chapters 2-5 show `attempt_count=0` but their runtime diagnostics confirm 2 provider writer attempts each. This is internally consistent but could confuse a reader who expects `attempt_count` to equal provider attempt count. The evidence artifact already includes the full runtime diagnostic data in sections 16-17, providing sufficient context. Not a finding — just a documentation nuance.

**Residual classification verdict: PASS.** `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL` is the correct classification.

## 7. Stop Condition: Chapter Acceptance Calibration

Evidence section 20 minimum next entry item 3: "Do not enter Chapter acceptance calibration yet."

This is correct. No chapter has an accepted draft or accepted conclusion. All 6 chapters have `failure_category=llm_timeout`. There is no content to calibrate against. Proceeding to Chapter acceptance calibration before resolving the provider runtime residual would be premature.

**Stop condition verdict: PASS.**

## 8. Individual Residual Scan of Retained Writer Markdown

The retained `chapter-01-attempt-00-writer.md` and `chapter-06-attempt-00-writer.md` were not promoted into the evidence artifact (per §17). Reviewer spot-checked these files for secret leakage only — no API key, base URL, provider/model name, Authorization header, or raw provider response found.

## 9. Controller Decision Artifact Consistency

The controller decision artifact (`controller-decision-20260604.md`) and the evidence artifact are consistent:
- Decision authorizes exactly one replacement attempt (§3).
- Evidence executes exactly one replacement attempt (§16).
- Decision requires external observation window of 2400s (§3) — the replacement attempt naturally returned, so this was not triggered.
- Decision stop conditions (§5) were all respected: no provider default/runtime/budget change, no secret disclosure, no second replacement attempt, no deterministic fallback.

No inconsistency found between decision and execution.

## 10. Findings

### Blocking findings

None.

### Non-blocking findings

**N1 attempt_count semantics:** The `attempt_count=0` for chapters 2-5 in the chapter matrix (section 17) correctly matches the retained summary.json but uses internal semantics where the count reflects chapter-level audit attempts, not raw provider attempts. The runtime diagnostic data in the retained artifact fully documents the 2 provider attempts per chapter. Not blocking — the evidence is complete and correct.

## 11. Verdict

**Review verdict: PASS.**

| Dimension | Verdict |
|---|---|
| A1-A9 mapping correctness | PASS |
| Secret-safe preflight and redaction scan adequacy | PASS |
| Direct-evidence integrity and no historical substitution | PASS |
| Correct residual classification | PASS |
| Stop condition (no Chapter acceptance calibration) | PASS |

## 12. Gate Outcome Recommendation

1. **Accept** the evidence artifact correctness as independently verified.
2. **Gate state remains BLOCKED** by `B3 provider_runtime_residual_all_chapters_llm_timeout`.
3. **Do not enter Chapter acceptance calibration** until the provider runtime residual is dispositioned (provider endpoint/runtime policy decision or calibration).
4. The `B2 operator_interrupted_before_derived_host_deadline` blocker is correctly superseded and should not be reopened.
