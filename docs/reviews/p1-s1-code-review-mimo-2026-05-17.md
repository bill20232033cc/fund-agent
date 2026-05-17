# P1-S1 Code Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> Branch：`chore/reconcile-baseline`
> Target：P1-S1 文档访问契约收口
> Scope：仅 review 当前 worktree 中属于 P1-S1 的文件及其 diff
> Mode：evidence-based，不实现修复

## 审查输入

- 已接受 plan：`docs/reviews/p1-plan-2026-05-17.md`
- plan review：`docs/reviews/p1-plan-review-2026-05-17.md`
- 基线对账：`docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md`
- 设计真源：`docs/design.md`
- 总控真源：`docs/implementation-control.md`
- 边界约束：`AGENTS.md`

## 审查范围

| 文件 | 类型 | 状态 |
|------|------|------|
| `fund_agent/fund/documents/__init__.py` | 新增 | 纯 re-export，无问题 |
| `fund_agent/fund/documents/models.py` | 新增 | 公共数据模型 |
| `fund_agent/fund/documents/repository.py` | 新增 | 仓库唯一公开入口 |
| `fund_agent/fund/documents/adapters/__init__.py` | 新增 | 纯 re-export，无问题 |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | 新增 | PDF 适配器 |
| `fund_agent/fund/pdf/downloader.py` | 修改 | docstring 更新 + `force_refresh` + 文档边界声明 |
| `tests/fund/documents/test_repository.py` | 新增 | 契约测试 |
| `tests/fund/pdf/test_downloader.py` | 新增 | 下载 helper 测试 |
| `fund_agent/fund/README.md` | 新增 | 文档同步例外 |
| `tests/README.md` | 新增 | 文档同步例外 |

**排除确认**：`fund_agent/fund/pdf/parser.py` 未被修改（已通过 `git diff HEAD` 验证），满足 P1-S1 禁止边界。

## Findings

### 1-未修复-高-同步阻塞 I/O 在 async 调用链中未隔离

