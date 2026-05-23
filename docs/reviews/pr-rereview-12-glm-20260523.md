# PR Re-Review

## Scope

- Mode: PR Re-Review
- PR: https://github.com/bill20232033cc/fund-agent/pull/12
- Branch: fix/repo-deepreview-audit-type-guards -> main
- Base: main
- Source review: docs/reviews/pr-review-12-glm-20260523.md
- Fix artifact: docs/reviews/pr-fix-12-glm-low-findings-20260523.md
- Latest commit: 7b5edbd
- CI: test pass (run 26318388067, 551 passed, ruff passed)
- Output file: docs/reviews/pr-rereview-12-glm-20260523.md

## Finding Verification

### 01-已修复-低-test_analyze_cli_help 宽度依赖

- **状态**: 已修复
- **验证**: CI run 26318388067 通过；test_cli.py:961 已设 `env={"COLUMNS": "120"}` 并改用 `get_command().params` 元数据断言，非渲染文本断言
- **结论**: closed

### 02-已修复-低-inception_date 测试 fixture 缺失

- **状态**: 已修复
- **验证**: `_bundle()` basic_identity 已加入 `"inception_date": "2020-01-15"`（test_renderer.py:199）；新测试 `test_render_template_report_renders_chapter_0_profile_with_inception_date`（test_renderer.py:759-774）断言渲染输出包含 `成立时间 2020-01-15`
- **结论**: closed

### 03-已修复-低-checklist bool guard 测试仅覆盖 True

- **状态**: 已修复
- **验证**: `test_run_checklist_rejects_bool_money_horizon_years`（test_checklist.py:406-418）改为 `for value in (True, False):` 循环，两个值均断言 `ValueError("不能为布尔值")`
- **结论**: closed

### 04-已修复-低-thermometer_source._to_decimal 缺少 bool guard

- **状态**: 已修复
- **验证**: `_to_decimal`（thermometer_source.py:262-263）新增 `if isinstance(value, bool): raise ThermometerSourceError(f"{field_name} 不能为布尔值")`；新测试 `test_akshare_index_source_rejects_bool_valuation_values`（test_thermometer_source.py:171-191）使用 `True` 作为 PE 值断言 `ThermometerSourceError("不能为布尔值")`
- **结论**: closed

## New Findings

无。

## CI Status

- Run 26318388067: test pass, 551 passed, ruff passed
- Commit: 7b5edbd

## Residual Risk

- 24 条 `narrative_guidance` must_not_cover 覆盖规则依赖下游 LLM 语义审计或人工复核，当前无自动化闭环验证
- `thermometer_cache.py` 非原子 `write_text`，并发场景理论风险（单用户 CLI 不触发）
- P19-S4 扩展指数覆盖 deferred，5 个目标指数无已验证 PE+PB 历史数据源
- P19-S5 全 A 市场 PE 历史来源未解决
