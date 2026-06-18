# MVP Small Golden Set Retained Excerpt Fixture - PDF-only

## Gate Metadata

- Gate: `retained excerpt fixture gate for accepted rows only`.
- Classification: `heavy`.
- Date: 2026-06-09.
- Source identity checkpoint: `866a12b`.
- Local PDF directory: `/Users/maomao/Downloads/基金年报/`.
- JSON artifact: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.

## Boundary

This gate used only user-provided local PDFs. It did not run network access, `FundDocumentRepository` live acquisition, fallback, live LLM/provider probes, extractor changes, fixture projection, exact/numeric correctness acceptance, or golden/readiness promotion.

## PDF Mapping

| fund_code | local PDF | sha256 |
|---|---|---|
| `004393` | `安信企业价值优选混合型证券投资基金2024年年度报告.pdf` | `bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf` |
| `004194` | `招商中证1000指数增强型证券投资基金2024年年度报告.pdf` | `c5b8efd8a4d57265e5ce34ff4a7426a259da19401638f859467b2ee76bb9d976` |
| `006597` | `国泰利享中短债债券型证券投资基金2024年年度报告.pdf` | `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` |
| `110020` | `易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告.pdf` | `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` |
| `017641` | `摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告.pdf` | `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` |

## Retained Field Coverage

Each row retains short same-source excerpts and expected values for:

- `identity`
- `benchmark`
- `manager`
- `scale`
- `fee`
- `return`
- `holdings`
- `risk`

The excerpts are intentionally short and field-scoped. They are not full pages, full tables, full PDF text, fixture projection, golden promotion, or extractor correctness acceptance.

## Row Summary

| fund_code | retained status | notes |
|---|---|---|
| `004393` | retained | A-share target row; active/mixed fund fields retained |
| `004194` | retained | A-share target row; enhanced-index fields retained |
| `006597` | retained | A-share target row; bond fund fields retained |
| `110020` | retained | A-share target row; ETF-link fields retained; Y share remains share-class boundary note |
| `017641` | retained | RMB A target row; QDII-specific risk retained; still non-promotion-ready |

## Next Unlock

This artifact may feed a later `row-field extractor correctness test gate` after review acceptance. Extractor fixes are still prohibited until same-source failing tests exist and a separate fix gate is opened.
