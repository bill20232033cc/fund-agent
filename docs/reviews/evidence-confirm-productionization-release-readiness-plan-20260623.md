# Evidence Confirm Productionization Release/readiness Plan

## Verdict

`PLAN_FIXED_READY_FOR_REREVIEW_NOT_READY`

## Gate

- Work unit: `Evidence Confirm Productionization Release/readiness`
- Gate: planning only
- Classification: `heavy`
- Branch checked locally: `evidence-confirm-productionization`
- Artifact: `docs/reviews/evidence-confirm-productionization-release-readiness-plan-20260623.md`
- Current remote PR-40 head: `b59aed754c491adb05e533fde812b3ba93fa3f96`
- Local observation: local `HEAD=89ccc4433b31efb67115c8c6247b2079a1d4421e` is one commit ahead of `origin/evidence-confirm-productionization`, and `origin/evidence-confirm-productionization=b59aed754c491adb05e533fde812b3ba93fa3f96`.

This plan does not implement code, run live/PDF/provider/LLM commands, mutate PR-40, push, mark ready, merge, request reviewers, release, or claim readiness.

## Goal / Motivation / Success Signal

Goal: produce a code-generation-ready release/readiness plan for Evidence Confirm productionization after PR-40 draft-PR-pass, without treating the accepted draft PR as release-ready.

Motivation: the original objective was not only to wire a default Evidence Confirm policy. The full objective was:

1. live source/PDF Evidence Confirm;
2. semantic entailment Evidence Confirm;
3. Service/UI/renderer/quality-gate production integration;
4. release/readiness.

Items 1-3 now have accepted implementation or partial evidence, but release/readiness still requires proof, not inference from code presence or PR cleanliness.

Success signal:

- Release/readiness matrix classifies every blocker as `met`, `not_met`, `deferred_with_owner`, or `requires_authorization`.
- Multi-sample live source/PDF proof is gathered only through `FundDocumentRepository` / Fund-layer runner boundaries.
- Provider-backed semantic proof demonstrates real provider behavior without allowing semantic pass to override deterministic V2/source failures.
- Checklist, annual-period summary display, and report-body rendering decisions are explicitly implemented or deliberately deferred with product owner disposition.
- PR-40 mark-ready/merge/release are separated from local readiness evidence and require explicit user authorization.
- Any readiness claim is backed by review artifacts, passing validation, PR state evidence, and residual routing.
- Release/readiness remains `NOT_READY` until RR-S1 through RR-S8 complete through accepted gates or unresolved release blockers receive reviewed explicit deferral with owner.

## Non-goals / Scope Boundary

- No code implementation in this planning gate.
- No live/PDF/provider/LLM/network-heavy command in this planning gate.
- No source fallback behavior change.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion unless a later reviewed gate proves it necessary.
- No Service/UI/Host/renderer/quality-gate direct PDF/cache/source-helper/parser access.
- No Docling/pdfplumber/EID HTML render direct consumption by Service/UI/Host/renderer/quality gate/LLM prompt/templates.
- No parser replacement, golden promotion, broad extractor correctness claim, or full field correctness claim.
- No Host durable runtime, Agent full tool-loop, provider default, provider budget, or LLM product default change.
- No PR-40 mark-ready, merge, release, request reviewers, PR body mutation, push, or commit without a later explicit authorization gate.
- No claim that single-sample live evidence, no-live tests, or CI success proves release readiness.

## Facts vs Unproven Items

### Proven / Current Facts

- `docs/implementation-control.md` names the active gate as `Evidence Confirm Productionization Release/readiness Planning Gate` and classifies it as `heavy`.
- PR-40 remains draft/open at remote head `b59aed754c491adb05e533fde812b3ba93fa3f96`, CI `test` success, merge state `CLEAN`.
- Product `fund-analysis analyze` defaults to repository-bounded Evidence Confirm with `warn` policy.
- Product `fund-analysis analyze-annual-period` inherits current-year `analyze()` behavior.
- Product `fund-analysis checklist` remains Evidence Confirm `off`.
- Developer `--evidence-confirm-policy off|warn|block` remains behind `--dev-override`.
- Renderer does not include Evidence Confirm content in report Markdown.
- Service/UI/renderer/quality-gate do not directly consume PDF/source internals in the accepted PR review judgment.

