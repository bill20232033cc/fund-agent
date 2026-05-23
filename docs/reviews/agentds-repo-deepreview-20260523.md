# Code Review — Repository-Level Deepreview

## Scope

- **Mode**: all repository
- **Branch**: main
- **Review date**: 2026-05-23
- **Output file**: docs/reviews/agentds-repo-deepreview-20260523.md
- **Included scope**: 全部 `fund_agent/` 生产代码（~54K LOC）、全部 `tests/` 测试代码（~23K LOC）、CI 配置、`pyproject.toml`、README 文档
- **Excluded scope**: `.venv/`、`node_modules/`、`__pycache__/`、`.git/`、`docs/reviews/` 历史 artifact、`cache/`、`reports/` 运行时产物
- **Parallel review coverage**: 6 个子代理覆盖了核心分析管线、文档仓库与数据源、模板/契约/审计、质量门控与评分、CLI 与层边界、测试覆盖与 CI 六个切片
- **Not-covered areas**: `docs/` 下非核心设计文档（历史 research notes、draft 等）仅抽查；部分 extractor 的边界输入组合未穷尽

---

## Findings

### F-1-严重-C2审计对must_not_cover缺少反向完整性校验，24条禁止项静默无规则覆盖

- **入口/函数**: `validate_programmatic_contract_rules()` → `_validate_forbidden_content_rules()`
- **文件(行号)**: `fund_agent/fund/audit/contract_rules.py:575-602`
- **输入场景**: 加载内置 `_FORBIDDEN_CONTENT_RULES`（9条）时调用校验
- **实际分支**: 逐条验证每条规则都在 manifest 中存在，但**不检查** manifest 的 must_not_cover 条目是否全部被规则覆盖
- **预期行为**: 与同模块 `_validate_required_item_rules()` 一致，计算 `missing_items = manifest_items - rule_items`，缺任一条就 raise ValueError
- **实际行为**: manifest 33 条 must_not_cover 中只有 9 条有程序化 forbidden marker 规则（`contract_rules.py:96-108`），剩余 24 条静默通过校验
- **直接证据**: `contract_rules.py:538-572` 的 `_validate_required_item_rules` 有 `missing_items` 双向校验；`contract_rules.py:575-602` 的 `_validate_forbidden_content_rules` 无此校验
- **影响**: 若 futures 在 CHAPTER_CONTRACT 新增 must_not_cover 条目（如"不展开行业比较"），会静默绕过 C2 程序审计，不报错也不审计，fail-closed 契约被破坏
- **建议改法和验证点**: 在 `_validate_forbidden_content_rules` 末尾追加与 required_item 同构的 `missing_items` 检查；对已存在但无规则覆盖的条目显式标注 `coverage_kind: narrative_guidance`
- **修复风险**: 低
- **严重程度**: 严重

### F-2-严重-Ch0两个required_output_items共享marker，C2审计无法独立区分

- **入口/函数**: `_audit_contract_conformance()` → `_REQUIRED_ITEM_RULES` 查找
- **文件(行号)**: `fund_agent/fund/audit/contract_rules.py:113-114`；渲染端 `fund_agent/fund/template/renderer.py:337`
- **输入场景**: 渲染第 0 章后执行 C2 审计
- **实际分支**: `ContractRequiredItemRule(0, "一句话这是什么基金", ("基金：",))` 与 `ContractRequiredItemRule(0, "基金简介", ("基金：",))` 使用相同 marker `"基金："`
- **预期行为**: 两个独立的 `required_output_item` 应有独立可审计的 marker，或在契约层显式合并为一条
- **实际行为**: renderer 只输出一条 `f"- 基金：{fund_name}（{fund_code}）。"`（`renderer.py:337`），两个条目共享同一 marker。C2 审计退化为重复检查，无法独立 fail
- **直接证据**: `contract_rules.py:113-114` 两条规则 marker 完全相同；`renderer.py:337` 只输出单条 bullet
- **影响**: 若未来 renderer 演化导致"基金简介"应包含更多信息而缺失，C2 审计无法发现
- **建议改法和验证点**: 方案 A：契约中合并两条条目；方案 B：为"基金简介"分配独立 marker 并 renderer 输出独立 bullet
- **修复风险**: 低（方案A）/ 中（方案B）
- **严重程度**: 严重

