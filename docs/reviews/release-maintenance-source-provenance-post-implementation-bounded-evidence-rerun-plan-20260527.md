# Source Provenance Post-Implementation Bounded Evidence Rerun Plan

> Worker: Codex planning worker  
> Date: 2026-05-27  
> Gate: `source provenance post-implementation bounded evidence rerun plan/review gate`  
> Output summary artifact for evidence worker: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`

## Startup Packet Replay

| Item | State |
|---|---|
| Repository | `/Users/maomao/fund-agent` |
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate entering this worker | `source provenance post-implementation bounded evidence rerun plan/review gate` |
| Latest accepted implementation commit | `f88a3aa feat: persist annual report fallback failure category` |
| Current truth | `AGENTS.md`, `docs/design.md` current sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted implementation controller judgment |
| Accepted implementation judgment | `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-controller-judgment-20260527.md` |

This worker is planning-only. It must not run evidence commands, inspect private repository/source/cache internals, implement code, edit `docs/design.md` / `docs/implementation-control.md`, commit, push, or open a PR.

## Objective

Produce a bounded public evidence rerun plan for `110020` / `2024` and `017641` / `2024` after the accepted source provenance implementation. The evidence worker must classify each fund only from public CLI outputs:

- `fund-analysis extraction-snapshot`
- `fund-analysis extraction-score`
- `fund-analysis quality-gate`

No row may be promoted. Every disposition row in the evidence artifact must keep `promotion_disposition=not_promoted`.

## Cache / Force Refresh Decision

Use the accepted public CLI option `fund-analysis extraction-snapshot --force-refresh` for both funds.

Reason: the accepted implementation records `primary_failure_category` only when fallback succeeds after an eligible primary failure. Existing cached metadata may already have `fallback_used=true` but lack `primary_failure_category`; if reused, public provenance would remain `unknown_public_metadata_absent` and could mask the newly accepted metadata propagation behavior. The CLI exposes `--force-refresh`, so the evidence worker must refresh through that public path.

The evidence worker must not delete, rename, inspect, or manually patch any cache file. If `--force-refresh` still yields public metadata with `fallback_used=true` and missing `primary_failure_category`, classify that fund as `provenance_unknown_public_metadata_absent`; do not infer the original source failure from logs, exception text, repository internals, or cache contents.

## Bounded Corpus

| fund_code | report_year | Scope reason |
|---|---:|---|
| `110020` | `2024` | Post-implementation public provenance classification candidate |
| `017641` | `2024` | Post-implementation public provenance classification candidate |

No other fund may be added in this evidence gate.

## Run IDs and Output Paths

Use one isolated run directory per fund under ignored generated reports output. These generated outputs are evidence inputs only and must not become durable baseline, golden, fixture, or clean-denominator assets.

| fund_code | run_id | output_dir |
|---|---|---|
| `110020` | `source-provenance-rerun-110020-2024-20260527` | `reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527` |
| `017641` | `source-provenance-rerun-017641-2024-20260527` | `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527` |

Expected per-run public outputs:

- `snapshot.jsonl`
- `errors.jsonl`
- `summary.md`
- `score.json`
- `score.md`
- `golden_set.json`
- `quality_gate.json`
- `quality_gate.md`

Tracked summary artifact to write after running evidence:

- `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`

## Exact Evidence Commands

Run from `/Users/maomao/fund-agent`. Execute the two fund pipelines independently; stop per the stop conditions below.

### 110020 / 2024

```bash
uv run fund-analysis extraction-snapshot \
  --run-id source-provenance-rerun-110020-2024-20260527 \
  --report-year 2024 \
  --fund-code 110020 \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527 \
  --force-refresh
```

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/snapshot.jsonl \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527 \
  --errors-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/errors.jsonl
```

```bash
uv run fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527/score.json \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-110020-2024-20260527
```

### 017641 / 2024

```bash
uv run fund-analysis extraction-snapshot \
  --run-id source-provenance-rerun-017641-2024-20260527 \
  --report-year 2024 \
  --fund-code 017641 \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527 \
  --force-refresh
```

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/snapshot.jsonl \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527 \
  --errors-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/errors.jsonl
```

```bash
uv run fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.json \
  --output-dir reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527