### Not Proven / Still Blocking Release

- Multi-sample live source/PDF readiness proof is absent.
- Provider-backed semantic quality proof is absent; current semantic layer is no-live/injected-client.
- Checklist Evidence Confirm CLI/support is absent.
- Annual-period CLI does not print Evidence Confirm summary lines even though current-year result can carry a summary.
- Report-body Evidence Confirm rendering has no product decision beyond current intentional non-rendering.
- PR-40 mark-ready/merge/release are not authorized.
- Local branch is ahead of remote by one closeout commit; external-state readiness must reconcile whether PR-40 should include that local artifact or whether it remains local-only evidence.
- Visible untracked residue remains in the worktree and must be classified before any release/readiness claim.

## Direct Code / Control Evidence

- Control truth: `docs/implementation-control.md:50-52` identifies this active gate and blocks live/PDF/provider commands, checklist support, annual-period summary refinement, mark-ready, merge, and release/readiness claims before reviewed gates.
- Startup packet: `docs/current-startup-packet.md:23-28` preserves PR-40 draft/open and lists the exact unproven blockers.
- Final closeout: `docs/reviews/evidence-confirm-productionization-default-on-policy-draft-pr-pass-final-closeout-20260623.md:23-34` records PR-40 state and no mark-ready/merge/release/provider/live mutation.
- Final closeout residuals: `docs/reviews/evidence-confirm-productionization-default-on-policy-draft-pr-pass-final-closeout-20260623.md:53-68` routes checklist, provider semantic, multi-sample live, annual-period summary, report-body rendering, and PR/release as deferred.
- Service default policy: `fund_agent/services/fund_analysis_service.py:1585-1591` sets product analyze `evidence_confirm_policy="warn"`.
- Developer override policy: `fund_agent/services/fund_analysis_service.py:1592-1618` keeps developer mode `evidence_confirm_policy` default `off`.
- Checklist boundary: `fund_agent/services/fund_analysis_service.py:1661-1687` forces `command_source="checklist"` to Evidence Confirm `off`.
- Service execution: `fund_agent/services/fund_analysis_service.py:1193-1218` extracts data, runs Evidence Confirm if enabled, then passes summary to quality gate and applies blocking.
- Repository runner boundary: `fund_agent/fund/evidence_confirm_sources.py:252-397` calls only `repository.load_annual_report()`, materializes references, and runs V2.
- Repository failure classification: `fund_agent/fund/evidence_confirm_sources.py:490-530` maps source failures into stable categories including `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`.
- Semantic boundary: `fund_agent/fund/evidence_confirm_semantic.py:1-8` is no-live and requires injected client; `fund_agent/fund/evidence_confirm_semantic.py:166-205` consumes V2 result/references/claims/client only.
- Production summary boundary: `fund_agent/fund/evidence_confirm_production.py:77-138` compresses repository/semantic results into a safe summary without raw excerpts or provider construction.
- Quality gate ECQ projection: `fund_agent/fund/quality_gate_integration.py:57-65` accepts optional `EvidenceConfirmProductionSummary`; `fund_agent/fund/quality_gate_integration.py:173-260` maps summary into ECQ issues without reading repository/PDF/source/provider.
- CLI analyze display: `fund_agent/ui/cli.py:747-753` exposes `--evidence-confirm-policy`; `fund_agent/ui/cli.py:901-903` prints quality gate and Evidence Confirm summary before report body; `fund_agent/ui/cli.py:2641-2668` prints safe Evidence Confirm summary lines.
- Annual-period CLI gap: `fund_agent/ui/cli.py:1080-1083` prints quality gate summary and multi-year summary, then report body; it does not call `_echo_evidence_confirm_summary(result.current_year_result)`.
- Annual-period Service inheritance: `fund_agent/services/fund_analysis_service.py:853-868` delegates current year to `analyze()`; tests at `tests/services/test_fund_analysis_service.py:2174-2184` prove current-year Evidence Confirm summary can exist and feed quality gate.
- Renderer non-rendering: `fund_agent/fund/template/renderer.py:87-138` has no Evidence Confirm field; `fund_agent/fund/template/renderer.py:141-185` renders existing 8 chapters and evidence appendix only.