### F-3-严重-`parse_ratio` bool被当作数值输入导致InvalidOperation（三处同源）

- **入口/函数**: `parse_ratio`
- **文件(行号)**: `fund_agent/fund/analysis/_ratios.py:34-35`；同模式出现在 `risk_check.py:985` 和 `checklist.py:750-751`
- **输入场景**: value 为 `True` 或 `False`（Python bool 是 int 子类）
- **实际分支**: `isinstance(value, int | float)` 对 `bool` 返回 `True`，`Decimal(str(True))` = `Decimal('True')` → `InvalidOperation`
- **预期行为**: bool 值应被拒绝并报告明确的 `ValueError`
- **实际行为**: 抛出 `InvalidOperation`，错误信息为 `"无法解析为数值：True"`，未指明调用方传入了非法类型
- **直接证据**: `_ratios.py:34-35`；Python 中 `isinstance(True, int)` 为 `True`；`Decimal("True")` 抛 `InvalidOperation`
- **影响**: 若任何调用方因 JSON 解析等原因传入 `true`/`false` 布尔值，会在深层抛出非预期异常类型。当前年报抽取产出均为字符串，实际触发概率低，但防御不足
- **建议改法和验证点**: 在 `isinstance(value, int)` 前增加 `if isinstance(value, bool): raise ValueError(...)` 显式排除 bool，三处同时修复
- **修复风险**: 低
- **严重程度**: 严重

### F-4-高-quality_gate中`_required_quality_number`与`_required_number`接受bool为合法数值

