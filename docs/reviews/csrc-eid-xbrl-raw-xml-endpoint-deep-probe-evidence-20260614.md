# CSRC EID XBRL Raw XML Endpoint Deep Probe Evidence

Date: 2026-06-14
Gate: `CSRC EID XBRL Raw XML Endpoint Discovery Deep Probe Gate`
Worker role: evidence worker only; not controller
Readiness state: `NOT_READY`

## 1. Scope

This evidence continues the raw XML discovery route after `CSRC EID XBRL Raw Instance Download Proof`.

Goal: inspect public EID XBRL pages, JavaScript, generated HTML references, and bounded endpoint-name candidates to determine whether a public raw XML/XBRL instance download endpoint is discoverable for concrete fund XBRL announcements.

This evidence does not parse production facts, does not validate field correctness, does not prove taxonomy compatibility, does not change `FundDocumentRepository`, does not replace the current PDF parser, and does not change release/readiness state.

## 2. Public Script Evidence

Command:

```bash
curl -sL --max-time 20 http://eid.csrc.gov.cn/fund/subpage/xbrl_affiche_subpage.js | rg -n "download|xml|XML|xbrl|XBRL|instance|\\.do|\\.json|\\.instance|href|url|showXbrlInfo"
```

Observed relevant entries:

| Line area | Observed public script fact |
|---|---|
| `171` / `237` | XBRL icon builds `xbrlHref = "/fund/disclose/instance_html_view.do?instanceid=" + data` |
| `247` | `dailyUrl = "/fund/disclose/daily_report_list_page.do"` |
| `248` | `normalUrl = "/fund/disclose/advanced_search_xbrl.do"` |
| `253` | metadata endpoint `"/fund/disclose/xbrlAfficheSearchData.json"` |
| `561` | default data endpoint `"/fund/disclose/xbrlAfficheData.json"` |
| `642-652` | `showXbrlInfo(xbrlHref)` only probes the HTML view and opens it on success |

Accepted meaning: the public XBRL announcement UI JavaScript exposes an HTML-view entry point, search/data endpoints, and no obvious raw XML download function.

Not accepted: absence of a hidden server-side endpoint.

## 3. Generated HTML Reference Evidence

Sample HTML:

```text
http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB030010/CN_50370000_000028_FB030010_20260003/CN_50370000_000028_FB030010_20260003.html
```

Command:

```bash
curl -sL --max-time 20 '<sample-html-url>' | rg -o "[A-Za-z0-9_./:-]+\\.(do|json|instance|xml|xbrl|zip|html)(\\?[^\\\"'<> ]*)?" | sort -u
```

Observed generated references:

```text
/create_assets_circs_charts.instance?instanceid=808080804ca256b9014cdb8c71327784&type=B
/create_bond_combination.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_by_trade_stock_detal_new.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common&type2=B
/create_invest_assembled_report_qimoquanzheng.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_invest_assembled_report_topten_stock.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_invest_assembled_report_zhaiquan.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_invest_assembled_report_zichan.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_main_finance_charts_new.instance?instanceid=808080804ca256b9014cdb8c71327784&type=B&fundType=6020-6030
/create_topfive_bond_detail.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
/create_topten_stock_detal.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
```

Accepted meaning: the generated HTML references chart/detail `.instance` endpoints, not raw `.xml` / `.xbrl` files.

Not accepted: these `.instance` endpoints as raw XML sources.

## 4. Generated HTML Support Script Evidence

Commands:

```bash
curl -sL --max-time 20 'http://eid.csrc.gov.cn/xbrl/REPORT/resource/instance_detail.js' | rg -n "download|xml|XML|xbrl|XBRL|instance|\\.do|\\.json|\\.instance|url|show|window.open"
curl -sL --max-time 20 'http://eid.csrc.gov.cn/xbrl/REPORT/resource/window_src.js' | rg -n "download|xml|XML|xbrl|XBRL|instance|\\.do|\\.json|\\.instance|url|show|window.open"
```