## Release/readiness Requirement Matrix

| ID | Requirement | Current status | Required proof / action | Owner gate | Release disposition |
|---|---|---|---|---|---|
| RR-01 | Source/PDF pathway uses only accepted repository boundary | Partly implemented | Multi-sample live evidence shows `FundDocumentRepository.load_annual_report()` path, EID single-source/no fallback where expected, stable failure categories where not expected | RR-S2 | blocking until accepted |
| RR-02 | Deterministic V2 remains fail-closed | Implemented no-live | Focused no-live regression plus live evidence showing candidate/not_proven/missing/wrong-year/value mismatch do not pass | RR-S1/RR-S2 | blocking until accepted |
| RR-03 | Provider-backed semantic quality | Not proven | Provider-backed evidence with bounded claims/excerpts, deterministic precondition enforcement, contradiction/insufficient cases, redaction, no deterministic override | RR-S3 | blocking unless explicitly deferred from release |
| RR-04 | Service/UI production default | Implemented | Static and test evidence that product analyze default warn is intentional, developer override off remains off, block behavior exits safely | RR-S1 | blocking until accepted |
| RR-05 | Quality gate ECQ integration | Implemented | Regression proving ECQ0-ECQ4 issue mapping, score JSON remains Evidence-Confirm-unaware, block/warn aggregation correct | RR-S1 | blocking until accepted |
| RR-06 | Checklist Evidence Confirm CLI/support | Absent | Either implement checklist support with explicit CLI/product semantics, or record product-owner deferral that checklist release is out of scope | RR-S4 | blocking until implemented or explicitly deferred |
| RR-07 | Annual-period Evidence Confirm CLI summary display | Partial | CLI must print current-year Evidence Confirm summary or document why summary is hidden; test output must prove chosen behavior | RR-S5 | blocking until decided |
| RR-08 | Report-body Evidence Confirm rendering | Intentionally absent | Product decision: keep summary out of report body, add a reviewed body section, or defer with explicit UX owner | RR-S6 | blocking until decided |
| RR-09 | Docs/readiness truth sync | Not done for release state | README/design/control/doc updates only after evidence gates decide current behavior; no future claims as current facts | RR-S7 | blocking before release |
| RR-10 | Worktree and artifact hygiene | Not clean | Classify visible untracked residue and local-only closeout/ahead state before release claim | RR-S7/RR-S8 | blocking before mark-ready/merge |
| RR-11 | PR-40 external state | Draft/open, clean, CI success | Explicit authorization for push/PR body if needed, mark-ready, merge, release; verify post-action state | RR-S8 | requires authorization |

## RR-S Dependency Graph / Order

The dependency order is binding for implementation/evidence gates:

1. `RR-S1` has no slice dependency and must run first because it establishes the no-live static/test baseline for current Evidence Confirm behavior.
2. `RR-S2`, `RR-S3`, and `RR-S5` depend on `RR-S1`. They must not claim source/PDF, provider-semantic, or annual-period display readiness if RR-S1 finds an instrumentation or current-behavior gap.
3. `RR-S4` and `RR-S6` are product decision gates. They may run after the RR-S1 preflight, or in parallel with RR-S2/RR-S3/RR-S5 only if there is no shared file ownership. Default recommendations are Option A for both gates in this release.
4. `RR-S7` depends on `RR-S1` through `RR-S6`. It must not sync docs or classify release hygiene as complete before product/evidence decisions are known.
5. `RR-S8` depends on `RR-S7`. PR-40 mark-ready, merge, release, or any external-state mutation cannot precede local/remote reconciliation and explicit user authorization.

## Small Gated Slices

### RR-S1 - Static / No-live Release Matrix Evidence Gate

