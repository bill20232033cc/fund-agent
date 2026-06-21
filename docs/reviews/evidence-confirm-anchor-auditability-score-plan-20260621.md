# Evidence Confirm / Anchor Auditability Score Plan - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- Branch: `evidence-confirm-anchor-audit-score`
- Classification: `standard`
- Verdict target: `PLAN_READY_FOR_REVIEW_NOT_READY`
- Release/readiness: `NOT_READY`

## Goal

Add a Fund-layer, no-live Evidence Confirm contract that can score whether a structured fact value is actually supported by the exact evidence anchor location supplied for that fact.

The first implementation slice must answer three questions deterministically:

1. E1: is the anchor precise enough to be auditable?
2. E2: does the fact value have same-source support in the text/table excerpt tied to that anchor?
3. E3: is a required fact or critical assertion missing any confirmable evidence?

## Motivation

Current extractor and Route C mechanics can prove that facts carry allowed anchor ids, and writer/auditor code can reject unknown anchors. That is not the same as proving that the field value and the cited evidence position are same-source.

Direct code evidence:

- `fund_agent/fund/chapter_facts.py` validates that `ChapterFactEntry.evidence_anchor_ids` refer to known `ChapterEvidenceAnchor` ids, but `ChapterEvidenceAnchor` has locator metadata only and no source excerpt text.
- `fund_agent/fund/chapter_auditor.py` checks unknown anchors and missing anchor markers as E1/E3-like programmatic issues, but its module docstring explicitly says E2 source-text verification is deferred to Evidence Confirm.
- `docs/design.md` says report-level `ProgrammaticAuditResult` currently runs only `P1/P2/P3/C2/L1/R1/R2`; `E1/E2/E3` remain later Evidence Confirm / semantic review targets and must not be described as already passing report-level programmatic audit.
- `report_evidence.py` already has `ReportEvidenceAnchor`, `ReportFact`, score dimensions including `evidence_traceability`, and `NextGateRecommendation="evidence_anchor"`, but no Evidence Confirm result type or same-source excerpt verifier.

## Success Signal

- A new Fund-layer module exposes deterministic typed contracts for Evidence Confirm without reading files, repository, PDF/cache/source helpers, Service, Host, provider, network, or external tools.
- Given a fact, its anchor ids, and explicit caller-supplied reference excerpts keyed by anchor id, the module emits stable per-fact results and aggregate score.
- Tests prove:
  - precise anchor + matching excerpt passes;
  - missing page/section/table/row precision is E1;
  - fact value absent from the same-anchor excerpt is E2;
  - fact with required/critical status but no anchor or no reference excerpt is E3;
  - derived facts are not forced through annual-report excerpt matching;
  - candidate-only or unproven references do not become source-truth evidence.
- Documentation states this is no-live Evidence Confirm phase 1, not golden/readiness, release, parser replacement, live PDF validation, or quality gate enforcement.

## Non-goals

- Do not read production PDFs, repository files, cache files, Docling JSON, EID HTML, provider output, or network.
- Do not call `FundDocumentRepository` or source helpers.
- Do not change extractor behavior, processor behavior, source policy, fallback behavior, or `EvidenceAnchor.source_kind`.
- Do not wire Evidence Confirm into default `fund-analysis analyze/checklist`, `quality_gate`, Service, UI, Host, renderer, score-loop, release/readiness, PR readiness, or final judgment.
- Do not claim real-report correctness or full field correctness.
- Do not implement multi-period LLM route or repair budget calibration.
- Do not implement durable Host/Agent runtime expansion, ToolRegistry, tool-loop, session resume, memory, or reply outbox.
- Do not promote candidate evidence, Docling, pdfplumber, or EID HTML render outputs into public source truth.

## Design Alignment

- Layer: Agent / Fund only. Evidence Confirm is domain evidence validation and belongs under `fund_agent/fund`.
- Current four-layer boundary remains `UI -> Service -> Host -> Agent`.
- Inputs must be explicit typed dataclasses. No explicit parameter may be hidden in `extra_payload`.
- The first slice is a no-live deterministic evidence contract. It consumes only already materialized `ChapterFactInput` / fact-like records and explicit same-source reference excerpts supplied by the caller.
- This work complements, but does not replace, `EvidenceAvailability`. Availability says whether a requirement has facts/anchors/gaps; Evidence Confirm scores whether the specific fact-anchor pair is confirmable.
- This work complements, but does not replace, `ChapterAudit`. Chapter audit checks draft behavior; Evidence Confirm checks fact-anchor support before or alongside writing/auditing.

## Proposed Module

Create `fund_agent/fund/evidence_confirm.py`.

### Public constants and aliases

- `EVIDENCE_CONFIRM_SCHEMA_VERSION = "evidence_confirm.v1"`
- `EvidenceConfirmRuleCode = Literal["E1", "E2", "E3"]`
- `EvidenceConfirmStatus = Literal["pass", "warn", "fail", "not_applicable"]`
- `EvidenceConfirmSeverity = Literal["blocking", "reviewable", "informational"]`
- `EvidenceConfirmReferenceKind = Literal["annual_report_excerpt", "reviewed_note", "derived_calculation"]`

