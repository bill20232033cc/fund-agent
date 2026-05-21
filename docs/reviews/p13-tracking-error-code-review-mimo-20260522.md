# Code Review

## Scope

- Mode: current changes
- Branch: `feat/p13-tracking-error-direct-disclosure`
- Base: `main` (workspace diff, unstaged changes on feature branch)
- Output file: `docs/reviews/p13-tracking-error-code-review-mimo-20260522.md`
- Included scope: 23 changed files (+2119/-61) — extractors/models, extractors/performance, extractors/profile, extractors/__init__, data_extractor, analysis/risk_check, analysis/__init__, template/renderer, audit/audit_programmatic, extraction_snapshot, services/fund_analysis_service, fund/README, tests/README, 11 test files, 5 new fixture files
- Excluded scope: `docs/repo-audit-20260521.md` (out-of-scope untracked)
- Parallel review coverage: 无
- Controller validation: pytest 420 passed, `ruff check fund_agent tests` passed, `git diff --check HEAD` passed

## Findings

### 1-未修复-低-渲染器用 assert 做运行时完整性校验

- **入口/函数**: `_render_tracking_error_segment` (`fund_agent/fund/template/renderer.py`)
- **文件(行号)**: `fund_agent/fund/template/renderer.py:695`
- **输入场景**: 跟踪误差字段 `extraction_mode == "direct"` 且 `value` 不为 `None` 时触发的正常渲染路径
- **实际分支**: `assert tracking_error.value is not None` 被执行
- **预期行为**: 用显式条件检查或 `if TYPE_CHECKING` 守护；`assert` 在 `python -O` 下被剥离
- **实际行为**: `assert` 在非优化模式下有效；Python 优化模式（`-O`）下被移除，后续 `value.value_text` 直接访问 `None` 属性会抛 `AttributeError`
- **直接证据**: `renderer.py:695` — `assert tracking_error.value is not None`；`renderer.py:696` — `value = tracking_error.value`；`renderer.py:698` — `value.value_text`
- **影响**: 当前生产不使用 `-O`，`_has_renderable_tracking_error()` 已覆盖 `value is not None` 检查，实际触发概率极低；但 assert 语义暗示"不可能发生"，与防御性编码规范不一致
- **建议改法和验证点**: 将 `assert tracking_error.value is not None` 替换为显式 `if tracking_error.value is None: return _render_tracking_error_insufficient(...)` 或在函数入口做 early return；验证优化模式下不 crash
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Review Summary

### 正确性

- **显式类型字段**: `IndexProfileValue` 和 `TrackingErrorValue` 为 frozen dataclass，字段全部显式声明，无 `extra_payload` 或 `dict[str, object]` 替代。符合 AGENTS.md "禁止把显式参数放在 extra_payload 里传递" 硬约束。
- **跟踪误差抽取**: `performance.py` 正确区分年报直接披露（"报告期年化跟踪误差：1.23%"）与目标/控制文本（"力争将年化跟踪误差控制在 4.00% 以内"）。`_tracking_error_context_is_target_or_ambiguous()` 过滤目标关键词；`_has_ambiguous_tracking_error_signal()` 检测同行混杂信号时 fail closed 返回 `missing`；`_find_tracking_error_header_index()` 排除"标准差"列。
- **基金类型适用性**: `_tracking_error_for_fund_type()` 正确仅保留 `index_fund` / `enhanced_index` 的跟踪误差字段；`active_fund` / `bond_fund` / `fof_fund` 返回 `missing("非指数基金不适用跟踪误差")`；`qdii_fund` 返回 `missing("QDII 基金当前不适用 P13 跟踪误差规则")`。
- **风险检查 authority 迁移**: `resolve_tracking_error_for_risk()` 实现了正确优先级链：结构化 Capability 数据 > 开发覆盖（仅 developer_override mode）> 缺失。结构化数据存在时 `is_product_evidence=True`，开发覆盖时 `is_product_evidence=False`。QDII 直接返回 `not_applicable`。`run_risk_checks` 已从 `Decimal | str | int | float | None` 迁移到 `ResolvedTrackingErrorForRisk | None`。
- **指数画像**: `_build_index_profile()` 正确从 benchmark 上下文派生指数画像，`methodology_availability` 和 `constituents_availability` 均标记为 `benchmark_only`，不声称编制方法或成分股直接披露。

