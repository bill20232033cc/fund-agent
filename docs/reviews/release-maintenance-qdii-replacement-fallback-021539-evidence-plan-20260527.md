# QDII Replacement Fallback Candidate Evidence Plan - 021539 / 2024

> Date: 2026-05-27
> Worker: AgentCodex planning worker, not controller, not evidence runner
> Gate: `QDII replacement fallback candidate evidence plan gate for 021539`
> Scope: plan artifact only. No evidence run.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement post-019172 disposition decision accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback candidate evidence plan gate for 021539; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement fallback candidate evidence plan gate for 021539` |
| Latest accepted checkpoint before this task | `bdae33c docs: accept qdii post 019172 disposition` |
| Accepted post-019172 controller judgment | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-controller-judgment-20260527.md` |
| Accepted post-019172 decision artifact | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-20260527.md` |
| Accepted enumeration plan | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |

This plan follows the Startup Packet next entry point. It is not a gate switch. This worker is producing only the requested plan artifact; the controller remains responsible for tmux handoff, independent reviews, controller judgment, control-doc update after acceptance, and any later evidence authorization.

The `init-agents` requirement is preserved for review and any later evidence gate: the controller must use tmux pane discovery before dispatching DS / GLM plan reviews or any later worker handoff.

## 2. Truth-Source Check And Candidate Selection

No truth-source contradiction was found in the required sources. The accepted post-019172 disposition decision selects exactly one next plan-first fallback candidate from the accepted enumeration order: `021539` / 2024.

The single planned fallback evidence candidate is:

| Field | Value |
|---|---|
| `fund_code` | `021539` |
| `report_year` | `2024` |
| Fund name from accepted enumeration plan | `华安法国CAC40ETF发起式联接(QDII)A` |
| CSV category from accepted enumeration plan | `海外股票类` |
| Planned role | one bounded fallback QDII replacement evidence candidate |
| Selection basis | accepted post-019172 disposition after `096001`, `040046`, and `019172` all became quality-blocked after eligible provenance |
| Current source provenance state before evidence | `provenance_unknown` |
| Current quality state before evidence | `quality_unknown` |
| Promotion state before evidence | `promotion_disposition=not_promoted` |

This plan does not make `021539` source-safe, scoring-ready, baseline-ready, golden-ready, accepted as a replacement, promoted, or approved for durable corpus use. A later evidence gate must prove public source provenance first, then interpret quality. It must not infer source safety from fund name, CSV category, candidate order, command success, or any other indirect signal.

## 3. Preserved Accepted States

The accepted states for prior candidates are preserved and must not be rerun, weakened, or reinterpreted in this plan gate.

| fund_code | report_year | Source provenance | Quality state | Terminal classification | Promotion state | Accepted blockers / residuals |
|---|---|---|---|---|---|---|
| `096001` | `2024` | eligible complete public fallback provenance; `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback` | `quality_gate_status=block` | `quality_blocked_after_provenance` | `promotion_disposition=not_promoted` | P0 `nav_benchmark_performance`; FQ4 missing-field-rate `42.9%`; P1 gaps including `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`; `manager_strategy_text` passed |
| `040046` | `2024` | eligible complete public fallback provenance; `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback` | `quality_gate_status=block` | `quality_blocked_after_provenance` | `promotion_disposition=not_promoted` | FQ4 missing-field-rate `35.7%` with P0 pass; P1 gaps including `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`; `manager_strategy_text` passed |
| `019172` | `2024` | eligible complete public fallback provenance; `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback` | `quality_gate_status=block`; `issue_count=9` | `quality_blocked_after_provenance` | `promotion_disposition=not_promoted` | P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%`; FQ4 missing-field-rate `35.7%`; P1 gaps `turnover_rate`, `holdings_snapshot`, `share_change` |

These accepted states mean `096001`, `040046`, and `019172` are source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted. This plan only prepares the next single-candidate evidence gate for `021539` / 2024.

## 4. Plan-Gate Prohibitions

This plan gate must not run evidence. It must not run:

- `fund-analysis extraction-snapshot`;
- `fund-analysis extraction-score`;
- `fund-analysis quality-gate`;
- `fund-analysis analyze`;
- `fund-analysis checklist`;
- any `fund-analysis --help` or subcommand `--help` command in this planning task.

