# Code Review

## Scope

- Mode: current changes
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-review-glm-20260527.md`
- Included scope:
  - `fund_agent/fund/documents/models.py` — `AnnualReportSourceFailureCategory` 类型搬迁、`primary_failure_category` 字段、序列化/反序列化
  - `fund_agent/fund/documents/sources.py` — `_mark_fallback_used()` 分类传播、import 重定向
  - `fund_agent/fund/source_provenance.py` — `effective_category` 元数据优先投影
  - `fund_agent/fund/data_extractor.py` — 生产路径 `project_public_source_provenance(report.metadata.source)` 调用点
  - `fund_agent/fund/documents/cache.py` — 元数据 JSON 持久化/反序列化路径
  - `tests/fund/test_source_provenance.py` — 新增 metadata-owned eligible/fail-closed、优先级、kwarg 兼容测试
  - `tests/fund/documents/test_cache.py` — 新增往返、legacy/unknown 降级、类型独立导出测试
  - `tests/fund/documents/test_annual_report_sources.py` — 已有 fallback 测试补充分类断言
  - `tests/fund/documents/test_repository.py` — 已有 fallback 元数据测试补充分类断言
  - `tests/fund/test_data_extractor.py` — 新增生产 extractor 投影 metadata 分类测试
  - `tests/fund/test_extraction_snapshot.py` — 更新已有 snapshot 测试匹配新 `complete`/`eligible` 状态
  - `docs/design.md` — provenance 契约段更新
  - `fund_agent/fund/README.md` — provenance 字段段更新
  - `tests/README.md` — 测试描述更新
- Excluded scope: `docs/implementation-control.md`（worker 不更新）、score/quality/renderer/default 行为代码（未变更）、未跟踪文件
- Parallel review coverage: 无；所有变更在 12 个文件内，scope 适中，主 reviewer 全量走读

## Findings

未发现实质性问题。

### 逐项 adversarial 走读结论

**1. Projection kwarg fallback 能否泄漏到生产路径或掩盖 metadata 分类？**

- **生产调用点** `data_extractor.py:210`：`project_public_source_provenance(report.metadata.source)` 不传 kwarg，kwarg 默认 `None`。
- **优先级逻辑** `source_provenance.py:139-143`：`effective_category` 优先取 `source_metadata.primary_failure_category`，仅在 metadata 为 `None` 时回退到 kwarg。
- **测试覆盖** `test_source_provenance.py`：
  - `test_metadata_failure_category_wins_over_keyword_override` — metadata 含 `schema_drift`（fail-closed），kwarg 传 `not_found`（eligible），结果正确取 metadata `fail_closed`。
  - `test_keyword_failure_category_still_applies_when_metadata_category_missing` — metadata 无分类，kwarg 传 `unavailable`，结果正确使用 kwarg `eligible`。
- **结论**：kwarg 无法覆盖或掩盖 metadata 分类。生产路径不传 kwarg，不存在泄漏风险。

**2. First failure vs primary failure 在 orchestrator 中的行为；fail-closed fallback 是否仍被阻断？**

- **`failures[0].category` 语义** `sources.py:654-658`：orchestrator 按 `self.sources` 顺序尝试，primary source 排第一。`failures` 列表按失败顺序追加，`failures[0]` 即 primary source 的失败类别。当前 2-source 模型（EID → Eastmoney）下语义正确。
- **fail-closed 阻断路径** `sources.py:642-653`：`identity_mismatch`、`schema_drift`、`integrity_error` 均直接调用 `_raise_fallback_blocked()` 抛出异常，不进入 `if failures:` 分支，不调用 `_mark_fallback_used()`。
- **`_can_fallback_after_failure` 仍只允许 `not_found`/`unavailable`** `sources.py:685-698`：`_FALLBACK_ELIGIBLE_CATEGORIES` 未变更。
- **`if failures:` 守卫** `sources.py:654`：保证 `failures` 非空时才访问 `failures[0]`，且此时 primary 必然已失败、fallback 已成功。
- **测试覆盖** `test_annual_report_sources.py`：`test_orchestrator_falls_back_to_eastmoney_after_eid_not_found`、`test_orchestrator_falls_back_after_unavailable_error`、`test_orchestrator_falls_back_after_not_found_error` 均新增 `primary_failure_category` 断言。
- **结论**：`failures[0].category` 正确捕获 primary source 失败类别；fail-closed 路径保持阻断，不传播分类。

**3. Cache/repository metadata 持久化与旧 metadata 兼容性。**

- **序列化** `models.py:93`：`to_dict()` 包含 `primary_failure_category` 字段，值为合法 category 或 `None`。
- **反序列化** `models.py:111,128`：`from_dict()` 通过 `_optional_string()` → `_normalize_failure_category()` 处理。未知字符串返回 `None`（不抛异常），缺失字段经 `_optional_string(None)` → `None` → `_normalize_failure_category(None)` → `None`。
- **缓存持久化** `cache.py:111`：`_source_metadata_to_json()` 使用 `metadata.to_dict()` + `json.dumps()`，新字段自然包含。
- **缓存读取** `cache.py:130-138`：`_source_metadata_from_json()` 调用 `AnnualReportSourceMetadata.from_dict()`，`ValueError` 被捕获降级为 `None`。
- **旧缓存兼容**：旧缓存行无 `primary_failure_category` key → `from_dict()` 中 `payload.get("primary_failure_category")` 返回 `None` → `_optional_string(None)` → `None` → 字段为 `None` → `source_provenance.py` 投影为 `unknown_public_metadata_absent`。
- **测试覆盖** `test_cache.py`：`test_source_metadata_round_trips_primary_failure_category`（往返）、`test_source_metadata_legacy_or_unknown_failure_category_degrades_to_none`（legacy/unknown 降级）。
- **结论**：序列化/反序列化正确；旧缓存完全兼容，降级为 `None` 后投影为 `unknown_public_metadata_absent`，与设计一致。

**4. Tests 和 docs/design/README 是否准确描述当前行为且不含未来声明？**

- `docs/design.md` 更新段：描述当前实现行为——"当前来源编排在主源 `not_found` / `unavailable` 后 fallback 成功时，会把第一条主源失败类别写入 `AnnualReportSourceMetadata.primary_failure_category`"。无未来时态或未实现声明。
- `fund_agent/fund/README.md` 更新行：描述 fallback 成功路径持久化分类，旧元数据缺失字段时输出 `unknown_public_metadata_absent`。无未来声明。
- `tests/README.md` 更新行：描述当前测试覆盖范围。无未来声明。
- `test_extraction_snapshot.py` 更新：将已有测试从 `primary_failure_category=None`/`incomplete`/`unknown_public_metadata_absent` 改为 `primary_failure_category="not_found"`/`complete`/`eligible`，匹配新的 metadata-owned 投影行为。
- **结论**：文档和测试准确同步当前行为，无未来声明。

**5. Score/FQ/quality/default 产品行为是否无变更？**

- 变更文件列表不含 `extraction_score.py`、`quality_gate.py`、`renderer.py`、`checklist.py`、`final_judgment.py` 或任何评分/质量相关文件。
- Source provenance 字段在 snapshot JSONL 中是 additive 字段，不影响 `comparable_values` 白名单或评分分母/分子计算。
- `test_extraction_score.py` 144 tests 全部通过，确认无 score/FQ 回归。
- **结论**：无 score/FQ/quality/default 产品行为变更。

## Open Questions

无。

## Residual Risk

- 现有缓存中 `fallback_used=true` 但无 `primary_failure_category` 的元数据在刷新前将保持 `unknown_public_metadata_absent`。这是设计接受的兼容行为。
- 多来源链（超过当前 primary + fallback 2-source 模型）不在本次 scope 内；未来如扩展需重新审视 `failures[0]` 语义是否仍代表 primary。
- `docs/implementation-control.md` 未在本 worker scope 内更新，需 controller 后续推进。
