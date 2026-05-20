# Code Review — P7-S3 EID Primary Annual-Report Source

## Scope

- Mode: current changes
- Branch: main (unstaged workspace changes)
- Base: main
- Output file: `docs/reviews/code-review-p7-s3-mimo-20260520.md`
- Included scope: P7-S3 EID primary annual-report source migration
  - `fund_agent/fund/documents/sources.py` — `EidAnnualReportSource`, typed EID dataclasses, 3 endpoint parsers, fail-closed filters, PDF validation, request-level retries
  - `tests/fund/documents/test_annual_report_sources.py` — 18 EID tests + 12 P7-S2 orchestrator/adapter tests
  - `fund_agent/fund/README.md` — EID primary source description
  - `tests/README.md` — fake EID network coverage description
- Excluded scope: Service, UI, Engine, CLI, template renderer, audit, quality gate, extraction, fund type, PDF parser, cache schema, `extra_payload`
- Parallel review coverage: 无
- Design source of truth: `docs/design.md`
- Plan: `docs/reviews/p7-s3-eid-primary-implementation-plan-20260520.md`
- Implementation report: `docs/reviews/p7-s3-implementation-20260520.md`

## Findings

### 1-未修复-低-`_eid_candidate_mismatch_reason` 附件链路使用 SchemaError 而非 MismatchError

- **入口/函数**: `_eid_candidate_mismatch_reason`
- **文件(行号)**: `sources.py:1011`
- **输入场景**: EID 候选包含 `attachFileName` 或 `attachFilePath`
- **实际分支**: `if candidate.attach_file_name or candidate.attach_file_path: raise AnnualReportSourceSchemaError("EID 候选包含 P7-S3 不支持的附件链路")`
- **预期行为**: 附件链路是候选数据与当前实现能力的矛盾，语义上属于 mismatch（数据与请求/能力不匹配），应使用 `AnnualReportSourceMismatchError`
- **实际行为**: 使用 `AnnualReportSourceSchemaError`，虽然两者在 orchestrator 中均 fail-closed 不进入 fallback，但错误类别语义不精确
- **直接证据**: `sources.py:1011` — `raise AnnualReportSourceSchemaError("EID 候选包含 P7-S3 不支持的附件链路")`；同函数中其他矛盾条件（fundCode、reportYear 等）返回 mismatch reason 字符串，最终在 `_select_eid_annual_report_candidate:970` 抛出 `AnnualReportSourceMismatchError`
- **影响**: 低。不影响 fallback 行为（两者均 stop fallback），不影响测试通过。但当调用方需要按错误类别做日志或监控时，附件链路会被归类为"结构非法"而非"数据矛盾"，不利于诊断
- **建议改法和验证点**:
  ```python
  # line 1011 改为：
  raise AnnualReportSourceMismatchError("EID 候选包含 P7-S3 不支持的附件链路")
  ```
  验证：`test_eid_source_rejects_attachment_candidate` 断言改为 `AnnualReportSourceMismatchError`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。

## Detailed Review Evidence

### 1. EID 3-endpoint flow

- `fetch_annual_report_pdf` (lines 331-380): 调用 `_validate_fund` → `_search_annual_report` → PDF download/cache
- `_validate_fund` (lines 382-406): POST to `validate_fund.do`，解析 `_parse_eid_validate_response`
- `_search_annual_report` (lines 408-448): GET to `advanced_search_report.do`，构造 `aoData`，解析候选，调用 `_select_eid_annual_report_candidate`
- PDF 下载 (lines 365-380): 构造 `instance_show_pdf_id.do?instanceid=...` URL，`_validate_pdf_response` 校验 Content-Type 和 `%PDF-`
- **Pass.**

### 2. Deterministic aoData encoding

- `_build_eid_ao_data` (lines 839-865): 包含 `reportType=FB010`、`reportYear=<year>`、`fundCode=<code>`，使用 `json.dumps(separators=(",",":"))` 确保确定性
- 测试验证 (test line 431-434): 解析 aoData 并断言 `{"name": "reportType", "value": "FB010"}` in ao_data
- **Pass.**

