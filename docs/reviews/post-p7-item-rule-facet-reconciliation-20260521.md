# Post-P7 ITEM_RULE Facet Reconciliation（2026-05-21）

## 背景

Repo-level deepreview 指出 `_FACET_FUND_TYPE_MAP` 只覆盖指数、主动权益与指数增强 facet，未覆盖 CHAPTER_CONTRACT 中声明的债券、QDII 与 FOF 细分标签。

代码事实：

- `evaluate_template_item_rule(..., facets=...)` 会先调用 `_validate_explicit_facets()`。
- 未知 facet 当前不会触发规则，也不会报错；已知 facet 与基金类型冲突时会 fail closed。
- 因此合法的债券、QDII、FOF facet 若不在 `_FACET_FUND_TYPE_MAP` 中，会被当作未知 facet 静默忽略。

## 裁决

接受该 finding。修复范围限定为“显式 facet 与标准基金类型的确定性映射完整性”，不改变当前 ITEM_RULE 的渲染接入边界。

本轮不做：

- 不新增内置 ITEM_RULE。
- 不让 renderer 自动推断 facet。
- 不把 ITEM_RULE 接入程序审计或质量门禁。

## 代码收口

变更点：

- `fund_agent/fund/template/item_rules.py`
  - 补全债券、QDII、FOF 相关 facet 映射。
  - 覆盖 `QDII基金` / `QDII 基金`、`FOF基金` / `FOF 基金` 等模板中存在的空格别名。
  - 覆盖 `二级债基/混合债基`、`偏债混合基金` 等 CHAPTER_CONTRACT 中已声明的债券 facet。
- `tests/fund/template/test_item_rules.py`
  - 新增合法非权益 facet 相容测试，验证这些 facet 会进入 evaluator 的触发原因，而不是被静默丢弃。
  - 新增非权益 facet 冲突测试，验证跨基金类型 facet 仍 fail closed。
- `fund_agent/fund/README.md`
  - 明确已知 facet 覆盖指数、主动、增强指数、债券、QDII 和 FOF。

## 验证

已运行：

```bash
pytest tests/fund/template/test_item_rules.py -q
```

结果：

```text
15 passed
```

## 残余风险

当前 evaluator 仍只消费调用方显式传入的 facet，不从报告文本或 `preferred_lens` 自动推断 facet。这与现有边界一致；如果后续需要基于 `classified_fund_type` 或 `classification_basis` 自动派生 facet，应另起模板渲染 design slice。
