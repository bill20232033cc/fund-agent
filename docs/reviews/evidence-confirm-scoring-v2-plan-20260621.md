# Evidence Confirm Scoring V2 Plan - 2026-06-21

## Gate

- Work unit: `Evidence Confirm Scoring V2 / Dayu-style Dimension Scoring`
- Current gate: `Evidence Confirm Scoring V2 Planning Gate`
- Branch: `evidence-confirm-anchor-audit-score`
- Classification: `heavy scoring-contract planning`
- Verdict target: `PLAN_READY_FOR_REVIEW_NOT_READY`
- Release/readiness: `NOT_READY`

## Goal

Design the next no-live Evidence Confirm scoring contract so implementation can separate:

1. hard gate semantics: whether Evidence Confirm is allowed to pass, warn, fail, or stay not applicable;
2. dimension scores: why a fact or chapter scored well or poorly;
3. aggregate auditability score: a deterministic score summary that is useful for later review workflows without replacing current FQ0-FQ6 quality gate.

This gate is planning only. It must produce an implementation-ready contract for the next implementation gate; it must not implement code or change runtime behavior.

## Motivation

Phase 1 accepted `fund_agent/fund/evidence_confirm.py` as a no-live helper. It can now validate caller-supplied references against `ChapterFactInput` / `ChapterFactProjection` and emit E1/E2/E3 issues plus a coarse `auditability_score`.

That is not yet enough for durable scoring because the current result shape collapses several different decisions into one score:

- source/support proof decision: candidate-only, not-proven or wrong source kind cannot support evidence;
- hard failure decision: missing support for an available required fact must fail closed;
- reviewability decision: imprecise locator can be warning-level while same-anchor value support still exists;
- score explanation: consumers need per-dimension reasons instead of interpreting raw 100/70/40/0.

The next contract must make those decisions explicit before any upper-layer adoption, quality-gate integration, live PDF/source retrieval or report workflow consumption is considered.

## Direct Code Evidence

- `fund_agent/fund/evidence_confirm.py` currently exposes `EvidenceConfirmReference`, `EvidenceConfirmIssue`, `EvidenceConfirmFactResult`, `EvidenceConfirmResult`, `confirm_chapter_evidence()` and `confirm_projection_evidence()` under `evidence_confirm.v1`.
- Current phase-1 result uses `overall_status` plus per-fact `auditability_score`, but there is no typed dimension-result object and no hard-gate summary object.
- Current phase-1 rules already distinguish E1 precision warning, E2 same-anchor value mismatch, and E3 missing/proof failure.
- `tests/fund/test_evidence_confirm.py` covers exact anchor pass, E1 warning, E2 fail, E3 fail, candidate-only / not-proven / unknown source fail-closed, derived / not-applicable behavior, projection aggregation and score averaging.
- `fund_agent/fund/report_evidence.py` already defines report-quality `ScoreDimension`, `ScoreRecordStatus`, `ScoreIssueSeverity` and `NextGateRecommendation`, including `evidence_traceability`, but it is report-quality artifact schema, not Evidence Confirm result schema.
- `docs/design.md` keeps Evidence Confirm phase 1 as a Fund-layer no-live helper and explicitly says full live source/PDF Evidence Confirm, report-level quality-gate consumption and dayu runtime are not implemented.

## Success Signal

The plan is successful when a later implementation worker can implement without inventing contract semantics:

- New V2 result dataclasses and literals are fully specified.
- Hard gate state, dimension status, dimension score and aggregate score semantics are separate.
- Existing V1 helper behavior can remain backward-compatible for phase-1 tests, or a named V2 function can coexist with V1.
- No implementation slice needs to decide whether to integrate with Service/UI/Host/renderer/quality_gate, live source/PDF, parser outputs, repository, PR readiness, release or golden promotion.
- Validation commands and expected assertions are concrete.

## Non-goals

- Do not read production PDFs, repository files, cache files, source helpers, Docling JSON, EID HTML, provider output or network.
- Do not call `FundDocumentRepository`.
- Do not change extractor, processor, source policy, fallback behavior, `EvidenceSourceKind`, public `EvidenceAnchor`, `StructuredFundDataBundle`, Service, UI, Host, renderer, quality gate, final judgment or CLI behavior.
- Do not mark PR #39 ready, merge it, push, create another PR, request reviewers, or change external GitHub state.
- Do not replace FQ0-FQ6 quality gate or current `extraction_score.py`.
- Do not promote candidate evidence, Docling, pdfplumber or EID HTML render outputs into source truth.
- Do not implement semantic entailment beyond current conservative material-token matching.
- Do not implement live source/PDF Evidence Confirm or reviewed-note / derived-calculation proof production.
- Do not update `docs/design.md`, `docs/implementation-control.md`, startup packet or README in this planning gate.

