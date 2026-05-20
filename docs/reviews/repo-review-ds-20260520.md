# Code Review — Repo-Level Deepreview

## Scope

- **Mode**: all repository
- **Branch**: `main` at `1c0b9e1` (Close P7 draft PR gate)
- **Review date**: 2026-05-20
- **Included**: `fund_agent/` (all production code), `tests/`, `docs/design.md`, `docs/implementation-control*.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `pyproject.toml`
- **Excluded**: `.venv/`, `__pycache__/`, `reports/`, `launchd/`, `scripts/`, `docs/reviews/`, `uv.lock`
- **Parallel coverage**:
  - **Covered**: CLI→Service→Capability entry path, Document Repository→Sources→Cache, Template Contracts→Renderer→Audit, Data Extractors chain, Tests/Docs/Instruction compliance
  - **Partially covered**: Extraction Snapshot/Score/Quality Gate path (subagent dispatched but did not return; prior P4-P7 aggregate reviews had no open blocking findings)

## Findings

### F-001-严重-CLAUDE.md 描述的是完全错误的项目

- **入口/函数**: CLAUDE.md (entire file)
- **文件(行号)**: `CLAUDE.md:1-85`
- **输入场景**: Claude Code session 读取 CLAUDE.md 获取项目指导
- **实际分支**: CLAUDE.md 描述 `zhixing agent`（AKShare/yfinance/DeepSeek 股票分析），目录 `zhixing/`，CLI `zhixing analyze --ticker 600519`
- **预期行为**: 应描述 fund-agent 项目：`fund-analysis` CLI，`fund_agent/` 目录，dayu-agent 框架，pdfplumber
- **实际行为**: 10 处引用旧项目术语，零处引用当前项目术语
- **直接证据**: `grep -c 'zhixing\|ticker\|600519\|akshare\|yfinance' CLAUDE.md` 返回 10+；`grep -c 'fund-analysis\|fund_agent\|dayu\|pdfplumber' CLAUDE.md` 返回 0
- **影响**: Claude Code 获得完全错误的项目上下文，每次任务指导错误
- **建议改法和验证点**: 用实际项目信息重写 CLAUDE.md。验证：`grep -c 'zhixing' CLAUDE.md` 应为 0
- **修复风险（低）**: 纯文档修改
- **严重程度（严重）**:

### F-002-严重-Eastmoney PDF 内容完全无校验

- **入口/函数**: `EastmoneyAnnualReportSource.fetch_annual_report_pdf` → `_download_pdf`
- **文件(行号)**: `sources.py:471-488`, `downloader.py:79-97`
- **输入场景**: Eastmoney CDN 返回 200 OK 但内容为 HTML 错误页面
- **实际分支**: `_download_pdf` 将 HTML 写入 .pdf 文件并返回路径，无 Content-Type 或 `%PDF-` 校验
- **预期行为**: 非 PDF 响应应被拒绝，触发 fallback 或明确错误
- **实际行为**: HTML 被静默缓存为 .pdf，后续 `force_refresh=False` 持续提供损坏文件
- **直接证据**: `downloader.py:79-96` 无 content-type/`%PDF-` 检查。EID 路径 `sources.py:991-1008` 有 `_validate_pdf_response`，Eastmoney 路径不调用任何校验
- **影响**: 损坏 PDF 缓存静默传播；调用者收到垃圾解析文本；无法自动恢复
- **建议改法和验证点**: 在 `_download_pdf` 返回后添加 magic-bytes + 最小文件大小校验。用 mock Eastmoney 返回 `text/html` 验证
- **修复风险（低）**:
- **严重程度（严重）**:

### F-003-严重-QDII 误分类：业绩比较基准进入分类文本

- **入口/函数**: `classify_fund_type`
- **文件(行号)**: `fund_type.py:283-291`
- **输入场景**: A股主动基金，业绩比较基准含"境外"（如 "中证800×80%+中证境外互联网指数×20%"）
- **实际分支**: `classification_text` 拼接 benchmark 后命中 `_QDII_KEYWORDS` 中的"境外"→ 返回 `qdii_fund`
- **预期行为**: 业绩比较基准仅描述收益参照物，不能决定基金身份（与 index 分支同一原则，241行注释已声明）
- **实际行为**: 基金被误分类为 QDII，触发错误的分析路径和压力测试阈值
- **直接证据**: 283 行 `classification_text = f"{fund_name} {fund_category} {benchmark} {investment_scope}"` 将 benchmark 拼接进 QDII/FOF 检查；241 行注释明确"业绩比较基准只能描述收益参照物，不能单独证明产品是指数基金"——但同一原则未应用于 QDII 分支
- **影响**: 分析结论严重失真（QDII 压力测试阈值 0.35/0.55/0.75 vs 主动基金 0.20/0.40/0.60）
- **建议改法和验证点**: QDII/FOF 检查使用不含 benchmark 的 `identity_text`。验证：benchmark 含"境外"的A股基金不归为 qdii_fund
- **修复风险（中）**: 需确认无合法 QDII 仅靠 benchmark 被识别
- **严重程度（严重）**:

### F-004-严重-must_answer 契约字段永不被审计执行

- **入口/函数**: `run_programmatic_audit` → `_audit_contract_conformance`
- **文件(行号)**: `contract_rules.py:105-116`, `audit_programmatic.py:300-350`
- **输入场景**: 任何报告通过 C2 审计
- **实际分支**: `_audit_contract_conformance` 只检查 `required_output_items`（52 条规则）和 `must_not_cover`（9 条规则），完全不检查 `must_answer`
- **预期行为**: C2 审计应覆盖契约三层约束 must_answer + required_output_items + must_not_cover
- **实际行为**: must_answer（每章 5-9 个必须回答的问题，约 40 条）仅在 contracts.py 中被校验非空，永不被任何审计模块消费；报告可以对所有 must_answer 问题不回答而仍通过 C2
- **直接证据**: `contract_rules.py` 中 `ProgrammaticContractRules` 仅含 `required_items` 和 `forbidden_contents`；`audit_programmatic.py:319-350` 仅循环处理这两个字段；全文 grep 确认 must_answer 仅出现在 contracts.py 声明/构造/校验中
- **影响**: 契约中最核心的"必须回答"约束形同虚设——约 40 条 must_answer 问题零审计覆盖
- **建议改法和验证点**: 在 audit/ 下扩展 C2 规则增加 answer_rules，或将 must_answer 明确划归 LLM 审计范围并在 C2 规则注释说明
- **修复风险（中）**: must_answer 含语义性问题难以关键词匹配
- **严重程度（严重）**:

### F-005-高-block 策略下质量 gate 使用错误的异常类型和 exit code

- **入口/函数**: `FundAnalysisService.analyze()` → `_run_quality_gate_if_enabled()`
- **文件(行号)**: `fund_analysis_service.py:249-251`, `cli.py:179-186`
- **输入场景**: `analyze --quality-gate-policy block <fund_code>`，基金不在精选池 CSV 中
- **实际分支**: `quality_gate_result is None` → `raise ValueError(...)` → CLI `except Exception` 捕获 → exit 1
- **预期行为**: 应抛出 `QualityGateBlockedError`，CLI 以 exit 2 退出并输出结构化阻断信息
- **实际行为**: 抛出 `ValueError`（非 `QualityGateBlockedError` 子类），exit 1，丢失 gate 产物路径
- **直接证据**: `fund_analysis_service.py:250-251` 使用 `ValueError` 而非 `QualityGateBlockedError`；`cli.py:181-183` 专门捕获 `QualityGateBlockedError` → exit 2；`cli.py:184-186` 通用 `except Exception` → exit 1
- **影响**: CI/CD 无法区分 gate 阻断（exit 2）与系统错误（exit 1）；结构化阻断信息丢失
- **建议改法和验证点**: 将 `ValueError` 改为 `QualityGateBlockedError`，构造包含 not_run_reason 的 QualityGateResult
- **修复风险（低）**:
- **严重程度（高）**:

### F-006-高-非原子 PDF 写入留下损坏缓存 + OSError 绕过编排器错误分类

- **入口/函数**: `_download_pdf` / `EidAnnualReportSource.fetch_annual_report_pdf` / Eastmoney wrapper
- **文件(行号)**: `downloader.py:93`, `sources.py:338,471-488`
- **输入场景**: (a) 进程崩溃或下载中断 → 部分文件残留；(b) 磁盘满/权限拒绝 → `OSError`
- **实际分支**: (a) 直接 `write_bytes` 到最终路径，无 temp+rename；(b) Eastmoney 包装器仅捕获 `FileNotFoundError` 和 `httpx.HTTPError`，`OSError` 未捕获
- **预期行为**: (a) 写入临时文件后原子 rename；(b) OSError 应分类为 `AnnualReportSourceUnavailableError`
- **实际行为**: (a) 部分 PDF 被视为有效缓存；(b) 原始 OSError 崩溃整个文档加载管线
- **直接证据**: `downloader.py:93` 和 `sources.py:338` 均直接 `write_bytes`；`downloader.py:123` 文档标注 `OSError`；`sources.py:477-480` 无 `except OSError`
- **影响**: 损坏缓存无限期存活；磁盘满时崩溃调用者而非优雅降级
- **建议改法和验证点**: 写入 `.tmp` 后 `os.replace`；添加 `except OSError as exc: raise AnnualReportSourceUnavailableError(str(exc)) from exc`
- **修复风险（低）**:
- **严重程度（高）**:

### F-007-高-并发缓存竞争无锁

- **入口/函数**: `FundDocumentRepository.load_annual_report`
- **文件(行号)**: `repository.py:290-385`, `cache.py:318-350,376-423,509-592`
- **输入场景**: 两个并发 `load_annual_report("000001", 2024)` 调用
- **实际分支**: 两线程独立执行完整 fetch-parse-cache 管线，零同步原语
- **预期行为**: 只应执行一次下载+解析；第二个调用者等待或返回缓存
- **实际行为**: 双重下载浪费资源；documents 行与 parsed_reports 行来源可能不一致
- **直接证据**: `repository.py` 和 `cache.py` 中零 `asyncio.Lock`/`threading.Lock`/`Semaphore`
- **影响**: 资源浪费；病态情况下来源信息不一致
- **建议改法和验证点**: 添加 per-document-key `asyncio.Lock`；`asyncio.gather` 压力测试验证
- **修复风险（中）**:
- **严重程度（高）**:

### F-008-高-preferred_lens 在渲染器中完全未使用

- **入口/函数**: `render_template_report`
- **文件(行号)**: `renderer.py:181,224` vs `contracts.py:789-811`
- **输入场景**: 任何基金类型通过模板渲染
- **实际分支**: 渲染器在 chapter 0/1 输出文本"应用对应 preferred_lens"，但从不调用 `resolve_preferred_lens()`
- **预期行为**: 渲染器应根据基金类型调用 `resolve_preferred_lens()` 获取视角规则并注入渲染输出
- **实际行为**: 6 种基金类型 × 8 章的 preferred_lens 规则在报告生成中完全未被使用；`resolve_preferred_lens()` 仅在 `extraction_score.py` 中被调用
- **直接证据**: `renderer.py` 全文无 `resolve_preferred_lens` 调用；`grep -rn resolve_preferred_lens fund_agent/` 仅命中 contracts.py（定义）、__init__.py（导出）、extraction_score.py（调用）
- **影响**: 指数基金报告不优先回答跟踪误差，主动基金不聚焦基金经理——所有基金类型输出相同通用模板
- **建议改法和验证点**: 在章节渲染中根据 classified_fund_type 调用 resolve_preferred_lens 注入 lens statements
- **修复风险（中）**:
- **严重程度（高）**:

### F-009-高-extraction_mode 报告 "direct" 但子字段缺失

- **入口/函数**: `_build_field_from_matches` → `_build_manager_alignment`, `_build_holder_structure`
- **文件(行号)**: `manager_ownership.py:602-630`, `performance.py:415-418`
- **输入场景**: manager_holding 抽取成功但 employee_holding 为 None
- **实际分支**: `_build_field_from_matches` 始终返回 `extraction_mode="direct"`，不检查 value dict 内部子字段完整性
- **预期行为**: 子字段缺失时 extraction_mode 应为 `"partial"` 或添加 note
- **实际行为**: 下游 checklist 信赖 `extraction_mode="direct"` 认为数据完整，实际 employee_holding 为 None
- **直接证据**: `performance.py:415-418` 明确检查子字段完整性后才返回 `"direct"`；`manager_ownership.py` 无等价检查
- **影响**: checklist 第2问（利益一致性）基于不完整数据给出可能误导的结论
- **建议改法和验证点**: `_build_field_from_matches` 增加 `required_keys` 参数检查子字段完整性
- **修复风险（中）**: 增加 `ExtractionMode` 枚举值会影响所有下游消费者
- **严重程度（高）**:

### F-010-高-parse_ratio 对 Decimal > 1 歧义处理

- **入口/函数**: `parse_ratio` → `normalize_numeric_ratio`
- **文件(行号)**: `_ratios.py:50-65`
- **输入场景**: 调用方传入 `Decimal("1.50")` 作为换手率（意为 150% = 1.5x）
- **实际分支**: `abs(value) > Decimal("1")` → True → `value / Decimal("100")` → 返回 `Decimal("0.015")`
- **预期行为**: Decimal("1.50") 是小数形式的比例值，不应除以 100
- **实际行为**: 返回 0.015，换手成本被低估 100 倍（0.015×0.003=0.000045 vs 正确 1.5×0.003=0.0045）
- **直接证据**: `_ratios.py:63-64` 假设 >1 的数值一定是以百分比为单位的整数（如 150→1.50），但 Decimal("1.50") 可能是 1.5x 的小数表达
- **影响**: C 成本项计算失真两个数量级，净超额判断不可靠
- **建议改法和验证点**: 增加 `is_percentage_hint` 参数，仅当调用方明确声明为百分比整数时才除 100；或要求统一传入字符串格式
- **修复风险（中）**: 需审计所有 `parse_ratio` 调用点
- **严重程度（高）**:

### F-011-高-增强指数误判："增强"关键词过宽

- **入口/函数**: `classify_fund_type` → `_has_index_identity_evidence`
- **文件(行号)**: `fund_type.py:309-317,39`
- **输入场景**: 纯指数基金，投资策略描述 "通过优化抽样复制方法增强收益稳定性"
- **实际分支**: `_ENHANCED_KEYWORDS = ("增强",)` 命中投资目标中的"增强"→ 返回 `enhanced_index`
- **预期行为**: "增强收益"是描述性用语，不应触发增强指数分类
- **实际行为**: 基金被误分类为 `enhanced_index`，使用更严格的跟踪误差否决阈值
- **直接证据**: `fund_type.py:39` 仅含单个通用词"增强"；`fund_type.py:281` 拼接 investment_objective/scope/strategy，任何一处出现"增强"即触发
- **影响**: 跟踪误差否决阈值被错误收紧（0.02 vs 纯指数基金豁免）
- **建议改法和验证点**: 收窄为 `("指数增强", "增强指数", "增强型指数")`
- **修复风险（低）**:
- **严重程度（高）**:

### F-012-高-facet 映射不完整导致债券/QDII/FOF facet 静默丢弃

- **入口/函数**: `_validate_explicit_facets`
- **文件(行号)**: `item_rules.py:37-45,459-462`
- **输入场景**: 调用方传入 `facets=("纯债基金",)` 且 `fund_type="bond_fund"`
- **实际分支**: `_FACET_FUND_TYPE_MAP` 不含"纯债基金"键，`mapped_fund_type` 为 None，line 461 `continue` 静默跳过
- **预期行为**: 未映射的合法 facet 应至少 warn
- **实际行为**: bond_fund（3 facets）、qdii_fund（1 facet）、fof_fund（1 facet）共 5 个 CHAPTER_CONTRACT 声明的细分标签在 `_FACET_FUND_TYPE_MAP` 中完全缺失
- **直接证据**: `item_rules.py:37-45` 仅映射 index_fund/active_fund/enhanced_index 的 7 个 facets；contracts.py 中存在但缺失映射的 5 个 facets；line 461-462 无任何日志
- **影响**: 债券/QDII/FOF 基金的显式 facet 触发 ITEM_RULE 路径完全失效
- **建议改法和验证点**: 补全 `_FACET_FUND_TYPE_MAP`；为未知 facet 添加 warning
- **修复风险（低）**: 纯数据补全
- **严重程度（高）**:

### F-013-中-fund_code 格式校验缺失（analyze 命令）

- **入口/函数**: `FundAnalysisService._validate_request()`
- **文件(行号)**: `fund_analysis_service.py:345-346`
- **输入场景**: `analyze ABCDEF` 或 `analyze 12345`（非 6 位数字）
- **实际分支**: 仅检查非空 → 非法格式通过 → 深层数据仓库报错
- **预期行为**: 应在 Service 层验证为 6 位数字（同项目 `extraction_snapshot_service.py:88` 已有此校验）
- **实际行为**: 非法代码穿透 Service 直达 Capability，用户看到底层混乱错误
- **直接证据**: `fund_analysis_service.py:345-346` 仅校验空值；`extraction_snapshot_service.py:88` 已有完整校验
- **影响**: 用户输入错误时获得底层异常而非友好提示
- **建议改法和验证点**: 增加 `len(request.fund_code) != 6 or not request.fund_code.isdigit()` 校验
- **修复风险（低）**:
- **严重程度（中）**:

### F-014-中-EID schema 错误中止 fallback 链

- **入口/函数**: `AnnualReportSourceOrchestrator.fetch_annual_report_pdf`
- **文件(行号)**: `sources.py:564-565`
- **输入场景**: EID API 响应格式变更（如 `aaData` 变为 `data`）
- **实际分支**: EID 抛出 `AnnualReportSourceSchemaError` → 编排器立即重新抛出，不尝试 Eastmoney
- **预期行为**: Schema 错误可能仍应允许 Eastmoney fallback
- **实际行为**: EID API 变更完全阻断年报访问，即使 Eastmoney 有相同报告
- **直接证据**: `sources.py:564-565` — `except (MismatchError, SchemaError): raise` 无 fallback。对比 558-563 行对 NotFound/Unavailable 有 fallback
- **影响**: EID API 演进造成单点故障
- **建议改法和验证点**: 考虑将 schema 错误也 fallback，或设为可配置
- **修复风险（低）**:
- **严重程度（中）**:

### F-015-中-design.md 结构与实现严重不同步

- **入口/函数**: `docs/design.md` §7
- **文件(行号)**: `docs/design.md:420-469`
- **输入场景**: 开发者查阅设计文档
- **实际分支**: 设计列出约 13 个不存在的模块（`dependency_setup.py`, `checklist_service.py`, `registrar.py`, `audit_coordinator.py` 等）；实现有约 19 个设计未列的模块（`sources.py`, `extraction_score.py`, `extraction_snapshot.py`, `quality_gate.py`, `contracts.py`, `item_rules.py` 等）
- **预期行为**: 设计文档应反映当前架构或明确标注已过时
- **实际行为**: 设计文档自称"设计真源"（AGENTS.md）又自称"设计草案"（design.md:8），两者矛盾
- **直接证据**: `find fund_agent/ -name '*.py' | sort` vs design.md:420-469 模块列表
- **影响**: 新贡献者查找不存在的模块
- **建议改法和验证点**: 更新 design.md §7 或添加明确过时声明
- **修复风险（低）**:
- **严重程度（中）**:

### F-016-中-P2 内容过短检查覆盖所有标题级别

- **入口/函数**: `_short_content_locations`
- **文件(行号)**: `audit_programmatic.py:585-606`
- **输入场景**: 报告某子节内容少于 10 字符
- **实际分支**: `_HEADING_PATTERN` 匹配 `^#{1,6}` 所有标题级别，任何相邻标题间内容 < 10 字符触发 P2 issue
- **预期行为**: P2 应只检查模板 8 章级别的内容长度
- **实际行为**: 子标题间短内容触发 P2 issue，location 为子节标题而非章节名，审计结果混淆
- **直接证据**: `audit_programmatic.py:599` 遍历所有标题级别匹配；line 604 `len(content) < 10` 对所有标题间隔生效
- **影响**: 审计 P2 结果包含噪音 issues，降低审计可用性
- **建议改法和验证点**: 过滤到只匹配一级标题区间，或子标题内容过短降级为 reviewable
- **修复风险（低）**:
- **严重程度（中）**:

