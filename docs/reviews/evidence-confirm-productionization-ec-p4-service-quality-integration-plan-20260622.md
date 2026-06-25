# Evidence Confirm Productionization EC-P4 Service/UI/Renderer/Quality-Gate Integration Plan

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `plan`
- Classification: `heavy`
- Branch: `evidence-confirm-productionization`
- Plan artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## Goal / Motivation / Success Signal

Goal: integrate accepted Evidence Confirm capabilities into the production-facing `analyze` / `checklist` path through typed Service contracts, CLI/UI summaries, and quality-gate issue projection, while preserving the Fund-layer repository boundary and `NOT_READY` readiness state.

Motivation: EC-P1A, EC-P2 and EC-P3 closed Fund-layer capabilities, but production `FundAnalysisService`, CLI, renderer and quality gate still do not consume them. Without a typed integration plan, implementation would have to invent request fields, source ownership, blocking semantics, UI behavior and issue taxonomy in one pass.

Success signal:

- `FundAnalysisService.analyze()` can optionally run deterministic repository-bounded Evidence Confirm through a Fund-layer facade in developer override mode.
- `FundAnalysisService.checklist()` remains default off/no runner in the first implementation slice; checklist Evidence Confirm CLI support is deferred to a later explicit gate.
- `FundAnalysisResult` and `FundChecklistResult` carry a compact typed Evidence Confirm summary without raw excerpts.
- CLI exposes Evidence Confirm summary lines for `analyze` on stderr/stdout as appropriate, with an explicit opt-in flag.
- Quality gate can map Evidence Confirm `pass / warn / fail / not_run` into stable `ECQ*` issues without reading documents.
- Renderer behavior is deliberate: EC-P4 does not append Evidence Confirm content to report Markdown; UI/CLI exposes it outside the investment report body.
- Semantic entailment remains a no-live injected-client companion and is not provider-backed or default-constructed.
- Release/readiness remains `NOT_READY`; PR-40 remains draft/open.

## Non-Goals / Scope Boundary

Non-goals:

- No default-on Evidence Confirm in product mode.
- No live/PDF/network/provider/LLM command execution in this gate or in no-live implementation tests.
- No provider-backed semantic client construction in Service/UI/renderer/quality gate.
- No Service/UI/renderer/quality-gate direct access to PDF cache, source helper, source adapter, parser JSON, Docling artifacts, pdfplumber JSON or EID HTML render artifacts.
- No `EvidenceSourceKind` or public `EvidenceAnchor` schema expansion.
- No parser replacement, fallback-source strategy change, golden promotion, readiness claim, PR mark-ready, merge, push or release transition.
- No claim that EC-P2's single authorized live sample proves general live correctness.
- No mutation of `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md` in this plan gate.

Implementation scope is limited to later code changes under:

- `fund_agent/fund/evidence_confirm_sources.py` or a new `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- focused tests under `tests/fund/`, `tests/services/`, `tests/ui/`
- README/design/control docs only in the later implementation/docs-sync gate required by actual source behavior changes.

Renderer scope decision: no report Markdown section in EC-P4. `fund_agent/fund/template/renderer.py` is not modified unless implementation review requires an explicit no-rendering guard type. Visibility is via Service result and CLI/UI summary outside the report body.

## Design / Control Alignment

- `AGENTS.md` requires production annual-report PDF access through `FundDocumentRepository` and forbids Service/UI/renderer/quality gate from calling concrete PDF cache/source/parser internals.
- `docs/design.md` states the current default deterministic chain is `CLI -> FundAnalysisService.analyze/checklist -> FundDataExtractor.extract -> quality gate -> P2 analysis -> renderer -> audit`, and that Service may call Fund public capabilities during the transition path.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` identify the current active gate as Service/UI/renderer/quality-gate production integration, classification `heavy`, with PR-40 draft/open and release/readiness `NOT_READY`.
- The controller goal confirmation artifact says current production path has no Evidence Confirm import/result field and requires this plan to resolve five open plan questions.

## First-Principles Judgment + Direct Code Evidence

First-principles judgment:

Evidence Confirm is a source-support gate, not a renderer feature and not a field coverage score. The correct integration layer is therefore:

1. Fund layer owns source/repository/reference materialization and deterministic V2/semantic mechanics.
2. Service owns user-visible policy, typed request/result propagation and error semantics.
3. Quality gate owns machine-readable issue projection.
4. CLI/UI owns status display and exit behavior.
5. Renderer should not mix audit status into the investment report body until a separate content-design gate accepts the wording.

Direct code evidence:

