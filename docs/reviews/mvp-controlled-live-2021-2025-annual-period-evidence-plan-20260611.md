# Controlled live 2021-2025 annual-period evidence plan

## Scope

- Gate: `controlled live 2021-2025 annual-period evidence planning gate`.
- Classification: `standard` for planning. Future live execution is a separate controlled-live gate and may escalate to `heavy` if the accepted command matrix expands.
- Controller status: this is a planning artifact only. No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run while writing this plan.
- Worker-channel residual: the preferred planning-worker pane was not clean after `/clear`; controller wrote this bounded plan directly under phaseflow controller allowlist and must request independent MiMo + DS review before acceptance.

## Truth Inputs

- `AGENTS.md`: EID annual-report access must remain behind `FundDocumentRepository`; Eastmoney, fund-company/CDN and CNINFO fallback are not current production policy; live/external execution requires a reviewed gate.
- `docs/design.md`: multi-year annual analysis productization is current code fact; `fund-analysis analyze-annual-period` is the current deterministic product path; live 2021-2025 proof and full cross-year narrative writer/reporting remain future scope.
- `docs/current-startup-packet.md`: current active gate is this planning gate; next entry is a planning worker for a bounded controlled live 2021-2025 evidence matrix; no live commands until matrix and stop conditions are accepted.
- `docs/implementation-control.md`: accepted input is multi-year implementation checkpoint `61ab780`; residuals include no live annual-period evidence, no full narrative report, source identity extension deferred and coverage measurement residual.
- `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md`: implementation accepted with residuals and explicitly routes live observation to a separately authorized controlled evidence gate.

## Objective

Define a future execution gate that can directly test the accepted `analyze-annual-period` product path against live EID annual-report access for target period `2021-2025`, without changing code, source policy, fallback behavior, quality gate semantics, provider/LLM configuration, golden/readiness status or release state.

The future evidence gate must answer only these questions:

1. Can the accepted CLI product path be invoked for a controlled fund/year period with target year `2025` and start year `2021`?
2. Does current-year annual-report acquisition remain EID single-source through `FundDocumentRepository`, with no fallback/source expansion?
3. Are optional prior years represented as available/gap/fail-closed records according to the accepted annual evidence degradation policy?
4. Does the command produce enough bounded metadata to classify live product-path behavior without storing raw PDF text or treating the generated report as release/readiness evidence?

## Non-goals

- No implementation, fix, refactor, schema, cache, downloader, repository, provider or test changes in this planning gate.
- No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command in this planning gate.
- No source acquisition policy change; do not reintroduce Eastmoney, fund-company/CDN, CNINFO or generic fallback.
- No `--use-llm`, provider smoke, endpoint/DNS/curl/socket probe, retry-budget change or provider default change.
- No full cross-year narrative writer/reporting implementation.
- No structured-data source identity extension.
- No `.gitignore`, README, design-doc or root metadata changes in this planning gate.
- No cleanup, archive, delete, move, stage, commit, push, PR, mark-ready, merge or external issue/comment action unless separately authorized by a later gate.

## Future Execution Command Matrix

These commands are proposed for the future live execution gate only. They are not authorized to run by this planning artifact alone.

### E0: local status preflight

Purpose: prove the live run starts from the accepted workspace state and does not hide unrelated source changes.

Allowed commands:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
git rev-parse --short HEAD
```

Acceptance evidence:

- Branch and HEAD recorded.
- Existing untracked residue recorded as unrelated residue; not used as proof.
- No unexpected source/test/runtime diff beyond accepted checkpoint.

Stop condition:

- Stop before live execution if tracked source/test/runtime diffs exist outside the accepted post-`61ab780` control/review artifacts.

### E1: CLI interface preflight

Purpose: prove the accepted CLI surface still exposes the required command and options before live execution.

Allowed command:

```bash
uv run fund-analysis analyze-annual-period --help
```

Acceptance evidence:

- Help output includes `--target-year`, `--start-year`, `--valuation-state`, `--force-refresh` and `--quality-gate-policy`.

Stop condition:

- Stop if the command or required options are missing; classify as CLI surface regression, not live EID evidence.

### E2: controlled live annual-period run

Purpose: exercise the accepted product path with one bounded live sample. This command may access EID/network/PDF/FDR and must be run only inside the future controlled live execution gate.

Primary sample:

- `fund_code=004393`
- `target_year=2025`
- `start_year=2021`
- Rationale: `004393 / 2024` is one of the accepted small-golden live EID/FDR acquisition proof rows in `docs/design.md`. That proof does not prove 2025 or the multi-year path; it only gives a low-risk starting sample.

Allowed future command:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Execution-capture requirement for the future gate:

- Capture stdout and stderr to a local run directory under `reports/live-evidence/controlled-2021-2025-annual-period-<run_id>/`.
- The durable review artifact under `docs/reviews/` must summarize metadata only: command, cwd, HEAD, timestamps, exit code, stdout/stderr byte counts, source/provenance summary, available/gap/fail-closed years, quality gate status and negative-action checklist.
- Do not paste raw PDF text, full report body, raw downloaded document content or cache paths into the durable review artifact.
- `--quality-gate-policy warn` is an explicit evidence-run override. The product default remains `block`; this plan does not change default quality gate behavior.
- `--force-refresh` is included to avoid treating pre-existing cache hits as fresh live acquisition proof. It must still preserve EID single-source behavior and must not enable fallback or source expansion.
- `--valuation-state unavailable` is included to avoid automatic valuation/thermometer lookup while the evidence gate is testing annual-report acquisition and annual-period product behavior.

Expected baseline outcome:

- Expected result is exit `0` with a target-year report and a multi-year evidence summary if `004393 / 2025` is available from EID and no quality gate hard failure remains after the explicit `warn` override.
- Any other exit code is acceptable only as classified evidence under the rules below; it is not an automatic plan failure.

Evidence classification:

- Exit `0` with target-year report and multi-year summary: candidate pass, subject to provenance and negative-action checks.
- Exit `2` from quality gate: quality-gate behavior is not source evidence by itself. Classify separately; retain any already emitted source/provenance metadata if available.
- Exit `1` with target-year not found/unavailable: target-year required failure. Classify as live product-path blocker or live-data unavailable residual, not as prior-year degradation.
- Optional prior-year `not_found` / `unavailable`: acceptable year-level gap if target year succeeds.
- Optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error`: acceptable fail-closed year record if target year succeeds and no cross-year claim consumes that failed year.

