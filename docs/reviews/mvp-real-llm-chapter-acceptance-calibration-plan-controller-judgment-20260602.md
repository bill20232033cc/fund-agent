# Controller Judgment: MVP Real LLM Chapter Acceptance Calibration Plan

## Self-check

- Phase: `MVP real LLM observability and chapter acceptance phase`.
- Gate: `MVP real LLM chapter acceptance calibration gate`.
- Role: controller only.
- Work type: plan review judgment and accepted checkpoint preparation.
- Scope boundary: no implementation, no real smoke execution by controller, no runtime/source/test/config change, no provider budget change, no score-loop, no push, no PR, and no mark-ready action.

## Inputs

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-plan-20260602.md` |
| AgentDS plan review | `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-plan-review-ds-20260602.md` |
| AgentMiMo plan review | `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-plan-review-mimo-20260602.md` |
| Current truth sync | `docs/reviews/mvp-real-llm-observability-progress-ux-truth-sync-controller-judgment-20260602.md` |

## Review Verdicts

| Reviewer | Verdict | Blocking findings |
|---|---|---|
| AgentDS | `PASS` | 0 |
| AgentMiMo | `PASS` | 0 |

Both reviewers agree the plan is code-generation-ready and aligned with current design/control truth.

## Non-blocking Observation Disposition

| Observation | Controller disposition | Implementation requirement |
|---|---|---|
| DS O1: implementation evidence should explicitly record provider-runtime-first check before applying L1 criteria | accepted non-blocking | Slice 1 evidence must include a provider-runtime precedence check before any L1 classification. |
| DS O2: Slice 2 priority order could be read as cumulative rather than sequential | accepted non-blocking | Implementation must use the smallest evidence-supported fix and justify why each changed file/change type is necessary. |
| DS O3: cold start may have no pre-existing retained artifacts | accepted non-blocking | If no pre-existing retained artifact exists, implementation may run fresh smoke first and then inspect the resulting artifact; evidence must record this ordering. |
| DS O4: provider credentials/network/cost may block fresh smoke | accepted non-blocking | If fresh smoke cannot run, implementation must stop at Slice 1 unless controller explicitly accepts retained-artifact-only risk. |
| MiMo O1: secondary root-cause observations need residual owner if independently actionable | accepted non-blocking | Slice 1 evidence must assign owner/destination to every independently actionable secondary observation. |
| MiMo O2: "likely allowed" files require implementation justification | accepted non-blocking | Implementation evidence must justify every touched file against the actual root-cause class. |
| MiMo O3: L1 audit tests must distinguish regression of existing behavior from code bug fix | accepted non-blocking | If audit tests are added, evidence must state whether they validate existing strict L1 behavior or a proven code bug fix. |
| MiMo O4: fresh smoke vs retained artifact precedence | accepted non-blocking | Fresh smoke evidence is primary for current-state diagnosis when it conflicts with older retained artifacts; discrepancies must be recorded. |

## Controller Decision

Accept the plan.

The plan is the right next action because artifact retention and progress UX now make real LLM failures observable, but chapter acceptance calibration still requires same-source root-cause proof before any prompt, repair, diagnostic, or audit-code change. The plan preserves the phase boundaries: it prioritizes chapter 2 `l1_numerical_closure`, requires retained artifacts plus a fresh real smoke rerun, and stops if the current first blocker is provider runtime. It also explicitly excludes provider budget changes, auditor relaxation, repair budget increases, deterministic fallback, partial stdout, score/golden/readiness changes, artifact schema expansion without controller approval, and Host/Agent/dayu runtime migration.

## Accepted Plan Guardrails

- Implementation must start with Slice 1 evidence triage.
- No code changes are authorized until Slice 1 proves an actionable non-provider-runtime root cause.
- Chapter 2 `l1_numerical_closure` calibration may proceed only with same-source retained/rerun evidence satisfying the plan's criteria.
- Chapters 3 and 6 must not trigger broad prompt rewrites; they may only be triaged or fixed if they share a proven root cause or receive their own same-source mini-triage.
- Fresh smoke evidence is primary for current-state diagnosis when it conflicts with older artifacts.
- If fresh smoke cannot run due to credentials/network/cost, implementation must stop and report unless controller explicitly accepts the risk.
- All evidence must preserve redaction and avoid prompts, raw provider/auditor responses, API keys, Authorization/Bearer/cookies, full config, stack traces, model names omitted by safe serializers, and full draft dumps.

## Next Entry Point

Create a local accepted plan checkpoint, then dispatch Slice 1 implementation/evidence triage through `$init-agents`. Do not implement calibration code until Slice 1 evidence authorizes it.