### Public dataclasses

`EvidenceConfirmReference`

- `anchor_id: str`
- `reference_kind: EvidenceConfirmReferenceKind`
- `source_kind: str`
- `document_year: int | None`
- `section_id: str | None`
- `page_number: int | None`
- `table_id: str | None`
- `row_locator: str | None`
- `excerpt_text: str`
- `source_truth_status: Literal["proven", "not_proven"] = "proven"`
- `candidate_only: bool = False`

`EvidenceConfirmIssue`

- `issue_id: str`
- `rule_code: EvidenceConfirmRuleCode`
- `severity: EvidenceConfirmSeverity`
- `fact_id: str`
- `source_field_id: str`
- `anchor_id: str | None`
- `message: str`

`EvidenceConfirmFactResult`

- `fact_id: str`
- `source_field_id: str`
- `status: EvidenceConfirmStatus`
- `matched_anchor_ids: tuple[str, ...]`
- `issue_ids: tuple[str, ...]`
- `auditability_score: int | None`

`EvidenceConfirmResult`

- `schema_version: str`
- `fund_code: str`
- `report_year: int`
- `fact_results: tuple[EvidenceConfirmFactResult, ...]`
- `issues: tuple[EvidenceConfirmIssue, ...]`
- `checked_rules: tuple[EvidenceConfirmRuleCode, ...]`
- `overall_status: EvidenceConfirmStatus`
- `auditability_score: int | None`

### Public functions

`confirm_chapter_evidence(chapter: ChapterFactInput, references: tuple[EvidenceConfirmReference, ...]) -> EvidenceConfirmResult`

- Validates only one chapter.
- Does not mutate `ChapterFactInput`.
- Does not read external state.

`confirm_projection_evidence(projection: ChapterFactProjection, references: tuple[EvidenceConfirmReference, ...]) -> EvidenceConfirmResult`

- Aggregates per-chapter fact results.
- Stable ordering by `chapter_id`, `source_field_id`, `fact_id`.

## Confirmation Semantics

### E1 anchor precision

For `annual_report_excerpt` references:

- `section_id` must be present.
- At least one of `page_number`, `table_id`, or `row_locator` must be present.
- For table facts, `table_id` or `row_locator` should be present; if neither is present, emit E1 reviewable.

For `reviewed_note` references:

- `excerpt_text` and `section_id` or `row_locator` must be present.

For `derived_calculation` references:

- E1 is not applicable; derived support is judged by linked input anchors in later slices.

### E2 value/excerpt same-source support

- For scalar string/number/Decimal/bool facts, normalize CJK whitespace, ASCII case, punctuation variants, commas in numbers, and `%` spacing before matching.
- For dict/list facts, flatten scalar leaves into tokens. A match passes when at least one material scalar token appears in an excerpt tied to one of the fact's own anchor ids.
- Ignore generic schema/version/fund code/year keys when flattening dict values.
- For oversized or complex object values where no scalar material token can be derived, return E2 `not_applicable` unless the fact is marked required/critical and lacks any confirmable anchor, in which case E3 applies.
- Do not match against excerpts for anchors not referenced by that fact.
- Do not close E2 by value equality across different anchors or by unrelated facts in the same chapter.

### E3 missing evidence

Emit E3 when any of these is true:

- `fact.status == "available"` and `fact.evidence_anchor_ids == ()` for non-derived annual-report facts.
- `fact.missing_reason == "evidence_missing"`.
- A fact required by a template requirement has anchors, but none of those anchors has a supplied proven reference excerpt.

Do not emit E3 for:

- `not_applicable` facts;
- derived or synthetic facts without annual-report source;
- facts already modeled as safe gaps.

### Candidate and proof boundary

- A reference can satisfy E1/E2/E3 support only when all proof predicates pass:
  - `candidate_only is False`;
  - `source_truth_status == "proven"`;
  - `source_kind in {"annual_report", "reviewed_note", "derived"}`;
  - `reference_kind == "annual_report_excerpt"` pairs only with `source_kind == "annual_report"`;
  - `reference_kind == "reviewed_note"` pairs only with `source_kind == "reviewed_note"`;
  - `reference_kind == "derived_calculation"` pairs only with `source_kind == "derived"`.
- Any other reference is non-proof and cannot satisfy E2 or E3.
- The issue should state that candidate evidence remains non-proof.
- Do not expand `EvidenceSourceKind`.

## Auditability Score

Per fact:

- `100`: no E1/E2/E3 issue and at least one matched anchor.
- `70`: only reviewable E1 precision issue, but E2 value support matched.
- `40`: anchor exists but no same-source value match.
- `0`: missing required evidence, unproven candidate-only reference, or dangling/no reference for required fact.
- `None`: derived/not-applicable fact that is not scored.

Aggregate score:

