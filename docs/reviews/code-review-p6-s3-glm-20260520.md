# Code Review

## Scope

- Mode: current changes
- Branch: main
- Base: main
- Output file: `docs/reviews/code-review-p6-s3-glm-20260520.md`
- Included scope: P6-S3 deterministic programmatic CHAPTER_CONTRACT audit — `fund_agent/fund/audit/audit_programmatic.py`, `fund_agent/fund/audit/contract_rules.py` (new), `fund_agent/fund/template/chapter_blocks.py` (new), `fund_agent/fund/template/renderer.py`, `fund_agent/fund/template/__init__.py`, `tests/fund/audit/test_audit_programmatic.py`, `tests/fund/template/test_renderer.py`, `tests/fund/integration/test_p3_cli_e2e_matrix.py`, `docs/design.md`, `fund_agent/fund/README.md`, `tests/README.md`
- Excluded scope: Service/UI/Engine/CLI behavior changes (verified: only test assertions updated), quality gate, extraction, fund type, document repository
- Parallel review coverage: 无，单 reviewer 全量走读

## Findings

### 001-未修复-[中]-C2 章节块元数据校验路径无直接测试覆盖

- **入口/函数**: `run_programmatic_audit` → `_audit_contract_conformance` → `_audit_chapter_block_metadata`
- **文件(行号)**: `audit_programmatic.py:352-386`; `tests/fund/audit/test_audit_programmatic.py`
- **输入场景**: `ProgrammaticAuditInput` 显式传入 `chapter_blocks`，其中某 block 的 `title`、`heading` 或 `chapter_id` 与 `contract` 不一致
- **实际分支**: 现有 C2 测试均通过修改 `report_markdown` 后 re-split 触发问题。`split_rendered_chapter_blocks` 是 fail-closed 的——一旦 Markdown 标题或章节序列异常就 raise `ValueError`，被 `_resolve_chapter_blocks_for_audit` 捕获为 P1，永远不会走到 C2 元数据校验
- **预期行为**: `_audit_chapter_block_metadata` 应能检测显式传入的 `chapter_blocks` 中 `chapter_id != contract.chapter_id`、`title != contract.title`、`heading != expected_heading`、或 `chapter_ids != (0..7)` 的不一致
- **实际行为**: 代码逻辑正确（已用 `dataclasses.replace` 手动验证，传入 `title='WRONG TITLE'` 的 block 能正确触发 C2 issue）。但测试套件中没有任何 test case 构造显式畸形 `chapter_blocks` 来覆盖这些路径
- **直接证据**: `audit_programmatic.py:377-385` 有 4 个独立校验条件；`test_audit_programmatic.py` 中所有 C2 测试均通过修改 Markdown 后 re-split，splitter 的 fail-closed 机制使这些校验在测试中不可达
- **影响**: 若后续重构 `_audit_chapter_block_metadata` 并引入回归，无测试能捕获
- **建议改法和验证点**: 新增测试：用 `dataclasses.replace` 构造 `title`/`heading`/`chapter_id` 不一致的 block，显式传入 `chapter_blocks`，断言 C2 issue message 包含对应不一致描述。同时测试 `chapter_ids` 不完整（如只传 7 个 block）触发 C2 sequence issue
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 002-未修复-[低]-renderer label 部分值用 `next_minimum_verification` 代理语义不匹配的 required item

