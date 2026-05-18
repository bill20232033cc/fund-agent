# P3-S3 Code Review — MiMo

- **Gate**: P3-S3 (real §2 table fields, low-quality cache filtering, fund type classification order, CLI e2e matrix)
- **Reviewer**: MiMo (mimo-v2.5-pro)
- **Date**: 2026-05-18
- **Scope**: `fund_agent/fund/documents/cache.py`, `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/fund_type.py`, `fund_agent/fund/template/renderer.py`, `tests/fund/documents/*`, `tests/fund/extractors/test_profile.py`, `tests/fund/integration/test_p3_cli_e2e_matrix.py`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/implementation-control.md`
- **Diff base**: `main..feat/p3-cli-integration` (8 files changed, +1046 / -25)

## Verdict

**PASS**

## Review Summary

P3-S3 实现了三项核心变更：(1) 真实年报 §2 键值型表格字段抽取作为 regex 行匹配的 fallback；(2) parsed report 缓存质量门槛过滤低质量历史缓存；(3) 三只样本基金经 CLI 端到端完整 8 章报告矩阵测试。代码质量、测试覆盖和契约边界均达到 gate 要求，无 BLOCK 级问题。

## Detailed Findings

### F1 — 缓存质量门槛正确实现 (cache.py)

`is_parsed_annual_report_cache_usable()` 在 `_load_parsed_report_sync` 中作为最后过滤层，检查两个条件：

- `raw_text.strip() >= 1000` 字符
- `{§2, §3, §4, §8, §9, §10}` ⊆ `report.sections`

阈值和章节集合均为 `Final` 常量，语义明确。测试 `test_cache_rejects_unusable_parsed_report_payload` 使用 `raw_text="§1 基金简介\n测试正文"` + `sections={}` 的低质量报告验证拒绝路径。仓库层测试 `_build_stub_report` 同步更新了 `"仓库缓存正文" * 160` 以通过质量门槛。

无问题。

### F2 — 表格字段抽取 fallback (profile.py)

`_extract_field()` 在 regex 行匹配返回 `None` 后，调用 `_extract_field_from_section_two_tables(report, field_name)`。该函数遍历 `report.tables`，通过 `_iter_key_value_rows`（表头+数据行）、`_match_key_value_row` 和 `_normalize_label` 匹配字段标签。`_TABLE_FIELD_LABELS` 映射覆盖了 `fund_name`、`fund_category`、`benchmark`、`investment_scope`、`management_fee`、`custody_fee`、`fund_manager`、`fund_scale`、`fund_short_name` 共 9 个字段。`_SECTION_TWO_TABLE_MIN_PAGE = 1` 过滤非 §2 页码的表格。

关键路径验证：`_iter_key_value_rows` 返回 `(table.headers, *table.rows)`，正确处理了真实年报把首个键值对放入表头的情况。

无问题。

### F3 — 基金类型分类顺序 (fund_type.py)

分类顺序（`classify_fund_type` 245-309 行）：

1. QDII：`classification_text` = name + category + benchmark + scope，检查 `("QDII", "境外")`
2. FOF：检查 `("FOF", "基金中基金")`
3. 债券（类别/名称）：检查 `("债券", "中债")`
4. 主动（类别）：检查 `("混合型", "股票型")` 且类别不含"指数"
5. 指数/增强：类别含"指数"或名称/基准含指数关键词
6. 债券（范围）：`investment_scope` 含债券关键词
7. 主动（默认）

关键路径验证：

- **110011 (QDII)**：`_profile_table` 的 `short_name="易方达优质精选混合（QDII）"` → 表格 fallback 匹配"基金简称" → `fund_name` 含"QDII" → `classification_text` 含 QDII 关键词 → 正确分类。即使 `category=None`，scope="本基金可投资于境内和境外证券市场"中的"境外"也会命中。
- **000171 (债券)**：`_profile_table` 的 `short_name="易方达裕丰回报债券A"` → fund_name 含"债券" → 步骤 3 命中 → 正确分类，不会被步骤 5 的基准"沪深300"误导。
- **510300 (指数)**：无 QDII/FOF/债券关键词，无主动类别，名称含"沪深300" → 步骤 5 命中 → 正确分类。

`_extract_profile_value` 的 fallback 链：regex 行匹配 → `_extract_profile_value_from_tables`（fund_type 内部版本）→ `_PROFILE_TABLE_LABELS` 查找。与 profile.py 的表格抽取逻辑独立实现但语义一致。

无问题。

### F4 — CLI 端到端矩阵测试 (test_p3_cli_e2e_matrix.py)

`_build_report` 为每只基金构造完整的 fake 年报：raw_text 含 §1-§10 全部章节、tables 含 `_profile_table` + `_product_table` + 持仓表 + 行业分布表 + 份额变动表。raw_text 通过 `"P3 CLI 样本正文" * 100` 确保通过质量门槛。

测试断言覆盖：

- `exit_code == 0`
- 8 章完整（`"# 0."` 到 `"# 7."`）
- 证据附录存在（`"## 证据与出处"`）
- 基金名称和代码在输出中
- 基金类型正确（`case.expected_type`）
- 产品本质和基准未显示"未披露"
- 表格锚点存在（`"表page-5-table-0"`, `"表page-5-table-1"`）
- 3 只基金全覆盖
- Repository 和 NavProvider 调用参数正确

无问题。

### F5 — 现有测试适配

`test_repository.py` 的 `_build_stub_report` 已同步更新，增加 `"仓库缓存正文" * 160` 和完整 §2-§10 章节集合，确保通过新的质量门槛。`test_cache.py` 新增 `_build_unusable_report` 验证低质量缓存拒绝路径。

无问题。

### F6 — README 与文档同步

`fund_agent/fund/README.md` 新增温度计适配器、仓库层、extractors 和分析模块的当前实现说明。`tests/README.md` 新增温度计测试、程序审计测试和 P3 CLI 矩阵测试条目。`docs/implementation-control.md` 记录 P3-S3 状态和 RR-9/RR-10 残余风险。

无问题。

## INFO-Level Observations (non-blocking)

### I1 — 表格抽取逻辑重复

`fund_type.py` 的 `_extract_profile_value_from_tables`、`_match_table_value`、`_iter_key_value_rows`、`_first_non_empty_after`、`_normalize_table_label` 与 `profile.py` 的 `_extract_field_from_section_two_tables`、`_iter_key_value_rows`、`_match_key_value_row`、`_first_non_empty_after`、`_normalize_label` 存在结构性重复。当前两模块的返回类型不同（`str | None` vs `_MatchedField | None`），合并需要引入公共 helper，属于后续 slice 的优化空间，不阻塞 P3-S3。

### I2 — E2E 测试未显式断言分类依据

`test_p3_cli_outputs_complete_reports_for_three_sample_funds` 断言 `case.expected_type` 出现在输出中，但不验证 `classification_basis` 的具体内容。当前通过 `test_profile.py` 的三只基金单独测试覆盖了分类依据，E2E 层只验证端到端类型正确性，覆盖策略合理。

### I3 — E2E 测试只覆盖 happy path

当前矩阵测试使用 `force_refresh=True` 和结构完整的 fake 报表，未覆盖缓存命中、低质量缓存回退、分类歧义等边界路径。这些路径已由 `test_repository.py`、`test_cache.py`、`test_profile.py` 单独覆盖，E2E 层聚焦编排正确性是合理的分层策略。

## Conclusion

P3-S3 的三项核心变更（表格字段抽取 fallback、缓存质量门槛、CLI 矩阵测试）实现正确，测试覆盖充分，契约边界清晰。6 个 INFO 级观察均为非阻塞的后续优化建议。**PASS**。
