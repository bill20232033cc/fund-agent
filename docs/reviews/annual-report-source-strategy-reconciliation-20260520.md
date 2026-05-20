# Annual Report Source Strategy Reconciliation - 2026-05-20

## Trigger

AgentCodex 建议调整基金年报下载源优先级：

- EID / 证监会资本市场电子化信息披露平台作为主源。
- 天天基金 / Eastmoney 作为 fallback。
- 巨潮不作为公募基金年报主源。

## Current Code Fact

当前实现不直接访问巨潮：

- `fund_agent/fund/pdf/downloader.py` 使用 `akshare.fund_announcement_report_em(symbol=fund_code)` 查询基金公告。
- 命中年度报告后取 `报告ID`，拼接 `https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf` 下载 PDF。
- 上层仍通过统一文档仓库入口 `FundDocumentRepository.load_annual_report(...)` 访问年报，不直接操作 PDF 文件。

这说明当前系统已经满足“不要把上层绑定到具体下载源”的主要边界，但底层主源仍是 Eastmoney/akshare，不是监管披露主源。

## External Source Check

已核对公开来源：

- 证监会公告称资本市场电子化信息披露平台已上线，网址为 `eid.csrc.gov.cn`，可免费查询公募基金管理公司等主体依法公开披露的信息。
- 证监会/人民银行已发布《公开募集证券投资基金信息披露电子化规范》金融行业标准，说明公募基金信息披露有电子化、结构化、数据化方向。
- 早期证监会基金信息披露网站上线公告提到基金信息披露 XBRL 工作、基金报告 XBRL 文档和信息披露平台。
- 公开基金销售机构页面提示可登录“中国证监会基金电子披露网站（http://eid.csrc.gov.cn/fund）”查询更多信息。

Sources:

- `https://www.csrc.gov.cn/csrc/c100028/c1000699/content.shtml`
- `https://www.csrc.gov.cn/csrc/c100028/c6987176/content.shtml`
- `https://www.csrc.gov.cn/csrc/c100028/c1002707/content.shtml`
- `https://szrcb.com/szrcb/grfw/cfgl/dxjj/dxjjxxpl/index.shtml`

## Controller Judgment

接受方向，但不进入当前 P6-S1。

理由：

- 当前 gate 是 `P6-S1 template contract manifest implementation`，目标是模板契约机器化；年报下载源迁移属于文档仓库 / data-source adapter 方向，模块所有权不同。
- 数据源迁移会触及 `fund_agent/fund/pdf/downloader.py`、`fund_agent/fund/documents/adapters/annual_report_pdf.py` 和相关 PDF 下载测试，应该作为独立 phase / slice 做 plan/review/implementation。
- 统一文档仓库接口已经存在，适合承载 EID-primary + fallback 的策略，不需要改变上层 extractor、Service 或 UI。

## Recommended Follow-up

新增后续阶段候选：`P7 annual report source migration`。

候选切片：

| Slice | Scope | Acceptance signal |
|---|---|---|
| P7-S1 | EID source research spike | 验证 `eid.csrc.gov.cn/fund` 的基金代码解析、公告查询、年度报告筛选和 PDF 下载路径；输出接口样本和失败模式 |
| P7-S2 | Document repository downloader abstraction | 在仓库内部抽象 `AnnualReportSource`，明确 source priority、fallback、timeout、rate limit、编码和接口变化处理 |
| P7-S3 | EID primary implementation | 先 EID，失败再 Eastmoney/akshare fallback；所有结果保留 source metadata |
| P7-S4 | Evidence/source metadata hardening | `ParsedAnnualReport` 或文档元数据记录 PDF source、公告 id、fund id、instance id / pdf id，供证据审计和排错 |

## Guardrails

- 不让 UI / Service 直接知道 EID、Eastmoney、天天基金或巨潮。
- 不把 PDF source 写进 `extra_payload`；所有源策略参数必须显式声明或封装在仓库配置中。
- EID 接口必须做 bounded timeout、限流、重试上限和 schema drift 失败闭合。
- Fallback 不能静默返回错误年份；请求年份必须同源校验。
- 当前 golden answer 和 correctness 仍以已下载 PDF 原文为准，数据源迁移不能改变证据锚点语义。

## Status

Tracked. Not a blocker for P6-S1.
