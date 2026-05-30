# CSRC EID Accumulated NAV Adapter Normalization — Plan Re-Review (MiMo)

日期：2026-05-29
角色：plan re-review worker（非 controller，非 implementation worker）
Re-review target：
- Updated plan: `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`
- Plan fix: `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-fix-20260529.md`
- Original reviews:
  - `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-mimo-20260529.md`
  - `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-glm-20260529.md`

## Verdict

**accepted**

所有 MiMo F1-F10 和 GLM R1-R2/N1-N4 均已充分关闭。Updated plan 已达到 code-generation-ready 状态，implementation worker 可按 Slice 1-5 无需自行做架构决策。

## Finding Disposition Table

### MiMo Original Findings

| Finding | Severity | Disposition | Verification |
|---|---|---|---|
| **F1** Repository Source Selection Mechanism 未定义 | blocking | **Closed** | §4.0 定义 `_NavSourceAdapter` Protocol，含完整 `load_raw_nav_source` 签名（`fund_code, *, share_class, start_date, end_date, force_refresh`）。§4.9 明确 `FundNavRepository()` 无参构造默认创建 `CsrcEidNavSource()`，CSRC classified failure 不 fallback，测试通过 constructor injection 覆盖。§5 指定 `FundNavRepository.__init__(source_adapter: _NavSourceAdapter \| None = None)`。架构选择已完全收敛。 |
| **F2** `_RawNavSourceResult` 与 CSRC EID DTO 类型不兼容 | blocking | **Closed** | §4.0 新增 `nav_source_contract.py` 定义统一 DTO，含 `source_nav_type: NavType` 和 `source_adjustment_basis: AdjustmentBasis` 为 required fields。Slice 3 明确 `_normalize_accumulated_nav_series(...)` 直接读取 CSRC 字段 `估值日期` / `累计净值`，不经过 Akshare `_normalize_raw_record(...)`。§5 指定 `nav_data.py` 移除或导入使用新 contract DTO。Normalization 路径已完全明确。 |
| **F3** `strong_drawdown_evidence_eligible` 状态语义冲突 | blocking | **Closed (Option A)** | §2 Goal 尾段明确 "source-level eligibility flag...不产生 drawdown metric，不构成 drawdown_stress evidence acceptance，也不解除 blocker"。§4.4 采用 Option A，明确 accumulated verified series 可为 `True`。§7 test matrix 增加 "CSRC source eligibility" 行。Slice 3 tests 要求断言 `True` 并附 evidence text。§10 working assumptions 重申 "source-level contract result only"。语义冲突已消除，且不需要修改 `FundNavSeries` 模型。 |
| **F4** Sync/async 和 HTTP client 选择未对齐 | blocking | **Closed** | §4.10 明确 `CsrcEidNavSource.load_raw_nav_source()` 是 async 方法，使用 `httpx.AsyncClient`（项目既有依赖）。Slice 2 指定 `httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)` 和最多 3 次尝试。`FundNavRepository.load_nav_series()` 的 `await` 调用链完整。 |
| **F5** HTML 解析依赖未声明 | non-blocking | **Closed** | §4.10 和 Slice 2 明确使用 stdlib `html.parser.HTMLParser`，禁止新增 BeautifulSoup/lxml。允许少量正则仅用于分页数字提取。 |
| **F6** HTTP 超时/重试策略未定义 | non-blocking | **Closed** | §4.10 和 Slice 2 指定 timeout policy（connect=10s, read=30s, write=10s, pool=10s）和 retry policy（最多 3 次，仅 timeout/transport/5xx 可重试，最终 `unavailable`）。HTTP 4xx 视具体 endpoint 归类。 |
| **F7** Pagination Error Handling 缺少具体场景覆盖 | non-blocking | **Closed** | Slice 2 增加 `total=0 -> not_found`、`total changes mid-fetch -> integrity_error`、`last page boundary mismatch -> integrity_error`。§7 test matrix 增加对应行。 |
| **F8** `strong_drawdown_evidence_eligible` 测试缺失 | non-blocking | **Closed** | §7 增加 "CSRC source eligibility" 行。Slice 3 tests 增加断言 `strong_drawdown_evidence_eligible is True` 并附 evidence text "no metric evidence/score acceptance"。 |
| **F9** stock-sdk Rejection Test 方式模糊 | non-blocking | **Closed** | Slice 4 改为三个具体测试：`test_no_stock_sdk_runtime_dependency`、`test_stock_sdk_date_shift_classified_as_integrity_error`、`test_dividend_list_cross_check_cannot_construct_fund_nav_series`。"may be" 模糊措辞已消除。 |
| **F10** docs/design.md 更新范围需对齐真源规范 | non-blocking | **Closed** | Slice 5 明确 "update only current code facts"，禁止写 "permanent primary/source-strategy" 决策措辞，由 controller judgment 负责。 |

### GLM Original Findings

