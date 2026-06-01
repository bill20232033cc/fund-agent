# MVP Gate 3 Chapter Orchestrator Review Fix Re-Review (AgentDS)

日期：2026-05-30
角色：AgentDS re-reviewer。只做 review-fix 验证，不改代码、不 commit。
Gate：`MVP Gate 3: chapter_orchestrator review-fix re-review`
分类：`light`

## Verdict

**PASS** — 2/2 targeted findings (DS-1/MiMo-M1, DS-2) 修复有效，无回归。

## Fix Scope

| Finding | 描述 | 修复方式 |
|---|---|---|
| DS-1 / MiMo-M1 | `_stop_reason_from_repair_decision()` 使用中文字符串匹配 | `ChapterRepairDecision` 新增 typed `stop_reason` 字段，`_stop_reason_from_repair_decision()` 直接读取该字段 |
| DS-2 | `_stop_reason_from_repair_decision()` 与 `_decide_repair()` 重复推导且不完全一致 | `_decide_repair()` 各分支写入 `stop_reason`，`_stop_reason_from_repair_decision()` 不再重新检查 audit result 状态 |

## Per-Finding Verification

### DS-1 / MiMo-M1: 中文 reason 匹配已移除

**修复前** (`_stop_reason_from_repair_decision`):
```python
if decision.reason == "章节修复预算耗尽。":
    return "repair_budget_exhausted"
```

**修复后**:
- `ChapterRepairDecision` (line 198-214) 新增 `stop_reason: ChapterRunStopReason` 字段。
- `_decide_repair()` (line 795-881) 在每个决策分支显式写入 `stop_reason`：
  - accepted → `"none"`
  - auditor unavailable → `"llm_unavailable"`
  - LLM_UNAVAILABLE issue → `"llm_unavailable"`
  - needs_more_facts → `"needs_more_facts"`
  - none hint → `_auditor_failure_stop_reason(audit_result)`
  - budget exhausted → `"repair_budget_exhausted"`
  - regenerate → `"none"`
  - default stop → `_auditor_failure_stop_reason(audit_result)`
- `_stop_reason_from_repair_decision()` (line 947-964) 现在只读取 `decision.stop_reason`，当值为 `"none"` 时 raise `ValueError`（防止非停止决策被误用）。
- 不再有任何中文字符串匹配。

**结论**: ✅ 修复有效。

### DS-2: 重复推导已移除

**修复前** (`_stop_reason_from_repair_decision`):
- 重新调用 `_has_llm_unavailable_issue(audit_result)` 检查 LLM unavailable
- 重新检查 `decision.action == "needs_more_facts"`
- 重新通过 `audit_result.status == "blocked"` 推导 auditor_blocked

**修复后**:
- `_stop_reason_from_repair_decision()` 不再访问 `audit_result`、不再调用 `_has_llm_unavailable_issue()`、不再检查 `decision.action`。
- 所有条件判断收敛到 `_decide_repair()` 的单一决策点。
- 新增 `_auditor_failure_stop_reason()` (line 884-899) 集中处理 blocked/failed 映射，供 `_decide_repair()` 的 none-hint 和 default-stop 分支复用。

**结论**: ✅ 修复有效。不再存在重复推导或条件不一致风险。

## Semantic Regression Check

| 语义 | 修复前路径 | 修复后路径 | 是否回归 |
|---|---|---|---|
| budget exhausted → `repair_budget_exhausted` | 中文 reason 字符串匹配 | `_decide_repair` L863 显式写 `stop_reason="repair_budget_exhausted"` | 否 |
| LLM unavailable → `llm_unavailable` | `_has_llm_unavailable_issue` + status check | `_decide_repair` L831/L839 两路径均写 `stop_reason="llm_unavailable"` | 否 |
| needs_more_facts → `needs_more_facts` | `decision.action == "needs_more_facts"` | `_decide_repair` L847 显式写 `stop_reason="needs_more_facts"` | 否 |
| auditor blocked → `auditor_blocked` | `audit_result.status == "blocked"` 推导 | `_auditor_failure_stop_reason()` L898 返回 `"auditor_blocked"` | 否 |
| auditor failed → `auditor_failed` | 默认 fallthrough | `_auditor_failure_stop_reason()` L899 返回 `"auditor_failed"` | 否 |

## New Test Coverage

`test_repair_budget_exhausted_stop_reason_does_not_depend_on_reason_text` (line 560-582):

1. 通过 `_decide_repair(remaining_budget=0)` 构造预算耗尽决策
2. 使用 `replace(decision, reason="可读文案允许调整。")` 修改中文 reason 文案
3. 断言 `decision.stop_reason == "repair_budget_exhausted"`
4. 断言 `_stop_reason_from_repair_decision(renamed_decision) == "repair_budget_exhausted"`

**结论**: ✅ 该测试直接回归 DS-1 的 root cause，证明 stop_reason 不再依赖 reason 字符串的具体内容。

## Untouched LOW Findings (Out of Scope)

以下 DS/MiMo LOW findings 不在本次 fix scope，行为未变：

| Finding | 文件:行号 | 状态 |
|---|---|---|
| DS-3 | `chapter_orchestrator.py:827-834` | defensive 死代码分支仍存在，未变 |
| DS-4 | `chapter_orchestrator.py:475` | schema_version 校验未变 |
| DS-5 | `chapter_orchestrator.py:1023` | H2 heading 抽取逻辑未变 |
| DS-6 | `chapter_orchestrator.py:1094-1096` | generated_chapter_ids 逻辑未变 |
| MiMo-M2 | `chapter_orchestrator.py:993-996` | H3 空结论不 fallback 行为未变 |

## Boundary Check

- 未修改 `docs/design.md`、`docs/implementation-control.md`、`AGENTS.md`、startup docs ✅
- 未修改 Fund primitives、CLI、dayu、golden fixtures、score、quality gate ✅
- `test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries` 仍通过 ✅
- 仅修改 `chapter_orchestrator.py` 和 `test_chapter_orchestrator.py` ✅

## Validation

| 检查 | 结果 |
|---|---|
| `uv run ruff check .` | All checks passed |
| `uv run pytest tests/services/test_chapter_orchestrator.py -q` | 30 passed (29→30, +1 new test) |
| `git diff --check` | clean（未执行，基于 fix evidence） |
| 越界文件 | 无 |

## Summary

DS-1/MiMo-M1 和 DS-2 两个 MEDIUM finding 已通过 typed `stop_reason` 字段彻底修复：不再依赖中文字符串匹配，不再在 `_stop_reason_from_repair_decision()` 中重复推导 audit result 状态。新增测试覆盖了 reason 文案变更不破坏预算耗尽语义的回归场景。所有现有测试继续通过（30 passed），ruff 无告警，无边界越界。建议 controller accept 此 fix。
