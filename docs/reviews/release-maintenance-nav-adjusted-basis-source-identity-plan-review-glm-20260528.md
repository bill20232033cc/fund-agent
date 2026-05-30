# NAV Adjusted-Basis Source Identity Gate — Plan Review (GLM)

日期：2026-05-28

角色：plan review worker (GLM)，非 controller、非 implementation worker。不写生产代码或测试，不修复 plan，不 commit、push、PR、merge、release 或 golden promotion。

Work unit：`NAV adjusted-basis source identity gate`

Review target：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`

## Verdict: **Accepted**

Plan 满足全部 review focus 要求，scope 边界严格，proof standard 可审计，fail-closed 语义充分。发现 3 条 findings（1 medium、2 informational），均不阻塞 accept。

## Truth Source Verification

本 review 独立读取并对照以下真源：

| 真源 | 核验内容 |
|------|---------|
| `AGENTS.md` | Gate 分类规则、模块边界、fail-closed 纪律、extra_payload 禁令、基金类型优先 |
| `docs/design.md` | §2.2 当前确定性执行链路、§6.2 P1 façade 与 `FundNavRepository.load_nav_series()` 契约、NAV adjusted basis 边界、failure taxonomy 对齐 |
| `docs/implementation-control.md` | Startup Packet current gate、next entry point、accepted artifacts、open residuals |
| NAV adjusted-basis contract controller judgment | 已接受的 typed NAV contract 方向、drawdown evidence boundary |
| Typed contract implementation controller judgment | 已实现的 `FundNavSeries` / `FundNavRecord` / `NavSourceMetadata` / `ShareClassMapping` |
| Aggregate deepreview DS/GLM | prior review 验证的 fail-closed taxonomy、raw_unit_nav 非强证据、legacy 兼容性 |
| snapshot.jsonl / score.json / quality_gate.json | `bond_risk_evidence.v1` contract_status=partial, weak_groups=[drawdown_stress], baseline_blocking=true |
| `nav_models.py` / `nav_repository.py` / `nav_data.py` | 当前 typed contract 实现、failure category Literal 域、repository normalization |

## Findings

### F-1 [medium] `insufficient_history` 与现有 taxonomy 存在术语间隙

Plan § Failure Taxonomy 列出 7 个 category，包含 `insufficient_history`。当前 `NavFailureCategory` Literal（`nav_models.py:53-62`）只有 `insufficient_records` 和 `missing_date_range`，无 `insufficient_history`。

Plan 在 Note 中已声明：如果需要 exact `insufficient_history`，必须 map 到现有 category 或开 minimal model taxonomy amendment。该声明本身正确，但 E1/E2 evidence artifact 在分类时需要明确使用现有 taxonomy term 还是新 term，避免 evidence artifact 与 typed model 之间的语义不一致。

**影响**：不阻塞。Evidence artifact 可以使用 `insufficient_history` 作为 evidence-level 诊断标签，后续 implementation gate 再决定是否需要新增 `NavFailureCategory` 值。但 controller 应在 evidence slice 指导中要求 reviewer 明确标注 evidence category 与 model category 的映射关系。

### F-2 [informational] E1 JS identity smoke 的变量值解析边界可更明确

Plan § Slice E1 Action 2 列出 public HTTP GET `pingzhongdata/{code}.js` 记录 `fS_code` / `fS_name` / 变量存在性。§ Candidate 2 Required inspection 明确说"如果解析 JS 变量内容，必须使用 structured JS parser...不得 brittle ad hoc regex 进入 production。Evidence-only regex 可以保留为 diagnostic。"

两处表述合在一起语义清晰，但 E1 actions 只说"变量存在性"，没有显式声明 E1 是否允许解析变量值（如 `Data_ACWorthTrend` 的具体数值序列）。建议 controller 在派发 E1 时明确：E1 只记录 identity header（`fS_code` / `fS_name`）和变量名存在性，不解析 `Data_ACWorthTrend` 等数值变量内容；数值变量的 cross-check 留给 E2。

**影响**：不阻塞。Plan Candidate 2 的 Required inspection 已充分约束 production 边界，E1 scope 由 controller 派发时可以补充。

### F-3 [informational] `累计收益率走势` 的 `period="成立来"` 参数未在 candidate 能力矩阵中显式论证

Plan § Direct Source Facts 记录 planning probe 使用 `indicator="累计收益率走势", period="成立来"` 返回了非空序列。但 Candidate 1 能力描述中没有讨论 `period` 参数的其他可能值（如 `"1年"` / `"3年"` 等），也没有讨论不同 `period` 值对 total-return candidate 语义的影响。

如果 `period="成立来"` 返回的累计收益率在数值上不等于 `累计净值走势` 的累计净值 / 单位净值 - 1 的增长率，则需要额外解释两者差异来源。这是 E2 的核心问题之一，plan 已正确地把 proof 留给 E2。

**影响**：不阻塞。Plan 已把 proof of semantics 归入 E2 必做项。

## Review Focus Checklist

### 1. Proof standard for accumulated_nav, dividend_adjusted_nav, total_return

**通过。** Plan § Proof Standard For Adjustment Basis 要求至少一条 primary proof + 一条 independent consistency check。

Primary proof options 覆盖了：
1. Provider documentation explicit definition
2. Source field semantics from official metadata
3. Official disclosure distribution events + provider series incorporation proof

Independent consistency checks 覆盖了：
1. Raw unit NAV vs adjusted divergence around dividend events
2. End-of-period reconciliation to annual report §3.2
3. Source identity match for same series

Mandatory block conditions 明确拒绝 column-name-only、no-identity、raw-equals-adjusted-with-known-distribution 等薄弱证据路径。

Accepted classifications 按强度排序：`total_return` / `dividend_adjusted_nav` > `accumulated_nav`（需额外 review）> `raw_unit_nav`（默认拒绝）。

该 proof standard 与 `AGENTS.md` "证据必须可溯源"原则一致，且不依赖 column name 推断 adjusted basis。

### 2. Current Akshare as raw-unit-only in production; public smoke as non-production evidence

**通过。** Plan 在多处明确区分：

- § Direct Source Facts § Current Code Facts 确认当前 Akshare path 只归一化为 `raw_unit_nav` / `not_adjusted` / `requested_code_only`。
- § Candidate 1 标记 `candidate-requires-proof`，`单位净值走势` 必须继续标为 raw unit NAV。
- § Non-Goals："不直接把 Akshare/public JS smoke 接入生产；smoke 仅能作为 evidence artifact 输入。"
- § Slice E1/E2 允许的文件仅限于 `docs/reviews/` evidence artifact。

Public smoke facts 声明为 "source evidence 输入，不是生产边界实现"。

### 3. A/C/E/F identity matrix prevents share-class mixing; avoids 006597 A as product-level substitute

**通过。** Plan § A/C/E/F Source Identity Plan 提供了完整矩阵：

| Code | Class | Identity rule |
|---|---|---|
| 006597 | A | verified only if source returns 006597 + A |
| 006598 | C | verified only if source returns 006598 + C |
| 014217 | E | verified only if source returns 014217 + E |
| 022176 | F | verified only if source returns 022176 + F |

规则 "Each fund code is its own series and share class. Never merge A/C/E/F by product name." 明确禁止 product-level 合并。

`share_class=None` 默认 A 只在 `fund_code=006597` 时允许，且必须保持 `requested_code_only` 直到 source identity verified。这防止了用 006597 A 作为整个产品 NAV 的替代。

### 4. E-class distribution case as blocker for raw unit NAV and mandatory cross-check

**通过。** Plan § Why E-Class Raw Unit NAV Is Not Strong Evidence 明确说明：

- E-class raw unit NAV across distribution periods 不能作为 strong evidence，因为 raw unit NAV 在现金分红时机械下跌，不反映投资者真实 total return。
- Prior accepted evidence 确认 E class 2023 distribution: 每 10 份 0.080。
- Planning smoke 显示 014217 的 `累计净值走势` 与 `单位净值走势` 在 2023-06 至 2023-09 窗口有差异。
- 若 accepted adjusted series for E，必须是 014217 E series（非 A/C/F），且 proof 必须包含 provider semantics + dividend-event cross-check。
- Raw unit NAV remains blocked even if adjusted series accepted。

这与 controller judgment "E-class raw unit NAV across the 2023 distribution period cannot be strong drawdown evidence" 完全一致。

### 5. NavSourceMetadata, ShareClassMapping, FundNavSeries at Agent/Fund data boundary without extractor/source-specific bypass

**通过。** Plan § Existing Typed Contract Fit 确认：

- `NavSourceMetadata` 已有 `source_name`, `origin_source`, `source_id`, `source_url`, `retrieved_at`, `cache_updated_at`, `requested_fund_code`, `returned_fund_code`, `returned_fund_name`, `failure_category`。
- `ShareClassMapping` 已有 requested/resolved code, share class, identity status, mapping evidence。
- `FundNavSeries` 已有 `nav_type`, `adjusted_basis`, `dividend_adjustment_status`, `identity_status`, `completeness_status`, `strong_drawdown_evidence_eligible`。
- Plan 结论：likely no new fields needed if source returns exactly one accepted series per call。
- Possible future schema slice 只在 3 个明确条件下触发，且要求 stop current implementation and open separate amendment。

所有 typed model 位于 `fund_agent/fund/data/nav_models.py`，repository 位于 `fund_agent/fund/data/nav_repository.py`，属于 Agent 层 Fund data 包。无 extractor 依赖、无 source-specific bypass。

### 6. Stop conditions and failure taxonomy strict enough

**通过。** Plan § Failure Taxonomy 列出 7 类：

| Category | Fallback |
|---|---|
| `not_found` | eligible |
| `unavailable` | eligible |
| `schema_drift` | fail-closed |
| `identity_mismatch` | fail-closed |
| `integrity_error` | fail-closed |
| `adjustment_basis_unknown` | fail-closed |
| `insufficient_history` | fail-closed for strong evidence |

这与 `AGENTS.md` 年报来源 fallback 策略语义对齐（`not_found`/`unavailable` eligible；`schema_drift`/`identity_mismatch`/`integrity_error` fail-closed），且新增了 `adjustment_basis_unknown` 作为本 gate 特有的 fail-closed category。

§ Stop Conditions 列出 7 个立即停止条件，terminal outputs 只有 `accepted-source-basis-candidate` 和 `blocked-with-source-gap`。没有隐含的 "弱接受" 路径。

注：`insufficient_history` 与现有 `NavFailureCategory` 的术语间隙见 F-1，plan 已声明需 mapping 或 amendment，不构成阻塞。

### 7. Plan avoids drawdown metric implementation and score/snapshot/quality gate/golden fixture changes

**通过。** Plan 在多处明确排除：

- § Non-Goals："不解除 drawdown_stress blocker"、"不把 raw unit NAV 或年报'控制回撤'文字视为 quantitative strong evidence"。
- § Goal："本 gate 的唯一成功输出是 source identity / adjusted basis 的可接受性裁决和后续最小实现入口。即使找到候选 adjusted / total-return 序列，也不得在本 gate 实现 max drawdown、volatility 或解除 blocker。"
- § Allowed Files By Outcome：evidence-only gate 和 future implementation gate 清晰分离；always disallowed 包含 snapshot、score、quality gate、golden fixtures、bond extractor、Host/Agent/dayu、release/PR。
- § Validation Matrix：evidence-only 不需要 full ruff / full pytest。

Plan 没有任何 drawdown metric 计算逻辑、score 字段修改、quality gate 语义变更或 golden fixture 操作。

### 8. Validation and artifact requirements sufficient

**通过。** Plan § Validation Matrix 按三类场景分层：

1. **Evidence-only**：只需 git branch/status、source smoke commands、artifact review。不要求 ruff/pytest。
2. **Tests added/changed**：focused ruff + focused pytest。
3. **Production code changed（future gate）**：full ruff + full pytest + real smoke + explicit assertions。

§ Allowed Files By Outcome 区分了 evidence-only gate 和 future implementation gate 的可修改文件范围。

§ Review Requirements 要求 DS + GLM 两个独立 plan review，review focus checklist 覆盖全部关键关注点。

## Residual Risks

1. **`insufficient_history` 术语映射**（见 F-1）。Evidence artifact 可能使用与 typed model 不同的 category name。Controller 应在 evidence slice 指导中要求显式映射。
2. **Source probe 可用性受限于 akshare 版本和网络环境**。E1 在 akshare API 不可用时应记录 `unavailable`，不安装新依赖。
3. **Eastmoney JS 结构可能变化**。E1 只记录当前快照；production implementation 需要更稳定的 source contract。
4. **`累计收益率走势` 的 `period` 参数语义**（见 F-3）。不同 `period` 值可能导致不同语义的累计收益率，E2 需要明确。
5. **022176 F 成立期短**。Plan 已预期 `insufficient_history`，但仍可能影响 F class 的 identity proof 可行性。

## Controller Proceed Statement

Controller **可以** proceed to evidence slice E1/E2。Plan 为 evidence slices 提供了：

- 明确的 allowed files 范围（仅 `docs/reviews/` evidence artifact）
- 明确的 smoke matrix（A/C/E/F 四个 code × 三类 indicator × JS identity）
- 明确的 proof standard（primary proof + independent check）
- 明确的 stop conditions（无 primary proof → stop）
- 明确的 terminal outputs（`accepted-source-basis-candidate` 或 `blocked-with-source-gap`）

E1 scope 建议补充：JS identity smoke 只解析 `fS_code` / `fS_name` header，不解析 `Data_ACWorthTrend` 等数值变量内容（见 F-2）。

## Conclusion

Plan 是一个 well-scoped、evidence-only gate handoff。Proof standard 不从 column name 推断 adjusted basis，A/C/E/F identity 规则禁止 share-class mixing，E-class distribution 正确标记为 raw unit NAV blocker，failure taxonomy 保持 fail-closed，没有 drawdown 实现或 score/snapshot/quality/golden 变更泄漏。

**Verdict: Accepted**

Controller 可 proceed to evidence slice E1/E2。
