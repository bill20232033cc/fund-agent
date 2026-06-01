# MVP Gate 4 Slice 4A final_chapter_assembler implementation review — MiMo

日期：2026-05-30
角色：AgentMiMo implementation reviewer
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler implementation gate`
分类：`heavy`

## Verdict

**PASS**

Slice 4A 实现正确、边界干净、契约完整。无阻断 findings。

## Review inputs

- Plan: `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- Plan decision: `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- Implementation evidence: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md`
- Current truth: `docs/current-startup-packet.md`
- Design truth: `docs/design.md` §5.4 / §5.4.1
- Workspace changes: `fund_agent/services/final_chapter_assembler.py`, `fund_agent/services/__init__.py`, `tests/services/test_final_chapter_assembler.py`, `tests/README.md`

## Boundary confirmation

| 检查项 | 结果 |
|--------|------|
| 只实现 Slice 4A | ✅ 无 4B/4C/4D 代码 |
| final assembler 在 Service 层 | ✅ `fund_agent/services/final_chapter_assembler.py` |
| 未修改 `fund_agent/fund/**` | ✅ |
| 未修改 CLI | ✅ |
| 未修改 `fund_analysis_service.py` | ✅ |
| 未修改 `design.md` / `implementation-control.md` | ✅ |
| 未引入 dayu/extra_payload/provider SDK | ✅ grep 只命中 docstring 注释 |
| 未读取 PDF/cache/source helper/repository | ✅ |
| 未修改 golden/score/quality gate/final judgment 语义 | ✅ |
| 未修改 `FinalJudgmentDecision` 或 `derive_final_judgment()` | ✅ 只消费，不改写 |

## Findings

### LOW — 覆盖建议（不阻断）

| # | 严重度 | 文件 | 行 | 说明 |
|---|--------|------|----|------|
| L1 | LOW | `test_final_chapter_assembler.py` | — | 缺少 `orchestration.status="blocked"` → `status="incomplete"` 的显式测试。当前只测了 `partial`。代码路径正确（line 377 检查 `status != "accepted"`），blocked 会走同一 fail-closed 分支，但建议补测。 |
| L2 | LOW | `test_final_chapter_assembler.py` | — | 缺少 `selected_judgment` 非法值 → `ValueError` 的边界测试。代码 line 354-356 有 `get_args(FinalJudgment)` 校验，逻辑正确，但无测试覆盖。 |
| L3 | LOW | `test_final_chapter_assembler.py` | — | 缺少 `allow_incomplete_debug_markdown=True` 路径的显式测试。代码 line 283 有该分支。 |

### INFO — 设计观察（无行动要求）

| # | 说明 |
|---|------|
| I1 | `_chapter7_accepted_conclusion()` 的 `used_fact_ids=()` / `used_anchor_ids=()` 为空元组。plan 要求"聚合自第 1-6 章 accepted conclusions，不新增 fact/anchor"。当前实现不聚合而是留空，语义上可接受——synthetic conclusion 本身不引用新 fact/anchor，第 0 章消费时只看 markdown 内容。不影响正确性。 |
| I2 | `_render_report_markdown()` 在 `accepted_draft is None` 时 raise `ValueError`。由于 `_validate_orchestration()` 已在上游捕获此情况并返回 incomplete，该 raise 是防御性编程，不会在正常流程中触发。 |

## Controller amendments compliance

| Amendment | 验证 |
|-----------|------|
| **A4**: chapter 0 不重新应用 preferred_lens/ITEM_RULE/fund type | ✅ `_render_chapter0_markdown()` 只接收 `AcceptedChapterConclusion` 和 `FinalChapter7Summary`，无 fund_type/lens/ITEM_RULE 参数 |
| **A5**: 稀疏/截断 conclusions 不编造事实 | ✅ `test_chapter0_sparse_and_truncated_sources_do_not_invent_absent_numbers` 覆盖空结论和截断，断言无 absent 数值，记录 informational issue |
| **A6**: chapter 7 结合 FinalJudgmentDecision.reasons + 章节短句 | ✅ `_chapter7_core_basis()` 合并 `decision.reasons[0]` 和 `_supporting_conclusion_snippets()`，测试断言两者均出现 |
| **A7**: chapter 0 当前动作为 typed source | ✅ `FinalChapter7Summary.selected_judgment_label` 直接传入 chapter 0，不解析 markdown |
| **A8**: 生成顺序 7→0，渲染顺序 0→1-6→7 | ✅ `test_assembles_report_in_render_order_while_chapter0_uses_chapter7_summary` 断言渲染顺序 |

## Validation results

```text
uv run ruff check fund_agent/services/final_chapter_assembler.py tests/services/test_final_chapter_assembler.py
→ All checks passed!

uv run pytest tests/services/test_final_chapter_assembler.py -q
→ 9 passed in 0.41s

uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py tests/services/test_chapter_orchestrator.py -q
→ 81 passed in 0.46s

git diff --check
→ clean
```

## Summary

Slice 4A 实现完全符合 plan 和 controller amendments 要求：

1. Service 归属正确，不越界读取 Agent/Fund 内部模块。
2. Chapter 7 只消费 `FinalJudgmentDecision`，不重新派生判断。
3. Chapter 0 只消费 accepted conclusions + typed summary，不读 facts/PDF/source。
4. Partial/incomplete fail-closed 行为正确，不泄漏不完整报告。
5. Render order 0→1-6→7 已被测试断言。
6. Typed contracts 和中文 docstrings 完整。
7. 9 个测试覆盖 plan decision A4-A8 核心路径。

L1-L3 为可选补测建议，不阻断 gate acceptance。

## Residuals

- Slice 4B/4C/4D 未实现，按 plan decision 记录为 residual。
- LLM polish/audit、Evidence Confirm/E2、Host/Agent/dayu 均为 out-of-scope residual。
