# P2-S1 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P2 / P2-S1 R=A+B-C 计算模块
> Implementation artifact：`docs/reviews/p2-s1-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `RabcInput`
  - `RabcAttribution`
  - `calculate_r_abc(...)`
  - `calculate_r_abc_series(...)`
  - `calculate_r_abc_from_bundle(...)`
- controller 本地边界检查确认：
  - analysis 模块不直接读取 PDF 或文件系统
  - analysis 模块只消费 P1 `StructuredFundDataBundle`
  - 股票仓位未稳定抽取时不静默默认，而是要求显式输入
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_r_abc.py -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/analysis/test_r_abc.py -q
```

结果：

```text
6 passed
All checks passed!
38 passed
```

## 2. Accepted Findings

### A1-已修复-中-P1 direct 字段子值缺失时错误过晚暴露

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - P1 字段可能 `extraction_mode=direct`，但具体子字段为 `None`
  - 如果只检查 `extraction_mode`，会在比例解析阶段抛出低质量错误
- **修复**：
  - `_missing_input_reasons(...)` 已检查 `nav_growth_rate`、`benchmark_return_rate`、`management_fee`、`custody_fee`、`turnover_rate` 子值
  - 新增 partial missing 单元测试

## 3. Deferred Findings

### D1-未修复-中-股票仓位仍需显式输入

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S3 or later extractor refinement`
- **原因**：
  - 设计公式需要股票仓位
  - P1 当前 12 项数据未稳定输出股票仓位
  - 当前 slice 不应伪造默认仓位，也不应越界新增持仓仓位 extractor

### D2-未修复-中-L1 公式审计尚未接入

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S8 programmatic audit`
- **原因**：
  - 当前 slice 目标是计算模块
  - L1 审计规则属于 `fund/audit/audit_programmatic.py` 的后续 slice

## 4. 当前 Gate 结论

- `P2-S1 code review` 结论：`pass`
- 当前没有 blocker
- `P2-S1` 可推进到 accepted local commit
