# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Plan

> Date: 2026-05-25
> Worker: AgentCodex implementation planning specialist only
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Scope: implementation plan artifact only. No source code, tests, renderer, FQ0-FQ6, config, README, design doc, control doc, Host/Agent package, `dayu.host`, `dayu.engine`, fixture promotion, commit, push, or PR work.

## Step Self-Check

- Role: implementation planning specialist only, not controller.
- Truth sources read: `AGENTS.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; `docs/design.md` §2.1, §5.4, §5.4.1, §5.4.2, §5.4.3, §7.2, §7.3, §7.4; accepted S2 bundle candidate plan and controller judgment.
- Code facts inspected: `fund_agent/fund/data_extractor.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/fund_type.py`, `fund_agent/fund/template/contracts.py`, `fund_agent/fund/template/lens_application.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_golden_prefill.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/extraction_score.py`.
- Current code already uses frozen slotted dataclasses for `StructuredFundDataBundle`, `ExtractedField`, `EvidenceAnchor`, `TemplateLensRule`, and quality rows. The plan follows that local pattern.
- Current production extraction path is already repository-bounded through `FundDataExtractor` -> `FundDocumentRepository`; the future projection must consume an already-created `StructuredFundDataBundle` and must not read PDFs, cache files, source helpers, or download helpers.

## Objective

Create a code-generation-ready implementation plan for the first typed `ReportEvidenceBundle` slice. This slice must turn accepted S2 design into executable model and projection code without changing the current renderer, FQ0-FQ6 quality gate, durable baseline selection, or Host/Agent runtime.

The first implementation should be deliberately narrow:

1. Add typed immutable report-evidence records inside Agent-layer `fund_agent/fund`.
2. Project current `StructuredFundDataBundle` `ExtractedField` groups into facts, anchors, gaps, preferred-lens projection, source-document context, quality context, score issue links, and derived `review_status`.
3. Add focused unit tests with fake bundles. Do not use tracked scoring-run outputs or promoted fixtures.

## Future File Ownership

### Source File

Add one cohesive module:

```text
fund_agent/fund/report_evidence.py
```

Ownership rationale:

- The model understands fund type, CHAPTER_CONTRACT, preferred_lens, evidence anchors, data gaps, scoring dimensions, and report-quality review state, so it belongs to Agent-layer Fund domain capability.
- It must not live in `fund_agent/services/`, because Service should orchestrate use cases and pass explicit typed parameters, not understand extractor internals.
- It must not live in `fund_agent/fund/template/renderer.py`, because the first slice is an input contract/projection, not report rendering.
- It must not be placed in `fund_agent/fund/extractors/models.py`, because extractor models describe P1 field extraction; `ReportEvidenceBundle` adds report-quality lifecycle, score linkage, and review status over the extraction bundle.

The module should contain:

- Literal domains and constants.
- Frozen slotted dataclasses for bundle records.
- A typed `ReportEvidenceProjectionContext` with explicit fields.
- `project_report_evidence_bundle(...)`.
- Deterministic id helpers for anchors, gaps, and score issues.
- `derive_report_evidence_review_status(...)`.
- Validation helpers for invalid combinations.

Do not edit `fund_agent/fund/data_extractor.py`, extractor modules, renderer, quality gate, Service, Host, or Agent runtime in the first slice.

### Test File

Add one focused test module:

```text
tests/fund/test_report_evidence.py
```

The tests should build fake `StructuredFundDataBundle` objects directly, following patterns in `tests/fund/test_extraction_snapshot.py` and `tests/fund/test_golden_prefill.py`. They must not call `FundDataExtractor.extract()`, `FundDocumentRepository`, PDF adapters, network, cache, CLI, renderer, or FQ0-FQ6.

### Public Export

Do not modify `fund_agent/fund/__init__.py` in the first implementation unless the controller explicitly wants a package-level public export. Direct imports from `fund_agent.fund.report_evidence` are enough for tests and keep the API surface small.

If the implementation gate includes documentation sync, update `fund_agent/fund/README.md` minimally after tests pass because `fund_agent/fund/` changed. If that gate's allowed files exclude README, record the README sync as a controller-owned residual rather than widening the code slice.

## Immutability Decision

Use `@dataclass(frozen=True, slots=True)` for all new records.

Reasons:

- It matches current local model style: `StructuredFundDataBundle`, `ExtractedField`, `EvidenceAnchor`, `TemplateLensRule`, `QualityGateResult`, and scoring rows are frozen slotted dataclasses.
- Report-evidence records are audit inputs. They should be constructed once, validated, and passed forward without accidental mutation.
- `slots=True` keeps instances small and prevents unreviewed ad hoc attributes, supporting the no-`extra_payload` rule.
- A Pydantic dependency is not currently present and would add validation machinery beyond the minimal slice.

Use tuple fields instead of mutable lists for child records and refs. Use mapping fields only for serializable value payloads already coming from extracted facts; do not add free dict catchalls for business parameters.

## Exact Value Domains

Implement domains as `Literal[...]` aliases plus `Final` tuples derived with `typing.get_args(...)` where useful for validation.

### Fund and Slot Domains

```python
ClassifiedFundType = FundType | Literal["unknown"]
FundTypeSlot = FundType
TypeSlotMembershipStatus = Literal[
    "matches_slot",
    "type_gap",
    "taxonomy_pending",
    "unknown",
    "not_applicable",
]
```

`ClassifiedFundType` is read only from `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]`. Projection must not infer it from fund name, benchmark, or category text.

### Source Document / Boundary Domains

```python
DocumentType = Literal["annual_report", "prospectus", "fund_contract", "periodic_report"]
DocumentIdentityStatus = Literal[
    "verified_annual_report",
    "unverified",
    "mismatch",
    "source_failed",
    "verified_as_annual_report_but_type_gap",
]
SourceBoundary = Literal[
    "repository_derived",
    "derived_calculation",
    "external_official",
    "manual_review",
    "unknown",
    "probe_only",
]
SourceFailureCategory = Literal[
    "none",
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "unknown_upstream_failure_category",
]
```

`external_official` is metadata only in this slice. It must not authorize direct external API calls and must not by itself make a bundle `scoring_ready`.

`SourceFailureCategory` must stay aligned with the accepted S2 source-failure domain. Do not add `data_gap` or `not_applicable` here. Fact-level data gaps and applicability gaps belong only to `GapKind`, `GapFailureCategory`, `DataGapReasonCode`, score records, or `ReportDataGap` records.

Fallback eligibility is derived:

- `fallback_allowed=True` only for `not_found` and `unavailable`.
- `schema_drift`, `identity_mismatch`, and `integrity_error` are fail-closed and derive `review_status="rejected"`.
- `unknown_upstream_failure_category` derives `review_status="deferred"` and blocks `scoring_ready`.

### Anchor Domains

Do not change `fund_agent/fund/extractors/models.py` `EvidenceSourceKind`. Wrap current anchors in the new report model.

```python
ReportAnchorSourceKind = Literal["annual_report", "external_api", "derived", "reviewed_note"]
SourceStrength = Literal[
    "fund_disclosure",
    "official_reference",
    "manager_statement",
    "third_party_reference",
    "derived",
    "manual_review",
]
```

Current `EvidenceAnchor.source_kind` values map as:

| Current `EvidenceAnchor.source_kind` | `ReportAnchorSourceKind` | Default `SourceStrength` |
|---|---|---|
| `annual_report` | `annual_report` | `fund_disclosure` |
| `external_api` | `external_api` | `third_party_reference` |
| `derived` | `derived` | `derived` |

`reviewed_note` is only for manual review artifact anchors supplied through explicit typed context or future review rows. It must not be added to extractor `EvidenceSourceKind`.

### Fact Domains

```python
FactCategory = Literal[
    "identity",
    "fund_type",
    "benchmark",
    "performance",
    "fee",
    "manager",
    "holdings",
    "holders",
    "risk",
    "valuation",
    "thermometer",
    "nav",
    "other",
]
ReportExtractionMode = Literal[
    "direct",
    "derived",
    "estimated",
    "missing",
    "manual_reviewed",
    "not_applicable",
]
FactUnit = Literal[
    "percent",
    "ratio",
    "cny",
    "date",
    "text",
    "count",
    "object",
    "not_applicable",
    "unknown",
]
```

`nav` remains in the value domain for future compatibility, but the initial projection must not emit `category="nav"` facts because `StructuredFundDataBundle.nav_data` is a `NavDataResult`, not an `ExtractedField`.

### Data Gap Domains

```python
GapKind = Literal[
    "missing_fact",
    "not_disclosed",
    "not_reviewed",
    "source_failure",
    "identity_conflict",
    "type_slot_gap",
    "unsupported_claim",
    "not_applicable",
    "manual_review_required",
]
GapFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "not_disclosed",
    "ambiguous",
    "not_applicable",
    "unsupported_source",
    "manual_review_required",
    "not_reviewed_in_current_slice",
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "unknown_upstream_failure_category",
]
DataGapReasonCode = Literal[
    "missing_from_extractor",
    "not_reviewed_in_current_slice",
    "not_disclosed",
    "manual_review_required",
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "classified_as_different_fund_type",
    "unknown_upstream_failure_category",
    "unsupported_stability_claim",
    "not_applicable_to_fund_type",
    "source_failed",
]
ChapterRef = Literal[
    "chapter_0",
    "chapter_1",
    "chapter_2",
    "chapter_3",
    "chapter_4",
    "chapter_5",
    "chapter_6",
    "chapter_7",
    "report_level",
]
```

### Review Status Domain

```python
ReviewStatus = Literal[
    "candidate",
    "repository_verified",
    "fact_prefill_generated",
    "fact_prefill_reviewed",
    "scoring_ready",
    "accepted_baseline",
    "rejected",
    "deferred",
    "expired",
]
FactReviewStatus = Literal["not_reviewed", "partially_reviewed", "reviewed"]
SchemaRevisionStatus = Literal["current", "expired"]
```

`accepted_baseline` must exist in the domain because S1/S2 accepted it as a future lifecycle state, but the first implementation must never derive it unless a later curated-fixture gate adds an explicit enablement path. For this slice, validation should reject any caller-supplied attempt to force `accepted_baseline`.

### Quality Context Domains

```python
FQGateStatus = Literal["pass", "warn", "block", "not_run"]
ProgrammaticAuditStatus = Literal["pass", "warn", "block", "not_run"]
JudgmentConstraint = Literal[
    "strong_allowed",
    "cautious_only",
    "must_downgrade_or_block",
    "not_evaluated",
]
```

### Score Domains

```python
ScoreDimension = Literal[
    "fact_coverage",
    "extraction_correctness",
    "evidence_traceability",
    "chapter_contract_completeness",
    "final_judgment_consistency",
    "investment_advice_boundary",
    "readability_actionability",
    "chapter_summary",
]
ScoreRecordStatus = Literal["pass", "issue", "blocked", "N/A", "skipped"]
ScoreIssueSeverity = Literal["blocking", "material", "minor"]
NextGateRecommendation = Literal[
    "source_reliability",
    "data_extraction",
    "evidence_anchor",
    "chapter_contract",
    "final_judgment_contract",
    "wording_audit",
    "writing_iteration",
    "manual_review",
    "fund_type_taxonomy",
    "stop_before_durable_baseline",
    "review_acceptance",
]
```

Validation rules:

- `ScoreRecordStatus="N/A"` requires `na_reason` or reviewer note.
- `ScoreRecordStatus="skipped"` requires `ScoreDimension="chapter_summary"`.
- `ScoreDimension="chapter_summary"` is invalid unless status is `skipped`.

### Derived Calculation Domains

```python
CalculationFormulaName = Literal[
    "r_abc",
    "cost_estimate",
    "thermometer_state",
    "pressure_test",
    "final_judgment_support",
    "other",
]
CalculationStatus = Literal[
    "computed",
    "blocked_by_missing_fact",
    "blocked_by_conflict",
    "not_applicable",
    "manual_review_required",
]
```

The minimal slice should define the `DerivedCalculation` record shape only, with `ReportEvidenceBundle.derived_calculations` defaulting to an empty tuple. Do not populate calculations and do not add calculation-specific validation branches in the first slice. This avoids coverage churn for R=A+B-C / pressure-test logic that belongs to a later calculation-source slice.

## Proposed Dataclasses

Implement these frozen slotted dataclasses in `fund_agent/fund/report_evidence.py`.

```text
ReportSourceDocument
ReportEvidenceAnchor
ReportDataGap
ReportFact
DerivedCalculation
ReportScoreIssueLink
ReportQualityContext
ReportPreferredLensChapter
ReportPreferredLensProjection
ReportEvidenceProjectionContext
ReportEvidenceBundle
ReportDataGapOverride
```

Important field rules:

- `fund_code` and `report_year` always come from the input `StructuredFundDataBundle`, not from `ReportEvidenceProjectionContext`. The context carries review/projection metadata only.
- Fields marked "default" must have immutable defaults such as `()` or explicit scalar defaults. Do not use mutable list/dict defaults.

### Dataclass Field Specifications

`ReportSourceDocument`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `document_id` | required | `str` | `doc:{fund_code}:{report_year}:annual_report`. |
| `document_type` | required | `DocumentType` | First slice always uses `annual_report`. |
| `identity_status` | required | `DocumentIdentityStatus` | From context. |
| `source_boundary` | required | `SourceBoundary` | From context. |
| `source_failure_category` | required | `SourceFailureCategory` | S2 source-failure domain only. |
| `fallback_allowed` | required | `bool` | Derived from source failure category. |
| `fallback_used` | required | `bool` | From context. |
| `review_artifact_refs` | default `()` | `tuple[str, ...]` | Tracked Markdown review refs only. |

`ReportEvidenceAnchor`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `anchor_id` | required | `str` | Deterministic bundle-local id. |
| `source_kind` | required | `ReportAnchorSourceKind` | Wrapper domain; do not widen extractor enum. |
| `source_strength` | required | `SourceStrength` | Default mapping from current anchor kind unless context supplies reviewed-note anchors. |
| `document_id` | default `None` | `str | None` | Required for annual-report anchors. |
| `document_year` | default `None` | `int | None` | Mirrors `EvidenceAnchor`. |
| `section_id` | default `None` | `str | None` | Mirrors `EvidenceAnchor`. |
| `page_number` | default `None` | `int | None` | Mirrors `EvidenceAnchor`. |
| `table_id` | default `None` | `str | None` | Mirrors `EvidenceAnchor`. |
| `row_locator` | default `None` | `str | None` | Mirrors `EvidenceAnchor`. |
| `review_artifact_ref` | default `None` | `str | None` | For `reviewed_note` anchors. |
| `note` | default `None` | `str | None` | Short provenance note only. |

`ReportDataGap`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `gap_id` | required | `str` | `gap:{fund_code}:{report_year}:{gap_kind}:{field_or_claim_path}:{reason_code}`. |
| `gap_kind` | required | `GapKind` | Fact/claim/source gap kind. |
| `field_path` | default `None` | `str | None` | Required for field-level gaps. |
| `related_fact_id` | default `None` | `str | None` | Required when gap is attached to a fact. |
| `related_claim_id` | default `None` | `str | None` | Required for unsupported claim gaps. |
| `chapter_ids` | required | `tuple[ChapterRef, ...]` | At least one; use `report_level` when not chapter-specific. |
| `failure_category` | required | `GapFailureCategory` | May include `not_applicable` / fact-level data-gap categories. |
| `reason_code` | required | `DataGapReasonCode` | Controlled snake_case reason. |
| `fallback_allowed` | required | `bool` | True only for document-source `not_found` / `unavailable` categories. |
| `fallback_used` | required | `bool` | Preserve original fallback state. |
| `required_report_wording` | required | `str` | Wording constraint, not renderer implementation. |
| `blocks_claim_ids` | default `()` | `tuple[str, ...]` | Claims blocked by the gap. |
| `blocks_scoring_dimensions` | default `()` | `tuple[ScoreDimension, ...]` | Affected score dimensions. |
| `score_issue_ids` | default `()` | `tuple[str, ...]` | Linked score issues. |

`ReportFact`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `fact_id` | required | `str` | `fact:{category}.{field_path}`. |
| `category` | required | `FactCategory` | From field spec. |
| `field_path` | required | `str` | Current bundle field path. |
| `value` | required | `object | None` | JSON-serializable extracted value or `None`. |
| `unit` | required | `FactUnit` | From field spec. |
| `period` | default `None` | `str | None` | Required only for time-sensitive values when known. |
| `source_anchor_ids` | default `()` | `tuple[str, ...]` | All mapped anchors; no secondary anchor drop. |
| `source_document_ids` | default `()` | `tuple[str, ...]` | Annual-report facts reference source document id. |
| `source_boundary` | required | `SourceBoundary` | Usually context source boundary. |
| `extraction_mode` | required | `ReportExtractionMode` | Current mode plus report-specific modes. |
| `review_status` | required | `FactReviewStatus` | From context / review state. |
| `failure_category` | default `None` | `GapFailureCategory | None` | Required for unsafe/missing/conflicted values. |
| `data_gap_refs` | default `()` | `tuple[str, ...]` | Must reference same-bundle gaps. |
| `score_issue_ids` | default `()` | `tuple[str, ...]` | Linked score issues. |

`DerivedCalculation`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `calculation_id` | required | `str` | `calc:{formula_name}.{scope}`. |
| `formula_name` | required | `CalculationFormulaName` | Record shape only in first slice. |
| `input_fact_ids` | default `()` | `tuple[str, ...]` | No automatic population in first slice. |
| `input_anchor_ids` | default `()` | `tuple[str, ...]` | Inherited anchors if supplied later. |
| `output_value` | default `None` | `object | None` | Empty unless supplied by later calculation slice. |
| `calculation_status` | required | `CalculationStatus` | Required for any manually supplied calculation record. |
| `assumptions` | default `()` | `tuple[str, ...]` | Empty when none. |
| `degradation_text` | default `None` | `str | None` | Required for blocked-but-mentioned calculations in future slices. |
| `data_gap_refs` | default `()` | `tuple[str, ...]` | Same-bundle gap ids. |
| `score_issue_ids` | default `()` | `tuple[str, ...]` | Linked score issues. |

`ReportScoreIssueLink`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `issue_id` | required | `str` | Canonical issue id. |
| `score_run_id` | required | `str` | Local score run id or reviewed artifact run id. |
| `chapter_id` | required | `ChapterRef` | Current v0 chapter or report-level. |
| `dimension` | required | `ScoreDimension` | S1 dimensions. |
| `status` | required | `ScoreRecordStatus` | Pass/issue/blocked/N/A/skipped. |
| `severity` | default `None` | `ScoreIssueSeverity | None` | Required when status is issue/blocked. |
| `field_path` | default `None` | `str | None` | Field-level linkage. |
| `claim_id` | default `None` | `str | None` | Claim-level linkage. |
| `contract_item_id` | default `None` | `str | None` | CHAPTER_CONTRACT / ITEM_RULE linkage. |
| `problem` | default `None` | `str | None` | Localized problem text. |
| `expected` | default `None` | `str | None` | Expected behavior. |
| `observed_ref` | default `None` | `str | None` | Reviewed evidence ref. |
| `evidence_anchor_refs` | default `()` | `tuple[str, ...]` | Anchor ids or reviewed Markdown refs. |
| `data_gap_refs` | default `()` | `tuple[str, ...]` | Same-bundle gap ids. |
| `next_gate_recommendation` | required | `NextGateRecommendation` | Owner of next action. |
| `na_reason` | default `None` | `str | None` | Required for `N/A` unless reviewer note equivalent exists. |
| `reviewer_note` | default `None` | `str | None` | Review note or N/A reason equivalent. |

`ReportQualityContext`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `fq_gate_status` | default `"not_run"` | `FQGateStatus` | Mirrors current FQ0-FQ6 final status semantics. |
| `fq_issue_refs` | default `()` | `tuple[str, ...]` | Rule ids or short issue refs. |
| `programmatic_audit_status` | default `"not_run"` | `ProgrammaticAuditStatus` | Observational only. |
| `report_quality_score_refs` | default `()` | `tuple[str, ...]` | Score issue ids / score run refs. |
| `known_residual_refs` | default `()` | `tuple[str, ...]` | Review artifacts / residual ids. |
| `judgment_constraint` | default `"not_evaluated"` | `JudgmentConstraint` | Derived confidence constraint. |

`ReportPreferredLensChapter`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `chapter_id` | required | `ChapterRef` | Only `chapter_0` to `chapter_7`; not `report_level`. |
| `lens_key` | required | `LensKey` | From `LensChapterApplication`. |
| `used_default` | required | `bool` | From `LensChapterApplication`. |
| `primary_focus` | required | `str` | Serializable focus label. |
| `watch_variable_label` | default `None` | `str | None` | Serializable focus label. |
| `risk_focus_label` | default `None` | `str | None` | Serializable focus label. |
| `source_statements` | default `()` | `tuple[str, ...]` | CHAPTER_CONTRACT statements. |

`ReportPreferredLensProjection`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `fund_type` | required | `ClassifiedFundType` | `unknown` allowed only with empty chapters. |
| `chapters` | default `()` | `tuple[ReportPreferredLensChapter, ...]` | Must cover 0..7 for scoring-ready bundles. |

`ReportEvidenceProjectionContext`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `run_id` | required | `str` | Bundle id component. |
| `corpus_id` | required | `str` | `ad_hoc` or `corpus:{name}:{version}`. |
| `source_boundary` | required | `SourceBoundary` | Required to avoid implicit evidence boundary. |
| `source_failure_category` | required | `SourceFailureCategory` | S2 source-failure domain only. |
| `fund_type_slot` | default `None` | `FundType | None` | Baseline slot; not duplicated from bundle. |
| `document_identity_status` | default `"verified_annual_report"` | `DocumentIdentityStatus` | Default fits already-extracted repository bundle. |
| `fallback_used` | default `False` | `bool` | Must be explicit when fallback happened. |
| `review_artifact_refs` | default `()` | `tuple[str, ...]` | Tracked Markdown artifacts. |
| `fact_review_status` | default `"not_reviewed"` | `FactReviewStatus` | Controls review-status derivation. |
| `schema_revision_status` | default `"current"` | `SchemaRevisionStatus` | `expired` derives expired. |
| `quality_context` | default factory | `ReportQualityContext` | Default all not-run / not-evaluated. |
| `data_gap_overrides` | default `()` | `tuple[ReportDataGapOverride, ...]` | Explicit reviewed gaps such as turnover. |
| `score_issue_links` | default `()` | `tuple[ReportScoreIssueLink, ...]` | Explicit score issue links. |
| `attempted_review_status` | default `None` | `ReviewStatus | None` | Must be rejected if set to `accepted_baseline` in first slice. |

`ReportEvidenceBundle`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `bundle_id` | required | `str` | `reb:{fund_code}:{report_year}:{schema_version}:{run_id}`. |
| `schema_version` | required | `str` | `REPORT_EVIDENCE_SCHEMA_VERSION`. |
| `corpus_id` | required | `str` | From context. |
| `fund_code` | required | `str` | From `StructuredFundDataBundle.fund_code`. |
| `report_year` | required | `int` | From `StructuredFundDataBundle.report_year`. |
| `classified_fund_type` | required | `ClassifiedFundType` | From `basic_identity.value`. |
| `fund_type_slot` | default `None` | `FundType | None` | From context. |
| `type_slot_membership_status` | required | `TypeSlotMembershipStatus` | Derived. |
| `preferred_lens` | required | `ReportPreferredLensProjection` | Serializable projection. |
| `source_documents` | default `()` | `tuple[ReportSourceDocument, ...]` | First slice creates one annual report doc. |
| `facts` | default `()` | `tuple[ReportFact, ...]` | Projected current field groups. |
| `derived_calculations` | default `()` | `tuple[DerivedCalculation, ...]` | Empty in first slice. |
| `evidence_anchors` | default `()` | `tuple[ReportEvidenceAnchor, ...]` | Projected anchors. |
| `data_gaps` | default `()` | `tuple[ReportDataGap, ...]` | Explicit missing/unsafe facts. |
| `quality_context` | required | `ReportQualityContext` | Context plus issue refs. |
| `score_issue_links` | default `()` | `tuple[ReportScoreIssueLink, ...]` | Context-supplied links after validation. |
| `review_status` | required | `ReviewStatus` | Derived only. |
| `validation_messages` | default `()` | `tuple[str, ...]` | Non-fatal warnings such as hash collision suffixing. |

`ReportDataGapOverride`:

| Field | Required / default | Type | Notes |
|---|---|---|---|
| `field_path` | required | `str` | May be short (`turnover_rate`) or normalized (`manager.turnover_rate`). |
| `gap_kind` | required | `GapKind` | Example: `not_reviewed`. |
| `failure_category` | required | `GapFailureCategory` | Example: `not_reviewed_in_current_slice`. |
| `reason_code` | required | `DataGapReasonCode` | Example: `not_reviewed_in_current_slice`. |
| `chapter_ids` | required | `tuple[ChapterRef, ...]` | Example: `("chapter_3",)`. |
| `required_report_wording` | required | `str` | Wording constraint. |
| `related_claim_id` | default `None` | `str | None` | Claim blocked by the gap, when known. |
| `blocks_claim_ids` | default `()` | `tuple[str, ...]` | Claim ids blocked by this override. |
| `blocks_scoring_dimensions` | default `()` | `tuple[ScoreDimension, ...]` | Affected scoring dimensions. |
| `score_issue_ids` | default `()` | `tuple[str, ...]` | Optional pre-linked issue ids. |

Use a module constant:

```python
REPORT_EVIDENCE_SCHEMA_VERSION = "report_evidence_bundle.v0"
```

Bundle id format:

```text
reb:{fund_code}:{report_year}:{schema_version}:{run_id}
```

`corpus_id` behavior:

- `ad_hoc` is allowed for local non-baseline inspection and must not derive `scoring_ready`.
- Baseline-like corpus ids use `corpus:{corpus_name}:{version}`, for example `corpus:rqb_s0:20260525`.

## Projection Algorithm

Implement:

```python
def project_report_evidence_bundle(
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
) -> ReportEvidenceBundle:
    ...