### 3. Fail-closed candidate filtering

- `_select_eid_annual_report_candidate` (lines 930-972): 空候选 → `NotFoundError`；单有效 → 返回；多有效 → `SchemaError`；全部矛盾 → `MismatchError`
- `_eid_candidate_mismatch_reason` (lines 975-1012): 7 个精确字段检查 + abstract 检查 + attachment 检查
  - fundCode exact match
  - fundId exact match (from validate)
  - reportYear exact match
  - reportCode = FB010010
  - reportDesp = 年度报告
  - tableName = PDF
  - reportName 含"摘要" → reject
  - attachFileName/attachFilePath 非空 → reject (finding 1: SchemaError vs MismatchError)
- 测试覆盖: parametrized `test_eid_source_rejects_mismatched_candidates` 覆盖 year/reportCode/tableName/abstract；独立测试覆盖 duplicate 和 attachment
- **Pass** (finding 1 为低严重程度语义问题)。

### 4. PDF validation

- `_validate_pdf_response` (lines 1032-1049): Content-Type split on ";" 前比较 `application/pdf`，body startswith `%PDF-`
- 测试: `test_eid_source_pdf_content_type_must_be_pdf` (text/html → SchemaError)、`test_eid_source_pdf_magic_bytes_must_be_pdf` (非 PDF body → SchemaError)
- **Pass.**

### 5. Request-level timeout semantics

- `_request_with_retries` (lines 739-790): 每次请求传入独立 `timeout` 参数
- `_validate_fund`: `timeout=self._config.metadata_timeout_seconds` (line 403)
- `_search_annual_report`: `timeout=self._config.metadata_timeout_seconds` (line 440)
- PDF download: `timeout=self._config.pdf_timeout_seconds` (line 374)
- 一个 async client/session per source call (line 357 `async with self._client_factory() as client`)，cookie preservation
- 测试: `_RecordingEidClient` 记录 `[3.5, 3.5, 77.0]` 对应 `[POST validate, GET search, GET PDF]`
- **Pass.**

### 6. Cache path and force_refresh

- `_build_pdf_cache_path` (line 464): `cache_dir / f"{fund_code}_{year}_annual_report_eid.pdf"`
- force_refresh=True 跳过 `pdf_path.exists()` 检查 (line 368)
- 非 force_refresh + 文件存在 → 直接返回，不请求 PDF endpoint (line 368-369)
- 测试: `test_eid_source_force_refresh_overwrites_cached_pdf` 和 `test_eid_source_without_force_refresh_reuses_existing_pdf_after_metadata_validation` 验证行为和请求链路
- **Pass.**

### 7. Default orchestrator order

- `AnnualReportSourceOrchestrator(None)` → `(EidAnnualReportSource(config=self.config), EastmoneyAnnualReportSource())` (lines 558-562)
- 空元组 `()` → `ValueError("sources 不能为空")` (lines 563-564)
- 测试: `test_orchestrator_rejects_empty_sources_but_none_uses_default` 验证长度 2、顺序 [Eid, Eastmoney]
- **Pass.**

### 8. Orchestrator fallback semantics (P7-S2 baseline preserved)

- `AnnualReportSourceNotFoundError` 和 `AnnualReportSourceUnavailableError` → continue to next source
- `AnnualReportSourceMismatchError` 和 `AnnualReportSourceSchemaError` → immediately raise
- `_raise_exhausted_sources`: all not_found → `NotFoundError`；single unavailable → `UnavailableError`；mixed/multi → `AggregateError`
- 测试: 6 个 orchestrator 测试覆盖成功、unavailable fallback、not-found fallback、mismatch stop、schema stop、exhausted all-not-found、exhausted unavailable、mixed
- **Pass.**

### 9. Scope compliance

- 仅变更 4 个文件: `sources.py`, `test_annual_report_sources.py`, `fund/README.md`, `tests/README.md`
- 无 Service/UI/Engine/CLI/template renderer/audit/quality gate/extraction/fund type/documents/PDF parser/cache schema/`extra_payload` 变更
- 无 source imports 泄漏到 `fund_agent/fund/documents/` 外部
- **Pass.**