- `fund_agent/services/fund_analysis_service.py` imports `run_quality_gate_for_bundle`, `render_template_report` and `run_programmatic_audit`, but has no Evidence Confirm import or result field.
- `FundAnalysisDeveloperOverrides` already carries explicit developer-only knobs such as `quality_gate_policy`; this is the narrowest current opt-in surface for EC-P4.
- `FundAnalysisRequest` has no top-level Evidence Confirm field; product mode rejects developer overrides, so adding only a developer override preserves product default behavior.
- `FundAnalysisService.analyze()` calls `_run_analysis_core()`, then renders `TemplateRenderInput`, then runs programmatic audit, then returns `FundAnalysisResult`.
- `FundAnalysisService.checklist()` returns `_run_analysis_core()` result without renderer involvement.
- `_run_analysis_core()` extracts `StructuredFundDataBundle`, runs quality gate, then P2 analysis/final judgment. It currently does not call `project_chapter_facts()` or Evidence Confirm.
- `fund_agent/fund/template/renderer.py` defines `TemplateRenderInput` / `TemplateRenderResult` without Evidence Confirm fields and always renders the existing report/evidence sections.
- `fund_agent/fund/quality_gate.py` defines `QualityGateIssue`, `QualityGateResult`, FQ0-FQ6 aggregation and Markdown/JSON serialization from score payloads.
- `fund_agent/fund/quality_gate_integration.py` states it does not re-extract fund documents and adapts an already extracted `StructuredFundDataBundle` into snapshot/score/quality-gate outputs.
- `fund_agent/fund/chapter_facts.py` projects `StructuredFundDataBundle` into `chapter_fact_projection.v1` without reading PDF/cache/source helpers.
- `fund_agent/fund/evidence_confirm_sources.py` provides `run_repository_bounded_evidence_confirm()` and explicitly confines repository loading to `FundDocumentRepository.load_annual_report()`.
- `fund_agent/fund/evidence_confirm_semantic.py` is no-live and requires an injected `EvidenceEntailmentClient`; it does not construct provider clients.
- `fund_agent/ui/cli.py` already has `_echo_quality_gate_summary()`, quality-gate blocked handlers and Typer option parsing; it has no Evidence Confirm summary output.

## Controller Artifact Five Questions: Plan Decisions

1. First slice: deterministic repository-bounded V2/source pathway only. Semantic no-live injected-client companion is a later additive slice because Service/UI/quality-gate behavior can be proven without provider-backed or client-injected semantic judgment.
2. Production first slice: `analyze` opt-in only. Add explicit `FundAnalysisDeveloperOverrides.evidence_confirm_policy: Literal["off", "warn", "block"] | None = None` and CLI `fund-analysis analyze --evidence-confirm-policy off|warn|block`, accepted only in developer override mode. Product default remains off. `checklist` Evidence Confirm CLI support is deferred because the current checklist command has no developer override mode path; default checklist behavior remains off/no runner.
3. Strict V2 fail under `quality_gate_policy=block`: if Evidence Confirm was explicitly requested with `evidence_confirm_policy="block"`, strict V2 fail must block report output by projecting an `ECQ2/block` issue into the combined quality gate result or by raising `EvidenceConfirmBlockedError` when quality gate is off/not runnable. If Evidence Confirm is off or warn, `quality_gate_policy=block` must not silently infer readiness; quality gate may emit `ECQ0/info reason=not_requested` when EC is off, and CLI emits EC summary lines only when EC was requested.
4. Renderer: deliberate non-rendering in EC-P4. Do not append an Evidence Confirm section to report Markdown. CLI/UI exposes Evidence Confirm outside report Markdown. This avoids mixing audit status into investment analysis content before wording and user experience are separately reviewed.
5. Quality gate issue codes/severities:
   - `ECQ0/info`: Evidence Confirm not run or policy off.
   - `ECQ1/block|warn`: repository/source/reference materialization pathway failure.
   - `ECQ2/block|warn`: deterministic V2 hard-gate fail.
   - `ECQ3/warn`: deterministic V2 warn, including accepted anchor-precision warnings.
   - `ECQ4/block|warn`: semantic companion fail/insufficient/contradicted/malformed client result when a later semantic slice provides a no-live injected result.

## Affected Files / Modules

Production modules:

- `fund_agent/fund/evidence_confirm_production.py` (new preferred module) or `fund_agent/fund/evidence_confirm_sources.py` for compact summary/projection helpers.
- `fund_agent/fund/quality_gate.py` for optional `ECQ*` issue/result types and merged serialization.
- `fund_agent/fund/quality_gate_integration.py` for optional Evidence Confirm summary ingestion.
- `fund_agent/services/fund_analysis_service.py` for request/result fields, dependency injection, execution order and blocking errors.
- `fund_agent/ui/cli.py` for opt-in flag parsing and summary output.

Test modules:

- `tests/fund/test_evidence_confirm_sources.py` or new `tests/fund/test_evidence_confirm_production.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`