### 源边界与 FundDocumentRepository 边界

- 跟踪误差抽取只从 `ParsedAnnualReport`（`FundDocumentRepository` 提供）的 `§3`/`§2` 表格和正文提取。不引入外部数据源、Service 层直接访问或 PDF cache 穿透。
- Service 层（`fund_analysis_service.py`）通过 `resolve_tracking_error_for_risk()` 消费 `structured_data.tracking_error`，开发覆盖通过 `FundAnalysisDeveloperOverrides` 嵌套传入且仅在 `developer_override` mode 生效。结构化数据优先于开发覆盖。
- `data_extractor.py` 中 `_classified_fund_type()` 从 `basic_identity.value["classified_fund_type"]` 读取标准类型，不重新分类。

### 渲染器与审计行为

- `_render_tracking_error_segment()` 仅从 `structured_data.tracking_error` 渲染跟踪误差段落；缺失时保持 `数据不足` 占位符。
- `_render_index_constituents_segment()` 优先使用 `index_profile` 渲染编制方法和成分股；`benchmark_only` 时保留 `数据不足`。
- `_audit_tracking_error_source_guard()` 检测渲染了非 `数据不足` 的跟踪误差但缺少 `structured_data.tracking_error` 支撑的场景（C2 规则）。
- `_audit_index_profile_source_guard()` 检测编制方法或成分股由 `benchmark_only` 证据误支撑的场景（C2 规则）。

### Quality Gate / Snapshot 策略

- `index_profile` 和 `tracking_error` 已加入 `SNAPSHOT_FIELD_ORDER` 作为观测字段。
- 测试验证 `comparable_values == {}`，确认不进入 FQ2 分母或 golden correctness 分母。符合 controller judgment 的 observability-only 策略。

### 测试覆盖

- **跟踪误差抽取**: 覆盖直接披露、目标值过滤、模糊文本 fail closed、标准差排除、表格抽取 5 个场景。
- **指数画像**: 覆盖纯指数（`identified`）、指数增强（`composite`）、非指数（`missing`）3 个场景。
- **风险检查 authority**: 覆盖结构化数据优先于开发覆盖、缺失时开发覆盖 fallback、product mode 不使用开发覆盖、QDII 不适用 4 个场景。
- **审计 guard**: 覆盖跟踪误差缺少结构化字段、结构化字段通过、benchmark-only 编制方法误用 3 个场景。
- **渲染器**: 覆盖跟踪误差从结构化字段替换、benchmark-only 编制方法/成分股保持不足 2 个场景。
- **回归**: P1 sample matrix 更新为 38 cells，验证 510300（指数基金）tracking_error 为 `direct`、110011/000171（非指数）为 `missing`。

### 文档同步

- `fund_agent/fund/README.md` 已更新：14→14 项结构化数据（新增 `index_profile`、`tracking_error`），snapshot 字段数 14→16，风险检查 tracking_error authority 描述已更新。
- `tests/README.md` 已更新：test_profile、test_performance、test_risk_check、test_audit_programmatic、test_renderer、test_extraction_snapshot 的描述已同步新增覆盖范围。

## Open Questions

- 无

## Residual Risk

- 跟踪误差计算路径（`calculated_from_series`）未实现，`TrackingErrorValue` 预留了 `fund_series_source`、`index_series_source`、`observation_count`、`annualization_factor` 等字段，但当前所有值为 `None`。后续实现时需确保 renderer 和审计 guard 覆盖 `derived` 模式。
- `_benchmark_components()` 的正则拆分只覆盖 `＋`/`+`，未覆盖 `_COMPOSITE_BENCHMARK_SEPARATORS` 中的 `×`/`*`/`和`/`及`。当前不影响正确性（`_benchmark_identity_status` 独立判断 composite），但未来若有含 `×` 的复合基准需拆分成分时需修正。
- `index_profile` 和 `tracking_error` 的 `comparable_values` 当前为空，FQ2/golden denominator 策略需在后续 phase 显式接受后才可变更。

## Verdict

**PASS**

实现符合 P13-S1 plan review controller judgment 接受的直接披露 scope。显式类型字段、FundDocumentRepository 边界、跟踪误差 authority 迁移、renderer/audit/risk 行为、quality gate observability-only 策略均按计划正确实现。唯一 finding（renderer assert）为低严重度，不影响当前生产行为。测试覆盖充分，文档已同步。
