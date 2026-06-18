# Provider/LLM Chapter 2 L1 Live-regression Disposition — AgentDS Independent Review

Date: 2026-06-14

Role: AgentDS (independent reviewer)

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Live-regression Disposition Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-20260614.md`

---

## Scope

This review assesses the disposition artifact's factual accuracy, classification defensibility, recommendation justification, overclaim detection, and residual completeness. It does not implement, re-run live/provider/network commands, read forbidden body/payload/source/PDF content, or change readiness/release state.

---

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Execution rules, gate classification, evidence溯源要求 |
| `docs/current-startup-packet.md` | Current phase/gate/checkpoint timeline |
| `docs/implementation-control.md` | Control truth, gate ledger, residual registry |
| `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-20260614.md` | Review target |
| `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Prior accepted Ch2 live evidence |
| `docs/reviews/provider-llm-chapter3-required-output-policy-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Current live evidence |
| `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-controller-judgment-20260614.md` | Accepted Ch2 L1 no-live fix |
| `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json` | Prior safe summary |
| `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json` | Prior safe Ch2 |
| `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json` | Current safe summary |
| `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-02.json` | Current safe Ch2 |

No writer Markdown, auditor feedback, repair Markdown, raw prompt, provider payload, source/PDF/cache body, or final report body was read.

---

## Findings

### F1 (MEDIUM): Comparison table understates prior run's non-terminal L1 presence

The disposition comparison table reports prior Chapter 2 `category` as `null` and `issues` as `[]`. These are factually correct at the chapter level after repair resolution. However, the prior run's Chapter 2 attempt 0 also had a `programmatic:L1` issue（`programmatic:L1:line:33:009a9dbf62`）, which was resolved by the one-regenerate repair on attempt 1. The prior run was therefore not "L1 clean on first attempt" — it passed only because the repair worked.

The disposition text does note `subcategory: l1_numerical_closure in summary metadata, non-terminal`, which partially addresses this. However, a reader scanning only the comparison table could miss that the prior accepted run and the current failed run share the same underlying L1 failure pattern, differing only in whether repair succeeded.

**Severity rationale**: Does not invalidate the disposition's core comparison or recommendation. The key fact — prior Ch2 accepted, current Ch2 failed — remains true. But the nuance matters for root-cause precision: this is not a new regression from a clean baseline, but a recurrence of an existing weakness that repair previously masked.

**Recommendation**: The disposition text is sufficient as-is; no amendment required. The no-live diagnostic gate should explicitly compare attempt-0 writer output shapes from both runs, not just terminal chapter status.

---

### F2 (MEDIUM): Potential code interaction between Ch3 policy fix and Ch2 repair checklist not considered

The commit timeline reconstructed from the startup packet and controller judgments:

```
842362d  Ch2 L1 no-live fix (modifies fund_agent/fund/chapter_writer.py)
765c616  Ch2 post-fix live → Ch2 ACCEPTED, Ch3 fact-gap
1b9cd00  Ch3 required-output policy fix (modifies fund_agent/fund/chapter_writer.py)
2f8dce9  Ch3 post-fix live → Ch3 ACCEPTED, Ch2 FAILED
```

Both the Chapter 2 L1 fix and the Chapter 3 required-output policy fix touched `fund_agent/fund/chapter_writer.py`. The Ch2 fix added a `programmatic:L1` repair checklist that renders only for `chapter_id == 2` with L1 issues in `repair_context.previous_issue_ids`. The Ch3 fix changed item 01 from `block` to `render_evidence_gap`.

The disposition attributes the Ch2 failure solely to LLM output sensitivity of prompt guidance. While this is the most likely explanation, it does not consider whether the Ch3 policy fix inadvertently altered shared code paths in `chapter_writer.py` that affect Ch2 repair context assembly, checklist rendering, or prompt construction.

**Severity rationale**: This is a confounding factor that, if true, would change the root cause from "prompt guidance unstable" to "prompt guidance regressed by adjacent change." The no-live diagnostic gate can resolve this by comparing the repair prompt content before and after `1b9cd00`.

**Recommendation**: The disposition should add this as an explicit hypothesis for the no-live diagnostic gate. The diagnostic should verify: (a) the Ch2 L1 repair checklist is still present after `1b9cd00`, (b) the checklist content is materially identical to what was accepted at `842362d`, and (c) no shared code path in `chapter_writer.py` was inadvertently altered.

---

### F3 (LOW): `max_output_chars=null` in auditor diagnostics is noted but not connected to repair budget exhaustion

Both runs show `max_output_chars=null` in the runtime diagnostics for the auditor phase, while `writer_max_output_chars=12000` is consistently recorded. The startup packet flags `max_output_chars=null` as a known residual from the Ch3 root cause evidence. The disposition correctly notes the Ch3 residual but does not clarify whether the null auditor `max_output_chars` has any bearing on the Chapter 2 L1 audit path.

**Severity rationale**: The L1 audit is programmatic (not LLM-generated), so `max_output_chars` in auditor diagnostics is likely irrelevant to the L1 numerical closure check. This finding is informational only.

**Recommendation**: No action needed for this disposition. The diagnostic gate may clarify the diagnostic schema's `max_output_chars` semantics for auditor vs writer phases if needed.

---

### F4 (LOW): Repair budget remains at `max_repair_attempts=1`, making every L1 failure binary pass/fail

Both runs show exactly `attempt_count=2` for Chapter 2 (1 initial + 1 repair). With a single repair attempt, any L1 issue that survives the first regenerate becomes terminal. The disposition correctly defers repair budget calibration to a separate gate, but the binary nature of the current budget means that a single flaky LLM output determines pass/fail for the entire chapter.

**Severity rationale**: This is a known architectural constraint, not a disposition error. The disposition's recommendation to diagnose before fixing is consistent with not calibrating the budget prematurely.

**Recommendation**: The diagnostic gate should collect information about whether a second repair attempt (budget=2) would plausibly resolve the L1 issues, without changing the default budget.

---

## Cross-check: Rejected Classifications

The disposition rejects four alternative classifications. Independent verification:

| Classification | Disposition decision | DS assessment |
|---|---|---|
| Provider/network/runtime failure | REJECT | **Agree**. Both runs show provider attempt count `0` for first failure; failures are at auditor (programmatic) phase, pre-provider. |
| Source/fallback failure | REJECT | **Agree**. No source policy evidence changed; EID single-source/no-fallback preserved across both runs. |
| Chapter 3 required-output regression | REJECT | **Agree**. Current run shows Ch3 `accepted` with no issues. |
| Release/readiness pass | REJECT | **Agree**. Both runs exit fail-closed with incomplete final assembly. |

All four rejections are supported by direct safe metadata evidence.

---

## Cross-check: Disposition Questions

| Question | Disposition answer | DS assessment |
|---|---|---|
| Did the no-live Ch2 L1 fix remain live-stable? | NO | **Agree**. Current run reintroduces terminal L1 issues; prior run's acceptance was repair-dependent. |
| Does this invalidate prior `765c616` evidence? | NO | **Agree**. Prior evidence is a true observation for that run; it's now insufficient as stability proof, not false. |
| Does this prove provider/network/source failure? | NO | **Agree**. Safe metadata shows pre-provider programmatic audit failure. |
| Does this prove source fallback or EID policy drift? | NO | **Agree**. No source policy evidence changed or read. |
| Is a direct implementation gate justified immediately? | NO | **Agree**. We don't yet know whether prompt hardening, deterministic post-processing, audit enrichment, or writer contract update is the correct fix. |
| Is more live evidence the next best step? | NO | **Agree**. Repeated live sampling without diagnostic understanding is wasteful and uninformative. |
| Should the next gate be no-live diagnostic evidence? | YES | **Agree with findings**. See F2 — the diagnostic should also verify the Ch3 fix didn't inadvertently affect Ch2 behavior. |

---

## Root-cause Classification Assessment

The disposition classifies the root cause as:

```
LLM_OUTPUT_SENSITIVE_PROMPT_CONTRACT_RESIDUAL
```

**Defensibility**: The classification is defensible from direct evidence. The prior run resolved L1 via repair; the current run did not. The only defense is prompt guidance (the checklist added at `842362d`), and prompt guidance is inherently sensitive to stochastic LLM output. The classification correctly avoids overclaiming a specific mechanism (e.g., "checklist not rendered," "checklist ignored by LLM") without body-level evidence.

**Precision gap**: As noted in F2, the classification does not rule out the confounding factor of the `1b9cd00` code change. If the diagnostic gate finds the Ch3 fix inadvertently altered Ch2 repair prompt assembly, the classification would shift from `LLM_OUTPUT_SENSITIVE` to `CODE_INTERACTION_REGRESSION`. The current classification is the strongest defensible classification *given evidence available at disposition time*, but it should be presented as a working hypothesis rather than a conclusion.

---

## Residuals

| Residual | Disposition handling | DS assessment |
|---|---|---|
| Ch2 L1 output-sensitive failure as current first live blocker | Routed to no-live diagnostic evidence gate | **Adequate**. Add F2 hypothesis to diagnostic scope. |
| Ch5 forbidden phrase as downstream blocker | Deferred | **Adequate**. Not the first blocker; sequential disposition is correct. |
| Provider/LLM full completion unproven | Deferred to future gate | **Adequate**. Both runs fail-closed with incomplete assembly. |
| Repair budget uncalibrated | Deferred to separate gate | **Adequate**. See F4 for nuance. |
| Potential Ch3 fix / Ch2 code interaction | **Missing** | See F2. Should be added as diagnostic hypothesis. |
| Prior run's repair-dependent acceptance | Not explicitly called out | See F1. Prior accepted run was also L1-fragile; this contextualizes the "regression" narrative. |

---

## Next Gate Recommendation Assessment

The disposition recommends:

```
Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence Gate
```

With required purpose: compare deterministic accepted/failing Ch2 output shapes without live execution, prove whether the repair checklist reaches the writer, and identify the correct narrow fix shape.

**Assessment**: The recommendation is justified and appropriately scoped. The diagnostic gate is the correct next step. Two amendments are recommended:

1. Add F2 hypothesis: verify the Ch2 L1 repair checklist is intact after `1b9cd00` and no shared `chapter_writer.py` path was inadvertently altered.
2. The disposition's forbidden list for the next gate is complete and should be preserved as-is.

---

## Verdict

**PASS_WITH_FINDINGS**

The disposition accurately compares the two live runs, correctly rejects alternative classifications, and makes a justified recommendation for no-live diagnostic evidence. The core reasoning chain — prompt-only fix is output-sensitive → live reruns are uninformative → diagnose deterministically before fixing — is sound.

Findings F1 and F2 are non-blocking but should be addressed:
- F1: Diagnostic gate should compare attempt-0 writer shapes, not just terminal chapter status.
- F2: Diagnostic gate should verify the Ch3 policy fix (`1b9cd00`) did not inadvertently affect Ch2 repair prompt assembly.

No blocker finding against controller acceptance. The disposition correctly preserves `NOT_READY`, EID single-source/no-fallback, and the prohibition on live/provider/network/source/PDF/readiness/release/PR actions.

Release/readiness remains `NOT_READY`.
