# Code Review

## Scope

- Mode: current changes
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-source-provenance-public-output-implementation-review-glm-20260527.md`
- Included scope: `fund_agent/fund/source_provenance.py`（新增）、`fund_agent/fund/data_extractor.py`（修改）、`fund_agent/fund/extraction_snapshot.py`（修改）、`tests/fund/test_source_provenance.py`（新增）、`tests/fund/test_data_extractor.py`（修改）、`tests/fund/test_extraction_snapshot.py`（修改）、`tests/fund/test_extraction_score.py`（修改）、`tests/services/test_extraction_score_service.py`（未改、验证兼容）、`fund_agent/fund/README.md`（文档同步）、`tests/README.md`（文档同步）
- Excluded scope: `fund_agent/fund/extraction_score.py`（未修改，仅 inspect）、`fund_agent/fund/report_evidence.py`（未触碰）、`fund_agent/fund/report_quality_validation.py`（未触碰）、所有 `documents/sources.py`/`cache.py`/`downloader`/`pdf/` 内部模块、renderer、FQ0-FQ6、Host/Agent/dayu、fund_type 逻辑、golden/baseline fixture
- Parallel review coverage: 无，单 reviewer 完整走读全部 diff 和关键上下游

## Findings

未发现实质性问题。

逐项 review 结论：

### 1. PublicSourceProvenance 投影正确性 — PASS

`project_public_source_provenance()`（`source_provenance.py:105-170`）完整覆盖计划要求的所有分支：

- `source_metadata is None` → `default_public_source_provenance()`：`fallback_used=False`、`fallback_eligibility=not_applicable`、`source_provenance_status=not_applicable` ✅
- `fallback_used=False`（不论 `resolved_source_name` 为 `eid` 或 `eastmoney`）→ `not_applicable`；source name 不被推断为 fallback 证据 ✅
- `fallback_used=True` + `primary_failure_category` 为 `None` 或不属于已知分类 → `unknown_public_metadata_absent`、`incomplete`；永远不被推断为 `eligible` ✅
- `fallback_used=True` + `not_found`/`unavailable` → `eligible`、`complete` ✅
- `fallback_used=True` + `schema_drift`/`identity_mismatch`/`integrity_error` → `fail_closed`、`incomplete`；下游抽取成功也不改变此分类 ✅

`_ELIGIBLE_FAILURE_CATEGORIES` 和 `_FAIL_CLOSED_FAILURE_CATEGORIES` 使用 `frozenset` + `in` 运算，`None` 不属于任何集合，自然落入 final return 的 `unknown_public_metadata_absent` 分支。类型标注 `PrimaryFailureCategory | None` 正确约束了参数域。运行时传入未知字符串也被 final return 保守处理为 unknown。

`_resolved_source_name()` 只接受 `{"eid", "eastmoney"}` 内的值，未知来源返回 `None`，不向公共输出泄漏仓库内部来源枚举。

### 2. 边界合规 — PASS

- `source_provenance.py` 仅 import `AnnualReportSourceMetadata` from `fund_agent.fund.documents.models`，这是仓库公共模型。未 import `documents/sources.py`、`cache.py`、`downloader`、PDF helper 或任何来源策略内部实现 ✅
- `data_extractor.py` 新增 import 仅为 projection 模块的三个公开符号（`PublicSourceProvenance`、`default_public_source_provenance`、`project_public_source_provenance`），未改变 FundDocumentRepository 来源策略 ✅
- `extraction_snapshot.py` 未新增任何 import；provenance 字段完全从 `bundle.source_provenance` 投影 ✅
- 未触碰 renderer、FQ0-FQ6、default analyze/checklist、Host/Agent/dayu、fund_type 逻辑、golden/baseline fixture、replacement candidate 或 extractor 逻辑 ✅
- `extraction_score.py` 生产代码未修改 ✅
- `report_evidence.py` 和 `report_quality_validation.py` 未触碰 ✅

### 3. StructuredFundDataBundle default factory 与生产显式投影 — PASS

- `source_provenance: PublicSourceProvenance = field(default_factory=default_public_source_provenance)`（`data_extractor.py:121-123`）确保未传 provenance 的 fixture 和旧调用方获得安全 `not_applicable` 默认值，永远不为 `None` ✅
- 生产路径 `FundDataExtractor.extract()` 在 `data_extractor.py:210` 显式调用 `project_public_source_provenance(report.metadata.source)` 填充投影值 ✅
- 测试 `test_structured_bundle_default_source_provenance_is_not_none` 验证构造不传 provenance 时默认值非 None 且为 `not_applicable` ✅
- 测试 `test_data_extractor_projects_primary_source_metadata` 和 `test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent` 验证生产路径分别对主源和 fallback 缺分类场景正确投影 ✅

### 4. SnapshotRecord/JSONL 和 summary Source Provenance 输出 — PASS

- `SnapshotRecord` 新增 8 个 additive provenance 字段（`extraction_snapshot.py:222-229`），类型标注为 `str`/`str | None`/`bool`，不含 default 值——构造时缺失会 TypeError，fail-closed ✅
- `_snapshot_record()`（`extraction_snapshot.py:1028-1058`）从 `bundle.source_provenance` 逐字段拷贝全部 8 个字段到每条记录 ✅
- JSONL 通过 `asdict(record)` 序列化，所有 provenance 字段值为 JSON 兼容 primitive ✅
- `build_snapshot_records` 每个分支（extracted field / classification / nav_data）都经 `_snapshot_record` 走同一投影路径，无遗漏 ✅
- `_source_provenance_summary_lines` 按计划生成独立 `## Source Provenance` 表，列头为 `fund_code, resolved_source_name, fallback_used, fallback_eligibility, source_provenance_status, source_provenance_reason` ✅
- 聚合使用 `first_records_by_fund.setdefault(record.fund_code, record)` 取首条记录；同一基金所有记录 provenance 相同（由 `test_build_snapshot_records_copies_identical_bundle_source_provenance_to_all_rows` 证明） ✅
- 失败基金在 v1 表中省略，并在有错误时输出 `_Failed funds without snapshot records are omitted from Source Provenance v1._` ✅
- `_summary_nullable_text` 返回 `"null"`、`_summary_bool_text` 返回 `"true"`/`"false"`，格式确定性 ✅
- `SNAPSHOT_FIELD_ORDER` 未变，selected count / record count / errors JSONL 语义未变 ✅

