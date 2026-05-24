# Release Maintenance 004393 Quality Gate S0 Evidence

## Scope

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S0 - Evidence Artifact`
- Date: 2026-05-24
- Artifact path: `docs/reviews/release-maintenance-004393-quality-gate-evidence-20260524.md`
- Boundary: annual-report access only through `FundDocumentRepository.load_annual_report("004393", 2024, force_refresh=False)`.
- No source/test/config/runtime/README/golden/plan/control file was modified for this evidence artifact.

## Commands

### Initial plan-pattern command

Exact command:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
import json
from fund_agent.fund.documents import FundDocumentRepository

KEYWORDS = (
    "基金管理人", "基金托管人", "基金合同生效日", "业绩比较基准",
    "管理费", "托管费", "7.4.10.2", "股票投资", "行业", "代码", "公允价值", "占基金资产净值比例",
    "份额", "A类", "C类", "期初", "期末", "申购", "赎回", "转手率", "换手率", "周转率", "turnover"
)


def text_preview(text, limit=7000):
    return text[:limit]


def table_payload(ordinal, table):
    return {
        "ordinal": ordinal,
        "page_number": table.page_number,
        "table_index": table.table_index,
        "headers": table.headers,
        "row_count": len(table.rows),
        "rows_preview": table.rows[:8],
    }


async def main() -> None:
    repo = FundDocumentRepository()
    report = await repo.load_annual_report("004393", 2024, force_refresh=False)
    print("METADATA_JSON")
    print(json.dumps(report.metadata.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    for section in ("§2", "§7", "§8", "§10"):
        print(f"SECTION {section}")
        print(text_preview(report.get_section_text(section)))
    print("MATCHING_TABLES_JSONL")
    for ordinal, table in enumerate(report.tables):
        headers = " | ".join(str(item) for item in table.headers)
        row_blob = " | ".join(" | ".join(str(cell) for cell in row) for row in table.rows[:5])
        combined = headers + " | " + row_blob
        if any(token in combined for token in KEYWORDS):
            print(json.dumps(table_payload(ordinal, table), ensure_ascii=False, sort_keys=True))


asyncio.run(main())
PY
uv run python "$tmp_script"
evidence_exit_code=$?
echo "exit_code=$evidence_exit_code"
rm -f "$tmp_script"
test "$evidence_exit_code" -eq 0
```

Exit code: `1`.

Reason: repository load succeeded, but `ParsedAnnualReport.get_section_text("§7")` returned `None`, and the temporary preview helper attempted to slice `None`. This did not require direct PDF/cache/source-helper access and did not contradict the facts; the follow-up commands preserve `None` explicitly and inspect the parser's actual section ids.

### Successful section/table evidence command

Exact command:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
import json
from fund_agent.fund.documents import FundDocumentRepository

KEYWORDS = (
    "基金管理人", "基金托管人", "基金合同生效日", "业绩比较基准",
    "管理费", "托管费", "7.4.10.2", "股票投资", "行业", "代码", "公允价值", "占基金资产净值比例",
    "份额", "A类", "C类", "期初", "期末", "申购", "赎回", "转手率", "换手率", "周转率", "turnover"
)


def text_preview(text, limit=12000):
    if text is None:
        return "<SECTION_NOT_FOUND>"
    return text[:limit]


def table_payload(ordinal, table):
    return {
        "ordinal": ordinal,
        "page_number": table.page_number,
        "table_index": table.table_index,
        "headers": table.headers,
        "row_count": len(table.rows),
        "rows_preview": table.rows[:12],
    }


