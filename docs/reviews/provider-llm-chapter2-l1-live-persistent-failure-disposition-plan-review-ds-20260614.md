# Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Plan — DS Review

Date: 2026-06-14

Role: AgentDS reviewer

Gate: `Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

## 1. Review Scope

This review verifies whether the disposition plan correctly classifies the live-persistent Chapter 2 L1 failure after accepted no-live prompt strengthening, and whether the recommended `deterministic Chapter 2 gap rendering planning gate` is the narrowest safe next gate consistent with current control truth.

Evidence reviewed:

| Artifact | Use |
|---|---|
| `AGENTS.md` | Execution truth, fail-closed posture, EID single-source/no-fallback boundary |
| `docs/current-startup-packet.md` | Current active gate, accepted checkpoint sequence, `NOT_READY` posture |
| `docs/implementation-control.md` | Current control truth and gate scope |
| Review target | Full plan body |
| `docs/reviews/provider-llm-chapter2-l1-prompt-strengthening-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Cross-check plan's accepted facts against source controller judgment |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-controller-judgment-20260614.md` | Cross-check plan's accepted facts against source controller judgment |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Cross-check plan's diagnostic facts against source controller judgment |

No report bodies, prompt bodies, provider payloads, PDF/source/cache bodies, or final report body were read.

## 2. Cross-check: Plan Facts vs Controller Judgments

