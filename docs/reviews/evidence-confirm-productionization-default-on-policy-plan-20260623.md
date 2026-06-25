# Evidence Confirm Productionization Default-on Policy Plan

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Gate: release/readiness planning gate.
- Role: AgentCodex planning worker only.
- Classification: heavy.
- Design truth: `docs/design.md`.
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`.
- Goal-confirmation artifact: `docs/reviews/evidence-confirm-productionization-release-readiness-goal-confirmation-20260623.md`.
- Requirements audit: `docs/reviews/evidence-confirm-productionization-release-readiness-requirements-audit-20260623.md`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`.

## Goal And Motivation

Release/readiness cannot claim production Evidence Confirm protection while the product default path does not call Evidence Confirm. This plan covers the first blocker only: default-on Evidence Confirm policy.

Success signal for the implementation gate:

- default product `fund-analysis analyze` runs repository-bounded Evidence Confirm by default with policy `warn`;
- default product `fund-analysis analyze-annual-period` inherits the same product `warn` policy through the existing `analyze_multi_year_annual()` -> `analyze()` -> `_resolve_analyze_contract()` path;
- product users have no normal CLI or Service product-mode switch that silently disables Evidence Confirm;
- developer override can still choose `off|warn|block`, but only in explicit developer mode;
- `fund-analysis checklist` remains Evidence Confirm `off` in this work unit and is routed to a separate checklist CLI/support gate;
- existing Service/UI/renderer/quality-gate repository boundary remains intact;
- deterministic no-live tests prove policy, runner invocation, warning projection, CLI visibility and non-goals.

## First-principles Judgment

Default-on should apply to the product analysis-report family in this work unit: direct `analyze` and the existing `analyze-annual-period` path that delegates to `analyze()`. It must not apply to `checklist`.

Reasoning:

- `analyze` is the primary product report path and already has accepted EC-P4 Service/UI/quality-gate integration and stderr summary display.
- `analyze-annual-period` reuses the `analyze()` product contract path; excluding it would require a new special-case branch and product semantics not justified by the current requirements audit.
- `checklist` shares `_run_analysis_core()`, but design/control truth explicitly classifies checklist Evidence Confirm CLI support as a separate readiness blocker. Turning it on here would silently change a product path with no CLI/UX contract.
- Default policy should be `warn`, not `block`. Evidence Confirm has accepted repository-bounded single-sample live source/PDF proof and no-live semantic companion projection, but multi-fund live coverage and provider-backed semantic quality remain unproven. `warn` makes default product Evidence Confirm visible and quality-gate projected without converting unproven coverage into a release hard block.
- `block` remains available for explicit developer override and should be reconsidered only after multi-sample live/source evidence and provider-backed semantic quality gates are accepted.

This is not over-design: it changes the smallest existing state-machine edge, reuses EC-P4 summary/ECQ plumbing, does not add new schema, does not add checklist flags, does not add provider clients, and does not render Evidence Confirm into report Markdown.

## Direct Code Evidence

- `fund_agent/services/fund_analysis_service.py`
  - `FundAnalysisService.analyze()` and `FundAnalysisService.checklist()` both call `_run_analysis_core()`.
  - `FundAnalysisService.analyze_multi_year_annual()` reaches `analyze()` with `FundAnalysisRequest(mode="product", ...)` when quality-gate options remain default, so it inherits `_resolve_analyze_contract()` product defaults.
  - `_run_analysis_core()` extracts `StructuredFundDataBundle`, then calls `_run_evidence_confirm_if_enabled(...)`, then passes `evidence_confirm_summary` into `_run_quality_gate_if_enabled(...)`.
  - `_resolve_analyze_contract()` product-mode branch currently sets `evidence_confirm_policy="off"`.
  - developer-mode branch currently resolves `overrides.evidence_confirm_policy or "off"`.
  - `_effective_evidence_confirm_policy()` currently returns `off` for `checklist` and returns the resolved policy for `analyze`.
  - `_run_evidence_confirm_if_enabled()` calls only the injected Fund-layer runner with `project_chapter_facts(structured_data)`; Service does not read PDF/cache/source/parser artifacts directly.
  - `_raise_evidence_confirm_block_if_required()` blocks only when summary policy is `block` and status is `fail`.
- `fund_agent/ui/cli.py`
  - `analyze` exposes `--evidence-confirm-policy` only as a developer override flag and `_build_developer_overrides()` rejects it without `--dev-override`.
  - `checklist` has no Evidence Confirm CLI parameter.
  - `_echo_evidence_confirm_summary()` already prints safe summary lines when Service result carries `evidence_confirm_summary`.
