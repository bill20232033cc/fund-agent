# CSRC EID and stock-sdk NAV Source Evaluation Gate — Plan Review (GLM)

日期：2026-05-28

角色：AgentGLM plan review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Plan artifact：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`

## Verdict

**Accepted with non-blocking findings.**

本 plan 整体结构严谨，与 AGENTS.md、design.md、implementation-control.md、前序 NAV source identity controller judgment / evidence 对齐良好。Plan 正确分类为 `heavy`，scope/non-goals 清晰，stop conditions 完备，validation matrix 合理。以下 findings 不阻断 controller 派发 evidence worker，但建议 evidence worker 在执行时注意。

## Step Self-Check

- Current gate / role：本 artifact 只产出 plan review prose；不启动 gateflow，不 implement、commit、push、PR、merge、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、前序 NAV source identity controller judgment / evidence、`nav_models.py`、`nav_repository.py`、`nav_data.py` 以及被审 plan artifact。
- Scope boundary：只新增本 review artifact；不改 plan、production code/tests、score、snapshot、quality gate、golden fixture、drawdown metric、Host/Agent/dayu、年报来源实现或 README。

## Findings

### F1 — Severity: Medium — CSRC EID cFundCode 身份映射的完整性

**Plan 行号**：E1 step 2（plan 第 77-78 行）

Plan 要求"找到官方页面字段、链接、表格或年报披露信息把 `5755` 映射到 `006597` / `006598` / `014217` / `022176`"。

**Finding**：Plan 只给了一个 `cFundCode=5755` 的候选 URL 示例，但没有明确要求 evidence worker 证明 `cFundCode` 是否为 CSRC EID 内部基金 ID 还是公开份额代码。若 `5755` 是 EID 内部 ID，需要找到从 6 位份额代码到该内部 ID 的可复现映射方法；若无法映射，应直接 `identity_status="unknown"`。

**Assessment**：Plan 的 E1 step 2 已经覆盖了这个问题——它要求"若 EID 使用内部基金 ID 而非 6 位份额代码，必须找到……映射"。这是充分的。但建议 evidence worker 在执行时优先确认 `cFundCode` 的编码体系，避免在无法证明映射关系时接受数据。

**Disposition**：Non-blocking。Plan 已覆盖，只是建议 evidence worker 特别关注此步骤。

### F2 — Severity: Medium — stock-sdk `getFundDividendList` 的角色需限定为 cross-check 而非独立来源

**Plan 行号**：E2 步骤列表第 4 点（plan 第 48 行）和 E3 cross-check（plan 第 131-155 行）

Plan 在 In Scope 中列出"评估 `getFundDividendList` 是否能 cross-check E 类 `014217` 历史分红"。

**Finding**：前序 evidence 已通过 `FundDocumentRepository` 年报 §3.3 和 Akshare/Eastmoney provider page 交叉验证了 E 类 2023 分红事件（每 10 份 0.080，精确日期 2023-01-11，accumulated - unit NAV 差值 0.0080）。stock-sdk `getFundDividendList` 只能作为 redundant cross-check，不能作为 primary evidence for dividend adjustment。Plan 在 E3 决策规则中已说"能证明 `accumulated_nav`：只分类为 `adjustment_basis="accumulated_nav"`，不得写成 `dividend_adjusted_nav`"，这是正确的。

**Assessment**：Plan 的处理是充分的。建议 evidence worker 在记录 `getFundDividendList` 结果时，明确标注其 underlying provider（很可能也是 Eastmoney），避免将其视为独立于已接受 evidence 的新证明。

**Disposition**：Non-blocking。

### F3 — Severity: Low — E3 cross-source reconciliation 的 Numeric tolerance 未定义具体值

**Plan 行号**：E3 step 4（plan 第 148-149 行）

Plan 说"允许 Decimal 精度差异必须显式定义容忍度"。

**Finding**：Plan 正确要求了显式容忍度，但没有在 plan 阶段给出推荐值。Evidence worker 需要在执行时自行定义。

**Assessment**：对于 accumulated NAV 的交叉验证，考虑到不同 source 对同一底层数据的 Decimal 精度（如 Akshare DataFrame 到 Python Decimal 的转换），合理的容忍度可能是 4 位小数绝对差 ≤ 0.0001，或相对差 ≤ 0.01%。但这属于 evidence worker 执行细节，不需要 plan 预先锁定。

**Disposition**：Non-blocking。Evidence worker 应在 artifact 中记录实际使用的容忍度及其理由。

### F4 — Severity: Low — Plan 的 stock-sdk decision 选项缺少 `accepted-secondary-candidate` 细分

**Plan 行号**：E4（plan 第 166-167 行）

Plan 给出的 stock-sdk decision 选项为：`accepted-runtime-candidate` / `secondary-only` / `evidence-only` / `rejected` / `blocked`。

**Finding**：前序 NAV source identity controller judgment 已接受 Eastmoney/Akshare `累计净值走势` 为 `accumulated_nav` source/basis identity candidate。若 stock-sdk underlying provider 就是 Eastmoney，那么按照 plan 的 E2 step 3（plan 第 108-110 行），stock-sdk 只能作为"secondary/cross-check candidate"。但 plan 的 E4 decision 选项中没有 `accepted-secondary-candidate`，只有 `secondary-only`。`secondary-only` 的语义可能不够明确——它是"接受为 secondary cross-check"还是"只能 evidence-only cross-check"？

**Assessment**：这不构成阻断。Plan 在 E2 step 3 和 E4 controller judgment guardrails（plan 第 173-176 行）已经足够清晰地说明了 stock-sdk 的默认位置。建议 evidence worker 在输出 decision 时，若 stock-sdk underlying provider 为 Eastmoney 且 license 可接受，使用 `secondary-only` 并在报告中明确说明其作为 "secondary cross-check / redundancy client" 的角色。

**Disposition**：Non-blocking。

### F5 — Severity: Low — Plan 缺少对 CSRC EID 数据更新频率和时效性的评估要求

**Plan 行号**：E1（plan 第 66-94 行）

Plan 要求验证 full-history 或明确覆盖所需窗口、date_range、record_count 等，但未显式要求评估 CSRC EID 数据的更新频率（是否每日更新？是否有延迟？）。

**Assessment**：对于历史 NAV source candidate，更新频率和时效性影响其作为 runtime source 的可行性。但当前 gate 只是 source identity / evaluation gate，不是 runtime adapter implementation gate。Plan 的 E4 decision 和升级条件（plan 第 38-39 行）已要求 evidence worker 在遇到 runtime dependency 需求时停止并交回 controller。这足以覆盖时效性风险。

**Disposition**：Non-blocking。可作为 evidence worker 执行时的观察项。

## Cross-Check Against Review Focus

### Is the CSRC EID evaluation plan strong enough to prove official machine-readable historical NAV identity and accumulated basis?

**Yes.** Plan E1 要求验证 HTTP GET/POST/XHR 可复现端点、身份映射、字段语义、full-history 覆盖和失败分类。Plan 明确区分了 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error` 和 `adjustment_basis_unknown`。若 CSRC EID 不能满足任一条件，plan 要求 `blocked` 或 `rejected`。

