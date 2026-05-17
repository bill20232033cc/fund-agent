# P1-S3 Code Review (GLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S3 两级缓存与仓库内解析物化
> 分支：`chore/reconcile-baseline`
> Review scope 裁决：`docs/reviews/p1-s3-baseline-reconciliation-2026-05-17.md`
> 已接受 plan：`docs/reviews/p1-plan-2026-05-17.md`
> 设计/总控真源：`docs/design.md`、`docs/implementation-control.md`

---

## 1. Review 结论

**PASS** — P1-S3 核心目标全部达成，无 blocking finding。

repository 通过缓存编排真正避免了重复下载与重复全文解析；parsed report 缓存留在 `documents` 层内部，未泄漏到上层或 `pdf/*`；`force_refresh` 正确绕过两级缓存；未提前冻结 `structured_data`；公开签名不变。

存在 3 项 non-blocking findings（1 medium / 1 low / 1 informational），均不影响当前 slice 正确性。

---

## 2. 审查范围

| 文件 | 状态 |
|------|------|
| `fund_agent/fund/documents/cache.py` | 新增 |
| `fund_agent/fund/documents/repository.py` | 修改 |
| `fund_agent/fund/documents/models.py` | 修改（增加序列化） |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | 修改（拆分方法） |
| `tests/fund/documents/test_cache.py` | 新增 |
| `tests/fund/documents/test_repository.py` | 扩展 |

---

## 3. 逐项合规核查

### 3.1 Repository 是否真的避免重复下载/重复解析

**缓存命中路径**（`force_refresh=False`）：

`repository.py:225-248` 的编排逻辑：

1. `:227-229`：先查 `load_parsed_report` 缓存 → 命中时直接返回，不触网、不解析。✅
2. `:231-233`：未命中时查 `get_pdf_path` → 命中时复用已记录的 PDF 路径。✅
3. `:234-240`：PDF 路径也未命中时才调用 `fetch_pdf_path` 下载。✅
4. `:242-247`：解析后回写 `save_parsed_report`。✅

**测试覆盖**：

- `test_repository_reuses_parsed_report_cache_without_reparsing`（:312-343）：首次加载后，第二次调用时 `fetch_pdf_path` 仅被调用一次（首次），`parse_pdf` 也仅被调用一次。✅
- `test_repository_reuses_cached_pdf_metadata_when_parsed_cache_missing`（:389-421）：仅预写 `documents` 表的 PDF 路径，不写 parsed report → 验证 `fetch_pdf_path` 不被调用，`parse_pdf` 被调用一次。✅

**判定**：重复加载确实避免了重复下载和重复解析。

### 3.2 Parsed report 缓存是否留在 documents 层内部

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `cache.py` 位于 `documents/` 内 | ✅ | `fund_agent/fund/documents/cache.py` |
| `cache.py` 无 `pdf/*` 引用 | ✅ | grep 确认无 `from fund_agent.fund.pdf` |
| SQLite 路径在 `cache/documents/` 下 | ✅ | `cache.py:18` `DOCUMENT_CACHE_ROOT = Path("cache/documents")` |
| JSON 物化在 `cache/documents/parsed_reports/` 下 | ✅ | `cache.py:19` + `:409` payload 路径 |
| 上层不直接访问 SQLite | ✅ | repository 仅通过 cache 对象的 async 方法交互 |

**判定**：缓存未泄漏到上层或 `pdf/*`。

### 3.3 force_refresh 是否正确绕过两级缓存

`repository.py:226-240`：

```python
if not force_refresh:
    cached_report = await self._cache.load_parsed_report(document_key)
    if cached_report is not None:
        return cached_report

pdf_path = None
if not force_refresh:
    pdf_path = await self._cache.get_pdf_path(document_key)
if pdf_path is None:
    pdf_path = await cache_aware_loader.fetch_pdf_path(...)
```

- `force_refresh=True`：跳过 `:227` 的 parsed report 读取和 `:232` 的 PDF 路径读取 → 强制走 `:235` 的下载。✅
- 解析完成后仍回写缓存（`:247`），这是正确行为——刷新后应更新缓存。✅

**测试覆盖**：

- `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report`（:346-386）：首次加载缓存后，`force_refresh=True` 时 `fetch_pdf_path.await_count == 2`、`parse_pdf.await_count == 2`，确认穿透。✅

**判定**：`force_refresh` 正确绕过两级缓存。

### 3.4 是否没有提前冻结 structured_data