Deliberately not modified in first implementation pass:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/documents/repository.py`
- PDF cache/source helpers/source adapters/parser/candidate modules
- Host/Agent runtime
- provider/LLM config or clients

## Contract / Schema / State-Machine / Public Interface Changes

### New Fund-layer production summary

Add a compact summary type in `fund_agent/fund/evidence_confirm_production.py`:

```python
EvidenceConfirmProductionPolicy = Literal["off", "warn", "block"]
EvidenceConfirmProductionStatus = Literal["pass", "warn", "fail", "not_run"]

@dataclass(frozen=True, slots=True)
class EvidenceConfirmProductionSummary:
    schema_version: Literal["evidence_confirm_production_summary.v1"]
    policy: EvidenceConfirmProductionPolicy
    status: EvidenceConfirmProductionStatus
    fund_code: str
    report_year: int
    pathway_status: Literal["pass", "fail", "not_run"]
    deterministic_status: Literal["pass", "warn", "fail", "not_applicable", "not_run"]
    semantic_status: Literal["pass", "warn", "fail", "not_applicable", "not_run"]
    checked_fact_count: int
    failed_fact_count: int
    warning_fact_count: int
    not_applicable_fact_count: int
    issue_count: int
    auditability_score: int | None
    blocking_issue_ids: tuple[str, ...]
    warning_issue_ids: tuple[str, ...]
    not_run_reason: str | None
