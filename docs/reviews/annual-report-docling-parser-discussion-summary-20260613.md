# 年报解析与 Docling 方向讨论总结

日期：2026-06-13

定位：本文件是一次讨论总结，不是 controller judgment、accepted design、implementation plan 或 release/readiness 结论。后续若要进入实现，仍需单独经过 plan / review / controller judgment。

## 讨论背景

本轮讨论从基金年报解析链路开始，核心问题是：

- 当前项目实际用什么工具提取基金年报。
- 基金年报是否存在扫描页、图片页或 OCR 刚需。
- `pdfplumber + 自研 extractor` 与 Dayu 采用 Docling 的差异。
- 如果目标从字段抽取扩大到整份年报全面信息处理，Docling 是否更适合作为下一代文档层。

## 当前项目实际链路

当前生产边界仍是：

```text
FundDocumentRepository.load_annual_report(...)
  -> EID single-source PDF 获取与缓存
  -> pdfplumber 提取 raw_text / tables
  -> locate_sections 定位章节
  -> ParsedAnnualReport
  -> 自研 extractor 抽取基金分析字段
  -> EvidenceAnchor / CHAPTER_CONTRACT / 审计 / 报告生成
```

当前底层 PDF 解析工具是 `pdfplumber`：

- `extract_text()` 使用 `page.extract_text()` 提取全文。
- `extract_tables()` 使用 `page.extract_tables()` 提取基础表格。
- `AnnualReportPdfAdapter.parse_pdf()` 将全文、表格、章节定位组合为 `ParsedAnnualReport`。

`ParsedAnnualReport` 包含：

- `raw_text`：PDF 可抽取全文。
- `sections`：章节起止偏移。
- `tables`：基础表格 rows / headers。
- `metadata`：来源、缓存、EID single-source 信息。

自研 extractor 当前抽取的是面向基金分析模板的结构化事实子集，而不是整份年报的全面结构化表示。已覆盖或部分覆盖的事实包括：

- 基金身份、披露类别、基金类型、分类依据。
- 投资目标、投资范围、投资策略、风险收益特征。
- 业绩比较基准。
- 管理费、托管费等费率。
- 净值增长率、基准收益率、跟踪误差。
- 基金经理、策略回顾、换手率。
- 管理人/员工持有、持有人结构。
- 前十大持仓、行业分布、份额变动。
- 债券风险证据组。

这些字段尽量绑定 `EvidenceAnchor`，用于追溯章节、页码、表格和行号。

## 当前样本诊断

对本地 `基金年报/` 下 5 份 2024 年基金年报做了诊断。样本覆盖：

- QDII 指数基金。
- 指数增强基金。
- 主动混合基金。
- ETF 联接基金。
- 债券基金。

诊断结果：

| 文件类型 | 页数范围 | 可抽取字符 | 表格数 | 无文本页 | 低文本页 | 大图扫描页 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 份年报合计 | 70-110 页 | 每份约 6.1 万至 9.7 万字符 | 每份约 85 至 118 张表 | 0 | 0 | 0 |

补充观察：

- PDF 内确实存在少量 image objects。
- 最大单图约占页面 19%-24%，没有发现整页扫描图。
- 每页都有可抽取文本。
- 当前样本不支持“基金年报存在大量扫描页或图片承载关键信息”的判断。
- 当前样本支持“基金年报主体是 text-based PDF，`pdfplumber` 可提取大量文本和表格”的判断。

因此，当前主要瓶颈不是 OCR，而是：

- 章节标题和章节边界定位。
- 表格结构稳定性。
- 跨页表、多层表头、合并单元格。
- 同名字段的上下文 disambiguation。
- 字段到证据 anchor 的稳定映射。

一次 `locate_sections()` 诊断显示，5 份样本都能定位核心章节的一部分，但存在漏定位：

- 多数样本定位到 `§1/§2/§3/§4/§5/§8/§9/§10`。
- `§6/§7/§11/§12` 普遍未定位。
- QDII 样本额外漏掉 `§4/§10`。

这说明当前章节定位规则仍有缺口，但不等同于 PDF 无法抽取文本。

## `pdfplumber + 自研 extractor` 的适用边界

当前链路的强项：

- 对固定字段抽取可控。
- 对基金分析模板高度贴合。
- 字段事实可绑定 evidence anchor。
- 失败可以显式归类为 missing / ambiguous / unavailable / fail-closed。
- 与 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、质量审计机制对齐。

当前链路的弱项：

- `raw_text + tables` 不是完整文档语义对象。
- 章节层级和阅读顺序依赖规则。
- 表格结构只保留基础 rows / headers。
- 跨页表、多层表头、合并单元格处理能力有限。
- 不提供统一版面块、坐标、阅读顺序、图片、公式等文档级结构。
- 不适合直接支撑“整份年报全面信息处理”的 Agent 阅读需求。

