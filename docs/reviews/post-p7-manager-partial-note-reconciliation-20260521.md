# Post-P7 Manager Extractor Partial Note Reconciliation（2026-05-21）

## 背景

`extract_manager_ownership()` 的多子字段输出存在一种灰区：字段整体有证据锚点并返回 `direct`，但子字段只命中一部分。此前调用方只能从 `value` 中的 `None` 推断部分缺失，`note` 没有明确提示。

## 裁决

接受 partial note 补强，但保留换手率的特殊边界。

规则：

- 策略文本、基金经理/从业人员持有、持有人结构：只要至少一个子字段命中，字段保持 `direct`；若有子字段缺失，`note` 标记“部分子字段缺失，仅抽取到部分信息”。
- 换手率：`turnover_rate` 数值是核心字段。数值命中时保持 `direct`，即使 `turnover_basis` 口径缺失也不单独标 partial；只有口径命中但数值缺失时返回 `missing`，并给出专门 note。

## 代码收口

变更点：

- `fund_agent/fund/extractors/manager_ownership.py`
  - `_build_field_from_matches(...)` 在部分子字段缺失时写入 partial note。
- `tests/fund/extractors/test_manager_ownership.py`
  - 对 partial fixture 增加 `manager_strategy_text` 和 `holder_structure` 的 partial note 断言。
  - 明确 `turnover_rate` 数值命中、口径缺失时 `note is None`。
- `fund_agent/fund/README.md`
  - 记录多子字段 partial note 与换手率特殊边界。

## 验证

已运行：

```bash
pytest tests/fund/extractors/test_manager_ownership.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
```

结果：

```text
31 passed
```

## 残余风险

该变更只增加字段级 note，不改变 extraction mode、value schema、anchor schema 或 correctness comparable fields。下游若需要把 partial note 升级为质量扣分，应在 extraction score 中另起规则，不应由 extractor 隐式改变状态。