```

Invariants:

- Summary never contains raw excerpts.
- Summary never contains parser JSON, PDF path, cache path or source adapter object.
- `policy="off"` implies `status="not_run"` and stable reason code `policy_off` only when a helper explicitly creates a not-run summary. In the normal Service path, `summary=None` means EC was not requested.
- Aggregate summary status precedence is `fail > warn > pass > not_run/not_applicable`; `pathway_status="fail"` always produces aggregate `status="fail"`.
- `deterministic_status="fail"` implies `status="fail"`.
- `deterministic_status="warn"` implies `status="warn"` unless a semantic fail is present in a later slice.
- Semantic fields remain `not_run` in the deterministic first slice.
- Stable reason codes are closed for EC-P4: `not_requested`, `policy_off`, `runner_exception:<class_name>`, `repository_failure:<reason>` and `invalid_request`. Add a new stable code plus tests before introducing any other reason string.

### Service request/result contracts

Add to `FundAnalysisDeveloperOverrides`:

```python
evidence_confirm_policy: EvidenceConfirmProductionPolicy | None = None
```

Effective Service policy:

- `developer_overrides is None` -> `off`
- `developer_overrides.evidence_confirm_policy is None` -> `off`
- explicit `off / warn / block` -> same value
- product mode with any developer override continues to raise the existing product-mode validation error.

Add to `ResolvedAnalyzeContract`:

```python
evidence_confirm_policy: EvidenceConfirmProductionPolicy
```

Add to `_AnalysisCoreResult`, `FundAnalysisResult`, `FundChecklistResult` and `FundLLMAnalysisResult` only if the LLM path is wired in the same implementation pass:

```python
evidence_confirm_summary: EvidenceConfirmProductionSummary | None = None
```

Implementation should prefer deterministic `analyze` first. `FundChecklistResult` may carry the field for type symmetry if `_AnalysisCoreResult` is shared, but first-slice checklist remains off/no runner and is not user-invoked via checklist CLI. LLM path can be deferred unless the implementation slice explicitly includes equal tests for hosted LLM.

### Service dependency injection

Add a Protocol-like callable field on `FundAnalysisService.__init__`:

```python
EvidenceConfirmRunner = Callable[[EvidenceConfirmRepositoryRunRequest], Awaitable[EvidenceConfirmRepositoryRunResult]]
```

Default runner is the Fund-layer `run_repository_bounded_evidence_confirm`. Tests inject fake async runners. Service must not instantiate `FundDocumentRepository`, inspect PDF/cache/source state or call materializer internals.

### State machine

Per request:

1. Resolve request and developer overrides.
2. Extract `StructuredFundDataBundle`.
3. If Evidence Confirm policy is `off`, do not call the runner and leave the Service result field `None`. `summary=None` means Evidence Confirm was not requested. If quality gate runs and needs an explicit issue, the quality-gate integration helper emits `ECQ0/info` with `reason=not_requested` from `summary=None`; Service does not allocate a summary for policy off.
4. If policy is `warn` or `block`:
   - build `ChapterFactProjection` with `project_chapter_facts(structured_data)`;
   - call the injected Fund-layer repository-bounded runner with explicit `fund_code`, `report_year`, `projection`, `force_refresh`;
   - convert repository result to `EvidenceConfirmProductionSummary`.
5. If the runner raises, convert it to a fail-closed `EvidenceConfirmProductionSummary` with `status="fail"` and stable reason code `runner_exception:<class_name>`; do not propagate an unstructured runner exception to CLI. If policy is `block`, this summary participates in the same blocking table below; if policy is `warn`, continue with the fail summary as warn-visible metadata.
6. Run quality gate if enabled, passing the optional summary to `run_quality_gate_for_bundle()`.
7. Blocking follows the decision table below.
8. Continue existing P2 analysis/render/audit.

Combined blocking decision table:

| `quality_gate_policy` | `evidence_confirm_policy` | EC aggregate status | FQ / combined gate status | Preferred error type | Exit behavior | ECQ issue placement |
|---|---|---|---|---|---|---|
| `off` | `warn` | `pass` | quality gate not run | none | report continues; CLI prints EC summary | no `QualityGateResult`; summary only |
| `off` | `warn` | `warn` or `fail` | quality gate not run | none | report continues; CLI prints warn/fail summary | no `QualityGateResult`; summary only |
| `off` | `block` | `pass` | quality gate not run | none | report continues; CLI prints EC summary | no `QualityGateResult`; summary only |
| `off` | `block` | `warn` | quality gate not run | none | report continues; CLI prints EC warn summary | no `QualityGateResult`; summary only |
| `off` | `block` | `fail` | quality gate not run | `EvidenceConfirmBlockedError` | exit code `2`, no report body | error carries safe summary; no `QualityGateResult` |
| `warn` | `warn` | `pass` / `warn` / `fail` | combined gate emitted as warn/pass/block by existing aggregation, but policy warn does not block | none | report continues; CLI prints quality + EC summary | ECQ issues included in `QualityGateResult`; ECQ severity follows EC policy warn |
| `warn` | `block` | `pass` | combined gate emitted; quality policy warn does not block | none | report continues | ECQ pass/no blocking issue |
| `warn` | `block` | `warn` | combined gate emitted; quality policy warn does not block | none | report continues with EC warn summary | ECQ warn issue included |
| `warn` | `block` | `fail` | combined gate includes ECQ block | `EvidenceConfirmBlockedError` | exit code `2`, no report body | error carries safe summary; EC policy block overrides quality warn policy for EC fail |
| `block` | `warn` | `pass` / `warn` / `fail` | combined gate status decides output | `QualityGateBlockedError` only if combined status is `block` | exit code `2` only when combined status blocks; otherwise report continues | ECQ issues included in `QualityGateResult`; no `EvidenceConfirmBlockedError` |
| `block` | `block` | `pass` / `warn` | combined gate status decides output | `QualityGateBlockedError` only if FQ/combined status is `block` | exit code `2` only when combined status blocks; otherwise report continues | ECQ issues included in `QualityGateResult` |
| `block` | `block` | `fail` | combined gate must re-aggregate to `block` after ECQ2/block merge | `QualityGateBlockedError` | exit code `2`, no report body | ECQ block issues are inside `QualityGateBlockedError.quality_gate_result`; do not raise `EvidenceConfirmBlockedError` |

Error ordering invariant: `QualityGateBlockedError` remains the canonical blocker when quality gate runs and contains merged ECQ issues. `EvidenceConfirmBlockedError` is EC-only blocking and is used only when quality gate is off/not runnable, or when `quality_gate_policy="warn"` but EC policy is explicitly `block` and EC fails.

### CLI public interface

Add Typer option to `analyze` only:

```text
--evidence-confirm-policy [off|warn|block]
```

Contract:

- Default is absent/`off`.
- It requires developer override mode for `analyze`, matching current quality-gate override discipline.
- `checklist` Evidence Confirm CLI support is explicitly deferred to a later slice/gate. Do not add `--evidence-confirm-policy` or `--mode developer_override` to checklist in the first implementation pass. Default checklist remains off/no runner; if `FundChecklistResult` has `evidence_confirm_summary`, it is always `None` in this first slice unless a later approved gate changes checklist request construction.
- CLI does not run Evidence Confirm directly and does not construct repositories/providers.
- On success with Evidence Confirm requested, stderr includes:
  - `evidence_confirm_status: <pass|warn|fail|not_run>`
  - `evidence_confirm_policy: <off|warn|block>`
  - `evidence_confirm_checked_facts: <int>`
  - `evidence_confirm_failed_facts: <int>`
  - `evidence_confirm_auditability_score: <int|none>`
- On `EvidenceConfirmBlockedError`, exit code `2`, no report body, stderr includes the summary lines and `Evidence Confirm 阻断报告输出`.

### Quality gate issue taxonomy

Add `ECQ*` rule codes as a separate family from existing FQ0-FQ6:

| Rule | Severity | Condition | Message invariant |
|---|---|---|---|
| `ECQ0` | `info` | summary absent or status `not_run` | must include stable reason code; use `reason=not_requested` when summary is absent |
| `ECQ1` | `block` when EC policy `block`, otherwise `warn` | repository/pathway/reference materialization fail | must include stable pathway reason |
| `ECQ2` | `block` when EC policy `block`, otherwise `warn` | deterministic V2 hard-gate fail | must include blocking issue count |
| `ECQ3` | `warn` | deterministic V2 warn | must include warning issue count |
| `ECQ4` | `block` when semantic policy later says block, otherwise `warn` | semantic no-live companion fail/warn | not emitted in deterministic first slice |

Issue ID format:

```text
evidence-confirm:{fund_code}:{report_year}:{rule_code}:{reason}
```

Do not include timestamp or run id in ECQ issue ids in EC-P4. Repeated identical source-support outcomes should deduplicate by fund/year/rule/reason. A safe `source_provenance` display summary is optional future UI work and is not required in EC-P4; raw excerpts, PDF/cache paths, parser JSON and source adapter identity remain prohibited.

`run_quality_gate()` remains a pure score-file evaluator for FQ0-FQ6. Evidence Confirm issue merging belongs in `quality_gate_integration.run_quality_gate_for_bundle()` or a helper it calls after score-file gate output exists.

## Implementation Decisions

- Choose opt-in first. Default-on would turn every production analyze/checklist call into repository/PDF work and would make EC-P2 single-sample live proof look broader than it is.
- Keep deterministic V2/source pathway in Slice 1. Semantic no-live companion is additive after Service/quality-gate propagation is proven.
- Keep renderer non-rendering in EC-P4. Evidence Confirm status is audit metadata; putting it inside the investment report requires separate wording and UX review.
- Use `ECQ` instead of `FQ7`. FQ rules currently mean extraction/field-quality gates. Evidence Confirm is source-support/anchor-validation and should not be conflated with FQ coverage or correctness.
- Do not mutate `score.json`. Existing score generation remains Evidence-Confirm-unaware; merged `quality_gate.json/md` carries ECQ issues.
- Use fake runner tests for Service/UI. No live repository/PDF/network/provider commands are required to prove integration contracts.
- Accept duplicate repository load for the opt-in first slice: the Evidence Confirm runner loads through the Fund repository boundary even if extraction already loaded the same annual report. Passing an already-loaded `ParsedAnnualReport` is a future performance gate, not EC-P4 scope.

## Small Implementation Slices

### Slice 1 - Fund Summary + Quality Gate ECQ Projection

Objective: create a compact Evidence Confirm production summary and map it to quality-gate `ECQ*` issues without document access.

Allowed files/modules:

- `fund_agent/fund/evidence_confirm_production.py` (new) or `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `tests/fund/test_evidence_confirm_production.py` or `tests/fund/test_evidence_confirm_sources.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`

