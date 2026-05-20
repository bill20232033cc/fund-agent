# P7 Aggregate Deep Review

## Scope

- Mode: all repository (P7 annual report source migration on main)
- Branch: main
- Base: `3f281e3` (P7-S1 accepted) through `707d89f` (P7-S4 accepted)
- Output file: docs/reviews/p7-aggregate-deepreview-glm-20260520.md
- Included scope:
  - P7-S1 EID source research spike
  - P7-S2 document repository source abstraction
  - P7-S3 EID primary implementation
  - P7-S4 source metadata hardening
  - All cross-slice integration paths: sources.py → orchestrator → adapter → repository → cache
  - Test coverage across all slices: 290 tests
- Excluded scope: P6 template contract, P5 quality gate, P4 extraction snapshot, Service/UI/Engine/CLI, parser, extractor, audit, renderer, template draft, extra_payload
- Parallel review coverage:
  - Subagent 1: Cross-slice data flow integrity (source → orchestrator → adapter → repository → cache metadata chain)
  - Subagent 2: Stale cache and source switch risks (PDF path collision, orphan files, cache row consistency)
  - Subagent 3: Error category composition (fail-closed vs fallback-eligible across all 4 layers)
  - Subagent 4: Boundary integrity and public export coherence (no upper-layer leaks, import DAG, no extra_payload)

## Findings

未发现实质性问题。

### Cross-Slice Correctness Summary

逐项审查结论：

#### 1. Source Abstraction + EID Primary + Eastmoney Fallback Composition

`AnnualReportSourceOrchestrator(None)` 构造 `(EidAnnualReportSource(config), EastmoneyAnnualReportSource())`（`sources.py:558-561`）。EID 先执行 3 步流程（`validate_fund.do` → `advanced_search_report.do` → `instance_show_pdf_id.do`），失败时按错误类别决定是否 fallback：

- `NotFoundError` / `UnavailableError`：append failure，continue 到 Eastmoney（`sources.py:599-604`）。
- `MismatchError` / `SchemaError`：立即 raise，阻止 fallback（`sources.py:605-606`）。

Eastmoney fallback 成功时，`_mark_fallback_used` 用 `dataclasses.replace` 设置 `fallback_used=True`（`sources.py:567`）。编排器返回的 `AnnualReportSourceResult` 始终携带非 None 的 `AnnualReportSourceMetadata`。

错误类别在所有 4 层正确组合：

| 层 | 行为 |
|---|---|
| Source (EID/Eastmoney) | 分类为 NotFound/Unavailable/Mismatch/Schema |
| Orchestrator | NotFound/Unavailable → continue; Mismatch/Schema → raise |
| Adapter | 纯透传，不 catch/wrap/suppress |
| Repository | 纯透传；`NotFoundError` is-a `FileNotFoundError`，`MismatchError`/`SchemaError` is-a `ValueError` |

`AggregateError` 继承自 `Exception`（非 `FileNotFoundError`），防止调用方意外将混合失败当作"文件未找到"。测试显式验证此不变量（`test_annual_report_sources.py`）。

#### 2. Cache/Source Metadata Composition

完整数据流追踪确认元数据在生产路径无损：

1. `EidAnnualReportSource.fetch_annual_report_pdf` 返回 `AnnualReportSourceResult(pdf_path, metadata)`，EID 元数据包含所有平台字段（`sources.py:280-339`）。
2. `AnnualReportPdfAdapter.fetch_pdf` 透传为 `AnnualReportPdfFetchResult(pdf_path, source_metadata)`（`annual_report_pdf.py:224-232`）。per-call immutable result，无 adapter-wide 可变状态。
3. `FundDocumentRepository.load_annual_report` 通过 `_get_metadata_aware_loader` 检测 loader 能力，优先 `fetch_pdf` 路径（`repository.py:346-354`）。
4. `parse_pdf` 不传 metadata（by design），repository 用 `_with_annual_report_metadata` 重新附加（`repository.py:373-379`）。
5. `save_parsed_report` 用 `source_metadata or report.metadata.source` 计算有效元数据（`cache.py:524`），然后用 `_normalize_report_source_metadata` 对齐 payload 和 documents row（`cache.py:525`），两处在同一 SQLite 事务中写入（`cache.py:532-586`），不会静默分叉。

