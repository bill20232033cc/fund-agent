# AgentDS Phaseflow Review — S1 Score-Schema Fixture Draft

> Date: 2026-05-25
> Reviewer: AgentDS (phaseflow independent review agent)
> Review target: `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md`
> Gate: `report-quality-baseline S1 score-schema fixture draft`
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4/§5.4.1/§5.4.2/§5.4.3/§6.1/§6.5, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, S0 controller judgment

## Scope of Review

This review checks the S1 draft against the eight review lens items defined by the controller. No files were modified, committed, pushed, or PR'd.

## Lens-by-Lens Assessment

### Lens 1: Seven Report-Quality Dimensions Coverage

| Dimension in target | `docs/design.md` §5.4.1 source | Match |
|---|---|---|
| `fact_coverage` | 事实覆盖度 | Yes |
| `extraction_correctness` | 抽取正确性 | Yes |
| `evidence_traceability` | 证据可追溯性 | Yes |
| `chapter_contract_completeness` | 章节契约完整性 | Yes |
| `final_judgment_consistency` | 最终判断一致性 | Yes |
| `investment_advice_boundary` | 投资建议边界 | Yes |
| `readability_actionability` | 可读性与行动性 | Yes |

**Result: PASS.** All seven canonical dimensions from §5.4.1 are present with semantic identity (not just name matching). Each dimension has a clear "what it checks" and "primary next-gate bias" column that aligns with the design doc's "失败时优先修复方向" guidance.

### Lens 2: Schema Field Coverage and document_identity_status / type_slot_membership_status Split

The control doc's Next Entry Point requires "separate fields for document identity verification and fund-type slot membership." The target delivers:

- `document_identity_status`: five distinct values with semantics (`verified_annual_report`, `unverified`, `mismatch`, `source_failed`, `verified_as_annual_report_but_type_gap`)
- `type_slot_membership_status`: five distinct values (`matches_slot`, `type_gap`, `taxonomy_pending`, `unknown`, `not_applicable`)

The split is explicitly justified in the "Document Identity vs Type-Slot Membership" section (lines 62-79), with a specific consequence statement that `verified_as_annual_report_but_type_gap` must not be interpreted as scoring-ready FOF. This directly addresses the control doc residual: "Split document verification from type-slot membership so `verified_as_annual_report_but_type_gap` cannot become scoring-ready FOF evidence."

All 17 mandatory fields required by the control doc expectations are present: `corpus_id`, `fund_code`, `report_year`, `fund_type_slot`, `classified_fund_type`, `document_identity_status`, `type_slot_membership_status`, `source_boundary`, `source_failure_category`, `review_state`, `chapter_id`, `dimension`, `status`, `issues`, `evidence_anchor_refs`, `data_gap_refs`, `ignored_run_path`, `next_gate_recommendation`.

**Result: PASS.** The split is clear, the fields are all present, and the consequence semantics are explicitly stated.

### Lens 3: source_boundary Domain and unknown/probe_only Exclusion

The `source_boundary` domain defines six values, each with durable baseline eligibility:

| Value | Durable baseline eligible |
|---|---|
| `repository_derived` | Yes (after identity, type-slot, manual review) |
| `derived_calculation` | Yes (when input facts/anchors reviewed) |
| `external_official` | Yes (when source identity and date explicit) |
| `manual_review` | Yes (as review evidence; promotion needs later gate) |
| `unknown` | **No** |
| `probe_only` | **No** |

Line 94 explicitly states: "`unknown` and `probe_only` may appear in S1 dry-run records to preserve uncertainty, but they must be excluded before `accepted_baseline`."

Stop condition 7 (line 209) enforces: "Any record uses `source_boundary=unknown` or `source_boundary=probe_only` as if it were durable evidence."

**Result: PASS.** The domain is clear, eligibility is binary and checkable, and both stop conditions and dry-run semantics are correctly specified.

### Lens 4: Issue-Based Output, N/A Denominator Exclusion, All-N/A Skipped, No Weighted Total

The target is explicit:

- Line 98: "S1 does not output weighted total. The mandatory output is localized `issues` and `next_gate_recommendation`."
- N/A status: "Excluded from denominator" (line 105)
- skipped status: "Not passing; excluded from pass rate and reported as skipped" (line 106)
- All-N/A chapters are `skipped`, not `passing` (line 108)
- Blocked chapters maintain their status — "A chapter with unresolved identity, type-slot, source-category, or fact-review prerequisites is `blocked`, not `N/A`" (line 108)

The issues structure (lines 112-124) provides issue_id, severity, field_path, claim_id, contract_item_id, problem, expected, observed_ref, evidence_anchor_refs, data_gap_refs, and next_gate_recommendation.

