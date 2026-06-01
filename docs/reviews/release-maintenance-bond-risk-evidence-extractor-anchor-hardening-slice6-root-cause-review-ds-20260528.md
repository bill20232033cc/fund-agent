# Bond Risk Evidence Extractor / Anchor Hardening — Slice 6 Root-Cause Review (DS)

> Date: 2026-05-28
> Role: Gateflow review worker DS
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: Slice 6 real `006597` / `2024` validation failure root-cause review
> Review type: root-cause analysis (no code changes, no file modifications)
> Status: complete

## Worker Self-Check

- Self-check: pass
- Role confirmed: review worker DS only; not controller, not implementer.
- Scope confirmed: root-cause review of the 2026-05-28 `006597`/2024 run artifacts. No code changes, no file modifications, no implementation, no staging, no commit, no PR, no golden promotion.
- Truth sources read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, plan artifact, Slice 5 controller judgment.
- Real outputs read: snapshot.jsonl, score.json, score.md, quality_gate.json, quality_gate.md from run `bond-risk-evidence-006597-2024-20260528`.

## Real Output Summary

### Snapshot (17 records, 1 fund)

`bond_risk_evidence` row (line 15):

| Field | Actual Value |
|---|---|
| `extraction_mode` | `estimated` |
| `value_present` | `true` |
| `anchor_present` | `true` |
| `bond_risk_contract_status` | `partial` |
| `bond_risk_satisfied_groups` | `duration_rate_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `convertible_bond_equity_exposure` |
| `bond_risk_missing_groups` | (empty) |
| `bond_risk_weak_groups` | `credit_risk`, `drawdown_stress` |
| `bond_risk_ambiguous_groups` | `redemption_share_pressure` |

First-anchor projection: `section_id=§2`, `page=null`, `table_id=null`, `row_id=line:21` — weak projection but structured fields carry authoritative state.

### Score

`score_applicability_issues` has 1 `bond_risk_evidence_missing` issue:
- `baseline_blocking`: `true`
- `missing_evidence_groups`: `["credit_risk", "drawdown_stress", "redemption_share_pressure"]`
- `required_evidence_groups`: all 7 (correct)
- `bond_risk_evidence` field score: coverage 100%, traceability 100%, status `pass` (P1)
- `p1_status`: `fail` (due to unrelated `turnover_rate`, `holder_structure`, `share_change`)

### Quality Gate

Status: `warn`, 7 issues:
- FQ2 ×3 (turnover_rate, holder_structure, share_change — unrelated P1 gaps)
- FQ2F (P1 failures aggregation — unrelated)
- FQ0 info (golden answer not configured — expected)
- FQ4 warn (28.6% missing rate > 20% — driven by unrelated P1 gaps)
- FQ2F warn (`bond_risk_evidence_missing`, `reason=bond_risk_evidence_missing`)

No FQ1 (correctness mismatch), no FQ3 (P0 anchor gap), no FQ6 (extraction failure). FQ0-FQ6 semantics unchanged from Slice 5.

## Question 1: Blocker 是否仍存在

**是。** `bond_risk_evidence_missing` issue 仍然存在于 score 和 quality gate 中，`baseline_blocking=true`。

但 blocker 已从「全部 7 组缺失」缩小为「3 组未满足」：`credit_risk`(weak)、`drawdown_stress`(weak)、`redemption_share_pressure`(ambiguous)。这是 Slice 5 设计意图的正确表现——partial contract 只对未满足组保持阻断，已满足的 4 组不再出现在 `missing_evidence_groups` 中。

**结论：blocker 存在但范围正确收缩。非 regression，是 partial contract 的预期行为。**

## Question 2: 三个未满足组的根因分析

### 2.1 `credit_risk` — weak

**根因：extractor 未命中评级分布表定量数据。**

证据链：
- 已接受的 evidence artifact（`bond-positive-risk-evidence-20260527.md`）明确记录：006597/2024 年报包含「中高等级信用策略、严格信用风险控制」文字，以及「短期债券、长期债券、ABS 等的评级分布表」。
- Plan Slice 2 明确要求：当评级分布表行存在时，`strength="quantitative_direct"`，`measurement_kind="actual_exposure"`，「定性策略文字单独不应作为唯一已接受证据」。
- 实际输出 `credit_risk` 为 `weak`，说明 extractor 未能将评级分布表解析为可规则化抽取的定量证据，只捕获了策略描述文字。

**判定：extractor 未命中，非证据不足、非 contract 太严、非 score policy 错误。** 年报中有评级分布表，但 extractor 的表格定位/解析/行提取逻辑未能产出 `quantitative_direct` 级证据。这是 extractor hardening 问题。

### 2.2 `drawdown_stress` — weak

**根因：真实证据不足——年报不含最大回撤或波动率量化指标。**

证据链：
- 已接受的 evidence artifact 记录：006597/2024 年报仅有「定性回撤控制意图」（如「控制回撤」措辞），无最大回撤数值、无波动率指标。
- Plan Slice 2 明确决策：`drawdown_control_intent` alone → `status="weak"`, `strength="qualitative_control_intent"`，不满足 required group。只有 `max_drawdown_metric`、`volatility_metric` 或 accepted direct stress metric 才能满足。
- Controller judgment 确认：safe option is selected，弱定性回撤文本不足。

**判定：真实证据不足，contract 正确执行了设计意图，非 extractor 错误、非 score policy 错误。** 这是 plan 已预见的 safe outcome——弱证据不应伪装为强证据。年报本身不提供 max drawdown / volatility 量化披露，无法通过 extractor hardening 解决。

### 2.3 `redemption_share_pressure` — ambiguous

**根因：extractor 多份额类别选择逻辑未能确定性解析 A 份额。**

证据链：
- Plan Slice 2 要求：`status="accepted"` only when share-class selection is deterministic or all-class aggregation is explicitly labelled。Ambiguous class selection → `status="ambiguous"`，不满足 group。
- Plan 建议：target A share selection can use same-report §2 subordinate fund code/name evidence plus §10 share-change columns。
- 实际 snapshot 中 `share_change` 字段（line 15）note 为：「§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别」。
- `bond_risk_evidence` 中 `redemption_share_pressure` 被标记为 `ambiguous`，与 share_change extractor 的多份额困境一致。

**判定：extractor 未命中。** 年报中有持有人结构表和 §10 多份额变动表数据，数据存在但 extractor 的份额类别消歧逻辑未成功执行。§2 的从属基金代码/名称证据可能未被正确关联到 §10 列选择。这是 extractor hardening 问题，非证据不足、非 contract 太严。

### 2.4 汇总

| 未满足组 | 根因类别 | 年报证据存在？ | 可通过 extractor hardening 修复？ | 需改 contract？ |
|---|---|---|---|---|
| `credit_risk` | extractor 未命中（评级分布表） | 是 | 是 | 否 |
| `drawdown_stress` | 真实证据不足（无量化指标） | 否（仅有定性意图） | 否 | 否 |
| `redemption_share_pressure` | extractor 未命中（多份额消歧） | 是 | 是 | 否 |

## Question 3: 是否可在不削弱 FQ0-FQ6、不伪装弱证据的情况下继续修

**可以。** 两个可修组（credit_risk、redemption_share_pressure）的修复路径不涉及任何 contract 削弱：

### credit_risk 修复路径

- 在 `_extract_credit_risk()` 中增加评级分布表的定位和解析逻辑。
- 从 `ParsedAnnualReport.tables` 中找到信用评级分布相关表格（关键词：信用评级/评级分布/AAA/AA+/长期/短期）。
- 提取行级数据并产出 `quantitative_direct` 证据，带 `section_id`、`page_number`、`table_id`、`row_locator`。
- 不改变 contract：`quantitative_direct` + rating distribution → `accepted`，该逻辑 plan 已定义。
- 不削弱：当前 weak → 修复后 accepted（quantitative_direct），是 extractor 更准确，不是门槛降低。

### redemption_share_pressure 修复路径

- 在 `_extract_redemption_share_pressure()` 中实现 §2 从属基金代码/名称 → §10 份额列的确定性消歧。
- 或者实现全份额汇总（all-class total）并显式标注 `all_classes_total`。
- 不改变 contract：确定性选择或显式标注 → `accepted`，ambiguous → 不满足，该逻辑 plan 已定义。
- 不削弱：当前 ambiguous → 修复后 accepted（quantitative_direct），是消歧逻辑正确，不是门槛降低。

### drawdown_stress 不可修

- 年报不含 max drawdown / volatility 量化披露。
- 将定性回撤意图升级为 accepted 会 **直接违反 plan 决策**：`drawdown_control_intent` alone is weak and does not satisfy。
- 唯一合规路径：从外部净值序列计算 max drawdown 并带 source anchor，但这超出当前 extractor 范围（extractor 只消费 ParsedAnnualReport，不接入 NAV 计算器）。
- 建议：接受 drawdown_stress 在 v1 中保持 weak，将 max drawdown 计算作为后续独立 gate（需要 NAV 计算器接入 + source anchor 契约）。

### 不变式验证

以下不变式在修复后必须保持：

- FQ0-FQ6 阈值、严重级别、规则语义不变（当前已保持，修复只改变 extractor 输出质量）。
- 弱/歧义证据不升级为 satisfied（credit_risk/redemption 修复后是找到更强的真实证据，不是把弱证据重标记）。
- `baseline_blocking=true` 对任何未满足组保持。
- `required_evidence_groups` 始终为全部 7 组。
- 无 golden corpus promotion、无 baseline promotion、无 Host/Agent/dayu、无 Service/UI 变更。

## Question 4: 推荐 Next Gate/Slice 和必须测试

### 推荐：Slice 6 Amendment — Extractor Hardening（credit_risk + redemption_share_pressure）

不做新 slice 编号，作为 Slice 6 的修正轮次。范围严格限定：

**修改文件（同 plan Slice 2 范围）：**
- `fund_agent/fund/extractors/bond_risk_evidence.py` — `_extract_credit_risk()` 和 `_extract_redemption_share_pressure()` 逻辑增强
- `tests/fund/extractors/test_bond_risk_evidence.py` — 新增 + 更新测试

**不修改：**
- 任何 contract / schema / Literal type / model
- score applicability 逻辑
- snapshot projection 逻辑
- quality gate
- 其他 5 个 group extractor

### 必须测试（按优先级）

**P0 — 阻断级（不通过不能 accept）：**

1. **credit_risk 评级分布表提取**：用 006597/2024 真实 `ParsedAnnualReport`（或结构等价的 synthetic table fixture），验证 `_extract_credit_risk()` 产出 `status="accepted"`, `strength="quantitative_direct"`, `measurement_kind="actual_exposure"`，且至少有一个带 `section_id/page/table_id/row_locator` 的 anchor。

2. **redemption_share_pressure 多份额消歧**：用包含 §2 从属代码/名称 + §10 多份额列的真实或 synthetic fixture，验证 A 份额被确定性选择（或 all-class 显式标注），产出 `status="accepted"`, `strength="quantitative_direct"`。Ambiguous 场景（无 §2 消歧证据）必须保持 `ambiguous`。

3. **drawdown_stress 不回退**：验证仅有定性回撤文本时仍产出 `status="weak"`, `strength="qualitative_control_intent"`，不出现在 satisfied_groups 中。

**P1 — 回归级：**

4. **已满足 4 组不回退**：`duration_rate_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `convertible_bond_equity_exposure` 仍为 satisfied。

