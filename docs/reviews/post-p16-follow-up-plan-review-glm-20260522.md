# Post-P16 Follow-up Plan Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Post-P16 follow-up planning 从第一性原理正确推导出 P17-S1 `tracking_error` extractor ambiguity boundary and note consistency 是 P16 合并后的正确下一步。Scope 收窄到 Fund Capability extractor 内部 hardening，不引入新架构、新数据源或 golden 变更，与 AGENTS.md 硬约束和 implementation-control.md Active Residuals 完全对齐。无阻断级问题。

## Review Target

`docs/reviews/post-p16-follow-up-planning-20260522.md`

## Inputs Read

| File | Role |
|---|---|
| `AGENTS.md` | Agent 执行规则权威来源 |
| `docs/design.md` | 设计真源文档 |
| `docs/implementation-control.md` | 实施总控真源 |
| `fund_agent/fund/extractors/performance.py:344-756` | tracking_error 提取/分类实际代码 |
| `fund_agent/fund/extractors/models.py` | TrackingErrorValue / ExtractedField 数据模型 |
| `fund_agent/fund/data_extractor.py:140-249` | tracking_error 对外 façade 与 fund-type 门控 |
| `tests/fund/extractors/test_performance.py:163-349` | 现有 7 个 tracking_error 测试用例 |
| `docs/reviews/p16-main-branch-closeout-20260522.md` | P16 closeout artifact |
| `docs/reviews/p16-aggregate-deepreview-glm-20260522.md` | GLM aggregate review |

Excluded inputs not read: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Code-Fact Verification

Plan 假设 P17-S1 的实现前提是 Fund Capability 内存在可分离的 `tracking_error` 分类边界。代码事实逐项验证：

| Plan 假设 | 代码事实 | 状态 |
|---|---|---|
| 存在可分离的 tracking_error 提取/分类函数 | `_extract_tracking_error()` at `performance.py:344-398`，内部调用 `_extract_tracking_error_from_tables()`、`_extract_tracking_error_from_text()`、`_has_ambiguous_tracking_error_text()` | **Confirmed** |
| 存在 broad early-return 可能抑制有效披露 | 两处独立 early-return：(1) `_has_ambiguous_tracking_error_text()` 在 `performance.py:357` 前置返回，当任意一行同时含 actual+target 关键词时丢弃整份报告；(2) `_extract_tracking_error_from_text()` 内部 `performance.py:494-496`，当某行含 target context + actual signal 时立即返回 `None`，中断整个 text 抽取 | **Confirmed，比 plan 描述的更广泛** |
| 存在 target/limit/narrative 阻断机制 | `_TRACKING_ERROR_NEGATIVE_KEYWORDS` + `_tracking_error_context_is_target_or_ambiguous()` | **Confirmed** |
| note 口径存在不一致 | `"tracking_error_ambiguous"` 同时用于 `performance.py:358`（行级歧义）和 `performance.py:364`（表/文值不一致），语义不同 | **Confirmed，见 F1** |
| multi-match 路径存在隐式抑制 | table 路径 `performance.py:465-466`：2+ match → `None`；text 路径 `performance.py:510-511`：2+ match → `None` | **Confirmed，见 F2** |
| 年报访问通过 FundDocumentRepository | `_extract_tracking_error` 接收 `ParsedAnnualReport`，不直接操作 PDF/cache | **Confirmed** |
| 代码结构可做窄口径 patch | keyword sets、early-return guard、table/text extraction 各自独立，可单独修改 | **Confirmed** |
| fund-type 门控在 data_extractor 层 | `_tracking_error_for_fund_type()` at `data_extractor.py:224-249`，非 index/enhanced_index 强制 missing | **Confirmed** |

Stop condition "Current code has no separable tracking_error classification boundary" **不会被触发**。代码确实存在可分离的分类边界。

## Findings

### F1 [LOW] Note 语义复用——两种不同失败模式共用同一 note

**Issue**: `performance.py:358` 和 `performance.py:364` 都使用 `"tracking_error_ambiguous"` 作为 missing note，但触发条件和语义不同：

- Line 358: `_has_ambiguous_tracking_error_text()` 返回 true → 任意单行同时出现 actual + target 关键词 → **报告级预检歧义**，跳过全部后续 table/text 抽取
- Line 364: `_select_consistent_tracking_error_match()` 发现 table 和 text 值不同 → **数据源间冲突**

