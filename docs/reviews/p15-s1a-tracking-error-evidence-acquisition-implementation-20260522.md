# P15-S1A Tracking Error Evidence Acquisition Implementation（2026-05-22）

## Verdict

`BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`

通过 `FundDocumentRepository` 和 `FundDataExtractor` 边界读取 `001548` 2024 年报后，未发现可支持生产
`tracking_error` golden rows 的 reviewed direct observed disclosure evidence。

结论：

- `001548` 2024 年报身份一致：基金代码 `001548`、年份 `2024`、文档类型 `annual_report`。
- `FundDataExtractor.extract("001548", 2024)` 将基金类型识别为 `index_fund`。
- `extract_performance(report).tracking_error` 返回 `extraction_mode="missing"`、`note="tracking_error_ambiguous"`、`value=None`、`anchors=()`。
- 年报关键词命中均属于 investment-objective target/limit、manager narrative 或同类目标/控制语义；没有报告期实际跟踪误差数值。
- 本 gate 不得添加 production golden rows；后续如要新增 `tracking_error` golden，必须先有单独 gate 接受 direct observed disclosure evidence。

## Request

| Field | Value |
|---|---|
| `fund_code` | `001548` |
| `report_year` | `2024` |
| `document_kind` | `annual_report` |
| `force_refresh` | `False` |
| Access boundary | `FundDocumentRepository.load_annual_report()` and `FundDataExtractor.extract()` |

## Repository Provenance

| Field | Value |
|---|---|
| Parsed identity | `DocumentKey(fund_code="001548", year=2024, document_kind="annual_report")` |
| Sections present | `§1`, `§2`, `§3`, `§4`, `§5`, `§8`, `§9`, `§10` |
| Parsed tables | `105` |
| Source metadata | `None` in parsed-cache hit result |
| Cache provenance | `parsed_cache_hit=True`, `pdf_cache_hit=False`, `pdf_path=None`, `source_metadata_present=False`, `cache_schema_version=1` |
| Fallback metadata | No fallback source metadata present in this cached parsed report |

Identity check passed. Because source metadata is absent on this parsed-cache hit, this artifact records cache provenance but does not infer an external source URL or fallback status beyond available repository metadata.

Residual note: a future retry/review may use explicit `force_refresh=True` through `FundDocumentRepository` to refresh source metadata. The current evidence classification remains valid because every observed candidate is target/limit language or manager narrative, not direct observed disclosure.

## Structured Extraction Decision

| Field | Value |
|---|---|
| Fund type | `index_fund` |
| Tracking error extraction mode | `missing` |
| Note | `tracking_error_ambiguous` |
| Value | `None` |
| Anchors | `()` |

The structured extractor did not accept any direct `tracking_error` value. This matches the evidence inventory below: the only numeric candidates are investment objective limits, not observed disclosure.

## Accepted Evidence

None.

There is no annual-report row or text line that simultaneously provides:

- an actual observed tracking-error value;
- a directly supported period label;
- a directly supported annualization status;
- `source_type="direct_disclosure"`;
- `calculation_method="disclosed"`;
- a complete annual-report anchor.

## Candidate Classification

The keyword inventory found 12 raw hits. All were rejected for production golden use.

