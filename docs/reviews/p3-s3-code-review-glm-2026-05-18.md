# P3-S3 Code Review (GLM)
Date: 2026-05-18
Gate: P3-S3 code review
Reviewer: AgentGLM

## Findings

### F1-pass-info-缓存质量门槛不包含 §1 但对所有当前 extractor 无影响
- **入口/函数**: `is_parsed_annual_report_cache_usable`
- **文件(行号)**: `fund_agent/fund/documents/cache.py:22-25,73-75`
- **输入场景**: 一份包含 §1/§2/§3/§4/§8/§9/§10 但因历史解析器遗漏 §5 的年报缓存
- **实际分支**: `REQUIRED_PARSED_REPORT_SECTION_IDS <= set(report.sections)` 判断为 True
- **预期行为**: 缓存可用
- **实际行为**: 缓存可用（正确）
- **直接证据**: `REQUIRED_PARSED_REPORT_SECTION_IDS = frozenset({"§2", "§3", "§4", "§8", "§9", "§10"})` 不含 §1 和 §5；当前所有稳定 extractor（profile/performance/manager_ownership/holdings_share_change）消费的章节恰好是 §1/§2/§3/§4/§8/§9/§10，其中 §1 只作为文本行抽取的 fallback 来源，§5 当前无 extractor 消费。门槛集合与实际 extractor 依赖完全对齐。
- **影响**: 无功能影响。门槛集合精确匹配当前 extractor 消费范围，不会拒绝合法缓存，也不会接受无法支撑抽取的低质量缓存。
- **建议改法和验证点**: 无需修改。后续若有 extractor 消费 §5，需同步扩展此集合。
- **修复风险**: N/A
- **严重程度**: info

### F2-pass-low-基金简称中的 QDII 标识不直接参与 fund_type 分类判断
- **入口/函数**: `classify_fund_type`
- **文件(行号)**: `fund_agent/fund/fund_type.py:225-309`
- **输入场景**: 110011 的基金简称为"易方达优质精选混合（QDII）"，但基金全称为"易方达优质精选混合型证券投资基金"
- **实际分支**: `_extract_profile_value(report, "fund_name")` 从表头 (`基金名称`, 全称) 匹配，返回不含 QDII 的全称。`fund_type.py` 的 `classification_text` 包含 `investment_scope`，其中含有"境外"，命中 `_QDII_KEYWORDS = ("QDII", "境外")`，正确分类为 `qdii_fund`。
- **预期行为**: 110011 被分类为 `qdii_fund`
- **实际行为**: 110011 被分类为 `qdii_fund`（正确，但通过 investment_scope 而非简称中的 QDII 标识）
- **直接证据**: e2e 测试 `_SAMPLE_CASES[0]` 设置 `expected_type="qdii_fund"`，测试断言 `基金类型：qdii_fund` 出现在输出中，且 `test_extract_profile_uses_table_short_name_for_qdii_classification` 单独验证了简称 QDII 路径。但该测试使用 `_build_table_profile_report` 构造的年报不含 investment_scope，因此只能通过简称命中 QDII。e2e 测试的 110011 案例走的是 investment_scope "境外" 路径。
- **影响**: 当前无功能问题。两种路径（简称 QDII 和 investment_scope "境外"）均可正确分类。但如果一只 QDII 基金的 investment_scope 中不出现"境外"且简称中的 QDII 仅出现在表格行而非表头（fund_name 从表头取全称），则 fund_name 不含 QDII，可能导致漏分类为 `active_fund`。
- **建议改法和验证点**: 无需在 P3-S3 修改。可在后续迭代中让 `classify_fund_type` 也检查 `_extract_profile_value(report, "fund_name")` 返回值之外的简称字段，或在 `classification_text` 中拼接从表格行抽取的简称。增加一个简称含 QDII 但 investment_scope 不含"境外"的 fixture 测试覆盖此边界。
- **修复风险**: 低风险，属于防御性增强。
- **严重程度**: low

