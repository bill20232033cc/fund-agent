# QDII Replacement Candidate Selection Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker, not controller
> Gate: `QDII replacement candidate selection plan gate`
> Scope: plan artifact only. Do not run evidence. Do not edit code, tests, design, control doc, renderer, source strategy, or product behavior.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `replacement/exclusion candidate selection accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate selection plan gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement candidate selection plan gate` |
| Latest accepted checkpoint | `667eed6 docs: accept replacement candidate disposition` |
| Current truth | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Next Entry Point; accepted controller judgment `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` |
| Architecture boundary | Dayu four-layer target `UI -> Service -> Host -> Agent`; current deterministic path remains UI -> Service -> `fund_agent/fund` |

This is the Startup Packet next entry point, not a gate switch. This worker is producing the requested QDII replacement candidate selection plan only. The controller remains responsible for plan review handoff, controller judgment, and any later evidence authorization.

## 2. Accepted 017641 Disposition To Preserve

The prior accepted controller judgment fixes `017641` / 2024 as:

| Field | Accepted state |
|---|---|
| Fund code | `017641` |
| Report year | `2024` |
| Slot | `qdii_fund` |
| Source provenance | `complete`; `primary_failure_category=unavailable`; `fallback_eligibility=eligible` |
| Quality state | `block` |
| Terminal classification | `disclosure_data_gap_not_baseline_ready` |
| Candidate disposition | `replace` |
| Promotion disposition | `not_promoted` |

This plan must not reinterpret `017641` as an extractor gap or policy issue. The accepted reason for replacement is narrower: current public evidence proves a P0 `manager_strategy_text` disclosure data gap that is not baseline-ready, and the accepted gate did not authorize extractor work, quality-policy weakening, taxonomy change, or promotion.

## 3. QDII Replacement Selection Criteria

A replacement candidate is eligible for future evidence only if all criteria below are met before evidence starts:

| Criterion | Requirement |
|---|---|
| Fund type slot | Candidate must be `qdii_fund` by current public classification or be explicitly accepted by controller as a QDII slot. QDII-FOF candidates do not count unless a separate taxonomy gate accepts QDII-FOF for this slot. |
| Report year | Candidate must use the same `report_year=2024` scope as `017641`. |
| Candidate source identity | Candidate must come from `docs/code_20260519.csv` or an already accepted artifact/list that cites the same selected-fund source identity. |
| Evidence route | Future evidence must use public CLI paths only: `extraction-snapshot`, `extraction-score`, and `quality-gate`. |
| Source provenance | Candidate must have either primary source success or complete eligible fallback provenance. `schema_drift`, `identity_mismatch`, and `integrity_error` remain fail-closed and cannot fallback. Missing public provenance category is not eligible. |
| Quality | Candidate must have no P0 quality block. `manager_strategy_text` must not fail P0 unless a separate design/policy gate first accepts a different classification. |
| Promotion | Candidate is evidence candidate only. No durable baseline, clean denominator, scoring-ready fixture, golden answer corpus, or report-quality corpus promotion is allowed in this gate. |

Successful extraction or a populated snapshot is not evidence of source eligibility. Source eligibility must come from public source provenance fields.

## 4. Candidate Source Policy And Recommended Method

Approved inputs for candidate selection are bounded to:

- accepted existing candidate lists and accepted controller judgments;
- `docs/code_20260519.csv`;
- current accepted artifacts under `docs/reviews/`.

No web search, external browsing, ad hoc fund discovery, direct PDF/cache/source-helper inspection, source adapter probing, or unreviewed ignored report output may be used.

Current accepted artifacts do not provide a controller-approved QDII replacement candidate. Therefore the next gate must be a `QDII replacement candidate enumeration plan gate`, not direct evidence.

Recommended bounded enumeration method for that next gate:

1. Read `docs/code_20260519.csv` as the only candidate universe.
2. Keep only rows whose selected-fund identity plausibly belongs to overseas/QDII coverage and exclude the known failed candidate `017641`.
3. Exclude QDII-FOF rows unless a taxonomy gate has explicitly accepted QDII-FOF for this QDII replacement slot.
4. Produce a candidate-order table only, with no evidence run. Candidate-order rationale should prefer non-FOF QDII rows, clear QDII naming/source-csv identity, same report year 2024, and shortest future public evidence loop.
5. Require MiMo and DS/GLM independent plan review plus controller judgment before any candidate evidence command runs.

