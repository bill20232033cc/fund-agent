# NAV Adjusted-Basis Source Identity Gate — Plan Review (DS)

日期：2026-05-28

角色：plan review worker (DS)，非 controller、非 implementation worker。

Work unit：`NAV adjusted-basis source identity gate`

Review target：`docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md`

## Verdict

**Accepted**

## Review Basis

本 review 基于以下真源交叉验证：

| 真源 | 用途 |
|------|------|
| `AGENTS.md` | 执行规则、Gate 轻重分类、模块边界、fail-closed taxonomy |
| `docs/design.md` (v2.2) | 架构边界、Fund 层 NAV repository/source adapter 契约、`FundDocumentRepository` 边界 |
| `docs/implementation-control.md` (v2.1) | 当前 gate 状态、next entry point、residuals、禁止事项 |
| Prior controller judgments (×2) | adjusted-basis contract + typed contract implementation 已接受裁决与 residual |
| Prior aggregate deepreviews (DS + GLM) | typed contract implementation 的 fail-closed taxonomy 验证、已知 non-blocking findings |
| Current snapshot / score / quality gate | 006597/2024 当前状态：`drawdown_stress` weak，baseline blocking |
| `nav_models.py` / `nav_repository.py` / `nav_data.py` | 当前 typed contract 字段、repository 硬编码、adapter 能力 |

## Findings

### F1 (Moderate) — E-class distribution ex-date not pinned; cross-check strategy underspecified

**位置**：Plan §Slice E2 — Adjustment Basis Proof, Actions item 3；§Why E-Class Raw Unit NAV Is Not Strong Evidence

**问题**：

Plan 要求 E2 找到 014217 E class 的 "exact 2023 distribution event date/range from official disclosure"。前序 controller judgment 已通过 `FundDocumentRepository` 确认 006597 2025 年报 §3.3 记载了 2023 年度 E class 分红事件（每 10 份 0.080），但年报 §3.3 通常只披露年度汇总分红金额，不一定披露每次分红的 ex-date。

Plan 未说明以下场景的处理策略：
- 年报未披露精确 ex-date 时，是否接受 window-based cross-check（例如在已知分红发生的季度窗口内对比 raw unit NAV 与 candidate accumulated/total-return series 的 divergence）？
- 如果 `FundDocumentRepository` 无法从年报文本中提取精确日期，E2 是否自动 fail？还是降级为 window-based consistency check？

**影响**：如果坚持精确 ex-date 才能通过 cross-check，可能因年报披露粒度不足而错误拒绝实际上可验证的 adjusted series。

**建议修复**：在 E2 Actions item 3 中增加 fallback 策略：若年报未披露精确 ex-date，接受 window-based divergence check（季度窗口），条件是 divergence 方向与分布金额一致，且 source semantics proof 已通过。

### F2 (Minor) — Output options 暗示二元结果，但 completion report 支持部分接受

**位置**：Plan §Slice E2 — Output options；§Completion Report Format

**问题**：

E2 Output options 列出两种结果：`accepted-source-basis-candidate` 和 `blocked-with-source-gap`。但 Completion Report Format 中实际包含 `share classes covered` 和 `insufficient classes/windows` 字段，说明设计意图是支持部分接受（例如 006597 A 的累计净值被接受，但 014217 E 因分布交叉验证失败而 blocked）。

Output options 应明确允许 partial acceptance 作为合法输出，避免 reviewer/controller 误认为必须全有或全无。

**建议修复**：在 E2 Output options 中增加第三种输出：`partial-acceptance-with-blocked-classes`，并交叉引用 Completion Report Format 中的 `share classes covered` / `insufficient classes/windows`。

### F3 (Informational) — `insufficient_history` 命名与当前模型不一致，已妥善处理

**位置**：Plan §Failure Taxonomy 表格及 Note

**确认**：

