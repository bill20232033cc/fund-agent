# Code Review

## Scope

- Mode: current changes (aggregate deepreview)
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main`
- Output file: `docs/reviews/p13-aggregate-deepreview-glm-20260522.md`
- Included scope: commits `3fef335` and `2172691` plus unstaged `docs/implementation-control.md` update; all production code, tests, README docs, and review artifacts on branch relative to `main`
- Excluded scope: `docs/repo-audit-20260521.md` untracked; `docs/reviews/*` review artifacts (not subject to product code review)
- Parallel review coverage: 3 subagents launched — (1) source code path walk-through covering extractors/performance, extractors/profile, extractors/models, analysis/risk_check, audit/audit_programmatic, data_extractor, template/renderer, services/fund_analysis_service, extraction_snapshot; (2) test coverage review covering all changed test files and fixtures; (3) scope compliance and docs sync review covering design.md, implementation-control.md, controller judgments, README files

## Aggregate Review Context

Current gate: `P13 tracking-error direct-disclosure implementation accepted`. Next gate: `P13 aggregate deepreview`. This review is the aggregate deepreview gate.

Reference documents used:
- `AGENTS.md` — Agent execution constraints
- `docs/design.md` — Design truth
- `docs/implementation-control.md` — Control truth
- `docs/reviews/next-phase-selection-controller-judgment-20260522.md` — Phase selection
- `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md` — P13 plan constraints
- `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md` — Code review judgment

Validation baseline: `424 passed in 1.20s`; `ruff check` passed; `git diff --check` passed.

## Findings

未发现实质性问题。

## Adversarial Failure Pass — Evidence

以下记录了对每个聚合风险面的走读结论和直接证据。

### 1. Phase scope compliance — PASS

**审查范围**: P13 计划范围是 direct annual-report tracking-error disclosure，不含 calculated index series、methodology extraction、constituents extraction。

**证据**:
- `performance.py:_extract_tracking_error()` 只从年报 `§3/§2` 直接文本/表格提取，`TrackingErrorValue.source_type` 只产出 `"direct_disclosure"`，不产出 `"calculated_from_series"`
- `profile.py:_build_index_profile()` 只使用已有 `benchmark` 字段的基准文本构造画像，`methodology_availability` 和 `constituents_availability` 固定为 `"benchmark_only"`，note 显式标注 "不得作为指数编制方法或成分股证据"
- `data_extractor.py:_tracking_error_for_fund_type()` 只对 `index_fund`/`enhanced_index` 保留跟踪误差字段，其他类型返回 `missing`
- 无任何文件引入外部指数序列、指数编制方法文档或成分股列表的读取/计算逻辑

### 2. No Dayu/LLM/E1-E3/Evidence Confirm — PASS

**证据**:
- grep 全部 P13 diff 和新增文件：无 `dayu`、`llm`、`evidence_confirm`、`E1`、`E2`、`E3` 引用
- `audit_programmatic.py` 新增审计规则使用确定性代码路径 (`_audit_tracking_error_source_guard`, `_audit_index_profile_source_guard`)，不引入 LLM 审计
- 所有审计消费的是结构化 `ExtractedField` 值，不是自然语言推理

### 3. FundDocumentRepository boundary — PASS

**证据**:
- `FundDataExtractor.extract()` 接收 `ParsedAnnualReport`（由 `FundDocumentRepository` 产出），不直接操作文件系统
- `extract_performance()` 和 `extract_profile()` 只消费 `report.get_section_text()` 和 `report.tables`，不直接读 PDF
- `FundAnalysisService` 通过 `FundDataExtractor` 获取结构化数据，不绕过仓库接口

### 4. Service/UI boundaries — PASS

**证据**:
- `fund_analysis_service.py` 新增的 `resolve_tracking_error_for_risk()` 调用位于 Service 层，消费的是 Capability 层结构化数据 `structured_data.tracking_error`
- Service 不直接调用 extractor 内部函数，不直接读 PDF/cache
- Renderer 只消费 `TemplateRenderInput.structured_data`，不直接调用 Service 或 Engine
- UI 层（CLI）不涉及变更

### 5. Risk-check authority migration — PASS

**审查范围**: `run_risk_checks()` 的 `tracking_error` 参数从 `Decimal | str | int | float | None` 迁移为 `ResolvedTrackingErrorForRisk | None`。

**证据**:
- `resolve_tracking_error_for_risk()` 优先链：capability_structured_data > developer_override（仅当 enabled 且 missing）> missing
- developer override 只在 `developer_override_enabled=True` 且结构化数据缺失时作为 fallback，`is_product_evidence=False`
- capability 数据存在时即使有 developer override 也优先使用，`conflict_note` 记录冲突但不改变行为
- `_check_tracking_error()` 不再调用 `parse_ratio()` 解析原始值，直接使用已解析的 `ResolvedTrackingErrorForRisk.value`
- 非指数基金通过 `_not_applicable_tracking_error_for_risk()` 返回不适用，不进入数值判断

### 6. Tracking error extraction correctness — PASS

**审查范围**: `performance.py` 新增约 420 行跟踪误差提取逻辑。

**证据**:
- 目标值/控制口径过滤：`_TRACKING_ERROR_NEGATIVE_KEYWORDS` 包含 "控制在"、"不超过"、"力争" 等关键词，`_tracking_error_context_is_target_or_ambiguous()` 返回 `True` 时跳过
- 实际值 vs 目标值混杂 fail-closed：`_has_ambiguous_tracking_error_text()` 检测同行同时出现 actual 和 target 关键词时返回 `missing`
- 表格+正文不一致 fail-closed：`_select_consistent_tracking_error_match()` 在两者解析值不等时返回 `None`
- 多值 fail-closed：`_extract_tracking_error_from_tables()` 和 `_extract_tracking_error_from_text()` 在 `len(matches) > 1` 时返回 `None`
- 标准差列排除：`_find_tracking_error_header_index()` 显式跳过含 "标准差" 的表头
- 所有 fail-closed 路径通过 `_missing_tracking_error()` 返回 `extraction_mode="missing"`，附具体 note

### 7. Renderer/audit consumption — PASS

**证据**:
- `_render_tracking_error_segment()` 通过 `_has_renderable_tracking_error()` 检查 extraction_mode、value 和 provenance_note 三条件后才渲染产品内容
- 缺失/不适用场景渲染固定 "数据不足" 文案，不暴露内部字段
- `_audit_tracking_error_source_guard()` 检查渲染输出是否由结构化字段支撑，防止 benchmark anchor 冒充跟踪误差证据
- `_audit_index_profile_source_guard()` 检查编制方法/成分股段落不能由 benchmark-only 证据替代
- 新字段 `index_profile` 和 `tracking_error` 正确传入 `ProgrammaticAuditInput` 和 `render_template_report()`

### 8. Snapshot observability — PASS

**证据**:
- `extraction_snapshot.py` 新增 `index_profile` 和 `tracking_error` 两个 snapshot 记录
- `fund_agent/fund/README.md` 显式声明 "只作为 observability 字段记录抽取状态、锚点和 note，不进入 `comparable_values`、FQ2 分母或 golden correctness 分母"
- `SNAPSHOT_FIELD_ORDER` 正确排列新字段位置（profile benchmark 之后、fee_schedule 之前；performance investor_return 之后）

### 9. Docs sync — PASS

**证据**:
- `fund_agent/fund/README.md`: 更新了 `StructuredFundDataBundle` 字段数（14→16）、snapshot 记录数（14→16）、risk-check 跟踪误差来源说明、新增 index_profile 和 tracking_error 的 observability 声明
- `tests/README.md`: 更新了 `test_profile.py`、`test_performance.py`、`test_risk_check.py`、`test_audit_programmatic.py`、`test_renderer.py`、`test_extraction_snapshot.py` 的覆盖说明
- 文档使用当前真实接口和参数名，无未来时态描述
- 未修改 `docs/design.md`、`AGENTS.md`、项目根 README（这些文件不需要因 P13 变更）

### 10. Tests — PASS

**证据**:
- `test_performance.py`: 新增 227 行，覆盖直接披露、目标值过滤、模糊文本 fail-closed、标准差误用防护、表格提取、多值 fail-closed、§2 兜底
- `test_profile.py`: 新增 135 行，覆盖纯指数/指数增强/非指数 `index_profile`、benchmark 身份识别、复合基准拆分、编制方法/成分股边界
- `test_risk_check.py`: 新增 181 行，覆盖 resolved authority 链（capability > developer override > missing）、开发覆盖 fallback、QDII 不适用、产品模式不使用覆盖
- `test_audit_programmatic.py`: 新增 103 行，覆盖跟踪误差 source guard 正向/反向、指数编制方法/成分股 source guard
- `test_renderer.py`: 新增 176 行，覆盖跟踪误差 structured_data 替换、benchmark-only 编制方法/成分股不足边界
- `test_extraction_snapshot.py`: 新增 25 行，覆盖 index_profile/tracking_error observability 不进 comparable 分母
- 测试 fixture: 5 个新增文本 fixture 覆盖直接披露、目标值、模糊文本、标准差、指数基金画像场景
- 全套 424 passed，无跳过、无失败

### 11. Residual owners — PASS

**证据**:
- `implementation-control.md` Active Residuals 表记录了所有未关闭风险和 owner
- Future tracking-error / index methodology / constituents extraction → Future P13 Fund Capability documents/extractor/calculation phase
- Future E1-E3 / Evidence Confirm → Future audit architecture phase
- `index_profile` 和 `tracking_error` 不进 comparable/golden/FQ2 → future source-contract scope
- QDII 跟踪误差适用性 → future subtype-design scope
- `docs/repo-audit-20260521.md` → Controller / user，保持排除

### 12. Unstaged implementation-control.md update — PASS

**证据**:
- 唯一 unstaged 改动是 `docs/implementation-control.md`：将 `P13 tracking-error direct-disclosure implementation/code review` 行的 commit 列从 `pending accepted local commit` 更新为 `2172691`（已接受的实现 commit hash）
- P13 Phase History Index 行同步更新 commit hash
- 此更新属于 controller 证据链记录，不改变设计/控制事实或产品行为

## Open Questions

无。

## Residual Risk

- P13 实现只覆盖年报直接披露的跟踪误差；后续计算口径（净值/指数日频序列标准差）和外部指数序列适配器需要独立的 source-contract 设计 phase，当前类型预留了 `calculated_from_series` / `annualized_stddev_active_return` 但未实现
- `index_profile` 的编制方法和成分股提取仍为 `benchmark_only` 层级，后续需要指数文档或招募说明书来源才能提升到 `direct_disclosure` / `source_reference`
- QDII 基金跟踪误差适用性在 `resolve_tracking_error_for_risk()` 中返回 `not_applicable`，但未来可能需要独立的 QDII 跟踪误差规则设计
- 测试 fixture 使用最小文本片段而非完整年报正文，真实年报格式差异（跨页表格、非标准表头）的回归覆盖依赖后续样本矩阵扩展
- `docs/repo-audit-20260521.md` 继续排除，除非后续 scope 显式接受发布

## Verdict

**PASS**

P13 direct tracking-error disclosure 实现完整、scope 合规、无阻断 finding。实现严格限制为年报直接披露提取，风险检查权威链正确迁移，renderer/audit 正确消费结构化数据，snapshot observability 不进分母，文档同步准确，测试覆盖充分。所有聚合风险面均已验证通过。分支已满足 draft PR readiness 条件。