结论：

```text
当前链路擅长从年报中抽取已定义字段，并让字段可审计。
当前链路不擅长把整份年报转成结构化、可遍历、可检索、适合 Agent 全面阅读的文档对象。
```

## Dayu 选择 Docling 的实际理由

对 Dayu 的判断基于公开仓库文档和依赖声明：

- `pyproject.toml` 中 `docling` / `docling-core` 是生产依赖，不是 optional 依赖。
- Dayu Fins README 显示下载完成态要求 PDF 和 `_docling.json` 同时落盘。
- CN/HK 的 `download --rebuild` 可只基于本地 PDF + Docling JSON 重建，不再访问原始披露来源或重新运行 Docling。

因此，Dayu 选择 Docling 的核心理由不是“年报一定需要 OCR”，而是：

```text
把证券财报文件预处理成可长期复用、可离线重建、适合 Agent 读取的统一文档中间层。
```

Dayu 面向的是更通用的证券文档 ingestion / process / rebuild / Agent read tools。它处理的不是单一基金年报固定字段抽取，而是 SEC、A 股、港股、上传材料、公告、PDF/HTML/附件、多语言和多版式文件。

Docling 对 Dayu 的价值主要在：

- 统一文档表示。
- 阅读顺序和版面块。
- 表格结构。
- Markdown / JSON / HTML 等可消费格式。
- provenance / bounding boxes。
- 预处理 artifact 可缓存、可跳过、可重建。

## Docling 对当前项目的价值判断

如果目标仍是当前 MVP 的固定字段抽取：

- 直接用 Docling 替换 `pdfplumber` 主链路，理由不足。
- 当前样本没有 OCR 刚需。
- 替换会引入依赖、耗时、版本漂移、产物映射和验收成本。
- Docling 本身不理解基金类型、preferred_lens、CHAPTER_CONTRACT 或投资分析规则。

如果目标扩大为“整份年报全面信息处理”：

- Docling 方向更合理。
- `pdfplumber + 自研 extractor` 的信息可处理性明显不足。
- Docling 更适合作为下一代年报文档表示层，而不是直接替代基金语义 extractor。

建议的架构方向：

```text
PDF
  -> FundDocumentRepository
  -> DoclingDocument / docling.json
  -> FundAnnualReportDocument 统一表示
  -> 自研 extractor / 章节事实投影 / EvidenceAnchor
  -> CHAPTER_CONTRACT / 审计 / 报告生成
```

职责划分：

- Docling 负责把整份年报转成更可处理的文档对象。
- 自研 extractor 负责基金语义事实抽取。
- EvidenceAnchor、字段置信度、失败分类、fail-closed 仍由本项目控制。
- 不把 Docling Markdown 直接当事实真源。
- 不把 AI 读 PDF 当审计依据。

## 建议采纳方式

不建议立即替换当前生产主链路。

建议先引入 parallel parse / benchmark：

```text
cache/docling/{fund_code}_{year}_annual_report_docling.json
```

初期目标不是生成报告，而是比较 Docling 是否能改善当前痛点：

1. 章节定位：当前漏掉的 `§6/§7/§11/§12`，Docling 是否能稳定提供更好的标题层级或阅读顺序。
2. 表格结构：当前容易错位的费用表、业绩表、持仓表、持有人结构、份额变动表，Docling 是否能更好保留行列关系。
3. 证据映射：Docling provenance / bbox 是否能稳定映射为当前 `EvidenceAnchor`。
4. 失败分类：Docling 输出缺失、低置信度、歧义或解析失败时，能否纳入当前 fail-closed 语义。
5. 性能与缓存：转换耗时、artifact 大小、可复用性是否可接受。

只有当这些验证成立，Docling 才应进入下一代文档层设计。

## 推荐结论

当前结论：

```text
短期：保留 pdfplumber + 自研 extractor 作为生产主链路。
中期：引入 Docling 做 parallel parse 和离线 benchmark。
长期：若 benchmark 证明章节、表格、provenance 显著优于当前 parser，则把 Docling 纳入 FundDocumentRepository 内部文档表示层。
```

不建议的做法：

- 不建议让 Service、UI、quality gate 或 Host 直接调用 Docling。
- 不建议用 Docling Markdown 直接替代当前字段事实。
- 不建议以 OCR 能力作为当前采纳 Docling 的主要理由。
- 不建议绕过 `FundDocumentRepository` 直接读取本地 PDF。

建议的下一步最小验证问题：

```text
在同一批 5 份 2024 年基金年报上，Docling 是否能比当前 pdfplumber parser 更稳定地输出章节层级、跨页表结构和可映射到 EvidenceAnchor 的 provenance？
```

如果答案是肯定的，后续可进入 Docling parallel parser 设计 gate；如果答案是否定的，Docling 暂时只保留为研究输入和异常 PDF fallback candidate。
