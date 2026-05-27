# QDII Replacement Fallback 040046 Evidence

> Date: 2026-05-27
> Worker: AgentCodex evidence worker, not controller
> Gate: `QDII replacement fallback 040046 evidence gate`
> Scope: bounded public evidence run for exactly `040046` / report_year `2024`
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md`
> Promotion disposition: `not_promoted`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement fallback 040046 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 040046 evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this task | `f05101f docs: accept qdii fallback 040046 evidence plan` |
| Accepted plan | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md` |
| Accepted plan controller judgment | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-controller-judgment-20260527.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet |

This evidence run follows the accepted next entry point. It is not a gate switch. This worker only ran the bounded public evidence commands for `040046` / 2024 and wrote this tracked summary.

## 2. Allowed Command Log

| Step | Command | Exit code | Result |
|---|---|---:|---|
| preflight | `uv run fund-analysis extraction-snapshot --help` | 0 | Required flags were present: `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, `--force-refresh`. |
| preflight | `uv run fund-analysis extraction-score --help` | 0 | Required flags were present: `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path`. |
| preflight | `uv run fund-analysis quality-gate --help` | 0 | Required flags were present: `--score-path`, `--output-dir`. |
| snapshot | `uv run fund-analysis extraction-snapshot --run-id qdii-replacement-fallback-040046-2024-20260527 --report-year 2024 --fund-code 040046 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527 --force-refresh` | 0 | Snapshot succeeded and generated public files. |
| score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527 --errors-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/errors.jsonl` | 0 | Score succeeded after provenance was confirmed eligible. |
| quality | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527` | 0 | Quality gate completed with `status=block`. |

No CLI flag mismatch was found. No command was adapted.

## 3. Generated Ignored Outputs

The run generated these scratch outputs under the accepted ignored output directory:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/errors.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/golden_set.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.md`

The provenance interpretation below uses generated public files, not stdout-only.

## 4. Public Source Provenance

Public provenance was read from:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`

| Field | Public value |
|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |

Interpretation:

- `primary_failure_category=unavailable` is an eligible fallback category under the accepted plan.
- `fallback_eligibility=eligible` and `source_provenance_status=complete` are publicly exposed.
- No public provenance showed `schema_drift`, `identity_mismatch`, or `integrity_error`.
- Source provenance status: `eligible`.

Because provenance was eligible, the score and quality commands were allowed to run.

## 5. Score And Quality Evidence

Score summary:

| Field | Value |
|---|---|
| `field_count` | 14 |
| `fund_count` | 1 |
| `failed_fund_count` | 0 |
| `score_applicability_issue_count` | 0 |
| `p0_status` | `pass` |
| `status_counts` | `pass=8`, `fail=6` |
| `correctness` | `unavailable` |
| `correctness reason` | strict golden answer JSON was not configured |

Fund quality from `score.md` / `score.json`:

| Field | Value |
|---|---|
| `fund_code` | `040046` |
| `fund_name` | `华安纳斯达克100ETF联接(QDII)A` |
| `app_category` | `海外股票类` |
| `classified_fund_type` | `qdii_fund` |
| `app_category_status` | `match` |
| `preferred_lens_status` | `resolved` |
| `preferred_lens_key` | `qdii_fund` |
| `missing_field_rate` | `35.7%` |
| `missing_p0_fields` | none |
| `missing_p1_fields` | `holder_structure`, `holdings_snapshot`, `share_change`, `turnover_rate` |

Quality gate:

| Field | Value |
|---|---|
| `quality_gate_status` | `block` |
| `issue_count` | 7 |
| `rule_result_count` | 1 |
| Blocking issue | `FQ4` block: missing field rate `35.7%` exceeds threshold `35.0%` |
| Rule result | `FQ5` info: template contract applicability `resolved` for `qdii_fund` |

P0 issues:

- No P0 field failed in `score.md` / `score.json`.
- `manager_strategy_text` is P0 and passed coverage/traceability.

P1 issues:

- `FQ2` warn: `turnover_rate` coverage `0.0%`, traceability `0.0%`.
- `FQ2` warn: `holder_structure` coverage `0.0%`, traceability `0.0%`.
- `FQ2` warn: `holdings_snapshot` coverage `0.0%`, traceability `0.0%`.
- `FQ2` warn: `share_change` coverage `0.0%`, traceability `0.0%`.
- `FQ2F` warn: fund `040046` has P1 failed fields `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`.

Informational issue:

- `FQ0` info: strict golden answer was not configured, so correctness oracle did not run.

## 6. `manager_strategy_text` Status

Public generated outputs show:

| Field | Value |
|---|---|
| priority | `P0` |
| score status | `pass` |
| coverage | `100.0%` |
| traceability | `100.0%` |
| snapshot `extraction_mode` | `direct` |
| snapshot `value_present` | `true` |
| snapshot `anchor_present` | `true` |
| snapshot `section_id` | `§4` |
| snapshot `row_id` | `strategy_summary` |
| issue severity | none |
| missing reason | not applicable |

`manager_strategy_text` is not the blocking field for this run.

## 7. False-Positive Suspicion And Required Next Action

`false_positive_suspicion=false`.

The public outputs identify a real quality block by current gate rules: FQ4 missing field rate `35.7%` is above the configured `35.0%` threshold. The public outputs do not provide a concrete basis to classify this as a false positive inside this evidence gate.

Required next action:

- Controller review should treat this row as public-provenance eligible but quality-blocked.
- Any diagnosis of QDII extraction gaps, field applicability, FQ4 threshold behavior, or replacement selection must be a separate future gate.

## 8. Terminal Classification

| Field | Value |
|---|---|
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| Replacement status | not accepted |
| Source-safe status | not promoted |
| Scoring-ready status | not promoted |
| Baseline status | not promoted |
| Golden status | not promoted |

`040046` / 2024 has eligible public source provenance, but the quality gate blocks on FQ4 missing-field-rate. It remains not promoted.

## 9. Scope Confirmations

- Ran evidence only for `040046` / report_year `2024`.
- Did not run `019172` or any other fallback candidate.
- Preserved the accepted `096001` state and did not rerun `096001`.
- Did not inspect PDFs.
- Did not inspect cache internals.
- Did not inspect source-helper outputs.
- Did not inspect downloader outputs.
- Did not inspect source-adapter internals.
- Did not use external web.
- Did not promote `040046` to source-safe, scoring-ready, baseline, golden, accepted replacement, or any equivalent durable corpus state.
- Did not edit code, tests, README, `docs/design.md`, or `docs/implementation-control.md`.
- Allowed tracked file change is limited to this evidence artifact.
