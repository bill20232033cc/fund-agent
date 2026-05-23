# Code Review

## Scope

- Mode: PR Review
- PR: https://github.com/bill20232033cc/fund-agent/pull/12
- Branch: fix/repo-deepreview-audit-type-guards -> main
- Base: main
- Output file: docs/reviews/pr-review-12-glm-20260523.md
- Included scope: PR 12 完整 diff（24 commits，96 files），重点审查 CHAPTER_CONTRACT must_not_cover coverage accounting、Ch0 marker 拆分、bool guard 覆盖、aggregate fix 后风险、CI 状态
- Excluded scope: docs/reviews/ 下 P19 历史 review artifacts（纯记录文档，非生产代码）；docs/p19-*.md 输入文档
- Parallel review coverage: 5 个 subagent 分别覆盖 audit/contract_rules、template/renderer、valuation_state/checklist、service/CLI、thermometer calculator/data

## PR Facts

- Repository: bill20232033cc/fund-agent
- PR Number: 12
- Title: Fix contract audit coverage and numeric bool guards
- Author: bill20232033cc
- Head: fix/repo-deepreview-audit-type-guards
- Base: main
- State: OPEN
- Commits: 24
- CI: test pass (run 26318095338)

## Findings

### 01-未修复-低-test_analyze_cli_help 宸剧宽度依赖

- **入口/函数**: `tests/ui/test_cli.py::test_analyze_cli_help_documents_auto_valuation_and_opt_out`
- **文件(行号)**: tests/ui/test_cli.py:961-975
- **输入场景**: CI runner 默认终端宽度窄于 Rich 渲染长选项所需宽度
- **实际分支**: PR 已在 commit 中修复：设置 `env={"COLUMNS": "120"}` 并改用 `get_command().params` 元数据检查替代渲染文本断言
- **预期行为**: help 输出测试在任何终端宽度下确定性通过
- **实际行为**: 早期 commit 在 CI 上因 Rich 截断 `--thermometer-cache-dir` 而失败；最新 commit 已修复
- **直接证据**: CI run 26317892560 失败（`AssertionError: assert '--thermometer-cache-dir' in ...`）；run 26318095338 通过
- **影响**: 仅为测试稳定性问题，不影响生产代码行为
- **建议改法和验证点**: 已修复，无需额外操作
- **修复风险（低）**: 低
- **严重程度（低）**: 低

### 02-未修复-低-inception_date 测试 fixture 缺失

- **入口/函数**: `tests/fund/template/test_renderer.py::_bundle()`
- **文件(行号)**: tests/fund/template/test_renderer.py:190-201
- **输入场景**: `_bundle()` 中 `basic_identity` 未包含 `inception_date` 键
- **实际分支**: `_value_text()` 返回 `"未披露"` 兜底文本，渲染不报错
- **预期行为**: 测试应覆盖 `inception_date` 有值和缺失两种路径
- **实际行为**: 所有 renderer 测试中 `inception_date` 均走缺失路径，有值路径零覆盖
- **直接证据**: `renderer.py:333` `fund_manager = _value_text(identity, "inception_date")`（实际变量名为 `inception_date`），`_value_text` 在 key 不存在时返回 `_MISSING_TEXT`
- **影响**: 仅影响测试覆盖，不影响生产渲染正确性（`_value_text` 缺失路径已被其他字段充分测试）
- **建议改法和验证点**: 在 `_bundle()` 中加入 `"inception_date": "2020-01-15"` 并验证渲染输出包含实际日期
- **修复风险（低）**: 低
- **严重程度（低）**: 低

### 03-未修复-低-checklist bool guard 测试仅覆盖 True

- **入口/函数**: `tests/fund/analysis/test_checklist.py::test_run_checklist_rejects_bool_money_horizon_years`
- **文件(行号)**: tests/fund/analysis/test_checklist.py:414
- **输入场景**: `user_money_horizon_years=True` 被测试，`False` 未被测试
- **实际分支**: `isinstance(True, bool)` 拦截成功；`False` 路径未被断言验证
- **预期行为**: `True` 和 `False` 均应被拒绝
- **实际行为**: `isinstance(False, bool)` 同样为 `True`，逻辑正确但测试不对称
- **直接证据**: 其他模块（_ratios、risk_check、investor_return）的 bool guard 测试同时覆盖 `True` 和 `False`；checklist 仅为 `True`
- **影响**: `isinstance(False, bool)` 逻辑无错，仅测试覆盖不对称
- **建议改法和验证点**: 补充 `user_money_horizon_years=False` 的断言
- **修复风险（低）**: 低
- **严重程度（低）**: 低

