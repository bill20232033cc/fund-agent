# MVP Provider Runtime Non-Timeout Residual Disposition / Diagnostic Plan — DS Plan Review

## 1. Scope

- Role: independent plan reviewer (AgentDS), not controller, not planning worker, not reviewer for MiMo scope
- Plan under review: `docs/reviews/mvp-provider-runtime-non-timeout-residual-disposition-diagnostic-plan-20260605.md`
- Review focus (from handoff): first-principles evidence logic; same-source root-cause discipline; decision model completeness; blocker taxonomy correctness; acceptance criteria testability; whether operator deferral vs separate diagnostic gate is a controller choice, not a planning-worker assumption
- This review does not authorize live provider commands, endpoint probes, HTTP calls, retries, fallback, code/config/runtime/default changes, or any external-state operation

## 2. Sources Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md` (current gate and startup sections)
- `docs/design.md` (architecture boundaries and current implementation facts)
- Plan artifact: `docs/reviews/mvp-provider-runtime-non-timeout-residual-disposition-diagnostic-plan-20260605.md`
- Accepted controller judgment: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-controller-judgment-20260605.md`

## 3. Review Findings

### 3.1 First-Principles Evidence Logic

**Finding: PASS**

The plan correctly anchors all claims to accepted evidence from the live rerun controller judgment. Section 3 (Current Same-Run Facts) directly quotes facts from the judgment artifact: readiness passed, exactly one unchanged-default command ran, exit 1, stdout empty, retained artifact path, orchestration_status=blocked, all six body chapters failed at writer with `llm_network_error` / `ConnectError`, zero accepted drafts/conclusions. Each fact is individually traceable to the judgment.

The plan's Section 5 (Non-Goals) enumerates 12 forbidden action categories. This derives correctly from first principles: the plan knows it is classifying a provider runtime residual, not diagnosing network reachability, so it forbids any action that would cross from classification into execution. This is logically sound.

Section 4 (Gate Question) forces the routing question into exactly one of three mutually exclusive outcomes — this is correct first-principles framing. The plan does not try to answer "is the endpoint reachable" and instead correctly reframes the gate as "what evidence and control decisions are required before anyone may attempt to answer that question."

No first-principles defect found.

### 3.2 Same-Source Root-Cause Discipline

**Finding: PASS**

The plan enforces same-source root-cause discipline at multiple layers:

- A3: explicitly requires same-run evidence as the only residual root-cause basis; historical timeout artifacts must not be used as root cause for current `ConnectError`.
- Section 5: explicitly forbids "inference from historical retained artifacts as root cause for this residual."
- All current facts in Section 3 cite only the accepted live rerun judgment and the same-run retained artifact at `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/`. No fact references the prior `ReadTimeout` run at `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/`.

One subtle point: the plan's Section 3 says "the residual is not the prior all-chapter `ReadTimeout` / `llm_timeout` shape." This is a negative claim (what it is NOT) rather than a positive claim derived from the prior run. However, it is a correct observation and does not constitute using the prior run as root-cause evidence — it simply distinguishes the current residual from an earlier different residual shape. This is acceptable and does not violate same-source discipline.

The distinction between `ConnectError` and `ReadTimeout` is correctly preserved as dispositive. The plan does not conflate the two residual shapes.

### 3.3 Decision Model Completeness

**Finding: PASS with one non-blocking observation**

Section 6 presents three routes:
1. Existing evidence sufficient for operator deferral
2. Separate local-first provider endpoint/network diagnostic gate
3. Existing evidence resolves current planning question

All three routes are logically distinct and collectively exhaustive for the gate question: given the same-run evidence, what should happen next? The plan covers:
- Do nothing with the repo, hand to operator (route 1)
- Open a new diagnostic gate (route 2)
- Do nothing at all, accept the classification as final (route 3)

**Non-blocking observation (NB1):** Route 2 is described as "local-first," and the tier structure in Section 7 enforces local-only evidence before any external diagnostic. This is correct. However, route 2's description in Section 6.2 says the diagnostic gate "may collect only non-live/local evidence from accepted artifacts, retained run artifacts, typed config schema/default definitions, and secret-safe environment presence metadata." This presupposes that local evidence is available and sufficient. If the controller chooses route 2 but local evidence is insufficient (e.g., retained artifact is corrupt, per `local_artifact_incomplete` blocker), the route's internal branch to an external diagnostic gate is already specified as a separate controller-authorized step. The tier structure handles this correctly, but route 2's header description could more explicitly name the fallback path. Since Section 6.2 paragraph 2 already covers this ("If local-first evidence is insufficient and an external diagnostic is still needed, that external step must be a separate controller-authorized gate"), this is not a gap — only a minor exposition preference. Non-blocking.

**Non-blocking observation (NB2):** Section 13 recommended next entry point mentions only routes 1 and 2 in the recommendation text ("Recommended controller disposition: `open_local_first_provider_endpoint_network_diagnostic_gate` only if the controller needs a durable local diagnostic record before operator handoff; otherwise choose `operator_deferred_no_repo_action`"). Route 3 (`existing_evidence_resolves_current_planning_question`) is not mentioned in the recommendation, though it is fully defined in Sections 6.3 and 12. The recommendation is explicitly hedged ("recommended") and does not constrain controller authority, so this is non-blocking.

### 3.4 Blocker Taxonomy Correctness

**Finding: PASS**

Eight blockers are defined in Section 8. Each has: unique identifier, clear definition, evidence source, designated owner, and handling instructions.

Correctness checks:
- `provider_runtime_error_non_timeout`: matches accepted controller judgment classification exactly. Correct.
- `environment_inheritance_unproven`: acknowledges that presence-only readiness does not prove operator shell can make provider calls. This is correct and properly scoped — it says "Fix shell inheritance outside repo; no code change implied."
- `local_artifact_incomplete`: correctly identifies dependency on retained artifact existence. Correct.
- `secret_safety_blocker`: correctly maps to AGENTS.md hard constraints. Correct.
- `forbidden_scope_drift`: correctly maps to the plan's own forbidden-action list and AGENTS.md scope rules. Correct.
- `endpoint_reachability_unknown`: correctly identifies the gap between local evidence and network path diagnosis. Owner is correctly assigned to provider runtime operator / future calibration controller. Correct.
- `chapter_calibration_blocked`: correctly tied to zero accepted drafts/conclusions. Correct per startup packet: "Chapter acceptance calibration remains unauthorized because no body chapter has an accepted draft/conclusion."
- `provider_default_change_requested`: correctly requires a separate reviewed implementation/config gate. Correct.

Blocker completeness: I considered whether any additional blocker is needed:
- "Controller deadlock" — controller cannot decide between options. This is a process concern, not a technical blocker. Not needed.
- "Reviewer unavailability" — if MiMo or DS cannot review. AGENTS.md handles this with "at least two independent reviews (unless recording reviewer unavailability)." Not a plan-level blocker.
- "Retained artifact format drift" — if the artifact exists but has unexpected schema. Covered by `local_artifact_incomplete` (missing/corrupt safe fields).

No missing blockers. The taxonomy is correct and complete.

### 3.5 Acceptance Criteria Testability

**Finding: PASS**

All 12 acceptance criteria (A1-A12) follow the same structure: ID | Criterion | Required evidence | Blocking failure. Each criterion has:
- A specific, falsifiable condition
- A concrete evidence requirement to verify it
- A blocking failure condition that would cause it to fail

Testability verification:
- A1: "Plan states `heavy` and rationale" → checkable by reading Section 1. Blocking: "classified as `fast_path` or unreasoned `standard`" → unambiguous.
- A2: "Plan distinguishes separate diagnostic gate vs operator deferral vs existing-evidence resolution" → checkable by reading Section 6. Blocking: "assumes a diagnostic command is already authorized" → unambiguous.
- A3: "Current facts cite accepted live rerun judgment and retained artifact" → checkable by verifying Section 3 source references. Blocking: "historical timeout artifacts used as root cause" → unambiguous.
- A4-A12: similar verifiability.

Each criterion can be objectively evaluated by a reviewer without needing to interpret intent or infer missing information. This is well-designed.

### 3.6 Operator Deferral vs Separate Diagnostic Gate: Controller Choice Verification

**Finding: PASS**

This is the specific question posed by the review handoff. I examined the plan for any language that pre-decides or assumes which route the controller should take.

Evidence that the plan preserves controller choice:

1. Section 6.1: "Choose this route **when controller agrees** that the current accepted evidence already proves..."
2. Section 6.2: "Choose this route **only if controller needs** a durable diagnostic artifact..."
3. Section 6.3: "Choose this route **when the controller decides** the accepted judgment already supplies..."
4. Section 11 (Controller Judgment Requirements): "Controller judgment after reviews must explicitly state... one chosen disposition: [three options listed]"
5. Section 12 (Residual Owners): lists all three dispositions with separate owners and next handling instructions
6. Section 13: uses "Recommended controller disposition" — the word "recommended" explicitly signals optionality

At no point does the plan say "the controller should choose X" or "X is the correct disposition." The three routes are presented as equal options in Section 6. The recommendation in Section 13 is explicitly conditional ("only if... otherwise") and hedged ("recommended").

The plan does not assume, pre-decide, or bias the controller toward any specific disposition. The planning worker correctly stops at framing the decision and leaves the choice to the controller.

## 4. Additional Observations

### 4.1 Classification Rationale

The plan classifies itself as `heavy` with rationale citing AGENTS.md. The rationale is: "it controls provider runtime residual routing after a live provider evidence gate... high-impact runtime/release-readiness adjacent decisions." This aligns with the startup packet's `Next gate classification: heavy` and AGENTS.md's criteria for `heavy` gates. Correct.

### 4.2 Scope Discipline

The plan's Section 1 explicitly states "This plan itself authorizes no live provider command, endpoint reachability probe, curl, handwritten HTTP, PASS-only timing probe, retry, deterministic fallback, provider override, runtime/default change, source change, or external-state operation." This matches the hard constraints in the review handoff. The plan does not accidentally authorize any forbidden action.

### 4.3 Tier Structure Consistency

Section 7 (Evidence Allowed For A Future Diagnostic Gate) defines four tiers. Tier 0-2 are explicitly allowed; Tier 3 is explicitly not authorized by this plan. The tier structure correctly:
- Prioritizes already-accepted evidence (Tier 0)
- Prefers local artifact inspection (Tier 1) before code/config inspection (Tier 2)
- Separates external diagnostics (Tier 3) into a later gate
- Specifies forbidden actions within each tier

One observation: Tier 1 (Section 7.2) says allowed actions include "read `manifest.json`, `summary.json`, and per-chapter JSON." These files exist under the retained artifact path but are not explicitly referenced in the accepted controller judgment. The plan is defining what a FUTURE diagnostic evidence worker may do, not what this plan review requires. This is within planning scope and does not create dependency on unverified files. Non-blocking.

### 4.4 Reviewer Handoff Actionability

Section 10 defines distinct MiMo and DS review focus areas. Each focus area maps to concrete, independently verifiable concerns. Verdict shapes (PASS / NEEDS_FIX / BLOCKED) are defined with clear semantics. This is actionable for both reviewers.

## 5. Verdict

**Verdict: PASS**

No blocking findings. The plan:
- Reasons from first principles and anchors all claims to accepted evidence
- Enforces same-source root-cause discipline consistently across multiple sections
- Presents a complete, three-route decision model
- Defines a correct and complete blocker taxonomy of eight blockers
- Provides 12 individually testable acceptance criteria
- Correctly frames operator deferral vs separate diagnostic gate as a controller choice; the planning worker makes recommendations but does not assume or pre-decide

### Non-Blocking Observations Summary

| ID | Section | Description |
|----|---------|-------------|
| NB1 | 6.2 | Route 2 header could more explicitly name the fallback from local-first to external diagnostic, but the fallback is already described in paragraph 2 |
| NB2 | 13 | Recommendation text mentions routes 1 and 2 but not route 3; route 3 is fully defined in Sections 6.3 and 12, and the recommendation is explicitly hedged |

Neither observation affects the plan's correctness, completeness, or safety.

## 6. Residual Remarks

- The plan's primary value is in defining what must NOT happen before a controller judgment. This defensive framing is appropriate for a `heavy` gate that touches provider runtime residual routing.
- The tier structure in Section 7, while defined for a future diagnostic gate, also serves as an implicit checklist for the plan reviewer: it demonstrates the plan author has thought through the evidence dependency chain without accidentally authorizing execution.
- The plan correctly inherits all constraints from the startup packet's "Next entry point" field: no retry, no reclassification as endpoint availability, no second live command, no Chapter acceptance calibration, no provider/default/runtime/budget changes.
