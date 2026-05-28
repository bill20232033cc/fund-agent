# NAV Adjusted-Basis Source Identity Gate — Evidence Review (GLM)

日期：2026-05-28

角色：evidence review worker (GLM)，非 controller、非 implementation worker。不修改 evidence、code 或 tests，不 commit/push/PR。

Work unit：`NAV adjusted-basis source identity gate`

Review target：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`

Accepted plan：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`

## Verdict: **Accepted**

Evidence 满足 accepted plan 的 proof standard，E-class cross-check 数学精确，failure 分类正确，scope 无越界。发现 3 条 findings（1 low、2 informational），均不阻塞 accept。

## Truth Source Cross-Check

本 review 独立对照以下真源：

| 真源 | 核验内容 |
|------|---------|
| `AGENTS.md` | 证据可溯源原则、fail-closed taxonomy、extra_payload 禁令 |
| `docs/design.md` | `FundNavRepository.load_nav_series()` 契约、NAV adjusted basis 边界 |
| `docs/implementation-control.md` | 当前 gate 状态、drawdown_stress blocker 未解除 |
| Prior controller judgments (×2) | typed contract 方向、drawdown evidence boundary |
| `nav_models.py` | `NavFailureCategory` Literal 域、`DividendAdjustmentStatus` 域、`NavType`/`AdjustmentBasis` 兼容矩阵 |
| Accepted plan | Proof standard（primary proof + consistency check）、E1/E2 边界、failure taxonomy、output options |

## Findings

### F-1 [low] A/C accumulated_nav 接受依赖从 E-class 行为的传递论证

**位置**：Evidence §Candidate Disposition Matrix — `累计净值走势` A/C 行（artifact L239-240）

**观察**：

E-class cross-check 是本 evidence 的核心 primary proof（plan Primary proof option 3）：official disclosure 提供分红事件，provider series 在精确日期展现出方向和量级完全一致的 divergent behavior（0.0080 per share）。这是强证明。

A/C 的接受逻辑是传递性的：
1. E-class 证明 `Data_ACWorthTrend` 对 014217 表现为 additive accumulated NAV。
2. A/C 使用同一 provider、同一 API 函数、同一变量名，只是 symbol 参数不同。
3. 年报 §3.3 和 provider page 确认 A/C 无分红。
4. A/C 的 accumulated = unit NAV，与"无分红"一致。

该传递论证合理——同 provider 同变量在不同 symbol 下通常保持一致语义。且 consistency check #1（divergence = expected distribution amount）对 A/C 成立（zero distributions → zero divergence）。

但 plan 的 proof standard 要求每个被接受的 class 至少满足 "at least one primary proof plus one independent consistency check"。严格来说，A/C 的 primary proof 不是独立于 E 的——它依赖于 E-class 对变量语义的证明。如果 plan 要求 per-class primary proof，A/C 可能需要额外论证。

**判定**：不阻塞。因为 (a) 同 provider 同变量的语义一致性是合理的工程假设，(b) consistency check（zero divergence = zero distributions）对 A/C 独立通过，(c) 年报和 provider page 的 zero-distribution 证据是独立于 E-class cross-check 的。但 implementation gate 应在 adapter normalization plan 中确认此传递性假设是否需要额外的 per-class smoke 验证。

### F-2 [informational] A/C accumulated = unit 的行级相等性仅通过 first/last sample 验证

**位置**：Evidence §E1 Smoke Matrix A/C 行（artifact L116-118, L127-129）

**观察**：

Evidence 报告 A/C 的 `单位净值走势` 和 `累计净值走势` 的 first 和 last 值完全一致，但未显式证明全部 1809 行都相等。在 confirmed zero distributions 条件下，first/last 匹配几乎可以确定全部行相等，但严格数学证明需要 row-by-row 检查或 `max(abs(accumulated - unit)) == 0` 断言。

**判定**：不阻塞。有年报 §3.3 "past three years no profit distribution" 和 provider page "dividend count 0, split count 0" 的双重官方证据，first/last 匹配已足够支持 evidence-level 接受。Future implementation gate 可在 adapter normalization 中加入 programmatic row-level equality check。

### F-3 [informational] `dividend_adjustment_status` 值的精确语义需在 implementation gate 确定

**位置**：Evidence §Candidate Disposition Matrix `累计净值走势` A/C 行的 `dividend_adjustment_status`（artifact L239-240）

**观察**：

Evidence 将 A/C 的 `dividend_adjustment_status` 标记为 "adjusted for cash distributions; no distribution observed"。当前 typed model `DividendAdjustmentStatus` Literal 域为 `not_adjusted | adjusted | unknown | not_applicable`。

