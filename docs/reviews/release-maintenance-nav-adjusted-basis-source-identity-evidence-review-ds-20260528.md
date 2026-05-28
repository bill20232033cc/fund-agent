# NAV Adjusted-Basis Source Identity Gate — Evidence Review (DS)

日期：2026-05-28

角色：evidence review worker (DS)，非 controller、非 implementation worker。不编辑 code/test/evidence，不 commit/push/PR。

Work unit：`NAV adjusted-basis source identity gate`

Accepted plan：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`

Evidence under review：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`

## Verdict

**Accepted**

## Review Basis

本 review 基于以下真源交叉验证（不再重新读取已在上轮 plan review/re-review 中覆盖的文件，除非 evidence 涉及新事实需要对照代码验证）：

| 真源 | 用途 |
|------|------|
| Accepted plan | Proof standard、failure taxonomy、E1/E2 actions scope、identity matrix、output options |
| Plan re-reviews (DS + GLM) | 确认所有 prior plan findings 已关闭，E1/E2 scope 约束已 fix |
| `nav_models.py` | `NavType` / `AdjustmentBasis` / `DividendAdjustmentStatus` Literal 域、`NavFailureCategory`、`insufficient_records` / `missing_date_range` |
| `nav_repository.py` | 当前 hard-coded `unit_nav` / `raw_unit_nav`；future implementation 的改造范围参考 |
| Prior controller judgments | E-class 2023 distribution facts (0.080 per 10 shares)、`FundDocumentRepository` 年报加载路径 |

## Plan Compliance Verification

### Proof Standard (Plan §Proof Standard For Adjustment Basis)

Plan 要求：至少一条 primary proof + 一条 independent consistency check。

Evidence 对 `累计净值走势` / `Data_ACWorthTrend` 的证明结构：

| 要素 | 来源 | 状态 |
|------|------|------|
| **Primary proof #3**：官方披露提供份额分红事件 + provider series 在除权日附近按预期方向体现分红 | 年报 §3.3（`FundDocumentRepository`）证明 E class 2023 分红 0.080/10 份；provider page 提供精确日期 2023-01-11 | **E class 满足**；A/C/F 无分红事件可观察 |
| **Independent check #1**：raw unit NAV 与 candidate accumulated NAV 在分红事件附近按分红金额 diverged | E class cross-check 表格（line 203-213）：2023-01-11 divergence 精确从 0.0000 变为 0.0080，持续至年末 | **E class 满足** |
| **Independent check #3**：candidate source identity 匹配 requested code/name/share class | 四个 code 的 `fS_code` / `fS_name` 均精确匹配，provider page + 年报 §2 独立确认 | **四个 class 全部满足** |

对 A/C 的额外验证：
- 年报 §3.3 证明 A/C 过去三年无利润分配 (line 181-182)
- Provider page 报告 dividend count = 0、split count = 0 (line 121, 132)
- 1809 rows 全部 unit NAV = accumulated NAV (line 117, 128)
- 因此对 A/C，accumulated NAV 语义通过同一 source variable 在 E class 的行为验证 + A/C 无分红独立确认来证明

**结论**：E class 满足 primary proof + independent check 的完整标准。A/C 通过同源变量推断 + 无分红独立确认 + 全量数据一致性来证明。——足够接受，但应记录推断性质（见 F1）。

### E1 Scope Compliance

Plan fix 要求 E1 "parse only `fS_code` / `fS_name` values and variable presence. Do not parse or record numeric content from JS variables."

Evidence (line 18): "E1 JS smoke 只解析 `fS_code` / `fS_name` 和变量存在性；未解析或记录 JS 数值变量内容。" E1 Smoke Matrix 中 JS rows 只记录 identity 值和 variable presence（`Data_netWorthTrend`, `Data_ACWorthTrend`, `Data_grandTotal` present）。**通过。**

### E2 Distribution Cross-Check Compliance

Plan fix 要求四条件 window-based divergence check（若精确 ex-date 不可得）。Evidence 中的 E-class cross-check 使用了精确 ex-date（provider page 提供的 2023-01-11），因此走的是精确日期路径，window fallback 未被触发。但 plan 的四条件作为兜底已就位。**通过。**

### Insufficient History Mapping

