# Docling Route A Local Artifact Conversion Quality Evidence - 2026-06-15

Status: `EVIDENCE_COMPLETE_NOT_READY`
Gate: `Docling Local Model Artifact Acquisition / Provenance And Conversion Quality Evidence Gate`
Role: AgentController acting as evidence executor after explicit user authorization
Release/readiness: `NOT_READY`

## 1. Scope

User authorized Route A: acquire or use accepted local Docling model artifacts and sufficiently validate Docling extraction quality.

This artifact records a local benchmark only. It does not change production parser behavior, `FundDocumentRepository`, source policy, Service/UI/Host/renderer/quality-gate access, LLM route, readiness/release state or PR state.

Sample:

```text
fund_code=004393
fund_name=安信企业价值优选混合A
report_year=2025
input_pdf=基金年报/安信企业价值优选混合型证券投资基金2025年年度报告.pdf
input_classification=user-owned local benchmark PDF; not source truth
```

## 2. Artifact Acquisition

Direct HuggingFace access failed:

```text
https://huggingface.co -> curl error 35 / connection reset by peer
huggingface_hub.snapshot_download -> httpx.ConnectError [Errno 54] Connection reset by peer
```

`hf-mirror.com` homepage was reachable, but repo/API/git routes either redirected to `huggingface.co` or reset. No model artifact was downloaded from network during this gate.

The required artifacts already existed in the local HuggingFace cache:

| Repo | Requested revision | Local snapshot revision | Source cache path |
|---|---|---|---|
| `docling-project/docling-layout-heron` | `main` | `8f39ad3c0b4c58e9c2d2c84a38465abf757272d8` | `~/.cache/huggingface/hub/models--docling-project--docling-layout-heron/snapshots/8f39ad3c0b4c58e9c2d2c84a38465abf757272d8` |
| `docling-project/docling-models` | `v2.3.0` | `fc0f2d45e2218ea24bce5045f58a389aed16dc23` | `~/.cache/huggingface/hub/models--docling-project--docling-models/snapshots/fc0f2d45e2218ea24bce5045f58a389aed16dc23` |

The snapshots were copied into the repo-local artifact root:

```text
cache/docling-artifacts/docling-project--docling-layout-heron
cache/docling-artifacts/docling-project--docling-models
```

Manifest:

```text
reports/docling-route-a/artifact-manifest.json
```

Manifest summary:

| Artifact folder | File count | Total bytes |
|---|---:|---:|
| `docling-project--docling-layout-heron` | 6 | 171,764,371 |
| `docling-project--docling-models` | 8 | 358,236,323 |

## 3. Conversion Configuration

Docling conversion was run with explicit local artifacts:

```text
docling_version=2.93.0
docling_slim_version=2.93.0
docling_ibm_models_version=3.13.2
artifacts_path=/Users/maomao/fund-agent/cache/docling-artifacts
do_ocr=false
do_table_structure=true
accelerator_device=CPU
socket_blocked=true
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

Network containment:

- The conversion process monkeypatched socket `connect` and `create_connection` to raise.
- Conversion completed successfully under that socket block.
- No EID HTTP, FDR/PDF acquisition, pdfplumber, provider/LLM, analyze/checklist/readiness/release/PR command was run.

## 4. Conversion Outputs

Output files:

```text
reports/docling-route-a/004393_2025_docling.json
reports/docling-route-a/004393_2025_docling.md
reports/docling-route-a/004393_2025_docling_summary.json
reports/docling-route-a/004393_2025_docling_quality_summary.json
```

Conversion summary:

| Metric | Value |
|---|---:|
| Exit status | success |
| Elapsed seconds | 63.483 |
| PDF size | 832,089 bytes |
| Page count | 65 |
| Text item count | 670 |
| Table count | 95 |
| Picture count | 4 |
| Group count | 33 |
| Markdown chars | 152,718 |
| Markdown lines | 2,134 |

Hashes:

| Output | SHA256 |
|---|---|
| Markdown | `e9644cceebc82a9d9a4a3a1af692e5c7a8fa99edc0ceec0a824e4f246dc87596` |
| JSON | `b7a664c31a11db332815884b5632451ed6e64c8d246254ed23f55f409364c933` |

## 5. Coverage Evidence

Section coverage from Markdown headings:

| Section | Present |
|---|---|
| `§1` | yes |
| `§2` | yes |
| `§3` | yes |
| `§4` | yes |
| `§5` | yes |
| `§6` | yes |
| `§7` | yes |
| `§8` | yes |
| `§9` | yes |
| `§10` | yes |
| `§11` | yes |
| `§12` | yes |
| `§13` | yes |

Additional structure:

```text
heading_count=213
table_count=95
max_table_rows=43
max_table_cols=11
tables_with_ge_5_cols=32
tables_with_ge_10_rows=28
```

Keyword coverage:

| Keyword | Markdown hits |
|---|---:|
| `基金基本情况` | 3 |
| `主要会计数据和财务指标` | 2 |
| `基金经理` | 10 |
| `报告期内基金投资策略和运作分析` | 1 |
| `资产负债表` | 10 |
| `利润表` | 2 |
| `投资组合报告` | 6 |
| `报告期末按行业分类的境内股票投资组合` | 1 |
| `期末按公允价值占基金资产净值比例大小排序的所有股票投资明细` | 2 |
| `基金份额持有人信息` | 2 |
| `交易费用` | 9 |
| `换手率` | 0 |

`换手率=0` is expected for this current regulatory/reporting context and is not a Docling failure in this evidence.

## 6. Representative Extraction Quality

### 6.1 Section 3 Financial Metrics

Docling extracted section `3.1 主要会计数据和财务指标` as Markdown tables and retained multi-year / multi-share-class rows, including:

```text
本期已实现收益
本期利润
本期基金份额净值增长率
期末基金资产净值
基金份额累计净值增长率
```

Quality:

- strong section localization;
- table structure retained;
- multi-level headers represented, but Markdown contains repeated header rows;
- some Chinese labels and numbers are split with spaces, e.g. `33,984,439 .75`, `154,973,70 4.60`.

Disposition: useful for document representation and candidate extraction, but raw Markdown text must be normalized before numeric field extraction.

### 6.2 Fund Manager Table

Docling extracted `4.1.2 基金经理（或基金经理小组）及基金经理助理简介` as a table containing:

```text
张明
2022年8月8日
14年
安信企业价值优选混合型证券投资基金
```

Quality:

- correct table localization;
- manager biography preserved;
- row/column structure usable;
- Chinese wrapping inserts spaces inside words.

Disposition: strong enough for candidate EvidenceAnchor / FundDisclosureDocument mapping after text normalization.

### 6.3 Financial Statements

Docling extracted `7.1 资产负债表` and `7.2 利润表` with major rows:

```text
货币资金
交易性金融资产
资产总计
负债合计
净资产合计
营业总收入
投资收益
交易费用
```

Quality:

- major financial statement rows and comparative-period columns preserved;
- multi-page table continuation is split into multiple Markdown tables;
- table cells in JSON retain `page_no`, `bbox`, `row/col offset` and text, which is better than Markdown for structured use.

Disposition: useful as structured document layer, not direct field truth without validation.

### 6.4 Investment Portfolio

Docling extracted `§8 投资组合报告`, including:

```text
8.2.1 报告期末按行业分类的境内股票投资组合
8.2.2 报告期末按行业分类的港股通投资股票投资组合
8.3 期末按公允价值占基金资产净值比例大小排序的所有股票投资明细
```

Representative table structure:

| Table | Page | Rows | Cols | Evidence |
|---|---:|---:|---:|---|
| Industry classification | 52 | 21 | 4 | code / industry / fair value / NAV ratio |
| Stock holding detail | 53 | 38 | 6 | stock code / name / quantity / fair value / NAV ratio |

Sample extracted holdings:

```text
00939 建设银行 1,050,000 7,293,049.89 4.30
01999 敏华控股 1,630,000 6,728,176.10 3.96
01088 中国神华 191,000 6,693,582.78 3.94
```

Quality:

- table reconstruction is materially useful;
- row/column offsets and page provenance exist in JSON;
- enough structure to support future candidate table-family pilot.

### 6.5 Manager Holding

Docling extracted fund manager holding information in table index 86 / page 60:

```text
本基金基金经理持有 本开放式基金
安信企业价值优选混合A
50~100
安信企业价值优选混合C
0
```

Quality:

- business-critical data is present;
- text wrapping splits labels;
- exact keyword search may fail unless whitespace is normalized.

Disposition: useful but requires text normalization and row-label matching.

## 7. Quality Findings

| Finding | Severity | Disposition |
|---|---|---|
| Full annual-report section coverage is strong: `§1-§13` all present, 213 headings, 95 tables. | positive | Docling is viable for broad document representation. |
| Table structure is materially better than plain text extraction for portfolio, financial statements and manager tables. | positive | JSON `table_cells` should be consumed instead of Markdown tables. |
| JSON carries page provenance, bbox and row/column offsets for tables. | positive | Good fit for candidate `EvidenceAnchor` mapping. |
| Markdown output inserts spaces inside Chinese words and numeric tokens. | medium | Requires normalization before extraction. |
| Multi-level headers are sometimes duplicated or split across multiple Markdown table blocks. | medium | Use JSON table cells and header reconstruction, not raw Markdown. |
| Cross-page tables are split. | medium | Requires table continuation stitching. |
| Exact keyword matching is brittle because of inserted spaces, e.g. manager holding label. | medium | Use whitespace-insensitive matching. |
| Local PDF input is user-owned benchmark artifact, not EID source truth. | high boundary | Do not promote values to field correctness proof. |
| Artifact source is local HuggingFace cache copied into repo-local cache, not newly downloaded during this gate. | provenance residual | Need later model provenance acceptance before production use. |

## 8. Comparison To Prior Blocked State

Before Route A, Docling was blocked because:

```text
artifacts_path=None
layout model path could call snapshot_download()
no accepted local layout/table artifact proof
```

After Route A:

```text
artifacts_path=cache/docling-artifacts
socket-blocked full conversion succeeded
layout/table artifacts were sufficient for this local benchmark
```

This resolves the local runtime containment blocker for this benchmark only. It does not prove production readiness or source truth.

## 9. Final Verdict

```text
VERDICT: DOCLING_ROUTE_A_LOCAL_BENCHMARK_SUCCEEDED_NOT_READY
```

Conclusion:

- Docling is effective for full-content annual-report document representation on `004393 / 2025`.
- It extracts all major report sections, 95 tables, section headings, financial statements, portfolio holdings and manager holding information.
- The correct consumption layer is `DoclingDocument` JSON, not Markdown text.
- Remaining work is schema/mapping/normalization, table continuation stitching and provenance acceptance.
- Docling should re-enter the candidate route as a viable document representation input, but not as production parser replacement or source truth.

Recommended next gate:

```text
Docling FundDisclosureDocument Mapping And Normalization Planning Gate
```

Deferred gates:

- model artifact provenance acceptance gate;
- same-report EID HTML vs Docling vs current parser quality comparison;
- production repository integration planning;
- readiness/release/PR.
