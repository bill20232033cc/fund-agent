# CSRC EID and stock-sdk NAV Source Evaluation Gate — Evidence Review (GLM)

日期：2026-05-28

角色：AgentGLM evidence review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Evidence artifact：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md`

## Verdict

**Accepted with non-blocking findings.**

Evidence 整体执行质量高，严格遵循 accepted plan 的 E1-E4 结构。CSRC EID 被充分证明为官方可机读 primary `accumulated_nav` source candidate。stock-sdk 被正确降级为 `evidence-only`。所有 failure category、cross-source reconciliation 和 non-goals 均得到正确处理。以下 findings 不阻断 controller judgment。

## Step Self-Check

- Current gate / role：本 artifact 只产出 evidence review prose；不启动 gateflow，不 implement、commit、push、PR、merge、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、前序 NAV source identity controller judgment / evidence、accepted plan（含 DS/GLM plan re-review）、`nav_models.py`、`nav_repository.py`、`nav_data.py` 以及被审 evidence artifact。
- Scope boundary：只新增本 review artifact；不改 evidence、production code/tests、score、snapshot、quality gate、golden fixture、drawdown metric、Host/Agent/dayu、年报来源实现或 README。

## Findings

### F1 — Severity: Medium — stock-sdk 行数差异（1809 vs 1810）未显式解释

**Evidence 行号**：E2 `getFundNavHistory` Smoke 表格（evidence 第 263-268 行）与 E4 stock-sdk matrix（evidence 第 383-387 行）

CSRC EID A/C 记录 1809 行，stock-sdk A/C 记录 1810 行。差一行未显式解释。

**Assessment**：差一行最可能由 stock-sdk 日期偏移引起——stock-sdk 将 Eastmoney 本地时间戳转换为 UTC 后，首行日期从 `2018-12-03`（Akshare/CSRC EID）偏移为 `2018-12-02`（stock-sdk），多出一个 UTC 日历日行。Evidence 已在第 272-275 行解释了日期偏移的根因（`new Date(timestamp).toISOString().slice(0,10)`），但未显式将行数差归因于此。

这不构成阻断，因为行数差已被 `integrity_error` classification 覆盖。但 future adapter 如果需要逐行对齐，需要理解这个差一行的根因。

**Disposition**：Non-blocking。Evidence 的 `integrity_error` classification 已充分表达此风险。

### F2 — Severity: Low — A/C earliest blank accumulated NAV 的精确日期集合未完整列举

**Evidence 行号**：E1 "A/C earliest-row caveat"（evidence 第 177-182 行）

Evidence 提到 A 的 2018-12-14 和 2018-12-07 行有 blank accumulated NAV，C 同理，并说从 2018-12-18 起 accumulated NAV 有值。但未列举 2018-12-07 到 2018-12-18 之间是否还有其他 blank 行（如 2018-12-10、2018-12-12 等是否也有 blank）。

**Assessment**：对于 evidence gate 的粒度，这不构成阻断。Evidence 已明确标记了 caveat 存在，并正确指出 future adapter 需要对请求包含 blank 行的窗口 fail-closed（`missing_date_range` 或 `schema_drift` / `integrity_error`）。Future implementation gate 应在 adapter 中精确处理空白行的边界条件。

**Disposition**：Non-blocking。

### F3 — Severity: Low — stock-sdk `dividendPerShare` 精度为 `0.008` 而非 `0.0080`

**Evidence 行号**：E2 `getFundDividendList` Smoke（evidence 第 306 行）

stock-sdk 返回 `dividendPerShare: 0.008`，而年报 §3.3 为每 10 份 `0.080`（即每份 `0.0080`），前序 evidence 使用 `0.0080` 作为标准值。

**Assessment**：`0.008` 和 `0.0080` 在数值上等价（JavaScript `0.008 === 0.0080`），但 Decimal 精度表示不同。NAV typed contract 使用 `Decimal` 类型（`nav_models.py`），后续 implementation gate 需确保 Decimal 构造时不受浮点表示丢失尾部零的影响。这属于 implementation detail，不构成 evidence 阻断。

**Disposition**：Non-blocking。Implementation gate 应注意 stock-sdk JSON 数值的 Decimal 转换。

### F4 — Severity: Info — CSRC EID `retrieved_at` 同一时间戳用于所有四个份额类别

**Evidence 行号**：E4 CSRC EID matrix（evidence 第 367-370 行）

所有四个代码的 `retrieved_at` 均为 `2026-05-28T15:45:54Z`。

**Assessment**：这是 evidence worker 执行 smoke 时的单次 session 时间戳，不是每个份额类别的独立检索时间。对于 evidence gate 这是可接受的。Future adapter implementation 应为每个 HTTP 请求记录独立的 `retrieved_at`。

**Disposition**：Info only。

## Cross-Check Against Review Focus

### Does CSRC EID evidence meet accepted plan proof standard for official primary accumulated_nav source candidate?

**Yes.** Evidence 满足了 accepted plan E1 的全部 7 个 steps（含 planning fix 新增的 step 0）：

1. **E1-0 Public search**：通过 `/fund/disclose/validate_fund.do` POST 用基金名称和 A/C/E 份额代码正向搜索，均返回 `fundId: 5755`。F 搜索缺失但 detail page 包含 F。✅
2. **E1-1 Machine-readable endpoints**：detail page 是可解析 HTML，classification 历史页面有稳定分页 `limit/start`。✅
3. **E1-2 Identity verification**：内部 ID 5755 通过公开搜索正向验证。Detail page 标题含 `006597`，classification rows 含 A/C/E/F 份额代码和名称。CSRC EID 使用 product fundCode `006597` + classification 参数实现份额级粒度。✅
4. **E1-3 Field check**：列名包含 `估值日期`、`单位净值`、`累计净值`。Evidence 记录了样例行。✅
5. **E1-4 Full-history coverage**：A/C 1809 行（2018-12-07 起），E 994 行（2022-04-25 起），F 398 行。分页机制稳定（`共50页`、`共994条`）。✅
6. **E1-5 Semantics**：E 类 2023-01-11 `accumulated_nav - unit_nav` 从 0.0000 变为 0.0080，与年报 §3.3 每 10 份 0.080 完全一致。✅
7. **E1-6 Failure classification**：覆盖 `not_found`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`。✅

