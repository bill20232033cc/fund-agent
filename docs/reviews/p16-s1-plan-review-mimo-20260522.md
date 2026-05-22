# P16-S1 Enhanced-index Production Golden Candidate Evidence Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan artifact `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` is accepted with 4 non-blocking findings.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | Plan under review |
| `AGENTS.md` | Agent execution rules |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/post-p15-follow-up-plan-review-controller-judgment-20260522.md` | Controller judgment with P16-S1 entry constraints |
| `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md` | Accepted P15 negative evidence result |

Excluded inputs: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md` — not read, not cited.

## Review Checklist

### R1. First-principles correctness — plan answers the right question

**PASS.** The plan's stated question (lines 12-15) is:

> 未来 evidence-acquisition implementation 是否可以在 selected-fund enhanced-index 候选中，按当前 P13/P14 index_profile / tracking_error 抽取与 comparable 路径，找到可复核的 production golden 候选证据？

This is exactly the question the post-P15 controller judgment assigned (constraint 1-9). The plan does not attempt to answer whether golden rows are ready, whether extractor behavior is correct, or whether calculated tracking error is viable. It stays within the plan-review scope: defining candidate identity, evidence contracts, source handling, and future handoff boundaries.

### R2. Candidate list and CSV row grounding

**PASS.** All 5 candidates verified against `docs/code_20260519.csv`:

| Plan eval order | Fund code | CSV line | CSV name match |
|---:|---|---:|---|
| 1 | `004194` | 38 | 招商中证1000指数增强A |
| 2 | `005313` | 39 | 万家中证1000指数增强A |
| 3 | `017644` | 40 | 博道中证1000指数增强A |
| 4 | `019918` | 41 | 招商中证2000指数增强A |
| 5 | `019923` | 42 | 华泰柏瑞中证2000指数增强A |

All 5 are in the selected CSV. `161725` is correctly absent (fixture-only, line 28). `001548` is correctly excluded from this candidate set (blocked by P15-S1A). The per-candidate identity record (lines 112-127) requires `selected_source_row` with exact CSV row path and line number, grounding each candidate to a specific auditable source location.

### R3. Candidate ordering rationale

**PASS with finding (F1).** The ordering principle is stated as CSV stable row order (lines 89-95). This is auditable and deterministic, which satisfies the post-P15 controller judgment constraint to "define an explicit candidate evaluation order and the ordering principle." However, the controller judgment also suggested the default should "prefer shortest evidence loop and highest production value" — the plan's rationale does not explicitly address production value or evidence-loop length. See F1.

### R4. Stop budget

**PASS.** The stop budget table (lines 99-108) covers:

- **Candidate budget**: exactly 5, no additions — correct.
- **Report budget**: exactly one identity per candidate (2024 annual report) — correct, matches the fixed scope declared in the candidate identity section.
- **Access budget**: only `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()` — correct, matches design truth §6.1.
- **Source fallback budget**: only repository-owned fallback triggered by `not_found` or `unavailable` — correct, matches the five-category taxonomy.
- **Evidence budget**: classify `index_profile` and `tracking_error` separately — correct, matches P14 conditional P1 field design.
- **Stop success**: all 5 classified (accepted or blocked) — correct, prevents early termination.
- **Stop blocked**: produce `BLOCKED_NO_ACCEPTED_SELECTED_ENHANCED_INDEX_EVIDENCE` — correct, fail-closed.
- **Stop fail-closed**: schema_drift, identity_mismatch, integrity_error, incomplete anchor, or contract/integrity breach blocks candidate — correct, matches AGENTS.md §年报来源 fallback 策略.

### R5. FundDocumentRepository / FundDataExtractor boundaries

**PASS.** The annual-report access contract (lines 130-142) explicitly lists allowed and forbidden access paths. Forbidden paths include direct filesystem reads, direct concrete source adapter calls, service/UI/Engine/renderer/quality gate source orchestration, and manual web search. This is fully consistent with design truth §6.1 and AGENTS.md §硬约束.

### R6. Source failure taxonomy and fail-closed handling

**PASS.** The source blocker handling table (lines 146-155) uses the exact five-category taxonomy from design truth §6.1: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. Fallback eligibility rules are correct (`not_found`/`unavailable` may fallback; `schema_drift`/`identity_mismatch`/`integrity_error` fail closed). The requirement to preserve `metadata.fallback_used=True` and provenance on fallback-blocked matches design truth exactly.

### R7. index_profile benchmark-context subfield contract