Objective: prove the accepted production integration behavior without live/PDF/provider execution.

Allowed files/modules:

- Write artifacts under `docs/reviews/`.
- Read-only production modules: `fund_agent/fund/evidence_confirm.py`, `fund_agent/fund/evidence_confirm_sources.py`, `fund_agent/fund/evidence_confirm_semantic.py`, `fund_agent/fund/evidence_confirm_production.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/quality_gate_integration.py`, `fund_agent/services/fund_analysis_service.py`, `fund_agent/ui/cli.py`, `fund_agent/fund/template/renderer.py`.
- Read-only tests under `tests/fund/`, `tests/services/`, `tests/ui/`.
- Include `tests/fund/test_evidence_confirm_runner.py` if present.
- Include a renderer-specific test module if present; current repository has `tests/fund/template/test_renderer.py`. If no renderer-specific test exists at RR-S1 execution time, the evidence artifact must include an explicit code-inspection note for `fund_agent/fund/template/renderer.py`.

Exact allowed changes:

- No production code changes.
- Produce one evidence artifact with matrix result, command output summaries, and residual disposition.
- If RR-S1 discovers missing no-live coverage that is required to prove the matrix, stop and create a separate reviewed no-live test/instrumentation plan instead of silently passing.

Validation commands:

```text
rg --files tests | rg "test_evidence_confirm_runner.py|test_renderer.py|template/test_renderer.py"
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/template/test_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
uv run pytest tests/fund/ tests/services/ tests/ui/ -q
uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_semantic.py fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/template/test_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
git diff --check -- fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_semantic.py fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/template/test_renderer.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Expected assertions:

- All focused tests pass.
- ECQ mapping covers `not_run`, repository/pathway fail, deterministic fail/warn, semantic fail/warn.
- `score.json` remains Evidence-Confirm-unaware.
- `checklist` Evidence Confirm remains `off`.
- Renderer report body remains free of Evidence Confirm summary.
- Broader focused suite is secondary evidence; failure there cannot be ignored, but root cause must be classified before expanding release scope.

Stop conditions:

- Any failed no-live regression.
- Any code path requiring live repository/PDF/provider to prove no-live behavior.
- Any finding that current product default is overclaimed as release-ready.

### RR-S2 - Multi-sample Live Source/PDF Readiness Evidence Gate

Objective: prove repository-bounded Evidence Confirm over multiple annual-report samples.

Allowed files/modules:

- Evidence artifact under `docs/reviews/`.
- Generated run outputs under an explicitly named ignored runtime directory such as `reports/evidence-confirm-release-readiness/<run_id>/`.
- Existing callable surfaces only: `fund_agent.fund.evidence_confirm_runner.run_repository_bounded_evidence_confirm`, `FundAnalysisService.analyze()`, or `fund-analysis analyze` CLI.
- No production code changes unless RR-S1 proves an instrumentation gap; if an instrumentation gap exists, stop and create a separate no-live instrumentation plan.

Sample policy:

- Preflight must enumerate the selected sample universe from accepted evidence or `FundDocumentRepository`-reachable metadata before live execution. The evidence artifact must record fund code, year, fund type, source expectation, and why each sample belongs to the release/readiness universe.
- Hard minimum for a multi-sample readiness claim: the prior accepted sample plus at least three additional fund/year samples across distinct fund types.
- If that floor cannot be met, RR-S2 result is `NOT_READY`, not a pass.
- Negative live cases are limited to safe `not_found` and controlled `unavailable` only.
- Exclude live `schema_drift`, `identity_mismatch`, and `integrity_error` cases unless a controlled non-live fixture or separately reviewed harness exists.
- Do not use arbitrary local PDFs or cache paths as proof.

Validation command pattern, requiring explicit live authorization before execution:

```text
uv run fund-analysis analyze <fund_code> --report-year <year> --valuation-state unavailable --quality-gate-policy warn
```

Expected assertions for each positive sample:

- Command exits `0`.
- Stderr includes `evidence_confirm_status: pass` or reviewed `warn`.
- `evidence_confirm_checked_facts` is greater than `0`.
- No raw excerpt, PDF path, cache path, parser JSON, provider payload, or source helper detail appears in stdout/stderr.
- Quality gate artifact contains ECQ issues only when summary status requires them.
- Evidence artifact records source provenance from the Fund-layer runner: selected source, source mode, fallback enabled/used, primary failure category, and metadata admission.

Expected aggregate assertions:

- Multiple samples pass or produce reviewed warnings without fallback policy drift.
- Any controlled non-live `schema_drift`, `identity_mismatch`, or `integrity_error` fixture/harness evidence remains fail-closed and is not masked by fallback.
- No Service/UI/renderer/quality-gate direct source/PDF/cache access is introduced.

Stop conditions:

- Any sample requires direct PDF/cache/source-helper access outside `FundDocumentRepository`.
- Any failure category is ambiguous and material to readiness.
- Any sample suggests EID single-source policy or fallback semantics need code changes.

### RR-S3 - Provider-backed Semantic Quality Evidence Gate

Objective: first decide provider-backed semantic readiness, then prove semantic Evidence Confirm with a real provider while keeping deterministic source/V2 failures authoritative.

Allowed files/modules:

- If implementation is needed, new Service-owned adapter module: `fund_agent/services/evidence_confirm_semantic_provider.py`.
- Existing provider surfaces: `fund_agent/config/llm.py`, `fund_agent/services/llm_provider.py` only through current public contracts; no config default or budget change.
- Existing Fund semantic protocol: `fund_agent/fund/evidence_confirm_semantic.py`; modify only if the current Protocol is insufficient and plan review accepts the exact contract change.
- Tests: `tests/services/test_evidence_confirm_semantic_provider.py`, `tests/fund/test_evidence_confirm_semantic.py`, `tests/fund/test_quality_gate_integration.py`.
- Evidence artifacts under `docs/reviews/`.

Semantic provider readiness preflight:

- Decide whether this release requires provider-backed semantic quality proof or an explicit reviewed deferral.
- Current no-live/injected semantic companion is not enough to claim provider-backed semantic quality.
- Release/readiness cannot claim RR-03 as `met` unless provider-backed evidence passes.
- If provider-backed semantic quality is deferred, the deferral must be reviewed, name an owner, preserve deterministic V2/source failures as authoritative, and keep release/readiness `NOT_READY` unless the release scope explicitly excludes RR-03.

Follow-on implementation/evidence path if code is required:

- Add a Service-owned adapter implementing `EvidenceEntailmentClient`.
- Adapter input must be `EvidenceEntailmentRequest` only; no repository/PDF/source/cache access.
- Adapter output must map provider response to closed statuses: `entailed`, `contradicted`, `insufficient`, `not_applicable`.
- Redact API key, headers, raw provider body, prompts, and full excerpt text from diagnostics.
- Do not change provider defaults, model defaults, retry defaults, timeout budgets, or deterministic Evidence Confirm policy.

No-live validation commands:

```text
uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_evidence_confirm_semantic_provider.py -q
uv run ruff check fund_agent/fund/evidence_confirm_semantic.py fund_agent/services/evidence_confirm_semantic_provider.py tests/fund/test_evidence_confirm_semantic.py tests/services/test_evidence_confirm_semantic_provider.py
git diff --check -- fund_agent/fund/evidence_confirm_semantic.py fund_agent/services/evidence_confirm_semantic_provider.py tests/fund/test_evidence_confirm_semantic.py tests/services/test_evidence_confirm_semantic_provider.py
```

Provider-backed validation command pattern, requiring explicit provider/live authorization:

```text
FUND_AGENT_LLM_PROVIDER=openai_compatible ... uv run <accepted semantic evidence command>
```

Expected assertions:

- Provider-backed positive claim returns `entailed`.
- Contradiction and insufficient support produce fail/warn as configured.
- If deterministic V2 fails, semantic client is not called or semantic result is blocked by `deterministic_gate_failed`.
- Provider exceptions are fail-closed and safe-redacted.
- Semantic pass never converts a deterministic fail into release-ready.

Stop conditions:

- Need to expose raw excerpts/provider payloads outside the evidence artifact boundary.
- Need to change provider defaults or runtime budgets.
- Need to let Service or provider adapter read repository/PDF/cache/source helper.
- Provider-backed semantic quality remains unproven and no reviewed deferral assigns owner.

### RR-S4 - Checklist Evidence Confirm CLI/support Gate

Objective: decide and implement checklist Evidence Confirm behavior or explicitly defer it from this release.

Allowed files/modules if implementation is chosen:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`
- README/docs only if the CLI behavior changes.