## Design Alignment

- Layer: Agent / Fund only. Evidence Confirm remains a Fund-domain evidence validation helper.
- Inputs: explicit typed dataclasses only; no explicit parameter may be hidden in `extra_payload`.
- Current four-layer boundary remains `UI -> Service -> Host -> Agent`.
- Current production default remains deterministic `fund-analysis analyze/checklist`; V2 no-live scoring is not production adoption.
- Current phase-1 closeout boundaries remain binding: no Service/UI/Host/renderer/quality-gate/readiness integration, no repository/PDF/cache/source helper/provider/network/dayu reads, no parser replacement and no schema expansion.
- Dayu is design input only. The implementation must internalize only the relevant hard-gate / dimension-score idea in this repo and must not import or depend on external `dayu-agent` runtime.

## Proposed V2 Contract

### Schema Version

- Keep existing `EVIDENCE_CONFIRM_SCHEMA_VERSION = "evidence_confirm.v1"` for existing phase-1 functions.
- Add `EVIDENCE_CONFIRM_V2_SCHEMA_VERSION = "evidence_confirm.v2"` for the new V2 result shape.

### New Literal Domains

Add these public type aliases in `fund_agent/fund/evidence_confirm.py`:

- `EvidenceConfirmGateStatus = Literal["pass", "warn", "fail", "not_applicable"]`
- `EvidenceConfirmDimension = Literal["anchor_precision", "source_support", "missing_evidence", "proof_boundary", "value_match"]`
- `EvidenceConfirmDimensionStatus = Literal["pass", "warn", "fail", "not_applicable"]`
- `EvidenceConfirmGateSeverity = Literal["blocking", "reviewable", "informational"]`
- `EvidenceConfirmNextGateRecommendation = Literal["evidence_anchor", "source_truth_proof", "value_matching", "manual_review", "not_applicable"]`

Do not reuse report-quality `ScoreDimension` inside the Evidence Confirm result type. A later bridge can map `anchor_precision` / `source_support` / `missing_evidence` to report-quality `evidence_traceability`.

### New Dataclasses

`EvidenceConfirmDimensionResult`

- `dimension: EvidenceConfirmDimension`
- `status: EvidenceConfirmDimensionStatus`
- `score: int | None`
- `issue_ids: tuple[str, ...]`
- `matched_anchor_ids: tuple[str, ...]`
- `next_gate_recommendation: EvidenceConfirmNextGateRecommendation`
- `message: str | None = None`

`EvidenceConfirmHardGate`

- `status: EvidenceConfirmGateStatus`
- `blocking_issue_ids: tuple[str, ...]`
- `reviewable_issue_ids: tuple[str, ...]`
- `informational_issue_ids: tuple[str, ...]`
- `passed_dimension_count: int`
- `failed_dimension_count: int`
- `warn_dimension_count: int`
- `not_applicable_dimension_count: int`

`EvidenceConfirmFactResultV2`

- `fact_id: str`
- `source_field_id: str`
- `status: EvidenceConfirmGateStatus`
- `hard_gate: EvidenceConfirmHardGate`
- `dimension_results: tuple[EvidenceConfirmDimensionResult, ...]`
- `matched_anchor_ids: tuple[str, ...]`
- `issue_ids: tuple[str, ...]`
- `auditability_score: int | None`

`EvidenceConfirmResultV2`

- `schema_version: str`
- `fund_code: str`
- `report_year: int`
- `fact_results: tuple[EvidenceConfirmFactResultV2, ...]`
- `issues: tuple[EvidenceConfirmIssue, ...]`
- `checked_rules: tuple[EvidenceConfirmRuleCode, ...]`
- `hard_gate: EvidenceConfirmHardGate`
- `overall_status: EvidenceConfirmGateStatus`
- `auditability_score: int | None`

### New Public Functions

`confirm_chapter_evidence_v2(chapter: ChapterFactInput, references: tuple[EvidenceConfirmReference, ...]) -> EvidenceConfirmResultV2`

- Uses the same proof predicates as phase 1.
- Produces V2 dimension results and hard gate.
- Does not mutate `ChapterFactInput`.
- Does not read external state.

`confirm_projection_evidence_v2(projection: ChapterFactProjection, references: tuple[EvidenceConfirmReference, ...]) -> EvidenceConfirmResultV2`

- Aggregates all chapter fact results.
- Stable ordering by `chapter_id`, `source_field_id`, `fact_id`.
- Aggregates hard gate from fact-level hard gates.

Existing `confirm_chapter_evidence()` and `confirm_projection_evidence()` remain unchanged unless implementation chooses to share private helpers internally. Existing tests must continue to pass.

## Dimension Semantics

### `anchor_precision`

