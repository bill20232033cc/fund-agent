# 004393 Field-family Correctness Pilot Evidence - 2026-06-15

Gate: `004393 Field-family Correctness Pilot Evidence Gate`  
Role: evidence worker  
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records a bounded field-family correctness pilot for the user-designated fund:

- fund code: `004393`
- fund name: 安信企业价值优选混合A
- report year: `2025`

The evidence checks selected current-envelope candidate facts against same-source repository-loaded annual-report PDF excerpts. It does not implement production code and does not promote any parser route to source truth.

## 2. Source Inputs

Accepted planning input:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-plan-controller-judgment-20260615.md`

Accepted current-envelope inputs:

| Route | Artifact | SHA-256 |
| --- | --- | --- |
| Docling candidate | `reports/representation-json/004393_2025_docling_current_envelope.json` | `f4ea5e1fa028a364c2286a9244e7d482c4851afbcefb506c5b5b08db4ff02d28` |
| pdfplumber candidate | `reports/representation-json/004393_2025_pdfplumber_current_envelope.json` | `c0fa747e157098efe6ca5c2ca4d68e47f64e22b2e63a7aeedb4d5aa547393794` |
| EID HTML render | `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json` | `6f0f6f52da5cad5ba14a5b1c7ebcbf87e8085c83ca7f42552f5a1770553a7d42` |

Reviewed-facts output:

| Artifact | SHA-256 | Purpose |
| --- | --- | --- |
| `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` | `8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb` | Materialized selected facts, candidate locators, candidate cell hashes, same-source PDF crop excerpts, match status, and non-proof guards. |

Reference source:

- Annual report loaded through `FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)`.
- Repository metadata source: `eid`.
- Repository parsed cache hit: `True`.
- Repository raw text length: `61863`.
- Repository parsed sections: `8`.
- Repository parsed tables: `88`.
- Local PDF path used for bounded evidence excerpts after repository load: `cache/pdf/004393_2025_annual_report_eid.pdf`.
- The PDF path above was read from `document.metadata.cache.pdf_path` after `FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)` completed; it was not discovered through a Service/UI/Host/cache helper path.
- `pdf_cache_hit = False` means this repository metadata field did not classify the load as a PDF cache hit in the returned document metadata. The evidence worker still used the repository-resolved `document.metadata.cache.pdf_path` for bounded local crop excerpts after the repository load succeeded.

## 3. Evidence Commands

Repository boundary preflight:

```text
uv run python - <<'PY'
from fund_agent.fund.documents.repository import FundDocumentRepository

doc = FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)
print("key", doc.key)
print("raw_text_len", len(doc.raw_text))
print("sections", len(doc.sections))
print("tables", len(doc.tables))
print("metadata_source", doc.metadata.source)
print("pdf_cache_hit", doc.metadata.pdf_cache_hit)
print("parsed_cache_hit", doc.metadata.parsed_cache_hit)
PY
```

Observed result:

```text
key DocumentKey(fund_code='004393', year=2025, document_kind='annual_report')
raw_text_len 61863
sections 8
tables 88
metadata_source eid
pdf_cache_hit False
parsed_cache_hit True
```

Reviewed-facts extraction command:

```text
uv run python - <<'PY'
import asyncio
import hashlib
import json
import re
from pathlib import Path

import pdfplumber

from fund_agent.fund.documents.repository import FundDocumentRepository

DOC_PATH = Path("reports/representation-json/004393_2025_docling_current_envelope.json")
PDFPLUMBER_PATH = Path("reports/representation-json/004393_2025_pdfplumber_current_envelope.json")
OUT_PATH = Path("reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json")

