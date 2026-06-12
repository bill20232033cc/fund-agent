# Controlled Live Annual-period Narrative Evidence Plan

Date: 2026-06-12

Role: controller-authored plan artifact

Gate: `Controlled live annual-period narrative evidence gate`

Classification: `standard`

Accepted input:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-release-readiness-ready-state-disposition-controller-judgment-20260612.md`
- Checkpoint `22a5e2a`
- Control-sync checkpoint `f8c6300`
- User live authorization on 2026-06-12

## 1. Objective

Run one controlled live evidence sample for the accepted `fund-analysis analyze-annual-period` product path after annual-period narrative/reporting implementation was accepted.

This gate asks only:

1. Can the current CLI produce the formal annual-period narrative report body for `004393 / 2021-2025` through live EID annual-report access?
2. Does the emitted CLI metadata still show EID single-source/no-fallback for each available year?
3. Does the generated annual-period output include the expected narrative/reporting sections, without treating the full report body as release/readiness evidence?

## 2. Non-goals

This gate does not authorize:

- source, tests, runtime, README, design, lockfile, `.gitignore` or config changes
- source acquisition policy changes
- Eastmoney, fund-company/CDN, CNINFO or fallback reintroduction
- provider, LLM, `--use-llm`, endpoint, DNS, curl, socket or runtime-budget probes
- golden, fixture, baseline or readiness promotion
- release, PR, push, merge, mark-ready, reviewer request, approval or external comment actions
- cleanup, delete, move, archive, import, ignore or promote actions
- broad live sample search or multi-fund data hunting

Release/readiness remains `NOT_READY` regardless of a successful single live run.

## 3. Controlled Sample

Primary and only sample:

| Field | Value |
|---|---|
| Fund code | `004393` |
| Target year | `2025` |
| Start year | `2021` |
| Quality gate policy | `warn` |
| Valuation state | `unavailable` |
| Refresh | `--force-refresh` |

Rationale:

- Earlier controlled live evidence accepted `004393 / 2021-2025` as a single-sample EID single-source/no-fallback product-path fact before the formal annual-period narrative/reporting implementation.
- This gate reuses the same bounded sample to prove the now-accepted formal annual-period narrative output on live data.
- A second sample requires a separate controller amendment and explicit authorization.

## 4. Execution Matrix

### E0: status preflight

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
git rev-parse --short HEAD
```

Acceptance:

- HEAD and branch captured.
- No tracked source/test/runtime diff.
- Existing unrelated untracked residue is recorded but not used as proof.

Stop:

- Stop before live execution if tracked source/test/runtime drift exists outside this gate.

### E1: CLI surface preflight

```bash
uv run fund-analysis analyze-annual-period --help
```

Acceptance:

- Help output includes `--target-year`, `--start-year`, `--valuation-state`, `--quality-gate-policy` and `--force-refresh`.

### E2: controlled live narrative run

Allowed command:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Capture policy:

- Capture stdout/stderr to a temporary local run directory outside the repository.
- Durable review artifacts may summarize command, exit code, byte counts, metadata header fields, source summary lines, quality gate status and section-presence checks.
- Durable review artifacts must not paste the full report body, raw PDF text, raw downloaded document content or cache paths.

Expected success:

- Exit code `0`.
- Metadata header shows years `2025,2024,2023,2022,2021`.
- Metadata/header or source summary shows `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false` for all available years.
- `fallback_year_count=0`.
- Output includes formal annual-period report sections:
  - annual coverage/source section
  - cross-year key changes section
  - impact-on-current-judgment section
  - gaps/degradation section
  - embedded target-year 8-chapter report section

Acceptable non-success classifications:

- Target-year live unavailability: blocker for this live evidence sample, not proof of product failure.
- Optional prior-year `not_found` / `unavailable`: year-level live-data gap if target year succeeds.
- Optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error`: fail-closed year record if target year succeeds.
- Quality gate `warn`: acceptable evidence-run status; not readiness proof.

Stop:

- Stop if any metadata/log indicates Eastmoney, fund-company/CDN, CNINFO, fallback invocation or non-EID annual-report source.
- Stop if target-year identity differs from requested `fund_code=004393` or `target_year=2025`.
- Stop if the run requires provider/LLM, `--use-llm`, golden/readiness/release or PR state.
- Stop if durable evidence would require committing raw report/PDF/cache files.

## 5. Evidence Artifact Requirements

The execution evidence artifact must include:

- `run_id`, timestamp, cwd, branch, HEAD and command
- user live authorization reference
- E0/E1/E2 command results with exit codes
- stdout/stderr byte counts
- metadata header summary
- year table for 2021-2025
- source/provenance summary
- quality gate summary
- narrative section-presence table
- negative-action checklist
- residual table
- explicit readiness statement

## 6. Required Reviews

Before controller acceptance:

- AgentDS review
- AgentMiMo review

Review focus:

- command matrix matches this plan
- live scope stayed bounded to one sample
- evidence supports annual-period narrative output, not only metadata summary
- source-policy/no-fallback boundaries are preserved
- durable artifacts avoid raw report/PDF body leakage
- `NOT_READY` is preserved

## 7. Acceptance Criteria

This gate can be accepted only if:

1. The plan is accepted after DS/MiMo review.
2. The live execution evidence is written under `docs/reviews/`.
3. DS/MiMo review the execution evidence.
4. Controller judgment maps findings and residuals.
5. `git diff --check` passes.
6. Local accepted checkpoint includes only plan/review/judgment/evidence/control artifacts.

## 8. Next Entry

If accepted, next recommended mainline:

`Live evidence ready-state disposition gate`

Deferred entries:

- live provider / LLM acceptance gate
- additional EID live sample gate
- CI quality warn-only planning gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready external-state gate
