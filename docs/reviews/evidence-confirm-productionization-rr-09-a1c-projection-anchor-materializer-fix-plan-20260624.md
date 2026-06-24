# RR-09 A1-C Projection / Anchor Locator / Reference Materializer Fix Plan

Verdict: `RR_09_A1C_FIX_PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

This is a no-live planning gate for RR-09 A1-C. It converts the accepted A1 R1-R4 fact diagnostic into an implementation-ready fix plan.

In scope:

- Fix the repository-bounded annual-report Evidence Confirm materializer path that turns projection anchors into `EvidenceConfirmReference`.
- Preserve source/PDF access through `FundDocumentRepository` and existing repository-bounded runner only.
- Preserve V2 hard-gate semantics: `missing_evidence` / `source_support` must pass only after a real annual-report excerpt is materialized.
- Preserve precision honesty: semantic row locators that degrade to table/section references must not be reported as row-precise.

Out of scope:

- No live/PDF re-evidence in this plan gate.
- No provider, LLM, semantic entailment, checklist support, report-body rendering, tag, release or readiness promotion.
- No quality-gate threshold change.
- No broad extractor rewrite across all `row_locator` producers.
- No direct PDF/cache/source-helper access outside `FundDocumentRepository`.

## 2. Accepted Input

Accepted A1 fact diagnostic:

- Artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a1-fact-diagnostic-evidence-20260624.md`
- Controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a1-controller-judgment-20260624.md`
- Accepted classification: R1-R4 source provenance is admitted, but repository-bounded Evidence Confirm fails because projection anchors do not materialize proof references.
- Dominant root cause: `projection_attachment_defect`, not source/PDF pathway failure and not proven value-match false positive.

A1 R1-R4 observed issue shape:

| Sample | Source/pathway | Reference count | Dominant materializer issues | V2 failed dimensions |
|---|---:|---:|---|---|
| R1 `004393 / 2025` | EID single-source admitted | 0 | `unsupported_row_locator_format=122`, `row_locator_without_table_id=22`, `anchor_not_applicable=2` | `missing_evidence=34`, `source_support=34` |
| R2 `004194 / 2024` | EID single-source admitted | 0 | `unsupported_row_locator_format=122`, `row_locator_without_table_id=22`, `anchor_not_applicable=2` | `missing_evidence=35`, `source_support=35` |
| R3 `006597 / 2024` | EID single-source admitted | 0 | `unsupported_row_locator_format=110`, `row_locator_without_table_id=22`, `anchor_not_applicable=2` | `missing_evidence=32`, `source_support=29` |
| R4 `110020 / 2024` | EID single-source admitted | 0 | `unsupported_row_locator_format=129`, `row_locator_without_table_id=29`, `anchor_not_applicable=2` | `missing_evidence=39`, `source_support=39` |

## 3. Current Code Facts

`fund_agent/fund/evidence_confirm_sources.py` currently:

- accepts only `table_id="page-{page_number}-table-{table_index}"`;
- accepts only `row_locator="row-{zero_based_index}"`;
- blocks any anchor with `row_locator` but no `table_id` as `row_locator_without_table_id`;
- blocks semantic row locators on compatible tables as `unsupported_row_locator_format`;
- computes repository status as fail when build status is fail or V2 is not pass;
- computes pathway status as pass only when source provenance is admitted, references exist, and V2 is pass or only E1 `anchor_precision` warn;
- intentionally allows `result.status="fail"` while `pathway_status="pass"` for the accepted section-only / E1 precision warning shape; therefore A1-C acceptance must key EC-P2 pathway proof on `pathway_status`, not strict runner `status`.

`fund_agent/fund/evidence_confirm.py` currently:

- passes `source_support` and `missing_evidence` when a proof reference exists for the fact anchor;
- treats E1 `anchor_precision` as reviewable warn;
- does not currently warn when an anchor declares `row_locator` but the materialized reference is deliberately downgraded to table/section scope, because `_precision_issue()` only checks whether the reference itself has enough locator fields.

Extractor/projection facts:

- Existing extractors emit many semantic row locators such as field names, role locators, row labels, `row:{index}:{label}`, `line:{index}` and prose locator strings.
- Some semantic locators include compatible `table_id`; others are section/prose anchors without table ids.
- Rewriting every extractor to emit row-N locators is broader than the A1-C defect and would mix reference materialization with extractor semantics.

## 4. Design Decision

Implement a bounded coarse-reference fallback in the annual-report materializer, plus an explicit V2 precision warning for anchor-to-reference locator downgrades.

Do not relax V2 thresholds. Do not mark semantic row locators as row-precise. The fix should convert the current zero-reference failure into:

- proof references for source-support and missing-evidence checks;
- E1 reviewable warnings when an anchor promised row-level semantics but the materializer can only provide table or section scope;
- blocking failure for still-unsafe or ambiguous locators.

If V2 returns only E1 `anchor_precision` warnings after the fix, `run_repository_bounded_evidence_confirm()` may still return `status="fail"` by strict aggregate status. That is acceptable only when `pathway_status="pass"` and `pathway_warning_reasons` records the accepted precision-warning reason.

## 5. Locator Handling Matrix

| Anchor shape | Planned materializer behavior | Planned V2 behavior |
|---|---|---|
| Annual-report anchor with compatible `table_id`, no `row_locator` | Existing table excerpt | pass if value/source checks pass |
| Annual-report anchor with compatible `table_id` and `row-N` | Existing row excerpt | pass if value/source checks pass |
| Annual-report anchor with compatible `table_id` and unsupported semantic `row_locator` | New informational issue, materialize table-level excerpt with `row_locator=None` | E1 `anchor_precision` warn because row locator was degraded; `missing_evidence` / `source_support` can pass |
| Annual-report anchor with no `table_id`, semantic `row_locator`, and valid `section_id` | New informational issue, materialize section-level excerpt with `table_id=None`, `row_locator=None` | E1 `anchor_precision` warn because row locator was degraded; `missing_evidence` / `source_support` can pass |
| Unsupported `table_id` format | Existing blocking failure | fail |
| Table id not found, duplicate table, page/table mismatch, row-N out of range | Existing blocking failure | fail |
| Missing/invalid section, wrong fund/year, source-truth admission failure | Existing blocking failure | fail |
| Non-annual anchors such as external API or derived anchors | Existing not-applicable handling | not applicable |

## 6. Implementation Plan

1. Update `fund_agent/fund/evidence_confirm_sources.py`.
   - Add helper logic for degraded table/section excerpts.
   - For unsupported semantic row locator with compatible table id, return the table excerpt plus an informational build issue such as `semantic_row_locator_degraded_to_table_excerpt`.
   - For row locator without table id but valid section id, return the section excerpt plus an informational build issue such as `semantic_row_locator_degraded_to_section_excerpt`.
   - Preserve all existing blocking outcomes for invalid source truth, invalid section, unsupported table id, unresolved table, duplicate table, page mismatch and row-N out-of-range.

2. Update `fund_agent/fund/evidence_confirm.py`.
   - Extend `_precision_issue()` or its call path so V2 can detect locator downgrade by comparing the declared anchor shape with the materialized reference shape.
   - Required behavior: if the original anchor has `row_locator` but the proof reference has no `row_locator`, emit E1 reviewable `anchor_precision` warning.
   - Preserve existing pass behavior for true row-N references and existing reviewable warnings for empty or under-located annual-report excerpts.

3. Add focused tests in `tests/fund/test_evidence_confirm_sources.py` and, if needed, `tests/fund/test_evidence_confirm.py`.
   - Cover table-level degradation for compatible `table_id` plus semantic row locator.
   - Cover section-level degradation for row locator without table id.
   - Cover V2 E1 warn on degraded row locator while `missing_evidence` and `source_support` pass.
   - Cover blocking retention for unsupported table id and row-N out-of-range.

4. Update `fund_agent/fund/README.md` only if the public developer-facing materializer behavior changes enough that current docs become stale.
   - If README does not describe row locator materialization semantics, no README update is required.

## 7. Test Matrix

Required no-live validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py -q --tb=short
uv run pytest tests/services/test_fund_analysis_service.py tests/services/test_quality_gate_service.py -q --tb=short
uv run ruff check fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py
git diff --check
```

