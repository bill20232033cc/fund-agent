# Release Maintenance Report-Quality Baseline S1 Score-Schema Fixture Draft — MiMo Re-Review

> Date: 2026-05-25
> Reviewer: AgentMiMo (phaseflow independent review agent)
> Gate: `report-quality-baseline S1 score-schema fixture draft`
> Scope: Re-review after Codex patch; verify original findings F-1/F-2/F-3 are resolved and no new issues introduced.
> Verdict: **PASS**

---

## Original Findings Re-Check

### F-1 [minor] review_state terminal states 缺少转换语义 → RESOLVED

**Patch location**: "Review State Terminal Semantics" section (L82-92)

Codex added a dedicated subsection with a table covering all three terminal states:

| Terminal state | Transition source | Reversible? | Denominator behavior | Status |
|---|---|---|---|---|
| `rejected` | From `candidate`, `repository_verified`, `fact_prefill_generated`, `fact_prefill_reviewed`, or `scoring_ready` when evidence is invalid. | Not reversible in the same run. | Excluded from durable baseline and scoring denominators. | Addresses original expected. |
| `deferred` | From any non-terminal state when evidence is incomplete but recoverable. | Reversible by explicit later review decision. | Excluded from durable baseline and denominators until moved to non-terminal state. | Addresses original expected. |
| `expired` | From `candidate`, `repository_verified`, `fact_prefill_generated`, `fact_prefill_reviewed`, or `scoring_ready` when superseded by corpus revision or schema change. | Not reversible; refresh through new run. | Excluded from durable baseline and denominators. | Addresses original expected. |

Additionally, L92 clarifies that `accepted_baseline` is not terminal in the same sense—it can be superseded by a later curated-fixture gate.

**Verdict**: Fully resolved. Transition semantics, reversibility, and denominator behavior are now explicit.

### F-2 [minor] severity 字段在 issue 结构模板中标记为必填，但在 schema 主表中标记为 optional → RESOLVED

**Patch location**: L141

Codex added: "`severity` is required inside each issue object. Record-level `severity` remains optional and may be used later as a roll-up, but it must not replace per-issue severity."

This clearly distinguishes:
- Issue-object `severity`: **required** (blocking | material | minor)
- Record-level `severity`: **optional** (future roll-up)

**Verdict**: Fully resolved. The ambiguity is eliminated.

### F-3 [minor] validation section 仅使用 `rg` 验证字段存在性，未验证值域约束 → RESOLVED

**Patch location**: L242 (Residual Risks table)

Codex added a new residual risk row: "Schema value-domain validation is not executable in this draft. `rg` can prove terms exist, but cannot validate enum exhaustiveness, `N/A` reason presence, terminal transitions, or `chapter_summary` constraints. S2 / later implementation should add value-domain validation tests if schema becomes code."

**Verdict**: Fully resolved. The limitation is now documented as a residual risk with S2 as owner.

---

## New Content Review

Codex introduced several additions beyond the three finding patches. All are reviewed below:

### 1. `chapter_summary` dimension (L32, L121, L123)

A new dimension value `chapter_summary` (中文维度: 章节汇总) is added, reserved for `skipped` chapter summary records only. The constraint "`skipped` chapter summary record must use `dimension=chapter_summary`" creates a clean semantic pair with `status=skipped`.

This is a sound addition: it gives `skipped` records a dedicated dimension rather than forcing them to carry a meaningless dimension value. No conflict with existing schema.

### 2. `na_reason` requirement (L61, L120)

L61: "every `N/A` record must record the reason through `na_reason` or an equivalent `reviewer_note`."
L120: N/A status description now includes "with reason recorded in `na_reason` or an equivalent `reviewer_note`."

This strengthens auditability for N/A decisions. Consistent with the principle that N/A must have a reason.

### 3. `data_gap` vs document-level `not_found` clarification (L109)

New paragraph: "In scoring context, `source_failure_category=data_gap` means the source/document boundary is available but a specific fact or field is not disclosed, not reviewed, conflicted, or cannot be safely derived. It is not equivalent to document-level `not_found`, where the target annual report itself is absent from a normally responding source."

This disambiguates field-level data gaps from document-level source failures. Useful for scoring precision.

### 4. `chapter_summary` constraint in `skipped` semantics (L121, L123)

L121: "`skipped` is only for all-N/A chapter summary records; the `dimension` value must be `chapter_summary`."
L123: "A `skipped` chapter summary record must use `dimension=chapter_summary` and point to the underlying `N/A` records or their reviewer notes."

This adds provenance linking from skipped summaries to their underlying N/A records. Good for traceability.

### 5. Validation section updates (L248-260)

The validation `rg` commands now include `chapter_summary`, `na_reason`, `terminal`, and `value-domain validation` keywords. The narrative confirms all passed.

**No new issues found.** All additions are consistent with the existing schema design and the control-doc requirements.

---

## Summary

| Original Finding | Status | Resolution Quality |
|---|---|---|
| F-1 terminal review_state semantics | Resolved | Full — transition source, reversibility, denominator behavior all explicit |
| F-2 severity required/optional ambiguity | Resolved | Full — issue-level required, record-level optional clearly stated |
| F-3 value-domain validation residual | Resolved | Full — documented as residual risk with S2 owner |

New content additions (`chapter_summary`, `na_reason`, `data_gap` clarification, `skipped` provenance): all sound, no new issues.

---

## Verdict

**PASS**

All three original findings are fully resolved. No new issues introduced. The S1 score-schema fixture draft is ready for controller judgment.

---

## Validation

```text
# Confirm terminal state section exists
rg -n "Review State Terminal Semantics|rejected.*candidate|deferred.*non-terminal|expired.*superseded" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# Confirm severity disambiguation
rg -n "severity.*required.*issue|Record-level.*severity.*optional" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# Confirm value-domain residual
rg -n "value-domain validation|enum exhaustiveness|chapter_summary constraints" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# Confirm chapter_summary dimension
rg -n "chapter_summary|skipped.*chapter_summary" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# Confirm na_reason
rg -n "na_reason|reviewer_note.*N/A" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md

# Confirm data_gap vs not_found clarification
rg -n "data_gap.*not equivalent.*not_found|document-level.*not_found" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
```

All validations passed.