### 10. Test coverage vs plan

| Plan test | Implementation | Pass? |
|---|---|---|
| 1. EID 004393/2024 happy path | `test_eid_source_fetches_004393_annual_report_with_validated_metadata` | Yes |
| 2. validate false → not-found | `test_eid_source_validate_fund_false_is_not_found` | Yes |
| 3. validate schema failure | `test_eid_source_validate_schema_error_fails_closed` | Yes |
| 4. empty aaData → not-found | `test_eid_source_search_empty_is_not_found` | Yes |
| 5. wrong year → mismatch | parametrized `test_eid_source_rejects_mismatched_candidates` | Yes |
| 6. quarterly report → mismatch | parametrized `test_eid_source_rejects_mismatched_candidates` | Yes |
| 7. non-PDF table → mismatch | parametrized `test_eid_source_rejects_mismatched_candidates` | Yes |
| 8. abstract title → mismatch | parametrized `test_eid_source_rejects_mismatched_candidates` | Yes |
| 9. duplicate valid → schema | `test_eid_source_rejects_duplicate_candidates` | Yes |
| 10. attachment → schema | `test_eid_source_rejects_attachment_candidate` | Yes |
| 11. PDF Content-Type | `test_eid_source_pdf_content_type_must_be_pdf` | Yes |
| 12. %PDF- magic bytes | `test_eid_source_pdf_magic_bytes_must_be_pdf` | Yes |
| 13. timeout → unavailable | `test_eid_source_transient_http_error_is_unavailable` | Yes |
| 14. default order EID then Eastmoney | `test_orchestrator_rejects_empty_sources_but_none_uses_default` | Yes |
| 15. fallback after EID not-found | `test_orchestrator_falls_back_to_eastmoney_after_eid_not_found` | Yes |
| 16. no fallback after EID mismatch | `test_orchestrator_does_not_fallback_after_eid_mismatch` | Yes |
| 17. force_refresh overwrites PDF | `test_eid_source_force_refresh_overwrites_cached_pdf` | Yes |
| 18. non-force reuses existing PDF | `test_eid_source_without_force_refresh_reuses_existing_pdf_after_metadata_validation` | Yes |
| 19. request-level timeouts differ | `test_eid_source_uses_distinct_request_level_timeouts` | Yes |

19/19 plan tests present and passing. All use fake network only.

276/276 full suite passes, ruff clean.

## Residual Risk

- EID response schema drift: `attachFileName`/`attachFilePath` 字段若被 EID 移除或重命名，附件检测会静默失效，候选将通过过滤。低风险，因为当前 EID 响应仍包含这些字段。
- `_request_with_retries` 的重试间隔使用 `asyncio.sleep(0)` (line 789)，仅让出事件循环，不做实际退避。生产环境中 EID 瞬时故障可能连续命中。低风险，因为 `retry_attempts` 默认值为 2。
- `_join_eid_url` 在 base_url 以 `/fund` 结尾且 path 以 `/fund/` 开头时会去掉 base_url 的 `/fund` 后缀 (line 734-735)。逻辑正确但依赖 URL 结构约定，若 EID 路径变更需同步检查。
- `AnnualReportSourceMetadata` 当前不持久化到 cache schema，仅在 `AnnualReportSourceResult` 中返回。后续如需持久化，需 cache schema migration。

## Conclusion

PASS with one low finding.

P7-S3 正确实现 EID 主源 → Eastmoney fallback 的来源编排。3 个 EID endpoint 解析、8 个 fail-closed 过滤规则、PDF 校验、request-level timeout 均按 plan 落地。无 scope 泄漏。276/276 测试通过，ruff clean。

一个低严重程度 finding：`_eid_candidate_mismatch_reason` 中附件链路使用 `SchemaError` 而非 `MismatchError`，不影响 fallback 行为但错误类别语义不精确。
