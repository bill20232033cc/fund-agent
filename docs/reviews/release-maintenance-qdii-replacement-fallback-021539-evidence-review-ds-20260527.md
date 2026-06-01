# QDII Replacement Fallback 021539 Evidence — DS Independent Evidence Review

> Date: 2026-05-27
> Reviewer: AgentDS (evidence review only; no implementation, commit, push, or PR)
> Target: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-20260527.md`
> Gate: `QDII replacement fallback 021539 evidence gate`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate in control doc | `QDII replacement fallback 021539 evidence plan accepted locally` |
| Control doc next entry point | `QDII replacement fallback 021539 evidence gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement fallback 021539 evidence gate` |
| Latest accepted checkpoint | `b575a49 docs: accept qdii fallback 021539 evidence plan` |

Control doc confirmed. This review follows the accepted next entry point.

## Verdict: PASS

No blocking or material findings. All 10 review criteria pass with direct evidence.

## Criterion-by-Criterion Evidence

### C1: Bounded 021539 / 2024 Only

Evidence §2: `fund_code=021539`, `report_year=2024`. Evidence §10: no `analyze`, no `checklist`, no `020712`/active QDII/QDII-FOF/`013308`/bond QDII/`017641`/`096001`/`040046`/`019172` or any later candidate.

PASS.

### C2: Startup Packet Next Entry Point, Not Gate Switch

Evidence §1 replays Startup Packet with next entry point `QDII replacement fallback 021539 evidence gate` and states: "This evidence task follows the Startup Packet next entry point. It is not a gate switch." Matches control doc §28–31.

PASS.

### C3: Provenance From Generated Public Outputs

Evidence §6 explicitly reads provenance from generated `summary.md` and `snapshot.jsonl`. Evidence §10: "Did not directly read PDF/cache/source-helper/downloader/source-adapter internals." Reviewer independently read `summary.md`, `snapshot.jsonl`, `score.json`, `quality_gate.json` and confirmed all claims are verifiable against public outputs.

PASS.

### C4: Provenance Interpretation Correct

Evidence §6 table from `snapshot.jsonl`:

| Field | Public value (verified) |
|---|---|
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |

Evidence §6 interpretation explicitly enumerates absent fail-closed categories: no `schema_drift`, `identity_mismatch`, `integrity_error`. Reviewer independently confirmed all fields in `snapshot.jsonl`. Interpretation matches AGENTS.md fallback table (lines 227–233): `unavailable` → fallback allowed.

PASS.

### C5: Score/Quality Only After Eligible Provenance

Evidence §5 shows command sequence: snapshot → score → quality gate. Evidence §6 ends: "The run therefore continued to extraction-score and quality-gate." — explicitly conditional on eligible provenance. Sequencing confirmed.

PASS.

### C6: Quality Evidence Matches Public Outputs

| Claim (Evidence §7) | Public output (verified) | Match |
|---|---|---|
| `quality_gate_status=block` | `quality_gate.json` status `"block"` | ✓ |
| `issue_count=7` | `quality_gate.json` issues array length 7 | ✓ |
| P0 `pass` | `score.json` p0_status `"pass"` | ✓ |
| `manager_strategy_text` pass, 100%/100% | `score.json` field_scores: coverage 1.0, traceability 1.0, status `"pass"` | ✓ |
| FQ4 missing-field-rate `35.7%` > threshold `35.0%` | `quality_gate.json` FQ4 issue: observed_rate 0.35714, threshold 0.35 | ✓ |
| P1 failed fields: turnover_rate, holder_structure, holdings_snapshot, share_change | `score.json` fund_scores[0].p1_failed_fields exact match | ✓ |
| Quality issues table (4×FQ2 + FQ2F + FQ0 + FQ4 = 7) | `quality_gate.json` issues array: 4×FQ2, 1×FQ2F, 1×FQ0, 1×FQ4 | ✓ |

Also verified: `field_count=14`, `fund_count=1`, `failed_fund_count=0`, `score_applicability_issue_count=0`, `correctness=unavailable`, status counts `pass=8, fail=6` (score.json field_scores: 8 pass + 6 fail = 14). All match.

PASS.

### C7: Terminal Classification Matches Accepted Matrix

Evidence §8: `terminal_classification=quality_blocked_after_provenance`, `promotion_disposition=not_promoted`. Matches the accepted matrix consistently applied to `096001` (040046 controller judgment §3), `040046` (040046 controller judgment §35–47), and `019172` (019172 controller judgment §35–47): eligible provenance + quality block → quality_blocked_after_provenance / not_promoted.

PASS.

### C8: Automatic QDII Probing Stop Declared

Evidence §8: "Because 021539 quality-blocked after eligible provenance, automatic QDII probing stops. A new disposition gate is required before any further QDII probing, diagnosis, taxonomy / asset-class fitness decision, or coverage-blockage decision." Evidence §9 reinforces: "Policy effect: None. Required next action: Separate future diagnosis/fix gate." Matches the explicit stop condition in the plan controller judgment (lines 73–76) and post-019172 disposition controller judgment (lines 30, 70–71).

PASS.

### C9: False-Positive Suspicion Has Public Basis, No Policy Effect

Evidence §9 basis: `snapshot.jsonl` shows `classified_fund_type=qdii_fund` while the fund is an ETF feeder tracking CAC40; `index_profile` record missing (verified in `summary.md`: coverage 0.0%). Evidence §9 explicitly: "Policy effect: None. This suspicion does not change terminal classification, does not authorize code or policy changes, and does not promote the candidate." Follows the accepted pattern from 019172 controller judgment (DS L2 false_positive_suspicion calibration residual).

PASS.

### C10: Scratch Ignored, No Forbidden Changes, git diff --check Passed

Evidence §10: generated outputs are "ignored scratch and were not added as tracked fixtures." Evidence §10 explicit negation of all forbidden change categories (code, tests, README, design.md, control.md, renderer, FQ0-FQ6, Service, CLI, FundDocumentRepository, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden files, baseline fixtures, durable corpus). Evidence §11: `git diff --check` exit 0. Reviewer independently ran `git diff --check`: exit 0. `git status` on generated output dir: no tracked files.

PASS.

## Findings

None. All 10 criteria pass with direct, independently verified evidence.

### Minor Observations (Not Findings)

1. **snapshot_records 16 vs field_count 14**: `summary.md` reports 16 snapshot records; `score.json` uses 14 applicable fields after applicability exclusions (2 fields excluded: `index_profile` and `tracking_error`). This is the same accepted pattern from 040046 and 019172 controller judgments (DS L1 / GLM L1 accepted as low residuals). Does not affect terminal classification.

2. **`fallback_used` boolean vs string presentation**: `snapshot.jsonl` stores `true` (JSON boolean); evidence artifact presents `true` (markdown string). Cosmetic, no substantive effect.

## Validation

- `git diff --check` exit 0 (independently verified).
- All generated public outputs (`summary.md`, `snapshot.jsonl`, `score.json`, `score.md`, `quality_gate.json`, `quality_gate.md`, `golden_set.json`, `errors.jsonl`) exist and are untracked.
- No implementation, commit, push, or PR performed by this reviewer.
- This artifact is the only intended output of this review.
