# CSRC EID and stock-sdk NAV Source Evaluation Plan — Plan Re-Review (DS)

日期：2026-05-28

角色：AgentDS plan review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Re-reviewed artifact：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`（Codex planning fix 后版本）

Prior DS review：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-review-ds-20260528.md`

## Verdict

**Accepted** — 上轮两条 required fixes (F1/F2) 及四条 non-blocking suggestions (F3–F6) 均已解决。未引入新的阻断问题。Plan 可进入 evidence slice。

## Per-Finding Status

### F1 — Missing `getFundDividendList` Evaluation Steps → FIXED

**Prior state**: E2 的 5 个 evaluation steps 完全没有涉及 `getFundDividendList`。

**Updated plan**: E2 新增 step 5（lines 117–121），包含：
- 调用参数明确：`fund_code="014217"`，可选 `start_date`/`end_date` 覆盖含 `2023-01-11` 的窗口
- 输出字段完整：分红日期/除息日/除权日、每份分红金额、权益登记日、provider/source URL、returned fund code/name/share class
- Cross-check 方法清晰：`getFundDividendList` 分红日期与金额，对照 `getFundNavHistory` 在 `2023-01-11` 前后 `accumulated_nav - unit_nav` 变化，期望与 `FundDocumentRepository.load_annual_report("006597", 2025)` §3.3 每 10 份 `0.080`（每份 `0.0080`）一致
- 失败分类六类齐全：`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`

定位正确（redundant cross-check，非独立 primary source），与前 gate evidence 标准一致。

### F2 — `cFundCode=5755` Origin Is Unstated → FIXED

**Prior state**: Plan 直接给出 `cFundCode=5755` 候选 URL，未说明来源，验证方向倒置。

**Updated plan**:
- URL 改标为 "User-supplied candidate URL"，新增显式声明："该 URL 只能作为用户提供的待验证候选，不是已接受身份。Evidence worker 不得从 `cFundCode=5755` 反向假设目标基金身份。"（lines 69–75）
- E1-0 前置步骤（line 79）：通过 CSRC EID 公开搜索按基金名称 `国泰利享中短债债券` 或份额代码定位，记录 EID 内部 ID 后再进入 HTTP/XHR。搜索不可复现时直接 block，不得 reverse-assume 5755
- Stop condition 同步更新（line 218）：新增 "public search cannot map fund name / target 6 位 share-class codes to an official EID internal ID"

验证方向已从"反向验证 5755"纠正为"先搜索定位，再记录内部 ID，再证明映射"。

### F3 — E3 Missing Conditional Dependency on E1/E2 → ADDRESSED

**Updated plan**: E3 新增 "Execution dependency" 节（lines 146–149），明确 E3 只对有至少一条 NAV row 且 identity 非 unknown/mismatch 的 source 执行；blocked/rejected 跳过并在 E4 标记 `not_applicable`。

### F4 — No Guidance for Product-Level CSRC EID Data → ADDRESSED

**Updated plan**: E1 step 2（line 81）新增："同时必须确认 CSRC EID 披露粒度是产品级还是份额级；若只返回产品级数据且无法拆分 A/C/E/F 份额类别，分类为 `identity_mismatch` 或 `blocked`，不得把产品级 NAV 当作份额级 series。"

### F5 — stock-sdk API Surface Assumption → ADDRESSED

**Updated plan**: E2 新增 step 3（lines 110–112），明确区分两种场景：API 不存在/函数名不同 → `not_found`，记录实际 API surface；API 存在但签名/字段语义不兼容 → `schema_drift`，记录实际 contract。

### F6 — No Explicit `dividend_reinvested` Boundary Rule → ADDRESSED

**Updated plan**: E3 decision rules 新增（line 174）："若 source 字段名暗示复权、分红调整、后复权或 total return，但没有可验证的 provider-owned 文档/公式/事件级 cross-check 说明其语义，分类为 `adjustment_basis_unknown`；不得从字段名推断为 `dividend_adjusted_nav` 或 `total_return`。"

## New Issue Check

逐项检查 fix 是否引入新问题：

| Check | Result |
|---|---|
| E2 步骤编号偏移（原 1-5 → 现 1-7）是否导致内部引用断裂 | 否，plan 内无步骤编号自引用 |
| E1-0 前置搜索是否改变了 E1 其他步骤的语义 | 否，step 2 的身份验证从"证明 cFundCode=5755"改为"证明前置搜索得到的 EID 内部 ID"，语义更精确 |
| `getFundDividendList` 是否被误标为 primary source | 否，定位为 "redundant cross-check，而非独立 primary source" |
| 新增内容是否超出 evidence-only scope | 否，所有新增内容为 evaluation steps / decision rules / dependency declarations |
| 原有 non-goals 是否被削弱 | 否，drawdown blocker、metric、code/test、score/snapshot/quality/golden、PR/push/release 仍全部排除 |
| E1-0 要求搜索 `006597`/`006598`/`014217`/`022176` 是否与 E2 的 A/C/E/F 分离要求一致 | 是，E1-0 按份额代码搜索，与 share class separation 要求对齐 |

## Prior Residual Risks (Still Applicable)

上轮 review 列出的四条 residual risk 在 plan fix 后仍然适用，controller 应在 evidence execution 前知晓：

1. CSRC EID 技术可达性未知（SPA/JS 渲染可能需要 headless browser）
2. stock-sdk npm transitive dependency 膨胀风险
3. E 类分红验证的单一事件依赖（仅 2023-01-11 一次 known distribution）
4. Cross-source reconciliation 的交易日历对齐

## Explicit Statement

Controller **可以** accept 当前 plan 并 proceed to evidence slice（派发 evidence worker 执行 E1-E4）。
