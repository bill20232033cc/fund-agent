# Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate`

Verdict: `ACCEPT_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the Chapter 6 invalid-marker live-blocker disposition planning gate.

The gate is no-code disposition/root-cause planning only. It does not implement a fix, modify source/tests/runtime behavior, run live/provider commands, change provider defaults, change repair budget, change EID source policy, open PR state, or claim readiness.

EID source policy remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Controller use |
|---|---|
| `AGENTS.md` | Rule truth: standard gate expectations, role boundaries, root-cause evidence discipline, EID single-source/no-fallback, `NOT_READY` preservation. |
| `docs/design.md` | Design truth: Route C `--use-llm` is explicit opt-in and fail-closed; current Agent body runner uses exact writer marker contracts; full runtime expansion/readiness remains future scope. |
| `docs/current-startup-packet.md` | Current active gate, accepted Chapter 2 live evidence checkpoint and no-code planning boundary. |
| `docs/implementation-control.md` | Control truth: current mainline is Chapter 6 invalid-marker disposition; release/readiness remains `NOT_READY`. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepted live fact: Chapter 2 is accepted in the exact sample and Chapter 6 `invalid_marker` is the new first failed blocker. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-20260614.md` | Accepted safe live metadata boundary and run summary. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md` | Disposition plan under judgment. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-ds-20260614.md` | Independent AgentDS review; verdict `ACCEPT`. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-mimo-20260614.md` | Independent AgentMiMo review; verdict `ACCEPT`. |

No writer/auditor/repair markdown bodies, prompt bodies, provider payloads, PDF/source/cache bodies, source bodies or final report bodies were read for this controller judgment.

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands were run for this controller judgment.

## 3. Accepted Current Facts

| Fact | Controller disposition |
|---|---|
| The accepted bounded live sample for exact `004393 / 2025` no longer first-fails Chapter 2; Chapter 2 is accepted in that metadata path. | Accepted as current routing fact only; not readiness proof. |
| The current first failed chapter is Chapter 6 with `stop_reason=llm_contract_violation`, `failure_category=prompt_contract`, `failure_subcategory=invalid_marker`. | Accepted as the active blocker identity. |
| Safe metadata records four `writer:invalid_anchor_marker` issues, `invalid_marker_count=4`, `unknown_anchor_count=0`, no required-output/structure missing, no forbidden phrase, no truncation, and provider attempt count `0`. | Accepted as strong pre-provider marker-format diagnostic evidence. |
| Existing marker contract requires exact writer anchor marker syntax, and existing mechanics distinguish invalid marker syntax from valid-but-unauthorized anchor IDs. | Accepted as current contract/mechanics context, not a fix decision. |
| The actual malformed marker strings, rendered Chapter 6 prompt body, allowed anchor list and provider output body were not read in this gate. | Accepted as a binding evidence gap. |

## 4. Review Disposition

| Review source | Finding | Controller disposition |
|---|---|---|
| AgentDS | No blocking findings; plan stays inside safe metadata/no-code boundary and preserves EID single-source/no-fallback and `NOT_READY`. | `ACCEPT` |
| AgentDS | Root-cause classification is calibrated: strongest current category is LLM output-format noncompliance, with missing no-live diagnostic evidence as the accepted gap. | `ACCEPT` |
| AgentDS | No-live diagnostic evidence gate is better supported than immediate fix planning, another live run or blocked. | `ACCEPT` |
| AgentMiMo | No blocking findings; safe metadata cross-check matches the plan's accepted facts. | `ACCEPT` |
| AgentMiMo | D1-D5 next-gate checks are specific enough for the next evidence worker. | `ACCEPT` |

No reviewer finding requires plan rewrite. No reviewer finding authorizes implementation.

## 5. Controller Decision

The disposition plan is accepted.

Controller reasoning:

1. The live metadata is sufficient to route away from source/provider/fallback/readiness/live repetition and toward Chapter 6 writer marker-contract diagnostics.
2. The metadata is not sufficient to choose a concrete fix surface because this gate deliberately did not read provider output body, prompt body, or actual malformed marker strings.
3. The next gate must therefore be no-live diagnostic evidence, not no-live implementation and not another bounded live command.
4. The gate remains fail-closed and preserves current release/readiness as `NOT_READY`.

## 6. Accepted / Rejected / Residual Table

| Item | Disposition | Reason |
|---|---|---|
| Strongest current root-cause category: LLM output-format noncompliance with existing anchor marker contract. | `ACCEPT` | Supported by invalid marker counts, zero unknown anchors, zero truncation, zero provider attempts and existing marker-contract mechanics. |
| Evidence gap: missing no-live reproducer/diagnostic evidence. | `ACCEPT` | Actual malformed strings, rendered prompt body, allowed anchors and provider output body were not read; fix surface remains under-proven. |
| Immediate no-live fix planning. | `REJECT_FOR_NEXT_ENTRY` | Premature before D1-D4 diagnostic evidence identifies whether the surface is prompt wording, repair context or validator behavior. |
| Additional bounded live evidence before no-live diagnostics. | `REJECT_FOR_NEXT_ENTRY` | Current gap is diagnostic isolation, not another live occurrence. |
| Parser/validator relaxation. | `DEFER` | Could become relevant only if no-live diagnostics prove accepted syntax is being rejected or the contract needs product recalibration. |
| Prompt/repair-context strengthening. | `DEFER` | Candidate fix surface only after no-live diagnostics. |
| Readiness / MVP-ready / LLM-path-ready claim. | `REJECT` | Current live sample still fails closed at Chapter 6 and final assembly is incomplete. |
| EID fallback/source expansion. | `REJECT` | Current source policy is EID single-source/no-fallback; Chapter 6 blocker is pre-provider writer marker parsing, not source acquisition. |

## 7. Accepted Next Gate

Next entry point:

```text
Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate
```

Required next-gate evidence questions:

1. D1: Does no-live rendered Chapter 6 writer prompt expose exact `<!-- anchor:<anchor_id> -->` syntax, allowed-anchor boundaries and Chapter 6 bond-risk internal-anchor prohibition clearly?
2. D2: Do fake/no-live writer outputs classify malformed marker comments as `invalid_marker` and valid syntax with unauthorized IDs as `unknown_anchor`?
3. D3: Do diagnostics count `writer:invalid_anchor_marker` as `invalid_marker_count` without leaking raw marker suffixes?
4. D4: Does repair context for `invalid_marker` instruct exact marker syntax clearly enough for the next writer attempt?
5. D5: Does the evidence gate preserve no-live/no-provider/no-source/no-fallback/no-readiness boundaries?

The next gate is evidence-only unless separately accepted by controller judgment. It must not implement fixes, run live commands, change prompt/runtime behavior, change repair budget, change source policy, or claim readiness.

## 8. Control-doc Update Recommendation

Update `docs/current-startup-packet.md` and `docs/implementation-control.md` after this judgment is checkpointed:

- current active gate: `Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate`
- accepted plan checkpoint: this controller judgment and its plan/review artifacts
- next entry point: no-live diagnostic evidence worker for D1-D5
- release/readiness: `NOT_READY`
- non-goals: no implementation, no live/provider, no source fallback, no provider default or repair-budget change, no PR/release/readiness state change

## 9. Final Verdict

`VERDICT: ACCEPT_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

Stop condition for this gate: satisfied after control docs are synchronized and the scoped accepted checkpoint is committed.