### F3-pass-info-§2 表头键值抽取对 3 只样本基金表格格式完全正确
- **入口/函数**: `_iter_key_value_rows`, `_match_table_value` (fund_type.py) / `_match_key_value_row` (profile.py)
- **文件(行号)**: `fund_agent/fund/fund_type.py:156-169,128-153` 和 `fund_agent/fund/extractors/profile.py:153-192`
- **输入场景**: 真实年报 §2 键值表，首个键值对位于表头（如 `(基金名称, 全称)`），后续键值对位于 rows（如 `(基金简称, 简称)`）
- **实际分支**: `_iter_key_value_rows` 返回 `(table.headers, *table.rows)`，先搜表头再搜数据行
- **预期行为**: 表头中的"基金名称"和 rows 中的"基金简称"、"业绩比较基准"等字段均被正确提取
- **实际行为**: 所有 3 只样本基金的表格字段均被正确提取（e2e 测试断言 `产品本质：未披露 not in result.output` 和 `业绩基准 未披露 not in result.output`，以及 `表page-5-table-0` 和 `表page-5-table-1` 出现在输出中）
- **直接证据**: e2e 测试 `test_p3_cli_outputs_complete_reports_for_three_sample_funds` 验证 3 只基金的完整输出；`test_extract_profile_reads_real_section_two_key_value_tables` 验证 510300 的表格字段抽取；`test_extract_profile_prefers_bond_name_before_mixed_index_benchmark` 验证 000171 的表格抽取；`test_extract_profile_uses_table_short_name_for_qdii_classification` 验证 110011 的表格抽取。
- **影响**: 无问题。
- **建议改法和验证点**: 无需修改。
- **修复风险**: N/A
- **严重程度**: info

### F4-pass-info-template benchmark_text 契约已对齐
- **入口/函数**: `_render_chapter_1`
- **文件(行号)**: `fund_agent/fund/template/renderer.py:212`
- **输入场景**: 渲染模板第 1 章"收益来源假设"行
- **实际分支**: `_value_text(benchmark, "benchmark_text")` 从 `benchmark.value` 字典读取 `benchmark_text` 键
- **预期行为**: `profile.py` 中 `_build_benchmark` 设置 `value={"benchmark_text": matched_field.value}`，键名完全匹配
- **实际行为**: 契约对齐，无错配。缺失时 `benchmark.value or {}` 变为空字典，`_value_text` 正确返回"未披露"
- **直接证据**: e2e 测试断言 `"业绩基准 未披露" not in result.output`，确认 3 只样本基金的基准都被正确提取并渲染。`test_extract_profile_outputs_classification_basis_and_anchors_for_active_fund` 断言 `result.benchmark.value == {"benchmark_text": "沪深300指数收益率×80%＋中债综合指数收益率×20%"}`。
- **影响**: 无问题。之前的契约错配（如果存在）已修复。
- **建议改法和验证点**: 无需修改。
- **修复风险**: N/A
- **严重程度**: info

