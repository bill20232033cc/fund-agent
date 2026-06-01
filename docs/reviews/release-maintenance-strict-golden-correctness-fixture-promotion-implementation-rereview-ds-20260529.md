# Strict Golden Correctness / Fixture Promotion — Implementation Re-Review (AgentDS)

日期：2026-05-29
角色：AgentDS implementation re-reviewer
审查对象：修正后的 decision artifact 与 implementation evidence artifact
前置阅读：DS implementation review (M1/M2)、MiMo implementation review (F1/F2)、修正后两个 artifact

## Re-Review Scope

本 re-review 只检查 DS M1/M2 和 MiMo F1/F2 是否已被修正后的 decision/evidence 关闭。不重新全量审查。

## Finding Closure Verification

### M1 (DS): `unavailable_records` 跨基金语义 — CLOSED

原 finding：004194 的 `unavailable_records=145` 未区分跨基金记录与本基金 intra-fund 不可比。

修正后状态：

- Decision §004194 Covered Scope Breakdown 明确声明：`unavailable_records=145` 全部为跨基金 `fund_code=004393` golden records，004194 intra-fund unavailable=0
- Evidence §Extracted Correctness Evidence 同样记录："004194 cross-fund unavailable split: all 145 are fund_code=004393 golden records; 004194 intra-fund unavailable=0"
- Decision §Strict Correctness Field Paths 新增 `covered` 语义说明：必须同时读取 `comparable_records`、`unavailable_records` 和 `record_results[]` 的 fund/field 分布

**结论：已关闭。** 跨基金组成在两类 artifact 中均已显式标注。

### M2 (DS): 004194 `covered` 仅覆盖 index_profile — CLOSED

原 finding：004194 的 `covered` 仅覆盖 5 个 index_profile 子字段 (3.3%)，future gate 可能误读为广义 correctness 验证。

修正后状态：

- Decision §004194 Covered Scope Breakdown 完整列出 5 个 matched 字段，并声明 `index_profile` 为 conditional P1（index/enhanced-index 适用），P0 strict correctness coverage = 0
- Decision §Strict Correctness Field Paths 新增 `covered` 语义约束："`coverage_scope=covered` 只表示当前 `comparable_records` 全部 matched 且无 mismatch，不表示 `total_records` 的大部分已验证"
- Decision table 004194 row 的 score_level_field_comparability 列标注 "comparable scope is index_profile-only; P0 strict correctness coverage is 0"
- 004194 decision 已从 `promotion_prep_ready_candidate` 降级为 `conditional_candidate_pending_p0_coverage_decision`

**结论：已关闭。** scope 限制、P0=0、语义说明、conservative 降级四项均已落实。

### F1 (MiMo): 004194 P0 零覆盖但标为 promotion_prep_ready — CLOSED

原 finding：004194 5 个 matched 字段全部为 P2 `index_profile`（P0 零覆盖），却被标为 `promotion_prep_ready_candidate`；004393 有 9 个 P0 matched 反而只是 `conditional_candidate`，语义倒挂。

修正后状态：

- 004194 decision 改为 `conditional_candidate_pending_p0_coverage_decision`，不再是 `promotion_prep_ready_candidate`
- §004194 Covered Scope Breakdown 显式记录 P0=0 total/comparable/matched，P1=5 全 matched
- Final Decision 节确认：`fixture_state_after_gate=absent`，`promotion_allowed=false`，无 promotion 授权
- 004393 保持 `conditional_candidate_pending_partial_coverage_decision`（P0 9/11，81.8%），与 004194（P0 0/0）的 decision 级别一致——两者均为 `conditional_candidate_pending_*`，语义不倒挂

关于 `index_profile` 的 P1 vs P2 分类差异：decision artifact 引用 `docs/design.md` §7.3 作为权威来源，将 `index_profile` 归类为 "conditional P1 for index/enhanced-index funds"。无论采用 P1 还是 P2，P0=0 的事实不变，conservative 降级决策不依赖此分类。

**结论：已关闭。** 降级消除了语义倒挂，P0=0 已显式记录。

### F2 (MiMo): 004393 P0/P1/P2 分类来源未引用 — CLOSED

