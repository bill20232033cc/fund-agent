# MVP typed template contract implementation planning plan

## Worker Self-Check

- Role: planning worker only, not controller and not implementation worker.
- Gate: `MVP typed template contract implementation planning gate`.
- Classification: `heavy`.
- Scope: plan artifact only.
- Output path: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/fund-analysis-template-draft.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-controller-judgment-20260602.md`, `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-controller-judgment-20260603.md`, and `docs/reviews/mvp-multi-year-annual-evidence-scope-controller-judgment-20260603.md`.
- Requested optional files `docs/reviews/mvp-fund-report-template-typed-contract-redesign-plan-controller-judgment-20260602.md` and `docs/reviews/mvp-fund-report-template-typed-contract-redesign-plan-20260602.md` were not present; the accepted files in this repo use `...-redesign-design-20260602.md` and `...-redesign-controller-judgment-20260602.md`.
- Actions intentionally not taken: no source code edit, no tests edit, no `docs/design.md` / `docs/implementation-control.md` / `docs/current-startup-packet.md` / `docs/fund-analysis-template-draft.md` edit, no `contracts.py` / auditor / provider / runtime / score / golden / readiness change, no live provider run, no commit, no push, no PR.
- Truth status: this is a code-generation-ready future implementation plan for review. It does not authorize implementation and does not make typed contracts current runtime fact.

## Objective

Map the accepted future typed template/audit/evidence design into conservative implementation slices that can be handed to future implementation workers after plan review and controller judgment.

The implementation sequence must cover:

- typed `ChapterContract`;
- derived `EvidenceAvailability`;
- evidence-conditional `must_not_cover`;
- `RequiredOutputItem.when_evidence_missing`;
- Ch0 consuming Ch7 with fail-closed required-body readiness;
- Ch2 internal typed subcontracts without changing public chapter ids;
- per-chapter `audit_focus` as bounded semantic audit emphasis only.

The plan preserves current public chapter ids `0-7`, current deterministic `analyze/checklist` defaults, current `--use-llm` fail-closed behavior, current no deterministic fallback for incomplete LLM results, and production annual-report access through `FundDocumentRepository` only.

## Accepted Design Requirements

| Requirement | Accepted boundary for implementation planning |
|---|---|
| typed `ChapterContract` | Future Fund-layer contract surface; current ids remain `0-7`; no `0+9`, `0+10`, or public Ch2 split. |
| `EvidenceAvailability` | Derived supplemental availability view over same-source `ChapterFactProjection`; not a replacement unless later accepted. |
| evidence-conditional `must_not_cover` | Programmatic-first; applies via typed evidence predicates and allowed contexts; polarity/quasi-positive feasibility is a prerequisite before full rollout. |
| `RequiredOutputItem.when_evidence_missing` | The accepted missing/degrade mechanism; clause-level fallback remains deferred. |
| Ch0 consumes Ch7 | Ch0 must render Ch7 final-judgment bundle and must not independently derive action; body readiness remains fail-closed. |
| Ch2 internal subcontracts | Performance / attribution / cost can be internal typed units inside `ChapterContract(chapter_id=2)` only. |
| per-chapter `audit_focus` | Only bounded semantic audit emphasis and repair hint grouping; never disables programmatic blockers. |

## Target Architecture Boundary

| Layer | Future responsibility in this implementation family | Explicit boundary |
|---|---|---|
| Fund | Owns typed template contract schema, contract manifest/projection, `EvidenceAvailability`, Ch2 internal subcontracts, evidence-conditional programmatic audit semantics, required-output missing/degrade semantics, writer/auditor domain inputs, and repair semantics. | Fund tools must not read Service/Host, provider config, CLI flags, raw filesystem documents, PDF cache, source helpers, or dayu runtime. Production annual reports still enter through `FundDocumentRepository` before projection. |
| Service | Owns use-case orchestration, `ExecutionContract`, provider construction for current first MVP, runtime ceilings, current `ChapterOrchestrator` facade until a later Agent implementation gate migrates execution mechanics, and final product fail-closed mapping. | Service may consume typed Fund outputs and pass explicit typed request fields. It must not implement Fund audit rules, parse fund template internals ad hoc, or put business parameters in `extra_payload`. |
| Host | Owns lifecycle only: run deadline, cancel token, terminal state, safe events and diagnostics. | Host must not inspect chapter ids semantically, `ChapterContract`, evidence availability, fund code/year business fields, provider clients, or tool loop details. |
| Agent | Future owner of runner/tool-loop/ToolRegistry/ToolTrace/task graph/repair budget/final assembly readiness after a separate implementation gate. | This planning gate must not implement Agent runtime. Typed contract work should be Fund-compatible with future Agent tools but may remain consumed by current Service facade until migration is accepted. |
| Config | Owns typed config only where explicit runtime/env configuration already belongs. | This implementation family should not add provider defaults, runtime budget defaults, prompt manifest config, source strategy config, or free-form payload bags. |

## Candidate Files For Future Implementation

Likely changed or added files in future implementation gates:

| Area | Candidate files |
|---|---|
| Typed contract schema / manifest | `fund_agent/fund/template/typed_contracts.py` or `fund_agent/fund/template/contracts_v2.py`; `fund_agent/fund/template/__init__.py`; possibly additive tests in `tests/fund/template/test_typed_contracts.py`. |
| Current manifest adapter | `fund_agent/fund/template/contracts.py` only if adding a read-only adapter/export; avoid rewriting current `_CHAPTERS` in the first slice. |
| Evidence availability | `fund_agent/fund/evidence_availability.py`; `fund_agent/fund/chapter_facts.py` only for explicit derived-input plumbing; tests in `tests/fund/test_evidence_availability.py` or `tests/fund/test_chapter_facts.py`. |
| Writer input / prompt fragments | `fund_agent/fund/chapter_writer.py`; tests in `tests/fund/test_chapter_writer.py`. |
| Programmatic audit | `fund_agent/fund/chapter_auditor.py`; `fund_agent/fund/audit/contract_rules.py`; possibly `fund_agent/fund/audit/audit_programmatic.py`; tests in `tests/fund/test_chapter_auditor.py` and `tests/fund/audit/test_audit_programmatic.py`. |
| Service orchestration and final assembly | `fund_agent/services/chapter_orchestrator.py`; `fund_agent/services/final_chapter_assembler.py`; `fund_agent/services/fund_analysis_service.py`; tests in `tests/services/test_chapter_orchestrator.py`, `tests/services/test_final_chapter_assembler.py`, and `tests/services/test_fund_analysis_service_llm.py`. |
| Artifact diagnostics | `fund_agent/services/llm_run_artifacts.py` only if new typed contract ids / availability summaries must be serialized safely; tests in `tests/services/test_llm_run_artifacts.py`. |
| Documentation after implementation acceptance | `fund_agent/fund/README.md`, `fund_agent/README.md`, `tests/README.md`; `docs/design.md` and control docs only in later controller truth-sync gates. |

Explicitly out of scope for this implementation family unless a later gate separately authorizes them:

- `docs/fund-analysis-template-draft.md` replacement or structural rewrite.
- Public chapter ids beyond `0-7`, `0+9`, `0+10`, independent Ch2 public subchapter ids, or separate chapter-matrix rows for Ch2 subcontracts.
- Provider runtime budget/default/endpoint changes, PASS-only live probe, split-audit live probe, or provider SDK changes.
- Deterministic `fund-analysis analyze/checklist` defaults.
- Incomplete LLM fallback to deterministic report or stdout partial report.
- Score-loop, golden/readiness/promotion, snapshot refresh, quality gate semantic changes, final judgment taxonomy change.
- Agent runner/tool-loop/ToolRegistry/ToolTrace implementation.
- Multi-year annual evidence runtime implementation.
- Direct repository/cache/PDF/source-helper access from Service/UI/Host/renderer/quality gate.
- Business parameter transport through `extra_payload`, `**kwargs`, or untyped dict payload bags.

## Implementation Slices

These slices are proposed future gates. Each slice should have implementation evidence, DS/MiMo review, and controller judgment before the next slice changes behavior.

### Slice 0: Preconditions And Fixture Calibration

Purpose: make the high-risk matching semantics explicit before changing programmatic blockers.

Implementation work:

- Add or update a planning/evidence artifact, not runtime code, that defines Chinese assertion polarity/quasi-positive fixture cases for Ch3-style `言行一致` / `风格稳定` wording.
- Define allowed-context fixture categories: required label only, explicit evidence-gap statement, bounded quote, anchor caption, positive assertion, quasi-positive assertion, unsupported causal assertion.
- Define item-level `block` criteria for `RequiredOutputItem.when_evidence_missing`.
- Confirm the first implementation slice will preserve public chapter ids `0-7`.

Acceptance criteria:

- Controller accepts fixture taxonomy before polarity-bearing `MustNotCoverClause` implementation.
- No runtime code, provider, config, auditor, or template truth changes in this precondition slice.
- Artifact states that brittle global Chinese stopword matching is not accepted.

Tests expected in later implementation slices:

- Required label containing `言行一致` does not block when it is only a label.
- Explicit insufficiency statement does not block.
- Positive and quasi-positive consistency claims block when required evidence is missing/unreviewed.
- Positive claim may pass only when reviewed evidence satisfies the predicate and all other audit rules pass.

### Slice 1: Add Typed Contract Schema As Additive Fund-Layer Sidecar

Purpose: introduce typed `ChapterContract` without replacing current `contracts.py` truth or current runtime behavior.

Implementation work:

- Add additive schema module such as `fund_agent/fund/template/typed_contracts.py`.
- Define stable schema/version literals, for example `typed_chapter_contract.v1`.
- Define typed objects: `TypedChapterContract`, `MustAnswerClause`, `MustNotCoverClause`, `EvidencePredicate`, `RequiredOutputItem`, `MissingEvidenceBehavior`, `TemplateLensRule`, `ChapterInternalSubcontract`, and `AuditFocusLiteral`.
- Provide loader/projection function that derives or manually maps current 8 chapters into typed contracts while preserving ids `0-7`.
- Include Ch2 internal typed subcontracts inside `chapter_id=2` only: `performance`, `attribution`, `cost`.
- Include Ch0 `consumes_chapter_conclusions=(7,)`.
- Include per-chapter `audit_focus` as data only; no programmatic rule selection.
- Add fail-closed validation: exact chapter ids `0-7`, no duplicates, no unknown dependency ids, Ch2 subcontracts cannot have public chapter ids, Ch0 must consume Ch7, required output item ids are unique, clause ids are stable, and `audit_focus` values are from a closed set.

Acceptance criteria:

- Existing `load_template_contract_manifest()` and current deterministic renderer/auditor behavior are unchanged.
- Typed loader validates all 8 chapters and returns no public ids outside `0-7`.
- Ch2 internal subcontracts are visible only under Ch2 typed contract and never as top-level manifest chapters.
- Ch0 typed contract declares Ch7 dependency and forbids independent action derivation.
- `audit_focus` is present but explicitly documented as semantic-only.
- No provider/runtime/default/score/golden/readiness changes.

Tests:

- `tests/fund/template/test_typed_contracts.py::test_typed_manifest_preserves_public_chapter_ids_0_to_7`
- `test_typed_manifest_rejects_ch2_public_subchapter_ids`
- `test_ch0_consumes_ch7_and_has_no_independent_action_source`
- `test_required_output_item_ids_are_unique`
- `test_audit_focus_literals_are_closed_and_do_not_imply_programmatic_disable`
- `test_typed_contract_loader_does_not_mutate_current_manifest`

Validation commands:

```bash
pytest tests/fund/template/test_typed_contracts.py
pytest tests/fund/template/test_contracts.py
```

### Slice 2: Derive EvidenceAvailability From ChapterFactProjection

Purpose: provide a machine-readable availability view from the same facts and anchors already used by the writer/auditor.

Implementation work:

- Add `fund_agent/fund/evidence_availability.py` or equivalent Fund-layer module.
- Define `EvidenceAvailability`, `RequirementAvailability`, `AvailabilityStatus`, `EvidenceRequirementId`, and safe gap references.
- Derive availability only from `ChapterFactProjection` / `ChapterFactInput` facts, anchors, missing reasons, `ReportDataGap`-like structures already present, and typed contract requirement ids.
- Represent `available`, `missing`, `unavailable`, `not_applicable`, and `unreviewed` distinctly.
- Support requirement-sensitive availability; coarse `1Y` / `3Y` / `5Y` or Ch2 horizon summaries must be derived from requirement availability, not independent truth.
- Add Ch3 requirements for manager strategy text, turnover, holdings snapshot, cross-period style evidence, and manager alignment.
- Add Ch2 requirement ids for internal performance / attribution / cost subcontracts without public chapter split.
- Keep multi-year runtime out of scope; if prior-year data is absent in current single-year projection, represent it as missing/unreviewed rather than loading documents.

Acceptance criteria:

- Availability derivation is pure and same-source: no repository, PDF/cache/source helper, Service, Host, provider, retained report, or filesystem reads.
- Missing vs not applicable vs unreviewed are testable and not collapsed into generic `missing`.
- Malformed typed contract requirement ids fail closed.
- `EvidenceAvailability` does not replace `ChapterFactProjection`.
- Optional future annual evidence fields are not implemented as runtime loading.

Tests:

- `tests/fund/test_evidence_availability.py::test_derives_available_requirements_from_fact_ids_and_anchor_ids`
- `test_distinguishes_missing_unavailable_not_applicable_unreviewed`
- `test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent`
- `test_ch2_subcontract_availability_stays_under_public_chapter_2`
- `test_derivation_does_not_call_document_repository`
- `test_unknown_requirement_id_fails_closed`

Validation commands:

```bash
pytest tests/fund/test_evidence_availability.py tests/fund/test_chapter_facts.py
```

### Slice 3: RequiredOutputItem.when_evidence_missing In Writer Inputs

Purpose: make missing/degrade behavior explicit before audit enforcement.

Implementation work:

- Extend `ChapterWriterInput` or add a typed adapter so writer receives typed required output items plus availability state.
- Preserve existing marker policy and allowed missing reasons; map them to typed `when_evidence_missing` behavior.
- Implement writer prompt fragment generation from typed required-output items only after typed contracts and availability are present.
- Behaviors to support: `render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, and `block`.
- `block` must stop the chapter fail-closed before unsupported writing if the item has no safe degrade path.
- Do not change current production defaults until the future gate explicitly wires the typed path.

