# Re-review: Fund-layer CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit

> Date: 2026-05-26
> Reviewer: second independent code re-reviewer
> Scope: repaired implementation after GLM/MiMo FAIL reviews
> Verdict: FAIL

## Scope Reviewed

- `fund_agent/fund/report_writing_audit.py`
- `fund_agent/fund/template/chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- Prior review artifacts:
  - `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md`
  - `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md`

## Accepted Findings Closure Status

- Closed: compatible `data_gap` with no positive claim now still requires insufficient-evidence wording / next minimum validation question.
  - Evidence: `_audit_active_chapter_3_turnover_requirement()` emits `insufficient_evidence_wording_missing` whenever a compatible gap exists but `_drafts_preserve_required_wording()` fails, independent of `stability_claim` (`fund_agent/fund/report_writing_audit.py:349-388`).
  - Test: `test_active_chapter_3_data_gap_missing_wording_emits_issue()` (`tests/fund/test_report_writing_audit.py:276-303`).
- Mostly closed: fully dangling `source_anchor_ids` no longer satisfy the requirement.
  - Evidence: `_find_satisfying_fact()` builds `existing_anchor_ids` and rejects facts with no intersection (`fund_agent/fund/report_writing_audit.py:637-649`).
  - Test: `test_fact_with_dangling_anchor_does_not_satisfy_requirement()` (`tests/fund/test_report_writing_audit.py:335-360`).
  - Remaining blocker below: mixed valid + dangling anchor ids still pass.
- Closed: malformed records `report_year` returns blocking `invalid_audit_input` and `failed_closed=True` instead of raising.
  - Evidence: `_coerce_report_year()` catches `TypeError` / `ValueError` and returns a blocking issue (`fund_agent/fund/report_writing_audit.py:1140-1167`).
  - Test: `test_malformed_records_report_year_fails_closed()` (`tests/fund/test_report_writing_audit.py:363-388`).
- Closed: conflicting explicit Chapter 3 `fund_type_slot` now returns blocking `input_conflict` and `failed_closed=True`.
  - Evidence: `_resolve_chapter_fund_type_slot()` detects multiple explicit non-default / non-unknown slots (`fund_agent/fund/report_writing_audit.py:1015-1034`).
  - Test: `test_conflicting_explicit_chapter_3_fund_type_slots_fail_closed()` (`tests/fund/test_report_writing_audit.py:391-422`).
- Closed: records `data_gap` missing explicit `reason_code`, `field_path`, or required wording no longer satisfies requirement.
  - Evidence: `_gap_from_mapping()` requires all compatibility-bearing fields before constructing `ReportDataGap` (`fund_agent/fund/report_writing_audit.py:557-573`).
  - Test: `test_records_data_gap_missing_reason_or_field_path_fails_closed()` (`tests/fund/test_report_writing_audit.py:425-472`).
- Closed: boundary grep found no renderer, FQ0-FQ6, Service/CLI, `FundDocumentRepository`, PDF/cache/source/extractor, Host/Agent/dayu references in the implementation or focused tests.

## Findings

### Major: a fact with mixed valid and dangling anchor ids still satisfies `required_evidence`

- Location: `fund_agent/fund/report_writing_audit.py:637-649`
- Evidence: `_find_satisfying_fact()` accepts a reviewed fact when `set(fact.source_anchor_ids).intersection(existing_anchor_ids)` is non-empty. That means a fact with `("anchor:turnover", "anchor:missing")` satisfies active Chapter 3 even though one claimed source anchor is dangling.
- Reproduction:

```bash
uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_bundle, ChapterDraftSurrogate; from tests.fund.test_report_writing_audit import _bundle, _turnover_fact; r=audit_report_writing_bundle(_bundle(facts=(_turnover_fact(source_anchor_ids=('anchor:turnover','anchor:missing')),)), chapter_drafts=(ChapterDraftSurrogate(chapter_id=3,fund_type_slot='active_fund',markdown='年报已复核换手率。'),)); print(r.failed_closed, r.summary); print([(i.failure_category, i.severity) for i in r.issues])"
```

Observed:

```text
False ReportWritingAuditSummary(issue_count=0, blocking_count=0, material_count=0, minor_count=0, informational_count=0, failure_category_counts=(), evidence_requirement_gap_count=0)
[]
```

Impact:

The accepted review finding was that dangling `source_anchor_ids` must not satisfy evidence requirements. The current check proves only that at least one referenced anchor exists, not that the fact's declared evidence references are internally valid. A malformed fact can therefore carry unresolved anchors and still produce a clean audit pass, weakening the evidence-anchor sidecar semantics this gate is meant to make executable.

Recommendation:

Require all `fact.source_anchor_ids` to resolve to existing `bundle.evidence_anchors` before a fact can satisfy `required_evidence`, or emit a dedicated blocking/material anchor-integrity issue and treat the evidence requirement as unsatisfied. Add a focused mixed-anchor test with one valid and one dangling anchor id.

## Challenged Points

- Records helper fail-closed behavior for all `data_gaps`: over-strict but acceptable for this slice. `_gap_from_mapping()` currently rejects any gap record lacking active Chapter 3 compatibility fields. That can false-block unrelated data gaps, but the helper is explicitly dev-only, this gate only supports the active Chapter 3 slice, and fail-closed is safer than silently treating incomplete records as compatible evidence. Documenting this as a first-slice limitation is sufficient unless records mode is broadened.
- `input_conflict` vs forbidden-content ordering: acceptable. `audit_report_writing_bundle()` adds input conflict issues, still runs `_audit_forbidden_content()`, and only skips the active Chapter 3 evidence requirement when input issues exist (`fund_agent/fund/report_writing_audit.py:189-206`). A targeted reproduction with conflicting slots plus `建议买入` returned both `input_conflict` and `forbidden_content`.
- Fact anchor check "all anchors" vs "any anchor": not acceptable as implemented; see Major finding.
- New failure categories stability: acceptable. `invalid_audit_input` and `input_conflict` are part of the stable `FailureCategory` literal in the sidecar (`fund_agent/fund/template/chapter_contract_constraints.py:29-39`) and are used deterministically.
- Duplicate `issue_id` occurrences from the prior review remain a deferred residual risk, not a new blocker for this re-review, because the controller explicitly deferred occurrence uniqueness.

## Commands Run

```bash
git status --short
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md
rg -n "def |class |FailureCategory|input_conflict|failed_closed|data_gap|source_anchor|anchor|forbidden|must_not|report_year|fund_type_slot" fund_agent/fund/report_writing_audit.py
rg -n "def |class |RequirementSeverity|chapter_3|turnover|source_anchor|required_evidence|must_not|failure" fund_agent/fund/template/chapter_contract_constraints.py
rg -n "data_gap|source_anchor|report_year|input_conflict|fund_type_slot|must_not|valid minimal|forbidden|failed_closed" tests/fund/test_report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|quality_gate_policy|FQ0|FQ6|renderer|FundAnalysisService|extra_payload|pdf|cache|extractor" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
git diff --no-index --check /dev/null fund_agent/fund/report_writing_audit.py
git diff --no-index --check /dev/null fund_agent/fund/template/chapter_contract_constraints.py
```

Focused tests passed:

```text
18 passed in 0.49s
```

Ruff passed:

```text
All checks passed!
```

Boundary grep returned no matches. `git diff --no-index --check` printed no whitespace errors; exit code `1` is expected for `/dev/null` comparisons against new files.

## Residual Risks

- Per-file coverage remains unverified in this re-review.
- Phrase matching remains intentionally narrow and should not be treated as natural-language coverage beyond the active Chapter 3 first slice.
- Records mode is fail-closed for unsupported gap records. This is acceptable while scoped to active Chapter 3, but should be revisited before records mode is used for broader chapter audit ingestion.
