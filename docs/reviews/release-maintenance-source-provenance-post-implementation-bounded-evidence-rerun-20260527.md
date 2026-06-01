# Source Provenance Post-Implementation Bounded Evidence Rerun

> Worker: Codex evidence worker  
> Date: 2026-05-27  
> Gate: `source provenance post-implementation bounded evidence rerun`  
> Repository: `/Users/maomao/fund-agent`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `source provenance post-implementation bounded evidence rerun` |
| Worker role | evidence worker, not controller |
| Truth sources replayed | `AGENTS.md`; `docs/design.md` current sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted rerun plan; accepted controller judgment |
| Accepted rerun plan | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-20260527.md` |
| Accepted controller judgment | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-controller-judgment-20260527.md` |
| Latest accepted checkpoint | `0d43ee4 docs: accept provenance rerun plan` |
| Bound corpus | `110020` / 2024 and `017641` / 2024 only |
| Forbidden scope observed | no code changes; no source strategy changes; no FQ0-FQ6 / quality semantics changes; no renderer/default CLI/Host/Agent/dayu changes; no baseline/golden/fixture/clean-denominator promotion; no private repository/source/cache/PDF inspection; no `docs/design.md` or `docs/implementation-control.md` edits; no commit/push/PR/branch operations |

## Command Summary

Commands were run from `/Users/maomao/fund-agent`.

| fund_code | command | exit_code | output paths |
|---|---|---:|---|
| `110020` | `uv run fund-analysis extraction-snapshot --run-id source-provenance-rerun-110020-2024-20260527 --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527 --force-refresh` | 0 | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/summary.md`; `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/errors.jsonl` |
| `110020` | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527 --errors-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/errors.jsonl` | 0 | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/score.json`; `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/score.md`; `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/golden_set.json` |
| `110020` | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/score.json --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527` | 0 | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/quality_gate.md` |
| `017641` | `uv run fund-analysis extraction-snapshot --run-id source-provenance-rerun-017641-2024-20260527 --report-year 2024 --fund-code 017641 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527 --force-refresh` | 0 | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/summary.md`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/errors.jsonl` |
| `017641` | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527 --errors-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/errors.jsonl` | 0 | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.json`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.md`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/golden_set.json` |
| `017641` | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.json --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527` | 0 | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/quality_gate.md` |

## Fund 110020 / 2024

| fund_code | report_year | run_id | snapshot_path | errors_path | score_path | quality_gate_path | fallback_used | primary_failure_category | fallback_eligibility | source_provenance_status | source_provenance_reason | quality_gate_status | terminal_state | promotion_disposition |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `110020` | 2024 | `source-provenance-rerun-110020-2024-20260527` | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/snapshot.jsonl` | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/errors.jsonl` | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/score.json` | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/quality_gate.json` | `true` | `unavailable` | `eligible` | `complete` | `fallback_used_primary_failure_category_eligible` | `warn` | `provenance_eligible_for_next_review` | `not_promoted` |

Public quality notes from `quality_gate.json` / `quality_gate.md`: status `warn`; issues are `FQ2` warn for `turnover_rate`, `FQ2F` warn for `110020` P1 field failure, and `FQ0` info because strict golden answer was not configured.

## Fund 017641 / 2024

| fund_code | report_year | run_id | snapshot_path | errors_path | score_path | quality_gate_path | fallback_used | primary_failure_category | fallback_eligibility | source_provenance_status | source_provenance_reason | quality_gate_status | terminal_state | promotion_disposition |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `017641` | 2024 | `source-provenance-rerun-017641-2024-20260527` | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/snapshot.jsonl` | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/errors.jsonl` | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.json` | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/quality_gate.json` | `true` | `unavailable` | `eligible` | `complete` | `fallback_used_primary_failure_category_eligible` | `block` | `quality_blocked_after_provenance` | `not_promoted` |

Public quality notes from `quality_gate.json` / `quality_gate.md`: status `block`; blocking issues are `FQ2` block for `manager_strategy_text`, `FQ3` block for `manager_strategy_text`, and `FQ2F` block for `017641` P0 field failure. Additional public issues are `FQ2` warn for `turnover_rate`, `FQ2` warn for `holdings_snapshot`, `FQ2F` warn for P1 fields, `FQ0` info because strict golden answer was not configured, and `FQ4` warn for high snapshot missing-field rate.

## Public Provenance Row-Consistency Check

| fund_code | report_year | snapshot rows | unique public provenance tuples | consistency |
|---|---:|---:|---:|---|
| `110020` | 2024 | 16 | 1 | pass |
| `017641` | 2024 | 16 | 1 | pass |

For both funds, all successful snapshot rows agree on the public tuple: `source_provenance_schema_version=repository_source_provenance.v1`, `source_strategy=primary_then_fallback`, `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, and `source_provenance_reason=fallback_used_primary_failure_category_eligible`.

Both public `errors.jsonl` files contained zero records. No repository failure classification was needed.

## Old-Cache Handling

Both accepted `extraction-snapshot` commands used the public `--force-refresh` option. I did not delete, rename, inspect, patch, or otherwise manually operate on cache, source, or PDF files. Classification used only public generated snapshot provenance fields and public score / quality outputs in the two run directories.

## Promotion Statement

No durable baseline, golden, fixture, corpus, clean-denominator, or promotion state was created or updated. Every disposition in this gate is `promotion_disposition=not_promoted`.

## Residual Risks

- `017641` has complete eligible fallback provenance, but public quality evidence blocks report usability; terminal state remains `quality_blocked_after_provenance`.
- `110020` is provenance-complete and quality `warn`, so it is only `provenance_eligible_for_next_review`; this is not a promotion and does not change any durable baseline, golden, fixture, corpus, or clean denominator.
