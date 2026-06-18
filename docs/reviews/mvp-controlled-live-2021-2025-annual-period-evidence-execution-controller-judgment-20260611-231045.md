# Controller judgment: controlled live 2021-2025 annual-period evidence execution

## Judgment

- Gate: `controlled live 2021-2025 annual-period evidence execution gate`.
- Classification: `heavy`.
- Verdict: `ACCEPT_WITH_RESIDUALS`.
- Decision time: `20260611-231045`.
- Accepted execution checkpoint: pending local commit.

This gate is accepted because the live command exactly matched the accepted E2 matrix, exited `0`, emitted a five-year `2021-2025` annual-period summary for `004393`, reported all five years as available, reported all five years as EID single-source with fallback disabled and unused, and kept quality gate `warn` separate from release/readiness or source-policy claims.

## Truth Inputs

- `AGENTS.md`.
- `docs/design.md`.
- `docs/current-startup-packet.md`.
- `docs/implementation-control.md`.
- Accepted plan: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`.
- Plan controller judgment: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-controller-judgment-20260611-225543.md`.
- Execution evidence: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-evidence-20260611.md`.
- DS evidence review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-review-ds-20260611.md`.
- MiMo evidence review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-review-mimo-20260611.md`.

## Accepted Evidence Facts

- Preflight HEAD was `928af83`.
- Preflight tracked diff was empty and `git diff --check` passed.
- E1 CLI help exited `0` and exposed `--target-year`, `--start-year`, `--valuation-state`, `--force-refresh` and `--quality-gate-policy`.
- E2 command was:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

- E2 exit code was `0`.
- Captured run directory is:

```text
reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/
```

- Captured byte counts:
  - `stdout.md`: `28563` bytes.
  - `stderr.txt`: `257` bytes.
- CLI emitted `canonical_years: 2025,2024,2023,2022,2021`.
- CLI emitted `available_years: 2025,2024,2023,2022,2021`.
- CLI emitted empty `gap_years` and empty `fail_closed_years`.
- CLI emitted `cross_year_fact_count: 3`.
- CLI emitted `fallback_year_count: 0`.
- CLI emitted these source summaries:

```text
source[2025]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2024]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2023]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2022]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2021]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
```

- Quality gate status was `warn` with three issues: two `turnover_rate` P1 coverage/traceability warnings and one info-level current-year golden coverage note.
- No reviewer ran additional live commands.

## Review Disposition

| Finding / question | Reviewer input | Controller disposition |
|---|---|---|
| Command matches accepted E2 matrix | DS `ACCEPT`; MiMo `ACCEPT` | `ACCEPTED` |
| Exit `0` plus CLI summary supports live product-path invocation for `004393 / 2021-2025` | DS `ACCEPT`; MiMo `ACCEPT` | `ACCEPTED` |
| Year table supports EID single-source and no fallback for all five years | DS `ACCEPT`; MiMo `ACCEPT` | `ACCEPTED` |
| Quality gate `warn` separated from source evidence and not claimed as release/readiness | DS `ACCEPT`; MiMo `ACCEPT` | `ACCEPTED_WITH_RESIDUAL` |
| Raw PDF/report body not promoted into durable review artifact | DS `ACCEPT`; MiMo `ACCEPT` | `ACCEPTED` |
| Negative-action grep lookahead parse error | DS observation | `ACCEPTED_AS_TOOL_HYGIENE_NOTE`; the failed grep was discarded and replaced by a simple pattern check |

## Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Evidence covers one bounded primary sample only: `004393` | Controller / future evidence owner | Accepted for this gate; alternate samples require controller amendment or separate matrix |
| Quality gate result is `warn`, not release/readiness pass | Release/quality owner | Release/readiness remains separate; do not claim ready |
| Safe document identity fields are not emitted by current CLI summary | Fund/source identity owner | Future source identity or CLI metadata enhancement gate |
| Cross-year fact categories, target chapter list and `cross_period_comparison_missing` state are not emitted by current CLI summary | Product/reporting owner | Future reporting/metadata enhancement gate |
| Raw live output remains under `reports/live-evidence/` and quality gate output remains under `reports/quality-gate-runs/` | Artifact owner / controller | Do not stage by default; route to future artifact-disposition gate if needed |

## Rejected Findings

| Finding | Disposition | Basis |
|---|---|---|
| Quality gate override ineffective | `REJECTED` for this execution | Direct observed evidence shows `quality_gate_status: warn` in stderr and `status: "warn"` in quality gate JSON. |
| Fallback or non-EID source used | `REJECTED` | Five CLI source summary lines all report `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`, and `fallback_year_count=0`. |
| Live evidence implies release/readiness pass | `REJECTED` | Evidence and both reviews keep quality/source evidence separate from release/readiness. |

## Validation

Controller validation run during this gate:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
git rev-parse --short HEAD
uv run fund-analysis analyze-annual-period --help
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Notes:

- The live command was run once and captured to `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/`.
- One attempted negative-action grep used unsupported ripgrep lookahead syntax and failed with a regex parse error; it was discarded and replaced by a simple pattern check.
- No provider/LLM/golden/readiness/release command was run.
- No source/test/runtime file was edited.

## Next Entry

Recommended next mainline:

1. `multi-year annual narrative writer/reporting planning gate`.

Deferred entries:

- `structured-data source identity extension gate`.
- `coverage measurement environment hygiene gate`.
- `runtime artifact disposition for reports/live-evidence and reports/quality-gate-runs`.
- `release-readiness residual acceptance evidence gate`.
