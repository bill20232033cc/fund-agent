# Retained Excerpt Fixture PDF-Only Review — AgentMiMo

- Date: 2026-06-09
- Gate: `retained excerpt fixture gate for accepted rows only`
- Classification: `heavy`
- Reviewer: AgentMiMo
- JSON artifact: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- MD artifact: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.md`

## Verdict: PASS

## Review Questions

### Q1: Does the JSON retain only short field-scoped same-source excerpts and expected values for the five accepted rows?

**Yes.** Each of the five rows retains exactly 8 fields (`identity`, `benchmark`, `manager`, `scale`, `fee`, `return`, `holdings`, `risk`). Every field contains exactly three keys: `expected`, `anchor`, and `excerpt`. Excerpts are short fragments (1-2 sentences), not full pages or full tables. No full PDF text, no full page text, no fixture projection is present.

### Q2: Are access_boundary and retention_boundary consistent with the PDF-only authorization?

**Yes.** `access_boundary` correctly reports:
- `local_pdf_read_performed: true`
- `sha256_computed: true`
- `pdf_text_extraction_tool: "pdfplumber via uv run python"`
- `network_access_performed: false`
- `fund_document_repository_live_acquisition_performed: false`
- `fallback_invocation_performed: false`
- `extractor_modified: false`
- `fixture_projection_performed: false`
- `exact_numeric_correctness_accepted: false`
- `golden_readiness_promotion_performed: false`

`retention_boundary` correctly states:
- `full_pdf_retained: false`
- `full_page_text_retained: false`
- `excerpt_policy: "Retain only short field-level excerpts needed to anchor expected values."`
- `next_unlock: "Rows and fields below may be used to write row-field extractor correctness tests; extractor fixes remain a later gate after same-source failing tests."`

### Q3: Are rows limited to accepted source identity rows from checkpoint 866a12b?

**Yes.** The JSON contains exactly 5 rows: `004393`, `004194`, `006597`, `110020`, `017641`. These match exactly the five accepted rows from checkpoint `866a12b` source identity acceptance decision:
- `004393`: `matched`
- `004194`: `matched_without_hash`
- `006597`: `matched_without_hash`
- `110020`: `matched_without_hash`
- `017641`: `matched_without_hash`

No additional rows are included. `source_identity_checkpoint` is correctly set to `866a12b`.

### Q4: Does any expected value lack a direct local-PDF excerpt/anchor or appear inferred from unrelated evidence?

**No.** All expected values are anchored with:
1. A specific `anchor` pointing to PDF page and section (e.g., `PDF p5 §2.1 基金基本情况`)
2. A short `excerpt` containing the source text fragment

Spot-checked against actual PDFs via `pdfplumber`:
- `004393` p5 identity: fund name, code, share classes all match PDF text
- `004393` p5 benchmark: exact match
- `004393` p13 manager: 张明, 2022年8月8日, role all match
- `004393` p55 holdings: 00939 建设银行, 18,182,239.78, 6.08% all match
- `004194` p5 identity: fund name, code, share classes (A=004194, C=004195) all match
- `004194` p5 benchmark: exact match
- `006597` p5 identity: fund name, code, share classes (A/C/E/F) all match
- `006597` p5 benchmark: exact match
- `110020` p5 identity: fund name, code, share classes (A=110020, C=007339, Y=022928) all match
- `110020` p6 benchmark: exact match
- `017641` p5 identity: fund name, code, share classes (人民币A=017641, 人民币C=019305) all match
- `017641` p7 benchmark: exact match
- `017641` p59 holdings: AAPL, APPLE INC, 148,655,637.71, 7.66% all match

No value appears inferred from unrelated evidence.

### Q5: Does the artifact accidentally unlock full golden/readiness or extractor correctness acceptance?

**No.** The artifact explicitly preserves non-goals:
- `"No full golden promotion."`
- `"No readiness or quality gate promotion."`
- `"No extractor fix without same-source failing row-field test."`
- `"No network, live provider, fallback, or FundDocumentRepository live acquisition."`

`access_boundary.exact_numeric_correctness_accepted` is `false`. `access_boundary.golden_readiness_promotion_performed` is `false`. `next_gate` is correctly set to `"row-field extractor correctness test gate after review acceptance"`, not to golden promotion or extractor fix.

### Q6: Are next gate boundaries correct?

**Yes.** The `next_gate` field states: `"row-field extractor correctness test gate after review acceptance"`. The `retention_boundary.next_unlock` correctly states: `"Rows and fields below may be used to write row-field extractor correctness tests; extractor fixes remain a later gate after same-source failing tests."` This correctly sequences: (1) this fixture review → (2) row-field extractor correctness tests → (3) extractor fixes only after same-source failing tests exist.

## Validation Performed

| Check | Result |
|---|---|
| `python -m json.tool` on JSON artifact | Valid JSON |
| `shasum -a 256` on all 5 PDFs | All 5 sha256 hashes match JSON `pdf_sha256` values exactly |
| `git log 866a12b` | Source identity checkpoint commit exists: "gateflow: accept source identity decisions" |
| Source identity decisions at 866a12b | 5 rows match: 004393=matched, 004194/006597/110020/017641=matched_without_hash |
| pdfplumber spot-check 004393 p5 identity/benchmark | Match |
| pdfplumber spot-check 004393 p13 manager | Match |
| pdfplumber spot-check 004393 p55 holdings | Match |
| pdfplumber spot-check 004194 p5 identity/benchmark | Match |
| pdfplumber spot-check 006597 p5 identity/benchmark | Match |
| pdfplumber spot-check 110020 p5/p6 identity/benchmark | Match |
| pdfplumber spot-check 017641 p5/p7 identity/benchmark | Match |
| pdfplumber spot-check 017641 p59 holdings | Match |
| JSON field structure: 5 rows × 8 fields × 3 keys each | All present |
| access_boundary flags | Consistent with PDF-only authorization |
| retention_boundary flags | No full PDF/page retention; short excerpts only |
| non_goals_preserved | All 4 prohibitions present |
| next_gate | Correctly sequences test gate before fix gate |

## Findings

No blocking findings.

### F1 (Informational): 004194 holdings anchor references `§8.3.1 指数投资股票明细`

The anchor `PDF p55 §8.3.1 指数投资股票明细` is specific and correct. 004194 is an enhanced-index fund with both index and active stock positions; the excerpt correctly points to the index investment detail section. No issue.

### F2 (Informational): 017641 scale uses `total_share_units` in addition to `target_share_net_asset_cny`

Row 017641 scale field includes `total_share_units` (fund-wide) and `target_share_net_asset_cny` (人民币A share class). This is a QDII-specific field inclusion. The excerpt anchors correctly to p5 and p9. No issue.

### F3 (Informational): 110020 holdings field uses `target_etf_holding` instead of `top_stock_table_row`

110020 is an ETF-link fund; its primary holding is the target ETF, not individual stocks. The field correctly models this as `target_etf_holding` with the ETF name, fair value, and net asset ratio. The anchor `PDF p64 §8.2 期末投资目标基金明细` is correct for ETF-link fund holdings. No issue.

### F4 (Informational): 110020 return includes `annual_tracking_error`

The return field for 110020 includes `annual_tracking_error: "0.99%"` in addition to NAV growth and benchmark return. This is appropriate for an ETF-link fund. No issue.

## Residual Risks

1. **Spot-check coverage**: Only a subset of fields per row were verified against the actual PDFs. A full field-by-field verification for all 5 × 8 = 40 field excerpts was not performed in this review. The spot-checked fields (identity, benchmark, manager, holdings across multiple funds) all matched, providing reasonable confidence.

2. **Page number drift**: pdfplumber page indexing is 0-based while the JSON uses 1-based PDF page numbers. The spot checks confirmed that the 1-based page references in anchors correspond to the correct content when accessed via pdfplumber (index = page - 1).

3. **Excerpt compression**: Excerpts use `=` notation (e.g., `基金名称=安信企业价值优选混合型证券投资基金`) rather than verbatim copy. This is a summarization style, not a verbatim quote. For extractor correctness tests, the `expected` values are the ground truth; excerpts serve as orientation anchors only.

## Gate Sequence Confirmation

This review confirms:
- The retained excerpt fixture artifact is valid and correctly scoped.
- It does NOT unlock golden promotion, readiness promotion, extractor correctness acceptance, or extractor fixes.
- The next gate is `row-field extractor correctness test gate` using these excerpts as anchors.
- Extractor fixes remain blocked until same-source failing row-field tests exist.
