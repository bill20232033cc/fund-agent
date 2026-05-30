# MVP Gate 3 chapter_orchestrator review-fix re-review (MiMo)

日期：2026-05-30
角色：AgentMiMo review-fix re-reviewer
Gate：`MVP Gate 3: chapter_orchestrator review-fix re-review`
分类：`heavy`

## Verdict

**PASS**

DS-1/MiMo-M1 和 DS-2 修复均有效。typed `stop_reason` 字段消除了中文字符串匹配和重复推导；语义无回归；新增回归测试覆盖；无越界文件。

## 1. Review Scope

| 输入文件 | 用途 |
|---|---|
| `docs/reviews/mvp-gate3-chapter-orchestrator-review-fix-evidence-20260530.md` | AgentCodex 修复证据 |
| `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-mimo-20260530.md` | MiMo 初始实现 review（M1 finding） |
| `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-review-ds-20260530.md` | DS 初始实现 review（DS-1/DS-2 findings） |
| `fund_agent/services/chapter_orchestrator.py` | 修复后源码 |
| `tests/services/test_chapter_orchestrator.py` | 修复后测试 |

## 2. DS-1 / MiMo-M1 修复验证：消除中文 reason 字符串匹配

**原始 finding**: `_stop_reason_from_repair_decision()` 通过 `decision.reason == "章节修复预算耗尽。"` 匹配推导 `repair_budget_exhausted`，reason 文案变更会导致静默误分类。

**修复方案**: 在 `ChapterRepairDecision` dataclass 新增 `stop_reason: ChapterRunStopReason` 字段（L212），`_decide_repair()` 在每个分支直接设置 typed `stop_reason`，`_stop_reason_from_repair_decision()` 改为直接读取该字段。

**验证**:

| 检查项 | 状态 | 说明 |
|---|---|---|
| `ChapterRepairDecision` 新增 `stop_reason` 字段 | ✅ | L212，类型为 `ChapterRunStopReason` |
| `_decide_repair()` 每个分支设置 `stop_reason` | ✅ | L823: `none`, L832: `llm_unavailable`, L839: `llm_unavailable`, L848: `needs_more_facts`, L855: `_auditor_failure_stop_reason()`, L863: `repair_budget_exhausted`, L871: `none` (regenerate), L878: `_auditor_failure_stop_reason()` |
| `_stop_reason_from_repair_decision()` 不再匹配中文字符串 | ✅ | L962-964：只读 `decision.stop_reason`，无字符串匹配 |
| `repair_budget_exhausted` 在 budget 耗尽分支显式设置 | ✅ | L859-866：`remaining_budget <= 0` → `stop_reason="repair_budget_exhausted"` |
| 新增回归测试锁定语义不依赖 reason 文案 | ✅ | `test_repair_budget_exhausted_stop_reason_does_not_depend_on_reason_text` (L560-582)：用 `replace(decision, reason="可读文案允许调整。")` 验证 `stop_reason` 不变 |

**结论**: DS-1/MiMo-M1 修复有效。中文字符串匹配完全消除，budget exhausted 语义通过 typed 字段保证。

## 3. DS-2 修复验证：消除 `_stop_reason_from_repair_decision` 重复推导

**原始 finding**: `_stop_reason_from_repair_decision()` 重新检查 `_has_llm_unavailable_issue()`、`decision.action == "needs_more_facts"`、`audit_result.status == "blocked"` 等条件，与 `_decide_repair()` 重复推导且不完全一致。

**修复方案**: `_stop_reason_from_repair_decision()` 简化为直接返回 `decision.stop_reason`（L962-964），所有推导逻辑集中在 `_decide_repair()` 完成。新增 `_auditor_failure_stop_reason()` 辅助函数（L884-899）封装 `auditor_blocked` / `auditor_failed` 映射。

**验证**:

| 检查项 | 状态 | 说明 |
|---|---|---|
| `_stop_reason_from_repair_decision()` 无条件重新推导 | ✅ | L962-964：仅检查 `stop_reason == "none"` 时 raise，否则直接返回 |
| `_decide_repair()` 集中设置所有 stop_reason | ✅ | 8 个分支全部显式设置 `stop_reason` |
| `_auditor_failure_stop_reason()` 封装 blocked/failed 映射 | ✅ | L884-899：`audit_result.status == "blocked"` → `auditor_blocked`，否则 `auditor_failed` |
| LLM unavailable / needs_more_facts 不再被重复检查 | ✅ | `_stop_reason_from_repair_decision()` 不引用 `audit_result` |

**结论**: DS-2 修复有效。重复推导完全消除，所有 stop reason 推导集中在 `_decide_repair()`。

## 4. 语义回归检查

| 场景 | 期望 stop_reason | 实现位置 | 状态 |
|---|---|---|---|
| 预算耗尽 | `repair_budget_exhausted` | L859-866 | ✅ |
| LLM unavailable（全局 preflight） | `llm_unavailable` | L405-411 | ✅ |
| LLM unavailable（audit result issue） | `llm_unavailable` | L835-842 | ✅ |
| needs_more_facts | `needs_more_facts` | L843-850 | ✅ |
| auditor blocked（无 hint） | `auditor_blocked` | L851-858 → L884-899 | ✅ |
| auditor failed（无 hint） | `auditor_failed` | L875-881 → L884-899 | ✅ |

所有语义路径未回归。

## 5. 测试覆盖验证

| 检查项 | 状态 |
|---|---|
| 测试数量从 29 增加到 30 | ✅ 新增 1 个回归测试 |
| 新增测试验证 budget exhausted 不依赖 reason 文案 | ✅ `test_repair_budget_exhausted_stop_reason_does_not_depend_on_reason_text` |
| 已有 budget exhausted 集成测试仍通过 | ✅ `test_repair_budget_exhausted_returns_failed_stop_reason` |
| 已有 max_repair_attempts=0 测试仍通过 | ✅ `test_max_repair_attempts_zero_does_not_retry_after_audit_failure` |
| 全部 30 测试通过 | ✅ 30 passed in 0.76s |

## 6. 边界文件检查

| 检查项 | 状态 |
|---|---|
| 只修改 `chapter_orchestrator.py` 和 `test_chapter_orchestrator.py` | ✅ |
| 未修改 `docs/design.md`、`docs/implementation-control.md`、startup docs | ✅ |
| 未修改 Fund primitives、CLI、dayu、golden fixtures、score、quality gate | ✅ |
| 未新增 repository/PDF/source 访问 | ✅ |
| ruff check 通过 | ✅ All checks passed |

## 7. 残余 Finding

无新增 finding。初始 review 中的 M2（空 heading 不 fallback）、LOW findings（L1、DS-3 至 DS-7）均为防御性改进，不阻断，与本次修复无关。

## 8. Validation

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
30 passed in 0.76s
```

```text
uv run ruff check fund_agent/services/chapter_orchestrator.py tests/services/test_chapter_orchestrator.py
All checks passed!
```
