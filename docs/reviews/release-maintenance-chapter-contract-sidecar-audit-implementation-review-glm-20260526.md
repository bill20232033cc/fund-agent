# Fund-layer CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit Code Review

> Date: 2026-05-26
> Reviewer: independent code reviewer 2
> Scope: current untracked implementation for Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit
> Verdict: FAIL

## Reviewed Files

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-controller-judgment-20260526.md`
- `docs/implementation-control.md` Startup Packet

## Findings

### Major: conflicting Chapter 3 draft fund types can silently disable the active-fund contract

- Location: `fund_agent/fund/report_writing_audit.py:183-198`, `fund_agent/fund/report_writing_audit.py:864-885`
- Evidence: `audit_report_writing_bundle()` groups all chapter drafts, then `_resolve_chapter_fund_type_slot()` returns the first explicit non-`default` / non-`unknown` draft type. It does not detect conflicting explicit slots in multiple drafts for the same chapter. The returned single slot decides whether `_audit_active_chapter_3_turnover_requirement()` runs; if the first draft is `index_fund`, line 308 returns no issues even if another Chapter 3 draft is explicitly `active_fund` and contains "风格稳定，言行一致".
- Reproduction:
  - Command:
    ```bash
    uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_bundle, ChapterDraftSurrogate; from tests.fund.test_report_writing_audit import _bundle; drafts=(ChapterDraftSurrogate(chapter_id=3,fund_type_slot='index_fund',markdown=''), ChapterDraftSurrogate(chapter_id=3,fund_type_slot='active_fund',markdown='基金经理风格稳定，言行一致。')); r=audit_report_writing_bundle(_bundle(fund_type_slot=None), chapter_drafts=drafts); print(r.summary); print(r.issues); print(r.failed_closed)"
    ```
  - Output:
    ```text
    ReportWritingAuditSummary(issue_count=0, blocking_count=0, material_count=0, minor_count=0, informational_count=0, failure_category_counts=(), evidence_requirement_gap_count=0)
    ()
    False
    ```
- Impact: The dev-only audit can report a clean pass while the exact target slice, active Chapter 3 unsupported stability claim, is present. This undermines the sidecar as an executable contract and makes `failed_closed` ineffective for contradictory audit inputs.
- Recommendation: Treat multiple explicit fund-type slots for the same chapter as an input contradiction. Emit a blocking issue and set `failed_closed=True`; or audit each explicit slot independently and still emit an input-conflict issue. The issue domain likely needs a stable category such as `invalid_audit_input` / `input_conflict`, rather than overloading evidence-missing categories.

### Major: records helper fabricates compatible data gaps from incomplete records

- Location: `fund_agent/fund/report_writing_audit.py:428-462`, `fund_agent/fund/report_writing_audit.py:491-516`, `fund_agent/fund/report_writing_audit.py:557-572`
- Evidence: `_gap_from_mapping()` defaults missing `reason_code` to `"not_reviewed_in_current_slice"` and missing `field_path` to `None`. `_find_compatible_gap()` accepts both that reason code and `field_path is None`. Therefore a caller-supplied record with only `chapter_ids=("chapter_3",)` is interpreted as a compatible turnover/style data gap even though it did not explicitly carry the required reason or field path.
- Reproduction:
  - Command:
    ```bash
    uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_records, ChapterDraftSurrogate; records=({'record_type':'bundle','bundle_id':'b','fund_type_slot':'active_fund','data_gaps':({'chapter_ids':('chapter_3',),'field_path':'manager.turnover_rate'},)},); r=audit_report_writing_records(records, chapter_drafts=(ChapterDraftSurrogate(chapter_id=3,fund_type_slot='active_fund',markdown='本章只描述任职背景，不判断风格稳定性。'),)); print(r.summary); print(r.issues)"
    ```
  - Output:
    ```text
    ReportWritingAuditSummary(issue_count=0, blocking_count=0, material_count=0, minor_count=0, informational_count=0, failure_category_counts=(), evidence_requirement_gap_count=0)
    ()
    ```
  - A still looser record with `chapter_ids=("chapter_3",)` and no `field_path` also passes because `None` is accepted.
- Impact: `audit_report_writing_records()` can mask missing required evidence by inventing the allowed gap semantics that the caller failed to provide. This directly conflicts with the gate goal that Chapter 3 data-gap wording be explicit and repeatable; it also makes record-based dev audit less strict than the typed `ReportEvidenceBundle` path.
- Recommendation: Do not default compatibility-bearing fields (`reason_code`, `field_path`, `required_report_wording`) to allowed values. In records mode, incomplete gap records should either be ignored as non-compatible or produce a blocking/input-invalid issue. If permissive parsing remains intentional, it must not satisfy `required_evidence` unless the compatible reason code and relevant field path are explicitly present in the record.

### Minor: repeated issues can share the same `issue_id`

- Location: `fund_agent/fund/report_writing_audit.py:271-284`, `fund_agent/fund/report_writing_audit.py:387-405`, `fund_agent/fund/report_writing_audit.py:722-770`
- Evidence: `_build_issue()` constructs ids from chapter, slot, failure category, and requirement/key. For direct trading-advice hits, `requirement_id` and `issue_key` are both absent, so repeated drafts in the same chapter/fund slot produce identical ids ending with `:none`. For `must_not_cover`, the key is only `must_not_cover:{index}`, so repeated drafts that hit the same rule also collide.
- Impact: The list remains deterministic, but the ids are not unique. Any dev consumer that groups or de-duplicates by `issue_id` can lose separate findings or anchor/data-gap refs.
- Recommendation: Include a stable draft-local locator in the issue key, such as a caller-supplied `draft_id` field on `ChapterDraftSurrogate`, or a deterministic ordinal assigned during grouping. If the contract intentionally allows duplicate ids, document that `issue_id` is a class id rather than an occurrence id.

## Positive Boundary Checks

- I did not find imports or references to `FundDocumentRepository`, PDF/cache/source helpers, downloaders, production extractors, `renderer`, FQ0-FQ6 quality gate, Service/CLI defaults, Host/Agent packages, `dayu.host`, or `dayu.engine` in the reviewed implementation/test files.
- The sidecar wraps the existing template manifest and does not modify the current renderer path.
- The focused tests cover the required happy paths and several targeted negative paths, but they do not cover the two major failure modes above.

## Tests / Commands Run

```bash
sed -n '1,260p' fund_agent/fund/template/chapter_contract_constraints.py
sed -n '1,320p' fund_agent/fund/report_writing_audit.py
sed -n '320,760p' fund_agent/fund/report_writing_audit.py
sed -n '760,1180p' fund_agent/fund/report_writing_audit.py
sed -n '1,260p' tests/fund/template/test_chapter_contract_constraints.py
sed -n '1,320p' tests/fund/test_report_writing_audit.py
sed -n '320,700p' tests/fund/test_report_writing_audit.py
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md
sed -n '1,260p' docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-controller-judgment-20260526.md
sed -n '1,180p' docs/implementation-control.md
rg -n "FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|quality_gate_policy|FQ0|FQ6|renderer|FundAnalysisService|dayu\\.host|dayu\\.engine|extra_payload" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
git status --short
git diff --no-index --check /dev/null fund_agent/fund/template/chapter_contract_constraints.py
git diff --no-index --check /dev/null fund_agent/fund/report_writing_audit.py
nl -ba fund_agent/fund/report_writing_audit.py | sed -n '130,230p'
nl -ba fund_agent/fund/report_writing_audit.py | sed -n '230,370p'
nl -ba fund_agent/fund/report_writing_audit.py | sed -n '370,520p'
nl -ba fund_agent/fund/report_writing_audit.py | sed -n '680,780p'
nl -ba fund_agent/fund/report_writing_audit.py | sed -n '820,900p'
nl -ba fund_agent/fund/template/contracts.py | sed -n '340,390p'
nl -ba fund_agent/fund/template/contracts.py | sed -n '660,690p'
uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_records, ChapterDraftSurrogate; records=({'record_type':'bundle','bundle_id':'b','fund_type_slot':'active_fund','data_gaps':({'chapter_ids':('chapter_3',),'field_path':'manager.turnover_rate'},)},); r=audit_report_writing_records(records, chapter_drafts=(ChapterDraftSurrogate(chapter_id=3,fund_type_slot='active_fund',markdown='本章只描述任职背景，不判断风格稳定性。'),)); print(r.summary); print(r.issues)"
uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_bundle, ChapterDraftSurrogate; from tests.fund.test_report_writing_audit import _bundle; drafts=(ChapterDraftSurrogate(chapter_id=3,fund_type_slot='index_fund',markdown=''), ChapterDraftSurrogate(chapter_id=3,fund_type_slot='active_fund',markdown='基金经理风格稳定，言行一致。')); r=audit_report_writing_bundle(_bundle(fund_type_slot=None), chapter_drafts=drafts); print(r.summary); print(r.issues); print(r.failed_closed)"
```

Focused test result:

```text
13 passed in 0.36s
```

Boundary grep returned no matches. `git diff --no-index --check` for the two untracked source files produced no whitespace warnings; exit code is expectedly non-zero because `/dev/null` differs from each new file.

## Residual Risks

- I did not run the broader adjacent test matrix or ruff in this review pass; the implementation evidence claims those passed.
- I did not review README / `docs/design.md` / `docs/implementation-control.md` updates because this implementation slice has not added them yet.
- The phrase matcher remains intentionally minimal; beyond the conflicts and records-default issues above, broader Chinese paraphrase coverage should remain a future audit-quality slice unless this gate expands.
