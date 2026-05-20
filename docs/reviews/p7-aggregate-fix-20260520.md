# P7 Aggregate Fix — Cache Source Metadata Resilience

## Scope

- Gate: P7 aggregate review judgment / fix
- Accepted finding: `docs/reviews/p7-aggregate-deepreview-mimo-20260520.md` Finding 1
- Fix time: 2026-05-20T23:42:01+0800
- Files changed:
  - `fund_agent/fund/documents/cache.py`
  - `tests/fund/documents/test_cache.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Controller Judgment

MiMo 的 medium finding 被接受并修复：`documents.source_metadata_json` 是缓存持久化字段，读取路径应具备恢复力。坏 JSON、非对象 JSON 或未知 `source` 不应阻断已存在且文件可用的 PDF cache entry。

该修复只放在 cache 读取容错层，不放宽模型层来源闭集校验。`AnnualReportSourceMetadata.from_dict(...)` 在 cache 之外仍按原契约对未知来源 fail closed。

MiMo 的两个 low finding 保留为 residual risk：

- fallback 成功时不保留失败来源链路：当前 P7 只要求最终来源和 `fallback_used`，不阻塞。
- legacy parsed cache 不自动刷新来源元数据：默认缓存语义下可接受，`force_refresh=True` 可刷新。

## Implementation

- `_source_metadata_from_json(...)` 现在对以下污染输入降级为 `None`：
  - JSON 解析失败
  - JSON 解析结果不是对象
  - 对象字段无法构造合法 `AnnualReportSourceMetadata`，包括未知 `source`
- `get_pdf_entry(...)` / `get_pdf_path(...)` 在 PDF 文件仍存在时继续返回 cache hit，仅 `source_metadata=None`。
- 新增参数化 cache 回归测试，覆盖 malformed JSON、非对象 JSON、未知来源名三种污染场景。
- README 同步记录当前 documents cache 容错行为和测试覆盖口径。

## Verification

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py -q
# 11 passed

.venv/bin/python -m pytest tests/ -q
# 293 passed

.venv/bin/python -m ruff check fund_agent/fund/documents/cache.py tests/fund/documents/test_cache.py
# All checks passed

git diff --check
# passed
```

## Result

P7 aggregate accepted finding 1 已关闭。当前需要进入 P7 aggregate targeted re-review，重点确认：

- cache 读取容错没有改变正常 metadata 写入与模型校验契约；
- 损坏 `source_metadata_json` 不再阻断 PDF 路径缓存读取；
- README 与测试手册描述与代码事实一致。
