# QDII Replacement Fallback 019172 Evidence — DS Review

> Date: 2026-05-27
> Reviewer: AgentDS (independent evidence review only; no implementation, no commit, no push, no PR)
> Gate: `QDII replacement fallback 019172 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this review | `QDII replacement fallback 019172 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 019172 evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint | `dafc72f docs: accept qdii fallback 019172 evidence plan` |
| Design truth | `docs/design.md` v2.2 |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |

This review is scoped to independent evidence review only. No implementation, commit, push, or PR activity is authorized.

## Context Loaded

- `AGENTS.md` — rule truth
- `docs/design.md` v2.2 — design truth, including source fallback policy (§6.1), quality gate rules (§7), fund type classification (§6.5)
- `docs/implementation-control.md` Startup Packet — current gate, next entry point
- Accepted 019172 evidence plan and controller judgment
- Accepted 096001 candidate evidence controller judgment
- Accepted 040046 evidence controller judgment
- Generated public outputs: `summary.md`, `snapshot.jsonl`, `score.json`, `quality_gate.json`

## Review Criteria: Blocking Checks

### 1. Bounded Scope: only 019172 / 2024

Evidence §2 identifies candidate as exactly `019172` / `2024`. Evidence §9 confirms no `096001`, `040046`, `017641`, or later fallback candidates were run. No `analyze` or `checklist` commands were executed. Prior accepted states for `096001` and `040046` are preserved in §2 as `quality_blocked_after_provenance` / `not_promoted`.

**PASS.**

### 2. Follows Startup Packet Next Entry Point, Not Gate Switch

Evidence §1 replays Startup Packet with next entry point `QDII replacement fallback 019172 evidence gate`. Evidence states: "This evidence run follows the Startup Packet next entry point. It is not a gate switch." Controller judgment confirms this is the accepted next entry point after `040046` evidence was accepted.

**PASS.**

### 3. Reads Provenance from Generated summary.md + snapshot.jsonl, Not stdout-only

Evidence §5 explicitly records that `summary.md` and `snapshot.jsonl` exist and were read. Each provenance field includes a "Public source" column citing which file it was read from. Independent verification: both files exist at the expected paths and contain the reported values.

**PASS.**

### 4. Provenance Interpretation Correct

Evidence §5 records the provenance tuple and interprets it:

| Field | Evidence Value | Generated Source Verified |
|---|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` | snapshot.jsonl L1 ✓ |
| `source_strategy` | `primary_then_fallback` | snapshot.jsonl L1 ✓ |
| `resolved_source_name` | `eastmoney` | summary.md + snapshot.jsonl L1 ✓ |
| `fallback_used` | `true` | summary.md + snapshot.jsonl L1 ✓ |
| `primary_failure_category` | `unavailable` | snapshot.jsonl L1 ✓ |
| `fallback_eligibility` | `eligible` | summary.md + snapshot.jsonl L1 ✓ |
| `source_provenance_status` | `complete` | summary.md + snapshot.jsonl L1 ✓ |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | summary.md + snapshot.jsonl L1 ✓ |

Evidence interpretation: "provenance is eligible because fallback was used after `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, and public provenance status is `complete`. No public generated output showed `schema_drift`, `identity_mismatch`, or `integrity_error`; no fail-closed stop was triggered."

This is correct per `docs/design.md` §6.1 fallback eligibility rules (`not_found` and `unavailable` are the two eligible failure categories) and the accepted plan's terminal-state matrix §7. No fail-closed category appears in any public output.

**PASS.**

### 5. Score/Quality Only After Provenance Eligible

Evidence structure: §5 establishes eligible provenance first, then §6 discusses score and quality. The flow is provenance interpretation → score → quality gate. This matches the accepted plan requirement: "Source provenance must be interpreted before score, quality status, replacement usefulness, or any promotion language."

**PASS.**

### 6. Quality Evidence Correctly Recorded

Evidence §6 records quality data. Cross-reference against generated outputs:

| Evidence Claim | Generated Source | Match |
|---|---|---|
| `quality_gate_status=block` | quality_gate.json `"status": "block"` | ✓ |
| `issue_count=9` | quality_gate.json `"issue_count": 9` | ✓ |
| `status_counts: pass=8, fail=6` | score.json `"fail": 6, "pass": 8` | ✓ |
| `p0_status=fail` | score.json `"p0_status": "fail"` | ✓ |
| P0 failed: `manager_strategy_text` | score.json fund_scores | ✓ |
| P1 failed: `turnover_rate, holdings_snapshot, share_change` | score.json fund_scores | ✓ |
| `manager_strategy_text` coverage/traceability `0.0%/0.0%` | score.json field_scores | ✓ |
| FQ2 block on `manager_strategy_text` | quality_gate.json issues[0] | ✓ |
| FQ3 block on `manager_strategy_text` | quality_gate.json issues[1] | ✓ |
| FQ2F block on `019172` P0 | quality_gate.json issues[5] | ✓ |
| FQ0 info: golden not configured | quality_gate.json issues[7] | ✓ |
| FQ4 block: `35.7% > 35.0%` | quality_gate.json: `0.35714 > 0.35` | ✓ |
| FQ5 resolved: `海外股票类` matched `qdii_fund` | quality_gate.json FQ5 `"resolved"` | ✓ |
| `missing_field_count=5, total_field_count=14, rate=35.7%` | score.json fund_quality: `5/14=0.35714` | ✓ |

