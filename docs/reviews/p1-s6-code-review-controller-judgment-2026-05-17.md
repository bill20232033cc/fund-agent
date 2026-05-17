# P1-S6 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S6 管理人文本、换手率、利益一致性与持有人结构
> Implementation artifact：`docs/reviews/p1-s6-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现严格限定在 `§4/§8/§9`：
  - `manager_strategy_text` 只消费 `§4`
  - `turnover_rate` 只消费 `§8`
  - `manager_alignment` 与 `holder_structure` 只消费 `§9`
- 当前实现未触碰：
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/documents/**`
  - `fund_agent/fund/pdf/**`
  - `fund_agent/fund/data/nav_data.py`
  - `§10` 份额变动
  - P2 分析或审计逻辑
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py -q
```

结果：`26 passed`

## 2. Accepted Findings

### A1-已修复-中-仅命中“换手率口径”时不应把 `turnover_rate` 标记为 `direct`

- **来源**：controller 本地 review
- **裁决**：`accepted`
- **原因**：
  - `P1-S6` 完成信号明确要求“换手率必须带数值 anchor”
  - 若只有“换手率口径”而无换手率数值，标记为 `direct` 会误导后续成本计算
- **修复**：
  - `fund_agent/fund/extractors/manager_ownership.py` 当前只有在 `turnover_rate` 数值命中时才返回 `extraction_mode="direct"`
  - 仅命中 `turnover_basis` 时返回 `extraction_mode="missing"`，保留口径 anchor 与说明
  - 完全未命中时仍返回标准 `missing` 且 `value=None`
- **测试**：
  - `tests/fixtures/fund/extractors/manager_ownership/manager_ownership_turnover_basis_only.txt`
  - `tests/fund/extractors/test_manager_ownership.py::test_extract_manager_ownership_requires_numeric_turnover_anchor`

## 3. Deferred Findings

### D1-未修复-中-真实年报 `§4/§8/§9` 表格格式尚未覆盖

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P1-S8 / real sample matrix`
- **原因**：
  - 当前 slice 以最小文本 fixture 锁定契约、状态和 anchor
  - 真实年报中的换手率、持有人结构可能以表格形式出现，适合在 P1 样本矩阵统一覆盖

### D2-未修复-低-换手率缺失时未做同类中位数估算

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P1-S8 or P2 cost analysis`
- **原因**：
  - 同类中位数需要明确同类口径和样本数据
  - 当前不能用间接经验填充数值，按项目约束应返回 `missing`

## 4. 当前 Gate 结论

- `P1-S6 code review` 结论：`pass`
- 当前没有 blocker
- `P1-S6` 可推进到 accepted local commit，并把下一 entry point 切到 `P1-S7 implementation + review`