Exact changes:

- Add `EvidenceConfirmProductionSummary` and builder helpers:
  - `summary_from_repository_result(result, policy)`
  - `not_run_evidence_confirm_summary(fund_code, report_year, policy, reason)`
- Add `evidence_confirm_summary: EvidenceConfirmProductionSummary | None = None` optional parameter to `run_quality_gate_for_bundle()`.
- Add helper `_evidence_confirm_quality_gate_issues(summary)` in `quality_gate_integration.py`.
- Merge ECQ issues with existing `QualityGateResult` after `run_quality_gate()` returns:
  - re-aggregate `QualityGateResult.status` on the combined FQ + ECQ issue list using existing `_aggregate_gate_status()` semantics, or extract a public/internal helper with identical precedence if necessary.
  - output `quality_gate.json` and `quality_gate.md` must include ECQ issues.
- Do not change `score.json` or `write_extraction_score_records()`.

Call paths/data flow:

```text
EvidenceConfirmRepositoryRunResult
  -> summary_from_repository_result()
  -> run_quality_gate_for_bundle(..., evidence_confirm_summary=summary)
  -> run_quality_gate(score.json)
  -> merge ECQ issues into QualityGateResult
  -> write combined quality_gate.json/md
```

Error handling/invariants:

- Summary builder must not raise on failed repository result; it converts failure to `status="fail"`.
- Missing summary keeps Service result fields as `None`; when explicitly passed to the ECQ helper for quality-gate visibility, it emits `ECQ0/info` with `reason=not_requested`.
- ECQ issue creation never reads repository/documents/parser/provider.
- `ECQ2/block` only when policy is `block` and deterministic status is `fail`.
- Aggregate summary status precedence is `fail > warn > pass > not_run/not_applicable`; `pathway_status="fail"` always produces aggregate `status="fail"`.

Tests/validation:

- `test_summary_from_repository_fail_is_compact_and_no_excerpt`
- `test_quality_gate_integration_without_summary_is_unchanged`
- `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block`
- `test_quality_gate_integration_ecq2_block_changes_gate_status_to_block`
- `test_quality_gate_integration_maps_evidence_confirm_warn_to_ecq3_warn`
- `test_quality_gate_integration_maps_not_run_to_ecq0_info`
- `test_score_json_schema_remains_evidence_confirm_unaware`
- `test_quality_gate_integration_boundary_no_repository_or_source_imports`

