# NAV Repository / Source Adapter Adjusted-Basis Primer

日期：2026-05-28

角色：Gateflow worker

Gate：`NAV repository/source adapter adjusted-basis contract gate`

结论：`blocked-with-contract-gap`

本 artifact 只建立 fund NAV / share-class / adjusted-basis primer，不做 implementation，不修改 Python / schema / score / quality gate，不解除 `drawdown_stress` blocker。

## 1. 真源复述

已读取并作为本 gate 真源：

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`
- `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`
- `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`
- `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`

复述结论：

- 当前架构真源是 `UI -> Service -> Host -> Agent`。当前确定性 CLI 主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力；未开 Host/Agent gate 前不得引入 Host/Agent/dayu runtime。
- 基金文档读取必须只通过 `FundDocumentRepository`。生产年报 PDF 访问不得绕过 repository 直接读 PDF / cache / source helper。
- 年报来源 fallback 只能在 `not_found` / `unavailable` 时允许；`schema_drift` / `identity_mismatch` / `integrity_error` 必须 fail-closed。
- `FundNavDataAdapter` 是当前 Fund-layer NAV 公开边界，但上一 gate 已判断它只能证明 006597 raw 单位净值序列可达，不能证明 adjusted / cumulative / total-return basis、source-returned identity、dividend adjustment status 或 calculation-ready provenance。
- 上一 `drawdown_stress NAV-derived evidence contract` gate 结论是 `blocked-with-decision`：NAV-derived drawdown 只能作为未来 candidate，当前 `drawdown_stress` 仍是 weak qualitative，不能把“控制回撤”升级为 quantitative。
- 最新 006597/2024 snapshot 显示 `bond_risk_evidence.v1` satisfied groups 为 `duration_rate_risk`、`credit_risk`、`leverage_liquidity`、`asset_allocation_holdings_mix`、`redemption_share_pressure`、`convertible_bond_equity_exposure`；weak groups 只有 `drawdown_stress`。
- 最新 score 的 `bond_risk_evidence_missing.baseline_blocking=true` 只剩 `drawdown_stress`。最新 quality gate 仍按 FQ0-FQ6 输出 warn，不允许削弱质量门控或把本 gate 作为 golden / baseline promotion。

## 2. 监管 / 行业 / 披露规则来源

已核验来源：

- 中国证监会《公开募集证券投资基金信息披露管理办法》页面：`https://www.csrc.gov.cn/csrc/c101877/c1029542/content.shtml`
- 中国证监会《公开募集证券投资基金信息披露管理办法》PDF / 国务院公报镜像：`https://www.gov.cn/gongbao/content/2019/content_5462516.htm`
- 中国证监会《关于实施〈公开募集证券投资基金信息披露管理办法〉有关问题的规定》：`https://www.csrc.gov.cn/csrc/c101877/c1029541/content.shtml`
- 中国基金业协会《5项公开募集证券投资基金信息披露XBRL模板》公告：`https://www.amac.org.cn/xwfb/xhyw/202603/t20260313_27409.html`
- 中基协 XBRL 模板 PDF 候选：净值公告、年度报告和中期报告模板。该来源能证明行业披露体系把净值公告、年度/中期报告作为结构化披露对象。
- 006597 的 2024/2025 年报 §3.1 / §3.2 / §3.3，通过 `FundDocumentRepository` 验证。

来源缺口：

- 未在证监会或中基协官网可靠定位到可直接引用的旧版《证券投资基金信息披露编报规则第2号〈基金净值表现的编制及披露〉》原文入口。第三方 PDF 可作为候选线索，但本 gate 不把它作为 contract 真源。
- 公开监管披露模板能证明“单位净值 / 累计净值 / 净值增长率 / 分红”披露对象；“复权净值 / total-return adjusted series”的具体计算口径通常出现在基金评价、数据商或投教材料中，不能在本 gate 中被当作已由当前 repository/provider 证明的生产数据。

## 3. NAV 概念 primer

### 3.1 单位净值

单位净值是每一基金份额在估值日对应的基金份额净值，通常用于申购赎回价格基础。监管披露规则要求公开披露基金资产净值、基金份额净值，且托管人需对基金管理人编制的基金资产净值、基金份额净值等公开披露信息复核。

Contract 含义：

- `raw_unit_nav` 只能表示未声明分红再投资调整的单位净值 path。
- 它可以用于展示净值走势或现值对照。
- 它不能在存在分红、拆分、折算、份额类别不明或 adjustment basis unknown 时直接作为 max drawdown strong evidence。

### 3.2 累计净值

累计净值通常表达单位净值加历史单位分红后的长期累计表现。年报 §3.1 披露的是“基金份额累计净值增长率”，不是每日 path。

Contract 含义：

- `accumulated_nav` 可以证明区间累计表现更接近含分红的长期收益披露口径。
- 只有当 provider 提供逐日 / 周 / 月 path，且字段明确为累计净值或累计净值增长率 path，才可用于 max drawdown 候选。
- 年报 §3.1 的年末累计净值增长率只是年度端点，不足以计算 path-dependent max drawdown。

### 3.3 复权 / 分红调整净值

复权或分红调整净值是把分红、拆分、折算等事件调整回净值序列，使序列更接近投资者持有期间总回报 path。行业常见做法区分累计净值和复权净值：累计净值通常把历史分红加回，复权净值通常进一步按分红再投资或还原因子生成连续收益序列。

Contract 含义：

