# Plan Review: Baseline Coverage Disposition Decision Plan

> **Reviewer**: AgentGLM (independent plan review)
> **Date**: 2026-05-27
> **Gate**: `baseline coverage disposition decision gate`
> **Reviewed artifact**: `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-20260527.md`
> **Verdict**: **PASS_WITH_FINDINGS** (all findings informational / LOW severity; no blocking issues)

---

## 1. Review Scope and Method

True-source basis:
- `AGENTS.md` (唯一规则真源)
- `docs/design.md` v2.2 当前设计章节
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Accepted Artifacts / Open Residuals / Active Gate Ledger
- Accepted artifacts for 110020, 017641, 006597, bond-lens, FOF, and small baseline

Review focus per assignment:
1. Adversarially challenge cursor choice against alternatives
2. Check whether plan writes future assumptions as current facts or incorrectly elevates candidates
3. Check 017641 `disclosure_data_gap_not_baseline_ready` treatment
4. Check 006597 bond residual and FOF taxonomy residual preservation
5. Check non-entry / prohibition completeness

---

## 2. Startup Packet Replay Check

| Plan field | implementation-control.md reference | Match? |
|---|---|---|
| Current phase `release maintenance` | Line 8: `release maintenance` | ✅ |
| Startup Packet current gate `017641 manager_strategy_text public evidence triage accepted locally` | Line 28 | ✅ |
| Current requested gate `baseline coverage disposition decision gate` | Line 29 / §Next Entry Point line 403 | ✅ |
| Next entry point | Line 29/403 | ✅ |
| Latest checkpoint `71f1aa4` | `git log --oneline -1` confirms `71f1aa4 docs: accept 017641 public evidence triage` | ✅ |
| Architecture guardrail | Lines 20-22: Dayu 四层, 确定性 CLI 过渡 | ✅ |

**Finding**: None. Startup Packet replay is accurate.

---

## 3. Accepted Evidence Reconciliation Check

### 3.1 110020 / index_fund

Plan states: "Reviewed coverage candidate input accepted. Public provenance is complete eligible fallback after primary `unavailable`: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`. Quality gate is `warn`. Terminal state is `reviewed_coverage_candidate_input_accepted`; `promotion_disposition=not_promoted`."

Cross-reference implementation-control.md Current Decisions:
> "110020 reviewed coverage candidate evidence is accepted locally. Public CLI `--force-refresh` snapshot, score, and quality-gate runs all exited 0; provenance tuple matched the accepted complete eligible fallback tuple; quality status remained `warn`... Terminal state is `reviewed_coverage_candidate_input_accepted`; promotion disposition remains `not_promoted`."

Residuals listed in plan: "Methodology / constituents evidence remains insufficient; `turnover_rate` P1 warning remains; strict golden is absent; reviewed fact freeze is still a residual."

Cross-reference Open Residuals:
> "`006597` turnover_rate / holder_structure: future evidence or policy gate... Evidence remains `needs_more_evidence`"

And Current Decisions:
> "110020 reviewed coverage candidate decision plan is accepted locally... requires independent `index_evidence_assessment`, CSV identity/version note, strict golden absence as carried-forward residual"

**Verdict**: ✅ Fully accurate. No elevation, no missing residuals.

### 3.2 017641 / qdii_fund

Plan states: "Complete eligible fallback after primary `unavailable`. Public evidence confirms `manager_strategy_text` remains missing with no value, no anchor, and no locator. Quality gate is `block` on P0 `manager_strategy_text`; terminal state is `disclosure_data_gap_not_baseline_ready`; `promotion_disposition=not_promoted`."

Plan explicitly says: "Excluded from baseline/golden readiness. This is not an authorized extractor fix or policy change; later work must either replace/exclude this row or open a separate same-source evidence / implementation path."

