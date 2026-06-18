# Controller Judgment: Controlled Live Annual-period Narrative Evidence

Date: 2026-06-12

Role: controller

Gate: `Controlled live annual-period narrative evidence execution gate`

Classification: `standard`

Accepted plan:

- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-plan-20260612.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-plan-controller-judgment-20260612.md`
- Plan checkpoint `37ec1d8`
- Execution control-sync checkpoint `385948a`

Execution evidence:

- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-20260612.md`

Independent reviews:

- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-review-ds-20260612.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-review-mimo-20260612.md`

User live authorization:

- `授权live gate` on 2026-06-12

## 1. Verdict

**ACCEPT_WITH_RESIDUALS_NOT_READY**

The controlled live annual-period narrative evidence execution gate is accepted for the single authorized sample:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Accepted evidence facts:

- command exited `0`
- `fund_code=004393`
- `target_year=2025`
- `canonical_years=2025,2024,2023,2022,2021`
- `available_years=2025,2024,2023,2022,2021`
- `gap_years` empty / `none`
- `fail_closed_years` empty / `none`
- `cross_year_fact_count=3`
- `fallback_year_count=0`
- emitted source lines for all five years show `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`
- annual-period narrative/reporting headings are present
- embedded current-year report headings `# 0` through `# 7` and `## 证据与出处` are present
- `quality_gate_status=warn` and `quality_gate_issues=3` are recorded as readiness residuals

This judgment accepts only bounded single-sample live evidence. It does not accept release/readiness, additional live sample coverage, provider/LLM readiness, fixture/golden promotion, cleanup, PR, merge or source-policy expansion.

Release/readiness remains **`NOT_READY`**.

## 2. Review Finding Disposition

| Finding | Controller disposition | Basis | Required handling |
|---|---|---|---|
| DS-1: unique command and single-sample boundary supported | ACCEPT | Evidence run identity and E2 command match accepted plan exactly | No additional sample or command is accepted |
| DS-2: exit `0` supported | ACCEPT | Evidence records verdict, run identity and E2 result as exit `0` | Accept as bounded live execution success |
| DS-3: all five years available | ACCEPT | Evidence records canonical and available years for 2025-2021, with empty gaps/fail-closed years | Accept as single-sample year availability fact |
| DS-4: EID single-source/no-fallback supported | ACCEPT | Evidence records emitted source lines for all five years and `fallback_year_count=0` | Accept as emitted-line source-policy evidence |
| DS-5: annual-period section presence supported | ACCEPT | Evidence section-presence table covers annual-period sections and current-year report headings | Accept as section-presence evidence, not full report quality proof |
| DS-6: no durable raw-body leak | ACCEPT | Evidence keeps full stdout in `/tmp` and summarizes only metadata/heading/source checks | Do not promote raw report/PDF/cache content |
| DS-7: warn quality gate preserved as `NOT_READY` residual | ACCEPT | Evidence records `quality_gate_status=warn` and residual classification | Preserve `NOT_READY` |
| DS-8: timestamp granularity weaker than plan | ACCEPT_AS_NONBLOCKING_RESIDUAL | Evidence has date, run_id, cwd, branch, HEAD and command, but no time-of-day timestamp | Record as evidence hygiene residual; does not block acceptance |
| MIMO-001: plan amendments covered | ACCEPT | Evidence includes source extraction method, metadata patterns, `--force-refresh` rationale, authorization and `NOT_READY` | No rewrite required |
| MIMO-002: narrative/reporting headings proven | ACCEPT | Evidence table records formal annual-period and embedded report headings | Accept as section-presence evidence only |
| MIMO-003: EID/no-fallback comes from emitted lines | ACCEPT | Evidence records five source lines and year/source tables | Accept as direct emitted-line evidence |
| MIMO-004: discarded `rg` syntax error handled | ACCEPT | Evidence states the failed lookahead command exited `2` and was not used; corrected negative check found no forbidden token | Keep discarded command outside evidence chain |
| MIMO-005: quality gate warn remains `NOT_READY` residual | ACCEPT | Evidence and residual table preserve this | No readiness claim |
| MIMO-006: artifact-only review, not raw output re-verification | ACCEPT_AS_REVIEW_SCOPE_RESIDUAL | DS/MiMo reviews intentionally did not read `/tmp` raw captures | Controller judgment treats them as evidence-artifact reviews |

No reviewer finding blocks acceptance.

## 3. Accepted / Rejected / Residual Table

