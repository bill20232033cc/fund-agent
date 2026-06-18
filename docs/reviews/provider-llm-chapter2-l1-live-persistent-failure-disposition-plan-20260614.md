# Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Plan

Date: 2026-06-14

Role: AgentCodex planning/disposition worker

Gate: `Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

Primary recommendation: `deterministic Chapter 2 gap rendering planning gate`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact classifies why exact `004393 / 2025` still first-fails Chapter 2 L1 after accepted no-live prompt strengthening, then recommends the next narrow gate.

This is planning/disposition only. It does not authorize source, test, runtime, README, design, startup packet, implementation-control, provider default, repair budget, annual-period LLM route, Docling, release/readiness, PR, push, merge, source policy or fallback changes.

EID annual-report access remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

No report bodies, prompt bodies, provider request/response payloads, PDF/source/cache bodies or final report body were read for this disposition. The classification below uses only control truth and accepted controller artifacts, including safe metadata already quoted by those artifacts.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, fail-closed posture, EID single-source/no-fallback boundary and planning-worker constraints. |
| `docs/current-startup-packet.md` | Current active gate, accepted checkpoint sequence and required `NOT_READY` posture. |
| `docs/implementation-control.md` | Current control truth: live-persistent Chapter 2 L1 failure after checkpoint `648c439`; no-code disposition/root-cause planning only. |
| `docs/design.md` relevant Route C / Host-Agent / fail-closed / source-policy sections | Confirms Route C is explicit opt-in, incomplete LLM result fails closed without deterministic fallback, repair budget calibration and full runtime expansion remain future gates, and EID single-source remains current policy. |
| `docs/reviews/provider-llm-chapter2-l1-live-regression-disposition-controller-judgment-20260614.md` | Establishes prior Chapter 2 acceptance was repair-dependent, current Chapter 2 failure is pre-provider/output-sensitive, and next diagnostic had to explain repair mechanics without live repetition. |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepts that checklist propagation and L1 fail-closed behavior are current-state proven; rejects missing checklist propagation as the main explanation; preserves uncertainty between ignored checklist and weak checklist wording. |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-controller-judgment-20260614.md` | Accepts the narrow no-live prompt strengthening, unchanged `_repair_context_prompt()`, unchanged repair budget, stable Chapter 2 headers and no-live validation. |
| `docs/reviews/provider-llm-chapter2-l1-prompt-strengthening-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepts the post-strengthening live failure: exact `004393 / 2025` still first-fails Chapter 2 with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`; repair worsened L1 count from 1 to 2. |

Earlier artifacts were not read because the required controller judgments provide enough accepted facts for this planning disposition.

## 3. Accepted Facts

