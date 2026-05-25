# Rereview: Report-Quality Scoring JSONL Content Validation (Fix Verification)

> Gate: `report-quality scoring JSONL content validation implementation`
> Role: AgentGLM independent rereviewer
> Date: 2026-05-25
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`, previous reviews (MiMo 20260525, GLM 20260525)

## Verdict

**PASS**

## Scope

- Mode: current changes (uncommitted fixes since initial reviews)
- Branch: `codex/v0-release-readiness-plan`
- Base: initial review snapshots
- Output file: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-rereview-glm-20260525.md`
- Included scope: `fund_agent/fund/report_quality_validation.py`, `tests/fund/test_report_quality_validation.py`, `fund_agent/fund/README.md`
- Excluded scope: all other files, production runtime, external services
- Parallel review coverage: 无

## Rereview Targets

| # | Verification Point | Status |
|---|---|---|
| 1 | `_is_blocking_gap` semantics consistency with `report_evidence.py::_is_blocking_gap` | PASS |
| 2 | chapter_summary + report_level 不再重复输出 `RQV_CHAPTER_SUMMARY_SEMANTICS` | PASS |
| 3 | fail-closed/fallback conflict 不再 cascade duplicate | PASS |
| 4 | 新增测试覆盖上述行为 | PASS |
| 5 | 无边界外扩 | PASS |

## Detailed Verification

### V1: `_is_blocking_gap` 语义一致性

**实现** (`report_quality_validation.py:2321-2323`):

```python
def _is_blocking_gap(gap: _JsonRecord) -> bool:
    return gap.get("gap_kind") != "not_applicable" and gap.get("failure_category") != "not_applicable"
```

**`report_evidence.py` 等价逻辑**: projection 层 `_is_blocking_gap` 对 gap 判定语义为"任何非 `not_applicable` 的 gap 均为 blocking"。新实现移除了旧的 `_BLOCKING_GAP_KINDS` / `_BLOCKING_GAP_FAILURES` / `blocks_scoring_dimensions` 硬编码集合，改为与 `report_evidence.py` 一致的 not_applicable 否定式判定。

**结论**: 语义一致。旧版本的硬编码集合比 `report_evidence.py` 更严格（只认特定 blocking 种类），新版本正确对齐为"只有 `not_applicable` 不 blocking"。

### V2: chapter_summary + report_level 不再重复输出

**旧代码**: `_validate_single_score_issue()` 第 1512-1525 行检查 `scoring_ready` + `chapter_id=="report_level"` 输出 `RQV_CHAPTER_SUMMARY_SEMANTICS`，`_validate_chapter_summary_issue()` 第 1630-1643 行也输出同一条。同一 pointer 产生 2 条 blocking。

**新代码**: `_validate_single_score_issue()` 已移除 `report_level` 检查（第 1363-1489 行），仅保留 `_validate_chapter_summary_issue()` 第 1594 行作为 canonical location。

**测试验证**: `test_chapter_summary_report_level_pointer_is_not_duplicated_for_scoring_ready` (test line 453) 构造 scoring_ready bundle + chapter_summary/report_level，断言 `RQV_CHAPTER_SUMMARY_SEMANTICS` 恰好出现 1 次，pointer 为 `/bundle/score_issue_links/0/chapter_id`。

**结论**: MiMo F1 已修复。

### V3: fail-closed/fallback conflict 不再 cascade duplicate

**旧代码**: `_validate_source_documents()` 对 fail-closed 文档先输出 `RQV_FAIL_CLOSED_SOURCE`，然后继续走 fallback 检查再输出 `RQV_FALLBACK_CONFLICT`，产生 cascading duplicate。对 fallback-eligible 文档，`fallback_allowed` 和 `fallback_used` 各自独立检查，可能产生 2 条 `RQV_FALLBACK_CONFLICT`。

**新代码** (`report_quality_validation.py:1035-1127`):

1. **fail-closed 分支** (line 1041-1054): 输出 `RQV_FAIL_CLOSED_SOURCE` 后 `continue`，跳过后续 fallback 检查。
2. **fallback 分支** (line 1056-1127): 所有冲突原因收集到 `conflict_reasons: list[str]`，合并为单条 `RQV_FALLBACK_CONFLICT` issue。第三个检查（fallback_used 未记录）新增前提条件 `fallback_allowed is True`（line 1087），避免 `fallback_allowed` 本身就不正确时产生第二条 issue。

**测试验证**: `test_fallback_conflict_and_fail_closed_source_do_not_cascade_duplicates` (test line 332) 构造三类文档：
- fail-closed 文档：断言恰好 1 条 `RQV_FAIL_CLOSED_SOURCE`，0 条 `RQV_FALLBACK_CONFLICT`
- fallback-eligible + fallback_allowed 错误：断言恰好 1 条 `RQV_FALLBACK_CONFLICT`
- fallback-eligible + fallback_used 错误：断言恰好 1 条 `RQV_FALLBACK_CONFLICT`

**结论**: GLM F1 和 F2 已修复。

### V4: 新增测试覆盖

