# Plan Review: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## Criterion 1: Does plan correctly reconcile Gate 4 accepted but golden corpus still blocked?

**Verdict: PASS**

The reconciliation (lines 18-25) correctly states:

- Clean coverage is 3 candidates / 3 slots, below 5-10 target.
- `006597` is quality-gate blocked by missing-field rate, not correctness mismatch.
- `110020` and `017641` remain fallback-blocked with unknown upstream failure category.
- `007721` and `017970` remain FOF data-gap / taxonomy-pending.
- `004393`/2025 remains probe-only.
- "The next gate must increase clean coverage and resolve the bond blocker before `golden answer corpus v1` can be considered."

This aligns precisely with the Gate 4 controller judgment. No finding.

---

## Criterion 2: Does it avoid big-bang implementation and choose a minimal next slice?

**Verdict: PASS**

The plan decomposes into three independent problems (A: index/QDII source recovery, B: FOF taxonomy, C: bond block triage) and recommends Subgate 1 as evidence-only triage before any implementation. Implementation slices 2A-2D are each gated behind same-source evidence from Subgate 1. Line 92: "Choose ordered subgates, not a big-bang implementation." Line 378: "Authorize Subgate 1 evidence-only triage next. Do not authorize implementation yet."

This is the correct minimal-slice approach. No finding.

---

## Criterion 3: Does Subgate 1 have executable commands, artifact policy, stop conditions, and no forbidden access?

**Verdict: PASS**

Subgate 1 specification:

- **Allowed operations** (lines 149-155): `extraction-snapshot`, `extraction-score`, `quality-gate`, `selected_funds_smoke.py`, read existing scratch outputs, write one tracked artifact.
- **Artifact policy** (lines 157-168): one tracked artifact under `docs/reviews/`, scratch paths explicitly listed, "No scratch output is a durable fixture or golden input."
- **Suggested commands** (lines 172-177): executable `uv run` commands with concrete `--run-id`, `--fund-code`, `--report-year`.
- **Candidate list guard** (line 179): "If no candidate list is accepted, stop and ask controller for the candidate source instead of ad hoc browsing or direct source calls."
- **Validation** (lines 183-185): `git diff --check`.
- **Stop conditions** (lines 189-195): 5 explicit conditions including direct PDF/cache access, source fallback ambiguity, and FOF probe finding only QDII-FOF.
- **Forbidden access** (lines 49-52): "Do not call concrete EID / Eastmoney adapters, PDF cache helpers, or download helpers directly."

No finding.

---

## Criterion 4: Are index/QDII fallback recovery/replacement rules safe?

**Verdict: PASS**

Problem A (lines 33-52) defines safe recovery rules:

- **Allowed categories**: `not_found`, `unavailable`.
- **Fail-closed categories**: `schema_drift`, `identity_mismatch`, `integrity_error`, `unknown_upstream_failure_category` after bounded recovery.
- **Safe path**: public CLI / Fund-layer repository paths only; no concrete adapter/helper calls.
- **Evidence gap handling** (line 50): "If current public artifacts do not expose upstream failure category, do not infer it from successful Eastmoney fallback. Record `needs-more-evidence`."
- **Replacement preference** (line 51): "Replacement is preferred over source implementation."
- **Scope boundary** (line 52): "Source fallback semantic changes are out of scope."

These rules correctly preserve fail-closed semantics under `AGENTS.md` §年报来源 fallback 策略. No finding.

---

## Criterion 5: Is FOF taxonomy handled without counting QDII-FOF as pure FOF?

**Verdict: PASS**

Problem B (lines 55-67) and Slice 2D (lines 300-316):

- Line 65: "Do not count QDII-FOF as pure FOF without an accepted taxonomy gate."
- Line 66: "Prefer pure FOF search first because it does not alter taxonomy semantics."
- Line 67: "Open taxonomy only if bounded pure FOF search fails or if the selected fund pool structurally contains only hybrid QDII-FOF examples."
- Line 305: "If no pure FOF is found, produce a taxonomy decision plan; do not implement."
- Stop condition line 315: "The plan would count QDII-FOF as pure FOF without explicit taxonomy decision."

