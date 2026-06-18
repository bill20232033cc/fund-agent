# AgentDS evidence review: controlled live 2021-2025 annual-period evidence execution

## Verdict

**ACCEPT**

## Scope

- Gate: `controlled live 2021-2025 annual-period evidence execution gate`.
- Role: AgentDS independent evidence reviewer.
- Accepted plan: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`.
- Controller judgment: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-controller-judgment-20260611-225543.md`.
- Evidence under review: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-evidence-20260611.md`.
- Captured run artifacts: `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/` and `reports/quality-gate-runs/analyze-004393-2025-20260611T150410374542Z/quality_gate.json`.

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run by this reviewer.

## Findings

No material findings. All five focus questions verified as pass.

### Finding 1: observation — negative-action grep tool failure (no severity)

The evidence artifact notes that one attempted negative-action grep used unsupported ripgrep lookahead syntax and failed with a regex parse error. It was discarded and replaced with a simple pattern check that produced the same coverage. The resulting negative-action checklist is complete and all seven checks passed. This is a tool-hygiene observation, not a defect in evidence quality.

### Finding 2: no material findings (confirmed)

All five focus questions verified below. No command mismatch, source-policy violation, quality gate conflation, raw content promotion or scope violation found.

## Focus Question Verification

### 1. Does the evidence command exactly match the accepted E2 matrix?

**Pass.** The accepted E2 command is:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

The execution evidence records this exact command string. No flag, argument or ordering difference.

### 2. Does exit code 0 plus CLI summary support live annual-period product-path invocation for 004393 / 2021-2025?

**Pass.** Exit code is `0`. CLI summary emitted:

- `canonical_years: 2025,2024,2023,2022,2021`
- `available_years: 2025,2024,2023,2022,2021`
- `gap_years:` (empty)
- `fail_closed_years:` (empty)
- `cross_year_fact_count: 3`
- `fallback_year_count: 0`

Target year 2025 succeeded, all four optional prior years are available, and the cross-year fact path produced 3 facts. This is one bounded sample (`004393` only), as the accepted plan restricts iteration. The result supports the product-path invocation claim for this sample.

### 3. Does the year table support EID single-source and no fallback for all five years?

**Pass.** All five years (2025, 2024, 2023, 2022, 2021) show identical source provenance:

- `selected_source=eid`
- `source_mode=single_source_only`
- `fallback_enabled=false`
- `fallback_used=false`

The year table in the evidence artifact is derived from CLI summary metadata lines, not from raw cache/PDF introspection. Source and fallback fields are emitted by the CLI (not `not_emitted_by_cli`), so the table is directly verifiable against captured stdout.

### 4. Is quality_gate warn correctly separated from source evidence and not claimed as release/readiness?

**Pass.** The evidence artifact:

- Classifies quality gate status as "accepted evidence-run quality status."
- States explicitly: "This does not claim release/readiness pass, golden promotion or correctness acceptance."
- Lists quality gate warn as a residual: "Quality gate status is `warn`, not release/readiness pass."
- Negative-action checklist confirms: "No golden/readiness/release — pass."

The three quality gate issues (FQ2 turnover_rate coverage warn, FQ2F P1 field failure warn, FQ0 golden year_not_covered info) are all at warn or info severity under the explicit `--quality-gate-policy warn` override. The product default remains `block`. The evidence does not treat these warnings as release/readiness pass or source-evidence deficiency.

The `quality_gate_policy` override was confirmed effective: the controller judgment noted the repo path (`_multi_year_developer_overrides` → inner `FundAnalysisRequest` → `_resolve_analyze_contract` consuming `overrides.quality_gate_policy or "block"`), and the observed stderr indeed shows `quality_gate_status: warn`.

### 5. Did this gate avoid raw PDF/report-body promotion and unrelated residue handling?

**Pass.** The evidence artifact:

- Summarizes metadata only (command, HEAD, exit code, byte counts, CLI summary lines).
- The only raw excerpts are the five `source[...]` CLI summary lines and the stderr quality gate summary — both are CLI metadata, not report body or PDF content.
- Year table and cross-year fact summary are populated from emitted CLI summaries, with missing fields correctly recorded as `not_emitted_by_cli`.
- Negative-action checklist confirms: "No raw PDF/report body in durable review artifact — pass."
- No cleanup, archive, delete, move, stage, commit, push or PR action was taken.

## Accepted Residuals / Deferred Candidates

| Residual | Classification | Basis |
|---|---|---|
| Safe document identity fields `not_emitted_by_cli` for all five years | Accepted residual | Predicted by accepted plan; current CLI does not emit document identity in multi-year summary. Future source-identity enhancement gate. |
| Cross-year fact categories, target chapters, and `cross_period_comparison_missing` state `not_emitted_by_cli` | Accepted residual | Predicted by accepted plan; current CLI emits fact count but not categories/chapters. Future reporting/metadata gate. |
| Quality gate warn (3 issues, no block) | Accepted residual | Evidence-run override only; product default is `block`. Release/readiness remains separate. |
| Raw live-output directory `reports/live-evidence/` | Runtime residue | Not staged; handle via future artifact-disposition gate if needed. |
| Single primary sample only (`004393`) | Accepted constraint | Per accepted plan E3: no alternate sample without controller amendment. |
| Regex parse error in negative-action grep attempt | Tool observation | Discarded and replaced; no evidence gap. |

## Validation Performed

1. Cross-checked exit code `0` against `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/exit_code.txt` — confirmed.
2. Cross-checked stderr quality gate summary against `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/stderr.txt` — confirmed (`quality_gate_status: warn`, 3 issues).
3. Cross-checked CLI source summary lines against `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/stdout.md` lines 1–13 — all five `source[...]` lines confirmed, all show `eid` / `single_source_only` / `fallback_enabled=false` / `fallback_used=false`.
4. Cross-checked quality gate issue count and severities against `reports/quality-gate-runs/analyze-004393-2025-20260611T150410374542Z/quality_gate.json` — confirmed: 3 issues at warn/warn/info, `status: "warn"`.
5. Verified negative-action checklist completeness: all seven checks have explicit pass/fail and basis.
6. Verified E0/E1 preflight results present in evidence artifact: branch `feat/mvp-llm-incomplete-run-artifacts`, HEAD `928af83`, no tracked diff, CLI help shows all five required options.
7. Verified no Eastmoney/CNINFO/fund-company strings in captured stdout/stderr — confirmed by CLI source metadata (all `selected_source=eid`) and negative-action pattern check.
8. Verified the `quality_gate_policy warn` override was effective by confirming stderr output shows warn (not block) and quality_gate.json status is warn.

## No Additional Live Commands

This reviewer ran zero live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands. All verification was performed by reading the captured output files and cross-referencing against the evidence artifact and accepted plan.
