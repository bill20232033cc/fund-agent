# P1-S3 Code Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> Branch：`chore/reconcile-baseline`
> Target：P1-S3 两级缓存与仓库内解析物化
> Scope：仅 review 当前 worktree 中属于 P1-S3 的文件

## 审查输入

- Baseline：`docs/reviews/p1-s3-baseline-reconciliation-2026-05-17.md`
- Implementation：`docs/reviews/p1-s3-implementation-2026-05-17.md`
- Plan：`docs/reviews/p1-plan-2026-05-17.md`
- 设计真源：`docs/design.md`

## 审查范围

| 文件 | 类型 | 变更摘要 |
|------|------|----------|
| `fund_agent/fund/documents/cache.py` | 新增 | `AnnualReportDocumentCache`，SQLite + JSON 物化 |
| `fund_agent/fund/documents/repository.py` | 修改 | 接入缓存编排，保持公开签名不变 |
| `fund_agent/fund/documents/models.py` | 修改 | 增加 `to_dict()` / `from_dict()` 序列化 |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | 修改 | 拆分 `fetch_pdf_path()` / `parse_pdf()` |
| `tests/fund/documents/test_cache.py` | 新增 | 缓存层单元测试（2 条） |
| `tests/fund/documents/test_repository.py` | 扩展 | 新增缓存行为测试（+3 条） |

**排除确认**：无 parser.py / extractor / cache 层外 / 上层目录文件变更。`structured_data` 未出现（仅 `cache.py` docstring 提及"不提前引入"）。

## Review Checklist 逐项审查

### 1. repository 是否真的避免重复下载/重复解析

**结论：是。**

- `test_repository_reuses_parsed_report_cache_without_reparsing`（test_repository.py:311-343）：调用两次 `load_annual_report("110011", 2024)`，断言 `loader.fetch_pdf_path` 和 `loader.parse_pdf` 各仅 awaited 一次。第二次调用命中 parsed report 缓存，跳过下载和解析。
- `test_repository_reuses_cached_pdf_metadata_when_parsed_cache_missing`（test_repository.py:389-421）：当 parsed report 缓存缺失但 PDF 路径已记录时，`loader.fetch_pdf_path.assert_not_awaited()` — 复用已缓存的 PDF 路径，仅重新解析。
- 仓库逻辑（repository.py:226-248）：优先级为 parsed report 缓存 > PDF 路径缓存 > 下载，逐级穿透。

### 2. parsed report 缓存是否仍留在 documents 层内部

**结论：是。**

- `cache.py` 位于 `fund_agent/fund/documents/cache.py`，仅被 `repository.py` 内部 import。
- `documents/__init__.py` 不 re-export `AnnualReportDocumentCache`，`__all__` 只含模型和 `FundDocumentRepository`。
- `cache.py` 模块级 docstring 明确标注"只服务 documents 层内部"。
- 无 extractor / 上层目录 import `cache.py`。

### 3. force_refresh 是否正确绕过 parsed report 与已记录 PDF 路径

**结论：是。**

- repository.py:226-240 逻辑：
  - `force_refresh=True` 时跳过 `load_parsed_report()` 和 `get_pdf_path()`，直接调用 `fetch_pdf_path(force_refresh=True)` + `parse_pdf()` + `save_parsed_report()`。
- `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report`（test_repository.py:346-386）：先加载一次写入缓存，再 `force_refresh=True` 加载，断言：
  - `loader.fetch_pdf_path.await_count == 2`
  - `loader.parse_pdf.await_count == 2`
  - `loader.fetch_pdf_path.assert_any_await("110011", 2024, force_refresh=True)`
  - 返回 `fresh_report` 而非 `stale_report`。

### 4. 是否没有提前冻结 structured_data

**结论：是。**

- `grep -rn "structured_data" fund_agent/fund/documents/` 仅命中 `cache.py` docstring 中的"不提前引入"声明。
- SQLite schema 只含 `documents` 和 `parsed_reports` 两张表（cache.py:116-139），无 `structured_data`。
- `test_cache_persists_pdf_metadata_and_parsed_report` 断言 `tables == {"documents", "parsed_reports"}`。

### 5. 是否没有改 repository 公开签名

**结论：是。**

- `load_annual_report(fund_code: str, year: int, *, force_refresh: bool = False) -> ParsedAnnualReport` — 签名未变。
- 内部新增 `_CacheAwareAnnualReportLoader` Protocol 和 `_get_cache_aware_loader()` 检测加载器是否支持缓存编排；对不支持的自定义 loader（如旧测试中的 Mock），继续走原有直接委派路径（repository.py:218-223），向后兼容。
- `__init__.py` 的 `__all__` 未变（除新增 `ANNUAL_REPORT_DOCUMENT_KIND` 常量外）。

### 6. cache.py/test_cache.py/test_repository.py 是否形成可重复的最小闭环

**结论：是。**

- `test_cache.py`（2 条）：
  - `test_cache_persists_pdf_metadata_and_parsed_report`：验证写入→读回 PDF 元信息 + parsed report + SQLite schema + schema_version。
  - `test_cache_returns_none_for_missing_or_stale_payload`：验证 payload 文件缺失时安全回退为缓存未命中。