Acceptance criteria:

- Missing evidence may satisfy a required output only through an approved degrade/gap output.
- Silent deletion is rejected unless `delete_if_not_applicable` has a typed reason.
- `block` produces a typed failure, not a deterministic fallback.
- Existing current writer tests still pass.
- No prompt/provider budget/default change.

Tests:

- `tests/fund/test_chapter_writer.py::test_required_output_missing_evidence_renders_gap_marker`
- `test_required_output_delete_if_not_applicable_requires_typed_reason`
- `test_required_output_block_stops_before_provider_success_path`
- `test_writer_prompt_contains_typed_required_output_ids_not_freeform_fallbacks`
- `test_existing_missing_marker_contract_remains_strict`

Validation commands:

```bash
pytest tests/fund/test_chapter_writer.py
```

### Slice 4: Evidence-Conditional must_not_cover Programmatic Audit

Purpose: fix the contract-shape class where a required label or evidence-gap statement is confused with a forbidden positive assertion, while preserving fail-closed semantics.

Implementation work:

- Extend programmatic audit to consume typed `MustNotCoverClause`, `EvidenceAvailability`, and allowed contexts.
- Implement `applies_when` predicates from availability state.
- Implement allowed-context matching for required label, explicit evidence-gap statement, quote, and anchor caption according to Slice 0 calibration.
- Implement Ch3 first as the acceptance target: if turnover / holdings / cross-period style evidence is missing or unreviewed, positive or quasi-positive `言行一致` / `风格稳定` claims block; labels and explicit insufficiency statements do not.
- Emit stable issue ids tied to `clause_id`, not only phrase hashes.
- Keep current programmatic blockers always-on; `audit_focus` does not disable C2, L1, marker, anchor, item-rule, forbidden advice, or missing/degrade checks.

