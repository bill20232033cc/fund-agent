# P6 Aggregate Targeted Re-Review - 2026-05-20

## Scope

- Mode: targeted re-review of accepted fixes from controller judgment `docs/reviews/p6-aggregate-deepreview-controller-judgment-20260520.md`
- Fix document: `docs/reviews/p6-aggregate-fix-20260520.md`
- Changed files: 8 production + 1 test file
- Excluded: no scope creep beyond accepted findings

## Finding Closure Verification

### P6-AGG-MIMO-001 — Shared `EVIDENCE_APPENDIX_HEADING` constant — Closed

- `chapter_blocks.py`: `_EVIDENCE_APPENDIX_HEADING` promoted to public `EVIDENCE_APPENDIX_HEADING`. Internal `_EVIDENCE_APPENDIX_HEADING_RE` updated to reference the public constant. ✅
- `__init__.py`: `EVIDENCE_APPENDIX_HEADING` exported in imports and `__all__`. ✅
- `renderer.py`: `["## 证据与出处"]` replaced with `[EVIDENCE_APPENDIX_HEADING]`. ✅
- `audit_programmatic.py`: `"## 证据与出处" in block.body_markdown` replaced with `EVIDENCE_APPENDIX_HEADING in block.body_markdown`. ✅
- No remaining hardcoded `"## 证据与出处"` string literal in renderer or audit.

### P6-AGG-MIMO-002 — C2 in programmatic audit docstring — Closed

- `run_programmatic_audit` docstring updated from `P1/P2/P3/L1/R1/R2` to `P1/P2/P3/C2/L1/R1/R2`. ✅

### P6-AGG-MIMO-003 — `locals()` guard removed — Closed

- `extraction_score.py:1365-1393`: `try/except` now wraps individual `resolve_preferred_lens` calls inside the `for chapter` loop, not the entire loop.
- No `locals()` reference anywhere in the diff. ✅
- Explicit `unresolved_chapter_ids: list[int]` and `resolution_errors: list[str]` accumulate across all chapters. ✅

### P6-AGG-MIMO-004 — All failed lens chapters collected — Closed

- Loop continues after `ValueError`, appending each failed chapter_id and error message. ✅
- `return _contract_applicability_result(...)` happens after the loop, not inside it. ✅
- Public field name `preferred_lens_unresolved_chapter_ids` unchanged per controller instruction. ✅
- `reason` now joins all resolution errors with `"; "` separator instead of showing only the first exception. ✅
- Fail-closed `mismatch` behavior preserved when any chapter fails. ✅

### P6-AGG-GLM-RISK-004 — `_SUPPORTED_FUND_TYPES` derived from `FundType` — Closed

- `contracts.py:23`: `_SUPPORTED_FUND_TYPES = get_args(FundType)`. ✅
- `item_rules.py:24`: `_SUPPORTED_FUND_TYPES = get_args(FundType)`. ✅
- Both modules import `get_args` from `typing`. ✅
- No remaining hardcoded fund type tuple in either file.

### P6-AGG-GLM-RISK-009 — Priority closed-set validation — Closed

- `contracts.py:25-26`: `_SUPPORTED_LENS_PRIORITIES = frozenset(("core", "high", "medium", "low"))`. ✅
- `contracts.py:908-909`: validation raises `ValueError` when `priority not in _SUPPORTED_LENS_PRIORITIES`. ✅
- `test_contracts.py:189-204`: test constructs a manifest with `priority="urgent"` and asserts `ValueError` with `"priority 不受支持"`. ✅

## Scope Compliance

Changed files match fix document exactly (8 source files, no untracked changes):

- `fund_agent/fund/template/chapter_blocks.py` ✅
- `fund_agent/fund/template/__init__.py` ✅
- `fund_agent/fund/template/renderer.py` ✅
- `fund_agent/fund/audit/audit_programmatic.py` ✅
- `fund_agent/fund/extraction_score.py` ✅
- `fund_agent/fund/template/contracts.py` ✅
- `fund_agent/fund/template/item_rules.py` ✅
- `tests/fund/template/test_contracts.py` ✅

No new behavior scope introduced. No changes to Service/UI/CLI/quality_gate beyond the extraction_score fix.

## Verification

```text
Targeted tests: 87 passed
Full suite: 246 passed
ruff check: All checks passed!
git diff --check: clean
```

## Verdict

PASS. All six accepted findings are closed. No new findings.

## Residual Risk

Deferred residual risks remain as recorded in `docs/reviews/p6-aggregate-deepreview-controller-judgment-20260520.md`. No new residual risk introduced by these fixes.
