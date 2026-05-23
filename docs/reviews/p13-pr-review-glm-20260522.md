# P13 PR Review — AgentGLM（2026-05-22）

## Verdict

**PASS**

PR 7 (`feat/p13-tracking-error-direct-disclosure` → `main`) 通过独立 PR 审查。无阻塞性发现。

## PR Metadata

| Field | Value |
|---|---|
| PR | 7, `OPEN`, `MERGEABLE` |
| Title | feat: add P13 tracking error disclosure path |
| Commits | 7 (post-P12 closeout ×2, next-phase selection ×1, plan accept ×1, implementation ×1, aggregate/docs ×2) |
| Files changed | 56 (+5921 / −73) |
| CI | test job SUCCESS |
| Reviews | none yet |

## Scope Summary

本 PR 为 P13 tracking-error direct-disclosure 的完整实现，包含：

- 两个新增结构化值类型 `IndexProfileValue` 和 `TrackingErrorValue`（`models.py`）
- 年报 `§3`/`§2` 直接披露跟踪误差抽取（`performance.py`，+465 行）
- 基准上下文指数画像构造（`profile.py`，+183 行）
- `StructuredFundDataBundle` 新增 `index_profile` / `tracking_error` 显式字段（`data_extractor.py`）
- 风险检查迁移到 `ResolvedTrackingErrorForRisk` 结构化权威（`risk_check.py`，+191 / −16 行）
- 模板渲染器跟踪误差和指数编制规则段落从结构化数据消费（`renderer.py`，+206 / −11 行）
- 确定性审计守卫：跟踪误差来源边界 + 指数画像 benchmark-only 防护（`audit_programmatic.py`，+197 行）
- Service 层调用 `resolve_tracking_error_for_risk()` 替代裸标量（`fund_analysis_service.py`）
- Snapshot 观测字段（不进 comparable/FQ2/golden 分母）（`extraction_snapshot.py`）
- 4 个新 fixture、+227 测试行（performance）、+134（profile）、+179（risk_check）、+102（audit）、+169（renderer）
- `docs/implementation-control.md` 状态同步到 `ready-to-open-draft-PR`
- Fund README / tests README 同步

## Correctness Findings

| # | Severity | Finding | Status |
|---|---|---|---|
| C-1 | info | `_extract_tracking_error_from_text` 在 `§3` 和 `§2` 间跨节扫描，多命中时返回 `None`（fail-closed）；对于同一值在两节重复披露的报告会丢失有效数据，但 MVP 阶段可接受 | accepted risk |
| C-2 | info | `_benchmark_components` 拆分结果保留权重百分比（如 `"80%"`），`benchmark_component_text` 为纯信息性元组，不做计算消费 | no issue |
| C-3 | info | `_extract_tracking_error_from_tables` 多行命中时返回 `None`；不同期间的跟踪误差行（如"过去一年"/"过去三年"）不会被错误合并 | correct behavior |

无阻塞性正确性问题。所有 fail-closed 路径（ambiguous text、table+text conflict、multi-match）均为保守策略。

## Stability Findings

| # | Severity | Finding | Status |
|---|---|---|---|
| S-1 | pass | `_has_renderable_tracking_error` 三重检查（extraction_mode + value + provenance_note）+ 渲染器内部 `value is None` 防御分支，不使用 `assert` 做运行时校验 | PASS |
| S-2 | pass | `resolve_tracking_error_for_risk` 显式处理 4 条分支：非指数→不适用，有结构化值→产品证据，开发覆盖→fallback，全缺→missing | PASS |
| S-3 | pass | `_missing_tracking_error_for_risk(fund_type)` 为 `run_risk_checks(tracking_error=None)` 提供保守默认 | PASS |

## Maintainability Findings

| # | Severity | Finding | Status |
|---|---|---|---|
| M-1 | pass | `ResolvedTrackingErrorForRisk` frozen dataclass + `slots=True`，字段语义明确（source_type, authority, is_product_evidence, conflict_note） | clean |
| M-2 | pass | 提取/解析/构造函数拆分清晰，单函数职责单一 | clean |
| M-3 | pass | 新增类型通过 `__init__.py` 和 `__all__` 导出，模块边界保持一致 | clean |

## Module Boundary Review

| Boundary | Assessment |
|---|---|
| `FundDocumentRepository` | 提取器只接收 `ParsedAnnualReport`，不直接访问文件/PDF/缓存。✓ |
| `ExtractedField[T]` 泛型 | `IndexProfileValue` 和 `TrackingErrorValue` 作为新类型参数，不破坏现有 `ExtractedField[dict]` 消费。✓ |
| Risk check → extractors models | `risk_check.py` 只导入 `TrackingErrorValue`, `EvidenceAnchor`, `ExtractedField`，不依赖提取实现。✓ |
| Service → analysis | `fund_analysis_service.py` 调用 `resolve_tracking_error_for_risk()`，不直接操作提取器。✓ |
| Renderer → structured data | 消费 `input_data.structured_data.tracking_error` 和 `input_data.structured_data.index_profile`，不反向注入。✓ |