- `dividend_adjusted_nav` / `total_return` 是 max drawdown strong evidence 的优先候选。
- provider 必须明确给出 adjustment basis、分红事件处理方式、份额类别、日期区间、记录数和来源元数据。
- 如果只拿 raw 单位净值，则必须证明目标期间无分红 / 拆分 / 折算，且 contract 明确允许 raw basis；否则 fail-closed。

### 3.4 净值增长率

年报 §3.1 披露本期基金份额净值增长率和累计期末指标；§3.2 披露不同阶段的份额净值增长率、净值增长率标准差、业绩比较基准收益率和标准差。

Contract 含义：

- §3.2 的“过去三个月 / 六个月 / 一年 / 三年 / 五年 / 自成立以来”区间净值增长率可以作为区间收益或波动标准差披露证据。
- §3.2 不能替代 daily / periodic NAV path 计算 max drawdown，因为 max drawdown 是路径指标，至少需要同一 share class、同一 adjustment basis、连续或有 completeness 状态的时间序列。
- §3.2 标准差是披露表中的波动统计，不等于最大回撤。

## 4. 年报 §3.1 / §3.2 / §3.3 的证据能力

| 年报章节 | 能证明 | 不能证明 |
|---|---|---|
| §3.1 主要会计数据和财务指标 | 各份额类别的本期基金份额净值增长率、期末基金份额净值、累计净值增长率、期末资产净值等端点事实 | 每日 path、最大回撤、分红再投资 path、provider 调整口径、source adapter identity |
| §3.2 基金净值表现 | 各份额类别在标准区间的净值增长率、净值增长率标准差、基准收益率、基准标准差；新增份额起算日说明 | max drawdown；daily / periodic path；分红调整后的可计算序列；A/C/E/F 混合序列 |
| §3.3 过去三年利润分配 | 各份额类别过去三年是否分红，以及分红金额、现金 / 再投资形式发放额 | 自动生成复权净值；证明 raw 单位净值已排除分红除息影响；证明 provider 已使用 total-return basis |

## 5. 006597 多份额类别 primer

通过 `FundDocumentRepository` 验证：

- 2024 source：`eid`，instance `1253099`，report_name `国泰利享中短债债券型证券投资基金2024年年度报告`。
- 2025 source：`eid`，instance `1450363`，report_name `国泰利享中短债债券型证券投资基金2025年年度报告`。
- 2025 §3.1 披露 A / C / E / F 四类期末基金份额净值：A `1.2192`，C `1.2022`，E `1.1967`，F `1.2191`。用户给定的 E `1.1744` 与 repository 读取的 2025 年报 §3.1 不一致，需 controller 复核是否来自其他报告期或其它来源。
- 2025 §3.2 按 A / C / E / F 分别披露净值增长率和标准差；F 类披露自新增 F 类份额起至今；§3.2 注释显示 F 自 `2024-10-08` 增加、`2024-10-15` 开始计算 F 类基金份额净值和基金份额累计净值。
- 2025 §3.3：A / C 过去三年未进行利润分配；E 类 2023 每 10 份基金份额分红 `0.080`，现金形式 `7,273,431.12`，再投资形式 `1,871,517.43`，合计 `9,144,948.55`，2024 / 2025 为 `-`；F 类自新增份额以来未进行利润分配。

Contract implication：

- `006597` 主代码优先映射 A 类；但产品层面报告可根据需要展示各份额类别 range / worst。
- A / C / E / F 不能混成一条 NAV。不同份额类别费率、起算日、分红历史和代码不同。
- E 类存在 2023 分红。如果使用 E 类 raw unit NAV 跨越分红期间，分红除息可能被误判为 drawdown；不得直接形成 strong quantitative evidence。
- F 类新增时间较晚，不能与 A/C/E 的全历史 path 混算；只能按其自身起算日起的序列和披露期判断。

## 6. 对 drawdown quantitative evidence 的要求

最大回撤是 path-dependent 风险指标。对于债券基金 `drawdown_stress`：

- 优先使用 `total_return` 或 `dividend_adjusted_nav` basis。
- 次优使用明确标注且足够连续的 `accumulated_nav` path，但需说明它是否等价于分红调整 path；不明时降级。
- `raw_unit_nav` 只在目标期间经 repository 年报 / 分红事件源证明无分红、拆分、折算，且 contract 明确允许时，才可作为 limited eligible basis。
- `adjustment_basis_unknown`、`share_class_unknown`、`identity_status != verified`、`schema_drift`、`identity_mismatch`、`integrity_error` 必须 fail-closed。
- §3.2 区间净值增长率不能替代 daily / periodic NAV path 的 max drawdown。

## 7. Primer 对后续 contract 的直接约束

1. 稳定 contract 必须放在 Agent/Fund NAV repository/source adapter 层，不能由 Service / score / quality gate 绕过 adapter 直接读 source/cache。
2. NAV record 必须绑定 share class。`006597` 默认 A 类映射只是一个 explicit mapping，不代表产品所有份额共用同一序列。
3. adjustment basis 必须是闭集 enum，并能区分 `raw_unit_nav`、`accumulated_nav`、`dividend_adjusted_nav`、`total_return`、`unknown`。
4. max drawdown 消费端只能消费 accepted NAV contract，不直接依赖 akshare / Eastmoney / sqlite / PDF cache internals。
5. 当前 `FundNavDataAdapter.load_nav_data("006597")` 不满足上述 contract，下一最小 gate 是 source adapter implementation gate，而不是 drawdown blocker 解除 gate。