- `test_repository.py`（8 条，其中 3 条为 P1-S3 新增）：
  - 缓存命中复用：`test_repository_reuses_parsed_report_cache_without_reparsing`
  - force_refresh 穿透：`test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report`
  - PDF 路径复用：`test_repository_reuses_cached_pdf_metadata_when_parsed_cache_missing`
- 测试结果：10 passed in 0.80s。
- 覆盖了"首次加载写缓存→重复加载命中→force_refresh 穿透→PDF 路径复用→payload 缺失回退"完整链路。

## Findings

### 1-未修复-低-`_create_default_cache()` 每次构造新实例无复用

- **文件(行号)**：`fund_agent/fund/documents/repository.py:130-143`
- **直接证据**：`_create_default_cache()` 每次返回 `AnnualReportDocumentCache()` 新实例。`FundDocumentRepository.__init__` 在 line 191 调用它。若同一进程创建多个 repository 实例，每个都会持有独立的缓存实例（各自持有一个 SQLite 连接路径）。
- **影响**：多 repository 实例场景下可能产生多份缓存目录初始化调用，但由于 `CREATE TABLE IF NOT EXISTS` 幂等，不会导致数据错误。当前 P1 单仓库实例场景无实际影响。
- **建议改法**：后续可在模块级或依赖注入层做缓存单例，但 P1-S3 不需要。
- **验证点**：N/A — 不阻塞当前 slice。
- **严重程度**：低 — 当前无实际触发路径。

### 2-未修复-低-`initialize()` 在每次缓存操作时重复调用

- **文件(行号)**：`fund_agent/fund/documents/cache.py:155`（`get_pdf_path`）、`201`（`record_pdf_path`）、`258`（`load_parsed_report`）、`315`（`save_parsed_report`）
- **直接证据**：每个 public async 方法都以 `await self.initialize()` 开头。`initialize()` 内部 `_initialize_sync()` 做 `mkdir` + `CREATE TABLE IF NOT EXISTS` + `commit`。
- **影响**：每次缓存操作多一次 SQLite 连接 + mkdir 系统调用。由于操作幂等，不影响正确性，仅增加微量开销。P1-S3 不要求缓存性能优化。
- **建议改法**：后续可用 `_initialized: bool` flag 做一次性初始化，或在 `__init__` 中同步初始化。P1-S3 不需要。
- **验证点**：N/A — 不阻塞当前 slice。
- **严重程度**：低 — 幂等操作，无正确性风险。

## AGENTS.md 边界检查

| 约束 | 状态 | 备注 |
|---|---|---|
| 中文 docstring | ✓ | cache.py、repository.py、models.py、adapter 所有函数均有完整中文 docstring |
| 基金文档只通过统一仓库接口访问 | ✓ | `FundDocumentRepository.load_annual_report` 是唯一入口 |
| 不提前冻结 structured_data | ✓ | SQLite 只含 documents + parsed_reports |
| 不暴露 SQLite 给上层 | ✓ | `AnnualReportDocumentCache` 不在 `__init__.py` 的 `__all__` 中 |
| 测试覆盖率 | ✓ | 10 条测试覆盖缓存读写、缓存命中、穿透、回退 |

## P1-S3 计划符合性检查

| 完成信号 | 状态 | 证据 |
|---|---|---|
| raw PDF 元信息缓存 + parsed report 物化缓存位于 documents 层内部 | ✓ | `cache.py` 在 `documents/` 下，`__init__.py` 不 re-export |
| 仓库优先命中缓存，不重复下载/不重复全文解析 | ✓ | `test_repository_reuses_parsed_report_cache_without_reparsing` 验证 |
| `force_refresh=True` 穿透缓存 | ✓ | `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report` 验证 |
| parsed report 缓存缺失时复用已记录 PDF 路径 | ✓ | `test_repository_reuses_cached_pdf_metadata_when_parsed_cache_missing` 验证 |
| `structured_data` 未在本 slice 冻结 | ✓ | grep 无实际表/schema 命中 |
| 公开签名不变 | ✓ | `load_annual_report` 签名未变 |
| `test_cache.py` 存在且通过 | ✓ | 2 passed |

## Residual Risk

1. **JSON 物化无校验和**：当前 parsed report 物化为 JSON 文件，无 checksum 校验。若文件被外部篡改，`from_dict()` 可能产生错误对象。P1-S3 不要求此能力。
2. **缓存根目录仍为相对路径**：`DOCUMENT_CACHE_ROOT = Path("cache/documents")` 依赖 CWD，已在 P1-S1 deferred（D2），归属 P1-S3 后续统一裁决。
3. **schema_version 升级策略**：当前 `PARSED_REPORT_SCHEMA_VERSION = 1`，版本不匹配时静默返回 `None` 触发重新解析。后续 schema 变更时需考虑迁移或批量失效策略。

## 结论

**结论：pass，无 blocking finding。**

P1-S3 的核心目标（parsed report 物化缓存、避免重复下载/解析、force_refresh 穿透、不提前冻结 structured_data）全部达成。实现质量良好：缓存层收口在 documents 内部、仓库通过 Protocol 检测实现向后兼容、10 条测试覆盖了完整的缓存行为链路。

2 个低严重程度 finding（缓存实例复用、initialize 重复调用），均不影响正确性，不阻塞 gate。