对于 A/C（无分红发生），语义上存在两种解读：
- `adjusted`：series 是 prepared to incorporate distributions 的 accumulated NAV，只是实际无分红发生。
- `not_adjusted`：因为没有实际调整发生，所以 "not adjusted"。

当前 `raw_unit_nav` 路径硬编码 `not_adjusted`，但那是完全不同的语境（unit NAV 从不调整）。Accumulated NAV 的语义是"会调整"，即使当前窗口无分红。这个精确值的选择不影响 evidence acceptance，但应在 implementation gate 中通过 review 确定。

**判定**：不阻塞。Evidence 正确描述了 series 的语义行为；精确 `DividendAdjustmentStatus` 值是 implementation gate 的决策范畴。

## Review Focus Checklist

### 1. Proof standard for accumulated_nav; avoid accepting total_return/dividend_adjusted without proof

**通过。**

Primary proof 满足 plan option 3（official disclosure + provider series incorporation proof）：
- 年报 §3.3 提供分红事件和金额（E class every 10 shares 0.080）。
- Provider page 提供精确 ex-date（2023-01-11）。
- `Data_ACWorthTrend` 在 ex-date 当天展现精确 0.0080 per-share divergence（unit NAV 1.1252 vs accumulated NAV 1.1332），方向和量级完全匹配。

Independent consistency checks 满足至少 2 条：
- Check #1：raw unit NAV vs accumulated divergence = expected distribution amount（0.0080 exactly）。
- Check #3：`fS_code` = requested code, `fS_name` includes correct share-class suffix。

未接受的候选：
- `累计收益率走势` / `LJSYLZS` 正确分类为 `adjustment_basis_unknown`：无 source-owned semantics 定义其为 total-return 或 dividend-reinvested series。
- `dividend_adjusted_nav` 未对任何 class 声称接受。
- `total_return` 未对任何 class 声称接受。

Evidence §What Was Not Proven 显式声明了两项未证明内容。

### 2. Source identity proof binds exact source series to exact share-class code/name

**通过。**

四个 code 的 Eastmoney JS identity 完整且一致：

| Code | fS_code | fS_name | Share-class suffix |
|---|---|---|---|
| 006597 | "006597" | "国泰利享中短债债券A" | A ✅ |
| 006598 | "006598" | "国泰利享中短债债券C" | C ✅ |
| 014217 | "014217" | "国泰利享中短债债券E" | E ✅ |
| 022176 | "022176" | "国泰利享中短债债券F" | F ✅ |

满足 plan A/C/E/F identity matrix 全部要求。`fS_code` 严格等于 requested code，`fS_name` 包含正确的份额类别后缀。无 identity mismatch。

### 3. No overclaim when A/C accumulated equals unit NAV due to no distributions

**通过（见 F-1、F-2）。**

Evidence 的 A/C 接受逻辑未 overclaim：
- 未声称 A/C accumulated_nav 提供与 unit_nav 不同的值。
- 明确标注 "accumulated equals unit NAV for the observed range"。
- 明确标注 "no distribution observed"。
- Annual report §3.3 "past three years no profit distribution" + provider page "dividend count 0" 双重确认。

接受的是 source/basis identity candidate（"这个 series 是 accumulated_nav 语义"），而非声称该 series 在当前窗口提供了超越 unit_nav 的额外 drawdown 信息。这是正确的 scope。

### 4. E-class distribution cross-check mathematical and evidential sufficiency

**通过。**

Cross-check 满足 plan 全部四项 proof 条件：

1. **精确日期**：provider page 给出 `2023-01-11`，不是 window-based fallback。满足 plan E2 Action 3（优先 exact date）。
2. **Divergence 方向**：unit NAV 在 ex-date 下降（1.1332 → 1.1252），accumulated NAV 保持（1.1332 → 1.1332）。正确：accumulated NAV 不受分红 drop 影响。
3. **Divergence 量级**：0.0080 per share，精确匹配年报 every 10 shares 0.080 = every share 0.0080。4 位小数完全一致。
4. **持续性**：Divergence 从 2023-01-11 持续到至少 2023-12-31（artifact L213，difference = 0.0080），表明 accumulated NAV 正确保留了分红金额。

数学精度排除了巧合解释。

### 5. F partial acceptance and insufficient_history → missing_date_range mapping

**通过。**

F class (022176) 处理正确：
- 历史从 2024-10-08 开始，398 rows。
- Accept for source-inception-forward candidate windows only。
- Block for 2023 and any pre-2024-10-08 window。
- `insufficient_history` → model `missing_date_range` 映射符合 plan Failure Taxonomy Note 的要求。
- 年报 §3.3 确认 F class "no profit distribution since the share class was added"。

Plan 的 Completion Report Format 要求记录 "evidence-level insufficient_history mapping, if any"，evidence 在 §Recommended Decision Insufficient classes/windows 中满足。

