# Code Review

## Scope

- Mode: current changes
- Branch: feat/mvp-llm-incomplete-run-artifacts
- Base: main
- Output file: docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-review-mimo-20260611-132347.md
- Included scope: fund_agent/fund/source_provenance.py, fund_agent/fund/extraction_snapshot.py, fund_agent/fund/documents/sources.py, fund_agent/fund/README.md, tests/fund/test_source_provenance.py, tests/fund/test_extraction_snapshot.py, tests/fund/test_extraction_score.py, tests/fund/test_data_extractor.py
- Excluded scope: docs/design.md, docs/implementation-control.md, docs/current-startup-packet.md, root README.md, pyproject.toml, .gitignore, fund_agent/fund/documents/repository.py, fund_agent/fund/documents/cache.py, fund_agent/fund/documents/models.py, live evidence/reports/golden/readiness artifacts
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Required Checks Verification

| 检查项 | 结果 | 证据 |
|---|---|---|
| 当前生产策略仍为 EID single-source only | PASS | `AnnualReportSourceOrchestrator.__init__` 强制 `len(self.sources) != 1` 时抛出 ValueError（sources.py:601-604）；`EastmoneyAnnualReportSource` docstring 明确标记为 "deferred future source candidate"（sources.py:502-507） |
| 未重新引入 Eastmoney/fund-company/CDN/CNINFO fallback | PASS | `git diff --name-only` 只包含 accepted write set；`rg` 未发现 fallback 来源重新接入生产路径 |
| Source Provenance v2 additive fields 正确 | PASS | `selected_source`/`source_mode`/`fallback_enabled` 在 `PublicSourceProvenance` dataclass 中正确添加（source_provenance.py:79-81）；投影逻辑从 `AnnualReportSourceMetadata` 直接读取，不从 `resolved_source_name` 推断（source_provenance.py:139-142） |
| legacy/unavailable provenance 输出 legacy_or_unknown | PASS | `default_public_source_provenance()` 返回 `source_strategy="legacy_or_unknown"`, `selected_source=None`, `source_mode="legacy_or_unknown"`, `fallback_enabled=None`（source_provenance.py:102-115） |
| 当前 EID 元数据路径无 primary_then_fallback | PASS | `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'` 只命中 required negative assertion test（test_source_provenance.py:337-360） |
| snapshot summary 与测试对齐 | PASS | 97 tests passed；snapshot summary 表包含 v2 字段（extraction_snapshot.py:1206-1210）；test_extraction_snapshot.py 验证 summary 行格式 |
| Fund README 同步为当前事实且不授权 fallback | PASS | README 更新记录 v2 additive fields 并明确 "source_strategy 只作为兼容 alias，不是来源获取策略或 fallback 授权"（README.md:196） |
| 无 accepted write set 外的源/测试变更 | PASS | `git diff --name-only` 只列出 8 个 accepted files |

## Implementation Path Walkthrough

### source_provenance.py - Schema 与投影逻辑

- Schema version 从 `repository_source_provenance.v1` 升级到 `v2`（source_provenance.py:14）
- `SourceStrategy` 类型从 `Literal["primary_then_fallback"]` 扩展为 `Literal["single_source_only", "legacy_or_unknown"]`（source_provenance.py:31）
- 新增 `SelectedSourceName`、`SourceMode` 类型（source_provenance.py:33-34）
- `PublicSourceProvenance` 新增 `selected_source`、`source_mode`、`fallback_enabled` 字段（source_provenance.py:79-81）
- `project_public_source_provenance()` 从 metadata 直接投影新字段，`source_strategy` 设为 `source_mode` 的别名（source_provenance.py:143）
- 元数据缺失时返回 `legacy_or_unknown` / `None` 安全默认值（source_provenance.py:102-115）
- `_selected_source_name()` 不从 `resolved_source_name` 推断（source_provenance.py:242-257）

### extraction_snapshot.py - Snapshot 传播

- `SnapshotRecord` 新增 `selected_source`、`source_mode`、`fallback_enabled` 字段（extraction_snapshot.py:237-239）
- `_snapshot_record()` 从 `bundle.source_provenance` 复制新字段（extraction_snapshot.py:1167-1169）
- Source Provenance summary 表更新为包含 v2 字段（extraction_snapshot.py:1206-1210）
- 新增 `_summary_nullable_bool_text()` helper 处理 `bool | None` 格式化（extraction_snapshot.py:1265-1281）

### sources.py - Docstring 修正

- `AnnualReportSourceOrchestrator.__init__` docstring 从 "EID 主源与 Eastmoney fallback" 修正为 "仅使用 EID single-source；Eastmoney 不在当前 production fallback 中"（sources.py:584-585）
- 无实现变更，仅 wording 修正

### README.md - 文档同步

- 更新 snapshot provenance 字段列表，包含 v2 additive fields（README.md:196）
- 明确 `source_strategy` 是兼容 alias，不是 fallback 授权（README.md:196）

## Tests Verification

- `test_source_provenance.py`: 19 passed - 覆盖 default provenance、EID single-source projection、fallback metadata、`primary_then_fallback` negative assertion、dict serialization
- `test_data_extractor.py`: 10 passed - 覆盖 EID metadata projection、fallback metadata、NAV failure degradation
- `test_extraction_snapshot.py`: 13 passed - 覆盖 snapshot record schema、source provenance fields、summary table、bond risk evidence
- `test_extraction_score.py`: 55 passed - 覆盖 additive provenance 不改变 score semantics、correctness、fund quality

## Residual Risk

- `docs/design.md` 仍包含旧 v1 public snapshot 字段描述，需后续 design-truth-sync 处理（implementation evidence 已记录）
- `AnnualReportSourceName` 仍包含 `eastmoney`，属于 deferred source-candidate/fallback 设计范围（plan 已记录）
- README 第 73 行使用 `mode=single_source_only` 而非 `source_mode=single_source_only`，这是 pre-existing naming inconsistency，不在本 gate 修改范围内
