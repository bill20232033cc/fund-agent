# Same-report Document Representation Quality Comparison Evidence - 2026-06-14

Status: EVIDENCE_STOPPED_NOT_READY
Gate: `Same-report Document Representation Quality Comparison Evidence Gate`
Controller: AgentController
Final verdict: `VERDICT: INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY`

## 1. Scope

This evidence gate tested whether accepted EID XBRL HTML render samples, current pdfplumber PDF parsing, and Docling candidate parsing can be compared on the same report identity.

This is not a production parser implementation gate. It does not change `FundDocumentRepository`, source policy, parser behavior, extractor behavior, `EvidenceAnchor`, `CHAPTER_CONTRACT`, Service, Host, UI, renderer, quality gate, readiness, release, PR, or source truth.

Readiness remains `NOT_READY`.

## 2. Inputs Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/same-report-document-representation-quality-comparison-plan-20260614.md`
- `docs/reviews/same-report-document-representation-quality-comparison-plan-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/pdf/parser.py`

Commands executed:

```text
git branch --show-current
git status --short
rg -n ...
uv run python -c "<docling availability check>"
uv run python - <<'PY' ... AnnualReportPdfAdapter.fetch_pdf(...) ... PY
uv run python - <<'PY' ... AnnualReportPdfAdapter.parse_pdf(...) ... PY
uv run python - <<'PY' ... DocumentConverter().convert(...) ... PY
ps -axo pid,ppid,command
ps -axo pid,ppid,command | rg "DocumentConverter|docling|uv run python|cache/pdf/180605"
kill 35096
```

The Docling conversion command was stopped after it triggered RapidOCR model downloads. See section 11.

## 3. Identity Matching Matrix

Accepted EID HTML annual samples from prior evidence:

| fund_code | EID HTML idStr | fundidStr | reportYear | report type | send date | render URL status | classification |
|---|---:|---:|---:|---|---|---|---|
| `180605` | `22086868` | `14650` | `2025` | `年度报告` | `2026-03-31` | `200` via official redirect | `eid_xbrl_html_render_candidate` |
| `180105` | `22088708` | `14252` | `2025` | `年度报告` | `2026-03-31` | `200` via official redirect | `eid_xbrl_html_render_candidate` |
| `508033` | `22088693` | `13700` | `2025` | `年度报告` | `2026-03-31` | `200` via official redirect | `eid_xbrl_html_render_candidate` |

PDF acquisition through current Fund documents adapter:

| fund_code | year | fetch status | PDF source URL | fund_id | report_code | report_desp | report_name | report_send_date | source_mode | fallback |
|---|---:|---|---|---:|---|---|---|---|---|---|
| `180605` | 2025 | `ok` | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1458902` | `14650` | `FB010010` | `年度报告` | `易方达华威农贸市场封闭式基础设施证券投资基金2025年年度报告` | `2026-03-31` | `single_source_only` | `fallback_enabled=false`, `fallback_used=false` |
| `180105` | 2025 | `ok` | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1459092` | `14252` | `FB010010` | `年度报告` | `易方达广州开发区高新产业园封闭式基础设施证券投资基金2025年年度报告` | `2026-03-31` | `single_source_only` | `fallback_enabled=false`, `fallback_used=false` |
| `508033` | 2025 | `ok` | `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1458109` | `13700` | `FB010010` | `年度报告` | `易方达深高速高速公路封闭式基础设施证券投资基金2025年年度报告` | `2026-03-31` | `single_source_only` | `fallback_enabled=false`, `fallback_used=false` |

Identity classification:

| sample | classification | basis | limitation |
|---|---|---|---|
| `180605 / 2025` | `identity_match_reit_annual` | same fund code, fund id, report year, annual report type, send date, EID source family | REIT annual; not Tier A ordinary non-REIT annual |
| `180105 / 2025` | `identity_match_reit_annual` | same fund code, fund id, report year, annual report type, send date, EID source family | REIT annual; not Tier A ordinary non-REIT annual |
| `508033 / 2025` | `identity_match_reit_annual` | same fund code, fund id, report year, annual report type, send date, EID source family | REIT annual; not Tier A ordinary non-REIT annual |

No Tier A ordinary non-REIT annual `identity_match` sample was available from the accepted EID HTML evidence. Therefore this gate cannot issue a route-strength verdict.

## 4. Route Availability Matrix

| route | status | evidence |
|---|---|---|
| `eid_xbrl_html_render_candidate` | available for accepted REIT annual samples | official render pages returned `200`, `<title>XBRL</title>`, `instance_navigation`, visible section labels, and table samples in accepted evidence |
| `pdfplumber_current` | available through Fund documents adapter for `180605 / 2025` | `AnnualReportPdfAdapter.fetch_pdf()` and `parse_pdf()` succeeded on `cache/pdf/180605_2025_annual_report_eid.pdf` |
| `docling_candidate` | blocked under current evidence boundary | project `uv run python` can import Docling `2.93.0`, but first conversion triggered external RapidOCR model downloads and was stopped |