```

## Public Evidence Fields to Read

For each fund, inspect only public output files from the run directory:

- `snapshot.jsonl`: one row per field, with public provenance fields.
- `errors.jsonl`: public snapshot failure accounting.
- `score.json`: public scoring output, including failed fund accounting when `--errors-path` is provided.
- `quality_gate.json` and `quality_gate.md`: public quality gate status and issues.

Required provenance fields in every successful snapshot row:

- `source_provenance_schema_version`
- `source_strategy`
- `resolved_source_name`
- `fallback_used`
- `primary_failure_category`
- `fallback_eligibility`
- `source_provenance_status`
- `source_provenance_reason`

All successful rows for the same fund must agree on the provenance tuple above. If rows disagree, classify `provenance_fail_closed` and record the exact public field mismatch in the summary artifact.

## Classification Rules

Classify one terminal state per fund, then add `promotion_disposition=not_promoted` for every row.

| Terminal state | Public evidence condition |
|---|---|
| `repository_run_failed` | `extraction-snapshot` exits non-zero, or `snapshot.jsonl` has no rows for the fund and `errors.jsonl` contains a public failure record for that fund. Record `error_type` and sanitized `error_message` from `errors.jsonl` only. Do not continue to score/gate if `snapshot.jsonl` is absent or empty for the fund. |
| `primary_succeeded_no_fallback` | Snapshot rows agree: `fallback_used=false`, `primary_failure_category=null`, `fallback_eligibility=not_applicable`, `source_provenance_status=not_applicable`, and `source_provenance_reason=primary_source_success_no_fallback` or another public no-fallback reason. Quality may still pass/warn/block separately, but provenance itself is complete enough to say primary succeeded without fallback. |
| `provenance_unknown_public_metadata_absent` | Snapshot rows agree: `fallback_used=true`, `primary_failure_category=null`, `fallback_eligibility=unknown_public_metadata_absent`, `source_provenance_status=incomplete`. This remains unknown even after public `--force-refresh`; do not promote and do not infer eligibility. |
| `provenance_fail_closed` | Snapshot rows expose `fallback_eligibility=fail_closed`, or `primary_failure_category` is one of `schema_drift`, `identity_mismatch`, `integrity_error`, or provenance fields are internally inconsistent. Treat this as fail-closed even if downstream score/gate exists. |
| `quality_blocked_after_provenance` | Provenance is `primary_succeeded_no_fallback` or eligible complete fallback, but `quality_gate.json` reports `status=block`, or quality-gate command exits non-zero after successful snapshot/score. Record quality issue IDs/statuses from public quality output. |
| `provenance_eligible_for_next_review` | Snapshot rows agree: `fallback_used=true`, `primary_failure_category` is `not_found` or `unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`; and quality gate status is `pass` or `warn`. This only means eligible for later review, not promotion. |
| `not_promoted` | Mandatory promotion disposition for every fund and every row in this gate, regardless of provenance or quality state. |

If `extraction-score` fails after a successful snapshot, classify based on snapshot provenance first, then mark quality as unavailable and do not attempt quality-gate. If the provenance state would otherwise be eligible, terminal state is `quality_blocked_after_provenance` because public quality evidence is not available.

## Evidence Summary Artifact Contract

The evidence worker must write `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md` with:

- Startup Packet replay.
- Exact command transcript summary: command, exit code, output paths. Do not paste noisy logs.
- One table per fund with:
  - `fund_code`
  - `report_year`
  - `run_id`
  - `snapshot_path`
  - `errors_path`
  - `score_path`
  - `quality_gate_path`
  - `fallback_used`
  - `primary_failure_category`
  - `fallback_eligibility`
  - `source_provenance_status`
  - `source_provenance_reason`
  - `quality_gate_status`
  - `terminal_state`
  - `promotion_disposition=not_promoted`
- Public provenance row-consistency check.
- Old-cache handling note confirming `--force-refresh` was used and no manual cache operation was performed.
- No durable baseline/golden/clean-denominator promotion statement.
- Residual risk section for any `repository_run_failed`, `provenance_unknown_public_metadata_absent`, `provenance_fail_closed`, or `quality_blocked_after_provenance` result.

## Review Matrix After Evidence

After the evidence summary artifact is written, send it for independent review:

| Reviewer | Scope |
|---|---|
| AgentMiMo | Verify public-only evidence discipline, command/run-id/path fidelity, old-cache handling, classification correctness, and no-promotion discipline. |
| AgentGLM | Verify terminal-state logic, provenance/quality separation, fail-closed handling, and forbidden-scope compliance. |

Controller may accept the evidence only after both reviews pass or after explicit controller judgment dispositions all findings. No promotion may occur in this gate even if both reviewers pass.

## Stop Conditions

Stop the evidence run and write the summary artifact with the terminal state reached when any condition applies:

- A snapshot command fails for a fund: classify that fund as `repository_run_failed`; do not use private source/cache inspection to diagnose.
- A successful snapshot has no rows for the fund and `errors.jsonl` has a public failure record: classify `repository_run_failed`.
- Public provenance fields are missing from snapshot rows: classify `provenance_unknown_public_metadata_absent` if fallback metadata is absent/unknown; classify `provenance_fail_closed` if fields are internally inconsistent.
- Public provenance exposes fail-closed category or `fallback_eligibility=fail_closed`: classify `provenance_fail_closed`; do not allow quality output to override it.
- Score or quality-gate fails after provenance is otherwise complete: classify `quality_blocked_after_provenance`.
- Any command path would require private `FundDocumentRepository`, source helper, PDF/cache inspection, manual cache deletion, code changes, or docs/design/control edits: stop and return to controller.

## Forbidden Scope

This gate forbids:

- Code changes.
- Source strategy changes.
- FQ0-FQ6 / quality gate semantic changes.
- Renderer changes.
- Default CLI behavior changes.
- Host / Agent / Dayu changes.
- Baseline, golden, fixture, clean-denominator, or corpus promotion.
- Manual cache deletion, cache inspection, private `FundDocumentRepository` calls, source helper calls, PDF inspection, or source/cache filesystem probing.
- Edits to `docs/design.md` or `docs/implementation-control.md`.
- Commit, push, PR, or branch operations.

## Acceptance Criteria for This Plan

- Commands use only public CLI paths and include exact run IDs and output paths.
- Both bounded fund/year pairs are covered and no additional fund is introduced.
- Public `--force-refresh` is required to avoid old metadata masking.
- Old metadata absence still has a conservative public classification.
- Classification uses only public snapshot provenance fields and public quality outputs.
- Every disposition remains `not_promoted`.
- Evidence summary path and MiMo/GLM review matrix are explicit.