Completion signal:

- Focused Fund tests pass.
- Existing quality-gate integration tests still pass.

Stop condition:

- Stop if adding ECQ requires changing `score.json` or `extraction_score.py`.

### Slice 2 - Service Deterministic Opt-In Propagation

Depends on: Slice 1.

Objective: wire deterministic repository-bounded Evidence Confirm into `FundAnalysisService.analyze()` through explicit developer override policy and fake-runner tests. `checklist` remains default off/no runner in this first slice.

Allowed files/modules:

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/services/test_execution_contract.py` only if it needs explicit contract assertion updates.

Exact changes:

- Add `evidence_confirm_policy` to `FundAnalysisDeveloperOverrides`, `ResolvedAnalyzeContract`, `_AnalysisCoreResult`, `FundAnalysisResult`, `FundChecklistResult` if shared result plumbing requires it.
- Add `EvidenceConfirmBlockedError` with a safe `EvidenceConfirmProductionSummary` field.
- Add Service constructor dependency injection for an async Evidence Confirm runner.
- In `_run_analysis_core()`:
  - resolve policy;
  - if off, do not call runner and keep result summary `None`;
  - if warn/block, call `project_chapter_facts(structured_data)`;
  - call `run_repository_bounded_evidence_confirm(EvidenceConfirmRepositoryRunRequest(...))` through injected runner;
  - convert to summary;
  - pass summary to `_run_quality_gate_if_enabled()`;
  - apply blocking rules.
- Preserve checklist as off/no runner: `FundAnalysisService.checklist()` may pass through the existing request shape, but first-slice CLI does not construct checklist developer overrides and tests must not require checklist EC execution.
- Update `_run_quality_gate_if_enabled()` signature to accept optional summary and forward it to `run_quality_gate_for_bundle()`.

Call paths/data flow:

```text
FundAnalysisService._run_analysis_core()
  -> FundDataExtractor.extract()
  -> project_chapter_facts(structured_data)
  -> injected Evidence Confirm runner
  -> EvidenceConfirmProductionSummary
  -> run_quality_gate_for_bundle(..., summary)
  -> P2 analysis/final judgment
```

Error handling/invariants:

- Runner exceptions must be converted to fail summary; if policy block then block, if warn then warn summary. Runner exception reason code must be `runner_exception:<class_name>`.
- Service must not import or instantiate `FundDocumentRepository`.
- Service must not inspect raw references/excerpts.
- Product mode with developer overrides must preserve existing validation error.
- Default product analyze/checklist must not call the runner.

Tests/validation:

- Default analyze policy off does not call fake runner and returns `evidence_confirm_summary is None`.
- Default checklist policy off does not call fake runner and returns `evidence_confirm_summary is None` if the field exists.
- Developer override `warn` calls fake runner and returns summary without blocking.
- Developer override `block` with fake fail raises `EvidenceConfirmBlockedError` when quality gate is off.
- `quality_gate_policy="warn"` plus EC policy `block` and EC fail raises `EvidenceConfirmBlockedError`.
- `quality_gate_policy="block"` plus EC fail produces `QualityGateBlockedError` when quality gate is configured and ECQ2 block is merged.
- Product mode with `developer_overrides.evidence_confirm_policy` keeps existing product-mode rejection.
- Boundary static test: `fund_agent/services/fund_analysis_service.py` contains no `FundDocumentRepository`, PDF cache helper, source adapter, Docling or pdfplumber imports.

Completion signal:

- Service tests pass with fake runner.
- Existing analyze/checklist default tests unchanged.

Stop condition:

- Stop if implementation requires live repository/PDF/network to test Service behavior.
- Stop if implementation needs a top-level product-mode `FundAnalysisRequest` field; that belongs to a later default-decision gate.
- Stop if checklist Evidence Confirm CLI support appears necessary; that belongs to a later explicit checklist EC slice/gate.

### Slice 3 - CLI/UI Summary and Exit Behavior

Objective: expose opt-in policy and Evidence Confirm summaries in CLI without moving evidence logic into UI.

Allowed files/modules:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Exact changes:

- Add `--evidence-confirm-policy off|warn|block` to `analyze`.
- Do not add checklist `--evidence-confirm-policy` in the first implementation pass. Checklist Evidence Confirm CLI support is a deferred residual, not a first-slice implementation option.
- Add `_echo_evidence_confirm_summary(result)` helper.
- Call it after `_echo_quality_gate_summary(result)` and before report body output.
- Add `_echo_evidence_confirm_blocked(error)` handler for `EvidenceConfirmBlockedError`; catch it after `QualityGateBlockedError`, exit with code `2` and no report body. Ordering is intentional because EC-only blocking is used only when the canonical quality-gate blocker is not carrying merged ECQ issues.
- Do not call any Fund Evidence Confirm function from CLI.

Call paths/data flow:

```text
CLI option
  -> FundAnalysisDeveloperOverrides.evidence_confirm_policy
  -> FundAnalysisService.analyze()
  -> result.evidence_confirm_summary
  -> stderr summary lines
