# DS Independent Review: Release-Maintenance Consolidation Post-021539 Disposition

> Date: 2026-05-27
> Reviewer: AgentDS
> Target: `docs/reviews/release-maintenance-consolidation-post-021539-disposition-20260527.md`
> Gate: `release-maintenance consolidation closeout / QDII post-021539 disposition gate`
> Review scope: adversarial review only; no implementation, no file modification, no commit.

## Verdict: PASS_WITH_FINDINGS

No blocking issues. Two medium findings and three low/info findings below. The disposition artifact is structurally sound, correctly records QDII hard stop, preserves all four candidates in correct terminal state, does not promote any sample, and recommends a defensible next cursor. It can proceed to controller judgment after the findings are acknowledged or patched.

---

## Findings

### Finding 1 — MEDIUM: Startup Packet replay "Gate switch? No" is ambiguous

**Reference**: disposition artifact line 17: `Gate switch? No. This gate follows the Startup Packet next entry point.`

The Startup Packet replay table shows:

- `Current gate`: `QDII replacement fallback 021539 evidence accepted locally` (the PREVIOUS gate)
- `Next entry point`: `QDII replacement post-021539 disposition decision gate` (THIS gate)

The disposition IS executing the next entry point, which constitutes a gate switch from the evidence gate to the disposition gate. The word "No" can be misread as denying a switch occurred. The quoted explanation clarifies intent ("follows the Startup Packet next entry point"), meaning "no unauthorized gate switch," but the bare "No" creates ambiguity for future recovery.

**Recommendation**: Change "Gate switch? No." to "Gate switch? Yes, from evidence gate to disposition gate as prescribed." Or drop the row and add a sentence: "This gate is entered as the Startup Packet next entry point; no unauthorized deviation occurred."

**Severity**: Medium. Does not affect disposition correctness but degrades future-recovery clarity.

---

### Finding 2 — MEDIUM: Active Gate Ledger in compressed control doc omits this disposition gate

**Reference**: `docs/implementation-control.md` diff, Active Gate Ledger section.

The compressed control doc (v2.1) Active Gate Ledger covers 9 recent gates from post-provenance recovery through QDII replacement fallback 021539 evidence. The disposition artifact's own Verifier Matrix (line 113) says "controller judgment: pending controller judgment artifact." But the disposition artifact does not explicitly state that the control doc must be updated AFTER controller judgment to add this disposition gate as the 10th ledger entry and to update the Startup Packet's Current gate and Next entry point.

The Open Residuals table in the compressed control doc already has the QDII hard stop row with owner `QDII replacement post-021539 disposition decision gate`. After this disposition is accepted, that residual row must be resolved and the Startup Packet updated.

**Recommendation**: Add an explicit statement in the disposition's Verifier Matrix or a new "Post-Acceptance Control Update" section listing which rows change: Current gate updated, Next entry point set to bond positive-risk evidence gate, QDII hard stop residual resolved, and a new Active Gate Ledger entry appended.

**Severity**: Medium. The control doc update is described in the Next Entry Point section of the control doc (line 79: "Update this control document after disposition controller judgment"), but the disposition artifact itself should explicitly state what updates are needed.

---

### Finding 3 — LOW: Artifact disposition table self-references as "stage current-gate artifact after review"

**Reference**: disposition artifact line 74.

The Artifact Disposition table lists itself (`docs/reviews/release-maintenance-consolidation-post-021539-disposition-20260527.md`) with decision "stage current-gate artifact after review." This is circular: the artifact dispositioning itself. While customary in disposition gates, the controller judgment should explicitly decide whether to stage this artifact, rather than the artifact pre-authorizing its own staging.

**Recommendation**: No change to the disposition artifact needed. The controller should separately confirm or override this decision in the controller judgment artifact.

**Severity**: Low. Standard practice in disposition gates; flagged for controller awareness.

---

### Finding 4 — LOW: Coverage matrix for `110020` references "quality `warn`" without restating the methodology/constituents residual

**Reference**: disposition artifact line 60: `index / 110020 / 2024 | reviewed coverage candidate input accepted; quality warn; not_promoted`.

