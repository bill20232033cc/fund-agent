# QDII Replacement Fallback 019172 Evidence

> Date: 2026-05-27
> Worker: AgentCodex evidence worker, not controller
> Gate: `QDII replacement fallback 019172 evidence gate`
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-20260527.md`
> Run id: `qdii-replacement-fallback-019172-2024-20260527`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement fallback 019172 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 019172 evidence gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement fallback 019172 evidence gate` |
| Latest accepted checkpoint | `dafc72f docs: accept qdii fallback 019172 evidence plan` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |
| Accepted plan | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-20260527.md` |
| Accepted plan judgment | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-plan-controller-judgment-20260527.md` |

This evidence run follows the Startup Packet next entry point. It is not a gate switch. This worker ran only the bounded public evidence sequence authorized by the accepted `019172` plan.

## 2. Candidate Identity And Pre-State

| Field | Value |
|---|---|
| `fund_code` | `019172` |
| `report_year` | `2024` |
| Fund name | `摩根纳斯达克100指数(QDII)人民币A` |
| App category | `海外股票类` |
| Classified fund type from generated public output | `qdii_fund` |
| Pre-run source provenance | `provenance_unknown` |
| Pre-run quality state | `quality_unknown` |
| Promotion disposition before run | `not_promoted` |

Preserved accepted prior states:

| fund_code | report_year | Preserved state |
|---|---:|---|
| `096001` | 2024 | Source-provenance eligible but quality `block`; terminal `quality_blocked_after_provenance`; `promotion_disposition=not_promoted`. Not rerun. |
| `040046` | 2024 | Source-provenance eligible but quality `block`; terminal `quality_blocked_after_provenance`; `promotion_disposition=not_promoted`. Not rerun. |

## 3. Public CLI Preflight

All preflight commands exited 0 and exposed the accepted public flags.

| Command | Exit | Required flags observed |
|---|---:|---|
| `uv run fund-analysis extraction-snapshot --help` | 0 | `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, `--force-refresh` |
| `uv run fund-analysis extraction-score --help` | 0 | `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path` |
| `uv run fund-analysis quality-gate --help` | 0 | `--score-path`, `--output-dir` |

Preflight terminal classification was not triggered; there was no CLI flag mismatch.

## 4. Commands Run

Only the accepted public commands below were run for `019172` / 2024.

```bash
uv run fund-analysis extraction-snapshot --run-id qdii-replacement-fallback-019172-2024-20260527 --report-year 2024 --fund-code 019172 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527 --force-refresh
```

Exit code: 0.

Generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/errors.jsonl` (0 lines)

```bash
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527 --errors-path reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/errors.jsonl
```

Exit code: 0.

Generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/golden_set.json`

```bash
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/score.json --output-dir reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527
```

Exit code: 0.

Generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/quality_gate.md`

## 5. Generated Public Provenance

Required files existed and were read after snapshot success:

| File | Exists | Use |
|---|---|---|
| `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/summary.md` | yes | public summary of source provenance and fund result |
| `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/snapshot.jsonl` | yes | exact public provenance tuple on generated records |

Public provenance tuple, read from generated files:

| Field | Value | Public source |
|---|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` | `snapshot.jsonl` |
| `source_strategy` | `primary_then_fallback` | `snapshot.jsonl` |
| `resolved_source_name` | `eastmoney` | `summary.md`, `snapshot.jsonl` |
| `fallback_used` | `true` | `summary.md`, `snapshot.jsonl` |
| `primary_failure_category` | `unavailable` | `snapshot.jsonl` |
| `fallback_eligibility` | `eligible` | `summary.md`, `snapshot.jsonl` |
| `source_provenance_status` | `complete` | `summary.md`, `snapshot.jsonl` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `summary.md`, `snapshot.jsonl` |

Interpretation before score/quality: provenance is eligible because fallback was used after `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, and public provenance status is `complete`. No public generated output showed `schema_drift`, `identity_mismatch`, or `integrity_error`; no fail-closed stop was triggered.

## 6. Score And Quality Status

Score summary:

| Field | Value |
|---|---|
| `field_count` | 14 |
| `fund_count` | 1 |
| `failed_fund_count` | 0 |
| `score_applicability_issue_count` | 0 |
| `status_counts` | `pass=8`, `fail=6` |
| `p0_status` | `fail` |
| `fund_scores[019172].status` | `fail` |
| `fund_scores[019172].p0_failed_fields` | `manager_strategy_text` |
| `fund_scores[019172].p1_failed_fields` | `turnover_rate`, `holdings_snapshot`, `share_change` |

Quality gate summary:

| Field | Value |
|---|---|
| `quality_gate_status` | `block` |
| `issue_count` | 9 |
| P0 block issues | `FQ2 manager_strategy_text`, `FQ3 manager_strategy_text`, `FQ2F 019172 P0 failed field manager_strategy_text` |
| P1 warn issues | `FQ2 turnover_rate`, `FQ2 holdings_snapshot`, `FQ2 share_change`, `FQ2F 019172 P1 failed fields` |
| FQ0 info | strict golden answer not configured; correctness oracle not run |
| FQ4 status | `block`; observed missing-field-rate `35.7%` > threshold `35.0%` |
| FQ5 status | `resolved`; App category `海外股票类` matched `qdii_fund`, preferred_lens resolved |

`manager_strategy_text` exact public status:

| Field | Value |
|---|---|
| priority | `P0` |
| score status | `fail` |
| coverage / traceability | `0.0% / 0.0%` |
| snapshot extraction mode | `missing` |
| value / anchor | `false / false` |
| public note | `§4 未披露可规则化抽取的投资策略/后市展望` |
| quality rules | `FQ2 block`, `FQ3 block`, `FQ2F block` |

FQ4 / structural quality status:

| Field | Value |
|---|---|
| missing_field_count / total_field_count | `5 / 14` |
| missing_field_rate | `35.7%` |
| FQ4 threshold | `35.0%` |
| FQ4 status | `block` |
| P0 pass case? | no. P0 failed on `manager_strategy_text`. |

## 7. Terminal Classification

Accepted plan matrix classification:

| Field | Value |
|---|---|
| Source provenance | eligible complete public fallback provenance |
| Quality status | `block` |
| Primary blocker | P0 `manager_strategy_text` coverage/traceability and evidence-anchor failure |
| Additional blocker | FQ4 missing-field-rate `35.7%` > `35.0%` |
| Terminal classification | `quality_blocked_after_provenance` |
| Promotion disposition | `not_promoted` |

`019172` is source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted.

## 8. False-Positive Suspicion

`false_positive_suspicion=true`.

Evidence basis from public generated outputs:

- `019172` is classified as `qdii_fund`, but `snapshot.jsonl` for `index_profile` says `非指数基金不适用指数画像` while the public classification basis includes QDII plus index/replication strategy text.
- `snapshot.jsonl` for `manager_strategy_text` says `§4 未披露可规则化抽取的投资策略/后市展望`; this may be a disclosure gap or extractor/template mismatch for this QDII index fund, but this evidence gate did not inspect PDF/cache/source-helper/downloader/source-adapter internals and did not diagnose root cause.

This suspicion does not change the accepted policy outcome. No code, extractor, taxonomy, source strategy, renderer, FQ0-FQ6, Service/CLI, golden, or baseline changes are authorized in this gate. Any diagnosis would require a separate controller-authorized gate.

## 9. Scope Confirmation

Confirmed:

- Did not run `analyze` or `checklist`.
- Did not run `096001`, `040046`, `017641`, or any later fallback candidate.
- Did not use external web.
- Did not directly read PDFs, cache files, source-helper internals, downloader internals, or source-adapter internals.
- Did not change production code, tests, README, `docs/design.md`, `docs/implementation-control.md`, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden files, or baseline fixtures.
- Generated `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/` only as ignored scratch output; it is ignored by `.gitignore` rule `reports/extraction-snapshots/`.

Pre-existing unrelated untracked files were present before writing this artifact and were not modified by this worker:

- `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
- `docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md`
- `docs/reviews/repo-review-20260526-231040.md`
- `docs/tmux-agent-memory-store.md`

## 10. Validation

`git diff --check` result after writing this artifact:

| Command | Exit |
|---|---:|
| `git diff --check` | 0 |

No commit was made.