### Is stock-sdk evaluated as both a possible client and a dependency/license/runtime risk?

**Yes.** Plan E2 要求评估 repository、package metadata、license、dependency model、provider lineage、错误分类和 runtime fit。Plan 显式区分了 `runtime dependency`、`subprocess adapter`、`MCP/evidence-only adapter` 和 `reject` 四种处置方式，且不允许在本 gate 中添加项目依赖。

### Are source metadata/provenance fields sufficient for typed NAV contract future implementation?

**Yes.** Plan 的 "Required Source Metadata" 表（plan 第 179-195 行）列出了 `source_name`、`source_url/provider`、`retrieved_at`、`fund_code`、`share_class`、`date_range`、`record_count`、`unit_nav`、`accumulated_nav`、`adjustment_basis`、`identity_status` 和 `failure_category`。这些与 `nav_models.py` 的 `NavSourceMetadata` 字段（`source_name`、`origin_source`、`source_id`、`source_url`、`cached`、`retrieved_at`、`cache_updated_at`、`requested_fund_code`、`returned_fund_code`、`returned_fund_name`、`failure_category`）基本对齐。

### Does the plan require source-owned semantics and cross-source reconciliation before accepting accumulated_nav?

**Yes.** Plan E2 step 3 要求反查 SDK underlying provider 并证明 lineage。Plan E3 要求用年报 §3.1/§3.2/§3.3、已接受 Eastmoney/Akshare evidence、CSRC EID 和 stock-sdk 互相校验。Plan 明确禁止字段名推断（E3 decision rules，plan 第 156-158 行）。

### Does it correctly block raw unit NAV, unknown cumulative return, total_return, and dividend_adjusted_nav unless separately proven?

**Yes.** Plan E3 decision rules（plan 第 156-158 行）明确规定：
- "只有 raw unit NAV 可得：保持 blocked"
- "能证明 `accumulated_nav`：只分类为 `adjustment_basis="accumulated_nav"`，不得写成 `dividend_adjusted_nav` 或 `total_return`"
- "能证明 dividend-reinvested total return：必须另开 source semantics gate"

