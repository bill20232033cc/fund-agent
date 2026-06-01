# QDII Replacement Fallback 021539 Evidence

> Date: 2026-05-27
> Worker: AgentCodex evidence worker, not controller
> Gate: `QDII replacement fallback 021539 evidence gate`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-controller-judgment-20260527.md`
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement fallback 021539 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 021539 evidence gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement fallback 021539 evidence gate` |
| Latest accepted checkpoint | `b575a49 docs: accept qdii fallback 021539 evidence plan` |

This evidence task follows the Startup Packet next entry point. It is not a gate switch. This worker ran only the accepted bounded public evidence sequence for `021539` / 2024 and did not act as controller.

`init-agents` was read before evidence execution. Tmux discovery was run before the public evidence sequence:

- `tmux-cli status` exit code `0`; current location reported `agents:claude.exe.2`.
- `tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command} #{pane_title}'` exit code `0`; visible panes included `agents:0.2 ... AgentCodex`, `agents:0.1 ... AgentGLM`, and `agents:0.3 ... AgentDS`.

## 2. Candidate Identity And Pre-State

| Field | Value |
|---|---|
| `fund_code` | `021539` |
| `report_year` | `2024` |
| Candidate name | `华安法国CAC40ETF发起式联接(QDII)A` |
| CSV category | `海外股票类` |
| Public run id | `qdii-replacement-fallback-021539-2024-20260527` |
| Source CSV | `docs/code_20260519.csv` |
| Pre-evidence source provenance | `provenance_unknown` |
| Pre-evidence quality state | `quality_unknown` |
| Promotion disposition | `not_promoted` |

Generated ignored output directory:

`reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527`

## 3. Preserved Prior Accepted States

This evidence gate did not rerun or reinterpret prior candidates.

| fund_code | report_year | Preserved state |
|---|---:|---|
| `096001` | 2024 | Source-provenance eligible; quality `block`; terminal `quality_blocked_after_provenance`; `promotion_disposition=not_promoted`. Accepted blockers include P0 `nav_benchmark_performance`, FQ4 missing-field-rate `42.9%`, and P1 gaps including `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`; `manager_strategy_text` passed. |
| `040046` | 2024 | Source-provenance eligible; quality `block`; terminal `quality_blocked_after_provenance`; `promotion_disposition=not_promoted`. P0 passed; FQ4 missing-field-rate `35.7%` blocked; P1 gaps include `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`; `manager_strategy_text` passed. |
| `019172` | 2024 | Source-provenance eligible; quality `block`; terminal `quality_blocked_after_provenance`; `promotion_disposition=not_promoted`. Accepted blockers include P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%`, FQ4 missing-field-rate `35.7%`, and P1 gaps `turnover_rate`, `holdings_snapshot`, `share_change`. |

## 4. Public CLI Preflight

| Command | Exit code | Flag check |
|---|---:|---|
| `uv run fund-analysis extraction-snapshot --help` | 0 | Required flags present: `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, `--force-refresh`. |
| `uv run fund-analysis extraction-score --help` | 0 | Required flags present: `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path`. |
| `uv run fund-analysis quality-gate --help` | 0 | Required flags present: `--score-path`, `--output-dir`. |

Preflight matched the accepted plan, so `cli_flag_mismatch_not_run` did not apply.

## 5. Commands Run

| Step | Command | Exit code | Generated public paths |
|---|---|---:|---|
| snapshot | `uv run fund-analysis extraction-snapshot --run-id qdii-replacement-fallback-021539-2024-20260527 --report-year 2024 --fund-code 021539 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527 --force-refresh` | 0 | `snapshot.jsonl`, `summary.md`, `errors.jsonl` |
| score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527 --errors-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/errors.jsonl` | 0 | `score.json`, `score.md`, `golden_set.json` |
| quality gate | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/score.json --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527` | 0 | `quality_gate.json`, `quality_gate.md` |

Generated snapshot files existed after snapshot:

| Path | State |
|---|---|
| `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/summary.md` | exists |
| `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl` | exists |
| `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/errors.jsonl` | exists; empty |

## 6. Public Provenance Reading

Provenance was read from generated public `summary.md` and `snapshot.jsonl`, not from stdout-only evidence and not from PDF/cache/source-helper/downloader/source-adapter internals.

`summary.md` exposed:

| fund_code | resolved_source_name | fallback_used | fallback_eligibility | source_provenance_status | source_provenance_reason |
|---|---|---|---|---|---|
| `021539` | `eastmoney` | `true` | `eligible` | `complete` | `fallback_used_primary_failure_category_eligible` |

`snapshot.jsonl` exposed the complete public provenance tuple:

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

Provenance interpretation before score / quality:

