# Plan Review: Baseline Coverage Disposition Decision Plan — AgentMiMo

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Artifact under review: `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-20260527.md`
> Gate: `baseline coverage disposition decision gate`
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Startup Packet Replay Verification

| Check | Result |
|---|---|
| Current phase `release maintenance` | Correct — matches control doc |
| Current gate in plan matches control doc | Correct — plan states `017641 manager_strategy_text public evidence triage accepted locally` which matches the control doc Startup Packet `Current gate` field |
| Next entry point in plan matches control doc | Correct — both state `baseline coverage disposition decision gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | Correct — plan references `71f1aa4 docs: accept 017641 public evidence triage`, which matches git log HEAD |
| Current truth sources replayed | Correct — lists `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, and current accepted artifacts |
| Architecture guardrail restated | Correct — Dayu four-layer target with current deterministic production path |

**Assessment**: Startup Packet replay is accurate. The plan correctly identifies this as a decision/planning gate that reconciles already accepted evidence and must not run new evidence, change code, promote fixtures, or enter the next gate.

No reconciliation artifact is needed because the plan correctly carries forward all accepted terminal states without re-running evidence.

---

## 2. Accepted Evidence Reconciliation Verification

### 2.1 `110020` / 2024 / `index_fund`

| Plan claim | Accepted artifact | Match |
|---|---|---|
| Complete eligible fallback after primary `unavailable` | Controller judgment: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete` | Yes |
| Quality gate `warn` | Evidence artifact: quality `warn` with `turnover_rate` P1 warnings | Yes |
| Terminal state `reviewed_coverage_candidate_input_accepted` | Controller judgment confirms this terminal state | Yes |
| `promotion_disposition=not_promoted` | Controller judgment: not promoted | Yes |
| Methodology/constituents evidence insufficient | Evidence artifact: carried forward as residual | Yes |
| Strict golden absent | Evidence artifact: strict golden not configured | Yes |

**Assessment**: Accurate.

### 2.2 `017641` / 2024 / `qdii_fund`

| Plan claim | Accepted artifact | Match |
|---|---|---|
| Complete eligible fallback after primary `unavailable` | Post-provenance rerun: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible` | Yes |
| `manager_strategy_text` missing with no value/anchor/locator | Public evidence triage: confirmed P0 block, no value, no anchor, no locator | Yes |
| Quality gate `block` on P0 | Evidence: `quality_gate_status=block` | Yes |
| Terminal state `disclosure_data_gap_not_baseline_ready` | Controller judgment confirms this classification | Yes |
| `promotion_disposition=not_promoted` | Controller judgment: not promoted | Yes |

**Assessment**: Accurate.

### 2.3 `006597` / 2024 / `bond_fund`

| Plan claim | Accepted artifact | Match |
|---|---|---|
| Bond-lens applicability improved | Bond-lens implementation controller judgment: equity-shaped `holdings_snapshot` excluded for exact `bond_fund` with replacement issue | Yes |
| Quality moved to `warn`, not `pass` | Implementation evidence: `warn` not `pass` | Yes |
| `bond_risk_evidence_missing.baseline_blocking=true` remains | Baseline triage evidence + controller judgments confirm | Yes |
| Residual P1 gaps: `holder_structure`, `share_change`, `turnover_rate` | Triage evidence field-level classification confirms all three as `needs_more_evidence` or `extractor_gap` | Yes |
| Positive bond-risk evidence absent | Triage evidence: no positive bond-risk evidence produced | Yes |

**Assessment**: Accurate.

### 2.4 FOF slot

| Plan claim | Accepted artifact | Match |
|---|---|---|
| Prior FOF attempts remain `data_gap` / `taxonomy_pending` | Small baseline corpus v1 controller judgment: FOF remains `data_gap` | Yes |
| QDII-FOF candidates cannot count as pure `fof_fund` | Control doc decisions: `007721` and `017970` classified as QDII-FOF, not pure FOF | Yes |
| No accepted taxonomy decision or pure FOF candidate | No standalone FOF accepted artifact exists | Yes |

**Assessment**: Accurate.

### 2.5 Reconciled blocker set

The plan's five-item reconciled blocker set is a correct aggregation of the individual evidence states. The statement "No sample may be promoted from this gate; all relevant rows remain `not_promoted`" is consistent with every accepted controller judgment.

