# P1-S3 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S3 implementation`
> slice：`P1-S3 两级缓存与仓库内解析物化`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 落地 `documents` 层内部的 raw PDF 元信息缓存与 parsed report 物化缓存。
- 在不改变 `FundDocumentRepository.load_annual_report(...)` 公开签名的前提下，让仓库优先命中缓存。
- 为 `force_refresh=True` 提供可测试的缓存穿透行为。

### Non-Goals

- 不修改 `parser.py` 章节语义。
- 不暴露 SQLite 给上层查询。
- 不提前落 `structured_data`。
- 不进入 extractor、`nav_data.py`、P1-S4 或上层目录。

## Changed Files

- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `tests/fund/documents/test_cache.py`
- `tests/fund/documents/test_repository.py`

## Implemented Items

1. 新增 `fund_agent/fund/documents/cache.py`
   - 提供 `AnnualReportDocumentCache`，只服务 `documents` 层内部。
   - 冻结最小缓存结构：
     - `documents` 表：记录 `document_key`、基金代码、年份、文档类型、原始 PDF 路径、更新时间
     - `parsed_reports` 表：记录 `document_key`、payload 路径、schema version、更新时间
   - parsed report 物化为 `cache/documents/parsed_reports/*.json`，SQLite 仅保存索引元信息。
2. 扩展 `fund_agent/fund/documents/models.py`
   - 为 `DocumentKey`、`ReportSection`、`ParsedTable`、`ParsedAnnualReport` 增加 `to_dict()` / `from_dict()`，支撑 parsed report 的 JSON 物化与反序列化。
3. 改造 `fund_agent/fund/documents/adapters/annual_report_pdf.py`
   - 拆分出 `fetch_pdf_path()` 和 `parse_pdf()`，保留原有 `load_annual_report()` 公开行为。
   - 让 repository 可以独立编排“先确保 PDF 存在，再决定是否解析”。
4. 改造 `fund_agent/fund/documents/repository.py`
   - 保持 `load_annual_report(fund_code, year, *, force_refresh=False)` 公开签名不变。
   - 对支持缓存编排的 loader：
     - `force_refresh=False` 时先读 parsed report 缓存
     - parsed report 未命中时再读 documents 中记录的 PDF 路径
     - 两者都未命中时再调用 loader 下载 PDF
     - 解析完成后回写 parsed report 与 PDF 元信息
   - `force_refresh=True` 时绕过 parsed report 与已记录 PDF 路径，强制重新下载并重新解析
   - 对不支持缓存编排的自定义 loader，继续走原有直接委派路径，避免破坏旧测试和现有契约。
5. 新增 `tests/fund/documents/test_cache.py`
   - 验证 documents / parsed_reports 两张表创建与最小 schema 落地
   - 验证 PDF 元信息与 parsed report 物化可读回
   - 验证 payload 缺失时安全回退为缓存未命中
6. 扩展 `tests/fund/documents/test_repository.py`
   - 验证重复加载同一年报时不会重复下载或重复解析
   - 验证 `force_refresh=True` 会穿透 raw PDF / parsed report 缓存
   - 验证 parsed report 缓存缺失时会复用已记录的 PDF 路径

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py -q
.venv/bin/python -m pytest tests/fund/documents/test_repository.py -q
.venv/bin/python -m pytest tests/fund/documents -q
```

结果：

```text
tests/fund/documents/test_cache.py -> 2 passed in 1.06s
tests/fund/documents/test_repository.py -> 8 passed in 0.39s
tests/fund/documents -q -> 10 passed in 0.40s
```

## Cache Behavior Closure

- raw PDF 缓存：
  - 继续由底层 downloader 的文件缓存负责实际 PDF 文件复用
  - `documents` 表只在仓库层内部记录该 PDF 路径，避免重复查询/下载
- parsed report 缓存：
  - 解析结果落为 JSON 文件，并由 `parsed_reports` 表建立索引
  - 同一年报重复加载时优先命中该缓存，不再重复全文提取、表格提取、章节定位
- `force_refresh=True`：
  - 会绕过 parsed report 缓存
  - 会绕过 `documents` 中已记录的 PDF 路径
  - 会重新调用 loader 下载 PDF 并重新解析，然后覆盖缓存
- `structured_data`：
  - 本 slice 未创建任何 `structured_data` 表，也未固化其 schema

## Residual Risks

### Fixed Later Slice

- 当前 parsed report 物化采用 JSON 文件 + SQLite 索引的最小实现，尚未引入更细粒度的失效策略或校验和。

### Later Phase

- `nav_cache` 与 `structured_data` 仍未落地，符合当前 slice 边界。
- 当前缓存根目录策略仍使用默认相对路径，后续若要做统一根路径策略，应在后续缓存相关 slice 一并裁决。

### User Decision

- 无。

## Completion Status

- `P1-S3` completion signal：`reached`
- 判断依据：
  - raw PDF 元信息缓存与 parsed report 物化缓存均已位于 `documents` 层内部
  - repository 返回解析结果时优先命中缓存，不再重复下载 / 重复全文解析
  - `force_refresh=True` 行为已落地且有测试覆盖
  - `structured_data` 未在本 slice 冻结或落地
