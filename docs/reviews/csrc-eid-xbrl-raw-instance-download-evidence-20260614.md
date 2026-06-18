# CSRC EID XBRL Raw Instance Download Evidence

Date: 2026-06-14
Gate: `CSRC EID XBRL Raw Instance Download Proof`
Worker role: evidence worker only; not controller
Readiness state: `NOT_READY`

## 1. Scope

This evidence attempts to prove whether concrete CSRC EID fund XBRL announcements expose raw XML/XBRL instance documents through public URLs.

It uses only public CSRC EID XBRL announcement metadata and concrete `instance_html_view.do?instanceid=<idStr>` rows. It does not parse production facts, does not validate field correctness, does not prove taxonomy compatibility, does not change `FundDocumentRepository`, does not replace the current PDF parser, and does not change release/readiness state.

## 2. Input Discovery Source

Input endpoint:

```bash
curl -sL --max-time 20 http://eid.csrc.gov.cn/fund/disclose/indexXbrlData.json
```

Accepted input lists from prior discovery:

| List | Meaning in this gate |
|---|---|
| `seasonXBRLReportList` | quarterly report samples |
| `halfyearXBRLReportList` | annual/interim report samples |
| `noticeXBRLReportList` | temporary announcement samples |
| `fAXBRLReportList` | fund contract effective announcement samples |

## 3. Method

For each sampled row:

1. Read `fundcode`, `fundidStr`, `idStr`, `reportYear`, `reportTypereportDesp`, and `reportSendDate` from `indexXbrlData.json`.
2. Request:

```text
http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=<idStr>
```

3. Record HTTP status and redirect `Location`.
4. Fetch the redirected HTML.
5. Confirm final HTML status, byte size, `<title>XBRL</title>`, and `instance_navigation`.
6. From the redirect path, test four raw-instance URL candidates:

```text
/xbrl/REPORT/XML/<year>/<report_type>/<folder>/<stem>.xml
/xbrl/REPORT/HTML/<year>/<report_type>/<folder>/<stem>.xml
/xbrl/REPORT/XBRL/<year>/<report_type>/<folder>/<stem>.xbrl
/xbrl/REPORT/<year>/<report_type>/<folder>/<stem>.xml
```

These four candidates are path-derived probes, not accepted official raw XML endpoints.

## 4. Sample Matrix

| Source list | Fund | idStr | Report year | Report type | Send date | instance view | HTML result | HTML bytes | Navigation | Raw XML candidate result |
|---|---:|---:|---:|---|---|---|---|---:|---|---|
| `seasonXBRLReportList` | `000028` | `22326918` | `2026` | 第一季度报告 | 2026-04-22 | 302 | 200 | 147507 | yes | 4/4 candidate paths returned 404 |
| `seasonXBRLReportList` | `000398` | `22326917` | `2026` | 第一季度报告 | 2026-04-22 | 302 | 200 | 127781 | yes | 4/4 candidate paths returned 404 |
| `seasonXBRLReportList` | `000757` | `22326916` | `2026` | 第一季度报告 | 2026-04-22 | 302 | 200 | 125516 | yes | 4/4 candidate paths returned 404 |
| `halfyearXBRLReportList` | `180605` | `22086868` | `2025` | 年度报告 | 2026-03-31 | 302 | 200 | 1084101 | yes | 4/4 candidate paths returned 404 |
| `halfyearXBRLReportList` | `180105` | `22088708` | `2025` | 年度报告 | 2026-03-31 | 302 | 200 | 1139744 | yes | 4/4 candidate paths returned 404 |
| `halfyearXBRLReportList` | `508033` | `22088693` | `2025` | 年度报告 | 2026-03-31 | 302 | 200 | 1078278 | yes | 4/4 candidate paths returned 404 |
| `noticeXBRLReportList` | `009092` | `22810156` | `2026` | 基金经理变更公告 | 2026-06-13 | 302 | 200 | 14891 | yes | 4/4 candidate paths returned 404 |
| `noticeXBRLReportList` | `100022` | `22810151` | `2026` | 基金经理变更公告 | 2026-06-13 | 302 | 200 | 14900 | yes | 4/4 candidate paths returned 404 |
| `noticeXBRLReportList` | `019347` | `22810146` | `2026` | 基金经理变更公告 | 2026-06-13 | 302 | 200 | 14876 | yes | 4/4 candidate paths returned 404 |
| `fAXBRLReportList` | `027705` | `22809743` | `2026` | 基金合同生效公告 | 2026-06-13 | 302 | 200 | 21627 | yes | 4/4 candidate paths returned 404 |
| `fAXBRLReportList` | `027765` | `22808159` | `2026` | 基金合同生效公告 | 2026-06-13 | 302 | 200 | 22926 | yes | 4/4 candidate paths returned 404 |
| `fAXBRLReportList` | `159065` | `22805751` | `2026` | 基金合同生效公告 | 2026-06-13 | 302 | 200 | 16572 | yes | 4/4 candidate paths returned 404 |