### F-017-中-L1 审计中使用裸 assert（python -O 下失效）

- **入口/函数**: `_audit_rabc_closure`
- **文件(行号)**: `audit_programmatic.py:416-420`
- **输入场景**: Python 以 `-O` 标志运行
- **实际分支**: assert 语句被完全剥离；后续 None 值上触发 TypeError
- **预期行为**: 所有审计路径应 fail-closed，返回 AuditIssue 而非抛出未捕获异常
- **直接证据**: `audit_programmatic.py:416-420` 使用裸 `assert` 检查 5 个字段非 None；Python 文档明确 `-O` 移除 assert。上层 line 406-407 有防御但中间无显式 None guard
- **影响**: 极端边界下审计崩溃而非优雅失败
- **建议改法和验证点**: 将 assert 替换为显式 `if value is None: continue`
- **修复风险（低）**:
- **严重程度（中）**:

### F-018-中-投资范围含债券可能误触发债券分类

- **入口/函数**: `classify_fund_type` fallback
- **文件(行号)**: `fund_type.py:335-341`
- **输入场景**: 混合型基金，类别为空，投资范围含"债券"（标配描述）
- **实际分支**: 通过 index/active equity 检测后进入 fallback → `_contains_any(investment_scope, _BOND_KEYWORDS)` → True → 返回 `bond_fund`
- **预期行为**: 投资范围提及"债券"是混合型基金的标配，不应触发债券分类
- **实际行为**: 未披露类别的混合基金被归类为债券基金，压力测试使用错误阈值
- **直接证据**: `fund_type.py:335-341` 对 investment_scope 做债券关键词检测，但几乎所有混合型基金的投资范围都提及"债券"作为可选标的
- **影响**: 压力测试阈值错误（债券 0.05/0.10/0.20 vs 混合基金实际风险）
- **建议改法和验证点**: 增加约束——仅在 investment_scope 同时不包含"股票"时才触发债券分类
- **修复风险（低）**:
- **严重程度（中）**:

### F-019-中-审计所有 issues 硬编码为 blocker

- **入口/函数**: `_issue`
- **文件(行号)**: `audit_programmatic.py:690-716`
- **输入场景**: 所有审计规则产生的 AuditIssue
- **实际分支**: `severity="blocker"` 硬编码，所有 issues 均为 blocker
- **预期行为**: `AuditSeverity` 定义了 `"blocker"` 和 `"reviewable"` 两级，应根据问题性质区分
- **实际行为**: `reviewable` 分支永不可达；全文 grep 仅命中类型定义，无任何赋值
- **直接证据**: `audit_programmatic.py:26` 定义双级别；line 713 硬编码 `"blocker"`
- **影响**: 审计结果失去区分度——缺证据行(P3)和数学闭合失败(L1)等同处理
- **建议改法和验证点**: 为 `_issue` 添加 severity 参数，不同规则不同严重性
- **修复风险（低）**:
- **严重程度（中）**:

### F-020-低-block 策略在基金池拒绝前做了昂贵的抽取 I/O

- **入口/函数**: `FundAnalysisService.analyze()`
- **文件(行号)**: `fund_analysis_service.py:240-248`
- **输入场景**: `analyze 000001 --quality-gate-policy block`（不在精选池中）
- **实际分支**: 先执行完整年报抽取 I/O → 再检查池成员 → 拒绝
- **预期行为**: 池成员检查仅需 fund_code 和 CSV 路径，应前置到抽取之前
- **直接证据**: `fund_analysis_service.py:240-244` 抽取在 quality gate（245）之前；`quality_gate_integration.py:127-155` 仅需 `source_csv` 和 `fund_code`
- **影响**: 每次拒绝浪费网络和计算资源
- **建议改法和验证点**: 将池成员检查前置到抽取之前
- **修复风险（中）**:
- **严重程度（低）**:

### F-021-低-TOCTOU PDF 存在性检查 + 缓存命中无完整性校验

- **入口/函数**: `_get_pdf_entry_sync` → `parse_pdf` / `_download_pdf` cache-hit
- **文件(行号)**: `cache.py:343-345`, `downloader.py:79-81`, `sources.py:327-328`
- **输入场景**: (a) 缓存检查和解析之间 PDF 被外部删除；(b) 上次下载中断留下 0 字节文件
- **实际分支**: (a) `exists()` 检查与 `parse_pdf()` 调用之间存在 TOCTOU 窗口；(b) 仅检查 `exists()` 无 `st_size > 0` 或 `%PDF-` 校验
- **预期行为**: 解析失败时使缓存失效并重试下载；缓存命中时验证文件完整性
- **实际行为**: (a) 原始异常传播；(b) 空/截断文件被当作有效 PDF
- **直接证据**: `cache.py:344` 和 `repository.py:368` 之间无保护；`downloader.py:79` 仅 `exists()`
- **影响**: 低概率场景——外部缓存清理或之前中断下载
- **建议改法和验证点**: 包裹 parse_pdf 调用 try/except；缓存命中时验证 `st_size > 0` 和 `%PDF-`
- **修复风险（低）**:
- **严重程度（低）**:

### F-022-低-golden answer/prefill 服务包装器无直接测试

- **入口/函数**: `GoldenAnswerService.build()`, `GoldenPrefillService.run()`
- **文件(行号)**: `golden_answer_service.py`, `golden_prefill_service.py`
- **输入场景**: 测试套件执行
- **实际分支**: 两个服务模块（66 和 76 行）无专门测试文件；底层 Capability 模块有测试
- **预期行为**: AGENTS.md 要求 "单文件测试覆盖率目标为 ≥80%"
- **实际行为**: 服务编排层无测试覆盖请求校验和错误传播路径
- **直接证据**: `find tests/ -name '*golden*'` 仅返回 Capability 层测试，无 Service 层测试
- **影响**: 低——模块是薄包装器，但请求校验逻辑未测试
- **建议改法和验证点**: 添加 `tests/services/test_golden_answer_service.py` 和 `test_golden_prefill_service.py`
- **修复风险（低）**:
- **严重程度（低）**:

### F-023-低-C2 required items 共享相同 marker 导致无法独立判定

- **入口/函数**: `validate_programmatic_contract_rules`
- **文件(行号)**: `contract_rules.py:59-60,155-189`
- **输入场景**: 报告 Chapter 0 仅含一次 "基金：" 文本
- **实际分支**: "一句话这是什么基金" 和 "基金简介" 两个独立 required_output_items 使用相同 marker `("基金：",)`，一次出现使两者均判定通过
- **预期行为**: 不同 required_output_items 应可由不同 marker 独立验证
- **实际证据**: `contract_rules.py:59-60`；`contracts.py:179` vs `contracts.py:180` 是两个独立条目
- **影响**: 报告可能只含一句"基金：XXX"而缺失独立基金简介，但两个 item 都判通过
- **建议改法和验证点**: 设计不同 marker 或合并条目
- **修复风险（低）**:
- **严重程度（低）**:

## Open Questions

1. **Extraction Snapshot/Score/Quality Gate 路径**：本 review 未完成此切片的完整逐行走读（subagent 未返回）。P4-P7 aggregate reviews 已知无 open blocking findings，但 snapshot schema drift、comparable_values whitelist 完整性、FQ5 template_contract_applicability 边界未在本轮独立验证。
2. **ExtractionMode "partial" 状态**：F-009 指出部分提取应增加 `"partial"` 状态，但增加枚举值会影响所有下游消费者，需评估影响面。

## Residual Risk

1. **Extraction/Quality 路径未独立重验**：依赖 P4-S1 至 P7-S4 的 slice-level acceptance 保证正确性。
2. **并发场景测试覆盖不足**：无 `asyncio.gather` 多基金并发加载测试，F-007 的 cache race 未在实际并发中验证。
3. **真实网络回归**：多数测试使用 fake sources/fixtures。真实 EID/Eastmoney/akshare 网络行为变化只能在手动 smoke test 中发现。
4. **CLAUDE.md 是最严重问题**：描述的是完全不同的项目，导致 Claude Code 在所有任务中给出错误指导。
5. **must_answer（约 40 条）零审计覆盖**：C2 审计不检查 must_answer，约 40 条契约约束没有程序化执行。
6. **preferred_lens 对报告生成是死代码**：48 条 lens 规则定义并校验但从未被 renderer 使用。