Plan 的 failure taxonomy 表格使用 `insufficient_history`，但 Note 显式声明当前模型使用 `insufficient_records` 和 `missing_date_range`，并给出了处理路径："must either map to existing completeness categories in evidence artifact or open a minimal model taxonomy amendment。"

这个处理是正确的。不构成 blocking issue，但 controller 在最终 judgment 中应确认 E1/E2 evidence artifact 使用了哪个术语。

### F4 (Informational) — 当前 repository 硬编码 `unit_nav`/`raw_unit_nav`，plan 正确推迟了实现

**位置**：Plan §Existing Typed Contract Fit；`nav_repository.py:206-207`

**确认**：

`FundNavRepository.load_nav_series()` 当前使用 `_CURRENT_NAV_TYPE = "unit_nav"` 和 `_CURRENT_ADJUSTED_BASIS = "raw_unit_nav"` 常量，且在构造 `FundNavSeries` 时硬编码这些值。Plan 在 §Existing Typed Contract Fit 中正确识别了这一点，并将 repository 修改推迟到 "Future implementation gate only after accepted evidence"。

Plan 正确地将 E1/E2 限定为 evidence-only（不修改 `nav_repository.py`），并将 E3 限定为 "a plan, not production implementation"。这避免了在当前 gate 做 premature implementation。

## Review Focus Checklist

| 关注点 | 状态 | 说明 |
|--------|------|------|
| Proof standard 足够强，不靠列名推断 | **通过** | 要求至少一个 primary proof + 一个 independent consistency check；明确列出仅靠列名 block 的条件 |
| A/C/E/F 份额类别分离，不混合 | **通过** | 显式矩阵、identity 验证规则、`share_class` 不混合声明 |
| E-class raw unit NAV 正确处理 | **通过** (见 F1) | 明确说明为何 raw unit NAV 在分布期间不能作为强证据；要求分布交叉验证；F1 仅涉及 ex-date 获取的 fallback 策略 |
| 现有 typed contract 字段足够或显式推迟 | **通过** | 正确识别当前字段足以覆盖需要的决策；明确如需新增字段则停止并开独立 schema amendment |
| Failure taxonomy 完整且 fail-closed | **通过** (见 F3) | 7 类分类完整；`not_found`/`unavailable` eligible fallback，其余 fail-closed；`insufficient_history` 命名已妥善处理 |
| 不实现 max drawdown / volatility | **通过** | Non-goals 显式排除；Stop conditions 包含"Any reviewer asks to implement max drawdown or volatility" |
| 不修改 score/snapshot/quality/golden | **通过** | Always disallowed 列表显式排除；§Non-Goals 再次确认 |
| 不解除 drawdown_stress blocker | **通过** | 多处显式声明（Step Self-Check、Non-Goals、Completion Report Format、Stop conditions） |
| Fund 层 repository/adapter 边界，不直接 Akshare/JS | **通过** | Evidence smoke 与 production path 明确区分；production 必须经过 `FundNavRepository.load_nav_series()` |
| 验证矩阵适合 evidence-only vs code-changing | **通过** | 三层矩阵：evidence-only（不需要 ruff/pytest）、tests added（focused）、production code changed（full） |

## Adversarial Pass

### 反向案例检查

1. **若 Akshare `累计净值走势` 返回值恰好等于 `单位净值走势`**：Plan §Mandatory block conditions 第 3 条覆盖——若 candidate series 在有已知分布的期间等于 raw unit NAV，block。通过。

2. **若 Eastmoney JS 返回的 `fS_name` 不含份额后缀**（如只返回"国泰利享中短债债券"而不含"A"/"C"/"E"/"F"）：Plan §A/C/E/F Source Identity Plan Rules 第 5 条覆盖——"If source returns fund name without suffix or with a conflicting suffix, fail `identity_mismatch`"。通过。

3. **若 022176 F 的累计净值序列只有 398 rows，不足以覆盖 future drawdown window**：Plan 在 real smoke matrix 中已将 022176 标记为 "classify `insufficient_history` if window predates inception"。通过。

