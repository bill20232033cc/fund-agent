# CSRC EID Accumulated NAV Adapter Normalization Implementation Review

日期：2026-05-29
角色：review worker（MiMo）
Gate：`CSRC EID accumulated NAV adapter normalization implementation gate`
Gate classification：`heavy`
Accepted plan commit：`6dce229`
Implementation evidence：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md`

## 1. Review Scope

已读取：
- `AGENTS.md`
- Accepted plan：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`
- Implementation evidence artifact
- 全部 production diff（`nav_source_contract.py`、`nav_models.py`、`nav_data.py`、`csrc_eid_nav_source.py`、`nav_repository.py`）
- 全部 test diff（`test_nav_repository_contract.py`、`test_csrc_eid_nav_source.py`、`test_nav_data.py`）
- docs diff（`docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md`）
- `fund_agent/fund/data/__init__.py`（确认未导出 CSRC EID 私有符号）

## 2. Verdict

**accepted**

无 blocking findings。实现与 accepted plan 一致，correctness、fail-closed 语义、份额分离、provenance 显式性、failure taxonomy、stock-sdk 拒绝和文档事实性均通过验证。

## 3. Findings

### 3.1 Residual Risk — `force_refresh` 出现在 CSRC EID `source_query_params` 中

- 文件：`fund_agent/fund/data/csrc_eid_nav_source.py:476-484`
- 严重度：low（non-blocking）
- 说明：`_load_all_pages` 在构造 `query_params` 时包含 `("force_refresh", str(force_refresh))`，但 `force_refresh` 不是 CSRC EID 公开 endpoint 的实际查询参数，它是 repository/adapter 层的控制参数。plan §4.5 的 provenance contract 示例只列出了 `fundCode`、`classification`、`limit`、`start` 等实际 CSRC 参数，以及 `requested_fund_code`、`share_class` 等请求上下文参数。将控制参数混入 `source_query_params` 不影响功能正确性，但语义上略有偏差。
- 建议：后续 cleanup gate 可将 `force_refresh` 从 `source_query_params` 移除，或在 plan 中显式确认该参数属于 adapter 请求上下文而非 CSRC 来源查询参数。当前不阻断 acceptance。

### 3.2 Residual Risk — `_parse_share_class_from_text` 正则依赖 detail 页特定格式

- 文件：`fund_agent/fund/data/csrc_eid_nav_source.py:681-707`
- 严重度：low（non-blocking）
- 说明：detail 页份额解析依赖 `净值日报{name}({code})` 格式的正则匹配。若 CSRC EID detail 页 HTML 结构变化（如基金名称包含括号、格式变化），该解析会返回 `None`，最终触发 `identity_mismatch` fail-closed。当前实现的 fail-closed 行为正确，但该正则的健壮性取决于 CSRC EID 页面格式稳定性。
- 建议：该风险已被 plan §4.6 failure taxonomy 中的 `schema_drift`/`identity_mismatch` 覆盖。若后续 CSRC EID 页面格式变化，adapter 会正确 fail-closed 并记录分类错误。无需当前修改。

### 3.3 Residual Risk — CSRC EID `_EXPECTED_SHARE_CLASSES` 硬编码常量

- 文件：`fund_agent/fund/data/csrc_eid_nav_source.py:41-46`
- 严重度：low（non-blocking）
- 说明：`_EXPECTED_SHARE_CLASSES` 将 006597 家族 A/C/E/F 的基金代码和分类 ID 硬编码为模块级常量。这些值是已验证的 identity（plan §4.3），adapter 在 detail 页解析后会与这些期望值交叉验证。若未来新增份额类别，需要更新该常量和 `_parse_detail_share_classes` 中的 `missing` 检查。
- 建议：当前 gate 范围只覆盖 006597 家族，该硬编码是 accepted design decision。未来扩展时需同步更新。

## 4. Review Checklist

### 4.1 CSRC EID Source Identity

| 检查项 | 结果 |
|--------|------|
| Search endpoint `POST /fund/disclose/validate_fund.do` 正确使用 | ✅ `csrc_eid_nav_source.py:362-367` |
| Detail endpoint `GET /fund/disclose/fund_detail_search.do` 正确使用 | ✅ `csrc_eid_nav_source.py:275-279` |
| Classification endpoint `GET /fund/disclose/list_net_classification.do` 正确使用 | ✅ `csrc_eid_nav_source.py:427` |
| 不依赖随机 `rnd`/`t` 参数 | ✅ 无 `rnd`/`t` 出现 |
| A/C/E/F 分份额独立输出 | ✅ `_select_share_class` 按份额验证；test `test_csrc_source_proves_all_share_class_mappings` 覆盖 |
| F direct-search gap fail-closed | ✅ `csrc_eid_nav_source.py:370-381`：search 失败后回退产品锚点，detail 页必须验证 F code/classification |
| fundId=5755 验证 | ✅ `csrc_eid_nav_source.py:382-388`：search 和 detail 双重验证 |