| Fact | Accepted disposition |
|---|---|
| Exact `004393 / 2025` remains the current live sample under discussion. | Accepted. Do not generalize to broader live/provider acceptance. |
| Prior Chapter 2 live acceptance at checkpoint `765c616` was repair-dependent, not first-attempt clean. | Accepted. It is single-run evidence, not stability proof. |
| Later live evidence at checkpoint `2f8dce9` returned Chapter 2 to a first-failed blocker after Chapter 3 policy changes. | Accepted. |
| No-live diagnostic evidence accepted that the Chapter 2 L1 repair checklist still reaches writer prompt assembly and that L1 fail-closed behavior remains valid. | Accepted. Missing checklist propagation is not the primary current explanation. |
| The narrow no-live fix accepted at `ee65f69` strengthened only Chapter 2 prompt contracts, kept `_repair_context_prompt()` unchanged, kept repair budget unchanged and passed the three-file no-live suite. | Accepted. |
| Post-strengthening live evidence at `648c439` still first-fails Chapter 2 with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`. | Accepted. |
| Post-strengthening live metadata shows Chapter 2 attempt-level L1 count went from 1 on the initial attempt to 2 on the repair attempt, with no required-output-marker miss. | Accepted. The repair did not converge. |
| The accepted controller judgment explicitly says this is not an implementation acceptance failure for the no-live prompt contract. | Accepted. Do not route directly to "fix the accepted no-live implementation" without a narrower product decision. |
| The current evidence does not prove whether the live model read and ignored the checklist, whether the checklist wording remains too weak, or whether body-level facts are insufficient. | Accepted residual. The current gate did not authorize body or payload reads. |
| Repair budget calibration is an open residual, but the current default of one regenerate is not product-calibrated and was not authorized for change in these gates. | Accepted. |
| Release/readiness, full LLM path readiness, PR/release state and broader live quality remain unproven. | Accepted. Preserve `NOT_READY`. |

## 4. Hypothesis Disposition Table

| Hypothesis | Disposition | Evidence basis | Planning consequence |
|---|---|---|---|
| Live model noncompliance despite prompt strengthening | `SUPPORTED_AS_OPERATIONAL_CLASSIFICATION_NOT_MECHANISTIC_PROOF` | Checklist propagation is no-live proven; prompt strengthening was accepted; exact live repair still worsened L1 from 1 to 2. However, body/payload reads were not authorized, so the exact mechanism remains unproven. | Treat prompt-only convergence as unreliable for this sample. Do not keep stacking prompt wording changes as the primary route unless a future plan proves a narrower contract mismatch. |
| Insufficient facts or anchors causing a legitimate fail-closed gap | `POSSIBLE_NOT_PROVEN` | L1 numerical closure failure may reflect inability to safely support a numeric claim, but safe metadata does not expose whether the required facts/anchors are absent, insufficient, or ignored. | The next gate should handle this as a product-safe output state: render an explicit Chapter 2 evidence gap/minimum-verification path when closure cannot be deterministically supported. |
| Auditor versus repair instruction mismatch not captured by no-live tests | `POSSIBLE_SECONDARY_NOT_PRIMARY` | Implementation judgment records an accepted residual that auditor wording still uses older terminology, while no-live tests preserve current deterministic output and accept safe gap/minimum-verification behavior. Current evidence does not prove a direct auditor/repair mismatch. | Include auditor/repair contract alignment in the next plan's validation matrix, but do not route to a narrow code fix as the primary next gate. |
| One-repair budget insufficiency as implementation or product-calibration issue | `DEFERRED` | The live run exhausted one repair attempt, but the repair moved L1 count in the wrong direction. More attempts might sample a better output, but this would not prove deterministic safety and repair budget calibration is explicitly a separate future gate. | Do not choose repair budget calibration as the immediate gate. Keep it deferred until deterministic gap behavior is specified or rejected. |
| Deterministic gap/minimum-verification rendering as a better product behavior | `PRIMARY` | No-live evidence already accepts fail-closed L1 behavior and a safe gap/minimum-verification case without concrete unsupported percentages. Live evidence shows prompt/repair alone does not reliably converge for exact `004393 / 2025`. | Choose `deterministic Chapter 2 gap rendering planning gate`: preserve L1, avoid unsupported numeric claims, and define when Chapter 2 should render an explicit evidence gap/minimum verification instead of relying on another LLM repair. |
| Residual diagnostic evidence gap requiring more no-live metadata evidence | `NOT_PRIMARY` | Existing no-live diagnostic already proved propagation, path independence and fail-closed behavior. The remaining uncertainty is semantic live content behavior, which metadata-only no-live evidence is unlikely to close without body/payload reads. | Do not choose another generic diagnostic evidence gate. The next gate may include bounded no-live validation requirements, but only as part of deterministic gap rendering planning. |

## 5. Recommended Next Gate

Choose exactly one primary next gate:

```text
deterministic Chapter 2 gap rendering planning gate
```

Recommended gate name:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate
```

Purpose:

Plan a narrow product-safe behavior for Chapter 2 when L1 numerical closure cannot be satisfied after the current one-repair flow: render a deterministic evidence-gap / minimum-verification output for the affected Chapter 2 requirement, without weakening L1, without accepting unsupported concrete percentages, without increasing repair budget, and without changing source/provider/fallback policy.

Why this gate, not the alternatives:

| Candidate next gate | Disposition |
|---|---|
| `additional no-live diagnostic evidence gate` | Rejected as primary. Existing no-live diagnostic evidence already proves the key mechanical path; additional metadata-only diagnostics would not explain the live semantic failure under the current read boundaries. |
| `deterministic Chapter 2 gap rendering planning gate` | Selected. It directly addresses the observed failure mode with fail-closed product behavior instead of relying on stochastic prompt compliance. |
| `repair budget calibration planning gate` | Deferred. More repair attempts may hide noncompliance and remain a product-calibration question, not the narrowest current safety route. |
| `narrower code fix planning gate` | Rejected for now. The accepted facts do not identify a direct minimal code defect after the no-live implementation acceptance. |
| `blocked pending user/product decision` | Rejected. The project already has a consistent fail-closed principle that supports planning deterministic gap rendering without a separate product decision blocker. |