### Are annual report checks constrained to FundDocumentRepository?

**Yes.** Plan E3 step 1（plan 第 137-141 行）明确要求"Annual report via `FundDocumentRepository`"、"只通过 repository 读取"、"必须记录年报章节/表格锚点，不得直接读 PDF/cache"。Non-goals（plan 第 58 行）也明确"不绕过 `FundDocumentRepository` 读取年报 / PDF / cache"。

### Does validation stay evidence-only unless code/tests change?

**Yes.** Plan Validation Matrix（plan 第 210-224 行）明确标注 `Full ruff: No unless code/tests changed`、`Full pytest: No unless code/tests changed`、`Snapshot / score / quality gate: No`。Plan 的 Step Self-Check（plan 第 17 行）也声明"Evidence and validation：本 gate 为 evidence-only"。

### Are decisions expressive enough: CSRC accepted/rejected/blocked and stock-sdk accepted/secondary-only/evidence-only/rejected/blocked?

**Yes.** Plan E4（plan 第 166-167 行）给出了 CSRC EID 的 `accepted-primary-candidate` / `rejected` / `blocked` 和 stock-sdk 的 `accepted-runtime-candidate` / `secondary-only` / `evidence-only` / `rejected` / `blocked`。这与 review focus 要求的表达力一致。Minor finding F4 关于 `secondary-only` 语义精确度不影响整体充分性。

## Alignment with Prior Accepted Artifacts

Plan 正确引用了前序 NAV source identity controller judgment 的以下关键结论：

1. Eastmoney/Akshare `累计净值走势` / `Data_ACWorthTrend` 已接受为 `accumulated_nav` source/basis identity candidate（plan Truth Source Recap 第 26 行）。
2. `LJSYLZS` 仍为 `adjustment_basis_unknown`（同上）。
3. raw unit NAV 仍非强证据（同上）。
4. 本 gate 只评估新来源，不进入 adapter normalization 或 drawdown metric（plan Truth Source Recap 第 27 行）。

Plan 正确与 `nav_models.py` 当前的 typed contract 对齐：
- `NavType` 包含 `unit_nav`、`accumulated_nav`、`adjusted_nav`、`total_return_index`、`unknown`。
- `AdjustmentBasis` 包含 `raw_unit_nav`、`accumulated_nav`、`dividend_adjusted_nav`、`total_return`、`unknown`。
- `NavFailureCategory` 包含 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`。
- `NavSourceMetadata` 包含 `source_name`、`origin_source`、`source_id`、`source_url`、`cached`、`retrieved_at`、`cache_updated_at`、`requested_fund_code`、`returned_fund_code`、`returned_fund_name`、`failure_category`。

Plan 的 Required Source Metadata 表与这些 typed 字段基本对齐，后续 implementation gate 不需要大改 schema。

## Required Fixes

None. All findings are non-blocking.

## Residual Risks

1. **CSRC EID 身份映射风险**：若 `cFundCode` 编码体系与 6 位份额代码无稳定映射关系，CSRC EID 可能只能被判为 `blocked`。这不影响已接受的 Eastmoney/Akshare accumulated NAV candidate。
2. **stock-sdk provider 透明度风险**：若 stock-sdk 隐藏 provider 或混合多个 source，可能被判为 `rejected` 或 `evidence-only`。这不影响已有路径。
3. **CSRC EID 可机读性风险**：若 CSRC EID 需要 captcha 或不可复现 session，只能被判为 `blocked`。Plan 的 stop conditions（plan 第 199-200 行）已覆盖此场景。
4. **Evidence-only scope drift 风险**：Evidence worker 需严格遵守不修改 code/tests 的约束。Plan 的 stop conditions（plan 第 207 行）和升级条件（plan 第 38-39 行）已覆盖。

## Controller May Proceed

**Yes.** Controller may proceed to dispatch evidence worker to execute E1-E4. Plan is handoff-ready.

Plan review 通过后，建议 controller：
1. 派发 evidence worker 执行 E1-E4。
2. Evidence worker 完成后派发 DS 和 GLM 进行 evidence review。
3. Review 通过后 controller 发出 judgment。

## Non-Goals Preserved

- No production code/tests were modified.
- No score, snapshot, quality gate, golden fixture, drawdown metric, Host/Agent/dayu, release, PR, push, merge, or promotion change occurred.
- No extractor direct source dependency was introduced.
- No runtime dependency was added.