### 4.2 HTTP/Parser/Pagination

| 检查项 | 结果 |
|--------|------|
| httpx timeout policy 正确 | ✅ `connect=10, read=30, write=10, pool=10` |
| retry policy 正确（3 次，timeout/transport/5xx） | ✅ `csrc_eid_nav_source.py:517-547` |
| 4xx 不重试 | ✅ 非 5xx 直接 raise |
| stdlib html.parser | ✅ `_TableParser(HTMLParser)` |
| 分页 total mismatch → `integrity_error` | ✅ `csrc_eid_nav_source.py:444-449`；tests 覆盖 |
| 分页 total=0 → `not_found` | ✅ `csrc_eid_nav_source.py:438-443` |
| 最后一页 row 数验证 | ✅ `csrc_eid_nav_source.py:459-464`；test `test_csrc_source_pagination_last_page_boundary_success` 覆盖 |
| 总 row 数与 total 一致性 | ✅ `csrc_eid_nav_source.py:470-475` |

### 4.3 Failure Taxonomy

| 检查项 | 结果 |
|--------|------|
| 8 类分类正确使用 | ✅ `not_found`/`unavailable`/`schema_drift`/`identity_mismatch`/`integrity_error`/`adjustment_basis_unknown`/`missing_date_range`/`insufficient_records` |
| 未新增 taxonomy | ✅ |
| fail-closed 语义 | ✅ classified errors 直接传播，不 fallback |
| `test_csrc_source_failure_taxonomy` 覆盖 | ✅ identity_mismatch/not_found/schema_drift/unavailable/transport |

### 4.4 Repository Boundary

| 检查项 | 结果 |
|--------|------|
| `FundNavRepository()` 默认 `CsrcEidNavSource()` | ✅ `nav_repository.py:88` |
| 无 fallback 到 Akshare/stock-sdk/Eastmoney | ✅ CSRC classified error 直接抛出 |
| constructor injection raw-unit 兼容 | ✅ `source_adapter: _NavSourceAdapter \| None = None` |
| `source_nav_type`/`source_adjustment_basis` 分支 | ✅ `nav_repository.py:162-196` |
| `_normalize_accumulated_nav_series` 不调用 `_normalize_raw_record` | ✅ 独立的 CSRC 函数 |
| `__init__.py` 不导出 CSRC EID 私有符号 | ✅ 只导出 `FundNavRepository` |

### 4.5 CSRC Accumulated Normalization

| 检查项 | 结果 |
|--------|------|
| 直接读 `估值日期`/`累计净值` | ✅ `_CSRC_DATE_COLUMN`/`_CSRC_ACCUMULATED_NAV_COLUMN` |
| `单位净值` 只 diagnostics | ✅ `_validate_csrc_unit_nav_diagnostics` 存入 `raw_payload`，不作为 `nav_value` |
| 空累计/空单位净值/重复日期/日期窗口/minimum_records | ✅ tests 覆盖全部路径 |
| blank accumulated outside window → dropped | ✅ `test_repository_csrc_blank_accumulated_before_window_is_dropped` |
| blank accumulated inside window → `missing_date_range` | ✅ `test_repository_csrc_blank_accumulated_inside_window_raises_missing_date_range` |
| all blank → `adjustment_basis_unknown` | ✅ `test_repository_csrc_all_blank_accumulated_raises_adjustment_basis_unknown` |
| 非正累计 → `integrity_error` | ✅ `nav_repository.py:475-481` |
| 非数值累计 → `schema_drift` | ✅ `_parse_decimal` |

### 4.6 strong_drawdown_evidence_eligible

| 检查项 | 结果 |
|--------|------|
| CSRC accumulated verified → `True` | ✅ `nav_repository.py:402` |
| 只 source-level，不构成 metric evidence | ✅ plan/evidence/test 均明确说明 |
| raw-unit → `False` | ✅ `nav_repository.py:294`；test 覆盖 |
| requested_code_only → `False` | ✅ `nav_models.py:564-568`；test 覆盖 |
| 未改 extractor/score/snapshot/quality/golden | ✅ diff 只涉及 data 层和 docs |