Acceptance criteria:

- Existing C2 forbidden content tests continue to pass.
- Evidence-disabled clauses do not run; evidence-enabled clauses run programmatically regardless of `audit_focus`.
- Required label and explicit evidence-gap statement are allowed only in their narrow contexts.
- Quasi-positive soft wording such as `基本一致`, `未见明显不一致`, `倾向一致` blocks under missing/unreviewed evidence unless calibration accepts a safer exception.
- Programmatic audit remains authoritative over bounded semantic audit.

Tests:

- `tests/fund/test_chapter_auditor.py::test_ch3_required_label_allowed_under_missing_evidence`
- `test_ch3_explicit_evidence_gap_statement_allowed`
- `test_ch3_positive_consistency_claim_blocks_when_actual_behavior_unreviewed`
- `test_ch3_quasi_positive_consistency_claim_blocks_when_style_evidence_missing`
- `test_audit_focus_cannot_disable_programmatic_must_not_cover`
- `tests/fund/audit/test_audit_programmatic.py::test_typed_must_not_cover_issue_id_uses_clause_id`

Validation commands:

```bash
pytest tests/fund/test_chapter_auditor.py tests/fund/audit/test_audit_programmatic.py
```

### Slice 5: Per-Chapter audit_focus As Bounded Semantic Audit Input

