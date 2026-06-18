# MVP typed template contract Slice 0 calibration/precondition evidence review — MiMo

## Reviewer Self-Check

- Role: AgentMiMo independent reviewer only. Do not implement, do not edit source/tests/control/design/template truth, do not commit/push/PR.
- Gate: `MVP typed template contract Slice 0 calibration/precondition gate`.
- Classification: `heavy`.
- Review target: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md`, and scoped code files for evidence verification.
- Actions intentionally not taken: no source code edit, no tests edit, no template truth edit, no provider/runtime/default/golden/readiness/score-loop edit, no live provider run, no commit, no push, no PR.

## Conclusion

**PASS** with residual risks only. No blocking findings.

## Hard Preconditions Verification

All eight hard preconditions from the accepted typed-template planning controller judgment are addressed:

### Precondition 1: Output form definition

Artifact section 1 explicitly states Slice 0 output is **reference markdown only**. It does not create a reusable fixture/test-data module because the gate forbids source/test implementation. Future Slice 4 owns programmatic encoding. A suggested future fixture shape is provided but not created. **Satisfied.**

### Precondition 2: Deterministic allowed_contexts matching

Artifact section 3 defines matching rules for `required_label`, `evidence_gap_statement`, `quote`, and `anchor_caption` using deterministic line/block structure and local lexical rules only. Each context has explicit allowed/blocked conditions with no LLM judgment dependency. **Satisfied.**

### Precondition 3: Same-source Ch3 C2 code-path/root-cause evidence

Artifact section 4 correctly identifies the emitting path in `chapter_auditor.py` `_audit_must_not_cover()`, not in `contract_rules.py` `_FORBIDDEN_CONTENT_RULES`. Code verification confirms:

- `chapter_auditor.py:342-353`: `audit_chapter_programmatic()` aggregates `_audit_must_not_cover()` into programmatic issues. **Confirmed.**
- `chapter_auditor.py:557-584`: `_audit_must_not_cover()` iterates `must_not_cover` clauses, extracts phrases, matches globally. **Confirmed.**
- `chapter_auditor.py:741-761`: `_must_not_cover_phrases()` removes prefix, splits, keeps fragments >= 4 chars. **Confirmed.**
- `chapter_auditor.py:798-814`: `_clean_must_not_cover_fragment()` strips stopwords without preserving polarity. **Confirmed.**
- `contracts.py:377`: Ch3 must-not-cover clause about missing turnover/style evidence. **Confirmed.**
- `contracts.py:383-386`: Ch3 required labels `言行一致性判断` and `风格稳定性判断`. **Confirmed.**
- `contract_rules.py:185-195`: `_FORBIDDEN_CONTENT_RULES` covers `性格`, `人品`, `动机` for Ch3, not `言行一致`. **Confirmed.**
- `contract_rules.py:276-281`: Ch3 style clause routed as `narrative_guidance` in `_MUST_NOT_COVER_COVERAGE_RULES`. **Confirmed.**

**Satisfied.**

### Precondition 4: Handle existing `_MUST_NOT_COVER_COVERAGE_RULES` / avoid duplicate enforcement

Artifact section 4 correctly identifies the conflict: `contract_rules.py` declares the Ch3 style clause as `narrative_guidance`, but `chapter_auditor.py` still extracts phrases from `must_not_cover` and matches globally. Section 8 states Slice 4 must migrate the Ch3 clause out of global phrase extraction and into typed `MustNotCoverClause` enforcement, and must avoid duplicate enforcement. **Satisfied.**

### Precondition 5: Preserve active-fund Ch3 renderer degradation

Artifact section 6 documents the existing degradation path with code evidence. Verification confirms:

- `renderer.py:1102`: `_is_active_fund()` checks `classified_fund_type == "active_fund"`. **Confirmed.**
- `renderer.py:1157-1158`: `_chapter_3_consistency_summary_line()` returns explicit `证据不足` / `不能据此判断` line. **Confirmed.**
- `renderer.py:1175-1176`: `_chapter_3_style_stability_line()` does the same. **Confirmed.**
- `renderer.py:1197-1198`: `_chapter_3_consistency_rollup_line()` says no consistency conclusion output. **Confirmed.**
- `renderer.py:1219-1225`: `_chapter_3_dimension_line()` preserves declared/actual but says no consistency conclusion. **Confirmed.**
- `renderer.py:1246-1249`: `_chapter_3_next_minimum_validation_line()` renders minimum follow-up question. **Confirmed.**

**Satisfied.**

### Precondition 6: Explicit reviewed mapping only, no fuzzy matching

Artifact section 7 states Slice 1 adapter must use explicit reviewed mapping with no fuzzy/substring/embedding/LLM matching. Unmapped strings fail closed at load/validation time. Suggested id style is provided for later review. **Satisfied.**

### Precondition 7: Slice 4 duplicate-enforcement and serializer impact preconditions

Artifact section 8 explicitly states:

- Ch3 clause should migrate out of global phrase extraction into typed `MustNotCoverClause`.
- `chapter_auditor.py` must not run both old and new paths for the same clause.
- Exact stable issue id format change requires serializer/retained artifact impact analysis.
- Whether typed clause fully replaces `_audit_must_not_cover()` is an unresolved controller decision.

**Satisfied.**

### Precondition 8: Slice 6 Ch7 bundle decision

Not directly a Slice 0 precondition (it is a Slice 6 precondition). The artifact stays within its scope. The controller judgment precondition #8 is about Slice 6, which is downstream. **Not applicable to Slice 0 review scope.**

## Review Criteria Verification

### Criterion 1: Output form

Section 1 clearly defines reference markdown vs future reusable fixture/test-data ownership. Future Slice 4 owns programmatic encoding. Suggested fixture shape with stable case ids and traceability to section names is provided.

### Criterion 2: Deterministic allowed_contexts matching

Section 3 defines matching rules for all four context types using deterministic lexical rules. No LLM judgment is involved. Rules are narrow and explicit with allowed/blocked examples.

### Criterion 3: Same-source Ch3 C2 code path/root cause

Section 4 correctly distinguishes three paths:

- `chapter_auditor.py` `_audit_must_not_cover()` — the actual emitting path for `programmatic:C2:言行一致`.
- `contract_rules.py` `_FORBIDDEN_CONTENT_RULES` — covers `性格`, `人品`, `动机`, not `言行一致`.
- `contract_rules.py` `_MUST_NOT_COVER_COVERAGE_RULES` — declares Ch3 style clause as `narrative_guidance`.

The root-cause mapping is correct: current path is global substring match with no polarity/allowed-contexts awareness.

### Criterion 4: RequiredOutputItem behavior

Section 5 distinguishes gap vs block vs delete-if-not-applicable with explicit criteria for each. Correctly states `delete_if_not_applicable` must not be used for active-fund Ch3 `言行一致性判断` or `风格稳定性判断`.

### Criterion 5: Preserve explicit reviewed mapping for Slice 1

Section 7 specifies explicit reviewed mapping only, with fail-closed behavior for unmapped items. No fuzzy matching authorized.

### Criterion 6: Slice 4 duplicate-enforcement and serializer impact

Section 8 states preconditions clearly and lists unresolved items for controller/Slice 4 decision.

### Criterion 7: Non-goals

Section 10 correctly lists all non-goals: no implementation, no tests/fixtures, no edits to control/design/template truth/source/tests/provider/runtime/score-loop/golden/readiness. No live probe. No commit/push/PR.

## Taxonomy Verification

The polarity taxonomy in section 2 is well-structured:

- `未见明显不一致` correctly classified as `quasi_positive_assertion` and blocking under missing/unreviewed evidence. This is the critical classification that prevents unsafe hedging.
- `基本一致`, `大体一致`, `较为一致` etc. correctly classified as quasi-positive and blocking.
- `neutral_label` correctly limited to required label context only.
- `gap_statement` correctly requires denial predicate and no positive reversal.
- `unsupported_causal_assertion` correctly identified as blocking when evidence predicate unsatisfied.

## Residual Risks

1. **Polarity taxonomy completeness**: The representative Chinese forms in section 2 are illustrative, not exhaustive. Future Slice 4 implementation must handle edge cases and near-synonyms not listed. The taxonomy should be treated as a seed fixture set, not a closed universe.

2. **Allowed-context boundary cases**: The deterministic matching rules in section 3 are well-specified for common cases, but edge cases around multi-sentence gap statements, nested quotes, or mixed label-then-assertion lines may need additional calibration during Slice 4 implementation.

3. **`_MUST_NOT_COVER_COVERAGE_RULES` validation logic**: `contract_rules.py:674-717` validates that a must-not-cover item cannot be both programmatic forbidden content and non-programmatic coverage. When Slice 4 migrates the Ch3 style clause to typed `MustNotCoverClause`, this validation must be updated to avoid false conflicts with the new typed path.

4. **Retained artifact references**: Section 4 references retained run artifacts for safe diagnostic fields. These references are safe (only issue_id/status fields, no raw prompts/responses), but the artifact paths are instance-specific and may not be available in all review environments.

5. **Future fixture id stability**: The suggested fixture case ids (e.g., `ch3_required_label_allowed_001`) are proposed but not binding. Slice 4 must formalize these ids and ensure they remain stable across future fixture updates.

## Review Checklist

- [x] Does the taxonomy classify `未见明显不一致` as quasi-positive and blocking under missing/unreviewed evidence?
- [x] Are required labels allowed only before the colon and only when the post-colon text is non-assertive?
- [x] Does the artifact avoid using LLM judgment for allowed-context matching?
- [x] Does the root-cause section cite same-source code rather than inferring from retained drafts?
- [x] Does the artifact distinguish `_FORBIDDEN_CONTENT_RULES`, `_MUST_NOT_COVER_COVERAGE_RULES`, and `chapter_auditor.py` runtime phrase extraction?
- [x] Does RequiredOutputItem behavior prevent silent deletion of active-fund Ch3 required labels?
- [x] Does the future Slice 4 note require duplicate-enforcement avoidance and serializer impact analysis before issue-id changes?

## Verifier Matrix Confirmation

| Area | Evidence verified | Result |
|---|---|---|
| Output form | Section 1 | PASS — reference markdown only; Slice 4 owns encoding. |
| Polarity taxonomy | Section 2 | PASS — positive/quasi-positive block under missing/unreviewed; labels/gaps not treated as claims. |
| Allowed contexts | Section 3 | PASS — deterministic and narrow for all four context types. |
| Current C2 path | Section 4 | PASS — `chapter_auditor.py` phrase extraction, not `_FORBIDDEN_CONTENT_RULES`. |
| Coverage conflict | Section 4, 8 | PASS — narrative guidance vs programmatic enforcement conflict identified; Slice 4 must resolve. |
| Required output behavior | Section 5 | PASS — gap vs block vs delete-if-not-applicable explicit. |
| Renderer preservation | Section 6 | PASS — existing active-fund Ch3 degradation preserved/formalized. |
| Adapter mapping | Section 7 | PASS — explicit reviewed mapping only; unmapped fail closed. |
| Safety / non-goals | Section 10 | PASS — no provider/runtime/Agent/score-loop/golden/readiness/template truth changes. |

## Secret-Safety Statement

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.

## Validation

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-mimo-20260603.md
```
