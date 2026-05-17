# P1-S1 Re-Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> Branch：`chore/reconcile-baseline`
> Gate：P1-S1 re-review
> Source judgment：`docs/reviews/p1-s1-code-review-controller-judgment-2026-05-17.md`
> Source fix artifact：`docs/reviews/p1-s1-fix-2026-05-17.md`

## 复核范围

仅复核 controller-accepted findings A1、A2，不扩展为新一轮 code review。

## A1：async 调用链中的同步 I/O 是否已被隔离

**最终状态：已修复**

### 证据

1. **`fund_agent/fund/pdf/downloader.py`**：
   - line 126：`report_id = await asyncio.to_thread(_find_annual_report_id, fund_code, year)` — akshare 同步查询已隔离到线程
   - line 70：`await asyncio.to_thread(dest_dir.mkdir, parents=True, exist_ok=True)` — 阻塞 `mkdir` 已隔离
   - line 79：`if await asyncio.to_thread(dest_path.exists)` — 阻塞 `exists()` 已隔离
   - line 93：`await asyncio.to_thread(dest_path.write_bytes, resp.content)` — 阻塞 `write_bytes` 已隔离
   - line 95：`file_stat = await asyncio.to_thread(dest_path.stat)` — 阻塞 `stat()` 已隔离

2. **`fund_agent/fund/documents/adapters/annual_report_pdf.py`**：
   - line 230：`raw_text = await asyncio.to_thread(self._text_extractor, pdf_path)` — pdfplumber 同步提取已隔离
   - line 231：`raw_tables = await asyncio.to_thread(self._table_extractor, pdf_path)` — 同理
   - line 232：`section_offsets = await asyncio.to_thread(self._section_locator, raw_text)` — 同理

3. **测试覆盖**：
   - `test_download_annual_report_uses_to_thread_for_lookup` — 验证 `_download_annual_report_pdf` 通过 `to_thread()` 调度 `_find_annual_report_id`，pass
   - `test_annual_report_pdf_adapter_runs_sync_helpers_via_to_thread` — 验证 adapter 通过 `to_thread()` 调度 `text_extractor`、`table_extractor`、`section_locator`，调用顺序正确，pass

4. **测试结果**：11 passed in 0.65s

### 结论

controller judgment 中列出的所有 4 处同步阻塞调用点（downloader line 33/126、adapter line 223/228 对应当前行号 126/230/231/232）均已用 `asyncio.to_thread()` 包装。额外的文件系统阻塞操作（`mkdir`、`exists`、`write_bytes`、`stat`）也被一并隔离。两条对应测试验证了 wrapper 生效。

---

## A2：目标年份缺失时是否不再静默回退到其它年份年报

**最终状态：已修复**

### 证据

1. **`fund_agent/fund/pdf/downloader.py`**：
   - line 42：`return None` — `_find_annual_report_id()` 在 `for` 循环未命中后直接返回 `None`，旧版的 `if len(annual) > 0: return str(annual.iloc[-1]["报告ID"])` fallback 已被移除
   - line 128-129：`if not report_id: raise FileNotFoundError(...)` — 上层 `_download_annual_report_pdf` 统一抛出 `FileNotFoundError`

2. **测试覆盖**：
   - `test_find_annual_report_id_returns_none_when_target_year_missing` — 用 DataFrame 构造含 2023/2022 年报但无 2024 年报的场景，验证返回 `None`，pass
   - `test_download_annual_report_raises_when_target_year_missing` — 验证上层抛出 `FileNotFoundError` 且消息匹配 `"未找到基金 110011 的 2024 年年报"`，pass

3. **测试结果**：11 passed in 0.65s

### 结论

silent fallback 已完全移除。未命中目标年份时 `_find_annual_report_id` 返回 `None`，上层统一抛出 `FileNotFoundError`，调用方可以明确感知"该年份年报不存在"。两条对应测试覆盖了函数层和上层集成层。

---

## 新 Blocker 检查

未发现新的 blocker。

## 结论

**pass**

- A1：已修复
- A2：已修复
- 新 blocker：无
- Artifact 路径：`docs/reviews/p1-s1-rereview-mimo-2026-05-17.md`