Purpose: reduce semantic audit ambiguity without changing programmatic severity or rule selection.

Implementation work:

- Add typed per-chapter `audit_focus` projection from `TypedChapterContract`.
- Pass per-chapter focus into `ChapterAuditLLMRequest` or future bounded semantic audit adapter.
- Keep `DEFAULT_AUDIT_FOCUS` compatibility for current path until typed path is accepted.
- Ensure focus affects only LLM semantic prompt wording and repair hint grouping.
- Do not use `audit_focus` to skip programmatic audit or change blocking severity.

Acceptance criteria:

- Programmatic audit produces identical blockers with full, reduced, or unrelated `audit_focus`.
- LLM audit request receives only closed-set focus values.
- Safe diagnostics/artifacts may include focus ids but no raw prompt/provider response.
- No provider timeout/budget changes are introduced.

Tests:

- `tests/fund/test_chapter_auditor.py::test_per_chapter_audit_focus_is_passed_to_llm_request`
- `test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary`
- `tests/services/test_llm_run_artifacts.py::test_artifact_serializes_audit_focus_ids_only_if_added`

Validation commands:

```bash
pytest tests/fund/test_chapter_auditor.py tests/services/test_llm_run_artifacts.py
```

### Slice 6: Ch0 Consumes Ch7 With Fail-Closed Required-Body Readiness

