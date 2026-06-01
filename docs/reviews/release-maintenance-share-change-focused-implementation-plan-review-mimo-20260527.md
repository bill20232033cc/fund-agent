# Plan Review: share_change Focused Implementation

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`
> Accepted evidence: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-controller-judgment-20260527.md`
> Verdict: **PASS**

---

## Criterion 1: Reconciles baseline triage correctly, does not overclaim 006597 readiness

**Verdict: PASS**

Lines 15-26: Reconciliation table correctly maps all 6 fields to accepted classifications. Line 26: "The next minimal implementation slice should not try to make 006597 fully quality-gate clean." Line 142: "Quality gate may still be `block` because `turnover_rate`, `holder_structure`, and `holdings_snapshot` are intentionally out of scope." Line 241: "Golden corpus v1 remains ineligible."

The plan explicitly scopes to reducing one confirmed extractor gap, not clearing the quality gate. No finding.

---

## Criterion 2: share_change root cause and implementation scope supported by evidence

**Verdict: PASS**

- Root cause (lines 36-41): snapshot shows `extraction_mode="missing"`, note says "§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别". Controller classified as `extractor_gap`.
- Behavior contract (lines 80-98): deterministic evidence for column selection, fail-closed ambiguity, explicit prohibitions against defaulting to wrong columns.
- Implementation strategy (lines 100-119): extend existing `_select_share_change_value_column()` conservatively with test-first approach.

The root cause is directly evidenced by the extraction attempt's own note. The implementation scope is narrow and proportionate. No finding.

---

## Criterion 3: File scope is minimal, respects module boundaries

**Verdict: PASS**

- Allowed production file: `holdings_share_change.py` (line 63).
- Conditionally allowed: `extraction_snapshot.py` only if controller explicitly accepts comparability (line 65).
- Focused tests: `test_holdings_share_change.py`, plus regression observation tests (lines 67-69).
- Forbidden (line 76): renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, repository, source fallback, PDF/cache, fixtures, golden, config, README, GitHub.
- No README expected (lines 71-72): private extractor fix with no public behavior change.

One production file, focused tests, no boundary violations. No finding.

---

## Criterion 4: Behavior contract avoids wrong-column selection, preserves fail-closed

**Verdict: PASS**

- Deterministic evidence rules (lines 83-86): exact fund_code header, §2 subordinate mapping with unique match.
- Fail-closed on ambiguity (lines 93-96): `extraction_mode="missing"`, no anchor, explicit ambiguity note.
- Explicit prohibitions (lines 97-98): no A-class default, no first-non-empty, no total-share column, no different fund code column. No P1/FQ/missing-rate weakening.

The contract is precise and safe. No finding.

---

## Criterion 5: Test strategy is sufficient and executable

**Verdict: PASS**

Focused unit tests (lines 125-131): 6 test cases covering correct selection, §2 no-unique-mapping ambiguity, multiple-matching ambiguity, total-share rejection, wrong-fund-code rejection, and existing test preservation.

006597 public rerun (lines 135-143): bounded CLI rerun with two valid outcomes — either `direct` with §10 anchor, or preserved `missing` with explicit ambiguity. Quality gate may still block.

Implementation gate commands (lines 147-155): unit tests, regression tests, ruff, extraction-snapshot, extraction-score, quality-gate, `git diff --check`. Full pytest triggered if snapshot/score/gate files are touched (lines 157-164).

Acceptance criteria (lines 230-239): deterministic selection covered, fail-closed tests pass, 006597 rerun produces direct or explicit ambiguity, FQ strictness unchanged.

No finding.

---

## Criterion 6: holdings_snapshot correctly deferred

**Verdict: PASS**

Lines 168-188: Explicit decision to not implement `holdings_snapshot` in this slice. Reasoning: equity-shaped semantics, affects field applicability/score denominators/quality-gate/template evidence contracts — larger scope than share_change.

Future design gate (lines 179-186): names 5 specific design questions for bond-specific holdings/risk evidence contract. Line 188: "Current `share_change` slice can ignore `holdings_snapshot` because it neither changes the accepted classification nor tries to clear the whole 006597 quality gate."

Clean separation. No finding.

---

## Criterion 7: Stop conditions and verifier matrix

**Verdict: PASS**

Stop conditions (lines 205-213): 7 conditions covering PDF access, ambiguous column choice, source fallback changes, FQ changes, broad bond analytics, Service/CLI changes, and persistent missing without deterministic next step.

Verifier matrix (lines 217-226): 8 rows covering plan closeout, unit tests, focused regression, lint, extraction-snapshot, extraction-score, quality-gate, and final hygiene. Each has a clear required outcome.

No finding.

---

## Criterion 8: Should implementation be authorized next?

**Verdict: YES — implementation should be authorized**

The plan meets all authorization gates:

1. Root cause is same-source evidenced (extraction attempt's own note).
2. File scope is minimal (one production file, focused tests).
3. Behavior contract prevents wrong-column selection and preserves fail-closed.
4. Test strategy covers focused unit tests and 006597 CLI rerun.
5. Stop conditions are explicit and strong.
6. `holdings_snapshot` is cleanly deferred to a separate design gate.
7. No FQ weakening, no renderer/Service/CLI/source changes.
8. Acceptance criteria allow both "direct with anchor" and "preserved ambiguity" outcomes.
9. Golden corpus remains ineligible until broader coverage is resolved.

The plan is safe to authorize for implementation.

---

## Summary

No findings. All 8 criteria pass. The plan is well-scoped, evidence-backed, and implementation-ready.

---

## Verdict

**PASS**

The plan correctly reconciles the baseline triage, narrows scope to one confirmed extractor gap (`share_change`), defines a precise behavior contract with fail-closed semantics, specifies executable tests with two valid outcomes, cleanly defers `holdings_snapshot` to a future design gate, and maintains all forbidden-module boundaries. Implementation should be authorized next.