legacy loader 路径（无 `fetch_pdf`）设 `source_metadata=None`，测试 `test_repository_legacy_fetch_pdf_path_loader_gets_empty_source_metadata` 显式覆盖。

#### 3. Stale/Wrong-Source Cache Risks

- **SQLite cache row 覆写**：`record_pdf_path` 和 `save_parsed_report` 均使用 `INSERT ... ON CONFLICT DO UPDATE`，source switch 时 `pdf_path` 和 `source_metadata_json` 被完全替换。
- **PDF 路径无碰撞**：EID 使用 `{fund_code}_{year}_annual_report_eid.pdf`（`sources.py:464`），Eastmoney 使用 `{fund_code}_{year}_annual_report.pdf`（`downloader.py:134`）。不同后缀，无碰撞。
- **Parsed cache hit 语义**：`force_refresh=False`（默认）时，parsed cache hit 直接返回（`repository.py:324-334`），不重新验证 source 可用性。这是正确的缓存语义——缓存元数据准确反映当初获取时的 source provenance，`parsed_cache_hit=True` 告知调用方数据来源。`force_refresh=True` 跳过两层缓存并重新写入。
- **文件存在性检查**：`_get_pdf_entry_sync` 在 `cache.py:338` 检查 `pdf_path.exists()`，文件缺失时返回 None 触发重新下载。系统自愈。
- **孤立项**：source switch 后旧 PDF 文件残留在磁盘但不再被引用，属 cosmetic disk-space 问题，不影响正确性。

#### 4. Legacy Cache Compatibility

- `_ensure_documents_source_metadata_column` 通过 `PRAGMA table_info` + `ALTER TABLE ADD COLUMN` 增量加列（`cache.py:243-261`），对旧 SQLite 文件零破坏。
- `ParsedAnnualReport.from_dict` 在 `models.py:568-569` 接受缺失的 metadata key，`AnnualReportMetadata.from_dict(None)` 返回空默认实例（`models.py:226-227`）。
- `_get_pdf_entry_sync` 对 `source_metadata_json` 为 null 的旧行返回 `source_metadata=None`。
- `PARSED_REPORT_SCHEMA_VERSION` 未递增，旧 payload 正确加载。
- 测试覆盖：`test_cache_loads_legacy_documents_row_without_source_metadata`、`test_legacy_parsed_report_without_metadata_loads_with_empty_metadata`。

#### 5. Provenance Boundaries

Source provenance 严格限制在 Fund Capability documents 层内部：

- `metadata.source` 描述的是文档获取来源，不是上层业务状态。
- Cache provenance（`pdf_cache_hit`、`parsed_cache_hit`、`source_metadata_present`）描述缓存命中事实。
- `AnnualReportSourceName` 为 `Literal["eid", "eastmoney"]` 闭集，新增来源需更新此类型（已知 residual risk）。
- 4 个 parallel grep 确认 Service/UI/Engine/CLI 零引用 sources/cache/repository 层符号。

#### 6. No Service/UI/Engine/CLI Source Awareness

Boundary audit 确认：

| 搜索目标 | 搜索范围 | 结果 |
|---|---|---|
| `documents.sources`, `documents.cache`, `documents.repository` | `services/`, `ui/`, `engine/` | 零匹配 |
| `EidAnnualReportSource`, `AnnualReportSourceOrchestrator` | `services/`, `ui/` | 零匹配 |
| `AnnualReportDocumentCache`, `AnnualReportSourceResult` | `services/`, `ui/` | 零匹配 |
| `extra_payload` | `documents/` | 零匹配 |

Import DAG 方向正确：`models.py`（leaf）← `sources.py`, `cache.py` ← `adapters/annual_report_pdf.py` ← `repository.py`。`repository.py` 不直接 import `sources.py`。无循环依赖。

#### 7. Public Model/Export Coherence

