# Evidence Confirm Default-on Policy Aggregate Deepreview Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization default-on policy.
- Gate: aggregate deepreview controller judgment.
- Classification: heavy.
- Review range: `cb199ce..362d5f5`.
- Design truth: `docs/design.md`.
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`.
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`.
- DS aggregate deepreview: `docs/reviews/evidence-confirm-productionization-default-on-policy-aggregate-deepreview-ds-20260623.md`.
- MiMo aggregate deepreview: `docs/reviews/evidence-confirm-productionization-default-on-policy-aggregate-deepreview-mimo-20260623.md`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-aggregate-deepreview-controller-judgment-20260623.md`.

## Controller Decision

Accept the aggregate deepreview gate. No fix or re-review gate is required.

Both independent aggregate deepreviews returned `AGGREGATE_DEEPREVIEW_PASS`:

- AgentDS verified all 10 default-on policy invariants against current code at `362d5f5`, ran the focused non-live suite, ruff, diff-check and stale wording audit, and reported no blocking findings.
- AgentMiMo independently verified the same 10 invariants, ran the same focused non-live suite, ruff and diff-check, and reported no findings.

Accepted validation evidence:

```text
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py -q
```

Result in both aggregate artifacts: `149 passed`.

```text
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py
```

Result in both aggregate artifacts: passed.

```text
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md
```

Result in both aggregate artifacts: passed.

No live/PDF/network/provider/LLM commands were run.

## Finding Disposition

| Finding | Controller disposition | Reason |
|---|---|---|
| DS F1: `MultiYearAnnualAnalysisRequest` has no `evidence_confirm_policy`; annual-period developer-mode EC cannot be re-enabled when developer mode is triggered by non-default quality-gate options. | deferred-with-owner | Accepted scope boundary. The accepted plan only required product default annual-period inheritance through `analyze()`; developer-mode annual-period EC enablement is a future annual-period developer-mode gate if needed. |
| DS F2: `analyze-annual-period` CLI does not print a dedicated Evidence Confirm summary line even though `current_year_result.evidence_confirm_summary` exists. | deferred-with-owner | Already recorded by EC-DO-4 design/control sync as future UI/CLI residual. Current slice only documents the fact and does not add behavior. |
| DS F3: LLM paths inherit product `warn` via `command_source="analyze"`, but no dedicated LLM-path EC test exists in this work unit. | deferred-with-owner | Accepted scope boundary. Default-on policy validation is deterministic/no-live. LLM-path EC behavior belongs to later LLM-path EC or provider-backed semantic quality gate. |

No accepted blocking findings. No code, test or docs fix is required before the accepted deepreview commit.

## Accepted Invariants

The aggregate gate accepts these current facts:

- Product `fund-analysis analyze` defaults to repository-bounded Evidence Confirm with policy `warn`.
- Product `fund-analysis analyze-annual-period` inherits product `warn` through existing `analyze_multi_year_annual()` -> `analyze()` delegation.
- Product `fund-analysis checklist` remains Evidence Confirm `off` and has no Evidence Confirm CLI support in this work unit.
- `--evidence-confirm-policy` remains developer-only behind `--dev-override`; plain `--dev-override` keeps Evidence Confirm `off`.
- Product users have no normal CLI or Service product-mode switch that silently disables Evidence Confirm.
- Service/UI/renderer/quality-gate boundaries remain intact; only compact Evidence Confirm summary crosses into UI/quality-gate surfaces.
- Quality gate consumes compact summary only; `score.json` remains Evidence Confirm unaware; `warn` policy maps ECQ fail projection to warn, not block.
- Renderer/report body still does not render Evidence Confirm content.
- Docs preserve future boundaries and `Release/readiness remains NOT_READY`.
- Focused deterministic tests cover the changed behavior and stale default-off assumptions are removed.

## Residual Risks And Owners

| Residual | Disposition | Owner / Destination |
|---|---|---|
| Checklist Evidence Confirm CLI/support | deferred-with-owner | Service/CLI owner; separate checklist Evidence Confirm gate |
| Provider-backed/live semantic quality | deferred-with-owner | Evidence Confirm semantic owner; separate provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage | deferred-with-owner | Evidence owner; separate multi-sample live evidence gate |
| Annual-period Evidence Confirm CLI summary display refinement | deferred-with-owner | UI/CLI owner; future UI/CLI residual gate |
| Annual-period developer-mode EC enablement | deferred-with-owner | Service/CLI owner; future annual-period developer-mode gate if needed |
| LLM-path EC dedicated test | deferred-with-owner | Service/LLM owner; future LLM-path EC or provider-backed semantic quality gate |
| Report-body Evidence Confirm rendering | deferred-with-owner | Renderer owner; future renderer gate, not authorized now |
| PR-40 mark-ready, merge and release transition | deferred-with-owner | Controller/release owner; separate explicit authorization and reviewed gate |

## Next Gate

The aggregate deepreview gate is accepted. The next Gateflow entry point after the accepted deepreview commit is:

`Evidence Confirm Productionization default-on policy Ready-to-open-draft-PR Gate`

Do not push, create/update PR, mark ready, merge or claim release/readiness without the corresponding reviewed gate and explicit authorization where required.

## Verdict

ACCEPT_DEFAULT_ON_POLICY_AGGREGATE_DEEPREVIEW_READY_FOR_ACCEPTED_DEEPREVIEW_COMMIT_NOT_READY