```

The context object is allowed because it has explicit typed fields. Do not accept `extra_payload`, `dict[str, object]` options, `**kwargs`, source helper objects, repository objects, file paths, or cache paths.

`fund_code` and `report_year` must be read from `bundle.fund_code` and `bundle.report_year`. Do not duplicate them in `ReportEvidenceProjectionContext`; duplicating identity fields creates mismatch risk between the wrapped extraction bundle and the projection metadata.

### Step 1: Validate Projection Context

Fail fast with `ValueError` for:

- empty `run_id`;
- empty `corpus_id`;
- illegal corpus id shape except exact `ad_hoc`;
- `fund_type_slot` outside `FundType` when provided;
- `fallback_used=True` with `source_failure_category="none"`;
- `fallback_used=True` with fail-closed categories `schema_drift`, `identity_mismatch`, or `integrity_error`;
- `source_boundary="external_official"` used as the only evidence boundary for annual-report facts.
- `context.attempted_review_status == "accepted_baseline"` because no curated-fixture gate exists in this slice.

Do not open documents or call repositories here.

### Step 2: Build Source Document Record

Create one annual-report document record:

```text
document_id = doc:{fund_code}:{report_year}:annual_report
document_type = annual_report
identity_status = context.document_identity_status
source_boundary = context.source_boundary
source_failure_category = context.source_failure_category
fallback_allowed = source_failure_category in {"not_found", "unavailable"}
fallback_used = context.fallback_used
review_artifact_refs = context.review_artifact_refs
```

This record describes the boundary; it does not expose PDF paths, cache paths, source helper names, or download URLs as operational access routes.

### Step 3: Read `classified_fund_type`

Read only:

```python
bundle.basic_identity.value["classified_fund_type"]
```

Rules:

- If `basic_identity.value` is not a mapping, set `classified_fund_type="unknown"` and create a `missing_fact` data gap with reason `classified_fund_type_missing`.
- If the key is absent, set `unknown` and create the same gap.
- If the value is not one of current `FundType` values, set `unknown` and create a `type_slot_gap` with reason `classified_fund_type_invalid`.
- Do not infer fund type from `fund_name`, `fund_category`, benchmark text, or app category.

Derive `type_slot_membership_status`:

| Context / classified type | Derived status |
|---|---|
| `fund_type_slot is None` | `not_applicable` |
| `classified_fund_type == "unknown"` | `unknown` |
| `classified_fund_type == fund_type_slot` | `matches_slot` |
| `fund_type_slot == "fof_fund"` and classified type is `qdii_fund` | `taxonomy_pending` |
| otherwise | `type_gap` |

For nonmatching slot states, create a `type_slot_gap` unless `fund_type_slot is None`.

### Step 4: Project Preferred Lens

If `classified_fund_type != "unknown"`:

1. Call `build_lens_application_plan(classified_fund_type)` from `fund_agent.fund.template.lens_application`.
2. Convert the returned dataclasses into serializable frozen projection records:
   - `fund_type`
   - `chapter_id` as `chapter_0` ... `chapter_7`
   - `lens_key`
   - `used_default`
   - `primary_focus`
   - `watch_variable_label`
   - `risk_focus_label`
   - `source_statements`

Chapter id conversion rule: `LensChapterApplication.chapter_id` is an `int`; convert it with `f"chapter_{chapter_id}"` and validate the integer is in `0..7` before constructing `ReportPreferredLensChapter`. Any value outside `0..7` is a template-contract inconsistency and derives `review_status="rejected"`.

If `classified_fund_type == "unknown"`, return an empty preferred lens projection and block `scoring_ready`.

If lens resolution raises `ValueError` for a supposedly valid `FundType`, derive `review_status="rejected"` because template and fund-type contracts disagree.

### Step 5: Project Current `ExtractedField` Groups

Use a module-level field-spec tuple. This is configuration, not renderer logic.

| Bundle attribute | Fact category | Field path | Unit |
|---|---|---|---|
| `basic_identity` | `identity` | `basic_identity` | `object` |
| virtual from `basic_identity.value["classified_fund_type"]` | `fund_type` | `classified_fund_type` | `text` |
| `product_profile` | `identity` | `product_profile` | `object` |
| `benchmark` | `benchmark` | `benchmark` | `object` |
| `index_profile` | `benchmark` | `index_profile` | `object` |
| `fee_schedule` | `fee` | `fee_schedule` | `object` |
| `turnover_rate` | `manager` | `turnover_rate` | `percent` |
| `nav_benchmark_performance` | `performance` | `nav_benchmark_performance` | `object` |
| `investor_return` | `performance` | `investor_return` | `object` |
| `tracking_error` | `performance` | `tracking_error` | `ratio` |
| `share_change` | `holders` | `share_change` | `object` |
| `manager_alignment` | `manager` | `manager_alignment` | `object` |
| `manager_strategy_text` | `manager` | `manager_strategy_text` | `object` |
| `holdings_snapshot` | `holdings` | `holdings_snapshot` | `object` |
| `holder_structure` | `holders` | `holder_structure` | `object` |

`nav_data` is excluded from the initial facts projection. Add a negative test that no `ReportFact` has `field_path="nav_data"` or `category="nav"`.

Fact id format:

```text
fact:{category}.{field_path}
```

Examples:

- `fact:identity.basic_identity`
- `fact:fund_type.classified_fund_type`
- `fact:manager.turnover_rate`

### Step 6: Map Anchors Without Dropping Secondary Anchors

For each `ExtractedField`:

- Project every `EvidenceAnchor` into `ReportEvidenceAnchor`.
- Normalize each locator object using the Step 9 locator normalization rules before any deduplication.
- Deduplicate anchors by normalized locator object, not by object identity.
- After deduplication, assign anchor ids, compute `sha256` locator hashes, and apply deterministic collision suffixes.
- Attach all projected `anchor_id` values to the corresponding `ReportFact.source_anchor_ids`.
- Splitting one field into subfacts is out of scope for the first slice. Therefore one `ExtractedField` maps to one `ReportFact`, except the virtual `classified_fund_type` fact reuses `basic_identity` anchors.

Traceability rule:

- `direct`, `derived`, and `estimated` facts with non-null value and empty anchors must create a `manual_review_required` gap unless `extraction_mode="manual_reviewed"` and an explicit review artifact anchor is supplied.
- Missing anchors must not be silently ignored.

### Step 7: Validate Extraction Mode / Value Consistency

Use current `ExtractionMode` plus report-specific modes.

| Mode / value condition | Required behavior |
|---|---|
| `missing` and `value is None` | Create `ReportFact(value=None)` plus `ReportDataGap`; attach `data_gap_refs`. |
| `missing` and `value is not None` | Return a constructed `ReportEvidenceBundle` with `review_status="rejected"` and a validation message / data gap explaining the contradiction; do not raise unless the underlying `ExtractedField` object itself cannot be inspected. |
| `direct` / `derived` / `estimated` and `value is None` | Create `manual_review_required` or `ambiguous` gap; derive at most `deferred`. |
| `direct` / `derived` / `estimated` and non-null value but no anchors | Create traceability gap; derive at most `deferred`. |
| `estimated` | Keep value only with `extraction_mode="estimated"`; do not allow strong claims unless a later calculation/wording rule accepts it. |
| `not_applicable` | Require `value is None`, unit `not_applicable`, and a nonblocking `not_applicable` gap or score record. |

Do not normalize contradictory states into clean passing records. The point of the bundle is to make failures visible.

### Step 8: Missing Fields Become Data Gaps

For each missing or unsafe field, create a gap id:

```text
gap:{fund_code}:{report_year}:{gap_kind}:{field_or_claim_path}:{reason_code}
```

Default rules:

- Missing `ExtractedField` without override:
  - `gap_kind="missing_fact"`
  - `failure_category="manual_review_required"`
  - `reason_code="missing_from_extractor"`
  - `required_report_wording="数据不足，需复核该字段后再作判断"`
- Explicit S1 turnover-style gap supplied by `ReportDataGapOverride`:
  - `gap_kind="not_reviewed"`
  - `field_path="manager.turnover_rate"` or `turnover_rate` normalized to the fact field path
  - `failure_category="not_reviewed_in_current_slice"`
  - `reason_code="not_reviewed_in_current_slice"`
  - `chapter_ids=("chapter_3",)`
  - `required_report_wording="当前 slice 未复核换手率，不能据此判断风格稳定"`
- Invalid classified fund type:
  - `gap_kind="type_slot_gap"`
  - `failure_category="classified_fund_type_invalid"`
  - `reason_code="classified_fund_type_invalid"`
- Missing classified fund type:
  - `gap_kind="missing_fact"`
  - `failure_category="classified_fund_type_missing"`
  - `reason_code="classified_fund_type_missing"`

`data_gap_refs` must reference only gap ids present in the same bundle. Score issue links may use legacy reviewed Markdown refs only in `evidence_anchor_refs`, not in `data_gap_refs`.

### Step 9: Deterministic Anchor ID Hashing

Anchor id format:

```text
anchor:{fund_code}:{report_year}:{source_kind}:{section_or_source}:{locator_hash}
```

Sanitize `section_or_source`:

- Unicode NFC normalize.
- Strip.
- Replace leading `§` with `sec`.
- Lowercase ASCII letters.
- Collapse ASCII whitespace to `_`.
- Replace characters outside `[A-Za-z0-9_.-]` with `_`.
- Collapse repeated `_`.
- Use `unknown` when empty.

`locator_hash`:

1. Build an ordered JSON-compatible object with keys:
   - `page_number`
   - `table_id`
   - `row_locator`
   - `note`
   - `review_artifact_ref`
2. Convert `None` to `""`.
3. Convert all values except integer `page_number` to strings.
4. Strip leading/trailing whitespace.
5. Collapse internal ASCII whitespace to one space.
6. Apply Unicode NFC normalization.
7. Serialize with `json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",", ":"))`.
8. Hash UTF-8 bytes with `sha256`.
9. Use the first 8 lowercase hex characters.

Collision handling:

- Normalize locator objects first, deduplicate identical normalized locator objects second, and assign ids / hashes / collision suffixes third.
- If two anchors have the same full id and the same normalized locator object after normalization, deduplicate them.
- If two distinct normalized locator objects produce the same 8-hex hash for the same prefix after deduplication, append `-2`, `-3`, etc.
- Assign suffixes in deterministic order by serialized normalized locator object.
- Record a validation warning or score issue link if collision suffixing occurs, but do not drop either anchor.

Tests should monkeypatch the private locator-hash helper to force a collision; do not depend on finding a real SHA-256 collision.

### Step 10: Score Issue Linkage

Canonical score issue id format:

```text
issue:{score_run_id}:{fund_code}:{report_year}:{chapter_id}:{dimension}:{field_or_claim_hash}
```

`field_or_claim_hash` uses `sha256` first 8 lowercase hex over normalized `field_path` if present, otherwise `claim_id`, otherwise `contract_item_id`.

Projection rules:

- Context-supplied `ReportScoreIssueLink` records are attached to facts/gaps by matching `field_path`, `claim_id`, and `data_gap_refs`.
- A fact's `score_issue_ids` includes issue ids whose `field_path` matches the fact field path.
- A gap's `score_issue_ids` includes issue ids whose `data_gap_refs` contain the gap id.
- Bundle-level `quality_context.report_quality_score_refs` includes all issue ids.

Validation rules:

- Every `data_gap_refs` entry on a score issue must exist in `bundle.data_gaps`.
- Every `evidence_anchor_refs` entry that starts with `anchor:` must exist in `bundle.evidence_anchors`.
- `status="pass"` with blocking gap refs for the same field or claim is invalid.
- `status="N/A"` without `na_reason` or reviewer note is invalid.
- `dimension="chapter_summary"` is valid only with `status="skipped"`.

### Step 11: Derive `review_status`

Derive bundle-level status; do not let callers set it directly.

Priority order:

```text
rejected > expired > deferred > scoring_ready > fact_prefill_reviewed > fact_prefill_generated > repository_verified > candidate
```

Derive `rejected` if any condition holds:

- document identity is `mismatch`;
- source failure category is `schema_drift`, `identity_mismatch`, or `integrity_error`;
- fallback is used for a fail-closed category;
- extraction mode / value consistency has a hard contradiction such as `missing` with non-null value;
- an anchor id is invalid or a `data_gap_refs` / `score_issue_ids` reference is broken;
- preferred_lens resolution fails for a valid `FundType`;
- `accepted_baseline` is attempted before a curated-fixture gate.

Derive `expired` if `context.schema_revision_status == "expired"`.

Derive `deferred` if any condition holds and no higher-priority status applies:

- `source_failure_category == "unknown_upstream_failure_category"`;
- `classified_fund_type == "unknown"`;
- `type_slot_membership_status in {"type_gap", "taxonomy_pending", "unknown"}` for a baseline slot;
- any source boundary needed for scoring is `unknown` or `probe_only`;
- any blocking `ReportDataGap` remains for an applicable dimension;
- fact review is only `partially_reviewed`;
- `fq_gate_status == "block"` or `programmatic_audit_status == "block"` in quality context.

Derive `scoring_ready` only when all conditions hold:

- `corpus_id != "ad_hoc"`;
- document identity is `verified_annual_report`;
- source boundary is neither `unknown` nor `probe_only`;
- `source_failure_category == "none"`;
- `classified_fund_type != "unknown"`;
- `type_slot_membership_status == "matches_slot"`;
- fact review status is `reviewed`;
- preferred_lens projection covers chapters `chapter_0` to `chapter_7`;
- all value-domain and id-reference validations pass;
- no blocking data gaps remain for applicable scoring dimensions;
- no score issue with severity `blocking` remains unresolved.

Derive `fact_prefill_reviewed` when:

- facts and anchors were generated;
- fact review status is `reviewed`;
- explicit data gaps exist for unresolved fields;
- scoring-ready preconditions are not all met.

Derive `fact_prefill_generated` when:

- facts and anchors/gaps were generated from `StructuredFundDataBundle`;
- fact review status is `not_reviewed` or only generated facts exist.

Derive `repository_verified` when:

- document identity is `verified_annual_report`;
- projection produced no fact records because validation stopped before fact generation.

Derive `candidate` otherwise.

## Minimal Implementation Slice

The first code gate should implement only:

1. `fund_agent/fund/report_evidence.py`
   - domains;
   - frozen slotted dataclasses;
   - explicit projection context;
   - anchor/gap/issue id helpers;
   - projection from current `StructuredFundDataBundle`;
   - preferred_lens serializable projection;
   - review-status derivation and validation.
2. `tests/fund/test_report_evidence.py`
   - fake bundles and targeted unit tests.

Do not implement:

- JSONL scorer;
- durable baseline fixtures;
- chapter writer;
- renderer changes;
- FQ0-FQ6 behavior changes;
- `nav_data` source contract;
- broad derived calculations;
- `DerivedCalculation` population or calculation-specific validation beyond storing an explicitly supplied empty/default tuple;
- Host/Agent runtime;
- direct repository, PDF, cache, or network calls.

## Test Plan

Use fake bundle builders copied/adapted from `tests/fund/test_extraction_snapshot.py` and `tests/fund/test_golden_prefill.py`.

Required tests in `tests/fund/test_report_evidence.py`:

1. `test_projects_current_extracted_field_groups_to_report_facts`
   - Build a fake active-fund bundle with all current `ExtractedField` attributes.
   - Assert facts include all mapped field paths except `nav_data`.
   - Assert virtual `fact:fund_type.classified_fund_type` is present and reads `basic_identity.value["classified_fund_type"]`.

2. `test_preferred_lens_projection_is_serializable_and_covers_8_chapters`
   - Use `classified_fund_type="active_fund"`.
   - Assert chapters are `chapter_0` through `chapter_7`.
   - Assert values are plain immutable projection records, not live `TemplateLensRule` or `LensApplicationPlan` objects.

3. `test_missing_classified_fund_type_derives_unknown_and_gap`
   - Remove key from `basic_identity.value`.
   - Assert `classified_fund_type=="unknown"`.
   - Assert gap reason `classified_fund_type_missing`.
   - Assert review status is not `scoring_ready`.

4. `test_illegal_classified_fund_type_blocks_scoring_ready`
   - Use `classified_fund_type="money_market"`.
   - Assert a `type_slot_gap` with reason `classified_fund_type_invalid`.
   - Assert `scoring_ready` is impossible.

5. `test_type_slot_membership_status_distinguishes_matches_type_gap_taxonomy_pending`
   - Parametrize active/matching, active/index mismatch, and QDII classified in FOF slot.
   - Assert `matches_slot`, `type_gap`, and `taxonomy_pending`.

6. `test_multi_anchor_field_preserves_all_source_anchor_ids`
   - Build `holdings_snapshot` or `manager_strategy_text` with two anchors.
   - Assert the fact has both anchor ids and bundle has both anchors.

7. `test_anchor_id_hash_is_stable_for_same_locator`
   - Same anchor input twice produces identical id.
   - Whitespace normalization does not create a different id.

8. `test_anchor_id_collision_suffix_is_deterministic`
   - Monkeypatch private hash helper to return the same hash for two different locators.
   - Assert suffix `-2` / `-3` order is deterministic.

9. `test_extraction_mode_missing_produces_data_gap_ref`
   - Set `turnover_rate=ExtractedField(value=None, extraction_mode="missing")`.
   - Supply a `ReportDataGapOverride` for the S1 turnover gap.
   - Assert gap id `gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice`.
   - Assert the turnover fact references the gap id.

10. `test_extraction_mode_missing_with_non_null_value_rejects_bundle`
    - Construct invalid `ExtractedField(value={"x": 1}, extraction_mode="missing")`.
    - Assert projection returns a `ReportEvidenceBundle` with `review_status=="rejected"`.
    - Assert the rejected bundle carries a validation message or data gap explaining `missing` mode with non-null value.
    - Do not accept `ValueError` for this case unless the object construction is impossible before projection can inspect the field.

11. `test_direct_value_without_anchor_creates_traceability_gap`
    - Non-null direct fact with `anchors=()`.
    - Assert a `manual_review_required` or traceability gap exists and status is at most `deferred`.

12. `test_nav_data_is_excluded_from_initial_fact_projection`
    - Fake bundle includes `NavDataResult`.
    - Assert no fact has `field_path="nav_data"` and no fact has `category="nav"`.

13. `test_review_status_priority_rejected_before_deferred`
    - Combine fail-closed source category with unknown upstream category.
    - Assert `rejected`.

14. `test_unknown_upstream_failure_category_defers_not_scoring_ready`
    - Use otherwise clean facts and `source_failure_category="unknown_upstream_failure_category"`.
    - Assert `deferred`.

15. `test_scoring_ready_requires_non_ad_hoc_reviewed_verified_matching_bundle`
    - Use `corpus:rqb_s0:20260525`, verified annual report, `matches_slot`, reviewed facts, valid anchors, no blocking gaps.
    - Assert `scoring_ready`.

16. `test_ad_hoc_bundle_cannot_be_scoring_ready`
    - Same as prior but `corpus_id="ad_hoc"`.
    - Assert `fact_prefill_reviewed` or `fact_prefill_generated`, not `scoring_ready`.

17. `test_score_issue_links_validate_data_gap_refs`
    - Link an issue to a missing gap id.
    - Assert rejected bundle or `ValueError`.

18. `test_score_issue_pass_with_blocking_gap_is_invalid`
    - Create a pass score issue that references a blocking turnover gap.
    - Assert validation blocks scoring-ready.

19. `test_na_and_chapter_summary_score_semantics`
    - Assert `N/A` without `na_reason` is invalid.
    - Assert `chapter_summary` with non-`skipped` status is invalid.

20. `test_projection_does_not_call_repository_or_source_helpers`
    - Use monkeypatch to make `FundDocumentRepository`, source helpers, or PDF/cache helper constructors raise if called, or assert imports are absent with static `rg` in validation.
    - The projection must pass because it only consumes fake bundle and context.

21. `test_accepted_baseline_cannot_be_derived_or_forced`
    - Construct a bundle satisfying every `scoring_ready` precondition.
    - Assert the derived `review_status` is `scoring_ready`, not `accepted_baseline`.
    - Construct a context with `attempted_review_status="accepted_baseline"`.
    - Assert projection rejects or blocks the attempt before curated-fixture gate, preferably by returning a `rejected` bundle with a validation message; fail-fast `ValueError` is acceptable only during context validation before bundle construction.

Coverage target: the new module should meet at least 80% line coverage in the focused test command. If helper branches for future score/calculation records are not fully covered, record the exact uncovered branch and owner before implementation acceptance.

## Validation Commands for Future Implementation

Run after source/tests are added:

```text
python -m pytest tests/fund/test_report_evidence.py
python -m pytest --cov=fund_agent.fund.report_evidence --cov-report=term-missing tests/fund/test_report_evidence.py
python -m pytest tests/fund/test_report_evidence.py tests/fund/template/test_lens_application.py tests/fund/test_extraction_snapshot.py
python -m ruff check fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py
rg -n "extra_payload|extra_payloads|dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|download|cache_path|\\.pdf" fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py
git diff --check
```

Expected validation behavior:

- `pytest` passes.
- Coverage for `fund_agent.fund.report_evidence` is at least 80%, or residual is explicitly accepted.
- `ruff` passes.
- `rg` may match boundary terms inside docstrings or negative-test names, but must not show imports or operational calls to repository/source/PDF/cache helpers in production code.
- `git diff --check` passes.

## Boundaries and Stop Conditions

Stop and return to controller if implementation needs any of the following:

1. Direct PDF, cache, source helper, downloader, or file-system annual-report access.
2. Calling `FundDocumentRepository` from the projection layer instead of consuming an already-created `StructuredFundDataBundle`.
3. A new extraction path parallel to `FundDataExtractor`.
4. A business parameter hidden in `extra_payload`, `extra_payloads`, `**kwargs`, or a free dict.
5. Renderer or current v0 8-chapter output changes.
6. FQ0-FQ6 quality gate behavior changes.
7. Promotion of ignored `reports/scoring-runs/` outputs or any curated fixture.
8. Durable baseline selection or `accepted_baseline` derivation.
9. `nav_data` facts before a later `nav_data` source-contract slice.
10. Creation of `fund_agent/host` or `fund_agent/agent`.
11. Importing or introducing `dayu.host` / `dayu.engine`.
12. Treating `schema_drift`, `identity_mismatch`, or `integrity_error` as fallback-eligible.
13. Treating active-fund Chapter 3 turnover/style-stability as automatic extraction work instead of explicit data-gap / wording constraint first.

## Residual Risks

| Residual | Risk | Owner / next handling |
|---|---|---|
| `nav_data` excluded | NAV time series facts remain unavailable to report-evidence facts | Future `nav_data` source-contract slice defines source, period, anchor, unit, and mapping. |
| Manual review remains Markdown-backed | Machine validation cannot fully prove reviewed rows | Keep Markdown review refs for this gate; curated JSON fixture gate decides promotion later. |
| `external_official` is metadata only | Future implementer might confuse it with permission for ad hoc network calls | Keep validation and tests blocking `external_official` as sole annual-report source boundary. |
| `accepted_baseline` domain exists but is not derivable | Future code might accidentally promote baseline | Add explicit test that first slice rejects or never derives `accepted_baseline`. |
| `DerivedCalculation` population deferred | Calculation records exist as shape only and may not be covered by population tests | Keep `derived_calculations=()` in first slice; later calculation-source gate owns population and branch coverage. |
| FOF pure coverage still missing | Baseline cannot claim full fund-type coverage | Fund-type taxonomy / corpus second pass gate. |
| Fallback category still unknown for `110020`, `017641`, `017970` | These candidates cannot be scoring-ready | Source reliability gate recovers category or excludes them. |
| README sync may be required after code | `AGENTS.md` says `fund_agent/fund/` code changes trigger `fund_agent/fund/README.md` update | Controller should include a minimal README sync in the implementation gate or record a doc-sync residual if source-only gate is intentionally narrower. |

## Next Recommended Gate

Proceed to independent plan review for this artifact. If accepted, the next gate should authorize the narrow implementation slice:

```text
fund_agent/fund/report_evidence.py
tests/fund/test_report_evidence.py
```

Recommended follow-up after implementation review passes: a code review / re-review gate focused on immutable model correctness, projection traceability, invalid-combination handling, and boundary compliance. Do not proceed directly to renderer, scoring JSONL validation, durable fixture promotion, or chapter writing until this typed bundle projection is accepted.

## Validation for This Artifact

Commands to run after writing this plan:

```text
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|fund_agent/fund/report_evidence.py|frozen|type_slot_membership_status|source_boundary|source_failure_category|review_status|data_gap_refs|sha256|nav_data|FundDocumentRepository|extra_payload|dayu\\.host|dayu\\.engine|renderer|FQ0-FQ6" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
git diff --check
```

Expected result: both pass. No `pytest`, `ruff`, renderer, quality-gate, source, or fixture validation is required for this artifact-only planning gate.