```

Error handling/invariants:

- Summary output is safe and compact; no excerpts, file paths, PDF/cache/source internals.
- Exit code `2` aligns with existing quality/evidence gate blocking semantics.
- Default CLI output remains unchanged.

Tests/validation:

- Default `analyze` output contains no `evidence_confirm_` lines.
- `analyze --mode developer_override --evidence-confirm-policy warn` passes policy to fake Service and prints summary.
- `analyze --mode developer_override --evidence-confirm-policy block` with fake blocked service exits `2`, prints block summary, emits no report body.
- No checklist EC CLI tests in the first implementation pass; add a test or help assertion proving checklist has no `--evidence-confirm-policy` flag if the CLI test suite already covers command help.
- Static guard: `fund_agent/ui/cli.py` does not import repository, source helper, parser, provider client, Docling or Evidence Confirm runner internals.

Completion signal:

- CLI tests pass.
- User-visible option help is explicit that this is opt-in and not readiness proof.

Stop condition:

- Stop if CLI implementation would need to call Fund-layer Evidence Confirm directly.
- Stop if checklist CLI developer override support is required.

### Slice 4 - Renderer Non-Rendering Guard

Objective: prove EC-P4 deliberately keeps Evidence Confirm outside report Markdown.

Allowed files/modules:

- Prefer tests only: `tests/fund/template/test_renderer.py` or `tests/services/test_fund_analysis_service.py`
- `fund_agent/fund/template/renderer.py` only if review requires an explicit dataclass field for future extension; default plan is no production renderer change.

Exact changes:

- Do not append an Evidence Confirm section to report Markdown.
- Add test that a Service result with Evidence Confirm summary still returns the existing renderer report body unchanged.
- If renderer type is touched, add only an optional `evidence_confirm_summary` field that is not rendered, with docstring stating EC-P4 non-rendering.

Call paths/data flow:

```text
EvidenceConfirmProductionSummary
  -> Service result / CLI summary
  -> not TemplateRenderInput report body
```

Error handling/invariants:

- Programmatic audit input remains current report Markdown.
- Evidence Confirm status is not treated as investment conclusion, chapter content or evidence appendix item.

Tests/validation:

- Existing renderer tests pass.
- New assertion: no `Evidence Confirm` / `evidence_confirm_status` string appears in report Markdown when EC summary exists.

Completion signal:

- Non-rendering decision is covered by test or documented in implementation evidence.

Stop condition:

- Stop if product owner requires a report section; that is a separate renderer wording gate.

### Slice 5 - No-Live Semantic Companion Propagation

Objective: add an optional typed slot for already-produced no-live semantic results without constructing provider clients.

Allowed files/modules:

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/fund_analysis_service.py` only for result-field propagation if Slice 2 summary type reserved semantic fields.
- `tests/fund/test_evidence_confirm_semantic.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/services/test_fund_analysis_service.py`

Exact changes:

- Accept an optional `EvidenceSemanticResult` only from injected test/future caller path; do not construct clients.
- Map semantic fail/warn to `ECQ4` only when semantic result is present.
- Keep semantic summary `not_run` in all default deterministic paths.

Call paths/data flow:

```text
EvidenceSemanticResult (injected/no-live only)
  -> EvidenceConfirmProductionSummary.semantic_status
  -> ECQ4 issue projection
```

Error handling/invariants:

- No Service/provider config parsing.
- No provider-backed semantic default.
- Deterministic V2 failure remains blocking even if semantic result says entailed.

Tests/validation:

- Injected semantic contradicted result maps to `ECQ4/block` under semantic block policy or `ECQ4/warn` under warn policy.
- Missing semantic result remains `semantic_status="not_run"`.
- Static guard: no provider/LLM client construction.

Completion signal:

- No-live semantic propagation works only with injected results.

Stop condition:

- Stop if implementation needs OpenAI/provider config, network, LLM calls or semantic prompt design.

### Slice 6 - Docs Sync and Control Evidence

Objective: sync documentation after source behavior changes without claiming readiness.

Allowed files/modules:

- `README.md` if CLI usage changes.
- `fund_agent/README.md` if Service/UI/Fund boundary wording changes.
- `fund_agent/fund/README.md` if Fund Evidence Confirm summary/quality-gate integration is added.
- `tests/README.md` if new test conventions/commands are added.
- `docs/design.md` only after implementation is accepted, with current/future/candidate labels.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` only through controller sync, not by implementation worker unless explicitly assigned.
- implementation evidence artifact under `docs/reviews/`.

Exact changes:

- Document opt-in CLI flag and summary semantics.
- Document `ECQ*` issue family.
- Document renderer non-rendering decision.
- Preserve `NOT_READY`.

Tests/validation:

- `rg` checks that docs do not say default-on, ready, release-ready or provider-backed semantic.
- `git diff --check` over changed docs/source/tests.

Completion signal:

- Docs match implemented behavior and do not overclaim.

Stop condition:

- Stop if docs need to state readiness or PR disposition; that belongs to later readiness/external-state gates.

## Tests / Validation Commands and Expected Assertions

No live/PDF/network/provider/LLM commands are part of EC-P4 no-live validation.

Recommended implementation validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_production.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
uv run ruff check fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py README.md fund_agent/README.md fund_agent/fund/README.md tests/README.md
```

Expected assertions:

- Product/default analyze and checklist do not call Evidence Confirm; checklist has no first-slice Evidence Confirm CLI opt-in.
- Opt-in warn returns summary and does not block.
- Opt-in block blocks deterministic V2 fail.
- `quality_gate_policy=block` plus ECQ block produces no report body and exit code `2`.
- EC not-run/off is visible as not readiness proof and does not become pass.
- CLI/UI imports no repository/PDF/source/parser/provider internals.
- `score.json` remains Evidence-Confirm-unaware.
- Renderer report Markdown remains unchanged and contains no Evidence Confirm section.
- Semantic no-live propagation uses injected result/client only; no provider-backed semantic client exists.

Plan-gate validation already required:

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md
```

Expected assertion: no whitespace errors in the single plan artifact.

## Docs Decision

This plan gate writes only this artifact.

Later implementation must update docs only after code behavior changes:

- root `README.md`: CLI flag and user-visible summary if CLI changes.
- `fund_agent/README.md`: boundary note if Service/Fund integration wording changes.
- `fund_agent/fund/README.md`: `EvidenceConfirmProductionSummary` and `ECQ*` summary semantics.
- `tests/README.md`: new focused validation commands if added.
- `docs/design.md`: only after implementation is accepted, marking EC-P4 as current implemented behavior and preserving future/default/readiness boundaries.
- `docs/implementation-control.md` / `docs/current-startup-packet.md`: controller sync only.

## Risks / Open Questions / Residual Owners

| Risk or residual | Owner | Disposition |
|---|---|---|
| Default-on policy could trigger repository/PDF work and block rate without enough sample evidence | Product/controller | Deferred to default-decision gate |
| EC-P2 single live sample does not prove general source/PDF correctness | Release/evidence owner | Deferred to readiness matrix gate |
| Semantic provider quality is unproven | Semantic owner | Future provider-backed semantic gate |
| Renderer section wording could confuse audit metadata with investment conclusion | Renderer/product owner | Deferred renderer wording gate; EC-P4 non-rendering |
| `ECQ*` taxonomy may need future calibration | Quality gate owner | Start additive and provisional; review after implementation evidence |
| Checklist Evidence Confirm CLI support is deferred | Service/UI owner + controller | Assigned to later explicit checklist EC slice/gate; first slice is analyze-only |
| Duplicated repository load may be inefficient under opt-in EC | Fund documents owner | Accept for opt-in first slice; runner loads through repository even if extraction already loaded the report; passing already-loaded reports is future performance gate |
| Existing untracked workspace residue | Artifact owners/controller | Out of scope; do not clean in EC-P4 |

Blocking open questions: none for implementation planning. All five controller plan-gate questions are decided above.

## Completion Report Format

Implementation worker should report:

- changed files;
- implemented slices;
- exact policy/default behavior;
- validation commands and results;
- Evidence Confirm status/blocking semantics;
- docs updated or deferred;
- residual risks and owners;
- verdict: `EC_P4_IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY` or `BLOCKED`.

Plan-gate final report should report only:

- artifact path;
- verdict;
- diff-check result;
- blockers.

## Why This Is Not Overdesigned

The plan adds only the minimum contracts needed to make accepted Fund-layer Evidence Confirm usable by production-facing paths:

- one compact summary type instead of exposing raw V2/repository internals to Service/UI;
- one explicit opt-in policy instead of default-on product behavior;
- one issue family `ECQ*` instead of overloading FQ field-quality rules;
- CLI summary outside Markdown instead of a new report section;
- fake-runner no-live tests instead of live/PDF/provider validation in an integration gate;
- semantic propagation deferred to an injected no-live slice rather than provider construction.

The boundaries match the failure modes: repository/source proof stays Fund-owned, Service owns user policy, quality gate owns issue projection, UI owns display, and release/readiness remains a later evidence-chain decision.
