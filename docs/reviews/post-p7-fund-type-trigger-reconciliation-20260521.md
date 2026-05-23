# Post-P7 Fund Type Trigger Reconciliation（2026-05-21）

## 背景

复合基金类型收口后，工作区中继续出现两类基金类型触发规则调整：

- QDII/FOF 判断不再消费业绩比较基准文本。
- 增强指数判断不再用单字“增强”，改为身份级短语“指数增强 / 增强指数 / 增强型指数”。

这些改动与既有设计原则一致：基金类型判断应基于产品身份、类别、投资目标、投资范围和投资策略；业绩比较基准只能作为参照，不应单独改变基金顶层类型。

## 裁决

接受该调整。

理由：

1. 基准中出现“境外指数”“FOF 指数”等词，只说明收益参照物，不足以证明产品是 QDII 或 FOF。
2. 普通指数基金文本中的“增强收益”“增强体验”等泛化表述，不等同于指数增强产品身份。
3. 该调整不会改变标准 `FundType` 枚举，也不改变 QDII/FOF 作为顶层分类的裁决。

## 代码收口

变更点：

- `fund_agent/fund/fund_type.py`
  - QDII/FOF 触发文本改为名称、类别、投资目标、投资范围、投资策略，不包含业绩比较基准。
  - 增强关键词改为 `指数增强`、`增强指数`、`增强型指数`。
- `tests/fund/extractors/test_profile.py`
  - 覆盖普通指数基金含泛化“增强”词时仍判为 `index_fund`。
  - 覆盖基准文本含境外/FOF 词时不触发 `qdii_fund` / `fof_fund`。
- `fund_agent/fund/README.md`
  - 更新基金类型识别触发口径。

## 验证

已运行：

```bash
pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_score.py -q
```

结果：

```text
32 passed
```

## 残余风险

真实年报中的“增强型指数”命名方式可能存在更多同义词。后续如扩展关键词，应继续使用身份级短语，并用 fixture 覆盖，不能回退到单字“增强”。
