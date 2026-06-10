# Controlled Live EID Failure-Branch Evidence Gate Plan - 2026-06-10

## Gate

- Gate: `controlled live EID failure-branch evidence gate`
- Classification: `heavy`
- User authorization: explicit authorization to enter this gate after accepted downstream integration implementation checkpoint `c3b9061` and control sync `d65a7b7`
- Current status: plan-first; no live command has run in this gate

## Objective

Observe the current EID single-source annual-report path under one bounded live acquisition window and record whether a natural live failure occurs.

This gate does not attempt to force EID failures. If the live command succeeds, the evidence only proves that no natural failure branch was observed during the bounded window. It must not be described as live proof for `not_found`, `unavailable`, `schema_drift`, `identity_mismatch` or `integrity_error`.

## Current Truth

- Current production annual-report source policy is EID single-source:
  - `selected_source=eid`
  - `mode=single_source_only`
  - `fallback_enabled=false`
- Eastmoney, CNINFO, fund-company official website/CDN and other non-EID routes remain deferred source candidates or historical evidence routes only.
- Accepted no-live EID failure-branch evidence already proves code behavior for:
  - `not_found`
  - `unavailable`
  - `schema_drift`
  - `identity_mismatch`
  - `integrity_error`
- Small-golden rows already have accepted live EID/FDR acquisition proof for happy-path acquisition and parser viability.
- This gate can add value only if the real EID endpoint naturally produces a failure during the authorized observation.

## Live Authorization Boundary

Authorized only after this plan is reviewed and accepted by controller judgment:

- One EID network/PDF acquisition attempt for the selected row.
- `FundDocumentRepository.load_annual_report()` as the only annual-report access boundary.
- Temporary cache directories for PDF and parsed document cache.
- Safe scalar evidence retention in a Markdown artifact.

Still forbidden:

- No fallback invocation.
- No Eastmoney, CNINFO, fund-company official website/CDN or other non-EID source construction.
- No source-policy, config, provider/default/runtime/budget, Service, Host, Agent, extractor, renderer, checklist, quality gate, golden/readiness, score-loop or source/test code change.
- No provider, LLM, endpoint probe, curl, DNS manipulation, socket probe outside the repository command path, network sabotage or induced outage.
- No fake-fund live request, parameter fuzzing, multi-row sweep, retry loop, weekly CI, cron, recurring live check, push, PR, merge or mark-ready.

## Selected Live Row

Primary row:

- `fund_code=006597`
- `report_year=2024`
- `document_kind=annual_report`

Reason:

- `006597 / 2024` is one of the five accepted small-golden rows with prior live EID/FDR happy-path proof.
- It is sufficient for one bounded observation and avoids expanding into a live sweep.
- A success outcome is expected but not treated as failure-branch proof.

No fallback row is authorized.

## Command Shape

The live command must:

- instantiate `EidAnnualReportSource` with a temporary PDF cache directory;
- instantiate `AnnualReportSourceOrchestrator` with exactly one source: the EID source;
- instantiate `AnnualReportPdfAdapter` with that orchestrator;
- instantiate `FundDocumentRepository` with that adapter;
- configure the repository instance parsed-document cache under a temporary directory by replacing that instance's `_cache` with `AnnualReportDocumentCache(root_dir=...)`; this is a gate-local cache-isolation step because production `FundDocumentRepository` has no public parsed-cache injection parameter;
- call exactly one `await repository.load_annual_report("006597", 2024, force_refresh=True)`;
- print only safe scalar metadata, report key, section/table counts and exception classification;
- retain no PDF bytes, no raw parsed text and no full report text in review artifacts.

The command must not:

- call `FundDataExtractor`;
- call `fund-analysis analyze`, `fund-analysis checklist`, renderer, Service, Host, UI or LLM path;
- instantiate or import `EastmoneyAnnualReportSource`;
- construct `AnnualReportSourceOrchestrator` with more than one source;
- persist PDF contents, raw text or full parsed report text in the artifact.

## Outcome Matrix