### 4.7 Contract / DTO

| 检查项 | 结果 |
|--------|------|
| `_RawNavSourceResult` 显式字段，无 extra_payload/kwargs | ✅ |
| `_NavSourceAdapter` Protocol 显式签名 | ✅ `load_raw_nav_source(fund_code, *, share_class, start_date, end_date, force_refresh)` |
| `NavSourceMetadata.source_query_params` 规范化为 tuple | ✅ `nav_models.py:154-158` |
| `source_nav_type`/`source_adjustment_basis` 是 required fields | ✅ 非 Optional |
| `FundNavDataAdapter.load_raw_nav_source` Protocol-compatible | ✅ `nav_data.py:282-357` |

### 4.8 stock-sdk Rejection

| 检查项 | 结果 |
|--------|------|
| 无 Node/npm/subprocess dependency | ✅ `test_no_stock_sdk_runtime_dependency` |
| date-shift → `integrity_error` | ✅ `test_stock_sdk_date_shift_classified_as_integrity_error` |
| dividend-list-only 不能构造 NAV series | ✅ `test_dividend_list_cross_check_cannot_construct_fund_nav_series` |

### 4.9 Docs Correctness

| 检查项 | 结果 |
|--------|------|
| `docs/design.md` 只写当前事实 | ✅ diff 准确描述 CSRC EID default path 和 legacy 兼容 |
| `fund_agent/fund/README.md` 当前行为 | ✅ 准确描述 source adapter、份额分离、provenance |
| `tests/README.md` fixture/smoke 说明 | ✅ 新增 CSRC EID 测试描述和 smoke 说明 |
| 不宣称 drawdown metric 或 permanent primary source | ✅ 明确标注 "只表示 source-level eligibility" |
| 不宣称 `drawdown_stress` blocker解除 | ✅ 明确标注 "未解除" |

### 4.10 Scope Compliance

| 检查项 | 结果 |
|--------|------|
| 只修改允许范围内的文件 | ✅ |
| 未修改 forbidden files（extractors/score/snapshot/quality/golden/services/ui/host） | ✅ |
| 未修改 reports artifacts | ✅ |
| 新文件在允许范围内 | ✅ `nav_source_contract.py`、`csrc_eid_nav_source.py`、`test_csrc_eid_nav_source.py` |

## 5. Test Coverage Summary

| 区域 | 测试数 | 覆盖情况 |
|------|--------|----------|
| CSRC source adapter | 10 | A success、A/C/E/F mapping、identity conflict、failure taxonomy、pagination boundary/edge、blank rows、protocol signature |
| stock-sdk rejection | 3 | no runtime dependency、date-shift、dividend-list-only |
| Repository accumulated | 9 | CSRC normalization、share-class separation、identity mismatch、blank accumulated 3 paths、malformed values 6 params、source eligibility |
| Repository raw-unit | 15 | raw fixture、explicit params、requested_code_only、identity mismatch、schema drift、date/growth/nav validation、duplicate date、date range、minimum records、unavailable、empty records、signature |
| NavData adapter | 3 | cache、force refresh、raw source metadata |
| Model contract | 13 | success path、failure category、query params、drawdown eligibility 2x、type/basis combos、empty/duplicate records、share class mismatch、identity mismatch、adjusted basis unknown、nav type unknown、record count mismatch、constraints、raw_payload diagnostics |
| **合计** | **64 passed** | |

## 6. Validation Evidence

Evidence artifact 声明的验证结果：

- `ruff check .` → All checks passed
- `pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` → 925 passed, 92.37% coverage
- Real CSRC EID smoke → A/C/E/F 全部 `accumulated_nav/accumulated_nav/verified/True`
- `drawdown_stress blocker remains unresolved` → evidence artifact 明确声明

## 7. Residual Risks

1. `force_refresh` 出现在 CSRC EID `source_query_params` 中（见 §3.1），语义略有偏差但不影响功能。
2. `_parse_share_class_from_text` 正则依赖 CSRC EID detail 页特定 HTML 格式（见 §3.2），fail-closed 行为正确。
3. `_EXPECTED_SHARE_CLASSES` 硬编码 006597 家族（见 §3.3），当前 gate 范围内合理。
4. `drawdown_stress` blocker 仍未解除——本 gate 只实现 source-level eligibility，后续需要 reviewed drawdown metric gate。
