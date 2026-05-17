# P1-S1 Code Review (GLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S1 文档访问契约收口
> 分支：`chore/reconcile-baseline`
> Review scope 裁决：`docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md`
> 已接受 plan：`docs/reviews/p1-plan-2026-05-17.md`
> 设计/总控真源：`docs/design.md`、`docs/implementation-control.md`

---

## 1. Review 结论

**PASS** — P1-S1 核心目标达成，无 blocking finding。

唯一仓库入口 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport` 已正确建立，公共契约位于 `fund_agent/fund/documents/*`，`pdf/*` 降级为内部 helper。边界无越界，`parser.py` 未被修改。

存在 5 项 non-blocking findings（2 medium / 2 low / 1 informational），建议 controller 裁决是否纳入后续 slice 修复。

---

## 2. 审查范围

| 文件 | 状态 |
|------|------|
| `fund_agent/fund/documents/__init__.py` | 新增 |
| `fund_agent/fund/documents/models.py` | 新增 |
| `fund_agent/fund/documents/repository.py` | 新增 |
| `fund_agent/fund/documents/adapters/__init__.py` | 新增 |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | 新增 |
| `fund_agent/fund/pdf/downloader.py` | 修改 |
| `tests/fund/documents/test_repository.py` | 新增 |
| `tests/fund/pdf/test_downloader.py` | 新增 |
| `fund_agent/fund/README.md` | 新增（文档同步例外） |
| `tests/README.md` | 新增（文档同步例外） |

---

## 3. Findings

### 3.1 F1-未修复-Medium-同步阻塞调用未隔离于异步上下文

**文件与行号**：
- `fund_agent/fund/pdf/downloader.py:32`（`ak.fund_announcement_report_em` 同步调用）
- `fund_agent/fund/pdf/downloader.py:125`（`_find_annual_report_id` 在 `async download_annual_report` 内被调用）
- `fund_agent/fund/documents/adapters/annual_report_pdf.py:172-174`（`text_extractor`、`table_extractor`、`section_locator` 均为同步函数，在 `async load_annual_report` 内直接调用）

**直接证据**：

`downloader.py:32`:
```python
df = ak.fund_announcement_report_em(symbol=fund_code)  # 同步 I/O
```

`annual_report_pdf.py:172-174`:
```python
raw_text = self._text_extractor(pdf_path)      # 同步 pdfplumber
raw_tables = self._table_extractor(pdf_path)     # 同步 pdfplumber
section_offsets = self._section_locator(raw_text) # 同步正则
```

以上调用均在 `async` 函数内直接执行，未使用 `asyncio.to_thread` 或 `run_in_executor`，会阻塞事件循环。

**影响**：
- 当前 P1-S1 场景下（单次调用、无并发），不会触发实际阻塞问题。
- 当 P2/P3 引入并发分析或多基金批量处理时，单次 `pdfplumber` 解析可耗时数百毫秒甚至数秒，会阻塞整个事件循环。
- akshare 同步 HTTP 请求在并发场景下同样会阻塞。

**建议改法**：
- P1-S1 不强制修复（不阻塞），但建议 P1-S3 缓存层落地时同步处理。
- 可选方案：`download_annual_report` 中把 `_find_annual_report_id` 包裹在 `await asyncio.to_thread(...)`；adapter 中同理包裹三个同步 parser 调用。

**验证点**：
- 在并发调用场景（如 `asyncio.gather` 同时加载 3 只基金年报）下，确认不出现串行阻塞。

---

### 3.2 F2-未修复-Medium-年报下载 fallback 静默返回错误年份

**文件与行号**：`fund_agent/fund/pdf/downloader.py:40-42`

**直接证据**：
```python
    # Fallback: return the latest annual report
    if len(annual) > 0:
        return str(annual.iloc[-1]["报告ID"])

    return None
```

当 `_find_annual_report_id("110011", 2023)` 找不到 2023 年报时（例如标题中不含 "2023"），但 DataFrame 中有 2024 年报，函数会静默返回 2024 年报的 ID。调用方 `download_annual_report` 随后下载该 ID 对应的 PDF，文件名却命名为 `{fund_code}_2023_annual_report.pdf`。

**影响**：
- 用户请求 2023 年报，实际下载 2024 年报，缓存文件名与内容不匹配。
- 后续缓存命中时返回错误年份的数据，且错误会沿 `ParsedAnnualReport.key.year` 传播到上层分析。
- 这属于**数据正确性**问题，但因当前仅在"标题不含目标年份"的边缘场景触发，且 P1-S1 的 downloader 仍是内部 helper，暂不判定为 blocking。

**建议改法**：
- 删除 fallback 逻辑，找不到时直接返回 `None`（让 `download_annual_report` 抛出 `FileNotFoundError`）。
- 或改为显式 warn + 返回 `None`，由调用方决定是否接受 fallback。

**验证点**：
- 测试用例：`_find_annual_report_id("110011", 2099)` 应返回 `None`，而非最新年报 ID。
- 测试用例：`download_annual_report("110011", 2099)` 应抛出 `FileNotFoundError`。

---

### 3.3 F3-未修复-Low-_build_tables 默认 page_number=0 语义模糊

**文件与行号**：`fund_agent/fund/documents/adapters/annual_report_pdf.py:95`

**直接证据**：
```python
page_number = int(raw_table.get("page_number", 0))
```

当 parser 返回的表格 dict 缺少 `page_number` 字段时，静默默认为 `0`。`0` 既可表示"页码未知"也可表示"第 0 页"，消费者无法区分。

**影响**：
- 证据锚点格式为 `年报{年份}§{章节}表{编号}行{行号}`，若 `page_number` 语义不清，P2 证据溯源可能输出不准确的页码。

**建议改法**：
- 使用 `-1` 或 `None` 表示未知页码，与 `page_number` 字段类型协调。或在 `ParsedTable` 上增加注释说明 `page_number=0` 的语义。

**验证点**：
- 确认 parser 实际返回的表格 dict 是否总是包含 `page_number`。

---

### 3.4 F4-未修复-Low-年度校验无上界

**文件与行号**：`fund_agent/fund/documents/repository.py:76-77`

**直接证据**：
```python
if year <= 0:
    raise ValueError("year 必须为正整数")
return year
```

`year=9999` 可通过校验。虽不构成运行时风险，但早期拒绝明显非法输入可避免下游无效网络请求。

**影响**：极低。下游 akshare 查询会自然失败（找不到 9999 年报）。

**建议改法**：
- 增加上界检查，如 `year > datetime.now().year + 1`，返回 `ValueError`。

**验证点**：
- 测试用例：`_validate_year(9999)` 应抛出 `ValueError`。

---

### 3.5 F5-未修复-Informational-测试未覆盖负向路径

**文件与行号**：`tests/fund/documents/test_repository.py`、`tests/fund/pdf/test_downloader.py`

**直接证据**：

当前测试全部为 happy path：
- `test_repository_returns_parsed_annual_report_without_path_exposure`：正常加载
- `test_annual_report_pdf_adapter_happy_path_builds_sections_and_tables`：正常适配
- `test_download_pdf_returns_cached_file_without_network`：缓存命中
- `test_download_pdf_downloads_file_when_force_refresh_enabled`：强制刷新
- `test_download_annual_report_delegates_to_download_pdf`：委托下载

未覆盖的负向路径：
- `_validate_fund_code("")` 应抛出 `ValueError`
- `_validate_fund_code("  ")` 应抛出 `ValueError`
- `_validate_year(-1)` / `_validate_year(0)` 应抛出 `ValueError`
- `_find_annual_report_id` 返回 `None` 时 `download_annual_report` 应抛出 `FileNotFoundError`
- `get_section_text("§99")` 应回回 `None`
- `_build_tables` 输入空列表
- `_extract_section_title` 对空字符串或越界 offset 的行为

**影响**：
- P1-S1 的 happy path 契约已充分验证。负向测试缺失不影响当前 slice 正确性，但会降低后续 slice 的回归保护力。

**建议改法**：
- 在 P1-S2 或 P1-S3 阶段补充负向测试，特别是验证逻辑和错误传播路径。

**验证点**：
- `pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py` 全部通过后，新增负向用例也应通过。

---

## 4. 边界合规性逐项核查

### 4.1 唯一仓库入口

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `FundDocumentRepository.load_annual_report()` 是唯一公开入口 | ✅ | `documents/__init__.py` 导出 `FundDocumentRepository`；`repository.py:103` 定义公开方法 |
| 返回 `ParsedAnnualReport`，不暴露 `Path` | ✅ | 测试 `test_repository.py:47-48` 显式断言 `not isinstance(report, Path)` 且 `not hasattr(report, "path")` |
| 上层不直接操作文件系统 | ✅ | `documents/` 内无 `mkdir`、`write_bytes`、`open` 调用；文件写入仅在 `pdf/downloader.py` |

### 4.2 公共契约位置

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 公共模型在 `documents/models.py` | ✅ | `DocumentKey`、`ParsedAnnualReport`、`ReportSection`、`ParsedTable` 均定义于此 |
| 仓库实现在 `documents/repository.py` | ✅ | `FundDocumentRepository` 定义于此 |
| `pdf/*` 不承载公共契约 | ✅ | `pdf/downloader.py` 仅暴露 `download_pdf` 和 `download_annual_report`（均为内部 helper） |

### 4.3 禁止越界核查

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `parser.py` 未被修改 | ✅ | `git diff 9956c45..HEAD -- fund_agent/fund/pdf/parser.py` 无输出 |
| 无 extractor / `data_extractor.py` 引用 | ✅ | `grep -rn` 确认无相关 import 或调用 |
| 无上层目录依赖 | ✅ | 所有 import 仅在 `fund_agent.fund.documents` 和 `fund_agent.fund.pdf` 内部 |
| 依赖方向 `documents → pdf` 单向 | ✅ | `grep -rn` 确认 `pdf/` 无反向 import `documents` |

### 4.4 AGENTS.md 约定合规

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 所有公共函数有中文 docstring | ✅ | 逐文件检查 `models.py`、`repository.py`、`annual_report_pdf.py`、`downloader.py` |
| Docstring 包含 Args/Returns/Raises | ✅ | 所有公共方法均包含三段式 docstring |
| 无嵌套函数（生产代码） | ✅ | 所有辅助函数为模块级私有函数（`_validate_*`、`_build_*`、`_extract_*`） |
| 无魔法数字/字符串 | ✅ | `_SECTION_MATCH_RULE` 和 `_SECTION_CONFIDENCE` 为命名常量 |
| `downloader.py` docstring 标注为内部 helper | ✅ | `:1-3` "当前模块只负责定位公告并下载 PDF 到本地缓存，不再作为上层公共文档读取契约" |

---

## 5. 残余风险

| ID | 风险 | 影响范围 | 建议处理时机 |
|----|------|---------|-------------|
| RR-S1-1 | 同步阻塞在异步上下文中未隔离 | P1-S3+ 并发场景 | P1-S3 缓存层落地时同步修复 |
| RR-S1-2 | 年报下载 fallback 可能返回错误年份 | 数据正确性 | P1-S1 后尽快修复，最迟 P1-S3 |
| RR-S1-3 | 负向测试覆盖不足 | 回归保护力 | P1-S2 或 P1-S3 补充 |

---

## 6. 汇总

| Finding 编号 | 严重程度 | Blocking? | 建议处理 |
|-------------|---------|-----------|---------|
| F1 | Medium | 否 | P1-S3 修复 |
| F2 | Medium | 否 | P1-S1 后尽快修复 |
| F3 | Low | 否 | P1-S3 酌情修复 |
| F4 | Low | 否 | 可选修复 |
| F5 | Informational | 否 | P1-S2/S3 补充 |

**总 findings 数量**：5（0 blocking / 2 medium / 2 low / 1 informational）
**Blocking accepted candidate**：无
**Artifact path**：`docs/reviews/p1-s1-code-review-glm-2026-05-17.md`