Cross-reference implementation-control.md Current Decisions:
> "017641 manager_strategy_text public evidence triage is accepted locally. Public CLI evidence kept complete eligible fallback provenance and confirmed `manager_strategy_text` remains a P0 quality block with no value, no anchor, and no locator... terminal classification `disclosure_data_gap_not_baseline_ready`... does not authorize extractor implementation, policy/taxonomy changes, baseline/golden promotion, or fixture promotion."

**Verdict**: ✅ Fully accurate. 017641 is correctly treated as exclusion/replacement input only. The plan does not treat this as an extractor gap — it correctly identifies the gap as `disclosure_data_gap` (disclosure absence, not extraction failure). This is consistent with the accepted terminal state classification and the 017641 quality triage plan's conclusion that "current `quality_gate_status=block` is not enough to infer an extractor gap."

### 3.3 006597 / bond_fund

Plan states: "Bond-lens applicability improved: equity-shaped `holdings_snapshot` no longer creates a stock-holdings denominator block for exact `bond_fund` when paired with explicit `bond_risk_evidence.v1` replacement issue output. Quality moved to `warn`, not `pass`."

Plan says: "Not golden ready. `bond_risk_evidence_missing.baseline_blocking=true` remains, and residual P1 gaps such as `holder_structure`, `share_change`, and `turnover_rate` remain. Positive bond-risk evidence is still absent."

Cross-reference implementation-control.md:
> "`006597` bond quality-gate block: Completed for holdings applicability; future bond/holder/turnover evidence gates remain... Do not route to golden while `bond_risk_evidence_missing.baseline_blocking=true` or other P1 gaps remain."
> "`006597` turnover_rate / holder_structure: future evidence or policy gate... Evidence remains `needs_more_evidence`; do not infer from missing public output or implement without accepted source/policy proof."
> "`006597` share_change ambiguity: next share_change focused implementation plan"

**Verdict**: ✅ Fully accurate. Bond residual is correctly preserved with all sub-residuals enumerated.

### 3.4 FOF slot

Plan states: "Prior FOF attempts remain `data_gap` / `taxonomy_pending`. Current QDII-FOF candidates cannot be counted as pure `fof_fund` coverage without an accepted taxonomy decision or a repository-safe pure FOF candidate."

Cross-reference implementation-control.md:
> "FOF coverage / taxonomy: next baseline coverage / taxonomy gate: Find pure `fof_fund` repository-verified candidate, or open a taxonomy gate before counting QDII-FOF attempts as FOF coverage."
> "S0 corpus transition triggers: FOF corpus coverage: S0 recorded QDII-FOF as `data_gap`; second pass must find pure `fof_fund` or open QDII-FOF taxonomy / precedence design"

**Verdict**: ✅ Fully accurate. FOF taxonomy residual correctly preserved.

### 3.5 Reconciled blocker set

Plan's blocker set:
1. 110020 source/fallback resolved but reviewed baseline suitability incomplete ✅
2. 017641 QDII blocked by P0 disclosure / quality evidence ✅
3. 006597 observable but baseline-blocked by `bond_risk_evidence_missing` ✅
4. Pure FOF representative coverage absent ✅
5. No sample promoted ✅

**Verdict**: ✅ Complete and accurate.

---

## 4. Adversarial Cursor Challenge

### 4.1 Why not direct FOF taxonomy gate?

**Plan's position**: FOF is listed as Option B (separate gate) but not the recommended cursor.

**Challenge**: FOF is the only fund type with zero representative coverage. If FOF is the most critical gap, shouldn't resolving it take priority over a broader disposition gate?

**Assessment**: The plan's logic is defensible. FOF resolution requires either (a) a pure `fof_fund` candidate (currently unavailable) or (b) a taxonomy design decision. Both are narrow, specialized work. Meanwhile, index (110020) and QDII (017641) also have unresolved dispositions that affect overall baseline scope. Resolving all three slots' disposition simultaneously in Option A is more efficient than serial narrow gates, because:
- Option A's output is a decision matrix, not evidence or code — the work is bounded
- Individual slot dispositions are interdependent: excluding 110020 changes index coverage requirements, which changes whether a replacement candidate is needed, which affects overall baseline readiness
- FOF taxonomy work isn't blocked by Option A; the controller can open it as a follow-up

