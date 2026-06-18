# MVP typed template truth-source replacement Slice 4 code review — AgentDS

## Review metadata

- Reviewer: AgentDS
- Date: 2026-06-04
- Gate: `MVP typed template truth-source replacement gate`
- Scope: Slice 4 typed consumers regression only
- Baseline: `202b396 gateflow: accept typed template truth source slice3`

## Scope files reviewed

- `fund_agent/fund/template/typed_contracts.py` (working tree diff vs HEAD)
- `tests/fund/template/test_typed_contracts.py` (working tree diff vs HEAD)
- `tests/fund/template/test_chapter_contract_constraints.py` (working tree diff vs HEAD)
- `tests/fund/test_evidence_availability.py` (working tree diff vs HEAD)
- `tests/services/test_chapter_orchestrator.py` (working tree diff vs HEAD)
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md`
- Accepted plan: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md`
- Accepted plan controller judgment: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md`
- Slice 3 controller judgment: `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-controller-judgment-20260604.md`
- Slice 3 DS review: `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-ds-20260604.md`
- Slice 3 MiMo review: `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-mimo-20260604.md`

## Supplementary correction acknowledged

This review incorporates the user's supplementary correction specifying exact file names and symbol names (`chapter_contract_constraints.py`, `_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES`) and the complete review focus checklist with 7 items. All review-focus items are explicitly addressed below.

## Validation reproduced

```text
# Slice 4 targeted consumer suite
uv run pytest tests/fund/template/test_chapter_contract_constraints.py \
  tests/fund/test_evidence_availability.py \
  tests/fund/test_chapter_writer.py \
  tests/fund/test_chapter_auditor.py \
  tests/services/test_chapter_orchestrator.py -q
→ 171 passed in 0.71s, exit 0

# Template consistency
uv run pytest tests/fund/template/test_contracts.py \
  tests/fund/template/test_typed_contracts.py -q
→ 46 passed in 0.50s, exit 0

# Static quality
uv run ruff check fund_agent/fund/template/typed_contracts.py \
  tests/fund/template/test_typed_contracts.py \
  tests/fund/template/test_chapter_contract_constraints.py \
  tests/fund/test_evidence_availability.py \
  tests/services/test_chapter_orchestrator.py
→ All checks passed!, exit 0

# Whitespace diff check
git diff --check -- fund_agent/fund/template/typed_contracts.py \
  tests/fund/template/test_typed_contracts.py \
  tests/fund/template/test_chapter_contract_constraints.py \
  tests/fund/test_evidence_availability.py \
  tests/services/test_chapter_orchestrator.py
