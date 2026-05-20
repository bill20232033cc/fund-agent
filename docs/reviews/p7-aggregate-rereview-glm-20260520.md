# P7 Aggregate Targeted Re-Review — Cache Source Metadata Resilience Fix

## Scope

- Gate: P7 aggregate targeted re-review
- Fix under review: `docs/reviews/p7-aggregate-fix-20260520.md` — Finding 1 cache resilience fix
- Prior reviews: `docs/reviews/p7-aggregate-deepreview-mimo-20260520.md`, `docs/reviews/p7-aggregate-deepreview-glm-20260520.md`
- Files reviewed:
  - `fund_agent/fund/documents/cache.py` — `_source_metadata_from_json` degradation logic
  - `tests/fund/documents/test_cache.py` — parametrized degradation test
  - `fund_agent/fund/README.md` — cache behavior doc update
  - `tests/README.md` — test coverage doc update
  - `fund_agent/fund/documents/models.py` — `_normalize_source_name` fail-closed preservation
- Excluded: all other P7 files, Service/UI/Engine/CLI

## Findings

无新增问题。

## Verification Items

### 1. Malformed JSON, Non-Dict JSON, Invalid Source → None

`_source_metadata_from_json` (`cache.py:119-136`) now handles three degradation paths:

| Input | Path | Result |
|---|---|---|
| `"{not-json"` | `json.loads` raises `ValueError` caught at line 129 | `None` |
| `["not", "object"]` | `isinstance(parsed, dict)` false at line 131 | `None` |
| `{"source": "cninfo"}` | `from_dict` → `_normalize_source_name` raises `ValueError` caught at line 135 | `None` |

Parametrized test `test_cache_degrades_invalid_source_metadata_json_to_none` (`test_cache.py:251-313`) covers all three inputs and asserts both `get_pdf_entry` returns a non-None entry with correct `pdf_path` and `source_metadata is None`, and `get_pdf_path` returns the correct path. **Pass.**

### 2. PDF Path Not Blocked

The test explicitly inserts a documents row with the corrupt `source_metadata_json`, then calls `get_pdf_entry` and `get_pdf_path`. Both return the correct PDF path — the corruption in the metadata column does not block cache reads. **Pass.**

### 3. `AnnualReportSourceMetadata.from_dict` Remains Fail-Closed

`_normalize_source_name` (`models.py:309-310`) still raises `ValueError` for source names outside `("eid", "eastmoney")`. The fix adds tolerance only in `_source_metadata_from_json` (the cache read helper). All other callers of `from_dict` — including the write path in `record_pdf_path` / `save_parsed_report` — still get fail-closed validation. **Pass.**

### 4. No Service/UI/Engine/CLI Source Leakage

Grep for `AnnualReportSourceMetadata`, `EidAnnualReportSource`, `AnnualReportSourceOrchestrator`, `documents.sources`, `documents.cache`, `documents.repository` across `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/engine/`, `fund_agent/cli.py`, `tests/services/`, `tests/ui/` — zero matches. **Pass.**

### 5. Minor Test Cleanup

`test_legacy_parsed_report_without_metadata_loads_with_empty_metadata` (`test_cache.py:370`) no longer writes an empty string before the real payload. The old double-write pattern was harmless but confusing; now uses a single `write_text`. No behavioral change. **Pass.**

### 6. Documentation Accuracy

- `fund_agent/fund/README.md:57`: Accurately describes cache degradation: "缓存读取时，如果历史或人工污染的 `source_metadata_json` 无法解析为合法来源元数据，documents 层会保留可用 PDF 路径并将 `metadata.source` 降级为 `None`；正常写入和模型反序列化仍保持来源闭集校验。"
- `fund_agent/fund/README.md:293`: Accurately describes cache behavior: "损坏的来源元数据只降级为空元数据，不阻断 PDF 路径缓存读取"
- `tests/README.md:9`: Coverage doc updated for degradation tests
- `tests/README.md:122`: Test conventions updated for corruption coverage

**Pass.**

## Verification Commands

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

## Residual Risk

| Risk | Severity | Status |
|---|---|---|
| `source_metadata_json` 人工损坏 | 低 | 已修复 — 降级为 None，不阻断缓存读取 |
| `_normalize_source_name` 未来新增来源未同步 | 低 | 已知约束，已记录；cache 层容错后不影响读取，写入路径 fail-closed 仍提供正确信号 |
| MiMo Finding 2 (fallback failure provenance) | 低 | 保留 — 当前 P7 不要求 |
| MiMo Finding 3 (legacy parsed cache no auto-refresh) | 低 | 保留 — `force_refresh=True` 可刷新 |

## Conclusion

PASS。

P7 aggregate Finding 1 修复正确、完整且无副作用。三层损坏输入（malformed JSON、非对象 JSON、非法 source name）均降级为 `None`，不阻断 `get_pdf_entry` / `get_pdf_path`。`AnnualReportSourceMetadata.from_dict` 在 cache 读取容错层外仍保持 fail-closed。Service/UI/Engine/CLI 零泄漏。测试覆盖充分（11 cache tests，含 3-way parametrized degradation test），文档与代码事实一致。293/293 tests pass, ruff clean。