Docling is installed in the project environment, but its runtime was not contained enough for this gate.

## 5. Sample Matrix

| tier | intended sample | executed status | result |
|---|---|---|---|
| Tier A ordinary non-REIT annual | not discovered in accepted EID annual render sample | not executed | route-strength verdict blocked |
| Tier B REIT annual | `180605 / 2025` | partial execution | EID HTML and pdfplumber compared; Docling stopped |
| Tier C accepted EID HTML baseline | prior EID HTML evidence samples | reviewed | HTML route remains candidate-only |

## 6. Section Structure Comparison

EID HTML render route:

- Accepted evidence shows `instance_navigation` and visible labels for REIT annual sample `22086868`.
- Representative labels: `重要提示`, `不动产基金产品基本情况`, `主要会计数据和财务指标`, `报告期末不动产基金的资产组合情况`, `资产负债表`, `利润表`, `现金流量表`.
- Locator classification in accepted evidence: `partly_stable`.

pdfplumber current route on `180605 / 2025`:

```json
{
  "raw_text_chars": 106540,
  "section_count": 1,
  "sections": {
    "§1": {
      "title": "§1 重要提示及目录",
      "matched_rule": "fund_agent.fund.pdf.parser.locate_sections",
      "confidence": 1.0
    }
  }
}
```

Finding: for this REIT annual sample, EID HTML exposes more usable visible section/navigation labels than current pdfplumber section indexing. This is a document representation observation only, not a field correctness proof.

Docling candidate route:

- Not comparable. Conversion was stopped after RapidOCR runtime model download began.

## 7. Table Structure Comparison

EID HTML render route:

- Accepted evidence includes table row/column locator candidates for the REIT annual render.
- Representative structured sections include main accounting and financial tables such as `资产负债表`, `利润表`, `现金流量表`.

pdfplumber current route on `180605 / 2025`:

```json
{
  "table_count": 130,
  "sample_tables": [
    {
      "page_number": 6,
      "table_index": 0,
      "headers": ["基金名称", "易方达华威农贸市场封闭式基础设施证券投资基金"],
      "row_count": 18,
      "sample_rows": [
        ["基金简称", "易方达华威农贸市场REIT"],
        ["场内简称", "易方达华威市场REIT"],
        ["基金代码", "180605"]
      ]
    },
    {
      "page_number": 7,
      "table_index": 0,
      "headers": ["项目公司名称", "福州华威智慧农产品有限公司"],
      "row_count": 3
    }
  ]
}
```

Finding: current pdfplumber route extracts many table objects and page/table ordinals. It does not provide the same section-navigation identity that EID HTML render exposes in this sample.

Docling candidate route:

- Not comparable under this gate because the runtime attempted external OCR model download before producing bounded output.

## 8. Cell Locator Comparison

EID HTML render candidate locator shape from accepted evidence:

```text
render_url=http://eid.csrc.gov.cn/xbrl/REPORT/HTML/2026/FB010010/CN_50110000_180605_FB010010_20260002/CN_50110000_180605_FB010010_20260002.html
html_section_id_or_anchor=<accepted render section anchor>
heading_text=<visible section heading>
table_index_under_section=<ordinal under section>
row_index=<row ordinal>
column_header_path=<rendered column header path>
rendered_text_observed=<cell text>
```

pdfplumber current locator shape observed:

```text
pdf_path=cache/pdf/180605_2025_annual_report_eid.pdf
page_number=6
table_index=0
headers=["基金名称", "易方达华威农贸市场封闭式基础设施证券投资基金"]
row_index=0
row_label=基金简称
rendered_text_observed=易方达华威农贸市场REIT
```

Docling candidate locator shape:

- Blocked. No Docling element path, bbox, table id, or cell path was accepted from this run.

## 9. Narrative/Text Block Comparison

EID HTML render:

- Good candidate for structured render sections and tables.
- Not accepted as narrative-text replacement.

pdfplumber current:

- Produces `raw_text_chars=106540` for the sample.
- Current section indexing collapsed to a single `§1` section, limiting chapter-level narrative routing.

Docling candidate:

- Not observed because conversion was stopped.

## 10. Candidate EvidenceAnchor Mapping

EID HTML render candidate:

```text
source_kind=eid_xbrl_html_render_candidate
document_year=2025
section_id=FB010010 + html heading or anchor
page_number=null
table_id=heading + table ordinal or stable DOM/table identifier
row_locator=row index + row label + column header path
note=idStr + render URL + report type + source list
```

pdfplumber current candidate:

```text
source_kind=annual_report_pdf_current
document_year=2025
section_id=current parser section id if available
page_number=page number
table_id=page_number + table_index
row_locator=row index + row label + headers
note=FundDocumentRepository EID metadata + PDF path provenance
```

