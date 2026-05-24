# Release Maintenance 004393 Quality Gate S5 Renderer Wording Fix

## Scope

- Fix worker: renderer direct trading advice wording guard.
- Allowed source files: `fund_agent/fund/template/renderer.py`, `tests/fund/template/test_renderer.py`.
- Non-goals: no extraction, golden, config, control, Host/Agent package, or `review_report_20260524.md` changes.

## Accepted Finding

`_DIRECT_TRADING_ADVICE_PATTERN` used broad modal words such as `可以` and `不宜`, so annual-report disclosure text like `好价格可以买入并持有好公司` or `市场波动时不宜卖出优质公司` could be blocked even though the renderer was preserving disclosed manager strategy context rather than emitting system trading advice.

## Fix

- Removed broad modal trigger words from the direct-advice regex.
- Kept explicit advice triggers: `建议` / `推荐` / `应当` / `应该` / `直接` / `立即` / `马上` before `买入` / `卖出` / `加仓` / `减仓`.
- Kept fixed forbidden phrases for explicit report advice and unsafe output, including `买入金额`, `买入信号`, `卖出信号`, `仓位比例`, and `收益预测`.
- Added regression coverage proving disclosed §4 strategy wording is allowed while `建议买入`, `建议卖出`, `买入金额`, and `买入信号` remain blocked.

## Validation

- `uv run pytest tests/fund/template/test_renderer.py -q` -> 56 passed.
- `uv run ruff check fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py` -> passed.
- `git diff --check -- fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py` -> passed.