**PASS.** The contract (lines 158-184) enumerates three acceptable subfields: `index_profile.index_name`, `index_profile.benchmark_context`, and `index_profile.source_tier` / provenance marker. Each has:

- Acceptable evidence definition
- Required anchor/provenance
- Explicit "not accepted" exclusions

The out-of-scope list (lines 176-181) explicitly excludes index methodology, constituent list/weights, provider details, rebalance frequency, index code, external adapter output, and calculated/inferred classification. This directly addresses the post-P15 MiMo F2 and GLM F3 findings that required P16-S1 to "enumerate which index_profile subfields can accept benchmark-context evidence under current extractor semantics."

### R8. tracking_error direct observed disclosure contract

**PASS.** The contract (lines 187-219) requires all 8 fields from the post-P15 controller judgment: `observed_value`, `period_label`, `annualization_support`, `source_type="direct_disclosure"`, `calculation_method="disclosed"`, `value_parse_status`, `anchor`, and `provenance`. The fail-closed list (lines 204-215) covers target/limit text, manager narrative, benchmark-only, standard-deviation-only, ambiguous/unparseable values, incomplete anchors, schema_drift, identity_mismatch, integrity_error, and any calculated/inferred value. This is fully consistent with P15-S1A's accepted negative result.

### R9. Evidence classification matrix

**PASS.** The matrix (lines 222-236) has 10 classifications covering:

- Accepted evidence (2): `accepted_index_profile_candidate`, `accepted_tracking_error_candidate`
- Blocked evidence (6): covering all failure modes
- Deferred (1): `defer_extractor_false_negative` — correctly routes to separate extractor refinement slice
- Each classification has clear golden implications

The `defer_extractor_false_negative` classification (line 236) is consistent with the post-P15 controller judgment and GLM F4 positive confirmation.

### R10. No-golden sequencing

**PASS.** The plan maintains clear sequencing:

- P16-S1 is plan-review only (line 7-8)
- Future evidence acquisition produces an artifact, not golden edits (lines 240-259)
- Future golden implementation opens only after reviewed evidence acceptance (lines 262-274)
- `001548` production tracking_error remains blocked unless new reviewed direct evidence is accepted (line 272)
- `161725` remains fixture-only (line 274)

### R11. Residual owners

**PASS.** The residuals table (lines 332-342) has 9 items, all correctly tracked:

| Residual | Status | Verified |
|---|---|---|
| `001548` production `tracking_error` | blocked by P15-S1A | ✓ |
| `161725` enhanced-index tracking-error | fixture only | ✓ |
| Enhanced-index production golden | P16-S1 future evidence acquisition | ✓ |
| Source metadata retry for `001548` | deferred | ✓ |
| Extractor early-return scope | deferred | ✓ |
| Index methodology / constituents | out of scope | ✓ |
| Calculated tracking error / external adapters | out of scope | ✓ |
| E1-E3 / Evidence Confirm | out of scope | ✓ |
| RR-13 duplicate `016492` | untouched | ✓ |

No residual is missing. No residual is mis-owned.

### R12. Validation signals

**PASS.** Three validation stages are defined:

1. **This plan gate** (lines 289-292): only plan artifact created, no source changes, `git diff --check HEAD` passes.
2. **Future evidence acquisition** (lines 295-304): identity records, separate field conclusions, benchmark-context anchors, direct-disclosure requirements, source blockers, no golden edits.
3. **Future golden gate** (lines 306-311): opens only after reviewed acceptance, targeted tests, full suite.

### R13. Over-coupling or scope creep

**PASS.** The scope (lines 53-72) is tightly bounded. Out-of-scope items include: no source/test/golden/README/design/control/CSV/RR-13 edits, no implementation evidence, no production golden edits, no calculated tracking error, no external index adapters, no methodology/constituents extraction, no QDII redesign, no E1-E3, no LLM writing, no Dayu runtime. File ownership (lines 277-285) correctly separates plan-review, evidence acquisition, extractor refinement, and golden implementation into distinct stages.

### R14. Reviewer rejection criteria

**PASS.** The rejection criteria (lines 314-328) cover all the post-P15 controller judgment constraints and both reviewer findings:

- `161725` misused as production evidence
- `001548` tracking_error unblocked without new evidence
- Candidate skipping without source blocker
- Candidate order change without first-principles reason
- Golden edits during plan-review or evidence acquisition
- Indirect tracking_error evidence accepted
- index_profile fields outside benchmark-context
- Repository/extractor bypass
- Fallback after fail-closed failures
- Out-of-scope features introduced

