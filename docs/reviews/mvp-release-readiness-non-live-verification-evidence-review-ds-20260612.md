# DS Evidence Review: Release-readiness Non-live Verification Evidence Gate

Date: 2026-06-12

Role: AgentDS evidence reviewer

Gate: `Release-readiness non-live verification evidence gate`

Review target:

- `docs/reviews/mvp-release-readiness-non-live-verification-evidence-20260612.md`

## 1. Verdict

**PASS_WITH_FINDINGS**

The evidence is self-consistent, follows the accepted plan, correctly classifies V7/V8 missing-path failures as blockers, avoids all prohibited claims, and does not override blockers with passing results. Two low-severity findings are noted below; neither changes the evidence outcome or the NOT_READY state.

## 2. Review Question Answers

### Q1: Is the evidence consistent with the accepted plan and control truth?

**YES.** The evidence executes the exact verification matrix commands (V1–V10) defined in the accepted plan Section 7. Each command's exit code and outcome are recorded. The failure classification rules (plan Section 7) are applied correctly: V7/V8 non-zero exits are classified as blockers, matching the plan's "blocker if fails" rule. The evidence preserves `NOT_READY` as required by the plan Section 1, the controller judgment, and the startup packet.

One consistency gap: the accepted plan matrix itself references three non-existent test paths. The evidence correctly surfaces this but does not attribute it. See Finding F1.

### Q2: Are V7/V8 missing-path failures correctly classified as blockers?

**YES.**

| Path | Plan rule | Evidence classification | Assessment |
|---|---|---|---|
| `tests/services/test_multi_year_annual_analysis.py` (V7) | "blocker if fails" | blocker | Correct. The matrix cannot execute as written. |
| `tests/ui/test_cli_annual_period.py` (V7) | "blocker if fails" | blocker | Correct. Second missing path in V7; command halted at first missing path. |
| `tests/services/test_llm_execution.py` (V8) | "blocker if fails due current Service/Host/Agent boundary" | blocker | Correct. The missing path is within the Service boundary under test. |

The evidence explicitly rejects the override: "Passing V9/V10 does not override missing-path blockers" (Section 7) and lists "V9/V10 pass overrides V7/V8 missing-path blockers" in Rejected Claims (Section 9).

### Q3: Does the evidence avoid readiness, release, PR, source acquisition, fallback or live claims?

**YES.** The evidence:

- Section 2: Explicitly enumerates all commands not run (live EID, network, PDF/FDR, provider/LLM, analyze/checklist, golden/readiness/release, PR/push/merge, cleanup/delete/move).
- Section 7: States "Release readiness is not proven" and "NOT_READY remains preserved."
- Section 9: Rejected Claims table explicitly rejects all six prohibited claim categories.

No readiness, release, PR, source acquisition, fallback, or live claim is made anywhere in the evidence.

### Q4: Are V5/V6/V9/V10 pass results recorded without overriding blockers?

**YES.** V5 (ruff), V6 (97 passed), V9 (1508 passed), and V10 (90.57% coverage, 50% floor passed) are all recorded as PASS with correct exit codes and measurements. The evidence:

- Section 7: "Passing V9/V10 does not override missing-path blockers."
- Section 7: "Passing V10 at the 50% floor is only a sanity check and does not itself prove readiness or single-file coverage sufficiency."
- Section 9: Rejects the override claim.

Pass results are recorded factually and walled off from blocker resolution.

### Q5: Is the recommended next entry appropriate?

**YES.** The evidence recommends `Release-readiness non-live verification matrix repair planning gate`. This is appropriate because:

1. The root cause is path drift in the accepted verification matrix, not a product-code failure.
2. A planning gate can correct the matrix paths using actually existing test files (the evidence lists candidate replacement paths observed via metadata-only filename scan).
3. The recommended gate preserves the same no-live/no-readiness/no-release/no-PR boundary.
4. Sequencing (plan → re-evidence → controller judgment) follows the established gateflow pattern.

The evidence correctly does not attempt to substitute paths itself, deferring that decision to a reviewed planning gate.

## 3. Findings

| # | Severity | Finding | Evidence | Required change |
|---|---|---|---|---|
| F1 | LOW | V8 partial execution: only the first missing path (`tests/services/test_llm_execution.py`) is reported as the cause of exit 4. The evidence does not separately confirm whether `tests/host` and `tests/agent` directories exist and were skipped due to the first-path error, or whether they would also fail. | Evidence Section 5 V8 row and Section 6 V8 row. | No change to evidence outcome. In the matrix repair planning gate, verify that `tests/host` and `tests/agent` exist and contain runnable tests before including them in the corrected V8 command. |
| F2 | INFO | The accepted plan matrix contained three non-existent test paths that neither DS nor MiMo plan review caught. | Plan Section 7 V7/V8 paths vs filesystem reality (evidence Section 5/6). | Process observation only. The matrix repair planning gate should include an explicit path-existence verification step before plan acceptance. |

## 4. Residual and Risk Table

| Residual / Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| V7/V8 matrix path drift | Blocker (current gate) | Controller / release verification owner | Matrix repair planning gate (recommended next entry). |
| `tests/host` and `tests/agent` not independently verified in V8 | Non-blocking | Evidence owner / matrix repair planning gate owner | Verify in repaired matrix. V9 broad pass (1508 tests) provides partial indirect coverage. |
| Static audit is keyword-based, not formal branch analysis | Non-blocking | Evidence owner | Accepted as-is; static audit + command behavior is sufficient for this gate classification. |
| Untracked workspace residue | Accepted residual | Artifact owners | Existing disposition gates; no action in this gate. |
| Planning review quality gap (path existence not verified) | Process risk | Controller / future plan reviewers | Include explicit path-existence check in future plan acceptance criteria. |

## 5. Final Recommendation

**ACCEPT** the evidence as a valid non-live verification execution record.

The evidence correctly:
- Follows the accepted plan's command matrix.
- Classifies V7/V8 missing-path failures as blockers per plan rules.
- Records V5/V6/V9/V10 pass results without allowing them to override blockers.
- Preserves `NOT_READY` and rejects all readiness/release/PR/live/source-acquisition/fallback claims.
- Recommends a properly scoped matrix repair planning gate as next entry.

Proceed to `Release-readiness non-live verification matrix repair planning gate` with the candidate replacement paths noted in evidence Section 6.
