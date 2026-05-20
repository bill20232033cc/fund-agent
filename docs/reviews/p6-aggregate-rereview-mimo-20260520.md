# P6 Aggregate Rereview — Fix Verification

## Scope

- Mode: targeted re-review of accepted fixes only
- Branch: main (unstaged workspace changes)
- Base: post-fix workspace vs accepted judgment `docs/reviews/p6-aggregate-deepreview-controller-judgment-20260520.md`
- Output file: `docs/reviews/p6-aggregate-rereview-mimo-20260520.md`
- Included scope: 5 accepted fixes from controller judgment
- Excluded scope: No new behavior, no new modules, no scope expansion

## Findings

未发现实质性问题。

## Fix Verification

### Fix 1: Shared EVIDENCE_APPENDIX_HEADING — PASS

- `chapter_blocks.py:18` — `EVIDENCE_APPENDIX_HEADING: Final[str] = "## 证据与出处"` (public, no underscore)
- `__init__.py:64` — exported in `__all__`
- `renderer.py:25` — `from fund_agent.fund.template.chapter_blocks import EVIDENCE_APPENDIX_HEADING`
- `renderer.py:468` — `lines = [EVIDENCE_APPENDIX_HEADING]` (no inline string)
- `audit_programmatic.py:18` — `from fund_agent.fund.template.chapter_blocks import EVIDENCE_APPENDIX_HEADING`
- `chapter_blocks.py:20` — regex uses `re.escape(EVIDENCE_APPENDIX_HEADING)` (derives from same constant)
- Grep `## 证据与出处` across `fund_agent/**/*.py` returns exactly 1 hit: the definition at `chapter_blocks.py:18`

**Pass.** Single source of truth, all three consumers import the constant.

### Fix 2: C2 in docstring — PASS

- `audit_programmatic.py:103` — `"""执行 P1/P2/P3/C2/L1/R1/R2 程序审计。`
- Matches `_CHECKED_RULES` at line 38: `("P1", "P2", "P3", "C2", "L1", "R1", "R2")`

**Pass.** Docstring and code are aligned.

### Fix 3: No locals() guard, all failed chapters collected — PASS

- `extraction_score.py:1367-1391` — `unresolved_chapter_ids` and `resolution_errors` initialized before loop (lines 1367-1368)
- Loop body: `for chapter in contract_manifest.chapters:` (line 1369), `chapter` is always assigned before `try` block
- `except ValueError` (line 1380): `unresolved_chapter_ids.append(chapter.chapter_id)` — no `locals()` guard
- Loop continues after failure (no `return` inside except), collecting all failures
- After loop: `if unresolved_chapter_ids:` (line 1383) returns mismatch with all collected IDs and joined error messages
- Fail-closed semantics preserved: any chapter failure → status=mismatch

**Pass.** No reflection, explicit state accumulation, all chapters attempted.

### Fix 4: FundType derived from type — PASS

- `contracts.py:12,21` — `from typing import ... get_args` ; `_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)`
- `item_rules.py:11,22` — `from typing import ... get_args` ; `_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)`
- Both modules derive supported types from `FundType` Literal, not a hand-maintained tuple

**Pass.** Single source of truth for supported fund types.

### Fix 5: Priority closed-set validation — PASS

- `contracts.py:23-25` — `_SUPPORTED_LENS_PRIORITIES: Final[frozenset[str]] = frozenset(("core", "high", "medium", "low"))`
- `contracts.py:909-910` — `if lens_rule.priority is not None and lens_rule.priority not in _SUPPORTED_LENS_PRIORITIES: raise ValueError(...)`
- `test_contracts.py:189-205` — test uses `priority="urgent"` (unsupported), expects `ValueError` with `"priority 不受支持"`

**Pass.** Closed-set validation enforced at manifest load time, test covers failure path.

### Scope Compliance — PASS

No new modules, no new behavior, no Service/UI/CLI changes, no fund document access, no extra_payload. All changes are maintenance fixes to existing P6 code.

## Verification

```
.venv/bin/python -m pytest tests/ -q          # 246 passed
.venv/bin/python -m ruff check .              # All checks passed
git diff --check                              # clean
```

## Conclusion

PASS.

All 5 accepted fixes from the controller judgment are correctly implemented. The evidence appendix heading is now a single shared constant. The audit docstring includes C2. The extraction_score loop collects all failed chapters without `locals()` reflection. Supported fund types are derived from `FundType` via `get_args`. Priority validation uses a closed-set frozenset. 246/246 tests pass, ruff clean, no new scope introduced.