- `fund_agent/fund/evidence_confirm_production.py`
  - `EvidenceConfirmProductionPolicy` is already `off|warn|block`.
  - `summary_from_repository_result()` aggregates pathway, deterministic and injected semantic statuses without exposing raw excerpts, paths, parser JSON or provider payloads.
- `fund_agent/fund/quality_gate_integration.py`
  - `run_quality_gate_for_bundle(..., evidence_confirm_summary=...)` merges ECQ issues only from compact summary.
  - `warn` policy maps fail summaries to ECQ warn; `block` policy maps fail summaries to ECQ block.
  - `score.json` remains Evidence Confirm unaware.
- Current tests assert the current opposite default and must be updated:
  - Service tests currently assert default analysis/checklist do not call fake Evidence Confirm runner.
  - CLI tests currently assert default analyze output has no Evidence Confirm lines.
  - checklist CLI tests assert no `--evidence-confirm-policy`; that assertion remains correct.

## Non-goals

- No checklist Evidence Confirm CLI support in this work unit.
- No provider-backed semantic client construction.
- No report-body or appendix Evidence Confirm rendering.
- No public `EvidenceSourceKind` or `EvidenceAnchor` expansion.
- No source fallback policy changes.
- No direct Service/UI/renderer/quality-gate access to repository internals, PDF/cache, source helpers, parser artifacts, Docling JSON, provider payloads or LLM clients.
- No Host/Agent runtime, LLM budget/provider/default, mark-ready, merge, release transition or PR external-state changes.

## Design And Control Alignment

- `docs/design.md` currently says default product `analyze` and `checklist` do not call Evidence Confirm, `analyze --dev-override --evidence-confirm-policy` is developer opt-in, checklist CLI support is future, and release/readiness remains `NOT_READY`.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` route the current active gate to Evidence Confirm Productionization release/readiness planning and forbid default-on, checklist CLI support, provider/live semantic quality, mark-ready, merge or release transition before separate reviewed gates.
- The requirements audit identifies default-on Evidence Confirm policy as the first blocker and checklist Evidence Confirm CLI support as a separate blocker.
- This plan updates only the first blocker for the product analysis-report family (`analyze` and inherited `analyze-annual-period`); it must leave `Release/readiness remains NOT_READY` after implementation because checklist CLI support, provider-backed semantic quality, multi-sample live coverage and PR/release transitions remain open.

## Recommended Default-on Policy

Decision:

- Product `analyze`: default `evidence_confirm_policy="warn"`.
- Product `analyze-annual-period`: inherits default `evidence_confirm_policy="warn"` through the existing product `analyze()` call path; no separate CLI flag or product opt-out is added.
- Product `checklist`: effective policy remains `off` in this work unit.
- Developer override `analyze`: `FundAnalysisDeveloperOverrides.evidence_confirm_policy` remains the only override field and may set `off|warn|block`; `--dev-override` without `--evidence-confirm-policy` keeps the CLI/default developer value `off` and does not inherit product `warn`.
- Developer override `checklist`: effective policy remains `off` until the checklist CLI/support gate.
- Product mode: no top-level request field and no CLI flag to disable Evidence Confirm.

Semantics:

- `warn` summary status `pass|warn|fail|not_run` is visible through existing safe stderr summary when present.
- EC fail under product `warn` must not raise `EvidenceConfirmBlockedError`.
- EC fail under product `warn` must project as ECQ warn when quality gate runs.
- Existing quality gate `block` remains the default product data-quality policy; FQ block/not-run behavior remains unchanged.
- Explicit developer `block` keeps current fail-closed semantics.

## Affected Modules

Implementation allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`
- `tests/fund/test_quality_gate_integration.py` for explicit ECQ warn-policy regressions; no production algorithm change expected.
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `README.md`

No other files are allowed in this work unit without plan review amendment.

## Contract And State-machine Changes

Service contract:

