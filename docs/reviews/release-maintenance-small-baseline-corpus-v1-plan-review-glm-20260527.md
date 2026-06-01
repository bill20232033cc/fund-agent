# Plan Review: Small Baseline Corpus v1 Evaluation Plan

> **Reviewer**: AgentGLM (independent plan reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, current accepted artifacts

---

## Findings

### F1 — MATERIAL: Clean denominator coverage 仅 3/6 fund types，低于 5-10 代表样本目标

**Evidence**:
- Control doc Next Entry Point 要求："Expand from `004393` toward 5-10 representative samples covering active/index/enhanced-index/bond/QDII/FOF."
- Plan 的 clean denominator 仅含 `004393`/active、`004194`/enhanced_index、`006597`/bond，共 3 个 clean fund-type slots。
- `110020`/index 和 `017641`/QDII 为 fallback-blocked，被排除出 clean denominator。
- `007721` 和 `017970` 为 FOF data_gap / taxonomy_pending，同样被排除。
- 最终 clean 覆盖率为 3/6 fund types（active, enhanced_index, bond），index 和 QDII 因 fallback-blocked 缺席，FOF 因纯 FOF 候选不可得而标记为 data_gap。

**Risk**: Gate closeout 时，若判定条件为"至少三个 clean candidates"，当前 plan 恰好卡在边界线上。但 control doc 原文要求覆盖六种 fund types，3/6 仅覆盖一半。Next gate decision rules 中"Clean coverage remains below three fund-type slots"的停条件应改为"below three clean candidates **or** below half of target fund-type slots"，否则 3 clean 恰好不触发停条件却无法满足 5-10 目标。

**Recommendation**: Plan 应在 Startup Packet Recap 或 Candidate Selection Strategy 中明确声明：(1) 当前 clean denominator 为 3/6 fund types，低于 5-10 目标；(2) 明确 index/QDII fallback-blocked 不影响本 gate closeout，但其 source recovery 应作为 next gate 的硬前提；(3) 将"three fund-type slots"decision boundary 从 `< 3` 调整为 `≤ 3` 并附注覆盖率不足的 residual。

---

### F2 — MATERIAL: extraction-score 命令引用 golden-answer 路径，未说明 004194/006597 的 golden 覆盖预期

**Evidence**:
- Verifier matrix 中三条 score 命令均引用 `--golden-answer-path reports/golden-answers/golden-answer.json`。
- 当前 accepted golden coverage 主要覆盖 `004393`/2024（从 control doc 多次 golden-prefill/golden-build 相关 accepted artifacts 可推断）。
- Control doc 决策："missing same-year golden coverage is reported as `year_not_covered` / `FQ0/info`"——即 004194 和 006597 的 score 结果将大量产生 `year_not_covered` FQ0/info 而非有意义的 correctness 信号。
- Plan 未在 verifier matrix 或 Run Procedure 中注明这一预期结果，可能导致 implementation worker 误解为 golden 覆盖充足。

**Risk**: Implementation worker 可能将大量 `year_not_covered` 误解为评分失败，或在 summary artifact 中将 golden 缺失与真实 extraction 问题混为一谈。Decision summary 阶段需要区分"golden 不存在"与"抽取字段缺失"两种不同根因。

**Recommendation**: Plan 应在 Run Procedure 的 Candidate probing and offline evaluation 阶段或 Verifier Matrix 的 Expected handling 列中注明：(1) 当前 golden answer 仅覆盖 004393/2024；(2) 004194 和 006597 的 score 结果预期以 `year_not_covered` 为主，correctness 维度不可解读；(3) summary artifact 需按"golden-covered"和"golden-missing"分组报告 FQ 结果。

---

### F3 — MINOR: Plan 声称 "7-row candidate matrix"，实际表格包含 8 行

**Evidence**:
- Candidate Selection Strategy 第 1 条："Use a 7-row candidate matrix for v1 evaluation planning."
- 实际 Candidate Matrix 表格含 8 行：`004393`/2024, `004393`/2025, `004194`/2024, `006597`/2024, `110020`/2024, `017641`/2024, `007721`/2024, `017970`/2024。
- 差异来自 `004393` 拆分为 2024 和 2025 两行（2025 为 probe-only）。

**Risk**: 低风险，但数字不一致会降低 plan 的形式可信度，尤其在 multi-agent review 流程中可能触发不必要的澄清回合。

**Recommendation**: 将 "7-row" 改为 "8-row"，或在 Candidate Selection Strategy 中注明 "7 unique fund codes across 8 candidate rows (004393 appears for both 2024 and 2025)."

---

### F4 — MINOR: 004393/2025 probe 使用 `--dev-override` 模式，对 FinalJudgmentDecision 的影响未充分说明

**Evidence**:
- Verifier matrix 的 004393/2025 analyze smoke 使用 `--dev-override --quality-gate-policy warn`。
- Per `docs/design.md` §2.2 和 §4.8，`AnalyzeMode.DEVELOPER_OVERRIDE` 允许通过 `FundAnalysisDeveloperOverrides` 覆盖最终判断，覆盖后 `selected_judgment` 可能与 `derived_judgment` 不一致。
- Plan 在 Expected handling 中仅说 "Probe availability / report-year correctness scope only"，未说明 dev-override 模式下最终判断的语义。

**Risk**: Implementation worker 若未注意 dev-override 的判断语义，可能在 summary artifact 中误报 judgment 不一致或覆盖行为。

**Recommendation**: 在 004393/2025 的 Expected handling 中补充："dev-override mode 下最终判断可能被覆盖；仅记录 exit code、quality gate stderr 和 report-year scope，不消费最终判断语义。"

---

### F5 — INFO: Reconciliation 正确处理已 accepted renderer minimal integration

**Evidence**:
- Plan 的 Reconciliation 和 Non-Goals 明确声明 active-fund Chapter 3 renderer minimal integration 已 accepted，本 gate 不重复。
- 与 control doc Current Gate Accepted Artifacts 和 Next Entry Point 中的 renderer 条目一致。

**Risk**: 无。

---

### F6 — INFO: Artifact policy、stop conditions、non-goals 和 prohibitions 全面且对齐 truth sources

**Evidence**:
- Non-Goals 列表完整覆盖 review criterion 3 的全部禁止项：renderer、FQ0-FQ6、Service/CLI defaults、Host/Agent/dayu、FundDocumentRepository/source fallback、extractor、extra_payload、durable baseline、unbounded product chains、GitHub mutation。
- Stop conditions 覆盖 PDF/cache 直访、fallback-blocked clean denominator 误用、fail-closed source issue、FOF 纯覆盖要求、2024/2025 golden 复用、validator schema 分离、large output 提交、evaluation scope 越界。
- Artifact policy 清晰区分 tracked（docs/reviews/ summary）和 scratch（/tmp/、reports/ ignored paths）。
- 所有禁止项与 `AGENTS.md` 硬约束、`docs/design.md` 非目标、control doc Non-Goals 一致。

**Risk**: 无。Plan 的 scope 纪律和边界意识优秀。

---

### F7 — INFO: Verifier matrix 对 plan-only artifact 的验证策略合理

**Evidence**:
- Plan 明确声明为 "documentation-only" artifact，不修改任何源码、测试或产品行为。
- Verifier matrix 中的 ruff 和 full pytest 行注明 "not required for this design-only / analysis-only plan"，但对后续 implementation gate 明确要求。
- Plan 的 Validation section 准确描述了 artifact 的创建过程和不变量。

**Risk**: 无。Plan-only artifact 不需要执行 full pytest 是合理的。

---

## Verdict

**PASS_WITH_FINDINGS**

Plan 的 scope 纪律、prohibitions 覆盖、fallback/FOF 排除策略、artifact policy 和 decision rules 均达到高质量水平。两个 MATERIAL finding 不阻碍 plan 的核心正确性，但应在 plan 被接受前或 implementation worker 执行前补强：

1. **F1**: 明确 3/6 clean coverage 的 residual 状态，调整 decision boundary 使其不恰好卡在边界线上。
2. **F2**: 明确 golden coverage 预期，避免 implementation worker 误读 `year_not_covered` 信号。

两个 MINOR finding（F3 行数不一致、F4 dev-override 语义）建议修正但不阻塞。

| Finding | Severity | Blocks gate? |
|---------|----------|-------------|
| F1: Clean coverage 3/6，低于 5-10 目标，decision boundary 卡线 | MATERIAL | No, but should be addressed |
| F2: Golden coverage 预期未说明 | MATERIAL | No, but should be addressed |
| F3: 7-row vs 8-row 不一致 | MINOR | No |
| F4: dev-override judgment 语义未注明 | MINOR | No |
| F5: Renderer reconciliation 正确 | INFO | No |
| F6: Prohibitions 全面对齐 | INFO | No |
| F7: Plan-only 验证策略合理 | INFO | No |

---

## Truth Source Alignment Confirmation

- [x] Plan 不违反 `AGENTS.md` 硬约束（四层边界、FundDocumentRepository、fallback 分类、extra_payload 禁止）。
- [x] Plan 不违反 `docs/design.md` 非目标（不引入 Host/Agent、不拼接 tool loop、不改 renderer/FQ0-FQ6）。
- [x] Plan 与 `docs/implementation-control.md` Startup Packet、Current gate、Next entry point 一致。
- [x] Plan 正确引用 accepted artifacts 作为 evidence chain，不作为 truth override。
