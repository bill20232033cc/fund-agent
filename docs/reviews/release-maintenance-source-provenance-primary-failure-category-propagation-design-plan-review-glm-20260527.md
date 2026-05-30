# Plan Review: Source Provenance Primary-Failure-Category Propagation Design

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27T06:26:34
> **Reviewed artifact**: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md`
> **Truth sources**: `AGENTS.md`; `docs/design.md` sections 6.1 (lines 593–624); `docs/implementation-control.md` Startup Packet
> **Verdict**: `pass-with-risks`

---

## Scope & Assumptions Tested

| Assumption | Tested | Result |
|---|---|---|
| `AnnualReportSourceMetadata` lacks `primary_failure_category` | Code fact verified | Confirmed: `models.py:39-53` has 15 fields, no failure category |
| `_mark_fallback_used()` only sets `fallback_used=True` | Code fact verified | Confirmed: `sources.py:767-780`, uses `dataclasses.replace` |
| `project_public_source_provenance()` already handles category via kwarg | Code fact verified | Confirmed: `source_provenance.py:105-170`, kwarg `primary_failure_category` exists but production path never passes it |
| Production path `FundDataExtractor.extract()` does not pass kwarg | Code fact verified | Confirmed: `data_extractor.py:210` calls `project_public_source_provenance(report.metadata.source)` with no kwarg |
| `AnnualReportSourceFailureCategory` is a `Literal` in `sources.py` | Code fact verified | Confirmed: `sources.py:26-32`, `Literal["not_found", ...]` |
| Fail-closed categories raise before fallback can succeed | Code fact verified | Confirmed: `sources.py:645-656`, `_raise_fallback_blocked` called immediately, no `continue` |
| `sources.py` imports from `models.py` (creates circular risk) | Code fact verified | Confirmed: `sources.py:21` imports `AnnualReportSourceMetadata, AnnualReportSourceName` from `models` |
| `primary_failure_category` already exists in design.md as a public field | Doc fact verified | Confirmed: `design.md:624` — field listed in public snapshot JSONL output, with fail-closed constraint |
| No baseline/golden promotion authorized | Constraint verified | Plan blocks explicitly in Non-Goals, Stop Conditions, Bounded Evidence section |
| No source strategy change authorized | Constraint verified | Plan blocks in Non-Goals and Current Code Facts table |

---

## Findings

### F1-未修复-中-Literal 类型引入路径未收敛，实现 Agent 可能触发循环导入

- **位置**: Plan "Implementation Files / `fund_agent/fund/documents/models.py`" 与 "Minimal Data Model Extension"
- **问题类型**: 架构边界 / 不可直接实施
- **当前写法**: Plan 写 "Add `AnnualReportSourceFailureCategory`-compatible optional field **or** a local literal alias with the same five values."
- **反例/失败场景**:
  - **路径 A**：`models.py` 从 `sources.py` 导入 `AnnualReportSourceFailureCategory`。但 `sources.py:21` 已从 `models.py` 导入 `AnnualReportSourceMetadata` 和 `AnnualReportSourceName`，形成 `models ↔ sources` 循环依赖。Python 在 `from __future__ import annotations` 下对 type hints 容忍循环，但 `models.py` 的 `from_dict()` 需要在运行时引用该 Literal 做验证/normalize，不是纯 type hint 用途，可能在 import 时触发 `AttributeError`。
  - **路径 B**：在 `models.py` 创建本地 Literal alias。两个独立 Literal 定义（`sources.py:26-32` 与 `models.py` 新增）会导致 drift 风险——后续新增 category 时需同步修改两处。Plan 的 "Validate/normalize through a shared helper" 未指定 helper 归属模块。
- **为什么有问题**: Plan 给 implementation agent 两个互斥选项但未裁决哪个安全，也没有分析循环依赖风险。这是 code-generation-ready 的必要前提。
- **直接证据**:
  - `sources.py:21`: `from fund_agent.fund.documents.models import AnnualReportSourceMetadata, AnnualReportSourceName`
  - `sources.py:26-32`: `AnnualReportSourceFailureCategory = Literal[...]`
  - Plan "Implementation Files": "Add `AnnualReportSourceFailureCategory`-compatible optional field or a local literal alias"
- **影响**: Implementation agent 选错路径会触发运行时 import 错误，或引入隐性类型 drift。
- **建议改法和验证点**:
  - 最小安全路径：将 `AnnualReportSourceFailureCategory` Literal 定义从 `sources.py` 上移到 `models.py`（与 `AnnualReportSourceName` 同位置），`sources.py` 改为从 `models.py` 导入。这是自然的依赖方向（sources 依赖 models），不引入新模块，且消除 alias drift 风险。
  - 验证：`uv run pytest tests/fund/documents/ -q` 全过确认无 import breakage。
- **修复风险**: 低——纯移动类型定义位置，不改变语义。
- **严重程度**: 中

### F2-未修复-中-投影优先级规则不完整，metadata=None + kwarg 存在时行为未规格化

- **位置**: Plan "Projection / Compatibility behavior" 与 "Public Contract"
- **问题类型**: 契约缺失 / 不可直接实施
- **当前写法**: Plan 写 "If both metadata and explicit keyword are present, metadata should be authoritative in production"，同时写 "Keep the explicit keyword argument as a test/development override" 和 "If metadata lacks the field, behavior remains exactly as today"。
- **反例/失败场景**:
  - 实现 Agent 添加 `primary_failure_category` 到 `AnnualReportSourceMetadata` 后，field 始终存在（默认 `None`）。"metadata lacks the field" 语义变成 "field is None"。
  - 当 `source_metadata.primary_failure_category=None`（旧缓存 / 未设值）且 `primary_failure_category="not_found"`（kwarg 显式传入）时，Plan 没有说明是使用 None（走 unknown 路径）还是使用 kwarg（走 eligible 路径）。
  - 如果实现为 "metadata authoritative" 包含 None → kwarg 被忽略 → 所有现有测试使用 kwarg 的场景（`test_fallback_with_eligible_category_is_complete` 等）会突然失败，因为 metadata 的 None 会覆盖 kwarg 的值。
  - 如果实现为 "metadata is None → fallback to kwarg" → 这不是 "metadata authoritative" 而是 "metadata 优先，None 时 fallback"，需要明确表述。
- **为什么有问题**: 当前的 7 个 projection 测试全部通过 kwarg 传入 category（因为 metadata 还没有这个 field）。实现后这些测试的 metadata 实例会多一个 `primary_failure_category=None`。如果优先级规则不精确，要么测试全部 break，要么 kwarg override 行为与 Plan 声称的 "metadata authoritative" 矛盾。
- **直接证据**:
  - `source_provenance.py:139`: `if primary_failure_category in _ELIGIBLE_FAILURE_CATEGORIES:` — 当前只读 kwarg
  - `tests/fund/test_source_provenance.py:114-162`: 所有 eligible/fail-closed 测试通过 kwarg 传入 category，metadata 无该 field
  - Plan "Compatibility behavior": "If both metadata and explicit keyword are present, metadata should be authoritative"
  - Plan "Compatibility behavior": "Keep the explicit keyword argument as a test/development override"
- **影响**: Implementation agent 可能写出与 Plan 文字矛盾或导致现有测试 break 的优先级逻辑。
- **建议改法和验证点**:
  - 明确写法：`effective_category = source_metadata.primary_failure_category if source_metadata.primary_failure_category is not None else primary_failure_category`
  - 即：metadata 非 None 时 metadata 优先（production path 的真源）；metadata 为 None 时 fallback 到 kwarg（test override 保持工作）。
  - 新增一条 negative test：metadata 为 `not_found`，kwarg 为 `schema_drift`，断言输出为 `eligible`（metadata wins）。metadata 为 None，kwarg 为 `not_found`，断言输出为 `eligible`（kwarg fallback）。
- **修复风险**: 低——明确的 3 行优先级逻辑 + 2 条新测试。
- **严重程度**: 中

### F3-未修复-低-Plan 引用类名与实际代码不一致

- **位置**: Plan "Current Code Facts" 表格与 "Implementation Files / `fund_agent/fund/documents/sources.py`"
- **问题类型**: 不可直接实施
- **当前写法**: Plan 多处引用 `AnnualReportSourceChain.fetch_annual_report_pdf()`
- **反例/失败场景**: 实际类名为 `AnnualReportSourceOrchestrator`（`sources.py:567`）。Implementation agent 搜索 `AnnualReportSourceChain` 找不到匹配，可能误以为需要新建类或在错误位置修改。
- **为什么有问题**: 类名错误增加实现 Agent 的搜索和确认成本。
- **直接证据**:
  - `sources.py:567`: `class AnnualReportSourceOrchestrator:`
  - Plan "Current Code Facts": "AnnualReportSourceChain.fetch_annual_report_pdf() allows fallback..."
  - Plan "Implementation Files": "Update AnnualReportSourceChain.fetch_annual_report_pdf()..."
- **影响**: 实现耗时增加，minor。
- **建议改法和验证点**: Plan 改为 `AnnualReportSourceOrchestrator`。
- **修复风险**: 低
- **严重程度**: 低

---

## Open Questions

1. **F1 路径裁决**：Plan 应在 review 后明确选择 "上移 Literal 到 models.py" 或 "本地 alias"，不应留 or 给 implementation agent。Controller 需裁决。
2. **F2 优先级精确规格**：Plan 应补充精确的优先级伪代码或 truth table，覆盖 `(metadata_value, kwarg_value)` 的全部 4 种组合。

---

## Residual Risks

| Risk | Severity | Tracking destination |
|---|---|---|
| 旧缓存 `fallback_used=True` 但无 `primary_failure_category` 持续投影为 `unknown_public_metadata_absent`，需 `force_refresh` 才能升级 | 低 | Implementation gate 的 evidence rerun 验证 |
| 多源链路（>2 sources）时 `failures[0]` 是否仍是 "primary" failure | 低 | Plan 已显式 scope-out，后续 provenance-chain schema gate 处理 |
| `_mark_fallback_used` 改签名后，外部 caller 是否有直接调用 | 低 | `grep "_mark_fallback_used"` 确认无外部 caller（当前仅为 module-private） |

---

## Special Lenses Applied

### Architecture Boundary Review

- Plan 正确识别了 metadata owner 层（`models.py`）与 source chain 层（`sources.py`）的边界。
- F1 指出类型定义位置需要调整以匹配自然依赖方向。
- Plan 不改变 `FundDocumentRepository` 公开入口、Service/Host/Agent 分层、或 CLI 可见行为。边界合规。

### Best-Practice Review

- "在决策边界持久化证据，下游只读" 是正确的 provenance 设计原则。
- Fail-closed 默认（missing category → unknown）符合 AGENTS.md 约束。
- Cache backward compatibility（缺失 key → None）是标准做法。

### Optimal-Solution Review

- 最小 field 扩展 + 现有 projection function 复用是最短路径。无需新模块、新协议或新 schema version。
- 未发现更简单的替代方案。

### Overengineering Review

- Plan scope 精确：一个 optional field + 一个 source-chain write point + 一个 projection read point。没有新 abstraction、builder 或 wrapper。
- 不需要 cache version bump、schema migration 或 cache invalidation。

### Overcoupling Review

- Plan 不引入跨层穿透。metadata → projection 是单向数据流。
- kwarg override 是 test-only escape hatch，不增加生产路径耦合。

---

## Conclusion

**Verdict: `pass-with-risks`**

Plan 的动机、scope、non-goals 和 fail-closed 约束与 AGENTS.md 和 design.md 一致。核心设计（在 metadata 持久化 primary failure category，投影到已有 public field）是最小安全路径。

两个中等级 finding（F1 类型引入路径未收敛、F2 投影优先级规则不完整）需要在 implementation 前由 controller 裁决，但两者都有明确的修复方向且修复成本极低。Plan 不需要结构性重写。
