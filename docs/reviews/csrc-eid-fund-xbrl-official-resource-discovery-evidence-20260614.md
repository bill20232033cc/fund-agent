# CSRC EID Fund XBRL Official Resource Discovery Evidence

Date: 2026-06-14
Gate: `CSRC EID XBRL Official Resource Discovery Evidence Gate`
Worker role: evidence worker only; not controller
Readiness state: `NOT_READY`

## 1. Scope

This evidence records only official-resource discovery facts for the CSRC EID public fund XBRL area:

- official XBRL standard package reachability
- official element-list reachability
- official technical-guide reachability
- official sample XML reachability and minimal XBRL shape
- public XBRL announcement JSON keys and sample rows
- one concrete `instance_html_view.do` redirect to generated XBRL HTML

This evidence does not parse production report facts, does not prove field correctness, does not prove taxonomy compatibility, does not prove raw XML instance download availability, does not change `FundDocumentRepository`, does not replace the current PDF parser, and does not change release/readiness state.

## 2. Why XBRL Is Architecturally Different From PDF

XBRL is not just another parser candidate. Relative to PDF, it has these candidate advantages:

| Dimension | XBRL advantage | Remaining limitation |
|---|---|---|
| Source structure | Facts are tagged by taxonomy elements rather than inferred from visual layout. | Need taxonomy-version and element mapping before use. |
| Units and periods | Numeric facts can carry `contextRef`, `unitRef`, `decimals`, and period semantics. | Need project-level normalization and same-source comparison. |
| Table reconstruction | Repeating facts can express rows without relying on PDF line breaks or cross-page table recovery. | Need tuple/dimension handling and row identity rules. |
| Validation | Official taxonomy, element list, technical guide, and validation rules can become deterministic intake constraints. | Need to verify current report instances against the correct DTS. |
| Failure taxonomy | Missing element, invalid context, unit mismatch, schema mismatch, and unsupported taxonomy can be classified explicitly. | Need a new XBRL-specific failure taxonomy inside Fund documents. |
| LLM boundary | XBRL can feed structured facts/gaps/anchors before any LLM writer sees data. | It likely does not replace PDF narrative evidence for all CHAPTER_CONTRACT requirements. |

Therefore, the next architecture question changes from "which PDF parser is better" to "whether official fund XBRL can become a first-class structured disclosure source inside the Fund documents boundary."

## 3. Commands And Evidence

### 3.1 Official DTS package

Command:

```bash
curl -sI http://eid.csrc.gov.cn/fund-xbrl/cfid-DTS20260309.zip
```

Observed facts:

- HTTP status: `200 OK`
- `Content-Type: application/zip`
- `Content-Length: 991830`
- `Last-Modified: Wed, 11 Mar 2026 06:10:40 GMT`

Accepted meaning: official CFID DTS package URL is reachable as a zip resource.

Not accepted: package contents, taxonomy compatibility, or production suitability.

### 3.2 Official element list

Command:

```bash
curl -sI http://eid.csrc.gov.cn/fund-xbrl/ElementList20260309.zip
```

Observed facts:

- HTTP status: `200 OK`
- `Content-Type: application/zip`
- `Content-Length: 396675`
- `Last-Modified: Tue, 10 Mar 2026 09:28:12 GMT`

Accepted meaning: official element-list URL is reachable as a zip resource.

Not accepted: element coverage for CHAPTER_CONTRACT or extractor mapping.

### 3.3 Official technical guide

Command:

```bash
curl -sI http://eid.csrc.gov.cn/fund-xbrl/CSRC_1_20260415.doc
```

Observed facts:

- HTTP status: `200 OK`
- `Content-Type: application/msword`
- `Content-Length: 233408`
- `Last-Modified: Tue, 02 Jun 2026 02:10:10 GMT`

Accepted meaning: official `CSRC_1_20260415.doc` technical-guide URL is reachable as a Word resource.

Not accepted: guide content, rule interpretation, or implementation authority.

### 3.4 Official sample XML

Commands:

```bash
curl -sI http://eid.csrc.gov.cn/fund-xbrl/example1.xml
curl -sL --max-time 20 http://eid.csrc.gov.cn/fund-xbrl/example1.xml | rg -n "<xbrl|schemaRef|<context|<unit|cfid-|contextRef|unitRef" | head -n 20
```

Observed facts:

- HTTP status: `200 OK`
- `Content-Type: text/xml; charset=ISO-88509-1`
- `Content-Length: 8135`
- Minimal XML shape includes:
  - `<xbrl ...>`
  - `<link:schemaRef ... xlink:href="http://eid.csrc.gov.cn/cn/fid/fi/ar/2007-09-01/cfid-fi-ar-2007-09-01.xsd" />`
  - `<context id="C_instant_20081231">`
  - `<unit id="U_CNY">`
  - `cfid-*` facts with `contextRef`, `unitRef`, and `decimals`

Accepted meaning: the official sample is a real XBRL instance-shaped XML document.

Not accepted: current production report XML availability or current taxonomy coverage.

### 3.5 XBRL announcement index JSON

Command:

```bash
curl -sL --max-time 20 http://eid.csrc.gov.cn/fund/disclose/indexXbrlData.json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s); console.log(Object.keys(j).join("\n")); for (const [k,v] of Object.entries(j)) { console.log(`${k}: count=${Array.isArray(v)?v.length:"non-array"}`); if (Array.isArray(v)&&v[0]) console.log(`${k}: sample=${JSON.stringify({fundcode:v[0].fundcode,fundidStr:v[0].fundidStr,idStr:v[0].idStr,reportYear:v[0].reportYear,reportTypereportDesp:v[0].reportTypereportDesp,reportSendDate:v[0].reportSendDate,newString:v[0].newString})}`); }})'
```

Observed keys and sample rows:

| JSON key | Count | Sample facts |
|---|---:|---|
| `fAXBRLReportList` | 5 | `fundcode=027705`, `idStr=22809743`, `reportYear=2026`, `reportTypereportDesp=基金合同生效公告`, `reportSendDate=2026-06-13` |
| `halfyearXBRLReportList` | 5 | `fundcode=180605`, `idStr=22086868`, `reportYear=2025`, `reportTypereportDesp=年度报告`, `reportSendDate=2026-03-31` |
| `noticeXBRLReportList` | 5 | `fundcode=009092`, `idStr=22810156`, `reportYear=2026`, `reportTypereportDesp=基金经理变更公告`, `reportSendDate=2026-06-13` |
| `seasonXBRLReportList` | 5 | `fundcode=000028`, `idStr=22326918`, `reportYear=2026`, `reportTypereportDesp=第一季度报告`, `reportSendDate=2026-04-22` |

Accepted meaning: EID exposes public XBRL announcement index JSON with concrete report rows and `idStr` identifiers.

Not accepted: full coverage, historical completeness, or fact correctness.

### 3.6 XBRL search metadata endpoint

Command:

```bash
curl -sL --max-time 20 -X POST -d 'reportTypeStatus=01' http://eid.csrc.gov.cn/fund/disclose/xbrlAfficheSearchData.json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s); console.log(Object.keys(j).join("\n")); for (const k of Object.keys(j)) { const v=j[k]; console.log(`${k}: ${Array.isArray(v)?"array len="+v.length:typeof v}`); if (Array.isArray(v)&&v[0]) console.log(`${k} sample=${JSON.stringify(v[0])}`); }})'
```

Observed facts:

- Keys include `reportType`, `fundCompanyShortName`, `netDate`, `fundTypeList`, `fundCode`, `reportTypeList`, `correctionAnnouncementCode`, `yearList`.
- `fundTypeList` has `array len=9`; sample `{"6020-6010":"股票型"}`.
- `reportTypeList` has `array len=42`; sample `{"FA":"【基金募集信息披露】"}`.
- `yearList` has `array len=30`; sample `"2026"`.

Accepted meaning: EID exposes a public XBRL search metadata endpoint with fund type, report type, and year lists.

Not accepted: the server-side search table query contract; a naive GET to `advanced_search_xbrl.do` returned a system error and is not accepted as valid query evidence.

### 3.7 Concrete instance HTML redirect