Exact allowed implementation options:

- Option A: keep checklist Evidence Confirm `off` for this release and write a product-owner/controller deferral artifact. This is the recommended default for this release.
- Option B: add explicit checklist CLI policy using the same `off|warn|block` semantics, with no direct UI repository/source access.
- Option C: default checklist to `warn` only after separate product review accepts user-facing semantics and validation proves no blocking surprise.

Default decision:

- Recommend Option A unless a later explicit product-owner/controller decision overrides it.
- Rationale: checklist UX semantics differ from `analyze`, checklist currently has no Evidence Confirm CLI/support, and enabling repository-bounded work on this surface should not be hidden inside a release/readiness gate.
- Option A produces a reviewed deferral artifact and keeps RR-06 as `deferred_with_owner`; it does not claim checklist Evidence Confirm support.

Validation commands for Option B/C:

```text
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Expected assertions:

- Checklist behavior is visible in CLI help/tests.
- `checklist` either remains explicitly off with no runner call, or prints safe Evidence Confirm summary lines.
- Any block behavior exits `2` without checklist body.

Stop conditions:

- Checklist requires a new developer override mode without product decision.
- Checklist would silently run repository/PDF work without user-visible policy.

### RR-S5 - Annual-period Evidence Confirm CLI Summary Display Gate

Objective: refine annual-period CLI display so Evidence Confirm inheritance is visible or explicitly hidden by product decision.

Allowed files/modules:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `fund_agent/services/fund_analysis_service.py` only if Service result projection is insufficient.
- `tests/services/test_fund_analysis_service.py` only for Service projection tests.

Exact allowed changes:

- Preferred small fix: call `_echo_evidence_confirm_summary(result.current_year_result)` in `analyze_annual_period()` after `_echo_quality_gate_summary(result.current_year_result)`.
- Do not add `--evidence-confirm-policy` to `analyze-annual-period` unless this gate explicitly expands to a developer-mode annual-period policy.
- Do not add LLM annual-period support.
- Do not change `annual_period_report.report_markdown`.

Validation commands:

```text
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service.py -q
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py
git diff --check -- fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py
```

Expected assertions:

- Annual-period CLI stderr/stdout contains safe Evidence Confirm summary lines when current-year analyze produced a summary.
- Report body remains annual-period report Markdown and does not embed raw Evidence Confirm excerpts.
- Existing multi-year metadata header remains stable.

Stop conditions:

- Display change requires new annual-period request contract.
- Display change implies `analyze-annual-period --use-llm` or multi-period LLM route.

### RR-S6 - Report-body Evidence Confirm Rendering / Product Decision Gate

Objective: decide whether Evidence Confirm belongs in investment report body.

Allowed files/modules:

- Decision-only artifact under `docs/reviews/`.
- If implementation is accepted later: `fund_agent/fund/template/renderer.py`, `fund_agent/services/fund_analysis_service.py`, `tests/fund/test_template_renderer.py` or current renderer test module, `tests/services/test_fund_analysis_service.py`.

Decision options:

- Option A: keep Evidence Confirm outside report body for this release; CLI/quality gate are sufficient. This is the recommended default for this release.
- Option B: add a short non-investment audit metadata section after the evidence appendix.
- Option C: add per-chapter Evidence Confirm labels only after wording review and audit contract review.

Default decision:

- Recommend Option A unless a later explicit product-owner/controller decision overrides it.
- Rationale: current renderer intentionally does not render Evidence Confirm, CLI safe summary plus ECQ issues already expose the `warn` policy surface, and report-body wording requires separate UX/audit-contract review.
- Option A keeps RR-08 as `deferred_with_owner` or out of this release scope by explicit decision; it must not be described as report-body Evidence Confirm support.

Required decision assertions:

- The report body must not mix audit state with buy/sell advice.
- No raw excerpts, PDF/cache paths, provider payloads, or parser JSON may render.
- Any report-body rendering must be covered by wording tests and audit tests.

Stop conditions:

- Product wording cannot distinguish source-support metadata from investment conclusion.
- Rendering requires expanding public EvidenceAnchor or EvidenceSourceKind.

### RR-S7 - Docs / Control / Hygiene Readiness Gate

Objective: sync current behavior only after evidence/product gates close and classify local artifacts.

Allowed files/modules:

- `README.md` only if user-facing CLI behavior changes.
- `fund_agent/README.md` only if Service/Fund boundary wording changes.
- `fund_agent/fund/README.md` only if Fund Evidence Confirm behavior changes.
- `fund_agent/config/README.md` only if provider env behavior changes.
- `tests/README.md` only if test conventions change.
- `docs/design.md` only for accepted current facts.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` only in controller truth-sync gate.
- `docs/reviews/` readiness evidence artifacts.