Plan 要求 evidence-level `insufficient_history` 必须映射到 current model category：`insufficient_records` 或 `missing_date_range`。

Evidence 对 F class (line 242): `insufficient_history` → "model mapping `missing_date_range`"。理由：F class 成立于 2024-10-08，2023 及之前窗口不可用。这是正确的映射（日期窗口不足，非行数不足）。**通过。**

### Failure Taxonomy Compliance

Evidence 使用了以下 plan taxonomy category：`adjustment_basis_unknown`（累计收益率）、`missing_date_range`（F class insufficient_history 映射）。`raw_unit_nav` 正确标记为 not strong evidence。**通过。**

### Output Options Compliance

Evidence 使用 `partial-acceptance-with-blocked-classes`（plan fix 新增的输出选项），并在 Recommended Decision 中显式记录 accepted/blocked classes。**通过。**

## Findings

### F1 (Moderate) — A/C accumulated_nav proof is inferential via same-variable E-class behavior; limitation should be explicitly recorded in disposition

**位置**：Evidence Candidate Disposition Matrix, `累计净值走势` A class row (line 239), C class row (line 240)

**分析**：

A 和 C class 的 `累计净值走势` 在整个历史期间（各 1809 rows）与 `单位净值走势` 完全相同（first=1.0, last=same as unit NAV）。Evidence 对此的证明链是：
1. E class 的 `Data_ACWorthTrend` 变量在 2023-01-11 精确体现了 0.0080 分红累加行为（直接定量证明）
2. A/C 同源同变量名 (`Data_ACWorthTrend`)、同 provider、同产品
3. 年报 + provider page 独立确认 A/C 无分红
4. 因此 A/C 的 accumulated NAV = unit NAV（无分红可累加）

这条证明链逻辑正确——E class 的精确定量证据证明了 `Data_ACWorthTrend` 的金融语义（unit NAV + 累计现金分红），且 A/C 确实没有分红事件。但 A/C 缺少直接可观察的分红事件来独立验证该变量对 A/C 特定 code 的行为。证明依赖跨 share class 的变量名语义一致性推断。

**建议**：在 evidence Candidate Disposition Matrix 的 A/C rows 中增加 limitation 说明：accumulated_nav semantics for A/C is proven by same-variable E-class distribution cross-check plus independent no-distribution confirmation; no directly observable distribution event exists for A/C per se. 同时 E class row 应注明它是唯一有直接定量证明的 class。

**严重程度**：不阻塞 accept。证据链充分，但 limitation 应在 decision record 中显式记录，避免 future consumer 误以为 A/C 有独立的分红事件验证。

### F2 (Minor) — Identity verification relies on cross-endpoint binding (JS pingzhongdata ≠ Akshare API); same-response binding not achieved

**位置**：Evidence Candidate Disposition Matrix 各 row 的 "Identity status if JS identity is integrated" 列；Recommended Decision source identity proof 段 (line 267-269)

**分析**：

Evidence 对所有四个 code 报告 `identity_status="verified"`（在 JS identity integrated 的条件下）。但 plan 的 A/C/E/F Source Identity Plan 要求 identity 为 "`verified` only if source returns code...or same-response metadata proves it."

当前证据结构：
- 数据 series 来自 Akshare `fund_open_fund_info_em` → DataFrame 无 identity 列
- 身份数据来自 Eastmoney JS `pingzhongdata/{code}.js` → 独立 HTTP 请求
- 两者是同 provider（Eastmoney/天天基金）、不同 endpoint

这不是 same-response binding。但 plan 的 Candidate 2 节明确允许 JS identity 作为 "source identity / source_id / source_url evidence candidate"，且 evidence 额外提供了 provider page + 年报 §2 两重独立确认。

**评估**：identity proof 整体强度足够（三重独立来源一致），但 "verified" 的 claim 应附带条件说明：identity is verified through same-provider cross-endpoint binding plus independent page/disclosure corroboration, not same-response metadata。Future implementation 中 `NavSourceMetadata.source_url` / `source_id` 应记录 identity 来源的 URL 以维持可审计性。

**建议**：在 Recommended Decision source identity proof 段增加一行，说明 identity 的 endpoint 来源与 data endpoint 不同，以及三重确认的来源列表。

**严重程度**：不阻塞 accept。但这是 future implementation 的一个重要设计约束。