All numeric values verified consistent between evidence artifact and generated public outputs.

**PASS.**

### 7. Terminal Classification Matches Accepted Matrix

Evidence §7 classifies as `quality_blocked_after_provenance` with `promotion_disposition=not_promoted`. Two independent blockers exist:

1. P0 `manager_strategy_text` (FQ2 + FQ3 + FQ2F → block)
2. FQ4 missing-field-rate `35.7% > 35.0%` → block

Both conditions independently map to `quality_blocked_after_provenance` in the accepted plan's terminal-state matrix (rows: "Provenance eligible, quality P0 block on manager_strategy_text" → `quality_blocked_after_provenance`; "Provenance eligible + FQ4 or other non-P0 structural quality block" → `quality_blocked_after_provenance`). The combined presence of both blockers does not change the classification.

**PASS.**

### 8. false_positive_suspicion Has Public Evidence Basis, Not Used to Bypass

Evidence §8 sets `false_positive_suspicion=true` with two public observations:

- `index_profile` note "非指数基金不适用指数画像" vs classification_basis including index/replication strategy text
- `manager_strategy_text` note "§4 未披露可规则化抽取的投资策略/后市展望" as potential disclosure gap or extractor mismatch

Both observations are verifiable in public `snapshot.jsonl` output (lines 4, 10). Evidence explicitly states: "This suspicion does not change the accepted policy outcome. No code, extractor, taxonomy, source strategy, renderer, FQ0-FQ6, Service/CLI, golden, or baseline changes are authorized in this gate."

Note: the `index_profile` observation reflects correct classification behavior—QDII keyword takes priority over index keyword in `classify_fund_type()`, producing `qdii_fund` rather than `index_fund`, so `index_profile` correctly does not apply. This is recorded as L2 below.

**PASS.**

### 9. Scratch Reports Ignored, No Production Changes

Evidence §9 confirms: no changes to production code, tests, design, control, renderer, FQ0-FQ6, Service, CLI, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden, or baseline. Generated `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/` is scratch output under `.gitignore`.

**PASS.**

### 10. git diff --check Passes

Evidence §10 records exit code 0. Independent verification: `git diff --check` exits 0 with no output.

**PASS.**

## Findings

### L1: 16-field summary vs 14-field score transition not explained

**Severity: low**

The `summary.md` header reports `snapshot_records: 16` and Field Coverage table lists 16 fields, while `score.json` reports `field_count: 14`. The 2 excluded fields are `index_profile` and `tracking_error`, which are conditionally applicable only for `index_fund`/`enhanced_index` per `docs/design.md` §7.3, and correctly excluded from scoring for `qdii_fund`. Same pattern as accepted `040046` evidence (controller accepted as low residual). The evidence artifact does not explicitly note this transition.

**Evidence**: summary.md Field Coverage shows 16 rows including `index_profile` and `tracking_error`; score.json `"field_count": 14` excludes both.

### L2: false_positive_suspicion re index_profile reflects correct behavior

**Severity: low**

The evidence flags `index_profile` note "非指数基金不适用指数画像" vs classification_basis including index/replication strategy text as suspicious. Per `docs/design.md` §6.5, QDII keyword takes priority over index keyword in `classify_fund_type()`, so `qdii_fund` is the correct classification, and `index_profile` is conditionally applicable only to `index_fund`/`enhanced_index`. The note is correct system behavior, not a false positive. The suspicion does not change outcomes or bypass blocks. Future evidence workers should calibrate false_positive_suspicion against known classification priority rules before flagging.

**Evidence**: snapshot.jsonl L4 `"note": "非指数基金不适用指数画像"`, L1 `"classified_fund_type": "qdii_fund"`; `docs/design.md` §6.5 classification priority: QDII before index.

## Scope Confirmation

- This review read generated public outputs at `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/`.
- Did not read PDF, cache, source-helper, downloader, or source-adapter internals.
- Did not run any `fund-analysis` commands, external web access, or code execution.
- Did not change any files other than this review artifact.

## Verdict Summary

| Criterion | Result |
|---|---|
| 1. Bounded scope: only 019172/2024 | PASS |
| 2. Follows Startup Packet next entry point | PASS |
| 3. Reads generated public files, not stdout-only | PASS |
| 4. Provenance interpretation correct | PASS |
| 5. Score/quality after eligible provenance | PASS |
| 6. Quality evidence correctly recorded | PASS |
| 7. Terminal classification matches accepted matrix | PASS |
| 8. false_positive_suspicion has public basis, not used to bypass | PASS |
| 9. Scratch reports ignored, no production changes | PASS |
| 10. git diff --check passes | PASS |

**Verdict: PASS_WITH_FINDINGS** (2 low findings, 0 material, 0 blocking)

All numeric values in the evidence artifact (status_counts, field_count, missing_field_rate, issue_count, P0/P1 failed fields) are consistent with generated public outputs and can be independently verified by any reviewer reading the same public files.