→ exit 0, no output
```

---

## Review Focus Checklist

### 1. Typed consumers 使用 template-doc-projected typed manifest，而非旧 code-authored mapping

**PASS。**

- `tests/services/test_chapter_orchestrator.py` 的 `test_typed_contract_path_preserves_independent_body_execution` (L2090-L2151) 显式调用 `load_typed_template_contract_manifest()` 获取 `typed_by_id`，然后对比：
  - `rows[2].attempts[0].writer_result.prompt.required_output_items == tuple(item.item_id for item in typed_by_id[2].required_output_items)` — Ch2 required output ids 完全来自 typed manifest 投影
  - `rows[3].attempts[0].writer_result.prompt.required_output_items == tuple(item.item_id for item in typed_by_id[3].required_output_items)` — Ch3 同理
  - `ch3_plan_by_id["ch3.required_output.item_03"].text == typed_by_id[3].required_output_items[2].text` — required output text 来自 typed manifest
  - `auditor.requests[0].audit_focus == typed_by_id[2].audit_focus` — Ch2 audit_focus 来自 typed manifest
  - `auditor.requests[1].audit_focus == typed_by_id[3].audit_focus` — Ch3 audit_focus 来自 typed manifest
- `tests/fund/template/test_chapter_contract_constraints.py` 的 `test_sidecar_wraps_existing_chapter_contract_without_parallel_truth` (L56-L72) 新增 typed manifest 对比：sidecar 的 `must_answer`/`must_not_cover` 同时匹配 untyped manifest 和 typed projection 的 text。
- 无旧 `_CURRENT_TEXT_MAPPING` 或硬编码 id/text 被 typed consumer 测试引用。

### 2. `chapter_contract_constraints.py` 是否仍是 public-manifest consumer；测试是否证明 wrapper 匹配 untyped + typed projection，overlay 仍可解析

**PASS。**

- `fund_agent/fund/template/chapter_contract_constraints.py` 本身无任何变更（`git diff HEAD` 输出为空）。模块仍只从 `contracts.py` 导入 `load_template_contract_manifest`（L19），不从 `typed_contracts.py` 导入任何内容。确认为 no-change public-manifest consumer。
- 测试 `test_sidecar_wraps_existing_chapter_contract_without_parallel_truth` 新增三层验证（L56-L80）：
  1. **untyped alignment**：`constraint.must_answer == source_by_id[chapter_id].must_answer` — default wrapper 与 untyped manifest text 元组一致
  2. **typed alignment**：`constraint.must_answer == tuple(item.text for item in typed_by_id[chapter_id].must_answer)` — default wrapper 同时与 typed manifest clause text 一致
  3. **overlay resolution**：`constraints_for_chapter(3, "active_fund")` 返回 `("default", "active_fund")` 两个 fund_type_slot，且两者的 `must_answer` 均与 source manifest Ch3 一致 — overlay 正确解析
- 已覆盖 `must_answer` 和 `must_not_cover` 两种 contract 字段。

### 3. EvidenceAvailability Ch2/Ch3 私有 specs 与 projected typed manifest 交叉验证

**PASS，含 1 个 LOW finding。**

新增 `test_requirement_specs_cross_validate_against_projected_typed_manifest` (L174-L223) 覆盖全部五个私有符号：

| 私有符号 | 验证方式 | 结果 |
|---|---|---|
| `_CH2_REQUIREMENT_SPECS` | `ch2_spec_ids == ch2_manifest_ids` — 精确双向相等（cover Ch2 must_answer clause ids + required_output item ids） | PASS |
| `_CH3_REQUIREMENT_SPECS` | `ch3_required_output_ids <= (ch3_base_spec_ids \| _CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS)` — manifest 的 required output ids 全在 specs 并集中 | PASS |
| `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID` | `in ch3_predicate_requirement_ids` — 该 requirement id 存在于 manifest Ch3 predicate 中 | PASS |
| `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` | `<= ch3_required_output_ids` — 全在 manifest Ch3 required output 中 | PASS |
| `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` | `<= ch3_base_spec_ids` — 全在 `_CH3_REQUIREMENT_SPECS` 中 | PASS |

Ch2 subcontract 交叉验证更细致：每个 subcontract（`performance`/`attribution`/`cost`）的 `_CH2_REQUIREMENT_SPECS` requirement_ids 与 manifest `internal_subcontracts[*].requirement_ids` 逐项精确相等（L195-L206）。

测试通过 `import fund_agent.fund.evidence_availability as evidence_availability_module` 访问私有符号，明确文档化了耦合关系。

**LOW finding D1**：Ch3 反向全覆盖不完整。测试验证了 `ch3_required_output_ids ⊆ (base ∪ actual_behavior)` 的单向子集关系，但未检查 `_CH3_REQUIREMENT_SPECS` 中的每个 requirement_id 是否都能在 typed manifest 中找到对应条目（Ch2 做了精确相等，Ch3 只做了单向子集）。当前数据下无实际漂移，但若未来有人向 `_CH3_REQUIREMENT_SPECS` 新增 requirement 但忘记更新模板 JSON，此测试不会发现。详见 Finding D1。

### 4. Service typed path regression 覆盖 template doc → typed manifest → EvidenceAvailability → writer/auditor/service

**PASS。**

- `test_typed_contract_path_preserves_independent_body_execution` (L2086-L2151) 已加强为端到端 typed projection regression：
  - **template doc → typed manifest**：L2090 `typed_manifest = load_typed_template_contract_manifest()`
  - **→ EvidenceAvailability**：L2094-L2101 monkeypatched `derive_evidence_availability` 内部验证 `availability.require("ch2.required_output.item_01").chapter_id == 2` 和 `availability.require("ch3.required_output.item_03").status == "unreviewed"`
  - **→ writer**：L2130-L2135 验证 Ch2/Ch3 `required_output_items` = `typed_by_id[chapter_id].required_output_items[*].item_id`
  - **→ writer evidence plan**：L2140-L2144 验证 `ch3.required_output.item_03` 的 `text`（来自 typed manifest）、`action`（`render_evidence_gap`）、`availability_status`（`unreviewed`）
  - **→ auditor**：L2147-L2149 验证 Ch2/Ch3 `audit_focus` = `typed_by_id[chapter_id].audit_focus`
  - **→ service final state**：L2150-L2151 验证 `skipped_chapter_ids == ()`，`stop_reason != "dependency_missing"`
- 测试只用 monkeypatch + FakeClient，无 provider/network/repository 访问。

### 5. LensKey runtime guard 是否正确解决 Slice 3 MiMo M1，且无 schema/behavior 漂移

**PASS。**

Slate 3 MiMo M1 指出 `_project_typed_lens_rules` 用 `cast(LensKey, ...)` 读取 fund_type，缺少运行时闭集校验。

Slice 4 的修复：

- `typed_contracts.py` L67-L71 新增 `SUPPORTED_LENS_KEYS`：从 `LensKey`（`FundType | Literal["default"]`）通过 `get_args` 递归提取所有合法 string literal 值。`LensKey = FundType | Literal["default"]`，`FundType = Literal["index_fund", "active_fund", ...]`，因此 `SUPPORTED_LENS_KEYS` 包含全部 6 个 `FundType` 字面量与 `"default"`。
- `typed_contracts.py` L811-L812 在 `_validate_preferred_lens` 中新增 guard：`if rule.fund_type not in SUPPORTED_LENS_KEYS: raise ValueError(...)`。此 guard 在 `validate_typed_template_contract_manifest` → `_validate_preferred_lens` 路径中触发，即 typed manifest load/validation 阶段 fail-closed。
- `tests/fund/template/test_typed_contracts.py` L358-L385 新增 `test_preferred_lens_fund_type_literal_is_closed`：构造 `fund_type="unsupported_fund"` 的非法 lens rule，assert `ValueError` 带 `"preferred_lens fund_type 不受支持"` 消息。

验证：

- 46 个 typed + untyped 测试全部通过，证明现有合法 `FundType` 值全部在 `SUPPORTED_LENS_KEYS` 中（否则 `load_typed_template_contract_manifest()` 就会 fail）。
- 无 behavior 漂移：`_project_typed_lens_rules` 的 `cast(LensKey, ...)` 保持不变（type-level only），运行时校验推迟到 `_validate_preferred_lens` 统一处理——这是 Slice 3 既有的 validate-first-then-return 模式，不引入新语义。

### 6. 非目标仍禁止

**PASS。**

对 diff 中所有变更文件和新增测试做全文搜索，确认无以下关键词侵入：

- `provider`、`runtime`、`live_probe`、`Host`、`Agent`（仅限 runtime 上下文）、`multi_year`、`score_loop`、`golden`、`readiness`、`PR`、`release`

`typed_contracts.py` 变更仅新增 8 行（SUPPORTED_LENS_KEYS 常量定义 + 1 个 if guard），不涉及 provider/runtime/Agent/score/golden/readiness。

测试文件：
- `test_chapter_contract_constraints.py`：仅新增 typed manifest 对齐断言和 overlay 解析断言
- `test_evidence_availability.py`：仅新增模块级常量交叉验证
- `test_chapter_orchestrator.py`：仅增强已有 typed path 测试的断言精度
- `test_typed_contracts.py`：仅新增 LensKey 闭集负面测试

全部变更仅限 typed consumer 回归验证范围，不改变 deterministic analyze/checklist 行为。

### 7. 测试不得依赖 provider/network/repository/PDF/cache/source helper

**PASS。**

逐项检查：

- **provider**：无。`test_chapter_orchestrator.py` 的 typed path 测试使用 `_ChapterPlanWriterClient` 和 `_FakeAuditLLMClient` fake 客户端 + `monkeypatch.setattr` 替换 `derive_evidence_availability`。
- **network**：无。无 `httpx`、`requests`、`urllib` 调用。
- **repository**：无。`evidence_availability` 交叉验证测试只读取模块级 Python 常量（`_CH2_REQUIREMENT_SPECS` 等 tuple of dataclass instances）。
- **PDF**：无。无 PDF 解析或文件读取。
- **cache**：无。无缓存读写。
- **source helper**：无。无 `FundDocumentRepository` 或来源相关调用。

唯一可能触发文件读取的是 `load_typed_template_contract_manifest()` → 读取 `docs/fund-analysis-template-draft.md`，这在 plan 中明确允许（"读取模板 markdown 是 repository template metadata，不是基金年报数据"）。

---

## Findings

### Finding D1: Ch3 private spec 反向全覆盖不完整（severity: LOW）

- 位置：`tests/fund/test_evidence_availability.py` L207-L223 `test_requirement_specs_cross_validate_against_projected_typed_manifest`
- 证据：Ch2 交叉验证使用精确双向相等 `ch2_spec_ids == ch2_manifest_ids`（L216），但 Ch3 基础 specs 只做了单向子集检查：`ch3_required_output_ids <= (ch3_base_spec_ids | ...)` （L221-L223）。测试不检查 `_CH3_REQUIREMENT_SPECS` 中的每个 id 是否反向存在于 typed manifest 的 `must_answer` / `must_not_cover` / `required_output_items` 中。
- 影响：若未来有人在 `_CH3_REQUIREMENT_SPECS` 新增 requirement 但忘记同步更新模板 JSON，此测试不会报警。当前数据无实际漂移，属于防御性覆盖缺口。
- 建议：在 Slice 5 docs sync 或后续 evidence-availability contract gate 中补充反向全覆盖断言，确保 `_CH3_REQUIREMENT_SPECS` 的每个 id 都能追溯到 typed manifest 中的具体 clause 或 output item。
- 是否为阻塞：否。当前数据一致，46 测试通过。

### Finding D2: monkeypatched 函数内硬编码 requirement id 不与 typed manifest 联动（severity: LOW）

- 位置：`tests/services/test_chapter_orchestrator.py` L2099-L2100
- 证据：`_record_derive_availability` 内部断言 `availability.require("ch2.required_output.item_01").chapter_id == 2` 和 `availability.require("ch3.required_output.item_03").status == "unreviewed"`。这些 `"ch2.required_output.item_01"` 和 `"ch3.required_output.item_03"` 是硬编码字符串，不是从 `typed_by_id` 推导。
- 影响：若模板 JSON 中这些 requirement id 的 index 或 id 本身发生变化，hardcoded 字符串不会跟随变化。但这些 id 是 contract-level 稳定标识符（在 `EvidenceRequirementId` Literal guard 中锁定），且同一测试函数已有大量 `typed_by_id` 对照断言覆盖其余字段。属于冗余防御缺口，不影响 regression 检测能力。
- 建议：可考虑改为 `typed_by_id[2].required_output_items[0].item_id` 以完全消除硬编码，但当前做法可接受。
- 是否为阻塞：否。

---

## Summary

- **BLOCKING**: 0
- **HIGH**: 0
- **MEDIUM**: 0
- **LOW**: 2 (D1: Ch3 reverse cross-validation incomplete; D2: hardcoded requirement ids in monkeypatched function)

## Verdict: PASS — no blocking findings

Slice 4 correctly validates typed consumers against the template-doc-projected typed manifest, not old code-authored mapping assumptions. `chapter_contract_constraints.py` is confirmed as a no-change public-manifest consumer with zero source changes; its tests now prove wrappers match both untyped and typed projections while active_fund overlay still resolves. EvidenceAvailability Ch2/Ch3 private specs (`_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES`) are cross-validated against the projected typed manifest. Service typed path regression covers template doc → typed manifest → EvidenceAvailability → writer/auditor/service typed path including required output ids/text and audit_focus from typed manifest. LensKey runtime guard correctly resolves Slice 3 MiMo M1 without introducing schema/behavior drift. Non-goals (deterministic analyze/checklist, provider/runtime/live probe, Host/Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/release) remain preserved. Tests avoid provider/network/repository/PDF/cache/source helper access. 46 typed/untyped + 105 targeted consumer + 171 full consumer tests pass with clean ruff.

## Residual risks

| Risk | Severity | Blocking? | Disposition |
|---|---|---|---|
| D1: Ch3 reverse cross-validation not bidirectional | LOW | No | Defer to Slice 5 docs sync or future evidence-availability contract gate |
| D2: Hardcoded requirement ids in monkeypatched function | LOW | No | Accept as-is; ids are contract-level stable in `EvidenceRequirementId` Literal guard |
| Slice 3 LOW findings (orphan reason, KeyError shape, double file read) not addressed | LOW | No | Explicitly deferred to Slice 5 per Slice 4 implementation evidence |
| `EvidenceAvailability` Ch3 actual-behavior aggregation specs still owned in code, not in template doc | INFO | No | Accepted residual from Slice 4 implementation evidence; runtime derivation specs belong in code |