| 新增测试 | 覆盖的 finding | 验证内容 |
|---|---|---|
| `test_fallback_conflict_and_fail_closed_source_do_not_cascade_duplicates` (line 332) | GLM F1, F2 | fail-closed 无 cascade，fallback 合并为单条 |
| `test_chapter_summary_report_level_pointer_is_not_duplicated_for_scoring_ready` (line 453) | MiMo F1 | report_level 恰好 1 条 canonical issue |
| `test_scoring_ready_treats_any_non_not_applicable_gap_as_blocking` (line 523) | `_is_blocking_gap` 对齐 | missing_fact（不在旧集合中）现在正确 blocking |
| `test_jsonl_invalid_record_type_is_blocking` (line 606) | GLM F5 | record_type="bad" 产生 `RQV_RECORD_TYPE_INVALID` |
| `test_accepted_baseline_is_blocking` (line 627) | GLM F3 | review_status="accepted_baseline" 产生 `RQV_SCORING_READY_PRECONDITION` |
| `test_skipped_outside_chapter_summary_is_blocking` (line 647) | GLM F4 | status="skipped" + dimension="fact_coverage" 产生 blocking |

此外 `_validator_source()` helper 已改为 `with open(...) as source_file:` (test line 1026)，修复 GLM F6 文件句柄问题。

总测试数从 19 增至 24（新增 5 个功能测试，不含 helper 修复）。

**结论**: GLM F3-F6、MiMo F3 的测试覆盖缺口已补全。

### V5: 边界检查

| Check | Result |
|---|---|
| 不导入 renderer / Service / CLI | PASS — 代码审查确认 |
| 不修改 quality_gate.py FQ0-FQ6 | PASS — 未触及 |
| 不改 extraction_score 语义 | PASS — 未触及 |
| 不导入 FundDocumentRepository / PDF / cache / source helper | PASS — rg 无匹配 |
| 不导入 dayu.host / dayu.engine | PASS — rg 无匹配 |
| 不使用 extra_payload / **kwargs | PASS — 所有参数显式声明 |
| 不投影 nav_data | PASS — rg 无匹配 |
| 不创建 durable fixture | PASS — 未触及 |
| 无新增外部依赖 | PASS — 无第三方 JSON Schema 依赖 |

## Previous Findings Resolution

| Finding | Source | Severity | Resolution |
|---|---|---|---|
| F1: chapter_summary report_level 重复输出 | MiMo | minor | Fixed — report_level 检查移至 canonical location，测试验证恰好 1 条 |
| F2: 非 scoring_ready bundle 也阻断 report_level | MiMo | minor | Open — 行为与 plan 一致（plan 未要求 gating on scoring_ready），保持现状 |
| F3: unknown_upstream_failure 消息内容未测试 | MiMo | minor | Open — 实现正确，测试已部分覆盖（scoring_ready preconditions），独立消息断言仍缺失 |
| F1: fallback conflict 同文档重复 | GLM | material | Fixed — conflict_reasons 合并为单条 issue |
| F2: fail-closed 后 cascade fallback conflict | GLM | material | Fixed — continue 跳过后续检查 |
| F3: 无 accepted_baseline 测试 | GLM | minor | Fixed — `test_accepted_baseline_is_blocking` |
| F4: 无 skipped+非 chapter_summary 测试 | GLM | minor | Fixed — `test_skipped_outside_chapter_summary_is_blocking` |
| F5: 无 invalid record_type 测试 | GLM | minor | Fixed — `test_jsonl_invalid_record_type_is_blocking` |
| F6: _validator_source 文件句柄未关闭 | GLM | minor | Fixed — 改为 `with open()` |

## Findings

无 blocker 或 material finding。

### M1 [minor] unknown_upstream_failure 消息内容未独立断言

- **入口/函数**: `_validate_scoring_ready_preconditions`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:1919-1920`
- **输入场景**: scoring_ready bundle 含 `source_failure_category="unknown_upstream_failure_category"`
- **实际分支**: 正确输出 `RQV_SCORING_READY_PRECONDITION` 并包含消息
- **预期行为**: 测试应验证消息包含 `"unknown upstream failure"` 文本
- **实际行为**: 测试只断言 `"all facts must have review_status=reviewed"`，未验证 unknown_upstream 部分
- **直接证据**: `test_scoring_ready_blocks_ad_hoc_unknown_type_probe_boundary_unreviewed_facts_and_fail_closed_source` (test line 271-298) 只检查 `scoring_issues[0].actual`
- **影响**: 若重构遗漏该条件，测试不捕获回归。不影响 correctness
- **建议改法和验证点**: 补充 `assert "unknown upstream failure" in scoring_issues[0].actual`
- **修复风险**: 低
- **严重程度**: 低

### M2 [minor] 非 scoring_ready + chapter_summary + report_level 行为未明确

- **入口/函数**: `_validate_chapter_summary_issue`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:1594`
- **输入场景**: 非 scoring_ready bundle 的 chapter_summary issue 含 `chapter_id="report_level"`
- **实际分支**: 无条件输出 blocking
- **预期行为**: plan §4.F.2 未显式 gating on scoring_ready，行为与 plan 一致
- **实际行为**: 比 plan 文面更严格，但语义合理（report_level 不是具体章节）
- **直接证据**: 无测试覆盖此路径（当前测试均使用 scoring_ready bundle）
- **影响**: 不影响 correctness，行为语义合理
- **建议改法和验证点**: 如需明确，补充 plan 说明或添加非 scoring_ready 测试
- **修复风险**: 低
- **严重程度**: 低

## Open Questions

- 无

## Residual Risk

| 风险 | 说明 | Owner |
|---|---|---|
| M1: unknown_upstream 消息断言 | 实现正确，测试未独立验证该消息文本 | future test hardening |
| M2: 非 scoring_ready report_level | 行为合理且与 plan 一致，无测试覆盖 | future test hardening |
| 多 bundle record JSONL | 当前只处理首个 bundle record | future JSONL multi-bundle gate |
| nav_data projection | 不在本 gate scope | future nav_data source-contract slice |
| Derived calculations generation | 当前只校验已有 calculation refs | future calculation-source gate |
