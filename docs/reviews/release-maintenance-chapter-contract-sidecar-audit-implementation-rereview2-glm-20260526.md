# Re-review 2: Fund-layer CHAPTER_CONTRACT Sidecar Fix2

> Date: 2026-05-26
> Reviewer: second independent code re-reviewer
> Scope: targeted Fix2 verification for mixed valid + dangling anchor ids
> Verdict: PASS

## Scope Reviewed

- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/test_report_writing_audit.py`
- Prior finding artifact:
  - `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-rereview-glm-20260526.md`

## Finding Closure

### Closed: mixed valid + dangling anchor ids no longer satisfy `required_evidence`

- Prior issue: `_find_satisfying_fact()` accepted a fact when `source_anchor_ids` had any intersection with `bundle.evidence_anchors`, so `("anchor:turnover", "anchor:missing")` could satisfy the active Chapter 3 turnover requirement.
- Current evidence: `_find_satisfying_fact()` now builds `existing_anchor_ids`, rejects empty `fact.source_anchor_ids`, and requires `fact_anchor_ids.issubset(existing_anchor_ids)` before returning the fact.
- Location: `fund_agent/fund/report_writing_audit.py:638-652`

This closes the exact data-path defect: every source anchor declared by a fact must resolve to an anchor in `bundle.evidence_anchors`; a mixed valid + dangling anchor set is treated as unsatisfied evidence.

## Test Evidence

- Mixed-anchor regression exists:
  - `tests/fund/test_report_writing_audit.py:363`
  - Uses `source_anchor_ids=("anchor:turnover", "anchor:missing")`.
  - Asserts `required_evidence_missing` is emitted.
- Valid minimal case still exists and passes:
  - `tests/fund/test_report_writing_audit.py:152`
  - Uses the default valid turnover fact and asserts no issues.

## Commands Run

```bash
rg -n "def _find_satisfying_fact|source_anchor_ids|evidence_anchors|required_evidence" fund_agent/fund/report_writing_audit.py tests/fund/test_report_writing_audit.py
sed -n '600,670p' fund_agent/fund/report_writing_audit.py
sed -n '320,400p' tests/fund/test_report_writing_audit.py
sed -n '140,180p' tests/fund/test_report_writing_audit.py
uv run pytest tests/fund/test_report_writing_audit.py::test_fact_with_mixed_valid_and_dangling_anchors_does_not_satisfy_requirement tests/fund/test_report_writing_audit.py::test_valid_minimal_active_chapter_3_case
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
uv run ruff check fund_agent/fund/report_writing_audit.py tests/fund/test_report_writing_audit.py
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|quality_gate_policy|FQ0|FQ6|renderer|FundAnalysisService|extra_payload|pdf|cache|extractor" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Focused results:

- Mixed-anchor + valid-minimal pytest: `2 passed`
- Focused sidecar/audit pytest: `19 passed`
- Ruff: `All checks passed`
- Boundary grep: no forbidden production-chain import/call matches

## Residual Risks

- No residual blocker for the targeted Fix2 finding.
- This review did not re-open broader coverage or duplicate issue occurrence uniqueness topics; those remain outside the targeted Fix2 scope.
