# Plan Re-Review — Evidence Confirm Default-on Policy Plan (DS Findings)

## Re-Review Metadata

- **Reviewer role**: AgentDS independent plan reviewer
- **Re-review type**: targeted — only adjudicate prior DS F1–F4
- **Reviewed target**: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md` (fixed version)
- **Prior review**: `docs/reviews/plan-review-20260623-ds-evidence-confirm-default-on-policy.md`
- **Review date**: 2026-06-23

## Finding Disposition

### DS F1 (中) — `_resolve_analyze_contract()`产品分支变更影响范围未完全声明

**FIXED**

Plan fix notes (line 384) confirm intent. Evidence of fix:

- **Success signal** (line 22): adds `analyze-annual-period` as an explicit inherited path
- **First-principles Judgment** (line 31): redefines scope to "product analysis-report family" — direct `analyze` and `analyze-annual-period` via delegation; explicitly excludes `checklist`
- **Direct Code Evidence** (line 47): documents `analyze_multi_year_annual()` → `analyze()` → `_resolve_analyze_contract()` linkage
- **Design And Control Alignment** (line 85): names "product analysis-report family (`analyze` and inherited `analyze-annual-period`)"
- **Recommended Default-on Policy** (line 92): explicit decision "Product `analyze-annual-period`: inherits default `warn` through the existing product `analyze()` call path; no separate CLI flag"
- **Service contract** (line 132): "Accept that `analyze-annual-period` inherits product `warn`"
- **Slice EC-DO-1 objective** (line 155): now reads "make product `analyze` and inherited `analyze-annual-period` run Evidence Confirm by default"
- **Required tests** (lines 193–195): adds product-mode `analyze_multi_year_annual()` test asserting runner invocation through delegated `analyze()` path
- **Validation commands** (line 308): adds `test_fund_analysis_service_analyze_annual_period_defaults_evidence_confirm_warn`

Residual note: the plan does not separately discuss `analyze_with_llm` / `analyze_with_llm_hosted` paths inheriting default `warn`. This is low materiality because `--use-llm` is already explicit opt-in, and Evidence Confirm fact verification is orthogonal to report writing path. Not a new finding.

### DS F2 (低) — 开发覆盖模式中`--dev-override`单独使用会静默禁用Evidence Confirm

**FIXED**

Plan fix notes (line 385) confirm intent. Evidence of fix:

- **Recommended Default-on Policy** (line 94): "`--dev-override` without `--evidence-confirm-policy` keeps the CLI/default developer value `off` and does not inherit product `warn`"
- **Service contract** (line 128): repeats this as an explicit contract rule
- **Slice EC-DO-1** (line 200): "`--dev-override` or `FundAnalysisDeveloperOverrides` without an explicit Evidence Confirm policy keeps Evidence Confirm `off`"
- **Slice EC-DO-2** (line 224): "Keep `_build_developer_overrides()` behavior where plain `--dev-override` uses the CLI default `evidence_confirm_policy="off"` and therefore disables Evidence Confirm for that developer run"
- **Slice EC-DO-2 required tests** (line 238): adds developer-mode CLI test proving plain `--dev-override` does not inherit product `warn`
- **Validation commands** (line 328): adds `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`
- **Risks** (line 377): states the behavior explicitly as developer sandbox default

### DS F3 (低) — docstring更新目标位置未枚举

**FIXED**

Plan fix notes (line 386) confirm intent. Evidence of fix:

- **Slice EC-DO-1 Exact changes** (lines 165–168): enumerates three exact docstring locations with intended wording:
  1. `FundAnalysisDeveloperOverrides.evidence_confirm_policy` — say it only affects developer mode; omitted developer policy remains `off` and does not inherit product `warn`
  2. `_run_evidence_confirm_if_enabled()` — say it runs according to the effective resolved policy; product `analyze`/`analyze-annual-period` default can be `warn`, while `checklist` remains `off`
  3. `_effective_evidence_confirm_policy()` — say `checklist` is forcibly `off`; `analyze` command-source uses the resolved contract policy, including product default `warn`

### DS F4 (低) — 验证命令中的测试名称尚未区分新旧

**FIXED**

Plan fix notes (line 387) confirm intent. Evidence of fix:

- **Tests And Validation Commands** (lines 303–356): each test label is now prefixed with `New/updated`, `New`, `Existing/updated`, or `Existing` before the corresponding `uv run pytest` command block

## Verdict

**PLAN_REREVIEW_PASS**

All four DS findings (F1–F4) are fixed with concrete evidence in the plan text. No new material issues introduced by the fixes.
