# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Review — MiMo

> Date: 2026-05-25
> Reviewer: AgentMiMo (independent code review)
> Gate: `typed ReportEvidenceBundle model/projection implementation`
> Scope: `fund_agent/fund/report_evidence.py`, `tests/fund/test_report_evidence.py`, `fund_agent/fund/README.md` minimal sync
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Plan reference: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`
> Controller judgment: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-controller-judgment-20260525.md`

## Conclusion

**PASS_WITH_FINDINGS**

Implementation is correct, boundary-compliant, and well-tested. No blocking issues. Two minor findings and documented residual risks.

## Validation Commands Run

| Command | Result |
|---------|--------|
| `pytest tests/fund/test_report_evidence.py -v` | 23/23 passed |
| `pytest --cov=fund_agent.fund.report_evidence --cov-report=term-missing tests/fund/test_report_evidence.py` | 93% coverage (target ≥80%) |
| `pytest tests/fund/test_report_evidence.py tests/fund/template/test_lens_application.py tests/fund/test_extraction_snapshot.py` | 40/40 passed |
| `ruff check fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py` | All checks passed |
| `rg -n "extra_payload\|...\|FundDocumentRepository\|...\|\.pdf" report_evidence.py test_report_evidence.py` | Only matches negative-test assertion strings |
| `git diff --check` | Clean |

## Scope Compliance

### Accepted boundaries respected

| Boundary | Status | Evidence |
|----------|--------|----------|
| Frozen slotted dataclasses | PASS | All 14 dataclasses use `@dataclass(frozen=True, slots=True)` |
| Literal domains | PASS | All 25+ Literal type aliases match plan spec exactly |
| Explicit `ReportEvidenceProjectionContext` | PASS | No `extra_payload`, `**kwargs`, or free dict |
| Deterministic ids | PASS | `build_gap_id`, `build_score_issue_id`, anchor hash with sha256[:8] |
| `project_report_evidence_bundle(bundle, context)` signature | PASS | Consumes `StructuredFundDataBundle` + explicit context |
| `preferred_lens` serializable projection | PASS | `ReportPreferredLensProjection` / `ReportPreferredLensChapter` frozen dataclasses |
| `data_gap_refs` / `score_issue_ids` consistency | PASS | Validation rejects missing gap refs, pass-with-blocking-gap, N/A without reason |
| Derived `review_status` | PASS | Priority: rejected > expired > deferred > scoring_ready > ... |
| `accepted_baseline` blocked | PASS | `ValueError` on `attempted_review_status="accepted_baseline"` |
| `nav_data` excluded from facts | PASS | Negative test confirms no `field_path="nav_data"` or `category="nav"` facts |
| `DerivedCalculation` shape only | PASS | `derived_calculations=()` default, no population logic |
| No repository/PDF/cache/source calls | PASS | Static `rg` check clean; test asserts no repository names in module |
| No renderer/FQ0-FQ6 changes | PASS | Module does not import or call renderer or quality gate |
| No Host/Agent/dayu imports | PASS | No `dayu.host` or `dayu.engine` references |
| `fund_code`/`report_year` from bundle, not context | PASS | Read from `bundle.fund_code` / `bundle.report_year` |
| Fail-closed source categories | PASS | `schema_drift`/`identity_mismatch`/`integrity_error` → rejected when `fallback_used=True` |

### Value domain alignment with S2 plan

All `Literal` domains match the accepted S2 bundle candidate plan and implementation plan:

- `ClassifiedFundType = FundType | Literal["unknown"]`
- `TypeSlotMembershipStatus`: matches_slot / type_gap / taxonomy_pending / unknown / not_applicable
- `SourceFailureCategory`: none / not_found / unavailable / schema_drift / identity_mismatch / integrity_error / unknown_upstream_failure_category
- `ReviewStatus`: candidate through accepted_baseline, plus rejected / deferred / expired
- `GapKind`, `GapFailureCategory`, `DataGapReasonCode`, `ChapterRef`, `ScoreDimension`, `ScoreRecordStatus`, etc.: all match plan

### Field projection alignment

`_FIELD_SPECS` covers exactly the 14 fields specified in the plan Step 5 table, in the same order. `classified_fund_type` is correctly handled as a virtual fact outside `_FIELD_SPECS` via `_project_classified_fund_type_fact`.

### Anchor id format

Format: `anchor:{fund_code}:{report_year}:{source_kind}:{section_or_source}:{locator_hash}` — matches plan Step 9. Section sanitization, locator normalization, sha256[:8] hash, and deterministic collision suffixing are all implemented correctly.

### Review status state machine

The derivation function follows plan Step 11 priority order exactly:

1. `rejected` if hard_rejected, document identity mismatch, or fail-closed source failure
2. `expired` if schema revision status is expired
3. `deferred` if unknown upstream, unknown fund type, type slot mismatch, blocking gaps, etc.
4. `scoring_ready` only when all conditions met (non-ad_hoc, verified, matches_slot, reviewed, etc.)
5. `fact_prefill_reviewed` / `fact_prefill_generated` / `repository_verified` / `candidate` fallback chain

## Findings

### F1 — Minor: No test for `expired` schema revision status

**Severity**: minor
**Location**: `tests/fund/test_report_evidence.py` (test gap)
**Description**: The plan lists `expired` as a derived status when `context.schema_revision_status == "expired"`. The implementation correctly handles this at line 854 (`if context.schema_revision_status == "expired": return "expired"`), but no test covers this path.
**Impact**: The branch is uncovered (line 854 in coverage report). Functionality is correct; coverage gap only.
**Recommendation**: Add a test with `schema_revision_status="expired"` asserting `review_status=="expired"`.

