# Bounded Same-report EID HTML Render Discovery Evidence

Date: 2026-06-15

Gate: `Bounded Same-report EID HTML Render Discovery Gate`

Role: evidence worker fallback executed by controller after AgentCodex approval UI blocked on bounded curl requests.

Readiness state: `NOT_READY`

## 1. Scope

This evidence checks only whether official CSRC EID XBRL HTML render can provide the missing same-report representation JSON for `004393 / 2025` (`安信企业价值优选混合A`).

It does not change source policy, parser behavior, `FundDocumentRepository`, Service/UI/Host/renderer/quality-gate access, extractor contracts, CHAPTER_CONTRACT, LLM route, readiness, release, PR, stage or commit state.

## 2. Official Requests

### 2.1 XBRL search metadata

Request:

```text
POST http://eid.csrc.gov.cn/fund/disclose/xbrlAfficheSearchData.json
body: reportTypeStatus=01
```

Accepted use: identify official XBRL report type code. Relevant observed code:

```text
FB010010 = 年度报告
```

### 2.2 Same-report XBRL search

Request:

```text
GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_xbrl.do?aoData=<json>
```

aoData:

```json
[
  {
    "name": "sEcho",
    "value": 1
  },
  {
    "name": "iColumns",
    "value": 8
  },
  {
    "name": "sColumns",
    "value": ""
  },
  {
    "name": "iDisplayStart",
    "value": 0
  },
  {
    "name": "iDisplayLength",
    "value": 20
  },
  {
    "name": "fundType",
    "value": ""
  },
  {
    "name": "reportTypeCode",
    "value": "FB010010"
  },
  {
    "name": "reportYear",
    "value": "2025"
  },
  {
    "name": "fundCompanyShortName",
    "value": ""
  },
  {
    "name": "fundCode",
    "value": "004393"
  },
  {
    "name": "fundShortName",
    "value": ""
  },
  {
    "name": "startUploadDate",
    "value": ""
  },
  {
    "name": "endUploadDate",
    "value": ""
  }
]
```

Observed response summary:

```json
{
  "iTotalRecords": 1,
  "iTotalDisplayRecords": 1,
  "aaData": [
    {
      "reportYear": "2025",
      "classificationCode": "",
      "reportDesp": "年度报告",
      "uploadDate": "2026-03-26",
      "reportSendDate": "2026-03-27",
      "uploadInfoId": 22053366,
      "fundId": 1618,
      "fundCode": "004393",
      "fundShortName": "安信企业价值优选混合",
      "fundSign": "9010-1020",
      "organName": "安信"
    }
  ]
}
```

Accepted fact: official XBRL search returns one concrete same-report row for `004393 / 2025 / 年度报告` with `uploadInfoId=22053366`.

### 2.3 Instance HTML view

Request:

```text
HEAD/GET http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=22053366
```

Observed initial response:

```text
HTTP/1.1 302 Moved Temporarily
Location: http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html
```

Final render artifact:

```text
GET http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 822146
SHA-256: 8e03dfee69eb8a17c653eb0ae5fcefd12d331820f0543bee83d7136c3cc3fb94
```

The redirect stayed within official `eid.csrc.gov.cn`.

## 3. Render Artifact Identity

