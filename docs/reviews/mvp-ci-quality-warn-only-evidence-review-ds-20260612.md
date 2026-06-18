# DS Review: CI Quality Warn-only Evidence Gate

Date: 2026-06-12

Role: AgentDS

Reviewed artifact:

- `docs/reviews/mvp-ci-quality-warn-only-evidence-20260612.md`

## Verdict

PASS_WITH_FINDINGS

## Findings

| id | severity | finding | evidence | recommendation |
|---|---|---|---|---|
| DS-EV-1 | PASS | Evidence is sufficient to show the default production policy remains `quality_gate_policy=block`. | `docs/design.md` states the default; product mode `_resolve_analyze_contract()` resolves `"block"`; `MultiYearAnnualAnalysisRequest.quality_gate_policy` defaults to `"block"`; CLI option defaults to `"block"`. | Accept. |
| DS-EV-2 | PASS | Evidence is sufficient to show `warn` is explicit, not a silent production default. | CLI default is `"block"`; tests reject non-default quality policy without `--dev-override`; Service developer override falls back to `"block"`. | Accept. |
| DS-EV-3 | PASS | Evidence is sufficient to show `block` / `not_run` fail closed under block policy. | `_run_analysis_core()` raises `QualityGateBlockedError` or `QualityGateNotRunBlockedError`; `_check_pool_membership_before_extraction()` fail-closes absent-fund membership under block; Service/CLI tests cover structured behavior. | Accept. |
| DS-EV-4 | PASS | The artifact does not claim `warn` as release/readiness proof. | Artifact rejects `warn` as readiness proof and keeps release/readiness `NOT_READY`. | Accept. |
| DS-EV-5 | PASS | No no-live/no-implementation boundary violation was found. | Artifact records no source/test/runtime changes and no live/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command. | Accept. |
| DS-EV-6 | PASS | Residual routing separates quality warning root cause from additional live sample work. | Artifact routes warning issues to root-cause planning and additional live samples to a separate reviewed live gate. | Accept. |
| DS-EV-7 | LOW | Original artifact text inaccurately said `FundAnalysisRequest.quality_gate_policy` existed. | `FundAnalysisRequest` has no such field; default block comes from product-mode `_resolve_analyze_contract()`, while `MultiYearAnnualAnalysisRequest` has an explicit default. | Non-blocking if controller corrects wording. |
| DS-EV-8 | LOW | Final status/diff verification must be re-recorded by controller after review artifacts are written. | Evidence artifact left some verification rows for controller judgment. | Controller should record `git status --short`, `git status --branch --short`, `git diff --name-only`, and `git diff --check`. |

## Residual Risks

- `quality_gate_status=warn` / `quality_gate_issues=3` still blocks any release/readiness claim.
- This gate proves policy coherence only; it does not resolve the three quality warnings.
- Single-sample live evidence is not broad live coverage.
- Provider/LLM readiness, fixture/golden/readiness promotion, additional live samples, cleanup/archive/delete/import/ignore and PR/release remain deferred.

## Required Controller Actions

- Keep final verdict in `ACCEPT_NOT_READY_NO_CODE_CHANGE` territory.
- Correct the `FundAnalysisRequest.quality_gate_policy` wording.
- Record final verification commands.
- Set next entry to `Quality warning issue root-cause planning gate`.
- Keep `Additional EID live sample planning/execution gate` separate.
