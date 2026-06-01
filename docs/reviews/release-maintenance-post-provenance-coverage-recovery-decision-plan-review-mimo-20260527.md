# Plan Review: Post-Provenance Coverage Recovery Decision Plan — AgentMiMo

> Reviewer: AgentMiMo, independent plan reviewer (not controller, not implementer)
> Date: 2026-05-27
> Review target: `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-20260527.md`
> Truth sources: `AGENTS.md`; `docs/design.md` (v2.2) current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts listed below

## Review Scope

1. Reconciliation: plan correctly recognizes golden answer corpus v1 cannot be entered directly.
2. Evidence table: only accepted evidence referenced; terminal states and `not_promoted` correctly explained.
3. Recommended next two gates: minimal, no missing blockers.
4. Scope creep: no code implementation, renderer, FQ0-FQ6, Service/CLI, source strategy, Host/Agent/dayu, fixture, golden, baseline promotion.
5. Acceptance matrix and stop conditions: sufficient to protect product path.

## Accepted Artifacts Verified

| Artifact | Accepted status | Evidence |
|---|---|---|
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | Accepted; MiMo PASS + GLM PASS | implementation-control.md Current Gate Accepted Artifacts table |
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md` | Accepted evidence worker artifact | implementation-control.md Current Gate Accepted Artifacts table |
| `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md` | Accepted locally; MiMo PASS + GLM PASS_WITH_FINDINGS (non-blocking) | implementation-control.md Current Gate Accepted Artifacts table |

## Startup Packet Replay Alignment

| Field | Plan states | Control doc states | Aligned? |
|---|---|---|---|
| Current phase | `release maintenance` | `release maintenance` | Yes |
| Current gate | `source provenance post-implementation bounded evidence rerun accepted locally` | `source provenance post-implementation bounded evidence rerun accepted locally` | Yes |
| Current requested gate | `post-provenance coverage recovery decision plan/review gate` | Next entry point: `post-provenance coverage recovery decision plan/review gate` | Yes |
| Branch | not explicitly stated (artifact scope) | `codex/local-reconciliation` | N/A — plan is branch-agnostic at artifact level |

Startup Packet replay is correctly aligned with implementation-control.md truth.

## Finding 1: Reconciliation with Golden Answer Corpus v1

**Verdict: CORRECT**

The plan explicitly states (line 38-39): "This gate should not enter user-facing long-term `golden answer corpus v1` directly."

Evidence chain:
- The accepted small baseline corpus v1 run controller judgment (line 47-48) explicitly concluded: "Gate 4 is accepted as an evidence run, but it does **not** satisfy entry conditions for `golden answer corpus v1`."
- Reasons cited: clean evaluated coverage only 3 candidates / 3 fund-type slots (below 5-10 target), one evaluated clean candidate quality-gate blocked, index/QDII fallback-blocked, pure FOF data-gap residual.
- The plan's Candidate E (golden entry gate) lists six unmet prerequisites, all traceable to accepted evidence.
- The plan correctly positions itself as a "post-provenance coverage recovery decision gate" that "converts newly accepted provenance evidence into ordered next gates, without treating review eligibility as promotion."

No finding.

## Finding 2: Evidence Table — Accepted Evidence and Terminal States

**Verdict: CORRECT**

### Row-by-row verification:

| Sample | Plan terminal state | Source | Verified? |
|---|---|---|---|
| `110020` / 2024 | `provenance_eligible_for_next_review` | Controller judgment line 28: `terminal_state = provenance_eligible_for_next_review` | Yes |
| `017641` / 2024 | `quality_blocked_after_provenance` | Controller judgment line 29: `terminal_state = quality_blocked_after_provenance` | Yes |
| `004393` / 2024 | clean candidate, not `scoring_ready` | Small baseline CJ: "quality gate `warn`"; "no sample is `scoring_ready`" | Yes |
| `004194` / 2024 | clean candidate, not `scoring_ready` | Small baseline CJ: "quality gate `warn`"; "no sample is `scoring_ready`" | Yes |
| `006597` / 2024 | evidence candidate with baseline-blocking residuals | Small baseline CJ: "quality-gate `block`"; bond-lens CJ: `bond_risk_evidence_missing.baseline_blocking=true` | Yes |
| `007721` / 2024 | `data_gap` / `taxonomy_pending` | Small baseline CJ: "FOF remains a `data_gap`" | Yes |
| `017970` / 2024 | `data_gap` / `taxonomy_pending` | Small baseline CJ: "FOF remains a `data_gap` / taxonomy residual" | Yes |

### Promotion disposition verification:

All samples are `not_promoted`. This is verified against:
- Controller judgment line 33: "No sample is promoted to durable baseline, clean denominator, fixture, or golden corpus in this gate."
- Small baseline CJ line 47: "it does **not** satisfy entry conditions for `golden answer corpus v1`."
- Bond-lens implementation CJ: `006597` quality gate is `warn`, not `pass`; `baseline_blocking=true`.

No finding.

## Finding 3: Recommended Next Two Gates — Minimal and No Missing Blockers

**Verdict: CORRECT**

### Gate ordering:

1. `110020 reviewed coverage candidate decision gate` — consumes newly source-recovered index row
2. `017641 manager_strategy_text extraction/quality triage gate` — consumes newly source-recovered QDII row

### Minimality justification (from plan, verified):

- These two gates directly consume the new accepted provenance evidence and avoid reopening already-settled source propagation work. **Verified**: source provenance implementation and rerun are complete; no source work is reopened.
- `110020` is the only newly source-recovered row that is quality `warn`. **Verified**: controller judgment confirms `110020` quality `warn`, `017641` quality `block`.
- `017641` is the paired QDII row whose source blocker is resolved but whose quality blocker is precise and P0. **Verified**: controller judgment line 31: "`017641` is source-provenance complete but still quality-gate `block` due to missing `manager_strategy_text`."
- FOF and bond remain real blockers but were not changed by the provenance rerun. **Verified**: the bounded evidence rerun only covered `110020` and `017641`.

### Missing blockers check:

- `110020` entry conditions require accepted provenance tuple remains complete and quality `warn`. These are verified from accepted evidence.
- `017641` entry conditions require accepted provenance tuple remains complete and quality blocker is explicitly `manager_strategy_text` FQ2/FQ3 P0. **Verified**: rerun artifact line 49 shows `FQ2 block for manager_strategy_text`, `FQ3 block for manager_strategy_text`.
- FOF and bond are correctly listed as deferred later gates with clear rationale.
- No missing blocker identified for the two recommended gates.

### Candidate C (pure FOF) and Candidate D (bond) check:

The plan correctly defers these as "Optional later gates, not recommended as the immediate next step" with deferral rationale:
- FOF: "not unlocked by the provenance rerun; needs approved pure FOF candidates or taxonomy design scope."
- Bond: "current accepted evidence already says it is a separate bond-risk / P1 residual path."

Both deferrals are supported by accepted evidence. No finding.

## Finding 4: Scope Creep Check

**Verdict: NO SCOPE CREEP**

### Forbidden scope in plan (lines 29-34):

| Forbidden item | Plan violates? | Evidence |
|---|---|---|
| No code implementation | No | Plan is purely decision/planning |
| No renderer, FQ0-FQ6, Service/CLI | No | No production behavior changes proposed |
| No Host/Agent/dayu | No | No Host/Agent packages or Dayu runtime mentioned |
| No source strategy, fallback semantics | No | Plan explicitly states "do not change source code" and "do not change `FundDocumentRepository`, source strategy, source helper fallback semantics" |
| No baseline/golden/fixture promotion | No | Plan states "Every row remains `not_promoted` until a later dedicated baseline/golden promotion gate" |
| No GitHub mutation, push, PR | No | Plan states "Do not run GitHub mutations, push, create PR" |

### Forbidden scope in recommended gates:

| Gate | Forbidden items | Plan violates? |
|---|---|---|
| `110020` gate | No durable baseline/golden/fixture promotion; no source strategy, FQ0-FQ6, renderer, Service/CLI, Host/Agent/dayu; no direct cache/PDF/source-helper inspection | No |
| `017641` gate | No extractor implementation; no quality-gate weakening or P0 reclassification; no QDII subtype redesign or `fund_type.py` changes | No |

### Boundary check against AGENTS.md and design.md:

- Four-layer boundary (`UI -> Service -> Host -> Agent`): not violated (no architecture changes).
- `FundDocumentRepository` as sole document access: not violated (no direct file system access).
- Source fallback fail-closed semantics: not violated (no source strategy changes).
- `pyproject.toml` engineering baseline: not affected (no code changes).
- Design.md plan review boundary checks (§12): all pass — no non-goal violation, no four-layer boundary breach, no production path change.

No finding.

## Finding 5: Acceptance Matrix and Stop Conditions

**Verdict: SUFFICIENT**

### Acceptance matrix review:

| Gate | Required artifact | Required review | Validation | Stop condition |
|---|---|---|---|---|
| `110020` gate | New plan artifact with date suffix | MiMo + GLM independent reviews + controller judgment | Reconcile provenance state with quality `warn`; list unresolved gaps; prove no promotion | Stop if plan attempts durable baseline/golden promotion, source strategy changes, or direct cache/PDF inspection |
| `017641` gate | New plan artifact with date suffix | MiMo + GLM independent reviews + controller judgment | Classify next action from public quality evidence | Stop if plan weakens P0/FQ2/FQ3, implements extractor changes, or infers root cause without same-source evidence |

### Stop condition sufficiency:

- `110020` stop condition covers: durable baseline/golden promotion (prevents premature promotion), source strategy changes (prevents production behavior change), direct cache/PDF inspection (prevents private evidence access). **Sufficient**.
- `017641` stop condition covers: P0/FQ2/FQ3 weakening (prevents quality gate degradation), extractor changes (prevents implementation in decision gate), root cause inference without same-source evidence (prevents logic/data同源 violation per AGENTS.md hard constraint). **Sufficient**.

### Review requirement:

Both gates require MiMo + GLM independent reviews and controller judgment. This matches the multi-agent flow specified in implementation-control.md next entry point: "must use init-agents / tmux multi-agent flow." **Correct**.

No finding.

## Additional Observations

### Observation 1: Validation evidence specificity for Candidate A (low severity)

Candidate A (line 78) states "Reuse accepted public provenance rerun artifact" without specifying the exact artifact path. The accepted artifacts section at the top of the plan does list the correct paths, and the gate's required artifact is a new plan document that would reference the correct paths. This is not a material issue but future gate plans should cross-reference the exact artifact path for traceability.

### Observation 2: Bond-lens evidence reference (low severity)

The evidence table for `006597` references "accepted baseline/bond-lens controller judgments" as the source artifact. The specific artifact paths are not listed in the plan's accepted artifacts section, but they are recorded in implementation-control.md's accepted artifacts table. This is acceptable for a decision plan but would need explicit paths in an implementation plan.

### Observation 3: Candidate D entry condition clarity (informational)

Candidate D (line 128-130) uses `006597` quality gate status `warn` and `bond_risk_evidence_missing.baseline_blocking=true` as entry conditions. Both values are verified from accepted bond-lens implementation evidence. The entry conditions are correctly stated.

## Boundary Check Summary (per design.md §12)

| Check | Result |
|---|---|
| §1.3 非目标 violation | None |
| `UI -> Service -> Host -> Agent` four-layer boundary | Preserved |
| `FundDocumentRepository` as sole document access | Preserved |
| No Host/tool loop/LLM writing in deterministic path | Preserved |
| `pyproject.toml` engineering baseline | Not affected |
| License / repo hygiene | Not affected |
| Dayu four-layer as rule truth source | Preserved |
| Success signal verifiable | Yes — both gates have explicit validation criteria and stop conditions |

## Conclusion

**PASS**

The plan correctly reconciles the current state: golden answer corpus v1 cannot be entered directly. The evidence table references only accepted evidence with correct terminal states and `not_promoted` dispositions. The two recommended next gates are minimal, directly consuming newly accepted provenance evidence without reopening settled work, and have no missing blockers for their entry conditions. FOF and bond are correctly deferred as parallel residuals. No scope creep into forbidden areas. The acceptance matrix requires dual independent reviews and controller judgment, and stop conditions are sufficient to protect the product path.
