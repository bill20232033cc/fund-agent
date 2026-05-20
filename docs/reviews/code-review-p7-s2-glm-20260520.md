# Code Review

## Scope

- Mode: current changes
- Branch: main
- Base: main
- Output file: `docs/reviews/code-review-p7-s2-glm-20260520.md`
- Included scope: P7-S2 document repository source abstraction — `fund_agent/fund/documents/sources.py` (new), `fund_agent/fund/documents/adapters/annual_report_pdf.py`, `tests/fund/documents/test_annual_report_sources.py` (new), `tests/fund/documents/test_repository.py`, `fund_agent/fund/README.md`, `tests/README.md`
- Excluded scope: Service/UI/Engine/CLI, cache schema changes, models.py, pdf/downloader.py, parser behavior, EID client, audit, quality gate, template, extraction, fund type
- Parallel review coverage: 无，单 reviewer 全量走读

## Findings

### P7S2-001-未修复-[中]-空元组静默回退到 Eastmoney 默认来源

- **入口/函数**: `AnnualReportSourceOrchestrator.__init__`
- **文件(行号)**: `sources.py:315-317`
- **输入场景**: `AnnualReportSourceOrchestrator(sources=())`
- **实际分支**: `sources or (EastmoneyAnnualReportSource(),)` — 空元组为 falsy，`or` 短路求值为默认值
- **预期行为**: docstring 声明 `ValueError: 来源列表为空时抛出`；显式传入空来源应被拒绝
- **实际行为**: 静默替换为 Eastmoney 默认来源，无任何错误或警告
- **直接证据**: 第 315 行 `self.sources = sources or (EastmoneyAnnualReportSource(),)` 对 `()` 和 `None` 不可区分；第 316 行 `if not self.sources: raise ValueError("sources 不能为空")` 为死代码，永远不可达
- **影响**: 调用方显式请求"无来源"时得到静默默认而非明确错误；docstring 合同被违反；死代码让维护者误以为空列表会被拒绝
- **建议改法和验证点**: 改为显式 `None` 检查：`if sources is None: sources = (EastmoneyAnnualReportSource(),)`，然后 `if not sources: raise ValueError(...)`。补充一个 `test_orchestrator_rejects_empty_sources_tuple` 测试断言 `ValueError`。验证已有测试不受影响。
- **修复风险（低）**: 单行逻辑改动，不影响 `None` 默认路径和显式非空 tuple 路径
- **严重程度（中）**: orchestrator 是内部 API，生产代码只传 `None` 或显式非空 tuple，但 docstring 合同与实际行为不一致且存在死代码

## Architecture Boundary Review

Pass. `sources.py` 只被 `annual_report_pdf.py`（同层 `documents/` 内部）和测试文件导入。Service/UI/CLI/audit/template/quality_gate 均未导入 `documents.sources`。`FundDocumentRepository.load_annual_report(...)` 公共签名未改变。

## Dependency Direction

```text
FundDocumentRepository → AnnualReportPdfAdapter → AnnualReportSourceOrchestrator → AnnualReportSource implementations
                                                                → fund_agent.fund.pdf.downloader (Eastmoney helper)
```

`sources.py` 导入 `httpx` 用于 `EastmoneyAnnualReportSource` 的异常映射。模块级 import 合理（Eastmoney 是生产默认来源），但意味着即使只使用 EID 来源也需要 httpx 安装。P7-S3 后若 EID 成为主源可考虑将 Eastmoney wrapper 移出 `sources.py` 以消除该依赖。不作为 finding 报告。

## Fallback Error Semantics

| 场景 | 行为 | 测试覆盖 |
|---|---|---|
| Primary 成功 | 返回结果，fallback 不调用 | ✅ |
| Primary unavailable → fallback 成功 | 返回结果，`fallback_used=True` | ✅ |
| Primary not-found → fallback 成功 | 返回结果，`fallback_used=True` | ✅ |
| Primary mismatch | 立即 raise，fallback 不调用 | ✅ |
| Primary schema error | 立即 raise，fallback 不调用 | ✅ |
| 全部 not-found | `AnnualReportSourceNotFoundError` (FileNotFoundError 子类) | ✅ |
| 全部 unavailable (多源) | `AnnualReportSourceAggregateError` (非 FileNotFoundError) | ✅ |
| 混合 not-found + unavailable | `AnnualReportSourceAggregateError`，保留两类 category | ✅ |
| 单源 unavailable | `AnnualReportSourceUnavailableError`（非 Aggregate） | ✅（`_raise_exhausted_sources:448` 单一 unavailable 分支） |
| `force_refresh=True` | 显式传递到 source | ✅ |
| Eastmoney `httpx.HTTPError` | 映射为 `AnnualReportSourceUnavailableError` | ✅ |
| Eastmoney `FileNotFoundError` | 映射为 `AnnualReportSourceNotFoundError` | ✅ |

Plan 要求的 12 条测试全部覆盖（11 条在 `test_annual_report_sources.py`，cache 相关 2 条在 `test_repository.py`）。

## Cache / force_refresh Behavior

- `AnnualReportPdfAdapter.fetch_pdf_path` 正确传递 `force_refresh` 到 orchestrator。 ✅
- `FundDocumentRepository.load_annual_report` 缓存行为未改变：parsed report cache 命中不调用 source；`force_refresh=True` 穿透 parsed report 和 PDF path 缓存。 ✅
- Cache schema 未修改。 ✅
- `test_repository_reuses_parsed_report_cache_without_reparsing` 和 `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report` 验证完整。 ✅

## Scope Compliance

- `FundDocumentRepository.load_annual_report(...)` 签名未改变。 ✅
- `pdf/downloader.py` 行为未改变。 ✅
- `models.py` / `cache.py` 未改变。 ✅
- Service/UI/Engine/CLI 未修改。 ✅
- 无 `extra_payload` 使用。 ✅
- 无 EID 端点实现。 ✅
- 无 real network 测试。 ✅
- 无 parser 行为变化。 ✅
- 无控制文档修改。 ✅

## Open Questions

- 无

## Residual Risk

- `sources.py` 模块级 `import httpx` 意味着所有 source 消费者（包括未来 EID-only 路径）需要 httpx 安装。P7-S3+ 可评估将 `EastmoneyAnnualReportSource` 移至独立 adapter 文件。
- `AnnualReportSourceConfig` 已定义但 P7-S2 未消费。这是计划内的（P7-S3 EID 客户端消费）。
- `_raise_exhausted_sources` 返回类型标注为 `AnnualReportSourceResult` 但实际总是 raise。这是类型收窄技巧（让调用点 `return _raise_exhausted_sources(...)` 通过类型检查），合理但可考虑 `NoReturn` 标注。