| Finding | Severity | Disposition | Verification |
|---|---|---|---|
| **R1** Source adapter Protocol / type contract 未定义 | required | **Closed** | §4.0 定义完整 `_NavSourceAdapter` Protocol、`_RawNavSourceResult` DTO、file location (`nav_source_contract.py`)、repository constructor type (`_NavSourceAdapter \| None`)。 |
| **R2** Repository source selection mechanism 未明确 | required | **Closed** | §4.9 明确 default CSRC、no fallback、constructor injection for fake/raw adapter、no `source_options`。 |
| **N1** `source_nav_type` / `source_adjustment_basis` 为 deferred choice | non-blocking | **Closed** | §4.0 选择 required fields，repository 按 `(source_nav_type, source_adjustment_basis)` 分支。不再 deferred。 |
| **N2** HTTP client 和 HTML parser 选择未指定 | non-blocking | **Closed** | §4.10 选择 `httpx.AsyncClient` + stdlib `html.parser`。 |
| **N3** A/C blank accumulated NAV 日期集合未完全枚举 | non-blocking | **Closed** | Slice 2 和 §7 增加 A/C exact blank fixture rows `2018-12-07` 和 `2018-12-14`。 |
| **N4** `单位净值` blank 处理语义需明确 | non-blocking | **Closed** | Slice 3 明确先处理 blank `累计净值`；若 `累计净值` 有值但 `单位净值` blank/non-numeric -> `schema_drift`，nonpositive -> `integrity_error`。 |

## Updated Plan Quality Assessment

### Code-Generation-Readiness

| Criterion | Assessment |
|---|---|
| Implementation worker 无需自行选架构 | **Pass** — Protocol/DTO/source selection/HTTP/parser/async 均已收敛 |
| Slice 边界清晰、可独立实现 | **Pass** — Slice 1-5 依赖链明确，每 slice 有独立 completion signal |
| Stop conditions 覆盖未知风险 | **Pass** — 每 slice 有具体 stop condition |
| Test matrix 覆盖所有 failure category | **Pass** — 8 类 taxonomy + pagination edge cases + unit NAV + stock-sdk + eligibility |
| No ambiguous "may be" / "if needed" | **Pass** — 原 F9 的 "may be" 已消除；`source_nav_type` 不再 deferred |

### Consistency Check

| Item | Updated plan | Consistent |
|---|---|---|
| §4.0 Protocol `share_class` param | `share_class: str \| None = None` | ✅ 与 `FundNavRepository.load_nav_series` 一致 |
| §4.0 DTO `source_nav_type` | `NavType` (not `str \| None`) | ✅ 类型安全 |
| §4.9 no fallback | "不 fallback 到 Akshare raw unit NAV、stock-sdk、Eastmoney 或任何 product-level mixed source" | ✅ 与 §4.6 failure taxonomy 一致 |
| §4.10 async | "`CsrcEidNavSource.load_raw_nav_source()` 是 async 方法" | ✅ 与 repository `await` 一致 |
| Slice 3 normalization path | "`_normalize_accumulated_nav_series(...)` 直接读取 CSRC-specific fields...不经过 `_normalize_raw_record(...)`" | ✅ 与 F2 fix 一致 |
| Slice 4 stock-sdk tests | 三个具体测试，无 "may be" | ✅ 与 F9 fix 一致 |
| Slice 5 docs wording | "update only current code facts...controller judgment owns source-strategy decision wording" | ✅ 与 F10 fix 一致 |
| §7 test matrix | 增加 CSRC eligibility、unit NAV diagnostics、pagination edge cases、A/C blank exact dates | ✅ 与 F7/F8/N3/N4 fixes 一致 |

## Residual Risks

无新增 residual risk。原 review 的 5 项 residual risks 仍然适用，且 plan 的 fail-closed 机制和 stop conditions 已充分覆盖：

1. **CSRC EID endpoint 稳定性** — Slice 2 stop condition 覆盖。
2. **A/C 最早 blank accumulated rows** — §4.6 missing accumulated handling + §7 exact fixtures 覆盖。
3. **F share search-index gap** — §4.3 identity_mismatch fail closed 覆盖。
4. **`source_query_params` tuple 可扩展性** — 当前场景足够，不影响本 gate。
5. **real smoke 网络依赖** — §8 minimum acceptance 要求 006597/A 或 controller-approved `unavailable` residual。

## Recommended Controller Action

Updated plan 已达到 code-generation-ready 状态。建议 controller：

1. 接受 updated plan + plan-fix 作为当前 gate 的 accepted plan artifacts。
2. 派 implementation worker 按 Slice 1-5 实现。
3. 实现后派至少两份独立 review，重点审查：source identity 双重验证、A/C/E/F 分离、provenance 显式字段、failure taxonomy fail-closed、`strong_drawdown_evidence_eligible` 语义文档化、no drawdown metric/no blocker 解除。