FACTS = [
    ("F001", "fund_identity_profile", "docling_pdf_candidate", "fund_name", DOC_PATH, "#/tables/2", 0, 1, "exact_match", "none"),
    ("F002", "fund_identity_profile", "docling_pdf_candidate", "fund_code", DOC_PATH, "#/tables/2", 2, 1, "exact_match", "none"),
    ("F003", "fund_identity_profile", "docling_pdf_candidate", "operation_mode", DOC_PATH, "#/tables/2", 3, 1, "exact_match", "none"),
    ("F004", "fund_identity_profile", "docling_pdf_candidate", "contract_effective_date", DOC_PATH, "#/tables/2", 4, 1, "exact_match", "none"),
    ("F005", "fund_identity_profile", "docling_pdf_candidate", "fund_manager_company", DOC_PATH, "#/tables/2", 5, 1, "exact_match", "none"),
    ("F006", "product_contract_profile", "docling_pdf_candidate", "investment_objective", DOC_PATH, "#/tables/3", 0, 1, "exact_match", "none"),
    ("F007", "product_contract_profile", "docling_pdf_candidate", "benchmark", DOC_PATH, "#/tables/3", 2, 1, "normalized_match", "numeric_format_loss"),
    ("F008", "product_contract_profile", "docling_pdf_candidate", "risk_return_characteristic", DOC_PATH, "#/tables/3", 3, 1, "exact_match", "none"),
    ("F009", "performance_indicators", "docling_pdf_candidate", "period_profit_A_2025", DOC_PATH, "#/tables/8", 1, 1, "exact_match", "none"),
    ("F010", "performance_indicators", "docling_pdf_candidate", "nav_growth_A_current_period", DOC_PATH, "#/tables/8", 4, 1, "exact_match", "none"),
    ("F011", "performance_indicators", "docling_pdf_candidate", "past_year_nav_growth_A", DOC_PATH, "#/tables/9", 3, 1, "exact_match", "none"),
    ("F012", "performance_indicators", "docling_pdf_candidate", "past_year_excess_A", DOC_PATH, "#/tables/9", 3, 5, "exact_match", "none"),
    ("F013", "expense_costs", "docling_pdf_candidate", "management_fee_current_year", DOC_PATH, "#/tables/48", 1, 1, "exact_match", "none"),
    ("F014", "expense_costs", "docling_pdf_candidate", "custodian_fee_current_year", DOC_PATH, "#/tables/50", 1, 1, "exact_match", "none"),
    ("F015", "expense_costs", "docling_pdf_candidate", "sales_service_fee_C_current_year", DOC_PATH, "#/tables/51", 2, 2, "exact_match", "none"),
    ("F016", "portfolio_structure", "docling_pdf_candidate", "manufacturing_fair_value", DOC_PATH, "#/tables/72", 3, 2, "exact_match", "none"),
    ("F017", "portfolio_structure", "docling_pdf_candidate", "manufacturing_nav_ratio", DOC_PATH, "#/tables/72", 3, 3, "exact_match", "none"),
    ("F018", "portfolio_structure", "docling_pdf_candidate", "hk_industry_financial_fair_value", DOC_PATH, "#/tables/73", 7, 1, "exact_match", "none"),
    ("F019", "manager_alignment", "docling_pdf_candidate", "manager_name", DOC_PATH, "#/tables/14", 2, 0, "exact_match", "none"),
    ("F020", "manager_alignment", "docling_pdf_candidate", "manager_holding_range_A", DOC_PATH, "#/tables/86", 4, 2, "exact_match", "none"),
    ("F025", "manager_alignment", "docling_pdf_candidate", "manager_tenure_start", DOC_PATH, "#/tables/14", 2, 2, "normalized_match", "text_wrap_loss"),
    ("F021", "fund_identity_profile", "pdfplumber_pdf_candidate", "fund_name_pdfplumber_comparator", PDFPLUMBER_PATH, "page:5:table:0", 0, 1, "mismatch", "wrong_cell"),
    ("F022", "fund_identity_profile", "pdfplumber_pdf_candidate", "fund_code_pdfplumber_comparator", PDFPLUMBER_PATH, "page:5:table:0", 2, 1, "mismatch", "wrong_cell"),
    ("F023", "product_contract_profile", "pdfplumber_pdf_candidate", "benchmark_pdfplumber_comparator", PDFPLUMBER_PATH, "page:5:table:1", 2, 1, "mismatch", "wrong_cell"),
    ("F024", "performance_indicators", "pdfplumber_pdf_candidate", "past_year_nav_growth_A_pdfplumber_comparator", PDFPLUMBER_PATH, "page:8:table:0", 3, 1, "mismatch", "wrong_cell"),
]

def sha256_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize_text(value):
    return re.sub(r"\s+", "", value or "")

def find_cell(data, table_id, row_index, column_index):
    for table in data["tables"]:
        if table["table_id"] != table_id:
            continue
        for cell in table["cells"]:
            if cell["row_start"] <= row_index < cell["row_end"] and cell["column_start"] <= column_index < cell["column_end"]:
                return table, cell
        raise KeyError(f"cell not found: {table_id} row={row_index} col={column_index}")
    raise KeyError(f"table not found: {table_id}")

def bbox_to_pdfplumber_crop(bbox):
    if {"l", "t", "r", "b"} <= set(bbox):
        return (bbox["l"], bbox["t"], bbox["r"], bbox["b"])
    return (bbox["x0"], bbox["top"], bbox["x1"], bbox["bottom"])

