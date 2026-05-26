# Plan Review: bond-lens contract + baseline coverage recovery plan

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md` v2.2 current design, `docs/implementation-control.md` Startup Packet / Next Entry Point / Open Residuals / Active Gate Ledger
> Review type: adversarial plan review

---

## 0. Verification

| Check | Result |
|---|---|
| `git diff --check` | pass, exit 0 |
| Scope file check | only the plan artifact is new; pre-existing untracked files are unrelated |
| Plan artifact path matches review target | confirmed |

---

## 1. Review Questions Against Checklist

### Q1: Does the plan correctly reconcile accepted `share_change` implementation with real `006597` still being quality-gate blocked?

**Finding: PASS**

Plan §2 explicitly states that `share_change` focused implementation was accepted because it correctly refused to guess when ambiguity existed, and that `006597` remains quality-gate `block` because `share_change` is still `missing` with explicit ambiguity note, P1 failed fields include `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, missing-field rate is 35.7% (above FQ4 block threshold). The plan correctly separates "implementation was correct" from "row is not baseline-ready." No silent quality-gate weakening detected.

### Q2: Is `holdings_snapshot` as fund-type-dependent for `bond_fund` the right first-principles decision?

**Finding: PASS**

Cross-verified against `extraction_score.py`: `_record_is_covered` currently requires `top_holdings_status` + `top_holdings_source` matching stock-centric pairs (`TOP_HOLDINGS_COVERED_STATUS_SOURCE_PAIRS`). There is no `bond_fund` branch. This means a bond fund with complete bond holdings data would still score as uncovered because the whitelist is equity-shaped. The plan's diagnosis in §3.1 is accurate: requiring stock top-ten as P1 evidence for a bond fund is a category error, and marking the whole slot N/A would lose bond risk evidence. The recommended approach — fund-type-dependent contract with explicit `bond_holdings_risk_evidence` — is the correct first-principles resolution.

### Q3: Does the proposed `bond_holdings_risk_evidence` contract cover the required evidence groups?

**Finding: PASS**

Plan §3.3 defines six evidence groups: duration/rate risk, credit risk, leverage/liquidity, asset allocation/holdings mix, drawdown/stress evidence, redemption/share pressure. Each maps to bond lens chapters (Chapter 4/5/6) per `docs/design.md` §5.4.3 matrix. The minimum-pass options (at least one direct anchor + explicit gaps, or explicit `insufficient` status) prevent both over-requirement and silent pass.

### Q4: Are `allowed_na_reason`, failure behavior, and issue taxonomy explicit enough?

**Finding: PASS**

Plan §3.4 defines narrow N/A reasons with explicit "not allowed" column. §3.5 defines fail-closed behavior for unknown/conflicted fund types. §3.6 defines eight issue categories with severity. §3.7 separates design-only from minimal implementation candidates. No silent quality-gate weakening path exists in the design.

### Q5: Does Gate C preserve current FQ0-FQ6 semantics while allowing bond-aware field applicability?

**Finding: PASS**

Plan §6 Gate C explicitly lists forbidden changes: extractor logic, renderer, FQ0-FQ6 thresholds/severity semantics, Service/CLI, source strategy/helpers, golden/baseline fixtures. The allowed range is narrow: `extraction_score.py` and focused tests. Stop conditions include "any non-bond fund field priority/coverage behavior changes unexpectedly" and "006597 becomes pass/warn only because evidence is suppressed without replacement bond issue." This is a safe containment boundary.

### Q6: Does the plan keep `turnover_rate` and `holder_structure` as `needs_more_evidence`?

**Finding: PASS**

Plan §5 explicitly keeps both as `needs_more_evidence` with the note "do not infer applicability or source absence from public missing output; no implementation from absence." This aligns with the triage evidence classification and the hard constraint against logic/data same-source violation.

### Q7: Does the plan keep `investor_return` and `nav_data` in future work?

**Finding: PASS**

Plan §5 classifies `investor_return` as `score_contract_gap` (future fallback/projection evidence-contract work, not bond N/A, not immediate P1 blocker) and `nav_data` as `score_contract_gap` for anchor/provenance (future external evidence provenance work, do not modify annual-report extractor). Both are correctly excluded from the current gate.

### Q8: Does the source recovery plan preserve fallback fail-closed semantics for `110020` and `017641`?

**Finding: PASS**

Plan §4.1 explicitly requires: recover original upstream failure category before durable baseline consideration; allow fallback only for `not_found` or `unavailable`; preserve fail-closed for `schema_drift`, `identity_mismatch`, `integrity_error`; do not weaken fallback semantics or patch source helpers. Stop conditions include "recovered failure category is fail-closed" and "only Eastmoney fallback can fetch the document without a safe upstream category."

### Q9: Does the FOF plan avoid counting QDII-FOF as pure FOF without a taxonomy gate?

**Finding: PASS**

Plan §4.2 explicitly states: "Do not count QDII-FOF as pure `fof_fund` coverage unless a separate taxonomy/precedence gate accepts that behavior." Selection criteria require "does not primarily classify as QDII under current accepted precedence." Candidates that become QDII-FOF are recorded as `taxonomy_pending`, not clean FOF. If no pure FOF can be found, FOF stays as `data_gap`.

