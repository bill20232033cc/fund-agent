# P1 数据层计划审查裁决

> 日期：2026-05-17
> Reviewed target: `docs/reviews/p1-plan-2026-05-17.md`
> 设计真源：`docs/design.md`
> 总控真源：`docs/implementation-control.md`
> 约束真源：`AGENTS.md`

## 审查范围

- P1 数据层的 plan 是否达到 code-generation-ready
- 切片顺序是否能在最短路径内形成可验证闭环
- 是否满足统一文档仓库接口、Capability 边界、基金类型优先、证据可溯源

## 审查输入

- 独立审查 A：当前 `downloader.py` / `parser.py` 能力边界、`§3` 漏识别 root cause、最小切片排序
- 独立审查 B：统一文档仓库接口的边界归属、命名空间约束、与 design/control 的张力
- controller 本地验证：
  - `110011` 的 2024 年报可下载
  - PDF 全文中 `§3` 正文实际存在
  - 当前 `locate_sections()` 未返回 `§3`

## 已测试假设

- 假设 1：`§3` 缺失是 PDF 噪声问题，而不是规则问题
  - 结论：不成立。正文中存在 `§3 主要财务指标、基金净值表现及利润分配情况`，当前规则写窄导致漏识别。
- 假设 2：可以先继续补 `downloader/parser/cache`，后面再统一接口
  - 结论：不成立。这样会把文件系统访问和 PDF 细节继续扩散到上层，违反 `AGENTS.md` 的统一文档仓库接口约束。
- 假设 3：在 extractor schema 冻结前就固化 `structured_data` SQLite 表是安全的
  - 结论：不成立。会导致 schema churn 和返工，应该后移到 extractor 收口后的集成 slice。

## Findings

### 编号-未修复-高-公共文档契约被放进了 `pdf` 命名空间
- **位置**: 原计划 `5.1 文档仓库契约`、`7.2 预计新增的 Capability 文件`
- **问题类型**: 架构边界 / 过度耦合
- **当前写法**: 把 `FundDocumentRepository`、`DocumentKey`、`ParsedAnnualReport` 等公共契约建议放在 `fund_agent/fund/pdf/*`
- **反例/失败场景**: 后续招募说明书、季报、审计复核都被迫依赖 `pdf` 命名空间，导致“统一文档仓库接口”沦为 PDF 具体实现
- **为什么有问题**: `AGENTS.md` 要求基金文档访问收口到统一仓库接口，公共契约不应绑定到底层适配器目录
- **直接证据**: `AGENTS.md` 中“基金文档只通过统一文档仓库接口访问”；设计/总控当前对 `pdf/*` 的描述只是能力预览而非公共契约
- **影响**: 后续文档类型扩展和 tool 化都会越界；implementation agent 会误把 `pdf/*` 当作上层稳定依赖面
- **建议改法和验证点**: 公共契约迁到 `fund_agent/fund/documents/*`；`fund_agent/fund/pdf/*` 仅保留为仓库内部 PDF 适配器；测试验证 extractor 不直接 import `fund_agent.fund.pdf.*`
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高
- **裁决**: accepted
- **修复状态**: 已修复进计划

### 编号-未修复-中-`structured_data` 缓存在 schema 冻结前落地
- **位置**: 原计划 `5.3 缓存 Schema`、`P1-S3`
- **问题类型**: sequencing / 不可直接实施
- **当前写法**: 在 P1-S3 冻结 `structured_data` SQLite 表
- **反例/失败场景**: `P1-S4 ~ P1-S7` 仍在演化 `StructuredFundDataBundle` 字段和提取模式，缓存 schema 会反复变更
- **为什么有问题**: 缓存应晚于 extractor schema accepted，否则会把未稳定契约提前固化
- **直接证据**: 计划本身把 extractor 逻辑安排在 `P1-S4 ~ P1-S7`；当前代码还没有 `data_extractor.py`、extractor 模块和测试
- **影响**: 返工、迁移逻辑提前出现、implementation slice 边界失真
- **建议改法和验证点**: `P1-S3` 只冻结 raw PDF / parsed report 缓存；`structured_data` 缓存后移到 `P1-S8`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中
- **裁决**: accepted
- **修复状态**: 已修复进计划

## 开放问题

- `BQ-2`：投资者收益率在样本年报上的披露覆盖率仍未知
  - 当前处理：按 `direct / estimated / missing` 三态建模，不阻塞 P1
- `BQ-4`：`akshare` 历史净值接口在 3 只样本上的稳定性仍待验证
  - 当前处理：放入 `nav_data.py` provider 验证，不阻塞 plan accepted

## 残余风险

- 年报格式异构仍可能导致后续章节规则补丁增多，但计划已把规则配置化和 stop condition 写清
- `110011` 的 `§3` root cause 已确认是规则问题，不代表所有基金的章节标题变体都已被覆盖

## 结论

结论：`pass`

理由：

- 计划已经把两个 material findings 修入 artifact
- 切片顺序满足“先统一文档仓库接口，再冻结 `§3`，再做提取，再做收口”的最短路径
- 当前没有新的 blocking questions，适合进入 `P1-S1 implementation + review`
