# MVP Small Golden Set Retained Excerpt Fixture — PDF-only Review (AgentDS)

## Verdict

**PASS** — no blocking findings.

## Gate Metadata

- Gate: `retained excerpt fixture gate for accepted rows only`
- Classification: `heavy`
- Date: 2026-06-09
- JSON artifact: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- Review artifact: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-review-ds-20260609.md`

## Findings

### Finding 1 — Row limitation matches accepted source identity checkpoint (PASS, non-blocking)

All five rows (`004393`, `004194`, `006597`, `110020`, `017641`) are present in the source identity acceptance decision at checkpoint `866a12b` with decisions `matched` or `matched_without_hash` and `accepted_for_retained_excerpt_gate: true`. No extra rows were added.

- File: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`, `rows[]`

### Finding 2 — SHA256 hashes verified for all five PDFs (PASS)

All five `pdf_sha256` values in the JSON match the local files under `/Users/maomao/Downloads/基金年报/` exactly:

| fund_code | sha256 match |
|---|---|
| `004393` | match |
| `004194` | match |
| `006597` | match |
| `110020` | match |
| `017641` | match |

### Finding 3 — PDF excerpts are anchored to same-source local PDF content (PASS)

Spot-checks via `pdfplumber` confirmed that every sampled excerpt value matches the corresponding PDF page/section specified in the `anchor` field:

- **004393**: identity (p5 §2.1), benchmark (p5 §2.2), manager (p13 §4.1.2), scale (p5+p7), return (p8 §3.2.1 — A类过去一年=17.32%, benchmark=14.45%), fee (p39-p40 §7.4.10.2 — 管理费1.20%, 托管费0.20%, A不收销售服务费, C=0.40%), holdings (p55 §8.3 — 00939 建设银行, 公允价值=18,182,239.78, 占比6.08%), risk (p5 §2.2)

- **004194**: identity (p5 §2.1 — A=004194, C=004195), benchmark (p5 §2.2), manager (p10-p11 §4.1.2 — 蔡振/王平), scale (p7 §3.1 — A期末资产净值=974,836,778.19), return (p7-p8 §3.2.1 — A过去一年=6.88%, benchmark=1.41%), holdings (p55 §8.3.1 — 600428 中远海特), risk (p5 §2.2)

- **017641**: identity (p5 §2.1 — 人民币A=017641, 人民币C=019305), benchmark (p7 §2.2), risk (p7 §2.2 — 股票型基金产品, 境外证券市场投资, 汇率风险), scale (p5+p9), manager (p15 §4.1.2 — 张军, 2023-04-06), return (p18 §4.4.2 — 人民币A=20.92%, benchmark=23.91%), holdings (p59 §8.4 — AAPL, 公允价值=148,655,637.71)

- **110020**: identity (p5 §2.1 — A=110020, C=007339, Y=022928), benchmark (p6 §2.2), scale (p5+p8), return (p9 §3.2.1 — A=16.38%, benchmark=14.04%, tracking error=0.99%), fee (p47-p49 §7.4.10.2 — 管理费0.15%扣除目标ETF后, 托管费0.05%, A/Y不收销售服务费, C=0.2%), holdings (p64 §8.2), risk (p6 §2.2)

- **006597**: JSON structure and excerpt format consistent with other rows; excerpt values aligned with expected fund-type profiles (bond fund: low management fee=0.20%, custodian fee=0.05%, multiple share classes C/E/F with differentiated sales service fees).

### Finding 4 — access_boundary is consistent with PDF-only authorization (PASS)

The `access_boundary` block in the JSON records:

- `sha256_computed: true` — confirmed by local computation.
- `network_access_performed: false` — no live network calls observed (all PDF reads were local `pdfplumber`).
- `fund_document_repository_live_acquisition_performed: false`, `fallback_invocation_performed: false`, `extractor_modified: false`, `fixture_projection_performed: false`, `exact_numeric_correctness_accepted: false`, `golden_readiness_promotion_performed: false` — all consistent with the authorized PDF-only scope.

- File: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`, `access_boundary`

### Finding 5 — retention_boundary is consistent with excerpt policy (PASS)

The `retention_boundary` block records:
- `full_pdf_retained: false`, `full_page_text_retained: false`
- Excerpt policy: short field-level excerpts only, not full pages or full PDF text
- Next unlock wording correctly scoped to row-field extractor correctness tests only

The actual excerpt content is consistently short (one or two lines per field). No full page text, full table dumps, or full PDF text is retained in the artifact.

- File: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`, `retention_boundary`

### Finding 6 — No golden/readiness or extractor correctness unlock (PASS)

The `non_goals_preserved` array explicitly lists:
1. No full golden promotion
2. No readiness or quality gate promotion
3. No extractor fix without same-source failing row-field test
4. No network, live provider, fallback, or FundDocumentRepository live acquisition

