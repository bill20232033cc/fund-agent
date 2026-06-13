# AgentDS Implementation Review: Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix

Date: 2026-06-14

## Scope

- **Mode**: role-scoped implementation review (AgentDS)
- **Gate**: `Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`
- **Review input**: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-evidence-20260614.md`
- **Accepted root cause**: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
- **Included scope**: `docs/fund-analysis-template-draft.md`, `tests/agent/test_runner.py`, `tests/fund/template/test_typed_contracts.py`, `tests/README.md`
- **Supporting reads**: `AGENTS.md`, `docs/implementation-control.md`, `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/evidence_availability.py`, `fund_agent/fund/template/typed_contracts.py`
- **Verification commands executed**:
  - `git diff -- docs/fund-analysis-template-draft.md tests/agent/test_runner.py tests/fund/template/test_typed_contracts.py tests/README.md`
  - `git diff --check`
  - `uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_evidence_availability_envelope_remains_value_error -q`
  - `uv run pytest tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks tests/fund/template/test_typed_contracts.py::test_current_typed_projection_matches_template_json_exact_fields -q`
  - `uv run ruff check tests/agent/test_runner.py tests/fund/template/test_typed_contracts.py`
- **Excluded scope**: Service layer, Host layer, Agent runner internals beyond the writer preflight path, live/provider/LLM, source/PDF, other chapters' required-output items
- **Parallel review coverage**: 无（单 reviewer 角色范围内审查）

## Intent Verification

实现声称修复：`ch3.required_output.item_01` 在 missing-evidence 状态下不再抛出 provider-before `ValueError`，转为 zero-provider fact-gap 阻断。

实际执行路径验证：

1. 模板 JSON 变更（`docs/fund-analysis-template-draft.md:667`）：`when_evidence_missing` 从 `null` 改为 `"block"`，同时新增 `missing_evidence_reason`。
2. Typed 投影（`fund_agent/fund/template/typed_contracts.py:498-508`）：`_project_required_output_entries()` 忠实读取 JSON 字段 → `RequiredOutputItem.when_evidence_missing="block"`。
3. Evidence availability 派生（`fund_agent/fund/evidence_availability.py:247-251`）：`ch3.required_output.item_01` 映射到 `("structured.basic_identity", "structured.portfolio_managers")`。任一 fact missing 时 `_combine_statuses()` 按优先级返回 `"missing"`（`evidence_availability.py:585-603`）。
4. Writer preflight（`fund_agent/fund/chapter_writer.py:931-968`）：`_required_output_plan_item()` → `_required_output_action(item, "missing")` → `behavior="block"` → `return "block"`（`chapter_writer.py:1024`）。
5. Preflight issue 生成（`chapter_writer.py:1090-1113`）：`_required_output_preflight_issues()` 为 `action="block"` 的 plan 生成 `missing_required_facts` issue。
6. Writer 主入口（`chapter_writer.py:759-762`）：`preflight_issues` 非空 → `_blocked_result()` 直接返回，不调用 `llm_client.generate_chapter()`。

全链路走通：模板声明 → typed 投影 → availability 派生 → action 裁定 → preflight 阻断 → zero provider call。与实现证据声称的行为一致。

## Findings

### 1-已修复-中-typed availability 空壳场景下的 `missing_availability` 过度保守

- **入口/函数**: `_required_output_plan_item()` → `missing_availability` 判定 (`fund_agent/fund/chapter_writer.py:955`)
- **文件(行号)**: `fund_agent/fund/chapter_writer.py:955`
- **输入场景**: `EvidenceAvailability.requirements` 为空（如 `test_chapter_3_missing_typed_availability_blocks_before_provider` 的 monkeypatch 场景），但 typed template 中某 item 声明了 `when_evidence_missing="render_evidence_gap"`。
- **实际分支**: `requirement is None` 为 True，`item.when_evidence_missing is not None` 为 True → `missing_availability = True` → `action = "block"`。
- **预期行为**: 若 typed template 已声明不缺证（`when_evidence_missing` 非 null），且只是 availability 系统恰好无此 requirement 映射，可能应允许 render 而非强制 block。但当前保守行为将 `render_evidence_gap` / `render_minimum_verification_question` 等已声明降级行为也强制为 `block`。
- **实际行为**: `action = "block"`，生成 preflight issue，writer 阻断。
- **直接证据**: `chapter_writer.py:955` 行 `missing_availability = requirement is None and item.when_evidence_missing is not None` 不区分 typed 已声明的具体降级行为类型，只判断 `when_evidence_missing is not None`。
- **影响**: availability 系统与模板不同步时，本可安全降级为 `render_evidence_gap` 的 item 被错误阻断。当前生产环境下 availability 与模板保持同步，实际触发概率低；此路径主要出现在测试 monkeypatch 场景。但在未来 availability 重构或新 item 添加时，可能造成不必要的 fail-closed。
- **建议改法和验证点**: `missing_availability` 分支应区分 `when_evidence_missing` 的具体值：`"block"` 和 `"delete_if_not_applicable"` 可继续 block；`"render_evidence_gap"` 和 `"render_minimum_verification_question"` 可考虑按 typed 声明的行为执行，因为 typed template 作者已明确审查并接受了该降级。或者，在 availability 无映射时应至少记录 `unreviewed` 状态而非直接 block。
- **修复风险（低）**: 需要确保区分逻辑不破坏 `"block"` 的 fail-closed 语义。建议先在 availability 同步校验层确保 `_KNOWN_REQUIREMENT_IDS` 与 typed item id 的交叉校验，从源头减少不同步可能。
- **严重程度（中）**: 当前生产路径不受影响（availability 与模板同步），但 `missing_availability` 分支的过度保守可能在未来演进中造成不必要的阻断。

## Open Questions

- `missing_availability` 分支是否需要更细粒度的 typed behavior 区分？当前实现对所有非 null `when_evidence_missing` 一视同仁为 `block`，是否为有意设计选择（fail-closed by default for unknown availability）还是未覆盖的边界情况？建议 controller 在下一 gate 裁决。

## Residual Risk

- 其他章节的 required-output items 中仍有 `when_evidence_missing=null` 的条目。若其同源 evidence 变为 missing，`_required_output_action()` 的 `behavior is None` 分支（`chapter_writer.py:1015`）仍会抛出 `ValueError`。已在实现证据 `Residuals` 表中记录为 `Deferred candidate`，本 gate 不处理。
- `test_chapter_3_missing_basic_manager_info_blocks_before_provider` 仅覆盖 `portfolio_managers` missing + `basic_identity` available 的组合。未覆盖两者均 missing、仅 `basic_identity` missing 或 `unreviewed` 状态。但 `_combine_statuses()` 和 `_required_output_action()` 的 fallthrough 逻辑简单，未覆盖状态组合的风险较低。
- 无 post-fix live 验证；release/readiness 保持 `NOT_READY`。符合本 gate 的 no-live 边界。

## Verdict

**PASS**

模板修复和测试正确将第 3 章基金经理基本信息缺证，从 provider-before `ValueError` / `code_bug` 转换为 zero-provider fact-gap 阻断。全链路逐行走读确认：typed template 声明 → availability 派生 → action 裁定 → preflight 阻断 → 零 provider 调用。一个中等严重程度的 finding（`missing_availability` 过度保守）建议 controller 裁决，不影响当前修复的正确性。