| Item | Disposition | Reason |
|---|---|---|
| Single authorized live command | ACCEPT | Exact command in accepted plan and evidence match |
| Single sample `004393 / 2021-2025` | ACCEPT_WITH_SCOPE_LIMIT | Accepted only for this sample; no additional coverage inferred |
| Exit `0` | ACCEPT | Evidence records exit `0` |
| Five years available | ACCEPT | Evidence records all target/prior years available |
| EID single-source/no-fallback | ACCEPT | Emitted lines show EID/single-source/no-fallback for each available year |
| `fallback_year_count=0` | ACCEPT | Evidence metadata records `0` |
| Annual-period narrative/reporting section presence | ACCEPT_WITH_SCOPE_LIMIT | Headings present; full report quality/readiness not accepted |
| `quality_gate_status=warn` | ACCEPT_AS_RESIDUAL | Acceptable under `--quality-gate-policy warn`; blocks readiness claim |
| `quality_gate_issues=3` | ACCEPT_AS_RESIDUAL | Recorded as material release/readiness residual |
| Raw stdout/report/PDF/cache content | REJECT_AS_DURABLE_EVIDENCE | Not promoted or pasted into durable artifacts |
| Additional EID live sample coverage | DEFER | Requires separate reviewed gate and authorization |
| Provider/LLM/`--use-llm` readiness | DEFER | Not authorized or tested |
| Fixture/golden/readiness promotion | DEFER | Not authorized |
| Cleanup/archive/delete/import/ignore artifact action | DEFER | Requires separate authorization |
| PR/push/merge/mark-ready/release | REJECT_FOR_THIS_GATE | External-state actions not authorized |

## 4. Boundary Assessment

| Boundary | Judgment |
|---|---|
| Source acquisition policy | Preserved: EID single-source operational policy only; no Eastmoney/fund-company/CNINFO fallback was accepted |
| Source/test/runtime behavior | Preserved: no source/test/runtime edits are part of this gate |
| Provider/LLM | Preserved: no provider/LLM/`--use-llm` path accepted |
| Raw artifact handling | Preserved: full report stdout remains outside repository under `/tmp`; durable artifacts summarize only |
| Release/readiness | Preserved as `NOT_READY` |
| External state | No PR/push/merge/mark-ready/release action accepted |

## 5. Review-channel Residual

The tmux DS and MiMo panes were available but did not reliably complete the bounded execution-evidence review:

- DS tmux pane attempted a full stdout read and then remained stuck in approval/queue state.
- MiMo tmux pane performed bounded summary reads but did not complete review artifact generation in time.

To complete the required independent reviews without violating raw-output boundaries, the controller used existing sub-agent channels for DS-role and MiMo-role artifact-only reviews. Those reviews were limited to accepted plan/control/evidence artifacts and did not read `/tmp` raw captures.

Disposition: **ACCEPT_AS_REVIEW_CHANNEL_RESIDUAL**.

This does not block this gate because two independent artifact-only reviews were completed and returned `PASS_WITH_FINDINGS`. Future gates should prefer shorter artifact-only handoffs or precomputed metadata summaries when raw report boundaries are strict.

## 6. Residuals

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| `quality_gate_status=warn`; `quality_gate_issues=3` | material release/readiness residual | release/readiness owner | `Live evidence ready-state disposition gate` with explicit `NOT_READY` preservation |
| Single sample only | material readiness residual; non-blocking for this evidence gate | release/evidence owner | additional live sample gate only if separately reviewed and authorized |
| No provider/LLM path evidence | deferred residual | provider/runtime owner | live provider / LLM acceptance gate |
| Full `/tmp` stdout/stderr captures not independently reviewed by DS/MiMo | artifact-only review residual | controller/evidence owner | acceptable under current raw-output boundary; no promotion |
| Runtime emitted local quality-gate report paths | artifact hygiene residual | artifact owner/controller | separate artifact disposition/cleanup gate only by explicit authorization |
| Missing time-of-day execution timestamp in evidence artifact | non-blocking evidence hygiene residual | controller | improve in future live evidence artifacts |

## 7. Next Entry

Recommended next mainline:

`Live evidence ready-state disposition gate (NOT_READY preservation)`

Deferred entries:

- additional EID live sample gate
- live provider / LLM acceptance gate
- CI quality warn-only planning gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready external-state gate

## 8. Final State

Controlled live annual-period narrative evidence execution is accepted for one sample.

Release/readiness remains `NOT_READY`.