### F5-pass-info-P3 CLI 端到端矩阵测试覆盖完整 Service -> template -> audit 管线
- **入口/函数**: `test_p3_cli_outputs_complete_reports_for_three_sample_funds`
- **文件(行号)**: `tests/fund/integration/test_p3_cli_e2e_matrix.py:416-456`
- **输入场景**: 3 只样本基金通过 Typer CLI `analyze` 子命令传入完整参数
- **实际分支**: CLI -> FundAnalysisService.analyze -> FundDataExtractor.extract (真实 Capability) -> extract_profile/extract_performance/extract_manager_ownership/extract_holdings_share_change (真实 extractor) -> calculate_r_abc_from_bundle -> judge_alpha_nature -> check_consistency -> analyze_investor_experience -> run_risk_checks -> run_stress_test -> run_checklist -> render_template_report (真实渲染) -> run_programmatic_audit (真实审计)
- **预期行为**: 完整 8 章 Markdown 报告输出，程序审计通过
- **实际行为**: 测试断言 exit_code==0（审计通过）、8 个章节标题存在、证据与出处附录存在、基金名称/代码/类型正确、产品和基准非缺失、表 ID 存在于证据中。唯一隔离措施是 `_FakeRepository` 和 `_FakeNavProvider`（符合 `tests/README.md` 维护约定）
- **直接证据**: `monkeypatch.setattr(cli, "FundAnalysisService", lambda: service)` 确保 CLI 调用注入的 Service；Service 构造时传入 `FundDataExtractor(repository=repository, nav_provider=nav_provider)` 使用真实 extractor 编排。所有 Capability 模块（extractors/analysis/template/audit）均为真实实现，无 mock。
- **影响**: 测试真实覆盖了完整的 CLI -> Service -> Capability 管线，不存在短路。
- **建议改法和验证点**: 无需修改。
- **修复风险**: N/A
- **严重程度**: info

### F6-pass-low-fund_type 分类优先级对 510300/000171/110011 三只样本基金均正确
- **入口/函数**: `classify_fund_type`
- **文件(行号)**: `fund_agent/fund/fund_type.py:225-309`
- **输入场景**: 510300（CSI 300 ETF）、000171（债券基金）、110011（QDII 混合基金）
- **实际分支**:
  - 510300: QDII/FOF/bond/active 均不命中 -> `"指数" not in fund_category` 但 `_contains_any(name_and_benchmark, _INDEX_NAME_KEYWORDS)` 命中"沪深300" -> `"增强" not in name_and_benchmark` -> `index_fund`
  - 000171: QDII/FOF 不命中 -> `_contains_any(fund_name, _BOND_KEYWORDS)` 命中"债券" -> `bond_fund`（在 index 检查之前）
  - 110011: `_contains_any(classification_text, _QDII_KEYWORDS)` 命中 investment_scope 中的"境外" -> `qdii_fund`（最高优先级）
- **预期行为**: 510300=index_fund, 000171=bond_fund, 110011=qdii_fund
- **实际行为**: 完全符合预期
- **直接证据**: e2e 测试 `_SAMPLE_CASES` 中 `expected_type` 分别为 `"index_fund"`, `"bond_fund"`, `"qdii_fund"`，断言 `基金类型：{case.expected_type}` 出现在输出中。单独的 `test_extract_profile_reads_real_section_two_key_value_tables` 验证 510300 表格抽取后分类为 `index_fund`。
- **影响**: 分类优先级正确：QDII > FOF > 债券 > 主动权益 > 指数/指数增强。债券检查在指数检查之前，避免了偏债产品因基准含沪深 300 被误判。
- **建议改法和验证点**: 无需修改。
- **修复风险**: N/A
- **严重程度**: info

### F7-pass-info-parsed report 缓存低质量门槛测试覆盖完整
- **入口/函数**: `test_cache_rejects_unusable_parsed_report_payload`
- **文件(行号)**: `tests/fund/documents/test_cache.py:180-199`
- **输入场景**: 保存一个 raw_text 仅为"§1 基金简介\n测试正文"（12 字符，sections 为空）的低质量年报缓存
- **实际分支**: `is_parsed_annual_report_cache_usable` 检查 `len(report.raw_text.strip()) < 1000` 为 True（12 < 1000），返回 False -> `load_parsed_report` 返回 None
- **预期行为**: 低质量缓存被拒绝，不返回给调用方
- **实际行为**: `await cache.load_parsed_report(document_key)` 返回 None（正确）
- **直接证据**: 测试先 `save_parsed_report` 保存低质量报告，再 `load_parsed_report` 断言返回 None。`_build_stub_report` 构造 1322 字符正文 + 6 个必需章节，验证可用缓存正常返回。
- **影响**: 质量门双重检查（正文长度 + 必需章节集合）确保历史低质量解析物不会被复用。
- **建议改法和验证点**: 无需修改。
- **修复风险**: N/A
- **严重程度**: info