**Conclusion**: Cursor choice withstands this challenge. **No finding.**

### 4.2 Why not bond positive-risk evidence gate?

**Plan's position**: Listed as Option C but not recommended. Bond's blocker is evidence (positive bond-risk), not disposition.

**Challenge**: 006597 is the only bond candidate and has observable quality improvement. Resolving its evidence gap might be faster than a broad multi-slot disposition gate.

**Assessment**: The plan correctly identifies that 006597's blocker is qualitatively different from the other three slots. 006597 doesn't need a disposition decision (it's not going to be excluded — it's the only bond candidate). It needs positive bond-risk evidence. This is correctly scoped as a follow-up gate, not the immediate next step. The disposition gate for the other three slots should happen first because:
- If all three (index, QDII, FOF) end up excluded from v1, the baseline scope changes significantly, which affects how urgently bond evidence is needed
- Bond positive-risk evidence requires design/planning work (what counts as positive bond-risk evidence?) that is separate from disposition

**Conclusion**: Cursor choice withstands this challenge. **No finding.**

### 4.3 Why not 110020 reviewed fact freeze gate?

**Challenge**: 110020 is the only index candidate with accepted provenance. Why not proceed directly to reviewed fact freeze for this one candidate?

**Assessment**: The plan's reasoning is sound. Reviewed fact freeze is a downstream activity that should only happen after the disposition gate confirms 110020 stays in the baseline scope. If Option A decides to replace or exclude 110020, reviewed fact freeze work would be wasted. Running disposition first is the correct sequencing.

**Conclusion**: Cursor choice withstands this challenge. **No finding.**

### 4.4 Why not golden corpus v1?

**Plan's position**: Option D is explicitly non-entry.

**Assessment**: All five golden corpus v1 entry conditions remain unmet (coverage, source, quality, fund-type, fixture-promotion). The plan correctly defers this. No challenge warranted.

**Conclusion**: **No finding.**

### 4.5 Why not extractor implementation?

**Plan's position**: Option E is deferred unless prior accepted evidence proves a same-source extractor gap.

**Assessment**: No accepted evidence proves an extractor gap for any of the current blockers. 017641's gap is disclosure (`disclosure_data_gap_not_baseline_ready`), not extraction. 110020's residuals are methodology/constituents sufficiency and reviewed fact freeze, not extraction. 006597's `share_change` was identified as an extractor gap in the baseline triage, but the focused implementation for that already completed and the real 006597 row still lacks deterministic public evidence. Correct to defer.

**Conclusion**: **No finding.**

### 4.6 Overall cursor assessment

Option A (Replacement / Exclusion Candidate Selection Gate) is the correct next cursor because:
1. It addresses the dominant unresolved problem (disposition of blocked candidates) before any further evidence or implementation work
2. It is strictly decision/planning — no evidence, no code, no promotion
3. It produces a durable matrix that informs all subsequent narrow gates
4. It correctly separates disposition from evidence generation and implementation
5. Its scope (QDII/index/FOF) covers the slots that need disposition rather than evidence

The plan's first-principles justification is coherent: the goal is not to maximize probed rows but to establish a source-safe, representative, quality-acceptable candidate set with explicit residual ownership.

---

## 5. Assumption-vs-Fact Check

Systematic check for any instance where the plan writes future assumptions as current facts or incorrectly elevates candidates:

| Claim in plan | True-source verification | Verdict |
|---|---|---|
| 110020 is `reviewed_coverage_candidate_input_accepted` | implementation-control.md Current Decisions confirms | ✅ Fact |
| 110020 `promotion_disposition=not_promoted` | implementation-control.md confirms | ✅ Fact |
| 017641 is `disclosure_data_gap_not_baseline_ready` | implementation-control.md Current Decisions confirms | ✅ Fact |
| 017641 quality gate is `block` | implementation-control.md confirms | ✅ Fact |
| 006597 quality moved to `warn`, not `pass` | implementation-control.md: "final gate `warn`, not `pass`" | ✅ Fact |
| FOF is `data_gap` / `taxonomy_pending` | implementation-control.md confirms | ✅ Fact |
| "No sample may be promoted from this gate" | Plan-only gate, explicit prohibition | ✅ Correct constraint |
| "Reviewed fact freeze is still a residual" for 110020 | Open Residuals and Current Decisions confirm | ✅ Fact |
| "Positive bond-risk evidence is still absent" for 006597 | Open Residuals: `bond_risk_evidence_missing.baseline_blocking=true` | ✅ Fact |

**Verdict**: No instances of future assumptions written as current facts. No incorrect elevation of any candidate to baseline/golden-ready status.

---

## 6. Findings

### F1 (LOW / Informational): Option A scope doesn't explicitly state bond disposition is deferred

**Location**: Plan Section 3 Option A and Section 4

**Evidence**: Option A's title is "Replacement / Exclusion Candidate Selection Gate For QDII / Index / FOF Coverage" — bond (006597) is not in scope. Section 4's follow-up list mentions "bond positive-risk evidence" but does not call out that bond's disposition (include/exclude/defer from v1) is also unresolved and should be addressed before golden corpus v1.

**Risk**: If the controller overlooks bond disposition as a separate follow-up, bond could remain in limbo after Option A completes without an explicit owner for the bond-disposition decision.

**Suggested action for controller**: When accepting Option A, explicitly record that bond (006597) disposition is a separate follow-up gate with an identified owner and revisit condition. The plan's Section 4 already implies this ("the controller can open one of the narrower follow-up gates: ... bond positive-risk evidence") but an explicit disposition entry for bond in the disposition matrix output would prevent this gap.

**Severity**: LOW — the plan's Section 5 (Explicit Non-Entry) correctly preserves `006597 bond_risk_evidence_missing.baseline_blocking=true` as a golden corpus blocker, so bond cannot be silently promoted even if disposition is deferred. The finding is about clarity, not safety.

### F2 (LOW / Informational): Section 6 prohibition could explicitly cover AGENTS.md / docs/design.md edits

**Location**: Plan Section 6 (Explicit Prohibition)

**Evidence**: Section 6 lists code changes, renderer, FQ0-FQ6, Service/CLI, FundDocumentRepository/source strategy, Host/Agent/dayu, baseline/golden promotion, new evidence runs, GitHub mutation, and `docs/implementation-control.md` editing. It does not explicitly mention editing `AGENTS.md` or `docs/design.md`.

**Risk**: Minimal. The plan's Section 1 scope states "plan artifact only; no new evidence, no implementation, no promotion, no `docs/implementation-control.md` update", and the general prohibition "Code changes" implicitly covers design-doc changes that would require code alignment. AGENTS.md is the rule authority and should not be changed by a plan-only gate.

**Suggested action for controller**: No change required. The existing prohibition set is sufficient for a plan-only gate. If the controller wants maximum defensiveness, an explicit "No AGENTS.md / docs/design.md / docs/implementation-control.md edits" line could be added.

**Severity**: LOW — covered by general scope and prohibition semantics.

### F3 (LOW / Informational): Plan doesn't address the "all candidates need evidence" edge case

**Location**: Plan Section 3 Option A and Section 4

**Evidence**: Option A's expected output is a disposition matrix with values `include_for_later_review`, `replace`, `exclude_from_v1`, `needs_taxonomy_gate`, or `needs_evidence_gate`. If all candidates receive `needs_evidence_gate`, the gate produces a valid but potentially unsatisfying result: no slot gets a definitive include/exclude decision.

