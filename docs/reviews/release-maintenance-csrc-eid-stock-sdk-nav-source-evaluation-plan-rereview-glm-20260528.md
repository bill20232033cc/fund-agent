# CSRC EID and stock-sdk NAV Source Evaluation Gate — Plan Re-Review (GLM)

日期：2026-05-28

角色：AgentGLM plan re-review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Updated plan：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`

Prior GLM review：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-review-glm-20260528.md`

DS prior review：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-review-ds-20260528.md`

## Verdict

**Accepted.**

Codex planning fix 已完整关闭 DS 两个 required findings（F1、F2）和全部四个 non-blocking findings（F3-F6），且未引入新的阻断问题。Plan is handoff-ready for controller to dispatch evidence worker。

## Step Self-Check

- Current gate / role：本 artifact 只产出 re-review prose；不启动 gateflow，不 implement、commit、push、PR、merge、release 或 golden promotion。
- Scope boundary：只新增本 re-review artifact；不改 plan、production code/tests、score、snapshot、quality gate、golden fixture、drawdown metric、Host/Agent/dayu、年报来源实现或 README。

## DS Required Findings Closure

### DS F1 — Missing `getFundDividendList` Evaluation Steps → Closed

**DS 要求**：在 E2 中新增 `getFundDividendList` evaluation step，明确调用参数、输出字段、cross-check 方法和失败分类。

**Fix 验证**：Plan E2 step 5（plan 第 117-121 行）现在包含：

- **调用参数**：`fund_code="014217"`；若 SDK 支持 `start_date` / `end_date`，显式覆盖包含 `2023-01-11` 的窗口。✅
- **输出字段**：原始字段名、样例行、分红日期 / 除息日 / 除权日字段、每份分红金额、权益登记日 / record date、provider/source URL 字段、returned fund code/name/share class 字段。✅
- **Cross-check 方法**：用 `getFundDividendList` 的 E 类 `014217` 分红日期和每份分红金额，对照 `getFundNavHistory` 在 `2023-01-11` 前后 `accumulated_nav - unit_nav` 的变化；期望与 `FundDocumentRepository.load_annual_report("006597", 2025)` 年报 §3.3 每 10 份 `0.080`（每份 `0.0080`）一致。✅
- **失败分类**：覆盖 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown` 六类。✅

**Assessment**：Fix 完整满足 DS F1 要求。Cross-check 方法正确锚定到前序 controller judgment 接受的 evidence 基准（年报 §3.3 每 10 份 0.080、精确日期 2023-01-11、accumulated - unit NAV 差值 0.0080）。

**Status**：**Closed.** ✅

### DS F2 — `cFundCode=5755` Origin Is Unstated → Closed

**DS 要求**：E1 新增前置步骤（E1-0），通过公开搜索定位 CSRC EID 基金页面再记录内部 ID，而非从 5755 反向验证。

**Fix 验证**：

1. Plan 候选 URL 下方新增显式声明（plan 第 75 行）："该 URL 只能作为用户提供的待验证候选，不是已接受身份。Evidence worker 不得从 `cFundCode=5755` 反向假设目标基金身份。" ✅
2. Plan E1 新增 step 0（plan 第 79 行）：要求 evidence worker 先使用 CSRC EID 公开搜索入口按基金名称 `国泰利享中短债债券` 或 6 位份额代码 `006597` / `006598` / `014217` / `022176` 定位官方披露详情页，记录 EID 返回的内部 ID、详情页 URL、搜索参数和返回身份字段。只有当前置搜索可复现地把名称 / 份额代码映射到 EID 内部 ID 后，才能把该内部 ID 用于后续候选 URL / XHR 解析。✅
3. 若搜索无法映射，分类为 `identity_status="unknown"` 并将 CSRC EID 判为 `blocked`；不得 reverse-assume `5755`。✅
4. Stop condition 更新（plan 第 218 行）新增 "public search cannot map fund name / target 6 位 share-class codes to an official EID internal ID" 作为 stop 条件。✅

**Assessment**：Fix 正确将验证方向从"从 5755 反向验证"改为"从公开搜索正向定位"，符合 AGENTS.md 的 root cause 同源要求。Plan 不再依赖 `cFundCode=5755` 作为已接受身份。

**Status**：**Closed.** ✅

## DS Non-Blocking Findings Closure

### DS F3 — E3 Missing Conditional Dependency → Addressed

Plan E3 新增 "Execution dependency" 段（plan 第 146-149 行）：E3 reconciliation 矩阵只对 E1/E2 中至少返回一条 NAV row 且 `identity_status` 非 `unknown` / `identity_mismatch` 的 source 执行；blocked/rejected/no-row/unknown-identity source 跳过数值 reconciliation，在 E4 matrix 中标记为 `not_applicable` 并保留原始 failure category。

