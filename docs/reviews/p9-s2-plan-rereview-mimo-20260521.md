# P9-S2 Quality Gate / Golden Coverage Calibration Plan — Re-Review (MiMo)

- **Reviewer**: AgentMiMo
- **Date**: 2026-05-21
- **Artifact under review**: `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md` (revised)
- **Prior review**: `docs/reviews/p9-s2-plan-review-mimo-20260521.md`

---

## Conclusion

**PASS**

所有前一轮 findings 均已闭环。修订后的计划在状态模型、FQ0 metadata 契约、边界 case 覆盖和 non-goals 方面均达到实现可执行水平。无剩余阻断项。

---

## Finding Closure Verification

### F-01 [Medium] FQ0 语义重载 → CLOSED

**修订内容**：新增 Section 5.1 FQ0/Info Metadata Contract，要求每条 FQ0/info issue 必须包含 `reason` 字段，值域为 `not_configured / fund_not_covered / no_comparable_fields / field_not_comparable`。

**验证**：`reason` 字段使诊断系统可以区分"golden 文件不存在"（`not_configured`）、"文件存在但基金无记录"（`fund_not_covered`）、"基金有记录但无 comparable 字段"（`no_comparable_fields`）。FQ0 rule code 可以承载多种 coverage 缺失场景，因为 metadata 层面已充分解耦。

### F-02 [Medium] comparable_records=0 边界未覆盖 → CLOSED

**修订内容**：
- Section 3 新增 `correctness_no_comparable_fields` 状态：golden 文件存在、当前基金有记录、但 `comparable_records=0`。
- Section 3.1 Mapping 表中 `correctness_no_comparable_fields` 映射为 `status=available, coverage_scope=no_comparable_fields`，`record_results` 为"target-fund records exist but all are unavailable because no comparable field/subfield is exposed"。
- Section 6 extraction_score.py 第 6 条："Treat valid golden file + current fund records + `comparable_records=0` as `no_comparable_fields`, not generic aggregate pass."
- Section 7 测试矩阵第 7 行：期望值收紧为 `scope no_comparable_fields; this must be distinguishable from aggregate pass`。
- Section 8 验收标准第 4 条：显式要求 `comparable_records=0` 触发 `FQ0/info` with `reason=no_comparable_fields`。

**验证**：前一轮发现的 `status="available"` + `comparable_records=0` 导致 FQ0 不触发的 gap 已被完全覆盖。实现路径清晰：`extraction_score.py` 派生 `coverage_scope`，`quality_gate.py` 消费并触发 FQ0。

### F-03 [Low] gate_not_run 与 FQ0 fund_quality 轻微矛盾 → CLOSED

**修订内容**：Section 3 最后一段新增显式定义："`gate_not_run` must mean pre-gate execution failure only: selected-pool CSV missing, CSV schema/validation failure, or membership failure before score/gate execution. It must not include gate-internal sub-rules that ran but produced `FQ0/info`, such as missing `fund_quality`, missing strict golden coverage, or non-comparable correctness fields."

**验证**：`gate_not_run` 的边界已明确为 pre-gate only，与 gate 内部 FQ0/info 触发场景正交。

### F-04 [Low] 测试矩阵 "all fields unavailable" 期望值含糊 → CLOSED

**修订内容**：
- Section 7 测试矩阵第 7 行期望值从含糊的 `partially_covered` 或 `fund_not_comparable` 收紧为明确的 `scope no_comparable_fields; this must be distinguishable from aggregate pass`。
- Section 7 新增 quality gate 层第 11 行："golden fund present but no comparable fields" → `fund-scoped FQ0/info present with reason=no_comparable_fields, aggregate status stays pass absent other issues`。

**验证**：期望值唯一且可测试。实现者可以直接断言 `coverage_scope == "no_comparable_fields"` 和 FQ0 issue `reason == "no_comparable_fields"`。

### F-05 [Low] correctness_required 机制未展开 → CLOSED

**修订内容**：
- Section 9 Non-Goals 新增："Do not implement a `correctness_required` policy mechanism in P9-S2."
- Section 4 新增："P9-S2 must not implement a `correctness_required` policy mechanism. The field `coverage_required=false` is only a diagnostic/default-policy fact in this slice, not a new configurable enforcement system."

**验证**：forward-looking 声明已明确推迟到后续 slice，不会导致实现者在 P9-S2 中临时设计 policy 机制。

---

## Additional Quality Observations (Non-Blocking)

### A-01 [Info] Section 3.1 7-step coverage derivation 顺序清晰

Single-fund `analyze` 的 coverage 派生顺序（`not_configured` → fail-closed on invalid → `fund_not_covered` → `no_comparable_fields` → `partially_covered` → `covered`）逻辑正确，优先级明确。步骤 2-3 对 malformed/invalid golden 文件的 fail-closed 要求防止了"坏 oracle 被静默当无 oracle"的降级路径。

### A-02 [Info] Section 5.1 invalid golden file 不是 FQ0/info 正确

"Empty, malformed, wrong schema version, duplicate, missing required fields, or otherwise invalid strict golden files must fail closed or raise a structured exception." 这防止了一个重要的正确性风险：broken oracle 不应被 FQ0/info 静默掩盖。

### A-03 [Info] Acceptance Criteria 完整覆盖新增状态

Section 8 验收标准新增了 `no_comparable_fields` 触发条件、`correctness_missing_comparable_value` mismatch 子路径、malformed golden fail-closed、CLI stderr info line 等条目，与 Section 3/5/7 的定义一致。

---

## Summary

| 前一轮 Finding | 修订后状态 |
|---------|----------|
| F-01 FQ0 语义重载 | CLOSED — `reason` metadata 已定义 |
| F-02 comparable_records=0 边界 | CLOSED — `no_comparable_fields` 状态和测试已补充 |
| F-03 gate_not_run 边界矛盾 | CLOSED — 显式定义 pre-gate only |
| F-04 测试矩阵期望值含糊 | CLOSED — 期望值收紧为唯一值 |
| F-05 correctness_required 机制 | CLOSED — Non-Goals 已补充 |

**无剩余阻断项。计划可进入实现。**