## Hard Constraint Compliance

| Constraint | Assessment |
|---|---|
| 显式参数 / no extra_payload | `StructuredFundDataBundle` 新增两个显式 typed 字段，无 dict 注入。✓ |
| No Dayu runtime / LLM / Evidence Confirm | 纯确定性提取和规则检查，无外部运行时。✓ |
| Fund type gating | `_tracking_error_for_fund_type`、`_build_index_profile`、`resolve_tracking_error_for_risk` 三层 fund type 门控。✓ |
| Tracking-error source authority | 结构化数据 > 开发覆盖 > missing，带 `is_product_evidence` 和 `authority` 标记。✓ |
| Renderer 只从 structured_data 消费 | `_render_tracking_error_segment` 只读取 `input_data.structured_data.tracking_error`。✓ |
| Snapshot 不进 comparable/FQ2/golden | `index_profile.comparable_values == {}`，`tracking_error.comparable_values == {}`。✓ |
| No calculated index series / methodology / constituents | 未实现，保持 future scope。✓ |
| No RR-13 / repo-audit | `docs/repo-audit-20260521.md` 未被修改或引入。✓ |

## Test Coverage Assessment

| Layer | Coverage |
|---|---|
| Extractor: tracking error | 文本直接披露 ✓、表格直接披露 ✓、目标值拒绝 ✓、模糊文本 fail-closed ✓、标准差排除 ✓、table+text 一致保留表格 ✓、table+text 冲突 fail-closed ✓ |
| Extractor: index profile | 纯指数 ✓、指数增强复合基准 ✓、非指数 missing ✓、复合基准分隔符覆盖 ✓ |
| Risk check: resolve authority | 结构化数据优先 ✓、开发覆盖 fallback ✓、product mode 忽略开发覆盖 ✓、QDII 不适用 ✓ |
| Renderer: tracking error | 结构化数据替换占位 ✓、缺失值防御性渲染 ✓ |
| Renderer: index profile | benchmark-only 不替代编制方法/成分股 ✓ |
| Audit: source guard | 跟踪误差无结构化支撑 → C2 issue ✓、benchmark-only 编制方法 → C2 issue ✓ |
| Integration: sample matrix | 510300 index_fund tracking_error=direct ✓、110011 active_fund missing ✓、000171 bond_fund missing ✓ |
| Snapshot: observability | index_profile/tracking_error comparable_values={} ✓ |

424 tests passed, ruff check passed, `git diff --check` passed。

## CI Evidence

- GitHub Actions `test` job: SUCCESS (completed 2026-05-21T20:58:41Z)

## Docs Sync

| Doc | Synced |
|---|---|
| `fund_agent/fund/README.md` | 12→14 项、14→16 字段、跟踪误差权威链描述 ✓ |
| `tests/README.md` | 新增测试描述同步 ✓ |
| `docs/implementation-control.md` | gate → ready-to-open-draft-PR、P13 archive 更新 ✓ |

## Out-of-Scope Verification

- `docs/repo-audit-20260521.md`：未包含在 diff 中。✓
- 无生产代码编辑、无 commit、无 push。✓

## Residual Risks / Test Gaps

| # | Risk | Owner / destination |
|---|---|---|
| R-1 | 年报同一跟踪误差在 `§3` 和 `§2` 重复披露时，当前 fail-closed（多命中→missing）；未来可考虑值一致去重 | Future tracking-error extractor refinement |
| R-2 | 计算跟踪误差（fund/index 日频序列）未实现 | Future P13 follow-up |
| R-3 | 外部指数序列适配器未实现 | Future source-contract phase |
| R-4 | 指数编制方法和成分股提取未实现 | Future index document/source-contract phase |
| R-5 | QDII 跟踪误差适用性未设计 | Future subtype-design phase |
| R-6 | `index_profile`/`tracking_error` 未提升到 comparable/golden/FQ2 分母 | Future quality-gate phase |
| R-7 | `_benchmark_components` 拆分保留权重百分比片段，未来如需消费需额外解析 | Future benchmark decomposition |
| R-8 | 表格多行不同期间跟踪误差当前 fail-closed，未做期间优先选择 | Future extractor refinement |

## Reviewer

AgentGLM (GLM-5.1), independent PR reviewer, 2026-05-22
