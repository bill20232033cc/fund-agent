# Review: Replacement / Exclusion Candidate Selection Decision — AgentDS

> Reviewer: AgentDS (independent decision/plan reviewer)
> Date: 2026-05-27
> Artifact under review: `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-20260527.md`
> Gate: `replacement/exclusion candidate selection gate for QDII/index/FOF coverage`
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Startup Packet Replay Verification

| Check | Source | Result |
|---|---|---|
| Current phase `release maintenance` | Control doc §Startup Packet, line 27 | Pass |
| Current gate `baseline coverage disposition decision plan accepted locally` | Control doc §Startup Packet, line 28 | Pass |
| Next entry point `replacement/exclusion candidate selection gate for QDII/index/FOF coverage` | Control doc line 29, §Next Entry Point line 408 | Pass |
| Latest accepted checkpoint `b919e5e` | `git log` HEAD, control doc line 16 | Pass |
| Truth sources replayed: AGENTS.md, design.md, control doc Startup Packet / Next Entry Point, accepted plan and review artifacts | Control doc §Startup Packet lines 18-19 | Pass |
| Artifact self-identifies as worker, not controller | Artifact §1: "This worker is producing the requested candidate disposition decision artifact only" | Pass |
| Artifact correctly identifies itself as Startup Packet next entry point, not gate switch | Artifact §1: "This is the Startup Packet next entry point, not a gate switch" | Pass |

**Assessment**: Startup Packet replay is accurate and complete.

---

## 2. Disposition Matrix Cross-Verification

### 2.1 110020 / index_fund → `include_for_later_review`

