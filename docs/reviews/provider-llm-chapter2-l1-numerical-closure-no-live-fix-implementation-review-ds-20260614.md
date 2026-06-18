# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Review (AgentDS)

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Gate`。

Role: AgentDS reviewer，不是 controller，不是 fix worker。

Review target diff:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-evidence-20260614.md`

## Evidence Inputs

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-20260614.md`
- Implementation evidence artifact
- `git diff` for target files only

控制面确认：当前 gate 为 `standard`；release/readiness 仍为 `NOT_READY`；年度报告源策略为 EID single-source/no-fallback。

## Review Findings

### F1 — Implementation exactly matches accepted plan and controller amendments. Severity: INFO.

**验证项**：

| Plan requirement | Implementation | Match? |
|---|---|---|
| `_has_l1_numerical_closure_repair_issue` helper with deterministic `programmatic:L1` prefix detection | `chapter_writer.py:1268-1283`，`issue_id.startswith("programmatic:L1")` | ✓ |
| `_ch2_l1_repair_guidance_prompt` returns checklist only for chapter 2 + L1 repair | `chapter_writer.py:1286-1316`，guard 为 `chapter.chapter_id != 2 or not _has_l1_numerical_closure_repair_issue(repair_context)` | ✓ |
| Checklist rendered adjacent to existing `repair_context` in `_chapter_prompt_fragments()` | `chapter_writer.py:737-744`，`"\n".join()` 拼接两个 fragment，filter 空串 | ✓ |
| `ChapterRepairContext` fields unchanged | 对比 diff，struct 定义无修改 | ✓ |
| `_repair_context_prompt()` stays generic | `chapter_writer.py:1456-1479`，diff 未触及 | ✓ |
| No typed patch API, no budget change, no `_audit_numerical_closure()` change | diff 未触及相关函数 | ✓ |
| Detection is `programmatic:L1` prefix only, no sanitized-message fallback (DS F1 amendment applied) | `_has_l1_numerical_closure_repair_issue` 仅检查 `issue_id.startswith("programmatic:L1")` | ✓ |
| Service/Agent correction-text alignment verified before deciding not to edit (DS F2/MiMo F6 amendment) | Evidence 记录：Service 现有 L1 repair-context test 已证明 `programmatic:L1` issue ids 传播；新增 orchestrator assertion 证明 checklist 到达 writer `user_prompt`。无需修改 `chapter_orchestrator.py` / `repair.py` | ✓ |

**结论**：实现忠实还原 accepted plan 全部 5 个 implementation steps，3 个 controller amendments 全部满足。

### F2 — L1 blocker semantics fully preserved, audit not weakened. Severity: INFO.

**验证项**：

- `_audit_numerical_closure()` 未修改。L1 仍是 blocking programmatic audit rule。
- 新增 checklist 强化 repair attempt 的锚点放置指令，不改变 L1 判定逻辑。
- After-repair fail path (`repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`) 保持不变。
- Orchestrator test `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` 通过。

**结论**：L1 语义未削弱，fail-closed 行为完整保留。

### F3 — Repair budget, action and stop reason unchanged; no typed patch API. Severity: INFO.

**验证项**：

- `max_repair_attempts` / `max_content_repair_attempts` 无变更。
- Repair action 仍为 whole-chapter regenerate（checklist 仅指导 regenerate 内容，不改变 action 语义）。
- Stop reason 仍为 `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`。
- 无 `ChapterPatchRequest`、typed patch mode、partial chapter edit 等新 API。

**结论**：完全满足 plan non-goal 约束。

### F4 — Helper detection is narrow and deterministic via `programmatic:L1` only. Severity: INFO.

**验证项**：

- `_has_l1_numerical_closure_repair_issue` 仅检查 `issue_id.startswith("programmatic:L1")`。
- 不检查 `previous_messages`、sanitized text、provider output 或 indirect diagnostics。
- `repair_context is None` 时直接返回 `False`。
- 无 `optionally` 后备逻辑（plan DS F1 amendment 要求移除的 fallback）。

**结论**：检测严格 narrow，满足 plan 和 amendment 要求。

### F5 — Checklist rendered only for Chapter 2 L1 repair context; absent elsewhere. Severity: INFO.

**验证项**：

Guard: `chapter.chapter_id != 2 or not _has_l1_numerical_closure_repair_issue(repair_context)`。

`test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context` 覆盖三个 absent 场景：

| 场景 | Result |
|---|---|
| Chapter 2 initial attempt（无 repair context） | checklist absent ✓ |
| Chapter 1 + L1 repair context | checklist absent ✓ |
| Chapter 2 + non-L1 repair context（`programmatic:C2:item`） | checklist absent ✓ |

**结论**：checklist 作用域严格限定，不存在泄漏。

### F6 — Tests are sufficient and no-live; no selector/test fragility. Severity: INFO.

**验证项**：

新增 tests：

| Test | 文件 | 覆盖目标 |
|---|---|---|
| `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist` | `tests/fund/test_chapter_writer.py` | Writer prompt 渲染 checklist，含 8 个语义 assertions + `extra_payload` guard |
| `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context` | `tests/fund/test_chapter_writer.py` | 3 个 absent 场景 |
| 扩展 `test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair` | `tests/services/test_chapter_orchestrator.py` | Orchestrator 路径：checklist 到达 writer `user_prompt`，3 个 assertions |

已有 regression tests 保持通过：

- `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` — 确认 after-repair fail-closed 语义
- L1 auditor tests 全套 — 确认 L1 判定逻辑不变
- `test_repair_context_is_rendered_into_writer_prompt_without_extra_payload` — 确认 `extra_payload` 不存在（该 test 不受 checklist 注入影响，因为其 repair context 不包含 `programmatic:L1`）

所有 tests 均为 no-live：使用 `FakeChapterLLMClient`、`FakeAuditLLMClient`，不涉及 provider/network/source/PDF。

Test selector 观察：`repair_context` 关键词在 `-k "ch2_l1_repair or l1_numerical_closure or repair_context"` 中较宽泛，会匹配所有含 `repair_context` 的 test（当前共 6 个）。这属于合理范围，不构成 selector 脆弱性，但 future 若新增大量无关 `repair_context` tests 可能拉宽测试面。

**结论**：red-test-first 证据充分，positive/negative/regression 覆盖完整。

### F7 — Worker avoided forbidden files and scope. Severity: INFO.

**验证项**（对照 plan 的 Explicitly Disallowed Write Targets）：

| Forbidden target | 是否被修改 |
|---|---|
| `docs/design.md` | 否 |
| `docs/implementation-control.md` | 否 |
| `docs/current-startup-packet.md` | 否 |
| root `README.md` | 否 |
| `fund_agent/services/chapter_orchestrator.py` | 否（经 red assertion 验证无需修改） |
| `fund_agent/agent/repair.py` | 否 |
| `tests/agent/test_repair_policy.py` | 否 |
| provider config/defaults | 否 |
| source policy, fallback, Docling, annual-report repository code | 否 |
| CLI live/provider commands, readiness/release/PR artifacts | 否 |

Worker 仅修改了 plan 允许的 3 个 core files + evidence artifact。

**结论**：scope discipline 严格。

### F8 — Docs/test README triggers correctly handled. Severity: INFO.

**验证项**：

- `tests/README.md` 未修改。新增 tests 遵循现有 conventions（pytest + fake LLM client），无需更新测试手册。
- `fund_agent/fund/README.md` 未修改。plan 未将 fund README 列入 write set；checklist 是 writer 内部 prompt 行为变化，不影响 Fund 包对外接口。
- 其他 README 未触发：`chapter_orchestrator.py` 和 `repair.py` 未修改，不触发 Service/Agent README 更新规则。
- Evidence artifact 记录了所有变更和未变更文件，符合 gate 透明度要求。

**结论**：docs/README 触发判断正确，无不必要修改也不缺失必要修改。

## Cross-check: Adversarial Failure Pass

审查以下 adversarial 场景：

| Scenario | 实现行为 | 判定 |
|---|---|---|
| `repair_context` 有 `programmatic:L1` 但 `chapter_id=1` | `_ch2_l1_repair_guidance_prompt` 返回 `""` | safe ✓ |
| `repair_context` 有 `programmatic:L2`（非 L1）在 chapter 2 | `_has_l1_numerical_closure_repair_issue` 返回 `False`（`L2` 不以 `L1` 开头） | safe ✓ |
| `repair_context` 有 `programmatic:L1_something` 在 chapter 2 | `startswith("programmatic:L1")` 匹配 → checklist 渲染。此为预期行为：`L1_something` 是 L1 子类。 | safe ✓ |
| `repair_context is None` 但 chapter 2 | `_has_l1_numerical_closure_repair_issue(None)` 返回 `False` | safe ✓ |
| `repair_context` 有 L1 但 `previous_issue_ids` 为空 tuple | `any()` 在空 iterable 返回 `False` | safe ✓ |
| 两个 fragment 都为空 | join 生成 `""`，template 渲染空字符串 | safe ✓ |
| `repair_context` 存在且 L1 命中，但 `_repair_context_prompt()` 也返回内容 | join 以 `\n` 拼接，两者都出现在 prompt 中 | correct ✓ |

无 adversarial bypass 发现。

## Final Summary

| 维度 | 判定 |
|---|---|
| 实现 vs accepted plan + amendments | 完全一致 |
| L1 blocker 语义保留 | 是 |
| Repair budget/action/stop reason 保留 | 是 |
| 无 typed patch API | 是 |
| Helper 检测 narrow + deterministic | 是（仅 `programmatic:L1` prefix） |
| Checklist 作用域限定 | 是（仅 Chapter 2 L1 repair） |
| Tests sufficient + no-live | 是 |
| 禁止文件/scope 遵循 | 是 |
| Docs/README 触发处理 | 正确（无缺失、无多余） |
| Adversarial pass | 通过 |

无 blocking finding，无 weakening finding，无 scope violation。

## Verdict

VERDICT: PASS
