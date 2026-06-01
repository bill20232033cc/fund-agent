# MVP Gate 3 chapter_orchestrator implementation review (AgentDS)

日期：2026-05-30
角色：AgentDS implementation reviewer。只 review，不改代码、不 commit。
Gate：`MVP Gate 3: chapter_orchestrator implementation gate`
分类：`heavy`

## Verdict

**PASS** — 7 findings，0 BLOCKING。所有 finding 均为 MEDIUM 或 LOW，不影响当前 fail-closed 安全性。建议 controller 在 accept 前裁决 MEDIUM finding DS-1（stop reason 字符串匹配）。

## Pre-review context

已读真源：`AGENTS.md`、`docs/current-startup-packet.md`、`docs/design.md` Route C/Gate 3 段落、`docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`、`docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md`、`docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md`。

已 review 的文件：`fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/__init__.py`、`tests/services/test_chapter_orchestrator.py`、`fund_agent/README.md`、`tests/README.md` 的 `git diff`。

## Findings

### DS-1 (MEDIUM) `_stop_reason_from_repair_decision` 使用中文字符串匹配替代 typed 决策推导

**文件**: `fund_agent/services/chapter_orchestrator.py:940`

```python
if decision.reason == "章节修复预算耗尽。":
    return "repair_budget_exhausted"
```

`_decide_repair()` 已经返回 typed `ChapterRepairDecision(action=...)` 。`_stop_reason_from_repair_decision()` 应通过 `decision.action` 和调用方传递的 `remaining_budget` 推导 stop reason，而不应匹配 `decision.reason` 的可读中文文本。当前 reason 字符串如果被任何人修改，stop reason 会静默变成 `auditor_failed`，破坏 budget exhaustion 语义且不会触发测试失败。

**建议**: 在 `_decide_repair` 返回值中携带 `remaining_budget` 上下文，或让 `_stop_reason_from_repair_decision` 接受 `remaining_budget` 参数，通过 `decision.action == "stop" and budget_exhausted` 推导 `repair_budget_exhausted`。若短期不改，至少加一个显式 unit test 锁定该字符串不变。

### DS-2 (MEDIUM) `_stop_reason_from_repair_decision` 与 `_decide_repair` 的 condition 重复推导且不完全一致

**文件**: `fund_agent/services/chapter_orchestrator.py:936-944`

`_stop_reason_from_repair_decision()` 重新检查 `_has_llm_unavailable_issue(audit_result)`（line 936）和 `decision.action == "needs_more_facts"`（line 938），这些条件 `_decide_repair()` 已经处理过。当前因为调用顺序保证（`_decide_repair` 在 LLM unavailable 时不会返回 `needs_more_facts`），行为正确，但存在两处细微不一致：

1. Line 936 的 `_has_llm_unavailable_issue` 不检查 `audit_result.llm.status == "blocked"`，而 `_decide_repair` line 831 要求两者同时成立。若 future auditor 在 `status != "blocked"` 时也能产生 `LLM_UNAVAILABLE` issue，此处会过度返回 `llm_unavailable`。

2. Line 942 通过 `audit_result.status == "blocked"` 推导 `auditor_blocked`，但没有区分该 blocked 是否源于 LLM unavailable（`_decide_repair` 已经排除了这种情况）。

**建议**: `_stop_reason_from_repair_decision` 应直接接收 `_decide_repair` 的决策上下文（action + 触发条件枚举），而非重新推导 audit result 状态。这是 maintainability 问题，当前无 bug。

### DS-3 (LOW) `_decide_repair` 中 `run_llm_audit and not auditor_available` 分支是死代码

**文件**: `fund_agent/services/chapter_orchestrator.py:824-830`

全局 preflight（line 403-409）在进入任何章节前已检查 `policy.run_llm_audit and llm_clients.auditor is None` 并返回全局 blocked。因此 `_decide_repair` line 824 的 `run_llm_audit and not auditor_available` 分支在正常 orchestration 流程中永远不可达。如果该分支以某种方式被触发（如绕过 preflight 的测试路径），其最终 `stop_reason` 会经由 `_stop_reason_from_repair_decision` 变成 `auditor_blocked`，而非 plan §8.2 指定的 `llm_unavailable`。