5. **完整 006597/2024 链路**：`extraction-snapshot` → `extraction-score` → `quality-gate`，验证 score 的 `missing_evidence_groups` 只含 `drawdown_stress`（如 credit_risk + redemption 修复成功），或最多 `["credit_risk", "drawdown_stress", "redemption_share_pressure"]`（如部分修复）。

6. **FQ0-FQ6 语义不变**：quality gate 规则码、严重级别、阈值与 Slice 5 基线一致。

7. **ruff + pytest 通过**：`uv run ruff check .` 零错误，`uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` 通过。

### 不接受的结果

- 为修复 credit_risk 而降低 contract 要求（如接受 qualitative strategy text 作为 satisfied）。
- 为修复 redemption_share_pressure 而在无消歧证据时强行选择份额类别。
- 将 drawdown_stress 从 weak 升级为 satisfied（除非有量化 max drawdown/volatility + source anchor）。
- 修改 score applicability 逻辑或 quality gate 规则。
- 任何 golden corpus / baseline promotion。

## 附加发现

### F1: `extraction_mode` 偏差

Plan Slice 1 定义了三种 extraction_mode：`direct`（全部满足）、`partial`（部分满足）、`missing`（全不满足）。实际输出为 `estimated`，不在 plan 定义的三种模式中。

