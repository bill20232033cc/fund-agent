# Evidence Confirm Productionization Default-on Policy Aggregate Deep Review

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Gate: Aggregate Deep Review.
- Role: AgentDS deep reviewer.
- Classification: heavy.
- Review range: `cb199ce..362d5f5` (5 commits, plan acceptance through slice 4).
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-aggregate-deepreview-ds-20260623.md`.

## Inputs

| Input | Artifact | Status |
|---|---|---|
| Accepted plan | `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md` | PLAN_READY_FOR_REVIEW |
| Slice 1 controller judgment | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-code-review-controller-judgment-20260623.md` | ACCEPT |
| Slice 2 controller judgment | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-controller-judgment-20260623.md` | ACCEPT (after fix/re-review) |
| Slice 3 controller judgment | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-code-review-controller-judgment-20260623.md` | ACCEPT |
| Slice 4 controller judgment | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice4-code-review-controller-judgment-20260623.md` | ACCEPT |

## Methodology

Read all changed source files at HEAD (`362d5f5`), cross-checked every invariant against the accepted plan and current code state. Searched for stale default-off wording in all four truth docs. Ran full scoped test suite, ruff, and `git diff --check`. No live/PDF/network/provider/LLM commands were run.

## Changed Files (cumulative across all 4 slices)

| File | Change |
|---|---|
| `fund_agent/services/fund_analysis_service.py` | Product `analyze` default EC policy `off` → `warn` in `_resolve_analyze_contract()`; updated docstrings |
| `fund_agent/ui/cli.py` | `--evidence-confirm-policy` help changed from opt-in to developer-override wording; no product opt-out added |
| `tests/services/test_fund_analysis_service.py` | +11 EC-related tests covering product warn, checklist off, annual-period inherit, runner exception safety, dev override, boundary |
| `tests/ui/test_cli.py` | +7 EC-related tests covering default warn summary, dev-override-without-policy-off, reject-without-dev-override, block-exit-2, checklist-no-ec-flag, boundary |
| `tests/fund/test_quality_gate_integration.py` | +6 EC-related tests covering ECQ1/ECQ2/ECQ3 warn policy, score.json unaware, boundary guard |
| `docs/design.md` | Updated Evidence Confirm current-state section; stale default-off wording removed |
| `docs/implementation-control.md` | Recorded all 4 slice acceptances; current gate updated to aggregate deepreview |
| `docs/current-startup-packet.md` | Synced current gate and slice acceptances |
| `README.md` | Updated user-facing analyze behavior; no product disable flag documented |

## Invariant Verification

### Invariant 1: Product analyze defaults to repository-bounded Evidence Confirm warn

**PASS**

`fund_agent/services/fund_analysis_service.py:1590` — `_resolve_analyze_contract()` product-mode branch sets `evidence_confirm_policy="warn"`.

`fund_agent/services/fund_analysis_service.py:1333-1353` — `_run_evidence_confirm_if_enabled()` calls only the injected Fund-layer runner with `project_chapter_facts(structured_data)`. Service does not read PDF, cache, source helpers, parser artifacts, Docling, or provider payloads directly.

Covered by: `test_fund_analysis_service_product_analyze_default_warn_calls_evidence_confirm` (line 705), `test_fund_analysis_service_evidence_confirm_warn_calls_runner_without_blocking` (line 920), `test_analyze_cli_default_product_prints_evidence_confirm_warn_summary` (line 2921).

### Invariant 2: analyze-annual-period inherits warn through existing delegation path

**PASS**

`fund_agent/services/fund_analysis_service.py:854-868` — `analyze_multi_year_annual()` calls `self.analyze(FundAnalysisRequest(mode="product", ...))`. The `analyze()` path reaches `_resolve_analyze_contract()` which sets product `evidence_confirm_policy="warn"`. No special-case annual-period `off` branch exists.

`fund_agent/services/fund_analysis_service.py:1835` — `_multi_year_developer_overrides()` returns `None` when all quality gate options are default, keeping `mode="product"`. When quality gate options are non-default, it creates `FundAnalysisDeveloperOverrides` without `evidence_confirm_policy`, which developer-mode resolution defaults to `"off"` per `_resolve_analyze_contract()` line 1617. This is consistent with the plan: developer mode keeps EC off by default. However, `MultiYearAnnualAnalysisRequest` has no `evidence_confirm_policy` field, so there is no CLI path to enable EC in annual-period developer mode (see Residual Risks).

Covered by: `test_multi_year_annual_analysis_product_default_inherits_evidence_confirm_warn` (line 2134).

### Invariant 3: checklist remains Evidence Confirm off

**PASS**

`fund_agent/services/fund_analysis_service.py:1683-1684` — `_effective_evidence_confirm_policy(command_source="checklist")` returns `"off"`.

`fund_agent/ui/cli.py:906-981` — `checklist` command has no `--evidence-confirm-policy` parameter.

Covered by: `test_fund_analysis_service_product_checklist_default_keeps_evidence_confirm_off` (line 851), `test_checklist_cli_help_does_not_expose_evidence_confirm_policy` (line 3592).

### Invariant 4: Developer override remains bounded

**PASS**

`fund_agent/ui/cli.py:747-753` — `--evidence-confirm-policy` defaults to `"off"` and help says "仅在 --dev-override 下生效".

`fund_agent/ui/cli.py:2212-2301` — `_build_developer_overrides()`: `_has_developer_override_options()` lists `--evidence-confirm-policy` only when value is not `"off"` (line 2207). If any developer options are provided without `--dev-override`, `typer.BadParameter` is raised (line 2276-2278).

`fund_agent/services/fund_analysis_service.py:1617` — Developer-mode resolved contract: `evidence_confirm_policy=overrides.evidence_confirm_policy or "off"`. Plain `--dev-override` without `--evidence-confirm-policy` ⇒ CLI default `"off"` ⇒ `or "off"` ⇒ `"off"`.

Covered by: `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off` (line 1805), `test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override` (line 3117), `test_analyze_cli_evidence_confirm_block_exits_2_without_report_body` (line 3173), `test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off` (line 1037).

### Invariant 5: No normal CLI or Service product-mode switch silently disables Evidence Confirm

**PASS**

No `--no-evidence-confirm`, `--evidence-confirm`, or product opt-out flag exists in any CLI command.

`fund_agent/services/fund_analysis_service.py:1572-1573` — Product mode rejects `developer_overrides`.

`FundAnalysisRequest` (line 248-275) has no `evidence_confirm_policy` top-level field.

Covered by: `test_fund_analysis_service_product_mode_rejects_evidence_confirm_override` (line 1158).

### Invariant 6: Service/UI/renderer/quality-gate boundaries remain intact

**PASS**

Service: `_run_evidence_confirm_if_enabled()` (line 1307-1353) uses `project_chapter_facts(structured_data)` to construct the runner request; no direct repository/PDF/cache/source/parser/provider access.

UI: `_echo_evidence_confirm_summary()` (line 2641-2668) prints only `status`, `policy`, `checked_fact_count`, `failed_fact_count`, `auditability_score` — no excerpts, paths, parser JSON, or provider payloads.

Renderer: `render_template_report()` in `analyze()` (line 750-763) receives `TemplateRenderInput` with no `evidence_confirm_summary` field. Evidence Confirm content structurally cannot appear in report Markdown.

Quality gate: `_run_quality_gate_if_enabled()` (line 1878-1917) passes only the compact `evidence_confirm_summary` to `run_quality_gate_for_bundle()`.

Covered by: `test_fund_analysis_service_evidence_confirm_boundary_static_imports` (line 1191), `test_cli_module_has_no_evidence_confirm_runner_imports` (line 2800), `test_quality_gate_integration_boundary_no_repository_or_source_imports` (line 633).

### Invariant 7: Quality gate consumes only compact Evidence Confirm summary; score.json Evidence Confirm unaware

**PASS**

`fund_agent/services/fund_analysis_service.py:1905-1916` — `run_quality_gate_for_bundle(..., evidence_confirm_summary=evidence_confirm_summary)` receives only the compact summary. No production code change to `score.json` schema was made in this work unit.

Covered by: `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` (line 262), `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` (line 502), `test_score_json_schema_remains_evidence_confirm_unaware` (line 603).

### Invariant 8: Renderer/report body still does not render Evidence Confirm content

**PASS**

`analyze()` at line 750-763 constructs `TemplateRenderInput` without `evidence_confirm_summary`. The `FundAnalysisResult` carries it as a separate field for CLI stderr display only.

Covered by: `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` (line 962).

### Invariant 9: Docs do not overclaim

**PASS**

Stale wording search (`rg` for "Evidence Confirm developer opt-in", "默认 product `analyze` 和 `checklist` 不调用 Evidence Confirm", "EC-DO-4 implementation gate", "completed default-on policy", etc. across `docs/design.md`, `README.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`) returned **zero matches**.

`docs/design.md:885-894` correctly states:
- Default product `analyze` runs repository-bounded Evidence Confirm with `warn`
- `analyze-annual-period` inherits `warn` through delegation
- `checklist` Evidence Confirm support remains future/separate gate
- Provider-backed semantic quality, report-body rendering, mark-ready, merge, release transition remain future/not authorized
- Release/readiness remains `NOT_READY`

`docs/implementation-control.md:10,51` correctly records all 4 slice acceptances and current aggregate deepreview gate.

`README.md:110-116` correctly describes default `analyze` runs Evidence Confirm with `warn`, `--evidence-confirm-policy` is developer-only, and `checklist` has no Evidence Confirm CLI support.

### Invariant 10: Tests cover changed behavior and no stale default-off assumptions remain

**PASS**

Search for stale default-off assertions (`evidence_confirm.*off.*default`, `assert.*evidence_confirm_summary.*is None.*analyze`, `assert.*evidence_confirm.*not.*called.*analyze`) returned **zero matches**.

24 EC-related tests exist across the three test files, covering:
- Product analyze warn default (pass, fail, exception)
- Checklist off
- Annual-period warn inheritance
- Developer override bounded (off default, explicit warn, explicit block)
- CLI default warn summary output
- CLI reject without dev-override
- CLI block exit 2
- CLI checklist no EC flag
- ECQ1/ECQ2/ECQ3 warn-policy projection
- score.json Evidence Confirm unaware
- Service/CLI/quality-gate boundary static import guards
- Report body no EC content
- Product mode reject override

## Findings

No blocking findings.

| # | Severity | Finding | File:Line | Disposition |
|---|---|---|---|---|
| F1 | info | `MultiYearAnnualAnalysisRequest` has no `evidence_confirm_policy` field. When quality gate options are customized, `_multi_year_developer_overrides()` triggers developer mode with EC `off`, and there is no CLI or Service path to re-enable EC in that annual-period developer scenario. | `fund_agent/services/fund_analysis_service.py:1813-1842` | Accepted residual. The plan explicitly scopes annual-period EC to the product default path. Annual-period developer-mode EC enablement is out of scope. |
| F2 | info | `analyze-annual-period` CLI at line 1080 calls `_echo_quality_gate_summary()` but does not call `_echo_evidence_confirm_summary()` for `current_year_result`. The EC summary is still computed and available on the result object for quality gate projection, but is not printed to stderr. | `fund_agent/ui/cli.py:1080` | Accepted residual. Acknowledged in slice 2 controller judgment and `docs/design.md:887` as deferred UI/CLI refinement. |
| F3 | info | `analyze_with_llm()` and `analyze_with_llm_execution()` inherit product `warn` EC through `_run_analysis_core()` with `command_source="analyze"`, but no dedicated LLM-path EC test exists in this work unit. | `fund_agent/services/fund_analysis_service.py:931-933` | Accepted residual. Noted in slice 1 controller judgment as deferred to later LLM-path EC or provider-backed semantic quality gate. |

## Residual Risks

| Residual | Classification | Owner / Destination |
|---|---|---|
| Checklist Evidence Confirm CLI/support remains absent | Separate blocker | Checklist Evidence Confirm gate |
| Provider-backed/live semantic quality remains unproven | Separate blocker | Provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage remains unproven | Separate blocker | Multi-sample live evidence gate |
| Annual-period CLI Evidence Confirm summary display not implemented | Deferred UI/CLI residual | Later UI/CLI refinement gate |
| Annual-period developer-mode EC enablement (no `evidence_confirm_policy` on `MultiYearAnnualAnalysisRequest`) | Scope boundary | Future annual-period developer-mode gate if needed |
| LLM-path EC no dedicated test | Deferred-with-owner | Later LLM-path EC or provider-backed semantic quality gate |
| Report-body Evidence Confirm rendering | Future scope | Renderer gate (not authorized) |
| PR-40 mark-ready, merge, release transition | Deferred-with-owner | Separate explicit authorization and reviewed gate |
| Release/readiness remains `NOT_READY` | Release/readiness gate | After all blocker closure |

## Validation Commands

### Full scoped test suite
```
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py -q
```
Result: **149 passed in 1.59s**

### Ruff lint
```
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py
```
Result: **All checks passed!**

### Whitespace check
```
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md
```
Result: **passed (no output)**

### Stale wording audit
```
rg -n 'Evidence Confirm developer opt-in|Evidence Confirm 仅支持.*显式开发|默认 product `analyze` 和 `checklist` 不调用 Evidence Confirm|默认未请求 Evidence Confirm 时不改变 product|EC-DO-4 implementation gate|completed default-on policy|Evidence Confirm 仅支持' docs/design.md README.md docs/implementation-control.md docs/current-startup-packet.md
```
Result: **no matches**

## Conclusion

All 10 key invariants are verified against the current code at HEAD (`362d5f5`). The implementation correctly:

- Sets product `analyze` and inherited `analyze-annual-period` default Evidence Confirm policy to `warn`
- Keeps `checklist` Evidence Confirm `off` with no CLI parameter
- Keeps developer override bounded (`--evidence-confirm-policy` only with `--dev-override`; plain `--dev-override` keeps EC `off`)
- Exposes no product opt-out or silent disable path
- Preserves all Service/UI/renderer/quality-gate repository boundaries
- Projects EC fail under `warn` to ECQ warn, not block
- Does not render Evidence Confirm into report Markdown
- Does not overclaim in docs — all stale default-off wording removed, release/readiness remains `NOT_READY`
- Has 24 deterministic no-live tests covering all changed behavior
- Has zero stale default-off assumptions in tests

149 tests pass, ruff passes, git diff --check passes, stale wording audit passes. No blocking findings. Three info-level residuals are all accepted as known scope boundaries or deferred items with owners.

No live/PDF/network/provider/LLM commands were run. No PR state, git state, remote state, or external state was mutated.

## Verdict

**AGGREGATE_DEEPREVIEW_PASS**
