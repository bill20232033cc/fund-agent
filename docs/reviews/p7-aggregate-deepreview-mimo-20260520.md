# P7 Aggregate Deepreview — Annual Report Source Migration

## Scope

- Mode: current changes (integrated on main)
- Branch: main
- Base: `3f281e3` (P7-S1 accepted, pre-P7-S2)
- Output file: `docs/reviews/p7-aggregate-deepreview-mimo-20260520.md`
- Included scope: all P7 slices integrated on main (S2 + S3 + S4)
  - `fund_agent/fund/documents/sources.py` — source protocol, orchestrator, EID source, Eastmoney wrapper, error hierarchy
  - `fund_agent/fund/documents/models.py` — metadata dataclasses, `ParsedAnnualReport.metadata`, `AnnualReportPdfFetchResult`
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py` — `fetch_pdf()` / `fetch_pdf_path()`, parser adaptation
  - `fund_agent/fund/documents/repository.py` — metadata-aware/legacy loader detection, metadata attachment, provenance
  - `fund_agent/fund/documents/cache.py` — additive `source_metadata_json` column, `get_pdf_entry()`, metadata precedence
  - `tests/fund/documents/test_annual_report_sources.py` — EID, orchestrator, adapter tests
  - `tests/fund/documents/test_repository.py` — repository metadata flow, concurrency regression
  - `tests/fund/documents/test_cache.py` — cache metadata, legacy compatibility
  - `fund_agent/fund/README.md`, `tests/README.md`
- Excluded scope: Service, UI, Engine, CLI, template renderer, audit, quality gate, extraction, fund type, PDF parser, extra_payload
- Parallel review coverage: 3 subagents (source chain, cache/metadata, tests/scope)
- Context artifacts: design.md, implementation-control-p4.md, 4 plan artifacts, 4 plan reviews, 4 code reviews, 4 controller judgments

## Findings

### 1-未修复-中-`_source_metadata_from_json` 对非法 source name 无恢复路径

- **入口/函数**: `_source_metadata_from_json` → `AnnualReportSourceMetadata.from_dict` → `_normalize_source_name`
- **文件(行号)**: `cache.py:112-130`, `models.py:87-117`, `models.py:294-311`
- **输入场景**: `documents.source_metadata_json` 中 `source` 字段值不在 `("eid", "eastmoney")` 闭集内
- **实际分支**: `_normalize_source_name` 检测到非法来源名，抛出 `ValueError`
- **预期行为**: 缓存读取应容错，非法来源元数据不应阻止 PDF 路径和 parsed report 的正常加载
- **实际行为**: `ValueError` 从 `_get_pdf_entry_sync` 向上传播，该 document key 的所有缓存读取（包括 PDF 路径）永久失败，直到手动修复 SQLite 或删除该行
- **直接证据**: `models.py:309-311` — `if source not in ("eid", "eastmoney"): raise ValueError(f"未知年报来源: {source}")`；`cache.py:127-130` — `_source_metadata_from_json` 无 try/except 包裹
- **影响**: 单点故障。虽当前只有代码写入 `source_metadata_json`（值域受控），但如果 SQLite 被手动编辑、未来新增来源名称后忘记更新 `_normalize_source_name`、或数据损坏，该 document key 将无法通过 `get_pdf_path` 或 `get_pdf_entry` 读取
- **建议改法和验证点**:
  ```python
  # cache.py:112-130 改为容错读取：
  def _source_metadata_from_json(payload: object) -> AnnualReportSourceMetadata | None:
      if payload is None:
          return None
      try:
          parsed = json.loads(str(payload))
      except (ValueError, TypeError):
          return None
      if not isinstance(parsed, dict):
          return None
      try:
          return AnnualReportSourceMetadata.from_dict(parsed)
      except ValueError:
          return None  # 非法来源名降级为无元数据
  ```
  验证：非法 source name 的 JSON 仍返回 `None` 而非崩溃；PDF 路径读取不受影响
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-低-orchestrator 不保留 fallback 失败来源链路

- **入口/函数**: `AnnualReportSourceOrchestrator.fetch_annual_report_pdf`
- **文件(行号)**: `sources.py:550-569`
- **输入场景**: 主源 not-found，fallback 源成功
- **实际分支**: `failures` 列表在方法返回时被丢弃，`_mark_fallback_used` 只标记 `fallback_used=True`
- **预期行为**: 返回结果应可追溯哪个主源失败及失败类别
- **实际行为**: `AnnualReportSourceResult.metadata` 只携带成功来源的元数据和 `fallback_used=True`，不携带失败来源的错误类别
- **直接证据**: `sources.py:550-551` — `failures: list[AnnualReportSourceFailure] = []` 为局部变量，方法返回后不可访问
- **影响**: 低。当前 P7 目标只要求标识最终来源和 fallback 标记，不要求失败链路。但如果未来需要审计"EID not-found 后 fallback 到 Eastmoney"的完整决策路径，需额外扩展
- **建议改法和验证点**: 可选增强：在 `AnnualReportSourceMetadata` 中添加 `fallback_reason: str | None` 或 `prior_failures: tuple[AnnualReportSourceFailure, ...]`。当前不修复可接受
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-低-legacy parsed report 缓存永不刷新来源元数据

- **入口/函数**: `cache.load_parsed_report` → `repository.load_annual_report`
- **文件(行号)**: `cache.py:463-464`, `repository.py:322-334`
- **输入场景**: P7 之前已缓存的 parsed report JSON 无 `"metadata"` 字段
- **实际分支**: `from_dict` 返回空 `AnnualReportMetadata(source=None)`，`schema_version == 1` 不触发缓存失效
- **预期行为**: legacy 缓存应加载成功但携带空元数据
- **实际行为**: 正确加载，但 legacy 条目永远不主动刷新元数据。即使 `documents.source_metadata_json` 已通过 `record_pdf_path` 写入，parsed cache hit 路径（`repository.py:324-334`）从 JSON 读取元数据而非 SQLite，导致 `source=None` 永久保留
- **直接证据**: `repository.py:327` — `source_metadata=cached_report.metadata.source` 从 JSON 反序列化，而非 `get_pdf_entry().source_metadata`
- **影响**: 低。legacy 条目的 `metadata.source` 永久为 `None`，`source_metadata_present` 永久为 `False`。只有 `force_refresh=True` 才能刷新
- **建议改法和验证点**: 可选增强：parsed cache hit 路径可从 `get_pdf_entry()` 补充 `source_metadata`（如果 JSON 中为空但 SQLite 中有值）。或 bump `PARSED_REPORT_SCHEMA_VERSION` 到 2 强制重解析
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。

## Detailed Review Evidence

### 1. Cross-Slice Composition: Source Abstraction + EID Primary + Eastmoney Fallback

**Source acquisition chain** (sources.py → adapters/annual_report_pdf.py → repository.py):

- `EidAnnualReportSource.fetch_annual_report_pdf()` (sources.py:290-339): validate_fund → search_report → download PDF → validate Content-Type + `%PDF-` → return `AnnualReportSourceResult` with rich metadata
- `EastmoneyAnnualReportSource.fetch_annual_report_pdf()` (sources.py:449-488): wrap legacy downloader → return `AnnualReportSourceResult` with sparse metadata (source, fund_code, report_year only)
- `AnnualReportSourceOrchestrator.fetch_annual_report_pdf()` (sources.py:550-569): iterate sources, catch `NotFoundError`/`UnavailableError` → continue, catch `MismatchError`/`SchemaError` → immediately raise
- `_mark_fallback_used()` (sources.py:613-627): nested `dataclasses.replace` on frozen dataclass — correct immutable update
- `AnnualReportPdfAdapter.fetch_pdf()` (adapters/annual_report_pdf.py:224-232): calls orchestrator, wraps in `AnnualReportPdfFetchResult(pdf_path, metadata)` — clean 1:1 mapping, no metadata loss

**Default orchestrator order** (sources.py:558-562):
```python
(EidAnnualReportSource(config=self.config), EastmoneyAnnualReportSource())
```
Tested in `test_orchestrator_rejects_empty_sources_but_none_uses_default`.

**Error category composition** (sources.py:599-606):
- `AnnualReportSourceNotFoundError` (extends `FileNotFoundError`) → fallback eligible
- `AnnualReportSourceUnavailableError` (extends `Exception`) → fallback eligible
- `AnnualReportSourceMismatchError` (extends `ValueError`) → fail-closed, stop fallback
- `AnnualReportSourceSchemaError` (extends `ValueError`) → fail-closed, stop fallback

This matches the plan's design intent: "mismatch/schema errors stop fallback to avoid hiding source identity or report-type contradictions."

**Eastmoney sparse metadata** (sources.py:481-488): When Eastmoney is the fallback, `source_url`, `fund_id`, `report_code`, etc. are all `None`. This is by design per plan: "Do not fake EID IDs for fallback results." The `fallback_used=True` flag correctly signals provenance.

**Pass.** Cross-slice source composition is correct.

### 2. Cache/Source Metadata Composition

**Metadata persistence chain**:
1. Repository receives `AnnualReportPdfFetchResult` from adapter (repository.py:348-354)
2. `record_pdf_path()` writes `source_metadata_json` to `documents` SQLite row (cache.py:390-417)
3. `save_parsed_report()` normalizes report metadata via `_normalize_report_source_metadata()` and writes both JSON payload and SQLite row from the same `effective_source_metadata` variable (cache.py:524-586)

**Metadata precedence** (cache.py:524):
```python
effective_source_metadata = source_metadata or report.metadata.source
```
Explicit `source_metadata` kwarg wins. Tested in `test_save_parsed_report_aligns_explicit_source_metadata_with_payload`.

**Divergence prevention** (cache.py:133-153): `_normalize_report_source_metadata()` uses `dataclasses.replace()` to overwrite `report.metadata.source` with the effective value before writing the JSON payload. Both JSON file and SQLite column are populated from the same variable in the same method — cannot diverge within a single call.

**Redundant UPSERT**: `record_pdf_path()` (repository.py:362) and `save_parsed_report()` (repository.py:380) both write to the `documents` table for the same key. The second UPSERT overwrites the first with identical values. Harmless but redundant.

**Pass.** Metadata composition is correct and divergence-proof.

### 3. Legacy Cache Compatibility

**Additive SQLite column** (cache.py:256-261):
```python
columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(documents)").fetchall()}
if "source_metadata_json" not in columns:
    connection.execute("ALTER TABLE documents ADD COLUMN source_metadata_json TEXT")
