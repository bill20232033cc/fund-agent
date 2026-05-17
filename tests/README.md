# 测试手册

当前测试按 Capability 边界分层，新增用例应跟随实现所在目录组织，并优先覆盖当前稳定公共契约，而不是偶然实现细节。

## 当前目录

- `tests/fund/documents/test_repository.py`：文档仓库契约测试，验证仓库对外返回 `ParsedAnnualReport`，不暴露本地 `Path`
- `tests/fund/documents/test_cache.py`：文档缓存最小闭环测试，覆盖 PDF 元信息缓存、parsed report 物化和缓存失效回退
- `tests/fund/pdf/test_downloader.py`：PDF 下载 helper 测试，验证内部缓存命中、强制刷新下载和年报 URL 组装
- `tests/fund/pdf/test_parser.py`：章节定位测试，覆盖 `§3` 正文命中、目录误判回归和偏移单调递增
- `tests/fund/extractors/test_profile.py`：基础画像 extractor 测试，覆盖分类先行、`classified_fund_type` / `classification_basis` 稳定输出，以及费率/基准/规模/经理 anchor
- `tests/fund/extractors/test_performance.py`：`§3` 表现 extractor 测试，覆盖净值增长率/基准收益率 anchor，以及投资者收益率 `direct / estimated / missing` 三态
- `tests/fund/extractors/test_manager_ownership.py`：`§4/§8/§9` 管理人/持有人 extractor 测试，覆盖策略文本、换手率、持有披露、持有人结构和 `missing` 路径
- `tests/fund/extractors/test_holdings_share_change.py`：`§8/§10` 持仓/份额 extractor 测试，覆盖前十大重仓、行业分布、份额变动和表格型 anchor
- `tests/fund/data/test_nav_data.py`：净值数据适配器测试，覆盖 `nav_cache` 命中和强制刷新
- `tests/fund/analysis/test_r_abc.py`：R=A+B-C 收益归因测试，覆盖公式闭合、P1 字段解析、证据锚点传递和缺失输入路径
- `tests/fund/analysis/test_alpha_judge.py`：超额收益性质判断测试，覆盖结构性、部分结构性、阶段性、不适用、样本不足和显式环境输入要求
- `tests/fund/analysis/test_consistency_check.py`：言行一致性检验测试，覆盖 4 维度信号、红灯冲突和显式实际风格/仓位输入要求
- `tests/fund/analysis/test_investor_return.py`：投资者获得感分析测试，覆盖行为损益、投资者收益缺失、追涨/抄底资金流向和份额字段缺失
- `tests/fund/analysis/test_risk_check.py`：否决项检查与压力测试，覆盖清盘风险、基金经理任期、风格漂移、费率远超同类、指数跟踪误差、显式输入缺失、`-20%/-40%/-60%` 场景和基金类型阈值
- `tests/fund/analysis/test_checklist.py`：买入前检查清单测试，覆盖 7 问题顺序、红黄绿灰汇总、缺失显式输入、估值状态、资金期限阈值和异常否决项输入
- `tests/fund/audit/test_audit_programmatic.py`：程序审计测试，覆盖 P1/P2/P3/L1/R1/R2 规则、必需输入缺失、故意注入错误和未知检查清单信号
- `tests/fund/integration/test_p1_sample_matrix.py`：P1 样本矩阵测试，验证 3 只样本基金 12 项结构化数据达到 `36/36`
- `tests/fixtures/fund/extractors/profile/*.txt`：基础画像最小文本夹具，当前覆盖主动权益、增强指数、债券三类样本
- `tests/fixtures/fund/extractors/performance/*.txt`：`§3` 最小文本夹具，当前覆盖直接披露、估算披露、未披露三类投资者收益率路径
- `tests/fixtures/fund/extractors/manager_ownership/*.txt`：`§4/§8/§9` 最小文本夹具，当前覆盖完整披露、部分披露、未披露、换手率口径-only 路径

## 运行方式

运行当前已接受 slice 直接相关的测试：

```bash
pytest tests/fund/documents -q
pytest tests/fund/pdf/test_parser.py -q
pytest tests/fund/extractors/test_profile.py -q
pytest tests/fund/extractors/test_performance.py -q
pytest tests/fund/extractors/test_manager_ownership.py -q
pytest tests/fund/extractors/test_holdings_share_change.py -q
pytest tests/fund/data/test_nav_data.py -q
pytest tests/fund/analysis/test_r_abc.py -q
pytest tests/fund/analysis/test_alpha_judge.py -q
pytest tests/fund/analysis/test_consistency_check.py -q
pytest tests/fund/analysis/test_investor_return.py -q
pytest tests/fund/analysis/test_risk_check.py -q
pytest tests/fund/analysis/test_checklist.py -q
pytest tests/fund/audit/test_audit_programmatic.py -q
pytest tests/fund/integration/test_p1_sample_matrix.py -q
```

如果只验证当前 extractor worktree，可运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q
```

## 维护约定

- 新增 Capability 测试时，优先使用 fixture、mock 或临时目录隔离网络和文件系统副作用。
- 文档仓库相关测试应围绕公共契约断言，不直接把 `pdf/*` helper 当成上层接口。
- `pdf/*` 目录下的测试允许直接覆盖内部 helper，但 README、示例和业务代码不应把它们当成稳定入口。
- extractor 测试必须优先锁定章节边界、证据锚点和 `missing/direct/estimated` 状态，不把后续 P2 的分析结论混入 P1 数据层测试。
- `§3` 表现相关测试当前只允许依赖 `ParsedAnnualReport.get_section_text("§3")`，不要在 P1 阶段把 `§10` fallback 或净值序列计算混进同一组测试。
- `§4/§8/§9` 管理人/持有人测试当前只锁定原始披露抽取，不写言行一致性、利益一致性或成本判断断言。
- `§8/§10` 持仓/份额测试必须优先锁定表格型 anchor，不把资金流向判断或投资者收益 fallback 混进 P1 数据层测试。
- R=A+B-C 测试必须锁定公式闭合与缺失输入状态；股票仓位在 P1 未稳定抽取前必须作为显式输入，不允许在测试中隐藏默认假设。
- 超额收益性质判断测试必须显式提供市场环境和来源解释强度；不要从收益结果中反推牛熊环境或基金经理能力。
- 言行一致性测试必须显式提供实际持仓风格和股票仓位；不要从重仓名称或行业分布中猜测风格。
- 投资者获得感测试必须区分投资者收益率直接披露和缺失路径；不要在分析层静默估算具体投资者收益。
- 否决项检查测试必须覆盖显式输入缺失路径；不要把缺少基金经理任期、同类费率或跟踪误差强行判为安全。
- 压力测试必须覆盖固定场景、基金类型阈值和缺少最大可承受亏损比例路径；不要在分析层猜测用户承受能力。
- 检查清单测试必须覆盖 7 问题完整性和红黄绿灰规则；估值、资金期限等用户/外部输入缺失时必须返回灰灯，不允许默认通过。
- 程序审计测试必须覆盖必需输入缺失和故意注入错误；P1/P2/P3 只审报告结构，L1/R1/R2 必须消费结构化结果，不靠报告文字间接判断，也不能把缺失输入伪装成规则通过。
- 新增基金类型或章节 extractor 时，先补 fixture，再补测试，再扩实现；不要只靠真实年报手工回归。
