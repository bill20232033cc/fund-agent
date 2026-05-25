# Rereview: Report-Quality Scoring JSONL Content Validation Implementation

> Gate: `report-quality scoring JSONL content validation implementation`
> Role: AgentMiMo rereview
> Date: 2026-05-25
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`, MiMo initial review, GLM initial review, controller judgment

## 结论

**PASS**

## Rereview Scope

| Item | Source |
|---|---|
| MiMo initial review findings | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-mimo-20260525.md` |
| GLM initial review findings | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-glm-20260525.md` |
| Changed files | `fund_agent/fund/report_quality_validation.py`, `tests/fund/test_report_quality_validation.py`, `fund_agent/fund/README.md` |

## Verification Results

### 1. `_is_blocking_gap` 与 `report_evidence.py` 语义一致

**PASS** — 已修复。

`report_evidence.py:2131-2144` 定义：
```python
def _is_blocking_gap(gap: ReportDataGap) -> bool:
    return gap.gap_kind != "not_applicable" and gap.failure_category != "not_applicable"
```

`report_quality_validation.py:2311-2321` 当前实现：
```python
def _is_blocking_gap(gap: _JsonRecord) -> bool:
    return gap.get("gap_kind") != "not_applicable" and gap.get("failure_category") != "not_applicable"
```

语义完全一致。旧版 `_BLOCKING_GAP_KINDS` 和 `_BLOCKING_GAP_FAILURES` 硬编码 frozenset 已移除。新测试 `test_scoring_ready_treats_any_non_not_applicable_gap_as_blocking`（第 523 行）覆盖此行为。

### 2. chapter_summary + report_level 不再重复输出

**PASS** — 已修复。

`report_level` 检查现在只存在于 `_validate_chapter_summary_issue()`（第 1594 行），`_validate_single_score_issue()` 中的重复检查已移除。`report_level` 在 validator 源码中仅出现 3 行（1594、1600、1605），全部在 `_validate_chapter_summary_issue` 内。

新测试 `test_chapter_summary_report_level_pointer_is_not_duplicated_for_scoring_ready`（第 453 行）断言 `len(chapter_pointer_issues) == 1`，直接验证无重复。

### 3. fail-closed / fallback conflict 不再 cascade duplicate

**PASS** — 已修复。

`_validate_source_documents()` 当前逻辑（第 1060-1127 行）：
- 第 1074 行：`RQV_FAIL_CLOSED_SOURCE` 后立即 `continue`，跳过后续 fallback 检查。
- 第 1076-1111 行：非 fail-closed 情况下，所有 fallback 矛盾原因累积为 `conflict_reasons` 列表，合并输出单条 `RQV_FALLBACK_CONFLICT`，然后 `continue`。
- 第 1113-1126 行：`unknown_upstream_failure_category` 单独输出 `RQV_FALLBACK_CONFLICT/material`。

新测试 `test_fallback_conflict_and_fail_closed_source_do_not_cascade_duplicates`（第 332 行）验证：
- `schema_drift + fallback_allowed=True`：1 条 `RQV_FAIL_CLOSED_SOURCE`，0 条 `RQV_FALLBACK_CONFLICT`。
- `not_found + fallback_allowed=False`：1 条 `RQV_FALLBACK_CONFLICT`。

### 4. 新增测试覆盖上述行为

**PASS** — 新增 6 个测试（从 19 增至 25）：

| 新增测试 | 覆盖 Finding |
|---|---|
| `test_fallback_conflict_and_fail_closed_source_do_not_cascade_duplicates` | GLM F1/F2 |
| `test_chapter_summary_report_level_pointer_is_not_duplicated_for_scoring_ready` | MiMo F1 |
| `test_scoring_ready_treats_any_non_not_applicable_gap_as_blocking` | `_is_blocking_gap` 语义对齐 |
| `test_jsonl_invalid_record_type_is_blocking` | GLM F5 |
| `test_accepted_baseline_is_blocking` | GLM F3 |
| `test_skipped_outside_chapter_summary_is_blocking` | GLM F4 |

GLM F6（`_validator_source()` 文件句柄）已修复为 `with open(...)` 语句（第 1026 行）。

### 5. 无边界外扩

**PASS** — 全部边界检查通过：

| Check | Result |
|---|---|
| 不导入 renderer/Service/CLI/quality_gate/extraction_score/repo/PDF/cache/source/Host/Agent/dayu | rg 无匹配 |
| 不导入 nav_data | rg 无匹配 |
| 不使用 extra_payload / **kwargs | 代码审查确认 |

## 验证命令结果

| Check | Result |
|---|---|
| validator tests | 25 passed |
| adjacent tests | 81 passed |
| coverage | 92% (≥80% target) |
| ruff | All checks passed |
| boundary rg | no matches |
| nav_data rg | no matches |

## 初始 Review Findings 状态

| Finding | Source | Status |
|---|---|---|
| F1: chapter_summary report_level 重复输出 | MiMo | **FIXED** — 移除 `_validate_single_score_issue` 中重复检查，测试验证 |
| F2: _validate_chapter_summary_issue 无条件阻断 report_level | MiMo | **OPEN** — 保持现状（更严格），plan 意图待 controller 裁决 |
| F3: scoring_ready 测试未验证 unknown_upstream_failure 消息 | MiMo | **OPEN** — minor，实现正确但测试不覆盖消息内容 |
| F1: fallback 重复 RQV_FALLBACK_CONFLICT | GLM | **FIXED** — 合并为单条 issue |
| F2: fail-closed cascade RQV_FALLBACK_CONFLICT | GLM | **FIXED** — continue 短路 |
| F3: 无 accepted_baseline 独立测试 | GLM | **FIXED** — 新增测试 |
| F4: 无 skipped + non-chapter_summary 测试 | GLM | **FIXED** — 新增测试 |
| F5: 无 invalid record_type 测试 | GLM | **FIXED** — 新增测试 |
| F6: _validator_source() 文件句柄 | GLM | **FIXED** — 改为 with 语句 |

## Residual Risk

| 风险 | 说明 |
|---|---|
| MiMo F2: 非 scoring_ready report_level 阻断 | 保持现状比 plan 更严格，无回归风险，待 controller 裁决是否需调整 |
| MiMo F3: unknown_upstream_failure 消息内容未测试 | minor，实现正确，重构风险低 |
