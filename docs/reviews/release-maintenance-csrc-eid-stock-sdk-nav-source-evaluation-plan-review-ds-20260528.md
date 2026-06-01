# CSRC EID and stock-sdk NAV Source Evaluation Plan — Plan Review (DS)

日期：2026-05-28

角色：AgentDS plan review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Reviewed artifact：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`

## Verdict

**Changes Required** — 2 required fixes, 4 non-blocking findings. Plan is structurally sound and correctly gates scope, but has two material gaps that must be closed before evidence execution: missing `getFundDividendList` evaluation steps in E2, and unstated origin of `cFundCode=5755`.

## Preflight

已读取全部必读真源：
- `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`
- 最新 NAV adjusted-basis source identity controller judgment + evidence
- `fund_agent/fund/data/nav_models.py`、`nav_repository.py`、`nav_data.py`

Scope check: 本 review 只产出本 artifact；不修改 plan、code、tests、score、snapshot、quality gate、golden、Host/Agent/dayu。

## Findings

### F1 — Missing `getFundDividendList` Evaluation Steps (Changes Required)

**Location**: Plan §E2 (lines 96–130), §Scope (line 48), §Validation Matrix (line 220)

**Finding**: Scope line 48 声明 `getFundDividendList` 为 in-scope，Validation Matrix line 220 也列出该项。但 E2 的 5 个 evaluation steps 完全没有涉及 `getFundDividendList` 的执行步骤、参数、接受标准和失败分类。

**Impact**: Evidence worker 缺少对 E 类分红交叉验证的执行指引，可能遗漏该检查或自行发明验证方法，导致 E 类 accumulated NAV 语义证明与 controller judgment 接受的 evidence 标准不一致。前一个 gate 的 controller judgment 明确以 exact-date E-class distribution cross-check 为核心证据锚点，本 gate 对 stock-sdk 也应保持同等验证强度。

**Required fix**: 在 E2 中新增一个 evaluation step（建议 E2-5b 或独立 step 6），明确：
- `getFundDividendList` 的调用参数（fund_code=014217，可选的 start_date/end_date）
- 输出应记录的字段：分红日期、每份分红金额、除权日 NAV（若有）
- 与 `getFundNavHistory` 返回的 accumulated NAV 在 2023-01-11 前后的 cross-check 方法
- 失败分类：无分红记录归 `not_found`，分红日期/金额与年报矛盾归 `identity_mismatch`，字段不可解析归 `schema_drift`

### F2 — `cFundCode=5755` Origin Is Unstated (Changes Required)

**Location**: Plan §E1 Candidate URL (line 72–73)

**Finding**: Plan 直接给出 `cFundCode=5755` 作为候选 URL，但没有说明 5755 的来源——是通过 EID 公开搜索得到的？是从年报披露中提取的？是推测的？E1 step 2 确实要求证明 5755 到目标份额代码的映射，但如果 5755 本身是错误代码，验证映射的步骤就会变成在错误的搜索空间中寻找正确映射。

**Why this matters**: E1 step 2 的验证方向是"证明 cFundCode=5755 是否映射到 006597/006598/014217/022176"。但第一性原理应该是：先在 CSRC EID 上用基金名称或 6 位代码搜索，再记录返回的内部 ID，然后建立映射。当前表述把验证方向倒置了，可能导致 evidence worker 围绕一个可能是任意值的 cFundCode 做大量无效验证。

**Required fix**: E1 新增一个前置步骤（E1-0），要求 evidence worker 先通过 CSRC EID 的公开搜索功能用基金名称（国泰利享中短债债券）或 6 位代码（006597）定位目标基金的披露页面，再记录 EID 内部使用的基金 ID（可能是 5755 或其他值）。只有在这个前置步骤确认 CSRC EID 内部 ID 之后，才能进入后续的 HTTP/XHR 端点发现和 NAV 表解析。这比"从 5755 反向验证映射"更符合 root cause 同源的约束（AGENTS.md）。

### F3 — E3 Missing Conditional Dependency on E1/E2 (Non-Blocking)

**Location**: Plan §E3 (lines 131–159)

**Finding**: E3 的 cross-source reconciliation 假设 CSRC EID 和 stock-sdk 都已返回 NAV 数据。但如果 E1 或 E2 返回 `blocked`（captcha、session、unavailable），E3 的部分或全部 cross-check 行会变成不可执行。Plan 没有声明 E3 对 E1/E2 结果的依赖关系。

**Risk**: Evidence worker 可能在 CSRC EID blocked 的情况下试图与空数据做 reconciliation，或浪费精力寻找不存在的数据。

**Suggested mitigation**: E3 开头新增条件声明："E3 reconciliation 矩阵仅对 E1/E2 中至少返回 `identity_status` 非 unknown 且至少有一条 NAV 记录的 source 执行；blocked/rejected sources 跳过对应行，在 E4 matrix 中标记为 `not_applicable`。"

### F4 — No Guidance for Product-Level CSRC EID Data (Non-Blocking)

**Location**: Plan §E1 step 5, §Stop Conditions (line 205)

**Finding**: Stop condition line 205 说 "Any source returns product-level data that cannot be separated by A/C/E/F share class" 必须 stop。但 E1 steps 中没有要求 evidence worker 主动检查 CSRC EID 返回的是产品级还是份额级数据。如果 CSRC EID 披露页面按产品（fund）而非按份额类别（share class）组织 NAV 数据，evidence worker 可能在 step 5 才首次发现这个问题，而 step 2 的身份映射可能已经错误地尝试把产品级 ID 映射到份额级代码。

**Suggested mitigation**: E1 step 2 新增检查项：确认 CSRC EID 披露粒度是产品级还是份额级。如果是产品级且无法拆分 A/C/E/F，直接报告 `identity_mismatch` 或 `blocked`。

### F5 — stock-sdk API Surface Assumption (Non-Blocking)

**Location**: Plan §E2 step 2 (lines 102–106)

**Finding**: Plan 假设 `chengzuopeng/stock-sdk` 提供 `getFundNavHistory` 函数，接受 `fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh` 参数。如果实际 API 形态不同（不同函数名、不同参数签名、只返回部分字段），evidence worker 需要判断"API 不存在"和"API 存在但语义不同"之间的区别。

**Suggested mitigation**: E2 新增一个分类规则："若 `getFundNavHistory` 不存在或函数名不同，记录实际 API surface，分类为 `not_found` 并报告。若存在但参数/返回值语义不同，分类为 `schema_drift` 并记录实际 contract。"

### F6 — No Explicit `dividend_reinvested` Boundary Rule (Non-Blocking)

**Location**: Plan §E3 Decision Rules (lines 156–159)

**Finding**: E3 decision rule line 158–159 说 "能证明 dividend-reinvested total return：必须另开 source semantics gate；本 gate 不接受字段名推断。" 这个规则正确，但它只覆盖了 source 主动声称 total return 的场景。没有覆盖另一种情况：stock-sdk 或 CSRC EID 的字段名暗示了 dividend adjustment（如 `复权净值`、`后复权单位净值`），但 provider 文档中没有明确说明这是 dividend-reinvested 还是 additive cash distribution。

**Suggested mitigation**: E3 decision rules 新增一条："若 source 返回的字段名暗示 dividend adjustment 但无可验证的 provider 文档说明其语义，分类为 `adjustment_basis_unknown`，不得从字段名推断为 `dividend_adjusted_nav` 或 `total_return`。"

## Positive Observations

以下设计点值得肯定：

1. **Scope gating 正确**: non-goals 明确排除了 drawdown blocker 解除、metric 实现、code/test 修改、score/snapshot/quality/golden 变更和 PR/push/release。E4 guardrails 重申了这些约束。

2. **Share class separation 正确**: 多处明确 A/C/E/F 必须分开，产品级数据不得混入份额级（E2 acceptance criteria, stop conditions）。

3. **Failure taxonomy 完整**: E1 step 6 的分类覆盖了 NavFailureCategory 的全部 8 个类别，且与 `nav_models.py` 对齐。

4. **Provider lineage 评估独立于 source output**: E2 step 3 要求反查 underlying provider，step 5 要求独立评估 dependency model。这避免了把 source semantics 和 runtime risk 混为一谈。

5. **Dependency model 分级合理**: `runtime dependency` / `subprocess adapter` / `MCP/evidence-only` / `reject` 四级分类清晰，每一级都有明确的进入条件和约束。

6. **Validation matrix 明确区分 what runs and what doesn't**: 清楚标注了 ruff/pytest/snapshot/score/quality gate 不需要在此 evidence gate 运行。

7. **Upgrade conditions 正确**: gate classification 节声明若需要 runtime dependency、schema change、public contract change 等必须升级到 implementation/architecture gate。

8. **Annual report reconciliation constrained to FundDocumentRepository**: E3 step 1 明确要求通过 `load_annual_report("006597", 2025)` 读取，不直接读 PDF/cache。

9. **Stop conditions 清晰**: 19 条 stop condition 覆盖了 captcha、manual-only、identity_mismatch、product-level data、dependency mutation 和 unclassified failure 等关键场景。

10. **Completion report format 完整**: 为 evidence worker 提供了结构化的输出模板。

## Required Fixes Summary

| ID | Severity | Location | Fix |
|----|----------|----------|-----|
| F1 | Changes Required | E2 | 新增 `getFundDividendList` evaluation step，明确调用参数、输出字段、cross-check 方法和失败分类 |
| F2 | Changes Required | E1 | 新增 E1-0 前置步骤，通过公开搜索定位 CSRC EID 基金页面再记录内部 ID，而非从 5755 反向验证 |

## Residual Risks (If Accepted After Fix)

1. **CSRC EID 技术可达性未知**: E1 假设 CSRC EID 有可复现的 HTTP API 或 XHR 端点。如果 CSRC EID 使用重度 JavaScript 渲染（SPA）、WebSocket 推送或需要复杂的反爬机制，evidence worker 可能需要浏览器自动化工具（headless browser）才能完成 E1 smoke，而 plan 没有预配这种工具链。

2. **stock-sdk 运行时依赖的隐藏成本**: E2 评估 stock-sdk dependency model，但 `chengzuopeng/stock-sdk` 作为 npm 包可能有自己的 transitive dependencies。如果 evidence worker 只在文档层面检查，可能遗漏实际安装后的依赖树膨胀。

3. **E 类分红验证的单一事件依赖**: 014217 只有一次 known distribution（2023-01-11）。如果 stock-sdk 或 CSRC EID 的 accumulated NAV 在这个日期有数据但数值偏离 0.0080，单一事件不足以区分"accumulated NAV 语义不同"和"数据精度/rounding 差异"。

4. **Cross-source reconciliation 的日期对齐**: Different sources may have different trading calendars (e.g., CSRC EID may skip certain days). The plan doesn't specify how to handle date mismatches in reconciliation.

## Controller Guardrail Verification

逐条检查 review focus 问题：

| Review Focus | Plan Status | Finding |
|---|---|---|
| CSRC EID 作为 official primary source candidate 而不假设 cFundCode=5755 身份 | 部分满足 | E1 step 2 有验证要求但缺少前置搜索步骤 → F2 |
| 要求 machine-readable date/unit_nav/accumulated_nav 且对 manual/session/captcha fail closed | 满足 | E1 steps 1-6 全覆盖 |
| stock-sdk provider lineage、field semantics、license、dependency model 与 source output 分开评估 | 满足 | E2 step 3,5 独立评估 |
| 防止 stock-sdk 不经 implementation/architecture gate 成为 runtime dependency | 满足 | E2 step 5, stop conditions, E4 guardrails |
| A/C/E/F 分开且要求 E 类 distribution cross-check | 部分满足 | Share class separation 到位但 E2 缺少 `getFundDividendList` 步骤 → F1 |
| 保留已接受 Eastmoney/Akshare accumulated_nav evidence，不过度声称 total_return/dividend_adjusted | 满足 | E3 decision rules, E4 guardrails |
| Failure taxonomy、metadata 要求、validation matrix、stop conditions 完整 | 满足 | 全部覆盖 |
| 避免 drawdown blocker 解除、metric 实现、score/snapshot/quality/golden 变更、PR/push/release | 满足 | Non-goals 和 E4 guardrails |

## Explicit Statement

Controller **不得** proceed to evidence slice 直到 F1 和 F2 被修复并 re-review accepted。修复后的 plan 需经 DS 和 GLM re-review（或至少 DS re-review 确认 F1/F2 已关闭），之后 controller 才可派发 evidence worker 执行 E1-E4。

F3–F6 为非阻断建议，controller 可选择是否要求 plan 修改，或将这些作为 evidence worker 执行时的注意事项交给 evidence review 检查。
