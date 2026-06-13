# Plan Review — 004393 / 2025 Tracked Golden Content Write Plan

Date: 2026-06-13

Reviewer: MiMo plan reviewer

Reviewed target: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-20260613.md`

Gate: `004393 / 2025 Tracked Golden Content Write Planning Gate`

## 1. Scope

This review assesses whether the plan correctly decides source-body verification
before tracked golden content write, correctly excludes fee rows, safely lists
accepted candidate rows, bounds future write scope, provides sufficient and safe
validation commands, and has complete stop conditions and residual owners.

## 2. Assumptions Tested

| # | Assumption | Evidence source | Result |
|---|---|---|---|
| A1 | Source-body verification must precede tracked write. | Plan §Decision; controller judgment `ACCEPT_WITH_FINDINGS_NOT_READY`; evidence boundary "did not read the 2025 annual-report body directly" | Correct. Candidate-level acceptance is not a correctness oracle. |
| A2 | Two fee rows are correctly excluded. | `docs/golden-answer-instructions.md` §Step 6 marks `fee_schedule` as skipped; `docs/golden-answer-template.md` has `fee_schedule — — — 当前 slice 不处理`; candidate rows have `年报2025 §5 management_fee` / `custody_fee` without page/table/row specificity | Correct. Template contract and locator quality both support exclusion. |
| A3 | Seven accepted candidate rows are exactly those in the candidate artifact. | Candidate artifact has 9 rows; evidence/controller judgment accepted 7 and rejected 2 fee rows; plan row disposition table lists exactly 7 `ACCEPT_CANDIDATE_*` rows matching the non-fee rows | Correct. Row list is exact and safe. |
| A4 | Future write scope is sufficiently bounded. | Plan §Proposed implementation/write scope; accepted write set is 3 implementation + 3 review/controller files; content edit shape is one `## 004393 ...` block with `report_year: 2025` | Correct. Write set and edit shape are explicit. |
| A5 | Validation commands prevent accidental overwrite of unrelated golden content. | Plan §Validation matrix "No tracked-output overwrite accident" row; `golden-answer.json` currently has 11 funds / 150 records; JSON rebuild from reviewed Markdown is the only write path | Mostly correct. The git diff comparison catches file-level and key-level drift. See F1 for the preservation gap. |
| A6 | Stop conditions and residual owners are complete. | Plan §Stop conditions (8 items) and §Residuals (5 items) | Correct. Stop conditions cover body-load failure, row mismatch, span ambiguity, formula drift, fee leakage, JSON hand-edit, unrelated mutation, and unauthorized actions. Residuals have explicit owners and destinations. |

## 3. Findings

### F1-未修复-中-JSON rebuild 不含 existing-content preservation 断言

- **位置**: Validation matrix — "Strict JSON build" row and "No tracked-output overwrite accident" row
- **问题类型**: 测试缺口
- **当前写法**: "Strict JSON build" 验证命令只检查 JSON 重建无 schema error；"No tracked-output overwrite accident" 用 `git show HEAD` 与 working tree 对比 `(fund_code, report_year, field_name, sub_field)` 键集。
- **反例/失败场景**: Implementation agent 在往 `golden-answer-prefill-reviewed.md` 追加 `004393/2025` block 时意外删除或改写了现有 2024 基金 block（当前文件有 268 行、11 只基金、150 条记录）。JSON 从 Markdown 全量重建，Markdown 中丢失的内容会直接导致 JSON 中对应记录消失。git diff 键集对比能捕获此类变更，但 diff 本身不区分"预期新增"和"意外丢失"——implementation agent 需要人工判读 diff 输出才能发现问题。
- **为什么有问题**: 当前 `golden-answer-prefill-reviewed.md` 包含 6 只基金的 2024 golden rows，这些是已 accepted 的 tracked strict golden truth。如果 implementation agent 在追加 2025 内容时误操作，已有的 2024 correctness oracle 基线会被破坏，直接影响 FQ1/block 正确性比对。
- **直接证据**: `reports/golden-answers/golden-answer.json` 当前 `fund_count=11, record_count=150`；`reports/golden-answers/golden-answer-prefill-reviewed.md` 当前 268 行；`build_golden_answer_json()` 从 Markdown 全量重建 JSON（`fund_agent/fund/golden_answer.py:131-164`）。
- **影响**: 已有 2024 golden rows 被意外删除或改写时，extraction_score correctness 比对基线丢失，quality gate FQ1 行为变化可能被掩盖。
- **建议改法和验证点**: 在 validation matrix 中增加一条 "Existing content preservation" 检查：重建 JSON 后 load 并断言原有 11 只基金的 fund_code 和 record_count 不变（或 `git diff --stat -- reports/golden-answers/golden-answer.json` 仅显示新增行、无删除行）。implementation agent 的 commit message 也应注明"追加 004393/2025 block，未修改现有内容"。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### F2-未修复-低-JSON build 命令无显式错误捕获

