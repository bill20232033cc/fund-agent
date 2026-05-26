# Code Re-review: CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit

> Date: 2026-05-26
> Reviewer: independent code re-reviewer
> Scope: repaired untracked implementation for Fund-layer executable CHAPTER_CONTRACT sidecar and dev-only report-writing audit
> Verdict: PASS

## Scope Reviewed

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md`

This re-review did not modify implementation or tests, did not run `git add` / `git commit`, and did not perform GitHub mutation.

## Accepted Finding Closure

### Closed: compatible `data_gap` now requires insufficient-evidence wording without a positive claim

Evidence:

- `fund_agent/fund/report_writing_audit.py` now checks `_drafts_preserve_required_wording(...)` whenever a compatible active Chapter 3 `data_gap` is used and no satisfying fact exists.
- `tests/fund/test_report_writing_audit.py::test_active_chapter_3_data_gap_missing_wording_emits_issue` covers the no-positive-claim case.
- Targeted reproduction returned `insufficient_evidence_wording_missing` for a Chapter 3 draft that only says it describes manager background.

Result:

```text
('data_gap_missing_wording_no_claim', False, ['insufficient_evidence_wording_missing'])
```

### Closed: dangling `source_anchor_ids` no longer satisfy evidence requirement

Evidence:

- `_find_satisfying_fact(...)` builds `existing_anchor_ids` from `bundle.evidence_anchors` and requires an intersection with each reviewed fact's `source_anchor_ids`.
- `tests/fund/test_report_writing_audit.py::test_fact_with_dangling_anchor_does_not_satisfy_requirement` covers a reviewed turnover fact pointing to `anchor:missing`.

Result:

```text
('dangling_anchor', False, ['required_evidence_missing'])
```

### Closed: malformed records `report_year` fails closed instead of raising

Evidence:

- `_coerce_report_year(...)` catches `TypeError` / `ValueError` and returns a blocking `invalid_audit_input` issue.
- `audit_report_writing_records(...)` returns `failed_closed=True` when record conversion emits input issues.
- `tests/fund/test_report_writing_audit.py::test_malformed_records_report_year_fails_closed` covers this path.

Result:

```text
('bad_report_year', True, ['invalid_audit_input'])
```

### Closed: conflicting explicit Chapter 3 `fund_type_slot` fails closed

Evidence:

- `_resolve_chapter_fund_type_slot(...)` detects multiple explicit non-default/non-unknown draft slots for one chapter and returns a blocking `input_conflict` issue.
- `audit_report_writing_bundle(...)` skips the active Chapter 3 material audit when this input conflict exists and sets `failed_closed=True`.
- `tests/fund/test_report_writing_audit.py::test_conflicting_explicit_chapter_3_fund_type_slots_fail_closed` covers this path.

Result:

```text
('conflicting_slots', True, ['input_conflict'])
```

### Closed: records-mode incomplete `data_gap` no longer satisfies requirement

Evidence:

- `_gap_from_mapping(...)` no longer defaults compatibility-bearing fields into allowed values.
- `_gap_has_required_explicit_fields(...)` requires an accepted `reason_code`, relevant `field_path`, and non-empty `required_report_wording`.
- `audit_report_writing_records(...)` fails closed if any records `data_gap` is malformed for this contract.
- `tests/fund/test_report_writing_audit.py::test_records_data_gap_missing_reason_or_field_path_fails_closed` covers missing `reason_code` and missing `field_path`.

Additional targeted check covered missing `required_report_wording`:

```text
True [('invalid_audit_input', 'blocking')]
```

### Closed: valid data-gap disclosure still passes

Evidence:

- A compatible active Chapter 3 `data_gap` with required wording and no positive stability claim returns no issues.

Result:

```text
False []
```

## Boundary Review

No boundary violation found in the repaired source or tests. The boundary grep had no matches for:

```text
quality_gate_policy|quality_gate|dayu\.host|dayu\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source helper|source adapter|pdf|cache|extractor|renderer|FundAnalysisService|extra_payload|FQ0|FQ6
```

The reviewed implementation remains in Fund-layer files and focused tests:

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`

It does not alter renderer, FQ0-FQ6 quality gate, Service/CLI defaults, document repository, PDF/cache/source helpers, production extractors, Host/Agent packages, or dayu runtime.

## Commands Run

```bash
git status --short
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-mimo-20260526.md
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-review-glm-20260526.md
rg -n "^class |^def |ReportWritingAuditIssue|failed_closed|input_conflict|dangling|source_anchor|data_gap|required_report_wording|report_year|fund_type_slot|insufficient|next minimum|下一步" fund_agent/fund/report_writing_audit.py
rg -n "^class |^def |fund_type_slot|must_answer|must_not_cover|required_evidence|allowed_na_reason|failure_behavior|RequirementSeverity|active_fund|chapter_3" fund_agent/fund/template/chapter_contract_constraints.py
rg -n "data_gap|dangling|report_year|input_conflict|fund_type_slot|required_report_wording|next minimum|下一步|anchor|must_not|valid minimal|unsupported" tests/fund/test_report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py
sed -n '1,280p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md
sed -n '1,260p' fund_agent/fund/report_writing_audit.py
sed -n '260,620p' fund_agent/fund/report_writing_audit.py
sed -n '620,940p' fund_agent/fund/report_writing_audit.py
sed -n '940,1260p' fund_agent/fund/report_writing_audit.py
sed -n '1,260p' fund_agent/fund/template/chapter_contract_constraints.py
sed -n '260,560p' fund_agent/fund/template/chapter_contract_constraints.py
sed -n '260,610p' tests/fund/test_report_writing_audit.py
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
rg -n "quality_gate_policy|quality_gate|dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source helper|source adapter|pdf|cache|extractor|renderer|FundAnalysisService|extra_payload|FQ0|FQ6" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
git diff --no-index --check /dev/null fund_agent/fund/template/chapter_contract_constraints.py
git diff --no-index --check /dev/null fund_agent/fund/report_writing_audit.py
git diff --no-index --check /dev/null tests/fund/template/test_chapter_contract_constraints.py
git diff --no-index --check /dev/null tests/fund/test_report_writing_audit.py
```

Focused tests:

```text
18 passed in 0.36s
```

Adjacent tests:

```text
147 passed in 0.50s
```

Ruff:

```text
All checks passed!
```

Boundary grep returned no matches. `git diff --no-index --check` printed no whitespace warnings for the checked new files; exit code `1` is expected for new files compared against `/dev/null`.

## Residual Risks

- Duplicate occurrence-level `issue_id` uniqueness remains deferred by controller policy from the first review cycle. I did not treat it as blocking in this re-review because the required accepted findings are closed and current ids remain deterministic class ids.
- Coverage measurement was not re-attempted in this re-review; prior implementation evidence records a local numpy / coverage collection issue. The focused and adjacent acceptance tests passed.
- Phrase matching remains intentionally narrow and deterministic for the first dev-only slice. Broader language coverage should remain a later writing-quality gate, not a blocker for this repaired implementation.
