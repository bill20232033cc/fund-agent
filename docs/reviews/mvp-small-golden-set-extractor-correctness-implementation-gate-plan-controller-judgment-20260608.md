# Small Golden Set / Extractor Correctness Implementation Gate Plan Controller Judgment

## Verdict

`PLAN_ACCEPTED`.

This accepts the implementation gate plan only. It does not implement the manifest, fixtures, extractor tests or extractor fixes. It does not authorize live LLM, retry, endpoint/DNS/curl/socket/PASS-only probe, fallback invocation, provider/default/runtime/budget/config changes, Agent runtime expansion, multi-year runtime, score-loop, golden/readiness promotion, release, merge or mark-ready.

## Current Truth Check

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Draft PR #22 review/fix/re-review gate remains accepted at checkpoint `2b1c804`.
- Small golden set fixture/evidence planning gate remains accepted at checkpoint `4ebaf0b`.
- Slice E first no-live Agent body-chapter mechanics remains current code fact.
- Full production Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion, durable Host features, live acceptance, multi-year runtime, score-loop, golden/readiness promotion and provider/default/runtime changes remain future scope.

## Accepted Plan Artifact

- Plan: `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md`

The accepted implementation plan authorizes only the following follow-up implementation scope:

- Slice A: five-row review-owned manifest and manifest schema guard.
- Slice B: offline extractor fixture strategy and retention evidence.
- Slice C: focused extractor correctness tests and narrowly scoped same-source Fund extraction-chain fixes.
- Slice D: implementation evidence, two independent code reviews, controller judgment, control/startup sync and local accepted checkpoint.

## Review Evidence

- Review A: `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-review-a-20260608.md`
- Review B: `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-review-b-20260608.md`
- Re-review A: `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-rereview-a-20260608.md`
- Re-review B: `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-rereview-b-20260608.md`

Independent sub-agents were used because the prior tmux AgentDS / AgentMiMo panes had stale PR #22 context after `/clear` attempts in the planning gate. The review tasks were read-only and produced no file changes.

## Finding Decisions

| Finding | Controller decision | Rationale |
|---|---|---|
| A1 fixture metadata could self-certify source identity | Accepted and fixed | Accepted planning requires source identity before correctness assertions. The implementation plan now requires matched or unavailable identity; synthetic and pending fixture metadata cannot satisfy source identity or exact/numeric correctness. |
| B1 repair scope too narrow | Accepted and fixed | Fund type and orchestration failures can live outside extractor leaf modules. The plan now allows the smallest proven Fund extraction-chain module and requires matching regression tests. |
| B2 promotion boundary command unreliable | Accepted and fixed | Promotion boundary evidence must cover untracked files and avoid shell glob fragility. The plan now uses `git status --short -- ...` plus gate-owned promotion-signal inspection. |
| B3 `tests/README.md` missing from Slice B allowed files | Accepted and fixed | Repo rules require README sync when tests/fixtures change. Slice B now allows and requires test manual sync when fixture/test directories are added. |
| B4 synthetic fixture boundary incomplete | Accepted and fixed | Synthetic fixtures may test parser mechanics but cannot become source truth. The plan now requires `fixture_source_kind` and restricts exact/numeric assertions to real minimal excerpts with matched identity. |

## Validation

Accepted validation for this plan gate:

```bash
git diff --check -- docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-review-a-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-review-b-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-rereview-a-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-rereview-b-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-controller-judgment-20260608.md
```

No implementation tests are required for this plan-only checkpoint.

## Residuals And Next Entry

Accepted next entry:

`small golden set extractor correctness implementation gate Slice A`

Required first implementation action:

- create `docs/reviews/mvp-small-golden-set-manifest-20260608.json`;
- add a manifest schema guard test;
- preserve exactly five rows and `promotion_allowed=false`;
- do not create source excerpts, modify extractors or change tests outside Slice A until Slice A evidence is complete;
- keep all validation offline and reproducible.

Closed for now:

- live acceptance evidence gate;
- fallback invocation;
- provider/default/runtime/budget/config changes;
- Chapter calibration;
- Agent runtime expansion;
- multi-year runtime;
- score-loop;
- golden/readiness promotion;
- release, merge and mark-ready.
