# Post-P7 Ratio Input Contract Reconciliation（2026-05-21）

## 背景

工作区中出现 `_ratios.py` 外部改动：`parse_ratio()` 对 `Decimal`、`int`、`float` 不再调用 `normalize_numeric_ratio()`，而是直接返回数值。

该改动会影响 R=A+B-C、言行一致性、投资者获得感、风险检查等所有分析模块，因此需要明确契约后再收口。

## 裁决

接受该改动，并将契约明确为：

- 字符串输入代表年报或调用方披露文本：
  - `"12.34%"` 解析为 `0.1234`
  - `"80"` 解析为 `0.8`
  - `"0.80"` 解析为 `0.80`
- 数值型输入代表调用方已经标准化的小数比例：
  - `Decimal("1.2345")` 保持 `1.2345`
  - `Decimal("2")` 保持 `2`
  - `1.2345` 保持 `1.2345`

理由：

1. 分析模块内部 dataclass 字段已标注“小数比例”，例如 `RabcInput.turnover_rate`。
2. 换手率等合法比例可以超过 1；`Decimal("1.2345")` 表示 123.45%，若按 `>1` 再除以 100，会错误缩小为 1.2345%。
3. 披露文本仍保留“带 % 或绝对值大于 1 的数字文本按百分比换算”的兼容逻辑，适合 P1 extractor 输出的字符串字段。

## 代码收口

变更点：

- `fund_agent/fund/analysis/_ratios.py`
  - `parse_ratio()` 对数值型输入不再二次归一。
  - docstring 明确字符串与数值型输入契约。
  - `normalize_numeric_ratio()` 保留给已知“数值百分比口径”的调用方。
- `tests/fund/analysis/test_ratios.py`
  - 新增公共比例解析直接测试。
  - 覆盖披露文本百分比、数值型已标准化小数比例、保留 helper 和非法输入。
- `tests/README.md`
  - 补充 `test_ratios.py` 的测试定位与运行命令。

## 验证

已运行：

```bash
pytest tests/fund/analysis -q
```

结果：

```text
51 passed
```

## 残余风险

如果未来有调用方以数值型 `80` 表示 80%，必须显式调用 `normalize_numeric_ratio(Decimal("80"))` 或改为传入字符串 `"80"` / `"80%"`。`parse_ratio()` 不再猜测数值型输入单位，避免在高换手率、倍数型比例等合法大于 1 的场景中产生静默错误。
