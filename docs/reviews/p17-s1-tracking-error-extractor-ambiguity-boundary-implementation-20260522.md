# P17-S1 tracking_error extractor ambiguity boundary implementation（2026-05-22）

## Verdict

`IMPLEMENTED_PENDING_REVIEW`

本实现按已接受的 P17-S1 plan 在 Fund Capability extractor 内收窄跟踪误差直接披露抽取语义：移除旧泛化 `tracking_error_ambiguous` 生产路径，改为具体 fail-closed note；修复两个早退位置，使前序目标/混杂文本不压制后续有效直接披露；保留直接披露成功契约。

## Scope

Changed files:

- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`
- `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-implementation-20260522.md`

Not changed:

- production golden files/templates
- selected CSV / RR-13 data
- `docs/design.md`
- `docs/implementation-control.md`
- README files
- Service/UI/Runtime/Engine/source orchestration/document adapters/PDF/cache helpers
- branch/PR/issue/external state
- excluded local drafts

## Implementation Summary

- Added `_TrackingErrorExtractionOutcome` and explicit tracking-error blocker note constants.
- Replaced broad precheck early return with table/text outcomes and precedence-based blocker note selection.
- Replaced text mixed actual/target early return with blocker recording plus continued scanning.
- Made target-only `continue` behavior explicit by recording `tracking_error_target_or_limit`.
- Made multi-match behavior explicit with `tracking_error_multi_match`.
- Split stale generic ambiguity semantics:
  - mixed actual/target: `tracking_error_mixed_actual_and_target`
  - table/text conflict: `tracking_error_table_text_inconsistent`
- Preserved direct-disclosure success contract:
  - `source_type="direct_disclosure"`
  - `calculation_method="disclosed"`
  - `frequency="annual_report_period"`
  - annual-report anchors with `row_locator="tracking_error"`
  - same provenance note.

## Focused Test Coverage

Added or updated focused tests for:

- target/limit note
- manager narrative note
- benchmark-only note
- standard-deviation-only note
- mixed actual/target note
- unparseable direct-looking note
- table/text inconsistency note
- multi-match note
- table-level multi-match note
- `§3` missing with `§2` direct tracking-error fallback
- direct disclosure after earlier mixed target line
- direct disclosure after earlier target-only line

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| `tracking_error_incomplete_anchor` fixture | future parser malformed-table fixture | Current text/table builders naturally produce complete annual-report anchors for accepted matches. I did not fabricate impossible malformed parser objects in focused tests. GLM F4 table-level multi-match and `§2` fallback gaps are now covered. |
| production `tracking_error` rows for `001548` and P16 enhanced-index candidates | future evidence-backed golden gate | Still blocked until reviewed direct observed disclosure evidence is accepted. No production golden rows were edited. |
| calculated tracking error / external index data | future design phase | Out of scope; not implemented. |

## Validation

Final local validation:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 22 passed in 0.37s

.venv/bin/python -m pytest tests/fund/extractors -q
# 62 passed in 0.36s

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed in 0.45s

.venv/bin/python -m ruff check fund_agent tests
# All checks passed!

git diff --check HEAD
# passed with no output
```