- **严重度**：低。不影响 score/quality gate 判断（score 消费的是结构化 bond_risk_* 字段，不依赖 extraction_mode）。
- **建议**：修复轮次中将 extraction_mode 改为 `partial`，与 contract_status 一致。

### F2: leverage_liquidity 被满足需验证

Plan 对 leverage_liquidity 的要求严格：「Flexible leverage strategy text alone must be `weak`」「implementation must normalize precise table/row anchors before treating this group as accepted」。当前 `leverage_liquidity` 在 satisfied_groups 中，说明 extractor 声称找到了精确表/行锚点。

- **建议**：修复轮次中显式验证 leverage_liquidity 的 anchor 是否为 row-level（非 broad page range），并在测试中记录实际锚点内容。如仅有宽泛页面引用，应降级为 weak。

### F3: 质量门控消息未更新

Quality gate FQ2F issue message 仍为静态模板「`bond_risk_evidence.v1` 尚无已复核债券风险证据」，未反映 partial contract 动态状态（4 satisfied / 2 weak / 1 ambiguous）。

- **严重度**：低（消息是给人看的，不影响 machine semantics）。score.json 的结构化字段 `missing_evidence_groups` 是准确的。
- **建议**：非阻塞，可在后续文档/消息 cleanup gate 中处理。