### Q10: Are file ranges, stop conditions, and validation commands narrow enough?

**Finding: PASS**

Six gates (A-F) are defined with explicit entry conditions, allowed files, validation commands, and stop conditions. Gate C limits files to `extraction_score.py` + focused tests + optional README. Gate D limits to tracked evidence artifacts + scratch output. Gate E limits to plan/evidence artifacts. Each gate has clear stop conditions that halt on scope violation.

---

## 2. Adversarial Challenges

### Challenge 1: Could Gate C implementation accidentally weaken non-bond fund scoring?

**Assessment: Low risk, adequately mitigated.**

The plan requires "active fund missing `holdings_snapshot` still behaves as before; index/enhanced behavior stays unchanged" as focused test cases. The existing `_is_non_applicable_index_quality_record` pattern in `extraction_score.py` provides a safe model for fund-type-aware filtering. However, the plan does not explicitly name the implementation pattern (analogous helper function vs. inline branch in `_scorable_records`). This is a minor gap — the implementation notes in §8 suggest "add a fund-type-aware path in `_scorable_records()` or an adjacent helper" which gives the implementation worker flexibility.

**Severity: informational**

### Challenge 2: Is the minimum pass for `bond_holdings_risk_evidence` too permissive?

**Assessment: Adequately constrained.**

The plan defines two minimum-pass options: (1) at least one direct annual-report anchor from duration/credit/leverage/asset-allocation plus explicit data gaps, or (2) explicit `bond_risk_evidence_status="insufficient"` that still emits a quality-gate issue. Option 2 could allow a bond fund to pass scoring while having zero bond risk evidence. However, the plan explicitly states this "removes the equity-shaped `holdings_snapshot` false blocker but still emits a report-quality / quality-gate issue under a bond-specific taxonomy" — so it passes scoring but not silently; it generates an observable issue. The FQ0-FQ6 semantics are unchanged, and the issue taxonomy in §3.6 ensures traceability.

**Severity: informational**

### Challenge 3: Could `investor_return` N/A semantics leak into bond funds?

**Assessment: Blocked by design.**

Plan §3.4 explicitly states "no bond N/A in this gate" for `investor_return`. The plan treats it as `score_contract_gap` requiring future fallback/projection work, not as bond-inapplicable. This prevents the silent weakening that would occur if bond funds could skip investor-return evidence.

**Severity: no finding**

### Challenge 4: Does the plan address the case where `classify_fund_type()` returns a different type for 006597 after future changes?

**Assessment: Adequately handled.**

Plan §3.5 states: "If fund type is unknown or conflicted: fail closed, keep generic required fields." This means any future change to `classify_fund_type()` that reclassifies 006597 would not silently skip bond-specific requirements — it would fall back to the conservative generic path.

**Severity: no finding**

### Challenge 5: Is the `score_contract_gap` issue taxonomy category well-defined?

**Assessment: Minor gap.**

Plan §3.6 defines `score_contract_gap` as "Existing score/evidence model cannot represent valid non-annual-report or derived evidence" with severity "future contract work." This is correct but could benefit from a clearer boundary: when does a `score_contract_gap` become a blocking issue vs. an informational residual? The plan defers this to future gates, which is safe but means the severity classification is intentionally loose.

**Severity: informational**

---

## 3. Scope Guard Compliance

| Hard constraint | Plan compliance |
|---|---|
| No renderer changes | PASS — §7 explicitly forbids |
| No FQ0-FQ6 weakening | PASS — §6 Gate C stop conditions + §7 |
| No Service/CLI changes | PASS — §7 explicitly forbids |
| No Host/Agent/dayu work | PASS — §7 explicitly forbids |
| No source strategy/helper changes | PASS — §7 explicitly forbids |
| No extractor logic changes | PASS — §7 explicitly forbids (Gate C only touches scoring, not extraction) |
| No golden/baseline promotion | PASS — §4.3 explicitly blocks |
| No extra_payload | PASS — §7 explicitly forbids |
| No GitHub mutation | PASS — §7 explicitly forbids |
| No silent quality-gate weakening | PASS — §3.4/§3.5/§3.6 define explicit failure paths |
| No QDII-FOF as pure FOF | PASS — §4.2 explicitly blocks |

---

## 4. Verdict

**PASS**

No material findings. All ten review questions are satisfied. Five adversarial challenges were evaluated: three produced no finding, two produced informational observations that do not block plan acceptance. The plan correctly diagnoses the bond-lens contract gap, proposes a sound first-principles resolution, preserves all hard constraints, and defines narrow gates with explicit stop conditions. The plan is code-generation-ready for Gate A (plan review) and lays safe groundwork for subsequent gates.

Re-review is **not required** unless the controller narrows scope or identifies a plan revision.

---

## 5. Material Findings Summary

No material findings. Two informational observations:

1. Gate C implementation pattern (analogous helper vs. inline branch) is left to implementation worker discretion — acceptable given §8 guidance, but worth noting for implementation review.
2. `score_contract_gap` severity is intentionally loose (deferred to future gates) — safe but means current gate cannot fully classify blocking vs. informational for these gaps.