| Plan claim | Controller source | Match? |
|---|---|---|
| Post-strengthening live evidence at `648c439` still first-fails Chapter 2 with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` | Post-fix controller judgment §Accepted Live Metadata Facts, §Controller Judgment | **Match** |
| Repair worsened L1 count from 1 to 2 | Post-fix controller judgment Chapter 2 attempt-level diagnostics: attempt 0 L1=1, attempt 1 L1=2 | **Match** |
| "This is not an implementation acceptance failure for the no-live prompt contract" | Post-fix controller judgment §Controller Judgment line 105 | **Match** |
| Checklist propagation is no-live proven; L1 fail-closed behavior is current-state proven | Diagnostic controller judgment §Finding Table: "Checklist currently reaches writer in no-live paths", "L1 fail-closed behavior remains valid" | **Match** |
| Auditor wording still uses older terminology | Narrow fix implementation controller judgment §Residuals: "Auditor `required_corrections` wording still uses older `第2章 R=A+B-C 数字闭环` terminology" | **Match** |
| Repair budget calibration is an open residual, not authorized for change | §1 "repair budget calibration is explicitly a separate future gate" in both startup packet and implementation control | **Match** |
| Prior Chapter 2 acceptance at `765c616` was repair-dependent | Diagnostic controller judgment: `T201900Z` Chapter 2 was `accepted` after repair; post-fix controller judgment Chapter 2 attempt count = 2 in the accepting run | **Match** |

All material claims trace to accepted controller judgments. No claim was found that contradicts the source evidence.

## 3. Findings

### F1 [MEDIUM] — Fact-Sufficiency Hypothesis Dismissal Is Under-Evidenced

**Location**: §4 Hypothesis Disposition Table, row "Insufficient facts or anchors causing a legitimate fail-closed gap"

**Finding**: The plan classifies this hypothesis as `POSSIBLE_NOT_PROVEN` and simultaneously promotes "Deterministic gap/minimum-verification rendering" as `PRIMARY`, using the same read-boundary limitation (no body/payload reads authorized) as the reason the fact-sufficiency hypothesis cannot be verified. This creates a directional asymmetry: the read boundary prevents disproving the hypothesis, but the plan uses that lack of disproof to route past it.

The diagnostic controller judgment explicitly notes: "The evidence does not prove whether the LLM read and ignored the checklist or whether checklist wording is too weak. Accepted residual." The plan correctly restates this, but its routing decision implicitly treats fact-sufficiency as secondary without establishing that gap rendering is safe for ALL cases, including cases where facts exist but the LLM ignores them.

**Why this matters**: If the root cause is genuinely absent facts/anchors in the source data, then deterministic gap rendering is correct product behavior. But if facts exist and the LLM is ignoring them despite checklist propagation, then gap rendering may mask a real pipeline defect that could affect Chapter 2 output for other funds.

**Recommendation**: The next planning gate should include a requirement to distinguish between "facts absent in source" and "facts present but LLM ignored" before committing to deterministic gap rendering as the primary product path.

### F2 [LOW] — "Fake-writer" Undefined in Validation Matrix

**Location**: §7 Validation Plan, row "Deterministic gap rendering trigger"

**Finding**: The validation matrix requires "A no-live fake-writer or fixture case where Chapter 2 L1 cannot be numerically closed after current repair budget." "Fake-writer" is not a term defined in the current architecture. The current `--use-llm` path uses a real provider-backed writer; the no-live test suite uses fixture/provider-mock patterns, not a "fake-writer." Without defining what "fake-writer" means (provider mock, deterministic stub, fixture-path writer bypass), the validation requirement is underspecified for code-generation.

**Why this matters**: The next planning gate needs to inherit this requirement. If "fake-writer" means mocking the provider at the writer level, that's a different architectural boundary than mocking at the provider-adapter level. The plan should clarify which layer is being faked and whether that fake must respect the same ToolTrace/repair contract as the real path.

**Recommendation**: In the plan's §7, replace "fake-writer" with a specific architectural term grounded in the current Service/Agent/Fund boundary, or add a clarifying note that the next planning gate must define the term before implementation.

### F3 [LOW] — Auditor/Repair Contract Residual Not Carried to Validation Matrix

**Location**: §4 row "Auditor versus repair instruction mismatch not captured by no-live tests" vs §7

**Finding**: The plan correctly records (§4) that the narrow fix implementation controller judgment accepted a residual where "auditor wording still uses older terminology." The hypothesis disposition correctly classifies this as `POSSIBLE_SECONDARY_NOT_PRIMARY`. However, §7's validation matrix does not include a row requiring auditor/repair contract alignment verification for the gap rendering path. If the gap rendering output must pass through the same auditor that uses older terminology, then the auditor's ability to recognize and accept a "gap/minimum-verification" output (as opposed to a numeric closure) should be explicitly validated.

**Why this matters**: The gap rendering output must satisfy the L1 auditor. If the auditor's contract uses older terminology that doesn't recognize "evidence gap" as a valid L1 resolution, the gap rendering could itself be rejected by the same auditor that currently rejects unconverged repair output.

**Recommendation**: Add a validation row in §7 requiring that the gap rendering output format is recognized and accepted by the current L1 auditor contract, or note the auditor terminology residual as an explicit test precondition for the next gate.

## 4. Cross-cutting Review Questions

### Q1: Control Truth, EID Single-source/No-fallback, NOT_READY

**PASS**. The plan explicitly preserves EID single-source/no-fallback (§1, §6). `NOT_READY` is preserved throughout (§1, §5, §6, §7, §8). The plan's scope matches the control truth definition: "no-code disposition/root-cause planning only." No unauthorized actions are proposed.

### Q2: Evidence Overstatement

**PASS with F1 residual**. The plan does not overstate what the evidence proves. It is transparent about the read boundary limitations (§1, §4). The hypothesis table uses calibrated language (`SUPPORTED_AS_OPERATIONAL_CLASSIFICATION_NOT_MECHANISTIC_PROOF`, `POSSIBLE_NOT_PROVEN`, `DEFERRED`). The primary concern is F1 above — the routing decision leans on the read boundary asymmetrically.

### Q3: Rejected/Deferred Alternatives

**PASS**. Each alternative has a clear, evidence-grounded justification:

- `additional no-live diagnostic evidence`: Correctly rejected — existing diagnostics already prove the mechanical path; metadata-only evidence won't close the semantic gap without body reads.
- `repair budget calibration`: Correctly deferred — more attempts might hide noncompliance; the controller judgment explicitly defers this to a separate gate.
- `narrower code fix`: Correctly rejected — the no-live implementation was accepted; no specific code defect is identified.
- `blocked pending user/product decision`: Correctly rejected — the fail-closed principle already supports planning deterministic gap behavior.

### Q4: Unauthorized Actions

**PASS**. The plan explicitly lists all unauthorized actions in §1, §6, and §8. No implementation, live command, source-policy change, fallback change, provider default change, repair budget change, annual-period LLM route, Docling, PR/release/readiness claim, or control-doc modification is authorized. The stop condition (§8) is explicit and complete.

### Q5: Validation Matrix Code-generation Readiness

**PASS with F2 and F3 residuals**. The validation matrix (§7) lists nine validation targets with required proofs and five planning artifact requirements. The targets are reasonably specific for a planning artifact. However, F2 (fake-writer undefined) and F3 (auditor contract alignment missing) mean the matrix would benefit from clarification before being inherited by a downstream implementation plan.

## 5. Residuals

| Residual | Severity | Reference finding | Next handling |
|---|---|---|---|
| Fact-sufficiency hypothesis not adequately distinguished from LLM noncompliance in routing decision | MEDIUM | F1 | Next planning gate should require distinguishing fact-absence from fact-ignored before committing to gap rendering as primary path |
| "Fake-writer" term undefined in current architecture | LOW | F2 | Clarify in next planning gate or in this plan's validation matrix |
| Auditor/repair contract alignment not in validation matrix | LOW | F3 | Add validation row for auditor acceptance of gap rendering output |
| Whether gap rendering could mask real pipeline defects for other funds | INFO | Derived from F1 | Next planning gate should discuss scope: single-sample vs general product behavior |
| Chapter 3 `missing_required_output_marker` in the same run is deferred but may interact with Chapter 2 first-fail ordering | INFO | Post-fix controller judgment §Residuals | Keep as a separate residual; if Chapter 2 gap rendering changes the first-fail chapter, Chapter 3 marker disposition may need re-ordering |

## 6. Recommendation for Controller

Accept the plan with F1-F3 amendments applied or recorded as binding residuals carried to the next `deterministic Chapter 2 gap rendering planning gate`.

The plan's core recommendation is sound: after two rounds of prompt strengthening failed to produce reliable Chapter 2 L1 convergence for the exact `004393 / 2025` live sample, continuing to stack prompt changes is not the narrowest safe route. Deterministic gap rendering is a legitimate fail-closed product behavior consistent with the project's fail-closed principle.

However, the next planning gate must:

1. Distinguish "facts absent from source" from "facts present but LLM ignored" before committing gap rendering as the universal product path (per F1).
2. Define the fake/mock/stub architecture for no-live gap-rendering validation (per F2).
3. Verify that the current L1 auditor contract can recognize and accept a gap/minimum-verification output without a terminology mismatch (per F3).

Release/readiness remains `NOT_READY`.