This plan gate also must not run or prepare contingency execution for `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, or `019172`.

## 5. Planned Public CLI Preflight

The future evidence runner must verify current CLI flags before executing evidence commands. This artifact plans the expected public command surface only; it does not authorize running these commands in this plan gate.

Planned preflight commands for the later evidence gate:

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

## 6. Planned Evidence Commands

These commands are future evidence commands only. This artifact does not authorize running them in this plan gate.

Run id and ignored output directory convention:

| Field | Planned value |
|---|---|
| Run id | `qdii-replacement-fallback-021539-2024-20260527` |
| Ignored output directory | `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527` |
| Tracked future summary artifact | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-20260527.md` |

Planned public commands:

```bash
uv run fund-analysis extraction-snapshot \
  --run-id qdii-replacement-fallback-021539-2024-20260527 \
  --report-year 2024 \
  --fund-code 021539 \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527 \
  --force-refresh
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/errors.jsonl`

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527 \
  --errors-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/errors.jsonl
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/golden_set.json`

```bash
uv run fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/score.json \
  --output-dir reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/quality_gate.md`

The future evidence artifact must record exact commands and exit codes. A non-zero exit code from any public CLI command must stop the run, preserve generated ignored paths if any, and classify the row as not promoted.

## 7. Generated-Output Provenance Reading

The future runner must read public provenance from generated output files, not from CLI stdout alone.

Required public files to inspect after snapshot success:

- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl`

The future evidence artifact must record whether each file exists and where each provenance field was read from. If stdout and generated files disagree, the generated public files control, and the discrepancy must be recorded for controller review.

Required public provenance tuple:

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

## 8. Source Provenance Stop Checks

Source provenance must be interpreted before score, quality status, replacement usefulness, or any promotion language.

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
- command success without public provenance fields;
- stdout-only provenance interpretation without reading generated `summary.md` and `snapshot.jsonl`.

If provenance is missing or unknown, the terminal classification should be `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted`, depending on the public output wording. The row remains `promotion_disposition=not_promoted`.

## 9. Quality Stop Checks

Quality interpretation is allowed only after source provenance reaches an eligible state. The future evidence artifact must then record:

- `quality_gate_status`;
- score status and field issue counts if public score output exposes them;
- all P0 issues;
- all P1 issues;
- the exact `manager_strategy_text` field status, issue severity, missing reason, traceability status, and any public evidence anchor state;
- FQ4 missing-field-rate status and threshold relationship;
- any public false-positive suspicion, with reason and required next action.

P0 handling:

- If `manager_strategy_text` is P0-blocking, stop and classify as `quality_blocked_after_provenance` when source provenance is eligible.
- If `manager_strategy_text` is missing because public disclosure genuinely lacks manager strategy discussion, classify as `disclosure_data_gap_not_baseline_ready` only when the public evidence supports that conclusion.
- If quality blocks P0 before provenance is eligible, do not use `quality_blocked_after_provenance`; classify by provenance first.
- If any other P0 block appears, record the exact rule/field and keep `promotion_disposition=not_promoted`.

FQ4 / non-P0 structural quality handling:

- If source provenance is eligible, P0 passes, and quality blocks on FQ4 missing-field-rate or another non-P0 structural quality rule, classify as `quality_blocked_after_provenance`.
- This row remains explicit because accepted `040046` evidence had P0 pass but quality blocked on FQ4; future `021539` evidence must not treat P0 pass as replacement readiness.

P1 handling:

- P1 issues may allow a `warn` result but must remain visible in the summary.
- P1 issues cannot be hidden by the fallback-candidate framing.
- A future durable-baseline gate, not this evidence gate, would be required to decide whether any P1 residual is acceptable.

False-positive handling:

- The future evidence artifact may record `false_positive_suspicion=true` only when public generated outputs provide a concrete reason.
- False-positive suspicion does not authorize code, extractor, taxonomy, source strategy, renderer, FQ0-FQ6, or quality-gate changes in this evidence path.
- If suspicion exists, the artifact must record the required next action as a separate future diagnosis/fix gate, with `promotion_disposition=not_promoted`.

## 10. Terminal-State Matrix

Every terminal state in this evidence gate keeps `promotion_disposition=not_promoted`. A future durable-baseline gate is the only gate that may change promotion disposition.

