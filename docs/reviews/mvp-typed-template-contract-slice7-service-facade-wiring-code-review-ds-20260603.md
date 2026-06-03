# MVP typed template contract Slice 7 Service Facade Wiring — Code Review DS

## Worker Self-Check

- Role: AgentDS，code review worker only，不是 controller / implementation worker。
- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`。
- Classification: `heavy`。
- Scope: review only；不修改代码，不 commit，不 push。
- Sources read: `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`（前 120 行控制面）、`docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md` Slice 7 段、`docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-implementation-evidence-20260603.md`、full worktree diff、以及 `fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/execution_contract.py`、`fund_agent/services/fund_analysis_service.py`、`fund_agent/fund/chapter_writer.py`、`fund_agent/fund/chapter_auditor.py`、`fund_agent/fund/template/typed_contracts.py` 相关段。

## Validation Result

| Command | Result |
|---|---|
| `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | **177 passed** |
| `uv run ruff check fund_agent/services tests/services tests/ui` | **All checks passed** |
| `git diff --check` | **Passed** (no whitespace errors) |

## Finding 1 — BLOCKING: typed_required_output_items 未从 Service facade 传入 writer

**严重程度**: Blocker。Slice 3 accepted `RequiredOutputItem.when_evidence_missing` 行为无法通过 Service facade 流入 writer。

**证据**:

`_run_single_chapter()` 在 `chapter_orchestrator.py:1053-1059` 构造首次 writer input：

```python
writer_input = build_chapter_writer_input(
    projection,
    chapter_id=chapter_id,
    max_output_chars=policy.max_output_chars,
    prompt_payload_mode=policy.prompt_payload_mode,
    evidence_availability=_typed_evidence_availability(typed_inputs),
)
```

缺少 `typed_required_output_items=...` 实参。修复写入路径（`:1243-1252`）同样缺少。

`build_chapter_writer_input()` 的签名 (`chapter_writer.py:544-555`) 明确接受 `typed_required_output_items`：

```python
def build_chapter_writer_input(
    ...
    typed_required_output_items: tuple[RequiredOutputItem, ...] = (),
    evidence_availability: EvidenceAvailability | None = None,
) -> ChapterWriterInput:
```

但 orchestrator 从未计算或传入该参数。

**根因**: `_TypedTemplateInputs` (`chapter_orchestrator.py:537-545`) 只持有 `evidence_availability`，不持有 typed chapter contract 的 `required_output_items`。没有代码从 `TypedChapterContract.required_output_items` 提取并桥接到 `build_chapter_writer_input(typed_required_output_items=...)`。

**为什么是 blocker**: `chapter_writer.py:914-916` 的 `_build_required_output_plan()` 在 `typed_required_output_items` 为空时直接返回 `()`：

```python
typed_items = input_data.typed_required_output_items
if not typed_items:
    return ()
```

这意味着即使 `evidence_availability` 已传入 writer，因为没有 `typed_required_output_items`，writer 完全跳过 typed required-output planning，停留在 legacy/default 路径。传入 `evidence_availability` 而不传入 `typed_required_output_items` 在当前 writer 实现中是 **无操作（no-op）**。

**影响**: Slice 3 接受的 `when_evidence_missing` 行为（`render_evidence_gap` / `render_minimum_verification_question` / `delete_if_not_applicable` / `block`）不会在 typed template path 上激活。typed 路径的 writer 行为与 legacy 路径完全相同，typed contract 的 required-output 语义被 Service facade 丢弃。

**修复范围（仅分析，不实施）**: 修复应限于 `fund_agent/services/chapter_orchestrator.py`，不改 Fund 层：

1. `_TypedTemplateInputs` 不需要扩展；改为在 `_run_single_chapter()` 中按 chapter_id 调用 `_typed_chapter_contract()` 获取 `TypedChapterContract`。
2. 从 `TypedChapterContract.required_output_items` 提取 `tuple[RequiredOutputItem, ...]`。
3. 传入 `build_chapter_writer_input(typed_required_output_items=...)`（初始写入 + 修复写入两处）。
4. 不需要改 `chapter_writer.py`、`typed_contracts.py`、`evidence_availability.py` 或任何 Fund 层文件。

## Finding 2 — NON-BLOCKING: auditor 双重加载 typed_chapter_contract

**严重程度**: Informational，不阻塞 gate。

**证据**: orchestrator 在 `chapter_orchestrator.py:1139` 向 `ChapterAuditInput` 传入 `typed_chapter_contract`：