---

## 3. Next Cursor Recommendation Verification

### 3.1 Recommended cursor

Plan recommends: `replacement/exclusion candidate selection gate for QDII/index/FOF coverage`

### 3.2 First-principles justification check

| Justification claim | Evidence | Assessment |
|---|---|---|
| Dominant problem is disposition, not evidence generation | Accepted evidence shows all four slots have accepted terminal states; no new evidence is needed to classify them | Correct |
| `110020` eligible only as reviewed index candidate input | Accepted: `reviewed_coverage_candidate_input_accepted`, `not_promoted` | Correct |
| `017641` is QDII data-gap / quality-blocked | Accepted: `disclosure_data_gap_not_baseline_ready`, `not_promoted` | Correct |
| FOF is absent | Accepted: `data_gap` / `taxonomy_pending` | Correct |
| `006597` is bond baseline-blocked | Accepted: `bond_risk_evidence_missing.baseline_blocking=true`, `not_promoted` | Correct |
| This cursor prevents repeated probing of rows with accepted terminal states | Rows already have accepted terminal states from prior gates | Correct |
| It preserves fail-closed source semantics | Stop conditions explicitly forbid source strategy weakening | Correct |
| It is narrower than golden corpus v1 (forbids promotion) | Stop conditions explicitly list promotion prohibition | Correct |
| It is broader than single FOF or bond gate | Covers QDII, index, and FOF disposition in one matrix | Correct |

### 3.3 Logical derivation check

The cursor derives from:
1. Accepted evidence shows four coverage slots with distinct terminal states.
2. Golden corpus v1 entry requires representative fund-type coverage, which is currently unmet.
3. The blocker is not "more evidence needed" but "what to do with already-classified slots."
4. A disposition gate is the minimal next step that resolves the coverage question without re-running evidence or promoting prematurely.

**Assessment**: The recommended cursor follows logically from the accepted evidence and first principles. The justification is sound.

---

## 4. Non-Entry and Prohibition Verification

### 4.1 Golden corpus v1 non-entry (Section 5)

The plan lists six explicit blockers. Each is directly supported by accepted evidence:

| Blocker | Evidence support |
|---|---|
| Coverage not source-safe and representative | Only 3 clean slots (active, enhanced-index, bond); index/QDII/FOF not covered |
| `017641` P0 quality block | Accepted `disclosure_data_gap_not_baseline_ready` |
| Pure FOF absent | `data_gap` / `taxonomy_pending` |
| `006597` baseline-blocking residuals | `bond_risk_evidence_missing.baseline_blocking=true` |
| `110020` lacks methodology/constituents sufficiency | Carried forward as residual |
| Durable fixture promotion not accepted | No fixture promotion has been accepted |

**Assessment**: Correct and complete.

### 4.2 Explicit prohibitions (Section 6)

The prohibition list covers all categories that a plan-only gate must not touch: code, renderer, FQ0-FQ6, Service/CLI, FundDocumentRepository/source strategy, Host/Agent/dayu, baseline/golden/fixture promotion, new evidence, GitHub mutation, and control doc editing.

**Assessment**: Correct and complete.

---

## 5. Candidate Options and Review Matrix

### 5.1 Option sufficiency

| Option | Entry conditions | Stop conditions | Assessment |
|---|---|---|---|
| A: Replacement/Exclusion | Defined from accepted terminal states | Promotion, source strategy, extractor/taxonomy weakening | Sufficient |
| B: FOF Taxonomy/Pure FOF | Controller chooses FOF as dominant blocker | Counting QDII-FOF as pure FOF, changing taxonomy without gate | Sufficient |
| C: Bond Positive-Risk Evidence | Accepted bond-lens state as starting point | Treating missing as N/A, entering golden while blocking | Sufficient |
| D: Durable Baseline/Golden | Prerequisites not met | Any remaining blocker | Correctly deferred as non-entry |
| E: Data Extraction Priority | Same-source evidence proves extractor gap | Indirect root cause inference | Correctly deferred |

### 5.2 Review matrix