| Condition | Terminal classification | promotion_disposition | Required next action |
|---|---|---|---|
| CLI help flag mismatch before execution | `cli_flag_mismatch_not_run` | `not_promoted` | Update evidence plan or CLI command plan after controller review. |
| Snapshot command non-zero exit | `snapshot_command_failed_not_promoted` | `not_promoted` | Record exit code, stderr summary if available, generated paths, and stop. |
| Public snapshot outputs missing after zero exit | `snapshot_outputs_missing_not_promoted` | `not_promoted` | Record missing paths and stop before provenance or score. |
| Public provenance missing or incomplete | `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted` | `not_promoted` | Do not infer eligibility; controller decides whether to open a new disposition gate. |
| Public provenance shows `schema_drift`, `identity_mismatch`, or `integrity_error` | `source_fail_closed_not_promoted` | `not_promoted` | Stop fail-closed; do not fallback or continue. |
| Public provenance shows ineligible or unknown fallback category | `source_not_eligible_not_promoted` | `not_promoted` | Stop; do not treat as eligible. |
| Score command non-zero exit after provenance eligibility | `score_command_failed_not_promoted` | `not_promoted` | Record exit code, generated snapshot paths, and stop before quality gate. |
| Quality-gate command non-zero exit after score success | `quality_gate_command_failed_not_promoted` | `not_promoted` | Record exit code, score path, and stop. |
| Provenance eligible, quality P0 block on `manager_strategy_text` | `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready` | `not_promoted` | Record public evidence basis and required next action; do not promote. |
| Provenance eligible, quality P0 block on another field | `quality_blocked_after_provenance` | `not_promoted` | Record exact field/rule and next action. |
| Provenance eligible + FQ4 or other non-P0 structural quality block + P0 pass | `quality_blocked_after_provenance` | `not_promoted` | Record FQ4/non-P0 rule, threshold/evidence basis, and P0 pass; do not promote. |
| Provenance eligible, quality `warn` with P1 residuals only | `candidate_public_evidence_warn_not_promoted` | `not_promoted` | Controller review decides whether a later durable-baseline plan is justified. |
| Provenance eligible, quality `pass` | `candidate_public_evidence_pass_not_promoted` | `not_promoted` | Still not promoted; controller may open a separate durable-baseline gate. |

## 11. Hard Stop After Later 021539 Evidence

If a later accepted `021539` evidence gate quality-blocks after eligible provenance, automatic QDII probing stops. The next step must be a new disposition gate that chooses between QDII extraction/applicability diagnosis, taxonomy / asset-class fitness, or recording QDII coverage as blocked.

This hard stop means the process must not automatically continue to `020712`, active QDII, QDII-FOF, `013308`, bond QDII, or any later candidate after a reviewed `021539` quality block.

## 12. Exclusions And Contingency Boundaries

This plan authorizes no contingency evidence execution. It only plans `021539` / 2024 as the next single candidate after `096001`, `040046`, and `019172` all quality-blocked.

Preserved exclusions:

- `017641` remains excluded because accepted evidence classified it as complete eligible fallback provenance but quality-blocked / not promoted; it must not be rerun in this gate.
- QDII-FOF candidates remain excluded unless a taxonomy gate accepts QDII-FOF for this replacement slot.
- `013308` remains pending because its QDII name conflicts with CSV category `国内股票类`; it must not enter evidence before a future taxonomy/controller decision resolves the conflict.
- Bond QDII candidates remain asset-class fitness pending and require controller acceptance before evidence.

This plan does not decide taxonomy, asset-class fitness, QDII-FOF eligibility, `013308`, bond QDII, baseline/golden status, durable corpus state, clean denominator status, or accepted replacement status.

## 13. Future Evidence Artifact Expectations

The future tracked evidence summary for `021539` must include:

- Startup Packet replay and statement that it follows the accepted next entry point, not a gate switch.
- Candidate identity: `021539`, `2024`, accepted enumeration row identity, CSV path, and run id `qdii-replacement-fallback-021539-2024-20260527`.
- The pre-evidence state: `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted`.
- Preserved accepted states for `096001`, `040046`, and `019172`: source-provenance eligible, quality gate `block`, terminal `quality_blocked_after_provenance`, `promotion_disposition=not_promoted`.
- Preflight help command results and exact flag verification outcome.
- Exact public commands executed and exit codes.
- Generated ignored paths.
- Public provenance tuple read from generated `summary.md` and `snapshot.jsonl`, not stdout-only.
- Provenance stop-check decision before score, quality, or promotion interpretation.
- Quality status.
- P0 issues and P1 issues.
- FQ4 / non-P0 structural quality block status, including the explicit P0-pass case if it occurs.
- `manager_strategy_text` status, issue severity, evidence anchor state, and root-cause classification if relevant.
- False-positive suspicion, if any, plus evidence basis and required next action.
- Terminal classification from this plan's terminal-state matrix.
- `promotion_disposition=not_promoted`.
- Confirmation that no later fallback candidate was run.
- Confirmation that no direct PDF/cache/source-helper/downloader/source-adapter inspection or external web access was used.
- Confirmation that no code, tests, renderer, FQ0-FQ6, Service/CLI defaults, source strategy, taxonomy, extractor, Host/Agent/dayu, fixtures, reports promotion, design doc, or control doc were changed by the evidence worker.
- If quality blocks after eligible provenance, explicit statement that automatic QDII probing stops and a new disposition gate is required.
- `git diff --check` result.