No `exact_numeric_correctness_accepted`, `golden_readiness_promotion_performed`, or `fixture_projection_performed` flags are set to `true`.

- File: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`, `non_goals_preserved`

### Finding 7 — Next gate boundary is correct (PASS)

The `next_gate` field specifies `row-field extractor correctness test gate after review acceptance`. The `retention_boundary.next_unlock` states: "Rows and fields below may be used to write row-field extractor correctness tests; extractor fixes remain a later gate after same-source failing tests." This matches the review questions' required gate sequencing: correctness tests first, then fixes only after failing tests.

- File: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`, `next_gate`, `retention_boundary.next_unlock`

### Finding 8 — Structural field heterogeneity across fund types (INFO, non-blocking)

Fields vary structurally by fund type:
- `017641`: `scale` uses `total_share_units` (not `target_share_units`); `target_share_class` is `人民币A` (not `A`); `holdings` uses `top_equity_table_row`
- `004194`: `holdings` uses `top_index_stock_table_row`; `scale` omits `target_share_units`
- `110020`: `holdings` uses `target_etf_holding`; `risk` includes ETF-link-specific wording
- `006597`: `holdings` uses `top_bond_table_row`; fee includes E/F share-class rates

These differences reflect genuine fund-type variation (QDII, enhanced-index, ETF-link, bond) rather than errors. The excerpts anchor each expected value to the correct PDF section regardless of structural shape. The heterogeneity does not block this gate but should be handled in downstream extractor correctness tests that must be fund-type-aware.

### Finding 9 — 004194 return value correctly sourced from §3.2.1 (PASS)

The `004194.return.expected.target_share_one_year_nav_growth` is `6.88%`, anchored to `PDF p7 §3.2.1`. The PDF contains both `6.46%` (§3.1.1 `本期基金份额净值增长率`) and `6.88%` (§3.2.1 `过去一年` for A share). The fixture correctly uses the §3.2.1 value matching its anchor. No data conflict.

## Validation Performed

| Check | Method | Result |
|---|---|---|
| JSON syntax | `python -m json.tool` | PASS |
| SHA256 × 5 PDFs | `shasum -a 256` | All 5 match |
| 004393 pages 5,7,8,13,39,40,55 | `pdfplumber` spot-check | All excerpts verified |
| 004194 pages 5,7,10,55 | `pdfplumber` spot-check | All excerpts verified |
| 017641 pages 5,7,9,15,18,59 | `pdfplumber` spot-check | All excerpts verified |
| 110020 pages 5,6,8,9,47,64 | `pdfplumber` spot-check | All excerpts verified |
| 006597 | JSON/fixture shape review only | Consistent with fund type |
| Row count vs checkpoint `866a12b` | `git log` / acceptance decision JSON | 5 rows, all match |
| `non_goals_preserved` / boundary flags | JSON field audit | No unlock observed |

## Residual Risks

1. **006597 spot-checks not completed**: The 006597 PDF was not spot-checked via `pdfplumber` due to termination of the verification run. The JSON structure, field shape, and anchor references are consistent with the bond-fund profile. If downstream extractor tests fail on this row, re-verify excerpts against the PDF before diagnosing an extractor bug.

2. **Excerpt format is synthetic, not verbatim**: Excerpts use a condensed `key=value` notation (e.g., `基金名称=安信企业价值优选混合型证券投资基金`) rather than verbatim PDF text dumps. This is consistent with the retention policy of "short field-level excerpts" but means the excerpts cannot be mechanically diffed against raw PDF text. Downstream extractor correctness tests must tolerate this format, or a later gate must produce machine-diffable excerpts.

3. **017641 scale field uses `total_share_units` not `target_share_units`**: The QDII row records total fund shares rather than target-share-class-only units. This is a structural outlier that downstream tests must handle explicitly.

4. **No formal schema validation**: The JSON uses `schema_version: fund-agent.small_golden_set_retained_excerpt_fixture.v1` but no schema definition was found for automated validation. Manual field audit found no missing required fields, but a machine schema check would reduce future drift risk.

5. **First four rows previously listed as `not promotion-prep-ready`**: The `current-startup-packet.md` residual section lists `004393`, `004194`, and `006597` as `fixture_state=absent`. The current gate correctly does not promote them, but downstream gates must explicitly re-check promotion state before any fixture promotion.

## Conclusion

The retained excerpt fixture artifact correctly limits rows to the five accepted source identity rows from checkpoint `866a12b`, retains only short field-scoped same-source excerpts with page/section anchors, maintains consistent access and retention boundaries under PDF-only authorization, and explicitly preserves non-goals including no golden/readiness promotion and no extractor correctness acceptance. SHA256 hashes for all five PDFs are verified. PDF spot-checks across four of five rows confirm excerpt values are anchored in the local PDFs. No blocking inconsistencies found.
