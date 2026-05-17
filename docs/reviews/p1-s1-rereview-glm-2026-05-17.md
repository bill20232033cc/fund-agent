# P1-S1 Re-Review (GLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S1 文档访问契约收口
> 分支：`chore/reconcile-baseline`
> Gate：P1-S1 re-review
> Source judgment：`docs/reviews/p1-s1-code-review-controller-judgment-2026-05-17.md`
> Source fix：`docs/reviews/p1-s1-fix-2026-05-17.md`

---

## 1. Re-Review 结论

**PASS** — 两项 controller-accepted findings 均已修复。

---

## 2. 逐 Finding 复核

### 2.1 A1：async 调用链中仍直接执行同步 I/O

**最终状态：已修复**

**修复验证**：

`fund_agent/fund/pdf/downloader.py`：

| 位置（修复后行号） | 原始行为 | 修复后行为 | 判定 |
|---------------------|---------|-----------|------|
| `:126` | `_find_annual_report_id(fund_code, year)` 同步调用 | `await asyncio.to_thread(_find_annual_report_id, fund_code, year)` | ✅ |
| `:70` | `dest_dir.mkdir(...)` 同步调用 | `await asyncio.to_thread(dest_dir.mkdir, ...)` | ✅ |
| `:79` | `dest_path.exists()` 同步调用 | `await asyncio.to_thread(dest_path.exists)` | ✅ |
| `:93` | `dest_path.write_bytes(resp.content)` 同步调用 | `await asyncio.to_thread(dest_path.write_bytes, resp.content)` | ✅ |
| `:95` | `dest_path.stat()` 同步调用 | `await asyncio.to_thread(dest_path.stat)` | ✅ |

`fund_agent/fund/documents/adapters/annual_report_pdf.py`：

| 位置（修复后行号） | 原始行为 | 修复后行为 | 判定 |
|---------------------|---------|-----------|------|
| `:230` | `self._text_extractor(pdf_path)` 同步调用 | `await asyncio.to_thread(self._text_extractor, pdf_path)` | ✅ |
| `:231` | `self._table_extractor(pdf_path)` 同步调用 | `await asyncio.to_thread(self._table_extractor, pdf_path)` | ✅ |
| `:232` | `self._section_locator(raw_text)` 同步调用 | `await asyncio.to_thread(self._section_locator, raw_text)` | ✅ |

**测试覆盖**：

- `tests/fund/documents/test_repository.py:207-263`（`test_annual_report_pdf_adapter_runs_sync_helpers_via_to_thread`）：monkeypatch `asyncio.to_thread` 为同步代理，验证适配器按顺序通过 `to_thread` 调用 `text_extractor`、`table_extractor`、`section_locator`。✅
- `tests/fund/pdf/test_downloader.py:278-347`（`test_download_annual_report_uses_to_thread_for_lookup`）：monkeypatch `asyncio.to_thread` 为同步代理，验证下载 helper 通过 `to_thread` 调用 `_find_annual_report_id`。✅

**备注**：
- `parser.py` 未被修改，符合 fix 约束。
- `_download_pdf` 和 `_download_annual_report_pdf` 均已重命名为私有函数（加下划线前缀），与"内部 helper"定位一致。
- `dest_path.exists` 作为 bound method 传给 `asyncio.to_thread` 是正确的用法。

---

### 2.2 A2：找不到目标年份时静默回退到最新年报

**最终状态：已修复**

**修复验证**：

`fund_agent/fund/pdf/downloader.py` `_find_annual_report_id`（:21-42）：

- 原始代码（:40-42，初审时）：
  ```python
  # Fallback: return the latest annual report
  if len(annual) > 0:
      return str(annual.iloc[-1]["报告ID"])
  return None
  ```
- 修复后代码（:41-42）：
  ```python
  return None
  ```

silent fallback 已完全移除。未命中目标年份时直接返回 `None`，由上层 `_download_annual_report_pdf`（:128-129）统一抛出 `FileNotFoundError`。

**测试覆盖**：

- `tests/fund/pdf/test_downloader.py:245-275`（`test_find_annual_report_id_returns_none_when_target_year_missing`）：构造含 2023/2022 年报但不含 2024 年报的 DataFrame，验证 `_find_annual_report_id("110011", 2024)` 返回 `None`。✅
- `tests/fund/pdf/test_downloader.py:350-369`（`test_download_annual_report_raises_when_target_year_missing`）：mock `_find_annual_report_id` 返回 `None`，验证 `_download_annual_report_pdf` 抛出 `FileNotFoundError` 且消息包含基金代码和年份。✅

---

## 3. 附带变更复核

Fix 引入了超出 A1/A2 最小范围的附带变更，以下逐项确认不引入新风险：

| 附带变更 | 判定 | 理由 |
|---------|------|------|
| `_build_tables` 中 `page_number` 从 `raw_table.get("page_number", 0)` 改为 `_normalize_page_number()` 显式校验 | ✅ 无风险 | 缺失时抛 `ValueError` 比静默写 `0` 更安全，符合 controller R1 裁决 |
| 新增 `_resolve_table_index` 处理同页多表格序号 | ✅ 无风险 | 纯增量功能，新增测试覆盖 |
| `download_pdf` → `_download_pdf`、`download_annual_report` → `_download_annual_report_pdf` 重命名 | ✅ 无风险 | 与"内部 helper"定位一致，测试和 adapter import 已同步更新 |
| `__all__: list[str] = []`（downloader.py:18） | ✅ 无风险 | 显式声明无公开导出，强化内部 helper 语义 |

---

## 4. 残余风险确认

与 fix 前一致，无新增残余风险：

- `parser.py` 仍为同步原型，`§3` 定位修复归 P1-S2。
- SQLite 缓存、结构化提取、证据锚点不在本 slice 范围。
- 当前仅覆盖 `annual_report`，未扩展到其它文档类型。

---

## 5. 汇总

| Finding | 初审状态 | Re-Review 状态 | 证据 |
|---------|---------|---------------|------|
| A1 | 未修复 | **已修复** | 所有同步阻塞调用已通过 `asyncio.to_thread` 隔离；2 条新增测试覆盖 |
| A2 | 未修复 | **已修复** | silent fallback 已删除；2 条新增测试覆盖 |

**结论**：PASS
**A1 状态**：已修复
**A2 状态**：已修复
**Artifact path**：`docs/reviews/p1-s1-rereview-glm-2026-05-17.md`
**新 blocker**：无