### F8-pass-info-缓存 initialize 在每次操作前重复执行但不影响正确性
- **入口/函数**: `AnnualReportDocumentCache.load_parsed_report`, `get_pdf_path`, `record_pdf_path`, `save_parsed_report`
- **文件(行号)**: `fund_agent/fund/documents/cache.py:164-177,209-224,266-281,320-341`
- **输入场景**: 连续多次调用缓存操作
- **实际分支**: 每个公开方法开头都调用 `await self.initialize()`，内部 `_initialize_sync` 使用 `mkdir(parents=True, exist_ok=True)` 和 `CREATE TABLE IF NOT EXISTS`
- **预期行为**: 重复初始化不会报错，只是浪费少量 I/O
- **实际行为**: 正确，幂等
- **直接证据**: `test_cache_persists_pdf_metadata_and_parsed_report` 连续调用 `record_pdf_path` 和 `save_parsed_report`，均通过。实现控制文档 P1-S3 residual risks 中已记录此问题。
- **影响**: 性能轻微浪费，无正确性风险。已作为 residual risk 记录。
- **建议改法和验证点**: 后续可考虑在 `__init__` 中标记已初始化状态，避免重复执行。当前 MVP 可接受。
- **修复风险**: N/A
- **严重程度**: info

## Open Questions

1. **QDII 简称 vs investment_scope 双路径依赖**: 110011 的 QDII 分类依赖 investment_scope 中的"境外"，而非基金简称中的"QDII"。当前两条路径都能覆盖，但如果出现一只 investment_scope 不含"境外"、fund_name (全称) 不含"QDII"但简称含"QDII"的基金，`classify_fund_type` 会将其分类为 `active_fund`。是否需要在后续迭代中让 `fund_name` 提取优先取简称（或同时拼接全称+简称）来增强 QDII 识别？

2. **fixture 覆盖缺口**: `tests/fixtures/fund/extractors/profile/` 当前只有 active_fund、index_enhanced、bond_fund 三类 fixture，缺少 `index_fund`（纯指数）和 `qdii_fund` 的纯文本 fixture。e2e 测试中的 510300/110011 使用 `_build_table_profile_report` 构造的表格年报覆盖了这些类型，但 profile fixture 层面没有对应 .txt 文件。是否需要补齐？

## Verdict
PASS

无 blocking finding。所有 8 项 finding 均为 info 或 low 级别。

- **parsed report 缓存质量门**: 双重检查（正文 >= 1000 字符 + 必需章节集合超集）设计合理，不会拒绝合法缓存（F1），测试覆盖了低质量缓存拒绝路径（F7）。
- **§2 表头键值抽取**: `_iter_key_value_rows` 返回 `(headers, *rows)` 正确处理了表头含首个键值对的格式，3 只样本基金的表格字段均被正确提取（F3）。
- **基金类型分类优先级**: QDII > FOF > 债券 > 主动权益 > 指数/指数增强，3 只样本基金分类结果正确（F6），债券优先于指数避免了偏债产品误判。
- **template benchmark_text 契约**: `profile.py` 输出 `{"benchmark_text": ...}` 与 `renderer.py` 读取 `benchmark["benchmark_text"]` 完全对齐（F4）。
- **P3 CLI 端到端矩阵**: 测试通过真实 Typer CLI、Service 编排、全部 Capability 模块（extractors/analysis/template/audit）完成完整管线验证，唯一隔离措施是 fake repo/nav（F5）。
- **残余风险**: 1 个 low 级别发现（F2）：基金简称中的 QDII 标识不直接参与 fund_type 分类，当前通过 investment_scope 间接覆盖，但存在理论上的漏分类边界。
