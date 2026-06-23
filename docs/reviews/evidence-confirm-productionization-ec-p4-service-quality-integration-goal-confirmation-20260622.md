# Evidence Confirm Productionization EC-P4 Service/UI/Renderer/Quality-Gate Integration Goal Confirmation

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `goal confirmation`
- Classification: `heavy`
- Control source: `docs/implementation-control.md`
- Design source: `docs/design.md`
- Timestamp: `2026-06-22 21:13 Asia/Shanghai`
- Controller verdict: `GOAL_CONFIRMED_READY_FOR_PLAN_GATE_WITH_SCOPE_GUARDS`

## Current State

EC-P1A, EC-P2 and EC-P3 are accepted inputs:

- EC-P1A closed no-live annual-report reference materialization.
- EC-P2 closed repository-bounded live source/PDF pathway for the exact authorized sample.
- EC-P3 closed no-live Fund-layer semantic entailment companion contract.

PR-40 remains draft/open at remote head `9db22cf931421563653e17cd2816cd80ad9d09fc`, merge state `CLEAN`, CI `test=SUCCESS`. Local branch `evidence-confirm-productionization` is ahead of origin by one EC-P3 local closeout commit. Release/readiness remains `NOT_READY`.

Current production path does not yet consume Evidence Confirm:

- `fund_agent/services/fund_analysis_service.py` imports `run_quality_gate_for_bundle`, `render_template_report`, and `run_programmatic_audit`, but has no Evidence Confirm import or result field.
- `FundAnalysisService.analyze()` renders `TemplateRenderInput`, runs `run_programmatic_audit(render_result.audit_input)`, and returns `FundAnalysisResult` with quality gate fields only.
- `FundAnalysisService.checklist()` returns `FundChecklistResult` with quality gate fields only.
- `_run_analysis_core()` extracts `StructuredFundDataBundle`, runs quality gate, derives final judgment, and returns `_AnalysisCoreResult`; it does not project chapter facts or run Evidence Confirm.
- `fund_agent/fund/template/renderer.py` defines `TemplateRenderInput` and `TemplateRenderResult` without Evidence Confirm input/output.
- `fund_agent/fund/quality_gate.py` consumes `score.json` quality signals and emits FQ quality gate status; it does not accept Evidence Confirm V2 or semantic results.
- `fund_agent/ui/cli.py` prints only `quality_gate_*` stderr summary for analyze/checklist; it does not expose Evidence Confirm status.

Current accepted Fund-layer seams:

- `fund_agent/fund/chapter_facts.py` provides `project_chapter_facts()` and `ChapterFactProjection` from `StructuredFundDataBundle` without repository/PDF/cache/source access.
- `fund_agent/fund/evidence_confirm.py` provides `confirm_projection_evidence_v2()` over explicit references.
- `fund_agent/fund/evidence_confirm_sources.py` provides `build_annual_report_evidence_confirm_references()` and `run_repository_bounded_evidence_confirm()` through the `FundDocumentRepository.load_annual_report()` boundary.
- `fund_agent/fund/evidence_confirm_semantic.py` provides no-live `confirm_semantic_entailment()` with explicit claims and injected `EvidenceEntailmentClient`.

## First-Principles Judgment

The work unit is valid. The user-requested end state requires Evidence Confirm to become part of the production-facing analysis path, not remain only a standalone helper/test harness.

The core product problem is not "more scoring code"; it is a boundary and contract problem:

1. Service must decide when and how Evidence Confirm is requested for `analyze` / `checklist`.
2. Fund layer must remain the owner of document repository access, reference materialization, V2 deterministic scoring, and semantic entailment mechanics.
3. Renderer/UI/quality gate must surface or consume Evidence Confirm without directly touching PDF/cache/source helpers or Docling/parser artifacts.
4. Quality gate semantics must distinguish field quality FQ status from Evidence Confirm E-rule/source-support status; otherwise a strict source failure could be hidden behind an otherwise passing FQ score.

Therefore EC-P4 should proceed to a plan gate. The plan must be code-generation-ready and should be assigned to an Agent per `phaseflow` rather than written by the controller.

## Goal

Integrate accepted Evidence Confirm capabilities into the production Service/UI/renderer/quality-gate surface in a typed, fail-closed, boundary-respecting way.

