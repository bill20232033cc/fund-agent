# Style Positioning Field Reconciliation - 2026-05-19

结论：`style_positioning` 字段已收口到 `product_profile`，不再属于 `manager_strategy_text`。这次收口是字段契约迁移，不属于 P4 aggregate fix / re-review 的质量 gate 证据。

## 背景

用户已在 `reports/golden-answers/golden-answer-prefill-reviewed.md` 第一张表中把 `004393 安信企业价值优选混合A` 的 `style_positioning` 调整到 `product_profile`。对照 `reports/golden-answers/golden-answer-prefill.md` 可见旧预填仍把该字段放在 `manager_strategy_text`。

从领域含义看，`style_positioning` 描述的是产品本质/风险收益/投资目标中的定位，应归属模板第 1 章的 `product_profile`；`manager_strategy_text` 应只承载 §4 管理人当期策略摘要与后市展望，避免把产品合同定位和经理当期表述混在同一字段。

## 代码事实

- `fund_agent/fund/extractors/profile.py`
  - `product_profile` 新增 `style_positioning`。
  - 优先从 §2 的“风格定位 / 风险收益特征 / 产品定位”读取。
  - 没有显式字段时，从 `investment_objective` 中谨慎提炼定位短语。
- `fund_agent/fund/extractors/manager_ownership.py`
  - `manager_strategy_text` 移除 `style_positioning`。
  - 字段值只保留 `strategy_summary` 和 `market_outlook`。
- `fund_agent/fund/analysis/consistency_check.py`
  - `check_consistency()` 显式接收 `product_profile`。
  - 投资风格维度优先读取 `product_profile.style_positioning / investment_strategy / investment_objective`。
  - 缺少 §2 定位时回退到 `manager_strategy_text.strategy_summary`。
- `fund_agent/fund/template/renderer.py`
  - 第 3 章展示“产品风格定位”，来源为 `product_profile.style_positioning`。
- `docs/golden-answer-template.md`
  - golden answer 模板行迁移为 `product_profile | style_positioning`。
  - 移除 `manager_strategy_text | style_positioning`。

## 测试覆盖

- `tests/fund/extractors/test_profile.py` 覆盖 §2 表格读取 `style_positioning`。
- `tests/fund/extractors/test_manager_ownership.py` 覆盖 §4 策略字段不再输出 `style_positioning`。
- `tests/fund/analysis/test_consistency_check.py` 覆盖 `check_consistency()` 通过 `product_profile` 判断风格一致性。
- `tests/fund/template/test_renderer.py` 覆盖模板渲染从产品画像展示风格定位。
- `tests/fund/test_golden_prefill.py` 覆盖 golden prefill 对 `product_profile.style_positioning` 的预填。

## 未纳入范围

- 未批量覆盖 `reports/golden-answers/golden-answer-prefill-reviewed.md` 中用户尚未审核的其它基金表。
- 未把旧 `reports/golden-answers/golden-answer-prefill.md` 当作人工真源；它是旧模板生成的预填底稿，后续可按新模板重新生成。
- 未改变 P4 aggregate fix 的 `fund_scores` / `quality_gate` 证据链。

## 裁决

字段契约已收口。后续 correctness golden answer 应使用：

- `product_profile.style_positioning`
- `manager_strategy_text.strategy_summary`
- `manager_strategy_text.market_outlook`

不再新增或依赖：

- `manager_strategy_text.style_positioning`
