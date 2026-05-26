# 测试手册

当前测试按 UI / Service / Agent 层基金能力边界分层，新增用例应跟随实现所在目录组织，并优先覆盖当前稳定公共契约，而不是偶然实现细节。

CI 当前固定 Python 3.11，使用 `uv sync --extra dev --frozen` 安装锁定依赖，并运行 `uv run ruff check .` 与 `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`。本地验证发布就绪时应优先复用同一组命令。

## 当前目录

- `tests/fund/documents/test_repository.py`：文档仓库契约测试，验证仓库对外返回 `ParsedAnnualReport`，不暴露本地 `Path`，并覆盖来源元数据、cache provenance、metadata-aware/legacy loader 和并发防串扰
- `tests/fund/documents/test_annual_report_sources.py`：年报来源编排测试，使用 fake source 和 fake EID network 覆盖 EID 主源、Eastmoney fallback、显式 fallback 分类、fail-closed 阻断 provenance、请求级 timeout、PDF 校验、PDF cache 完整性校验、原子写入、`force_refresh` 转发和 PDF 适配器来源调用；不触发真实 EID/Eastmoney/akshare 网络
- `tests/fund/documents/test_cache.py`：文档缓存最小闭环测试，覆盖 PDF 元信息缓存、source metadata JSON、损坏来源元数据降级、parsed report 物化、parsed payload 原子替换失败清理、损坏 parsed payload 回退未命中、legacy metadata 兼容和缓存失效回退
- `tests/fund/pdf/test_downloader.py`：PDF 下载 helper 测试，验证内部缓存命中、损坏缓存刷新、非 PDF 响应拒绝、强制刷新下载和年报 URL 组装
- `tests/fund/pdf/test_parser.py`：章节定位测试，覆盖 `§3` 正文命中、目录误判回归和偏移单调递增
- `tests/fund/extractors/test_profile.py`：基础画像 extractor 测试，覆盖分类先行、`classified_fund_type` / `classification_basis` 稳定输出、纯指数/指数增强/非指数 `index_profile`，以及费率/基准/规模/经理 anchor
- `tests/fund/extractors/test_performance.py`：`§3` 表现 extractor 测试，覆盖冒号行与年度表现表中的净值增长率/基准收益率 anchor、投资者收益率 `direct / estimated / missing` 三态，以及跟踪误差直接披露、目标/限制、mixed actual/target、manager narrative、benchmark-only、standard-deviation-only、unparseable、table/text inconsistency、多候选、表格多候选、`§2` fallback 和早期 blocker 后继续扫描
- `tests/fund/extractors/test_manager_ownership.py`：`§4/§8/§9` 管理人/持有人 extractor 测试，覆盖编号标题策略文本、换手率、持有披露表、跨页持有人结构和 `missing` 路径
- `tests/fund/extractors/test_holdings_share_change.py`：`§8/§10` 持仓/份额 extractor 测试，覆盖前十大重仓、行业分布、净变动表、申购/赎回拆分表、多份额列选择、非 A 份额不默认 A 类、歧义多列表 missing、利润变动表误命中回归和表格型 anchor
- `tests/fund/test_extraction_snapshot.py`：P4-S1/P5-S3/P13/P14-S1 精选基金池字段级抽取快照测试，覆盖 CSV 校验、snapshot schema、`comparable_values` 白名单子字段、`index_profile` / `tracking_error` dataclass 子字段序列化、summary 重复代码标红、单基金失败继续和 `004393` known failure 捕获；使用 fake extractor，不触发真实网络或 PDF
- `tests/fund/test_extraction_score.py`：P4-S2/P4-R10/P5-S2/P5-S3/P5-S4/P6-S5/P9-S2/P14-S1 字段级评分测试，覆盖 snapshot JSONL coverage / traceability / status / priority 映射、单基金质量汇总、指数质量字段按基金类型条件进入 P1 分母、`fund_quality` 模板契约适用性派生、`failed_funds` accounting、score 输出、最小 golden set 选择、correctness perfect match、mismatch、白名单缺失、旧 snapshot 兼容、skipped 分母处理和 report-year scoped golden coverage scope；不触发真实网络或 PDF
- `tests/fund/test_golden_prefill.py`：correctness golden answer 预填底稿测试，覆盖模板基金代码识别、dict/dataclass 字段预填、证据 source 和跳过字段保留；使用 fake extractor，不触发真实网络或 PDF
- `tests/fund/test_golden_answer.py`：人工审核后的 golden answer Markdown 转 JSON 与 strict JSON loader 测试，覆盖 strict 校验、跳过字段、转义竖线、report_year legacy 默认值、跨年份重复 identity 和机器可读 JSON 输出；不触发真实网络或 PDF
- `tests/fund/test_quality_gate.py`：P4-S4/P5-S2/P5-S4/P6-S5/P9-S2 报告质量 gate 测试，覆盖字段级与单基金 P0 fail 阻断、P1 fail 警告、correctness 未接入 info、correctness coverage FQ0 metadata、report-year coverage gap、correctness mismatch 触发 FQ1、App 类别冲突 FQ1、缺失率 FQ4、模板契约适用性 FQ5、`rule_results`、失败基金 FQ6 和旧 score 兼容；只消费 score JSON，不触发真实网络或 PDF
- `tests/fund/test_quality_gate_integration.py`：P5-S1/P9-S2 单基金 quality gate adapter 测试，覆盖从已抽取 `StructuredFundDataBundle` 生成 snapshot/score/gate 产物、精选池成员缺 golden coverage 或当前 report_year 缺 golden coverage 仍运行 gate，以及基金不在精选池时返回 not-run reason；不触发真实网络或 PDF
- `tests/fund/data/test_nav_data.py`：净值数据适配器测试，覆盖 `nav_cache` 命中和强制刷新
- `tests/fund/data/test_thermometer.py`：有知有行温度计适配器测试，覆盖全市场/指数/宏观解析、24h 缓存复用、强制刷新、抓取失败 stale fallback、无缓存 unavailable 和 malformed HTML
- `tests/fund/data/test_thermometer_source.py`：自建温度计 akshare 数据源测试，覆盖沪深300/中证500 PE/PB 表合并、指数与全 A PE/PB 顺序抓取、全 A `wind_all_a` PE/PB 共同日期合并、同日期重复修正行确定性折叠、不支持代码和 schema drift fail-closed
- `tests/fund/data/test_thermometer_cache.py`：自建温度计 JSON 缓存测试，覆盖 index/market 命名空间隔离、fresh cache、stale policy 和损坏缓存降级
- `tests/fund/analysis/test_ratios.py`：分析模块公共比例解析测试，覆盖披露文本百分比解析、数值型输入已标准化契约、保留的显式数值百分比归一 helper 和非法输入 fail-closed
- `tests/fund/analysis/test_r_abc.py`：R=A+B-C 收益归因测试，覆盖公式闭合、P1 字段解析、证据锚点传递和缺失输入路径
- `tests/fund/analysis/test_alpha_judge.py`：超额收益性质判断测试，覆盖结构性、部分结构性、阶段性、不适用、样本不足和显式环境输入要求
- `tests/fund/analysis/test_consistency_check.py`：言行一致性检验测试，覆盖 4 维度信号、红灯冲突和显式实际风格/仓位输入要求
- `tests/fund/analysis/test_investor_return.py`：投资者获得感分析测试，覆盖行为损益、投资者收益缺失、追涨/抄底资金流向和份额字段缺失
- `tests/fund/analysis/test_risk_check.py`：否决项检查与压力测试，覆盖清盘风险、基金经理任期、风格漂移、费率远超同类、指数跟踪误差 resolved authority、开发覆盖 fallback、QDII 不适用、显式输入缺失、`-20%/-40%/-60%` 场景和基金类型阈值
- `tests/fund/analysis/test_valuation_state.py`：自动估值状态解析测试，覆盖 `index_fund` / `enhanced_index` 到沪深300/中证500 exact identity 映射、主动/债券/QDII/FOF 不适用、派生/策略/行业指数 fail-closed、复合支持指数歧义、显式/不可用/温度计 resolution 构造
- `tests/fund/analysis/test_checklist.py`：买入前检查清单测试，覆盖 7 问题顺序、红黄绿灰汇总、缺失显式输入、估值状态、`ValuationStateResolution` 投影、资金期限阈值和异常否决项输入
- `tests/fund/analysis/test_final_judgment.py`：最终判断派生策略测试，覆盖否决项、检查清单红灯、压力测试、quality gate block/not_run、黄灯/灰灯/数据不足、全绿值得持有、原因去重和 developer override 冲突记录
- `tests/fund/analysis/test_thermometer_calculator.py`：自建温度计纯计算器测试，覆盖 PE/PB 百分位、综合温度、阈值映射、空历史和非法估值 fail-closed
- `tests/fund/audit/test_audit_programmatic.py`：程序审计测试，覆盖 P1/P2/P3/C2/L1/R1/R2 规则、每章最小证据行、required_output_items marker、must_not_cover 禁止 marker、ITEM_RULE 渲染/删除合规、跟踪误差和指数画像 deterministic source guard、估值状态结构化真源 R1 审计、章节切分 fallback、必需输入缺失、selected/derived/source 最终判断冲突、故意注入错误和未知检查清单信号
- `tests/fund/template/test_contracts.py`：模板 CHAPTER_CONTRACT manifest 测试，覆盖 0-7 章完整性、设计标题、必需字段非空、所有标准基金类型 preferred_lens 解析和 fail-closed 校验
- `tests/fund/template/test_chapter_contract_constraints.py`：CHAPTER_CONTRACT 可执行 sidecar 测试，覆盖第 0-7 章 wrapper、主动基金第 3 章 material 证据要求，以及 deferred config-only 要求映射
- `tests/fund/template/test_lens_application.py`：preferred_lens 应用计划测试，覆盖所有标准基金类型 8 章 plan、default fallback 标记，以及非法基金类型、空章节、重复章节和越界章节 fail-closed
- `tests/fund/template/test_item_rules.py`：模板 ITEM_RULE manifest 测试，覆盖四条 conditional 规则、源文案 fidelity、optional schema fixture、显式 facet/fund type 冲突 fail-closed 和唯一段落标记检查
- `tests/fund/template/test_renderer.py`：模板渲染器测试，覆盖 8 章完整性、CHAPTER_CONTRACT 标题来源、渲染章节块、splitter fail-closed、正文与附录证据锚点格式、缺证章节显式输出、页码保留、非年报来源标注、preferred_lens 第 0/1 章确定性应用、第 0 章 veto/watch/压力测试最大风险与 checklist/stress/all-green 阈值、ITEM_RULE 六类基金渲染/删除矩阵、主动基金第 3 章缺 reviewed turnover/style evidence 降级措辞、非主动基金第 3 章文本回归、test-only 写作审计验证、跟踪误差 structured_data 替换、benchmark-only 编制方法/成分股不足边界、ITEM_RULE 多锚点证据边界、温度计免责声明和 external_api 锚点、程序审计输入兼容、缺失数据显式渲染、最终判断边界、禁用交易措辞和 README 同步
- `tests/fund/test_report_writing_audit.py`：dev-only 报告写作审计测试，覆盖主动基金第 3 章缺少换手率 / 风格变化证据时禁止稳定性正向判断、`data_gap` 降级措辞、证据锚点完整性、records fail-closed、must_not_cover 和 valid minimal case
- `tests/services/test_fund_analysis_service.py`：Service 编排测试，使用 fake extractor 避免网络/PDF 下载，覆盖 product mode 最小请求、developer override nested 契约、结构化抽取到渲染和程序审计的完整调用路径、自动估值显式短路、沪深300/中证500 exact identity 调用、不支持基金类型/不支持 exact code/复合支持指数歧义不调用、温度计不可用/计算错误灰灯/provider contract error fail-closed、fund_code 入口校验和规范化、quality gate `off / warn / block / not-run` 路径、结构化阻断异常、默认 gate run id 不覆盖，并验证不含 PDF 下载的单只基金分析低于 30 秒
- `tests/services/test_extraction_score_service.py`：P4-S2/P5-S4 评分 Service 测试，覆盖显式参数转发、`errors_path` 转发、非法 snapshot 路径和非法 errors 路径拒绝
- `tests/services/test_thermometer_service.py`：温度计 Service 测试，覆盖注入 fake adapter、默认全 A `wind_all_a` 路由、显式 cache_dir/force_refresh 转发、非法缓存路径拒绝、自建 `--index 000300` / `--index wind_all_a` 路由、批量代码规范化、preserve-order 去重、partial unavailable、stale cache fallback 和 unavailable；不触发真实网络
- `tests/ui/test_cli.py`：Typer CLI 测试，覆盖 `analyze` product mode 最小请求、缺省 `valuation_state=None` 自动估值契约、显式 `--valuation-state unavailable` 手动灰灯 opt-out、developer override 参数门禁、nested override 构造、gate summary/blocked/info 信息输出、失败非零退出、`checklist` 通过 Service 输出摘要、`thermometer` 默认全 A plain/JSON 输出、help 文案、自建 `--index wind_all_a` 和 `--index 000300` plain/JSON 输出、批量 `--index wind_all_a,000300` / `--index 000300,000905` 输出、malformed index exit 2
- `tests/scripts/test_selected_funds_smoke.py`：有知有行精选基金池 smoke 脚本测试，覆盖 CSV 数据质量、分层抽样、指定代码、CLI 命令构造和 `quality_gate_status` 记录；命令显式使用 `--dev-override --quality-gate-policy warn`，测试不触发真实网络
- `tests/scripts/test_report_quality_eval.py`：report-quality maintainer-only/dev-only 汇总脚本测试，使用 `tmp_path` fake JSONL / bundle 输入覆盖显式输入、summary 输出和 validator issue 汇总；不读取年报、不触发网络、PDF、extractor、Service、renderer 或产品 CLI
- `tests/config/test_paths.py`：仓库默认路径迁移守卫测试，覆盖 `fund_agent.config.paths` 默认值、导入隔离、UI 只依赖 Service 且不越过 Service 直连 Agent 层基金能力、旧常量别名、CLI 历史 score fixture 排除和散落 `Path("docs|reports|cache/...")` 默认值扫描
- `tests/test_repo_hygiene.py`：仓库发布卫生测试，覆盖 MIT License、`pyproject.toml` license、GitHub Actions CI 命令和 `.gitignore` artifact policy
- `tests/fund/integration/test_p1_sample_matrix.py`：P1 样本矩阵测试，验证 3 只样本基金 12 项结构化数据达到 `36/36`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`：P3 CLI 端到端矩阵测试，验证 3 只样本基金经 Typer CLI、Service、Agent 层基金能力、模板渲染和程序审计输出完整 8 章报告，并显式断言 P1/P2/P3/L1/R1/R2 全部审计规则执行通过、每章正文证据行和附录来源锚点完整；P19-S6 追加缺省 `--valuation-state` 的 510300 自动估值样本，断言 exact benchmark 只调用 `000300` 自建温度计
- `tests/fixtures/fund/extractors/profile/*.txt`：基础画像最小文本夹具，当前覆盖主动权益、增强指数、债券三类样本
- `tests/fixtures/fund/extractors/performance/*.txt`：`§3` 最小文本夹具，当前覆盖直接披露、估算披露、未披露三类投资者收益率路径
- `tests/fixtures/fund/extractors/manager_ownership/*.txt`：`§4/§8/§9` 最小文本夹具，当前覆盖完整披露、部分披露、未披露、换手率口径-only 路径

## 运行方式

运行当前已接受 slice 直接相关的测试：

```bash
pytest tests/test_repo_hygiene.py tests/config/test_paths.py -q
pytest tests/fund/documents -q
pytest tests/fund/pdf/test_parser.py -q
pytest tests/fund/extractors/test_profile.py -q
pytest tests/fund/extractors/test_performance.py -q
pytest tests/fund/extractors/test_manager_ownership.py -q
pytest tests/fund/extractors/test_holdings_share_change.py -q
pytest tests/fund/test_extraction_snapshot.py -q
pytest tests/fund/test_extraction_score.py -q
pytest tests/fund/data/test_nav_data.py -q
pytest tests/fund/data/test_thermometer.py -q
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py -q
pytest tests/fund/analysis/test_ratios.py -q
pytest tests/fund/analysis/test_thermometer_calculator.py -q
pytest tests/fund/analysis/test_valuation_state.py -q
pytest tests/fund/analysis/test_r_abc.py -q
pytest tests/fund/analysis/test_alpha_judge.py -q
pytest tests/fund/analysis/test_consistency_check.py -q
pytest tests/fund/analysis/test_investor_return.py -q
pytest tests/fund/analysis/test_risk_check.py -q
pytest tests/fund/analysis/test_checklist.py -q
pytest tests/fund/audit/test_audit_programmatic.py -q
pytest tests/fund/template/test_contracts.py -q
pytest tests/fund/template/test_renderer.py -q
pytest tests/services -q
pytest tests/ui -q
pytest tests/scripts/test_selected_funds_smoke.py -q
pytest tests/scripts/test_report_quality_eval.py -q
pytest tests/fund/integration/test_p1_sample_matrix.py -q
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
```

P19-S6 生产验证当前推荐的确定性回归组合：

```bash
pytest tests/fund/analysis/test_valuation_state.py tests/services/test_fund_analysis_service.py -q
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/fund/data/test_thermometer.py -q
```

以下 CLI smoke 会触发真实 akshare / 缓存路径，不放入常规 pytest；用于发布前人工验证当前本机依赖和网络状态：

```bash
fund-analysis thermometer --json
fund-analysis thermometer --index 000300 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --force-refresh --json
```

如果只验证当前 extractor worktree，可运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q
```

覆盖率 gate：

```bash
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

该命令要求安装 dev 依赖中的 `pytest-cov`。当前 CI / P3-S7 gate 要求 `fund_agent` 总覆盖率不低于 50%，这是自动阻断阈值，不是单文件质量目标。

单文件覆盖率 ≥80% 是新增或大幅修改模块的评审目标。实现或重构时应优先补足对应测试；暂时无法达到时，必须在 code review、controller judgment 或 residual risk 中说明原因、风险范围和后续补测路径。不要把全局 50% gate 当作单文件覆盖率目标已满足的证明，也不要在未完成缺口评估前直接提高 CI 阈值。

发布就绪完整验证：

```bash
uv sync --extra dev --frozen
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

性能 gate：

```bash
pytest tests/services/test_fund_analysis_service.py -q
```

Service 性能测试使用 fake extractor 排除网络和 PDF 下载，只验证结构化数据已就绪后的单只基金分析、模板渲染和程序审计低于 30 秒。

真实精选基金池 smoke 不放入常规 pytest。它会触发网络、PDF 下载和真实缓存写入，应单独运行：

```bash
.venv/bin/python scripts/selected_funds_smoke.py
.venv/bin/python scripts/selected_funds_smoke.py --code 004393 --run --output-dir reports/smoke/004393
.venv/bin/python scripts/selected_funds_smoke.py --sample-per-category 1 --run --continue-on-fail --output-dir reports/smoke/selected-1x
```

脚本默认 dry-run，只校验 `docs/code_20260519.csv` 并打印计划；`--run` 才执行 `fund-analysis analyze`。输出目录会保留每只基金报告、stderr、`results.jsonl` 和 `summary.md`，便于人工复核和后续回归比较。

P4-S1 字段级快照可通过 CLI 单独运行，会触发真实年报仓库和净值数据路径：

```bash
fund-analysis extraction-snapshot --run-id p4-s1-004393 --fund-code 004393 --report-year 2024
fund-analysis extraction-snapshot --run-id p4-s1-selected-1x --sample-per-category 1 --report-year 2024
fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s1-selected-1x/snapshot.jsonl
```

pytest 中的 snapshot 和 score 测试必须继续使用 fake extractor 或临时 JSONL，禁止依赖真实 PDF、缓存或网络。

report-quality dev-only 汇总工具只消费调用方显式准备好的 JSONL 或 bundle JSON，不属于产品 CLI。当前真实用法：

```bash
.venv/bin/python scripts/report_quality_eval.py \
  --jsonl /tmp/fund-agent-small-baseline-eval-20260526/bundles.jsonl \
  --bundle /tmp/fund-agent-small-baseline-eval-20260526/bundle.json \
  --output /tmp/fund-agent-small-baseline-eval-20260526/validator-summary.json \
  --run-id small-baseline-eval:20260526
```

测试必须继续使用 `tmp_path` fake JSONL / bundle 输入，不得读取年报、PDF、cache 或网络。

## 维护约定

- 新增 Agent 层基金能力测试时，优先使用 fixture、mock 或临时目录隔离网络和文件系统副作用。
- 会产生报告、snapshot、quality gate run、写作迭代、评分迭代、数据源迭代或 cache 的测试必须使用临时目录；默认生成目录 `cache/`、`reports/extraction-snapshots/`、`reports/quality-gate-runs/`、`reports/smoke/`、`reports/scoring-runs/`、`reports/writing-runs/` 和 `reports/data-source-runs/` 属于本地运行产物，不应作为测试 fixture 写入。
- 仓库默认路径变更必须同步更新 `fund_agent/config/paths.py`、`tests/config/test_paths.py` 和相关 README；不要在 UI、Service 或 Fund 模块里新增散落的 `Path("docs/...")`、`Path("reports/...")` 或 `Path("cache/...")` 默认值。
- 文档仓库相关测试应围绕公共契约断言，不直接把 `pdf/*` helper 当成上层接口。
- 年报来源编排与仓库 metadata 测试必须使用 fake source、fake network 和临时 PDF 路径，覆盖 unavailable 与 not-found 最终错误语义、schema drift / identity mismatch / integrity error 阻断 fallback、EID request-level timeout、PDF Content-Type 与 `%PDF-` 校验、source metadata 持久化、损坏来源元数据降级、legacy cache 兼容和并发防串扰；不得依赖真实 EID、Eastmoney 或 akshare。
- `pdf/*` 目录下的测试允许直接覆盖内部 helper，但 README、示例和业务代码不应把它们当成稳定入口。
- extractor 测试必须优先锁定章节边界、证据锚点和 `missing/direct/estimated` 状态，不把后续 P2 的分析结论混入 P1 数据层测试。
- `§3` 表现相关测试当前只允许依赖 `ParsedAnnualReport` 的 `§3` 章节文本与表格，不要在 P1 阶段把 `§10` fallback 或净值序列计算混进同一组测试。
- `§4/§8/§9` 管理人/持有人测试当前只锁定原始披露抽取，不写言行一致性、利益一致性或成本判断断言；真实年报表头换行和跨页组表头必须用构造的 `ParsedTable` 复现。
- `§8/§10` 持仓/份额测试必须优先锁定表格型 anchor，不把资金流向判断或投资者收益 fallback 混进 P1 数据层测试；申购/赎回拆分表应覆盖净变动计算，非份额变动表应覆盖误命中回归。
- 有知有行公开页温度计测试必须使用 fake fetcher 和 HTML snippet，覆盖缓存新鲜度、stale fallback 和 unavailable 状态；自建温度计 source/cache/service/CLI 测试必须使用 fake akshare、临时缓存或 fake Service 覆盖 `wind_all_a` 与宽基指数路径；常规 pytest 不得依赖实时有知有行页面或实时 akshare 网络，真实 `fund-analysis thermometer` 只作为人工 smoke。
- R=A+B-C 测试必须锁定公式闭合与缺失输入状态；股票仓位在 P1 未稳定抽取前必须作为显式输入，不允许在测试中隐藏默认假设。
- 超额收益性质判断测试必须显式提供市场环境和来源解释强度；不要从收益结果中反推牛熊环境或基金经理能力。
- 言行一致性测试必须显式提供实际持仓风格和股票仓位；不要从重仓名称或行业分布中猜测风格。
- 投资者获得感测试必须区分投资者收益率直接披露和缺失路径；不要在分析层静默估算具体投资者收益。
- 否决项检查测试必须覆盖显式输入缺失路径；不要把缺少基金经理任期、同类费率或跟踪误差强行判为安全。
- 压力测试必须覆盖固定场景、基金类型阈值和缺少最大可承受亏损比例路径；不要在分析层猜测用户承受能力。
- 检查清单测试必须覆盖 7 问题完整性和红黄绿灰规则；估值、资金期限等用户/外部输入缺失时必须返回灰灯，不允许默认通过。
- 程序审计测试必须覆盖必需输入缺失和故意注入错误；P1/P2/P3 只审报告结构与每章最小证据行，C2 只审确定性 CHAPTER_CONTRACT marker / 元数据一致性和 ITEM_RULE 段落标记合规，L1/R1/R2 必须消费结构化结果，不靠报告文字间接判断，也不能把缺失输入伪装成规则通过。
- 模板契约测试必须覆盖 8 章 CHAPTER_CONTRACT manifest 完整性、标题、必需字段、所有标准基金类型 preferred_lens 可解析性和 fail-closed 漂移场景；不得依赖 renderer 私有常量。
- CHAPTER_CONTRACT sidecar / 写作审计测试必须只消费手工构造的 `ReportEvidenceBundle`、records 或章节草稿代理；不得读取 PDF/cache、调用文档仓库、接入 renderer、Service/CLI 或 FQ0-FQ6 quality gate。
- 模板 ITEM_RULE 测试必须覆盖内置 manifest 只包含当前模板草稿四条 conditional 规则，optional 只用本地 fixture 验证 schema/evaluator，显式 facet 不得覆盖已识别基金类型，段落存在判断不得使用普通正文短语。
- 模板渲染测试必须覆盖 8 章结构、CHAPTER_CONTRACT 标题来源、渲染章节块、splitter fail-closed、证据锚点格式、缺证章节显式文本、页码保留、非年报来源标注、第 0 章最大风险和动作阈值结构化信号、ITEM_RULE 固定段落与六类基金触发矩阵、主动基金第 3 章缺 reviewed turnover/style evidence 降级措辞、非主动基金第 3 章文本回归、test-only 写作审计验证、ITEM_RULE 多锚点/空锚点/重复锚点证据边界、程序审计输入兼容和禁用交易建议措辞；不得只做字符串存在性 smoke test。
- Service 测试必须通过 fake extractor 隔离网络、PDF 下载和文档仓库副作用，只断言 Service 对 Agent 层基金能力的编排契约；自动估值测试必须显式断言 unsupported / ambiguous 映射不调用温度计，避免用灰灯结果间接证明调用边界。
- UI CLI 测试只验证参数解析、Service 调用、stdout/stderr 和退出码；不得在 UI 层直接断言基金分析规则。
- Snapshot 测试只断言 CSV 校验、字段级 schema、`comparable_values` 白名单、summary/error 写入和 known failure 捕获；指数质量字段可比性只覆盖稳定标量子字段，不加入计算跟踪误差或外部指数序列；不得在 P4-S1 测试中修正或期待 `004393` 分类改善。
- Score 测试只消费 P4-S1 snapshot 记录、P4-S1 errors 记录、精选基金池 CSV 或 strict golden answer JSON；不得读取 PDF/cache，correctness 断言只能基于 snapshot `comparable_values` 显式字段，并必须区分白名单字段明确缺失、非白名单字段 unavailable、`not_configured`、`fund_not_covered`、`year_not_covered` 和 `no_comparable_fields`；`fund_quality` 断言必须覆盖 App 类别、基金类型、缺失率、指数质量字段适用性过滤和同一基金多行冲突路径；`failed_funds` 断言必须只来自 `errors.jsonl`。
- Golden answer build 测试只消费人工审核后的 Markdown；不得读取 PDF/cache，不得把预填底稿未审核值直接当 correctness 真值；strict JSON identity 必须覆盖 `fund_code + report_year + field_name + sub_field`。
- Quality gate 测试只消费 `score.json` 形态输入；不得读取 PDF/cache，不得执行 LLM 审计；FQ0 correctness coverage 测试必须断言 `reason`、`coverage_scope` 和 fund-scoped metadata，不能把 golden coverage absence 断言成 gate `not_run`；FQ4 必须基于结构化缺失率，不允许通过解析报告 Markdown 中的“数据不足”字样实现；FQ6 必须基于 `score.json.failed_funds`，不得扫描 `errors.jsonl`。
- P3 CLI 端到端矩阵可通过 fake repository、fake nav provider 和 fake thermometer 隔离网络/PDF/akshare 副作用，但必须经过真实 CLI 参数解析、Service 编排、模板渲染和程序审计，并断言 `ProgrammaticAuditResult.checked_rules` 覆盖 P1/P2/P3/C2/L1/R1/R2，同时验证 8 章正文证据行、附录年报章节/表格/行定位和无缺证占位。
- 新增基金类型或章节 extractor 时，先补 fixture，再补测试，再扩实现；不要只靠真实年报手工回归。
