# P5-S2 Code Review - 2026-05-20

## Findings

### P5S2-CR-1 - 已修复 - 高 - FQ5 派生路径没有随 App 类别冲突变成 mismatch

- 入口 / 触发输入：`derive_fund_quality_records(...)` 处理 `app_category="国内债券类"` 且 `classified_fund_type="active_fund"` 的 snapshot records。
- 期望行为：P5-S2 plan 要求 App 类别可明确映射但与系统基金类型冲突时，FQ1 表达类型冲突，FQ5 表达 preferred_lens 选择不可信。
- 原实现行为：`_preferred_lens_status(...)` 只检查 `classified_fund_type` 是否能解析 `preferred_lens_key`。因此真实派生出的 `fund_quality` 会是 `app_category_status=conflict` 但 `preferred_lens_status=match`。
- 影响：quality gate 会触发 FQ1，但不会触发 FQ5；P5-S2 plan 中“类型冲突导致 lens 选择不可信”的验收信号没有被真实 score 派生路径覆盖。
- 修复：`_preferred_lens_status(...)` 显式接收 `app_category_status`，当 `app_category_status=conflict` 时返回 `mismatch`。
- 回归测试：新增 `test_derive_fund_quality_records_marks_lens_mismatch_on_app_category_conflict()`，从 snapshot 派生路径验证 `preferred_lens_status=mismatch`。
- 严重程度：高。

## Open Questions

无。

## Residual Risk

- FQ5 当前仍是 preferred_lens resolvability，不是最终报告 CHAPTER_CONTRACT lens 校验；该边界已写入 plan 和 implementation artifact。
- P5-S3 仍负责扩大 correctness denominator。
- P5-S4 仍负责失败基金只落 `errors.jsonl` 时的 fund-level accounting。

## Validation

- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`: `37 passed`
- `.venv/bin/ruff check .`: passed
- `git diff --check`: passed

## Conclusion

`pass after fix`

P5-S2 implementation can move to full validation and acceptance.