| 检查项 | 结果 | 证据 |
|--------|------|------|
| cache.py 无 `structured_data` 表 | ✅ | SQLite schema 仅含 `documents` 和 `parsed_reports`（`:116-139`） |
| 代码注释明确标注不引入 | ✅ | `cache.py:3-4` "不提前引入 `structured_data`" |
| grep 确认无相关引用 | ✅ | 仅在注释中出现 |

**判定**：未提前冻结 `structured_data`。

### 3.5 是否没有改 repository 公开签名

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `load_annual_report(fund_code, year, *, force_refresh=False)` 签名不变 | ✅ | `repository.py:193-199` |
| 返回类型仍为 `ParsedAnnualReport` | ✅ | `repository.py:199` |
| 构造器签名 `__init__(annual_report_loader=None)` 不变 | ✅ | `repository.py:177` |
| 新增的 `_build_document_key` 是私有方法 | ✅ | `repository.py:250` |

**判定**：公开签名未改变。

### 3.6 cache.py/test_cache.py/test_repository.py 闭环

| 闭环环节 | 覆盖 |
|---------|------|
| documents + parsed_reports 表创建 | ✅ `test_cache_persists_pdf_metadata_and_parsed_report:77` |
| PDF 元信息写+读回 | ✅ `test_cache:62` |
| parsed report 写+读回（含 schema_version） | ✅ `test_cache:63,78` |
| payload 文件缺失时安全回退 None | ✅ `test_cache_returns_none_for_missing_or_stale_payload:99,126` |
| 缓存命中后不重复下载/解析 | ✅ `test_repository_reuses_parsed_report_cache:342-343` |
| force_refresh 穿透两级缓存 | ✅ `test_repository_force_refresh:383-384` |
| parsed report 缺失时复用 PDF 路径 | ✅ `test_repository_reuses_cached_pdf_metadata:420-421` |
| 非缓存感知 loader 走原始直接委派路径 | ✅ `test_repository_returns_parsed_annual_report_without_path_exposure:55-57` |

**判定**：形成了可重复的最小闭环。

---

## 4. Findings

### 4.1 F1-未修复-Medium-缓存 initialize 在每次读操作中重复执行

**文件与行号**：`fund_agent/fund/documents/cache.py:155, 201, 258, 315`

**直接证据**：

每个公开 async 方法都以 `await self.initialize()` 开头：

```python
async def get_pdf_path(self, key: DocumentKey) -> Path | None:
    await self.initialize()                    # :155
    return await asyncio.to_thread(...)

async def record_pdf_path(self, key: DocumentKey, pdf_path: Path) -> None:
    await self.initialize()                    # :201
    ...

async def load_parsed_report(self, key: DocumentKey) -> ParsedAnnualReport | None:
    await self.initialize()                    # :258
    ...

async def save_parsed_report(self, report: ParsedAnnualReport, ...) -> None:
    await self.initialize()                    # :315
    ...
```

`initialize()` 内部执行 `_initialize_sync()`，每次都会：
- `mkdir(parents=True, exist_ok=True)` × 2（目录操作，幂等但仍有系统调用开销）
- `sqlite3.connect()` + `CREATE TABLE IF NOT EXISTS` × 2（SQLite 连接 + DDL 检查）

在 repository 的一次 `load_annual_report` 调用中，缓存路径会依次触发 `load_parsed_report` → `get_pdf_path` → `record_pdf_path` / `save_parsed_report`，每次都会 `initialize()`。

**影响**：
- 当前 MVP 场景下不会造成可见性能问题（SQLite 连接轻量，DDL 幂等）。
- 但在并发或高频调用场景下（如 P1-S8 批量处理 3 只基金 × 12 项提取），不必要的重复初始化会累积为可感知的开销。
- 每次 `sqlite3.connect()` 创建新连接而非复用，也意味着 SQLite 的 WAL 锁和事务隔离模式未被利用。

**建议改法**：
- 引入 `self._initialized: bool` 标志位，`initialize()` 首次执行后设为 `True`，后续调用直接返回。
- 或将 SQLite 连接提升为实例级长期连接（`self._connection`），在 `__init__` 时创建。

**验证点**：
- 并发调用 `load_parsed_report` 和 `save_parsed_report` 不应触发竞态。
- 缓存初始化只执行一次的断言测试。

---

### 4.2 F2-未修复-Low-AnnualReportLoader Protocol 从公开降为私有后导出未同步

**文件与行号**：`fund_agent/fund/documents/repository.py:18`、`fund_agent/fund/documents/__init__.py`

**直接证据**：