Post-implementation live/PDF re-evidence:

- R1-R4 repository-bounded re-evidence remains required before release/readiness.
- That re-evidence must be a separate explicitly authorized live/PDF gate.
- B1 `017641 / 2024` runtime product CLI re-evidence remains separate and still requires explicit live/PDF authorization.

## 8. Acceptance Criteria

Implementation can be accepted only if:

- unsupported semantic row locators no longer produce zero references when a safe table or section excerpt is available;
- source/PDF provenance admission remains unchanged and fail-closed;
- `missing_evidence` and `source_support` no longer fail solely because semantic row locators are not row-N;
- row locator downgrades produce reviewable E1 precision warnings instead of silent pass;
- repository-bounded re-evidence distinguishes strict aggregate `status` from EC-P2 `pathway_status`, accepting a strict fail only for the already documented all-E1 precision warning shape;
- no direct PDF/cache/source-helper access is introduced outside the repository boundary;
- no quality-gate threshold, report-body, checklist, provider, LLM, tag, release or readiness behavior changes are made.

## 9. Residuals

- R1-R4 remain release-blocking until the targeted fix is implemented, reviewed and re-evidenced against live repository-loaded annual reports.
- B1 `017641 / 2024` remains open for runtime product CLI re-evidence after explicit live/PDF authorization.
- Checklist support, report-body rendering, provider-backed semantic production default, tag/release and release/readiness promotion remain separate gates.
- Release/readiness remains `NOT_READY`.
