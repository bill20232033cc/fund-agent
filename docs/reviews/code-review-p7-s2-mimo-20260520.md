# Code Review — P7-S2 Source Abstraction

## Scope

- Mode: current changes
- Branch: main (unstaged workspace changes)
- Base: main
- Output file: `docs/reviews/code-review-p7-s2-mimo-20260520.md`
- Included scope: P7-S2 annual-report source abstraction
  - `fund_agent/fund/documents/sources.py` — source protocol, orchestrator, errors, Eastmoney wrapper (new)
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py` — constructor updated to source orchestrator
  - `tests/fund/documents/test_annual_report_sources.py` — orchestrator/source tests (new)
  - `tests/fund/documents/test_repository.py` — updated for orchestrator injection
  - `fund_agent/fund/README.md` — source abstraction docs
  - `tests/README.md` — test coverage docs
- Excluded scope: EID client, Service/UI/Engine/CLI, extraction, audit, quality gate, template renderer, PDF parser, cache schema
- Parallel review coverage: 无

## Findings

### 1-未修复-中-`AnnualReportSourceOrchestrator(())` 静默回退到 Eastmoney

- **入口/函数**: `AnnualReportSourceOrchestrator.__init__`
- **文件(行号)**: `sources.py:315-317`
- **输入场景**: 调用方显式传入空元组 `sources=()`
- **实际分支**: `self.sources = sources or (EastmoneyAnnualReportSource(),)` — 空元组 `()` 在 Python 中为 falsy，`or` 表达式取右侧默认值
- **预期行为**: 空元组应触发 `ValueError("sources 不能为空")`，因为调用方明确表示"没有可用来源"
- **实际行为**: 空元组被静默替换为 `(EastmoneyAnnualReportSource(),)`，`if not self.sources:` 检查成为死代码
- **直接证据**: 运行 `AnnualReportSourceOrchestrator(())` → `sources[0].name == "eastmoney"`，无异常抛出
- **影响**: 违反 fail-closed 原则。调用方传入空元组意图禁用来源或表达配置错误，但系统静默回退到 Eastmoney，可能掩盖配置问题
- **建议改法和验证点**:
  ```python
  # 修改 line 315-317 为：
  self.sources = sources if sources is not None else (EastmoneyAnnualReportSource(),)
  if not self.sources:
      raise ValueError("sources 不能为空")
  ```
  验证：`AnnualReportSourceOrchestrator(())` 应抛出 `ValueError`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-低-Eastmoney 来源缺少 `FileNotFoundError` 映射测试

- **入口/函数**: `EastmoneyAnnualReportSource.fetch_annual_report_pdf`
- **文件(行号)**: `sources.py:276-277`
- **输入场景**: 底层 downloader 抛出 `FileNotFoundError`
- **实际分支**: `except FileNotFoundError as exc: raise AnnualReportSourceNotFoundError(str(exc)) from exc`
- **预期行为**: `FileNotFoundError` 应被映射为 `AnnualReportSourceNotFoundError`
- **实际行为**: 代码逻辑正确，但无测试覆盖此路径
- **直接证据**: `test_annual_report_sources.py` 只有 `test_eastmoney_source_maps_http_error_to_unavailable`（测试 `httpx.TimeoutException`），无 `FileNotFoundError` 映射测试
- **影响**: 回归风险。如果此映射被意外删除，Eastmoney 的 not-found 会被当作未捕获异常传播，而非触发 fallback
- **建议改法和验证点**: 添加测试：downloader 抛出 `FileNotFoundError("未找到")`，断言 `AnnualReportSourceNotFoundError` 被抛出
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-低-单个不可用来源的聚合路径未被测试覆盖

- **入口/函数**: `_raise_exhausted_sources`
- **文件(行号)**: `sources.py:448-449`
- **输入场景**: 恰好一个来源失败且为 unavailable
- **实际分支**: `if categories == {"unavailable"} and len(failures) == 1: raise AnnualReportSourceUnavailableError(message)`
- **预期行为**: 单个 unavailable 应抛出 `AnnualReportSourceUnavailableError`，而非 `AnnualReportSourceAggregateError`
- **实际行为**: 代码逻辑正确，但测试 7（`test_orchestrator_unavailable_exhaustion_is_not_file_not_found`）使用两个不可用来源，走的是 `AnnualReportSourceAggregateError` 路径
- **直接证据**: line 448-449 的 `len(failures) == 1` 分支无测试覆盖
- **影响**: 低。两个不可用来源的测试已覆盖聚合路径，单来源路径逻辑简单
- **建议改法和验证点**: 添加单来源不可用测试，断言抛出 `AnnualReportSourceUnavailableError`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。

## Detailed Review Evidence

### 1. Protocol and model boundary

- `AnnualReportSource` Protocol 定义在 `sources.py:192-222`，包含 `name` 属性和 `fetch_annual_report_pdf` 方法
- 错误类层次结构：`AnnualReportSourceUnavailableError(Exception)`、`AnnualReportSourceNotFoundError(FileNotFoundError)`、`AnnualReportSourceMismatchError(ValueError)`、`AnnualReportSourceSchemaError(ValueError)`、`AnnualReportSourceAggregateError(Exception)`
- `AnnualReportSourceAggregateError.__init__` 在 `failures` 为空时抛出 `ValueError` (line 119-120)
- 所有 dataclass 均 `frozen=True, slots=True`
- **Pass.**

### 2. Orchestrator fallback semantics

- `fetch_annual_report_pdf` (lines 320-364): 遍历 sources，`AnnualReportSourceNotFoundError` 和 `AnnualReportSourceUnavailableError` 触发 continue，`AnnualReportSourceMismatchError` 和 `AnnualReportSourceSchemaError` 立即 raise
- `_mark_fallback_used` (line 408-421): 使用 `dataclasses.replace` 标记 `fallback_used=True`
- `_raise_exhausted_sources` (lines 424-450): 全部 not-found → `AnnualReportSourceNotFoundError`；单 unavailable → `AnnualReportSourceUnavailableError`；其他 → `AnnualReportSourceAggregateError`
- **Pass.**

### 3. Eastmoney wrapper

- `EastmoneyAnnualReportSource` (lines 225-287): 包装 `_download_annual_report_pdf`
- `FileNotFoundError` → `AnnualReportSourceNotFoundError` (line 276-277)
- `httpx.HTTPError` → `AnnualReportSourceUnavailableError` (line 278-279)
- 返回 `AnnualReportSourceResult` 带 metadata (lines 280-287)
- **Pass.**

### 4. Adapter changes

- `AnnualReportPdfAdapter.__init__` (lines 174-199): 接收 `source_orchestrator: AnnualReportSourceOrchestrator | None = None`
- `fetch_pdf_path` (lines 201-228): 调用 `self._source_orchestrator.fetch_annual_report_pdf(...)`，返回 `result.pdf_path`
- `parse_pdf` 和 `load_annual_report` 不变
- **Pass.**

### 5. Repository behavior preserved

- `test_repository_returns_parsed_annual_report_without_path_exposure`: 验证 `source_orchestrator` 注入
- `test_repository_reuses_parsed_report_cache_without_reparsing`: 缓存命中不调用 source
- `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report`: force_refresh 穿透缓存
- **Pass.**

### 6. Scope compliance

- 无 Service/UI/Engine/CLI 文件变更
- 无 `extra_payload` 引用
- 无 source imports 泄漏到 `fund_agent/fund/documents/` 外部
- 无 PDF parser 行为变更
- 无 cache schema 变更
- **Pass.**

### 7. Test coverage vs plan

| Plan test | Implementation | Pass? |
|---|---|---|
| 1. orchestrator returns first successful source | `test_orchestrator_returns_first_successful_source` | Yes |
| 2. falls back after unavailable | `test_orchestrator_falls_back_after_unavailable_error` | Yes |
| 3. falls back after not-found | `test_orchestrator_falls_back_after_not_found_error` | Yes |
| 4. stops on mismatch | `test_orchestrator_stops_on_mismatch_error` | Yes |
| 5. stops on schema error | `test_orchestrator_stops_on_schema_error` | Yes |
| 6. all not-found → FileNotFoundError | `test_orchestrator_raises_file_not_found_when_all_sources_are_not_found` | Yes |
| 7. unavailable exhaustion ≠ FileNotFoundError | `test_orchestrator_unavailable_exhaustion_is_not_file_not_found` | Yes |
| 8. mixed preserves unavailable | `test_orchestrator_mixed_not_found_and_unavailable_preserves_unavailable_category` | Yes |
| 9. force_refresh passed to source | `test_orchestrator_passes_force_refresh_to_source` | Yes |
| 10. adapter uses orchestrator | `test_annual_report_pdf_adapter_fetch_pdf_path_uses_source_orchestrator` | Yes |
| 11. cache hit skips source | `test_repository_reuses_parsed_report_cache_without_reparsing` | Yes |
| 12. force_refresh bypasses cache | `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report` | Yes |

12/12 plan tests present. Additional: `test_eastmoney_source_maps_http_error_to_unavailable`.

257/257 full suite passes, ruff clean.

## Residual Risk

- `httpx.HTTPError` catch at `sources.py:278` is broad — covers both transport errors and HTTP status errors (e.g., 404). If downloader passes through a 404 as `httpx.HTTPStatusError`, it would be mapped to "unavailable" rather than "not_found". Low risk because `_download_annual_report_pdf` handles fund-not-found via `FileNotFoundError` internally.
- `AnnualReportSourceConfig` is defined but not consumed by any source in P7-S2. Config fields (timeout, retry, concurrency) are dead code until P7-S3 EID source.
- `_download_annual_report_pdf` import at `sources.py:16` uses private-name import (`_download_annual_report_pdf`). Acceptable for internal module coupling, but means the downloader's public surface is explicitly not a stable API.

## Conclusion

PASS with one medium finding.

P7-S2 correctly introduces the source protocol, orchestrator, error hierarchy, and Eastmoney wrapper. The adapter cleanly delegates to the orchestrator. Repository behavior is preserved. No scope leaks. 257/257 tests pass, ruff clean.

One medium-severity finding: `AnnualReportSourceOrchestrator(())` silently defaults to Eastmoney because empty tuple is falsy in Python. The `sources or (EastmoneyAnnualReportSource(),)` expression at `sources.py:315` bypasses the `ValueError` guard at line 316-317. Fix: use explicit `if sources is None` check. Two low-severity test gaps: no `FileNotFoundError` mapping test for Eastmoney source, no single-unavailable-source test.