P1-S1 初审时 `repository.py` 定义了公开 `AnnualReportLoader` Protocol，P1-S3 将其重命名为 `_AnnualReportLoader`（私有），并新增 `_CacheAwareAnnualReportLoader`（私有）。

`documents/__init__.py` 当前导出列表为：
```python
__all__ = [
    "DocumentKey",
    "ParsedAnnualReport",
    "ParsedTable",
    "ReportSection",
    "FundDocumentRepository",
]
```

`AnnualReportLoader` 从未在 `__all__` 中出现过（P1-S1 时也没有），而 `__init__.py` 也没有 import 它。当前外部代码如果需要实现自定义 loader（如测试），只能通过 import `repository._AnnualReportLoader`，这暴露了内部路径。

**影响**：低。自定义 loader 场景有限，且 adapter 直接提供了默认实现。但 Protocol 作为契约接口，其可发现性对后续扩展者有价值。

**建议改法**：
- 在 `__init__.py` 中导出 `_CacheAwareAnnualReportLoader` 的公开别名（如 `AnnualReportLoader`），或将 Protocol 重命名回公开名。
- 或保持现状但在 README 中说明自定义 loader 的接入方式。

**验证点**：
- `from fund_agent.fund.documents import FundDocumentRepository` 后，用户能找到 Protocol 定义。

---

### 4.3 F3-未修复-Informational-ParsedAnnualReport.from_dict 反序列化不校验 schema_version

**文件与行号**：`fund_agent/fund/documents/cache.py:288-293`、`fund_agent/fund/documents/models.py:238-266`

**直接证据**：

`cache.py:288-293`：
```python
if schema_version != PARSED_REPORT_SCHEMA_VERSION:
    return None
payload = json.loads(payload_path.read_text(encoding="utf-8"))
return ParsedAnnualReport.from_dict(payload)
```

缓存层在读取 JSON 前检查了 `schema_version`，这是正确的。但 `ParsedAnnualReport.from_dict()` 本身不感知 schema version——它只是从 dict 反序列化。如果未来 schema 升级但 `from_dict` 被其他调用方直接使用（绕过 cache 层），不会有版本保护。

**影响**：极低。当前所有反序列化都通过 cache 层，cache 层已做了版本检查。`from_dict` 的调用方只有 cache。

**建议改法**：
- 当前可接受。若后续 `from_dict` 被更多场景使用，可在 payload 中嵌入 `_schema_version` 字段并在 `from_dict` 内校验。

**验证点**：
- 无需立即行动。

---

## 5. 附带变更复核

P1-S3 引入了超出纯缓存的附带变更，逐项确认不引入新风险：

| 附带变更 | 判定 | 理由 |
|---------|------|------|
| `models.py` 增加 `to_dict()` / `from_dict()` 序列化方法 | ✅ 无风险 | 必要支撑，所有字段显式映射，反序列化有类型转换 |
| `annual_report_pdf.py` 拆分 `fetch_pdf_path()` + `parse_pdf()` | ✅ 无风险 | 原有 `load_annual_report()` 保留并委托到两个新方法，公开行为不变 |
| `repository.py` 新增 `_CacheAwareAnnualReportLoader` Protocol | ✅ 无风险 | 用 `getattr` + `iscoroutinefunction` 做鸭子类型判断，非缓存感知 loader 走原有路径 |
| `repository.py` Protocol 重命名为 `_AnnualReportLoader` | ✅ 无风险 | 仅限内部使用，不影响上层 |

---

## 6. 残余风险

| ID | 风险 | 影响范围 | 建议处理时机 |
|----|------|---------|-------------|
| RR-S3-1 | 缓存根目录仍使用相对路径 CWD | 跨目录调用时缓存可能分散 | P1-S8 统一根路径策略时一并裁决 |
| RR-S3-2 | SQLite 连接未复用，每次操作新建连接 | 并发场景下有潜在性能开销 | P1-S8 或后续性能优化时处理 |
| RR-S3-3 | payload 文件无校验和，意外篡改不会被发现 | 数据完整性 | 后续 phase 视需求引入 |

---

## 7. 汇总

| Finding 编号 | 严重程度 | Blocking? | 建议处理 |
|-------------|---------|-----------|---------|
| F1 | Medium | 否 | P1-S8 或性能优化时引入初始化标志位 |
| F2 | Low | 否 | 可选：导出 Protocol 或更新 README |
| F3 | Informational | 否 | 记录为已知 risk |

**总 findings 数量**：3（0 blocking / 1 medium / 1 low / 1 informational）
**Blocking accepted candidate**：无
**Artifact path**：`docs/reviews/p1-s3-code-review-glm-2026-05-17.md`