def crop_reference_excerpt(pdf, page_number, bbox):
    page = pdf.pages[page_number - 1]
    x0, top, x1, bottom = bbox_to_pdfplumber_crop(bbox)
    crop_box = (max(0, x0), max(0, top), min(page.width, x1), min(page.height, bottom))
    text = page.crop(crop_box).extract_text(x_tolerance=1, y_tolerance=3) or ""
    return " ".join(text.split())

async def main():
    document = await FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)
    pdf_path = Path(document.metadata.cache.pdf_path)
    data_by_path = {
        DOC_PATH: json.loads(DOC_PATH.read_text()),
        PDFPLUMBER_PATH: json.loads(PDFPLUMBER_PATH.read_text()),
    }
    reviewed = []
    with pdfplumber.open(pdf_path) as pdf:
        for fact in FACTS:
            fact_id, family, route, field_name, source_path, table_id, row_index, column_index, match_status, mismatch_type = fact
            table, cell = find_cell(data_by_path[source_path], table_id, row_index, column_index)
            reference_excerpt = crop_reference_excerpt(pdf, table["page_number"], cell["bbox"])
            reviewed.append({
                "fact_id": fact_id,
                "family": family,
                "candidate_route": route,
                "field_name": field_name,
                "candidate_value": cell["text"],
                "candidate_artifact": str(source_path),
                "candidate_table_id": table_id,
                "candidate_page_number": table["page_number"],
                "candidate_row_index": row_index,
                "candidate_column_index": column_index,
                "candidate_bbox_or_null": cell.get("bbox"),
                "candidate_cell_hash_or_null": cell.get("cell_hash"),
                "reference_source": "same-source repository-loaded PDF bbox crop excerpt",
                "reference_pdf_path": str(pdf_path),
                "reference_page_number": table["page_number"],
                "reference_excerpt": reference_excerpt,
                "candidate_excerpt": cell["text"],
                "match_status": match_status,
                "mismatch_type": mismatch_type,
                "normalized_equal": normalize_text(cell["text"]) == normalize_text(reference_excerpt),
            })
    output = {
        "schema_version": "004393_field_family_correctness_pilot_reviewed_facts.v1",
        "fund_code": "004393",
        "document_year": 2025,
        "report_type": "annual_report",
        "repository_load": {
            "metadata_source": document.metadata.source.source,
            "source_mode": document.metadata.source.source_mode,
            "fallback_enabled": document.metadata.source.fallback_enabled,
            "fallback_used": document.metadata.source.fallback_used,
            "pdf_path": str(pdf_path),
            "pdf_cache_hit": document.metadata.cache.pdf_cache_hit,
            "parsed_cache_hit": document.metadata.cache.parsed_cache_hit,
            "raw_text_len": len(document.raw_text),
            "section_count": len(document.sections),
            "table_count": len(document.tables),
        },
        "input_hashes": {
            str(DOC_PATH): sha256_path(DOC_PATH),
            str(PDFPLUMBER_PATH): sha256_path(PDFPLUMBER_PATH),
        },
        "candidate_field_correctness_status_remains": "not_proven",
        "pilot_result": "bounded_pilot_pass_for_selected_docling_facts_not_ready",
        "not_source_truth": True,
        "not_readiness_proof": True,
        "not_production_parser_replacement": True,
        "facts": reviewed,
    }
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(str(OUT_PATH))
    print(sha256_path(OUT_PATH))