| Location | Short excerpt | Classification | Reason |
|---|---|---|---|
| 年报2024§2 line 33 | “偏离度和跟踪误差的最小化。” | investment-objective target/limit | Adjacent lines identify this as `投资目标`; no observed value. |
| 年报2024§2 line 56 | “紧密跟踪标的指数，追求跟踪偏离度和跟踪误差的最” | investment-objective target/limit | Part of target paragraph; no observed value. |
| 年报2024§2 line 57 | “投资目标 小化，本基金力争将日均跟踪偏离度控制在0.2%以” | investment-objective target/limit | `跟踪偏离度` / daily tracking deviation is not the same as observed annualized `tracking_error`; `0.2%` is a daily deviation control target, not golden evidence. |
| 年报2024§2 line 58 | “内，年化跟踪误差控制在2%以内。” | investment-objective target/limit | `2%` is an annualized tracking-error control limit, not an observed value. |
| 年报2024§4 line 87 | “相关和跟踪误差最小化。” | manager narrative | Strategy narrative; no observed value. |
| 年报2024§4 line 88 | “出于基金充分投资、减少交易成本、降低跟踪误差的需要，基于谨慎原则，报告期” | manager narrative | Risk-management narrative; no observed value. |
| 年报2024§4 line 92 | “控制联接基金跟踪误差的前提是控制ETF基金的跟踪误差，报告期内，本基金跟踪” | manager narrative | Discusses control premise; no measured value. |
| 年报2024§4 line 93 | “误差的来源主要是申购赎回、打新、成分股调整以及ETF对指数的跟踪误差。当由于申” | manager narrative | Describes sources of tracking error; no measured value. |
| 年报2024§4 line 95 | “基金采取被动复制与组合优化相结合的方式跟踪指数。在ETF的跟踪误差管理上，我们” | manager narrative | Management discussion; no numeric disclosure. |
| 年报2024§4 line 97 | “造成跟踪误差的扩大，争取保障联接基金的跟踪效果。” | manager narrative | Management discussion; no numeric disclosure. |
| 年报2024§5 line 1407 | “是通过投资于目标ETF，紧密跟踪标的指数，追求跟踪偏离度和跟踪误差最小化。本基” | investment-objective target/limit | Objective/risk-control framing; no observed value. |
| 年报2024 page 6 table 1 header | “投资目标……日均跟踪偏离度控制在0.2%以内，年化跟踪误差控制在2%以内。” | investment-objective target/limit | Table header encodes objective limits only; cannot prove observed tracking error. |

Classification summary:

| Class | Count | Golden eligibility |
|---|---:|---|
| direct observed disclosure | 0 | No evidence found |
| benchmark-only | 0 | Not applicable; benchmark evidence separately supports only `index_profile` |
| investment-objective target/limit | 6 | Rejected |
| manager narrative | 6 | Rejected |
| standard-deviation-only | 0 | Not found; not used |
| meta: direct observed disclosure not found | n/a | Meta result, not a 13th candidate |

The benchmark evidence observed separately supports only `index_profile`: `上证50指数收益率×95%＋银行活期存款利率（税后）×5%`.

## Anchor Appendix

| Anchor | Candidate class | Reusable for golden? |
|---|---|---|
| 年报2024§2 lines 31-33 | investment-objective target/limit | No |
| 年报2024§2 lines 56-58 | investment-objective target/limit | No |
| 年报2024§4 lines 85-87 | manager narrative | No |
| 年报2024§4 lines 88-90 | manager narrative | No |
| 年报2024§4 lines 92-93 | manager narrative | No |
| 年报2024§4 lines 95-97 | manager narrative | No |
| 年报2024§5 line 1407 | investment-objective target/limit | No |
| 年报2024 page 6 table 1 header | investment-objective target/limit | No |

Line numbers are section-local line numbers from the parsed `ParsedAnnualReport` text returned by `FundDocumentRepository`.
Anchor rows are grouped by section/range for review readability, so one anchor row may cover multiple raw candidate lines from the 12-hit inventory.

## Golden Decision

`do_not_edit_golden`

Production `tracking_error` golden rows for `001548` remain blocked. Adding rows from the `0.2%` daily tracking-deviation control target or `2%` annualized tracking-error control target would violate the P15-S1A source contract because those values are investment-objective limits, not reviewed direct observed disclosure.

## Validation

Commands run:

| Command | Result | Key fact |
|---|---|---|
| `.venv/bin/python - <<'PY' ... FundDocumentRepository().load_annual_report("001548", 2024) ... extract_performance(report) ... PY` | Passed | Repository identity matched; structured `tracking_error` was missing with `tracking_error_ambiguous`; 12 keyword hits inventoried before context dedupe. |
| `.venv/bin/python - <<'PY' ... context inventory ... PY` | Passed | Context confirmed all hits are objective/target-limit or manager narrative; no direct observed value. |
| `.venv/bin/python - <<'PY' ... FundDataExtractor().extract("001548", 2024) ... PY` | Passed | Bundle identified `index_fund`; `tracking_error` remained missing with no anchors. |
| `.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q` | Passed | `14 passed`; existing extractor tests cover direct disclosure, target-only, ambiguous, standard deviation, and table/text consistency behavior. |

## Scope Self-Check

- No source code changed.
- No tests changed.
- No README changed.
- No golden answer or selected-fund data changed.
- No production `tracking_error` golden rows added.
- No Dayu Host/Engine/tool loop, external runtime, LLM audit, Evidence Confirm, external index adapter, or calculated tracking-error path introduced.
- Excluded local drafts and excluded repo-audit artifact were not used as evidence.
