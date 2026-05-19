# Code Review

## Scope

- Mode: current changes
- Branch: `main`
- Base: `main`
- Output file: `docs/reviews/p4-aggregate-rereview-glm-20260519.md`
- Included scope: P4 aggregate fix（per-fund score / quality gate blocking）+ style_positioning field-contract reconciliation
- Excluded scope: reports/golden-answers 生成或手动审核的 Markdown；未提交的 untracked 文件
- Parallel review coverage: 无 subagent；主 reviewer 独立走读全部 22 个变更文件

## Verdict

**PASS**

P4 aggregate fix 的核心 blocking finding（F1：score / quality gate 缺少 per-fund 粒度）已被正确实现并测试覆盖。style_positioning 字段收口到 product_profile 的变更与主链路一致。control docs 和 README 已同步当前契约。未发现 blocking 或高严重程度 finding。

## Findings

未发现实质性问题。

以下为低严重程度观察，不阻塞 gate：

### O1-未修复-低-单基金 P1 fail 未独立测试

- **入口/函数**: `quality_gate._evaluate_fund_score`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:277-287`
- **输入场景**: 单基金 p1_status=fail 但 p0_status=pass，且字段聚合全部 pass
- **实际分支**: `_evaluate_fund_score` 正确生成 `FQ2F/warn` issue，gate 状态为 `warn`
- **预期行为**: 按当前设计应生成 warn 而非 block
- **实际行为**: 实现正确，但缺少该场景的独立测试
- **直接证据**: `tests/fund/test_quality_gate.py` 中 `test_run_quality_gate_blocks_single_fund_p0_failure_even_when_field_aggregate_passes` 只测试 P0 fail 场景；P1 fail 的 fund-level warn 只有字段级测试 `test_run_quality_gate_warns_failed_p1_without_blocking` 覆盖
- **影响**: 无正确性风险，仅 test coverage gap
- **建议改法和验证点**: 可在后续 test hardening slice 补充 `test_run_quality_gate_warns_single_fund_p1_failure_even_when_field_aggregate_passes`
- **修复风险（低）**: 低
- **严重程度（低）**: 低

## Adversarial Failure Pass

以下为 adversarial pass 中逐一验证的场景：

1. **per-fund gate backward compatibility**: `_evaluate_score_payload` 对 `fund_scores` 使用 `score_payload.get("fund_scores")` + `if fund_scores is not None`。旧版 score.json 无 `fund_scores` 时只走 field_scores 路径，不报错、不遗漏。正确。

2. **fund 只有 P2 字段记录时 p0_status**: `_aggregate_status([])` 返回 `STATUS_FAIL`。若 snapshot 只含 P2 字段，该 fund 的 p0_status=fail 触发 block。这是保守但正确的默认行为。

3. **fund_code 缺失的 snapshot 记录**: `score_fund_records` 内 `_required_text(record, "fund_code")` 抛出 ValueError。不会静默跳过。正确。

4. **重复 fund_code**: `score_fund_records` 按 `fund_code` 聚合，同一基金的多条记录正确合并。正确。

5. **空 fund_scores 数组**: `_evaluate_score_payload` 中 `for index, raw_row in enumerate(fund_scores)` 不执行循环，无 issue 生成。只靠 field_scores 判断。正确。

6. **style_positioning 回退链**: `consistency_check._check_investment_style` 优先读 `product_profile` 的 `style_positioning / investment_strategy / investment_objective`，为空时回退到 `manager_strategy_text.strategy_summary`。`profile._build_product_profile` 优先从 §2 显式字段读，为空时调用 `_derive_style_positioning(objective)` 从投资目标提炼。回退链合理，不会产生静默空值。

7. **golden-answer-template 一致性**: 6 只基金模板均已将 `style_positioning` 从 `manager_strategy_text` 迁移到 `product_profile`。一致。

8. **Service 层 contract change**: `check_consistency()` 新增 `product_profile` 必选参数。`FundAnalysisService` 已传入 `structured_data.product_profile`。所有调用方已对齐。

## Design / Control / Code Reconciliation

| 项 | design.md | implementation-control-p4.md | 当前代码事实 | 裁决 |
|---|---|---|---|---|
| per-fund score | 北极星要求避免内容不可用报告误导用户 | P4-R7: score 输出 fund_scores | `ExtractionScoreResult.fund_scores` + `score.json` fund_scores | aligned |
| per-fund gate blocking | 同上 | P4-R7: quality gate 单基金 P0 fail 阻断 | `FQ2F/block` with fund_code | aligned |
| style_positioning 收口 | 未细化 | 未涉及 | profile.py 新增, manager_ownership.py 移除 | aligned with field reconciliation |
| quality gate 未接入 analyze | 设计 gap | P4-R8: deferred to integration slice | gate 仍只消费 score.json | aligned, deferred |
| FQ1/FQ4/FQ5 | 候选规则 | P4-R9: deferred | 未实现 | aligned, deferred |
| correctness | P4-S2 后半段 | P4-R10: deferred | FQ0/info | aligned, deferred |
| README 同步 | 控制文档要求 | 状态回写 | README / fund README / tests README 已同步 score/gate 契约 | aligned |

## Tests Run

```bash
# P4 aggregate fix 主测试
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_fund_analysis_service.py -v
# 结果: 13 passed

# style-positioning 相关测试
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_manager_ownership.py tests/fund/analysis/test_consistency_check.py tests/fund/template/test_renderer.py tests/fund/test_golden_prefill.py -v
# 结果: 37 passed

# Lint
.venv/bin/ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py
# 结果: All checks passed!

# Whitespace
git diff --check
# 结果: 无输出（通过）
```

未能运行: `tests/ui/test_cli.py`（scope 外 CLI 测试）、全量覆盖率矩阵（非本次 re-review scope）。

## Open Questions

无。

## Residual Risk

- **O1 test gap**: 单基金 P1 fail 的 fund-level warn 场景缺少独立测试。可在后续 test hardening slice 补充。严重程度低。
- **P4-R8**: quality gate 未接入 `analyze` 主链路。作为后续 `quality gate integration slice` owner 追踪，不影响当前 gate。
- **P4-R9**: FQ1/FQ4/FQ5 未实现。延后到 `quality gate rules slice`。
- **P4-R10**: correctness 自动比对未实现。延后到用户完成人工审核 golden JSON 后的 `correctness slice`。
- **完全缺失基金的 gate 覆盖**: 若某只基金在 snapshot 中无任何记录（snapshot 生成阶段就失败），则该基金不出现在 `fund_scores` 中，quality gate 无法对它生成 issue。这是 P4-S1 snapshot 生成层面的 concern，不阻塞当前 P4 aggregate fix gate。
