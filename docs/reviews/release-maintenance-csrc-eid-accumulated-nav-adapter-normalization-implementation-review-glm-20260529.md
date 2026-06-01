# CSRC EID Accumulated NAV Adapter Normalization — Implementation Review (GLM)

日期：2026-05-29
角色：review worker（GLM）
Gate：`CSRC EID accumulated NAV adapter normalization implementation gate`
Accepted plan：`6dce229`
Implementation evidence：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md`

## Verdict：**accepted**

无 blocking findings。实现与 accepted plan 高度一致，fail-closed 语义完备，无 drawdown metric/blocker 解除泄露。

---

## Findings

按严重度排序。无 CRITICAL / HIGH。

### F1. [LOW] source_query_params 混入非 HTTP provenance 元数据

**文件**：`csrc_eid_nav_source.py:476-488`
**函数**：`CsrcEidNavSource._load_all_pages`

`source_query_params` 同时包含实际 HTTP 查询参数（`fundCode`、`classification`、`limit`、`start`）和请求上下文元数据（`requested_fund_code`、`share_class`、`force_refresh`、`start_date`、`end_date`）。前者是 source 发出的实际参数，后者是 repository 传入的请求上下文。

**风险**：future consumer 如果把 `source_query_params` 当作可重放 HTTP 参数使用，会因多出 `requested_fund_code` 等字段而困惑。当前无 consumer 做此假设。

**建议**：可在后续 gate 考虑拆分为 `source_http_params` 和 `request_context`，但当前不阻塞。fake adapter 只返回 HTTP 子集，tests 与 real output 的不一致已被控制在合理范围。

### F2. [LOW] 累计净值路径无显式重复日期检测

**文件**：`nav_repository.py:415-498`
**函数**：`_normalize_csrc_accumulated_records`

该函数按日期排序输出但不检测重复日期。plan §3 Slice 3 原文 "Duplicate dates remain model-level integrity_error"，即重复日期应在 model 层检测——这是 pre-existing 行为，raw-unit 路径同样不在此处检测。

**风险**：若 CSRC EID 返回同一估值日期的两行，会生成两条 `FundNavRecord`，下游 consumer 需自行处理。CSRC EID 真实数据未观察到此情况（smoke 1807 条无重复）。

**建议**：在后续 model-level invariant gate 中统一补强，不阻塞本 gate。

### F3. [LOW] `_normalize_raw_unit_series` 与 `load_nav_series` 存在重复空 records 检查

**文件**：`nav_repository.py:154-160` 与 `nav_repository.py:228-234`

`load_nav_series()` 在分发前检查 `not raw_source.records` 并 raise `not_found`；`_normalize_raw_unit_series()` 开头再次做相同检查。防御性编码，无 correctness 风险，仅冗余。

### F4. [INFO] `NavSourceMetadata.__post_init__` docstring 冗余

**文件**：`nav_models.py`（`__post_init__` 方法）

方法的 Args/Returns/Raises docstring 均为"无"/"无返回值"/"无显式抛出"。不影响 correctness，但与同模块其他方法风格一致，可保留也可后续压缩。

---

## Verification Checklist

### Source Identity & Classification

- [x] `CsrcEidNavSource` 通过 3 步验证：search → detail → classification
- [x] search 解析 `fundId=5755`，非 5755 触发 `identity_mismatch`
- [x] detail 页解析 A/C/E/F 四个份额分类链接，缺一则 `identity_mismatch`
- [x] classification 行级别验证 `基金代码=006597` 且 `分级代码=请求份额代码`
- [x] `_EXPECTED_SHARE_CLASSES` 固定映射 `006597=A/2030-1010`、`006598=C/2030-1020`、`014217=E/2030-1040`、`022176=F/2030-1050`
- [x] `_select_share_class()` 验证 `fund_code/share_class/classification/product_fund_code` 四重一致性
- [x] A/C/E/F 各自输出独立 `FundNavSeries`，无 product-level 混合

### F Direct-Search Gap

- [x] F (`022176`) direct search 返回 `not_found/schema_drift` 时回退到 `_PRODUCT_FUND_CODE="006597"`
- [x] 回退后仍要求 detail 页包含 F code/classification，否则 `identity_mismatch`
- [x] 非 F 基金代码不触发回退路径（hardcoded `"022176"` 检查）
- [x] 回退仅在 `NavDataContractError` 且 `category in {"not_found", "schema_drift"}` 时生效，其他异常直接上抛

### Endpoint / Params / rnd/t

- [x] Search: `POST /fund/disclose/validate_fund.do`，form `cFundCode`，无 rnd/t
- [x] Detail: `GET /fund/disclose/fund_detail_search.do`，param `cFundCode`，无 rnd/t
- [x] Classification: `GET /fund/disclose/list_net_classification.do`，params `fundCode/classification/limit/start`，无 rnd/t

### HTTP / Retry / Timeout

- [x] `httpx.Timeout(connect=10, read=30, write=10, pool=10)` 与 plan 一致
- [x] 最多 3 次尝试（initial + 2 retries）
- [x] 重试范围：`_TransientHttpError`（5xx）、`httpx.TimeoutException`、`httpx.TransportError`
- [x] 最终失败 `unavailable` + cause preserved
- [x] HTTP 4xx → `unavailable`；空响应 → `schema_drift`

### HTML Parser / Pagination

- [x] `_TableParser` 基于 stdlib `html.parser.HTMLParser`，无 BeautifulSoup/lxml
- [x] `_find_header_index` 验证必需表头（`基金代码/分级代码/基金简称/单位净值/累计净值/估值日期`）
- [x] 分页 total 声明必须存在且一致
- [x] 跨页 total/total_pages 变化 → `integrity_error`
- [x] 当页 range_start/range_end 与 start/limit 不一致 → `integrity_error`
- [x] 当页 row 数与声明不一致 → `integrity_error`
- [x] 最终总 row 数与 total 不一致 → `integrity_error`
- [x] total=0（verified identity 后）→ `not_found`

### Failure Taxonomy

- [x] 8 类不扩展：`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`
- [x] 每类归类与 plan §4.6 一致

### Repository Default Source / No Fallback

- [x] `FundNavRepository()` 无参默认 `CsrcEidNavSource()`
- [x] CSRC EID classified error 直接上抛，无 fallback 到 Akshare/stock-sdk/Eastmoney
- [x] constructor injection 保留：tests 可传入 `_FakeRawNavAdapter` 进入 raw-unit 分支

### Constructor Injection Raw-Unit Compat

- [x] `FundNavDataAdapter.load_raw_nav_source()` 接受 `share_class/start_date/end_date` 但显式忽略（`_ = (share_class, start_date, end_date)`）
- [x] 返回 `source_nav_type="unit_nav"/source_adjustment_basis="raw_unit_nav"`
- [x] 既有 `load_nav_data()` 行为不变

### Protocol / DTO

- [x] `_RawNavSourceResult` 显式字段，无 `extra_payload`/`**kwargs`
- [x] `_NavSourceAdapter` Protocol 签名显式：`fund_code, *, share_class, start_date, end_date, force_refresh`
- [x] Test `test_nav_source_adapter_protocol_has_explicit_signature` 验证无 `extra_payload` / `VAR_KEYWORD`
- [x] `source_nav_type`/`source_adjustment_basis` 为 required 字段，非 optional

### source_nav_type / source_adjustment_basis Branching

- [x] `("unit_nav", "raw_unit_nav")` → `_normalize_raw_unit_series`
- [x] `("accumulated_nav", "accumulated_nav")` → `_normalize_accumulated_nav_series`
- [x] 其他组合 → `adjustment_basis_unknown` fail-closed

### CSRC Accumulated Normalization

- [x] 直接读 `估值日期` 作为 `FundNavRecord.date`
- [x] 直接读 `累计净值` 作为 `FundNavRecord.nav_value`（Decimal 正数）
- [x] `单位净值` 仅 diagnostics（`_validate_csrc_unit_nav_diagnostics`），不作为 typed `nav_value`
- [x] 空累计净值（requested window 外）→ 丢弃并记录 evidence
- [x] 空累计净值（requested window 内）→ `missing_date_range`
- [x] 全部空累计净值 → `adjustment_basis_unknown`
- [x] 累计净值 ≤ 0 → `integrity_error`
- [x] 单位净值缺失/空/不可解析 → `schema_drift`
- [x] 单位净值 ≤ 0 → `integrity_error`
- [x] `raw_change_rate=None`，不用单位净值推导

### strong_drawdown_evidence_eligible

- [x] CSRC accumulated verified series: `strong_drawdown_evidence_eligible=True`
- [x] 仅 source-level eligibility，不产生 drawdown metric
- [x] docs 多处显式声明："当前未实现 drawdown metric，未解除债券基金 drawdown_stress blocker"
- [x] 无 consumer 可误用为 blocker 解除——bond extractor / score / snapshot / quality gate / golden 均未修改
- [x] Raw-unit path 保持 `strong_drawdown_evidence_eligible=False`

### stock-sdk Runtime Rejection

- [x] `test_no_stock_sdk_runtime_dependency`：source code 无 `stock-sdk`/`subprocess`/`node` 痕迹
- [x] `test_stock_sdk_date_shift_classified_as_integrity_error`：date-shift fixture 归为 `integrity_error`
- [x] `test_dividend_list_cross_check_cannot_construct_fund_nav_series`：dividend-only 不能构造 `FundNavSeries`
- [x] 三者均为 test-local helper/diagnostics，未成为 runtime adapter

### Tests Coverage

- [x] A/C/E/F 份额分离测试：`test_repository_csrc_share_classes_remain_separated`
- [x] A/C 早期空累计净值（window 外丢弃 + window 内 raise）：`test_repository_csrc_blank_accumulated_before_window_is_dropped` + `test_repository_csrc_blank_accumulated_inside_window_raises_missing_date_range`
- [x] 全部空累计净值：`test_repository_csrc_all_blank_accumulated_raises_adjustment_basis_unknown`
- [x] 单位净值 diagnostics（blank/non-numeric/negative）：parametrized `test_repository_csrc_malformed_values_raise`
- [x] 分页边界（`total % limit != 0`）：`test_csrc_source_pagination_last_page_boundary_success`
- [x] 分页 integrity（total mismatch / total changes / last page mismatch）：parametrized `test_csrc_source_pagination_integrity_errors`
- [x] Source failure taxonomy（missing classes / empty list / bad header / 503 / transport）：parametrized `test_csrc_source_failure_taxonomy`
- [x] Identity mismatch（code/share_class 冲突 + returned code 冲突）：两个独立测试
- [x] Explicit params 传递：`test_repository_passes_explicit_params_to_source_adapter`

### Docs

- [x] `docs/design.md`：只写当前实现事实，不宣称 drawdown metric 已完成或 permanent primary source
- [x] `fund_agent/fund/README.md`：当前 source 行为、份额分离、provenance、failure categories
- [x] `tests/README.md`：deterministic fixtures + real smoke 说明
- [x] 无 drawdown_stress blocker 解除措辞

### Validation Evidence

- [x] `ruff check .`：All checks passed
- [x] Focused pytest：64 passed
- [x] Full pytest：925 passed，92.37% coverage
- [x] Real CSRC EID smoke：A(1807)/C(1807)/E(994)/F(398) 四份额全部成功，identity verified，accumulated_nav confirmed

---

## Residual Risks

1. **CSRC EID endpoint 可用性**：依赖公开 HTTP endpoint，无 SLA 保证。未来 endpoint 变化（schema/auth/下线）将触发 `schema_drift`/`unavailable`/`identity_mismatch` fail-closed。建议后续 gate 评估缓存策略。

2. **006597 家族硬编码**：`_EXPECTED_SHARE_CLASSES`/`_VERIFIED_FUND_ID`/`_PRODUCT_FUND_CODE` 固定为 006597 家族。扩展到其他基金家族需新增 verified identity 常量并修改 `_parse_share_class_from_text`。当前 scope 正确限定为单家族。

3. **F direct-search 回退路径硬编码**：`_resolve_fund_id` 中 `if fund_code != "022176"` 硬编码了 F 的特殊处理。如果未来有其他份额出现 direct-search gap，需通用化。当前 scope 内可接受。

4. **重复日期检测缺失**：`_normalize_csrc_accumulated_records` 不检测重复估值日期。应在后续 model-level invariant gate 中与 raw-unit 路径统一补强。

5. **`source_query_params` 语义混合**：实际 HTTP 参数与请求上下文元数据共存于同一 tuple。Future consumer 应区分使用。

6. **drawdown_stress blocker 未解除**：`strong_drawdown_evidence_eligible=True` 仅表示 source-level eligibility。后续需要独立的 reviewed drawdown metric gate 才能解除 blocker。

---

## Scope Boundary Verification

- [x] 未修改 bond extractor、score、snapshot、quality gate、golden fixture
- [x] 未修改 `data_extractor.py`、`extraction_snapshot.py`、`extraction_score.py`
- [x] 未修改 Service/UI/Host/Agent-dayu
- [x] 未引入 stock-sdk runtime dependency、Node subprocess、Eastmoney fallback
- [x] 未 commit/push/PR/merge/release
- [x] `git diff --name-only` 仅含允许文件（已在 evidence 中确认）