The blocker reason says "Methodology / constituents evidence, reviewed-fact freeze, strict golden absence disposition still unresolved." This is correct. However, the `110020` row in the disposition's coverage matrix does not restate the accepted terminal classification from the `110020` evidence gate: `reviewed_coverage_candidate_input_accepted`. A future reader might not know that `110020` was accepted only as coverage input, not as a coverage baseline candidate.

**Recommendation**: Consider adding the accepted terminal classification to the blocker reason, e.g., "Accepted as `reviewed_coverage_candidate_input_accepted` (not baseline-ready); methodology / constituents evidence …"

**Severity**: Low. The matrix correctly marks it "not yet eligible" and "not_promoted." The blocker description is accurate but could be more precise for recovery.

---

### Finding 5 — LOW: Comprehensive audit reports are stale relative to HEAD but correctly dispositioned

**Reference**: disposition artifact lines 75-76.

The `20260527` comprehensive audit report was produced at `f88a3aa` (21 commits ahead of main, per its header). Current HEAD is `7ab5656` (42 commits ahead). The audit report's Current gate stated `source provenance primary-failure-category propagation implementation accepted locally` — several gates behind the current state. The disposition correctly marks both audit reports as "evidence-chain / research input" and "historical audit report, not current truth." No action needed.

**Severity**: Low / Info. Confirmed disposition is correct.

---

### Finding 6 — INFO: `--help` stray file correctly handled

**Reference**: disposition artifact line 79.

Confirmed: `/Users/maomao/fund-agent/--help` exists as a zero-byte file (verified via `ls -la`). The disposition correctly marks it "ask-before-delete; do not stage" with owner "user authorization required." This is the only safe disposition for a stray file whose origin is uncertain.

**Severity**: Info. Disposition is correct.

---

## Cross-Reference Verification

### QDII candidate evidence accuracy

Spot-checked all four candidates against their accepted evidence artifacts:

| Candidate | Claim in disposition | Evidence artifact | Match? |
|---|---|---|---|
| `096001` | P0 `nav_benchmark_performance`, FQ4 42.9% | 021539 evidence line 51 | Yes |
| `040046` | P0 pass, FQ4 35.7% | 040046 evidence lines 106, 117, 122 | Yes |
| `019172` | P0 `manager_strategy_text` 0.0%/0.0%, FQ4 35.7% | 019172 evidence lines 142, 165, 178 | Yes |
| `021539` | P0 pass, `manager_strategy_text` pass, FQ4 35.7% | 021539 evidence lines 139, 162, 177, 189 | Yes |

All four are correctly recorded as `provenance=eligible, quality=block, promotion=not_promoted`. The hard stop decision is consistent with the accepted evidence gate judgments.

### Coverage matrix consistency

All six coverage slots are dispositioned with "not yet eligible" or "blocked" status. No promotion to baseline, golden, or scoring-ready state occurs. The matrix is internally consistent and aligns with the accepted artifacts referenced in the Active Gate Ledger.

### Scope compliance

The disposition artifact declares scope as "docs/control/disposition only; no production code, renderer, quality gate, extractor, baseline/golden promotion, or new QDII probing." Review of the git diff (`docs/implementation-control.md` only) and the untracked file list confirms no production code, renderer, or quality gate changes are included.

---

## Verdict Summary

| Criterion | Assessment |
|---|---|
| 1. Source-document standards check | PASS — correct; archive does not override Startup Packet |
| 2. QDII post-021539 disposition | PASS — all four candidates correctly recorded; hard stop enforced |
| 3. Coverage disposition matrix | PASS — consistent; no promotion |
| 4. Untracked artifact disposition | PASS — `--help` correctly ask-before-delete |
| 5. Next cursor recommendation | PASS — bond positive-risk evidence gate is defensible; alternatives adequately rejected |
| 6. Scope authorization | PASS — no production code, renderer, quality gate, or unauthorized changes |

**Overall**: PASS_WITH_FINDINGS. The two medium findings (ambiguous gate-switch wording, missing explicit post-acceptance control update instructions) should be addressed before or during controller judgment. No re-review is required after those patches unless the controller introduces materially different disposition decisions.

---

## Re-review Statement

Re-review is NOT required if controller judgment acknowledges Finding 1 and Finding 2 and either patches the wording or accepts the ambiguity. If the controller makes substantive changes to the disposition matrix, QDII terminal states, or next cursor recommendation, a fresh DS review is required.