The bounded CSV-derived enumeration pool may include non-FOF overseas/QDII rows such as `019172`, `040046`, `096001`, `006282`, `539003`, `000614`, `021539`, `020712`, `007280`, `007360`, `100050`, and `013308`, but this list is not an approved replacement list. The enumeration gate must classify fund type and taxonomy eligibility through accepted public outputs or controller-approved slot decisions before selecting any evidence candidate.

## 5. Future Evidence Matrix

This gate does not run evidence. The commands below are future command shapes only, allowed after a reviewed and accepted enumeration/selection plan names one bounded candidate.

| Purpose | Future command shape | Output policy |
|---|---|---|
| Snapshot | `uv run fund-analysis extraction-snapshot --run-id qdii-replacement-<code>-2024-20260527 --report-year 2024 --fund-code <code> --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-<code>-2024-20260527` | Generated output stays ignored under `reports/extraction-snapshots/...`. |
| Score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/qdii-replacement-<code>-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/qdii-replacement-<code>-2024-20260527/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/qdii-replacement-<code>-2024-20260527` | Generated output stays ignored under `reports/scoring-runs/...`. |
| Quality gate | `uv run fund-analysis quality-gate --score-path reports/scoring-runs/qdii-replacement-<code>-2024-20260527/score.json --output-dir reports/quality-gate-runs/qdii-replacement-<code>-2024-20260527` | Generated output stays ignored under `reports/quality-gate-runs/...`. |
| Closeout validation | `git diff --check` | Required in the future evidence closeout. |

The future tracked summary artifact should be:

`docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`

That tracked summary must record exact commands, exit codes, ignored output paths, selected-fund source row identity, public source provenance tuple, quality status, P0/P1 issues, terminal classification, and `promotion_disposition=not_promoted`.

## 6. Stop Conditions

Stop and return to controller if any condition occurs:

- Candidate taxonomy is ambiguous, including QDII vs QDII-FOF ambiguity without an accepted taxonomy gate.
- Source provenance regresses, is missing, or cannot prove primary success / eligible fallback through public output.
- Any fail-closed source category appears: `schema_drift`, `identity_mismatch`, or `integrity_error`.
- Candidate has a P0 quality block.
- `manager_strategy_text` remains P0-blocking and no separate design/policy gate has reclassified that rule.
- Evidence requires direct PDF/cache/source-helper/downloader/source-adapter access.
- Evidence requires source strategy mutation, fallback semantic changes, or `FundDocumentRepository` changes.
- Evidence requires renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, extractor, taxonomy, or quality weakening work.
- Any worker attempts durable baseline, clean denominator, fixture, golden, report-quality corpus, or candidate promotion.
- A new unexplained P0/P1 issue appears.
- The proposed next step enters evidence without an accepted enumeration/selection plan and controller judgment.

## 7. Review Matrix

The controller must use `init-agents` tmux discovery before actual handoff. This planning worker does not dispatch agents.

| Stage | Agent | Required artifact |
|---|---|---|
| Plan review 1 | AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-review-mimo-20260527.md` |
| Plan review 2 | AgentDS or AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-review-ds-20260527.md` or `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-review-glm-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-controller-judgment-20260527.md` |
| Next gate if accepted | Planning worker | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` |

Review focus:

- Preserve Startup Packet next entry point and `017641` accepted disposition.
- Confirm no evidence commands are authorized by this plan.
- Confirm candidate source policy is bounded to accepted artifacts and `docs/code_20260519.csv`.
- Confirm absence of an approved replacement candidate leads to enumeration plan first.
- Confirm source fail-closed semantics, P0 quality discipline, no-promotion guardrails, and forbidden scope.

## 8. Explicit Non-Goals

This gate does not authorize:

- code changes;
- test changes;
- `docs/design.md` changes;
- `docs/implementation-control.md` changes;
- README or AGENTS changes;
- extraction, analyze, checklist, quality, source-probing, or evidence CLI runs;
- renderer, FQ0-FQ6, Service, CLI, source strategy, source helpers, `FundDocumentRepository`, Host, Agent, or Dayu work;
- direct PDF/cache/source-helper access;
- taxonomy implementation or policy changes;
- baseline, clean-denominator, scoring-ready, fixture, golden, report-quality corpus, or candidate promotion;
- commit, push, PR, merge, branch deletion, issue/comment, or other GitHub mutation.

## 9. Validation

Only final whitespace validation is allowed for this planning artifact.

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | 0 | passed |