4. **若 evidence slice 中 akshare/public API 不可用**：Plan §Slice E1 Stop condition 覆盖——"If public APIs are unavailable, classify `unavailable` and produce evidence artifact with commands and failure causes." 通过。

5. **若 `FundDocumentRepository` 无法加载 006598/014217/022176 的年报**：由于这是同一产品不同份额，同一份年报（国泰利享中短债债券）覆盖所有份额类别。年报加载使用的是产品级 fund_code 006597，不要求每个 share class code 独立加载年报。Plan 未显式说明这一点，但实际实现路径是可行的。低风险。

6. **若 E2 接受 `累计收益率走势` 为 total_return，但该序列只有 202 rows（vs 1809 rows for unit NAV）**：这个大幅减少的记录数可能触发 `insufficient_history`。Plan §Candidate 1 已记录 row count 差异，但未在 accept criteria 中设定最小记录数阈值。建议 controller 在 E2 中定义可接受的 minimum_records 门槛。低风险。

### 边界条件

- Plan §Candidate 4 作为 `future-source-gap-option` 存在，确保即使 Akshare/Eastmoney 不可证明，也不会降级证明标准。通过。
- Plan §Proof Standard 中的 block condition "Cross-check cannot identify the ex-dividend / distribution date range for the share class" 与 F1 的 window-based fallback 建议存在张力——前者说找不到日期范围就 block，后者说可以用季度窗口。这进一步支持 F1 的修复建议。

## Scope Boundary Verification

对比 `docs/implementation-control.md` Next Entry Point 的 allowed scope：

| 约束 | Plan 是否遵守 |
|------|--------------|
| Consume only `FundNavRepository.load_nav_series()` | **是** — §Non-Goals + §Existing Typed Contract Fit 确认 |
| Explicit params, no `extra_payload` | **是** — §Non-Goals 显式禁止 |
| Reject `raw_unit_nav` + `requested_code_only` as strong evidence | **是** — §Proof Standard + §Why E-Class Raw Unit NAV 多处覆盖 |
| Keep A/C/E/F separated | **是** — §A/C/E/F Source Identity Plan |
| Preserve fail-closed taxonomy | **是** — §Failure Taxonomy |
| No score/snapshot/quality/golden changes | **是** — §Always disallowed |
| No Host/Agent/dayu | **是** — Non-goals |
| Two independent reviews before acceptance | **是** — §Review Requirements 要求 DS + GLM |

## Residual Risks If Accepted

1. **E-class ex-date granularity**（F1）：年报可能不披露精确 ex-date，window-based cross-check 需要显式接受为合法 fallback。
2. **Partial acceptance 表述**（F2）：当前 Output options 暗示二元结果，可能造成 controller 混淆。
3. **累计收益率序列记录数大幅少于单位净值**：006597 累计收益率只有 202 rows vs 1809 rows 单位净值。即使 basis 被证明，未来 drawdown window 可能因 `insufficient_records` 而被拒绝。此风险不在本 gate 范围内，但应在 evidence artifact 中标记。
4. **022176 F class inception recency**：398 rows 意味着约 1.5 年历史，可能不足以支持有意义的 max drawdown 计算。同样不在本 gate 范围内。
5. **Repository 修改范围未知**：当前 repository 不支持切换 indicator（硬编码 `单位净值走势`）。未来 implementation gate 的修改范围（是否只需参数化 indicator，还是需要更根本的 repository 重构）要到 E3 才能评估。

## Controller May Proceed

Controller 可以派发 evidence slice E1（Source Capability And Identity Smoke）。

E2（Adjustment Basis Proof）建议在 F1 修复后再启动，或由 controller 在 E2 启动时明确接受 window-based distribution cross-check 作为合法 fallback。

F2（partial acceptance output option）不阻塞 evidence 启动，但应在 controller judgment 中确认。

## Validation

本 review 未修改任何 production code、test、schema、score、snapshot、quality gate、golden fixture。未执行 ruff/pytest（docs/reviews-only artifact）。