**Status**：Addressed. ✅

### DS F4 — Product-Level CSRC EID Data → Addressed

Plan E1 step 2（plan 第 81 行）新增："同时必须确认 CSRC EID 披露粒度是产品级还是份额级；若只返回产品级数据且无法拆分 A/C/E/F 份额类别，分类为 `identity_mismatch` 或 `blocked`，不得把产品级 NAV 当作份额级 series。"

**Status**：Addressed. ✅

### DS F5 — stock-sdk API Surface Assumption → Addressed

Plan E2 新增 step 3 "验证 stock-sdk API surface"（plan 第 110-112 行）：若 `getFundNavHistory` 不存在或函数名不同，记录实际 API surface，分类为 `not_found`；若存在但参数签名 / 分页模型 / 返回字段或字段语义与 contract 不兼容，分类为 `schema_drift` 并记录实际 contract。

**Status**：Addressed. ✅

### DS F6 — No Explicit `dividend_reinvested` Boundary Rule → Addressed

Plan E3 decision rules 新增（plan 第 174 行）："若 source 字段名暗示复权、分红调整、后复权或 total return，但没有可验证的 provider-owned 文档 / 公式 / 事件级 cross-check 说明其语义，分类为 `adjustment_basis_unknown`；不得从字段名推断为 `dividend_adjusted_nav` 或 `total_return`。"

**Status**：Addressed. ✅

## GLM Prior Findings Re-Assessment

### GLM F1 (Medium) — CSRC EID cFundCode 身份映射 → Resolved by DS F2 Fix

E1 step 0 直接解决了此问题。Evidence worker 现在必须先通过公开搜索正向定位，不再依赖 `cFundCode=5755` 作为起点。

**Status**：Resolved. ✅

### GLM F2 (Medium) — getFundDividendList 作为 cross-check → Resolved by DS F1 Fix

E2 step 5 现在明确限定 `getFundDividendList` 为"E 类分红冗余 cross-check，而非独立 primary source"，且 cross-check 方法锚定到年报 §3.3 基准。

**Status**：Resolved. ✅

### GLM F3 (Low) — Numeric tolerance 未定义具体值 → Unchanged, Non-Blocking

Plan 仍未给出具体容忍度推荐值，但这属于 evidence worker 执行细节。Evidence worker 应在 artifact 中记录实际使用的容忍度及其理由。

**Status**：Remains non-blocking. No action required.

### GLM F4 (Low) — secondary-only 语义精确度 → Unchanged, Non-Blocking

Plan 的 stock-sdk decision 选项未新增 `accepted-secondary-candidate` 细分。但 E2 step 3（plan 第 114 行）和 E4 guardrails（plan 第 192 行）已足够清晰。`secondary-only` 在上下文中的语义是"接受为 secondary cross-check / redundancy client"。

**Status**：Remains non-blocking. No action required.

### GLM F5 (Low) — CSRC EID 更新频率 → Unchanged, Non-Blocking

Plan 未新增时效性评估要求，但升级条件（plan 第 38-39 行）已覆盖 runtime dependency 需求。

**Status**：Remains non-blocking. No action required.

## New Findings Introduced by Fix

逐一检查 fix 新增的 plan 文本，未发现新的阻断问题：

1. E1 step 0 的 "reverse-assume" 禁令（plan 第 79 行）措辞明确，不会导致 evidence worker 误解。
2. E2 step 5 的 cross-check 锚定到年报 §3.3 基准（plan 第 120 行），与前序 controller judgment 一致。
3. E3 execution dependency 的 `not_applicable` 标记（plan 第 149 行）与 E4 per-code matrix 的 `not_applicable` 填写（plan 第 185 行）保持一致。
4. E3 decision rule 新增的 field-name-implied adjustment 规则（plan 第 174 行）措辞无歧义。

**No new blocking findings.** ✅

## Explicit Statement

Controller **may** accept this plan and proceed to evidence slice. DS F1 and F2 required fixes are closed. All DS non-blocking findings are addressed in the updated plan. GLM prior non-blocking findings remain non-blocking and do not require additional plan changes.

建议 controller：
1. Accept plan。
2. 派发 evidence worker 执行 E1-E4。
3. Evidence worker 完成后派发 DS 和 GLM 进行 evidence review。
4. Review 通过后 controller 发出 judgment。

## Non-Goals Preserved

- No plan/code/tests/evidence modified by this re-review.
- No score, snapshot, quality gate, golden fixture, drawdown metric, Host/Agent/dayu, release, PR, push, merge, or promotion change occurred.
- No extractor direct source dependency was introduced.
- No runtime dependency was added.
