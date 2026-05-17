# P1-S1 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S1 implementation`
> slice：`P1-S1 文档访问契约收口`
> 分支：`chore/reconcile-baseline`

## Approved Plan

- 计划来源：`docs/reviews/p1-plan-2026-05-17.md` 第 `8.2` 节 `P1-S1 文档访问契约收口`
- review 裁决：`docs/reviews/p1-plan-review-2026-05-17.md` 结论 `pass`
- baseline 对账：`docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md` 结论 `pass`

## Scope / Non-Goals

### Scope

- 在 `fund_agent/fund/documents/*` 定义并收口年报文档公共契约。
- 对外只保留 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`。
- 把 `fund_agent/fund/pdf/*` 降为仓库内部 helper / adapter。
- 补齐与该契约直接相关的测试和包级文档同步。

### Non-Goals

- 不修改 `fund_agent/fund/pdf/parser.py`。
- 不进入 extractor、`fund_agent/fund/data_extractor.py`、Service / UI / Engine。
- 不扩展非年报文档类型。
- 不进入 `P1-S2` 的 `§3` 章节定位修复。

## Changed Files

- `fund_agent/fund/documents/__init__.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/pdf/downloader.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/pdf/test_downloader.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Implemented Items

1. 在 `fund_agent/fund/documents/models.py` 固化 `DocumentKey`、`ReportSection`、`ParsedTable`、`ParsedAnnualReport`，并新增 `ANNUAL_REPORT_DOCUMENT_KIND` 常量，避免文档类型魔法字符串散落。
2. 在 `fund_agent/fund/documents/repository.py` 收口唯一公开入口 `FundDocumentRepository.load_annual_report(...)`，补充基金代码和年份校验，不向上层暴露本地 `Path`。
3. 在 `fund_agent/fund/documents/adapters/annual_report_pdf.py` 把现有 PDF 下载/解析 helper 适配成 `ParsedAnnualReport`，补充章节标题提取与按页 `table_index` 归一化。
4. 在 `fund_agent/fund/pdf/downloader.py` 把下载函数显式降为内部 helper：改为 `_download_pdf()`、`_download_annual_report_pdf()`，并用 `__all__ = []` 避免作为包级公开契约扩散。
5. 在 `tests/fund/documents/test_repository.py` 增补仓库入口测试，覆盖：
   - 返回 `ParsedAnnualReport` 且不暴露 `Path`
   - 基金代码标准化
   - 非法输入拒绝
   - 适配器表格序号归一化
6. 在 `tests/fund/pdf/test_downloader.py` 调整为覆盖内部 helper 语义，验证缓存命中、强制刷新下载、年报 URL 与文件名拼装。

## Validation

### Required Command

```bash
.venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py
```

结果：

```text
7 passed in 0.38s
```

### Environment Notes

- 在 follow-up 之前，我曾尝试：
  - `pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py`
  - `python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py`
- 上述两次都失败，原因分别是：
  - shell 中不存在 `pytest` 可执行文件
  - 当前默认 Python 环境未安装 `pytest`
- 按 controller 指定改用仓库 `.venv` 后，所需验证命令已由我本地跑通，因此本 artifact 不依赖额外的 controller 交叉验证兜底。

## Docs Decision

- 更新 `fund_agent/fund/README.md`，明确当前 Fund capability 的稳定入口只有 `FundDocumentRepository.load_annual_report(...)`，`pdf/*` 仅为仓库内部 helper / adapter。
- 更新 `tests/README.md`，明确文档仓库测试围绕公共契约断言，`pdf/*` 测试只覆盖内部 helper，不应被业务代码当成稳定入口。

## Residual Risks

### Fixed Later Slice

- `fund_agent/fund/pdf/parser.py` 仍是当前原型实现，`§3` 漏识别问题未在本 slice 处理，需在 `P1-S2 章节定位修复与 §3 冻结` 继续收口。

### Later Phase

- 当前文档仓库只支持 `annual_report`，未扩展招募说明书、季报等其他文档类型。
- SQLite 文档缓存、结构化提取、证据锚点与审计规则尚未进入本 slice。

### User Decision

- 无。

## Completion Status

- `P1-S1` completion signal：`reached`
- 判断依据：
  - 对外存在且仅存在一个仓库入口：`FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`
  - 公共契约定义位于 `fund_agent/fund/documents/*`
  - `fund_agent/fund/pdf/*` 已降为仓库内部 helper / adapter
  - slice 相关测试已通过，且仓库契约测试已断言业务调用方不再需要直接拿 `Path`
