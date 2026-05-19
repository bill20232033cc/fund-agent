# Code Review (Targeted Re-review)

## Scope

- Mode: current changes (targeted re-review of GLM F1 fix)
- Branch: main
- Base: main
- Output file: `docs/reviews/p4-s3a-rereview-glm-20260519.md`
- Included scope: delta since `p4-s3a-code-review-glm-20260519.md`
  - `fund_agent/fund/fund_type.py` line 33: `紧密跟踪` → `紧密跟踪标的指数` + `紧密跟踪指数`
  - `tests/fund/extractors/test_profile.py`: new `test_extract_profile_does_not_treat_tracking_market_dynamics_as_index`
  - `docs/reviews/p4-s3a-implementation-20260519.md` update
- Excluded scope: all unchanged code from prior review

## Verdict: PASS

GLM F1 closed. No new findings.

## Verification

| Check | Result |
|---|---|
| F1 closed: `紧密跟踪市场动态` → `active_fund` | ✅ |
| 004393-like → `active_fund` | ✅ |
| `紧密跟踪标的指数` → `index_fund` | ✅ |
| `紧密跟踪指数` variant → `index_fund` | ✅ |
| All 13 profile + snapshot tests pass | ✅ |
| ruff check passed | ✅ |

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py -q
# 13 passed in 0.37s

.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py
# All checks passed!
```

Adversarial simulation confirmed all four scenarios.

## Findings

未发现实质性问题。`紧密跟踪` 已正确收窄为 `紧密跟踪标的指数` / `紧密跟踪指数`，新测试直接覆盖 GLM F1 场景。

## Open Questions

无

## Residual Risk

- 与首次 review 相同：无 FOF 显式测试用例（既有问题），004393 测试未含 investment_strategy 字段（不影响分类正确性）
