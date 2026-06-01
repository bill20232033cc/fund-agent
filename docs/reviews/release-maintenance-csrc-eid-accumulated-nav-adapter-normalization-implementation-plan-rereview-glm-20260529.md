# CSRC EID Accumulated NAV Adapter Normalization — Plan Re-Review (GLM)

日期：2026-05-29
角色：plan re-review worker（GLM），非 controller，非 implementation worker。
Work unit：`CSRC EID accumulated NAV adapter normalization implementation gate`
Review targets：更新后 plan + plan-fix artifact。

## Verdict

**accepted**

所有 MiMo F1-F10 和 GLM R1-R2/N1-N4 均在更新后 plan 中得到充分关闭。Plan 已达到 code-generation-ready 状态。Implementation worker 无需自行选择架构。无遗留 required fix。

---

## Finding Disposition — MiMo Review

| MiMo Finding | Severity | Status | Verification |
|---|---|---|---|
| F1 Repository Source Selection 未定义 | Required | **Closed** | §4.0 定义 `_NavSourceAdapter` Protocol（含完整签名 + 返回类型）；§4.9 明确默认 `CsrcEidNavSource()`；§5 构造函数类型 `_NavSourceAdapter \| None = None`；Slice 3 补充默认构造 + constructor injection。三层闭合。 |
| F2 `_RawNavSourceResult` 与 CSRC DTO 不兼容 | Required | **Closed** | §4.0 新增 `nav_source_contract.py` 统一 DTO，含 `source_nav_type/source_adjustment_basis` required fields；§5 指定 `nav_data.py` 移除或导入该 DTO；Slice 3 明确 `_normalize_accumulated_nav_series(...)` 直接读 `估值日期/累计净值`，不走 Akshare `_normalize_raw_record(...)`。DTO 类型和 normalization 路径均已收敛。 |
| F3 `strong_drawdown_evidence_eligible` 语义冲突 | Required | **Closed (Option A)** | §2 Goal 补充 source-level eligibility 说明；§4.4 明确采用 Option A 并给出完整语义解释；§7 Test Matrix 新增 "CSRC source eligibility" 行；§8 Smoke 输出 `strong_drawdown_evidence_eligible`；§9 Review Focus 新增验证点；§10 Working assumptions 补充假设；Slice 3 tests 显式断言 `True` 并要求 evidence 声明 no metric/no blocker。六处闭合，语义清晰。 |
| F4 Sync/async 和 HTTP client 未对齐 | Required | **Closed** | §4.10 明确 `async` + `httpx.AsyncClient`；§4.0 Protocol 签名是 `async def`；Slice 2 明确 `httpx>=0.28.0` 已有依赖。三层一致。 |
| F5 HTML 解析依赖未声明 | Minor | **Closed** | §4.10 + Slice 2 明确 `stdlib html.parser.HTMLParser`，禁止 BeautifulSoup/lxml。 |
| F6 HTTP 超时/重试未定义 | Minor | **Closed** | §4.10 定义 `httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)` + 最多 3 次尝试 + 重试条件（timeout/transport/5xx）；Slice 2 同步。 |
| F7 Pagination 场景覆盖不足 | Minor | **Closed** | Slice 2 新增 total 0 → `not_found`、total changes → `integrity_error`、last-page boundary mismatch；§7 Test Matrix 同步。 |
| F8 `strong_drawdown_evidence_eligible` 测试缺失 | Minor | **Closed** | §7 "CSRC source eligibility" 行 + Slice 3 tests 显式断言 `True` 与 no metric 声明。 |
| F9 stock-sdk rejection test 模糊 | Minor | **Closed** | Slice 4 改为三个具体测试：`test_no_stock_sdk_runtime_dependency`、`test_stock_sdk_date_shift_classified_as_integrity_error`（含具体 fixture 值 `2023-01-12` vs `2023-01-11`）、`test_dividend_list_cross_check_cannot_construct_fund_nav_series`。 |
| F10 docs/design.md 措辞风险 | Minor | **Closed** | Slice 5 明确只写当前代码事实，禁止 "permanent primary source" 等永久决策措辞，controller judgment 负责策略决策回写。 |

---

## Finding Disposition — GLM Review

| GLM Finding | Severity | Status | Verification |
|---|---|---|---|
| R1 Source adapter Protocol 未定义 | Required | **Closed** | 与 MiMo F1 同源；§4.0 新增 Protocol + DTO + file location + implementation requirements。 |
| R2 Repository source selection 未明确 | Required | **Closed** | 与 MiMo F1 同源；§4.9 明确默认 CSRC EID、no fallback、constructor injection、no source_options。 |
| N1 `source_nav_type/source_adjustment_basis` deferred | Non-blocking | **Closed** | §4.0 明确为 required fields，repository 按显式 pair 选择 normalization branch，不再是 deferred choice。 |
| N2 HTTP/HTML parser 未指定 | Non-blocking | **Closed** | §4.10 明确 `httpx.AsyncClient` + `html.parser.HTMLParser`。 |
| N3 A/C blank accumulated 日期未枚举 | Non-blocking | **Closed** | Slice 2 + §7 明确 fixture rows `2018-12-07` 和 `2018-12-14`。 |
| N4 `单位净值` blank 处理语义 | Non-blocking | **Closed** | Slice 3 明确处理顺序：先处理 blank `累计净值`；`累计净值` 有值但 `单位净值` blank/non-numeric → `schema_drift`，nonpositive → `integrity_error`。§7 "Unit NAV diagnostics" 行同步。 |