Purpose: make final assembly dependency explicit and prevent Ch0 from independently deriving or strengthening final action.

Implementation work:

- Extend `FinalChapterAssembler` readiness inputs or add a typed readiness adapter to consume body chapter acceptance, Ch7 final-judgment bundle, and Ch0 dependency.
- Required body chapters remain public ids `1-6` unless a later gate changes required chapter policy.
- Ch7 bundle contains action, primary reason, largest risk, minimum verification question, threshold, and evidence/readiness status.
- Ch0 renders from Ch7 bundle and accepted body conclusions only; it must not introduce new action, new facts, new anchors, or stronger conclusion.
- Incomplete body chapters, missing Ch7, missing accepted conclusion, or readiness mismatch produce incomplete final assembly and empty stdout in current `--use-llm` path.

Acceptance criteria:

- Ch0 action equals Ch7 action exactly.
- Ch0 cannot be assembled as complete when Ch7 is missing/unaccepted.
- Ch7 cannot be produced as accepted when required body readiness is incomplete, unless an explicit future policy says a chapter is optional.
- Existing incomplete LLM behavior remains fail-closed with no deterministic fallback.
- Deterministic default `analyze/checklist` behavior remains unchanged.

Tests:

- `tests/services/test_final_chapter_assembler.py::test_ch0_action_must_equal_ch7_action`
- `test_missing_required_body_chapter_blocks_ch7_and_ch0`
- `test_missing_ch7_blocks_ch0_complete_report`
- `tests/services/test_fund_analysis_service_llm.py::test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`
- `tests/ui/test_cli.py::test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one`