### 5. Score 兼容性测试 — PASS

- `test_source_provenance_keys_do_not_change_score_outputs`（`test_extraction_score.py:145-189`）：构造无 provenance 和有 provenance 的 snapshot 记录，逐个比较 `score_snapshot_records`、`score_fund_records`、`derive_fund_quality_records`、`derive_field_applicability_decisions`、`derive_score_applicability_issues` 输出完全一致 ✅
- `test_run_extraction_score_output_ignores_additive_source_provenance`（`test_extraction_score.py:1042-1123`）：运行完整 `run_extraction_score` 管线，验证 `score.json` 顶层 key 集合不变（`_SCORE_JSON_TOP_LEVEL_KEYS`），且 13 个 gate 敏感 key 值完全一致，包括 `thresholds`、`field_scores`、`fund_scores`、`fund_quality`、`field_applicability_decisions`、`score_applicability_issues`、`failed_funds`、`golden_set`、`correctness` ✅
- `tests/services/test_extraction_score_service.py` 未修改且验证通过，证明 Service 层未受影响 ✅

### 6. 测试/文档覆盖和 README 同步 — PASS

- `test_source_provenance.py`：7 个测试覆盖默认值、主源 not_applicable、eastmoney 不推断、fallback 缺分类 unknown、eligible/fail-closed 分类映射、字典序列化 ✅
- `test_data_extractor.py`：4 个新测试覆盖默认 factory 非 None、主源投影、fallback 缺分类投影、NAV 降级不影响 provenance ✅
- `test_extraction_snapshot.py`：2 个新测试覆盖 snapshot 记录包含全部 8 字段、同一基金所有记录复制相同 provenance、summary Source Provenance 表格式和失败基金省略 ✅
- `fund_agent/fund/README.md` 同步更新：新增 provenance 字段说明和 Source Provenance summary 描述 ✅
- `tests/README.md` 同步更新：新增 `test_source_provenance.py`、`test_data_extractor.py` provenance 部分、`test_extraction_snapshot.py` provenance 部分和 `test_extraction_score.py` provenance 兼容性测试描述 ✅

## Open Questions

- 无

## Residual Risk

- 当前仓库公共元数据 `AnnualReportSourceMetadata` 不持久化 `primary_failure_category`，所以生产 fallback 行正常投影为 `unknown_public_metadata_absent`。后续如需区分 eligible 和 fail-closed fallback，需要单独的来源元数据 schema gate，不在本 slice 范围内。证据文档已记录此 residual。
- `_source_provenance_summary_lines` 中的 failed-fund omission note 仅在有实际错误记录时显示。若需在无错误时也固定显示该说明，需一行改动；当前行为在语义上合理——无失败基金时省略说明更清晰。
