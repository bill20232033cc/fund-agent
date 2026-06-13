# Provider/LLM Chapter 2 L1 No-live Diagnostic Evidence — DS Review

Date: 2026-06-14

Role: AgentDS independent reviewer

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Diagnostic Evidence Gate`

Target: `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

## Scope

This review assesses whether the no-live diagnostic evidence artifact satisfies the seven controller amendments from `557fd6c` (`docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-controller-judgment-20260614.md`), whether the no-live commands and safe-read boundaries are compliant, and whether the conclusion `READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY` is adequately supported.

## Evidence Reviewed

| Artifact | Use |
|---|---|
| `AGENTS.md` | Execution rules, module boundaries, EID single-source policy |
| `docs/current-startup-packet.md` | Current gate definition, checkpoint chain, residual ownership |
| `docs/implementation-control.md` | Control truth, current gate scope, non-goal reminder |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-20260614.md` | Primary evidence under review |
| `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-controller-judgment-20260614.md` | Controller amendments baseline |
| `fund_agent/fund/chapter_writer.py` | Code cross-check of F2/F3 claims |
| `tests/fund/test_chapter_writer.py` | Cross-check of writer test claims |
| `tests/services/test_chapter_orchestrator.py` (L1/repair functions) | Cross-check of orchestrator test claims |
| `tests/fund/test_chapter_auditor.py` | Cross-check of auditor test claims |

No forbidden files were read. The four safe metadata JSON files were not independently re-read; the evidence artifact's metadata table is taken at face value and cross-checked against the controller judgment's accepted facts.

## Findings

### F1 (BLOCKER): Amendment 2 is only partially satisfied — no `1b9cd00` diff verification

**Severity: High. Does not block gate acceptance but must be carried as binding residual into next gate.**

The controller judgment at `557fd6c` Amendment 2 explicitly requires:

> Verify that `1b9cd00` did not inadvertently change Chapter 2 repair prompt assembly, checklist rendering, or shared `chapter_writer.py` paths relevant to Chapter 2 L1.

The evidence artifact F3 acknowledges:

> No git history comparison command was authorized, so this artifact does not claim byte-for-byte identity with checkpoint `842362d`.

The evidence instead performs current-state code inspection, concluding that Chapter 3 typed required-output paths (`render_evidence_gap`, `delete`, `block`, etc.) are structurally separate from the Chapter 2 L1 checklist condition (`_ch2_l1_repair_guidance_prompt()` gated on `chapter.chapter_id != 2` plus `_has_l1_numerical_closure_repair_issue()`).

My independent code cross-check confirms this structural separation in current code:

- `_ch2_l1_repair_guidance_prompt()` (line 1286) depends only on `chapter.chapter_id == 2` and `_has_l1_numerical_closure_repair_issue()` (line 1268), which checks `programmatic:L1` prefix in `repair_context.previous_issue_ids`.
- `_chapter_prompt_fragments()` (line 660) assembles repair_context by joining `_repair_context_prompt()` and `_ch2_l1_repair_guidance_prompt()` — both are generic infrastructure.
- Chapter 3 typed required-output logic flows through `_required_output_evidence_plan()` → `_required_output_plan_item()` → `_required_output_action()`, none of which touch `_ch2_l1_repair_guidance_prompt()` or `_has_l1_numerical_closure_repair_issue()`.
- The focused writer tests (`test_ch2_l1_repair_context_renders_local_anchor_placement_checklist`, `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context`) and orchestrator test (`test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair`) all pass after `1b9cd00`.

**However**, the current-state analysis cannot rule out that `1b9cd00` touched shared infrastructure in ways not visible through path-independence reasoning alone. For example, if `1b9cd00` modified `_chapter_prompt_fragments()` or `build_chapter_prompt()` in a way that subtly changed prompt assembly order, token budget, or fragment joining, the current-state code would show the post-`1b9cd00` state but could not prove the absence of such a change without a diff. The evidence correctly identifies this as a limitation.

**Disposition**: The current-state evidence is strong and the structural separation is real, so I do not recommend rejecting the gate. But the next fix-planning gate must either authorize a `git diff 842362d..1b9cd00 -- fund_agent/fund/chapter_writer.py` inspection or accept this residual as an explicit planning assumption. The controller should amend the next gate's scope to close this gap.

### F2: Metadata-only comparison cannot distinguish "LLM ignored checklist" from "checklist wording insufficient"

**Severity: Medium. Acknowledged by evidence; shapes next gate scope.**

The evidence F1 and the limitation note correctly state that safe metadata (status, issue ids, counts, attempt counts, writer response lengths) cannot reveal whether the LLM read and disregarded the checklist, or whether the checklist wording is too weak to reliably change model behavior. H5 is correctly rejected as overclaim.

This is not a flaw in the evidence — it is a design constraint of the no-live metadata approach. But it means the next fix-planning gate operates under uncertainty about the precise failure mechanism. The evidence's recommendation to treat this as a "prompt-contract determinism problem" is the correct framing, but the fix plan must explicitly acknowledge this residual uncertainty and design mitigations that work under either interpretation (e.g., stronger segmentation, deterministic post-writer validation, safer required correction wording).

### F3: Focused test selection is narrow but appropriate for diagnostic gate

**Severity: Low. Informational.**

The evidence ran three focused `pytest -k` invocations selecting 16 tests total (6 writer + 4 orchestrator + 6 auditor). This is adequate for a diagnostic evidence gate that must not change code. The full test suite was not run, which is correct — this is not an implementation gate.

However, the evidence does not report whether any tests were skipped, deselected due to keyword mismatch, or failed for unrelated reasons. The `-q` flag suppresses this detail. The deselected counts (40 + 76 + 43) suggest the focused filters worked correctly. No action required.

### F4: Commands and safe-read boundaries are fully compliant

**Severity: None. Confirmed compliant.**

The commands table lists only `git status`, `git diff --check`, `sed`/`rg` on allowed files, `jq` on the four metadata JSON files, and `uv run pytest` on focused tests. No live, provider, network, source, PDF, FDR, analyze, checklist, readiness, release, or PR commands were run. The evidence explicitly disclaims reading forbidden body/payload/source/final report files.

This satisfies Amendments 6 and 7 (no live commands, preserve EID single-source/no-fallback and `NOT_READY`).

### F5: Controller Amendment 1 (attempt-level comparison) is satisfied

**Severity: None. Confirmed.**

The comparison table correctly shows:
- Prior run: attempt 0 had 1 `programmatic:L1`, attempt 1 had 0 (repair cleared it)
- Current run: attempt 0 had 2 `programmatic:L1`, attempt 1 had 2 (repair did not clear)
- Both runs used 2 total attempts (initial + one repair)

F1 correctly characterizes this as "repair-effectiveness failure, not clean-baseline regression." The prior Chapter 2 acceptance was repair-dependent, which the controller already accepted as fact.

### F6: Controller Amendments 3, 4, 5 are satisfied

**Severity: None. Confirmed.**

- Amendment 3 (prove checklist reaches writer): F2 and the focused writer/orchestrator tests prove this. My code cross-check confirms the checklist assembly path.
- Amendment 4 (preserve L1, do not weaken): Auditor tests confirm L1 remains fail-closed. H6 correctly rejects weakening.
- Amendment 5 (do not change repair budget): Scope excludes budget changes; residual table defers calibration to separate gate.

### F7: Conclusion READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY is supported with caveats

**Severity: Low. The conclusion is correct given the evidence, provided F1 and F2 residuals are carried forward.**

The evidence correctly identifies that:
- The pipeline is intact (checklist reaches writer)
- Chapter 3 does not interfere
- L1 semantics are preserved
- The failure is repair-effectiveness, not a broken pipeline
- Live re-sampling is not the answer
- Immediate implementation is premature

The next gate recommendation correctly scopes the fix planning:
- Assume pipeline intactness
- Target deterministic L1 compliance under fake-LLM/fixture evidence
- Consider stronger prompt contract segmentation, safer correction wording, deterministic post-writer validation
- Do not change repair budget or weaken L1

## Residuals

| Residual | Severity | Owner/Handling |
|---|---|---|
| `1b9cd00` diff verification not performed | High | Next fix-planning gate must either authorize a bounded `git diff` or accept this as explicit planning assumption |
| Metadata-only: cannot prove LLM read vs ignored checklist | Medium | Next fix-planning gate must design mitigations robust to either interpretation |
| Focused test selection — full suite not run | Low | Acceptable for diagnostic gate; implementation gate requires full suite |
| Attempt-level body/proof gap | Medium | Already acknowledged; requires future body-read or fixture diagnostic gate |
| Repair budget calibration, Chapter 5 blocker, workspace residue | Deferred | Already in residual table; not this gate's scope |

## Verdict

`PASS_WITH_FINDINGS`

The evidence satisfies six of seven controller amendments. Amendment 2 is partially satisfied: current-state code inspection confirms path independence, but the absence of a `git diff 842362d..1b9cd00` inspection means the controller's explicit request for `1b9cd00`-specific verification is not fully closed. This finding does not block gate acceptance — the structural evidence is strong — but F1 must be carried as a binding residual into the next no-live fix planning gate.

The conclusion `READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY` is supported.