| Field | Value |
|---|---|
| source_kind | `eid_xbrl_html_render_candidate` |
| fund_code | `004393` |
| fund name | `安信企业价值优选混合` |
| report year | `2025` |
| report type | `FB010010 / 年度报告` |
| idStr / uploadInfoId | `22053366` |
| fundidStr / fundId | `1618` |
| reportSendDate | `2026-03-27` |
| render URL | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html` |
| content hash | `8e03dfee69eb8a17c653eb0ae5fcefd12d331820f0543bee83d7136c3cc3fb94` |
| classification | `same_report_html_render_found_candidate_not_ready` |

## 4. Extracted Render Structure

Summary from `reports/representation-json/004393_2025_eid_html_render_full.json`:

| Metric | Value |
|---|---:|
| html bytes | 822146 |
| navigation labels | 211 |
| heading candidates | 261 |
| paragraph blocks | 750 |
| tables | 802 |
| table cells | 5526 |
| target table candidates | 14 |
| has page number | false |
| has content hash | true |
| has URL/source locator | true |

### 4.1 Navigation label samples

```text
目录全部展开
目录全部收拢
重要提示
基金简介
基金基本情况
基金产品说明
基金管理人和基金托管人
信息披露方式
其他相关资料
主要财务指标、基金净值表现及利润分配情况
主要会计数据和财务指标
基金净值表现
基金份额净值增长率及其与同期业绩比较基准收益率的比较
自基金合同生效以来基金份额累计净值增长率变动及其与同期业绩比较基准收益率变动的比较
自基金合同生效以来基金每年净值增长率及其与同期业绩比较基准收益率的比较
其他指标
过去三年基金的利润分配情况
管理人报告
基金管理人及基金经理情况
基金管理人及其管理基金的经验
```

### 4.2 Section/title samples

```text
基金简介
主要财务指标、基金净值表现及利润分配情况
基金净值表现
其他指标
过去三年基金的利润分配情况
管理人报告
基金管理人及基金经理情况
管理人对报告期内公平交易情况的专项说明
托管人报告
审计报告
年度财务报表
报表附注
买入返售金融资产
股票投资收益
债券投资收益
贵金属投资收益
衍生工具收益
或有事项、资产负债表日后事项的说明
通过关联方交易单元进行的交易
关联方报酬
```

### 4.3 Paragraph samples

```text
安信企业价值优选混合型证券投资基金 2025年年度报告
基金管理人：安信基金管理有限责任公司
基金托管人：中国银行股份有限公司
报告送出日期：2026-03-27
主要财务指标、基金净值表现及利润分配情况
过去三年基金的利润分配情况
基金管理人及基金经理情况
管理人对报告期内公平交易情况的专项说明
或有事项、资产负债表日后事项的说明
通过关联方交易单元进行的交易
```

### 4.4 Table locator samples

```json
[
  {
    "table_index": 2,
    "hit_terms": [
      "主要财务指标",
      "基金净值表现",
      "基金资产组合",
      "股票投资组合",
      "前十名股票",
      "开放式基金份额变动",
      "基金份额持有人信息"
    ],
    "row_count": 1,
    "cell_count": 1,
    "locator_candidate": {
      "render_url": "http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html",
      "html_section_id_or_anchor": null,
      "table_index_under_document": 2,
      "row_locator_rule": "row_index plus row_label_text when available",
      "column_header_path_rule": "nearest preceding header row text path when available"
    },
    "sample_rows": [
      {
        "row_index": 0,
        "cells": [
          "目录全部展开 目录全部收拢 重要提示 基金简介 基金基本情况 基金产品说明 基金管理人和基金托管人 信息披露方式 其他相关资料 主要财务指标、基金净值表现及利润分配情况 主要会计数据和财务指标 基金净值表现 基金份额净值增长率及其与同期业绩比较基准收益率的比较 自基金合同生效以来基金份额累计净值增长率变动及其与同期业绩比较基准收益率变动的比较 自基金合同生效以来基金每年净值增长率及其与同期业绩比较基准收益率的比较 其他指标 过去三年基金的利润分配情况 过去三年基金的利润分配情况 管理人报告 基金管理人及基金经理情况 基金管理人及其管理基金的经验 基金经理（或基金经理小组）及基金经理助理简介 期末兼任私募资产管理计划投资经理的基金经理同时管理的产品情况 基金经理薪酬机制 管理人对报告期内本基金运作遵规守信情况的说明 管理人对报告期内公平交易情况的专项说明 公平交易制度和控制方法 公平交易制度的执行情况 增加执行的基金经理公平交易制度执行情况及公平交易管理情况 异常交易行为的专项说明 管理人对报告期内基金的投资策略和业绩表现的说明 报告期内基金投资策略和运作分析 报告期内基金的业绩表现 管理人对宏观经济、证券市场及行业走势的简要展望 管理人内部有关本基金的监察稽核工作情况 管理人对报告期内基金估值程序等事项的说明 管理人对报告期内基金利润分配情况的说明 报告期内管理人对本基金持有人数或基金资产净值预警情形的说明 托管人报告 报告期内本基金托管人遵规守信情况声明 托管人对报告期内本基金投资运作遵规守信、净值计算、利润分配等情况的说明 托管人对本年度报告中财务信息等内容的真实、准确和完整发表意见 审计报告 审计报告基本信息 审计报告的基本内容 年度财务报表 资产负债表 利润表 净资产变动表 报表附注 基金基本情况 会计报表的编制基础 遵循企业会计准则及其他有关规定的声明 重要会计政策和会计估计 会计年度 记账本位币 金融资产和金融负债的分类 金融资产和金融负债的初始确认、后续计量和终止确认 金融资产和金融负债的估值原则 金融资产和金融负债的抵销 实收基金 损益平准金 收入/(损失)的确认和计量 费用的确认和计量 基金的收益分配政策 外币交易 分部报告 其他重要的会计政策和会计估计 会计政策和会计估计变更以及差错更正的说明 会计政策变更的说明 会计估计变更的说明 差错更正的说明 税项 重要财务报表项目的说明 银行存款 衍生金融资产/负债 买入返售金融资产 各项买入返售金融资产期末余额 期末买断式逆回购交易中取得的债券 应收利息 其他资产 应付交易费用 其他负债 实收基金 未分配利润 存款利息收入 股票投资收益 股票投资收益项目构成 股票投资收益——买卖股票差价收入 股票投资收益——赎回差价收入 股票投资收益——申购差价收入 股票投资收益——证券出借差价收入 债券投资收益 债券投资收益项目构成 债券投资收益——买卖债券差价收入 债券投资收益——赎回差价收入 债券投资收益——申购差价收入 资产支持证券投资收益 贵金属投资收益 贵金属投资收益项目构成 贵金属投资收益——买卖贵金属差价收入 贵金属投资收益——赎回差价收入 贵金属投资收益——申购差价收入 衍生工具收益 衍生工具收益——买卖权证差价收入 衍生工具收益——其他投资收益 股利收益 公允价值变动收益 其他收入 交易费用 其他费用 分部报告 或有事项、资产负债表日后事项的说明 或有事项 资产负债表日后事项 关联方关系 本报告期及上年度可比期间的关联方交易 通过关联方交易单元进行的交易 股票交易 权证交易 应支付关联方的佣金 关联方报酬 基金管理费 基金托管费 销售服务费 与关联方进行银行间同业市场的债券(含回购)交易 报告期内转融通证券出借业务发生重大关联交易事项的说明 与关联方通过约定申报方式进行的适用固定期限费率的证券出借业务的情况 与关联方通过约定申报方式进行的适用市场化期限费率的证券出借业务的情况 各关联方投资本基金的情况 报告期内基金管理人运用固有资金投资本基金的情况 报告期末除基金管理人之外的其他关联方投资本基金的情况 由关联方保管的银行存款余额及当期产生的利息收入 本基金在承销期内参与关联方承销证券的情况 其他关联交易事项的说明 利润分配情况 利润分配情况——非货币市场基金 期末本基金持有的流通受限证券 因认购新发/增发证券而于期末持有的流通受限证券 期末持有的暂时停牌等流通受限股票 期末债券正回购交易中作为抵押的债券 银行间市场债券正回购 交易所市场债券正回购 期末参与转融通证券出借业务的证券 金融工具风险及管理 风险管理政策和组织架构 信用风险 按短期信用评级列示的债券投资 按短期信用评级列示的资产支持证券投资 按短期信用评级列示的同业存单投资 按长期信用评级列示的债券投资 按长期信用评级列示的资产支持证券投资 按长期信用评级列示的同业存单投资 流动性风险 金融资产和金融负债的到期期限分析 报告期内本基金组合资产的流动性风险分析 市场风险 利率风险 利率风险敞口 利率风险的敏感性分析 外汇风险 外汇风险敞口 外汇风险的敏感性分析 其他价格风险 其他价格风险敞口 其他价格风险的敏感性分析 采用风险价值法管理风险 有助于理解和分析会计报表需要说明的其他事项 投资组合报告 期末基金资产组合情况 报告期末按行业分类的股票投资组合 报告期末按行业分类的股票投资组合 报告期末按行业分类的港股通投资股票投资组合 期末按公允价值占基金资产净值比例大小排序的股票投资明细 期末按公允价值占基金资产净值比例大小排序的所有股票投资明细 报告期内股票投资组合的重大变动 累计买入金额超出期初基金资产净值2%或前20名的股票明细 累计卖出金额超出期初基金资产净值2%或前20名的股票明细 买入股票的成本总额及卖出股票的收入总额 期末按债券品种分类的债券投资组合 期末按公允价值占基金资产净值比例大小排名的前五名债券投资明细 期末按公允价值占基金资产净值比例大小排名的所有资产支持证券投资明细 报告期末按公允价值占基金资产净值比例大小排序的前五名贵金属投资明细 期末按公允价值占基金资产净值比例大小排名的前五名权证投资明细 本基金投资股指期货的投资政策 报告期末本基金投资的国债期货交易情况说明 本期国债期货投资政策 本期国债期货投资评价 投资组合报告附注 本基金投资的前十名证券的发行主体本期受到调查以及处罚情况的说明 基金投资的前十名股票超出基金合同规定的备选股票库情况的说明 期末其他各项资产构成 期末持有的处于转股期的可转换债券明细 期末前十名股票中存在流通受限情况的说明 投资组合报告附注的其他文字描述部分 基金份额持有人信息 期末基金份额持有人户数及持有人结构 期末基金管理人的从业人员持有本基金的情况 期末基金管理人的从业人员持有本开放式基金份额总量区间的情况 发起式基金发起资金持有份额情况 开放式基金份额变动 重大事件揭示 基金份额持有人大会决议 基金管理人、基金托管人的专门基金托管部门的重大人事变动 涉及基金管理人、基金财产、基金托管业务的诉讼 基金投资策略的改变 为基金进行审计的会计师事务所情况 管理人、托管人及相关从业人员受调查或处罚等情况 基金租用证券公司交易单元的有关情况 基金租用证券公司交易单元进行股票投资及佣金支付情况 其他重大事件 影响投资者决策的其他重要信息 报告期内单一投资者持有基金份额比例达到或超过20%的情况 影响投资者决策的其他重要信息 备查文件目录 备查文件目录 存放地点 查阅方式"
        ]
      }
    ]
  },
  {
    "table_index": 28,
    "hit_terms": [
      "主要财务指标",
      "基金净值表现"
    ],
    "row_count": 1,
    "cell_count": 1,
    "locator_candidate": {
      "render_url": "http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html",
      "html_section_id_or_anchor": null,
      "table_index_under_document": 28,
      "row_locator_rule": "row_index plus row_label_text when available",
      "column_header_path_rule": "nearest preceding header row text path when available"
    },
    "sample_rows": [
      {
        "row_index": 0,
        "cells": [
          "主要财务指标、基金净值表现及利润分配情况"
        ]
      }
    ]
  },
  {
    "table_index": 34,
    "hit_terms": [
      "基金净值表现"
    ],
    "row_count": 1,
    "cell_count": 1,
    "locator_candidate": {
      "render_url": "http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html",
      "html_section_id_or_anchor": null,
      "table_index_under_document": 34,
      "row_locator_rule": "row_index plus row_label_text when available",
      "column_header_path_rule": "nearest preceding header row text path when available"
    },
    "sample_rows": [
      {
        "row_index": 0,
        "cells": [
          "基金净值表现"
        ]
      }
    ]
  },
  {
    "table_index": 633,
    "hit_terms": [
      "基金资产组合"
    ],
    "row_count": 1,
    "cell_count": 1,
    "locator_candidate": {
      "render_url": "http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50700000_004393_FB010010_20260002/CN_50700000_004393_FB010010_20260002.html",
      "html_section_id_or_anchor": null,
      "table_index_under_document": 633,
      "row_locator_rule": "row_index plus row_label_text when available",
      "column_header_path_rule": "nearest preceding header row text path when available"
    },
    "sample_rows": [
      {
        "row_index": 0,
        "cells": [
          "期末基金资产组合情况"
        ]
      }
    ]
  },
  {
    "table_index": 637,
    "hit_terms": [
      "股票投资组合"
    ],
    "row_count": 1,
    
```

## 5. Candidate Mapping

### 5.1 FundDisclosureDocument candidate

| Field | Candidate mapping |
|---|---|
| document_id | `eid-xbrl-html-render:004393:2025:22053366` |
| source_kind | `eid_xbrl_html_render_candidate` |
| owner boundary | future `fund_agent/fund/documents` / `FundDocumentRepository` internal candidate only |
| document_year | `2025` |
| render_url | official redirected HTML URL |
| content_hash | SHA-256 of final HTML body |
| sections | navigation labels plus heading candidates, not accepted schema |
| blocks | paragraph blocks and table rows/cells from generated HTML render |

### 5.2 EvidenceAnchor candidate

| Field | Candidate mapping |
|---|---|
| source_kind | `eid_xbrl_html_render_candidate` |
| document_year | `2025` |
| page_number | `null` |
| section_id | `report_type_code + html section id/heading text when available` |
| table_id | `heading text + table_index_under_document or stable DOM id when available` |
| row_locator | `row index + row label text when available` |
| column_header_path | `nearest header row text path when available` |
| note | `idStr=22053366 + redirect/render URL + content hash + report type + endpoint provenance` |

## 6. Guardrails And Non-proofs

- `not_raw_xml_download_proof`: this gate used generated HTML render only, not raw XML or raw XBRL instance.
- `not_field_correctness_proof`: extracted cells are observed HTML render text only; no PDF/source-body value comparison was performed.
- `not_taxonomy_compatibility_proof`: no schemaRef/contextRef/unitRef/taxonomy compatibility was proven.
- `not_source_truth`: HTML render remains candidate evidence, not source truth.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_repository_behavior_change`: no production `FundDocumentRepository` behavior changed.
- `no_non_eid_fallback`: no Eastmoney, CNINFO, fund-company website or other fallback was used.
- `no_production_parser_replacement`: no parser replacement is authorized.

## 7. Residuals

| Residual | Status | Next handling |
|---|---|---|
| HTML table count includes layout tables as well as data tables | accepted residual | Candidate schema must define table filtering and section/table ownership. |
| HTML has URL/hash/table locators but no PDF page numbers | accepted residual | PDF or Docling remains needed for page-number anchors and narrative/page provenance. |
| Field correctness unverified | blocked claim | Requires later same-field validation gate against accepted source-body/PDF or raw XML if proven. |
| Taxonomy/raw XML compatibility unverified | blocked claim | Requires separate raw XML endpoint or taxonomy proof gate. |
| Production ingestion contract absent | blocked claim | Requires future FundDisclosureDocument candidate schema/design gate. |

## 8. Validation

Worker/controller validation required after artifact write:

```text
python -m json.tool reports/representation-json/004393_2025_eid_html_render_full.json > /dev/null
git diff --check
```

## 9. Final Verdict

`VERDICT: SAME_REPORT_EID_HTML_RENDER_FOUND_CANDIDATE_JSON_WRITTEN_NOT_READY`
