# Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence — DS Review

Date: 2026-06-14

## Scope

- **Mode**: Role-scoped root-cause evidence review (not code review, not implementation)
- **Gate**: `Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`
- **Input artifact**: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-20260614.md`
- **Reviewer role**: AgentDS
- **Output file**: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-ds-20260614.md`
- **Included scope**: The no-live root-cause evidence artifact and all allowed verification sources
- **Excluded scope**: Implementation, code changes, control/design doc updates, live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR
- **Parallel review coverage**: 无（单 reviewer 全量走读）

## Evidence Sources Reviewed

Control/truth:
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Accepted upstream:
- `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`

Code paths (full read):
- `fund_agent/agent/runner.py`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/evidence_availability.py`
- `fund_agent/fund/template/typed_contracts.py`

Template truth:
- `docs/fund-analysis-template-draft.md` (TEMPLATE_CONTRACT_MANIFEST_JSON — `ch3.required_output.item_01` verified)

Tests:
- `tests/agent/test_runner.py`
- `tests/fund/test_chapter_facts.py`

Independent reproducer:
- Reproducer B executed and confirmed (see Verification section below)

## Root-cause Chain Verification

### Step 1: Availability derivation for `ch3.required_output.item_01`

`evidence_availability.py:246-251` — `_CH3_REQUIREMENT_SPECS` 定义：

```python
_RequirementSpec(
    "ch3.required_output.item_01", 3,
    ("structured.basic_identity", "structured.portfolio_managers"),
    detail="基金经理基本信息 required output 证据。",
),
```

该 requirement 依赖两个 source field：`structured.basic_identity` 和 `structured.portfolio_managers`。

`evidence_availability.py:437-461` — `_facts_for_spec()` 按 `source_field_id` 匹配同章 facts。

`evidence_availability.py:464-508` — `_status_for_facts()` 调用 `_status_for_fact()` 对每个 fact 求 status，再用 `_combine_statuses()` 取最保守状态。

`evidence_availability.py:489-508` — `_status_for_fact()`：
- `fact.status == "available"` 且有 `evidence_anchor_ids` 且 `missing_reason is None` → `"available"`
- `fact.status in ("missing", "unavailable", "not_applicable")` → 同值返回
- 其他 → `"unreviewed"`

当 `portfolio_managers` 为 `ExtractedField(value=None, extraction_mode='missing')` 时：
- `portfolio_managers` fact → `status="missing"` → `_status_for_fact` → `"missing"`
- `basic_identity` fact → `status="available"` → `_status_for_fact` → `"available"`

`evidence_availability.py:585-603` — `_combine_statuses(("available", "missing"))` 按 `_STATUS_ORDER = ("unreviewed", "unavailable", "missing", "not_applicable", "available")` 首次命中返回 `"missing"`。

**结论：`ch3.required_output.item_01` 的 availability status 为 `"missing"`。** ✓

### Step 2: Typed template `when_evidence_missing` 为 null

`docs/fund-analysis-template-draft.md` 模板 JSON：

```json
{
  "id": "ch3.required_output.item_01",
  "text": "基金经理基本信息",
  "when_evidence_missing": null,
  "missing_evidence_reason": null
}
```

Python typed projection 确认：`item.when_evidence_missing = None`，`item.missing_evidence_reason = None`。

**结论：`ch3.required_output.item_01` 的 typed contract 未声明缺证行为。** ✓

### Step 3: `_required_output_action()` 触发 ValueError

`chapter_writer.py:931-968` — `_required_output_plan_item()`：

```python
requirement = _availability_for_required_output(item, evidence_availability)
status = requirement.status if requirement is not None else None  # → "missing"
missing = status in _MISSING_EVIDENCE_STATUSES  # → True
missing_availability = requirement is None and item.when_evidence_missing is not None  # → False
action = "block" if missing_availability else _required_output_action(item, status)
```

因为 `requirement is not None`（requirement 在 availability 中存在），不进入 `missing_availability` 的 `"block"` 路径。进入 `_required_output_action(item, "missing")`。

`chapter_writer.py:994-1024` — `_required_output_action()`：

```python
if status == "available" or status is None:  # False, status is "missing"
    return "render"
behavior = item.when_evidence_missing  # → None
if behavior is None:  # → True
    raise ValueError(f"typed required output 缺证但未声明 when_evidence_missing：{item.item_id}")