### F2 — Minor: `turnover_rate` field path normalization creates minor asymmetry with data gap override

**Severity**: minor
**Location**: `fund_agent/fund/report_evidence.py:1750-1752` (`_normalize_override_field_path`)
**Description**: The `turnover_rate` field spec uses `field_path="turnover_rate"` (line 270), but `_normalize_override_field_path` converts `turnover_rate` to `manager.turnover_rate` for gap records. The `_gap_matches_fact` function handles this via `endswith` matching (line 1846), so gap-to-fact linkage works correctly. However, this creates a minor asymmetry where the fact's `field_path` is `turnover_rate` while the gap's `field_path` is `manager.turnover_rate`.
**Impact**: No functional impact — gap refs attach correctly. The asymmetry is intentional per S2 design (override field paths use category-qualified form). Test `test_extraction_mode_missing_produces_data_gap_ref` validates the correct gap id and fact linkage.
**Recommendation**: No action required. Document as design note if future consumers need clarity.

## Uncovered Branches (Residual)

Coverage is 93%. The 44 uncovered lines are edge-case and error-handling paths:

| Lines | Description | Risk | Owner |
|-------|-------------|------|-------|
| 854 | `expired` schema revision branch | Low — simple condition | F1 above |
| 873-877 | `repository_verified` / `candidate` fallback in review status | Low — fallback chain end | Future test expansion |
| 938 | `build_score_issue_id` ValueError when all target fields None | Low — caller contract | Future test expansion |
| 957-969 | `_validate_projection_context` error branches (empty run_id, corpus_id, etc.) | Low — defensive validation | Future test expansion |
| 1200-1201, 1211-1213 | `_project_preferred_lens` ValueError and chapter_id out-of-range | Low — template contract consistency | Future test expansion |
| 1370-1372 | `_map_anchor_source` derived branch | Low — third source kind | Future test expansion |
| 1443-1455 | `_project_extracted_field_fact` direct/derived/estimated with None value | Low — defensive gap creation | Future test expansion |
| 1472-1475 | `not_applicable` extraction mode branch | Low — future mode | Future test expansion |
| 1569, 1752, 1770-1774 | `_coerce_extraction_mode` unknown mode, override path helpers | Low — edge helpers | Future test expansion |
| 1950-1960 | Score issue validation: missing anchor refs, severity check | Low — defensive checks | Future test expansion |
| 2045-2049 | Deferred condition: `partially_reviewed`, fq/audit block | Low — additional defer reasons | Future test expansion |
| 2127-2130 | `_validate_chapter_refs` empty/invalid chapter_ids | Low — defensive validation | Future test expansion |

All uncovered branches are error-handling or edge-case paths. No production logic gaps.

## README Sync Assessment

`fund_agent/fund/README.md` minimal sync is correct:

- `report_evidence.py` added to internal layering section with accurate description
- `project_report_evidence_bundle()` documented in current implementation section with correct boundary claims
- No overclaiming: correctly states `nav_data` excluded, `accepted_baseline` blocked, `DerivedCalculation` shape-only, no repository/PDF/cache calls
- No old terminology, stale paths, or architecture drift detected
- Document scope stays within `fund_agent/fund/README.md` boundaries (development manual for Fund package)

## Adversarial Checks

| Check | Result |
|-------|--------|
| Can `accepted_baseline` be derived through any code path? | No — `_is_scoring_ready` does not check for it; `derive_report_evidence_review_status` never returns it; `ValueError` on explicit attempt |
| Can `nav_data` leak into facts? | No — not in `_FIELD_SPECS`; negative test confirms |
| Can `extra_payload` sneak in? | No — `ReportEvidenceProjectionContext` has explicit typed fields only; no `**kwargs` or free dict |
| Can a caller bypass review_status derivation? | No — `ReportEvidenceBundle.review_status` is set only by `derive_report_evidence_review_status` inside `project_report_evidence_bundle` |
| Can fail-closed source failures get fallback? | No — `_validate_projection_context` raises `ValueError`; `_has_rejected_condition` returns True |
| Can `external_official` be sole source boundary? | No — `_validate_projection_context` raises `ValueError` |
| Can unknown `FundType` bypass type slot check? | No — `_read_classified_fund_type` checks against `_SUPPORTED_FUND_TYPES` |
| Can score issue pass status reference blocking gap? | No — `_validate_score_issue_links` detects and rejects |
| Can N/A score status lack reason? | No — validation checks `na_reason` or `reviewer_note` |
| Is `chapter_summary` dimension properly constrained? | Yes — only valid with `skipped` status; `skipped` only valid for `chapter_summary` |

## Remaining Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| `nav_data` facts unavailable to report evidence | Low | Future `nav_data` source-contract slice |
| Manual review backed by Markdown only | Low | Keep Markdown refs for this gate; curated JSON fixture gate decides later |
| `external_official` is metadata only | Low | Validation blocks it as sole source; test confirms |
| `DerivedCalculation` population deferred | Low | Shape defined; `derived_calculations=()` default; later calculation gate |
| FOF pure corpus coverage missing | Low | Fund-type taxonomy gate |
| Fallback category unknown for `110020`, `017641`, `017970` | Low | Source reliability gate |
| `expired` schema revision untested | Very Low | F1 above; simple condition, correct implementation |

## Summary

The implementation correctly and completely follows the accepted plan. All 23 tests pass with 93% coverage. Boundary checks confirm no prohibited imports or calls. The README sync is minimal and accurate. Two minor findings (F1: untested `expired` branch, F2: field path normalization asymmetry) are non-blocking. The `ReportEvidenceBundle` typed model/projection is ready for the next gate.