Plan 第 85 行提到 "missing reason / note / source_type / calculation_method 口径一致、可测试"，但没有显式将此复用列为需要拆分的 case。

**Risk**: 实现阶段可能只加固 early-return 行为但保留语义模糊的 note，导致后续 evidence acquisition 无法区分"文本歧义"和"数据冲突"两种根本不同的失败模式。审计日志和质量门控也无法按失败类型做精确统计。

**Required plan change**: 在 Implementation Shape 第 2 步或 Success Signals 中显式要求拆分，例如 `"tracking_error_line_ambiguous"` vs `"tracking_error_table_text_inconsistent"`。无需修改 plan 结构，补充一条 success signal 即可。MiMo 独立审查也独立确认了此发现。

### F2 [LOW] Multi-match 隐式抑制路径未在 plan 中显式覆盖

**Issue**: Plan 第 133-139 行的 Implementation Shape 列出了 blocker 分类（target/limit、narrative、benchmark-only、standard-deviation-only、ambiguous、incomplete-anchor），但没有显式覆盖 multi-match 抑制路径：

- `performance.py:465-466`: table 路径发现 2+ match 时返回 `None`（不返回任何值，视为无结果）
- `performance.py:510-511`: text 路径发现 2+ match 时返回 `None`

这些路径在当前测试中未被覆盖（7 个现有用例均使用单 match 场景）。

**Risk**: 如果某只基金的年报表格中有多个 tracking-error 行（如不同年度、不同频率的行），当前逻辑会静默丢弃全部结果，既不是 accepted 也不是显式 blocker。实现 P17-S1 时如果只加固 explicit blocker 分类而不处理 multi-match，此隐式抑制路径会继续存在。

**Required plan change**: 在 Implementation Shape 中补充一条：multi-match 抑制路径应产生显式 missing reason（如 `"tracking_error_multiple_matches"`）而不是静默返回 `None`。或者，如果 plan 判定 multi-match 在当前 direct-disclosure 场景下频率极低且 fail-closed 行为可接受，应在 Residual Risks 中显式记录此设计决策。

### F3 [INFO] Text extraction 内部 early-return 未单独列出

**Issue**: Plan 第 140 行提到 "Avoid broad early-return that prevents a later valid direct-looking disclosure in the same bounded section/table from being evaluated"。Code-fact verification 发现 plan 只讨论了 `_has_ambiguous_tracking_error_text()` 的 top-level pre-check（line 357），但 `_extract_tracking_error_from_text()` 内部也有独立的 early-return（line 494-496）：当某行同时含 target context 和 actual signal 时，立即返回 `None` 中断整个 text 抽取。

**Risk**: 低。两处 early-return 的语义方向一致（都是 broad suppression），实现时修复一处通常会连带检查另一处。但如果只修复 top-level pre-check 而遗漏 text 函数内部的 early-return，问题会部分残留。

**Required plan change**: 无需修改 plan。P17-S1 plan gate 应要求实现阶段显式检查两处 early-return（`performance.py:357` 和 `performance.py:494-496`），确保两者都不抑制同报告内其他位置的 valid disclosure。

### F4 [INFO] source_type / calculation_method 在 missing 路径不可访问

**Issue**: Plan 第 85 行提到 "missing reason / note / source_type / calculation_method 口径一致"。但代码事实是：`source_type` 和 `calculation_method` 是 `TrackingErrorValue` 的字段（`models.py:148-149`），当 `ExtractedField.value=None`（missing path）时这些字段不可访问。Missing 路径实际可用的区分字段只有 `note` 和 `extraction_mode`。

**Risk**: 极低。这只是一个表述精确性问题。实现者理解 "口径一致" 的实际含义是 `note` 的语义精确化，不会误以为需要为 missing path 添加 `source_type`/`calculation_method` 字段。

**Required plan change**: 无。如果 plan gate 希望表述更精确，可将第 85 行的 "source_type / calculation_method" 限定为 success path 的 consistency requirement，但非必要。

## Positive Observations