- Change product-mode resolved contract default from `evidence_confirm_policy="off"` to `evidence_confirm_policy="warn"`.
- Keep developer-mode resolved contract default as `overrides.evidence_confirm_policy or "off"` to preserve explicit developer sandbox behavior.
- Keep `--dev-override` without `--evidence-confirm-policy` as developer-mode `off`; this is an explicit developer sandbox default, not product behavior.
- Keep product-mode rejection of `developer_overrides`.
- Keep `_effective_evidence_confirm_policy(command_source="checklist") == "off"`.
- Keep `_effective_evidence_confirm_policy(command_source="analyze") == resolved_contract.evidence_confirm_policy`.
- Accept that `analyze-annual-period` inherits product `warn` because it delegates to `analyze()` and `_resolve_analyze_contract()`; do not add a special-case annual-period `off` branch unless this plan is amended.

CLI contract:

- Keep `--evidence-confirm-policy` behind `--dev-override`; do not create a product opt-out.
- Update help/docstring wording from opt-in-only to developer override wording.
- Keep checklist command without Evidence Confirm option.
- Keep existing safe stderr summary output; default analyze now prints it when Service returns summary.

Quality-gate contract:

- Do not modify `score.json`.
- Continue merging ECQ issues only into `quality_gate.json` / Markdown output through `run_quality_gate_for_bundle(..., evidence_confirm_summary=...)`.
- For product default `warn`, ECQ1/ECQ2/ECQ4 fail severities must be `warn`; ECQ3 remains `warn`.

Renderer contract:

- No Evidence Confirm content in report Markdown body or evidence appendix.

## Implementation Slices

### Slice EC-DO-1: Service Default-on Analyze Policy

Objective: make product `analyze` and inherited `analyze-annual-period` run Evidence Confirm by default with warn policy while preserving checklist off and developer-mode override.

Allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service.py`

Exact changes:

- In `_resolve_analyze_contract()` product-mode branch, set `evidence_confirm_policy="warn"`.
- Update these exact service docstrings/comments if they still describe Evidence Confirm as developer-only:
  - `FundAnalysisDeveloperOverrides.evidence_confirm_policy`: say this field only affects developer mode; omitted developer policy remains `off` and does not inherit product `warn`.
  - `_run_evidence_confirm_if_enabled()`: say it runs according to the effective resolved policy; product `analyze`/`analyze-annual-period` default can be `warn`, while `checklist` remains `off`.
  - `_effective_evidence_confirm_policy()`: say `checklist` is forcibly `off`; `analyze` command-source uses the resolved contract policy, including product default `warn`.
- Do not add fields to `FundAnalysisRequest`.
- Do not move Evidence Confirm policy into `extra_payload`.
- Do not alter `FundAnalysisDeveloperOverrides` field shape.
- Do not change runner request shape or repository/source boundaries.
- Do not change `_effective_evidence_confirm_policy()` checklist off behavior except comment/docstring wording.

Required tests:

- Add a product-mode `analyze` test with fake extractor and fake Evidence Confirm runner returning pass:
  - assert extractor called once;
  - assert runner called once;
  - assert runner request uses normalized fund code, report year, non-null projection and request `force_refresh`;
  - assert result summary policy is `warn`;
  - assert report Markdown is still produced.
- Add a product-mode `analyze` test with fake runner fail and quality gate off or warn:
  - assert no `EvidenceConfirmBlockedError`;
  - assert summary status is `fail`;
  - assert policy is `warn`.
- Add a product-mode `analyze` test with fake runner raising an exception:
  - assert the exception does not propagate;
  - assert result carries a safe compact Evidence Confirm summary;
  - assert summary policy is `warn`;
  - assert no raw exception internals, excerpt, PDF path, parser payload or provider payload leaks.
- Add a product-mode `analyze_multi_year_annual()` or CLI-equivalent service-path test:
  - assert the default product annual-period path invokes the fake Evidence Confirm runner through the delegated `analyze()` path;
  - assert summary policy is `warn`;
  - assert no special-case annual-period `off` branch is introduced.
- Add or adjust checklist test:
  - assert product/default `checklist` does not call runner;
  - assert `evidence_confirm_summary is None`.
- Preserve developer override tests:
  - `--dev-override` or `FundAnalysisDeveloperOverrides` without an explicit Evidence Confirm policy keeps Evidence Confirm `off`;
  - explicit `warn` calls runner;
  - explicit `block` still blocks on fail;
  - product mode still rejects `developer_overrides`.

Stop conditions:

- Stop if making product default warn requires a top-level public opt-out field.
- Stop if checklist must be changed to satisfy tests.
- Stop if Service would need direct repository/PDF/cache/source/parser/provider access.

### Slice EC-DO-2: CLI Surface And No-opt-out Guard

Objective: align CLI behavior and tests with product analyze default warn without adding a product disable flag.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Exact changes:

- Update `--evidence-confirm-policy` help text to say it is a developer override for `off|warn|block`, not the product default opt-in.
- Keep `_build_developer_overrides()` rejection when `--evidence-confirm-policy` is provided without `--dev-override`.
- Keep `_build_developer_overrides()` behavior where plain `--dev-override` uses the CLI default `evidence_confirm_policy="off"` and therefore disables Evidence Confirm for that developer run.
- Keep checklist command with no Evidence Confirm parameter.
- Keep `_echo_evidence_confirm_summary()` safe fields only.
- Do not add `--no-evidence-confirm`, `--evidence-confirm`, or checklist Evidence Confirm flags.

Required tests:

- Replace the current default analyze "no Evidence Confirm lines" test with a default product analyze test using a fake Service result carrying a safe summary:
  - assert `mode == "product"`;
  - assert `developer_overrides is None`;
  - assert `evidence_confirm_status`, `evidence_confirm_policy: warn`, checked/failed counts and auditability score print to stderr/output;
  - assert report body still prints after summary;
  - assert no excerpt/PDF/path/parser/provider payload appears.
- Keep `test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override`.
- Add or keep a CLI developer-mode test proving plain `--dev-override` without `--evidence-confirm-policy` does not inherit product `warn`.
- Keep checklist help/command tests asserting `--evidence-confirm-policy` is absent.
- Keep Evidence Confirm block CLI test for explicit developer `block`.

Stop conditions:

- Stop if Typer requires exposing a product opt-out to represent the default.
- Stop if default analyze output would require report-body rendering changes.

### Slice EC-DO-3: Quality Gate Regression Guard

Objective: prove the existing ECQ mapping is sufficient for product default warn and remains boundary-safe.

Allowed files:

- `tests/fund/test_quality_gate_integration.py`

Exact changes:

- Prefer no production code change.
- Add or keep an explicit regression that `policy="warn", status="fail", deterministic_status="fail"` maps to `ECQ2/warn` and gate status `warn`.
- Add an explicit pathway regression that `policy="warn"` and `pathway_status="fail"` maps to `ECQ1/warn`, not `block`.
- Keep `score.json` Evidence Confirm unaware.
- Keep static boundary test forbidding repository/source/parser/provider imports in quality gate integration.

Stop conditions:

- Stop if supporting product default warn requires changing `quality_gate.py` score schema.
- Stop if quality gate integration tries to read source/PDF/parser artifacts.

### Slice EC-DO-4: Documentation And Control Sync

Objective: make truth docs match the accepted implementation without claiming release readiness.

Allowed files:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `README.md`

Exact changes:

- `docs/design.md`:
  - update Evidence Confirm current-state wording to say default product `analyze` runs Evidence Confirm with `warn`;
  - state that product `analyze-annual-period` inherits that `warn` policy through the existing `analyze()` delegation path, with no separate product opt-out;
  - keep `checklist` Evidence Confirm support as future/separate gate;
  - keep provider-backed semantic quality, report-body rendering, mark-ready, merge and release transition as future/not authorized;
  - keep release/readiness `NOT_READY`.
- `docs/implementation-control.md` and `docs/current-startup-packet.md`:
  - record accepted default-on analyze policy implementation after code/tests pass;
  - preserve remaining blockers and next gates.
- `README.md`:
  - update user-facing analyze behavior if the README describes Evidence Confirm or quality summary output;
  - do not document a product disable flag.

Stop conditions:

- Stop if docs would need to claim full release readiness.
- Stop if control sync requires PR mark-ready, push, merge, or external state mutation.

## Tests And Validation Commands

Targeted deterministic validation:

Service test labels:

- New/updated: `test_fund_analysis_service_product_analyze_defaults_evidence_confirm_warn`
- New/updated: `test_fund_analysis_service_product_analyze_evidence_confirm_warn_fail_does_not_block`
- New: `test_fund_analysis_service_product_analyze_warn_runner_exception_becomes_safe_summary`
- New: `test_fund_analysis_service_analyze_annual_period_defaults_evidence_confirm_warn`
- New/updated: `test_fund_analysis_service_checklist_defaults_evidence_confirm_off`
- Existing: `test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off`
- Existing: `test_fund_analysis_service_product_mode_rejects_evidence_confirm_override`

```text
uv run pytest -q \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_product_analyze_defaults_evidence_confirm_warn \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_product_analyze_evidence_confirm_warn_fail_does_not_block \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_product_analyze_warn_runner_exception_becomes_safe_summary \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_analyze_annual_period_defaults_evidence_confirm_warn \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_checklist_defaults_evidence_confirm_off \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off \
  tests/services/test_fund_analysis_service.py::test_fund_analysis_service_product_mode_rejects_evidence_confirm_override
