# Controller Judgment: CI Quality Warn-only Evidence Gate

Date: 2026-06-12

Role: controller

Gate: `CI quality warn-only evidence gate`

Classification: `standard`

Evidence artifact:

- `docs/reviews/mvp-ci-quality-warn-only-evidence-20260612.md`

Independent reviews:

- `docs/reviews/mvp-ci-quality-warn-only-evidence-review-ds-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-evidence-review-mimo-20260612.md`

Accepted input:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-plan-controller-judgment-20260612.md`
- Plan checkpoint `e4056e6`
- Control-sync checkpoint `50439a7`

## 1. Verdict

**ACCEPT_NOT_READY_NO_CODE_CHANGE**

The evidence gate is accepted. Current code/docs/tests preserve the required quality gate boundary:

- product/default path resolves to `quality_gate_policy=block`
- `warn` remains explicit and transparent
- `block` and `not_run` fail closed under `block`
- `warn` is not release/readiness proof

Release/readiness remains **`NOT_READY`**.

No source, tests, runtime behavior, README, design, config, source acquisition policy, quality gate severity or FQ0-FQ6 semantics changed in this gate.

The user's live authorization is not consumed by this no-live gate. It remains available only for a future separately reviewed live gate with exact commands, samples, stop conditions and evidence artifacts.

## 2. Review Finding Disposition

| Finding | Controller disposition | Basis | Required handling |
|---|---|---|---|
| DS-EV-1: default production policy remains `block` | ACCEPT | `docs/design.md`, product-mode `_resolve_analyze_contract()`, `MultiYearAnnualAnalysisRequest`, CLI defaults | Accepted evidence fact |
| DS-EV-2: `warn` is explicit | ACCEPT | CLI/default/developer override tests and Service contract resolution | Accepted evidence fact |
| DS-EV-3: `block` / `not_run` fail closed | ACCEPT | Service exception paths plus Service/CLI tests | Accepted evidence fact |
| DS-EV-4: no readiness proof from `warn` | ACCEPT | Evidence artifact rejects warn-as-ready and control docs preserve `NOT_READY` | Carry forward |
| DS-EV-5: no boundary violation | ACCEPT | No implementation diff; no live/runtime command | Carry forward |
| DS-EV-6: residual routing separates root cause and live samples | ACCEPT | Evidence routes quality warnings to root-cause planning and live samples to separate live gate | Carry forward |
| DS-EV-7: inaccurate `FundAnalysisRequest.quality_gate_policy` wording | ACCEPT_AS_FIXED | Evidence artifact was amended to say single-year product-mode `_resolve_analyze_contract()` resolves `"block"` | No further change |
| DS-EV-8: final verification needed | ACCEPT_AS_COMPLETED | Controller re-ran status/diff/check after review artifacts | Recorded below |
| MIMO-CI-EV-001: evidence sufficient for quality gate semantics | ACCEPT | Matches direct source/test evidence | Accepted evidence fact |
| MIMO-CI-EV-002: inaccurate `FundAnalysisRequest.quality_gate_policy` wording | ACCEPT_AS_FIXED | Same amendment as DS-EV-7 | No further change |
| MIMO-CI-EV-003: no readiness proof from `warn` | ACCEPT | Evidence and control docs preserve `NOT_READY` | Carry forward |
| MIMO-CI-EV-004: no boundary violation | ACCEPT | No implementation diff; pytest/ruff limited to no-live deterministic unit/lint | Carry forward |
| MIMO-CI-EV-005: next gate routing reasonable | ACCEPT | Root-cause planning is the mainline; live sample remains separate | Carry forward |

No review finding blocks acceptance.

## 3. Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Current default `quality_gate_policy=block` | ACCEPT | Direct design, Service and CLI evidence agree |
| Explicit warn path | ACCEPT | Warn does not become silent production default |
| `block` / `not_run` fail-closed behavior | ACCEPT | Service exceptions and tests cover both |
| Annual-period `quality_gate_status=warn` transparency | ACCEPT | Renderer and tests expose status |
| `warn` as release/readiness proof | REJECT | Contradicts accepted control/design policy |
| Implementation change in this gate | REJECT | Evidence supports no-code acceptance |
| Release/readiness state | ACCEPT_NOT_READY | The gate proves policy coherence only |
| Quality warning root cause | DEFER_TO_NEXT_MAINLINE | Needs a planning/evidence gate for the three warning issues |
| Additional EID live samples | DEFER | Requires separate reviewed live gate |
| Provider/LLM live acceptance | DEFER | Requires separate live provider/LLM gate |
| Fixture/golden/readiness promotion | DEFER | Requires separate promotion/readiness gate |
| Cleanup/archive/delete/import/ignore | DEFER | Requires explicit artifact-action gate |
| PR / push / merge / mark-ready / release | DEFER | Requires explicit external-state authorization |

## 4. Verification

| Command | Result |
|---|---|
| `rg -n "quality_gate_policy\|quality_gate_status\|quality_gate_issues\|QualityGate\|quality gate status=warn" fund_agent tests docs README.md` | Exit `0`; located default policy, warn/block/not-run paths, renderer status exposure and tests |
| `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py -q` | Exit `0`; `131 passed in 1.42s` |
| `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/golden_readiness_preflight.py fund_agent/fund/template/annual_period_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_annual_period_report.py` | Exit `0`; `All checks passed!` |
| `git status --short` | Exit `0`; existing unrelated untracked residue plus this gate's four new docs/reviews artifacts |
| `git status --branch --short` | Exit `0`; branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 195]`; existing unrelated untracked residue plus this gate's four new docs/reviews artifacts |
| `git diff --name-only` | Exit `0`; no output |
| `git diff --check` | Exit `0`; no output |

No live/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run.

## 5. Residuals

| Residual | Owner | Next handling | Blocks readiness? |
|---|---|---|---|
| Accepted live sample emitted `quality_gate_status=warn` and `quality_gate_issues=3` | release/readiness owner + quality gate owner | `Quality warning issue root-cause planning gate` | Yes |
| Single accepted live annual-period narrative sample only | evidence/release owner | Additional EID live sample gate only through separate reviewed live plan | Yes for broader readiness |
| Provider/LLM path not covered | provider/runtime owner | Live provider / LLM acceptance gate | Yes for LLM readiness |
| No release/readiness acceptance matrix has been accepted | release owner | Later readiness/release gate after residual disposition | Yes |

## 6. Next Entry

Recommended single mainline next entry:

`Quality warning issue root-cause planning gate`

Purpose:

- identify the three accepted live `quality_gate_issues`
- map each issue to root cause, owner, evidence requirement and possible fix/no-fix disposition
- preserve `quality_gate_policy=block` default and fail-closed semantics
- avoid live/provider/PDF/LLM/readiness/release commands unless a separate reviewed gate authorizes them

Deferred entries:

- `Additional EID live sample planning/execution gate`
- `Live provider / LLM acceptance gate`
- `Fixture/golden/readiness promotion gate`
- `Cleanup/archive/delete/import/ignore artifact-action gate`
- `PR / push / merge / mark-ready / release external-state gate`

## 7. Final State

CI quality warn-only evidence is accepted.

Release/readiness remains **`NOT_READY`**.