Observed facts:

- No raw XML/XBRL download endpoint was found in these support scripts by the searched patterns.
- `instance_detail.js` is primarily UI/navigation behavior for the generated HTML view.

Accepted meaning: the public support scripts inspected in this gate do not expose a raw XML download route.

Not accepted: full server-side endpoint absence.

## 5. Detail `.instance` Endpoint Probe

The generated HTML includes detail/chart endpoints under root paths such as:

```text
/create_main_finance_charts_new.instance?instanceid=808080804ca256b9014cdb8c71327784&type=B&fundType=6020-6030
/create_assets_circs_charts.instance?instanceid=808080804ca256b9014cdb8c71327784&type=B
/create_topten_stock_detal.instance?instanceid=808080804ca256b9014cdb8c71327784&type=common
```

Bounded probe result for ten referenced `.instance` paths:

- `HEAD`: returned `404 text/html; charset=utf-8` for all sampled paths.
- `GET`: returned `404 text/html; charset=utf-8` for all sampled paths.

Accepted meaning: these root `.instance` paths are not directly usable public raw XML endpoints from this environment.

Not accepted: whether they require browser context, referer, relative deployment path, or additional session state.

## 6. Bounded Endpoint-Name Candidate Probe

For sample `instanceid=22326918`, the probe tested bounded endpoint-name candidates under `/fund/disclose/`:

- `download_xbrl.do`
- `instance_show_xml_id.do`
- `instance_show_xbrl_id.do`
- `instance_show.do`
- `instance_view.do`
- `instance_xml_view.do`
- `instance_xbrl_download.do`
- `instance_html_view.do`

Parameter names tested:

- `instanceid`
- `uploadInfoId`
- `id`
- `reportPdfId`

Observed result:

- Candidate raw XML/XBRL endpoint names did not return XML-like response bodies.
- Several non-scripted candidates returned `405 text/html; charset=utf-8` in the bounded GET sweep.
- The only endpoint intentionally exposed by the public UI remains `instance_html_view.do?instanceid=<idStr>`, which is an HTML-view route.

Accepted meaning: bounded public endpoint-name probing did not discover a raw XML endpoint.

Not accepted: exhaustive endpoint nonexistence.

## 7. Classification

| Proof target | Result | Evidence |
|---|---|---|
| Public UI exposes raw XML download function | `NOT_FOUND_IN_PUBLIC_JS` | `xbrl_affiche_subpage.js` exposes only `instance_html_view.do` for XBRL icon opening. |
| Generated HTML links to raw XML/XBRL files | `NOT_FOUND_IN_GENERATED_HTML` | Extracted references contain `.instance` detail/chart endpoints, images, CSS, JS, and HTML anchors; no raw XML/XBRL file link. |
| Support scripts expose raw XML route | `NOT_FOUND_IN_SUPPORT_JS` | `instance_detail.js` / `window_src.js` pattern search did not expose raw XML download route. |
| Detail `.instance` endpoints are raw XML sources | `NOT_PROVEN` | Bounded direct HEAD/GET returned 404 for sampled root `.instance` paths. |
| Guessed `/fund/disclose/*xml/xbrl*` endpoints return raw XML | `NOT_PROVEN` | Bounded candidate probe did not return XML-like bodies. |
| Concrete raw XML direct download | `NOT_PROVEN` | No public raw XML endpoint discovered. |

## 8. Decision Impact

The raw XML route should remain blocked unless a new official endpoint is found.

The next valid implementation/evidence route is:

```text
CSRC EID XBRL HTML Structured Render Artifact Evaluation Gate
```

That route must use a separate source classification, for example:

```text
source_kind = eid_xbrl_html_render_candidate
```

It must not claim:

- raw XBRL fact access
- concrete report `schemaRef`
- XML `contextRef` / `unitRef`
- taxonomy cross-year compatibility from concrete instances
- raw XML field correctness

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
- readiness, release, PR, cleanup, or merge state changes