```python
audit_input = ChapterAuditInput(
    writer_input=writer_input,
    draft=draft,
    typed_chapter_contract=_typed_chapter_contract(
        chapter_id, typed_inputs=typed_inputs,
    ),
    ...
)
```

但 `chapter_auditor.py:715,742` 的 `_typed_chapter_contract_for()` 也独立调用 `get_typed_chapter_contract(chapter_id)`。两条路径加载同一个 typed contract，orchestrator 传入的值在某些 code path 中可能被 auditor 自身加载覆盖。

**判定**: 这不是 bug——auditor 的 `_typed_chapter_contract_for()` 在 `input_data.typed_chapter_contract` 为 None 时作为 fallback，行为一致。双重加载只是冗余，不产生分歧。不阻塞 gate。

## Finding 3 — PASS: 显式 typed_template_path 字段，无自由参数袋

**验证结果**: 通过。

- `TypedTemplatePathMode = Literal["legacy_contract", "typed_template_contract"]` 是闭集合。
- `typed_template_path` 作为显式字段出现在 `FundLLMExecutionRequest`、`FundLLMRuntimePlan`、`ChapterOrchestrationPolicy`。
- `test_no_extra_payload_or_free_business_payload_bag` 验证了 `extra_payload`、`kwargs`、`payload`、`metadata`、`context` 均不存在于公开类型和签名。
- `test_typed_template_flags_are_explicit_fields_if_added` 验证了 `typed_template_path` 只能通过显式字段选择。
- `test_execution_request_rejects_typed_template_path_mismatch` 验证了 request/runtime_plan/chapter_policy 三处的 typed path 必须一致。
- 无 `dict[str, Any]` / `Mapping[str, Any]` 自由业务参数袋。

## Finding 4 — PASS: build_fund_llm_execution_request 只在 explicit --use-llm path 选择 typed_template_contract

**验证结果**: 通过。

- `build_fund_llm_execution_request()` (`fund_analysis_service.py:950`) 硬编码 `typed_template_path="typed_template_contract"`。
- 该函数只在 CLI `--use-llm` 路径被调用；默认 `analyze` 和 `checklist` 不经过该函数。
- `test_default_analyze_unchanged_with_typed_contract_modules_present` 确认默认 analyze 不调用 `build_fund_llm_execution_request`、不 invoke Host、不调用 `analyze_with_llm_execution`、不写 LLM incomplete artifact。
- checklist 已有测试拒绝 `--use-llm`。

## Finding 5 — PASS: ChapterOrchestrator 保持 Service-owned transition facade，独立章节执行

**验证结果**: 通过。

- `ChapterOrchestrator` 和 `orchestrate_chapters()` 留在 `fund_agent/services/`。
- 无 Host/Agent runtime 迁移。
- `test_typed_contract_path_preserves_independent_body_execution` 验证：
  - typed path 上 Ch1 失败（`llm_timeout`）后 Ch2 仍 accepted，Ch3 独立失败（`repair_budget_exhausted`）。
  - 无 `dependency_missing` stop reason 误用。
  - `availability_calls` 确认 `derive_evidence_availability` 只在 orchestrator 入口调用一次（同源派生）。
  - auditor requests 的 `audit_focus` 正确传入。
- `test_dependency_missing_only_for_true_writer_dependency_not_prior_failure` 保持通过。

## Finding 6 — PASS: Host 仍只接收 generic operation/deadline/session

**验证结果**: 通过。

- 无 Host 文件被修改。
- 现有 Host 接口不变：Host 仍只接收 generic `operation`、`deadline_seconds`、`session_id`。
- 无业务字段暴露给 Host。

## Finding 7 — PASS: 无 scope 越界

**验证结果**: 通过。以下均在 diff 中确认未修改：

- provider/default/runtime/live probe：未修改 `fund_agent/config/llm.py`、provider 默认值、超时预算、endpoint 行为。
- Agent runtime/tool-loop：未实现，未导入 dayu。
- score/golden/readiness/template truth：未修改。
- quality gate：未修改 FQ0-FQ6 语义。
- deterministic default 行为：`analyze` 和 `checklist` 默认路径不变，回归测试通过。

## Finding 8 — PASS: audit_focus 通过 typed_chapter_contract 正确接入 auditor

**验证结果**: 通过。

- `_typed_chapter_contract()` 在 orchestrator 中调用 `get_typed_chapter_contract(chapter_id)` 获取 typed contract。
- `ChapterAuditInput.typed_chapter_contract` 接受该值。
- `chapter_auditor.py:1466` 的 `_llm_audit_focus()` 从 `input_data.typed_chapter_contract` 提取 `audit_focus`。
- `test_typed_contract_path_preserves_independent_body_execution` 的 auditor request assertion 确认了 Ch2 的 `("r_abc", "evidence_anchors")` 和 Ch3 的 `("manager_consistency", "evidence_anchors")` 正确传入。
- `audit_focus` 是 bounded semantic only；programmatic audit 不受影响。