This correctly preserves the existing `data_gap` / `taxonomy_pending` status. No finding.

---

## Criterion 6: Is 006597 bond block triage rigorous enough?

**Verdict: PASS_WITH_FINDINGS**

**Finding M1: Bond triage methodology lacks explicit investigation path for "does field exist in annual report"**

Evidence: Problem C (lines 69-88) defines four root-cause categories with clear classification criteria:

- `extractor_gap`: "If the annual report has the field and the extractor failed."
- `field_applicability_policy`: "If the field is equity-specific or irrelevant for bond lens."
- `evidence_anchor_or_score_projection`: "If the fact exists but lacks stable anchor / comparable subfield exposure."
- `bond_lens_contract_gap`: "If the current quality score asks for the wrong bond-lens facts."

However, the plan does not specify how the triage worker will determine whether a field "exists in the annual report" without direct PDF/cache access (which is forbidden). The suggested commands (lines 172-177) are `extraction-snapshot` → `extraction-score` → `quality-gate`, which produce snapshot data showing what was extracted and what's missing, but do not directly reveal whether the missing field is present in the source PDF.

Risk: The triage worker may need to inspect existing extractor test fixtures (e.g., `tests/fund/fixtures/`) or rely on domain knowledge about bond fund annual report structure. Without explicit guidance, the worker might either (a) make assumptions about field presence without same-source evidence, or (b) request PDF access and hit a stop condition.

Recommendation: Add a note in the Slice 1 specification clarifying that the triage may use existing extractor test fixtures and domain knowledge about bond fund annual report §2/§8/§9/§10 structure to classify field applicability, without needing direct PDF access. This keeps the triage evidence-based while respecting the no-PDF-access constraint.

Severity: **MATERIAL**

---

**Finding M2: Bond triage does not address `investor_return` missing field**

Evidence: Gate 4 run (line 45 of run artifact) observed `investor_return` as missing for `006597`. Problem C (lines 74-79) lists `turnover_rate`, `holder_structure`, `holdings_snapshot`, and `share_change` but does not mention `investor_return`. The `investor_return` field is §3-based and applies to all fund types per the 2026 new regulation, so its absence for bond funds is likely a real extraction gap, not a field-applicability issue.

Risk: If the triage omits `investor_return`, the root-cause classification may be incomplete, and the bond missing-field rate may remain above FQ4 threshold even after other fields are reclassified.

Recommendation: Add `investor_return` to Problem C's field list with the note that it is §3-based and applicable to all fund types, so its absence is likely `extractor_gap` or `evidence_anchor_or_score_projection`, not `field_applicability_policy`.

Severity: **MATERIAL**

---

## Criterion 7: If implementation slices are described, are file scopes/tests minimal and gated behind evidence?

**Verdict: PASS**

- **Slice 2A** (lines 197-237): Allowed files are `extraction_score.py`, optionally `fund_type.py`, optionally README. Tests are `test_extraction_score.py`, `test_quality_gate.py`, `test_quality_gate_integration.py`. Gated behind "same-source evidence proves one or more `006597` failing fields are not applicable for `bond_fund`."
- **Slice 2B** (lines 238-268): Allowed files are narrow extractor module, optionally `extraction_snapshot.py` or `extraction_score.py`, optionally README. Tests are existing focused extractor tests plus snapshot/score/quality tests. Gated behind "same-source evidence proves annual-report facts exist and current extraction / anchor / score projection misses them."
- **Slice 2C** (lines 269-299): Evidence-only for this gate; source-boundary implementation requires a separate plan/review gate.
- **Slice 2D** (lines 300-316): Evidence-only first; taxonomy implementation requires an accepted taxonomy plan.

