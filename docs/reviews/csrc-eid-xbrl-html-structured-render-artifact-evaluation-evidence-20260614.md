# CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence

Date: 2026-06-14

Gate: `CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate`

Worker role: evidence worker output corrected by controller after bounded official EID retry

Verdict: `HTML_RENDER_ARTIFACT_AVAILABLE_PARTLY_STABLE_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope

This artifact records bounded live HTTP evidence for official CSRC EID XBRL HTML render artifacts as `eid_xbrl_html_render_candidate`.

Authorized objective:

- fetch official EID `indexXbrlData.json`;
- select 3 rows each from `seasonXBRLReportList`, `halfyearXBRLReportList`, `noticeXBRLReportList`, and `fAXBRLReportList`;
- request each concrete `instance_html_view.do?instanceid=<idStr>`;
- record redirect and final HTML render metadata;
- locally parse downloaded JSON/HTML for navigation labels, section/title samples, table samples, paragraph samples, hashes, and locator candidates;
- write evidence only, with no production behavior changes.

This artifact does not implement a parser, does not call production `FundDocumentRepository`, does not access PDF/provider/LLM/analyze/checklist/golden/readiness/release/PR paths, and does not enter another gate.

## 2. Official Request URLs

Index JSON:

```text
http://eid.csrc.gov.cn/fund/disclose/indexXbrlData.json
```

Instance view URL pattern:

```text
http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=<idStr>
```

Commands used were bounded official EID HTTP `HEAD` / `GET` style requests via `curl` and local HTML/JSON parsing. No production repository/source/parser/PDF/provider/LLM/readiness/release command was run.

## 3. Index JSON Evidence

| Field | Value |
|---|---|
| request URL | `http://eid.csrc.gov.cn/fund/disclose/indexXbrlData.json` |
| HTTP status | `200 OK` |
| content-type | `application/json` |
| content-length | `12721` |
| SHA-256 | `78124698b77230647a7156e89c6c0138f41fc77d6f725a864eaa1d42fe8da56c` |
| list keys | `fAXBRLReportList`, `halfyearXBRLReportList`, `noticeXBRLReportList`, `seasonXBRLReportList` |
| row counts in current JSON | each observed list has `5` rows |

`halfyearXBRLReportList` current first five rows are all REIT annual reports. The plan requirement "include non-REIT if discoverable" is therefore not satisfied from the current JSON sample window; this remains a residual, not a blocker for HTML render availability.

## 4. Required Sample Matrix

| Source list | Rows required | Rows executed | Status |
|---|---:|---:|---|
| `seasonXBRLReportList` | 3 | 3 | `executed` |
| `halfyearXBRLReportList` | 3 | 3 | `executed_reit_only_current_json` |
| `noticeXBRLReportList` | 3 | 3 | `executed` |
| `fAXBRLReportList` | 3 | 3 | `executed` |

## 5. Per-row Availability Matrix

All 12 current rows resolved from `instance_html_view.do?instanceid=<idStr>` to official `eid.csrc.gov.cn/xbrl/REPORT/HTML/...html` render pages. Each final HTML response returned `200`, `text/html; charset=utf-8`, `<title>XBRL</title>`, and `instance_navigation`.

