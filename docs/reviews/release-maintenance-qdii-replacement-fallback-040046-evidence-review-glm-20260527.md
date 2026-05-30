# Evidence Review: QDII Replacement Fallback 040046

> Date: 2026-05-27
> Reviewer: AgentGLM, independent evidence reviewer, not controller
> Gate: `QDII replacement fallback 040046 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-controller-judgment-20260527.md`
> Review artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-review-glm-20260527.md`

## Scope

- Mode: evidence review only
- Evidence artifact reviewed: section-by-section
- Public generated outputs verified: `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/` (summary.md, snapshot.jsonl, score.json, score.md, quality_gate.json, quality_gate.md)
- Git status and diff checked
- Excluded: PDF/cache/source-helper/downloader/source-adapter internals, code inspection, external web

## Verdict: PASS_WITH_FINDINGS

One non-blocking finding on terminal-state matrix coverage gap. No material misclassification, no boundary violation, no promotion claim, and all public outputs support the evidence artifact's claims.

## Review Questions

### RQ1: Did the worker follow accepted scope?

**PASS.** The evidence artifact ran only `040046` / `2024`. Commands in Section 2 match the accepted plan Section 5 exactly: same run-id, same flags, same output-dir convention, same source-csv. No `096001` rerun. No `019172` run. No promotion language. Section 9 confirms all exclusions. No contradiction found.

### RQ2: Are command outcomes, generated paths, and git status claims credible?

**PASS.** Filesystem verification confirms all 8 declared generated paths exist under `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/`:

| Declared file | Exists | Size |
|---|---|---|
| summary.md | yes | 1997 bytes |
| snapshot.jsonl | yes | 24556 bytes |
| errors.jsonl | yes | 0 bytes |
| score.json | yes | 10458 bytes |
| score.md | yes | 4259 bytes |
| golden_set.json | yes | 1612 bytes |
| quality_gate.json | yes | 6590 bytes |
| quality_gate.md | yes | 2118 bytes |

Git status shows only untracked docs files. No staged changes, no code modifications. `git diff --check` exits 0. Claims are credible.

### RQ3: Is provenance recorded correctly and eligible?

**PASS.** Cross-verified against snapshot.jsonl and summary.md:

| Evidence claim | snapshot.jsonl value | summary.md value | Match |
|---|---|---|---|
| `source_provenance_schema_version` = `repository_source_provenance.v1` | confirmed on every record | not in summary table | yes |
| `source_strategy` = `primary_then_fallback` | confirmed | not in summary table | yes |
| `resolved_source_name` = `eastmoney` | confirmed | confirmed | yes |
| `fallback_used` = `true` | confirmed | confirmed | yes |
| `primary_failure_category` = `unavailable` | confirmed | not in summary table | yes |
| `fallback_eligibility` = `eligible` | confirmed | confirmed | yes |
| `source_provenance_status` = `complete` | confirmed | confirmed | yes |
| `source_provenance_reason` = `fallback_used_primary_failure_category_eligible` | confirmed | confirmed | yes |

`primary_failure_category=unavailable` is an eligible fallback category under the plan Section 7. No `schema_drift`, `identity_mismatch`, or `integrity_error` appears in any snapshot record. Provenance was correctly interpreted before score/quality (Section 4 precedes Section 5).

### RQ4: Are score and quality summaries accurate?

**PASS.** Cross-verified against score.json, score.md, quality_gate.json, quality_gate.md:

| Evidence claim | Public output value | Match |
|---|---|---|
| `field_count` = 14 | score.json `field_count`: 14, score.md lists 14 field rows | yes |
| `fund_count` = 1 | score.json `fund_count`: 1 | yes |
| `failed_fund_count` = 0 | score.md failed_funds table empty | yes |
| `score_applicability_issue_count` = 0 | score.md applicability table empty | yes |
| `p0_status` = `pass` | score.json `p0_status`: `pass` | yes |
| `status_counts` pass=8, fail=6 | score.md: 8 pass + 6 fail | yes |
| `correctness` = `unavailable` | score.json reason: golden answer not provided | yes |
| `quality_gate_status` = `block` | quality_gate.json `status`: `block` | yes |
| `issue_count` = 7 | quality_gate.json: 7 issues (4xFQ2 warn + 1xFQ2F warn + 1xFQ0 info + 1xFQ4 block) | yes |
| `rule_result_count` = 1 | quality_gate.json: 1 rule_result (FQ5 info) | yes |
| FQ4 block: 35.7% > 35.0% | quality_gate.json FQ4: observed=0.3571428571, threshold=0.35 | yes |
| No P0 field failed | score.md: all P0 fields = pass | yes |
| P1 failed: turnover_rate, holder_structure, holdings_snapshot, share_change | score.json `p1_failed_fields`: matching list | yes |
| FQ0 info: golden not configured | quality_gate.json FQ0 reason: `not_configured` | yes |
| `manager_strategy_text`: P0, 100% coverage, 100% traceability, pass | snapshot.jsonl: direct, value_present=true, anchor_present=true, section_id=§4, row_id=strategy_summary; score.json: coverage=1.0, trace=1.0, status=pass | yes |

All claims match public outputs. No discrepancy found.

### RQ5: Is terminal_classification=quality_blocked_after_provenance correct?

**PASS_WITH_FINDING (non-blocking).** The classification is defensible and conservative, but the plan's terminal-state matrix does not explicitly cover the scenario where:

- Provenance is eligible
- P0 fields all pass
- Quality gate blocks on FQ4 structural rule (missing-field-rate) rather than a specific P0 field

The matrix rows for provenance-eligible quality outcomes are:

1. P0 block on `manager_strategy_text` → quality_blocked_after_provenance or disclosure_data_gap_not_baseline_ready
2. P0 block on another field → quality_blocked_after_provenance
3. Quality `warn` with P1 residuals only → candidate_public_evidence_warn_not_promoted
4. Quality `pass` → candidate_public_evidence_pass_not_promoted

The actual condition (eligible provenance + FQ4 block + P0 pass) falls between rows 2 and 3. The evidence worker chose `quality_blocked_after_provenance`, which is the most conservative option from the available matrix entries. This is correct in substance because:

- Provenance is eligible
- Quality gate returned `block`
- Promotion disposition remains `not_promoted`
- The FQ4 block is real and evidenced

This is a matrix coverage gap, not a misclassification. The controller may want to add an explicit FQ4-block row to the terminal-state matrix in future plans. Not blocking because promotion disposition is correct and the classification does not overstate the evidence quality.

### RQ6: Promotion disposition confirmation

**PASS.** `promotion_disposition=not_promoted` is recorded in Section 8. No claim of source-safe, scoring-ready, baseline, golden, or accepted replacement appears anywhere in the artifact. Section 9 explicitly states: "Did not promote `040046` to source-safe, scoring-ready, baseline, golden, accepted replacement, or any equivalent durable corpus state."

### RQ7: Generated reports stay ignored/untracked

**PASS.** Git status confirms all `reports/extraction-snapshots/` files are untracked (not staged, not committed). The only tracked artifact is the evidence doc itself, which is also untracked. No generated output was committed or staged.

### RQ8: No boundary violations or missing required fields

**PASS.** Checked against plan Section 11 expected fields:

| Required field | Present in evidence artifact |
|---|---|
| Startup Packet replay | Section 1 |
| Follows accepted next entry point, not gate switch | Section 1 statement |
| Candidate identity (040046, 2024, run-id, csv) | Section 1, 2 |
| Preflight help results and flag verification | Section 2 |
| Exact commands and exit codes | Section 2 |
| Generated ignored paths | Section 3 |
| Public provenance tuple from summary.md/snapshot.jsonl | Section 4 |
| Provenance stop-check before quality | Section 4 → Section 5 ordering |
| Quality status | Section 5 |
| P0 and P1 issues | Section 5 |
| manager_strategy_text status with evidence anchor | Section 6 |
| False-positive suspicion and next action | Section 7 |
| Terminal classification | Section 8 |
| promotion_disposition=not_promoted | Section 8 |
| No 019172 or other fallback run | Section 9 |
| No PDF/cache/source-helper/external web inspection | Section 9 |
| No code/test/design/control-doc changes | Section 9 |
| git diff --check result | Confirmed: exit 0 |

No required field is missing. No boundary violation found.

## Findings

### F1-低-terminal_state_matrix缺少FQ4结构阻断行

- **入口/函数**: Evidence artifact Section 8, terminal classification
- **文件**: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md`
- **输入场景**: Provenance eligible, P0 fields pass, quality gate blocks on FQ4 missing-field-rate (35.7% > 35.0%)
- **实际分支**: Worker chose `quality_blocked_after_provenance` from the plan's terminal-state matrix
- **预期行为**: Plan matrix should explicitly cover FQ4 structural block with P0 pass
- **实际行为**: Matrix has P0-block and P1-warn rows but no FQ4-structural-block row
- **直接证据**: Plan Section 9 terminal-state matrix rows list P0 block and P1 warn scenarios but not FQ4 aggregate block when P0 passes
- **影响**: None on promotion outcome. Classification chosen is conservative and correct in substance.
- **建议改法和验证点**: Future plans should add an explicit row: "Provenance eligible, FQ4 block on missing-field-rate, P0 pass" → `quality_blocked_after_provenance`
- **修复风险（低）**: Documentation-only change to plan template
- **严重程度（低）**: Matrix coverage gap, no material misclassification

## Open Questions

- 无

## Residual Risks

- The FQ4 threshold (35.0%) is narrow: 040046's 35.7% misses by 0.7pp. Whether this reflects genuine data quality issues or QDII-specific field applicability gaps (e.g., ETF-linked funds may legitimately lack holder_structure/holdings_snapshot) is a question for a future diagnosis gate, not this evidence review.
- The evidence artifact correctly flags this as requiring future controller action and does not diagnose the root cause within the evidence gate.

## Reviewer Self-Check

- Evidence artifact reviewed section-by-section against public generated outputs: done
- All 8 review questions answered with explicit verdicts: done
- Terminal classification correctness assessed explicitly: done (F1 finding, non-blocking)
- Provenance verified against both snapshot.jsonl and summary.md: done
- Quality claims verified against score.json, score.md, quality_gate.json, quality_gate.md: done
- Boundary violations checked via git status and git diff --check: done
- No code was read or modified during this review: confirmed
- Output path matches required pattern: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-review-glm-20260527.md`