1. **Root problem 推导正确**: Plan 从第一性原理推导出 post-P16 的核心质量风险是 "让 fail-closed 行为更稳定" 而非 "继续寻找 golden data"，这与 P15-S1A 的 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 和 P16 aggregate residual 的 "extractor early-return / note consistency" 完全对齐。

2. **Candidate table 裁决严谨**: 所有 reject/defer 决策都有 first-principles 论证。特别是拒绝 calculated tracking error（line 69）、E1-E3 / Evidence Confirm（line 70）和 RR-13 auto mutation（line 72）的理由充分，与 AGENTS.md 硬约束和 implementation-control.md non-goal reminder 完全一致。

3. **Non-goals 覆盖完整**: Plan 第 96-103 行的 non-goals 完整覆盖了 AGENTS.md 的所有硬约束：无 Dayu/LLM/Evidence Confirm、无 Service/UI/Engine 改造、无 design/control 修改、无 golden rows、无外部数据源、无 `extra_payload`。

4. **Stop conditions 设计合理**: 两层 stop（plan 阶段 stop conditions + merge 前 stop conditions）覆盖了关键风险点。特别值得注意的是 "不得把 `schema_drift`/`identity_mismatch`/`integrity_error` 静默转为 fallback success" 这条与 AGENTS.md 来源失败分类策略完全一致。

5. **Owned files 边界清晰**: 明确区分了 owned（extractor、tests、可选 README）和 not-owned（golden、design、control、CSV、Service/UI/Engine、PR/issue），与 Fund Capability 模块边界一致。

6. **Validation 要求具体**: 第 148-153 行的 pytest 命令覆盖了 extractor 单测、snapshot/score/quality 集成、ruff 和 whitespace 检查，同时正确排除了 direct PDF/cache/source-helper reads。

7. **Handoff prompt 完整且可执行**: 第 222-238 行的 handoff prompt 为 P17-S1 plan gate 提供了清晰的入场约束，包括所有禁止引入的内容清单。

## Scope And Boundary Verification

| 检查项 | 结果 |
|---|---|
| 是否 smuggle in golden expansion | No — non-goals 显式禁止，candidate table reject |
| 是否 smuggle in external index data | No — non-goals 显式禁止，candidate table reject |
| 是否 smuggle in calculated tracking error | No — non-goals 显式禁止，candidate table reject |
| 是否 smuggle in Dayu/LLM/Evidence Confirm | No — non-goals 显式禁止，candidate table reject |
| 是否 smuggle in Service/UI/Engine source access | No — non-goals 显式禁止，owned files 限定在 Fund Capability |
| 是否修改 design/control 真源 | No — non-goals 显式禁止 |
| 是否触碰 RR-13 或 source CSV | No — what-must-not-be-touched 显式排除 |
| 模块边界是否违反 AGENTS.md | No — extractor hardening 属于 Fund Capability 职责 |
| 排除的本地草案是否被引用 | No — explicitly excluded 并列于 what-must-not-be-touched |

## Residual Risks For Controller

| Residual | Handling |
|---|---|
| F1 note 语义复用 | P17-S1 plan gate 应显式要求拆分 `"tracking_error_ambiguous"` 为两种 note |
| F2 multi-match 隐式抑制 | P17-S1 plan gate 应要求显式处理或显式记录设计决策 |
| F3 text extraction 内部 early-return | P17-S1 实现阶段应检查两处 early-return 而非仅 top-level pre-check |
| `_extract_tracking_error_from_text` 与 `_has_ambiguous_tracking_error_text` 重复扫描 §2+§3 | 低风险，性能可忽略；实现时可考虑合并或保留为 defensive redundancy |
| Multi-match suppression 在某些年报中可能频繁触发（如多年度对比表格） | 如果未来 evidence acquisition 扩展到 multi-period 场景，此路径需要重新评估 |

## Blocking Issues

无。

## Conclusion

Post-P16 follow-up planning 推荐的 P17-S1 是 P16 合并后正确的下一个 implementable phase。Plan scope 收窄到 Fund Capability extractor 内部 hardening，不越权、不引入新架构、不违反 AGENTS.md 硬约束。F1 note 语义复用和 F2 multi-match 隐式抑制是 LOW 级发现，应在 P17-S1 plan gate 中显式处理，但不阻断当前 planning gate。MiMo 独立审查也独立确认了 F1 并给出了相同的结论。