**Result: PASS.** No weighted total semantics are present. Denominator rules are explicit. All-N/A chapter handling is `skipped` (not `passing`), preventing silent coverage inflation.

### Lens 5: S0 Fallback Candidates 110020/017641/017970 and Stop Before Durable Baseline

The S0 Corpus Applicability Rules table (lines 130-138) handles each candidate:

| Candidate | Handling |
|---|---|
| `110020` index | Used fallback with `unknown_upstream_failure_category`; recover original category or exclude |
| `017641` QDII | Used fallback with `unknown_upstream_failure_category`; recover original category or exclude |
| `017970` QDII-FOF | Fallback has `unknown_upstream_failure_category`; exclude from durable FOF baseline unless both taxonomy and source category resolved |

Lines 138 explicitly state the recovery requirement: category must be restored to `not_found` or `unavailable`, or the candidate excluded. If restored to `schema_drift`, `identity_mismatch`, or `integrity_error`, fail closed.

Stop conditions 1-2 (lines 203-204) directly enforce:
1. Stop if `source_failure_category` for any of the three remains `unknown_upstream_failure_category`
2. Stop if a fallback category restores to `schema_drift`, `identity_mismatch`, or `integrity_error`

This aligns with `AGENTS.md` fallback rules: `schema_drift`, `identity_mismatch`, `integrity_error` must fail-closed.

**Result: PASS.** The three fallback candidates each have explicit handling, the recovery semantics are specified, and stop conditions are present.

### Lens 6: FOF/QDII-FOF as data_gap/taxonomy Issue, Not Pure fof_fund

The target maintains the S0 decision that `007721` and `017970` are QDII-FOF, not pure FOF:

- Line 79: "`verified_as_annual_report_but_type_gap` must not be interpreted as scoring-ready FOF."
- Lines 135-136: `007721` → "record as FOF `data_gap`, not scoring-ready FOF." `017970` → "exclude from durable FOF baseline unless both taxonomy and source category are resolved."
- Stop condition 3 (line 205): "FOF coverage still has no repository-verified pure `fof_fund`, and no accepted fund-type taxonomy / QDII-FOF precedence gate exists."

**Result: PASS.** FOF remains correctly gated as a data gap. No QDII-FOF candidate is presented as fulfilling the `fof_fund` slot.

### Lens 7: Dry-Run Plan — Ignored Outputs, No Fixture Promotion, No Full Scorer Claim

The Reviewed Dry-Run Fixture Plan table (lines 144-149) explicitly marks manifest.json and score-records.jsonl as "No" for tracked. Only review artifacts and controller judgment are tracked.

Line 151: "Ignored run outputs under `reports/scoring-runs/` must remain scratch. Tracked artifacts retain only schema, plan, and artificial/manual review evidence. No fixture is promoted until a later curated-fixture gate."

The example JSON (line 155) states: "This is an illustrative S1 record using S0 corpus evidence and existing reviewed rows. It does not claim a full scorer has run."

The issue localization example (line 197): "It is not a full report-quality score and it is not an accepted baseline."

**Result: PASS.** The dry-run plan correctly keeps all run outputs in ignored `reports/scoring-runs/`. No fixture promotion. Examples include explicit disclaimers that a full scorer has not run.

### Lens 8: Non-Goal Violations

The Step Self-Check (lines 12-13) declares the boundary:
- does not change current v0 8-chapter renderer
- does not change FQ0-FQ6
- does not enter S2 code implementation
- does not create Host/Agent runtime work

The Next Step Recommendation (line 213): "It is not S2 code implementation."

I verified that no section of the document:
- Proposes renderer changes
- Modifies FQ0-FQ6 rules
- Describes Host/Agent package work
- References `dayu.host` or `dayu.engine` (except in the validation `rg` command showing they are non-goals)
- Describes S2 code implementation details

**Result: PASS.** No non-goal violation detected. The boundary is explicitly declared and respected throughout.

## Findings

### Finding 1 — Severity: Minor — N/A Reason Not a Dedicated Field

**Location:** Lines 33, 55, 104-105

**Problem:** Line 33 states "A dimension may be `N/A` for a chapter/fund-type pair only with a reason." However, the mandatory schema fields do not include a dedicated `na_reason` field. The `issues` list must be empty for `N/A` records (line 55), and the optional fields list includes `reviewer_note` but does not explicitly designate it as the carrier for N/A reasons.

**Risk:** Without a clear convention, N/A reasons may be inconsistently recorded or omitted, weakening downstream auditability of denominator exclusions.