```

**结论：`_required_output_action()` 对 status=`"missing"` + `when_evidence_missing=None` 抛出 `ValueError`。** ✓

### Step 4: ValueError 在 provider 调用前发生

`chapter_writer.py:741-807` — `write_chapter()`：

```python
prompt = build_chapter_prompt(input_data)  # line 759 — 此处抛出 ValueError
```

`build_chapter_prompt()` → `_required_output_evidence_plan()` → `_required_output_plan_item()` → `_required_output_action()` 在 provider/fake-writer 调用前抛出。Reproducer B 确认 `writer_requests 0`。

**结论：ValueError 发生在 provider 调用之前。** ✓

### Step 5: Agent runner 映射到 live 诊断形态

`runner.py:336-356` — `_run_single_chapter()` 中 `write_chapter_tool()` 捕获异常：

```python
if writer_execution.exception is not None:
    return _exception_task(...)
```

`runner.py:907-963` — `_exception_task()`：
- `terminal = _terminal_from_exception(exception)` → `"blocked_internal_code_bug"`（因为 `ValueError` 不在 provider runtime 异常名集合中，`runner.py:1399-1414`）
- `stop_reason = _stop_reason_from_exception(exception)` → `"llm_exception"`（因为 `ValueError` 不匹配任何 provider 异常类型名，`runner.py:1417-1439`）
- `failure_category = _failure_category_from_exception(exception)` → `"code_bug"`（因为不在 provider runtime 异常集合中，`runner.py:1464-1481`）

**结论：Agent runner 将 Fund writer 的 `ValueError` 映射为 `blocked_internal_code_bug` / `llm_exception` / `code_bug`，与 live evidence 完全一致。** ✓

### Step 6: 为什么前一个 patch（`2bced82`）未覆盖此分支

前一个 patch 处理的是 `missing_availability` 路径：
- **条件**：`requirement is None`（availability 中不存在该 requirement mapping）且 `item.when_evidence_missing is not None`
- **动作**：`action = "block"`，返回 `blocked_fact_gap` Writer 结果

当前 root cause 是不同的分支：
- **条件**：`requirement is not None`（availability 中存在该 requirement mapping），但 `status` 非 available，且 `item.when_evidence_missing is None`
- **动作**：`_required_output_action()` 抛出 `ValueError`

两个分支互斥，前一个 patch 正确覆盖了 `missing_availability` 路径，但未触及 `present-but-non-available + null-behavior` 路径。

**结论：前一个 patch 与当前 bug 覆盖不同分支，证据 artifact 的区分正确。** ✓

## Independent Verification

执行 Reproducer B 确认：

```text
req ch3.required_output.item_01 missing fact ('structured.basic_identity', 'structured.portfolio_managers')
req ch3.required_output.item_02 available fact ('structured.manager_strategy_text',)
req ch3.required_output.item_06 available fact ('structured.manager_alignment',)
req ch3.required_output.item_03 unreviewed derived (...)
req ch3.required_output.item_04 unreviewed derived (...)
req ch3.required_output.item_05 unreviewed derived (...)
writer_input_ok ChapterWriterInput
write_chapter_exception ValueError typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01
writer_requests 0
```

与证据 artifact 记录完全一致。

## Findings

### F1-未修复-中-typed template `ch3.required_output.item_01` 缺少缺证行为声明

- **入口/函数**: `_required_output_action()` → `_required_output_plan_item()` → `build_chapter_prompt()`
- **文件(行号)**: `fund_agent/fund/chapter_writer.py:1011-1015`, `fund_agent/fund/chapter_writer.py:956`
- **输入场景**: `portfolio_managers` 字段缺失（`ExtractedField(value=None, extraction_mode='missing')`），`ch3.required_output.item_01` availability status 为 `"missing"`
- **实际分支**: `_required_output_action()` 中 `status != "available"` 且 `status is not None` → `behavior is None` → `raise ValueError`
- **预期行为**: 按 typed contract 设计，每个 required output item 应对非 available 状态有明确降级行为（`render_evidence_gap` / `render_minimum_verification_question` / `delete_if_not_applicable` / `block`）
- **实际行为**: `ch3.required_output.item_01` 在模板 JSON 中 `when_evidence_missing=null`，而 `item_02` 至 `item_06` 均有显式降级行为。当 `item_01` 的 availability 为非 available 时，`_required_output_action()` 无法找到合法降级路径而抛出 `ValueError`
- **直接证据**: 模板 JSON `"when_evidence_missing": null`（`docs/fund-analysis-template-draft.md`）；Python typed projection 输出 `when_evidence_missing=None`（`typed_contracts.py:498-509`）；`_required_output_action()` 在 `behavior is None` 时抛出（`chapter_writer.py:1014-1015`）
- **影响**: 第 3 章在 provider 调用前 fail-closed，阻止了其他 5 个有合法降级声明的 required output items 进入 writer；外部表象为 `llm_exception` / `code_bug`，误导诊断为 provider 或代码缺陷
- **建议改法和验证点**: 下一实现 gate 应为 `ch3.required_output.item_01` 选择显式 `when_evidence_missing` 行为（推荐 `render_evidence_gap` 或 `block`），并同步更新 `missing_evidence_reason`；type-check 和 focused test 须验证 `portfolio_managers` 缺失时 Chapter 3 不再抛出 ValueError
- **修复风险（低）**: 只修改模板 JSON 中一个字段的 null → 合法值，以及可能的 `missing_evidence_reason`；不影响其他 5 个 items 的现有行为
- **严重程度（中）**: 虽然根因是 typed template 配置不完整而非代码逻辑错误，但该缺陷导致整个第 3 章静默 fail-closed，且错误分类误导（`code_bug` 而非 `fact_gap`）

### F2-未修复-低-`_required_output_action()` 的 fail-closed 路径分类不够精确

- **入口/函数**: `_required_output_action()`
- **文件(行号)**: `fund_agent/fund/chapter_writer.py:1011-1015`
- **输入场景**: availability 存在 mapping 但 status 非 available，且 typed template 未声明 `when_evidence_missing`
- **实际分支**: `behavior is None` → `raise ValueError`
- **预期行为**: 当前抛出 `ValueError` 是安全的 fail-closed。但该错误被 Agent runner 归类为 `code_bug`（`runner.py:1481`），而实际根因是 typed template 配置不完整（更接近 `fact_gap` 或 `prompt_contract`）
- **实际行为**: Agent runner 将任意非 provider-runtime `Exception` 归类为 `code_bug`，无法区分 "typed template 配置不完整" 与 "代码逻辑缺陷"
- **直接证据**: `runner.py:1464-1481` — `_failure_category_from_exception()` 只按异常类型名判断，不按发生位置判断
- **影响**: 运维诊断时 `code_bug` 分类将操作引导向代码修复，而非模板配置修复；若未来其他 chapter/item 出现同样模式（availability present but non-available + null behavior），错误分类会重复
- **建议改法和验证点**: 下一实现 gate 可考虑让 `_required_output_action()` 抛出更具体的异常类型（如 `TypedContractConfigurationError`），或在 `_failure_category_from_exception()` 中检查异常消息前缀；但这不是当前 root cause 的必要修复
- **修复风险（低）**: 只影响异常分类字符串，不改变 fail-closed 行为
- **严重程度（低）**: 不影响正确性（fail-closed 行为不变），仅影响诊断精度

## Open Questions

- `ch3.required_output.item_01` 的 `when_evidence_missing=null` 是 intentional（基金经理基本信息在有知有行方法论下不允许缺失）还是模板编辑遗漏？若为 intentional，当前代码路径应在 availability 非 available 时 fail-closed 但应分类为 `fact_gap` 而非 `code_bug`；若为遗漏，应补充 `render_evidence_gap`。
- 其他章节（ch1, ch2, ch6）的 required output items 是否也存在 `when_evidence_missing=null` + availability 可能非 available 的同样模式？本 gate scope 限第 3 章，未检查其他章节。

## Residual Risk

- 本 gate 未读取实际 live projection 的 field 状态（`chapter-03.json` 在 incomplete-run artifact 中不包含 fact-level detail）。No-live reproducer 使用 `ExtractedField(value=None, extraction_mode='missing')` 构造缺失场景，与 live 的精确 field state 可能不同（例如 live 中 `portfolio_managers` 可能是 `available` 但无 evidence anchors，此时 status 为 `"unreviewed"` 而非 `"missing"`，但 `_required_output_action()` 同样会抛出 ValueError）。证据 artifact 已将此列为 residual。
- `fund_agent/agent/tools.py`（`write_chapter_tool` 实现）不在本 gate 允许的读取范围内，未验证其异常捕获和包装逻辑。但 `test_runner.py` 中 `test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool` 间接覆盖了异常映射路径。
- 未检查 typed template 中其他章节 items 的 `when_evidence_missing` 完整性。

## Verdict

VERDICT: **PASS_WITH_FINDINGS**

Root cause is proven with direct code-path evidence across all six steps of the chain:

1. `ch3.required_output.item_01` availability derived as `"missing"` when `portfolio_managers` field is absent
2. Typed template declares `when_evidence_missing=null` for `item_01`
3. `_required_output_action()` raises `ValueError` for non-available status with null behavior
4. ValueError occurs in `build_chapter_prompt()` before any provider call
5. Agent runner maps to `blocked_internal_code_bug` / `llm_exception` / `code_bug`
6. Prior patch (`2bced82`) covered a different branch (`missing_availability` vs `present-but-non-available`)

Two findings (F1 medium, F2 low) are recorded. The evidence artifact correctly distinguishes the root cause from the prior patch's scope and correctly identifies residuals.