**建议**: 保留 defensive 分支但加注释说明可达性；或在此分支设置 `stop_reason="llm_unavailable"` 以 match plan 契约。

### DS-4 (LOW) `_validate_orchestration_input` 的 schema_version 检查可能有冗余

**文件**: `fund_agent/services/chapter_orchestrator.py:473-474`

```python
if input_data.schema_version != CHAPTER_ORCHESTRATOR_SCHEMA_VERSION:
    raise ValueError(...)
```

`ChapterOrchestratorSchemaVersion` 是 `Literal["chapter_orchestrator.v1"]`，Python type checker 在静态分析时已保证只有该值。运行时校验是 fail-closed 防御层，保留了未来新增 schema version 的扩展能力。建议加一行注释说明这是 forward-compat guard，不算 bug。

### DS-5 (LOW) `_extract_heading_block` 对 `##` heading 只截止到 `## `，不会截止到 `### `

**文件**: `fund_agent/services/chapter_orchestrator.py:1023`

```python
if heading.startswith("##") and stripped.startswith("## "):
    break
```

Plan §10 规定 `## 结论要点` 截止到下一个 `## `。当前实现正确：H2 heading 的结论块不会被 `### ` 打断，只被 `## ` 打断。但 test `test_h2_conclusion_extraction_stops_before_next_h2`（line 712）只用 `## 详细情况` 做 next heading，未覆盖文档中先出现 `### 某子节` 的场景。当前行为符合 plan，非 bug，但建议加一个交叉 heading 测试（H2 conclusion + 中间 `### 子节` 不被截断）。

### DS-6 (LOW) `generated_chapter_ids` 对 writer blocked 和 global blocked 的语义区分依赖 `attempts` 是否为空

**文件**: `fund_agent/services/chapter_orchestrator.py:1074-1076`

```python
generated_chapter_ids = tuple(
    result.chapter_id for result in chapter_results if result.attempts and result.status != "skipped"
)
```

对于 writer `llm_unavailable`（writer 为 None → `write_chapter` 被调用 → 返回 blocked → 产生一个 `ChapterAttemptRecord`），该章节会进入 `generated_chapter_ids`。对于 global blocked（`fund_type_unknown` / auditor `llm_unavailable`），`attempts=()` → 不进入。语义合理，但依赖 `attempts` 是否为空作为“是否尝试过生成”的 proxy。如果 future 修改让某些 blocked 场景也创建 attempt record，会改变 `generated_chapter_ids` 行为。建议加注释说明该约定。

### DS-7 (LOW) README 代码阅读顺序更新为包含 orchestrator

**文件**: `fund_agent/README.md:43`、`tests/README.md:55`

`fund_agent/README.md` 在阅读顺序中新增 `fund_agent/services/chapter_orchestrator.py`（第 3 位），并在 Service 边界描述中新增一句话说明 orchestrator 的定位和限制。`tests/README.md` 新增一行测试描述和一条运行命令。两处更新均只同步当前事实，不写未来功能。✓

## Cross-cutting checks

### Service/Fund 边界

Orchestrator 通过显式导入消费 `chapter_facts`、`chapter_writer`、`chapter_auditor` 的 public API 和类型，未重新实现 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点或审计规则。fact_provider 通过注入复用，不从零构造。✓

### 禁止越界

- 未导入 `documents`、`repository`、`cache`、`pdf`、`source`、`downloader`、`parser`、`dayu`、`openai`、`httpx` ✓（见 `test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries`）
- 未修改 golden、score、snapshot、quality gate、FQ0-FQ6、final judgment ✓
- 未新增 CLI `--use-llm` ✓
- 未实现第 0/7 章生成 ✓（policy 拒绝 0/7、generated 范围只含 1-6）
- 未实现 final assembler、Host/Agent/dayu ✓

### 显式参数无 `extra_payload`

所有参数均通过 typed dataclass（`ChapterOrchestrationInput`、`ChapterOrchestrationPolicy`、`ChapterOrchestratorLLMClients`）或显式 keyword-only 参数传递。未发现 `extra_payload` 使用。✓

### Writer stop reason 映射完整性