- **入口/函数**: `_required_quality_number` / `_required_number`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:976-994` 与 `quality_gate.py:1164-1182`
- **输入场景**: score.json 中 `missing_field_rate` 或 `coverage_rate` 被错误写入布尔值
- **实际分支**: `isinstance(True, int | float)` 返回 `True`，直接通过类型守卫，`float(True)` 返回 `1.0`
- **预期行为**: 拒绝非数值类型的输入，抛出 `ValueError`
- **实际行为**: `missing_field_rate: true` → `float(True)` = `1.0`，FQ4 判定 100% 缺失率并虚假 BLOCK。同模块的 `_optional_correctness_int`（line 1119）已有 `isinstance(value, bool)` 守卫，此处缺失
- **直接证据**: `quality_gate.py:992` 无 `isinstance(value, bool)` 守卫；`quality_gate.py:1119` 有显式 bool 守卫（证明已知此问题）
- **影响**: 上游 score.json 意外将字段写为布尔值时，FQ4 会误判 100% 缺失率虚假阻断
- **建议改法和验证点**: 在两处函数增加 `isinstance(value, bool)` 前置守卫并 raise
- **修复风险**: 低
- **严重程度**: 高

### F-5-高-UI层直接从Capability import类型，违反AGENTS.md模块边界

- **入口/函数**: `thermometer()` → `_thermometer_reading_payload()` / `_thermometer_batch_payload()`
- **文件(行号)**: `fund_agent/ui/cli.py:46-47`
- **输入场景**: 运行 `fund-analysis thermometer --index 000300 --json`
- **实际分支**: `from fund_agent.fund.data.thermometer_types import ThermometerBatchResult, ThermometerReading`
- **预期行为**: AGENTS.md:68-70 — UI 层依赖约束：只依赖 Application 层提供的接口，不直接调用 Engine 或 Capability
- **实际行为**: UI 绕过 Service 层，从 Capability 层（`fund_agent.fund.data.thermometer_types`）直接 import 类型用于 `isinstance` 类型分发
- **直接证据**: `cli.py:46`；`cli.py:822-846` 的 `isinstance(result, ThermometerReading)` 等分发逻辑
- **影响**: 违反分层架构合约；Capability 类型变更直接打破 CLI；新增返回类型可能被 duck typing fall-through 遗漏
- **建议改法和验证点**: Service 层 `services/__init__.py` 重新导出这些类型；UI 改为 `from fund_agent.services import ...`
- **修复风险**: 低
- **严重程度**: 高

### F-6-高-CI未强制覆盖率门禁，与AGENTS.md和tests/README.md声明的目标矛盾

- **入口/函数**: `.github/workflows/ci.yml` pytest 调用行
- **文件(行号)**: `.github/workflows/ci.yml:21`
- **输入场景**: CI 执行测试
- **实际分支**: `uv run pytest -q` 不带 `--cov` 参数
- **预期行为**: AGENTS.md:159 要求单文件覆盖率≥80%；tests/README.md:105 要求 `--cov-fail-under=50`；pyproject.toml 已声明 `pytest-cov>=7.1`
- **实际行为**: CI 无覆盖率收集或门禁，任何新代码在无测试覆盖时 CI 仍然通过
- **直接证据**: `ci.yml:21`；`pyproject.toml:18` 有 `pytest-cov` 依赖但 ci.yml 未使用
- **影响**: CI 无法防止覆盖率退化
- **建议改法和验证点**: CI 命令改为 `uv run pytest -q --cov=fund_agent --cov-fail-under=50`
- **修复风险**: 低
- **严重程度**: 高

### F-7-中-`_parse_scale_to_yuan`不识别中文千位/百万级量词，导致清盘误判

- **入口/函数**: `_parse_scale_to_yuan`
- **文件(行号)**: `fund_agent/fund/analysis/risk_check.py:766-788`
- **输入场景**: 基金规模披露为"5千万"（即 5000 万 = 50000000 元）
- **实际分支**: 正则匹配"5"，"万"在"5千万"中 → `5 × 10000 = 50000`
- **预期行为**: 应正确解析为 50000000 元
- **实际行为**: 解析为 50000 元，远低于 5000 万元清盘阈值，触发虚假清盘否决
- **直接证据**: `risk_check.py:784-788` 只处理 `亿`（×10^8）和 `万`（×10^4），不识别 `千万`（×10^7）、`百万`（×10^6）
- **影响**: 若年报用"x千万"表示规模，会导致虚假清盘否决，`derive_final_judgment` 返回 `suggest_replace`
- **建议改法和验证点**: 在乘万之前扫描千/百/十等量词前缀；或无法确认语义时返回 `insufficient_data` 而非错误解析
- **修复风险**: 中（需处理"千万"的歧义）
- **严重程度**: 中

### F-8-中-言行一致性风格桶/仓位桶first-match-wins导致混合策略误分类

- **入口/函数**: `_style_bucket` / `_position_bucket_from_text`
- **文件(行号)**: `fund_agent/fund/analysis/consistency_check.py:507-525, 568-589`
- **输入场景**: 产品说明书同时包含"价值"和"成长"风格关键词；或同时出现"高仓位"和"均衡配置"
- **实际分支**: dict 迭代顺序 `value → growth → balanced → quality`，先匹配"价值" → 返回 "value"
- **预期行为**: 应返回 "balanced" 或标记为 ambiguous
- **实际行为**: 多风格混合策略被硬分类为第一个匹配桶，导致言行一致性投资风格维度可能产生虚假 "misaligned"
- **直接证据**: `consistency_check.py:522-524` `for bucket, keywords in _STYLE_KEYWORDS.items(): if any(keyword in text ...): return bucket`
- **影响**: 风格分类不准确 → 一致性判断错误 → 可能触发严重风格漂移否决
- **建议改法和验证点**: 多桶命中时返回最特定匹配或标记为 ambiguous/balanced
- **修复风险**: 中
- **严重程度**: 中

### F-9-中-Eastmoney来源将PDF完整性错误错分为unavailable，违反AGENTS.md fail-closed契约

- **入口/函数**: `EastmoneyAnnualReportSource.fetch_annual_report_pdf` → `_download_annual_report_pdf`
- **文件(行号)**: `fund_agent/fund/pdf/downloader.py:109-124`（抛 `ValueError`）；`fund_agent/fund/documents/sources.py:555`（catch `ValueError` → `AnnualReportSourceUnavailableError`）
- **输入场景**: Eastmoney CDN 返回 HTTP 200 但 body 是非 PDF 内容（HTML 错误页）
- **实际分支**: `_validate_pdf_bytes` 发现不以 `%PDF-` 开头 → 抛 `ValueError` → Eastmoney source 的 `except ValueError` 转抛为 `AnnualReportSourceUnavailableError`
- **预期行为**: AGENTS.md:218 规定 `integrity_error` 必须 fail-closed，禁止被 fallback 静默掩盖。应抛 `AnnualReportSourceIntegrityError`
- **实际行为**: 抛 `AnnualReportSourceUnavailableError`（语义为"可重试、可fallback"）
- **直接证据**: `downloader.py:124` → `sources.py:555`；Eastmoney source 在整个 fetch 方法中从未 raise `AnnualReportSourceIntegrityError`
- **影响**: 当前很少触发（EID优先且EID有正确的integrity校验）；但若配置变更使Eastmoney成为第一来源则暴露
- **建议改法和验证点**: 在 Eastmoney 的 except 分支中区分 `ValueError`：若消息含 PDF/CONTENT-TYPE 关键词则抛 `AnnualReportSourceIntegrityError`
- **修复风险**: 低
- **严重程度**: 中

### F-10-中-EID HTTP非200状态码语义丢失，404被当作临时不可用

- **入口/函数**: `_request_with_retries`
- **文件(行号)**: `fund_agent/fund/documents/sources.py:888-896`
- **输入场景**: EID 返回 HTTP 404（路径变更）、403（反爬封禁）
- **实际分支**: 所有 `status_code != 200` 统一抛为 `AnnualReportSourceUnavailableError`
- **预期行为**: 4xx（尤其是 404）应抛 `AnnualReportSourceNotFoundError` 或 `AnnualReportSourceSchemaError`
- **实际行为**: 404 → `AnnualReportSourceUnavailableError`（允许 fallback），但实际更可能是 `not_found` 或 `schema_drift`（URL变更），不应 fallback
- **直接证据**: `sources.py:892-896` 对 `status_code != 200` 统一抛 `AnnualReportSourceUnavailableError`
- **影响**: EID 接口下架时编排器静默 fallback 到 Eastmoney，不触发告警
- **建议改法和验证点**: 区分 4xx→schema_drift/not_found，5xx→unavailable
- **修复风险**: 中（需确认 EID 实际可能返回的各种 4xx 场景语义）
- **严重程度**: 中

### F-11-中-akshare阻塞调用无超时包装，可无限挂起异步任务

- **入口/函数**: `_download_annual_report_pdf` / `_default_nav_fetcher` / `AkshareIndexThermometerSource.load_index_history`
- **文件(行号)**: `fund_agent/fund/pdf/downloader.py:210`; `fund_agent/fund/data/nav_data.py:52`; `fund_agent/fund/data/thermometer_source.py:99-101`
- **输入场景**: akshare 网络库在等待外部 API 时无限阻塞（DNS 卡住、TCP 连接无响应）
- **实际分支**: `await asyncio.to_thread(...)` 将 akshare 同步调用扔进线程池，无任务级超时
- **预期行为**: 所有外部 I/O 应有超时保护，超时后降级为不可用
- **实际行为**: 全项目 `asyncio.wait_for` 搜索结果为零。一个调用挂起可耗尽线程池
- **直接证据**: `downloader.py:210`、`nav_data.py:52`、`thermometer_source.py:99-101` 均无外层 `asyncio.wait_for`
- **影响**: 线程池耗尽后所有依赖 `to_thread` 的操作（SQLite 写入、文件 I/O）全部阻塞
- **建议改法和验证点**: 为每个 `asyncio.to_thread` 包装的 akshare 调用添加 `asyncio.wait_for(..., timeout=30)`
- **修复风险**: 低
- **严重程度**: 中

### F-12-中-FQ3对traceability 0.7-0.9区间产生误导性阻断

- **入口/函数**: `_evaluate_field_score`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:569-580`
- **输入场景**: P0 字段 coverage_rate=0.65（低于 watch 阈值），traceability_rate=0.85（高于 watch 但低于 pass 阈值 0.9）
- **实际分支**: FQ2 因 status=FAIL（coverage<0.7）触发 BLOCK；FQ3 因 `traceability_rate < 0.9` 也触发 BLOCK
- **预期行为**: 根因是 coverage 不足（65%）而非 traceability（85%），FQ3 消息固定为"证据锚点不足"会误导排查方向
- **实际行为**: traceability 85% 处于合理水平，但被 FQ3 判定为"证据锚点不足"并追加 BLOCK
- **直接证据**: `quality_gate.py:569` 使用 `traceability_rate < 0.9`（pass阈值）而非 `< 0.7`（watch阈值）作为 FQ3 触发条件
- **影响**: 对 P0 字段误报"证据锚点不足"，误导下游排查
- **建议改法和验证点**: FQ3 阈值改为 0.7 以对齐"不足"语义；或消息中区分"不足"vs"偏低"
- **修复风险**: 中（需确认业务接受边缘字段不再被 FQ3 阻断）
- **严重程度**: 中

