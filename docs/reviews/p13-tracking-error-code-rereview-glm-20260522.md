# Code Re-Review

## Scope

- Mode: targeted re-review (finding closure only)
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main`
- Output file: `docs/reviews/p13-tracking-error-code-rereview-glm-20260522.md`
- Prior reviews:
  - `docs/reviews/p13-tracking-error-code-review-glm-20260522.md` — GLM F1, F2
  - `docs/reviews/p13-tracking-error-code-review-mimo-20260522.md` — MiMo finding 1
- Included scope: only the three findings from the two prior reviews
- Excluded scope: all other P13 implementation code unchanged since prior reviews
- Controller validation: profile/performance 31 passed, renderer 38 passed, audit 36 passed, `ruff check` passed, `git diff --check` passed

## Finding Closure

| # | Source | Finding | Status | Evidence |
|---|--------|---------|--------|----------|
| GLM F1 | GLM review | `_benchmark_components` 仅拆分 `+`/`＋`，遗漏 `和`/`及`/`×`/`*` | **已修复** | `profile.py:592` — `re.split(r"[＋+×*]\|和\|及", benchmark_text)` 覆盖 `_COMPOSITE_BENCHMARK_SEPARATORS` 全部 6 种分隔符。测试 `test_extract_profile_splits_composite_benchmark_with_chinese_and_multiply_separators` 验证 `×` 和 `和` 分隔符场景。 |
| GLM F2 | GLM review | 表格和正文同一跟踪误差值误判 ambiguous | **已修复** | `performance.py:361-364` — 双命中时调用 `_select_consistent_tracking_error_match`，比较 `_parse_percent_ratio` 解析的 Decimal 值：一致返回 `table_match`，不一致返回 `None`（ambiguous）。测试 `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error` 验证一致场景保留表格锚点；`test_extract_performance_marks_table_text_conflicting_tracking_error_as_ambiguous` 验证不一致场景 fail closed。 |
| MiMo 1 | MiMo review | 渲染器用 `assert` 做运行时完整性校验 | **已修复** | `renderer.py:669-671` — `assert tracking_error.value is not None` 替换为显式 `if value is None: return _render_tracking_error_insufficient(anchors)`。Python `-O` 模式下不再跳过校验。 |

## Verdict

**PASS**

三项 finding 均已按建议修复，修复范围仅限于 finding 指出的代码路径和对应测试，未引入 scope creep。Controller 和 worker 验证全部通过。
