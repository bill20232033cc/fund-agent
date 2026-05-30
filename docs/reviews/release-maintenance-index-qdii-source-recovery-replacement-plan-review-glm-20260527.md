# Plan Review: Index/QDII Source Recovery And Replacement Plan

> Reviewer: AgentGLM
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-20260527.md`
> Truth sources: `AGENTS.md`; `docs/design.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; baseline coverage recovery decision controller judgment
> Checkpoint: `1a28919`
> Scope: review only. No plan edit, no code, no commit, no push, no PR.

---

## Startup Packet Replay Verification

| Check | Plan state | Control doc / truth source | Match |
|---|---|---|---|
| Phase | `release maintenance` | `release maintenance` | ✅ |
| Gate | `index/QDII source recovery and replacement decision gate` | Next Entry Point: same | ✅ |
| Checkpoint | `1a28919` | Latest commit `1a28919` | ✅ |
| Truth sources | `AGENTS.md`; `docs/design.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals | Startup Packet Current Truth Guardrails | ✅ |
| Plan-before-evidence | §1 explicitly states evidence must not run until MiMo review, GLM review, and controller judgment pass | IC Next Entry Point: "no source recovery evidence run or candidate replacement probing may start until the next gate has its own accepted plan/review/controller judgment" | ✅ |
| Architecture | `UI -> Service -> Host -> Agent`; deterministic production path UI -> Service -> `fund_agent/fund` | Startup Packet Current Truth Guardrails | ✅ |
| Annual-report boundary | `FundDocumentRepository` or public Fund/CLI paths | AGENTS.md hard constraint | ✅ |

Startup Packet replay is correct and complete.

---

## Review Focus 1: Source Fallback Taxonomy Precision

Plan §3.1 defines two eligibility classes:

| Failure category | Plan treatment | AGENTS.md §年报来源 fallback 策略 | Controller judgment constraint | Match |
|---|---|---|---|---|
| `not_found` | `recovered_eligible` — fallback allowed | allowed | "only not_found / unavailable may be fallback-eligible" | ✅ |
| `unavailable` | `recovered_eligible` — fallback allowed | allowed | same | ✅ |
| `schema_drift` | `recovered_fail_closed` — fallback blocked | not allowed | "fail-closed" | ✅ |
| `identity_mismatch` | `recovered_fail_closed` — fallback blocked | not allowed | same | ✅ |
| `integrity_error` | `recovered_fail_closed` — fallback blocked | not allowed | same | ✅ |

The taxonomy is precise and matches all truth sources exactly. No additional failure categories are introduced. No eligible categories are missing. No fail-closed categories are silently downgraded.

§2 Current Blockers correctly identifies that `110020` and `017641` have `fallback_used=True` with unknown original upstream failure category, and therefore cannot enter the clean denominator.

**Finding F1 (Informational)**: The plan §3.1 step 4 prohibits inferring root cause from indirect symptoms, but does not explicitly address the case where a new evidence CLI run for `110020` or `017641` itself triggers Eastmoney fallback again. In that scenario, the original failure category remains unexposed and the correct classification is `unrecoverable_safe_path`. This is implicitly covered by the `unrecoverable_safe_path` definition ("public repository-backed output does not expose the original category"), but explicit mention would reduce ambiguity for the evidence worker.

---

## Review Focus 2: Evidence State Machine Auditability

Plan §3.1 and §6 define the following terminal states:

| State | Defined in §3.1 | Defined in §6 closeout | Semantics clear |
|---|---|---|---|
| `recovered_eligible` | ✅ step 3 | ✅ | Original category recovered and is `not_found` / `unavailable` |
| `recovered_fail_closed` | ✅ step 3 | ✅ | Original category recovered and is `schema_drift` / `identity_mismatch` / `integrity_error` |
| `unrecoverable_safe_path` | ✅ step 3 | ✅ | Original category not exposed via public output |
| `repository_run_failed` | ✅ step 3 | ✅ | Public CLI cannot complete |
| `not_run_no_approved_candidates` | ✅ §3.2 | ✅ | No approved replacement candidates exist |
| `replacement_verified` | — | ✅ | Replacement candidate verified |
| `excluded` | — | ✅ | Row excluded from clean denominator |

**Finding F2 (Low)**: The state `excluded` appears in the §6 closeout enumeration but is not formally defined in §3.1 or §3.2 as a distinct state. Its semantic boundary with `recovered_fail_closed`, `unrecoverable_safe_path`, and `repository_run_failed` is implicit: those three states also result in exclusion, but `excluded` appears to be a separate terminal state for when a row is excluded without a specific recovery outcome (e.g., Subgate B closes with "no approved candidates" and the original row is kept out). Recommend adding an explicit one-line definition in §3.2: `excluded` = row excluded from clean denominator by explicit decision after Subgate A/B analysis, with recorded reason.

The state machine is otherwise complete and auditable: every candidate must end in exactly one terminal state, and the closeout artifact must record which state applies per candidate.

---

## Review Focus 3: Candidate Replacement Controller Guard and Exact fund_type_slot

Plan §3.2 replacement rules:

| Rule | Present | Verifiable |
|---|---|---|
| Controller-supplied or accepted-artifact-derived provenance | ✅ | Yes — provenance must be recorded |
| No ad hoc web/search/scrape candidate discovery | ✅ | Yes — explicit prohibition |
| `repository_verified` through public Fund/CLI paths | ✅ | Yes — via CLI evidence commands |
| Exact `fund_type_slot` match: index → `index_fund`, QDII → `qdii_fund` | ✅ | Yes — explicit slot requirement |
| No `unknown`, `probe_only`, or fallback-unknown source boundary | ✅ | Yes — explicit exclusion |
| No QDII-FOF taxonomy assumption | ✅ | Yes — explicit exclusion |
| No `baseline_blocking=true` carry-over | ✅ | Yes — explicit exclusion |

The controller guard is strong. No evidence worker autonomy is granted for candidate selection. The `not_run_no_approved_candidates` terminal state correctly handles the "no candidates exist" case without pressuring the worker to search.

§5 stop conditions also mirror these constraints as hard stops, providing a redundant safety net.

---

## Review Focus 4: No Golden/Baseline Promotion and No Scope Creep

| Check | Plan statement | Truth source alignment |
|---|---|---|
| No golden fixture promotion | §5: "pressured to enter durable baseline/golden promotion" is a stop condition; §7: "golden fixture or baseline fixture changes" prohibited | IC: "Do not promote samples to durable baseline or golden answer corpus" ✅ |
| No baseline fixture promotion | §2: "Neither row is scoring_ready, accepted_baseline, or golden material" | IC: "Keep durable baseline/golden promotion blocked" ✅ |
| No renderer changes | §7 explicit | IC: "Do not modify renderer" ✅ |
| No FQ0-FQ6 changes | §7 explicit | IC: "Do not change FQ0-FQ6 quality gate behavior" ✅ |
| No Service/CLI changes | §7 explicit | IC: "Do not modify Service/CLI behavior" ✅ |
| No Host/Agent/Dayu | §7 explicit | IC: "Do not create Host/Agent packages" ✅ |
| No source strategy/helper/downloader/cache changes | §7 explicit | IC: "Do not modify FundDocumentRepository source strategy" ✅ |
| No extractor/fund_type.py changes | §7 explicit | IC: "Do not modify extractor logic, fund_type.py" ✅ |
| No direct PDF/cache/source-helper access | §5 stop condition + §7 | AGENTS.md: "生产年报 PDF 访问必须经过 FundDocumentRepository" ✅ |

Scope creep is comprehensively blocked. The plan correctly distinguishes lightweight read-only commands (`rg`, `git status`, `git diff --check`) from real repository access commands (`extraction-snapshot`, `extraction-score`, `quality-gate`), and explicitly marks the latter as evidence-gate-only, not planning-gate tools.

§1 verifier matrix confirms only this plan artifact should be attributable to this task, with unrelated pre-existing untracked files untouched.

---

## Review Focus 5: Validation/Review/Closeout Clarity

### Validation

§6 Evidence gate validation matrix covers: startup replay, source recovery, fallback taxonomy, replacement provenance/slot, output policy, baseline/golden exclusion, and closeout diff check. All pass conditions are explicit and testable.

### Review

§6 Review matrix specifies:
- AgentMiMo: product-methodology safety, clean-denominator discipline, source/fallback false-positive risk, index/QDII representative coverage
- AgentGLM: repository boundary, failure taxonomy precision, command/output discipline, no indirect evidence, no hidden implementation scope
- Controller: accept/reject/defer findings, authorize evidence run, record next residual owner

This matches the controller judgment pattern established in prior gates.

### Closeout

§6 closeout requirements:
- Tracked closeout artifact under `docs/reviews/` required ✅
- Per-candidate terminal state from the defined enumeration required ✅
- Explicit answer to "is another evidence run needed" required ✅
- Correct next state when no recovery/replacement possible: stop/exclude, not repeated probing ✅
- MiMo review, GLM review, and controller judgment required before any next gate can treat a recovered/replaced candidate as clean evidence ✅

---

## Cross-Check Against Controller Judgment Constraints

The baseline coverage recovery decision controller judgment established explicit constraints for this gate:

| Constraint | Plan compliance |
|---|---|
| Repository-safe public/product paths only | ✅ §3.1 procedure uses public CLI only; §5 blocks direct PDF/cache/source-helper |
| Preserve fail-closed semantics | ✅ §3.1 taxonomy matches exactly |
| Do not count QDII-FOF as pure FOF | ✅ §3.2 explicit prohibition |
| Do not promote durable baseline or golden | ✅ §2, §5, §7 |
| Do not modify renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, source strategy, extractors, fund_type.py, fixtures | ✅ §7 |
| Plan-before-evidence | ✅ §1 explicitly requires MiMo + GLM + controller before evidence |

All controller judgment constraints are satisfied.

---

## Findings Summary

| ID | Severity | Area | Summary | Re-review required |
|---|---|---|---|---|
| F1 | Informational | Source recovery procedure | §3.1 does not explicitly address the case where a new evidence CLI run also triggers fallback; implicitly covered by `unrecoverable_safe_path` but explicit mention would reduce evidence-worker ambiguity | No |
| F2 | Low | Evidence state machine | `excluded` terminal state used in §6 closeout but not defined in §3.1/§3.2 state enumeration; recommend one-line explicit definition | No |

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is structurally sound, scope-controlled, and truth-source-aligned. Source fallback taxonomy is precise. The evidence state machine is complete and auditable. Replacement candidate guards are controller-gated with exact fund_type_slot requirements. Golden/baseline promotion is blocked. Validation, review, and closeout are clear and match the established gateflow pattern.

Both findings are informational/low severity and do not require re-review. The plan may proceed to MiMo review and controller judgment.

---

## Checklist Confirmation (per §8)

| Question | Answer |
|---|---|
| Phase/gate/next/checkpoint and truth hierarchy replayed correctly? | Yes |
| `110020` and `017641` kept outside clean denominator while fallback category unknown? | Yes |
| Original upstream failure-category recovery required before fallback-based evidence? | Yes |
| Fail closed for `schema_drift`, `identity_mismatch`, `integrity_error`? | Yes |
| Direct PDF/cache/source-helper/downloader access prohibited? | Yes |
| `extraction-snapshot`, `extraction-score`, `quality-gate` treated as real repository evidence commands, not lightweight read-only probes? | Yes |
| Replacement candidates require controller-supplied or accepted-artifact-derived provenance? | Yes |
| `repository_verified`, exact `fund_type_slot`, no unknown fallback boundary for replacements? | Yes |
| Stops when no approved candidates, no ad hoc web/search? | Yes |
| Outputs in scratch/ignored paths, tracked artifacts to summaries/paths only? | Yes |
| Renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/source/extractor/fund-type/golden/baseline scope creep prevented? | Yes |
| Later evidence closeout artifact plus MiMo/GLM review and controller judgment required? | Yes |
