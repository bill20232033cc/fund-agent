# Golden Answer 填写指南

## 目标

为 6 只 golden set 基金填写 correctness expected_value，用于验证 extractor 抽取结果是否正确。

## Golden Set 基金

| 序号 | 基金代码 | 基金名称 | 类别 |
|---|---|---|---|
| 1 | 004393 | 安信企业价值优选混合A | 国内股票类 |
| 2 | 000216 | 华安黄金ETF联接A | 黄金类 |
| 3 | 007721 | 天弘标普500发起(QDII-FOF)A | 海外股票类 |
| 4 | 007360 | 易方达中短期美元债债券(QDII)A | 海外债券/稳健类 |
| 5 | 006597 | 国泰利享中短债债券A | 国内债券类 |
| 6 | 001548 | 天弘上证50ETF联接A | 国内股票类 |

## 数据源

- **主源**：`report_year` 对应年份的年度报告原文（extractor 解析的就是年报原文）
- **辅源**：仅用于人工交叉验证数值型字段；不能替代年报原文作为 `source`

## 填写步骤

### Step 1: 准备年报 PDF

准备每只基金 `report_year` 对应年份的年度报告原文。

### Step 2: 打开模板

模板文件：`docs/golden-answer-template.md`

每只基金一张表，共 6 张表。

### Step 3: 确认 report_year

每个基金标题下必须先确认基金级 metadata：

````markdown
```golden-answer-metadata
report_year: 2024
```
````

`report_year` 是 strict golden answer 身份键的一部分。同一基金不同年份可并存，但不能把其他年份的行复用为当前年份 correctness 证据。历史 reviewed Markdown 如果缺少 metadata，只按 legacy 2024 兼容解析。

### Step 4: 逐行填写

每行有 5 列：

| 列名 | 含义 | 示例 |
|---|---|---|
| field | 字段名 | nav_benchmark_performance |
| sub_field | 子字段名 | nav_growth_rate |
| expected_value | PDF 原文中的精确值 | 17.32% |
| confidence | 把握程度 | high / medium / low |
| source | 数据来源页码 | 年报2024 §3 page-8 |

### Step 5: 标注 confidence

- `high`：PDF 原文明确，无歧义
- `medium`：需要判断（如多列选哪一列、文本截取范围）
- `low`：PDF 披露模糊或格式异常

### Step 6: 标记跳过行

当前 slice 未实现的字段已标 `—`，跳过即可：
- fee_schedule（费率）
- investor_return（投资者收益率）
- turnover_rate（换手率）
- holdings_snapshot（持仓快照）

### Step 7: 交付

填完后告诉我，我来：
1. 转成 golden set JSON
2. 接入 extraction-score 的 correctness 评分
3. 跑 6 只基金的 snapshot 对比

## 各字段填写参考

### basic_identity（基础身份）

从年报 §1/§2 抽取：
- fund_name：基金全称
- fund_code：基金代码
- management_company：基金管理人
- custodian：基金托管人
- inception_date：基金合同生效日

### product_profile（产品概况）

从年报 §2 抽取：
- investment_objective：投资目标
- investment_scope：投资范围

### benchmark（业绩基准）

从年报 §2 抽取：
- benchmark_name：业绩比较基准名称

### nav_benchmark_performance（净值表现）

从年报 §3 净值表现表抽取：
- nav_growth_rate：过去一年份额净值增长率（如 17.32%）
- benchmark_return_rate：过去一年业绩比较基准收益率（如 14.45%）

### manager_strategy_text（策略文本）

从年报 §4 管理人报告抽取：
- strategy_summary：报告期内基金投资策略和运作分析正文
- style_positioning：风格定位（如有）
- market_outlook：后市展望正文

注意：填写 PDF 中的原文段落，不要缩写或改写。

### manager_alignment（利益一致性）

从年报 §9 抽取：
- manager_holding：基金经理持有份额区间（如 0~10 万份）
- employee_holding：从业人员持有份额和比例（如 10,000.00 份, 0.01%）

### holder_structure（持有人结构）

从年报 §9 持有人结构表抽取：
- institutional_holder：机构投资者持有比例（如 86.46%）
- individual_holder：个人投资者持有比例（如 13.54%）

### share_change（份额变动）

从年报 §10 份额变动表抽取：
- beginning_share：期初基金份额总额（如 27,666,410.41 份）
- ending_share：期末基金份额总额（如 149,565,740.00 份）
- net_change：净变动（如 121,899,329.59 份）

注意：net_change = ending_share - beginning_share，保留两位小数，带千分位逗号。
