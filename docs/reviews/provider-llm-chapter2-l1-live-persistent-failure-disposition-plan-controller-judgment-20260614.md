# Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

Verdict: `ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_DETERMINISTIC_GAP_RENDERING_PLANNING_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the no-code disposition/planning gate for the live-persistent Chapter 2 L1 failure after accepted no-live prompt strengthening.

This judgment does not authorize implementation, live/provider commands, source-policy changes, fallback expansion, provider default changes, repair budget changes, annual-period LLM route design, Docling work, readiness/release/PR actions, staging beyond this accepted checkpoint, push or merge.

EID annual-report access remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, fail-closed posture, EID single-source/no-fallback boundary and standard gate expectations. |
| `docs/current-startup-packet.md` | Current active gate and `NOT_READY` posture after checkpoint `75e7e57`. |
| `docs/implementation-control.md` | Control truth and current no-code disposition scope after checkpoint `75e7e57`. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-20260614.md` | Planning/disposition artifact under review. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-review-ds-20260614.md` | DS independent review, verdict `PASS_WITH_FINDINGS`. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-review-mimo-20260614.md` | MiMo independent review, verdict `PASS_WITH_FINDINGS`. |
| `docs/reviews/provider-llm-chapter2-l1-prompt-strengthening-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepted live fail-closed evidence at checkpoint `648c439`. |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-controller-judgment-20260614.md` | Accepted no-live prompt strengthening implementation at checkpoint `ee65f69`. |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepted no-live diagnostic evidence at checkpoint `7fbc862`. |

No report bodies, prompt bodies, provider request/response payloads, PDF/source/cache bodies, source bodies or final report body were read for this judgment.

## 3. Accepted Current Facts

| Fact | Disposition |
|---|---|
| Exact `004393 / 2025` post-strengthening live evidence still first-fails Chapter 2 with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`. | Accepted from checkpoint `648c439`. |
| The repair attempt worsened L1 count from 1 to 2 in safe metadata. | Accepted from checkpoint `648c439`. |
| No-live evidence proves checklist propagation and current L1 fail-closed behavior. | Accepted from checkpoint `7fbc862`. |
| Narrow prompt strengthening was implemented and accepted without changing `_repair_context_prompt()` or repair budget. | Accepted from checkpoint `ee65f69`. |
| The post-strengthening live failure is not, by itself, an implementation acceptance failure for the no-live prompt contract. | Accepted from checkpoint `648c439`. |
| Current evidence does not prove whether the live model ignored present facts, facts/anchors were insufficient, or auditor/repair wording remained semantically misaligned. | Accepted residual. |
| Release/readiness remains unproven. | Accepted; preserve `NOT_READY`. |

## 4. Review Disposition

| Reviewer finding | Controller disposition | Binding amendment |
|---|---|---|
| DS F1 / MiMo Finding 1: gap rendering may mask model noncompliance if facts are present but ignored. | `ACCEPT_WITH_REWRITE` | The next gate must not treat deterministic gap rendering as a universal answer for all live L1 failures. It must distinguish fact absence/insufficiency from present-but-ignored facts when possible; if it cannot under no-live boundaries, it must record that ambiguity as an explicit residual and constrain product wording accordingly. |
| DS F2 / MiMo Finding 2: validation matrix is contract-level and underspecified for implementation. | `ACCEPT` | The next planning gate must produce concrete validation specifications before implementation: file scope, fixture or mock/stub layer, test function intent and expected assertions. |
| DS F3: auditor/repair contract alignment must be validated. | `ACCEPT` | The next planning gate must require proof that the current Chapter 2 L1 auditor contract recognizes the deterministic gap/minimum-verification output path, including repair-attempt coverage. |
| MiMo Finding 3: repair budget interaction is unscoped. | `ACCEPT` | The next planning gate must explicitly declare repair budget interaction in-scope or out-of-scope. It must not change `max_repair_attempts` unless a later separately accepted gate authorizes it. |
| MiMo Finding 4: product direction is implicit. | `ACCEPT_WITH_REWRITE` | Controller accepts the product direction only as a planning hypothesis: an explicit evidence gap/minimum-verification output is preferable to opaque `repair_budget_exhausted` when Chapter 2 numerical closure cannot be safely supported. The next gate must still specify exact user-visible semantics before implementation. |
| MiMo Finding 5: L1 subcategory scope unclear. | `ACCEPT` | The next planning gate must scope the behavior to `l1_numerical_closure` unless it separately proves and justifies extension to other L1 subcategories. |

## 5. Rejected Alternatives

| Candidate next gate | Controller disposition | Basis |
|---|---|---|
| Additional generic no-live diagnostic evidence gate | `REJECT_AS_PRIMARY` | Existing no-live evidence already proves the key mechanical propagation path. More metadata-only diagnostics would not resolve the semantic live ambiguity under current read boundaries. |
| Repair budget calibration planning gate | `DEFER` | Repair budget remains an accepted residual, but the latest repair moved L1 count in the wrong direction. More attempts could hide noncompliance and is not the narrowest current fail-closed route. |
| Narrower code fix planning gate | `REJECT_AS_PRIMARY` | The accepted evidence does not identify a direct minimal code defect after the no-live implementation acceptance. |
| Blocked pending user/product decision | `REJECT` | The project already has a fail-closed principle that permits planning explicit evidence-gap behavior. User-visible wording and exact semantics remain next-gate requirements, not a blocker for planning. |

## 6. Accepted Next Gate

Primary next gate:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate
```

