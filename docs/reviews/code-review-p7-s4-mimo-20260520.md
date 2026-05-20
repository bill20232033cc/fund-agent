# Code Review — P7-S4 Source Metadata Hardening

## Scope

- Mode: current changes
- Branch: main (unstaged workspace changes)
- Base: main
- Output file: `docs/reviews/code-review-p7-s4-mimo-20260520.md`
- Included scope: P7-S4 source metadata hardening
  - `fund_agent/fund/documents/models.py` — `AnnualReportSourceMetadata`, `AnnualReportCacheProvenance`, `AnnualReportMetadata`, `AnnualReportPdfFetchResult` dataclasses; `ParsedAnnualReport.metadata` field with `to_dict()`/`from_dict()` compatibility
  - `fund_agent/fund/documents/sources.py` — imports metadata from `models.py`; removed local duplicate `AnnualReportSourceName`/`AnnualReportSourceMetadata`
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py` — `fetch_pdf() -> AnnualReportPdfFetchResult`; `fetch_pdf_path()` delegates to `fetch_pdf()`
  - `fund_agent/fund/documents/repository.py` — `_MetadataAwareAnnualReportLoader` protocol; metadata-aware fetch preference; `_with_annual_report_metadata()` helper; `load_annual_report()` metadata attachment and provenance
  - `fund_agent/fund/documents/cache.py` — `AnnualReportPdfCacheEntry`; `get_pdf_entry()`; additive `source_metadata_json` column; `save_parsed_report()` metadata precedence; `_normalize_report_source_metadata()`
  - `tests/fund/documents/test_cache.py` — 5 new/updated cache metadata tests
  - `tests/fund/documents/test_repository.py` — 9 new/updated repository metadata tests including concurrency regression
  - `tests/fund/documents/test_annual_report_sources.py` — import updates only
  - `fund_agent/fund/README.md` — metadata persistence description
  - `tests/README.md` — metadata test coverage description
- Excluded scope: Service, UI, Engine, CLI, template renderer, audit, quality gate, extraction, fund type, PDF parser, extra_payload
- Parallel review coverage: 无
- Design source of truth: `docs/design.md`
- Plan: `docs/reviews/p7-s4-source-metadata-hardening-plan-20260520.md`
- Plan review: `docs/reviews/p7-s4-plan-review-controller-20260520.md` (P7S4-PR-1 concurrency finding)
- Plan rereview: `docs/reviews/p7-s4-plan-rereview-controller-20260520.md` (P7S4-PR-1 closed)
- Implementation report: `docs/reviews/p7-s4-implementation-20260520.md`

## Findings

未发现实质性问题。

## Open Questions

- 无。

## Detailed Review Evidence

### 1. Metadata model moved to models.py (schema drift prevention)

- `models.py:14` defines `AnnualReportSourceName = Literal["eid", "eastmoney"]`
- `models.py:17-117` defines `AnnualReportSourceMetadata` with `to_dict()`/`from_dict()`
- `models.py:120-179` defines `AnnualReportCacheProvenance` with `to_dict()`/`from_dict()`
- `models.py:182-240` defines `AnnualReportMetadata` with `to_dict()`/`from_dict()`
- `sources.py:19` imports `AnnualReportSourceMetadata, AnnualReportSourceName` from `models.py`
- No duplicate local definitions remain in `sources.py`
- **Pass.**

### 2. Explicit per-call fetch result contract (P7S4-PR-1 closure)

- `models.py:243-253` defines `AnnualReportPdfFetchResult(pdf_path, source_metadata)` — `frozen=True, slots=True`
- `annual_report_pdf.py:202-232` implements `fetch_pdf() -> AnnualReportPdfFetchResult` calling source orchestrator
- `annual_report_pdf.py:234-261` implements `fetch_pdf_path() -> Path` delegating to `fetch_pdf()`
- No `_latest_source_metadata`, `consume_latest_source_metadata()`, or any adapter-wide mutable metadata state exists
- **Pass.** P7S4-PR-1 concurrency finding fully resolved.

### 3. Repository metadata-aware loader preference

- `repository.py:81-104` defines `_MetadataAwareAnnualReportLoader` protocol with `fetch_pdf()` and `parse_pdf()`
- `repository.py:204-225` implements `_get_metadata_aware_loader()` using `inspect.iscoroutinefunction()`
- `repository.py:346-354` prefers `fetch_pdf()` when available, receives `AnnualReportPdfFetchResult`
- `repository.py:355-361` falls back to legacy `fetch_pdf_path()` with `source_metadata=None`
- **Pass.**

### 4. Repository metadata attachment and provenance

- `repository.py:228-264` implements `_with_annual_report_metadata()` using `dataclasses.replace()` on frozen dataclass
- `repository.py:322-334`: parsed cache hit → retains existing `metadata.source`, sets `parsed_cache_hit=True`
- `repository.py:339-344`: PDF cache hit → uses `entry.source_metadata`, sets `pdf_cache_hit=True`
- `repository.py:368-384`: fresh fetch → attaches fetch result metadata, sets both cache hits `False`, saves with metadata
- **Pass.**

### 5. Cache metadata persistence and precedence

- `cache.py:30-41` defines `AnnualReportPdfCacheEntry(pdf_path, source_metadata, updated_at)`
- `cache.py:243-261` adds `source_metadata_json` column via `ALTER TABLE` (additive, non-destructive)
- `cache.py:280-294` adds `get_pdf_entry()` returning full entry; `get_pdf_path()` (line 263-278) delegates to it
- `cache.py:346-417` `record_pdf_path()` accepts `source_metadata` and writes JSON
- `cache.py:503-586` `_save_parsed_report_sync()`:
  - line 524: `effective_source_metadata = source_metadata or report.metadata.source` — explicit wins
  - line 525: normalizes report so payload metadata = documents row metadata
  - lines 532-559: writes documents row with same `effective_source_metadata`
  - lines 560-586: writes parsed payload with normalized report
- **Pass.** Documents row and parsed payload cannot diverge.

### 6. ParsedAnnualReport.metadata extension with legacy compatibility

- `models.py:514` adds `metadata: AnnualReportMetadata = field(default_factory=AnnualReportMetadata)` after `tables`
- `models.py:537` `to_dict()` writes `"metadata": self.metadata.to_dict()`
- `models.py:568-570` `from_dict()` uses `AnnualReportMetadata.from_dict(payload.get("metadata"))` — missing metadata returns empty `AnnualReportMetadata()`
- `PARSED_REPORT_SCHEMA_VERSION` remains `1` (cache.py:22) — no version bump
- **Pass.**

### 7. Concurrency regression test

- `test_repository.py:507-560` defines `_ConcurrentMetadataAwareLoader` with `asyncio.Event` barriers to force interleaving between two `fetch_pdf()` calls
- `test_repository.py:999-1049` runs two concurrent `load_annual_report()` for different fund codes via `asyncio.gather()`
- Asserts each report carries its own metadata: `report_a.metadata.source == metadata_a`, `report_b.metadata.source == metadata_b`
- Asserts each cache entry also carries correct metadata
- **Pass.** Guards against reintroduction of adapter-wide mutable state.

### 8. Eastmoney fallback metadata — no fake EID IDs

- `test_repository.py:193-215` constructs `_eastmoney_fallback_metadata()` with `source="eastmoney"`, `fallback_used=True`, all EID fields `None`
- `test_repository.py:738-775` asserts `fund_id is None`, `upload_info_id is None`, `upload_info_detail_id is None`
- **Pass.**

### 9. Force refresh metadata overwrite

- `test_repository.py:886-929`: first load persists `metadata_a`, force refresh returns `metadata_b`
- Asserts returned report, cached report, and PDF entry all carry `metadata_b`
- **Pass.**

### 10. Metadata-aware vs legacy loader preference

- `test_repository.py:932-965`: loader has both `fetch_pdf()` and `fetch_pdf_path()`, asserts `fetch_pdf()` is called and `fetch_pdf_path()` is not
- `test_repository.py:968-996`: loader has only `fetch_pdf_path()`, asserts `metadata.source is None` and `source_metadata_present is False`
- **Pass.**

### 11. Scope compliance

- Only 10 files changed (implementation report lists 11 including the review artifact itself)
- No Service/UI/Engine/CLI file changes
- No source-specific imports leak above Fund Capability (`grep` confirms imports from `models.py`/`sources.py` only in `tests/fund/documents/` and `fund_agent/fund/documents/`)
- No `extra_payload`
- No parser/extractor/audit/renderer/score/quality gate changes
- **Pass.**

### 12. Test coverage vs plan

| Plan test | Implementation | Pass? |
|---|---|---|
| Cache: PDF source metadata persistence | `test_cache_persists_pdf_source_metadata` | Yes |
| Cache: legacy documents row without metadata | `test_cache_loads_legacy_documents_row_without_source_metadata` | Yes |
| Cache: parsed report metadata round-trip | `test_parsed_report_payload_round_trips_metadata` | Yes |
| Cache: legacy parsed payload without metadata | `test_legacy_parsed_report_without_metadata_loads_with_empty_metadata` | Yes |
| Cache: explicit source_metadata alignment | `test_save_parsed_report_aligns_explicit_source_metadata_with_payload` | Yes |
| Repo: EID source metadata on fresh fetch | `test_repository_attaches_eid_source_metadata_on_fresh_fetch` | Yes |
| Repo: Eastmoney fallback metadata | `test_repository_attaches_eastmoney_fallback_metadata_on_fresh_fetch` | Yes |
| Repo: parsed cache hit retains metadata | `test_repository_parsed_cache_hit_retains_metadata` | Yes |
| Repo: PDF cache hit uses cached metadata | `test_repository_pdf_cache_hit_uses_cached_source_metadata` | Yes |
| Repo: legacy cache without metadata | `test_repository_legacy_cache_without_metadata_still_loads` | Yes |
| Repo: force refresh overwrites metadata | `test_repository_force_refresh_overwrites_source_metadata` | Yes |
| Repo: metadata-aware preferred over legacy | `test_repository_metadata_aware_loader_preferred_over_legacy_fetch_pdf_path` | Yes |
| Repo: legacy loader gets empty metadata | `test_repository_legacy_fetch_pdf_path_loader_gets_empty_source_metadata` | Yes |
| Repo: concurrent loads no cross-attach | `test_repository_concurrent_loads_do_not_cross_attach_source_metadata` | Yes |

14/14 plan tests present and passing. Source tests updated for moved imports only.

290/290 full suite passes, ruff clean.

## Residual Risk

- `AnnualReportSourceMetadata.from_dict()` 对 `source` 字段执行闭集校验 (`_normalize_source_name` 在 models.py:294-311)，如果未来新增来源名称但忘记更新 `_normalize_source_name`，反序列化会抛 `ValueError`。低风险，因为 `AnnualReportSourceName` Literal 类型会在类型检查时提示。
- `_get_metadata_aware_loader()` 使用 `inspect.iscoroutinefunction()` 检测 `fetch_pdf` (repository.py:222-224)，而非 Protocol structural subtyping。低风险，因为 Python runtime Protocol checking 本身也有局限。
- `_normalize_report_source_metadata` (cache.py:133-153) 使用 `replace()` 始终覆盖 `report.metadata.source`，即使 `source_metadata` 为 `None`。这与 `effective_source_metadata = source_metadata or report.metadata.source` 配合使用时行为正确（`None` 不会覆盖），但如果未来有人单独调用 `_normalize_report_source_metadata(report, None)` 会丢失已有 source metadata。低风险，因为该函数是私有的且仅在 `_save_parsed_report_sync` 中调用。

## Conclusion

PASS. No findings.

P7-S4 正确实现来源元数据从 `AnnualReportSourceResult` 到 `ParsedAnnualReport.metadata` 的完整持久化链路。metadata 模型移至 `models.py` 消除 schema drift 风险；`AnnualReportPdfFetchResult` 消除并发元数据串扰（P7S4-PR-1 已关闭）；cache precedence 确保 documents row 与 parsed payload 不会静默分叉；legacy 兼容性通过 additive column 和缺失 metadata 默认值保证。290/290 测试通过，ruff clean。