### 6. Failure classifications strict enough

**通过。**

| 失败分类 | 适用场景 | 严格性 |
|---|---|---|
| `adjustment_basis_unknown` | `LJSYLZS` / `累计收益率走势` 对全部 4 个 class | 正确：无 source-owned semantics |
| `insufficient_history` → `missing_date_range` | F class pre-inception windows | 正确：398 rows 不覆盖 2023 |
| 无 `schema_drift` | Source response shape 未偏离已知契约 | 正确：所有 API 返回预期 columns |
| 无 `identity_mismatch` | fS_code/fS_name 全部匹配 | 正确 |

`schema_drift`、`identity_mismatch`、`integrity_error` 保持 fail-closed 语义，未被 evidence 弱化。

### 7. No drawdown implementation, blocker解除, score/snapshot/quality/golden changes

**通过。**

Evidence §Non-Goals Preserved 显式声明 7 项未变更：
- `drawdown_stress` blocker remains unchanged。
- `raw_unit_nav` remains not strong evidence。
- No max drawdown or volatility implemented。
- No production code/tests modified。
- No score/snapshot/quality gate/golden/bond extractor/Host/Agent/dayu/release changes。

Evidence 未包含任何 drawdown 计算、score 字段修改或 quality gate 语义变更。Validation section 正确跳过 ruff/pytest（docs/reviews-only artifact）。

## Scope Boundary Verification

| Plan 约束 | Evidence 是否遵守 |
|---|---|
| E1 JS smoke 只解析 fS_code/fS_name 和变量存在性 | **是** — artifact L19 和 L68 显式声明 |
| E2 数值 cross-check 使用 Akshare API + FundDocumentRepository | **是** — 年报通过 repository 读取 |
| 只新增 docs/reviews evidence artifact | **是** — preflight 确认 |
| 不修改 production code/tests | **是** — validation section 确认 |
| `accumulated_nav` 不等于 drawdown suitability 接受 | **是** — L244 显式声明 "Future drawdown suitability still needs a separate reviewed metric contract" |
| `partial-acceptance-with-blocked-classes` 正确使用 plan output option | **是** — blocked classes/windows 显式列出 |

## Residual Risks

1. **A/C accumulated_nav 传递性假设**（F-1）：E-class 证明 `Data_ACWorthTrend` 语义后传递到 A/C，未 per-class 独立验证 divergence。Implementation gate 应决定是否需要 per-class programmatic equality check。
2. **`dividend_adjustment_status` 精确值**（F-3）：A/C 无分红下的 "adjusted" vs "not_adjusted" 选择留给 implementation gate。
3. **`accumulated_nav` 非 total-return**：Evidence 正确标注 limitation。Future drawdown metric gate 需独立裁决 accumulated_nav 的 drawdown suitability（additive cash-distribution accumulated NAV 可能不适合直接计算 total-return drawdown，因为 cash distribution 部分未 reinvested）。
4. **Provider page 作为 evidence**：天天基金 fund pages 和 help page 是 provider-owned metadata，可作为 plan primary proof option 2 的输入。但这些 pages 无版本化 contract，未来可能变化。Implementation gate 的 adapter normalization 应考虑 cache/schema-drift 检测。
5. **F class 历史长度**：398 rows（约 1.5 年）可能不足以支持有意义的 max drawdown 计算。此风险不在本 gate scope 内，但 evidence 已正确 block pre-inception windows。
6. **`LJSYLZS` row count 差异**：A/C 202 rows vs 1809 daily NAV rows, E 250 rows vs 994 rows。即使未来 semantics 被证明，低频采样可能限制 path metric 可用性。Evidence 正确 block。

## Controller Proceed Statement

Controller **可以** accept evidence 并 move to controller judgment。

Evidence 满足 accepted plan 的 proof standard：
- E-class exact-date cross-check 数学精确（4 位小数匹配）。
- Source identity 通过 JS `fS_code` / `fS_name` 完整验证。
- A/C/F 通过传递论证 + zero-distribution 确认合理接受。
- `累计收益率走势` / `LJSYLZS` 正确 block 为 `adjustment_basis_unknown`。
- F class pre-inception 正确 block 并映射到 `missing_date_range`。
- Terminal result `partial-acceptance-with-blocked-classes` 正确使用 plan output option。
- 无 drawdown implementation、blocker解除、score/snapshot/quality/golden 变更。

No required fix. 3 条 findings 均为 low/informational，可在后续 implementation gate 中处理。

## Validation

本 review 未修改任何 production code、test、schema、score、snapshot、quality gate 或 golden fixture。未执行 ruff/pytest（docs/reviews-only artifact）。