## Findings

### F1 — LOW: Candidate ordering rationale does not address production value or evidence-loop length

**Location:** `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` lines 89-95

**Issue:** The post-P15 controller judgment stated that P16-S1 should "define an explicit candidate evaluation order and the ordering principle. The default should prefer shortest evidence loop and highest production value while still covering all five candidates unless a source blocker is recorded." The plan's ordering rationale (CSV stable row order, group by index family, no management-entity jumping) is auditable and deterministic, but it does not explicitly discuss production value or evidence-loop length as ordering factors.

**Impact:** Low. The plan's ordering is defensible on first-principles grounds (auditability, determinism, reduced evidence-form variables). The stop-success condition requires all 5 candidates to be classified regardless of order, so the ordering only affects implementation efficiency, not correctness. If the first candidate has good evidence, the implementation agent still must complete all 5.

**Recommendation:** No revision required. The ordering rationale is sound and meets the core requirement (explicit, deterministic, auditable). The production-value preference from the controller judgment was a default suggestion, not a hard constraint. Accept as-is.

### F2 — INFO: CSV "category" reference is slightly imprecise

**Location:** `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` line 127

**Issue:** Line 127 states "CSV name and category are candidate-selection facts only." However, `docs/code_20260519.csv` column 3 is labeled "国内股票类" / "国内债券类" etc. — this is the fund category in the CSV, not a structured fund type. The plan's intent is correct (CSV metadata alone is not enough to accept fund type), but the word "category" could be confused with the `FundType` classification system (`index_fund` / `enhanced_index` / etc.).

**Impact:** None on plan correctness. The per-candidate record requirement `classified_fund_type` (line 122) and `fund_type_source` (line 123) correctly require structured extraction or annual-report identity as the fund type source, not CSV name alone.

**Recommendation:** No revision required. The intent is clear from context. Accept as-is.

### F3 — INFO: Per-candidate record `source_blocker` optionality is implicit

**Location:** `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` lines 112-127

**Issue:** The required per-candidate record table lists `source_blocker` as a required field (line 125), but the description says "One of the taxonomy categories if annual-report access or identity fails." This implies `source_blocker` is conditional (only populated on failure), not always required. The table format lists it as required without clarifying the condition.

**Impact:** None on implementation correctness. An implementation agent would reasonably interpret this as: populate `source_blocker` if access fails; leave it empty/null if access succeeds. The evidence classification matrix (lines 222-236) provides the mapping from blocker categories to classification outcomes.

**Recommendation:** No revision required. Accept as-is.

### F4 — INFO: Future evidence-acquisition artifact path suggestion is well-defined

**Location:** `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` lines 240-244

**Issue (positive):** The plan suggests a concrete artifact path for the future evidence-acquisition implementation: `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`. This is good practice — it gives the implementation agent a clear output target and allows the review gate to check artifact existence.

**Impact:** Positive. Reduces ambiguity in the handoff from plan-review to evidence acquisition.

## Summary

The plan artifact correctly:

1. Answers the narrow question assigned by the post-P15 controller judgment: can selected-fund enhanced-index candidates have reviewed production evidence through the current P13/P14 path?
2. Grounds all 5 candidates to specific CSV rows with auditable line references.
3. Defines explicit, deterministic candidate ordering based on CSV stable row order and index-family grouping.
4. Sets a bounded stop budget covering candidates, reports, access, source fallback, evidence, and stop conditions.
5. Preserves FundDocumentRepository / FundDataExtractor boundaries with explicit allowed/forbidden access paths.
6. Uses the accepted five-category source failure taxonomy with correct fallback eligibility rules.
7. Enumerates `index_profile` benchmark-context subfields (3 acceptable, 7+ out-of-scope) with anchor/provenance requirements.
8. Requires direct observed disclosure for `tracking_error` with all 8 required fields and comprehensive fail-closed conditions.
9. Maintains no-golden sequencing: plan-review → evidence acquisition → reviewed acceptance → separate golden gate.
10. Tracks all residuals with correct owners and status.
11. Defines validation signals for all three stages (plan gate, evidence acquisition, golden gate).
12. Provides reviewer rejection criteria covering all controller and reviewer constraints.

Four non-blocking findings are informational. No revision is required before acceptance.

## Verdict

`PASS_WITH_FINDINGS`

All findings are non-blocking. The plan is ready for controller judgment.