Validation commands:

```bash
pytest tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

### Slice 7: Service Facade Wiring Behind Explicit Typed Path

Purpose: wire typed contract/availability/audit behavior into the current Service-owned LLM facade without changing default deterministic behavior or entering Agent runtime implementation.

Implementation work:

- Add explicit typed path selection in `FundLLMExecutionRequest` or Service internals only after previous slices are accepted.
- Keep explicit typed fields; no `extra_payload`.
- Current `ChapterOrchestrator` may consume typed contract inputs as a transition facade, but implementation evidence must state this remains Service-owned until Agent migration.
- Keep provider construction, runtime ceilings, and clients Service-owned for current first MVP.
- Preserve independent body chapter execution; one body chapter failure must not skip unrelated body chapters.

Acceptance criteria:

- `fund-analysis analyze` default does not read LLM config or typed LLM provider config.
- `fund-analysis checklist` remains deterministic and does not accept typed LLM behavior.
- `fund-analysis analyze --use-llm` remains opt-in and fail-closed.
- Incomplete typed results produce diagnostics/artifacts only under existing safe policies; no stdout partial report.
- No Host business-field exposure.

Tests:

- `tests/services/test_execution_contract.py::test_typed_template_flags_are_explicit_fields_if_added`
- `test_no_extra_payload_or_free_business_payload_bag`
- `tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution`
- `tests/ui/test_cli.py::test_default_analyze_unchanged_with_typed_contract_modules_present`

Validation commands:

```bash
pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py
```

### Slice 8: Documentation And Control Sync After Accepted Implementation

Purpose: update user/developer documentation only after code behavior is accepted.

Implementation work:

- Update `fund_agent/fund/README.md` to document current typed template contract implementation, `EvidenceAvailability`, required-output missing semantics, and programmatic-first audit boundaries.
- Update `fund_agent/README.md` only if Service/Fund boundary wording changes.
- Update `tests/README.md` for new test files and conventions.
- Update `docs/design.md`, `docs/current-startup-packet.md`, and `docs/implementation-control.md` only in controller truth-sync gates, not by implementation worker unless explicitly authorized.
- Do not update `docs/fund-analysis-template-draft.md` in this gate family unless a separate template truth replacement gate authorizes it.

Acceptance criteria:

- README text describes current implementation only after acceptance.
- Docs do not claim Agent runtime, multi-year runtime, provider budget/default changes, score-loop, or Ch2 public split are implemented.
- Old and new terms are not mixed in a way that suggests duplicate truth sources.

Tests / validation:

```bash
pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
git diff --check -- fund_agent/fund/README.md fund_agent/README.md tests/README.md
```

## Migration And Compatibility Plan

- Use additive typed modules first. Do not replace `docs/fund-analysis-template-draft.md` or current `contracts.py` as the source used by deterministic rendering until a later controller gate accepts that migration.
- Keep a one-way adapter from current 8-chapter manifest to typed contracts for the MVP implementation. The adapter must fail closed if a current natural-language item has no typed id.
- Preserve public chapter ids `0-7` in all user-visible report output, chapter blocks, chapter matrix rows, artifacts, and tests.
- Keep Ch2 performance/attribution/cost as internal typed subcontracts under public chapter id `2`.
- Preserve deterministic `fund-analysis analyze/checklist` output behavior unless a future gate explicitly changes deterministic rendering.
- Preserve `--use-llm` fail-closed semantics: incomplete result means exit code `1`, empty stdout, no deterministic fallback, and only safe diagnostics/artifacts.
- Do not migrate execution mechanics into Agent in this typed-template implementation family. The typed contracts should be shaped so a later Agent runner can consume them, but current execution remains Service facade until a separate Agent implementation gate.
- Treat `EvidenceAvailability` as supplemental and derived. Existing `ChapterFactProjection` remains canonical structured fact projection.
- Introduce strict validation before behavior wiring. A malformed typed contract must fail closed during construction/test, not silently downgrade to old free-text behavior.
- Any future controller-approved switch from current free-text contract to typed contract should be reversible at gate level by keeping current deterministic path untouched until accepted evidence says otherwise.

## Risk Matrix

| Risk | Impact | Likelihood | Mitigation | Owner |
|---|---:|---:|---|---|
| Typed contract becomes a second template truth competing with `docs/fund-analysis-template-draft.md` | High | Medium | Additive adapter, explicit schema ids, validation that every typed item maps to current chapter ids; no template replacement in this gate. | Fund |
| Ch2 internal subcontracts leak into public chapter ids or artifacts as new chapters | High | Medium | Validation rejects top-level ids outside `0-7`; tests assert Ch2 subcontracts stay under chapter `2`. | Fund / Service |
| `audit_focus` accidentally disables programmatic blockers | High | Medium | Programmatic audit independent of focus; tests run blockers with reduced focus. | Fund |
| Polarity/quasi-positive detection is brittle and either overblocks labels or underblocks unsafe claims | High | High | Slice 0 calibration first; allowed contexts narrow; stable fixture set before rollout. | Fund |
| `EvidenceAvailability` diverges from `ChapterFactProjection` | High | Medium | Pure derivation from same-source facts/anchors; no LLM inference; no repository calls. | Fund |
| Missing evidence degrade semantics become loopholes for unsupported positive conclusions | High | Medium | `when_evidence_missing` has closed behaviors; programmatic audit checks positive/quasi-positive claims under missing predicates. | Fund |
| Ch0 repeats or strengthens final judgment independently from Ch7 | High | Medium | Ch0 consumes Ch7 bundle; equality and readiness tests. | Service |
| Future implementation unintentionally changes deterministic defaults | High | Low | Additive typed path, CLI regression tests, no default flag changes. | Service / UI |
| Incomplete LLM result falls back to deterministic | High | Low | Existing fail-closed tests plus typed readiness tests. | Service / UI |
| Provider-runtime timeout work is mixed into typed contract implementation | Medium | Medium | Non-goals and review checklist reject budget/default/endpoint changes. | Controller / Reviewers |
| Host receives business fields or provider clients | High | Low | ExecutionContract tests; Host boundary tests; no extra payload. | Service / Host |
| Documentation says future design is current fact before code acceptance | Medium | Medium | Docs only in Slice 8 after controller acceptance. | Controller / Docs worker |

## Non-Goals

- Do not implement code in this planning gate.
- Do not edit source code, tests, runtime docs, control docs, startup packet, design truth, template truth, or retained reports in this gate.
- Do not replace `docs/fund-analysis-template-draft.md`.
- Do not relax auditor rules, C2, L1, missing marker, anchor, forbidden advice, quality gate, or fail-closed semantics.
- Do not change deterministic `analyze/checklist` defaults.
- Do not let incomplete LLM result fall back to deterministic output.
- Do not enter provider runtime, PASS-only live probe, provider endpoint/default/budget tuning, score-loop, golden/readiness, Agent runtime implementation, or multi-year runtime implementation.
- Do not expose raw five-year PDF/parsed text to LLM prompts.
- Do not add `dayu-agent`, `dayu.host`, or `dayu.engine` as production runtime dependencies.
- Do not pass explicit business parameters through `extra_payload`.

## Verifier Matrix

Future implementation gates should map each accepted design requirement to direct same-source evidence like this:

| Accepted requirement | Direct evidence expected in future implementation gate |
|---|---|
| Public chapter ids remain `0-7` | Typed manifest validation tests; serialized chapter matrix fixture with only ids `0-7`; no Ch2 subchapter top-level rows. |
| Typed `ChapterContract` | New typed schema module with Chinese docstrings; loader tests; every chapter has stable clause/item ids; current manifest still loads unchanged. |
| `EvidenceAvailability` is derived | Unit tests with fake `ChapterFactProjection`; monkeypatch/fake proving no `FundDocumentRepository`, PDF/cache/source helper, Service, Host, or provider call. |
| Evidence-conditional `must_not_cover` | Ch3 tests for label/gap allowed contexts and positive/quasi-positive blockers; issue ids include `clause_id`; `audit_focus` omission does not suppress C2. |
| `RequiredOutputItem.when_evidence_missing` | Writer/auditor tests for gap rendering, minimum verification question, delete-if-not-applicable reason, and block behavior. |
| Ch0 consumes Ch7 | Final assembler tests proving Ch0 action equals Ch7 action and Ch0 cannot complete without accepted Ch7. |
| Required body readiness fail-closed | Service/final assembly tests where missing Ch2/Ch3/Ch4/Ch6 blocks full report, stdout remains empty for `--use-llm` incomplete. |
| Ch2 internal typed subcontracts | Contract tests proving `performance`, `attribution`, `cost` are internal units under chapter `2`; artifacts and matrices still show Ch2 only. |
| `audit_focus` bounded semantic only | Tests showing programmatic blockers fire independent of focus; LLM request includes closed-set focus values only. |
| Deterministic defaults unchanged | CLI tests for default `analyze` and `checklist`; no LLM env/provider construction on deterministic path. |
| No deterministic fallback | `--use-llm` incomplete tests: exit `1`, empty stdout, safe diagnostic/artifact only. |
| No provider/runtime/default change | Diff/evidence showing no edits to `fund_agent/config/llm.py`, provider defaults, timeout defaults, endpoint behavior, or live provider commands unless separately authorized. |
| Production annual report access boundary | EvidenceAvailability and typed contract tests use in-memory projections; no Service/UI/Host/renderer direct source/cache/PDF calls. |
| Explicit typed params only | Dataclass/Protocol field tests; no `extra_payload`, `**kwargs`, or free-form business dict added. |

## Reviewer Checklist For DS/MiMo

Reviewers should answer these as blocking or non-blocking findings:

- Does the plan preserve public chapter ids `0-7` everywhere, including artifacts and matrices?
- Does Ch2 remain a single public `chapter_id=2` with internal typed subcontracts only?
- Is `EvidenceAvailability` derived from same-source `ChapterFactProjection`, rather than inferred from LLM prose or loaded from documents directly?
- Are all explicit parameters represented as typed fields, with no `extra_payload` / `**kwargs` / business payload bag?
- Does any slice relax programmatic audit, fail-closed semantics, missing markers, anchor validation, L1, C2, or forbidden investment advice?
- Does `audit_focus` remain semantic-only and unable to disable programmatic blockers?
- Does the Ch3 must-not-cover plan distinguish required labels, evidence-gap statements, quotes/anchor captions, positive claims, and quasi-positive claims?
- Is Chinese polarity/quasi-positive calibration required before full polarity-bearing implementation?
- Does Ch0 consume Ch7 and fail closed when required body readiness is incomplete?
- Does the plan keep deterministic `analyze/checklist` defaults unchanged?
- Does the plan keep incomplete `--use-llm` from falling back to deterministic or emitting stdout partial reports?
- Does the plan avoid provider runtime/default/endpoint changes, PASS-only live probe, score-loop, golden/readiness, Agent runtime implementation, and multi-year runtime implementation?
- Are candidate files scoped to Fund/Service tests and docs that naturally own the behavior?
- Are future docs updates placed after implementation acceptance rather than before code truth exists?
- Are acceptance criteria specific enough that an implementation worker can generate code and tests without inventing architecture?

## Suggested Gate Sequence

1. Plan review gate for this artifact: DS + MiMo review, fix if needed, controller judgment.
2. Slice 0 calibration/precondition gate.
3. Slice 1 typed schema sidecar implementation gate.
4. Slice 2 EvidenceAvailability implementation gate.
5. Slice 3 required-output missing/degrade implementation gate.
6. Slice 4 Ch3-first evidence-conditional `must_not_cover` implementation gate.
7. Slice 5 per-chapter semantic `audit_focus` wiring gate.
8. Slice 6 Ch0/Ch7 typed readiness integration gate.
9. Slice 7 Service facade wiring gate only after Fund-layer semantics are accepted.
10. Slice 8 docs/control truth sync gate after accepted implementation.

## Validation For This Planning Artifact

Recommended command for this artifact:

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md
```

Secret-safety statement: this plan contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