Current visible untracked inventory starting input:

RR-S7 must refresh `git status --short --branch` before execution. The current visible untracked inventory from this plan-fix preflight is only a starting input, not a classification:

```text
?? docs/code-wiki.md
?? docs/codewiki.md
?? docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
?? docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
?? docs/next-development-phaseflow.md
?? docs/reviews/code-review-20260623-033703.md
?? docs/reviews/evidence-confirm-productionization-release-readiness-plan-20260623.md
?? docs/reviews/evidence-confirm-productionization-release-readiness-plan-fix-20260623.md
?? docs/reviews/evidence-confirm-productionization-release-readiness-plan-review-controller-judgment-20260623.md
?? docs/reviews/plan-review-ds-evidence-confirm-release-readiness-20260623.md
?? docs/reviews/plan-review-mimo-evidence-confirm-release-readiness-20260623.md
?? docs/reviews/pr-40-review-mimo-ec-p3-20260622.md
?? docs/tmux-agent-memory-store.md
?? scripts/claude_mimo_simple.py
?? scripts/review-artifact.sh
```

Do not classify unrelated residue during this plan-fix. RR-S7 classification must be scoped to release/readiness blockers, generated readiness artifacts, and artifacts that could be mistaken for source truth, PR readiness, release evidence, or current implementation truth.