**Risk**: Low. This is a valid disposition outcome — "everything needs more evidence" is a legitimate conclusion. The plan's purpose is to produce the matrix, not to guarantee at least one slot is resolved.

**Suggested action for controller**: Accept this as a possible outcome. If it occurs, the controller should still record the matrix with explicit owners and revisit conditions for each slot, then open the appropriate narrow evidence gates.

**Severity**: LOW — the gate's purpose is to produce a decision matrix, and "all need evidence" is a valid decision.

---

## 7. Non-Entry / Prohibition Completeness Check

| Prohibition required | Plan Section 5/6 covers? | Notes |
|---|---|---|
| No promotion to baseline/golden/fixture | ✅ Sections 5, 6 | Explicit |
| No quality gate (FQ0-FQ6) weakening | ✅ Section 3 stop conditions, Section 6 | "Any plan that tries to... weaken FQ0-FQ6" |
| No source strategy changes | ✅ Section 3 stop conditions, Section 6 | "Any direct PDF/cache/source-helper/FundDocumentRepository source-strategy access" |
| No Host/Agent/dayu work | ✅ Section 6 | Explicit |
| No GitHub mutation (push/PR/merge/branch delete/commit) | ✅ Section 6 | Explicit |
| No code changes | ✅ Section 6 | Explicit |
| No renderer work | ✅ Section 6 | Explicit |
| No Service/CLI changes | ✅ Section 6 | Explicit |
| No new evidence runs | ✅ Section 6 | Explicit |
| No editing implementation-control.md | ✅ Section 6 | Explicit |
| No fund_type.py / taxonomy changes | ✅ Section 3 stop conditions | "change fund-type taxonomy... without a separate accepted design/implementation gate" |
| No extractor behavior changes | ✅ Section 3 stop conditions | "Any plan that tries to fix extractor behavior" |

**Verdict**: Prohibition set is comprehensive. No gaps that would allow promotion, quality gate weakening, source strategy changes, Host/Agent/dayu, or GitHub mutation.

---

## 8. Validation Check

Plan Section 8: `git diff --check` with exit code `0` — passed.

For a plan-only gate with no code changes, no tests, no evidence runs, no CLI commands, and no GitHub operations, this validation scope is appropriate and sufficient.

---

## 9. Summary

| Review dimension | Result |
|---|---|
| Startup Packet replay accuracy | ✅ PASS |
| Evidence reconciliation accuracy | ✅ PASS (all four slots verified against true sources) |
| No future assumptions as facts | ✅ PASS |
| No incorrect baseline/golden elevation | ✅ PASS |
| 017641 correctly treated as exclusion/replacement, not extractor gap | ✅ PASS |
| 006597 bond residual preserved | ✅ PASS |
| FOF taxonomy residual preserved | ✅ PASS |
| Cursor choice withstands adversarial challenges | ✅ PASS |
| Non-entry / prohibition completeness | ✅ PASS |
| Validation appropriateness | ✅ PASS |
| Findings | F1 (LOW), F2 (LOW), F3 (LOW) — all informational |

---

## 10. Verdict

**PASS_WITH_FINDINGS**

The plan accurately carries forward all accepted evidence states, correctly preserves all residuals, makes no unsupported factual claims, and chooses a defensible next cursor. All three findings are LOW severity and informational; none block acceptance. The controller may accept the plan as-is and address the informational findings during controller judgment if desired.

---

## 11. Controller Guidance

- **F1**: When recording the accepted plan, add an explicit note that bond (006597) disposition is a separate follow-up with owner and revisit condition.
- **F2**: No action required; consider adding explicit true-source doc protection in future plan-only gates for maximum defensiveness.
- **F3**: Accept as a possible valid outcome; ensure the disposition matrix records owners and revisit conditions even when all slots land on `needs_evidence_gate`.
