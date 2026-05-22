# P16-S1 Enhanced-index Production Golden Candidate Evidence Implementation（2026-05-22）

## Verdict

`PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY`

本 gate 只创建本 evidence artifact。未修改 source code、tests、golden files、README、`docs/design.md`、`docs/implementation-control.md`、`docs/code_20260519.csv`、RR-13 data、commits、branches、PRs 或外部发布状态。

5 个固定候选的 2024 年报均通过 `FundDocumentRepository.load_annual_report()` 命中，`FundDataExtractor.extract()` 的实际 `classified_fund_type` 均为 `enhanced_index`，未出现 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch` 或 `integrity_error` source blocker。

结论：

| Field | Disposition |
|---|---|
| `index_profile` | 5 个候选均为 `accepted_index_profile_candidate`，但仅限当前 extractor 的 `benchmark_context` / `benchmark_text` / `benchmark_component_text` 证据。`benchmark_index_name` 在复合基准下均为 `null`，不得改写成单一 index name。 |
| `tracking_error` | 5 个候选均为 `blocked_no_direct_tracking_error`。年报内可见 mention 仅为目标/限制/管理策略叙述或无数值叙述；没有 direct observed disclosure。 |

因此，本 gate 没有可进入 tracking-error golden 的候选。`index_profile` 候选仅可进入后续 reviewed golden gate；本 artifact 不添加 golden rows。

## Input Boundary

使用输入：

- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md`
- `docs/reviews/p16-s1-plan-review-controller-judgment-20260522.md`
- `docs/code_20260519.csv` 的固定行 `38-42`
- `FundDocumentRepository.load_annual_report(fund_code, 2024)`
- `FundDataExtractor.extract(fund_code, 2024)`