- No fail-closed category appeared in public provenance: no `schema_drift`, no `identity_mismatch`, no `integrity_error`.
- Fallback is eligible because `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, and public provenance is complete.
- The run therefore continued to `extraction-score` and `quality-gate`.

## 7. Score And Quality Status

Public score summary:

| Field | Value |
|---|---|
| `field_count` | 14 |
| `fund_count` | 1 |
| `failed_fund_count` | 0 |
| `score_applicability_issue_count` | 0 |
| `p0_status` | `pass` |
| `correctness` | `unavailable` because strict golden answer JSON was not provided |
| status counts | `pass=8`, `fail=6`, `watch=0` |

Fund score row:

| fund_code | p0_status | p1_status | status | p0_failed_fields | p1_failed_fields |
|---|---|---|---|---|---|
| `021539` | `pass` | `fail` | `fail` | none | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` |

Fund quality row:

| Field | Value |
|---|---|
| `classified_fund_type` | `qdii_fund` |
| `app_category_status` | `match` |
| `preferred_lens_status` | `resolved` |
| `preferred_lens_key` | `qdii_fund` |
| `missing_field_count` / `total_field_count` | `5 / 14` |
| `missing_field_rate` | `35.7%` |
| `missing_p0_fields` | none |
| `missing_p1_fields` | `holder_structure`, `holdings_snapshot`, `share_change`, `turnover_rate` |
| FQ5 / template applicability | resolved; 8 chapters resolved; ITEM_RULE evaluated |

Public quality-gate summary:

| Field | Value |
|---|---|
| `quality_gate_status` | `block` |
| `issue_count` | 7 |
| `rule_result_count` | 1 |

Quality issues:

| Rule | Severity | Field / fund | Status |
|---|---|---|---|
| FQ2 | warn | `turnover_rate` P1 | coverage `0.0%`, traceability `0.0%` |
| FQ2 | warn | `holder_structure` P1 | coverage `0.0%`, traceability `0.0%` |
| FQ2 | warn | `holdings_snapshot` P1 | coverage `0.0%`, traceability `0.0%` |
| FQ2 | warn | `share_change` P1 | coverage `0.0%`, traceability `0.0%` |
| FQ2F | warn | `021539` | P1 failed fields: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` |
| FQ0 | info | `021539` | strict golden answer not configured; correctness oracle not run |
| FQ4 | block | `021539` | missing-field-rate `35.7%` > threshold `35.0%` |

`manager_strategy_text` status:

| Field | Value |
|---|---|
| priority | `P0` |
| records | 1 |
| covered_records | 1 |
| traceable_records | 1 |
| coverage_rate | `100.0%` |
| traceability_rate | `100.0%` |
| status | `pass` |
| blocking issue | none |

P0 / FQ4 structural interpretation:

- P0 passed; there were no `p0_failed_fields` and no missing P0 fields.
- The quality block came from FQ4 / non-P0 structural missing-field-rate, not a P0 field failure.
- This matches the accepted plan matrix row: eligible provenance plus FQ4 or other non-P0 structural quality block plus P0 pass.

## 8. Terminal Classification

| Field | Value |
|---|---|
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| Classification basis | Public provenance eligible, score command exit `0`, quality-gate command exit `0`, quality status `block`, P0 pass, FQ4 missing-field-rate `35.7%` > threshold `35.0%`. |

Because `021539` quality-blocked after eligible provenance, automatic QDII probing stops. A new disposition gate is required before any further QDII probing, diagnosis, taxonomy / asset-class fitness decision, or coverage-blockage decision.

## 9. False-Positive Suspicion

| Field | Value |
|---|---|
| `false_positive_suspicion` | `true` |
| Evidence basis | `snapshot.jsonl` shows `classified_fund_type=qdii_fund` while classification basis also says it was an ETF feeder tracking the France CAC40 index; the `index_profile` record is missing with note `非指数基金不适用指数画像`. Public score / quality nevertheless treats P0 as pass and blocks on FQ4 / P1 structural missing fields. |
| Policy effect | None. This suspicion does not change terminal classification, does not authorize code or policy changes, and does not promote the candidate. |
| Required next action | Separate future diagnosis/fix gate if the controller chooses to investigate QDII index / feeder applicability behavior. |

## 10. Scope Confirmation

- No later candidate ran.
- Did not run `analyze` or `checklist`.
- Did not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, `019172`, or any later fallback candidate.
- Did not directly read PDF/cache/source-helper/downloader/source-adapter internals.
- Did not use external web.
- Did not change production code, tests, README, `docs/design.md`, `docs/implementation-control.md`, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, taxonomy, extractor, Host, Agent, Dayu, golden files, baseline fixtures, or durable corpus state.
- Generated `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/` outputs are ignored scratch and were not added as tracked fixtures.

## 11. Validation

`git diff --check` was run after writing this artifact and exited `0`.

The only intended tracked change from this worker is this evidence artifact.
