# CSRC EID Accumulated NAV Adapter Normalization — Plan Fix

日期：2026-05-29  
角色：planning fix worker  
目标 plan：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`  
Review inputs：

- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-mimo-20260529.md`
- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-glm-20260529.md`

## Step Self-Check

- Current gate / role：我仍是 planning worker，只修 plan 与写 plan-fix artifact；不实现、不 review、不 commit、不 push、不 PR、不 merge、不 release、不做 golden promotion。
- Source of truth：已读取 MiMo/GLM plan review，按用户指定 accepted required fixes 处理。
- Scope boundary：仅更新 plan artifact，并新增本 plan-fix artifact；不碰 production code/tests/docs implementation。
- Stop conditions：未发现需要 controller 回答的 material unresolved option；所有 required fixes 均可在 plan 层收敛。
- Evidence and validation：本次不运行代码验证；完成信号是 plan 变为 code-generation-ready 并有 finding disposition table。

## Fix Summary

本次修订把原 plan 中留给 implementation worker 的架构选择全部收敛：

- 新增 `fund_agent/fund/data/nav_source_contract.py`，定义 `_NavSourceAdapter` Protocol 与 `_RawNavSourceResult` explicit DTO。
- 固定 `FundNavRepository()` 默认创建 `CsrcEidNavSource()`，CSRC EID classified failure 不 fallback。
- 固定 `_RawNavSourceResult.source_nav_type/source_adjustment_basis` 为 required fields，repository 以它们选择 raw-unit vs accumulated normalization branch。
- 明确 `_normalize_accumulated_nav_series(...)` 直接读取 CSRC 字段 `估值日期` / `累计净值`，不复用 Akshare `_normalize_raw_record(...)`。
- 采用 Option A：CSRC EID accumulated verified series 可 `strong_drawdown_evidence_eligible=True`，但这只是 source-level eligibility，不实现 metric、不解除 `drawdown_stress`。
- 固定 HTTP/parser：`httpx.AsyncClient`、明确 timeout/retry、stdlib `html.parser`。
- 补齐 pagination、A/C blank accumulated、unit NAV blank、stock-sdk date shift、CSRC source eligibility 的测试矩阵。
- 收紧 `docs/design.md` 更新措辞为当前代码事实，不写永久 source strategy 判断。

## Finding Disposition

| Reviewer | Finding | Disposition | Plan changes |
|---|---|---|---|
| MiMo | F1 Repository Source Selection Mechanism 未定义 | Fixed | 新增 §4.0 Protocol、§4.9 source selection；Slice 3 指定 `FundNavRepository.__init__(source_adapter: _NavSourceAdapter \| None = None)`，默认 `CsrcEidNavSource()`，测试用 constructor injection。 |
| MiMo | F2 `_RawNavSourceResult` 与 CSRC EID DTO 类型不兼容 | Fixed | 新增 `nav_source_contract.py` DTO；Slice 3 明确 `_normalize_accumulated_nav_series(...)` 直接读取 `估值日期` / `累计净值`，不走 Akshare `_normalize_raw_record(...)`。 |
| MiMo | F3 `strong_drawdown_evidence_eligible` 状态语义冲突 | Fixed via Option A | §2、§4.4、§7、§9、Working assumptions 均明确 CSRC accumulated verified series 可为 `True`，仅表示 source-level eligibility，不等于 metric evidence、score acceptance 或 blocker解除。 |
| MiMo | F4 Sync/async 和 HTTP client 选择未对齐 | Fixed | §4.10 和 Slice 2 明确 `CsrcEidNavSource.load_raw_nav_source()` 是 async，使用既有 `httpx.AsyncClient`。 |
| MiMo | F5 HTML 解析依赖未声明 | Fixed | §4.10 和 Slice 2 明确使用 stdlib `html.parser.HTMLParser`，不新增 BeautifulSoup/lxml。 |
| MiMo | F6 HTTP 超时/重试策略未定义 | Fixed | §4.10 和 Slice 2 明确 timeout 与最多 3 次尝试，timeout/transport/5xx 可重试，最终 `unavailable`。 |
| MiMo | F7 Pagination Error Handling 缺少具体场景覆盖 | Fixed | Slice 2 与 §7 增加 total 0、total changes、last-page boundary mismatch。 |
| MiMo | F8 `strong_drawdown_evidence_eligible` 测试缺失 | Fixed | §7 增加 CSRC source eligibility 测试；Slice 3 测试要求断言 `True` 并说明 no metric/no blocker解除。 |
| MiMo | F9 stock-sdk Rejection Test 方式模糊 | Fixed | Slice 4 改成三个具体测试：无 runtime dependency、date-shift `integrity_error`、dividend-list-only 不能构造 series。 |
| MiMo | F10 docs/design.md 更新范围需对齐真源规范 | Fixed | Slice 5 改为只写当前代码事实，禁止写永久 primary/source-strategy 决策，controller judgment 负责决策措辞。 |
| GLM | R1 Source adapter Protocol / type contract 未定义 | Fixed | 新增 §4.0，指定 file、DTO、Protocol、repository constructor type、adapter compatibility signature。 |
| GLM | R2 Repository source selection mechanism 未明确 | Fixed | 新增 §4.9；明确 default CSRC、no fallback、constructor injection for fake/raw adapter、no source_options。 |
| GLM | N1 `source_nav_type` / `source_adjustment_basis` 为 deferred choice | Fixed | 选择 required DTO fields；repository branch by explicit `(source_nav_type, source_adjustment_basis)`。 |
| GLM | N2 HTTP client 和 HTML parser 选择未指定 | Fixed | 选择 `httpx.AsyncClient` + stdlib `html.parser`；无新增依赖。 |
| GLM | N3 A/C blank accumulated NAV 日期集合未完全枚举 | Fixed | Slice 2 / §7 增加 A/C exact blank fixture rows `2018-12-07`、`2018-12-14`。 |
| GLM | N4 `单位净值` blank 处理语义需明确 | Fixed | Slice 3 明确先处理 blank `累计净值`；若 `累计净值` 有值但 `单位净值` blank/non-numeric -> `schema_drift`，nonpositive -> `integrity_error`。 |

## Updated Plan Sections

- §0 Step Self-Check：补充已读取 MiMo/GLM plan review。
- §2 Goal：补充 source-level eligibility 与 no metric/no blocker 区分。
- §4.0：新增 source adapter Protocol / DTO contract。
- §4.4：采用 Option A 解决 `strong_drawdown_evidence_eligible` 语义。
- §4.9：新增 repository source selection。
- §4.10：新增 HTTP/parser strategy。
- §5：新增/修改 allowed production files 与 constructor/Protocol 责任。
- §6 Slice 1-5：补齐 DTO、Protocol、httpx/parser、repository branch、stock-sdk tests、docs wording。
- §7 Test Matrix：补齐 pagination、A/C blank、unit NAV、stock-sdk、source eligibility 测试。
- §8 Smoke：输出 `strong_drawdown_evidence_eligible`。
- §9 Review Focus：补充 source-level eligibility review point。
- §10 Working assumptions：补充 default source 与 source eligibility assumption。

## Completion

Updated plan path：

`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`

Plan-fix artifact path：

`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-fix-20260529.md`

Blocking Questions For Controller：无。