- Average only facts where `auditability_score is not None`.
- `None` is allowed only when `status == "not_applicable"`.
- Aggregate `auditability_score` is `None` when there are no numeric fact scores.
- `overall_status`:
  - `fail` if any blocking E2/E3 exists.
  - `warn` if any reviewable E1/E2 exists.
  - `pass` if all numeric fact results pass.
  - `not_applicable` if there are no numeric fact results.

## Affected Files

Implementation slice:

- `fund_agent/fund/evidence_confirm.py`
- `tests/fund/test_evidence_confirm.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- implementation evidence artifact under `docs/reviews/`

Plan/review slice:

- `docs/reviews/evidence-confirm-anchor-auditability-score-plan-20260621.md`
- plan review artifact under `docs/reviews/`
- plan controller judgment artifact under `docs/reviews/`

No other files are authorized without a reviewed amendment.

## Slices

### Slice 1 - Contract and deterministic no-live scorer

Objective:

- Add `evidence_confirm.py` with typed dataclasses and deterministic scorer.

Allowed changes:

- New module only.
- No integration into Service, quality gate, CLI, Host, Agent runner, processors, extractors, repository, or source helpers.

Tests:

- Unit tests for E1/E2/E3 semantics with hand-built `ChapterFactInput`.

Completion signal:

- Focused `uv run pytest tests/fund/test_evidence_confirm.py -q` passes.

### Slice 2 - Boundary and regression coverage

Objective:

- Add tests proving candidate-only references, derived facts, and unrelated anchor excerpts cannot satisfy same-source confirmation.

Allowed changes:

- `tests/fund/test_evidence_confirm.py`
- Minimal bug fixes in `fund_agent/fund/evidence_confirm.py` only.

Tests:

- `uv run pytest tests/fund/test_evidence_confirm.py -q`
- `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py`

Completion signal:

- Negative tests fail before implementation if behavior is missing and pass after implementation.

### Slice 3 - Docs sync

Objective:

- Record current phase-1 facts without claiming quality gate, release, source truth, or real-report correctness.

Allowed changes:

- `fund_agent/fund/README.md`
- `docs/design.md`
- implementation evidence artifact.

Tests/validation:

- `rg -n "Evidence Confirm|E1|E2|E3|quality gate|NOT_READY" docs/design.md fund_agent/fund/README.md`
- `git diff --check`

Completion signal:

- Docs state Evidence Confirm phase 1 is no-live, explicit-reference, Fund-layer only.

## Validation Matrix

Required implementation validation:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py fund_agent/fund/README.md docs/design.md
git diff --check
```

Expected assertions:

- E1 is emitted for imprecise annual-report anchor references.
- E2 is emitted when the fact value does not appear in the same referenced excerpt.
- E3 is emitted for required/available annual-report facts with no confirmable anchor reference.
- Candidate-only / not_proven / candidate-source references never satisfy source support.
- Invalid `reference_kind` / `source_kind` pairs never satisfy source support.
- Derived/not-applicable facts are not forced through annual-report excerpt matching and use `auditability_score=None`.
- Existing chapter auditor and evidence availability tests remain unchanged.

## Review Requirements

- Plan review must challenge whether explicit reference excerpts are enough for phase 1 and whether the plan overclaims same-source proof.
- Code review must verify no external reads, no repository/source helper import, no Service/UI/Host integration, no `EvidenceSourceKind` expansion, and no readiness/golden/release claim.
- Deepreview must review the new module, tests, docs, and evidence artifact as one aggregate.

## Risks and Disposition

| Risk | Disposition |
|---|---|
| Phase 1 only proves same-source support against caller-supplied excerpts, not live PDF truth. | Accepted residual assigned to future repository-mediated Evidence Confirm gate. |
| Complex dict/list values may have weak token extraction. | Covered by fail-closed tests for required facts and documented as phase-1 limitation. |
| Candidate references may look precise but remain non-proof. | Must be explicit negative test and docs non-claim. |
| Wiring into quality gate too early would overclaim readiness. | Non-goal; no Service/quality gate changes in this work unit. |
| Repair budget and multi-period LLM route remain tempting follow-ups. | Deferred by user steering; not part of this work unit. |
| Host/Agent runtime expansion is architecture-heavy. | Deferred until extractor correctness / evidence confirmation surfaces are stable. |

## Why This Is Not Over-designed

The plan introduces one small Fund-layer module because current code already has facts, anchors, and chapter audit, but lacks the missing relationship: fact value to same-anchor source excerpt. It does not add a new runtime layer, storage system, provider call, repository adapter, parser, quality gate, or public product behavior. The explicit-reference input is the minimal testable contract needed before any live PDF or repository-mediated Evidence Confirm gate.

## Completion Report Format

Use Chinese and include:

- PR #38 ready-state result;
- current branch;
- plan/review/implementation artifact paths;
- changed files;
- validation commands and results;
- E1/E2/E3 behavior summary;
- residual risks and owners;
- verdict token.

## Current Verdict

`PLAN_READY_FOR_REVIEW_NOT_READY`