- **入口/函数**: `_render_chapter_0`
- **文件(行号)**: `renderer.py:191-192`（diff 上下文中 `- 当前最值得盯住的变量` 和 `- 当前最大的风险` 两行）
- **输入场景**: 正常渲染路径，`checklist_result.next_minimum_verification` 和 `risk_check_result.next_minimum_verification` 都有值
- **实际分支**: label 的值使用 `next_minimum_verification` 作为代理
- **预期行为**: plan 明确要求 "Missing data must be explicit as `数据不足` / `未披露` / `未定位`; do not infer unavailable values"
- **实际行为**: `当前最值得盯住的变量：{checklist.next_minimum_verification}` 和 `当前最大的风险：{risk_check.next_minimum_verification}` 使用了"下一步验证问题"的值作为"最值得盯住的变量"和"最大风险"的代理。Marker 通过审计，但 label 声称的内容与实际数据语义不完全匹配
- **直接证据**: `renderer.py` diff 中 `- 当前最值得盯住的变量：{input_data.checklist_result.next_minimum_verification}` 和 `- 当前最大的风险：{input_data.risk_check_result.next_minimum_verification}`；这两个值是验证问题文本，不是变量名或风险描述
- **影响**: 低。Marker 存在且审计通过，当前不存在正确的变量/风险数据源时用最接近的数据填充。但违反了 plan 的 "do not infer unavailable values" 约束
- **建议改法和验证点**: 将这两个 label 的值改为 `_INSUFFICIENT_TEXT` + 上下文说明（如 `数据不足，当前未提供独立的风险识别输入`），或在后续 slice 中为这两个 required item 提供真正的数据源
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Architecture Boundary Review

Pass. `audit_programmatic.py` 不导入 `renderer.py`；所有 `chapter_blocks` 相关类型和 splitter 函数从 `template/chapter_blocks.py` 导入，dependency direction 正确：`contracts.py ← chapter_blocks.py ← renderer.py / audit_programmatic.py`。`__init__.py` 使用 `__getattr__` lazy import 避免触发 cycle，验证通过：audit import 后 renderer 未加载；仅显式 import `render_template_report` 时才加载 renderer。`contract_rules.py` 属于 `audit/` 模块，只依赖 `template/contracts.py`（manifest 读取和校验），不依赖 `renderer.py` 或 `chapter_blocks.py`。

## Import Cycle Verification

```text
contracts.py ← chapter_blocks.py ← audit_programmatic.py   ✅ 无 cycle
contracts.py ← chapter_blocks.py ← renderer.py → audit     ✅ audit 不反向导入 renderer
```

Python 验证：`import audit_programmatic` 后 `sys.modules` 不含 `renderer`；仅 `from template import render_template_report` 后才加载。

## Required Item Marker Matrix Verification

- Manifest `required_output_items`: 45 条
- `contract_rules.py` 规则: 45 条
- 覆盖率: 100%，无遗漏无多余
- `危级/降级阈值` typo 保留与 manifest 一致 ✅

## Forbidden Content Coverage

- Manifest `must_not_cover`: 27 条
- Deterministic forbidden rules: 9 条
- 未覆盖的 18 条均为无法用字面 marker 判定的语义约束（如"不写成摘要复述"、"不写成风险罗列"），plan 明确要求不覆盖这些条目 ✅

## Renderer Output Scope Review

- Renderer 仅添加 plan marker matrix 中列出的 `renderer-label-needed` label，未引入新的数据源或 prose 重写 ✅
- `_FORBIDDEN_TERMS` 和 `_validate_report_wording` 未被修改 ✅
- `ProgrammaticAuditInput` 构造正确传入 `chapter_blocks=chapter_blocks` ✅
- 现有 Service/UI/CLI 行为未改变（仅 `checked_rules` assertion 更新）✅

## Open Questions

- 无

## Residual Risk

- Finding 001 的 C2 元数据校验路径无测试覆盖，存在回归风险。
- Finding 002 的 label 值代理问题在后续 slice 需要回归。
- `load_programmatic_contract_rules()` 在每次 audit 调用时重新加载和校验全部规则。MVP 阶段可接受，但若 manifest 或规则集增长，应考虑缓存。
- `_REQUIRED_CHAPTER_TITLES` 的 P1 substring 匹配机制沿用了 pre-existing 设计，manifest 派生后标题为完整标题，当前匹配行为正确但不如精确匹配健壮。非 P6-S3 引入。