Docling candidate:

```text
source_kind=docling_candidate
document_year=2025
section_id=not_observed
page_number=not_observed
table_id=not_observed
row_locator=not_observed
note=blocked_by_runtime_model_download_required
```

No mapping is accepted as current `EvidenceAnchor` schema or source truth in this gate.

## 11. Failure Taxonomy

| failure | status | evidence | consequence |
|---|---|---|---|
| `tier_a_ordinary_annual_not_available` | observed | accepted EID annual samples are REIT annual reports | route-strength verdict blocked |
| `docling_runtime_model_download_required` | observed | `DocumentConverter().convert(...)` initiated RapidOCR model downloads from `modelscope.cn` | bounded Docling comparison stopped |
| `review_sidecar_unavailable` | observed | sub-agent spawn failed: agent thread limit reached | no content blocker; controller performed local review |
| `raw_xml_not_proven` | retained | prior XBRL evidence did not prove raw XML public download | HTML render must not be called raw XBRL |
| `field_correctness_not_proven` | retained | no PDF value comparison or raw XML context proof performed | no field correctness claim |
| `taxonomy_compatibility_not_proven` | retained | no raw XML schemaRef/taxonomy proof performed | no taxonomy compatibility claim |

Boundary incident note:

The Docling command was intended as a bounded local parse on a repository-produced PDF path. At runtime, Docling/RapidOCR attempted to download OCR model files into the project virtual environment. The process was terminated with `kill 35096`, and the tool session exited with code `143`. The downloaded model side effect is not used as evidence of parser quality and is not promoted. No repository tracked source/test/runtime file was modified by this gate.

## 12. Comparative Findings

| question | evidence-backed answer |
|---|---|
| Can EID HTML render be extracted from official EID render pages? | Yes, from accepted evidence: public EID `instance_html_view.do` redirects to official `/xbrl/REPORT/HTML/...html` render pages. |
| Is it raw XML / raw XBRL instance proof? | No. This remains `eid_xbrl_html_render_candidate`, not raw XML. |
| Is EID HTML render comparable with pdfplumber on a same-report identity? | Partly, for REIT annual samples only. Same fund/year/type/date can be matched, and EID HTML section navigation can be compared with pdfplumber section/table output. |
| Does EID HTML look better for structured table locators in this sample? | It appears stronger for section-linked structured table locator candidates, but this is REIT-only and cannot be generalized. |
| Does pdfplumber still add value? | Yes. It provides PDF page numbers, raw text and 130 table objects for `180605 / 2025`, which EID HTML render does not provide as PDF page anchors. |
| Is Docling comparable in this gate? | No. It triggered runtime model download before bounded output was produced. |
| Can this gate decide a production route? | No. There is no Tier A ordinary non-REIT annual tri-route comparison and Docling output is blocked. |

## 13. Blocked Proofs And Residuals

- `not_raw_xml_download_proof`: HTML render access does not prove raw XML direct download.
- `not_field_correctness_proof`: observed table/cell text is render output only; no field correctness claim is made.
- `not_taxonomy_compatibility_proof`: no schemaRef/contextRef/unitRef/taxonomy compatibility proof exists.
- `not_source_truth`: EID HTML render remains candidate input, not accepted source truth.
- `not_readiness_proof`: this is not release/readiness evidence.
- `no_repository_behavior_change`: no repository behavior change was implemented.
- `no_parser_replacement`: neither EID HTML nor Docling replaces current parser.
- `tier_a_missing`: ordinary non-REIT annual same-report comparison remains unproven.
- `docling_runtime_uncontained`: Docling requires a separate no-network/offline-model containment gate before quality comparison can be accepted.

## 14. Next Gate Recommendation

Recommended next gate:

```text
Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate
```

Purpose:

- define whether Docling may use OCR/model assets in this repo;
- require no-network/offline model availability before any candidate parse;
- keep Docling inside Fund documents / `FundDocumentRepository` ownership;
- select at least one ordinary non-REIT annual sample with same-report identity before route-strength comparison;
- then rerun the same-report comparison evidence gate.

Deferred entries:

- `FundDisclosureDocument Candidate Source Design Gate`
- `Narrow EID HTML vs pdfplumber REIT table-family evidence gate`
- `Docling Candidate Adapter Design Gate`
- `production parser replacement`
- `readiness/release/PR`

## 15. Final Verdict

```text
VERDICT: INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY
```

Rationale:

- EID HTML render and pdfplumber can be partially compared on REIT annual same-report samples.
- No Tier A ordinary non-REIT annual same-report sample was available from accepted evidence.
- Docling is installed but runtime is not contained; first conversion attempted external OCR model download and was stopped.
- The evidence is insufficient for a route-strength winner, implementation design, production parser replacement, source truth, or readiness claim.