Stop conditions:

- Stop immediately if logs or metadata show any Eastmoney, fund-company/CDN, CNINFO, fallback invocation or non-EID annual-report source.
- Stop immediately if any source/cache/PDF helper is called outside `FundDocumentRepository` boundaries.
- Stop if target-year identity differs from requested `fund_code=004393` or `report_year=2025`.
- Stop if the run requires `--use-llm`, provider configuration, endpoint/DNS/curl/socket probes, golden/readiness, release or PR state.
- Stop if output would require committing raw reports, PDFs, downloaded documents or cache files.

### E3: optional alternate sample policy

The future execution gate must not iterate across many funds by default. If the primary sample fails because target-year `2025` is not published/available, the execution worker must stop and report the classification. A second sample requires a controller amendment or a separately accepted execution matrix.

Reason: switching samples after observing live data can turn a bounded evidence gate into ad hoc data hunting and weakens provenance of the result.

When the primary sample stops before a full year table can be produced, the execution worker must still write a truncated evidence artifact with E0/E1 results, attempted E2 command, exit code, observed failure category, stdout/stderr byte counts, negative-action checklist and residual classification. Missing year rows must be marked `not_reached`, not inferred.

## Evidence Artifact Schema For Future Gate

The future live evidence artifact must include:

- `run_id`, local date/time, branch, HEAD and command.
- Explicit statement that the command was run only after the execution gate opened.
- E0/E1 preflight results, either in the same evidence artifact or a directly linked adjacent preflight artifact.
- Exit code and summarized stdout/stderr byte counts.
- Requested identity: fund code, target year and start year.
- Current-year classification: success, target-year required failure, quality-gate-only block, or unexpected failure.
- Year table with one row per 2021-2025 year:
  - `year`
  - `role`: target/current or optional prior
  - `record_status`: available/gap/failed_closed/not_reached
  - `failure_category` when applicable
  - `selected_source`
  - `source_mode`
  - `fallback_enabled`
  - `fallback_used`
  - safe document identity fields if emitted by the product path
- Cross-year fact summary:
  - eligible fact count
  - fact categories
  - chapters receiving facts
  - any removed/preserved `cross_period_comparison_missing` state if visible
- Extraction rule: populate the year table and fact summary from emitted CLI stdout/stderr summaries when available. If a field is not emitted by the CLI, record `not_emitted_by_cli` rather than reading raw cache/PDF files or adding ad hoc introspection in the live execution gate.
- Negative-action checklist:
  - no Eastmoney/fund-company/CNINFO
  - no fallback
  - no provider/LLM
  - no golden/readiness/release
  - no source/test/runtime changes
  - no raw PDF/report body persisted in review artifact
- Residual table:
  - accepted residual
  - blocker
  - deferred candidate
  - rejected finding

## Acceptance Criteria For This Planning Gate

This planning gate can be accepted only if reviewers and controller agree that:

- The plan preserves EID single-source policy and does not create a fallback/source-expansion path.
- The future live command matrix is explicit, bounded and reviewable.
- Stop conditions protect against scope drift into provider/LLM/golden/readiness/release or raw data capture.
- Evidence classification separates product invocation, current-year acquisition, optional prior-year degradation, quality gate status and report narrative completeness.
- The future execution gate still requires separate controlled-live opening before any live command is run.

## Review Handoff

MiMo and DS should review this plan for:

- Whether the command matrix is sufficiently bounded for a controlled live gate.
- Whether `--quality-gate-policy warn` is acceptable as evidence-only execution control without claiming product default behavior changed.
- Whether the primary sample `004393 / 2025 / 2021-2025` is a reasonable first live sample, given only 2024 small-golden proof is already accepted.
- Whether stop conditions sufficiently prevent fallback/source expansion and uncontrolled data hunting.
- Whether evidence schema is enough for a later controller judgment without storing raw report/PDF content.

## Next Entries

Recommended mainline after this plan is reviewed and accepted:

1. `controlled live 2021-2025 annual-period evidence execution gate` - separate controlled-live opening required before running EID/network/PDF/analyze.

Deferred entries:

- `multi-year annual narrative writer/reporting planning gate`.
- `structured-data source identity extension gate`.
- `coverage measurement environment hygiene gate`.
- `release-readiness residual acceptance evidence gate`.