### F-13-中-P0/P1字段watch状态在quality gate中完全静默

- **入口/函数**: `_evaluate_field_score`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:536-595`
- **输入场景**: P0 字段 coverage_rate=0.85, traceability_rate=0.85（watch区间）
- **实际分支**: 只处理 `status == STATUS_FAIL` 的两个分支（P0→BLOCK, P1→WARN），不存在对 watch 状态的处理
- **预期行为**: P0 字段在 watch 区间应触发至少 WARN 级别的 gate issue
- **实际行为**: P0 字段从 89% 掉到 71% 不产生任何 gate 告警，直到跌破 70% 才 BLOCK
- **直接证据**: `quality_gate.py:555-594` 无 `STATUS_WATCH` 处理分支
- **影响**: 质量门控在 pass（≥90%）和 fail（<70%）之间有 20 个百分点静默区间，不利于持续质量监控
- **建议改法和验证点**: 增加 `status == STATUS_WATCH` 分支，P0→WARN，P1→INFO
- **修复风险**: 低
- **严重程度**: 中

### F-14-中-R2开发覆盖冲突总是blocker级别，合法覆盖也被拒绝

- **入口/函数**: `_audit_final_judgment()` → developer_override 分支
- **文件(行号)**: `fund_agent/fund/audit/audit_programmatic.py:1262-1269`
- **输入场景**: Service 层合法使用 `override_judgment` 覆盖系统派生判断
- **实际分支**: `developer_override` 且 `final_judgment != derived_final_judgment` 时创建 issue，使用默认 `severity="blocker"`
- **预期行为**: 冲突已由 `FinalJudgmentDecision.conflict_reasons` 显式记录，审计应标记为 `reviewable` 而非 `blocker`
- **实际行为**: `_issue()` 默认 `severity="blocker"`（`audit_programmatic.py:1464`），导致每次合法覆盖都阻断审计通过
- **直接证据**: `audit_programmatic.py:1262-1269` 不传 severity 参数
- **影响**: 所有使用 developer override 的报告无法通过程序审计，破坏"override + 人工复核"工作流
- **建议改法和验证点**: 将 severity 改为 `"reviewable"`
- **修复风险**: 低
- **严重程度**: 中

### F-15-中-Ch0渲染器忽略可用risk_check_result，"当前最大风险"始终输出"数据不足"

- **入口/函数**: `_render_chapter_0()`
- **文件(行号)**: `fund_agent/fund/template/renderer.py:343`
- **输入场景**: `risk_check_result` 有完整否决项和关注项数据
- **实际分支**: 硬编码 `f"- 当前最大的风险：{_INSUFFICIENT_TEXT}，当前未提供独立最大风险排序输入。"`
- **预期行为**: CHAPTER_CONTRACT must_answer 要求回答"当前最大的风险是什么"，应消费 `risk_check_result` 派生
- **实际行为**: 无论 risk_check_result 内容如何，Ch0 该 bullet 始终为"数据不足"
- **直接证据**: `renderer.py:343` 硬编码 INSUFFICIENT_TEXT；`renderer.py:86` risk_check_result 为非 Optional 必填字段
- **影响**: 封面页关键风险信息缺失，违背"一眼看懂"设计目标；C2 审计因 marker 存在而通过
- **建议改法和验证点**: 从 `risk_check_result.veto_items` 或 `overall_status` 派生出 Ch0 风险摘要
- **修复风险**: 低
- **严重程度**: 中

### F-16-中-Ch0"什么变化会升级降级终止"无对应输入字段，结构性不可满足

- **入口/函数**: `_render_chapter_0()`
- **文件(行号)**: `fund_agent/fund/template/renderer.py:346`
- **输入场景**: 任意渲染请求
- **实际分支**: 硬编码 `f"- 什么变化会升级、降级或终止当前动作：{_INSUFFICIENT_TEXT}，需要后续跨期证据确认。"`
- **预期行为**: CHAPTER_CONTRACT must_answer 要求回答此问题，但 `TemplateRenderInput` 无对应字段
- **实际行为**: 该 must_answer 在当前架构下结构性不可满足
- **直接证据**: `renderer.py:346`；`renderer.py:65-93` TemplateRenderInput 字段列表无 upgrade/downgrade threshold
- **影响**: 封面页关键判断依据永久缺失
- **建议改法和验证点**: 新增 `action_thresholds` 字段或将此 must_answer 声明为后续 LLM 审计层覆盖
- **修复风险**: 低
- **严重程度**: 中

### F-17-中-禁止词检查朴素子串匹配可误伤年报会计术语

- **入口/函数**: `_validate_report_wording()`
- **文件(行号)**: `fund_agent/fund/template/renderer.py:54, 1623-1638`
- **输入场景**: 证据锚点描述包含"买入返售金融资产"（年报 §7 标准科目）
- **实际分支**: `"买入" in report_markdown` 匹配，renderer raise ValueError
- **预期行为**: 只禁止"建议买入"语义，不应误伤年报披露原文中的标准科目名称
- **实际行为**: 朴素子串匹配，不区分语境
- **直接证据**: `renderer.py:54` `_FORBIDDEN_TERMS = ("买入", "卖出", "仓位比例", "收益预测")`；`renderer.py:1636` `if term in report_markdown`
- **影响**: 当基金持有买入返售资产且被证据锚点引用时，整份报告渲染失败。当前可能未触发但属潜伏误拒绝
- **建议改法和验证点**: 升级为上下文感知匹配（如排除证据附录段落）或加词边界
- **修复风险**: 低
- **严重程度**: 中

### F-18-中-fallback成功时不保留失败来源历史，违反AGENTS.md追溯要求

- **入口/函数**: `AnnualReportSourceOrchestrator.fetch_annual_report_pdf`
- **文件(行号)**: `fund_agent/fund/documents/sources.py:657-658`
- **输入场景**: EID `not_found` → Eastmoney 成功
- **实际分支**: `_mark_fallback_used(result)` 只设 `fallback_used=True`；failures 列表未被持久化
- **预期行为**: AGENTS.md:220-222 要求 fallback 成功时保留 metadata；当前只保留布尔值，无失败来源列表
- **直接证据**: `sources.py:780` 只在 metadata 设 `fallback_used=True`；`models.py:53` `fallback_used: bool` 是唯一字段
- **影响**: 运维无法回溯"某次分析使用了 fallback 是因为哪个来源以何种原因失败"
- **建议改法和验证点**: 在 `AnnualReportSourceMetadata` 增加 `fallback_failures` 字段
- **修复风险**: 低
- **严重程度**: 中

### F-19-中-`comparable_values: {}`空dict与字段缺失混淆，可能误判mismatch

- **入口/函数**: `_snapshot_actual_index`
- **文件(行号)**: `fund_agent/fund/extraction_score.py:1800-1809`
- **输入场景**: snapshot 记录包含 `comparable_values: {}`（空 dict）
- **实际分支**: `has_explicit_comparable_values=True`，白名单子字段全被 `setdefault` 为 `None`，golden answer 有该字段时 `actual_value=None` → 进入 mismatch 分支
- **预期行为**: 空 `comparable_values` 表示字段存在但未暴露可比子字段，应归为 unavailable 而非 mismatch
- **实际行为**: 与"snapshot 明确缺失该字段"语义混淆
- **直接证据**: `extraction_score.py:1800` 只区分 `comparable_values` 键是否存在，不区分空 dict vs 有值 dict
- **影响**: 字段未暴露可比值时被误判为 mismatch，可能触发 FQ1 block
- **建议改法和验证点**: 区分"未初始化（unavailable）"和"初始化为None（明确缺失）"
- **修复风险**: 中
- **严重程度**: 中

### F-20-中-温度计批量查询串行执行

- **入口/函数**: `ThermometerService._load_index_batch()`
- **文件(行号)**: `fund_agent/services/thermometer_service.py:187-188`
- **输入场景**: `fund-analysis thermometer --index 000300,000905`
- **实际分支**: `tuple([await self._load_index_reading(request, index_code) for index_code in index_codes])` 串行执行
- **预期行为**: 多个独立指数查询应并发执行（`asyncio.gather`）
- **实际行为**: N 个指数总耗时 = N × 单个耗时
- **直接证据**: `thermometer_service.py:187-188` 使用 list comprehension 内 await
- **影响**: 批量查询延迟线性累加
- **建议改法和验证点**: 改为 `asyncio.gather(*[self._load_index_reading(request, code) for code in index_codes])`
- **修复风险**: 低
- **严重程度**: 中

### F-21-中-CLI退出码2多重语义与文档不一致

- **入口/函数**: `analyze()` / `checklist()` / `thermometer()`
- **文件(行号)**: `fund_agent/ui/cli.py:205-207, 224, 227, 254, 300-301`
- **输入场景**: (a) BadParameter参数错误 (b) quality gate block (c) 参数校验ValueError (d) checklist未实现
- **实际分支**: 四种场景均以 `exit code=2` 退出
- **预期行为**: 设计文档声明退出码 2 只表示 quality gate block
- **实际行为**: exit 2 同时承载 quality gate block、参数校验失败和命令未实现
- **直接证据**: `cli.py:207` BadParameter→2；`cli.py:224` gate block→2；`cli.py:301` ValueError→2
- **影响**: 脚本依赖退出码做分支决策时，可重试的参数错误和不可重试的 gate block 无法区分
- **建议改法和验证点**: 统一退出码语义：exit 1=系统异常；exit 2=质量门禁阻断；exit 3=用户输入参数错误
- **修复风险**: 低
- **严重程度**: 中

### F-22-中-基金类型识别顺序与预期优先级不符

- **入口/函数**: `classify_fund_type()`
- **文件(行号)**: `fund_agent/fund/fund_type.py:324-400`
- **输入场景**: QDII-ETF 基金（既是 QDII 又跟踪指数）
- **实际分支**: QDII(324)→FOF(338)→债券(352)→指数/增强(360-375)→主动权益；QDII/FOF 优先于指数
- **预期行为**: 设计文档 §6.5 声明优先级为 指数→增强→QDII→FOF→债券→主动权益
- **实际行为**: QDII 和 FOF 作为顶层 regulatory 类别优先返回，指数/增强在后
- **直接证据**: `fund_type.py:324-327` QDII 分支在最前；`fund_type.py:360-375` 指数/增强在后
- **影响**: QDII-ETF 被归为 `qdii_fund` 而非 `index_fund`，影响 preferred_lens 和估值状态解析
- **建议改法和验证点**: 与设计方确认优先级；若指数优先则提前指数判断并保留并发 QDII 证据
- **修复风险**: 中（需确认下游所有 fund_type 消费者行为）
- **严重程度**: 中

### F-23-中-fund_type.py与profile.py存在大量重复表格解析函数

- **入口/函数**: `_match_table_value` / `_iter_key_value_rows` / `_first_non_empty_after` / `_normalize_table_label`
- **文件(行号)**: `fund_agent/fund/fund_type.py:139-216` vs `fund_agent/fund/extractors/profile.py:172-247`
- **输入场景**: 年报解析中的键值型表格字段抽取
- **实际分支**: 两模块各自维护功能几乎相同的四对辅助函数
- **预期行为**: AGENTS.md:137 — "重复逻辑必须抽取为公共函数/类"
- **实际行为**: 逻辑一致但参数签名有细微差异，独立演化容易出现行为分歧
- **直接证据**: `fund_type.py:139-164` ≡ `profile.py:188-211` 逐行比对
- **影响**: 两份代码独立演化，bug fix 不互通
- **建议改法和验证点**: 抽取公共模块 `fund_agent/fund/extractors/_table_utils.py`
- **修复风险**: 低
- **严重程度**: 中

### F-24-中-Alpha归因恒返回insufficient_data，模板第2章Alpha判断永久缺失

- **入口/函数**: `FundAnalysisService.analyze()` → `judge_alpha_nature()`
- **文件(行号)**: `fund_agent/services/fund_analysis_service.py:399-403`
- **输入场景**: 所有 analyze 调用
- **实际分支**: 恒传入 `observations=()`，恒返回 `AlphaJudgment(nature="insufficient_data", ...)`
- **预期行为**: AGENTS.md:235 要求必须区分结构性超额 vs 阶段性超额
- **实际行为**: 已知 MVP 限制，Service 层无法提供 market_environments 和 source_confidences
- **直接证据**: `fund_analysis_service.py:399-403` 注释声明 MVP 限制
- **影响**: 报告第 2 章 Alpha 归因部分永久显示"数据不足"，削弱分析完整性
- **建议改法和验证点**: 补齐 market_environments 和 source_confidences 数据链路
- **修复风险**: 中
- **严重程度**: 中

### F-25-中-多文件IO缺少并发保护

- **入口/函数**: `record_pdf_path` vs `save_parsed_report`、`FundNavDataAdapter.load_nav_data`、`_append_jsonl`
- **文件(行号)**: `fund_agent/fund/documents/cache.py:360-382`（无锁）；`fund_agent/fund/data/nav_data.py:184-222`（无锁）；`fund_agent/fund/extraction_snapshot.py:1241-1257`（无锁）
- **输入场景**: 并发分析多只基金时
- **实际分支**: `save_parsed_report` 持有锁但 `record_pdf_path` 不持有；`load_nav_data` 无并发去重；JSONL 追加无原子性
- **预期行为**: 写入操作应有并发保护
- **实际行为**: SQLite 可能 `database is locked`；重复 akshare 调用；JSONL 行可能交错
- **直接证据**: 见各文件行号
- **影响**: 高并发下缓存写入失败、外部调用浪费、输出文件可能损坏
- **建议改法和验证点**: 统一锁粒度；`load_nav_data` 增加 per-key 锁；JSONL 增加文件锁或原子 rename
- **修复风险**: 低
- **严重程度**: 中

---

## Open Questions

1. **基金类型识别优先级**（F-22）：设计文档 §6.5 声明的优先级（指数→增强→QDII→FOF→债券→主动）与代码实现（QDII→FOF→债券→指数/增强→主动）不一致，需确认哪个是正确意图。
2. **Ch0 must_answer 覆盖路由**（F-15, F-16）：Ch0 两个 must_answer（最大风险、升级降级阈值）当前结构性不可满足，是应补齐结构化输入还是声明为 LLM 审计层覆盖？
3. **FQ3 traceability 阈值**（F-12）：将 FQ3 触发阈值从 0.9 改为 0.7 是否会被业务接受？当前 0.7-0.9 区间的 P0 字段会被 FQ2 覆盖（因 coverage 不足），收紧 FQ3 阈值主要影响 traceability 独立触发的场景。
4. **must_not_cover 覆盖策略**（F-1）：当前 24 条无程序化规则覆盖的 must_not_cover 条目，哪些需要程序审计规则、哪些可以叙事引导（narrative_guidance）？

## Residual Risk

1. **Product mode 端到端链路无自动化回归**：3 只样本基金的集成测试全部使用 `--dev-override` 模式。product mode 完整链路（无开发覆盖、自动估值）无自动化测试保护。
2. **akshare 外部依赖可用性**：3 处 akshare 调用无超时保护（F-11），线程池耗尽风险真实存在但当前单进程部署下触发概率低。
3. **并发场景未充分验证**：缓存锁粒度不一致（F-25 三处）、JSONL 写入无原子性等问题在单进程串行部署下不触发，但多协程并发场景未测试。
4. **Eastmoney 完整性错误分类**（F-9）：当前默认编排 EID 优先降低了触发风险，但配置变更后暴露。
5. **温度计数据质量**（非正 PE/PB 静默丢弃）：依赖上游 akshare 数据质量，个别异常值可能影响分位数基准。
6. **bool-int 类型混淆**（F-3, F-4）：4 处 `isinstance(value, int)` 未排除 bool，当前上游输出均为字符串故未触发，但防御缺失。
7. **R=A+B-C 零仓位场景**无测试覆盖；**最终判断 None 输入**无防御测试；**温度计最小样本边界**（29 vs 30）无精确测试；**压力测试指数基金类型**正常路径无测试。
8. **pytest-cov 配置缺失**：`pyproject.toml` 无 `[tool.coverage.*]` 配置，本地运行覆盖率需手动传参。

---

## Review Summary

- **Total findings**: 25 (3 严重, 3 高, 19 中)
- **Highest severity**: 严重
- **Blocker present**: 否（无阻止当前发布的数据损坏或安全漏洞）
- **Key risk areas**: C2 审计完整性（F-1/F-2）、类型防御（F-3/F-4）、外部 I/O 可靠性（F-9/F-11）、层边界合规（F-5）、质量门控正确性（F-7/F-12/F-13）
- **Test health**: 537 测试全部通过，ruff 零告警
