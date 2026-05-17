# Fund Capability

`fund_agent/fund` 是基金分析 Capability 层，负责承载基金领域知识、年报解析规则和模板取证输入，不负责 UI、Service、Runtime 或 Engine。

## 当前实现

当前已经落地的稳定公共契约只有文档仓库：

```python
from fund_agent.fund.documents import FundDocumentRepository

repository = FundDocumentRepository()
report = await repository.load_annual_report("110011", 2024)
```

`load_annual_report()` 返回 `ParsedAnnualReport`，包含：

- `key`：基金代码、年份和 `annual_report` 文档类型
- `raw_text`：年报全文文本
- `sections`：章节索引，供后续模板第 2 章 `R=A+B-C` 和第 4 章“投资者获得感”提取复用
- `tables`：年报表格的结构化结果

仓库层位于 `fund_agent/fund/documents/`：

- `models.py`：`DocumentKey`、`ParsedAnnualReport`、`ReportSection`、`ParsedTable`
- `repository.py`：对外唯一公开读取入口 `FundDocumentRepository`
- `adapters/annual_report_pdf.py`：把底层 PDF helper 适配为统一仓库返回值

当前边界要求：

- 业务调用方只通过 `FundDocumentRepository.load_annual_report(...)` 读取年报。
- `fund_agent/fund/pdf/*` 只作为仓库内部 helper / adapter，允许返回本地 `Path`，但这不是上层公共契约。
- `ParsedAnnualReport` 是后续模板第 2 章和第 4 章提取的统一输入；本 slice 不扩展到非年报文档类型。

## 内部分层

- `documents/`：公共契约与仓库实现。上层应通过这里读取基金文档。
- `pdf/`：底层 PDF helper。当前包含：
  - `downloader.py`：仅供仓库内部使用的 PDF 下载 helper，会写入本地缓存
  - `parser.py`：PDF 全文、表格与章节定位原型
- `analysis/`、`audit/`、`data/`、`template/`：后续分析、审计、数据和模板能力的扩展位置

## 当前边界

- 当前只支持 `annual_report`。
- `parser.py` 仍沿用现有章节定位原型；本 slice 不修复 `§3` 章节定位问题。
- 结构化 12 项提取、SQLite 缓存和审计规则尚未在该包内落地。
