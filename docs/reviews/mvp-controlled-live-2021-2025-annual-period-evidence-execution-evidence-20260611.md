# Controlled live 2021-2025 annual-period evidence execution evidence

## Scope

- Gate: `controlled live 2021-2025 annual-period evidence execution gate`.
- Classification: `heavy` because this gate ran live EID/network/PDF/FDR/analyze through the accepted product path.
- Accepted plan: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`.
- Plan controller judgment: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-controller-judgment-20260611-225543.md`.
- Planning checkpoint: `4f8908b`.
- Control-sync checkpoint before execution: `928af83`.
- User opened this live gate after planning acceptance.

No source, test, runtime behavior, source policy, fallback policy, provider/LLM configuration, golden/readiness status, release state, PR state or external repository state was changed by this evidence run.

## E0: Local Status Preflight

Command matrix:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
git rev-parse --short HEAD
```

Observed result:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Branch state: ahead of origin by `122` commits at preflight time.
- HEAD: `928af83`.
- `git diff --name-only`: no output.
- `git diff --check`: passed with no output.
- Working tree tracked diff: none.
- Existing untracked residue remained visible and was not used as evidence. Notable current new residue from this gate after E2 is `reports/live-evidence/`.

## E1: CLI Interface Preflight

Command:

```bash
uv run fund-analysis analyze-annual-period --help
```

Exit code: `0`.

Required options present in help output:

- `--target-year`
- `--start-year`
- `--valuation-state`
- `--force-refresh`
- `--quality-gate-policy`

Classification: CLI surface preflight passed.

## E2: Controlled Live Annual-Period Run

Command:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Capture directory:

```text
reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/
```

Captured files:

- `stdout.md`: `28563` bytes.
- `stderr.txt`: `257` bytes.
- `exit_code.txt`: `0`.

Raw stdout contains generated report body plus the CLI multi-year evidence summary. Raw stderr contains quality gate summary. Neither raw file is copied into this durable review artifact.

### Command Result

| Field | Observed value |
|---|---|
| Exit code | `0` |
| Requested fund code | `004393` |
| Requested target year | `2025` |
| Requested start year | `2021` |
| Canonical years emitted by CLI | `2025,2024,2023,2022,2021` |
| Available years emitted by CLI | `2025,2024,2023,2022,2021` |
| Gap years emitted by CLI | empty |
| Fail-closed years emitted by CLI | empty |
| Cross-year fact count emitted by CLI | `3` |
| Fallback year count emitted by CLI | `0` |
| Quality gate status | `warn` |
| Quality gate issue count | `3` |

Classification: candidate pass for live product-path invocation and EID single-source annual-period evidence. Final acceptance depends on independent evidence review and controller judgment.

### Year Table

| Year | Role | Record status | Failure category | Selected source | Source mode | Fallback enabled | Fallback used | Safe document identity |
|---|---|---|---|---|---|---|---|---|
| 2025 | target/current | available | none | `eid` | `single_source_only` | `false` | `false` | not_emitted_by_cli |
| 2024 | optional prior | available | none | `eid` | `single_source_only` | `false` | `false` | not_emitted_by_cli |
| 2023 | optional prior | available | none | `eid` | `single_source_only` | `false` | `false` | not_emitted_by_cli |
| 2022 | optional prior | available | none | `eid` | `single_source_only` | `false` | `false` | not_emitted_by_cli |
| 2021 | optional prior | available | none | `eid` | `single_source_only` | `false` | `false` | not_emitted_by_cli |

Basis: the CLI emitted five source summary lines:

```text
source[2025]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2024]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2023]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2022]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2021]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
```

This excerpt is CLI summary metadata, not raw PDF text or full report body.

### Cross-Year Fact Summary

| Field | Observed value |
|---|---|
| Eligible fact count | `3` |
| Fact categories | not_emitted_by_cli |
| Chapters receiving facts | not_emitted_by_cli |
| Removed/preserved `cross_period_comparison_missing` state | not_emitted_by_cli |

The execution plan required missing fields to be recorded as `not_emitted_by_cli` rather than inferred from raw cache/PDF files or ad hoc introspection.

### Quality Gate Summary

`stderr.txt` emitted:

```text
quality_gate_status: warn
quality_gate_issues: 3
quality_gate_json: reports/quality-gate-runs/analyze-004393-2025-20260611T150410374542Z/quality_gate.json
quality_gate_md: reports/quality-gate-runs/analyze-004393-2025-20260611T150410374542Z/quality_gate.md
```

Quality gate JSON summary:

| Severity | Message |
|---|---|
| warn | P1 field `turnover_rate` coverage/traceability did not meet threshold; report should disclose data insufficiency |
| warn | Fund `004393` has P1 field failure: `turnover_rate` |
| info | Fund `004393` has strict golden answer records, but current report year is not covered; correctness oracle did not use other-year golden answer |

Classification: accepted evidence-run quality status. This does not claim release/readiness pass, golden promotion or correctness acceptance.

## Negative-Action Checklist

| Check | Result | Basis |
|---|---|---|
| No Eastmoney/fund-company/CNINFO | pass | simple pattern check found no `Eastmoney`, `eastmoney`, `CNINFO`, `cninfo`, or `基金公司` in captured stdout/stderr |
| No fallback | pass | CLI summary emitted `fallback_enabled=false` and `fallback_used=false` for all five years; `fallback_year_count=0` |
| EID single-source only | pass | CLI summary emitted `selected_source=eid` and `source_mode=single_source_only` for all five years |
| No provider/LLM | pass | command did not include `--use-llm`; no provider/LLM command was run |
| No golden/readiness/release | pass | only quality gate warn artifacts were produced by the accepted product path; no golden/readiness/release command was run |
| No source/test/runtime changes | pass | preflight tracked diff was empty; no source/test/runtime edit was made |
| No raw PDF/report body in durable review artifact | pass | this artifact includes only metadata summaries and short CLI summary lines |

Note: one attempted negative-action grep used unsupported ripgrep lookahead syntax and failed with regex parse error. It was discarded and replaced by the simple pattern check summarized above.

## Residuals

| Residual | Classification | Next handling |
|---|---|---|
| Safe document identity fields are not emitted by current CLI summary | accepted residual | Future source identity / CLI metadata enhancement gate if needed |
| Cross-year fact categories and target chapter list are not emitted by current CLI summary | accepted residual | Future reporting/metadata enhancement gate; not a blocker for source-policy evidence |
| Quality gate status is `warn`, not release/readiness pass | accepted residual | Release/readiness remains separate and not claimed here |
| Raw live-output directory remains under `reports/live-evidence/` | runtime residue | Do not stage by default; handle only through a future artifact-disposition gate if needed |

## Review Request

Implementation/evidence review should verify:

- The observed command exactly matches the accepted E2 matrix.
- The result supports live product-path invocation for `004393 / 2021-2025`.
- The year table is derived only from emitted CLI summary metadata.
- The evidence supports EID single-source and no fallback for all five years.
- The quality gate `warn` status is correctly separated from source evidence and does not imply release/readiness pass.
- No raw report/PDF content was promoted into this durable artifact.
