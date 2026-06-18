# MVP typed template contract Slice 7 Service Facade Wiring — Re-Review DS

## Worker Self-Check

- Role: AgentDS，code review worker only。
- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`。
- This is a **re-review** following the blocking finding fix documented in `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-fix-evidence-20260603.md`。
- Previous review artifact: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-code-review-ds-20260603.md` (1 blocker, 7 pass)。
- Sources read: fix evidence, full current worktree diff, `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、Slice 7 planning section、`chapter_orchestrator.py`、`execution_contract.py`、`fund_analysis_service.py`、`chapter_writer.py`、`chapter_auditor.py`、`typed_contracts.py`。
- Scope: review only；不修改代码，不 commit，不 push。

## Validation Result

| Command | Result |
|---|---|
| `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | **178 passed** (+1 vs 初次 review 的 177) |
| `uv run ruff check fund_agent/services tests/services tests/ui` | **All checks passed** |
| `git diff --check` | **Passed** |

## Re-Review: 原 Blocker 修复验证

### 原 Blocker (Finding 1): typed_required_output_items 未传入 writer

**状态: 已修复。**

修复方式：新增 `_typed_required_output_items()` (`chapter_orchestrator.py:1008-1025`)：

```python
def _typed_required_output_items(
    chapter_id: int,
    *,
    typed_inputs: _TypedTemplateInputs | None,
) -> tuple[RequiredOutputItem, ...]:
    typed_contract = _typed_chapter_contract(chapter_id, typed_inputs=typed_inputs)
    if typed_contract is None:
        return ()
    return typed_contract.required_output_items
```

两处调用点均已接入：

| 调用位置 | 行号 | 用途 |
|---|---|---|
| 初始 writer input | `:1086-1089` | 首次写作传入 typed required output items |
| 修复 writer input | `:1284-1287` | regenerate 轮次同样传入 typed required output items |

**Slice 3 行为激活证据**：`test_typed_contract_path_preserves_independent_body_execution` 中断言：

```python
assert ch3_plan_by_id["ch3.required_output.item_03"].action == "render_evidence_gap"
assert ch3_plan_by_id["ch3.required_output.item_03"].availability_status == "unreviewed"
```

这证明 typed path 上 `RequiredOutputItem.when_evidence_missing` → `render_evidence_gap` 行为已通过 Service facade 流入 writer prompt plan。Writer 接收到 `typed_required_output_items` → `_build_required_output_plan()` 不再跳过（不再是 no-op）→ 基于 `EvidenceAvailability` 的 `unreviewed` 状态生成 `render_evidence_gap` action。

## 逐项验证

### 1. Slice 3 when_evidence_missing 行为通过 Service facade 激活 — PASS

- `_typed_required_output_items()` 从 `TypedChapterContract.required_output_items` 提取 items。
- 传入 `build_chapter_writer_input(typed_required_output_items=...)`。
- Writer 的 `_build_required_output_plan()` 因 `typed_items` 非空而执行 typed planning（不再跳过 `chapter_writer.py:914-916`）。
- 测试验证 Ch3 `item_03` 的 `action == "render_evidence_gap"` + `availability_status == "unreviewed"`——Slice 3 accepted 行为完整激活。

### 2. 初始写入和 repair 写入都传入 typed_required_output_items — PASS

- 初始: `chapter_orchestrator.py:1086-1089`。
- 修复: `chapter_orchestrator.py:1284-1287`。
- `test_typed_contract_path_repair_keeps_typed_required_output_items` 验证 repair attempt 的 `required_output_evidence_plan` 非空、`required_output_items[0]` 以 `ch2.required_output.` 开头，两个 attempt 均满足。
- 两处使用的 `_typed_required_output_items()` 入参相同（`chapter_id` + `typed_inputs`），保证 initial/repair 一致性。

### 3. Legacy path 不激活 typed required-output behavior — PASS

- `_typed_template_inputs()` 在 `policy.typed_template_path == "legacy_contract"` 时返回 `None`。
- `_typed_required_output_items()` 在 `typed_inputs is None` 时返回 `()`。
- 空 `()` 使 writer 的 `_build_required_output_plan()` 走 `if not typed_items: return ()` 分支，完全跳过 typed planning。
- 所有 legacy path 测试保持通过，无行为变更。

### 4. 各项不变量保持 — PASS

| 不变量 | 验证方式 |
|---|---|
| Independent body execution | `test_typed_contract_path_preserves_independent_body_execution` 确认 Ch1 超时后 Ch2/Ch3 仍执行，无 `dependency_missing` |
| audit_focus 正确接入 | auditor requests 的 `audit_focus` 断言：Ch2 `("r_abc", "evidence_anchors")`，Ch3 `("manager_consistency", "evidence_anchors")` |
| 显式 typed_template_path，无自由参数袋 | `test_typed_template_flags_are_explicit_fields_if_added` + `test_no_extra_payload_or_free_business_payload_bag` 通过 |
| 默认 analyze 不变 | `test_default_analyze_unchanged_with_typed_contract_modules_present` 通过 |
| checklist 不变 | 已有 checklist 拒绝 `--use-llm` 测试通过 |
| Host business-field opacity | 无 Host 文件修改 |
| provider/runtime/score/golden/quality gate 未动 | diff 确认无相关文件修改 |

### 5. 新 blocking finding — NONE

逐项检查后未发现新的 blocking finding。两个观察（均为 non-blocking）：

**Obs A (non-blocking)**：`test_typed_contract_path_preserves_independent_body_execution` 的 `result.status` 从初次 review 的 `"partial"` 变为 `"blocked"`。原因是 typed path 上 fake writer 的默认输出不满足 typed required output marker 格式，导致 Ch2 也失败。这不是回归——typed path 要求 stricter contract，fake 不满足是预期行为。独立执行的核心断言（所有章节都执行、无 `dependency_missing`）仍然通过。

**Obs B (non-blocking)**：`_typed_required_output_items()` 按 chapter 调用 `get_typed_chapter_contract(chapter_id)`，每个 chapter 的 writer input 构造时独立加载一次。与 `derive_evidence_availability()` 的 once-per-orchestration 不同，这是 per-chapter 加载。这正确——不同 chapter 的 `required_output_items` 不同。性能影响可忽略（typed contract 是内存中的 dataclass 查找）。

## Disposition Matrix

| # | Focus Area | Initial Verdict | Re-Review Verdict |
|---|---|---|---|
| 1 | typed_required_output_items 传入 writer | **BLOCKING** | **FIXED** — 两处调用点均已接入 |
| 2 | auditor 双重加载 typed_chapter_contract | Non-blocking | 不变 |
| 3 | 显式 typed_template_path，无自由参数袋 | Pass | 不变 |
| 4 | build_fund_llm_execution_request 只在 --use-llm | Pass | 不变 |
| 5 | ChapterOrchestrator facade + 独立执行 | Pass | 不变 |
| 6 | Host business-field opacity | Pass | 不变 |
| 7 | 无 scope 越界 | Pass | 不变 |
| 8 | audit_focus 正确接入 auditor | Pass | 不变 |

## 结论

**通过。** 原 blocker 已修复：`_typed_required_output_items()` 将 `TypedChapterContract.required_output_items` 桥接到 writer input，Slice 3 `when_evidence_missing` 行为（`render_evidence_gap`）已通过 Service facade 激活。初始写入与修复写入两处均已接入。Legacy path 不受影响。无新增 blocking finding。178 tests pass，ruff clean，git diff --check clean。

---

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