Each slice has focused validation commands (ruff, pytest, `git diff --check`) and stop conditions. No finding.

---

## Criterion 8: Are verifier matrix and golden eligibility criteria sufficient?

**Verdict: PASS**

**Verifier matrix** (lines 331-343): 8 rows covering plan-only closeout, evidence-only bond triage, score, quality gate, replacement smoke, and conditional implementation tests. Each row is gated by prerequisites (snapshot exists, implementation authorized, etc.).

**Golden eligibility criteria** (lines 368-374): 5 conditions:

1. At least five representative clean candidates across at least half target fund-type slots.
2. No `unknown_upstream_failure_category`, fail-closed source, `taxonomy_pending`, or `probe_only`.
3. No quality-gate blocked clean candidate.
4. Same-year golden coverage separated from missing coverage, no correctness mismatch.
5. Curated-fixture / golden-corpus gate explicitly authorizes tracked paths.

These are sufficient and align with the Gate 4 run review's next-gate decision rules. No finding.

---

## Additional Observations

### Finding I1: `004393`/2025 probe-only not explicitly mentioned in Problem decomposition

Evidence: The reconciliation (line 24) correctly notes `004393`/2025 remains probe-only, but the three-problem decomposition (Problems A/B/C) does not include a problem statement for the 2025 probe. The 2025 probe is implicitly covered by "not baseline or golden material" in the reconciliation, but it is not mentioned in the recommended next slice or acceptance criteria.

Risk: Low. The 2025 probe is correctly excluded from clean denominator in Gate 4 and does not block the next gate. It is a residual that will need attention only if 2025 coverage becomes a target.

Severity: **INFO**

---

### Finding I2: Candidate replacement probe assumes selected-fund CSV has clean index/QDII candidates

Evidence: Slice 1 suggested commands (line 176) use `<INDEX_REPLACEMENT>`, `<QDII_REPLACEMENT>`, `<FOF_REPLACEMENT>` as placeholders. Line 179 says "Candidate replacement commands must be accepted selected-fund CSV evidence or a controller-approved candidate list." The Gate 4 candidate selection only evaluated `110020` (index, fallback-blocked) and `017641` (QDII, fallback-blocked) from the selected-fund CSV.

Risk: If the selected-fund CSV has no other index/QDII candidates, the replacement probe will find nothing, and the triage will need to either (a) search outside the CSV, or (b) accept that index/QDII coverage remains blocked. The stop condition at line 179 handles this correctly by requiring a controller-approved candidate list.

Severity: **INFO**

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| M1 | MATERIAL | Bond triage methodology lacks explicit investigation path for field existence without PDF access |
| M2 | MATERIAL | `investor_return` missing field not listed in Problem C's bond triage field list |
| I1 | INFO | `004393`/2025 probe-only not in problem decomposition (implicit coverage is sufficient) |
| I2 | INFO | Candidate replacement assumes selected-fund CSV has clean index/QDII candidates |

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is well-structured. It correctly reconciles Gate 4, avoids big-bang implementation, defines Subgate 1 as evidence-only triage with executable commands and stop conditions, preserves fail-closed fallback semantics, does not count QDII-FOF as pure FOF, gates implementation slices behind evidence with minimal file scopes, and provides sufficient verifier matrix and golden eligibility criteria.

Two material findings require attention before or during Subgate 1 execution:

1. **M1**: The bond triage should clarify that existing extractor test fixtures and domain knowledge about bond fund annual report structure can be used to classify field applicability without direct PDF access.
2. **M2**: `investor_return` should be added to Problem C's field list as a likely `extractor_gap` or `evidence_anchor_or_score_projection` (not `field_applicability_policy`), since it is §3-based and applies to all fund types.

Neither finding blocks plan acceptance. Both can be addressed as clarifications in the Subgate 1 evidence artifact or as guidance to the triage worker.
