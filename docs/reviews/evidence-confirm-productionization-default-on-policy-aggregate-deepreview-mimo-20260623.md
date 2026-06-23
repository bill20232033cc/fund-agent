# Evidence Confirm Productionization Default-on Policy Aggregate Deepreview

## Gate

- Work unit: Evidence Confirm Productionization default-on policy.
- Gate: Aggregate Deepreview Gate.
- Role: AgentMiMo deepreview worker.
- Classification: heavy.
- Review range: `cb199ce..362d5f5` (5 commits).
- Design truth: `docs/design.md`.
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`.
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`.
- Accepted slice judgments:
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-code-review-controller-judgment-20260623.md`
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-controller-judgment-20260623.md`
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-code-review-controller-judgment-20260623.md`
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice4-code-review-controller-judgment-20260623.md`

## Verdict

**AGGREGATE_DEEPREVIEW_PASS**

## Invariant Verification

### Invariant 1: Product `analyze` defaults to repository-bounded Evidence Confirm `warn`

**PASS.**

- `fund_agent/services/fund_analysis_service.py:1591` — `_resolve_analyze_contract()` product-mode branch sets `evidence_confirm_policy="warn"`.
- Service test `test_fund_analysis_service_product_analyze_default_warn_calls_evidence_confirm` verifies runner is called, request uses normalized fund code/report year/non-null projection/force_refresh, summary policy is `warn`, and report is produced.
- CLI test `test_analyze_cli_default_product_prints_evidence_confirm_warn_summary` verifies `mode == "product"`, `developer_overrides is None`, safe summary fields print to output, report body prints after summary, and no excerpt/PDF/path/parser/provider payload leaks.

### Invariant 2: `analyze-annual-period` inherits `warn` through existing delegation path

**PASS.**

- `analyze_multi_year_annual()` at line 854 delegates to `self.analyze()` with `mode="product"` when `_multi_year_developer_overrides()` returns `None` (default quality gate block with no explicit overrides).
- Service test `test_multi_year_annual_analysis_product_default_inherits_evidence_confirm_warn` verifies the EC runner is called once through the delegated `analyze()` path, summary policy is `warn`, and no special-case annual-period `off` branch exists.
- No separate annual-period product opt-out field or CLI flag was added.

### Invariant 3: `checklist` remains Evidence Confirm `off` with no CLI support

**PASS.**

- `_effective_evidence_confirm_policy()` at line 1683 returns `"off"` for `command_source == "checklist"` unconditionally.
- Service test `test_fund_analysis_service_product_checklist_default_keeps_evidence_confirm_off` verifies runner is not called and `evidence_confirm_summary is None`.
- CLI `checklist` command (line 906) has no `--evidence-confirm-policy` parameter.
- CLI test `test_checklist_cli_help_does_not_expose_evidence_confirm_policy` verifies `--evidence-confirm-policy`, `--no-evidence-confirm`, and `--evidence-confirm` are all absent from checklist help.

### Invariant 4: Developer override remains bounded

**PASS.**

- `--evidence-confirm-policy` is behind `--dev-override`: `_build_developer_overrides()` at line 2275 rejects it when `dev_override=False`.
- Plain `--dev-override` without `--evidence-confirm-policy` keeps Evidence Confirm `off`: CLI default is `evidence_confirm_policy="off"` (line 753), and `_resolve_analyze_contract()` developer-mode branch at line 1617 uses `overrides.evidence_confirm_policy or "off"`.
- CLI test `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off` verifies `developer_overrides.evidence_confirm_policy == "off"`.
- CLI test `test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override` verifies the rejection.
- Service test `test_fund_analysis_service_developer_default_and_explicit_off_do_not_inherit_warn` verifies developer off/default does not call runner.

### Invariant 5: Product users have no normal CLI or Service product-mode switch that silently disables Evidence Confirm

**PASS.**

- No `--no-evidence-confirm` or `--evidence-confirm` flag exists (verified by CLI tests).
- Service product mode always resolves to `warn` (line 1591); no request field or extra_payload can override it in product mode.
- Product mode rejects `developer_overrides` (line 1572).