**Recommendation:** Either add an optional-but-recommended `na_reason` field to the mandatory schema, or explicitly state that `reviewer_note` (or an optional `na_reason`) must carry the reason for every `N/A` record.

### Finding 2 — Severity: Minor — Dimension Value for skipped Chapter Summary Records

**Location:** Lines 52, 106

**Problem:** `dimension` is a required field (line 52), but the `skipped` status is defined as "Chapter summary only: every dimension for the chapter is `N/A`" (line 106). The schema does not specify what value `dimension` should take for a chapter-level `skipped` summary record. Should it repeat one of the seven dimensions, use a sentinel like `chapter_summary`, or be absent?

**Risk:** Ambiguity could lead to inconsistent record shapes for skipped chapters, complicating downstream consumers that aggregate by dimension.

**Recommendation:** Define a convention for `dimension` in `skipped` records, e.g., set `dimension` to `chapter_summary` or allow it to be `null`/absent specifically for `skipped` records.

### Finding 3 — Severity: Info — source_failure_category Includes data_gap

**Location:** Line 49

**Problem:** `source_failure_category` includes `data_gap` alongside source-level failure categories (`not_found`, `unavailable`, `schema_drift`, etc.). A `data_gap` can exist even when the source is working correctly (e.g., the annual report is valid but a specific field is not disclosed). This differs from `not_found` (source-level: document not available) and `not_applicable` (dimension-level: dimension doesn't apply).

**Risk:** Low. The distinction between source-level failure and field-level gap is implicit but defensible as a natural extension of the AGENTS.md taxonomy for the scoring context.

**Recommendation:** No change required for S1 draft acceptance. Consider adding a clarifying sentence that `data_gap` in this context means "source is available but specific fact/field is not disclosed or cannot be derived," distinct from `not_found` which means "source document itself could not be acquired."

### Finding 4 — Severity: Info — Example ignored_run_path Self-References Output File

**Location:** Line 178

**Problem:** The example JSON record has `ignored_run_path` set to `reports/scoring-runs/s1-dry-run-20260525/score-records.jsonl`, which is the same path as the file that would contain this record. This is a minor self-reference that doesn't affect schema correctness but could confuse readers about whether each record carries the output path or the input path.

**Risk:** None for schema correctness. Cosmetic issue in the example.

**Recommendation:** Either clarify that `ignored_run_path` is the output file path (making the self-reference intentional and meaningful), or change the example to use a distinct input path.

## Open Residuals

| Residual | Status |
|---|---|
| FOF corpus coverage | Carried forward; target correctly gates on pure `fof_fund` or taxonomy gate. |
| Fallback upstream failure category recovery | Carried forward; target adds explicit stop conditions before durable baseline selection. |
| Review-state terminal states (`rejected`, `deferred`, `expired`) | Allowed in schema but declared unused by S0 (line 50). Consistent with control doc residual. |
| `fq_gate_status` citation | Not addressed in S1 draft. This is an S2 concern per the control doc residual owner (`S1 / S2`). Deferred. |
| Anchor naming normalization | Not addressed. This is an S1/S2 residual per control doc. Deferred. |

## Required Fixes Before Controller Acceptance

None. All findings are minor or informational and do not block controller acceptance. The schema correctly addresses all eight review lenses.

## Verdict

**PASS_WITH_FINDINGS**

The S1 score-schema fixture draft correctly:
- Covers all seven report-quality dimensions from `docs/design.md` §5.4.1
- Splits `document_identity_status` from `type_slot_membership_status` with clear consequence semantics
- Defines `source_boundary` with explicit durable baseline eligibility and prohibits `unknown`/`probe_only`
- Implements issue-based output with `N/A` denominator exclusion, all-`N/A` skipped, and no weighted total
- Handles fallback candidates 110020/017641/017970 with `unknown_upstream_failure_category` recovery requirements and stop-before-durable-baseline conditions
- Maintains FOF/QDII-FOF as `data_gap`/taxonomy issue without claiming pure `fof_fund` coverage
- Keeps dry-run outputs in ignored `reports/scoring-runs/` with no fixture promotion and no false claim of a complete scorer
- Respects all non-goals: no renderer changes, no FQ0-FQ6 modifications, no Host/Agent work, no `dayu.host`/`dayu.engine` references, no S2 implementation

The four findings (two minor, two informational) are schema clarifications that can be addressed in the S1 controller judgment or deferred to S2 schema refinement without blocking acceptance.

## Recommendation

**Yes — proceed to controller judgment.** The S1 draft is of sufficient quality for the controller to decide whether to accept the schema and authorize the dry-run evidence collection or move to the next gate.