### F3 (Informational) — A/C dividend_adjustment_status "adjusted" technically correct but could surprise a reader

**位置**：Evidence Candidate Disposition Matrix, `累计净值走势` A/C rows (line 239-240)

**分析**：

Evidence 对 A/C 标记 `dividend_adjustment_status="adjusted" for cash distributions; no distribution observed`。从 accumulated NAV 的定义看，它按定义是对现金分红做了加法调整的序列，因此 `adjusted` 正确。但 A/C 实际没有可观察的分红事件，`adjusted` + `no distribution observed` 的组合可能让读者困惑。

这纯粹是表述层面。不阻塞，不要求修改 evidence。Controller 在 judgment 中确认即可。

## Review Focus Adversarial Check

### 1. Does evidence overclaim dividend-adjusted or total_return?

**否。** Evidence 反复申明（line 220, 244, 255）`accumulated_nav` 不是 dividend-reinvested total-return 路径。`累计收益率走势` / `LJSYLZS` 全部 blocked as `adjustment_basis_unknown`。`raw_unit_nav` 全部 retained as not strong evidence。

### 2. Is source identity auditable and not guessed?

**是。** 每个 code 的 identity 有四重锚点：JS `fS_code`/`fS_name`、provider page 显示、年报 §2 code-class mapping、Akshare source inspection 确认 endpoint lineage。无 name suffix guessing。

### 3. Could E-class cross-check have been a coincidence?

**否。** Divergence 精确到 0.0080（等于年报公布的分红金额），发生日期精确匹配 provider page 公布的除权日 2023-01-11，且差距在整个后续序列中持续。数学精确性排除了巧合。

### 4. Does F partial acceptance map correctly?

**是。** F class 标记 `missing_date_range`（2023 及 pre-2024-10-08 窗口不可用）。这符合 plan 的映射规则：uncovered date windows → `missing_date_range`。

### 5. Is scope truly evidence-only?

**是。** Evidence artifact 位于 `docs/reviews/` 下，未修改任何 Python、test、schema、score、snapshot、quality gate、golden fixture。Validation 段正确记录了未运行 ruff/pytest 的原因。

## Residual Risks

1. **A/C accumulated_nav 推断性质**（F1）：缺少 A/C 自身分红事件直接验证。如果 A 或 C 未来发生分红而 `Data_ACWorthTrend` 行为异常，当前证据无法预先检测。风险低——同一 provider、同一变量名、同一产品跨 share class 的语义一致性假设合理。
2. **Cross-endpoint identity binding**（F2）：Future implementation 必须在 adapter 层绑定两个 endpoint（data + identity），并在任一 endpoint 不可用时正确 fail。风险低——两个 endpoint 同 provider，且 provider page 可作为第三个 corroborating source。
3. **accumulated_nav 对 drawdown metric 的适用性未验证**：Plan 和 evidence 都明确 accumulated_nav 不是 total-return，未来 drawdown metric 需要独立的 metric contract gate 决定是否接受 accumulated_nav 作为输入。这是 intentional residual，不是 evidence 的缺陷。
4. **Provider page 依赖**：E2 依赖天天基金 provider pages 获取精确除权日期和 dividend/split count。这些页面是 public HTML，结构可能变化。当前只用于 evidence（非 production），但 future adapter 如需消费这些数据需要更稳定的接口。
5. **No production data-path validation**：Evidence 证明了 source capability 和 semantics，但未通过 `FundNavRepository.load_nav_series()` 验证 typed 路径（当前 repository 不支持 `累计净值走势` indicator）。这被正确地推迟到 future implementation gate。

## Controller May Proceed

Controller 可以接受此 evidence artifact 并进入 controller judgment。

F1 和 F2 均为非阻塞——evidence 整体满足 plan 的 proof standard。建议 controller 在 judgment 中确认 F1（A/C inferential proof limitation）和 F2（cross-endpoint identity binding）的接受态度，并在 future implementation gate 中作为设计约束。

E-class cross-check 是本次 evidence 的核心定量锚点：精确日期、精确金额、精确 divergence、年报 + provider page 双重确认。这为 `累计净值走势` / `Data_ACWorthTrend` 作为 `accumulated_nav` source 提供了可靠的 proof foundation。
