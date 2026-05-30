# QDII Replacement Fallback 021539 Evidence — MiMo Independent Evidence Review

> Date: 2026-05-27
> Reviewer: AgentMiMo (evidence review only; no implementation, commit, push, or PR)
> Target: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-20260527.md`
> Gate: `QDII replacement fallback 021539 evidence gate`
> Reason: AgentGLM review was interrupted; MiMo is second independent reviewer

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

No blocking or material findings. All 11 review criteria pass with direct evidence.

## Criterion-by-Criterion Evidence

### C1: Bounded 021539 / 2024 Only

Evidence §2: `fund_code=021539`, `report_year=2024`, single candidate. Evidence §10: no `analyze`, no `checklist`, no `020712`/active QDII/QDII-FOF/`013308`/bond QDII/`017641`/`096001`/`040046`/`019172` or any later candidate.

PASS.

### C2: Startup Packet Next Entry Point, Not Gate Switch

Evidence §1 replays Startup Packet with next entry point `QDII replacement fallback 021539 evidence gate` and states: "This evidence task follows the Startup Packet next entry point. It is not a gate switch." Matches `docs/implementation-control.md` Startup Packet (line 29).

PASS.

### C3: Provenance From Generated Public Outputs

Evidence §6 explicitly reads provenance from generated `summary.md` and `snapshot.jsonl`. Evidence §10: "Did not directly read PDF/cache/source-helper/downloader/source-adapter internals." Reviewer independently read `summary.md` (line 46: `eastmoney | true | eligible | complete`) and `snapshot.jsonl` (record 1: full provenance tuple). Both files exist and confirm all claimed fields.

PASS.

### C4: Provenance Interpretation Correct

Evidence §6 table from `snapshot.jsonl`:

| Field | Public value (verified in snapshot.jsonl record 1) |
|---|---|
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |

Evidence §6 interpretation explicitly enumerates absent fail-closed categories: no `schema_drift`, no `identity_mismatch`, no `integrity_error`. Reviewer independently confirmed: `snapshot.jsonl` 16 records all carry identical provenance tuple, none contain any fail-closed category. Interpretation matches AGENTS.md fallback table: `unavailable` → fallback allowed.

PASS.

### C5: Score/Quality Only After Eligible Provenance

Evidence §5 shows command sequence: snapshot (exit 0) → score (exit 0) → quality gate (exit 0). Evidence §6 ends: "The run therefore continued to extraction-score and quality-gate." — explicitly conditional on eligible provenance. Sequencing confirmed.

PASS.

### C6: Quality Evidence Matches Public Outputs

| Claim (Evidence §7) | Public output (verified) | Match |
|---|---|---|
| `quality_gate_status=block` | `quality_gate.json` status `"block"` | ✓ |
| `issue_count=7` | `quality_gate.json` issues array length 7 | ✓ |
| P0 `pass` | `score.json` p0_status `"pass"` | ✓ |
| `manager_strategy_text` pass, 100%/100% | `score.json` field_scores: coverage 1.0, traceability 1.0, status `"pass"` | ✓ |
| FQ4 missing-field-rate `35.7%` > threshold `35.0%` | `quality_gate.json` FQ4 issue: observed_rate 0.35714..., threshold 0.35 | ✓ |
| P1 failed fields: turnover_rate, holder_structure, holdings_snapshot, share_change | `score.json` fund_scores[0].p1_failed_fields exact match | ✓ |
| Quality issues: 4×FQ2 + FQ2F + FQ0 + FQ4 = 7 | `quality_gate.json` issues: 4×FQ2 (warn), 1×FQ2F (warn), 1×FQ0 (info), 1×FQ4 (block) | ✓ |
| `missing_field_count/total_field_count` = 5/14 | `score.json` fund_quality: missing_field_count=5, total_field_count=14 | ✓ |

Also verified: `field_count=14`, `fund_count=1`, `failed_fund_count=0`, `score_applicability_issue_count=0`, `correctness=unavailable`, status counts `pass=8, fail=6` (score.json field_scores: 8 pass + 6 fail = 14). All match.

PASS.

### C7: Terminal Classification Matches Accepted Matrix

Evidence §8: `terminal_classification=quality_blocked_after_provenance`, `promotion_disposition=not_promoted`. Condition: eligible provenance + P0 pass + FQ4 non-P0 structural quality block. This matches the accepted matrix row (evidence plan §10): "Provenance eligible + FQ4 or other non-P0 structural quality block + P0 pass → quality_blocked_after_provenance / not_promoted."

Consistent with prior accepted states: `096001` (P0 fail + FQ4 block), `040046` (P0 pass + FQ4 block), `019172` (P0 fail + FQ4 block) — all classified `quality_blocked_after_provenance`.

PASS.

### C8: Automatic QDII Probing Stop Declared

Evidence §8: "Because 021539 quality-blocked after eligible provenance, automatic QDII probing stops. A new disposition gate is required before any further QDII probing, diagnosis, taxonomy / asset-class fitness decision, or coverage-blockage decision." Matches the explicit stop condition in the plan controller judgment (lines 73–76) and post-019172 disposition controller judgment (lines 30, 70–71).

PASS.

### C9: False-Positive Suspicion Has Public Basis, No Policy Effect

Evidence §9 basis: `snapshot.jsonl` shows `classified_fund_type=qdii_fund` with classification_basis citing index-tracking strategy evidence, yet `index_profile` record is missing with note `非指数基金不适用指数画像`. This is a concrete public-output inconsistency.

Evidence §9 explicitly: "Policy effect: None. This suspicion does not change terminal classification, does not authorize code or policy changes, and does not promote the candidate." Required next action: "Separate future diagnosis/fix gate." Correct — suspicion does not alter outcome.

PASS.

### C10: Scratch Ignored, No Forbidden Changes, git diff --check Passed

Evidence §10: generated outputs are "ignored scratch and were not added as tracked fixtures." Evidence §10 explicit negation of all forbidden change categories. Evidence §11: `git diff --check` exit 0.

Reviewer independently ran `git diff --check`: exit 0. Generated output directory `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/` is not tracked. No production code, tests, README, design doc, control doc, renderer, FQ0-FQ6, Service, CLI, FundDocumentRepository, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden files, baseline fixtures, or durable corpus state changed.

PASS.

### C11: Stray Untracked File Noted

Git status shows `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-review-ds-20260527.md` as untracked — this is the DS review artifact from the same evidence gate, produced by a different reviewer. It is a legitimate review output, not a stray artifact needing controller disposition. Also present: `--help` (empty/unrelated untracked file from prior session). Neither affects this review's correctness.

PASS.

## Findings

None. All 11 criteria pass with direct, independently verified evidence.

### Minor Observations (Not Findings)

1. **snapshot_records 16 vs field_count 14**: `summary.md` reports 16 snapshot records; `score.json` uses 14 applicable fields after applicability exclusions (2 fields excluded: `index_profile` and `tracking_error`). This is the same accepted pattern from `040046` and `019172` evidence reviews. Does not affect terminal classification.

2. **Four consecutive QDII quality blocks**: `096001`, `040046`, `019172`, and now `021539` all quality-blocked after eligible provenance. The same P1 fields (`turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`) are consistently missing across all four candidates. This is a structural pattern for QDII funds, not an individual extraction failure. The required new disposition gate should weigh this evidence.

## Validation

- `git diff --check` exit 0 (independently verified).
- All generated public outputs exist and are untracked.
- No implementation, commit, push, or PR performed by this reviewer.
- This artifact is the only intended output of this review.