```
Idempotent guard, runs on every `_get_pdf_entry_sync` and `_initialize_sync`. New column defaults to `NULL`. No destructive migration.

**Legacy documents row** (cache.py:325-344): `source_metadata_json` is `NULL` → `_source_metadata_from_json(None)` returns `None`. Tested in `test_cache_loads_legacy_documents_row_without_source_metadata`.

**Legacy parsed JSON** (models.py:568-570): `payload.get("metadata")` returns `None` → `AnnualReportMetadata.from_dict(None)` returns empty metadata. Tested in `test_legacy_parsed_report_without_metadata_loads_with_empty_metadata`.

**PARSED_REPORT_SCHEMA_VERSION** remains `1` (cache.py:22). Legacy entries with `schema_version=1` pass the check and load with empty metadata. No version bump means legacy entries persist indefinitely without source metadata in their JSON payload. This is a data quality gap, not a corruption risk.

**Pass.** Legacy compatibility is robust.

### 4. Stale/Wrong-Source Cache Risks

**Force refresh** (repository.py:323, 339): `force_refresh=True` skips both parsed cache and PDF cache, fetches fresh, overwrites both documents row and parsed payload with fresh metadata. Tested in `test_repository_force_refresh_overwrites_source_metadata`.

**PDF cache hit with stale metadata**: If a PDF was cached with EID metadata but EID later becomes unavailable, the cached PDF and metadata persist. On next load (without force_refresh), the cached EID metadata is returned. This is correct cache behavior — the PDF is still valid, and the metadata accurately reflects how it was originally acquired.

**Parsed cache hit path** (repository.py:324-334): Returns `cached_report.metadata.source` from the JSON payload, not from the SQLite row. Both were written with the same metadata during `save_parsed_report()`, so they should be consistent. If JSON is manually corrupted, divergence is possible — but this is a manual intervention scenario, not a normal operation risk.

**Pass.** Stale cache behavior is correct and intentional.

### 5. Provenance Boundaries

**No Service/UI/Engine/CLI source awareness**: Grep confirms no imports of `fund_agent.fund.documents.sources`, `fund_agent.fund.documents.models`, `AnnualReportSourceMetadata`, `EidAnnualReportSource`, `EID_*` constants, or source error classes in `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/engine/`, `fund_agent/cli.py`, `tests/services/`, or `tests/ui/`.

**Public model export**: `ParsedAnnualReport` (with `metadata` field) is the only document model visible above Fund Capability. Source metadata travels inside `ParsedAnnualReport.metadata.source` — upper layers see it as an opaque provenance field, not as source selection input.

**No extra_payload**: No `extra_payload` field or references added in P7.

**Pass.** Provenance boundaries are clean.

### 6. Public Model/Export Coherence

- `AnnualReportSourceMetadata` in `models.py`: frozen dataclass, `to_dict()`/`from_dict()`, closed-set source name validation
- `AnnualReportCacheProvenance` in `models.py`: frozen dataclass, tracks `pdf_cache_hit`, `parsed_cache_hit`, `source_metadata_present`, `cache_schema_version`
- `AnnualReportMetadata` in `models.py`: wraps source + cache, `to_dict()`/`from_dict()` with missing-payload defaults
- `AnnualReportPdfFetchResult` in `models.py`: frozen per-call immutable result, concurrency-safe
- `ParsedAnnualReport.metadata` in `models.py`: appended field with `default_factory=AnnualReportMetadata`, backward-compatible
- `sources.py` imports metadata from `models.py` — single source of truth, no duplicate definitions

**Pass.** Public models are coherent and consistently exported.

### 7. Test Adequacy

**Source tests** (test_annual_report_sources.py): 13 EID + 13 orchestrator + 1 adapter = 27 tests. Error-category × fallback-behavior matrix is well-covered except for one gap: no test where primary throws continue-category error and fallback throws stop-category error (e.g., primary=not_found + fallback=schema_error). The "all fail" tests cover the case where both throw the same category, and the "fallback succeeds" tests cover the happy path, but the mixed-error-after-continue path is untested.

**Repository tests** (test_repository.py): All 9 planned metadata tests present. Concurrency test uses `asyncio.Event` barriers for deterministic interleaving. Legacy loader and metadata-aware loader preference tests present.

**Cache tests** (test_cache.py): Legacy documents row and legacy parsed payload compatibility tests present. Metadata round-trip and precedence alignment tests present.

**Full suite**: 290/290 passed, ruff clean.

## Residual Risk

| Risk | Severity | Status |
|---|---|---|
| Invalid source name in cached metadata crashes all reads for that key | Medium | Finding 1 — needs fix |
| Orchestrator discards failure provenance after fallback success | Low | Finding 2 — by design, acceptable |
| Legacy parsed cache never auto-refreshes source metadata | Low | Finding 3 — data quality gap, acceptable |
| No test for primary=not_found + fallback=schema_error path | Low | Test gap, non-blocking |
| No adapter-level test for `fetch_pdf()` returning metadata | Low | Test gap, covered indirectly by repository tests |
| Eastmoney fallback metadata has sparse fields (no source_url, fund_id) | Low | By design per plan |
| Redundant documents table UPSERT in non-force-refresh path | Negligible | Idempotent, no correctness impact |
| `get_pdf_path()` unused by repository (dead code) | Negligible | Convenience API, harmless |

## Conclusion

PASS with one medium finding and two low findings.

P7 annual report source migration composes correctly across all four slices. Source abstraction with EID primary → Eastmoney fallback, fail-closed error categories, metadata persistence through cache and parsed report, legacy compatibility, and provenance boundaries are all correctly implemented. 290/290 tests pass, ruff clean, no scope leakage.

One medium finding: `_source_metadata_from_json` does not handle invalid source names gracefully, which can permanently block cache reads for a document key. Two low findings: orchestrator discards fallback failure provenance (by design), and legacy parsed cache never auto-refreshes source metadata (data quality gap).
