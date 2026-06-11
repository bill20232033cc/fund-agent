# AgentDS plan review: multi-year annual narrative writer/reporting planning gate

## Verdict

**ACCEPT**

The plan correctly targets the real product gap, preserves Fund/Service/UI boundaries, proposes an acceptable output contract, bounds cross-year claims with explicit deterministic language constraints, and provides sufficient implementation slices and validation for a no-live implementation gate.

## Scope Confirmation

- Reviewed artifact: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`
- Reviewed only the plan. Did not enter implementation, run live commands, or modify any source/test/runtime/design/control/startup files.
- Pane footer PR 22 is treated as unrelated UI residue per review scope and not considered in this review.

## Findings

### F1: `report_markdown` forward-compatibility risk (MEDIUM)

- Section: `Product Contract Decisions → New typed report result`, Compatibility decision.
- The plan presents a fork: either change `MultiYearAnnualAnalysisResult.report_markdown` to return the annual-period report, or keep it as current-year and add a separate `annual_period_report` field.
- The plan expresses preference for "explicit annual-period field plus CLI consumption," but leaves the final decision to the implementation gate.
- Risk: if the implementation gate chooses to change `report_markdown`, any existing consumer (test, script, evidence harness) that reads `report_markdown` expecting target-year content silently breaks.
- Recommendation: the implementation gate should either (a) make the plan decision explicit now (separate field, leave `report_markdown` unchanged) or (b) if changing `report_markdown`, add an explicit deprecation/rename audit as a required validation step in the implementation evidence.

### F2: "对当前判断的影响" section heading invites semantic drift (LOW)

- Section: `Rendering Contract → Minimum annual-period sections`, item 4.
- The section heading "对当前判断的影响" is semantically open-ended. Without tight implementation guardrails, a future writer/renderer could drift into unsupported investment conclusions.
- Mitigation already present: the plan explicitly requires "bounded deterministic language only; no prediction, no buy/sell language, no unsupported causality; if facts are insufficient, state insufficiency and next minimum validation question."
- Residual: the implementation gate should add a wording guard test that red-flags any appearance of buy/sell language, return prediction, or unsupported causal language in this section specifically.

### F3: Quality gate caveat defaults are underspecified (LOW)

- Section: `Rendering Contract → Minimum annual-period sections`, item 2 ("quality gate caveat if provided").
- The phrase "if provided" leaves the renderer behavior ambiguous when quality gate context is absent.
- The current live evidence shows quality gate `warn` for `004393 / 2021-2025`. If quality gate info is missing in a future run, the renderer could silently omit quality warnings, creating a false impression of cleanliness.
- Recommendation: the annual-period report should explicitly state when quality gate status is unknown or not provided, rather than silently omitting the caveat. This can be a `quality_gate_status=not_available` line in the coverage section.

### F4: Cross-year fact eligibility criteria deferred to existing implementation (INFO)

- Section: `Rendering Contract → Minimum annual-period sections`, item 3.
- The plan says "render each eligible CrossYearDerivedFact" but does not define eligibility criteria beyond what the existing `AnnualEvidenceBundle` already provides (currently 3 cross-year facts from the live evidence run).
- This is acceptable for MVP because the existing `cross_year_facts` field already contains only safe typed facts with explicit `fact_type` and source years. The plan's rendering contract correctly requires rendering typed fact ids and fact types rather than prose inference when categories are unavailable.
- No change required for this gate; the implementation gate tests for gap/fail-closed bundles will implicitly confirm that only available facts are rendered.

## Accepted Residuals

| Residual | Rationale |
|---|---|
| `report_markdown` semantics decided at implementation time | Acceptable for planning gate; the preference is stated and both options are bounded. Recommend implementation gate explicitly lock the decision in acceptance criteria. |
| Renderer location fork (`annual_period_report.py` vs `template/annual_period_renderer.py`) | Both locations are in Fund layer, respecting the boundary constraint that the renderer must not access repository/PDF/source. The implementation gate can choose either without violating any architectural rule. |
| Coverage measurement not independently verified | Same environment constraint as the prior productization implementation gate (akshare → pandas → numpy import failure before test execution). Deterministic functional tests are the acceptance standard for this gate; coverage measurement is a separate deferred gate. |
| No additional live samples beyond `004393` | Explicitly a non-goal. The plan correctly scopes verification to no-live deterministic tests with fake/in-memory inputs. |

## Deferred Candidates

- Wording guard for "对当前判断的影响" section → implementation gate should add a targeted test.
- Quality gate `not_available` explicit rendering → implementation gate should decide: render `not_available` line vs omit. Recommend explicit line.
- `report_markdown` forward-compatibility → if implementation changes `report_markdown` semantics, add deprecation audit to implementation evidence.

## Validation Performed

Static review only, against these inputs:

- `AGENTS.md` — architecture boundaries, hard constraints, annual-report access rules, fallback strategy,禁止事项/必须事项.
- `docs/design.md` (v2.17) — current architecture facts, multi-year annual productization implementation status, Fund/Service/UI contracts, deterministic execution chain, CHAPTER_CONTRACT mechanism, report rendering contract.
- `docs/current-startup-packet.md` — current gate scope, accepted checkpoint `271a052`, non-goals, open residuals.
- `docs/implementation-control.md` (v2.7) — current gate, accepted artifacts, residual owners, non-goal reminder.
- `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md` — the plan under review.
- `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-controller-judgment-20260611-231045.md` — accepted live evidence facts: `004393 / 2021-2025`, 5 years available, 3 cross-year facts, 0 fallback, all EID single-source.
- `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md` — accepted implementation facts: Fund-owned `AnnualEvidenceBundle`, Chapter 5 cross-year projection, Service request/result types, CLI `analyze-annual-period`, boundary compliance.

Cross-checked plan claims against:

- **Product gap**: confirmed. Current CLI output is metadata header + target-year report; Chapter 5 renders largely insufficient-data prose; `AnnualEvidenceBundle` cross-year facts are computed but not rendered into a formal narrative. The plan's gap diagnosis matches the facts.
- **Boundary compliance**: confirmed. Plan explicitly restricts renderer to in-memory typed inputs (no repository/PDF/cache/source helper access), keeps Service assembly as orchestrator, keeps CLI as UI consumer. All three slices respect `UI → Service → Fund`.
- **Output contract**: confirmed acceptable. Metadata header preserved, formal annual-period narrative added, current-year report embedded without new public chapter ids, Chapter 5 projection surface unchanged.
- **Cross-year claim bounding**: confirmed. Plan includes explicit evidence wording requirements, "bounded deterministic language only" constraint, and non-goals excluding buy/sell/prediction/unsupported causality.
- **Slice and validation sufficiency**: confirmed. Four slices with explicit file lists, implementation requirements, test specifications, and validation commands. All slices are no-live.

No contradictions found between the plan and the truth sources.

## Explicit Statement

**No live commands were run.** This review is static analysis only. No EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were executed. No source, test, design, control, or startup files were modified.
