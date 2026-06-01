# NAV Adjusted-Basis Source Identity Gate — Plan Re-Review (DS)

日期：2026-05-28

角色：plan review worker (DS)，re-review only。不编辑 plan、code、test，不 commit/push/PR。

Work unit：`NAV adjusted-basis source identity gate`

Prior review：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-review-ds-20260528.md`

GLM prior review：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-review-glm-20260528.md`

## Verdict

**Accepted**

## Per-Finding Verification

### F1 (Moderate) — E-class distribution ex-date fallback → **Resolved**

**Prior finding**：E2 要求精确 ex-date，但年报 §3.3 通常不披露精确日期，缺少 window-based fallback 策略。

**Fix applied**：

Plan §Slice E2 新增 Actions item 4–5，定义四条件 window-based divergence check：
- provider/source semantics primary proof 已通过（前置条件）
- window 可追溯到官方披露或 `FundDocumentRepository` 证据
- raw unit NAV 与 candidate series 的 divergence 方向和量级与分红金额一致
- evidence artifact 记录不确定性、选定窗口、来源锚点、预期效应和观测效应

Actions item 5 显式 fail-closed：若既无精确日期也无 defensible official window，归类为 `adjustment_basis_unknown`。

§Proof Standard Mandatory block conditions 同步更新为 "Cross-check cannot identify either an exact ex-dividend date or a defensible distribution window"。

**验证**：四条件门控严格（先 proof、再 window traceability、再 quantitative consistency、最后 uncertainty recording），fail-closed 覆盖无日期无窗口场景。**通过。**

### F2 (Minor) — Output options 二元 → **Resolved**

**Prior finding**：E2 Output options 只有 `accepted-source-basis-candidate` / `blocked-with-source-gap` 二元结果，不支持部分接受。

**Fix applied**：

- §Slice E2 Output options 新增第三种输出 `partial-acceptance-with-blocked-classes`，描述为 "at least one share class passes...while other classes remain blocked"。
- §Stop Conditions Terminal outputs 同步增加 `partial-acceptance-with-blocked-classes`。
- §Completion Report Format Decision 行增加 `partial-acceptance-with-blocked-classes` 选项。
- Completion Report 新增 `share classes covered` / `insufficient classes/windows` 字段。

**验证**：三个位置一致更新，描述精确，引用 completion report 字段做交叉引用。**通过。**

### F3 (Informational) — `insufficient_history` 术语映射 → **Resolved (enhanced)**

**Prior finding**：Plan 已妥善处理，但可更明确 evidence artifact 中如何映射到当前 model category。

**Fix applied**：

§Failure Taxonomy Note 扩展为：
- `insufficient_history` 明确为 "evidence-level diagnostic label only"
- E1/E2 evidence artifact 使用该标签时 "must also record the current model mapping"，给出具体映射规则：`model_category="insufficient_records"`（行数不足）或 `model_category="missing_date_range"`（日期窗口不足）
- 若 future implementation 需要 runtime `NavFailureCategory="insufficient_history"`，必须先开 model taxonomy amendment

§Slice E2 Accept criteria、§Completion Report Format 同步增加映射要求和 `evidence-level insufficient_history mapping` 字段。

**验证**：术语分层清晰（evidence label vs model category），映射规则具体可操作，amendment gate 显式。此修复同时覆盖了 GLM F-1（medium）。**通过。**

### Fix 4 (GLM F-2) — E1 JS identity smoke 范围收窄 → **Resolved**

**说明**：此 fix 来自 GLM F-2（informational），用户要求一并验证。

**Fix applied**：

- §Slice E1 Actions item 4（新增）："parse only `fS_code` / `fS_name` values and `Data_netWorthTrend` / `Data_ACWorthTrend` / `Data_grandTotal` variable presence. Do not parse or record numeric content from those JS variables in E1."
- §Candidate 2 Required inspection 重写为两条：E1 只用 HTTP GET 读 identity header + 变量存在性；E1 不解析数值变量内容；E2 如需解析数值内容必须用 structured JS parser。

**验证**：E1/E2 职责边界清晰——E1 = identity + capability smoke，E2 = semantics proof + numeric cross-check。**通过。**

## No New Blocking Findings

Fix 引入的变更严格限定在四个修改区域，未发现新问题：

- E2 Actions 4 的 window-based fallback 正确地将 primary proof 作为前置条件，避免 window check 降级为唯一证据。
- `partial-acceptance-with-blocked-classes` 在所有相关位置（Output options、Terminal outputs、Completion Report）一致。
- `insufficient_history` 映射规则使用具体字段名 (`model_category="insufficient_records"` / `"missing_date_range"`)，不会与现有 Literal 域冲突。
- E1 JS scope 收窄不会影响 E2——E2 仍可独立解析数值变量内容（通过 structured parser）。

## Controller May Proceed

所有 prior findings 已关闭。Controller 可以接受 plan 并派发 evidence slice E1/E2。

E1 可立即启动（scope：A/C/E/F × 三类 indicator smoke + JS identity header only）。E2 的 window-based distribution cross-check 已在 plan 中定义完整的四条件门控和 fail-closed 路径，无需额外 controller 裁定即可执行。