Validation commands:

```text
rg -n "release/readiness|NOT_READY|Evidence Confirm|checklist|annual-period|provider-backed|report-body" README.md fund_agent/README.md fund_agent/fund/README.md fund_agent/config/README.md tests/README.md docs/design.md docs/implementation-control.md docs/current-startup-packet.md
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py -q
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_quality_gate_integration.py tests/fund/template/test_renderer.py -q
git status --short --branch
git diff --check -- README.md fund_agent/README.md fund_agent/fund/README.md fund_agent/config/README.md tests/README.md docs/design.md docs/implementation-control.md docs/current-startup-packet.md docs/reviews/
```

Expected assertions:

- Docs state only accepted current behavior.
- Docs may describe accepted current behavior, but must not imply release readiness, production release, PR readiness, mark-ready eligibility, merge readiness, or merged state before RR-S8.
- No-live integration smoke exercises CLI -> Service -> Evidence Confirm -> quality gate -> CLI display -> report body non-rendering using no-live fixtures.
- Visible untracked residue is either out of scope with accepted disposition, ignored by policy, or promoted through review.
- Local ahead/remote PR-head state is explicitly dispositioned.

Stop conditions:

- Any unclassified untracked source-like or release evidence artifact remains.
- Any doc wants to turn future work into current fact.

### RR-S8 - PR-40 Mark-ready / Merge / Release Authorization Gate

Objective: separate local release readiness from external GitHub/release state mutation.

