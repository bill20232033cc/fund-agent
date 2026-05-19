# Correctness Golden Answer Completion - 2026-05-19

结论：`reports/golden-answers/golden-answer-prefill-reviewed.md` 已完成 6 只基金的 correctness golden answer 人工底稿形态收口，并已通过 strict JSON 构建。

## 输入

- 用户已人工完成第一张表：`004393 安信企业价值优选混合A（国内股票类）`
- AgentCodex 参考第一张表的格式和标注口径，补全后续 5 张表：
  - `000216 华安黄金ETF联接A（黄金类）`
  - `007721 天弘标普500发起(QDII-FOF)A（海外股票类）`
  - `007360 易方达中短期美元债债券(QDII)A(人民币份额)（海外债券/稳健类）`
  - `006597 国泰利享中短债债券A（国内债券类）`
  - `001548 天弘上证50ETF联接A（国内股票类）`

## 字段契约

当前 reviewed Markdown 已采用最新字段契约：

- `product_profile.style_positioning`
- `manager_strategy_text.strategy_summary`
- `manager_strategy_text.market_outlook`

不再使用：

- `manager_strategy_text.style_positioning`

对后续 5 张表中当前证据不足的 `product_profile.investment_scope`，已按 skip 规则显式标注为：

`| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |`

没有为缺少可复核来源的字段编造值。

## 输出

- Reviewed Markdown：`reports/golden-answers/golden-answer-prefill-reviewed.md`
- Strict JSON：`reports/golden-answers/golden-answer.json`

构建结果：

- funds: 6
- records: 121
- skipped: 29

## 验证

- `.venv/bin/python -m fund_agent.ui.cli golden-build --input-path reports/golden-answers/golden-answer-prefill-reviewed.md --output-path reports/golden-answers/golden-answer.json`
  - passed
  - `funds: 6`
  - `records: 121`
  - `skipped: 29`
- `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py -q`
  - `4 passed`

## 裁决

`correctness golden answer completion` 已完成。

下一 gate 应进入 `correctness slice implementation`：基于 `reports/golden-answers/golden-answer.json` 接入 correctness 自动比对，并让 quality gate 不再只输出 `FQ0/info`。
