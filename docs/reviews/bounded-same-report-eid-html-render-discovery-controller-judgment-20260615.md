# Bounded Same-report EID HTML Render Discovery Controller Judgment

Date: 2026-06-15

Gate: `Bounded Same-report EID HTML Render Discovery Gate`

Role: controller

Verdict: `ACCEPT_SAME_REPORT_EID_HTML_RENDER_FOUND_READY_FOR_HYBRID_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_PLANNING_GATE_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the bounded live discovery gate authorized after the full annual-report representation JSON evidence gate.

Accepted artifacts:

- Evidence: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md`
- EID HTML render full JSON: `reports/representation-json/004393_2025_eid_html_render_full.json`
- DS review: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-review-ds-20260615.md`
- MiMo review: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-review-mimo-20260615.md`

This judgment does not authorize raw XML claims, field correctness claims, taxonomy compatibility claims, source-truth promotion, production parser replacement, `FundDocumentRepository` behavior changes, source policy changes, Service/UI/Host/renderer/quality-gate direct XBRL access, readiness/release/PR state changes, staging, committing, pushing or merging.

## 2. Accepted Current Facts

| Fact | Disposition |
|---|---|
| Official EID XBRL search metadata exposes `FB010010 = 年度报告`. | ACCEPT |
| Official EID XBRL search for `fundCode=004393`, `reportYear=2025`, `reportTypeCode=FB010010` returned exactly one same-report row. | ACCEPT |
| The matched row has `uploadInfoId=22053366`, `fundId=1618`, `fundCode=004393`, `fundShortName=安信企业价值优选混合`, `reportYear=2025`, `reportDesp=年度报告`, `reportSendDate=2026-03-27`. | ACCEPT |
| `instance_html_view.do?instanceid=22053366` returned a 302 redirect to official `eid.csrc.gov.cn/xbrl/REPORT/HTML/...` render URL. | ACCEPT |
| Final HTML returned `200`, `text/html; charset=utf-8`, byte size `822146`, SHA-256 `8e03dfee69eb8a17c653eb0ae5fcefd12d331820f0543bee83d7136c3cc3fb94`, `<title>XBRL</title>` and `instance_navigation`. | ACCEPT |
| `reports/representation-json/004393_2025_eid_html_render_full.json` is a valid candidate full representation JSON with navigation labels, heading candidates, paragraph blocks, tables and locator candidates. | ACCEPT |

The accepted source classification remains `eid_xbrl_html_render_candidate`. This is generated HTML render evidence, not raw XBRL/XML instance proof.

## 3. Review Disposition

| Source | Finding | Controller disposition | Rationale |
|---|---|---|---|
| DS | Verdict `PASS`; no blocking findings. | ACCEPT | DS verified same-report scope, EID-only requests, JSON provenance, guardrails and validation. |
| DS residual | HTML table count includes layout tables; no PDF page numbers; field correctness/taxonomy/source truth remain unverified. | ACCEPT_AS_RESIDUAL | These are already in evidence residuals and define future schema/validation work. |
| MiMo F1 | Evidence summary table uses semantic labels instead of exact JSON `summary_metrics` keys. | ACCEPT_AS_NONBLOCKING_RESIDUAL | JSON content is valid and complete; future evidence should include exact JSON field names or a mapping column. |
| MiMo F2 | AgentCodex approval block and controller live fact collection could be described more explicitly. | ACCEPT_AS_NONBLOCKING_RESIDUAL | Evidence honestly records controller fallback after AgentCodex approval UI blocked; future evidence should state direct controller fact collection more explicitly. |
| MiMo review note | Review text lists one blocked-claims item as `no_funddisclosuredocument_schema`; JSON actually carries `no_page_number_anchor`. | ACCEPT_AS_REVIEW_TEXT_RESIDUAL | This is a reviewer wording mismatch, not an evidence artifact defect. Core blocked claims are present in the JSON and evidence. |

No blocking findings remain.

## 4. Blocked Claims

The following claims remain blocked:

- raw XML direct download;
- raw XBRL instance truth;
- `schemaRef` / `contextRef` / `unitRef` fact provenance;
- field correctness;
- taxonomy compatibility;
- source truth;
- production `FundDisclosureDocument` schema;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- Service/UI/Host/renderer/quality-gate direct XBRL endpoint access;
- readiness/release/PR readiness.

## 5. Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| EID HTML render has many layout tables mixed with data tables. | Fund documents/schema owner | Hybrid candidate source planning must define filtering, section ownership and table-family pilot boundaries. |
| EID HTML render has URL/hash/table locators but no PDF page numbers. | Fund documents/EvidenceAnchor owner | Hybrid plan must preserve page-number null for EID HTML and combine with PDF/Docling where page anchors are required. |
| Docling/pdfplumber/EID JSONs are representation evidence, not field truth. | Fund documents/extractor owner | Later validation gates must compare fields before CHAPTER_CONTRACT consumption. |
| Raw XML endpoint remains unproven. | Fund documents/source research owner | Keep raw XML proof separate and blocked unless a public endpoint is discovered. |
| AgentCodex could not complete live requests because its approval UI blocked. | Controller/process owner | Record as process residual; does not invalidate controller-collected bounded live evidence. |

## 6. Controller Decision

The bounded same-report EID HTML render discovery gate is accepted.

The previous full-JSON blocker is closed for `004393 / 2025`: all three representation routes now have same-report JSON artifacts:

- Docling full JSON;
- pdfplumber full JSON;
- EID XBRL HTML render full candidate JSON.

This does not mean the three routes are equally suitable or production-ready. It only means the missing EID HTML same-report render artifact is now available for planning.

Primary next gate:

`Hybrid FundDisclosureDocument Candidate Source Planning Gate`

The next gate is planning-only unless separately scoped otherwise. It must decide how to combine or route Docling, pdfplumber and EID HTML render candidate representations inside the Fund documents boundary, while preserving `NOT_READY` and all blocked claims above.

## 7. Deferred Entries

- FundDisclosureDocument Candidate Source No-live Implementation Planning Gate.
- Extractor Projection Over Document Representation Planning Gate.
- EID HTML field correctness validation gate.
- Raw XML endpoint proof gate.
- Taxonomy compatibility gate.
- Docling section/paragraph semantics planning gate.
- Pdfplumber full representation export contract planning gate.
- Readiness/release/PR gates.

## 8. Validation

Controller validation after evidence and reviews:

```text
python -m json.tool reports/representation-json/004393_2025_eid_html_render_full.json > /dev/null
git diff --check
```

Both commands passed before this judgment was written.

## 9. Final Verdict

`VERDICT: ACCEPT_SAME_REPORT_EID_HTML_RENDER_FOUND_READY_FOR_HYBRID_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_PLANNING_GATE_NOT_READY`