```

CLI test labels:

- New/updated: `test_analyze_cli_default_prints_evidence_confirm_warn_summary`
- Existing: `test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override`
- New/updated: `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`
- Existing/updated: `test_analyze_cli_evidence_confirm_block_exits_2_without_report_body`
- Existing: `test_checklist_cli_help_does_not_expose_evidence_confirm_policy`
- Existing: `test_checklist_cli_rejects_use_llm_option`

```text
uv run pytest -q \
  tests/ui/test_cli.py::test_analyze_cli_default_prints_evidence_confirm_warn_summary \
  tests/ui/test_cli.py::test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override \
  tests/ui/test_cli.py::test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off \
  tests/ui/test_cli.py::test_analyze_cli_evidence_confirm_block_exits_2_without_report_body \
  tests/ui/test_cli.py::test_checklist_cli_help_does_not_expose_evidence_confirm_policy \
  tests/ui/test_cli.py::test_checklist_cli_rejects_use_llm_option
```

Quality-gate test labels:

- Existing/updated: `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn`
- New: `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn`
- Existing: `test_score_json_schema_remains_evidence_confirm_unaware`
- Existing: `test_quality_gate_integration_boundary_no_repository_or_source_imports`

```text
uv run pytest -q \
  tests/fund/test_quality_gate_integration.py::test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn \
  tests/fund/test_quality_gate_integration.py::test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn \
  tests/fund/test_quality_gate_integration.py::test_score_json_schema_remains_evidence_confirm_unaware \
  tests/fund/test_quality_gate_integration.py::test_quality_gate_integration_boundary_no_repository_or_source_imports
```

Broader deterministic validation before implementation closeout:

```text
uv run pytest -q tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/test_quality_gate_integration.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md
```

No live/PDF/network/provider/LLM commands are authorized by this plan.

## Risks And Open Questions

- Remaining release blockers after this work unit:
  - checklist Evidence Confirm CLI/support remains separate gate;
  - provider-backed/live semantic quality remains unproven;
  - multi-sample live source/PDF coverage remains unproven;
  - report-body Evidence Confirm rendering remains unauthorized unless a future product gate requires it;
  - PR-40 mark-ready, merge and release transition remain unauthorized.
- Developer mode can explicitly disable Evidence Confirm through `FundAnalysisDeveloperOverrides.evidence_confirm_policy="off"` or `--dev-override --evidence-confirm-policy off`. This is accepted as bounded developer behavior, not product behavior.
- Plain `--dev-override` without `--evidence-confirm-policy` also keeps Evidence Confirm `off` through the CLI/developer default. This must be documented in tests and code comments as developer sandbox behavior so it is not mistaken for product default `warn`.
- Default `warn` may surface EC fail summaries without blocking output. This is intentional for first default-on release-readiness step; `block` requires later evidence gates.

No blocking open question remains for this plan. If reviewers require checklist default-on in the same work unit, this plan must be amended before implementation because that would authorize a separate blocker and CLI/UX contract.

## Plan Review Fix Notes

- DS F1 fixed: the plan now declares `analyze-annual-period` as an inherited product default `warn` path and requires a dedicated no-live regression.
- DS F2 fixed: the plan now states that plain `--dev-override` without `--evidence-confirm-policy` keeps Evidence Confirm `off`.
- DS F3 fixed: service docstring/comment updates name the exact locations and intended wording.
- DS F4 fixed: validation targets are labeled as new, updated, or existing before the commands.
- MiMo F001 fixed: ECQ1 pathway fail under product/default `warn` is now an explicit required regression, not conditional wording.
- MiMo F002 fixed: product default `warn` runner-exception safe-summary behavior is now an explicit required service regression.

## Completion Report Format

Implementation closeout must report:

- artifact path(s);
- default-on decision actually implemented;
- changed files;
- tests/validation commands and results;
- docs/control sync performed;
- residual blockers and owner/next gate;
- explicit statement that no live/PDF/network/provider/LLM command, PR mark-ready, merge or release transition was performed.

## Verdict

PLAN_READY_FOR_REVIEW
