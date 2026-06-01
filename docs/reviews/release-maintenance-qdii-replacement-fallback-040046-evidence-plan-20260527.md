# QDII Replacement Fallback Candidate Evidence Plan - 040046 / 2024

> Date: 2026-05-27
> Worker: AgentCodex planning worker, not controller, not evidence runner
> Gate: `QDII replacement fallback candidate evidence plan gate for 040046`
> Scope: plan artifact only. No evidence run.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement candidate evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback candidate evidence plan gate for 040046; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement fallback candidate evidence plan gate for 040046` |
| Latest accepted checkpoint before this task | `c6a5042 docs: accept qdii replacement evidence` |
| Accepted enumeration plan | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` |
| Accepted enumeration controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-controller-judgment-20260527.md` |
| Accepted candidate evidence controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-controller-judgment-20260527.md` |
| Accepted candidate evidence | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Next Entry Point |

This plan follows the Startup Packet next entry point. It is not a gate switch. This worker is producing only the requested plan artifact; the controller remains responsible for tmux handoff, independent reviews, judgment, control-doc update after acceptance, and any later evidence authorization.

## 2. Truth-Source Check And Candidate Selection

No truth-source contradiction was found in the required sources. If a contradiction is later found between `AGENTS.md`, `docs/design.md`, the Startup Packet, the accepted enumeration artifacts, or the accepted `096001` evidence artifacts, the controller must stop this fallback path and document the contradiction instead of silently selecting another candidate.

The single planned fallback evidence candidate is:

| Field | Value |
|---|---|
| `fund_code` | `040046` |
| `report_year` | `2024` |
| Fund name from accepted enumeration plan | `华安纳斯达克100ETF联接(QDII)A` |
| CSV category from accepted enumeration plan | `海外股票类` |
| Planned role | one bounded fallback QDII replacement evidence candidate |
| Selection basis | accepted enumeration fallback order after `096001` quality-blocked |
| Current source provenance state | `provenance_unknown` |
| Current quality state | `quality_unknown` |
| Promotion state | `promotion_disposition=not_promoted` |

This plan selects `040046` / 2024 because the accepted enumeration fallback order was `096001`, then `040046`, then `019172`, then remaining eligible equity QDII rows, and accepted evidence has now quality-blocked `096001`.

This plan does not make `040046` source-safe, scoring-ready, baseline-ready, golden-ready, accepted as a replacement, promoted, or approved for durable corpus use. The later evidence gate must prove public source provenance first, then interpret quality. It must not infer source safety from fund name, CSV category, candidate order, command success, or any indirect signal.

## 3. Preserved 096001 Accepted State

The accepted state for `096001` / 2024 is preserved and must not be rerun in this fallback plan gate.

| Field | Accepted state |
|---|---|
| `fund_code` | `096001` |
| `report_year` | `2024` |
| Source provenance | eligible complete public fallback provenance |
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| Quality state | `quality_gate_status=block` |
| Terminal classification | `quality_blocked_after_provenance` |
| Promotion state | `promotion_disposition=not_promoted` |

Accepted blockers for `096001` include P0 `nav_benchmark_performance`, FQ4 missing-field-rate, and P1 gaps. `manager_strategy_text` passed in the accepted `096001` evidence and is not the blocker there. This plan must not weaken or reopen that accepted state.

## 4. Planned Public CLI Preflight

The future evidence runner must verify current CLI flags before executing evidence commands. This artifact plans the expected public command surface only; it does not authorize running these commands in this plan gate.

Planned preflight commands:

```bash
uv run fund-analysis extraction-snapshot --help
uv run fund-analysis extraction-score --help
uv run fund-analysis quality-gate --help
```

Preflight acceptance criteria:

- `extraction-snapshot` still exposes public options equivalent to `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, and `--force-refresh`.
- `extraction-score` still exposes public options equivalent to `--snapshot-path`, `--source-csv`, `--output-dir`, and `--errors-path`.
- `quality-gate` still exposes public options equivalent to `--score-path` and `--output-dir`.
- Help output must not be treated as evidence about fund data, source provenance, extraction quality, or promotion readiness.
- If any flag has changed, the runner must stop and record `terminal_classification=cli_flag_mismatch_not_run`, `promotion_disposition=not_promoted`, and the exact mismatch in the tracked evidence summary.

## 5. Planned Evidence Commands

These commands are planned only. This artifact does not authorize running them.

Run id and ignored output directory convention:

| Field | Planned value |
|---|---|
| Run id | `qdii-replacement-fallback-040046-2024-20260527` |
| Ignored output directory | `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527` |
| Tracked future summary artifact | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md` |

Planned public commands:

```bash
uv run fund-analysis extraction-snapshot \
  --run-id qdii-replacement-fallback-040046-2024-20260527 \
  --report-year 2024 \
  --fund-code 040046 \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527 \
  --force-refresh
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/errors.jsonl`

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527 \
  --errors-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/errors.jsonl
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/golden_set.json`

```bash
uv run fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.md`

The future evidence artifact must record exact commands and exit codes. A non-zero exit code from any public CLI command must stop the run, preserve generated ignored paths if any, and classify the row as not promoted.

## 6. Generated-Output Provenance Reading

The future runner must read public provenance from generated output files, not from CLI stdout alone.

Required public files to inspect after snapshot success:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`

The future evidence artifact must record whether each file exists and where each provenance field was read from. If stdout and generated files disagree, the generated public files control, and the discrepancy must be recorded for controller review.

## 7. Source Provenance Stop Checks

Source provenance must be interpreted before quality status, replacement usefulness, or any promotion language.

The future evidence artifact must record this public provenance tuple:

| Field | Required recording |
|---|---|
| `source_provenance_schema_version` | exact public value if exposed |
| `source_strategy` | exact public value |
| `resolved_source` / `resolved_source_name` | exact public value |
| `fallback_used` | exact public value |
| `primary_failure_category` | exact public value, including null/missing |
| `fallback_eligibility` | exact public value |
| `source_provenance_status` | exact public value |
| `source_provenance_reason` | exact public value if exposed |

Fail-closed categories:

- `schema_drift`
- `identity_mismatch`
- `integrity_error`

If any fail-closed category appears in public provenance, the future evidence run must stop before score/quality interpretation and record `terminal_classification=source_fail_closed_not_promoted`.

Eligible provenance requires one of:

- primary source success with no fallback and complete public provenance; or
- fallback with `primary_failure_category` exactly `not_found` or `unavailable`, public `fallback_eligibility=eligible`, and complete public provenance.

The following are not eligible and must not be treated as fallback permission:

- missing `primary_failure_category`;
- missing or incomplete public provenance tuple;
- `fallback_used=true` with unknown or absent fallback category;
- `fallback_eligibility` missing, unknown, or not eligible;
- unknown fallback category;
- source/provenance values visible only through PDF/cache/source-helper/downloader/source-adapter internals;
- command success without public provenance fields.

If provenance is missing or unknown, the terminal classification should be `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted`, depending on the public output wording. The row remains `promotion_disposition=not_promoted`.

## 8. Quality Stop Checks

Quality interpretation is allowed only after source provenance reaches an eligible state. The future evidence artifact must then record:

- `quality_gate_status`;
- score status and field issue counts if public score output exposes them;
- all P0 issues;
- all P1 issues;
- the exact `manager_strategy_text` field status, issue severity, missing reason, traceability status, and any public evidence anchor state;
- any public false-positive suspicion, with reason and required next action.

P0 handling:

- If `manager_strategy_text` is P0-blocking, stop and classify as `quality_blocked_after_provenance` when source provenance is eligible.
- If `manager_strategy_text` is missing because public disclosure genuinely lacks manager strategy discussion, classify as `disclosure_data_gap_not_baseline_ready` only when the public evidence supports that conclusion.
- If quality blocks P0 before provenance is eligible, do not use `quality_blocked_after_provenance`; classify by provenance first.
- If any other P0 block appears, record the exact rule/field and keep `promotion_disposition=not_promoted`.

P1 handling:

- P1 issues may allow a `warn` result but must remain visible in the summary.
- P1 issues cannot be hidden by the fallback-candidate framing.
- A future durable-baseline gate, not this evidence gate, would be required to decide whether any P1 residual is acceptable.

False-positive handling:

- The future evidence artifact may record `false_positive_suspicion=true` only when public generated outputs provide a concrete reason.
- False-positive suspicion does not authorize code, extractor, taxonomy, source strategy, renderer, FQ0-FQ6, or quality-gate changes in this evidence path.
- If suspicion exists, the artifact must record the required next action as a separate future diagnosis/fix gate, with `promotion_disposition=not_promoted`.

## 9. Terminal-State Matrix

Every terminal state in this evidence gate keeps `promotion_disposition=not_promoted`. A future durable-baseline gate is the only gate that may change promotion disposition.

| Condition | Terminal classification | promotion_disposition | Required next action |
|---|---|---|---|
| CLI help flag mismatch before execution | `cli_flag_mismatch_not_run` | `not_promoted` | Update evidence plan or CLI command plan after controller review. |
| Snapshot command non-zero exit | `snapshot_command_failed_not_promoted` | `not_promoted` | Record exit code, stderr summary if available, generated paths, and stop. |
| Public snapshot outputs missing after zero exit | `snapshot_outputs_missing_not_promoted` | `not_promoted` | Record missing paths and stop before provenance or score. |
| Public provenance missing or incomplete | `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted` | `not_promoted` | Do not infer eligibility; controller decides whether to plan another candidate. |
| Public provenance shows `schema_drift`, `identity_mismatch`, or `integrity_error` | `source_fail_closed_not_promoted` | `not_promoted` | Stop fail-closed; do not fallback or continue. |
| Public provenance shows ineligible or unknown fallback category | `source_not_eligible_not_promoted` | `not_promoted` | Stop; do not treat as eligible. |
| Score command non-zero exit after provenance eligibility | `score_command_failed_not_promoted` | `not_promoted` | Record exit code, generated snapshot paths, and stop before quality gate. |
| Quality-gate command non-zero exit after score success | `quality_gate_command_failed_not_promoted` | `not_promoted` | Record exit code, score path, and stop. |
| Provenance eligible, quality P0 block on `manager_strategy_text` | `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready` | `not_promoted` | Record public evidence basis and required next action; do not promote. |
| Provenance eligible, quality P0 block on another field | `quality_blocked_after_provenance` | `not_promoted` | Record exact field/rule and next action. |
| Provenance eligible, quality `warn` with P1 residuals only | `candidate_public_evidence_warn_not_promoted` | `not_promoted` | Controller review decides whether a later durable-baseline plan is justified. |
| Provenance eligible, quality `pass` | `candidate_public_evidence_pass_not_promoted` | `not_promoted` | Still not promoted; controller may open a separate durable-baseline gate. |

## 10. Fallback Contingency Planning

Fallback is only contingency planning in this gate. It does not authorize fallback execution beyond the planned `040046` evidence gate.

If `040046` fails in a later accepted evidence gate, the preserved contingency order is:

1. `019172`
2. remaining eligible equity QDII rows from the accepted enumeration table

This plan does not authorize `019172` evidence, any later equity QDII row, or any non-equity/QDII-FOF/conflict row. The controller must authorize a new plan before any additional fallback candidate evidence run.

Preserved exclusions:

- `017641` remains excluded because accepted evidence classified it as `disclosure_data_gap_not_baseline_ready` / `not_promoted`; it must not be rerun in this gate.
- QDII-FOF candidates remain excluded unless a taxonomy gate accepts QDII-FOF for this replacement slot.
- `013308` remains excluded until the QDII name vs `国内股票类` category conflict is resolved by a future taxonomy/controller gate.
- Bond QDII candidates require an asset-class replacement fitness gate before evidence.

## 11. Future Evidence Artifact Expectations

The future tracked evidence summary for `040046` must include:

- Startup Packet replay and statement that it follows the accepted next entry point, not a gate switch.
- Candidate identity: `040046`, `2024`, accepted enumeration row identity, CSV path, and run id `qdii-replacement-fallback-040046-2024-20260527`.
- Preflight help command results and exact flag verification outcome.
- Exact public commands executed and exit codes.
- Generated ignored paths.
- Public provenance tuple read from `summary.md` and `snapshot.jsonl`, not stdout-only.
- Provenance stop-check decision before quality interpretation.
- Quality status.
- P0 issues and P1 issues.
- `manager_strategy_text` status, issue severity, evidence anchor state, and root-cause classification if relevant.
- False-positive suspicion, if any, plus evidence basis and required next action.
- Terminal classification from this plan's terminal-state matrix.
- `promotion_disposition=not_promoted`.
- Confirmation that no `019172` or other fallback candidate was run.
- Confirmation that no direct PDF/cache/source-helper/downloader/source-adapter inspection or external web access was used.
- Confirmation that no code, tests, renderer, FQ0-FQ6, Service/CLI defaults, source strategy, taxonomy, extractor, Host/Agent/dayu, fixtures, reports promotion, design doc, or control doc were changed by the evidence worker.
- `git diff --check` result.

## 12. Review Matrix

The controller must use `init-agents` / tmux discovery before actual handoff. This planning worker did not dispatch agents.

Required review sequence:

| Stage | Agent | Required artifact |
|---|---|---|
| Plan review 1 | AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-review-mimo-20260527.md` |
| Plan review 2 | AgentDS or AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-review-ds-20260527.md` or `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-review-glm-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-controller-judgment-20260527.md` |
| Control-doc update after acceptance | Controller | `docs/implementation-control.md` Startup Packet / Current Gate / Active Gate Ledger update after accepted judgment only |

Review focus:

- confirm this is plan-only and does not run evidence;
- confirm this follows the Startup Packet next entry point, not a gate switch;
- confirm `040046` / 2024 is the only planned fallback candidate and remains `provenance_unknown` / `quality_unknown`;
- confirm `096001` accepted state is preserved and not rerun;
- confirm public CLI command plan uses explicit paths and has help/flag mismatch stop behavior;
- confirm provenance is read from generated public files and checked before quality or promotion interpretation;
- confirm fail-closed source categories stop;
- confirm missing/incomplete provenance or unknown fallback category is not eligible;
- confirm `manager_strategy_text` P0 quality handling;
- confirm every terminal state has `promotion_disposition=not_promoted`;
- confirm `019172` and later rows are contingency-only and exclusions are preserved;
- confirm no code/test/product-flow/source-helper/taxonomy/renderer/golden/baseline changes are authorized.

## 13. Stop Conditions And Non-Goals

Stop conditions for this plan gate:

- do not run evidence;
- do not run `fund-analysis extraction-snapshot`;
- do not run `fund-analysis extraction-score`;
- do not run `fund-analysis quality-gate`;
- do not run `fund-analysis analyze`;
- do not run `fund-analysis checklist`;
- do not run any `fund-analysis --help` command in this planning task;
- do not inspect PDFs, cache, source-helper outputs, downloader outputs, source-adapter outputs, or external web;
- do not infer provenance from indirect evidence;
- do not edit `docs/implementation-control.md`, `docs/design.md`, code, tests, README, fixtures, reports, or generated ignored outputs;
- do not change renderer, FQ0-FQ6, Service, CLI, default behavior, `FundDocumentRepository`, source-helper, taxonomy, extractor, Host, Agent, dayu, golden files, baseline fixtures, or corpus state;
- do not commit, push, open PR, merge, delete branch, or mutate GitHub state.

Non-goals:

- no durable-baseline decision;
- no scoring-ready decision;
- no golden answer corpus decision;
- no accepted replacement decision;
- no taxonomy conflict resolution;
- no QDII-FOF acceptance;
- no bond QDII asset-class fitness decision;
- no source strategy or fallback behavior redesign;
- no diagnosis or fix for `096001` quality blockers.

## 14. Validation For This Plan Gate

This plan gate validation is limited to:

```bash
git diff --check
```

No other validation, evidence command, fund-analysis command, help command, PDF/cache inspection, external web access, code execution for extraction, or CLI probing is part of this planning worker scope.