| Outcome | Controller classification | Evidence meaning | Continuation |
|---|---|---|---|
| live acquisition succeeds | `accepted_live_window_no_failure_observed` | EID/FDR happy path worked during the window; no live failure branch was observed. This does not mean live failure-branch proof was accepted | Stop |
| natural `unavailable` | `accepted_live_unavailable_observed` only if category is directly evidenced | The real endpoint naturally produced an availability failure; preserve exception type/category | Stop |
| natural `not_found` | `blocked_live_not_found_observed` | Unexpected for a known-good row; record category and stop for manual review | Stop |
| natural `schema_drift` | `blocked_live_schema_drift_observed` | EID response contract may have drifted; fail closed | Stop |
| natural `identity_mismatch` | `blocked_live_identity_mismatch_observed` | EID returned contradictory identity; fail closed | Stop |
| natural `integrity_error` | `blocked_live_integrity_error_observed` | EID PDF/integrity path failed; fail closed | Stop |
| environment/tooling failure | `blocked_environment` | Local environment prevented controlled observation | Stop |
| fallback/non-EID source observed | `blocked_policy_violation` | Contradicts current source policy or command boundary | Stop |

## Residual Semantics

- `schema_drift`, `identity_mismatch` and `integrity_error` are not realistically observable under controlled live conditions unless EID naturally misbehaves.
- `not_found` would require changing live parameters or selecting an absent row; that is not authorized here.
- `unavailable` is the only failure category plausibly observable in a short live window.
- If the command succeeds, all live failure branches remain unproven as live endpoint behavior.
- The no-live evidence at checkpoint `ac6bbe9` remains the accepted proof for all five categories (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`). This live gate cannot replace or upgrade that proof regardless of outcome.

## Evidence Artifact

Write:

- `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`

The artifact must include:

- exact command;
- exit code;
- safe stdout/stderr summary;
- report key if successful;
- scalar source metadata if successful:
  - `source`
  - `selected_source`
  - `source_mode`
  - `fallback_enabled`
  - `fallback_used`
  - `primary_failure_category`
  - `identity_status`
  - `integrity_status`
- section/table counts if successful;
- exception type and mapped category if failed;
- explicit no-fallback/no-non-EID/no-provider/no-LLM/no-golden/no-readiness statement;
- explicit statement that success is not live failure-branch proof.

## Validation

Before live command:

```bash
git status --short
git status --branch --short
```

EID single-source acquisition has no API key, env var or typed config dependency. E1 provider readiness is not applicable.

Live command:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

The helper script is gate-local, review-scoped and does not change package runtime behavior. It must be reviewed before the live command runs. No inline fallback command is authorized.

After live command:

```bash
git status --short
git status --branch --short
git diff --check
```

No pytest is required unless tracked source/test files are changed. This gate should not change source/test files.

## Review Routing

Plan review:

- AgentDS: review source-policy boundary, failure-branch semantics and stop conditions.
- AgentMiMo: review live authorization boundary, evidence retention and overclaim risk.

Evidence review after live command:

- AgentDS: verify evidence follows the accepted plan and no fallback/source bypass occurred.
- AgentMiMo: verify outcome classification, safe retention and residual wording.

## Stop Conditions

Stop before live command if:

- plan review is missing or blocking;
- controller judgment has not accepted the plan;
- command requires source/test/runtime/config changes;
- exact command cannot be represented as one bounded acquisition attempt;
- workspace has staged changes or unrelated modified tracked files;
- user authorization scope becomes ambiguous.

Stop during/after live command if:

- any non-EID source is instantiated or observed;
- fallback is invoked;
- more than one live acquisition attempt would be needed;
- EID returns any failure category; record the classification per the outcome matrix, then stop;
- stdout/stderr cannot be captured safely;
- raw PDF bytes, raw text, API secrets or full parsed report text would be retained;
- evidence would imply weekly live CI, recurring probes or fallback reauthorization.

## Completion Report Format

Final closeout must report:

- plan artifact path;
- plan review artifact paths;
- controller plan judgment path;
- live evidence artifact path, if execution proceeds;
- evidence review artifact paths;
- exact validation commands and results;
- final classification;
- residuals;
- next entry recommendation.
