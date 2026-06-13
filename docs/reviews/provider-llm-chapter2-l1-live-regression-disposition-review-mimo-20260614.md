# Provider/LLM Chapter 2 L1 Live-regression Disposition Review (MiMo)

Date: 2026-06-14

Reviewer: AgentMiMo

Review target: `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-20260614.md`

## Scope

Independent review of the disposition gate artifact that reconciles current live Chapter 2 L1 failure against prior accepted Chapter 2 live evidence and recommends the next gate path.

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-20260614.md` | Review target |
| `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Prior accepted Chapter 2 live evidence judgment |
| `docs/reviews/provider-llm-chapter3-required-output-policy-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Current live evidence judgment |
| `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-controller-judgment-20260614.md` | Accepted no-live fix implementation judgment |
| `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json` | Prior live summary metadata |
| `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json` | Prior live Chapter 2 metadata |
| `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json` | Current live summary metadata |
| `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-02.json` | Current live Chapter 2 metadata |
| `AGENTS.md` | Execution rules |
| `docs/current-startup-packet.md` | Current control truth |
| `docs/implementation-control.md` | Control doc |

No writer/auditor/repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body was read.

## Findings

### F1 [INFO] Comparison table accuracy — PASS

The disposition's `Accepted Comparison Facts` table is accurate against raw metadata:

- Prior run (`4a531cbe94604e4`): Chapter 2 `status=accepted`, `stop_reason=none`, `failure_category=null`, `failure_subcategory=l1_numerical_closure` (non-terminal in summary), `issues=[]` in chapter metadata, `attempt_count=2`. First failed = Chapter 3 (`fact_gap`). Verified.
- Current run (`605e381de24f4ab`): Chapter 2 `status=failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`, 2 `programmatic:L1` issues per attempt (4 total across 2 attempts). First failed = Chapter 2. Verified.
- Both runs: `provider_attempt_count=0` for first failure. Verified.
- Both runs: `final_assembly_status=incomplete`. Verified.

The table correctly captures the regression: prior run's Chapter 2 passed repair on attempt 1 with 0 issues; current run's Chapter 2 failed repair on both attempts with 2 L1 issues each, exhausting the budget.

### F2 [INFO] Subcategory field accuracy — MINOR_IMPRECISION

The disposition table states for the prior run: `failure_subcategory=l1_numerical_closure` in summary metadata, non-terminal. Raw metadata confirms this: `failure_subcategory` is `"l1_numerical_closure"` in the chapter matrix and summary, and `failure_category` is `null`, `stop_reason` is `"none"`. The "non-terminal" characterization is accurate — the subcategory was recorded as diagnostic metadata but did not block acceptance. No finding.

### F3 [INFO] Root-cause classification defensibility — PASS

The classification `LLM_OUTPUT_SENSITIVE_PROMPT_CONTRACT_RESIDUAL` is defensible from direct evidence:

1. The no-live fix at `842362d` added Chapter 2 L1-specific repair checklist guidance (prompt-only change, no auditor/repair-budget/repair-action changes).
2. Prior live run passed Chapter 2 after the fix (attempt 0 had 1 L1 issue, attempt 1 passed with 0 issues).
3. Current live run failed Chapter 2 with the same L1 family on both attempts (2 issues each), exhausting repair budget.
4. The failure is pre-provider (auditor path, `provider_attempt_count=0`), so it is not a provider/network issue.
5. The instability across live samples with the same fix points to LLM-output-sensitive behavior: the writer sometimes produces anchor-marker-compliant output and sometimes does not, and the prompt-only checklist does not deterministically guarantee compliance.

The classification is neither overclaimed nor underclaimed. It correctly identifies the residual as prompt-contract output sensitivity rather than a code bug or provider failure.

### F4 [INFO] Rejected classifications — PASS

All four rejected classifications are well-justified:
- Provider/network/runtime: `provider_attempt_count=0`, failure is auditor-phase. Correct rejection.
- Source/fallback: no source policy evidence changed. Correct rejection.
- Chapter 3 regression: current live shows Chapter 3 accepted. Correct rejection.
- Release/readiness pass: both runs exit `1` with incomplete assembly. Correct rejection.

### F5 [INFO] Recommendation justification — PASS

The recommendation to proceed to no-live diagnostic evidence rather than immediate fix or repeated live is justified:

1. **Not immediate fix**: The disposition correctly notes that body/prompt content was not read and the exact minimal code change is not yet known. The prior fix was prompt-only and proved insufficient — a different fix strategy (deterministic repair context, audit diagnostics, or stricter writer contract) needs diagnostic evidence first.
2. **Not repeated live**: The disposition correctly argues that repeating live would only sample stochastic writer behavior again without explaining the repair mechanics. Two live samples already show instability; a third would not add diagnostic value.
3. **No-live diagnostic evidence**: Can reproduce accepted/failing Chapter 2 writer output shapes with fixtures or fake LLM responses, then determine whether the fix should be prompt guidance hardening, deterministic repair context, safe diagnostic enrichment, or a stricter Chapter 2 writer contract. This is the correct evidence-first approach.

### F6 [INFO] Overclaims check — PASS

No overclaims detected:
- The disposition does not claim the prior evidence was invalid — it correctly states it "remains a true observation for that run; it is now insufficient as stability proof."
- The disposition does not claim content correctness for either run.
- The disposition does not claim readiness or completion.
- The disposition preserves `NOT_READY` and EID single-source/no-fallback throughout.

### F7 [INFO] Missing residuals check — PASS

The residual table covers the key items:
- Chapter 2 L1 output-sensitive failure as first live blocker (correct owner routing)
- Chapter 5 forbidden phrase as downstream blocker (correct deferral)
- Provider/LLM full completion unproven (correct residual)
- Repair budget uncalibrated (correct residual)

No material residual is missing. The Chapter 3 fact-gap residual is implicitly covered by the Chapter 3 acceptance in the current run — it is no longer a blocker in this run's context.

### F8 [INFO] Blocker findings against controller acceptance — NONE

No blocker findings against the disposition. The artifact:
- Correctly reconciles the two live observations
- Uses only safe metadata reads (no forbidden body/payload reads)
- Preserves all required guardrails (`NOT_READY`, EID single-source/no-fallback)
- Makes a defensible next-gate recommendation with clear forbidden-scope boundaries
- Does not overclaim or introduce unstated assumptions

## Residuals

| Residual | Note |
|---|---|
| `LLM_OUTPUT_SENSITIVE_PROMPT_CONTRACT_RESIDUAL` is a classification, not a root cause | The next no-live diagnostic gate must identify the specific fix mechanism; this classification only narrows the search space |
| Only 2 live samples observed | The instability pattern (pass/fail) is directionally clear but statistically thin; the no-live diagnostic route is the right response rather than collecting more live samples |
| Chapter 5 forbidden phrase deferred | Correct deferral; does not block this disposition |

## Verdict

**PASS**

The disposition artifact is accurate, defensible, and correctly routes the next gate to no-live diagnostic evidence. No blocker findings. The comparison table matches raw metadata, the root-cause classification is supported by direct evidence, the recommendation is justified, and no overclaims or missing residuals were identified.
