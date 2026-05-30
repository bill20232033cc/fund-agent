# QDII Replacement Post-019172 Disposition Decision — AgentDS Independent Review

> Date: 2026-05-27
> Reviewer: AgentDS, independent decision review only. No implementation, no commit, no push, no PR.
> Target: `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-20260527.md`
> Scope: review artifact only. No evidence run. No code/test/production changes.

## Verdict

**PASS_WITH_FINDINGS**

No blocking findings. Three low findings. The recommendation to proceed to one bounded `021539` plan-first gate with hard stops is first-principles sound and consistent with all accepted evidence. The controller may accept this disposition as input to the next handoff.

---

## 1. Startup Packet Alignment (Criterion 1)

**PASS**

| Check | Result |
|---|---|
| Current phase `release maintenance` matches | yes |
| Startup Packet current gate matches `QDII replacement fallback 019172 evidence accepted locally` | yes |
| Startup Packet next entry point matches `QDII replacement post-019172 disposition decision gate` | yes |
| This artifact gate declared as same | yes (§1 table) |
| Not a gate switch | confirmed (§1 prose) |
| `init-agents` / tmux requirement preserved for controller | yes (§1 last paragraph) |
| Latest accepted checkpoint `d2fdbdb` matches HEAD | yes (`git log` confirms) |

The artifact correctly replays the Startup Packet and states it is not a gate switch. The `init-agents` workflow requirement is preserved as a controller obligation for the next handoff, which is the correct boundary: this worker is not the controller and did not dispatch agents.

---

## 2. Accepted Evidence State Accuracy (Criterion 2)

**PASS**

### 2.1 `096001` / 2024

| Field | Disposition Document | Accepted Evidence (control doc line 438) | Match |
|---|---|---|---|
| Source provenance | complete eligible fallback, `eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable` | same | yes |
| Quality gate | `block`, `issue_count=10` | `block` | yes |
| P0 blocker | `nav_benchmark_performance` coverage/traceability | same | yes |
| FQ4 | `42.9%` | `42.9%` | yes |
| `manager_strategy_text` | passed | passed | yes |
| P1 gaps | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | consistent with quality gate output | yes |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |

### 2.2 `040046` / 2024

| Field | Disposition Document | Accepted Evidence (control doc line 440) | Match |
|---|---|---|---|
| Source provenance | complete eligible fallback, `eastmoney`, same tuple | same | yes |
| Quality gate | `block`, `issue_count=7` | `block` | yes |
| P0 fields | all pass | all P0 fields pass | yes |
| FQ4 | `35.7%` > `35.0%` | `35.7%` > `35.0%` | yes |
| P1 gaps | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | same four fields | yes |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |

### 2.3 `019172` / 2024

| Field | Disposition Document | Accepted Evidence (control doc line 442) | Match |
|---|---|---|---|
| Source provenance | complete eligible fallback, `eastmoney`, same tuple | same | yes |
| Quality gate | `block`, `issue_count=9` | `block` | yes |
| P0 blocker | `manager_strategy_text` `0.0%/0.0%` | `manager_strategy_text` coverage/traceability `0.0%/0.0%` | yes |
| FQ4 | `35.7%` > `35.0%` | `35.7%` > `35.0%` | yes |
| P1 gaps | `turnover_rate`, `holdings_snapshot`, `share_change` | consistent; `holder_structure` not in P1 for this candidate | yes |
| Terminal | `quality_blocked_after_provenance` | `quality_blocked_after_provenance` | yes |
| Promotion | `not_promoted` | `not_promoted` | yes |

The three accepted candidate summaries are accurate and consistent with the accepted controller judgments at implementation-control lines 438, 440, 442. The distinction between `019172` (P0 `manager_strategy_text` block) and `040046` (no P0 field failures, FQ4 structural block) is correctly preserved.

The disposition summary (lines 33–38 of the target) correctly states: all three have eligible provenance, all three are quality-blocked, none is replacement-ready or promoted, and the repeated block pattern requires disposition but does not silently skip enumeration order.

---

## 3. Option Comparison Quality (Criterion 3)

**PASS**

| Option | Correctly characterized | Future-as-fact avoided |
|---|---|---|
| A (continue to `021539`) | yes — respects enumeration order, non-FOF, bounded single-candidate | yes — `021539` correctly labeled `provenance_unknown`, `quality_unknown`, `not_promoted` |
| B (taxonomy/asset-class fitness) | yes — scope defined as QDII-FOF, `013308`, bond QDII; correctly noted as not producing near-term replacement | yes — taxonomy gate described as future path, not current accepted state |
| C (stop QDII replacement) | yes — correctly described as premature before testing `021539` | yes — not written as the current decision |

The option comparison correctly treats `021539` as the next untested non-FOF equity QDII row per the accepted enumeration order (candidate_order=4 in `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md`). It does not write taxonomy changes, QDII-FOF eligibility, `013308` resolution, or bond QDII fitness as current facts.

The "arguments against" for Option A correctly identify the structural signal in three consecutive blocks. This signal is treated as a decision input, not as proof that all QDII candidates will fail — a correct first-principles stance.

---

## 4. First-Principles Recommendation Quality (Criterion 4)

**PASS**

The §4 judgment correctly anchors to:
- The goal is a small usable baseline corpus, not maximizing row count.
- Source eligibility alone is insufficient (proven by three eligible-provenance, all quality-blocked).
- Repeated blocks signal a likely structural gap but don't prove the next row fails.
- Skipping enumeration order requires a reason stronger than fatigue.
- A bounded, reviewed, plan-first gate for exactly one candidate is the smallest move respecting both constraints.

The hard stop conditions (§5) are explicit and well-formed:

| Stop trigger | Correct |
|---|---|
| Plan review finds `021539` is not the accepted next non-FOF equity-QDII row | yes |
| Plan review finds proposed commands require direct PDF/cache/source-helper access | yes |
| Public provenance missing, incomplete, or fail-closed before quality | yes |
| Quality gate blocks on P0, FQ4, or equivalent before promotion | yes |
| If `021539` is quality-blocked after eligible provenance → stop automatic QDII probing, require new disposition gate | yes |
| Do not continue automatically to `020712` or later candidates | yes |

**Low Finding F1**: The stop condition "Stop at plan review if the proposed commands require direct PDF/cache/source-helper/downloader/source-adapter access" (§5, line 137) is a forward-looking constraint on an evidence plan gate worker, not something the current decision worker can enforce. It is valid guidance but lives at the wrong level of abstraction for a disposition decision artifact. The next plan gate should restate this as its own scope constraint, not rely on this decision artifact as the authority.

Severity: low. Does not affect the correctness of the disposition recommendation.

---

## 5. Preserved Exclusions (Criterion 5)

**PASS**

| Exclusion | Preserved | Evidence |
|---|---|---|
| `017641` | yes | §6 line 152: remains excluded, complete eligible fallback provenance, quality-blocked, not promoted |
| QDII-FOF | yes | §6 line 153: excluded unless separate taxonomy gate accepts QDII-FOF |
| `013308` | yes | §6 line 154: naming/category conflict, must not enter evidence without separate taxonomy/controller decision |
| Bond QDII | yes | §6 line 155: asset-class fitness pending, must not enter evidence without controller acceptance |

All four exclusions match the accepted states in the enumeration plan (lines 57–70 of that artifact) and the implementation-control accepted decisions.

---

## 6. Prohibited Actions (Criterion 6)

**PASS**

The §7 prohibition list is comprehensive and correctly forbids:
- `fund-analysis` evidence commands
- `analyze`, `checklist`, `extraction-snapshot`, `extraction-score`, `quality-gate`
- Code, test, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, taxonomy, extractor, Host, Agent, Dayu changes
- Golden files, baseline fixtures, durable corpus, clean denominator, report-quality corpus changes
- `docs/design.md` or `docs/implementation-control.md` changes
- Promotion of any candidate to any accepted state
- Commit, push, PR, merge, branch deletion, GitHub mutations

The artifact's own scope (decision artifact only, no evidence run, no code change) matches these prohibitions.

---

## 7. Next Entry Point Assessment (Criterion 7)

**PASS**

The recommended next entry point is:

> `QDII replacement fallback candidate evidence plan gate for 021539`

I do not oppose this recommendation. The reasoning chain is sound:

1. `021539` is candidate_order=4 in the accepted enumeration table. Candidates 1, 2, 3 have been tested and quality-blocked. It is the next row.
2. Three failures is a signal, not proof. A bounded single-candidate gate with transparent stop conditions is the minimum additional evidence needed to distinguish "three bad rows" from "all QDII rows are structurally quality-blocked."
3. The plan-first constraint (plan before evidence, review before execution) prevents unreviewed evidence runs.
4. The hard stop on quality block closes the probing loop at exactly the right point: after testing the remaining non-FOF equity QDII row, before entering more exotic QDII rows (`020712` Japan, `006282` active, etc.).

**Low Finding F2**: The gate name `evidence plan gate` could be misinterpreted by a future worker as authorizing evidence execution after the plan is accepted. The constraints in §5 are clear that this is plan-first, but the gate name itself doesn't encode that distinction. A more precise name would be `QDII replacement plan-first gate for 021539` or similar, but this is naming hygiene, not a correctness issue.

Severity: low.

I do not recommend taxonomy gate or stop gate as the next entry point. Reason: `021539` is the last non-FOF overseas equity QDII in the enumeration order (after it, candidates 5-9 are Japan QDII, active QDII, or taxonomy-unknown rows). Testing it closes the equity-QDII enumeration path with direct evidence rather than premature taxonomy decisions. A stop gate after a clean `021539` quality-block would have a stronger evidence basis.

---

## 8. Validation Scope (Criterion 8)

**PASS**

The only validation command is `git diff --check`, exit code 0. No code tests, no ruff, no pytest, no analyze/checklist smoke, no extraction/quality commands were run. This is appropriate for a decision artifact with no code changes.

**Low Finding F3**: The artifact does not explicitly state that broader validation (pytest, ruff, boundary checks) is not required because no code was changed. While this is implied by the §7 prohibition list, an explicit validation-scope statement would make the boundary clearer for future reviewers.

Severity: low.

---

## Findings Summary

| ID | Severity | Criterion | Description |
|---|---|---|---|
| F1 | low | 4 | Stop condition about "proposed commands" in plan review is forward-looking guidance that a future plan gate must restate as its own scope constraint |
| F2 | low | 7 | Gate name `evidence plan gate` doesn't encode the plan-first constraint; a future worker could misinterpret it as authorizing evidence execution |
| F3 | low | 8 | Validation scope doesn't explicitly state why broader validation is not required |

No blocking findings. No material findings.

---

## Review Boundary

This review is a decision review artifact only. It does not authorize:
- any evidence run, fund-analysis command, CLI execution;
- any code, test, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, taxonomy, extractor, Host, Agent, or Dayu change;
- any promotion of any candidate to baseline, golden, clean denominator, fixture, report-quality corpus, scoring-ready, source-safe, or replacement-accepted state;
- any commit, push, PR, merge, or GitHub mutation;
- updating `docs/implementation-control.md` or `docs/design.md`.

The controller retains authority for judgment, control-doc update, and the next handoff.