Gate classification: `standard`.

Purpose:

Plan a narrow, fail-closed Chapter 2 behavior for `l1_numerical_closure` when the current one-repair flow cannot safely close unsupported numeric claims: render an explicit evidence gap / minimum-verification path rather than accepting unsupported percentages or relying on another prompt-only repair.

Binding constraints for the next gate:

1. Planning only; no implementation until a later accepted implementation gate.
2. Preserve Chapter 2 L1 severity; do not downgrade to warn.
3. Preserve EID single-source/no-fallback; do not introduce Eastmoney, fund-company, CNINFO or other fallback.
4. Preserve current repair budget unless a later separate gate authorizes calibration.
5. Define whether the gap path applies only to `l1_numerical_closure` or any broader L1 subcategory.
6. Distinguish fact absence/insufficiency from present-but-ignored facts when possible; otherwise record the ambiguity and constrain output wording.
7. Produce code-generation-ready validation details: exact test scope, fixtures or mock/stub layer, expected assertions and no-live command matrix.
8. Include auditor/repair alignment proof requirements.
9. Preserve release/readiness = `NOT_READY`.

## 7. Accepted / Rejected / Residual Finding Table

| Item | Disposition | Owner / next handling |
|---|---|---|
| Deterministic Chapter 2 gap rendering as the next primary route | `ACCEPT_WITH_AMENDMENTS` | Next planning gate. |
| Generic additional no-live diagnostic route | `REJECT_AS_PRIMARY` | Reopen only if next planning gate identifies a missing direct proof. |
| Immediate repair budget calibration | `DEFER` | Separate future standard gate after gap-rendering scope is decided. |
| Immediate narrower code fix | `REJECT_AS_PRIMARY` | Requires direct minimal defect evidence. |
| Fact absence vs present-but-ignored ambiguity | `ACCEPTED_RESIDUAL` | Must be handled explicitly in next planning gate. |
| Validation matrix underspecification | `ACCEPTED_RESIDUAL` | Must be converted into concrete test specs in next planning gate. |
| Auditor/repair terminology and contract alignment | `ACCEPTED_RESIDUAL` | Must be covered in next planning gate validation requirements. |
| L1 subcategory scope | `ACCEPTED_RESIDUAL` | Next gate defaults to `l1_numerical_closure` unless justified otherwise. |
| Release/readiness | `NOT_READY` | No readiness/release claim accepted. |

## 8. Validation

Controller validation for this disposition gate:

```text
git diff --check
```

Required before checkpoint:

```text
git status --short
git status --branch --short
git diff --check
```

No live/provider/LLM/network/source/PDF/readiness/release/PR validation is authorized by this gate.

## 9. Final Verdict

`VERDICT: ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_DETERMINISTIC_GAP_RENDERING_PLANNING_GATE_NOT_READY`

Next entry point:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate
```
