# Correctness Golden Answer Template

## Instructions

- 数据源：以 `report_year` 对应年份的年度报告原文为准
- 每只基金标题下用 `golden-answer-metadata` 标注基金级 `report_year`
- `expected_value`：extractor 应返回的精确字符串值，与 PDF 原文一致
- `confidence`：`high`（PDF 明确）/ `medium`（需判断）/ `low`（PDF 模糊）
- `source`：标注来源页码，如 `年报2024 §3 page-8`
- 当前 slice 未实现的字段标 `—`，不填 expected_value
- 每只基金独立一张表，填完后用于构建 golden set JSON

---

## 004393 安信企业价值优选混合A（国内股票类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| index_profile | benchmark_text | | | |
| index_profile | benchmark_identity_status | | | |
| index_profile | benchmark_index_name | | | |
| index_profile | source_tier | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |

---

## 000216 华安黄金ETF联接A（黄金类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |

---

## 007721 天弘标普500发起(QDII-FOF)A（海外股票类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |

---

## 007360 易方达中短期美元债债券(QDII)A(人民币份额)（海外债券/稳健类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |

---

## 006597 国泰利享中短债债券A（国内债券类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |

---

## 001548 天弘上证50ETF联接A（国内股票类）

```golden-answer-metadata
report_year: 2024
```

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | | | |
| basic_identity | fund_code | | | |
| basic_identity | management_company | | | |
| basic_identity | custodian | | | |
| basic_identity | inception_date | | | |
| product_profile | investment_objective | | | |
| product_profile | investment_scope | | | |
| product_profile | style_positioning | | | |
| benchmark | benchmark_name | | | |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | | | |
| nav_benchmark_performance | nav_growth_rate | | | |
| nav_benchmark_performance | benchmark_return_rate | | | |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | | | |
| manager_strategy_text | market_outlook | | | |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | | | |
| manager_alignment | employee_holding | | | |
| holder_structure | institutional_holder | | | |
| holder_structure | individual_holder | | | |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | | | |
| share_change | ending_share | | | |
| share_change | net_change | | | |