未读取或引用：

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`
- excluded audit inputs

为避免 `FundDataExtractor.extract()` 拉取净值外部数据，本次注入只读空 `nav_provider`。年报访问和字段抽取仍只经过 `FundDocumentRepository` 与 `FundDataExtractor`。

## Field Mapping

| Plan field | Actual extractor output | Mapping disposition |
|---|---|---|
| `index_profile.index_name` | `IndexProfileValue.benchmark_index_name` | 5 个候选均为 `null`，因为当前 extractor 将“指数收益率 * 权重 + 存款利率 * 权重”识别为 `benchmark_identity_status=composite`。不得把 product name 或 CSV name 补成单一 index name。 |
| `index_profile.benchmark_context` | `IndexProfileValue.benchmark_text` + `IndexProfileValue.benchmark_component_text` | 可接受的 benchmark-context evidence；来源为年报 `§2` 业绩比较基准表格行。 |
| `index_profile.source_tier` | `IndexProfileValue.source_tier` | 实际字段存在，5 个候选均为 `benchmark_context`，并与同一 `§2` anchor 绑定。 |
| provenance / anchor | `ExtractedField.anchors` | 5 个候选均为 `source_kind=annual_report`、`document_year=2024`、`section_id=§2`，且有 page/table/row locator。 |

## Candidate Records

### 1. `004194` 招商中证1000指数增强A

| Item | Evidence |
|---|---|
| selected CSV row | `docs/code_20260519.csv:38` = `招商中证1000指数增强A,004194,国内股票类,` |
| requested document | `report_year=2024`, `report_kind=annual_report` |
| document identity | `DocumentKey(fund_code=004194, year=2024, document_kind=annual_report)`; `document_identity_status=matched` |
| repository source metadata | `source=eid`; `report_name=招商中证1000指数增强型证券投资基金2024年年度报告`; `report_year=2024`; `report_code=FB010010`; `report_desp=年度报告`; `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248907`; `fallback_used=False` |
| source blocker | absent |
| actual classified fund type | `enhanced_index` |
| fund-type source | `basic_identity.extraction_mode=direct`; anchor `annual_report 2024 §2 page=5 table=page-5-table-0 row=fund_name`; note `基金名称：招商中证1000指数增强型证券投资基金` |
| index_profile classification | `accepted_index_profile_candidate` for benchmark context only |
| index_profile value | `benchmark_text=中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%`; `benchmark_identity_status=composite`; `benchmark_index_name=null`; `benchmark_component_text=(中证1000指数收益率, 95%, 同期银行活期存款利率（税后）, 5%)`; `source_tier=benchmark_context`; `methodology_availability=benchmark_only`; `constituents_availability=benchmark_only` |
| index_profile anchor | `annual_report 2024 §2 page=5 table=page-5-table-1 row=benchmark`; note `业绩比较基准：中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` |
| tracking_error classification | `blocked_no_direct_tracking_error` |
| tracking_error extractor output | `extraction_mode=missing`; `note=tracking_error_ambiguous`; `value=null`; anchors absent |
| rejected tracking_error mentions | `§2` target/limit text: `日均跟踪偏离度...不超过0.5%，年化跟踪误差不超过7.75%`; strategy narrative: `力争在控制跟踪误差的基础上获取超越标的指数的投资收益`; same text also appears in `page=5 table=page-5-table-1` investment objective/strategy rows |
| residual | `index_profile` benchmark-context candidate only; no tracking-error golden eligibility; no extractor false negative suspected |

### 2. `005313` 万家中证1000指数增强A

| Item | Evidence |
|---|---|
| selected CSV row | `docs/code_20260519.csv:39` = `万家中证1000指数增强A,005313,国内股票类,` |
| requested document | `report_year=2024`, `report_kind=annual_report` |
| document identity | `DocumentKey(fund_code=005313, year=2024, document_kind=annual_report)`; `document_identity_status=matched` |
| repository source metadata | `source=eid`; `report_name=万家中证1000指数增强型发起式证券投资基金2024年年度报告`; `report_year=2024`; `report_code=FB010010`; `report_desp=年度报告`; `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1254429`; `fallback_used=False` |
| source blocker | absent |
| actual classified fund type | `enhanced_index` |
| fund-type source | `basic_identity.extraction_mode=direct`; anchor `annual_report 2024 §2 page=5 table=page-5-table-0 row=fund_name`; note `基金名称：万家中证1000指数增强型发起式证券投资基金` |
| index_profile classification | `accepted_index_profile_candidate` for benchmark context only |
| index_profile value | `benchmark_text=中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%`; `benchmark_identity_status=composite`; `benchmark_index_name=null`; `benchmark_component_text=(中证1000指数收益率, 95%, 一年期人民币定期存款利率（税后）, 5%)`; `source_tier=benchmark_context`; `methodology_availability=benchmark_only`; `constituents_availability=benchmark_only` |
| index_profile anchor | `annual_report 2024 §2 page=5 table=page-5-table-1 row=benchmark`; note `业绩比较基准：中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` |
| tracking_error classification | `blocked_no_direct_tracking_error` |
| tracking_error extractor output | `extraction_mode=missing`; `note=年报未直接披露跟踪误差`; `value=null`; anchors absent |
| rejected tracking_error mentions | `§2` target/limit text: `日均跟踪偏离度的绝对值不超过0.5%、年跟踪误差不超过7.75%`; same target text appears in `page=5 table=page-5-table-1` investment objective row |
| residual | `index_profile` benchmark-context candidate only; no tracking-error golden eligibility; no extractor false negative suspected |

### 3. `017644` 博道中证1000指数增强A

| Item | Evidence |
|---|---|
| selected CSV row | `docs/code_20260519.csv:40` = `博道中证1000指数增强A,017644,国内股票类,` |
| requested document | `report_year=2024`, `report_kind=annual_report` |
| document identity | `DocumentKey(fund_code=017644, year=2024, document_kind=annual_report)`; `document_identity_status=matched` |
| repository source metadata | `source=eid`; `report_name=博道中证1000指数增强型证券投资基金2024年年度报告`; `report_year=2024`; `report_code=FB010010`; `report_desp=年度报告`; `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1256479`; `fallback_used=False` |
| source blocker | absent |
| actual classified fund type | `enhanced_index` |
| fund-type source | `basic_identity.extraction_mode=direct`; anchor `annual_report 2024 §2 page=5 table=page-5-table-0 row=fund_name`; note `基金名称：博道中证1000指数增强型证券投资基金` |
| index_profile classification | `accepted_index_profile_candidate` for benchmark context only |
| index_profile value | `benchmark_text=中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%`; `benchmark_identity_status=composite`; `benchmark_index_name=null`; `benchmark_component_text=(中证1000指数收益率, 95%, 同期银行活期存款利率(税后), 5%)`; `source_tier=benchmark_context`; `methodology_availability=benchmark_only`; `constituents_availability=benchmark_only` |
| index_profile anchor | `annual_report 2024 §2 page=6 table=page-6-table-0 row=benchmark`; note `业绩比较基准：中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` |
| tracking_error classification | `blocked_no_direct_tracking_error` |
| tracking_error extractor output | `extraction_mode=missing`; `note=年报未直接披露跟踪误差`; `value=null`; anchors absent |
| rejected tracking_error mentions | strategy narrative without observed value: `在控制跟踪误差的基础上力求获得超越标的指数的业...`; same narrative appears in `page=5 table=page-5-table-1` investment strategy row |
| residual | `index_profile` benchmark-context candidate only; no tracking-error golden eligibility; no extractor false negative suspected |

### 4. `019918` 招商中证2000指数增强A

| Item | Evidence |
|---|---|
| selected CSV row | `docs/code_20260519.csv:41` = `招商中证2000指数增强A,019918,国内股票类,` |
| requested document | `report_year=2024`, `report_kind=annual_report` |
| document identity | `DocumentKey(fund_code=019918, year=2024, document_kind=annual_report)`; `document_identity_status=matched` |
| repository source metadata | `source=eid`; `report_name=招商中证2000指数增强型证券投资基金2024年年度报告`; `report_year=2024`; `report_code=FB010010`; `report_desp=年度报告`; `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1249250`; `fallback_used=False` |
| source blocker | absent |
| actual classified fund type | `enhanced_index` |
| fund-type source | `basic_identity.extraction_mode=direct`; anchor `annual_report 2024 §2 page=5 table=page-5-table-0 row=fund_name`; note `基金名称：招商中证2000指数增强型证券投资基金` |
| index_profile classification | `accepted_index_profile_candidate` for benchmark context only |
| index_profile value | `benchmark_text=中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%`; `benchmark_identity_status=composite`; `benchmark_index_name=null`; `benchmark_component_text=(中证2000指数收益率, 95%, 中国人民银行人民币活期存款利率（税后）, 5%)`; `source_tier=benchmark_context`; `methodology_availability=benchmark_only`; `constituents_availability=benchmark_only` |
| index_profile anchor | `annual_report 2024 §2 page=5 table=page-5-table-1 row=benchmark`; note `业绩比较基准：中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` |
| tracking_error classification | `blocked_no_direct_tracking_error` |
| tracking_error extractor output | `extraction_mode=missing`; `note=tracking_error_ambiguous`; `value=null`; anchors absent |
| rejected tracking_error mentions | `§2` target/limit text: `日均跟踪偏离度的绝对值不超过0.5%，年化跟踪误差不超过7.75%`; strategy narrative: `在有效控制基金跟踪误差的前提下，对基金资产进行合理配置`; same text appears in `page=5 table=page-5-table-1` investment objective/strategy rows |
| residual | `index_profile` benchmark-context candidate only; no tracking-error golden eligibility; no extractor false negative suspected |

### 5. `019923` 华泰柏瑞中证2000指数增强A

| Item | Evidence |
|---|---|
| selected CSV row | `docs/code_20260519.csv:42` = `华泰柏瑞中证2000指数增强A,019923,国内股票类,` |
| requested document | `report_year=2024`, `report_kind=annual_report` |
| document identity | `DocumentKey(fund_code=019923, year=2024, document_kind=annual_report)`; `document_identity_status=matched` |
| repository source metadata | `source=eid`; `report_name=华泰柏瑞中证2000指数增强型证券投资基金2024年年度报告`; `report_year=2024`; `report_code=FB010010`; `report_desp=年度报告`; `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1258961`; `fallback_used=False` |
| source blocker | absent |
| actual classified fund type | `enhanced_index` |
| fund-type source | `basic_identity.extraction_mode=direct`; anchor `annual_report 2024 §2 page=5 table=page-5-table-0 row=fund_name`; note `基金名称：华泰柏瑞中证2000指数增强型证券投资基金` |
| index_profile classification | `accepted_index_profile_candidate` for benchmark context only |
| index_profile value | `benchmark_text=中证2000指数收益率×95%＋人民币活期存款税后利率×5%`; `benchmark_identity_status=composite`; `benchmark_index_name=null`; `benchmark_component_text=(中证2000指数收益率, 95%, 人民币活期存款税后利率, 5%)`; `source_tier=benchmark_context`; `methodology_availability=benchmark_only`; `constituents_availability=benchmark_only` |
| index_profile anchor | `annual_report 2024 §2 page=6 table=page-6-table-0 row=benchmark`; note `业绩比较基准：中证2000指数收益率×95%＋人民币活期存款税后利率×5%` |
| tracking_error classification | `blocked_no_direct_tracking_error` |
| tracking_error extractor output | `extraction_mode=missing`; `note=年报未直接披露跟踪误差`; `value=null`; anchors absent |
| rejected tracking_error mentions | `§2` target/limit text: `日均跟踪偏离度的绝对值不超过0.5%，年跟踪误差不超过8%`; strategy narrative: `降低组合跟踪误差`; strategy narrative: `追求跟踪偏离度和跟踪误差的最小化`; same text appears in `page=5 table=page-5-table-1` investment objective/strategy rows |
| residual | `index_profile` benchmark-context candidate only; no tracking-error golden eligibility; no extractor false negative suspected |

## Tracking Error Acceptance Check

| Candidate | observed_value | period_label | annualization_support | source_type | calculation_method | parseable value | complete anchor | Disposition |
|---|---:|---|---|---|---|---|---|---|
| `004194` | absent | absent | absent | absent | absent | no | no | `blocked_no_direct_tracking_error`; target/limit and strategy narrative only |
| `005313` | absent | absent | absent | absent | absent | no | no | `blocked_no_direct_tracking_error`; target/limit only |
| `017644` | absent | absent | absent | absent | absent | no | no | `blocked_no_direct_tracking_error`; strategy narrative without value |
| `019918` | absent | absent | absent | absent | absent | no | no | `blocked_no_direct_tracking_error`; target/limit and strategy narrative only |
| `019923` | absent | absent | absent | absent | absent | no | no | `blocked_no_direct_tracking_error`; target/limit and strategy narrative only |

No candidate satisfies the required direct observed disclosure contract:

```text
observed value + period label + annualization support + source_type=direct_disclosure
+ calculation_method=disclosed + parseable value + complete annual-report anchor
```

## Commands And Results

| Command | Result |
|---|---|
| `sed -n '1,240p' docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | Confirmed accepted plan scope, exact candidate order, source taxonomy, index_profile/tracking_error evidence contracts, and artifact path. |
| `sed -n '1,240p' docs/reviews/p16-s1-plan-review-controller-judgment-20260522.md` | Confirmed controller verdict `ACCEPTED_READY_FOR_EVIDENCE_ACQUISITION_IMPLEMENTATION` and implementation constraints. |
| `nl -ba docs/code_20260519.csv \| sed -n '38,42p'` | Confirmed selected rows 38-42 exactly match `004194`, `005313`, `017644`, `019918`, `019923` in required order. |
| `uv run python - <<'PY' ...` | Used only `FundDocumentRepository.load_annual_report()` and `FundDataExtractor.extract()` for annual-report access/extraction. Result: 5/5 document identities matched; 5/5 repository source `eid`; 5/5 `fallback_used=False`; 5/5 actual `classified_fund_type=enhanced_index`; 5/5 `index_profile.source_tier=benchmark_context`; 0/5 accepted direct `tracking_error`. |
| `git status --short` before artifact write | Showed only pre-existing untracked excluded files: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`. They were not read or modified. |
| `git diff --check HEAD` after artifact write | Passed with no output, exit code `0`. Note: the artifact is a new untracked file, so this command checks tracked diff state and does not list the untracked artifact content. |
| `git status --short` after artifact write | Shows only the three pre-existing untracked excluded files plus this new artifact path. |
| `git diff --name-only HEAD` after artifact write | No output because there are no tracked-file diffs and the new artifact is untracked. |

## Residuals

- `index_profile`: accepted only for current extractor benchmark-context output. The current extractor does not expose a single `benchmark_index_name` for these composite benchmarks; later golden review must decide whether to golden the actual full `IndexProfileValue` shape.
- `tracking_error`: blocked for all five candidates. No candidate should be promoted to tracking-error golden from target/limit text, manager narrative, benchmark-only text, standard-deviation-only text, ambiguous text, or incomplete anchors.
- `defer_extractor_false_negative`: not used. No repository-loaded annual report showed anchored, direct-looking observed tracking-error evidence that the extractor missed.