---

## Cross-Review 一致性检查

MiMo F1 与 GLM R1/R2 重叠（均指向 repository source selection + Protocol），plan-fix 通过 §4.0 + §4.9 统一解决，两份 review 的 fix 需求已合并收敛。无遗漏。

MiMo F3 与 GLM N1 部分重叠（strong_drawdown 语义），plan-fix 通过 Option A + source_nav_type required field 分别解决。无遗漏。

---

## 新增内容一致性验证

Plan-fix 引入了 §4.0（Protocol/DTO）、§4.9（source selection）、§4.10（HTTP/parser），以下验证三节之间的内部一致性：

| 检查项 | 结果 |
|---|---|
| §4.0 Protocol 签名与 Slice 2 CsrcEidNavSource 签名一致 | ✅ 两者均为 `async load_raw_nav_source(fund_code, *, share_class, start_date, end_date, force_refresh) -> _RawNavSourceResult` |
| §4.0 DTO `source_nav_type/source_adjustment_basis` 与 §4.0 branching logic 一致 | ✅ Repository 按 `("unit_nav","raw_unit_nav")` / `("accumulated_nav","accumulated_nav")` 分支 |
| §4.9 no fallback 与 §4.6 failure taxonomy 一致 | ✅ §4.9 显式声明不 fallback 到 Akshare/stock-sdk/Eastmoney，§4.6 的 `unavailable` 可由 future strategy fallback 但本 gate 默认抛出 |
| §4.10 httpx + async 与 §4.0 Protocol async 签名一致 | ✅ |
| §4.10 timeout/retry 与 Slice 2 实现要求一致 | ✅ |
| §4.10 html.parser 与 Slice 2 parser 描述一致 | ✅ |
| §5 nav_data.py DTO 迁移与 §4.0 DTO 定义一致 | ✅ §5 指定 "移除或导入使用 nav_source_contract.py 的 _RawNavSourceResult" |
| Slice 3 `_normalize_accumulated_nav_series` 与 §4.2 字段映射一致 | ✅ 均指定直接读 `估值日期/累计净值` |

无内部矛盾。

---

## Residual Risks（accepted 后保留）

| Risk | Owner | 说明 |
|---|---|---|
| CSRC EID endpoint schema 在实现期变化 | implementation worker + controller | Slice 2 stop condition 已覆盖；fixture tests 不依赖网络 |
| `_RawNavSourceResult` 从 `nav_data.py` 迁移到 `nav_source_contract.py` 时可能影响 `nav_data.py` 内部引用 | implementation worker | §5 已明确迁移方向，不阻塞 |
| `FundNavDataAdapter.load_raw_nav_source()` 签名变更需同时更新 `_FakeRawNavAdapter` test helper | implementation worker | Slice 1 已要求 Protocol-compatible fake adapter |
| `strong_drawdown_evidence_eligible=True` 可能被 future consumer 误解为 blocker 已解除 | controller judgment + future gate | Plan 已在 6 处显式声明 source-level only；controller judgment 应在 accepted 语句中重申 |

---

## 结论

Plan fix 质量高，所有 required fixes 均已充分关闭：

- **Protocol/DTO**：§4.0 完整定义 `_NavSourceAdapter` Protocol 和 `_RawNavSourceResult` DTO，含 required `source_nav_type/source_adjustment_basis`，file location 明确。
- **Repository default source/no fallback**：§4.9 明确默认 `CsrcEidNavSource()`、无任何 fallback、constructor injection 保留 raw-unit 兼容。
- **CSRC DTO normalization path**：Slice 3 明确 `_normalize_accumulated_nav_series` 直接读 CSRC 字段，不走 Akshare `_normalize_raw_record`。
- **strong_drawdown_evidence_eligible 语义**：Option A 在 6 处闭合，source-level eligibility only。
- **async/http/parser**：§4.10 明确 `httpx.AsyncClient` + `html.parser.HTMLParser` + timeout/retry。
- **Pagination/A-C blank/unit-nav/stock-sdk tests**：§7 + Slice 2/3/4 补齐具体场景和 fixture。
- **docs wording**：Slice 5 限制为当前代码事实，不写永久决策。

Implementation worker 可按 Slice 1-5 直接实现，无需自行选架构。

建议 controller 接受 plan，派 implementation worker 开始实现。
