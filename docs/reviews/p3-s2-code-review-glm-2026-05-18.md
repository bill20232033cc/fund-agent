# P3-S2 Code Review (GLM)

Date: 2026-05-18
Gate: P3-S2 code review
Reviewer: AgentGLM
Scope: P3-S2 thermometer adapter uncommitted changes — `fund_agent/fund/data/thermometer.py`, `fund_agent/fund/data/__init__.py`, `tests/fund/data/test_thermometer.py`, `README.md`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/implementation-control.md`

Design truth: `docs/design.md`
Control truth: `docs/implementation-control.md`

Reviewed against latest workspace state including all controller corrections (index-table header selection, code-in-name-cell, treasury maturity-yield label, cache-write failure isolation). Latest validation: thermometer tests 12 passed; broader regression 59 passed; `git diff --check` clean.

---

## Findings

### F1-未修复-低-_extract_valuation_band 回退正则可能匹配非市场估值文本

- **入口/函数**: `_parse_market_temperature` → `_extract_valuation_band`
- **文件(行号)**: `fund_agent/fund/data/thermometer.py:702-719`
- **输入场景**: 页面同时包含温度概率说明表（"温带 低估 发生概率 40%"）和度数式全市场温度（"70° 高估"），且无显式"估值状态"标签
- **实际分支**: `_extract_label_text` 未命中显式标签 → 进入回退正则
- **预期行为**: 返回市场级估值标签"高估"
- **实际行为**: 回退正则 `re.search(r"(低估|偏高|高估|...)", text)` 从全文开头扫描，匹配到说明表中第一个出现的"低估"，返回错误的估值标签
- **直接证据**: 当前有知有行 `/data` 页面包含温度概率说明表 `<tr><td>低估</td><td>40%</td>...`，该文本经归一化后出现在全市场温度段之前。`_find_index_table_header` 已正确过滤指数表，但估值标签提取无类似位置约束。
- **影响**: `valuation_band` 字段可能返回说明表的温度区间标签而非当前市场估值。该字段仅用于信息展示，不驱动检查清单或分析逻辑，不会导致错误结论。
- **建议改法和验证点**: 在 `_extract_valuation_band` 中先从市场标签附近窗口提取估值关键词（与 `_degree_after_heading` 类似近邻策略），回退到全文扫描作兜底。验证点：构造含前置说明表的 HTML fixture，断言 `valuation_band` 返回市场段标签。
- **修复风险（低）**: 仅影响估值标签提取策略，不影响温度数值或缓存行为。
- **严重程度（低）**: 信息字段，不驱动业务逻辑；当前实时页面因布局巧合不会触发。

### F2-未修复-低-_extract_as_of_text 无标签回退可能匹配无关日期

- **入口/函数**: `_extract_as_of_text`
- **文件(行号)**: `fund_agent/fund/data/thermometer.py:539-558`
- **输入场景**: 页面归一化文本中不存在"更新时间"等标签，但散布年份字符串（如版权"© 2026"或导航"2026年5月"）
- **实际分支**: 标签匹配全部未命中 → `_DATE_PATTERN.search(text)` 回退
- **预期行为**: 返回 `None` 或仅在有温度上下文时返回更新时间
- **实际行为**: 返回全文第一个日期形式字符串，可能是版权年份
- **直接证据**: 代码第 557 行 `date_match = _DATE_PATTERN.search(text); return date_match.group(0) if date_match else None`。`_DATE_PATTERN` 匹配 `\d{4}` 起始日期，"2026"同样命中。
- **影响**: `as_of_text` 和 `as_of_date` 可能包含无关日期。当前实时页面有明确"温度更新时间"标签，不触发回退。
- **建议改法和验证点**: 限制无标签回退仅在温度数值已成功解析时执行，或将回退范围限制在市场标签附近窗口。验证点：构造无标签日期的 HTML fixture，断言 `as_of_text` 为 `None`。
- **修复风险（低）**: 仅影响更新时间字段。
- **严重程度（低）**: 信息字段；当前实时页面有标签。

### F3-未修复-低-缓存写入非原子，崩溃可残留损坏文件

- **入口/函数**: `FundThermometerAdapter._save_snapshot`
- **文件(行号)**: `fund_agent/fund/data/thermometer.py:279`
- **输入场景**: 抓取解析成功，写入缓存时进程崩溃或断电
- **实际分支**: `write_text` 写入一半被中断
- **预期行为**: 下次启动后缓存可正常加载或被安全忽略
- **实际行为**: 磁盘残留截断 JSON；`_load_cache_payload` 捕获 `JSONDecodeError` 返回 `None`，等价于无缓存
- **直接证据**: `_load_cache_payload` 第 262 行 `except (json.JSONDecodeError, OSError): return None`。损坏文件不被误读但残留在磁盘。
- **影响**: 功能正确性无损。残留文件在下次成功写入时被覆盖。
- **建议改法和验证点**: 改为 write-to-temp-then-rename 原子写入。验证点：模拟写入中途截断，断言下次加载返回 `None` 且不抛异常。
- **修复风险（低）**: 仅影响缓存写入方式。
- **严重程度（低）**: 损坏缓存已被安全忽略。

---

## Additional Observations (Info, non-blocking)

- **指数代码列位回退正确**: `_parse_index_row` 第 411 行在无显式代码列时回退到名称列搜索代码。当前实时页面代码嵌在名称单元格中，已通过 `test_parse_thermometer_pages_parses_index_code_inside_name_cell` 验证。
- **部分抓取失败不保留成功数据**: data 页面成功但 macro 页面失败时，整个 try 块进入 except，成功数据不单独使用。合理设计选择——MVP 可接受。
- **国债收益率标签已扩展**: 控制器补充了"10年期国债到期收益率"和"十年期国债到期收益率"变体，已通过 `test_parse_thermometer_pages_parses_ten_year_treasury_maturity_yield_label` 验证。
- **缓存写入失败不污染抓取结果**: 内层 `try/except OSError: pass`（第 213-216 行）确保磁盘写入失败不将成功抓取转为 unavailable。已通过 `test_parse_thermometer_pages_parses_ten_year_treasury_maturity_yield_label` 等验证。
- **前置非指数表过滤**: `_find_index_table_header` 通过检查表头必须同时含"指数名称"/"指数" + "温度" + "内在"/"股息"来定位正确的指数表，已通过 `test_parse_thermometer_pages_skips_non_index_table_before_index_table` 验证。
- **测试覆盖完整**: 12 个测试覆盖成功路径、fresh cache、force refresh、stale fallback、无缓存 unavailable、malformed HTML、缓存写入失败、空 HTML、度数式全市场布局、代码内嵌名称、前置非指数表过滤、国债到期收益率标签。

---

## Open Questions

无阻塞性 open question。

---

## Verdict

**PASS**

3 个低严重程度 findings 均为信息字段的防御性边界问题，不影响温度数值解析、缓存语义或 unavailable 状态的正确性。当前实时页面不受影响。

P3-S2 成功信号"能获取全市场和指数温度"已满足：live smoke test 验证了全市场温度 70、11 条指数行（含沪深300 温度 59、内在收益率 5.11、股息率 2.42）、债券温度 77、国债到期收益率 1.77。

Capability 层边界正确，无 Service/CLI 泄露。12 个测试全部通过，回归套件 59 passed。