## 6. Non-goals and Deferred Gates

Non-goals for the recommended next gate:

- Do not weaken, downgrade or convert Chapter 2 L1 to warn.
- Do not accept unsupported concrete percentages or unanchored numerical closure.
- Do not change provider defaults, timeout defaults, output budget, model selection or runtime defaults.
- Do not change current `max_repair_attempts=1`.
- Do not implement typed patch API.
- Do not run live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release commands.
- Do not read report bodies, prompt bodies, provider payloads, source/PDF/cache bodies or final report body unless a future controller gate explicitly authorizes a safe body-read boundary.
- Do not change EID single-source/no-fallback policy.
- Do not update source, tests, runtime behavior, README, design, startup packet or implementation-control in this current disposition gate.
- Do not claim release/readiness, MVP readiness, LLM path readiness or live quality acceptance.

Deferred gates:

| Deferred gate | Reason |
|---|---|
| Repair budget calibration planning | Needs a separate standard gate comparing `max_repair_attempts=1/2/3` under no-live/fake-provider evidence after deterministic fail-closed behavior is defined. |
| Narrow prompt/code fix | Needs direct evidence of a specific contract mismatch; current evidence supports unreliable live compliance, not a proven minimal code defect. |
| Chapter 3 missing marker disposition | Separate residual from the same live sample; not the current first-failed blocker route. |
| Chapter 5 forbidden phrase disposition | Prior residual; not reproduced in the latest post-strengthening sample and remains separate. |
| Provider/LLM full completion live evidence | Premature while Chapter 2 first-fails. |
| Release-readiness rollup / PR / release | Current state remains `NOT_READY`. |

## 7. Validation Plan for Next Gate

The next planning gate should require a no-live validation matrix for any later implementation plan. It should specify expected tests before code is touched, not execute them in this current gate.

Minimum validation requirements for the future implementation gate:

| Validation target | Required proof |
|---|---|
| Deterministic gap rendering trigger | A no-live fake-writer or fixture case where Chapter 2 L1 cannot be numerically closed after current repair budget must produce an explicit evidence-gap / minimum-verification output instead of unsupported numeric claims. |
| L1 remains fail-closed for unsafe content | A concrete unanchored percentage or unclosed numerical claim must still fail L1 and must not be silently accepted. |
| Safe gap wording remains accepted | A gap/minimum-verification output without concrete unsupported percentages must pass the Chapter 2 L1 auditor path. |
| Repair budget unchanged | Tests must prove the path works with current one-repair semantics and does not increase `max_repair_attempts`. |
| Auditor/repair alignment | Tests must cover both initial and repair attempts so the accepted deterministic gap path is recognized by the same L1 contract the repair loop uses. |
| Service/Agent boundary | The plan must keep Chapter 2 product behavior inside the current Service/Agent/Fund boundary and must not route source access, provider config or Host lifecycle changes through this gate. |
| Source policy guard | Tests or static guards must show no Eastmoney, fund-company, CNINFO, fallback, PDF/cache body read or source-policy change is introduced. |
| Regression coverage | Existing no-live Chapter writer, orchestrator and auditor tests remain required; any new focused tests must be additive and scoped to Chapter 2 gap rendering. |
| Readiness posture | Evidence artifacts must preserve `NOT_READY` and avoid release/MVP/LLM-ready claims. |

Planning artifact requirements for the next gate:

1. Define the exact Chapter 2 item or L1 condition that may render a deterministic gap.
2. Define forbidden output: no unsupported concrete percentages, no implied R=A+B-C closure without anchors, no softened L1 severity.
3. Define accepted output: explicit evidence gap, minimum verification question and source-limited explanation.
4. Define ownership: Fund writer/auditor behavior if local to Chapter 2; Service/Agent orchestration only if final assembly or incomplete-run semantics must change.
5. Define the smallest allowed file set for any later implementation gate.
6. Define the full no-live validation matrix before authorizing code.

## 8. Stop Condition

Stop after writing this artifact.

No code, test, runtime, README, design, startup packet, implementation-control, source policy, provider default, repair budget, live command, readiness, release, PR, stage, commit, push or merge action is authorized by this artifact.

Final recommendation:

```text
deterministic Chapter 2 gap rendering planning gate
```
