# Gate B Validator Fix Evidence

> Date: 2026-05-26
> Worker: AgentCodex specialist implementation/fix agent
> Scope: Small concrete quality fix for multi-bundle report-quality JSONL validation ownership. No commit, push, PR, merge, reset, rebase, delete, GitHub mutation, renderer, FQ0-FQ6, Service/CLI default behavior, Host/Agent/dayu, FundDocumentRepository, repository/PDF/cache/source helper, nav_data, durable fixture, product analyze/checklist default, or quality-gate change.

## Truth Sources

- `AGENTS.md`
- Gate A artifact: `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md`
- Current source:
  - `fund_agent/fund/report_quality_validation.py`
  - `tests/fund/test_report_quality_validation.py`
  - `fund_agent/fund/README.md`

## Root Cause

Gate A showed that each per-sample `ReportEvidenceBundle` and per-sample JSONL passed, while the combined multi-bundle JSONL failed with `RQV_REF_MISSING=4`.

The same-source code cause was in `validate_report_quality_jsonl()`: after parsing all records, it collected every standalone `record_type="score_issue"` row and validated them against the first bundle's id indexes. Score issues after later bundles therefore failed when they referenced anchors or gaps that existed only in their actual bundle.

## Change

- `validate_report_quality_jsonl()` now assigns standalone `score_issue` rows to the nearest preceding `record_type="bundle"` record.
- A `score_issue` row before any bundle remains fail-closed with stable pointer `line:N` and precise error code `RQV_SCORE_ISSUE_ORPHANED`.
- Cross-bundle anchor or gap references still fail against the owning bundle's local indexes.
- Existing bundle validation and line-based pointers are preserved.
- `fund_agent/fund/README.md` now documents the multi-bundle JSONL ownership semantics.
- Follow-up review cleanup replaced the internal tuple-with-mutable-list grouping with a small `_ScoreIssueRecordGroup` dataclass for readability; duplicate-index residuals were left unchanged.

## Focused Coverage

Added tests in `tests/fund/test_report_quality_validation.py`:

- Multi-bundle JSONL with a `score_issue` after each bundle passes.
- A `score_issue` after the second bundle that references first-bundle anchor and gap ids fails with `RQV_REF_MISSING`.
- A `score_issue` before any bundle fails closed with `RQV_SCORE_ISSUE_ORPHANED`.
- Existing single-bundle JSONL behavior remains covered by `test_jsonl_accepts_bundle_record_and_score_issue_records`.

## Validation Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/fund/test_report_quality_validation.py -q` | `28 passed in 0.41s` |
| `.venv/bin/ruff check fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py` | `All checks passed!` |
| `.venv/bin/python -m pytest tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py -q` | `51 passed in 0.59s` |
| `.venv/bin/python -c "... validate_report_quality_jsonl(Path('/tmp/fund-agent-small-baseline-real-eval-20260526/bundles.jsonl')) ..."` | `total_records=9`, `blocking_count=0`, `material_count=0`, `minor_count=0`, `failed_closed=false`, `error_code_counts=[]` |
| `git diff --check` | passed |

## Residual Risk

- This fix intentionally does not introduce a new explicit ownership field. It uses nearest-preceding-bundle ownership because no clearer existing ownership field is present in the standalone `score_issue` records.
- This fix does not promote Gate A scratch outputs into durable fixtures or change scoring readiness semantics.