## 5. Concrete Redirect Examples

Quarterly sample:

```text
idStr=22326918
Location=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.html
```

Annual sample:

```text
idStr=22086868
Location=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_180605_FB010010_20260002/CN_50110000_180605_FB010010_20260002.html
```

Temporary announcement sample:

```text
idStr=22810156
Location=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FC100050/CN_50100000_009092_FC100050_20260009/CN_50100000_009092_FC100050_20260009.html
```

Fund contract effective announcement sample:

```text
idStr=22809743
Location=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FA050010/CN_50020000_027705_FA050010_20260001/CN_50020000_027705_FA050010_20260001.html
```

## 6. HTML Evidence

For `idStr=22326918`, the redirected HTML contains:

- `<title>XBRL</title>`
- `resource/instance_detail.css`
- `id="instance_navigation"`
- section labels including:
  - `基金产品概况`
  - `主要财务指标和基金净值表现`
  - `主要财务指标`
  - `报告期末基金资产组合情况`
- generated detail/chart endpoints such as:
  - `/create_main_finance_charts_new.instance?...`
  - `/create_assets_circs_charts.instance?...`
  - `/create_topten_stock_detal.instance?...`

Accepted meaning: concrete EID XBRL announcements expose generated HTML views with structured XBRL-derived sections.

Not accepted: these HTML views are not raw XML instance documents.

## 7. Raw XML Probe Result

For every sampled row, all four path-derived raw-instance candidates returned HTTP 404.

Classification:

| Proof target | Result |
|---|---|
| Concrete XBRL announcement row exists | `PASS_HTML_INSTANCE_VIEW` |
| Concrete XBRL HTML view is publicly reachable | `PASS_HTML_INSTANCE_VIEW` |
| Raw XML instance is directly downloadable by discovered or path-derived public URL | `NOT_PROVEN` |
| Field correctness from raw XML facts | `BLOCKED_BY_RAW_XML_NOT_PROVEN` |
| Taxonomy cross-year compatibility from concrete raw XML `schemaRef` | `BLOCKED_BY_RAW_XML_NOT_PROVEN` |

## 8. Downstream Gate Impact

The planned `XBRL Field Correctness Proof` cannot proceed as a raw-XML fact proof because this gate did not discover any public raw XML instance URL for concrete report rows.

The planned `Taxonomy Cross-Year Compatibility Proof` also cannot proceed as a concrete-instance `schemaRef` proof because generated HTML paths do not expose `link:schemaRef`.

Two possible next gates remain valid:

1. `CSRC EID XBRL HTML Structured Render Artifact Evaluation Gate`
   - Treat generated HTML as a structured render artifact.
   - Evaluate whether HTML tables can be parsed into candidate facts.
   - Keep classification separate from raw XML fact proof.

2. `CSRC EID XBRL Raw XML Endpoint Discovery Deep Probe Gate`
   - Search for official download endpoints beyond path-derived guesses.
   - Use only public endpoints and documented site JavaScript.
   - Stop if no endpoint is discovered.

## 9. Stop Rule

This evidence does not authorize:

- production source strategy changes
- `FundDocumentRepository` behavior changes
- direct Service/UI/Host/renderer/quality-gate access to XBRL endpoints
- parser replacement
- extractor migration
- field correctness claims
- taxonomy compatibility claims
- provider/LLM route changes
- live readiness, release, PR, cleanup, or merge state changes