### 04-未修复-低-thermometer_source._to_decimal 缺少 bool guard

- **入口/函数**: `fund_agent/fund/data/thermometer_source.py::_to_decimal()`
- **文件(行号)**: fund_agent/fund/data/thermometer_source.py:247-266
- **输入场景**: 原始数据记录 PE/PB 字段为 `True` 或 `False`
- **实际分支**: `Decimal(str(True))` 抛出 `InvalidOperation`，fail-closed
- **预期行为**: 与 PR 中其他 `_parse_decimal` 统一，显式 `isinstance(value, bool)` 拒绝并给出清晰错误信息
- **实际行为**: 以 `InvalidOperation` 而非 `"不能为布尔值"` 错误信息失败
- **直接证据**: `thermometer_source.py:210` `value = _to_decimal(raw.get(col), col)`；`_to_decimal` 无 bool guard；`_ratios.py:31-32`、`checklist.py:748`、`risk_check.py:983` 均已添加 bool guard
- **影响**: 功能上 fail-closed（不会产生错误结果），但错误信息不一致，调试困难
- **建议改法和验证点**: 在 `_to_decimal` 开头添加 `if isinstance(value, bool): raise ThermometerSourceError(f"{field_name} 不能为布尔值")`
- **修复风险（低）**: 低
- **严重程度（低）**: 低

## 核心审查结论（无 finding 区域）

### CHAPTER_CONTRACT must_not_cover coverage accounting

`contract_rules.py` 的 `_validate_must_not_cover_coverage_rules`（lines 658-701）实施 4 不变量验证：无重复、无未知引用、无程序化规则重叠、全覆盖。24 条 `narrative_guidance` 覆盖规则均附带 rationale，且 rationale 为空时 fail-closed。`narrative_guidance` 路由是设计意图（C2 marker 无法验证语义约束），不是掩码 bug。验证流程正确，测试覆盖 4 条 fail-closed 路径。

### Ch0 marker 拆分

旧代码两个 required item 共享 marker `"基金："`, 审计无法独立验证。新代码拆分为 `"这是什么基金："` 和 `"基金简介："`，与 `renderer.py:340-341` 渲染输出一致。`test_chapter_0_required_items_use_distinct_markers` 断言 marker 不相交。章节分割逻辑无 Ch0 特殊处理，正则 `r"(?m)^#\s+(\d+)\.\s+(.+?)\s*$"` 正确匹配 `0.` 开头的标题。

### bool guard 覆盖

5 个生产文件 7 处 bool guard 均正确放置在 `isinstance(value, int | float)` 之前。Python `bool <: int` 关系被正确处理。`quality_gate.py` 使用复合 `isinstance(value, bool) or not isinstance(value, int | float)` 形式同样正确。所有数值入口（`_parse_decimal`、`_required_number`、`_required_quality_number`）均已覆盖。

### aggregate fix 后风险

PR 包含 24 commits，覆盖 P19-S1 到 P19-S3 全部实现和 review/fix 循环。aggregate fix 在 `docs/reviews/aggregate-fix-repo-deepreview-audit-type-guards-20260523.md` 中记录。各 subagent 确认无逻辑错误、无边界条件缺陷、无状态机回归。

### CI 状态

CI run 26318095338: test pass。早期 run 26317892560 因 help 文本宽度截断失败，已在后续 commit 修复。

## Open Questions

- 无

## Residual Risk

- `thermometer_source.py:_to_decimal()` 缺少 bool guard，功能 fail-closed 但错误信息与 PR 中其他模块不一致（Finding 04）
- `_bundle()` 测试 fixture 缺少 `inception_date`，renderer 有值路径零覆盖（Finding 02）
- `test_checklist.py` bool guard 测试仅覆盖 `True` 未覆盖 `False`（Finding 03）
- 24 条 `narrative_guidance` must_not_cover 覆盖规则依赖下游 LLM 语义审计或人工复核，当前无自动化闭环验证
- `thermometer_cache.py:107` 使用非原子 `write_text`，并发场景下可能读到部分写入；`load()` 侧 `try/except` 兜底降级为 cache miss
- P19-S4 扩展指数覆盖已 deferred，5 个目标指数无已验证 PE+PB 历史数据源
- P19-S5 全 A 市场 PE 历史来源未解决，全 A 温度计等待 source gate
