# Release Maintenance Report-Quality Baseline S1 Score-Schema Fixture Draft — MiMo Review

> Date: 2026-05-25
> Reviewer: AgentMiMo (phaseflow independent review agent)
> Gate: `report-quality-baseline S1 score-schema fixture draft`
> Verdict: **PASS_WITH_FINDINGS**

---

## Review Lens Checklist

### L1. 是否覆盖七个 report-quality dimensions

**PASS.** §"Canonical Scoring Dimensions" 定义了全部七个维度，与 `docs/design.md` §5.4.1 一一对应：

| design.md §5.4.1 | S1 dimension value | Present |
|---|---|---|
| 事实覆盖度 | `fact_coverage` | Yes |
| 抽取正确性 | `extraction_correctness` | Yes |
| 证据可追溯性 | `evidence_traceability` | Yes |
| 章节契约完整性 | `chapter_contract_completeness` | Yes |
| 最终判断一致性 | `final_judgment_consistency` | Yes |
| 投资建议边界 | `investment_advice_boundary` | Yes |
| 可读性与行动性 | `readability_actionability` | Yes |

每个维度都有中文名称、检查目标和 primary next-gate bias，且说明了 fund type 控制适用性（N/A 需给 reason）。无遗漏。

### L2. schema 字段是否满足 control_doc，并明确拆分 document_identity_status 与 type_slot_membership_status

**PASS.** Next Entry Point 明确要求 "separate fields for document identity verification and fund-type slot membership"。S1 拆分如下：

- `document_identity_status`：`verified_annual_report` / `unverified` / `mismatch` / `source_failed` / `verified_as_annual_report_but_type_gap`
- `type_slot_membership_status`：`matches_slot` / `type_gap` / `taxonomy_pending` / `unknown` / `not_applicable`

两者各有独立值域表，含义清晰。§"Document Identity vs Type-Slot Membership" 明确说明 `verified_as_annual_report_but_type_gap` 不等于 scoring-ready FOF，呼应 S0 controller judgment DS F-2 finding 的 deferred 处置。Schema 的 17 个必填字段和可选字段列表均与 control-doc 要求匹配。

### L3. source_boundary domain 是否清楚，unknown/probe_only 是否被禁止进入 durable baseline

**PASS.** `source_boundary` 值域表定义了 6 个值，每个值有含义和 durable baseline eligibility 说明：

- `repository_derived`：eligible after identity, type-slot, and manual review states pass
- `derived_calculation`：eligible only when input facts and anchors are reviewed
- `external_official`：eligible when source identity and date are explicit
- `manual_review`：eligible as review evidence; machine fixture promotion still needs later gate
- `unknown`：**Not eligible** for durable baseline selection
- `probe_only`：**Not eligible** for durable baseline selection

Stop condition #7 进一步强化："Any record uses `source_boundary=unknown` or `source_boundary=probe_only` as if it were durable evidence" 触发 stop。约束足够清晰。

### L4. issue-based 输出、N/A 分母排除、all-N/A skipped 是否清楚，是否避免 weighted total

**PASS.**

- 明确声明 "S1 does not output weighted total. The mandatory output is localized `issues` and `next_gate_recommendation`."（L98）
- `N/A`："Excluded from denominator"（L105）
- `skipped`："Chapter summary only: every dimension for the chapter is `N/A`. Not passing; excluded from pass rate and reported as skipped."（L106）
- `blocked`："Included as blocked when chapter is otherwise applicable"（L104）
- 明确区分 `N/A`（不适用，有 reason）和 `blocked`（身份/来源/锚点不足），避免 blocked 被降级为 N/A 绕过分母（L108）

Issue 结构模板包含 `issue_id` / `severity` / `field_path` / `problem` / `expected` / `observed_ref` / `next_gate_recommendation` 等字段，支持字段级定位。

### L5. 是否正确处理 S0 fallback candidates 110020/017641/017970 的 unknown_upstream_failure_category，并设置 stop before durable baseline selection

**PASS.** §"S0 Corpus Applicability Rules" 逐一处理三个 fallback candidate：

| Candidate | S1 handling | Correct |
|---|---|---|
| `110020` index | "Repository-verified S0 evidence only. It used fallback with `unknown_upstream_failure_category`; recover original category or exclude before durable baseline selection." | Yes |
| `017641` QDII | Same handling as 110020 | Yes |
| `017970` QDII-FOF | "also fallback has `unknown_upstream_failure_category`; exclude from durable FOF baseline unless both taxonomy and source category are resolved." | Yes |