### F4: 与 Slice 5 预期对比

Slice 5 controller judgment 列出了 deferred residuals：
- 「Per-group anchor validation remains outside Slice 5」— 此 residual 在 Slice 6 中仍然 open。snapshot 只暴露 field-level anchor_present，不暴露 per-group anchor booleans。
- 「Multiple same-fund same-year bond_risk_evidence rows fail closed」— 当前 run 只有 1 row，未触发。

## 结论

1. **Blocker 仍存在**，但已正确收缩为 3/7 组未满足（credit_risk weak, drawdown_stress weak, redemption_share_pressure ambiguous），非 regression。

2. **三个未满足组的根因**：
   - `credit_risk`: **extractor 未命中**评级分布表（年报有数据，extractor 未捕获为 quantitative）
   - `drawdown_stress`: **真实证据不足**（年报无 max drawdown / volatility 量化披露，plan 正确将其保留为 weak）
   - `redemption_share_pressure`: **extractor 未命中**多份额消歧（年报有数据，§2→§10 关联逻辑未成功）

3. **可以不削弱任何 contract 继续修**。credit_risk 和 redemption_share_pressure 的修复是 extractor 更准确找到已存在的证据，不是降低门槛。drawdown_stress 应保持 weak，不可伪装。

4. **推荐 Slice 6 Amendment**：extractor hardening for credit_risk + redemption_share_pressure，附带必须测试清单和明确的不可接受结果列表。修复后最佳预期：missing_evidence_groups 只剩 drawdown_stress（1/7），baseline_blocking 仍为 true（因为仍有未满足组）。

## Review Signature

- Reviewer: DS (Gateflow review worker)
- Review type: root-cause analysis
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-root-cause-review-ds-20260528.md`
- Verdict: **PASS_WITH_FINDINGS** — extractor hardening needed for credit_risk and redemption_share_pressure; drawdown_stress is correctly weak; proceed to amendment round with specified tests and stop conditions.