## 14. Review Matrix

The controller must use `init-agents` / tmux discovery before actual handoff. This planning worker did not dispatch agents.

Required review sequence:

| Stage | Agent | Required artifact |
|---|---|---|
| Plan review 1 | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-review-ds-20260527.md` |
| Plan review 2 | AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-review-glm-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-controller-judgment-20260527.md` |
| Control-doc update after acceptance | Controller | `docs/implementation-control.md` Startup Packet / Current Gate / Active Gate Ledger update after accepted judgment only |

Review focus:

- confirm this is plan-only and does not run evidence;
- confirm this follows the Startup Packet next entry point, not a gate switch;
- confirm `021539` / 2024 is the only planned fallback candidate and remains `provenance_unknown` / `quality_unknown` / `not_promoted` before evidence;
- confirm `096001`, `040046`, and `019172` accepted states are preserved as source-provenance eligible, quality-blocked, terminal `quality_blocked_after_provenance`, and not promoted;
- confirm no `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, or `019172` run is authorized;
- confirm public CLI command plan uses explicit paths and has help/flag mismatch stop behavior;
- confirm future evidence reads generated `summary.md` and `snapshot.jsonl`, not stdout-only;
- confirm source provenance is checked before score, quality, or promotion interpretation;
- confirm fail-closed source categories `schema_drift`, `identity_mismatch`, and `integrity_error` stop the evidence path;
- confirm fallback is eligible only for `not_found` / `unavailable` with public `fallback_eligibility=eligible` and complete public provenance;
- confirm the terminal matrix includes CLI mismatch, snapshot fail, missing outputs, provenance incomplete, fail-closed source, ineligible fallback, score fail, quality gate fail, P0 block, FQ4/non-P0 block including the P0-pass case, warn-only, and pass;
- confirm the hard stop after a later accepted `021539` quality block prevents automatic QDII probing;
- confirm `017641`, QDII-FOF, `013308`, and bond QDII exclusions are preserved;
- confirm no code/test/product-flow/source-helper/taxonomy/renderer/golden/baseline changes or promotions are authorized.

## 15. Stop Conditions And Non-Goals

Stop conditions for this plan gate:

- do not run evidence;
- do not run `fund-analysis extraction-snapshot`;
- do not run `fund-analysis extraction-score`;
- do not run `fund-analysis quality-gate`;
- do not run `fund-analysis analyze`;
- do not run `fund-analysis checklist`;
- do not run any `fund-analysis --help` command in this planning task;
- do not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, `019172`, or any later fallback candidate in this plan gate;
- do not inspect PDFs, cache, source-helper outputs, downloader outputs, source-adapter outputs, or external web;
- do not infer provenance from indirect evidence;
- do not edit `docs/implementation-control.md`, `docs/design.md`, production code, tests, README, fixtures, reports, or generated ignored outputs;
- do not change renderer, FQ0-FQ6, Service, CLI, default behavior, `FundDocumentRepository`, source strategy, source-helper fallback semantics, taxonomy, extractor, Host, Agent, Dayu, golden files, baseline fixtures, or corpus state;
- do not promote any candidate to durable baseline, clean denominator, fixture, report-quality corpus, golden answer corpus, accepted replacement, source-safe state, or scoring-ready state;
- do not commit, push, open PR, merge, delete branch, or mutate GitHub state.

Non-goals:

- no durable-baseline decision;
- no scoring-ready decision;
- no golden answer corpus decision;
- no accepted replacement decision;
- no taxonomy conflict resolution;
- no QDII-FOF acceptance;
- no bond QDII asset-class fitness decision;
- no QDII extraction/applicability diagnosis.

## 16. Plan-Gate Validation

Only the following validation is required for this plan gate:

| Command | Required result |
|---|---|
| `git diff --check` | pass |
