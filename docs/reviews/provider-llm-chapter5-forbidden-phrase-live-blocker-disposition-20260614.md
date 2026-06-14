# Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition Gate`

Verdict: `PROCEED_TO_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This disposition classifies the current strongest root cause after accepted Chapter 6 post-fix bounded live evidence checkpoint `4fb5284`.

This gate does not implement code, change tests, run another live command, change provider/source policy, change repair budget, claim readiness, or touch PR/release state.

Source policy remains unchanged. No fallback design or source expansion is accepted or implied.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution boundary and source-policy truth. |
| `docs/current-startup-packet.md` | Current active gate. |
| `docs/implementation-control.md` | Control truth and latest accepted checkpoint. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepted live evidence basis. |
| Safe metadata: `reports/llm-runs/004393-2025-20260614T002657Z-host_run_8c795cd1469b44d/summary.json` and `chapters/chapter-05.json` | Direct runtime metadata for current blocker. |
| Static symbol search over `fund_agent` and `tests` for `forbidden_phrase` / forbidden wording routes | Candidate no-live evidence map only. |

No writer Markdown body, auditor feedback body, repair Markdown body, raw prompt, provider request/response payload, credential, raw source/PDF/cache body, accepted final report body or generated report Markdown body was read.

## 3. Accepted Current Facts

From accepted live evidence checkpoint `4fb5284`:

| Fact | Disposition |
|---|---|
| Exact live sample is `004393 / 2025`. | ACCEPT |
| Chapter 6 is accepted after the no-live invalid-marker fix. | ACCEPT |
| Final assembly remains incomplete. | ACCEPT |
| Current first failed chapter is Chapter 5. | ACCEPT |
| First failed stop reason is `llm_contract_violation`. | ACCEPT |
| Current failure category is `audit_parse`. | ACCEPT |
| Current failure subcategory is `forbidden_phrase`. | ACCEPT |
| First failed runtime operation is `auditor`. | ACCEPT |
| First failed provider attempt count is `0`. | ACCEPT |
| Release/readiness remains `NOT_READY`. | ACCEPT |

From safe `chapter-05.json` metadata:

| Attempt | Writer status | Writer stop reason | Audit status | Runtime operation | Runtime `chapter_failure_category` | Repair context |
|---|---|---|---|---|---|---|
| `0` | `drafted` | `none` | `blocked` | `auditor` | `audit_parse` | absent |
| `1` | `blocked` | `llm_contract_violation` | `null` | `writer` | `prompt_contract` | absent in safe metadata |

Chapter 5 issue list contains one safe issue id:

```text
5:llm_contract_violation:writer:forbidden_phrase:7
```

## 4. Root-cause Classification

Strongest current classification:

```text
LLM_OUTPUT_POLICY_NONCOMPLIANCE_AFTER_REPAIR_ATTEMPT
```

Rationale:

- Attempt `0` produced a draft that failed programmatic audit with `audit_parse` / `forbidden_phrase`.
- The repair loop then reached attempt `1`.
- Attempt `1` did not reach audit; writer validation itself blocked with `writer:forbidden_phrase`.
- Provider attempt count is `0`, so this is not provider response classification or provider readiness evidence.
- The current blocker is within the writer/auditor/repair contract around forbidden wording, not source acquisition.

This classification is sufficient to route to no-live diagnostic evidence, but not sufficient to implement a fix yet.

## 5. Hypotheses For Next No-live Evidence Gate

| Hypothesis | Current disposition | Direct evidence needed next |
|---|---|---|
| H1: Chapter 5 prompt does not explicitly forbid the phrase family seen in live metadata. | OPEN | No-live prompt/input rendering test or static prompt contract inspection using fake writer only. |
| H2: Prompt forbids the phrase, but the LLM violates it and writer validation correctly blocks. | OPEN | No-live writer validation test for Chapter 5 forbidden phrase and repair-context rendering evidence. |
| H3: Audit repair context does not carry a specific forbidden-phrase correction into the second writer attempt. | OPEN | No-live runner/repair evidence proving what `ChapterRepairContext` contains after audit C1 forbidden phrase. |
| H4: Auditor and writer classify the same forbidden wording through different categories, causing confusing diagnostics but correct fail-closed behavior. | OPEN | No-live taxonomy evidence over `chapter_auditor`, `chapter_writer` and Service diagnostic mapping. |
| H5: Existing repair budget of `1` means a second-attempt writer forbidden phrase becomes terminal; this may be intended fail-closed behavior. | OPEN | No-live budget-path test proving no hidden second repair and documenting whether this is accepted product behavior. |

## 6. Rejected Or Deferred Paths

| Path | Disposition | Reason |
|---|---|---|
| Direct implementation now | REJECT_FOR_THIS_GATE | Root cause is not yet specific enough; no-live diagnostic evidence should identify whether prompt, repair context, taxonomy or budget behavior is at fault. |
| Additional live command now | REJECT_FOR_THIS_GATE | The current live blocker is already identified. More live evidence would not isolate the deterministic contract path. |
| Provider readiness or provider-response classification | REJECT | Provider attempt count is `0`. |
| Source acquisition or fallback change | REJECT | Current blocker is writer/auditor forbidden phrase policy, not annual-report source acquisition. |
| Repair budget calibration | DEFER | Budget policy is broader than this disposition; next evidence may inform a later budget calibration gate. |
| Readiness/release/PR claim | REJECT | Final assembly remains incomplete and `NOT_READY` remains controlling. |

## 7. Recommended Next Gate

Next entry:

```text
Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate
```

Goal:

Collect deterministic no-live evidence that distinguishes:

1. prompt contract omission,
2. LLM policy noncompliance caught by writer validation,
3. missing or underspecified audit repair context,
4. audit/writer diagnostic taxonomy mismatch,
5. intended repair-budget fail-closed behavior.

Allowed evidence direction:

- Read relevant source/test paths only:
  - `fund_agent/fund/chapter_writer.py`
  - `fund_agent/fund/chapter_auditor.py`
  - `fund_agent/agent/repair.py`
  - `fund_agent/agent/runner.py`
  - `fund_agent/services/chapter_orchestrator.py`
  - targeted tests in `tests/fund/test_chapter_writer.py`, `tests/fund/test_chapter_auditor.py`, `tests/agent/test_repair_policy.py`, `tests/agent/test_runner.py`, `tests/services/test_chapter_orchestrator.py`
- Run no-live focused tests or add no-live evidence artifact only if the gate is opened as evidence/implementation later.
- Use safe metadata only from the accepted runtime artifact; do not read raw bodies.

Forbidden:

- No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR command.
- No source/test/runtime behavior change in the diagnostic evidence gate unless a later implementation gate accepts a fix plan.
- No source policy, provider default, repair budget, annual-period route or fallback change.

## 8. Residuals

- Chapter 5 forbidden phrase blocks final assembly.
- It is not yet known whether the actionable fix is prompt salience, repair-context specificity, taxonomy clarity, writer validation behavior, or no code change.
- Chapter 2 non-terminal L1 metadata remains a monitoring residual, not current first blocker.
- Provider response classification remains unproven.
- Release/readiness remains `NOT_READY`.

## 9. Final Verdict

`VERDICT: PROCEED_TO_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

The current strongest root cause class is Chapter 5 LLM output policy noncompliance after a repair attempt, observed as `audit_parse` / `forbidden_phrase` followed by `writer:forbidden_phrase` fail-closed behavior. The correct next gate is no-live diagnostic evidence, not implementation or another live run.