The matrix correctly assigns:
- `AgentMiMo` for Startup Packet replay, evidence reconciliation, no-promotion discipline, stop conditions, cursor derivation.
- `AgentGLM` / `AgentDS` for first-principles challenge, missing blockers, fund-type/taxonomy logic, fail-closed semantics.
- Controller for accept/reject/select next entry point/record residual owners.

**Assessment**: Review matrix is sufficient and follows the `init-agents` / tmux multi-agent convention.

---

## 6. Findings

### F1 (Informational): Clean candidates `004393` and `004194` not explicitly listed in reconciliation table

**Evidence**: The reconciliation table (Section 2) lists four coverage slots: `110020`, `017641`, `006597`, and FOF. The accepted small baseline corpus v1 run also accepted `004393` / active and `004194` / enhanced-index as clean evaluated candidates (quality `warn`, not `scoring_ready`, not durable baseline). These two are not individually reconciled in the disposition plan's evidence table.

**Impact**: Low. The plan's focus is on blocked/incomplete slots that need disposition decisions. `004393` and `004194` are already accepted as clean candidates and do not require a disposition decision — they are carry-forward inputs to any future baseline/golden preflight. The reconciled blocker set correctly notes that only 3 clean fund-type slots exist. The omission does not create a promotion risk or a coverage miscount.

**Controller action**: Informational only. The controller may optionally add a one-line note to the disposition matrix acknowledging `004393` and `004194` as "already accepted clean candidates, retained as-is" for completeness, but this is not required for correctness.

### F2 (Informational): Candidate options lack explicit owner assignment

**Evidence**: Section 3 lists five candidate options with entry/stop conditions and expected outputs, but none assigns an explicit owner (agent or controller) for producing the expected output. Section 7 review matrix assigns review tracks, but the disposition matrix production owner is implicit.

**Impact**: Low. The review matrix and controller judgment section together make it clear that the controller assigns the next gate after review acceptance. The stop condition "Any candidate inclusion without explicit blocker disposition and review owner" partially addresses this. However, the options themselves do not name who produces the disposition matrix.

**Controller action**: Informational. The controller should assign the disposition matrix production owner when selecting the next cursor. No plan patch is required.

### F3 (Informational): Option B does not explicitly address whether FOF coverage is required for v1 baseline

**Evidence**: Option B asks "whether the baseline should require a pure FOF candidate now" but frames the expected output as either a pure FOF entry contract or an explicit "FOF deferred from golden v1" decision. The plan does not pre-analyze whether the current design mandates FOF coverage for baseline v1 or whether a 3-slot baseline (active, enhanced-index, bond) plus deferred index/QDII/FOF could be an acceptable v1 scope.

**Impact**: Low. This is a legitimate question for the disposition gate to resolve. The plan correctly defers the answer to the controller rather than prejudging it. The current `docs/design.md` lists `fof_fund` as a fund type but does not specify a minimum coverage requirement for baseline v1.

**Controller action**: Informational. The disposition gate should explicitly decide whether baseline v1 requires all five fund-type slots or can proceed with a reduced set. This is within the disposition gate's scope.

---

## 7. Scope Drift / Promotion Risk / Over-Generalization Check

| Check | Result |
|---|---|
| Scope drift | None detected. The plan stays within decision/planning boundaries and does not authorize implementation, evidence, or promotion. |
| Promotion risk | None detected. Every section explicitly states `not_promoted` and forbids promotion. Stop conditions are comprehensive. |
| Over-generalization | None detected. The plan correctly scopes to the four coverage slots with accepted terminal states and does not attempt to solve extractor, taxonomy, or source strategy problems. |
| Missing urgent blocker | None detected. The plan addresses all four coverage blockers identified in accepted evidence and does not defer a more urgent problem. |

---

## 8. Verdict

**PASS_WITH_FINDINGS**

The plan accurately replays the Startup Packet, correctly reconciles all accepted evidence (110020, 017641, 006597, FOF), derives the recommended next cursor from first principles and accepted terminal states, correctly blocks golden corpus v1 and all prohibited actions, and provides sufficient candidate options and review matrix for controller execution.

Three informational findings (F1-F3) do not require plan patches. The controller may optionally address them when selecting the next cursor and assigning the disposition matrix production owner.

---

## 9. Validation

```bash
git diff --check
```

No code changes were made by this review. The review artifact is a new file under `docs/reviews/`.