Allowed operations only after explicit user authorization:

- Push local accepted readiness/closeout commits if needed.
- Update PR body only if current PR body is stale.
- Mark PR-40 ready.
- Request reviewers.
- Merge PR-40.
- Create release/tag if separately authorized.

Required preflight:

```text
git branch --show-current
git status --short --branch
git rev-parse HEAD
git rev-parse origin/evidence-confirm-productionization
gh pr view 40 --json number,state,isDraft,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url,body
```

Local/remote reconciliation requirement:

- RR-S8 must explicitly reconcile local accepted commits and artifacts against PR-40 remote head `b59aed754c491adb05e533fde812b3ba93fa3f96`.
- Current known local accepted closeout/control commit is `89ccc44`; release/readiness plan, plan review, plan-fix, re-review, evidence, and closeout artifacts remain local-only until their own accepted gates complete.
- Local accepted release/readiness artifacts should enter PR-40 only after accepted gate plus explicit push authorization.
- If the intended PR-40 head remains `b59aed7`, document why local-only artifacts are not part of PR-40.
- If the intended PR-40 head includes `89ccc44` or later accepted release/readiness artifacts, push must be authorized and completed before mark-ready.
- Mark-ready cannot precede this reconciliation.

Expected assertions before mark-ready:

- PR head matches the intended accepted commit.
- CI `test` is success on the intended head.
- Merge state is `CLEAN`.
- PR body does not overclaim readiness evidence.
- No unclassified release blockers remain.
- User authorization explicitly names the allowed external action.

Stop conditions:

- PR head drift.
- CI missing/failing/pending.
- Merge state not clean.
- Local unpushed commit contains readiness evidence that should be part of PR but has not been authorized for push.
- User authorization is ambiguous.

## Authorization Boundaries

- Live source/PDF commands require explicit live evidence authorization.
- Provider/LLM commands require explicit provider authorization and must use redacted diagnostics.
- PR state changes require explicit user authorization per action: push, mark-ready, request reviewers, merge, release.
- Source fallback policy changes require a separate source/failure-class gate.
- Checklist default-on, annual-period developer policy, report-body rendering, provider default/budget, and release state each require separate reviewed gates.

## Residual Risk Routing

| Residual | Route |
|---|---|
| Multi-sample source/PDF failures | Source/PDF evidence gate; ambiguous failure categories route to source failure-class gate |
| Provider semantic instability | Provider semantic evidence gate; deterministic V2 remains authoritative |
| Checklist UX/product ambiguity | Checklist Evidence Confirm CLI/support gate |
| Annual-period summary visibility | Annual-period CLI summary display gate |
| Report-body wording/product ambiguity | Renderer/product decision gate |
| Local ahead/untracked residue | Docs/control/hygiene readiness gate |
| PR body/head drift | PR external-state authorization gate |
| Full field correctness/golden/parser readiness | Out of scope; route to extractor/golden/parser-specific gates |

## Why This Is Not Over-designed

- The plan does not introduce a new release framework, schema, source kind, parser, or provider default.
- It keeps proof layers separate: no-live deterministic regression, live source/PDF proof, provider semantic proof, product UX decisions, docs sync, and PR external-state mutation.
- It reuses existing Fund runner, Service summary, ECQ projection, CLI summary, and current gateflow artifact discipline.
- It allows deliberate deferral for checklist/report-body only through explicit owner disposition, not by silently omitting blockers.
- It avoids turning a single PR with clean CI into a readiness claim.

## Completion Report Format

Future implementation/evidence gates should close with:

```text
artifact path:
verdict token:
completed slices:
checks:
- <command> -> <key assertion>
release/readiness matrix:
- RR-01: met/not_met/deferred/requires_authorization
- RR-02: met/not_met/deferred/requires_authorization
- ...
remaining blockers:
- <blocker> -> <owner / next gate>
authorization boundary:
- no push/mark-ready/merge/release performed, or exact authorized action performed with PR state evidence
next gate:
```

This planning gate completion token is `PLAN_FIXED_READY_FOR_REREVIEW_NOT_READY`.
