# Code Re-Review

## Scope

- Mode: current changes (targeted re-review of prior findings)
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main`
- Output file: `docs/reviews/p13-tracking-error-code-rereview-mimo-20260522.md`
- Included scope: 3 findings from `p13-tracking-error-code-review-mimo-20260522.md` (MiMo) and `p13-tracking-error-code-review-glm-20260522.md` (GLM F1, F2)
- Excluded scope: `docs/repo-audit-20260521.md`, unchanged files, residual-risk items

## Finding Closure Table

| Finding | Source | Severity | Status | Evidence |
|---|---|---|---|---|
| MiMo: renderer assert 做运行时完整性校验 | MiMo review #1 | 低 | **closed** | `assert tracking_error.value is not None` 已替换为 `if value is None: return _render_tracking_error_insufficient(anchors)`；提取 `_render_tracking_error_insufficient()` helper；新增 `test_render_template_report_defensively_handles_missing_tracking_error_value` 测试 |
| GLM F1: 复合基准拆分仅处理 `+`/`＋` | GLM review F1 | 低 | **closed** | `re.split(r"[＋+]", ...)` 已扩展为 `re.split(r"[＋+×*]\|和\|及", ...)`，与 `_COMPOSITE_BENCHMARK_SEPARATORS` 一致；新增 `test_extract_profile_splits_composite_benchmark_with_chinese_and_multiply_separators` 测试，验证 `×` 和 `和` 分隔符 |
| GLM F2: 表格和正文同时命中同一跟踪误差值时误判 ambiguous | GLM review F2 | 低 | **closed** | 无条件 fail-closed 已替换为 `_select_consistent_tracking_error_match(table_match, text_match)`，比较两者解析值：值相等时优先返回 table_match（有更精确锚点），不等时返回 `None` 触发 ambiguous；新增 `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error` 和 `test_extract_performance_marks_table_text_conflicting_tracking_error_as_ambiguous` 测试 |

## Fix Details

### MiMo: renderer assert → explicit early return

`fund_agent/fund/template/renderer.py` — `_render_tracking_error_segment`:

- Old: `assert tracking_error.value is not None` followed by `value = tracking_error.value`
- New: `if value is None: return _render_tracking_error_insufficient(anchors)` — explicit defensive check
- Extracted `_render_tracking_error_insufficient()` helper to share insufficient-data rendering logic
- Test: `test_render_template_report_defensively_handles_missing_tracking_error_value` constructs a field with `extraction_mode="direct"` but `value=None` and verifies renderer produces `数据不足` without crashing

### GLM F1: composite benchmark split coverage

`fund_agent/fund/extractors/profile.py` — `_benchmark_components`:

- Old: `re.split(r"[＋+]", benchmark_text)` — only split on `+`/`＋`
- New: `re.split(r"[＋+×*]|和|及", benchmark_text)` — covers all `_COMPOSITE_BENCHMARK_SEPARATORS`
- Test: `test_extract_profile_splits_composite_benchmark_with_chinese_and_multiply_separators` uses benchmark text `"沪深300指数收益率×80%和中证500指数收益率×20%"` and verifies `benchmark_identity_status == "composite"` and correct component splitting

### GLM F2: table+text same value consistency check

`fund_agent/fund/extractors/performance.py` — `_extract_tracking_error`:

- Old: `if table_match is not None and text_match is not None: return _missing_tracking_error("tracking_error_ambiguous")` — unconditional fail-closed
- New: calls `_select_consistent_tracking_error_match(table_match, text_match)` which compares `_parse_percent_ratio()` of both matches; equal values return `table_match` (better anchors), unequal return `None` triggering ambiguous
- Tests: `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error` (same value → table preserved) and `test_extract_performance_marks_table_text_conflicting_tracking_error_as_ambiguous` (different values → ambiguous)

## Residual Risk

- 无新增 residual risk。三个 finding 均为低严重度修复，修改范围小且有对应测试覆盖。

## Verdict

**PASS**

三个 finding 全部 closed。MiMo assert 替换为显式 early return，GLM F1 复合基准拆分覆盖全部分隔符，GLM F2 表格+正文一致性检查取代无条件 fail-closed。每个修复均有对应新增测试验证。
