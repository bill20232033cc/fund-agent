# Source Provenance Bounded Evidence Classification

> Date: 2026-05-27
> Role: evidence worker
> Gate: `source provenance bounded evidence run`
> Summary artifact: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`

## Startup Packet Replay

| Item | Replayed state |
|---|---|
| Rule truth | `AGENTS.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |
| Current phase | `release maintenance` |
| Current gate | `source provenance bounded evidence classification plan accepted locally` |
| Worker scope | Run only accepted public CLI evidence commands for `110020` / 2024 and `017641` / 2024; classify only from public snapshot provenance fields plus public quality output |
| Latest accepted checkpoint from handoff | `26e61f7 docs: accept source provenance evidence plan` |
| Promotion constraint | No baseline, golden answer, strict golden, curated fixture, or clean denominator promotion in this gate |

Allowed terminal-state vocabulary for this gate is exactly:

- `repository_run_failed`
- `primary_succeeded_no_fallback`
- `provenance_unknown_public_metadata_absent`
- `provenance_fail_closed`
- `quality_blocked_after_provenance`
- `provenance_eligible_for_next_review`

Every row also receives final `promotion_disposition=not_promoted`.

## Command Results

| # | Command | Exit code |
|---:|---|---:|
| 1 | `uv run fund-analysis extraction-snapshot --run-id source-provenance-bounded-110020-2024-20260527 --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527` | 0 |
| 2 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/source-provenance-bounded-110020-2024-20260527` | 0 |
| 3 | `uv run fund-analysis quality-gate --score-path reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/score.json --output-dir reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527` | 0 |
| 4 | `uv run fund-analysis extraction-snapshot --run-id source-provenance-bounded-017641-2024-20260527 --report-year 2024 --fund-code 017641 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527` | 0 |
| 5 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/source-provenance-bounded-017641-2024-20260527` | 0 |
| 6 | `uv run fund-analysis quality-gate --score-path reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/score.json --output-dir reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527` | 0 |

## Per-Fund Evidence

### `110020` / 2024

| Field | Public evidence |
|---|---|
| Snapshot path | `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/snapshot.jsonl` |
| Snapshot summary path | `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/summary.md` |
| Snapshot errors path | `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/errors.jsonl` |
| Score path | `reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/score.json` |
| Score summary path | `reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/score.md` |
| Golden set output path | `reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/golden_set.json` |
| Quality gate path | `reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527/quality_gate.json` |
| Quality gate summary path | `reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527/quality_gate.md` |
| Snapshot rows inspected | 16 |
| `fallback_used` | `true` |
| `primary_failure_category` | `null` |
| `fallback_eligibility` | `unknown_public_metadata_absent` |
| `source_provenance_status` | `incomplete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_absent` |
| `source_provenance_schema_version` | `repository_source_provenance.v1` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| Quality status | `warn` |
| Quality issue count | 3 |
| Quality issue summary | `FQ2/warn turnover_rate`; `FQ2F/warn 110020`; `FQ0/info strict golden not configured` |
| Terminal state | `provenance_unknown_public_metadata_absent` |
| `promotion_disposition` | `not_promoted` |

Classification basis: public snapshot provenance shows fallback was used, but public metadata does not expose a primary failure category and marks fallback eligibility as `unknown_public_metadata_absent`. The row therefore stops at `provenance_unknown_public_metadata_absent`; the non-blocking `warn` quality result does not prove fallback eligibility.

### `017641` / 2024

| Field | Public evidence |
|---|---|
| Snapshot path | `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/snapshot.jsonl` |
| Snapshot summary path | `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/summary.md` |
| Snapshot errors path | `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/errors.jsonl` |
| Score path | `reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/score.json` |
| Score summary path | `reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/score.md` |
| Golden set output path | `reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/golden_set.json` |
| Quality gate path | `reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527/quality_gate.json` |
| Quality gate summary path | `reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527/quality_gate.md` |
| Snapshot rows inspected | 16 |
| `fallback_used` | `true` |
| `primary_failure_category` | `null` |
| `fallback_eligibility` | `unknown_public_metadata_absent` |
| `source_provenance_status` | `incomplete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_absent` |
| `source_provenance_schema_version` | `repository_source_provenance.v1` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| Quality status | `block` |
| Quality issue count | 8 |
| Quality issue summary | `FQ2/block manager_strategy_text`; `FQ3/block manager_strategy_text`; `FQ2/warn turnover_rate`; `FQ2/warn holdings_snapshot`; `FQ2F/block 017641`; `FQ2F/warn 017641`; `FQ0/info strict golden not configured`; `FQ4/warn high missing-field rate` |
| Terminal state | `provenance_unknown_public_metadata_absent` |
| `promotion_disposition` | `not_promoted` |

Classification basis: public snapshot provenance shows fallback was used, but public metadata does not expose a primary failure category and marks fallback eligibility as `unknown_public_metadata_absent`. The row therefore stops at `provenance_unknown_public_metadata_absent` before any `quality_blocked_after_provenance` classification can apply. The quality gate is `block`, but public provenance did not first prove fallback eligibility.

## Denominator Decision

| Fund code | Year | Terminal state | Quality status | Clean denominator decision | Promotion disposition |
|---|---:|---|---|---|---|
| `110020` | 2024 | `provenance_unknown_public_metadata_absent` | `warn` | Excluded. Public provenance does not prove eligible fallback because `primary_failure_category` is absent and `fallback_eligibility=unknown_public_metadata_absent`. | `not_promoted` |
| `017641` | 2024 | `provenance_unknown_public_metadata_absent` | `block` | Excluded. Public provenance does not prove eligible fallback; quality output also blocks report usability, but terminal provenance classification is already unknown-public-metadata-absent. | `not_promoted` |

## Generated-Output Hygiene

The bounded CLI commands wrote generated outputs only under these ignored report directories:

- `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/`
- `reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/`
- `reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527/`
- `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/`
- `reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/`
- `reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527/`

`git status --short` for those six generated output directories returned no tracked or untracked entries, consistent with ignored generated-output handling. The only intended tracked artifact from this worker scope is this summary file.

No source code, tests, `docs/design.md`, `docs/implementation-control.md`, renderer, source strategy, `FundDocumentRepository`, Host/Agent/dayu, baseline, golden, fixture, or clean-denominator state was changed.

## Evidence Boundary Statement

Classification used only public generated outputs from the six accepted CLI commands: snapshot JSONL, score JSON/Markdown, and quality gate JSON/Markdown under the accepted output directories. It did not inspect or call `FundDocumentRepository`, source helpers, downloader internals, PDF/cache internals, private source exceptions, web/search, or non-public repository metadata.

Successful extraction, populated `snapshot.jsonl`, populated `score.json`, and quality-gate completion were not used as fallback eligibility evidence. Fallback eligibility would require public provenance fields showing `fallback_used=true`, eligible `primary_failure_category` in `not_found` / `unavailable`, and `fallback_eligibility=eligible`; neither bounded row met that public-evidence requirement.