| Source list | fundcode | fundidStr | idStr | reportYear | report type | send date | instance status | final status | bytes | contains XBRL title | contains navigation | classification |
|---|---|---:|---:|---:|---|---|---|---|---:|---|---|---|
| `seasonXBRLReportList` | `000028` | `3383` | `22326918` | `2026` | `第一季度报告` | `2026-04-22` | `302` | `200` | 147507 | yes | yes | `eid_xbrl_html_render_candidate` |
| `seasonXBRLReportList` | `000398` | `3554` | `22326917` | `2026` | `第一季度报告` | `2026-04-22` | `302` | `200` | 127781 | yes | yes | `eid_xbrl_html_render_candidate` |
| `seasonXBRLReportList` | `000757` | `3710` | `22326916` | `2026` | `第一季度报告` | `2026-04-22` | `302` | `200` | 125516 | yes | yes | `eid_xbrl_html_render_candidate` |
| `halfyearXBRLReportList` | `180605` | `14650` | `22086868` | `2025` | `年度报告` | `2026-03-31` | `302` | `200` | 1084101 | yes | yes | `eid_xbrl_html_render_candidate` |
| `halfyearXBRLReportList` | `180105` | `14252` | `22088708` | `2025` | `年度报告` | `2026-03-31` | `302` | `200` | 1139744 | yes | yes | `eid_xbrl_html_render_candidate` |
| `halfyearXBRLReportList` | `508033` | `13700` | `22088693` | `2025` | `年度报告` | `2026-03-31` | `302` | `200` | 1078278 | yes | yes | `eid_xbrl_html_render_candidate` |
| `noticeXBRLReportList` | `009092` | `7511` | `22810156` | `2026` | `基金经理变更公告` | `2026-06-13` | `302` | `200` | 14891 | yes | yes | `eid_xbrl_html_render_candidate` |
| `noticeXBRLReportList` | `100022` | `119` | `22810151` | `2026` | `基金经理变更公告` | `2026-06-13` | `302` | `200` | 14900 | yes | yes | `eid_xbrl_html_render_candidate` |
| `noticeXBRLReportList` | `019347` | `13648` | `22810146` | `2026` | `基金经理变更公告` | `2026-06-13` | `302` | `200` | 14876 | yes | yes | `eid_xbrl_html_render_candidate` |
| `fAXBRLReportList` | `027705` | `17101` | `22809743` | `2026` | `基金合同生效公告` | `2026-06-13` | `302` | `200` | 21627 | yes | yes | `eid_xbrl_html_render_candidate` |
| `fAXBRLReportList` | `027765` | `17128` | `22808159` | `2026` | `基金合同生效公告` | `2026-06-13` | `302` | `200` | 22926 | yes | yes | `eid_xbrl_html_render_candidate` |
| `fAXBRLReportList` | `159065` | `17011` | `22805751` | `2026` | `基金合同生效公告` | `2026-06-13` | `302` | `200` | 16572 | yes | yes | `eid_xbrl_html_render_candidate` |

## 6. Redirect Locations And Content Hashes