原 finding：P0/P1/P2 breakdown 的分类来源未显式引用 design.md 或 extraction_score.py。

修正后状态：

- Decision §004393 Partial Coverage Breakdown 新增："Priority classification source：`docs/design.md` §7.3 defines `extraction_score` field priorities and §7.4 defines quality-gate severity semantics for P0/P1 fields; the code implementation source named there is `fund_agent/fund/extraction_score.py`"
- Decision §004194 Covered Scope Breakdown 同样引用相同来源
- Evidence §Extracted Correctness Evidence 也增加相同引用

**结论：已关闭。** 两处 breakdown 和 evidence 均已显式引用权威来源。

### F3 (MiMo): `covered` + `unavailable_records=145` 语义张力 — CLOSED

原 finding（low）：`covered` 不等同于"大部分已验证"的语义未解释。

修正后状态：

- Decision §Strict Correctness Field Paths 新增独立段落说明 `covered` 的精确语义：只表示 comparable_records 全部 matched，不表示 total_records 的大部分已验证，必须同时读取其他字段

**结论：已关闭。** 语义说明已写入 decision artifact 的前置规则节。

## Git Diff Check 验证

```
git diff --check -- docs/reviews/...decision-20260529.md docs/reviews/...implementation-evidence-20260529.md
```

无输出（clean），无 whitespace 错误。两个产物均为 untracked Markdown-only 文件，无 JSON 产出，`python -m json.tool` 不适用。验证仍合理。

## Guardrails 再确认

| Guardrail | 原始 DS review 状态 | 修正后状态 | 变化 |
|---|---|---|---|
| `promotion_allowed=false` 全部 10 行 | ✅ | ✅ | 不变 |
| 无 `fixture_state=promoted` | ✅ | ✅ | 不变 |
| 无 `fixture_state=promotion-prep-ready` | ✅ | ✅ | 不变 |
| 无 golden answer / fixture 修改 | ✅ | ✅ | 不变 |
| 无 QDII probing | ✅ | ✅ | 不变 |
| 无 FQ0-FQ6 weakening | ✅ | ✅ | 不变 |
| 无 commit | ✅ | ✅ | 不变 |
| 无 JSON manifest 修改 | ✅ | ✅ | 不变 |

**全部 guardrails 维持不变。** 修正仅涉及两个 Markdown artifact 内的语义说明、scope 标注、decision enum 值，不触及任何 guardrail 边界。

## 004194 Decision 降级合理性

004194 从 `promotion_prep_ready_candidate` 降级为 `conditional_candidate_pending_p0_coverage_decision` 是保守且合理的：

- 5 个 matched 字段全部为 `index_profile.*`（conditional P1），无 P0 字段经过 correctness 验证
- `coverage_scope=covered` 仅表示 5/5 comparable matched，不代表覆盖面充分
- 降级后 004194 与 004393（`conditional_candidate_pending_partial_coverage_decision`）同属 `conditional_candidate_pending_*` 层级，语义一致
- `promotion_allowed=false` 和 `fixture_state_after_gate=absent` 不变，不产生 promotion 风险

## 004393 `unavailable_records=141` 的隐式拆分

004393 的 P0/P1/P2 breakdown 隐式给出了 intra-fund unavailable 组成（2 P0 + 10 P1 = 12），剩余 ~129 为跨基金 004194 golden records。Decision artifact 未像 004194 那样显式写出 "cross-fund split"，但 M1 仅针对 004194 提出要求，004393 的 breakdown 已足够推导。不构成新 finding。

## Overall Verdict

**PASS** — 无新 finding。

DS M1/M2 和 MiMo F1/F2 已全部关闭。修正后的 decision artifact 和 evidence artifact 在跨基金语义透明性（M1）、scope 限制标注（M2）、P0 coverage 显式记录与 decision 降级（F1）、优先级来源引用（F2）、`covered` 语义说明（F3）五项上均已落实。

Git diff check 验证仍合理。Guardrails 全部不变。004194 降级是保守且正确的处置。可以进入 controller judgment。

## Review Completion

本 re-review 不修改任何 artifact、不执行 promotion、不提交。由 controller 做最终裁决。
