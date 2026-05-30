# Targeted Re-Review: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage Plan

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md` (revised)
> Prior review: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-review-mimo-20260527.md`
> Verdict: **PASS**

---

## Finding Resolution

### M1 (MATERIAL): Bond triage methodology lacks explicit investigation path for field existence without PDF access

**Status: RESOLVED**

Evidence of resolution:

1. **Allowed evidence** (lines 90-96): Explicitly lists public CLI outputs, Gate 4 artifacts, accepted review evidence, "current tracked extractor tests / fixtures, if they already exist and can be read without generating new production data," and domain rules from accepted design/template sections.

2. **Forbidden evidence** (lines 98-103): Explicitly lists "direct production PDF reads," "direct cache inspection," "concrete source helper / downloader / source adapter calls," and "ad hoc parsing of production annual-report files outside the public repository / extractor path."

3. **No-inference rule** (line 105): "If the allowed evidence cannot prove whether an annual-report fact exists, classify the field as `needs-more-evidence` rather than inferring presence or absence."

4. **Forbidden operations** (lines 182-188): Repeats the no-PDF, no-cache, no-inference constraints at the slice specification level.

5. **Bond triage checklist** (lines 192-199): Each of the 6 fields now has an explicit initial question and allowed classifications, giving the triage worker clear guidance on what to investigate and what conclusions are permitted.

The investigation path is now explicit: the triage worker uses snapshot/score/quality-gate outputs, existing extractor test fixtures, and domain knowledge to classify fields, with `needs-more-evidence` as the safe fallback when allowed evidence is insufficient.

---

### M2 (MATERIAL): `investor_return` missing field not listed in Problem C's bond triage field list

**Status: RESOLVED**

Evidence of resolution:

1. **Problem C** (line 79): "`investor_return`: missing; this is generally Chapter 3 / investor-return evidence, not equity-only. Its absence should be classified as `extractor_gap`, `evidence_anchor_or_score_projection`, or score-contract gap unless a reviewed design explicitly says it is not applicable to `bond_fund`."

2. **Root-cause decision** (line 86): "Do not classify `investor_return` as `field_applicability_policy` for bond funds unless an accepted design / template artifact explicitly says investor-return evidence is not applicable to `bond_fund`."

3. **Bond triage checklist** (line 198): `investor_return` row with allowed classifications: `extractor_gap`, `evidence_anchor_or_score_projection`, `score_contract_gap`, `needs-more-evidence`; explicitly "not `field_applicability_policy` without accepted design support."

4. **Stop condition** (line 240): "`investor_return` would be treated as not applicable for bond funds without an accepted design / template decision."

`investor_return` is now fully integrated into the triage with appropriate guardrails.

---

## Scope Check

Additional revisions beyond M1/M2 resolution:

1. **Subgate track independence** (lines 129-132): Subgate 1 now has two independently closeable tracks — Track 1A (bond triage) and Track 1B (replacement probing). If no controller-approved candidates exist, Track 1B closes as `not_run_no_approved_candidates` without blocking Track 1A. This is a structural improvement.

2. **Bond triage checklist** (lines 192-199): New table with 6 fields, initial questions, and allowed classifications. This is a significant improvement in triage executability.

3. **`nav_data` anchor** (line 199): Added to the triage checklist as a `score_contract_gap` / `evidence_anchor_or_score_projection` candidate. This addresses the Gate 4 observation that `nav_data` has no annual-report anchor.

4. **Replacement candidate guard** (line 223): Now explicitly says to close Track 1B as `not_run_no_approved_candidates` rather than blocking the entire Subgate 1.

All revisions are within the plan-only scope. No source, test, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, source fallback, extractor, fixture, golden corpus, or package config changes are introduced.

---

## Summary

| Finding | Status | Notes |
|---------|--------|-------|
| M1 | RESOLVED | Allowed/forbidden evidence lists, no-inference rule, bond triage checklist |
| M2 | RESOLVED | `investor_return` in Problem C, triage checklist, stop condition, and root-cause guardrail |

---

## Verdict

**PASS**

Both material findings are fully resolved. The revised plan adds explicit allowed/forbidden evidence boundaries, a no-inference safety rule, a structured bond triage checklist covering all 6 missing fields, and independent track closeability for Subgate 1. All revisions remain within plan-only scope. No new findings.