CSRC EID 是 `csrc.gov.cn` 官方域名，提供可复现 HTTP GET/POST 端点、机器可解析 HTML、稳定分页、份额级粒度和经过 cross-check 的 `accumulated_nav` 语义。`accepted-primary-candidate` 判定合理。

### Does evidence correctly distinguish CSRC internal ID 5755, product-level fund code 006597, and A/C/E/F classification rows?

**Yes.** Evidence 清晰区分了三个层次：

- **EID internal ID `5755`**：通过 `/fund/disclose/validate_fund.do` 搜索返回，不是公开份额代码（evidence 第 119 行证明 `5755` 直接搜索返回 `isSuccess: false`）。✅
- **Product-level fund code `006597`**：Detail page 标题为 `国泰利享中短债债券(006597)`；classification URL 使用 `fundCode=006597`。✅
- **Share-class classification**：A `2030-1010`，C `2030-1020`，E `2030-1040`，F `2030-1050`。每类有独立分页和行计数。✅

### Are record counts/date ranges/unit_nav/accumulated_nav/source metadata sufficient?

**Yes.** E4 disposition matrix（evidence 第 365-387 行）完整记录了全部字段。Caveats（A/C earliest blank rows、F search-index gap、F pre-inception `missing_date_range`）均有显式标注。Source metadata（`source_name`、`source_url/provider`、`retrieved_at`、`identity_status`、`failure_category`）对齐 `nav_models.py` 的 `NavSourceMetadata` 结构。

### Is stock-sdk correctly downgraded to evidence-only?

