# MVP Real LLM Chapter Acceptance Calibration Slice 1A-1G No-Live Closeout Plan

## 1. Goal / Motivation

目标是在不运行 live LLM 的前提下，对 `Real LLM chapter acceptance calibration gate` 的 Slice 1A-1G 做控制面 closeout evidence：判断 retained post-config live artifact 中已经被识别的 deterministic residuals 是否都有本地 accepted fix / evidence 覆盖，并明确剩余 residual 只属于 live acceptance 未验证或下一 reviewed gate。

本 gate 不接受任何 live chapter，不接受完整 0-7 报告，不改变 provider/runtime/default/budget/config，也不打开 Agent runtime、multi-year、score-loop、golden/readiness、PR/push/release。

## 2. Scope

Allowed evidence artifact:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-1g-no-live-closeout-evidence-20260607.md`

Allowed controller artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-1g-no-live-closeout-plan-review-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-1g-no-live-closeout-controller-judgment-20260607.md`

Allowed control sync after accepted evidence judgment:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 3. Non-Goals

- No live LLM command, `--use-llm`, provider retry, endpoint probe, fallback or request-shape experiment.
- No provider/default/runtime/budget/config change.
- No production code, tests, README, template JSON, schema, quality gate, score-loop, golden/readiness, Host runtime, Agent runtime, multi-year runtime, PR, push or release change.
- No claim that Ch1-Ch6 live acceptance passed.
- No claim that a full fail-closed report is accepted.
- No new root-cause inference from indirect evidence.

## 4. Direct Evidence Inputs

The closeout evidence worker must use only same-source control/evidence artifacts:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-post-config-live-smoke-evidence-disposition-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-evidence-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-implementation-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-implementation-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-implementation-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-implementation-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1g-ch2-delete-rule-and-ch6-pressure-implementation-controller-judgment-20260607.md`

If an artifact is missing or contradicts the control docs, stop and report `BLOCKED_CONFLICTING_CONTROL_TRUTH`.

## 5. Evidence Method

The evidence worker must produce a compact matrix with these columns:

- retained residual from post-config live artifact
- accepted slice / evidence owner
- direct artifact citation
- local coverage verdict
- live acceptance status
- remaining residual owner

Allowed verdicts:

- `covered_locally`
- `covered_by_no_code_evidence`
- `not_covered`
- `not_applicable`
- `blocked_conflict`

The worker must separate:

- local deterministic fix/evidence coverage
- live acceptance proof
- full report acceptance proof

Local coverage may pass while live acceptance remains unproven.

## 6. Slice Coverage Matrix To Verify

| Residual / route | Expected accepted owner | Expected local closeout claim |
|---|---|---|
| Ch1 typed required-output marker-protocol mismatch | Slice 1A | `covered_locally`; typed writer path checks stable item id markers |
| Ch3/Ch5 marker-protocol sharing | Slice 1B + Slice 1A | `covered_by_no_code_evidence`; marker sub-residuals share Slice 1A fix |
| Ch6 synthesized/internal `bond_risk_evidence` unknown anchors | Slice 1C | `covered_locally`; writer prompt forbids synthesized/non-citeable anchors |
| Ch2 `l1_numerical_closure` | Slice 1D | `covered_locally`; prompt/repair guidance hardened, auditor remains fail-closed |
| Ch4 `audit_parse` | Slice 1E | `covered_locally`; auditor line-protocol prompt/repair guidance hardened, parser remains fail-closed |
| Ch3/Ch5 bounded missing-marker semantics | Slice 1F | `covered_locally`; approved missing markers are evidence gaps, deterministic claims from missing data still block |
| Ch2 deleted ITEM_RULE false positive / repair ambiguity | deterministic residual evidence + Slice 1G | `covered_locally`; detector narrowed and writer/repair guidance clarified |
| Ch6 pressure-test `must_not_cover` exception extraction | deterministic residual evidence + Slice 1G | `covered_locally`; `除非` exception is handled while true forbidden phrase remains blocked |

## 7. Validation Commands

Evidence worker should run only local, no-live checks:

```bash
rg -n 'Slice 1A, Slice 1B, Slice 1C, Slice 1D, Slice 1E and Slice 1F|Current closeout evidence artifact: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f|Next entry is deterministic residual evidence|Continue with deterministic residual evidence|Ch2 `delete_if_not_applicable` and any surviving Ch6|retained Ch6 pressure-test `must_not_cover` C2 may still require' docs/current-startup-packet.md docs/implementation-control.md
git diff --check -- docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected:

- `rg` exits `1` with no stale-route matches.
- `git diff --check` exits `0`.

If the evidence worker reads validation results from accepted Slice 1G judgment, it must quote them as historical accepted validation, not rerun live/provider commands.

## 8. Review Gates

Plan review must check:

- plan stays no-live and docs/evidence-only;
- coverage matrix includes every retained chapter blocker route from the accepted post-config live smoke disposition and subsequent deterministic residual evidence;
- live acceptance and full report acceptance remain explicitly unproven;
- validation commands cannot hit provider/runtime or fund document repositories.

Evidence review must check:

- evidence cites direct artifacts, not inferred memory;
- every `covered_locally` or `covered_by_no_code_evidence` row has an accepted artifact;
- no row claims live acceptance;
- stale-route search and diff check passed or blocker is reported.

## 9. Stop Conditions

Stop before evidence judgment if any of these occur:

- required accepted artifact missing;
- control docs disagree with Slice 1G judgment;
- any deterministic residual from the retained artifact maps to `not_covered`;
- validation command fails;
- worker needs live LLM/provider/runtime evidence;
- reviewer reports blocking finding;
- scope requires code/test/template/runtime changes.

## 10. Residual Risk Routing

Expected after accepted closeout:

- Closed locally: known deterministic residuals identified through Slice 1A-1G and deterministic residual evidence.
- Still open: Ch1-Ch6 live acceptance remains unproven.
- Still open: complete fail-closed 0-7 report acceptance remains unproven.
- Still open: Ch3/Ch5 required-output marker live proof remains unproven, although local typed marker protocol coverage is accepted.
- Next reviewed gate should be chosen by controller judgment; it must not be a live rerun unless separately planned/reviewed and explicitly authorized.

## 11. Planning Worker Availability Note

AgentCodex was first assigned this plan, read the required control files and accepted artifacts, but did not produce the target artifact after repeated captures. Controller fallback created this plan to avoid blocking the gate. This note is evidence of process fallback only; it does not relax the plan review or evidence review requirements.

## 12. Completion Report Format

Evidence worker final report must include:

- artifact path;
- coverage matrix verdict counts;
- validation command results;
- explicit residuals still open;
- recommended next gate;
- confirmation that no live LLM/provider/runtime command ran.
