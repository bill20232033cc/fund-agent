# MVP provider runtime budget calibration plan review — MiMo

## Reviewer Role

Independent plan reviewer only. No implementation, no code edit, no commit, no push, no PR.

## Gate

`MVP provider runtime budget calibration gate`. Classification: `heavy`.

## Plan Under Review

`docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md`

## Review Focus Checklist

### 1. Same-Source Evidence And 2026-05-31 vs 2026-06-02 Distinction

**Verdict: PASS**

The plan correctly:
- Declares the 2026-06-02 timeout follow-up implementation evidence as missing and explicitly labels the 2026-05-31 substitute as historical only (Source Truth table, lines 20-27).
- Distinguishes the two evidence sets in the "Important correction" block (line 44-45): 2026-05-31 = writer timeout at compact-mode prompt sizes; 2026-06-02 = auditor timeout with writer drafts already produced.
- Uses only same-source retained run fields (`summary.json` chapter_matrix, runtime_diagnostics, prompt_contract_diagnostics) for the 2026-06-02 claims.
- Hypothesis table (H1, H3) explicitly references which evidence year supports or opposes each claim.

No mixing of historical and retained evidence found.

### 2. Root-Cause Claim Support

**Verdict: PASS with one non-blocking observation**

Each hypothesis is correctly scoped:

| Hypothesis | Assessment |
|---|---|
| H1 (provider small-prompt timeout) | Correctly supported by retained Ch2/Ch4/Ch6 auditor rows with `provider_runtime_category=timeout`, `approx_prompt_tokens` 584-743, `elapsed_ms` ~60000 |
| H2 (budget too low) | Correctly marked unresolved; bounded higher budget test is the right diagnostic |
| H3 (writer timeout primary) | Correctly disproved for 2026-06-02 retained run, correctly preserved as historically observed 2026-05-31 |
| H4 (auditor prompt format hang) | Correctly marked unresolved; PASS-only probe is a sound diagnostic |
| H5 (audit rules too strict) | Correctly nuanced: not supported for Ch2/Ch4 (timeout before audit result), mixed for Ch6 (attempt 0 C2/C1 before terminal timeout) |
| H6 (prompt contract/fact gap/code bug) | Correctly not supported for terminal timeout rows |

Non-blocking observation: the plan's H5 characterization for Ch6 attempt 0 is correct but the PoC matrix does not cleanly separate Ch6's mixed-failure nature from pure-timeout diagnostics (see Finding R2 below).

### 3. Hard Constraints Preservation

**Verdict: PASS**

All hard constraints are preserved:
- Fail-closed: explicitly stated (Hard Constraints, line 49)
- No deterministic fallback: explicitly stated
- No auditor relaxation: not proposed anywhere
- No score/golden/quality/readiness mutation: explicitly excluded (Hard Constraints, line 53)
- No provider default change: explicitly gated (Hard Constraints, line 52; Slice 2, line 321)
- No secrets in artifacts: explicitly forbidden (Hard Constraints, line 54-55; Option F, line 203-204)
- Stop condition (line 276) correctly routes "proposed fix requires auditor relaxation" to controller disposition

### 4. Future Evidence Commands, Stop Conditions, And Implementation Slices

**Verdict: PASS**

Future evidence commands:
- Read-only retained checks are safe (lines 228-231)
- Live commands are correctly gated as "controller-authorized only" (lines 238-249)
- Secret-safety scan command is provided (lines 258-261)

Stop conditions (lines 269-277) are well-formed and cover:
- Missing provider env
- Secret-bearing artifacts
- Missing runtime identification fields
- Ch2/Ch4/Ch6 failure mode change
- Bounded higher timeout still failing → classify as provider residual, not increase budget again
- Proposed fix requiring constraint violations

Implementation slices are conditional, small, and do not require ownership redesign:
- Slice 1: evidence-only serializer improvement, targeted files, no ownership change
- Slice 2: operation-specific budget policy, explicit "do not change defaults in same slice"
- Slice 3: diagnostic-only PASS-only probe, explicitly not production
- Slice 4: design-only split-audit, deferred to Agent-aware plan

### 5. Ownership Boundary

**Verdict: PASS**

- Current Service-owned provider construction and runtime ceilings are correctly stated (lines 364-369)
- Host is correctly scoped as lifecycle-only (line 368)
- Fund owns domain writer/auditor semantics (line 369)
- Accepted future Agent/tool-loop boundary is correctly described (lines 371-376)
- Split-audit is correctly deferred to Agent ownership (line 376)
- Provider clients remain Service-constructed explicit typed fields, not ToolRegistry tools (line 374)

---

## Blocking Findings

**None.** No blocking findings identified.

---

## Non-Blocking Risks

### R1: Ch6 Mixed Failure Not Cleanly Addressed In PoC Matrix

The plan correctly identifies Ch6's mixed failure in the Residual Risks table (line 394): "Ch6 has non-terminal C2/C1 evidence before terminal timeout." However, the PoC matrix (lines 213-218) and stop conditions treat Ch2/Ch4/Ch6 uniformly. If bounded higher auditor timeout resolves Ch6's timeout, the chapter will still fail on programmatic C2 (压力测试) and LLM C1 (unavailable compressed bond-risk evidence) from attempt 0. The PoC matrix's expected outcome column should note that Ch6 "accepted" is not achievable through budget calibration alone.

The plan's residual risk table and recommendation to route to "separate Ch6 audit/contract calibration only after timeout no longer blocks" is the correct disposition. The PoC matrix would benefit from a footnote acknowledging this, but it does not block the plan.

### R2: Intermediate Timeout Values Not Considered

The design compares `60s x2` against `120s x2`. If the endpoint responds at, say, 90s for auditor prompts, the 120s test would pass but the optimal budget might be lower than 120s. This is acceptable for a first diagnostic gate; a finer-grained sweep can follow if 120s passes.

### R3: `timeout_budget_kind` Field Reliability

The jq command (line 230) relies on `timeout_budget_kind` to identify auditor-timeout rows. This field is present in the retained run's runtime_diagnostics (verified: Ch2/Ch4/Ch6 all have `timeout_budget_kind=auditor`). No issue with current evidence; noted for future runs where this field might be absent if serializers change.

### R4: Ch4 Writer Draft Evidence Gap

Ch4 has `attempt_count=1` in the retained run, meaning it timed out on the first auditor call without a repair attempt. The plan correctly records this (chapter matrix, line 79). However, unlike Ch2 (which also has `attempt_count=1` and a writer draft file), Ch4's writer draft at `chapters/chapter-04-attempt-00-writer.md` confirms the writer succeeded. This is consistent with the plan's claim that writer drafts were produced for all timeout chapters. No issue; just confirming the evidence chain is complete.

---

## Summary

**PASS.** No blocking findings. The plan correctly uses same-source evidence, distinguishes 2026-05-31 historical writer-timeout from 2026-06-02 retained auditor-timeout, preserves all hard constraints, defines well-scoped future evidence commands with clear stop conditions, and respects ownership boundaries. Four non-blocking risks are noted for controller awareness.

---

## Validation Performed

- Read `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md`, `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1-controller-judgment-after-provider-restore-20260602.md`, and `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json`.
- Verified retained summary.json chapter_matrix and runtime_diagnostics fields against plan claims.
- `git diff --check` — to be run after write.
