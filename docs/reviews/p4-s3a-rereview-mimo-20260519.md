# P4-S3a Targeted Re-Review

## Scope

- Mode: targeted re-review of GLM F1 fix
- Base: changes since `p4-s3a-code-review-mimo-20260519.md`
- Changed files: `fund_agent/fund/fund_type.py` (`_INDEX_STRATEGY_KEYWORDS`), `tests/fund/extractors/test_profile.py` (new test), `docs/reviews/p4-s3a-implementation-20260519.md` (follow-up section)
- Output file: `docs/reviews/p4-s3a-rereview-mimo-20260519.md`

## Verdict

**PASS**

## Verification

### 1. F1 closed: generic "紧密跟踪市场动态" no longer triggers index_fund

Confirmed. `_INDEX_STRATEGY_KEYWORDS` changed from containing `"紧密跟踪"` to `"紧密跟踪标的指数"` and `"紧密跟踪指数"`. Direct verification:

```
_contains_any("紧密跟踪市场动态", _INDEX_STRATEGY_KEYWORDS) → False
_contains_any("紧密跟踪标的指数", _INDEX_STRATEGY_KEYWORDS) → True
_contains_any("紧密跟踪指数", _INDEX_STRATEGY_KEYWORDS) → True
```

New test `test_extract_profile_does_not_treat_tracking_market_dynamics_as_index` (fund_code=019999, investment_objective="紧密跟踪市场动态，灵活调整投资组合。", benchmark含沪深300) asserts `active_fund`.

### 2. 004393-like case still active_fund

Confirmed. `test_extract_profile_classifies_004393_like_mixed_fund_as_active_not_index` passes unchanged.

### 3. True index/enhanced/bond/QDII tests still pass

Confirmed. 145 tests pass (was 144 before this change), ruff clean. All existing index_fund (510300), enhanced_index (161725), bond_fund, QDII classification tests unaffected.

### 4. No new blocking finding

No new findings. The keyword narrowing is precise: only removes the over-broad "紧密跟踪" standalone match while preserving explicit index-semantic phrases. Implementation artifact accurately documents the follow-up change.

## Commands Run

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py -q
# 13 passed

.venv/bin/python -m pytest tests/ -q
# 145 passed

.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py
# All checks passed

.venv/bin/python -c "from fund_agent.fund.fund_type import _contains_any, _INDEX_STRATEGY_KEYWORDS; print(_contains_any('紧密跟踪市场动态', _INDEX_STRATEGY_KEYWORDS))"
# False
```