Commands:

```bash
curl -sI 'http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=22326918'
curl -sL --max-time 20 'http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=22326918' | rg -n "<title>|instance_navigation|resource/instance_detail|create_.*\.instance|基金产品概况|主要财务指标|报告期末基金资产组合情况"
```

Observed facts:

- Initial response: `302 Moved Temporarily`
- Redirect `Location`: `http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.html`
- Final HTML includes:
  - `<title>XBRL</title>`
  - `resource/instance_detail.css`
  - `id="instance_navigation"`
  - sections such as `基金产品概况`, `主要财务指标和基金净值表现`, `主要财务指标`, `报告期末基金资产组合情况`
  - generated chart/detail endpoints such as `/create_main_finance_charts_new.instance?...`, `/create_assets_circs_charts.instance?...`, `/create_topten_stock_detal.instance?...`

Accepted meaning: at least one concrete XBRL announcement `idStr` resolves to a generated public XBRL HTML report view with structured sections.

Not accepted: raw XML instance availability, XBRL fact correctness, or coverage for all report types.

### 3.8 Negative check for guessed raw XML path

Command:

```bash
curl -sI 'http://eid.csrc.gov.cn/xbrl/REPORT/XML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.xml'
```

Observed facts:

- HTTP status: `404 Not Found`
- `Content-Type: text/html; charset=utf-8`
- `Content-Length: 153`

Accepted meaning: the naive HTML-to-XML path substitution is not a valid proof of raw XML instance availability.

Not accepted: absence of raw XML by other endpoints or authenticated/internal paths.

## 4. Evidence Classification

| Question | Status | Evidence |
|---|---|---|
| Do official CSRC EID fund XBRL standard resources exist and respond? | confirmed-discovery | DTS zip, element-list zip, technical guide doc all return `200 OK`. |
| Does the site expose concrete XBRL announcement rows? | confirmed-discovery | `indexXbrlData.json` returns four lists with concrete `idStr` samples. |
| Does a concrete `idStr` resolve to a public XBRL view? | confirmed-discovery | `instanceid=22326918` redirects to `/xbrl/REPORT/HTML/...html`. |
| Is an official sample XML available and XBRL-shaped? | confirmed-discovery | `example1.xml` returns XML with `xbrl`, `schemaRef`, `context`, `unit`, and `cfid-*` facts. |
| Can raw XML for concrete report instances be downloaded by guessed path? | not-proven | Guessed `/xbrl/REPORT/XML/...xml` path returns `404`. |
| Are report facts correct? | not-proven | No production fact extraction or comparison was performed. |
| Is taxonomy compatibility across years proven? | not-proven | No DTS package contents or concrete report `schemaRef` matrix was inspected. |
| Can XBRL replace current PDF parser? | not-proven | This gate is discovery-only and does not authorize production replacement. |

## 5. Impact On Next Gate

The next gate should be `CSRC EID XBRL Instance Availability Matrix Gate`.

Minimum matrix rows:

| Report family | Source list | Minimum sample |
|---|---|---|
| Quarterly report | `seasonXBRLReportList` | at least 3 funds across current/latest year |
| Annual/interim report | `halfyearXBRLReportList` | at least 3 funds, including non-REIT if discoverable |
| Temporary announcement | `noticeXBRLReportList` | at least 3 manager-change or other announcement rows |
| Fund contract effective announcement | `fAXBRLReportList` | at least 3 rows |

The next gate should record for each sample:

- `fundcode`
- `fundidStr`
- `idStr`
- `reportYear`
- `reportTypereportDesp`
- `reportSendDate`
- `instance_html_view` status
- redirect location
- final HTML status/size
- whether the HTML contains `instance_navigation`
- whether a raw XML endpoint is discoverable

## 6. Stop Rule

Stop after this artifact. This artifact does not authorize:

- production source strategy changes
- `FundDocumentRepository` behavior changes
- direct Service/UI/Host/renderer/quality-gate access to XBRL endpoints
- parser replacement
- Docling replacement or removal
- extractor migration
- provider/LLM route changes
- live readiness, release, PR, cleanup, or merge state changes