- **文件(行号)**：
  - `fund_agent/fund/pdf/downloader.py:32` — `_find_annual_report_id` 在 async 协程 `download_annual_report` (line 125) 内同步调用 `ak.fund_announcement_report_em()`
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py:172-173` — `self._text_extractor(pdf_path)` 和 `self._table_extractor(pdf_path)` 在 async 方法 `load_annual_report` 内同步调用 pdfplumber
- **直接证据**：
  - `downloader.py:32`：`df = ak.fund_announcement_report_em(symbol=fund_code)` — akshare 同步 HTTP 查询，被 `download_annual_report` (line 125) 直接调用，无 `to_thread` 包装
  - `adapter.py:172`：`raw_text = self._text_extractor(pdf_path)` — `text_extractor` 默认值为 `extract_text`（parser.py），内部 `pdfplumber.open()` 是同步磁盘 I/O
  - `adapter.py:173`：`raw_tables = self._table_extractor(pdf_path)` — 同理
- **影响**：在 asyncio runtime（FastAPI、CLI 的 async main）中，单次年报加载会阻塞事件循环数百毫秒至数秒。并发场景下所有协程被串行化，延迟线性叠加。
- **建议改法**：
  - `download_annual_report` 内：`report_id = await asyncio.to_thread(_find_annual_report_id, fund_code, year)`
  - `load_annual_report` 内：`raw_text = await asyncio.to_thread(self._text_extractor, pdf_path)` 及同理包裹 table_extractor
  - 不需要修改 parser.py，适配器层可独立包装
- **验证点**：用 `pytest-asyncio` + 模拟 1 秒耗时的 mock extractor/downloader，确认协程并发时总耗时接近 1 秒而非 N 秒
- **严重程度**：高 — 静默性能退化，异步运行时从并发退化为串行

### 2-未修复-中-年报年份查找 fallback 静默返回错误年份

- **文件(行号)**：`fund_agent/fund/pdf/downloader.py:41-42`
- **直接证据**：
  ```python
  # downloader.py:35-42
  for _, row in annual.iterrows():
      title = str(row["公告标题"])
      if str(year) in title:
          return str(row["报告ID"])

  # Fallback: return the latest annual report
  if len(annual) > 0:
      return str(annual.iloc[-1]["报告ID"])
  ```
  当 `year=2020` 但公告列表无 2020 年报时，fallback 返回最新年报 ID（可能是 2024 年）。`DocumentKey.year=2020` 但 `raw_text` 实际是 2024 年内容，年份与内容静默错配。
- **影响**：后续分析（如跨期对比 §5、投资者收益率 §4）将错误年份数据当年份正确消费，无任何异常信号。
- **建议改法**：
  - 方案 A（推荐）：移除 fallback，未匹配时返回 `None`，由 `download_annual_report` 抛出 `FileNotFoundError`
  - 方案 B（最低成本）：在 fallback 路径加 `logger.warning("未找到 %d 年报，回退到最新年报", year)` 并让调用方感知
- **验证点**：新增测试用例 — 请求不存在年份 → 预期 `FileNotFoundError`（方案 A）或 warning 日志（方案 B）
- **严重程度**：中 — 数据正确性问题，P1-S1 样本基金均有对应年份年报，触发概率取决于调用方输入

### 3-未修复-中-章节置信度硬编码为 1.0 掩盖解析不可靠性

- **文件(行号)**：`fund_agent/fund/documents/adapters/annual_report_pdf.py:29`（定义），line 75（使用）
- **直接证据**：
  ```python
  _SECTION_CONFIDENCE = 1.0  # line 29
  # ...
  sections[section_id] = ReportSection(
      ...
      confidence=_SECTION_CONFIDENCE,  # line 75，所有章节无条件使用 1.0
  )
  ```
  已知 BQ-5：`110011` 的 `§3` 存在定位问题（parser 用纯正则匹配，漏判风险真实存在），但所有 `ReportSection` 均声明 `confidence=1.0`。
- **影响**：下游模板分析（如 P1-S5 投资者收益率提取）可能基于错误定位的章节做数据提取，且无信号表明数据不可靠。违反 AGENTS.md"证据必须可溯源"原则。
- **建议改法**：P1-S1 阶段将常量降为 `0.8` 并加注释说明 P1-S2 之前为临时值；P1-S2 修复 `§3` 后可回升。后续 adapter 应根据 parser 返回的匹配方式动态计算置信度。
- **验证点**：常量值 < 1.0 且注释说明后续 slice 会动态化
- **严重程度**：中 — 下游信任不准确信号，但 P1-S2 即为章节定位修复，影响窗口限于 S1→S2

### 4-未修复-低-`_build_tables` 缺页号时默认填入非法值 0

- **文件(行号)**：`fund_agent/fund/documents/adapters/annual_report_pdf.py:95`
- **直接证据**：`page_number = int(raw_table.get("page_number", 0))` — PDF 页码从 1 开始，0 是非法值
- **影响**：证据锚点中页码错误（`年报2024§3表1行0`），影响 traceability 但不导致崩溃
- **建议改法**：改为 `-1` 明确标记缺失，或直接用 `raw_table["page_number"]` 让 KeyError 传播
- **验证点**：缺页号时 `page_number == -1` 或抛出 `KeyError`
- **严重程度**：低 — 仅影响可选元数据缺失兜底值

### 5-未修复-低-`DocumentKey.document_kind` 类型从 `Literal` 弱化为 `str`

- **文件(行号)**：`fund_agent/fund/documents/models.py:23`
- **直接证据**：`document_kind: str = "annual_report"` vs plan 5.1 节指定 `document_kind: Literal["annual_report"]`
- **影响**：类型系统不阻止 `DocumentKey(..., document_kind="quarterly_report")`，P1-S1 仅支持年报，但后续 slice 误用时运行时才发现
- **建议改法**：改为 `Literal["annual_report"]`（需 `from typing import Literal`），或在 `__init__` / repository 入口校验
- **验证点**：类型检查器对非法 `document_kind` 报错
- **严重程度**：低 — 当前无实际触发路径，预防性修复

### 6-未修复-低-缓存目录使用相对路径依赖 CWD

- **文件(行号)**：`fund_agent/fund/pdf/downloader.py:16`
- **直接证据**：`DEFAULT_CACHE_DIR = Path("cache/pdf")` — 相对路径，CWD 变化时缓存分散到不同位置
- **影响**：同一 PDF 可能被下载到多个位置，缓存失效，但不导致错误结果
- **建议改法**：改为 `Path(__file__).resolve().parent.parent.parent / "cache" / "pdf"`（即 `fund_agent/cache/pdf`），或接受来自上层的显式 `dest_dir`
- **验证点**：从非项目根目录运行时缓存仍落入同一目录
- **严重程度**：低 — 仅影响缓存效率

### 7-未修复-中-测试未覆盖错误路径

- **文件(行号)**：
  - `tests/fund/documents/test_repository.py` — 仅 2 个 happy path 测试
  - `tests/fund/pdf/test_downloader.py` — 仅 3 个 happy path 测试
- **直接证据**：
  - `test_repository.py`：覆盖了 `load_annual_report` 正常返回 + 适配器 happy path，未覆盖 `ValueError`（空 fund_code / 非正 year）、`FileNotFoundError` 传播、`get_section_text` 未命中返回 `None`
  - `test_downloader.py`：覆盖了缓存命中 + 强制刷新 + 年报 URL 组装，未覆盖 `_find_annual_report_id` 返回 `None` 触发 `FileNotFoundError`、`httpx.HTTPError` 传播
- **影响**：错误路径无回归保护，P1-S2/S3 改动可能意外破坏错误处理
- **建议改法**：补充以下测试用例：
  1. `test_repository_raises_value_error_on_empty_fund_code`
  2. `test_repository_raises_value_error_on_non_positive_year`
  3. `test_repository_propagates_file_not_found_from_adapter`
  4. `test_get_section_text_returns_none_for_missing_section`
  5. `test_download_annual_report_raises_when_no_report_found`
- **验证点**：新增测试全部 pass
- **严重程度**：中 — 错误路径无测试覆盖，违反 AGENTS.md"单文件测试覆盖率 ≥80%"

### 8-未修复-低-`_find_annual_report_id` docstring 混合中英文

- **文件(行号)**：`fund_agent/fund/pdf/downloader.py:19-31`
- **直接证据**：docstring 主体为中文，但 Raises 行写 `Exception: 允许 akshare 查询异常直接传播`（中文）— 这部分是正确的。但 diff 显示旧版有英文注释 `Uses akshare (synchronous) to search eastmoney fund announcements`，已被移除。当前版本 docstring 全部中文，此项已修复。
- **影响**：无 — 已在本次 diff 中修复
- **严重程度**：N/A — 撤回此 finding

## P1-S1 计划符合性检查

| 完成信号 | 状态 | 证据 |
|---|---|---|
| 仓库入口唯一：`load_annual_report(...) -> ParsedAnnualReport` | ✓ | `FundDocumentRepository.load_annual_report` 是唯一公开入口，返回 `ParsedAnnualReport` |
| 公共契约在 `fund_agent/fund/documents/*` 非 `pdf/*` | ✓ | `models.py`、`repository.py`、`adapters/` 均在 `documents/` 下 |
| 调用方不再直接拿 `Path` | ✓ | 测试断言 `assert not isinstance(report, Path)` 和 `assert not hasattr(report, "path")` |
| `parser.py` 未被修改 | ✓ | `git diff HEAD -- parser.py` 无输出 |
| 未触碰 extractor / data_extractor.py / 上层目录 | ✓ | 无相关文件变更 |
| 仓库外无新增 PDF 文件系统写操作 | ✓ | `download_pdf` 的 `write_bytes` 仅在 `pdf/downloader.py` 内部 |

**偏差说明**：plan 5.1 节建议 `FundDocumentRepository` 为 `Protocol`，实现为具体类 + 独立 `AnnualReportLoader` Protocol。该偏差属于改进（Protocol 无法实例化，分离 Protocol + concrete class 是更合理的设计），不视为缺陷。

## AGENTS.md 边界检查

| 约束 | 状态 | 备注 |
|---|---|---|
| 基金文档只通过统一仓库接口访问 | ✓ | `FundDocumentRepository.load_annual_report` 是唯一入口 |
| 中文 docstring | ✓ | 所有 public 函数均有完整中文 docstring（Args/Returns/Raises） |
| 禁止魔法数字/字符串 | ⚠️ | `_SECTION_MATCH_RULE` 和 `_SECTION_CONFIDENCE` 为模块级常量但值硬编码（Finding 3） |
| 测试覆盖率 ≥80% | ⚠️ | 错误路径未覆盖（Finding 7） |
| 以代码为准 | ✓ | README 同步的是当前已实现接口，未设计未来 |

## Residual Risk

1. **parser.py 阻塞 I/O**：P1-S1 禁止修改 parser.py，适配器层可通过 `asyncio.to_thread` 包装但当前未实施（Finding 1）。风险由 P1-S3 缓存层部分缓解。
2. **年份 fallback**：当前样本基金均有对应年份年报，不触发 fallback。但若上层传入不存在的年份，会静默返回错误数据（Finding 2）。
3. **`pdf/__init__.py` 为空**：未明确标记 `downloader.py` / `parser.py` 为内部模块（如 `__all__ = []`）。当前依赖约定（README + docstring）约束调用方，缺乏代码级强制。不阻塞 P1-S1 但建议 P1-S3 补充。

## 结论

**结论：pass（附 2 个中高 finding 待裁决）**

P1-S1 的核心目标（统一文档仓库接口 + 公共契约收口到 `documents/` 命名空间 + 文件系统边界收口）已达成。实现质量整体良好：模型设计合理（frozen dataclass）、Protocol 分离清晰、测试覆盖了核心契约。

需裁决的 findings：
- **Finding 1（高）**：同步阻塞 I/O — 建议 P1-S1 内修复（改动小：3 处 `asyncio.to_thread` 包装）
- **Finding 2（中）**：年份 fallback — 建议 P1-S1 内修复（改动小：移除 fallback 或加 warning）
- **Finding 3-7**：均为低/中，可 deferred 到 P1-S2 或 P1-S3

无 blocking accepted candidate 阻塞 P1-S1 gate，但 Finding 1 和 Finding 2 建议在进入 P1-S2 前修复。