Stop condition #1："`source_failure_category` for fallback candidates `110020`, `017641`, or `017970` remains `unknown_upstream_failure_category`" 触发 stop before durable baseline selection。

额外约束（L138）："The fallback candidates must not rely on an implicit assumption that fallback was compliant. Their `unknown_upstream_failure_category` must be restored to `not_found` or `unavailable`, or the candidate must be excluded. If the category restores to `schema_drift`, `identity_mismatch`, or `integrity_error`, fail closed."——与 `AGENTS.md` 年报来源 fallback 策略完全一致。

### L6. FOF/QDII-FOF 是否继续作为 data_gap/taxonomy issue，不冒充 pure fof_fund

**PASS.**

- `007721`："Annual report may be verified, but current classifier and reviewed golden rows say `qdii_fund`; record as FOF `data_gap`, not scoring-ready FOF."（L135）
- `017970`："current classifier says `qdii_fund`; also fallback has `unknown_upstream_failure_category`; exclude from durable FOF baseline unless both taxonomy and source category are resolved."（L136）
- Stop condition #3："FOF coverage still has no repository-verified pure `fof_fund`, and no accepted fund-type taxonomy / QDII-FOF precedence gate exists"（L205）
- `document_identity_status = verified_as_annual_report_but_type_gap` 明确声明 "must not be interpreted as scoring-ready FOF"（L79）

FOF 作为 `data_gap` 的处置与 S0 controller judgment 完全一致。

### L7. dry-run plan 是否只放 ignored reports/scoring-runs，未提升 fixture，示例是否没有声称完整评分器已运行

**PASS.**

- Dry-run plan 表格（L144-151）四个步骤中，步骤 1-2 标记 "Tracked? No"，步骤 3-4 标记 "Tracked? Yes"（仅 review artifact 和 controller judgment）
- 明确声明："Ignored run outputs under `reports/scoring-runs/` must remain scratch. Tracked artifacts retain only schema, plan, and artificial/manual review evidence. No fixture is promoted until a later curated-fixture gate accepts exact JSON fixture shape and review criteria."（L151）
- 示例声明："This is an illustrative S1 record using S0 corpus evidence and existing reviewed rows. It does not claim a full scorer has run."（L155）
- `ignored_run_path` 字段指向 `reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl`，符合 ignored scratch 语义

### L8. 是否违反非目标：renderer、FQ0-FQ6、Host/Agent、dayu.host/dayu.engine、S2 code implementation

**PASS.** 边界声明明确（L6, L12-13）：

- "no source code, tests, renderer, FQ0-FQ6, Host/Agent package, `dayu.host`, `dayu.engine`, PR, push, or commit work"
- "It does not promote ignored run outputs into tracked fixtures, does not change current v0 8-chapter renderer, does not change FQ0-FQ6, does not enter S2 code implementation"
- Next Step Recommendation 明确："It is not S2 code implementation."（L213）

全文无 renderer 改动、FQ0-FQ6 变更、Host/Agent 包创建、dayu 引用或 S2 代码实现声明。

---

## Findings

### F-1 [minor] review_state terminal states 缺少转换语义

**Location**: Score Record Schema Draft, `review_state` field (L50)

**Problem**: Schema 定义了 `rejected`, `deferred`, `expired` 三个 terminal states，并注明 "Terminal states are allowed in schema but do not imply S0 used them"。但 S0 controller judgment finding MiMo F-3 已将 terminal/rollback states deferred 到 S1/S2 state model extension，S1 应为这些 terminal states 提供最低限度的转换语义（从哪些前置状态可进入、是否可逆、对分母的影响），而非仅声明允许存在。

**Expected**: 至少说明 `rejected` 从 `candidate` / `repository_verified` / `fact_prefill_reviewed` 进入；`deferred` 从任意非 terminal 状态进入；`expired` 基于时间条件；terminal 状态的记录是否纳入 applicable denominator。

**Severity**: minor — 不阻塞 S1 schema draft 接受，但应在 S1 review/controller judgment 或 S2 中补全。

### F-2 [minor] severity 字段在 issue 结构模板中标记为必填，但在 schema 主表中标记为 optional

**Location**: Issue structure template (L112-124) vs Optional fields (L60)