## Disposition Matrix

| # | Focus Area | Verdict | Blocker? |
|---|---|---|---|
| 1 | typed_required_output_items 未传入 writer | 确认 gap | **BLOCKING** |
| 2 | auditor 双重加载 typed_chapter_contract | 冗余，无分歧 | No |
| 3 | 显式 typed_template_path，无自由参数袋 | 通过 | No |
| 4 | build_fund_llm_execution_request 只在 --use-llm | 通过 | No |
| 5 | ChapterOrchestrator facade + 独立执行 | 通过 | No |
| 6 | Host business-field opacity | 通过 | No |
| 7 | 无 scope 越界 | 通过 | No |
| 8 | audit_focus 正确接入 auditor | 通过 | No |

## Specific Blocker Analysis: typed_required_output_items

**问题**: 当前 implementation 传入了 `EvidenceAvailability` 和 `typed_chapter_contract`/`audit_focus`，但没有向 writer 传入 `typed_required_output_items`。

**判断**: **Blocking**。

**依据**:

1. `ChapterWriterInput` 已支持 `typed_required_output_items: tuple[RequiredOutputItem, ...]`（Slice 3 产物）。
2. `build_chapter_writer_input()` 已接受 `typed_required_output_items` 参数。
3. `_build_required_output_plan()` 在 `typed_required_output_items` 为空时立即返回 `()`，完全跳过 typed required-output planning。
4. 传入 `evidence_availability` 而不传入 `typed_required_output_items` 是 **no-op**：writer 不会基于 availability 做任何 typed 缺证行为决策。
5. Slice 3 的 `RequiredOutputItem.when_evidence_missing` 是 typed template contract 的核心行为语义，Slice 7 的 facade wiring 必须将其桥接到 writer。
6. 修复范围极小：只需在 `_run_single_chapter()` 中调用 `_typed_chapter_contract()` 取 `required_output_items`，传入 `build_chapter_writer_input(typed_required_output_items=...)`。不涉及 Fund 层修改。

**不是 design gap，是 wiring gap**：所有需要的 Fund 层能力（`TypedChapterContract.required_output_items`、`ChapterWriterInput.typed_required_output_items`、`build_chapter_writer_input(typed_required_output_items=)`）均已就绪。缺失的只是 orchestrator 中的桥接代码。

## Residual Risks (after blocker fix)

- Producer-side evidence availability 派生正确性由 Slice 2 tests 覆盖，不在本 review scope。
- `typed_required_output_items` 传入后，writer prompt 中的 typed required-output marker 行为是否正确渲染，需要现有 `tests/fund/test_chapter_writer.py` 覆盖（未在本次 diff 中修改）。
- 修复后 repair 路径的 `typed_required_output_items` 一致性需确认：repair 的 writer input 应传入与初始写入相同的 typed items。

## Verifier Summary

| Accepted Requirement | Evidence |
|---|---|
| 显式 typed 字段，无 extra_payload | `test_no_extra_payload_or_free_business_payload_bag` + `test_typed_template_flags_are_explicit_fields_if_added` |
| build_fund_llm_execution_request 只在 --use-llm | 硬编码 `typed_template_path="typed_template_contract"` 仅在该函数内；`test_default_analyze_unchanged_with_typed_contract_modules_present` |
| ChapterOrchestrator facade + 独立章节 | `test_typed_contract_path_preserves_independent_body_execution`；无 Host/Agent 迁移 |
| Host 不暴露业务字段 | 无 Host 文件修改 |
| audit_focus 正确接入 | auditor `audit_focus` 断言在 `test_typed_contract_path_preserves_independent_body_execution` |
| typed_required_output_items 接入 writer | **GAP** — 见 Finding 1 |
| 无 provider/default/runtime/score/golden 改动 | diff 确认未修改相关文件 |
| 默认 analyze/checklist 不变 | `test_default_analyze_unchanged_with_typed_contract_modules_present`；checklist 拒绝 --use-llm |

## Recommendation

**不通过当前 gate**，等待 `typed_required_output_items` wiring gap 修复后重新 review。修复范围建议限定在 `fund_agent/services/chapter_orchestrator.py` 的 `_run_single_chapter()` 函数内（初始写入 + 修复写入两处），不涉及 Fund 层或其他模块。

---

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