asyncio.run(main())
PY
```

Observed output:

```text
reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json
8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb
```

The executed command used the same algorithm shown above and the 25 facts listed in section 4. It did not change repository, parser, source policy, Service, Host, UI, renderer, quality gate, LLM route, readiness, release, or PR state.

## 4. Reviewed Fact Table

Reference excerpts are same-source repository-loaded PDF bbox crop excerpts. `normalized_match` only removes whitespace or line-wrap differences without changing field meaning.

| Fact | Family | Route | Field | Candidate | Reference excerpt | Status | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | fund_identity_profile | docling_pdf_candidate | fund_name | `安信企业价值优选混合型证券投资基金` | `安信企业价值优选混合型证券投资基金` | exact_match | `p5 #/tables/2 r0 c1` |
| F002 | fund_identity_profile | docling_pdf_candidate | fund_code | `004393` | `004393` | exact_match | `p5 #/tables/2 r2 c1` |
| F003 | fund_identity_profile | docling_pdf_candidate | operation_mode | `契约型开放式` | `契约型开放式` | exact_match | `p5 #/tables/2 r3 c1` |
| F004 | fund_identity_profile | docling_pdf_candidate | contract_effective_date | `2022年8月8日` | `2022年8月8日` | exact_match | `p5 #/tables/2 r4 c1` |
| F005 | fund_identity_profile | docling_pdf_candidate | fund_manager_company | `安信基金管理有限责任公司` | `安信基金管理有限责任公司` | exact_match | `p5 #/tables/2 r5 c1` |
| F006 | product_contract_profile | docling_pdf_candidate | investment_objective | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争 实现基金资产的长期稳健增值。` | `本基金在有效控制组合风险并保持基金资产流动性的前提下，力争 实现基金资产的长期稳健增值。` | exact_match | `p5 #/tables/3 r0 c1` |
| F007 | product_contract_profile | docling_pdf_candidate | benchmark | `沪深300指数收益率×60%+恒生指数收益率 （经汇率调整后） ×20%+ 中债综合（全价）指数收益率×20%` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+ 中债综合（全价）指数收益率×20%` | normalized_match | `p5 #/tables/3 r2 c1` |
| F008 | product_contract_profile | docling_pdf_candidate | risk_return_characteristic | `本基金为混合型基金，其预期收益及预期风险水平高于债券型基金 和货币市场基金，但低于股票型基金。 根据《证券期货投资者适当性管理办法》及其配套规则，基金管理 人及本基金其他销售机构将定期或不定期...` | `本基金为混合型基金，其预期收益及预期风险水平高于债券型基金 和货币市场基金，但低于股票型基金。 根据《证券期货投资者适当性管理办法》及其配套规则，基金管理 人及本基金其他销售机构将定期或不定期...` | exact_match | `p5 #/tables/3 r3 c1` |
| F009 | performance_indicators | docling_pdf_candidate | period_profit_A_2025 | `28,909,958 .71` | `28,909,958 .71` | exact_match | `p7 #/tables/8 r1 c1` |
| F010 | performance_indicators | docling_pdf_candidate | nav_growth_A_current_period | `12.77%` | `12.77%` | exact_match | `p7 #/tables/8 r4 c1` |
| F011 | performance_indicators | docling_pdf_candidate | past_year_nav_growth_A | `12.77%` | `12.77%` | exact_match | `p8 #/tables/9 r3 c1` |
| F012 | performance_indicators | docling_pdf_candidate | past_year_excess_A | `-2.57%` | `-2.57%` | exact_match | `p8 #/tables/9 r3 c5` |
| F013 | expense_costs | docling_pdf_candidate | management_fee_current_year | `3,033,849.49` | `3,033,849.49` | exact_match | `p37 #/tables/48 r1 c1` |
| F014 | expense_costs | docling_pdf_candidate | custodian_fee_current_year | `505,641.58` | `505,641.58` | exact_match | `p38 #/tables/50 r1 c1` |
| F015 | expense_costs | docling_pdf_candidate | sales_service_fee_C_current_year | `75,815.59` | `75,815.59` | exact_match | `p38 #/tables/51 r2 c2` |
| F016 | portfolio_structure | docling_pdf_candidate | manufacturing_fair_value | `39,484,558.44` | `39,484,558.44` | exact_match | `p52 #/tables/72 r3 c2` |
| F017 | portfolio_structure | docling_pdf_candidate | manufacturing_nav_ratio | `23.27` | `23.27` | exact_match | `p52 #/tables/72 r3 c3` |
| F018 | portfolio_structure | docling_pdf_candidate | hk_industry_financial_fair_value | `17,612,049.35` | `17,612,049.35` | exact_match | `p52 #/tables/73 r7 c1` |
| F019 | manager_alignment | docling_pdf_candidate | manager_name | `张明` | `张明` | exact_match | `p11 #/tables/14 r2 c0` |
| F020 | manager_alignment | docling_pdf_candidate | manager_holding_range_A | `50~100` | `50~100` | exact_match | `p60 #/tables/86 r4 c2` |
| F025 | manager_alignment | docling_pdf_candidate | manager_tenure_start | `2022年8 月8日` | `2022 年 8 月 8 日` | normalized_match | `p11 #/tables/14 r2 c2` |
| F021 | fund_identity_profile | pdfplumber_pdf_candidate | fund_name_pdfplumber_comparator | `安信企业价值优选混合型证券投资基金` | `基金简称` | mismatch | `p5 page:5:table:0 r0 c1` |
| F022 | fund_identity_profile | pdfplumber_pdf_candidate | fund_code_pdfplumber_comparator | `004393` | `报告期末基金份 额总额` | mismatch | `p5 page:5:table:0 r2 c1` |
| F023 | product_contract_profile | pdfplumber_pdf_candidate | benchmark_pdfplumber_comparator | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+ 中债综合（全价）指数收益率×20%` | `资产配置上，本基金以基于宏观、政策及市场分析的定性研究为主， 同时结合定量分析的方法，对未来各大类资产的风险和预期收益率 进行分析评估，制定股票、债券、现金等大类资产之间的配置比例、 调整原则...` | mismatch | `p5 page:5:table:1 r2 c1` |
| F024 | performance_indicators | pdfplumber_pdf_candidate | past_year_nav_growth_A_pdfplumber_comparator | `12.77%` | `20.43%` | mismatch | `p8 page:8:table:0 r3 c1` |

## 5. Result Summary

By route:

| Route | Reviewed facts | exact_match | normalized_match | mismatch | Evidence interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `docling_pdf_candidate` | 21 | 19 | 2 | 0 | Passes this bounded field-family correctness pilot. |
| `pdfplumber_pdf_candidate` | 4 | 0 | 0 | 4 | Comparator subset shows bbox/locator misalignment for selected cells. |
| `eid_html_render_candidate` | 0 | 0 | 0 | 0 | Excluded; current-envelope remains blocked for this sample. |

By Docling field family:

| Family | Reviewed Docling facts | Result |
| --- | ---: | --- |
| `fund_identity_profile` | 5 | pass |
| `product_contract_profile` | 3 | pass |
| `performance_indicators` | 4 | pass |
| `expense_costs` | 3 | pass |
| `portfolio_structure` | 3 | pass |
| `manager_alignment` | 3 | pass |

## 6. Evidence Interpretation

Accepted evidence:

- Docling current-envelope cells for the selected `004393_2025` field families match same-source repository-loaded PDF bbox crop excerpts in 21/21 reviewed facts.
- Two Docling facts are `normalized_match` because the candidate text and reference excerpt differ only in whitespace or line-wrap formatting.
- The selected pdfplumber comparator facts do not provide equivalent stable bbox/locator evidence for the same fields in this bounded sample.
- EID HTML render is not part of this correctness pilot and remains blocked current-envelope for `004393_2025`.

Not accepted as evidence:

- This is not parser-vs-parser agreement proof.
- This is not field correctness proof for unreviewed tables, unreviewed funds, unreviewed years, or narrative sections.
- This is not proof that Docling output is source truth.
- This is not proof that pdfplumber generally fails; only four selected comparator locator/crop checks mismatched.
- This is not raw XML/XBRL proof, taxonomy compatibility proof, EID HTML table-bearing proof, or readiness proof.

## 7. Residuals

| Residual | Status | Owner / next handling |
| --- | --- | --- |
| Evidence uses local PDF crop excerpts as same-source reference, not human visual screenshots. | accepted residual | Future broader correctness gate may add rendered-page image review for ambiguous cells. |
| Pilot covers 20 Docling facts, not full annual-report coverage. | accepted residual | Later production planning must define broader acceptance matrix before any parser replacement. |
| pdfplumber comparator sample is only 4 facts. | accepted residual | Do not generalize beyond locator/crop mismatch in the selected comparator rows. |
| EID HTML current-envelope remains blocked. | accepted residual | Separate EID HTML mapping gate required before any EID HTML field-family correctness claim. |
| Candidate artifacts are report files, not production repository behavior. | accepted residual | Production integration requires a separate design and implementation gate. |

## 8. Boundary Statement

- `release/readiness = NOT_READY`.
- `source_truth_status = not_proven`.
- Candidate artifact `field_correctness_status` remains `not_proven`.
- Pilot result is `bounded_pilot_pass_for_selected_docling_facts_not_ready`.
- `production_parser_replacement_status = not_authorized`.
- `FundDocumentRepository` behavior was not changed.
- Service, Host, UI, renderer, quality gate, LLM writer/auditor, source policy, and `EvidenceAnchor` schema were not changed.

## 9. Evidence Verdict

`EVIDENCE_RESULT: DOCLING_004393_FIELD_FAMILY_CORRECTNESS_PILOT_PASS_NOT_READY`

Recommended controller decision:

`ACCEPT_004393_DOCLING_FIELD_FAMILY_CORRECTNESS_PILOT_PASS_NOT_READY`

Recommended next gate:

`Docling Baseline Qualification Closeout / Truth-doc Sync Gate`

The next gate should reconcile this accepted bounded evidence into control/design truth before any production integration planning gate.
