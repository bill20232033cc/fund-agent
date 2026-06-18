# Controller judgment: controlled live 2021-2025 annual-period evidence plan

## Judgment

- Gate: `controlled live 2021-2025 annual-period evidence planning gate`.
- Classification: `standard` for planning; future live execution remains a separate controlled-live gate.
- Verdict: `ACCEPT_WITH_NONBLOCKING_RESIDUALS`.
- Decision time: `20260611-225543`.
- Accepted planning checkpoint: pending local commit.

This planning gate is accepted because it defines a bounded future live command matrix, preserves current EID single-source annual-report policy, prohibits fallback/source expansion, separates quality gate behavior from source evidence, defines stop conditions and prevents raw PDF/report content from becoming durable review evidence.

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run in this planning gate.

## Truth Inputs

- `AGENTS.md`.
- `docs/design.md`.
- `docs/current-startup-packet.md`.
- `docs/implementation-control.md`.
- Accepted implementation input: `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md`.
- Plan: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`.
- DS review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-review-ds-20260611.md`.
- MiMo review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-review-mimo-20260611.md`.
- DS re-review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-rereview-ds-20260611.md`.
- MiMo re-review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-rereview-mimo-20260611.md`.

## Accepted Plan Facts

- Future execution gate is limited to one primary sample: `004393`, `target_year=2025`, `start_year=2021`.
- Future live command matrix is explicit:
  - E0: local git/status preflight.
  - E1: CLI help preflight.
  - E2: one controlled `fund-analysis analyze-annual-period` run.
  - E3: no alternate sample without controller amendment or separately accepted matrix.
- Future E2 command includes:
  - `--valuation-state unavailable` to avoid automatic valuation/thermometer lookup.
  - `--quality-gate-policy warn` as an evidence-run override only; product default remains `block`.
  - `--force-refresh` to avoid treating old cache hits as fresh live acquisition proof.
- Durable evidence must summarize metadata only and must not embed raw PDF text, full report body, downloaded document content or cache paths.
- If target year `2025` is unavailable, the execution worker must write a truncated evidence artifact and mark missing year rows `not_reached`.
- Year table and fact summary must come from emitted CLI stdout/stderr summaries when available; missing fields must be recorded as `not_emitted_by_cli`, not recovered by reading raw cache/PDF files or ad hoc introspection.

## Review Disposition

| Finding | Source | Controller disposition | Basis |
|---|---|---|---|
| Target-year unavailable path lacked artifact shape | DS review | `ACCEPTED_AND_FIXED` | Plan now requires a truncated evidence artifact with E0/E1, attempted E2 command, exit code, failure category, byte counts, negative-action checklist and `not_reached` missing rows. |
| E0/E1 preflight results were not integrated into evidence schema | DS review | `ACCEPTED_AND_FIXED` | Plan now requires E0/E1 results in the evidence artifact or a linked adjacent preflight artifact. |
| `--quality-gate-policy warn` needed inline clarification | DS review | `ACCEPTED_AND_FIXED` | Plan now states `warn` is evidence-only and product default remains `block`. |
| `--force-refresh` strategy missing | MiMo review | `ACCEPTED_AND_FIXED` | Plan now adds `--force-refresh` and constrains it to EID single-source behavior without fallback/source expansion. |
| Expected exit baseline missing | MiMo review | `ACCEPTED_AND_FIXED` | Plan now states exit `0` is expected when `004393 / 2025` is available from EID, while other exits are classified evidence rather than automatic plan failure. |
| Year-table parsing mechanism missing | MiMo review | `ACCEPTED_AND_FIXED` | Plan now limits extraction to emitted CLI stdout/stderr summaries and records absent fields as `not_emitted_by_cli`. |
| `--valuation-state unavailable` rationale missing | MiMo review | `ACCEPTED_AND_FIXED` | Plan now states the flag avoids automatic valuation/thermometer lookup during annual-report evidence testing. |
| `quality_gate_policy` not forwarded to inner analyze | MiMo review/re-review | `REJECTED_AS_BLOCKER / ACCEPTED_AS_LIVE_OBSERVATION_RESIDUAL` | Repo fact shows `analyze_multi_year_annual()` calls `_multi_year_developer_overrides(request)`, passes `developer_overrides` to inner `FundAnalysisRequest`, and `_resolve_analyze_contract()` consumes `overrides.quality_gate_policy or "block"`. The plan does not require a source fix before execution. Future live evidence must still record actual exit behavior and quality gate status. |

## Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| No live 2021-2025 annual-period evidence has been run | Controller / future evidence owner | Separate `controlled live 2021-2025 annual-period evidence execution gate`; requires explicit controlled-live opening before EID/network/PDF/analyze. |
| `quality_gate_policy warn` behavior remains unobserved in live annual-period run | Future evidence owner | Record actual exit behavior and quality gate status in execution artifact; source fix only if direct evidence shows override is ineffective. |
| Single primary sample only | Controller / future evidence owner | Accepted as bounded first evidence gate; alternate sample needs controller amendment or separate matrix. |
| Full cross-year narrative writer/reporting not implemented | Product/reporting owner | Deferred planning gate after live evidence or if product priority changes. |
| Structured-data source identity extension deferred | Fund/source identity owner | Separate implementation gate. |
| Coverage measurement environment residual | Test/quality owner | Separate coverage hygiene gate. |

## Validation

Passed:

```bash
git diff --check
```

Result: passed with no output.

Static review:

- DS initial review: `ACCEPT_WITH_FINDINGS`.
- DS re-review: `ACCEPT`.
- MiMo initial review: `ACCEPT_WITH_FINDINGS`.
- MiMo re-review: `ACCEPT_WITH_FINDINGS`, with no new blockers.

No live command was run by controller or reviewers.

## Next Entry

Recommended next mainline:

1. `controlled live 2021-2025 annual-period evidence execution gate` - requires separate controlled-live opening before running any EID/network/PDF/FDR/analyze command.

Deferred entries:

- `multi-year annual narrative writer/reporting planning gate`.
- `structured-data source identity extension gate`.
- `coverage measurement environment hygiene gate`.
- `release-readiness residual acceptance evidence gate`.