**Problem**: Issue 结构模板（text block）列出了 `severity: blocking | material | minor` 作为 issue 对象的一部分，但 schema 主表中 `severity` 被列为 optional field ("Optional fields may include ... `severity` ...")。如果 issue 内的 severity 是结构化输出的一部分，应明确其在 issue 对象中的 required/optional 状态。

**Expected**: 在 schema 主表或 issue 结构描述中明确 `severity` 在 issue 对象内是否必填。

**Severity**: minor — 不阻塞，但应消除歧义。

### F-3 [minor] validation section 仅使用 `rg` 验证字段存在性，未验证值域约束

**Location**: Validation section (L228-242)

**Problem**: Validation 使用 `rg -n` 验证字段名和关键词在文档中存在，但未验证值域约束（如 `chapter_id` 只允许 `chapter_0` 到 `chapter_7` 或 `report_level`，`document_identity_status` 和 `type_slot_membership_status` 的组合合法性等）。作为 S1 draft 文档 gate 这是可接受的，但若后续进入 S2 实现，需要更精确的 schema validation。

**Expected**: 在 Residual Risks 或 Next Step 中注明值域约束验证属于 S2 实现范畴。

**Severity**: minor — 不阻塞 S1 draft 接受。

---

## Open Residuals

| Residual | Source | Owner / next gate |
|---|---|---|
| review_state terminal states 缺少转换语义 | F-1, S0 controller MiMo F-3 deferred | S1 review/controller judgment or S2 state model |
| severity 字段 required/optional 歧义 | F-2 | S1 review or S2 |
| Schema 值域约束验证 | F-3 | S2 implementation |
| FOF corpus coverage 仍未满足 | control-doc Open Residuals | S1 second pass or fund-type taxonomy gate |
| Fallback upstream failure category 未知 | control-doc Open Residuals | S1 entry gate / source reliability evidence |
| Anchor naming and review status derivation | control-doc Open Residuals | S1 / S2 |
| `fq_gate_status` citation | control-doc Open Residuals | S1 / S2 |

---

## Required Fixes Before Controller Acceptance

无 blocking findings。三个 minor findings 均不阻塞 S1 schema draft 进入 controller judgment。

建议 controller 在 judgment 中：
1. 明确 F-1 的处置（接受为 minor residual 并指定 owner，或要求 S1 patch 补全 terminal state 语义）
2. 明确 F-2 的处置（接受歧义或要求消除）
3. 确认 S1 是否需要在 Residual Risks 中增加 F-3 的值域验证说明

---

## Verdict

**PASS_WITH_FINDINGS**

S1 score-schema fixture draft 满足 control-doc Next Entry Point 的全部 7 项要求：七个评分维度完整覆盖、document_identity_status 与 type_slot_membership_status 明确拆分、source_boundary 值域清晰且 unknown/probe_only 被禁止进入 durable baseline、issue-based 输出且无 weighted total、S0 fallback candidates 的 unknown_upstream_failure_category 正确处理并设置 stop 条件、FOF/QDII-FOF 继续作为 data_gap 不冒充 pure fof_fund、dry-run plan 只放 ignored outputs 未提升 fixture、未违反非目标边界。

三个 minor findings 不阻塞接受，建议 controller judgment 统一处置。**建议进入 controller judgment。**

---

## Validation

Review 验证：

```text
# 确认 review target 存在且可读
ls -la docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 seven dimensions 覆盖
rg -n "fact_coverage|extraction_correctness|evidence_traceability|chapter_contract_completeness|final_judgment_consistency|investment_advice_boundary|readability_actionability" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 document_identity_status 与 type_slot_membership_status 拆分
rg -n "document_identity_status|type_slot_membership_status" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 source_boundary unknown/probe_only 禁止
rg -n "unknown|probe_only|Not eligible|not eligible" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 no weighted total
rg -n "weighted total|does not output weighted" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 fallback candidates stop conditions
rg -n "110020|017641|017970|unknown_upstream_failure_category|stop.*before.*durable" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 FOF data_gap
rg -n "007721|017970|data_gap|not scoring-ready FOF|pure.*fof_fund" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 dry-run ignored, no fixture promotion
rg -n "ignored|scratch|not tracked|must remain|No fixture" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# 确认 non-goal boundaries
rg -n "renderer|FQ0-FQ6|Host/Agent|dayu.host|dayu.engine|S2 code implementation|not.*S2" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
```

All validations passed.
