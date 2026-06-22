# Targeted Re-Review: EC-P4 Slice 2 — Service Deterministic Opt-In Propagation

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code-review targeted re-review
- Slice: Slice 2 - Service Deterministic Opt-In Propagation
- Classification: heavy
- Release/readiness: NOT_READY
- Timestamp: 2026-06-22 23:06 Asia/Shanghai

## Reviewed Artifacts

- Original review: `docs/reviews/code-review-20260622-225412-mimo-ec-p4-slice2.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-code-review-fix-20260622.md`
- Changed files: `fund_agent/services/fund_analysis_service.py`, `tests/services/test_fund_analysis_service.py`

## Verdict

**PASS**

## Finding Status

### MiMo F-01 — Runner exception conversion path has direct regression coverage

**Status: 已修复**

Evidence:

- New test `test_fund_analysis_service_evidence_confirm_runner_exception_becomes_safe_summary` added at `tests/services/test_fund_analysis_service.py:669-705`.
- Injects `RuntimeError("boom")` into `_FakeEvidenceConfirmRunner` (line 682).
- Calls `analyze` with `evidence_confirm_policy="warn"`, `quality_gate_policy="off"` (lines 689-694).
- Asserts safe fail-closed summary shape:
  - `status == "fail"` (line 697)
  - `not_run_reason == "runner_exception:RuntimeError"` (lines 698-700)
  - `pathway_status == "fail"` (line 701)
  - `deterministic_status == "not_run"` (line 702)
  - `result.report_markdown` still renders (line 703)
- 39 tests pass (was 38).

### MiMo F-02 — EvidenceConfirmRunner type alias has Chinese comment

**Status: 已修复**

Evidence:

- Chinese comment added at `fund_agent/services/fund_analysis_service.py:200`:
  `# EvidenceConfirmRunner 是 Service 注入的 Fund 层 Evidence Confirm 异步运行器类型。`

## DS Accepted Fix Areas Cross-Check

### DS-ECP4S2-01 / DS-ECP4S2-04: Raises docs for EvidenceConfirmBlockedError

**Status: 已修复**

`EvidenceConfirmBlockedError` added to Raises sections:

| Method | Line |
|---|---|
| `analyze()` | 742 |
| `checklist()` | 798 |
| `_run_analysis_core()` | 1182 |
| `analyze_with_llm()` | 924 |
| `analyze_with_llm_execution()` | 1001 |

### DS-ECP4S2-02: analyze_with_llm_hosted structured propagation

**Status: 已修复**

Evidence at `fund_agent/services/fund_analysis_service.py`:

- `structured_block_exception` union type now includes `EvidenceConfirmBlockedError | None` (lines 1052-1057).
- `operation()` except clause catches `(QualityGateBlockedError, QualityGateNotRunBlockedError, EvidenceConfirmBlockedError)` (lines 1079-1083).
- Diagnostic recorded via `host_context.record_diagnostic(error_type=type(exc).__name__)` (line 1084).
- Re-raises through post-Host branch at line 1094: `if structured_block_exception is not None: raise structured_block_exception`.

## New Blockers Introduced by Fix

None.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/services/test_fund_analysis_service.py -q` | 39 passed in 0.85s |
| `uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py` | All checks passed |
| `rg -n "EvidenceConfirmBlockedError\|runner_exception\|EvidenceConfirmRunner"` | All references verified |

## Residual Risks

| Risk | Classification | Owner / Destination |
|---|---|---|
| CLI/UI EC summary and exit behavior | later approved slice | Slice 3 |
| Renderer non-rendering guard | later approved slice | Slice 4 |
| Semantic companion propagation | later approved slice | Slice 5 |
| Checklist EC remains off/no runner | later approved slice | Slice 6 or separate checklist gate |
| Default-on/product-mode EC and readiness | future work unit | NOT_READY preserved |
