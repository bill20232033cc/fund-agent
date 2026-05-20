# P6 Aggregate Fix - 2026-05-20

## Verdict

P6 aggregate accepted immediate fixes completed locally. No commit or push was performed.

## Fixes Applied

1. Promoted public `EVIDENCE_APPENDIX_HEADING`
   - Added `EVIDENCE_APPENDIX_HEADING` in `fund_agent/fund/template/chapter_blocks.py`.
   - Exported it from `fund_agent/fund/template/__init__.py`.
   - Used it in `fund_agent/fund/template/renderer.py`.
   - Used it in `fund_agent/fund/audit/audit_programmatic.py`.

2. Updated programmatic audit docstring
   - `run_programmatic_audit(...)` now documents `P1/P2/P3/C2/L1/R1/R2`.

3. Removed `locals()` guard in FQ5 contract applicability
   - `_derive_contract_applicability(...)` now explicitly accumulates `unresolved_chapter_ids` and resolution error messages while iterating all chapters.
   - Public score field name `preferred_lens_unresolved_chapter_ids` is unchanged.
   - Fail-closed `mismatch` behavior is preserved when any chapter lens resolution fails.

4. Derived supported fund type tuples from `FundType`
   - `fund_agent/fund/template/contracts.py`
   - `fund_agent/fund/template/item_rules.py`

5. Added closed-set validation for `TemplateLensRule.priority`
   - Supported priorities are `core / high / medium / low`.
   - Added focused test coverage for unsupported priority fail-closed behavior.

## Verification

```text
.venv/bin/python -m pytest tests/fund/template/test_contracts.py tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py -q
38 passed

.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py -q
16 passed

.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
33 passed

.venv/bin/python -m pytest tests/ -q
246 passed

.venv/bin/python -m ruff check .
All checks passed!

git diff --check
passed
```

## Files Changed

- `fund_agent/fund/template/chapter_blocks.py`
- `fund_agent/fund/template/__init__.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/audit/audit_programmatic.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/template/item_rules.py`
- `tests/fund/template/test_contracts.py`
- `docs/reviews/p6-aggregate-fix-20260520.md`

## Residual Risk

No new behavior scope was introduced. Deferred P6 aggregate residual risks remain as recorded in `docs/reviews/p6-aggregate-deepreview-controller-judgment-20260520.md`.
