# Post-P16 Follow-up Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Post-P16 follow-up planning 正确识别了 P15/P16 后的真实质量风险：`tracking_error` 在无直接披露时的 fail-closed 行为和 note 口径一致性。推荐的 P17-S1 是 Fund Capability extractor 内部的窄口径 hardening，scope 合理、边界清晰、不越权。无阻断级问题，可以进入 P17-S1 plan gate。

## Review Target

`docs/reviews/post-p16-follow-up-planning-20260522.md`

## Inputs Read

| File | Role |
|---|---|
| `AGENTS.md` | Agent 执行规则权威来源 |
| `docs/implementation-control.md` | 实施总控真源 |
| `docs/reviews/p16-aggregate-deepreview-controller-judgment-20260522.md` | P16 aggregate 裁决 |
| `docs/reviews/p16-main-branch-closeout-20260522.md` | P16 closeout |
| `docs/reviews/p16-pr-review-controller-judgment-20260522.md` | P16 PR review |
| `fund_agent/fund/extractors/performance.py:344-539` | tracking_error 提取/分类实际代码 |

Excluded inputs not read: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Code-Fact Verification

Plan 声称 P17-S1 的实现前提是 Fund Capability 内存在可分离的 `tracking_error` 分类边界。代码事实确认：

| Plan 假设 | 代码事实 | 状态 |
|---|---|---|
| 存在 tracking_error 提取/分类函数 | `_extract_tracking_error()` at `performance.py:344` | **Confirmed** |
| 存在 broad early-return 可能抑制有效披露 | `_has_ambiguous_tracking_error_text()` at `performance.py:517` 在 `performance.py:357` 前置返回，当任意一行同时含 actual+target 关键词时丢弃整份报告 | **Confirmed** |
| 存在 target/limit/narrative 阻断机制 | `_TRACKING_ERROR_NEGATIVE_KEYWORDS` at `performance.py:41` + `_tracking_error_context_is_target_or_ambiguous()` | **Confirmed** |
| note 口径存在不一致 | `"tracking_error_ambiguous"` 同时用于两种不同失败模式（行级歧义 vs 表/文不一致） | **Confirmed，见 F1** |
| 年报访问通过 FundDocumentRepository | `_extract_tracking_error` 接收 `ParsedAnnualReport`，不直接操作 PDF | **Confirmed** |
| 代码结构可做窄口径 patch | keyword sets、early-return guard、table/text extraction 各自独立，可单独修改 | **Confirmed** |

Stop condition "Current code has no separable `tracking_error` classification boundary" 不会被触发。代码确实存在可分离的分类边界。

## Findings

### F1 [LOW] Note 语义复用未在 plan 中显式列为修复目标

**Issue**: `performance.py:358` 和 `performance.py:364` 都使用 `"tracking_error_ambiguous"` 作为 note，但含义不同：
- Line 358: 行级歧义（同一行同时出现 actual+target 关键词）
- Line 364: 表/文值不一致（table 和 text 都命中但解析值不同）

Plan 第 85 行提到 "missing reason / note / source_type / calculation_method 口径一致、可测试"，但没有明确将此复用列为需要拆分的 case。

**Risk**: 实现阶段可能忽略此不一致，导致测试覆盖了行为但 note 仍然语义模糊，后续 evidence acquisition 判断无法区分"文本歧义"和"数据冲突"。

**Required plan change**: 在 Implementation Shape 第 2 步或 Success Signals 中显式要求拆分这两种 note，例如 `"tracking_error_line_ambiguous"` vs `"tracking_error_table_text_inconsistent"`。无需修改 plan 结构，补充一条 success signal 即可。

### F2 [INFO] Validation section 缺少具体 blocker-type test case 清单

**Issue**: Plan 第 146-153 行列出了 pytest 命令，但没有列出每个 blocker 类型需要的 fixture snippet 示例（如 target/limit 文本、narrative 文本、benchmark-only 文本等）。Success Signals 第 166-172 行描述了行为期望，但没有映射到具体测试输入。

**Risk**: 低。实现阶段会自行构造 fixture，但缺少明确清单可能导致遗漏某些边界 case（如 "standard-deviation-only" 在 P16 之前未被显式测试）。

**Required plan change**: 无需修改 plan。建议 P17-S1 plan gate 在 plan-review 阶段补充 fixture snippet 清单。

### F3 [INFO] Non-goals 列表完整且与 AGENTS.md 一致

**Observation**: Plan 第 96-103 行的 non-goals 完整覆盖了 AGENTS.md 的硬约束：
- 不引入 Dayu/LLM/Evidence Confirm ✅
- 不修改 Service/UI/Engine 边界 ✅
- 不修改 design/control 真源 ✅
- 不添加 golden rows ✅
- 不引入外部数据源 ✅
- 不使用 `extra_payload` ✅

与 `implementation-control.md` Startup Packet 的 non-goal reminder 和 Active Residuals 完全对齐。

## Positive Observations

1. **Root problem 分析准确**: Plan 正确指出 post-P16 的根问题是"让现有 direct-disclosure 抽取边界更稳定"，而非继续 golden expansion。这与 P15/P16 的 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 结论一致。

2. **Candidate table 裁决合理**: 所有 reject/defer 决策都有 first-principles 依据，特别是拒绝 calculated tracking error 和 E1-E3 Evidence Confirm 的理由充分。

3. **Stop conditions 设计合理**: 两层 stop（plan 阶段和 merge 前）覆盖了关键风险点，特别是"不得把 `schema_drift`/`identity_mismatch`/`integrity_error` 静默转为 fallback success"。

4. **Owned files 边界清晰**: 明确区分了 owned 和 not-owned 文件，与 Fund Capability 模块边界一致。

5. **Code-fact 假设可验证**: Plan 要求实现前先检查代码事实，这与 AGENTS.md "以代码为准" 原则一致。

## Residual Risks For Controller

| Residual | Handling |
|---|---|
| F1 note 语义复用 | P17-S1 plan gate 应要求拆分两种 `"tracking_error_ambiguous"` note |
| Early-return 可能需要 per-line 而非 per-report 级别的歧义判断 | P17-S1 plan gate 应要求实现检查：当报告中某行歧义但另一行有 clean direct disclosure 时，是否应接受后者 |
| `_has_ambiguous_tracking_error_text` 扫描 §2+§3，但 `_extract_tracking_error_from_text` 也扫描 §2+§3，存在重复扫描 | 低风险，性能影响可忽略，但实现时可考虑合并 |

## Blocking Issues

无。

## Conclusion

Post-P16 follow-up planning 推荐的 P17-S1 是 P16 之后正确的下一个 implementable phase。Plan scope 收窄到 Fund Capability extractor 内部，不越权、不引入新架构、不违反 AGENTS.md 硬约束。F1 note 语义复用应在 P17-S1 plan gate 中显式处理，但不阻断当前 planning gate。