### Invariant 6: Service/UI/renderer/quality-gate boundaries remain intact

**PASS.**

- Service boundary: `test_fund_analysis_service_evidence_confirm_boundary_static_imports` verifies no `FundDocumentRepository`, `pdf_cache`, `cache_helper`, `source_adapter`, `Docling`, `docling`, `pdfplumber` in service source.
- CLI boundary: `test_cli_module_has_no_evidence_confirm_runner_imports` verifies no `evidence_confirm_sources`, `evidence_confirm_production`, `run_repository_bounded_evidence_confirm` imports in CLI.
- Quality gate boundary: `test_quality_gate_integration_boundary_no_repository_or_source_imports` verifies no `repository`, `source`, `parser`, `docling`, `provider` imports in quality gate integration.
- `_run_evidence_confirm_if_enabled()` at line 1307 only calls the injected runner with `project_chapter_facts(structured_data)`; Service never reads PDF/cache/source/parser artifacts directly.

### Invariant 7: Quality gate consumes only compact summary; score.json EC unaware; warn maps fail to warn

**PASS.**

- `test_score_json_schema_remains_evidence_confirm_unaware` verifies `score.json` has no `evidence_confirm` keys while `quality_gate.json` has ECQ issues.
- `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` verifies `policy="warn", status="fail", deterministic_status="fail"` maps to ECQ2/warn and gate status `warn`.
- `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` verifies `policy="warn", pathway_status="fail"` maps to ECQ1/warn, not block.

### Invariant 8: Renderer/report body does not render Evidence Confirm content

**PASS.**

- `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` verifies report Markdown is identical with and without EC summary, and contains no "Evidence Confirm" or "evidence_confirm_status" strings.
- CLI test verifies no "secret excerpt", "source.pdf", "parser json", "provider body" in output.

### Invariant 9: Docs do not overclaim

**PASS.**

- `README.md`: updated to say `analyze` runs Evidence Confirm with `warn`; checklist explicitly "当前没有 Evidence Confirm CLI 参数，checklist CLI 支持属于后续单独 gate".
- `docs/design.md`: states default product `analyze` runs EC with `warn`; `checklist` support is future/separate gate; provider-backed semantic quality, report-body rendering, mark-ready, merge and release transition remain future/not authorized; release/readiness remains `NOT_READY`.
- `docs/implementation-control.md`: records accepted default-on policy implementation; preserves remaining blockers and next gates; explicitly states "Release/readiness remains `NOT_READY`".

### Invariant 10: Tests cover changed behavior; no stale default-off assumptions

**PASS.**

- 149 tests pass across all three test files.
- Product-mode `analyze` default warn tests: pass, fail (non-blocking), runner exception (safe summary).
- Annual-period inheritance test exists.
- Checklist default off test exists.
- Developer override isolation tests exist (default off, explicit off, explicit warn, explicit block).
- Quality gate ECQ1/ECQ2 warn-policy regression tests exist.
- No stale "default analysis does not call EC runner" assertions remain.

## Findings

No findings. All 10 invariants pass. The implementation is minimal, correct, and matches the accepted plan exactly.

## Validation Commands And Results

| Command | Result |
|---------|--------|
| `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py -q` | 149 passed in 1.19s |
| `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py` | All checks passed |
| `git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md` | Clean (no whitespace issues) |

## Residual Risks / Uncovered Areas

| Risk | Owner | Destination |
|------|-------|-------------|
| checklist Evidence Confirm CLI support | Gate owner | Separate checklist CLI/support gate |
| provider-backed semantic quality | Gate owner | Separate provider semantic quality gate |
| multi-sample live source/PDF coverage | Gate owner | Separate multi-sample evidence gate |
| annual-period Evidence Confirm CLI summary display refinement | UI/CLI owner | Separate UI refinement gate |
| PR-40 mark-ready, merge, release transition | Release owner | Separate release gate |

## Scope Boundary

- No live/PDF/network/provider/LLM commands were executed.
- No source, tests, docs/control, PR state, git state, remote state, or external state was mutated.
- Only the review artifact file was written.
