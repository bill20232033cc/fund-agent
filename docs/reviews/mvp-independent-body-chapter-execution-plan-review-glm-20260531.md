# MVP Independent Body Chapter Execution Plan — GLM Review

## Review Meta

- Reviewer: GLM (plan review worker)
- Date: 2026-05-31
- Plan artifact: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`
- Classification: `heavy`
- Verdict: **PASS**

---

## Challenge 1: 模板第 1-6 章基于同一 ChapterFactProjection 独立 write/audit/repair，前章失败不遮蔽后章

### Finding: PASS

Plan 精确定位了当前 fail-fast 根因：

- `orchestrate_chapters()` line 604-618：`stop_remaining` 标志在 `fail_fast=True` 且首个非 accepted 章节后置 `True`，后续章节直接调用 `_skipped_result()` 并被标记为 `skipped` / `dependency_missing`。
- `_skipped_result()`（line 2766-2776）硬编码 `status="skipped"`, `stop_reason="dependency_missing"`, `failure_category="fact_gap"`, `attempts=()`。

Plan 的 Slice 1 提出移除 body chapter 循环中的 `stop_remaining` 逻辑，改为无条件调用 `_run_single_chapter()`。这与 `orchestrate_chapters()` 当前的 projection 共享（line 582 `projection = _resolve_projection(...)` + line 583 `_validate_projection_coverage(...)`）一致：所有 body chapter 共享同一 `ChapterFactProjection`，独立执行不依赖前章 writer/auditor 结果。

**验证**：`_run_single_chapter()` 只消费 `projection`、`chapter_id`、`policy`、`llm_clients`（line 880-886），不消费前章 `ChapterRunResult`。独立执行语义正确。

**残余风险**：Plan 建议保留 `_skipped_result()` 用于 "narrow internal compatibility"（Slice 1 step 4），但没有定义什么场景仍需调用它。建议实现时要么完全移除，要么严格限定于 `fund_type_unknown` / `auditor is None` 等全局阻断路径（这些已由 `_global_blocked_result()` 处理，不经过 `_skipped_result()`）。

---

## Challenge 2: Final assembly fail-closed 保持

### Finding: PASS

当前 `assemble_final_chapters()` 已实现完整的 fail-closed 逻辑：

1. `_validate_orchestration()`（line 356-414）：`require_orchestration_accepted=True` 时，`result.status != "accepted"` 直接阻断。
2. `_validate_required_chapter()`（line 417-462）：逐章检查 `status != "accepted"` → blocking issue `chapter_not_accepted`；`accepted_draft is None` → blocking issue `missing_accepted_draft`；`accepted_conclusion is None` → blocking issue `missing_accepted_conclusion`。
3. `_incomplete_result()`（line 1036-1068）：`report_markdown=None`，不输出完整报告。
4. `allow_incomplete_debug_markdown` 默认 `False`（line 78）。

Plan 的 Slice 2 正确指出"prefer no production-code change"并聚焦于加强测试覆盖。这是正确策略：当前 fail-closed 逻辑不依赖章节是否因 fail-fast 跳过，只依赖每个 `ChapterRunResult.status` 是否为 `accepted`。独立执行后，非 accepted 章节会有真实的 `failed` / `blocked` status 而非 `skipped`，但 `_validate_required_chapter()` 的检查逻辑（`chapter_result.status != "accepted"`）覆盖了所有非 accepted 状态，不需要改变。

**残余风险**：Plan 没有显式提到 `source_accepted_chapter_ids` 的安全语义。当前 `assemble_final_chapters()` line 253 从 `accepted_conclusion` 提取 `source_chapter_ids`，partial 场景下只有 accepted 章节被列入。这本身是安全的——`_incomplete_result()` 的 `report_markdown=None` 保证了 partial 矩阵不会作为完整报告输出。但建议 Slice 2 测试显式断言 `source_accepted_chapter_ids` 不包含非 accepted 章节编号。

---

## Challenge 3: first_failed + all chapter matrix + 安全序列化

### Finding: PASS

Plan 对诊断和安全的考虑非常完整：

1. **first_failed 保留**：`_first_failed_chapter_summary()` 和 `_first_failed_diagnostic()` / `_first_failed_runtime_diagnostic()` 遍历 `chapter_results` 取首个非 accepted 章节，逻辑独立于 fail-fast。
2. **all chapter matrix**：`serialize_chapter_prompt_contract_diagnostics()` 的 `chapter_phase_matrix`（line 647-650）和 `serialize_chapter_runtime_diagnostics()` 的 `chapter_runtime_matrix`（line 678-681）都遍历 `orchestration_result.chapter_results`，独立执行后每行都是真实结果。
3. **安全序列化**：`_chapter_diagnostic_row()`（line 2487-2498）和 `_chapter_runtime_diagnostic_row()`（line 2514-2525）只输出 allowlisted scalar；`_runtime_diagnostic_payload()`（line 2564-2583）排除 `message`、`model_name`；`_sanitize_text()`（line 2158-2177）redact `Authorization`、`Bearer`、`sk-`、`api_key`、`prompt`。
4. **CLI matrix 安全**：Plan Slice 3 的建议格式 `chapter_matrix=1:failed/llm_timeout/llm_timeout/unknown;2:accepted/none/unknown/unknown;...` 只包含 `chapter_id`、`status`、`stop_reason`、`failure_category`、`failure_subcategory`，不包含 issue messages、prompt、draft 或 provider response。

**残余风险**：Plan Slice 3 step 6 "Extend secret-safety assertions to cover the new matrix string" 是正确要求，但 plan 没有规定具体检测方法。建议实现时对 matrix 字符串做与现有 `_llm_incomplete_message()` 相同的负向断言：不含 `Authorization`、`Bearer`、`sk-`、`api_key`、`prompt`、`markdown`。

---

## Challenge 4: fail_fast 字段的兼容/废弃语义

### Finding: PASS (with note)

Plan 的建议是正确的：

1. **保留 `fail_fast` 字段**：`ChapterOrchestrationPolicy.fail_fast` 是 frozen dataclass field，移除会破坏所有现有构造调用和测试。
2. **废弃语义**：Plan 建议 "deprecate `fail_fast` in the docstring as legacy/no-op for body chapters, or change its default to `False`"。
3. **消除依赖路径**：Plan 明确要求 `orchestrate_chapters()` 不再基于 `fail_fast` 设置 `stop_remaining`，也不再调用 `_skipped_result()` 为前序 body failure 构造 synthetic skip。

**当前代码验证**：`fail_fast=True` 是默认值（line 291），`orchestrate_chapters()` line 617 `if policy.fail_fast and run_result.status != "accepted": stop_remaining = True` 是唯一消费点。Plan 的改造只需移除这个条件分支和 `stop_remaining` 变量。

**Note**：Plan 没有明确选择 "deprecated docstring" 还是 "default to False"。建议实现时选择后者（`fail_fast: bool = False`）并更新 docstring 说明 body chapters 不受此字段影响。这样做的好处是：如果有外部调用方显式传 `fail_fast=True`，新代码会忽略它（无 `stop_remaining` 路径），行为与 `False` 一致，不存在可重新触发 `dependency_missing` 的路径。但 Plan 的 Slice 1 step 6 已经要求更新相关测试，这足够防止回归。

---

## Challenge 5: 测试覆盖

### Finding: PASS

Plan 的测试设计覆盖了全部关键场景：

| 场景 | Plan 位置 | 覆盖评估 |
|---|---|---|
| Chapter 1 timeout 后 2-6 仍执行 | Slice 1 step 7 | PASS：显式要求 assert writer requests / attempt records |
| 多章混合矩阵 | Slice 1 step 8 | PASS：6 章各自独立 status/stop_reason/failure_category/failure_subcategory |
| Final assembly incomplete | Slice 2 step 3 | PASS：assert `status="incomplete"`, `report_markdown is None` |
| first_failed 不遮蔽 matrix | Slice 1 step 8 + Slice 3 step 4 | PASS：matrix 行独立，first_failed 只是首个非 accepted |
| dependency_missing 只用于真实依赖缺失 | Slice 1 step 9 | PASS：assert `dependency_missing` 只出现在 `chapter_requires_accepted_conclusions` |
| CLI matrix 安全 | Slice 3 step 5-6 | PASS：assert stderr 包含全章行、不含 secret |

**残余风险**：Plan 没有显式要求 "所有 6 章都 timeout" 的极端场景测试。虽然 Slice 1 step 7 的 "chapter 1 timeout 后 2-6 仍执行" 可以推广，但建议实现时增加一个全部 blocked 的测试以确保 `_orchestration_result()` 正确聚合为 `blocked`（而非 `partial`）。

---

## Challenge 6: 边界约束

### Finding: PASS

Plan 的 Non-Goals 和 Dirty Scope Boundary 严格对齐了 `AGENTS.md` 和 `docs/implementation-control.md`：

1. **不进 Host/Agent/dayu**：Plan 明确列出 disallowed files 包括 `AGENTS.md` 和 Host/Agent/dayu packages。
2. **不改 golden/fixtures/score/quality gate**：Disallowed files 包含 score, quality gate, golden, fixture, snapshot, manifest。
3. **不放松 writer/auditor 规则**：Disallowed files 包含 `chapter_writer.py` 和 `chapter_auditor.py`。
4. **不改变 deterministic analyze/checklist**：Validation Plan 包含 `uv run fund-analysis analyze 006597 --report-year 2024` 和 `uv run fund-analysis checklist 006597 --report-year 2024`，要求输出不变。
5. **不改 `AGENTS.md`**：Disallowed files 明确包含。

**验证**：Plan 的 allowed files 只包含 `chapter_orchestrator.py`、`final_chapter_assembler.py`（可选）、`cli.py` 和对应 tests + docs。这完全在 Service/UI 层边界内，不触碰 Fund 层、Host 层或 Agent 层。

---

## Challenge 7: Dirty worktree 处理

### Finding: PASS

Plan 的 Dirty Scope Boundary 正确声明：

1. "Implementation must treat them as existing local state and must not revert, clean, delete, restage, rename or normalize unrelated files."
2. Allowed files 列表限定为 7 个文件 + 可选文档。
3. Stop conditions 包含 "Dirty worktree conflicts make it impossible to isolate this gate's diff."

这与 `docs/current-startup-packet.md` Prohibited Actions "Do not delete or clean unrelated untracked files" 一致。

**残余风险**：当前 worktree 有大量 untracked review artifacts 和 modified 文件。实现 worker 需要在 diff 中只包含 allowed files 的变更。Plan 已通过 Stop Conditions 覆盖此风险，但实现 worker 应在开始前用 `git diff --name-only` 确认 diff 隔离性。

---

## Summary of Residual Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | `_skipped_result()` 是否完全移除或保留未定义 | Low | 实现时应完全移除或限定为 dead code path |
| R2 | `source_accepted_chapter_ids` 安全断言未在 plan 中显式要求 | Low | Slice 2 测试应增加断言 |
| R3 | CLI matrix secret-safety 断言方法未具体规定 | Low | 实现时复用现有负向断言模式 |
| R4 | 全部 blocked（6 章）极端场景未显式列为测试 | Low | 实现时补充 |
| R5 | `fail_fast` 废弃策略选择（docstring vs default）未最终确定 | Low | 建议改 default 为 False + docstring deprecated |
| R6 | Dirty worktree diff 隔离依赖实现 worker 自查 | Low | Start condition 已覆盖 |

---

## Verdict

**PASS** — Plan 精确定位了 fail-fast 根因，提出了正确的改造方案（移除 body chapter `stop_remaining` 逻辑），保持了 final assembly fail-closed 语义，保留了 first_failed + all chapter matrix 双层诊断，安全序列化完整，测试覆盖关键场景，边界约束与 `AGENTS.md` / `docs/implementation-control.md` 一致，dirty worktree 处理声明正确。6 个残余风险均为 Low severity，可在实现阶段处理。

---

## Self-Check

- Role: plan review worker only; no code, commit, push or PR.
- Source files read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, plan artifact, `chapter_orchestrator.py`, `final_chapter_assembler.py`, `cli.py`.
- Scope: review artifact only; no implementation changes.
- Stop conditions: no blocking findings.