`_WRITER_STOP_REASON_MAPPING` 覆盖当前 `ChapterWriteStopReason` 全部 10 个值（不含 `none`），每个映射为唯一 `(status, stop_reason)`。未在表中的值会 raise `ValueError`（fail-closed）。test `test_every_writer_stop_reason_maps_to_exact_run_reason` 通过 `set(expected) == set(ChapterWriteStopReason.__args__) - {"none"}` 做运行时完备性断言，未来若 Gate 2 新增 stop reason 测试会直接失败。✓

### Auditor unavailable early stop

`orchestrate_chapters()` line 403-409 在进入任何章节前检查 `policy.run_llm_audit and llm_clients.auditor is None`，直接返回全局 `blocked`，`generated_chapter_ids=()`，不调用 writer，不进入 repair loop。✓

### Repair decision / budget / fail_fast / partial

- `_decide_repair()` 决策表与 plan §8.2 一致（顺序、条件、action）✓
- `max_repair_attempts=0` 在首次 audit 失败后 `remaining_budget=0`，`_decide_repair` 返回 `stop`，不 retry ✓
- `patch` → best-effort `regenerate`，受 budget 限制 ✓
- `needs_more_facts` 不重试，不 source probing ✓
- `fail_fast=True` 首个非 accepted 后 skip 后续章节 ✓
- `partial` status 当至少一个 accepted 但非全部时正确产生 ✓

### Accepted conclusion extraction hard cap

- `MAX_ACCEPTED_CONCLUSION_CHARS = 500` ✓
- `### 结论要点` 和 `## 结论要点` 均支持 ✓
- heading extraction 截止到下一个同级或更高级 heading ✓
- fallback 只取前 3 个非空行 ✓
- 不做 LLM 总结、不改写、不生成新判断 ✓

### Tests 覆盖关键 fail-closed 行为

29 tests，包括：输入互斥/同源校验、policy 范围/预算校验、happy path、writer unavailable、auditor unavailable early stop、writer stop reason 全量映射、writer/auditor 异常、unknown fund type、repair retry/budget exhaustion、`max_repair_attempts=0`、LLM_UNAVAILABLE stop、`needs_more_facts`、`fail_fast` true/false、conclusion heading/H2/fallback/500 cap 提取、chapter 0/7 exclusion、façade provider 注入、projection 覆盖校验、import 边界。✓

未覆盖：交叉 heading 场景（H2 conclusion 中含 `### 子节`）、defensive 死代码路径的 stop_reason 回归测试。均 ≤LOW。

### README 同步

`fund_agent/README.md` 和 `tests/README.md` 只同步当前实现事实，不越界写 future design、CLI、dayu。✓

## Residual risks

| Risk | Disposition | DS review note |
|---|---|---|
| `patch` 映射为 best-effort regenerate | 与 plan 一致；budget-bounded | 已有测试覆盖 |
| `partial` result Gate 4 消费契约 | Gate 4 裁决 | Gate 3 不预判 |
| E2 source verification | 已延期 | Gate 3 无 source 访问 |
| Chapter 5 cross-period | 已延期 | 无 source probing |
| 无生产 LLM provider | 显式注入 | Gate 4 裁决 |
| `_stop_reason_from_repair_decision` 字符串匹配脆弱 | **DS-1**，新增 | 建议 controller 在 accept 前裁决 |
| `_stop_reason_from_repair_decision` 重复推导 | **DS-2** | maintainability，无当前 bug |

## Validation reviewed

Implementation evidence 报告的验证结果已确认：

- `ruff check .` — All checks passed ✓
- `pytest tests/services/test_chapter_orchestrator.py -q` — 29 passed ✓
- `pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q` — 51 passed ✓
- `pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` — 1039 passed, 91.73% total, orchestrator 93% ✓
- `git diff --check` — clean ✓

未重新执行验证命令；本 review 基于 implementation evidence 记录和源码静态分析。

## Summary

实现严格遵循 accepted plan 的 public contract、data flow、repair decision table、writer stop reason mapping、conclusion extraction 和边界约束。7 个 finding 中最高为 MEDIUM（DS-1 字符串匹配、DS-2 重复推导），均不影响当前 fail-closed 语义，不构成 BLOCKED。tests 覆盖 plan 要求的全部关键 fail-closed 路径。无越界导入、无 `extra_payload`、无第 0/7 章生成、无 repository/source/dayu 访问。