- **位置**: Validation matrix — "Strict JSON build" row
- **问题类型**: 最佳实践偏离
- **当前写法**: `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import build_golden_answer_json; print(build_golden_answer_json(input_path=Path('reports/golden-answers/golden-answer-prefill-reviewed.md'), output_path=Path('reports/golden-answers/golden-answer.json')))"` — 命令通过 `print()` 输出结果，但无显式 assert 或 `sys.exit(1)` 逻辑。
- **反例/失败场景**: 如果 `build_golden_answer_json` 内部捕获了异常但仍然输出了部分结果，`print()` 不会暴露问题。实际上当前代码在 validation error 时会抛 `GoldenAnswerValidationError`，Python 会以非零退出码退出，所以当前实现是安全的。但如果未来代码变更引入了静默降级，此命令可能不再足够。
- **为什么有问题**: 当前实现安全，但验证命令依赖隐式异常传播而非显式断言，属于 fragile validation。
- **直接证据**: `fund_agent/fund/golden_answer.py:131-164` — `build_golden_answer_json` 调用 `parse_golden_answer_markdown` 后写入 JSON；`parse_golden_answer_markdown` 在 errors 非空时 raise `GoldenAnswerValidationError`。
- **影响**: 低。当前 Python 异常传播机制保证了非零退出码。但后续 "Strict JSON load" 行的验证命令包含显式 `assert len(matches)==1`，风格不一致。
- **建议改法和验证点**: 在 build 命令末尾增加 `assert result.record_count > 0` 或等价显式断言，与 load 命令风格一致。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### F3-未修复-低-source-body verification gate 未指定文档读取路径

- **位置**: Plan §Proposed implementation/write scope — "Minimum controlled source-body verification scope" 第一条
- **问题类型**: 契约缺失
- **当前写法**: "Read only the 2025 annual-report body for 004393 through the project-authorized document repository boundary."
- **反例/失败场景**: Implementation agent 进入 source-body verification gate 时，可能不清楚应使用 `FundDocumentRepository.load_annual_report()` 还是直接读取 `基金年报/` 下的 PDF 文件。根据 `AGENTS.md` 硬约束，生产年报访问必须通过 `FundDocumentRepository`；但 source-body verification 是 review/gate 操作，不是生产路径，边界可能被误判。
- **为什么有问题**: `docs/design.md` §6.1 明确"对基金文档的存取统一通过 FundDocumentRepository，禁止直接操作文件系统"。如果 verification gate 的 implementation agent 绕过 repository 直接读 PDF，会违反该约束。
- **直接证据**: `AGENTS.md` "对基金文档的存取，都应该只通过统一的文档仓库接口，禁止直接操作文件系统"；`docs/design.md` §6.1 "FundDocumentRepository —— 对外唯一文档读取入口"。
- **影响**: 低。这是对未来 gate 的 guidance gap，不是当前 planning gate 的 blocker。但明确路径可避免 implementation agent 重新决策。
- **建议改法和验证点**: 在 source-body verification scope 中注明"通过 `FundDocumentRepository.load_annual_report()` 或等价受控路径读取"。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 4. Open Questions

无。所有 review lens 问题已在 findings 中覆盖。

## 5. Residual Risks

| Risk | Severity | Tracking destination |
|---|---|---|
| Source-body verification 可能发现 candidate row expected_value 与年报原文不一致，需要修正或拒绝部分行。 | Medium | `004393 / 2025 Controlled Source-body Verification Gate` |
| `product_profile.investment_objective` 长文本 span 边界可能在 source-body verification 后仍需调整。 | Medium | Source-body verification gate — row-specific judgment |
| `benchmark.benchmark_name` 公式字符、百分比权重、指数名称、汇率调整措辞可能与年报原文有微小差异。 | Medium | Source-body verification gate — row-specific judgment |
| Fixture promotion 仍然 year-blind，无法表达 `004393 / 2025` 特定 promotion。 | Low | Separate fixture promotion design/evidence gate |

## 6. Conclusion

**Verdict: PASS_WITH_FINDINGS**

Plan 正确决策了 source-body verification 前置于 tracked golden content write。Fee row 排除理由充分。七条 accepted candidate rows 列表准确。未来 write scope 边界清晰。Stop conditions 和 residual owners 完整。

三个 findings 均为 non-blocking：

- F1（中）：validation matrix 缺少 existing-content preservation 断言，建议在 JSON rebuild 后增加已有基金不变性检查。
- F2（低）：JSON build 命令风格与 load 命令不一致，建议增加显式断言。
- F3（低）：source-body verification scope 未指定文档读取路径，建议注明 `FundDocumentRepository`。

无 blocking findings。Plan 可进入 controller judgment。

## 7. Next Entry Recommendation

```text
004393 / 2025 Tracked Golden Content Write Plan Controller Judgment
```