Minimum target for the next plan:

- Add explicit Service request/contract controls for Evidence Confirm execution or reporting.
- Add typed result fields so `FundAnalysisResult` / `FundChecklistResult` can carry Evidence Confirm outcomes.
- Use `ChapterFactProjection` as the deterministic bridge from `StructuredFundDataBundle` to Evidence Confirm.
- Keep all annual-report source/PDF access inside Fund-layer repository-bounded capability.
- Define how renderer and CLI expose Evidence Confirm status without implying release readiness.
- Define how quality gate consumes Evidence Confirm status, including strict fail/warn/not-run mapping.
- Preserve semantic entailment as no-live/injected-client unless the plan explicitly creates a separate provider-backed gate.

## Success Signals

- Production `analyze` and/or `checklist` can produce a structured Evidence Confirm status from current analysis inputs through accepted Fund-layer boundaries.
- No Service/UI/renderer/quality-gate code directly calls PDF cache, source helper, parser JSON, Docling artifacts, or specific annual-report source adapters.
- Evidence Confirm V2 status and repository/pathway status are visible in Service results and CLI/UI-facing summary.
- Renderer either accepts a typed Evidence Confirm summary or records a deliberate non-rendering decision; no silent omission.
- Quality gate has explicit behavior for Evidence Confirm `pass/warn/fail/not_run` and does not conflate it with existing FQ0-FQ6 field-quality rules.
- Semantic entailment remains explicit and bounded: no provider-backed semantic quality claim is made without a separately reviewed provider/client construction gate.
- Tests prove Service result propagation, CLI/UI summary behavior, renderer or non-rendering decision, quality gate mapping, and boundary guards.

## Non-Goals

- No live/PDF command rerun without new explicit user authorization.
- No provider-backed semantic client construction in Service by default.
- No mark-ready, merge, release, or readiness transition.
- No direct Service/UI/renderer/quality-gate access to PDF cache, source helpers, specific source adapters, Docling JSON, pdfplumber JSON, or EID HTML render artifacts.
- No `EvidenceSourceKind` public expansion unless the plan proves it is required and keeps migration scoped.
- No parser replacement, source fallback strategy change, golden/readiness promotion, or baseline/golden qualification.
- No change to existing `quality_gate_policy=block` semantics unless the plan specifies exact user-visible behavior and tests.
- No claim that EC-P2 single authorized live sample proves general live correctness.

## Scope Boundary

Allowed planning surface:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/fund/evidence_confirm*.py` only for additive public-summary helpers if required
- `fund_agent/fund/chapter_facts.py` only for additive projection helpers if required
- focused tests under `tests/services/`, `tests/fund/`, and UI/CLI test locations
- README/design/control docs required by changed production behavior

Files/modules requiring explicit plan justification:

- repository/source/PDF internals
- public extractor evidence models
- parser/candidate document modules
- Host/Agent runtime
- provider/LLM construction
- release/readiness automation

## Blocking Open Questions For Plan Gate

The following are not blockers to goal confirmation, but must be resolved in the plan artifact before implementation:

1. Should EC-P4 first integrate deterministic V2/source pathway only, leaving semantic entailment as a typed optional companion, or should semantic no-live injected-client propagation also be part of the first slice?
2. Should production `analyze` run repository-bounded Evidence Confirm by default, or should it be opt-in because it can trigger live/repository/PDF work?
3. Should strict V2 `fail` block report output under `quality_gate_policy=block`, or should EC status first surface as warn/not-ready metadata until broader samples are accepted?
4. Should renderer append an Evidence Confirm section to the report, or should UI/CLI expose it outside report Markdown to avoid mixing audit status into investment analysis content?
5. What exact quality gate issue codes and severities should represent Evidence Confirm failures, warnings, and not-run states?

## Controller Decision

Proceed to EC-P4 plan gate after user confirmation.

The next concrete task must be dispatched to an Agent with a code-generation-ready plan assignment. The controller must not write the implementation plan itself.

Expected next handoff:

- Gate: `plan`
- Required skill: `gateflow` for task framing; plan review later must use `planreview`
- Candidate assignee: `AgentCodex` or `AgentDS`
- Expected artifact path: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- Stop condition: write exactly the plan artifact and stop; no source changes, no tests, no commit, no push, no PR mutation.