async def main() -> None:
    repo = FundDocumentRepository()
    report = await repo.load_annual_report("004393", 2024, force_refresh=False)
    print("METADATA_JSON")
    print(json.dumps(report.metadata.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    print("SECTIONS_JSON")
    print(json.dumps({key: value.to_dict() for key, value in report.sections.items()}, ensure_ascii=False, indent=2, sort_keys=True))
    for section in ("§2", "§7", "§8", "§10"):
        print(f"SECTION {section}")
        print(text_preview(report.get_section_text(section)))
    print("MATCHING_TABLES_JSONL")
    for ordinal, table in enumerate(report.tables):
        headers = " | ".join(str(item) for item in table.headers)
        row_blob = " | ".join(" | ".join(str(cell) for cell in row) for row in table.rows[:8])
        combined = headers + " | " + row_blob
        if any(token in combined for token in KEYWORDS):
            print(json.dumps(table_payload(ordinal, table), ensure_ascii=False, sort_keys=True))


asyncio.run(main())
PY
uv run python "$tmp_script"
evidence_exit_code=$?
echo "exit_code=$evidence_exit_code"
rm -f "$tmp_script"
test "$evidence_exit_code" -eq 0
```

Exit code: `0`.

### Detail locator command

Exact command:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-detail-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
import json
from fund_agent.fund.documents import FundDocumentRepository

NEEDLES = ("7.4.10.2", "管理费", "托管费", "基金份额", "中债综", "转手", "换手", "周转")
PAGES = set(range(3, 6)) | set(range(24, 31)) | set(range(54, 57)) | set(range(63, 65))
ORDINALS = {71, 72, 74, 90, 91}


def dump_table(ordinal, table):
    print(json.dumps({
        "ordinal": ordinal,
        "page_number": table.page_number,
        "table_index": table.table_index,
        "headers": table.headers,
        "row_count": len(table.rows),
        "rows": table.rows,
    }, ensure_ascii=False, sort_keys=True))


async def main() -> None:
    report = await FundDocumentRepository().load_annual_report("004393", 2024, force_refresh=False)
    print("METADATA_JSON")
    print(json.dumps(report.metadata.to_dict(), ensure_ascii=False, sort_keys=True))
    print("SECTION_TEXT_LOCATORS")
    for section_id in ("§2", "§5", "§8", "§10"):
        text = report.get_section_text(section_id) or ""
        for needle in NEEDLES:
            idx = text.find(needle)
            if idx >= 0:
                start = max(0, idx - 220)
                end = min(len(text), idx + 700)
                print(json.dumps({
                    "section_id": section_id,
                    "needle": needle,
                    "char_index": idx,
                    "snippet": text[start:end],
                }, ensure_ascii=False, sort_keys=True))
    print("TABLES_SELECTED_JSONL")
    for ordinal, table in enumerate(report.tables):
        headers = " | ".join(table.headers)
        row_blob = " | ".join(" | ".join(row) for row in table.rows)
        combined = headers + " | " + row_blob
        if table.page_number in PAGES or ordinal in ORDINALS or any(needle in combined for needle in NEEDLES):
            dump_table(ordinal, table)


asyncio.run(main())
PY
uv run python "$tmp_script"
evidence_exit_code=$?
echo "exit_code=$evidence_exit_code"
rm -f "$tmp_script"
test "$evidence_exit_code" -eq 0
```

Exit code: `0`.

### Summary assertion command

Exact command:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-summary-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
import json
from fund_agent.fund.documents import FundDocumentRepository


def contains_any(blob, tokens):
    return any(token in blob for token in tokens)


async def main() -> None:
    report = await FundDocumentRepository().load_annual_report("004393", 2024, force_refresh=False)
    section2 = report.get_section_text("§2") or ""
    section5 = report.get_section_text("§5") or ""
    section8 = report.get_section_text("§8") or ""
    section10 = report.get_section_text("§10") or ""
    inspected = section5 + "\n" + section8 + "\n" + section10
    turnover_tokens = ("转手率", "换手率", "股票换手", "周转率", "turnover_rate", "turnover rate")
    tables = list(report.tables)
    result = {
        "metadata": report.metadata.to_dict(),
        "sections_present": sorted(report.sections.keys()),
        "facts": {
            "identity_company": "基金管理人 安信基金管理有限责任公司" in section2,
            "identity_custodian": "基金托管人 中国银行股份有限公司" in section2,
            "identity_inception": "基金合同生效日 2022年8月8日" in section2,
            "share_class_a_identity": "安信企业价值优选混合A" in section2 and "004393" in section2,
            "benchmark_raw": section2[section2.find("业绩比较基准"):section2.find("风险收益特征")].strip(),
            "management_fee_rate": "1.20%" in section5 and "7.4.10.2.1 基金管理费" in section5,
            "custody_fee_rate": "0.20%" in section5 and "7.4.10.2.2 基金托管费" in section5,
            "turnover_direct_row_observed": contains_any(inspected, turnover_tokens),
        },
        "tables": {
            "profile_ordinal_0": {"page": tables[0].page_number, "index": tables[0].table_index, "headers": tables[0].headers, "rows": tables[0].rows},
            "benchmark_ordinal_1": {"page": tables[1].page_number, "index": tables[1].table_index, "headers": tables[1].headers, "rows": tables[1].rows},
            "fee_management_ordinal_45": {"page": tables[45].page_number, "index": tables[45].table_index, "headers": tables[45].headers, "rows": tables[45].rows, "text_locator": section5.find("7.4.10.2.1 基金管理费")},
            "fee_custody_ordinal_46": {"page": tables[46].page_number, "index": tables[46].table_index, "headers": tables[46].headers, "rows": tables[46].rows, "text_locator": section5.find("7.4.10.2.2 基金托管费")},
            "industry_a_ordinal_71": {"page": tables[71].page_number, "index": tables[71].table_index, "headers": tables[71].headers, "row_count": len(tables[71].rows)},
            "industry_hk_ordinal_72_73": {"page_indexes": [(tables[72].page_number, tables[72].table_index), (tables[73].page_number, tables[73].table_index)], "headers": [tables[72].headers, tables[73].headers], "row_count": len(tables[72].rows) + len(tables[73].rows)},
            "stock_details_ordinal_74_75": {"page_indexes": [(tables[74].page_number, tables[74].table_index), (tables[75].page_number, tables[75].table_index)], "headers": [tables[74].headers, tables[75].headers], "row_count": len(tables[74].rows) + len(tables[75].rows), "first_12_rows": tables[74].rows[:12]},
            "share_header_ordinal_90": {"page": tables[90].page_number, "index": tables[90].table_index, "headers": tables[90].headers, "rows": tables[90].rows},
            "share_data_ordinal_91": {"page": tables[91].page_number, "index": tables[91].table_index, "headers": tables[91].headers, "rows": tables[91].rows, "a_class_net_change": "121,899,329.59"},
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


asyncio.run(main())
PY
uv run python "$tmp_script"
evidence_exit_code=$?
echo "exit_code=$evidence_exit_code"
rm -f "$tmp_script"
test "$evidence_exit_code" -eq 0
```

Exit code: `0`.

## Repository Metadata

Observed from `ParsedAnnualReport.metadata.to_dict()` returned by `FundDocumentRepository`:

```json
{
  "cache": {
    "cache_schema_version": 1,
    "parsed_cache_hit": true,
    "pdf_cache_hit": false,
    "pdf_path": null,
    "source_metadata_present": false
  },
  "source": null
}
```

- Source metadata: `null` in the returned parsed-cache object.
- Fallback-used status: not available because `metadata.source` is `null`.
- Cache status: `parsed_cache_hit=true`, `pdf_cache_hit=false`, `source_metadata_present=false`, `force_refresh=false`.
- Parser section ids present: `§1`, `§2`, `§3`, `§4`, `§5`, `§8`, `§9`, `§10`.
- Parser does not expose `§7` as a standalone section for this cached parse. The `7.4.10.2` subsection text is present inside parser section `§5` because the cached section span runs through the financial statement notes.

## Per-Fact Checklist

| Fact ID | Status | Same-source locator | Observation |
|---|---|---|---|
| `E-identity-company` | `confirmed` | `§2`; table ordinal `0`, page `5`, table_index `0`; profile row `基金管理人` | Row value is `安信基金管理有限责任公司`. Metadata/cache status as above. |
| `E-identity-custodian` | `confirmed` | `§2`; table ordinal `0`, page `5`, table_index `0`; profile row `基金托管人` | Row value is `中国银行股份有限公司`. Metadata/cache status as above. |
| `E-identity-inception` | `confirmed` | `§2`; table ordinal `0`, page `5`, table_index `0`; profile row `基金合同生效日` | Row value is `2022年8月8日`, parser-equivalent to `2022 年 8 月 8 日`. Metadata/cache status as above. |
| `E-fee-management` | `confirmed` | Parser section `§5`; subsection text locator `7.4.10.2.1 基金管理费` at char index `21297`; table ordinal `45`, page `39`, table_index `1` | Text states the management fee is accrued at `1.20%` annual rate: `H=E×1.20%/当年天数`. Table row also records `当期发生的基金应支付的管理费 = 2,308,368.87`. Metadata/cache status as above. |
| `E-fee-custody` | `confirmed` | Parser section `§5`; subsection text locator `7.4.10.2.2 基金托管费` at char index `21673`; table ordinal `46`, page `40`, table_index `0` | Text states the custody fee is accrued at `0.20%` annual rate: `H=E×0.20%/当年天数`. Table row also records `当期发生的基金应支付的托管费 = 384,728.17`. Metadata/cache status as above. |
| `E-holdings-stock-details` | `confirmed` | `§8`; text heading `8.3 期末按公允价值占基金资产净值比例大小排序的所有股票投资明细`; table ordinals `74` and `75`, page/index pair `(55, 1)` and `(56, 0)` | Stock-detail semantics are present: headers include `序号`, `股票代码`, `股票名称`, `数量（股）`, `公允价值（元）`, `占基金资产净值比例（%）`. Combined row count is `74`, so row count is at least `10`. Metadata/cache status as above. |
| `E-holdings-industry` | `confirmed` | `§8`; headings `8.2.1` and `8.2.2`; table ordinals `71`, `72`, `73`, page/index `(54, 1)`, `(54, 2)`, `(55, 0)` | Industry-distribution evidence is separate from stock-detail holdings. Domestic industry table has headers `代码`, `行业类别`, `公允价值（元）`, `占基金资产净值比例（%）` and row_count `20`; HK industry tables have combined row_count `11`. Metadata/cache status as above. |
| `E-share-split-header` | `confirmed` | `§10`; adjacent tables ordinal `90` and `91`, page/index pair `(63, 3)` and `(64, 0)` | Header table ordinal `90` has headers `项目`, `安信企业价值优选混合A`, `安信企业价值优选混合C`. Data table ordinal `91` has split header text `（2022年8月8日）\n基金份额总额` with the adjacent A/C headers inherited from ordinal `90`. Metadata/cache status as above. |
| `E-share-values-a` | `confirmed` | `§10`; table ordinals `90`/`91`, page/index `(63, 3)` and `(64, 0)`; selected column reason: §2 maps current fund code `004393` to `安信企业价值优选混合A` | A-class values in ordinal `91`: beginning `本报告期期初基金份额总额 = 27,666,410.41`; ending `本报告期期末基金份额总额 = 149,565,740.00`; net change by same table arithmetic `149,565,740.00 - 27,666,410.41 = 121,899,329.59`. Metadata/cache status as above. |
| `E-share-class-identity` | `confirmed` | `§2`; table ordinal `0`, page `5`, table_index `0`; rows `下属分级基金的基金简称` / `下属分级基金的交易代码` / `报告期末下属分级基金的份额总额` | Same-source table explicitly maps `004393` to `安信企业价值优选混合A`, and `020964` to `安信企业价值优选混合C`; no fund-code suffix inference is needed. Metadata/cache status as above. |
| `E-benchmark-whitespace` | `confirmed` | `§2`; table ordinal `1`, page `5`, table_index `1`; row `业绩比较基准`; text locator char index `643` for `中债综` | Raw parser text is `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综\n合（全价）指数收益率×20%`. Removing the visual newline produces `中债综合（全价）指数收益率×20%`, so the observed mismatch is whitespace/newline only. Metadata/cache status as above. |
| `E-turnover-deferred` | `not_observed` | Inspected parser sections `§8`, `§5` containing `7.4.10.2`, and `§10`; searched tokens `转手率`, `换手率`, `股票换手`, `周转率`, `turnover_rate`, `turnover rate` | No directly disclosed stock turnover-rate row was observed in the inspected same-source text/tables. This is recorded only as deferred disclosure-applicability evidence, not as proof that a proxy turnover value should be calculated. Metadata/cache status as above. |

## Notes For Controller

- The evidence supports the handoff facts for identity, §7.4.10.2 fee rates, §8 all-stock details plus industry distribution, §10 split header/data, A-class share values, and benchmark whitespace normalization.
- The only `not_observed` fact is `E-turnover-deferred`, consistent with the plan's deferred applicability scope.
- No direct PDF file, cache file, or concrete annual-report source helper was opened or called.
