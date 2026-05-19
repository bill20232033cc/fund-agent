# P4-S2 人工处理清单

本文档用于 P4-S2 后半段开始前的人工确认与标注。当前代码已经完成字段级 coverage / traceability scoring；correctness scoring 仍需要人工 golden answer。

## 1. 确认最小 Golden Set

当前自动选择的 6 只基金如下，全部来自 `docs/code_20260519.csv`。

| 基金代码 | 基金名称 | App 类别 | 入选原因 |
|---|---|---|---|
| `004393` | 安信企业价值优选混合A | 国内股票类 | 必选 known failure case |
| `000216` | 华安黄金ETF联接A | 黄金类 | 黄金类样本 |
| `007721` | 天弘标普500发起(QDII-FOF)A | 海外股票类 | 海外股票类样本 |
| `007360` | 易方达中短期美元债债券(QDII)A(人民币份额) | 海外债券/稳健类 | 海外债券/稳健类样本 |
| `006597` | 国泰利享中短债债券A | 国内债券类 | 国内债券类样本 |
| `001548` | 天弘上证50ETF联接A | 国内股票类 | 额外国内股票类样本 |

请确认：

- 是否接受这 6 只作为 P4-S2 后半段人工 golden answer 样本。
- 如需替换，替换代码必须来自 `docs/code_20260519.csv`。
- `004393` 建议保留，因为它是当前基金类型误判的基线样本。

## 2. 裁决货币基金类

当前实现暂时排除：

| 基金代码 | 基金名称 | App 类别 |
|---|---|---|
| `001821` | 兴全天添益货币B | 货币基金类 |

当前排除原因：

- 现有 8 章基金分析模板更适配权益、债券、QDII、FOF 等产品。
- 货币基金的收益、风险、持仓、费用和投资者获得感口径与当前模板差异较大。
- P4-S2 前半段先把它作为 edge case 记录，避免影响主流程质量基线。

请裁决：

- 继续排除，后续单独设计货币基金模板与评分字段。
- 或纳入 P4-S2 golden set，并补充货币基金专用字段和评分口径。

## 3. 核对 CSV 数据质量

当前已知 `docs/code_20260519.csv` 中 `016492` 重复：

| 基金代码 | 基金名称 | App 类别 |
|---|---|---|
| `016492` | 南方均衡成长混合A | 国内股票类 |
| `016492` | 易方达逆向投资混合A | 国内股票类 |

请核对有知有行 App 原始清单，确认：

- 哪一条记录是正确的。
- 另一条是否基金代码录错。
- 是否需要删除重复行或修正基金代码。

当前代码只会在 snapshot summary 中标红重复代码，不会自动修改 CSV。

## 4. 准备 Correctness Golden Answer

P4-S2 后半段要实现 correctness scoring，需要你为 golden set 标注 P0 字段的人工正确答案。

### 4.1 标注范围

至少标注以下 P0 字段：

| field_name | 需要标注的内容 |
|---|---|
| `basic_identity` | 基金名称、基金代码、基金规模、基金经理或管理人 |
| `classified_fund_type` | 正确基金类型 |
| `benchmark` | 业绩比较基准 |
| `nav_benchmark_performance` | 净值增长率、基准收益率 |
| `fee_schedule` | 管理费、托管费 |
| `manager_strategy_text` | 基金经理或管理人策略文本摘要 |

### 4.2 建议标注格式

每只基金、每个字段建议写成：

```markdown
## 004393 安信企业价值优选混合A

### classified_fund_type

- expected_value: active_fund
- evidence: 年报2024§2 表X 行Y
- matching_rule: exact
- note: 当前 extractor 误判为 index_fund，P4-S3 需要修复

### benchmark

- expected_value: 中证800指数收益率 * 60% + 中证全债指数收益率 * 40%
- evidence: 年报2024§2 表X 行Y
- matching_rule: normalized_text
- note:
```

### 4.3 matching_rule 建议

| matching_rule | 适用场景 |
|---|---|
| `exact` | 基金代码、基金类型、费率等需要完全一致的字段 |
| `normalized_text` | 基准、策略文本等允许空格、标点、换行差异的字段 |
| `numeric_tolerance` | 规模、收益率等数值字段，允许小数位或单位差异 |
| `contains_key_points` | 策略摘要类文本，只要求包含关键要点 |

## 5. 推荐处理顺序

1. 先确认 golden set 是否接受。
2. 再裁决货币基金类是否继续排除。
3. 然后核对 `016492` 重复数据。
4. 最后开始为 6 只 golden set 基金标注 P0 correctness answer。

完成第 1-3 项后，可以先进入 P4-S2 后半段的数据结构设计；第 4 项完成后，才能真正实现 correctness scoring。