Purpose: capture E1 locator auditability.

- `pass` / score `100`: proven reference has enough locator precision.
- `warn` / score `70`: reference is proven and value-supported, but locator is imprecise.
- `fail`: not used for locator precision alone in V2 unless the implementation discovers a logically impossible locator conflict that already makes the reference non-proof.
- `not_applicable`: derived calculation or not-applicable fact.
- next gate: `evidence_anchor`.

### `source_support`

Purpose: capture whether the fact has a proven reference excerpt for one of its own anchors.

- `pass` / score `100`: at least one proven reference is tied to the fact's own known anchor.
- `fail` / score `0`: no proven reference exists for required available annual-report fact.
- `not_applicable`: derived / synthetic / not-applicable fact outside current phase-1 proof source kinds.
- next gate: `source_truth_proof`.

### `missing_evidence`

Purpose: capture E3 missing required evidence.

- `pass` / score `100`: required available fact has at least one known anchor and proven reference.
- `fail` / score `0`: `fact.missing_reason == "evidence_missing"`, no fact anchors, dangling anchors, or no proven reference for required available fact.
- `not_applicable`: safe gap / not-applicable / derived fact.
- next gate: `evidence_anchor` or `source_truth_proof` depending on whether the missing object is anchor or proven reference.

### `proof_boundary`

Purpose: make candidate-only / not-proven / unsupported source-kind handling explicit instead of hiding it under E3.

- `pass` / score `100`: every supporting reference used by the fact satisfies the closed proof predicate.
- `fail` / score `0`: any reference is candidate-only, not-proven, invalid kind-pair, unknown source kind, year-mismatched, or anchor-mismatched. **Mixed-reference rule**: if a fact has both valid proven references and invalid references, `proof_boundary` still fails because the presence of invalid same-anchor references introduces auditability uncertainty — the invalid reference may have been the one relied upon. The valid references are counted in `source_support` and `value_match` independently.
- `not_applicable`: no references were supplied and missing evidence is already represented by `missing_evidence`.
- next gate: `source_truth_proof`.

### `value_match`

Purpose: capture E2 same-anchor material-token support.

- `pass` / score `100`: at least one material token from the fact value appears in a proven same-anchor excerpt.
- `fail` / score `40`: proven same-anchor reference exists but no material token matches.
- `not_applicable`: no material token can be derived for non-required fact, or derived / not-applicable fact.
- next gate: `value_matching` or `manual_review`.

## Hard Gate Semantics

Fact-level hard gate:

- `fail` if any dimension result has status `fail` and any linked issue severity is `blocking`.
- `warn` if no blocking failure exists and at least one dimension is `warn`.
- `pass` if all applicable dimensions pass.
- `not_applicable` if every dimension is `not_applicable`.

Aggregate hard gate:

- `fail` if any fact-level hard gate fails.
- `warn` if no fact fails and at least one fact warns.
- `pass` if at least one fact passes and no fact fails or warns.
- `not_applicable` if no fact has an applicable result.

The V2 `overall_status` must equal the aggregate hard gate `status`.

## Score Semantics

### Status-aware score cap rule / fail cap (resolves finding 001)

Fact-level `auditability_score`:

- Compute the raw average of numeric dimension scores for that fact, excluding `None` / not-applicable dimensions.
- **Blocking failure cap**: if the fact hard gate status is `fail`, the fact `auditability_score` must be capped at the lowest blocking-failing dimension score (i.e., the minimum score among all dimensions whose status is `fail` and whose linked issue severity is `blocking`). This prevents a single blocking failure (e.g., `value_match=40`) from being diluted by high-scoring passing dimensions (e.g., `anchor_precision=100, source_support=100`).
- Round to nearest integer with deterministic integer behavior.
- Return `None` only when all dimensions are not applicable.

Aggregate `auditability_score`:

- Average numeric fact scores (using capped fact scores from above).
- **Aggregate blocking failure cap**: if any fact hard gate fails, the aggregate `auditability_score` must be capped at the lowest capped failing fact score.
- Return `None` only when no fact has a numeric score.

This replaces phase-1 coarse per-fact constants only for V2 functions. Phase-1 functions may keep their existing `100/70/40/0/None` behavior.

### Required score-cap validation assertions

Implementation must include these tests:

- Value mismatch hard-gate fail produces fact `auditability_score` ≤ `40` (the `value_match` fail score), not the naive average `88`.
- Candidate-only proof failure produces fact `auditability_score` = `0` (the `source_support` / `proof_boundary` fail score).
- Aggregate score with one blocking fact cannot report a pass-like score (≥ `70`).
- Aggregate score with all passing facts uses the uncapped average.

## Implementation Slices

### Slice 1 - V2 schema, scoring and proof-boundary implementation (merged)

