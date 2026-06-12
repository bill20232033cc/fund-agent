# CI Quality Warn-only Evidence Gate

Date: 2026-06-12

Role: controller-authored no-live evidence artifact

Gate: `CI quality warn-only evidence gate`

Classification: `standard`

Accepted input:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-review-ds-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-review-mimo-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-controller-judgment-20260612.md`
- Plan checkpoint `e4056e6`
- Control-sync checkpoint `50439a7`

## 1. Objective

Verify, without implementation changes or live commands, whether current code/docs/control evidence preserves the accepted quality gate policy boundary:

- production/default `quality_gate_policy=block`
- `warn` is explicit and may emit output in controlled/developer evidence paths
- `block` and `not_run` fail closed under `block`
- `quality_gate_status=warn` is transparent evidence and remains a release/readiness residual, not readiness proof

## 2. Boundary

This evidence gate did not:

- modify source, tests, runtime behavior, README, design, config or quality gate semantics
- run live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR commands
- read raw generated report, PDF, cache or corpus bodies
- clean, delete, move, archive, ignore, import or promote artifacts
- claim release/readiness

The user's live authorization is recorded as available only for a future separately reviewed live gate. It was not consumed by this no-live evidence gate.

## 3. Evidence Matrix

| Claim | Evidence type | Direct evidence | Disposition |
|---|---|---|---|
| Default production policy remains `block` | truth-doc fact + repo fact | `docs/design.md` states `quality_gate_policy=block` is the default; single-year product-mode `_resolve_analyze_contract()` resolves `"block"`; `MultiYearAnnualAnalysisRequest.quality_gate_policy` defaults to `"block"` | PASS |
| `warn` remains explicit, not silent production default | repo fact + test evidence | CLI `--quality-gate-policy` defaults to `"block"`; `test_analyze_cli_rejects_quality_gate_policy_without_dev_override` rejects non-default policy without `--dev-override`; Service developer override resolves `overrides.quality_gate_policy or "block"` | PASS |
| `block` fails closed under `block` policy | repo fact + test evidence | `_run_analysis_core()` raises `QualityGateBlockedError` when policy is `block` and gate status is `block`; `test_fund_analysis_service_block_policy_raises_structured_error` and checklist equivalent cover this | PASS |
| `not_run` fails closed under `block` policy | repo fact + test evidence | `_check_pool_membership_before_extraction()` raises `QualityGateNotRunBlockedError` for absent fund when policy is `block`; `_run_analysis_core()` also raises not-run if no gate result under `block`; service and CLI tests cover structured `not_run` exit `2` | PASS |
| `warn` may emit output but keeps gate evidence | repo fact + test evidence | `test_fund_analysis_service_warn_policy_keeps_report_and_gate_result` verifies warn policy returns a report even when gate status is `block`; CLI warn test exits `0` and emits `quality_gate_status: warn` | PASS |
| Annual-period report exposes quality status | repo fact + test evidence | `AnnualPeriodReportRenderInput.quality_gate_status` is rendered as `quality_gate_status=<value>`; `test_annual_period_report...` asserts `quality_gate_status=warn` in report Markdown | PASS |
| Readiness/golden preflight does not treat warn as ready proof | repo fact + test evidence | `golden_readiness_preflight._derive_quality_blockers()` converts `status=warn` into `quality_gate_warn` with message `不能证明 ready`; test asserts warn creates warning and not `quality_gate_block` | PASS_WITH_RESIDUAL |
| Current accepted live evidence with `quality_gate_status=warn` remains `NOT_READY` | accepted controller fact | `mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md` accepted warn live output with residuals; `mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md` preserved `NOT_READY`; current control docs route to this evidence gate | PASS_WITH_RESIDUAL |

## 4. Verification Commands

| Command | Result |
|---|---|
| `git status --short` | Exit `0`; only pre-existing unrelated untracked residue plus this new evidence artifact after writing |
| `git status --branch --short` | To be re-run for controller judgment after reviews |
| `git diff --name-only` | To be re-run for controller judgment after reviews |
| `git diff --check` | To be re-run for controller judgment after reviews |
| `rg -n "quality_gate_policy\|quality_gate_status\|quality_gate_issues\|QualityGate\|quality gate status=warn" fund_agent tests docs README.md` | Exit `0`; located default policy, warn/block/not-run paths, renderer status exposure and tests |
| `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py -q` | Exit `0`; `131 passed in 1.42s` |
| `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/golden_readiness_preflight.py fund_agent/fund/template/annual_period_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py` | Exit `0`; `All checks passed!` |

No live/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run.

## 5. Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Current default `quality_gate_policy=block` | ACCEPT | Direct design, Service and CLI evidence agree |
| Explicit warn path for controlled/developer evidence | ACCEPT | Warn requires explicit option/developer override and does not become product default |
| `block` / `not_run` fail-closed under `block` | ACCEPT | Service exceptions and CLI exit-code tests cover both branches |
| Annual-period `quality_gate_status=warn` transparency | ACCEPT | Renderer and tests expose status instead of hiding it |
| `warn` as release/readiness proof | REJECT | Design/control and golden readiness evidence keep warn as residual/non-proof |
| Release/readiness state | ACCEPT_NOT_READY | Evidence supports policy coherence only; it does not clear quality issues or broaden live coverage |
| Root cause of the three accepted live quality issues | DEFER | Requires separate quality warning issue root-cause planning/evidence gate |
| Additional EID live samples | DEFER | Requires separate reviewed live gate; current user live authorization is not consumed here |
| Provider/LLM live acceptance | DEFER | Requires separate live provider/LLM gate |
| Fixture/golden/readiness promotion | DEFER | Requires separate promotion/readiness gate |
| Cleanup/archive/delete/import/ignore | DEFER | Requires explicit artifact-action gate |

## 6. Residuals

| Residual | Owner | Next gate | Blocks readiness? |
|---|---|---|---|
| Accepted live sample emitted `quality_gate_status=warn` and `quality_gate_issues=3` | release/readiness owner + quality gate owner | `Quality warning issue root-cause planning gate` | Yes |
| Only one controlled live annual-period narrative sample accepted | evidence/release owner | additional EID live sample planning/execution gate only when separately reviewed | Yes for broader readiness |
| Provider/LLM path remains outside this evidence | provider/runtime owner | live provider / LLM acceptance gate | Yes for LLM readiness |
| This evidence gate is no-live/static plus unit/lint only | controller/release owner | future readiness gate must define broader acceptance matrix | Yes for release claim |

## 7. Controller Evidence Conclusion

Static evidence and focused no-live tests support `ACCEPT_NOT_READY_NO_CODE_CHANGE` for this evidence gate:

- current implementation preserves `block` as the default and fail-closed policy
- `warn` remains explicit and transparent
- `warn` is not a readiness pass
- no implementation is required in this gate before routing residuals

Recommended next entry after review and controller judgment:

`Quality warning issue root-cause planning gate`

Deferred live entry:

`Additional EID live sample planning/execution gate`, using the user's live authorization only after a separate reviewed live plan defines exact commands, samples, stop conditions and evidence artifacts.