**Yes.** 降级理由充分且分层清晰：

1. **Provider lineage**：源码直接调用 `fund.eastmoney.com/pingzhongdata/{code}.js` 并解析 `Data_ACWorthTrend`。stock-sdk 不是独立来源，而是 Eastmoney 的 JavaScript client wrapper。✅
2. **Date normalization integrity_error**：`new Date(timestamp).toISOString().slice(0,10)` 将本地时间戳转为 UTC，导致日期偏移一天。E 类 2023-01-11 事件在 stock-sdk 中被标为 `2023-01-12` 的值。`date` 是 typed NAV record 的必要键，偏移构成 `integrity_error`。✅
3. **Decision 为 `evidence-only` 而非 `secondary-only`**：即使忽略 integrity_error，stock-sdk 也不提高 provenance 等级。加上 integrity_error，连 secondary typed source 都不适合。`evidence-only` 是 plan E4 选项中最严格的非 reject/block 判定。✅

### Are getFundDividendList results properly treated as cross-check?

**Yes.** Evidence 第 310-315 行明确说明：

- stock-sdk dividend list 与年报 §3.3 每 10 份 0.080 匹配。✅
- 与 accepted Eastmoney 事件日期 2023-01-11 匹配。✅
- "NAV-history event-level date alignment remains unsafe as runtime typed evidence"——dividend list 只作为冗余 cross-check，不能弥补 NAV history 的 date integrity 问题。✅

Evidence 正确将 `getFundDividendList` 定位为"有用但不改变 stock-sdk 整体 disposition 的 cross-check"。

### Are failure categories and not_applicable treatment correct?

**Yes.**

- CSRC EID：`null`（无 failure）for complete windows；earliest blank rows 标注为 future adapter fail-closed。✅
- CSRC EID F 类：`null` for source-inception-forward；`missing_date_range` for pre-inception。✅
- stock-sdk：`integrity_error` for all four codes（date shift）。✅
- E3 reconciliation：stock-sdk 标为"values inspected; not accepted as typed series"——这是因为 stock-sdk 有 NAV rows 且 identity verified，但 date 有 integrity_error，所以不是 `not_applicable` 而是带 `integrity_error` 的 inspected source。这与 plan 的 execution dependency 规则一致（stock-sdk 满足"至少返回一条 NAV row 且 identity_status 非 unknown"的条件，所以进入 reconciliation，但 reconciliation 结果是不接受为 typed series）。✅

### Does evidence preserve no runtime dependency, no code/test changes, no drawdown blocker解除?

**Yes.** Non-Goals Preserved（evidence 第 405-411 行）和 Completion Report（evidence 第 437-456 行）均明确声明：

- No production code/tests modified. ✅
- No project dependency files modified（stock-sdk 使用 `/tmp` 临时解压）. ✅
- No adapter, drawdown metric, score, snapshot, quality gate, golden, PR, push, merge, release changes. ✅
- `drawdown_stress` blocker 未解除. ✅
- Annual report 只通过 `FundDocumentRepository`. ✅
- Accepted basis 只有 `accumulated_nav`，不是 `dividend_adjusted_nav` 或 `total_return`. ✅

## Alignment With Prior Accepted Evidence

Evidence 正确引用和扩展了前序 NAV source identity gate 的 accepted facts：

1. **Eastmoney/Akshare `Data_ACWorthTrend` 已接受为 `accumulated_nav` candidate**：Evidence 在 E3 reconciliation 中将 CSRC EID 与 prior Eastmoney/Akshare evidence 对齐（evidence 第 341-347 行）。CSRC EID row counts 和 latest values 与 prior evidence 一致。✅

2. **E 类 2023 分红事件**：CSRC EID E-class 2023-01-11 `accumulated - unit = 0.0080` 与 prior evidence 完全一致。年报 §3.3 每 10 份 0.080 通过 `FundDocumentRepository` 再次验证。✅