`models.py` 定义全部 5 个公共元数据类型：`AnnualReportSourceName`、`AnnualReportSourceMetadata`、`AnnualReportCacheProvenance`、`AnnualReportMetadata`、`AnnualReportPdfFetchResult`。`sources.py` 从 `models.py` import，无重复定义。所有新增类均为 `frozen=True, slots=True`。

`ParsedAnnualReport.metadata` 通过 `field(default_factory=AnnualReportMetadata)` 提供默认值，现有构造代码无需修改。

#### 8. Tests Adequate for Fail-Closed and Concurrent Metadata

- EID fail-closed 测试：wrong year、quarterly report、non-PDF table、abstract title、duplicate candidates、attachment link 均验证抛出 MismatchError 或 SchemaError。
- Orchestrator fallback 测试：not-found → fallback、mismatch → 不 fallback、unavailable → fallback、schema → 不 fallback。
- Metadata 测试：EID fresh fetch、Eastmoney fallback、parsed cache hit、PDF cache hit、legacy cache、force_refresh overwrite、metadata-aware preferred、legacy empty。
- 并发防串扰测试：`test_repository_concurrent_loads_do_not_cross_attach_source_metadata` 使用 `asyncio.Event` 屏障强制交错，通过 `asyncio.gather` 并发运行两个不同基金，断言每个返回的 report 和 cache entry 携带各自的 source metadata。直接回归 P7S4-PR-1 识别的并发 provenance corruption 风险。
- Cache precedence 测试：`test_save_parsed_report_aligns_explicit_source_metadata_with_payload` 验证显式 source_metadata B 覆盖 report 内嵌 metadata A 后 documents row 和 parsed payload 一致。
- 全部测试使用 fake network（MockTransport / _RecordingEidClient），无 live EID/Eastmoney 依赖。

## Open Questions

- 无

## Residual Risk

| Risk | Severity | Detail |
|---|---|---|
| EID response schema drift | 低 | EID 端点响应字段可能变更；当前 fail-closed 设计（`_parse_eid_candidate`、`_select_eid_annual_report_candidate`）会拒绝不符合预期的响应，但缺少主动 schema drift 监测。 |
| Parsed cache 无 TTL / source liveness check | 低 | `force_refresh=False`（默认）时，parsed cache hit 直接返回，不重新验证 EID 可用性。这是正确的缓存语义，但意味着 source 可用性变化不会反映到已缓存报告。需要 `force_refresh=True` 强制刷新。 |
| Orphan PDF 文件累积 | 低 | Source switch 后旧 PDF 文件残留在磁盘但不再被引用，无清理机制。不影响正确性，仅消耗磁盘空间。 |
| `source_metadata_json` 人工损坏 | 低 | `_source_metadata_from_json` 对非法 JSON raise ValueError，会从 `get_pdf_entry` 传播。代码控制的写入不受影响，但人工编辑 SQLite 行可能导致该条目不可读。 |
| `AnnualReportSourceName` 闭集扩展 | 低 | 新增来源需更新 `Literal["eid", "eastmoney"]` 和 `_normalize_source_name` 验证，属已知的未来扩展约束。 |
| Legacy loader 元数据丢失 | 低 | 自定义 loader 不实现 `fetch_pdf` 时 `source_metadata=None`，所有 source 元数据被丢弃。默认 `AnnualReportPdfAdapter` 不受影响，测试显式覆盖此路径。 |

## Verification

```bash
.venv/bin/python -m pytest tests/ -q
# 290 passed

.venv/bin/python -m ruff check .
# All checks passed

git diff --check
# passed

git log --oneline -8
# 3a84f1b Accept P7 aggregate readiness
# 707d89f Implement P7-S4 source metadata hardening
# 9faf61e Plan P7-S4 source metadata hardening
# f727ca7 Implement P7-S3 EID primary source
# dc9e2f0 Plan P7-S3 EID primary source
# eb39877 Implement P7-S2 source abstraction
# 92d23c3 Plan P7-S2 source abstraction
# 3f281e3 Accept P7-S1 EID source research

# Boundary integrity: zero matches in Service/UI/Engine/CLI for all source-layer symbols
# Import DAG: models ← sources, cache ← adapters ← repository (clean, no cycles)
# No extra_payload in documents module
```
