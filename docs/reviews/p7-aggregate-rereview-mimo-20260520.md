# P7 Aggregate Targeted Re-review — Finding 1 Fix Verification

## Scope

- Mode: targeted re-review of accepted finding fix
- Branch: main (unstaged workspace changes)
- Base: `docs/reviews/p7-aggregate-deepreview-mimo-20260520.md` finding 1
- Output file: `docs/reviews/p7-aggregate-rereview-mimo-20260520.md`
- Included scope: `_source_metadata_from_json` cache read tolerance, related tests, README sync
- Excluded scope: all other P7 aggregate findings and code

## Finding

### 1-已修复-中-`_source_metadata_from_json` 对非法 source name 无恢复路径

- **文件(行号)**: `cache.py:112-136`
- **修复前**: `json.loads()` 和 `AnnualReportSourceMetadata.from_dict()` 均无 try/except，非法 JSON 或未知 `source` 直接抛 `ValueError` 向上传播，阻断 `get_pdf_entry` / `get_pdf_path`
- **修复后**: 三层 try/except 降级为 `None`：
  1. `json.loads()` 失败（malformed JSON）→ `None`
  2. 解析结果不是 dict（non-object JSON）→ `None`
  3. `from_dict()` 抛 `ValueError`（含未知 `source`）→ `None`

**边界验证**：

| 检查点 | 预期 | 实际 | 结果 |
|---|---|---|---|
| `_source_metadata_from_json(None)` | `None` | `None` | PASS |
| `_source_metadata_from_json("{not-json")` | `None` | `None` | PASS |
| `_source_metadata_from_json('["not","object"]')` | `None` | `None` | PASS |
| `_source_metadata_from_json('{"source":"cninfo"}')` | `None` | `None` | PASS |
| `get_pdf_entry()` with 损坏 metadata | 返回 entry, `source_metadata=None` | entry 返回, PDF 路径可用 | PASS |
| `get_pdf_path()` with 损坏 metadata | 返回 Path | Path 返回 | PASS |
| `AnnualReportSourceMetadata.from_dict({"source":"cninfo"})` | `ValueError` | `ValueError: 未知年报来源: cninfo` | PASS |

**关键边界确认**：
- `models.py:87-117` 的 `AnnualReportSourceMetadata.from_dict()` 无 try/except，`_normalize_source_name`（models.py:309-311）仍对未知来源抛 `ValueError`。缓存容错仅在 `cache.py:133-136` 的 except 层，模型层来源闭集校验未被放宽。
- `get_pdf_entry()` 和 `get_pdf_path()` 在 PDF 文件存在时继续返回缓存命中，仅 `source_metadata` 降级为 `None`。

**测试验证**：
- 新增参数化测试 `test_cache_degrades_invalid_source_metadata_json_to_none`（test_cache.py:249-318）
- 覆盖三种污染场景：malformed JSON、非对象 JSON、未知来源名
- 同时断言 `get_pdf_entry()` 和 `get_pdf_path()` 均正常返回
- 11/11 cache tests passed，293/293 full suite passed，ruff clean

**文档同步**：
- `fund_agent/fund/README.md`: 新增缓存容错行为描述
- `tests/README.md`: 新增"损坏来源元数据降级"测试覆盖描述

## Conclusion

PASS. Finding 1 修复已验证。`_source_metadata_from_json` 正确降级损坏元数据为 `None`，不阻断 PDF 路径缓存读取。模型层 `from_dict()` 仍保持来源闭集校验。293/293 测试通过。