Merged from prior Slice 1 + Slice 2 to ensure independently executable slice. The V2 type aliases, dataclasses, hard-gate helpers, public V2 functions, dimension scoring and proof-boundary logic are implemented together because V2 result construction and dimension-order tests require the public V2 functions to exist.

Allowed files:

- `fund_agent/fund/evidence_confirm.py`
- `tests/fund/test_evidence_confirm.py`
- implementation evidence artifact under `docs/reviews/`

Allowed changes:

- Add V2 type aliases and dataclasses.
- Add private helpers to build fact-level and aggregate `EvidenceConfirmHardGate`.
- Implement `confirm_chapter_evidence_v2()` and `confirm_projection_evidence_v2()`.
- Reuse existing proof predicate and material-token matching helpers.
- Add proof-boundary dimension results for candidate-only, not-proven, wrong source kind, invalid kind pair, document-year mismatch and anchor-source mismatch.
- Implement status-aware score cap rule.
- Do not change existing public V1 function output.

Required tests:

- V2 result uses `evidence_confirm.v2`.
- V2 fact result includes all five dimensions in deterministic order.
- Blocking E3 produces hard gate `fail`.
- E1-only imprecision produces hard gate `warn`.
- All applicable pass produces hard gate `pass`.
- Derived / not-applicable-only input produces hard gate `not_applicable`.
- Candidate-only reference fails `proof_boundary` and `source_support`.
- Not-proven reference fails `proof_boundary`.
- Invalid reference kind/source kind pair fails `proof_boundary`.
- Wrong document year fails `proof_boundary`.
- Mixed references (valid proven + invalid same-anchor) fail `proof_boundary` even when valid proof exists.
- Proven same-anchor value mismatch fails `value_match` while `source_support` can pass.
- Unrelated anchor excerpt cannot pass `value_match`.
- Projection aggregation remains deterministic and averages only numeric fact scores.
- Value mismatch hard-gate fail produces fact `auditability_score` ≤ `40`.
- Candidate-only proof failure produces fact `auditability_score` = `0`.
- Aggregate score with one blocking fact cannot report a pass-like score (≥ `70`).
- Aggregate score with all passing facts uses the uncapped average.

Validation:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py docs/reviews/evidence-confirm-scoring-v2-implementation-evidence-20260621.md
```

### Slice 2 - Documentation sync after implementation acceptance

Allowed files:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- docs sync evidence artifact under `docs/reviews/`

Allowed changes:

- State current code fact: Evidence Confirm V2 no-live scoring contract exists in Fund layer.
- Preserve boundaries: no Service/UI/Host/renderer/quality-gate/live source/PDF/parser/release integration.
- Keep release/readiness `NOT_READY`.

Required validation:

```bash
rg -n "Evidence Confirm|evidence_confirm.v2|hard gate|dimension" docs/design.md fund_agent/fund/README.md tests/README.md
git diff --check -- docs/design.md fund_agent/fund/README.md tests/README.md docs/reviews/evidence-confirm-scoring-v2-docs-sync-evidence-20260621.md
```

## Plan Review Focus

Plan reviewers should specifically challenge:

- whether V2 should coexist with V1 or replace V1;
- whether `proof_boundary` overlaps too much with `source_support`;
- whether fact-level score averaging hides blocking failures;
- whether `EvidenceConfirmDimension` should map now or later into report-quality `ScoreDimension`;
- whether the proposed slices are small enough for separate implementation/review loops;
- whether any wording accidentally authorizes upper-layer consumption, live source/PDF access, parser replacement, quality-gate change, PR ready/merge or release transition.

## Expected Completion Report Format

Implementation worker must report:

- Changed files.
- Implemented slice id(s).
- Public API added.
- V1 compatibility statement.
- Validation commands and observed results.
- Boundary confirmation.
- Residual risks.
- Final verdict token.

Expected implementation verdict token:

```text
IMPLEMENTATION_COMPLETE_VALIDATED_NOT_READY
```

## Residual Risks / Owners

- Dayu upstream details were not locally re-read in this planning gate; only the accepted control-doc direction "hard gate + dimension score" is used. Owner: implementation controller if finer Dayu parity becomes necessary.
- V2 remains no-live and caller-supplied-reference only. Owner: later live source/PDF Evidence Confirm gate.
- Semantic entailment beyond conservative material-token matching remains unimplemented. Owner: later semantic Evidence Confirm gate.
- Report-quality bridge from V2 Evidence Confirm dimensions to `ReportScoreIssueLink` remains future work. Owner: later report workflow adoption gate.
- Quality gate impact remains out of scope. Owner: later FQ gate integration gate if authorized.

## Verdict

PLAN_READY_FOR_REVIEW_NOT_READY