3. **F 类 `missing_date_range`**：Prior evidence 已接受 F 仅限 source-inception-forward windows。CSRC EID evidence 保持了这一限制（398 行，inferred from total rows）。✅

4. **`LJSYLZS` / `累计收益率走势` 仍为 `adjustment_basis_unknown`**：本 gate 未重新评估此 source，正确保持 prior judgment。✅

## New Information Evaluation

CSRC EID 带来的新信息：

1. **CSRC EID 作为 official primary source**：这是全新信息。前序 gate 只评估了 Eastmoney/Akshare。CSRC EID 来自 `eid.csrc.gov.cn`（证监会官方域名），provenance 等级高于第三方 Eastmoney。如果 controller 接受，future adapter 的 source 优先级应考虑 CSRC EID > Eastmoney/Akshare。

2. **CSRC EID 份额级粒度**：通过 `classification` 参数实现 A/C/E/F 分离。这是前序 gate 未发现的新信息。

3. **A/C earliest blank accumulated NAV rows**：前序 Akshare evidence 未报告此问题。CSRC EID 的 A/C 前两行（2018-12-07 和 2018-12-14）有 blank accumulated NAV。这是一个新发现的 caveat。

4. **stock-sdk date normalization bug**：虽然前序 gate 未评估 stock-sdk，但此发现对理解 Eastmoney JS timestamp 的 UTC 转换有独立价值——future adapter 如果直接使用 Eastmoney JS 数据，也需要注意 timestamp 时区处理。

## Required Fixes

None. All findings are non-blocking.

## Residual Risks

1. **CSRC EID F 类 direct search gap**：F 类 `022176` 无法通过 CSRC EID 公开搜索直接定位，只能通过 detail page 的 classification 链接发现。Future adapter 需要硬编码或通过其他方式获取 F 类的 classification ID。若 CSRC EID 修改 classification 编码体系，adapter 可能需要更新。

2. **CSRC EID A/C earliest blank rows**：前两行（2018-12-07, 2018-12-14）accumulated NAV 为空白。Future adapter 必须对包含空白行的请求窗口 fail-closed。这可能影响需要完整 inception-to-date 历史的窗口。

3. **CSRC EID HTML 解析稳定性**：Evidence 证明当前 HTML schema 可解析，但 CSRC EID 未提供版本化 API 或 schema 契约。HTML schema 变更可能触发 `schema_drift`。Future adapter 需要足够 defensive 的解析逻辑。

4. **stock-sdk date bug 的可修复性**：stock-sdk 的日期偏移根因已明确定位（UTC 转换）。如果 stock-sdk 修复此 bug 或 future wrapper 正确处理时区，stock-sdk 可能从 `evidence-only` 升级为 `secondary-only`。但这需要新的 implementation gate 验证。

5. **CSRC EID 分页可靠性**：Evidence 验证了分页参数（`limit/start`），但未测试极端分页场景（如并发请求、大数据量分页完整性）。Future adapter implementation gate 应验证分页完整性。

6. **CSRC EID 更新频率**：Evidence 记录了 2026-05-28 的最新值，但未评估 CSRC EID 净值数据的更新频率和延迟。这属于 runtime feasibility，不影响 source identity / semantics acceptance。

## Explicit Controller Proceed Statement

**Controller may accept this evidence and move to controller judgment.**

Evidence execution 满足 accepted plan 全部要求。CSRC EID `accepted-primary-candidate` 和 stock-sdk `evidence-only` 判定均有充分 evidence 支持。Controller 可基于此 evidence artifact 发出 judgment，决定 CSRC EID 是否进入 future adapter normalization implementation gate 作为 primary source candidate。

## Non-Goals Preserved

- No evidence/plan/code/tests modified by this review.
- No score, snapshot, quality gate, golden fixture, drawdown metric, Host/Agent/dayu, release, PR, push, merge, or promotion change occurred.
- No extractor direct source dependency was introduced.
- No runtime dependency was added.
