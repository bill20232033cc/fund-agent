# NAV Adjusted-Basis Source Identity Gate — Plan Re-Review (GLM)

日期：2026-05-28

角色：re-review worker (GLM)，非 controller、非 implementation worker。不修改 plan、code 或 tests，不 commit/push/PR。

Work unit：`NAV adjusted-basis source identity gate`

Re-review target：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`（post-fix 版本）

## Verdict: **Accepted**

四项 fix 全部正确应用。Prior findings F-1 至 F-3（GLM）和 F1 至 F4（DS）均已关闭或经 fix 充分处理。无新增 blocking finding。

## Per-Fix Verification

### Fix 1: E-class exact ex-date missing fallback

**状态：已修复，通过。**

更新后 plan §Slice E2 Actions items 3-5 构成完整的三层策略：

1. **Item 3**：优先从 official disclosure 获取 exact distribution date/range（通过 `FundDocumentRepository`）。
2. **Item 4**：若精确日期不可得，window-based divergence check 必须同时满足四项前置条件：
   - provider/source semantics primary proof 已通过（非单独靠 window check 兜底）；
   - window 可追溯至 official disclosure 或 `FundDocumentRepository` 证据（如披露年度/期间和份额类别分红金额）；
   - divergence 方向和近似量级与 distribution amount 一致；
   - evidence artifact 记录不确定性、所选窗口、来源锚点、预期效应和观察效应。
3. **Item 5**：若既无精确日期也无 defensible official window，fail closed 为 `adjustment_basis_unknown`。

§Proof Standard Mandatory block conditions 同步更新为 "Cross-check cannot identify either an exact ex-dividend date or a defensible distribution window"，与三层策略一致。

**对照 DS F1**：DS 建议 "若年报未披露精确 ex-date，接受 window-based divergence check（季度窗口），条件是 divergence 方向与分布金额一致且 source semantics proof 已通过"。Fix 实现了该建议，且额外增加了 official traceability 约束和 uncertainty 记录要求，比建议更严格。正确。

### Fix 2: Output options include partial-acceptance-with-blocked-classes

**状态：已修复，通过。**

更新后 plan 三处新增 `partial-acceptance-with-blocked-classes`：

1. **§Slice E2 Output options**：新增第三项，明确定义为 "at least one share class passes source/basis/identity proof while other classes remain blocked"，并要求 cross-reference `share classes covered` 和 `insufficient classes/windows`。
2. **§Stop Conditions Terminal outputs**：同步新增，要求 "blocked classes/windows stay fail-closed and must be listed"。
3. **§Completion Report Format Decision 行**：包含该选项。

这消除了 DS F2 指出的 "Output options 暗示二元结果" 的歧义。Partial acceptance 不等于弱接受——blocked classes 保持 fail-closed。

### Fix 3: insufficient_history maps to current model terms

**状态：已修复，通过。**

更新后 plan 四处显式处理 `insufficient_history` 到现有 taxonomy 的映射：

1. **§Failure Taxonomy Note**：声明 `insufficient_history` 为 evidence-level diagnostic label only；要求每个使用该标签的 E1/E2 evidence artifact 同时记录 current model mapping（`model_category="insufficient_records"` 或 `model_category="missing_date_range"`）。
2. **§Slice E2 Accept criteria**：`insufficient_history` 分类时显式映射到 `insufficient_records` 或 `missing_date_range`。
3. **§Slice E3 potential tests**：022176 insufficient lookback -> current model `insufficient_records` 或 `missing_date_range`；如需 exact `insufficient_history`，先开 model taxonomy amendment。
4. **§Completion Report Format**：新增 "evidence-level insufficient_history mapping, if any" 字段。

这消除了 GLM F-1 的术语间隙风险，同时保留了 evidence-level 诊断灵活性。

### Fix 4: E1 JS identity smoke only parses fS_code/fS_name and variable presence

**状态：已修复，通过。**

更新后 plan 两处明确约束 E1 JS smoke 边界：

1. **§Candidate 2 Required inspection**：新增显式段落——"E1 identity smoke 只能用 public HTTP GET 读取...JS header、fS_code、fS_name 和变量名存在性"；"E1 不解析 Data_ACWorthTrend、Data_grandTotal 或其他数值变量内容；这些数值序列的语义证明和 cross-check 只属于 E2"。
2. **§Slice E1 Actions item 4**：新增——"For JS identity smoke, parse only fS_code / fS_name values and Data_netWorthTrend / Data_ACWorthTrend / Data_grandTotal variable presence. Do not parse or record numeric content from those JS variables in E1."

E1/E2 边界无歧义：identity 和 capability 在 E1，数值内容解析和 semantics proof 在 E2。这直接解决了 GLM F-2。

## Prior Findings Closure

### GLM Prior Findings

| Finding | Severity | Post-fix Status |
|---------|----------|----------------|
| F-1 `insufficient_history` 术语间隙 | medium | **Closed** — Fix 3 在 taxonomy Note、E2 accept criteria、E3 tests、completion report 四处显式声明映射 |
| F-2 E1 JS 变量值解析边界不明确 | informational | **Closed** — Fix 4 在 Candidate 2 inspection 和 E1 Actions 两处显式约束 |
| F-3 `累计收益率走势` period 参数 | informational | **Remains informational** — 未在 fix scope 内；plan 已正确把 proof 留给 E2，不阻塞 |

### DS Prior Findings

| Finding | Severity | Post-fix Status |
|---------|----------|----------------|
| F1 E-class ex-date fallback 策略 | moderate | **Closed** — Fix 1 三层策略覆盖 exact date / window-based / fail-closed |
| F2 Output options 二元结果歧义 | minor | **Closed** — Fix 2 新增 `partial-acceptance-with-blocked-classes` |
| F3 `insufficient_history` 命名 | informational | **Closed** — Fix 3 同 GLM F-1 |
| F4 Repository 硬编码推迟 | informational | **Remains informational** — 正确推迟，无需 fix |

## New Findings Introduced By Fix

无。四项 fix 均为增量补充，未改变 proof standard 强度、scope 边界、fail-closed 语义或 non-goals。

以下为观察性确认：

- Fix 1 的 window-based check 前置条件（primary proof 已通过）确保不会在缺乏 provider semantics 时仅靠 window divergence 接受 candidate。正确。
- Fix 2 的 partial acceptance 语义要求 blocked classes 保持 fail-closed 并显式列出，不会创造"弱接受"后门。正确。
- Fix 3 的映射规则只约束 evidence artifact 标注，不影响 typed model `NavFailureCategory` Literal 域。若后续需要 runtime `insufficient_history`，需开独立 amendment。正确。
- Fix 4 的 E1/E2 边界划分清晰，E2 仍保留 JS 数值解析的 structured parser 要求。正确。

## Controller Proceed Statement

Controller **可以** accept plan 并 proceed to evidence slice E1/E2。

四项 fix 均已正确应用，prior findings 全部关闭或维持为 informational。Plan 的 proof standard、scope boundary、failure taxonomy、E1/E2 边界划分均符合 `AGENTS.md`、`docs/design.md` 和 `docs/implementation-control.md` 真源要求。

## Validation

本 re-review 未修改任何 production code、test、schema、score、snapshot、quality gate 或 golden fixture。未执行 ruff/pytest（docs/reviews-only artifact）。