| idStr | final render URL | SHA-256 |
|---:|---|---|
| `22326918` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.html` | `45c29f9014b4e7d776ea03a9a77eb1c16121367adec57381d5df37f0e5ca355d` |
| `22326917` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000398_FB030010_20260003/CN_50370000_000398_FB030010_20260003.html` | `c77681037b3846018325db34a6608579b5056ca724631fad057b16070a74a73a` |
| `22326916` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000757_FB030010_20260003/CN_50370000_000757_FB030010_20260003.html` | `a5019810c5111231ee8478546e623b3aaf290b789a9a757e15cc49da7bb8b2f1` |
| `22086868` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_180605_FB010010_20260002/CN_50110000_180605_FB010010_20260002.html` | `aa7035ad0d20a4bad7ada9bd260b3390d27126387ac37d9ddb7c1c27e9d55448` |
| `22088708` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_180105_FB010010_20260002/CN_50110000_180105_FB010010_20260002.html` | `e03c1b8d56756d2e1b9132cf1c6b603c8d30e9acd20968876950fc692463d521` |
| `22088693` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_508033_FB010010_20260002/CN_50110000_508033_FB010010_20260002.html` | `59d049a9056f7bd801611665e59496895d82d29246fa2f4b4c351f51f411d5e9` |
| `22810156` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FC100050/CN_50100000_009092_FC100050_20260009/CN_50100000_009092_FC100050_20260009.html` | `a650ad8f894121d3b390ebd63264d541ef1bc30a4cdd1151d47cc1fa1c14f4d2` |
| `22810151` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FC100050/CN_50100000_100022_FC100050_20260022/CN_50100000_100022_FC100050_20260022.html` | `2fa19c6a33e3ffca12072dbec1082ac3fd5ed60ab82059432dcbb4ab7617b210` |
| `22810146` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FC100050/CN_50100000_019347_FC100050_20260016/CN_50100000_019347_FC100050_20260016.html` | `a9684a497ac6b0addd698ece1d5884a6626307699e4a4b714fdebfea2fe545fc` |
| `22809743` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FA050010/CN_50020000_027705_FA050010_20260001/CN_50020000_027705_FA050010_20260001.html` | `01ee149b676ad881df085dfc36da4ff1fdaba621b7b37b3204770cde91ffd1b6` |
| `22808159` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FA050010/CN_50080000_027765_FA050010_20260001/CN_50080000_027765_FA050010_20260001.html` | `41018da9d3a945b0c40c069024f5fd93924efa83101350744f79c0008c999cb1` |
| `22805751` | `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FA050010/CN_50290000_159065_FA050010_20260001/CN_50290000_159065_FA050010_20260001.html` | `04c691e8994e2962513f61a8aeb77f1f48ca1e0fc1f9a439acdb1fc1a9fb034c` |

## 7. Navigation And Section Labels

Observed `instance_navigation` is extractable in all 12 samples. Representative labels:

| Sample | Major visible section labels |
|---|---|
| `22326918` quarterly report | `重要提示`, `基金基本情况`, `主要财务指标`, `基金份额净值增长率及其与同期业绩比较基准收益率的比较`, `报告期末基金资产组合情况`, `开放式基金份额变动` |
| `22086868` REIT annual report | `重要提示`, `不动产基金产品基本情况`, `主要会计数据和财务指标`, `报告期末不动产基金的资产组合情况`, `资产负债表`, `利润表`, `现金流量表` |
| `22810156` fund manager change notice | `公告基本信息`, `离任基金经理的相关信息`, `其他需要说明的事项` |
| `22809743` fund contract effective announcement | `公告基本信息`, `基金募集情况`, `其他需要提示的事项`, `发起式基金发起资金持有份额情况` |

Locator stability classification:

- quarterly report: `partly_stable` because navigation anchors and headings are extractable, but section-specific table selection still needs tested normalization rules;
- REIT annual report: `partly_stable` because many structured sections exist, but REIT-specific labels differ from ordinary fund reports and current sample did not include a non-REIT annual report;
- temporary announcement: `stable_for_notice_family_candidate` for the observed manager-change notice family;
- fund contract effective announcement: `stable_for_fA_family_candidate` for the observed contract-effective notice family.

## 8. Table Samples And Locator Candidates

Representative table samples show extractable row/column structure. These are render artifact cell samples only, not field correctness proof.

### Quarterly Report `22326918`

Candidate locator:

```text
render_url=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.html
html_section_id_or_anchor=tabItem2_mainFinanceItem
heading_text=主要财务指标
table_index_under_section=2
row_index=1
column_header_path=华富安鑫债券A(元) 2026-01-01 - 2026-03-31
cell_text=638,365.46
```

Observed rows:

| Row | Cells |
|---:|---|
| 0 | `主要财务指标` / `主基金(元)` / `华富安鑫债券A(元) 2026-01-01 - 2026-03-31` / `华富安鑫债券C(元) 2026-01-01 - 2026-03-31` |
| 1 | `1.本期已实现收益` / `638,365.46` / `1,514,389.43` |
| 2 | `2.本期利润` / `-1,594,438.81` / `-631,176.55` |

Additional locator:

```text
html_section_id_or_anchor=tabItem4_assetsCircs
heading_text=报告期末基金资产组合情况
table_index_under_section=1
row_index=1
column_header_path=金额（元）
cell_text=34,117,026.62
```

### REIT Annual Report `22086868`

Candidate locator:

```text
render_url=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_180605_FB010010_20260002/CN_50110000_180605_FB010010_20260002.html
html_section_id_or_anchor=tabItem1_fundIntro9
heading_text=主要会计数据和财务指标
table_index_under_section=1
row_index=1
column_header_path=2025年01月13日 - 2025年12月31日
cell_text=108,207,131.86
```

Observed rows:

| Row | Cells |
|---:|---|
| 0 | `期间数据和指标` / `2025年01月13日 - 2025年12月31日` |
| 1 | `本期收入` / `108,207,131.86` |
| 2 | `本期净利润` / `34,594,265.02` |

Additional locator:

```text
html_section_id_or_anchor=tabItem1_fundIntro51
heading_text=资产负债表
table_index_under_section=3
row_index=2
column_header_path=本期末 2025-12-31
cell_text=14,647,732.73
```

### Temporary Announcement `22810156`

Candidate locator:

```text
render_url=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FC100050/CN_50100000_009092_FC100050_20260009/CN_50100000_009092_FC100050_20260009.html
html_section_id_or_anchor=tabItem0_fundIntro
heading_text=公告基本信息
table_index_under_section=1
row_index=2
column_header_path=value
cell_text=009092
```

Observed rows:

| Row | Cells |
|---:|---|
| 0 | `基金名称` / `富国新材料新能源混合型证券投资基金` |
| 1 | `基金简称` / `富国新材料新能源混合` |
| 2 | `基金主代码` / `009092` |

### Fund Contract Effective Announcement `22809743`

Candidate locator:

```text
render_url=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FA050010/CN_50020000_027705_FA050010_20260001/CN_50020000_027705_FA050010_20260001.html
html_section_id_or_anchor=tabItem0_jiJinMuJiQingKuangBeiZhu
heading_text=发起式基金发起资金持有份额情况
table_index_under_section=2
row_index=1
column_header_path=持有份额总数
cell_text=10,000,750.00
```

Observed rows:

| Row | Cells |
|---:|---|
| 0 | `项目` / `持有份额总数` / `持有份额占基金总份额比例` / `发起份额总数` / `发起份额占基金总份额比例` / `发起份额承诺持有期限` |
| 1 | `基金管理人固有资金` / `10,000,750.00` / `37.95%` / `10,000,000.00` / `37.94%` / `自合同生效之日起不少于3年` |
| 2 | `基金管理人高级管理人员` / `-%` / `-%` |

## 9. Paragraph / Narrative Samples

The HTML render pages are not binary-only or image-only. They contain text nodes, navigation labels, section headings, table cells and note-like paragraphs.

Representative extracted paragraph-like text:

- Quarterly report `22326918`: note under main financial indicators begins with `注：1、本期已实现收益指基金本期利息收入、投资收益...`.
- REIT annual report `22086868`: note under major metrics begins with `注：1.本表中的各项数据和指标均指合并财务报表层面的数据...`.
- Fund contract effective announcement `22809743`: note under fundraising section begins with `注：1、本公司高级管理人员、基金投资和研究部门负责人认购本基金份额总量的数量区间...`.

This proves text extraction potential from the render artifact. It does not prove full CHAPTER_CONTRACT narrative coverage.

## 10. Candidate Mapping To `FundDisclosureDocument`

Status: `candidate_supported_for_design_planning_only`

| `FundDisclosureDocument` candidate field | Candidate HTML render mapping | Evidence status |
|---|---|---|
| `source_kind` | `eid_xbrl_html_render_candidate` | accepted candidate classification |
| document identity | `idStr`, `fundcode`, `fundidStr`, report type, report year, send date from official JSON | supported by current JSON |
| official render URL | final `/xbrl/REPORT/HTML/.../*.html` redirect target | supported by current 12-row matrix |
| content identity | final HTML byte size and SHA-256 | supported by current 12-row matrix |
| sections | navigation labels / anchor ids / section headings | supported as candidate, partly stable |
| tables | HTML table boundaries and row/column locator candidates | supported as candidate, partly stable |
| narrative blocks | paragraph/text blocks if present | supported as candidate, coverage not proven |
| source caveat | render artifact below fact truth | accepted guard only |

No production `FundDisclosureDocument` schema change or implementation is authorized by this artifact.

## 11. Candidate Mapping To `EvidenceAnchor`

Status: `candidate_supported_for_design_planning_only`

| `EvidenceAnchor` field | Candidate HTML render mapping | Evidence status |
|---|---|---|
| `source_kind` | `eid_xbrl_html_render_candidate` | candidate only |
| `document_year` | `reportYear` from official JSON, with report period if render text exposes one | candidate supported |
| `section_id` | normalized section heading/navigation id such as `tabItem2_mainFinanceItem` | candidate supported |
| `page_number` | `null` unless later official render-to-PDF relation is proven | candidate caveat |
| `table_id` | heading text plus table ordinal under section | candidate supported, needs normalization |
| `row_locator` | row index plus row label plus optional DOM/table path | candidate supported, needs stability tests |
| `column_header_path` | normalized header cell path from table row/column context | candidate supported, needs merged-cell handling |
| `note` | idStr, redirect location, render URL, content hash, report type and source list | candidate supported |

This mapping is weaker than raw XML `contextRef`, `unitRef`, QName and `schemaRef` proof. It may be sufficient for structured table extraction if locator stability is accepted in a later design gate. PDF remains needed for narrative text, page-number anchors and non-XBRL disclosure coverage unless later evidence proves otherwise.

## 12. Blocked Proofs And Residuals

| Proof / residual | Status | Reason |
|---|---|---|
| Public HTML render access | `proven_for_12_current_samples` | Current official JSON rows redirect to official HTML render pages and return final 200. |
| Stable navigation extraction | `partly_proven` | `instance_navigation` exists in all 12 samples; labels differ by report family. |
| Stable table row/column locators | `partly_proven` | Candidate row/column structures extract in representative samples; robust merged-cell/hidden-table handling is not proven. |
| Non-REIT annual/interim sample | `not_discovered_in_current_halfyear_json_sample` | Current `halfyearXBRLReportList` first five rows are REIT annual reports. |
| Ordinary non-REIT annual fund HTML render | `not_proven_in_this_gate` | Requires later sample discovery beyond current first-five list evidence. |
| Full narrative coverage | `not_proven` | Text exists, but CHAPTER_CONTRACT coverage is not evaluated. |
| Raw XML direct download | `not_proven` | Not part of this HTML render evidence; prior raw XML probes remain blocked. |
| Field correctness | `not_proven` | Rendered cell extraction was not validated against authoritative field definitions or independent source. |
| Taxonomy compatibility | `not_proven` | No raw instance `schemaRef`, DTS, namespace or cross-year taxonomy proof. |
| Production implementation | `not_authorized` | Evidence-only gate. |
| Release/readiness | `NOT_READY` | No readiness claim accepted. |

## 13. Explicit Guard Labels

- `not_raw_xml_download_proof`: this artifact did not fetch any concrete raw XML endpoint and does not claim raw XML direct download availability.
- `not_field_correctness_proof`: this artifact did not validate any rendered value against an authoritative field definition or independent source.
- `not_taxonomy_compatibility_proof`: this artifact did not inspect concrete raw instance `schemaRef`, DTS linkage, namespaces or cross-year taxonomy compatibility.
- `not_source_truth`: HTML/JSON/render outputs are not fund fact truth until projected through accepted extractor / section fact / EvidenceAnchor / fail-closed boundaries in a future reviewed gate.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_repository_behavior_change`: no production `FundDocumentRepository`, source, parser, extractor, Service, UI, Host, renderer, quality gate or LLM behavior changed.

## 14. Evidence Verdict

`HTML_RENDER_ARTIFACT_AVAILABLE_PARTLY_STABLE_NOT_READY`

The official EID HTML render route is publicly reachable for the current 12-row matrix and produces parseable HTML pages with navigation sections, headings, table cells, paragraph-like text, byte sizes and content hashes. This supports continuing to a candidate documents-layer design/planning gate.

The evidence is still partial. It does not prove raw XML availability, field correctness, taxonomy compatibility, ordinary non-REIT annual coverage, full narrative coverage, production parser replacement, repository behavior change, source truth, readiness, release readiness, or PR readiness.
