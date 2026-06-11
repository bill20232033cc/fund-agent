# Controller judgment: multi-year annual narrative writer/reporting planning gate

## Verdict

`ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`

The amended plan is accepted as the code-generation-ready plan for the next `multi-year annual narrative writer/reporting implementation gate`.

This is a planning acceptance only. It does not implement source/test/runtime behavior, does not run live evidence, does not change source acquisition policy, and does not claim release/readiness.

## Truth Inputs

- `AGENTS.md`: rule source; requires current truth separation, FundDocumentRepository boundary, explicit typed parameters, no fallback/source-policy drift, no buy/sell/prediction language, and standard/heavy gate discipline.
- `docs/design.md` v2.17: current code fact is deterministic `analyze-annual-period` productization with Service request/result, Fund `AnnualEvidenceBundle`, Chapter 5 cross-year fact projection and CLI surface; full cross-year narrative writer/reporting remains future scope.
- `docs/current-startup-packet.md`: current active gate is `multi-year annual narrative writer/reporting planning gate`; next entry must remain planning until reviewed plan is accepted.
- `docs/implementation-control.md` v2.7: accepted inputs include productization implementation checkpoint `61ab780` and controlled live evidence checkpoint `271a052`; current next entry is planning worker for narrative writer/reporting.
- Plan: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`.
- DS review: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-review-ds-20260611.md`.
- MiMo review: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-review-mimo-20260611.md`.
- DS targeted re-review: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-rereview-ds-20260611.md`.

## Controller Findings

| Finding | Disposition | Basis |
|---|---|---|
| Product gap: current annual-period output is metadata summary plus target-year report, not formal annual-period narrative | ACCEPT | `docs/design.md` states full cross-year narrative writer/reporting is future scope; plan targets exactly that gap |
| Preserve `MultiYearAnnualAnalysisResult.report_markdown` current-year semantics | ACCEPT | DS F1 identified forward-compat risk; amended plan locks current-year semantics and requires explicit `annual_period_report` field plus CLI consumption |
| Explicit quality gate absence behavior | ACCEPT | DS F3 and MiMo F3 identified ambiguity; amended plan requires `quality_gate_status=not_available` when absent and a bounded no-readiness note |
| Section-specific wording guard for `对当前判断的影响` | ACCEPT | AGENTS prohibits buy/sell, prediction and unsupported causality; amended plan makes this a targeted implementation/test requirement |
| All-prior-years-gap test case | ACCEPT | MiMo F5 requested explicit edge coverage; amended plan adds a degenerate availability test |
| Renderer location fork under Fund layer | ACCEPT_WITH_RESIDUAL | MiMo prefers `fund_agent/fund/template/annual_period_renderer.py`, but both allowed locations remain within Fund boundary; implementation may choose and update ruff target |
| Cross-year fact eligibility criteria not re-specified | ACCEPTED_RESIDUAL | Existing `AnnualEvidenceBundle.cross_year_facts` remains the typed eligibility surface; renderer must not infer beyond typed facts |
| Single-file coverage measurement | DEFER | Coverage measurement environment remains separate hygiene/residual work; deterministic functional tests are acceptance gate for this implementation |
| Additional live samples / readiness / release | DEFER | Not authorized by this planning gate and not needed for no-live implementation planning |

## Review Disposition

- DS initial verdict: `ACCEPT` with one medium and low/info findings.
- MiMo initial verdict: `ACCEPT` with non-blocking findings.
- Controller amended the plan to resolve the shared compatibility and quality-gate ambiguities.
- DS targeted re-review verdict: `ACCEPT`; DS judged F1-F3 resolved and F4 accepted residual.
- MiMo targeted re-review channel residual: MiMo accepted the original plan, but the targeted re-review pane stalled during local timestamp/write preparation and was interrupted without an artifact. This is recorded as a review-channel residual, not a plan blocker, because:
  - MiMo original findings were non-blocking;
  - amended plan directly addresses MiMo F1, F3, F4 and F5;
  - DS targeted re-review independently confirmed the amendment dispositions;
  - no source/test/runtime/design/control behavior is accepted from the stalled pane.

## Accepted Plan Contract

The next implementation gate must follow these locked decisions:

1. `MultiYearAnnualAnalysisResult.report_markdown` remains the target-year current report.
2. A distinct annual-period report field, preferably `annual_period_report`, carries the formal annual-period report.
3. CLI `analyze-annual-period` keeps the machine-readable metadata header and prints the explicit annual-period report body after it.
4. Renderer consumes only in-memory typed inputs from `AnnualEvidenceBundle` plus explicit current-year/quality-gate inputs.
5. Renderer must not access repository, PDF/cache/source helper, downloader, provider, LLM, filesystem document corpus or live command.
6. Annual-period output must include coverage/source, cross-year facts, bounded current-judgment impact, gaps/degradation and current-year report sections.
7. Missing quality-gate context renders `quality_gate_status=not_available` and cannot imply pass/readiness.
8. Implementation must add section-specific wording guard coverage for buy/sell language, return prediction wording and unsupported causality.
9. No public chapter id expansion beyond `0-7`.
10. No source-policy, fallback, Eastmoney, fund-company/CDN or CNINFO change.

## Validation

Executed by controller:

```text
git diff --check
```

Result: pass.

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run. No source/test/runtime/design/control/startup file was modified in this planning judgment step.

## Next Entry

Mainline next entry:

1. `multi-year annual narrative writer/reporting implementation gate`

Deferred entries:

- additional controlled live annual-period samples;
- structured-data source identity extension;
- coverage measurement environment hygiene;
- runtime artifact disposition for `reports/live-evidence` and quality-gate outputs;
- release-readiness residual acceptance evidence.