| Artifact claim | Accepted source | Match |
|---|---|---|
| `reviewed_coverage_candidate_input_accepted` | 110020 evidence controller judgment: terminal state confirmed | Yes |
| Complete eligible fallback: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete` | 110020 evidence controller judgment §Accepted Evidence State | Yes |
| Quality `warn` | Same source: `quality_gate_status=warn` | Yes |
| `promotion_disposition=not_promoted` | Same source: confirmed | Yes |
| Residuals: methodology/constituents sufficiency, turnover_rate P1, strict golden absence, reviewed fact freeze | 110020 controller judgment §Index Evidence Judgment: methodology/constituents `insufficient`, `benchmark_identity_status=missing` | Yes |
| Disposition `include_for_later_review` | Consistent with terminal state: accepted for coverage-candidate input only, not baseline/golden ready | Yes |

### 2.2 017641 / qdii_fund → `replace`

| Artifact claim | Accepted source | Match |
|---|---|---|
| `qdii_fund`, complete eligible fallback | 017641 public evidence controller judgment: provenance tuple confirmed | Yes |
| Quality `block` | Same source: P0 fails coverage/traceability at 0.0 | Yes |
| Terminal `disclosure_data_gap_not_baseline_ready` | Same source: terminal classification confirmed | Yes |
| `manager_strategy_text` missing: no value, no anchor, no locator | Same source: `extraction_mode=missing`, `value_present=false`, `anchor_present=false` | Yes |
| P0 quality block persists | Same source: FQ2/FQ3/FQ2F all cite `manager_strategy_text` | Yes |
| Disposition `replace` | Correct: terminal disclosure data gap means current candidate cannot represent QDII coverage; promoting would convert known missing fact into baseline truth | Yes |

### 2.3 FOF slot → `needs_taxonomy_gate`

| Artifact claim | Accepted source | Match |
|---|---|---|
| No pure `fof_fund` representative accepted | Small baseline corpus v1 controller judgment + control doc decisions: FOF remains `data_gap` / `taxonomy_pending` | Yes |
| QDII-FOF candidates (`007721`/`017970`) classified as `qdii_fund`, not pure FOF | Control doc open residual line 472; type identification via `classify_fund_type()` yields `qdii_fund` | Yes |
| No accepted taxonomy decision | No standalone FOF taxonomy accepted artifact exists in control doc Accepted Artifacts | Yes |
| Disposition `needs_taxonomy_gate` | Correct: FOF coverage cannot be resolved without taxonomy decision | Yes |

### 2.4 004393 / active_fund → `include_for_later_review`

| Artifact claim | Accepted source | Match |
|---|---|---|
| Accepted clean evaluated active-fund candidate | Small baseline corpus v1 controller judgment: `004393` / active as clean evaluated candidate | Yes |
| Quality `warn`, not `scoring_ready`, not durable baseline | Control doc decision line 371: "not as a durable baseline or golden corpus" | Yes |
| Small baseline corpus v1 accepted as evaluated evidence only | Same source | Yes |
| Disposition `include_for_later_review` | Correct: carry-forward input, not promoted fixture | Yes |

### 2.5 004194 / enhanced_index → `include_for_later_review`

| Artifact claim | Accepted source | Match |
|---|---|---|
| Accepted clean evaluated enhanced-index candidate | Small baseline corpus v1 controller judgment: `004194` / enhanced-index as clean evaluated candidate | Yes |
| Quality `warn`, not `scoring_ready`, not durable baseline | Same as 004393 | Yes |
| Disposition `include_for_later_review` | Correct | Yes |

### 2.6 006597 / bond_fund → `needs_evidence_gate`

| Artifact claim | Accepted source | Match |
|---|---|---|
| Bond-lens applicability improvement accepted | Bond-lens score applicability implementation controller judgment: accepted | Yes |
| Quality improved to `warn`, not `pass` | Same source: final gate `warn`, not `pass` | Yes |
| `bond_risk_evidence_missing.baseline_blocking=true` remains | Control doc residual line 473: confirmed | Yes |
| Residual P1 gaps: `holder_structure`, `share_change`, `turnover_rate` | Control doc residuals lines 475, 477: `share_change` still missing, `turnover_rate`/`holder_structure` remain `needs_more_evidence` | Yes |
| Positive bond-risk evidence absent | Triage evidence: no positive bond-risk evidence produced | Yes |
| Disposition `needs_evidence_gate` | Correct: bond remains golden blocker; separate from QDII/index/FOF scope | Yes |
| Owner scoped as "not part of QDII/index/FOF replacement scope" | Aligns with controller judgment requirement: "bond disposition remains a separate follow-up" | Yes |

**Assessment**: All six disposition rows are materially accurate against accepted evidence. No misclassification.

---

## 3. Owner and Revisit Condition Specificity Audit

| Slot | Owner specificity | Revisit condition specificity | Assessment |
|---|---|---|---|
| 110020 | Controller to assign reviewer before fixture/golden step — sufficiently scoped | Gates on accepted index reviewed fact freeze / evidence sufficiency + strict golden disposition — concrete preconditions | Adequate |
| 017641 | Controller to open/assign QDII replacement candidate evidence gate — actionable | Replacement must have source-safe provenance, same-year evidence, no P0 quality block, explicit no-promotion review; fallback to `exclude_from_v1` — covers both outcomes | Adequate |
| FOF | Controller to open/assign FOF taxonomy / pure FOF candidate gate — actionable | Two explicit paths: pure FOF entry contract + candidate, or explicit `FOF deferred from golden v1` with owner and revisit trigger — covers both outcomes | Adequate |
| 004393 | Controller / future baseline preflight owner — least specific, forward reference to future gate | Durable baseline or golden preflight after prerequisites met — defers appropriately | Adequate for carry-forward |
| 004194 | Same as 004393 | Same as 004393 | Adequate for carry-forward |
| 006597 | Controller to open/assign separate bond positive-risk evidence gate — actionable, correctly scoped as separate | Accepted positive bond-risk evidence contract or bond exclusion/deferral decision resolves `baseline_blocking=true` — concrete resolution path | See F2 |

All six slots have explicit owners and specific revisit conditions, satisfying the controller judgment requirement (lines 61-62).

---

## 4. Next Cursor Recommendation Adversarial Review

### 4.1 Recommended cursor

`QDII replacement candidate evidence gate`

### 4.2 First-principles trace

| Justification | Evidence | Assessment |
|---|---|---|
| 110020 preserved as `include_for_later_review`; index fact freeze is downstream | Matrix disposition confirmed | Sound — index fact freeze is gated on broader coverage path confirmation |
| 017641 terminal state; replacement is least ambiguous | 017641 controller judgment: `disclosure_data_gap_not_baseline_ready` | Sound — concrete failed candidate, clear action |
| FOF is taxonomy/scope first; QDII replacement is narrower | FOF disposition is `needs_taxonomy_gate` | Sound — QDII replacement doesn't require taxonomy changes |
| Bond is separate follow-up | 006597 disposition is `needs_evidence_gate` with separate owner | Sound |
| Durable baseline/golden preflight remains non-entry | §5 lists all blockers | Sound |

### 4.3 Alternative evaluation

| Alternative | Why rejected | Assessment |
|---|---|---|
| FOF taxonomy gate | Broader scope question; QDII replacement is concrete and narrow | Reasonable |
| Bond evidence gate | Separate golden blocker, outside QDII/index/FOF scope | Correct rejection |
| Index fact freeze | Downstream of coverage confirmation; 110020 is `include_for_later_review`, not ready for facts | Correct rejection |
| Reduced-scope decision | Only if QDII replacement fails; artifact correctly reserves this as fallback | Correct sequencing |

### 4.4 Finding: next cursor gate type naming (F1, LOW)

The recommended cursor is named `QDII replacement candidate evidence gate`. The accepted gate flow pattern consistently uses plan → review → evidence → controller judgment (see Active Gate Ledger: index/QDII source recovery plan → evidence → judgment; 110020 decision plan → evidence → judgment; 017641 triage plan → evidence → judgment).

A "replacement candidate" is a **selection/scope decision** ("which fund can serve as QDII replacement?"), not a pure evidence question. The next worker could interpret "evidence gate" as authorization to immediately run CLI extraction/provenance commands without first defining: what makes a valid replacement, source safety requirements, stop conditions, and explicit no-promotion guardrails.

**Recommendation**: Either rename to `QDII replacement candidate selection plan gate` to enforce plan-before-evidence, or add an explicit scope note in the recommendation: "The first step must be a plan defining valid replacement criteria, source safety requirements, and stop conditions; evidence CLI commands only after plan review."

**Controller action**: Accept the recommendation as-is with the understanding that the next gate must still plan-before-evidence (consistent with the control doc's "decision/planning gate" language in Next Entry Point), or accept the rename.

---

## 5. Hidden Promotion / Baseline-Golden Readiness Overclaim Audit

| Check | Result |
|---|---|
| Any slot claimed as `accepted_baseline`, `scoring_ready`, `golden_ready`, or durable fixture | No |
| 110020 overclaimed | No — "not baseline/golden ready" with explicit residuals |
| 017641 overclaimed | No — terminal `disclosure_data_gap_not_baseline_ready` |
| 004393/004194 overclaimed | No — "carry-forward evaluated candidates only" |
| 006597 overclaimed | No — explicit golden blocker |
| FOF overclaimed | No — explicit data gap |
| §5 Explicit Blockers list complete | Yes — covers all six slots plus absence of fixture/golden promotion gate |
| "Why not promote" column populated for every row | Yes — all six rows have explicit rationale |
| Any language implying readiness ("mature", "stable", "verified", "clean") | No — language consistently uses accepted terminal states and negative disposition |

**Assessment**: No hidden promotion or readiness overclaim. Every slot is accurately classified with explicit no-promotion rationale. §5 provides a comprehensive blocker checklist that a future golden preflight gate must clear.

---

## 6. Prohibition Compliance Audit

| Prohibition category | Source requirement | Artifact compliance |
|---|---|---|
| New evidence / CLI commands | Control doc §Next Entry Point, artifact §6 | Only `git diff --check` run; no extraction/analyze/checklist/quality/source-probing |
| Code / test / config changes | AGENTS.md, control doc | No code changes |
| AGENTS.md / design.md changes | Artifact §6 | No truth doc changes |
| implementation-control.md changes | Control doc §Next Entry Point: "Update after controller judgment" | No premature update; worker correctly defers to controller |
| Renderer / FQ0-FQ6 / Service / CLI changes | Control doc non-goals | No product flow changes |
| Source strategy / FundDocumentRepository / source-helper | Control doc non-goals | No source changes |
| Host / Agent / Dayu | Control doc non-goals | No runtime changes |
| Baseline / golden / fixture promotion | Control doc non-goals | No promotion |
| Taxonomy / extractor implementation | Control doc non-goals | No implementation |
| GitHub mutation | Control doc non-goals | No commit/push/PR/merge |
| Entering next cursor from worker | Artifact §6 | Explicitly forbidden |

**Assessment**: All prohibitions followed. §6 is comprehensive and consistent with the control doc's Next Entry Point scope and non-goals.

---

## 7. Review Matrix Cross-Verification (Artifact §7)

| Entry | Verification against source |
|---|---|
| MiMo plan review: `PASS_WITH_FINDINGS` | Matches `release-maintenance-baseline-coverage-disposition-decision-plan-review-mimo-20260527.md` |
| GLM plan review: `PASS_WITH_FINDINGS` | Matches `release-maintenance-baseline-coverage-disposition-decision-plan-review-glm-20260527.md` |
| Controller judgment: `ACCEPTED LOCALLY` | Matches controller judgment artifact |
| Carried-forward findings correctly mapped to matrix | MiMo F1→004393/004194 inclusion, MiMo F2→owners/revisit, GLM F1→bond separate follow-up |
| "No re-review triggered" claim | Correct — artifact follows controller judgment requirements, introduces no implementation/evidence/promotion |

---

## 8. Prior Finding Resolution Check

| Prior finding | Expected resolution | Status |
|---|---|---|
| MiMo F1: 004393/004194 not in reconciliation table | Include in disposition matrix | Resolved — both rows present as `include_for_later_review` |
| MiMo F2: candidate options lack owner assignment | Assign owner and revisit for every slot | Resolved — all six slots have both |
| MiMo F3: FOF v1 requirement not pre-decided | Decide or defer with owner/revisit | Resolved — `needs_taxonomy_gate` with two-path revisit condition |
| GLM F1: bond explicit follow-up / golden blocker | Explicit separate disposition | Resolved — `needs_evidence_gate` with separate owner scoping |
| GLM F2: protect AGENTS.md/design.md | List in prohibition scope | Resolved — §6 explicitly lists both |
| GLM F3: all slots may land on `needs_evidence_gate` | Record owners and revisit, don't silently loop | Resolved — every slot has owner and revisit; diverse dispositions used |

All prior plan review findings are resolved.

---

## 9. Cross-Review Consistency Note

AgentMiMo's independent review of the same artifact returned **PASS** with no findings. This DS review independently verified all MiMo's checks and reached the same material conclusions. The three LOW/INFO findings below represent additional adversarial scrutiny beyond MiMo's review scope, not disagreements.

---

## 10. Findings

### F1 (LOW): Next Cursor Gate Type Naming

**Evidence**: The accepted gate flow pattern (Active Gate Ledger) consistently uses plan → review → evidence → controller judgment. The recommended cursor `QDII replacement candidate evidence gate` names an "evidence gate" but the actual next step involves selecting/approving replacement candidates — a scope/selection decision. A worker interpreting this as pure evidence authorization could skip the plan/review step and run CLI extraction commands without first defining valid replacement criteria, source safety requirements, or stop conditions.

**Controller-actionable recommendation**:
- Option A: Rename to `QDII replacement candidate selection plan gate` to enforce plan-before-evidence.
- Option B: Keep the name but add scope language: "The first step must be a plan defining valid replacement criteria, source safety requirements, and stop conditions; evidence CLI commands only after independent plan review."

### F2 (INFO): Disposition Rows Lack Artifact Cross-References

**Evidence**: The "Accepted evidence" column in §3 summarizes evidence states but doesn't cite the specific controller judgment artifact path that established each terminal state (e.g., `110020 evidence controller judgment`). The review matrix in §7 provides artifact-level cross-references for the plan stage, but the disposition rows' evidence claims are self-referential. A future reader tracing the evidence chain would need to consult the review matrix and then the control doc's Accepted Artifacts list to find the source.

**Controller-actionable recommendation**: No action required for this gate. Future disposition artifacts should consider citing the controller judgment artifact path in the "Accepted evidence" column (e.g., "per `release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md`").

### F3 (INFO): Worker Artifact Requires Explicit Controller Acceptance

**Evidence**: The artifact §1 correctly states "The controller remains responsible for accepting, recording, or opening any later gate." Section 7 correctly states "No re-review is triggered by this worker artifact." The artifact does not claim controller authority. However, the artifact's §4 recommendation (`QDII replacement candidate evidence gate`) and the Startup Packet next entry point both reference this gate as the current step — the control doc won't advance to the next entry point until the controller explicitly accepts this artifact and records the judgment.

**Controller-actionable recommendation**: No change to the artifact. The controller should explicitly accept (or reject) this disposition matrix, record the judgment in the control doc, and update the Startup Packet current gate / next entry point before any worker enters the recommended next cursor.

---

## 11. Validation

| Command | Expected | Result |
|---|---|---|
| `git diff --check` | exit 0 | Artifact reports exit 0 |

This review is a new file under `docs/reviews/`. No code, truth doc, control doc, or GitHub changes were made.

---

## Verdict

**PASS_WITH_FINDINGS**

The disposition matrix is materially accurate against all accepted evidence. Startup Packet replay is correct. All six slots have specific owners and revisit conditions. The next cursor recommendation follows logically from accepted evidence and first principles. No hidden promotion, readiness overclaim, or prohibition violation was found. All prior plan review findings are resolved.

Three findings (one LOW, two INFO) are provided for controller consideration. None is blocking. F1 recommends clarifying the next cursor gate type; F2 and F3 are informational documentation and process observations.
