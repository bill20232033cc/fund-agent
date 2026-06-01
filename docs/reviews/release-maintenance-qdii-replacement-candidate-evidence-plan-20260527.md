# QDII Replacement Candidate Evidence Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker, not controller, not evidence runner
> Gate: `QDII replacement candidate evidence plan gate`
> Scope: plan artifact only. No evidence run.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement candidate enumeration plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate evidence plan gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement candidate evidence plan gate` |
| Latest accepted checkpoint before this task | `461ff08 docs: accept qdii replacement enumeration plan` |
| Accepted enumeration plan | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` |
| Accepted enumeration controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-controller-judgment-20260527.md` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Next Entry Point |

This plan follows the Startup Packet next entry point. It is not a gate switch. This worker is producing only the requested plan artifact; the controller remains responsible for tmux handoff, independent reviews, judgment, control-doc update after acceptance, and any later evidence authorization.

## 2. Candidate Selection

The single planned evidence candidate is:

| Field | Value |
|---|---|
| `fund_code` | `096001` |
| `report_year` | `2024` |
| Fund name from accepted enumeration plan | `大成标普500等权重指数(QDII)A人民币` |
| CSV category from accepted enumeration plan | `海外股票类` |
| Planned role | one bounded QDII replacement evidence candidate |
| Current source provenance state | `provenance_unknown` |
| Current quality state | `quality_unknown` |
| Promotion state | `promotion_disposition=not_promoted` |

No truth-source contradiction was found in the required sources. The accepted enumeration controller judgment states that `096001` / 2024 is accepted only as the single candidate for the next future evidence plan gate. It does not make `096001` source-safe, quality-passing, scoring-ready, baseline-ready, golden-ready, promoted, or accepted as a replacement.

This plan therefore treats `096001` as `provenance_unknown` and `quality_unknown`. The later evidence gate must prove public provenance first, then interpret quality. It must not infer source safety from name fit, CSV category, candidate order, or successful command execution alone.

## 3. Planned Public CLI Preflight

The future evidence runner must verify current CLI flags before executing evidence commands. This plan records the expected public command surface, but the runner must stop on help/flag mismatch instead of guessing.

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

## 4. Planned Evidence Commands

These commands are planned only. This artifact does not authorize running them.

Run id and ignored output directory convention:

| Field | Planned value |
|---|---|
| Run id | `qdii-replacement-candidate-096001-2024-20260527` |
| Ignored output directory | `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527` |
| Tracked future summary artifact | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md` |

Planned public commands:

```bash
uv run fund-analysis extraction-snapshot \
  --run-id qdii-replacement-candidate-096001-2024-20260527 \
  --report-year 2024 \
  --fund-code 096001 \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527 \
  --force-refresh
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/errors.jsonl`

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl \
  --source-csv docs/code_20260519.csv \
  --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527 \
  --errors-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/errors.jsonl
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/golden_set.json`

```bash
uv run fund-analysis quality-gate \
  --score-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.json \
  --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527
```

Expected generated ignored paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/quality_gate.md`

The future runner must record exact commands and exit codes in the tracked summary. A non-zero exit code from any public CLI command must stop the run, preserve generated ignored paths if any, and classify the row as not promoted.

## 5. Source Provenance Stop Checks

Source provenance must be interpreted before quality status, candidate usefulness, or any replacement language.

The future evidence artifact must record the public provenance tuple from the snapshot output:

| Field | Required recording |
|---|---|
| `source_provenance_status` | exact public value |
| `resolved_source` | exact public value |
| `fallback_used` | exact public value |
| `primary_failure_category` | exact public value, including null/missing |
| `fallback_eligibility` | exact public value |
| `source_chain` or public equivalent | exact public value if exposed |

Fail-closed categories:

- `schema_drift`
- `identity_mismatch`
- `integrity_error`

If any fail-closed category appears in public provenance, the future evidence run must stop before quality or promotion interpretation and record `terminal_classification=source_fail_closed_not_promoted`.

Eligible provenance requires one of:

- primary source success with no fallback and complete public provenance; or
- fallback with `primary_failure_category` exactly `not_found` or `unavailable`, public `fallback_eligibility=eligible`, and complete public provenance.

The following are not eligible and must not be treated as fallback permission:

- missing `primary_failure_category`;
- missing or incomplete provenance tuple;
- `fallback_used=true` with unknown or absent fallback category;
- `fallback_eligibility` missing, unknown, or not eligible;
- source/provenance values visible only through PDF/cache/source-helper/downloader/source-adapter internals;
- command success without public provenance fields.

If provenance is missing or unknown, the terminal classification should be `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted`, depending on the public output wording. The row remains `promotion_disposition=not_promoted`.

## 6. Quality Stop Checks

Quality interpretation is allowed only after source provenance reaches an eligible state. The future evidence artifact must then record:

- `quality_gate_status`;
- score status and field issue counts if public score output exposes them;
- all P0 issues;
- all P1 issues;
- the exact `manager_strategy_text` field status, issue severity, missing reason, traceability status, and any public evidence anchor state;
- any public false-positive suspicion, with the reason and the required next action.

P0 stop checks:

- If `manager_strategy_text` is P0-blocking, stop and classify as `quality_blocked_after_provenance` when source provenance is eligible.
- If `manager_strategy_text` is missing because the public disclosure genuinely lacks manager strategy discussion, classify as `disclosure_data_gap_not_baseline_ready` when the public evidence supports that conclusion.
- If quality blocks P0 before provenance is eligible, do not use `quality_blocked_after_provenance`; classify by provenance first, such as `provenance_unknown_public_metadata_absent`.
- If any other P0 block appears, record the exact rule/field and keep `promotion_disposition=not_promoted`.

P1 checks:

- P1 issues may allow a `warn` result but must remain visible in the summary.
- P1 cannot be hidden by the replacement-candidate framing.
- A future durable-baseline gate, not this evidence gate, would be required to decide whether any P1 residual is acceptable.

## 7. Terminal States

Every expected outcome in this evidence gate keeps `promotion_disposition=not_promoted`. A future durable-baseline gate is the only gate that may change promotion disposition.

| Condition | Terminal classification | promotion_disposition | Required next action |
|---|---|---|---|
| CLI help flag mismatch before execution | `cli_flag_mismatch_not_run` | `not_promoted` | Update evidence plan or CLI command plan after controller review. |
| Snapshot command non-zero exit | `snapshot_command_failed_not_promoted` | `not_promoted` | Record exit code, stderr summary if available, generated paths, and stop. |
| Score command non-zero exit | `score_command_failed_not_promoted` | `not_promoted` | Record exit code, generated snapshot paths, and stop before quality gate. |
| Quality-gate command non-zero exit | `quality_gate_command_failed_not_promoted` | `not_promoted` | Record exit code, score path, and stop. |
| Public provenance missing or incomplete | `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted` | `not_promoted` | Do not infer eligibility; controller decides whether to plan another candidate. |
| Public provenance shows `schema_drift`, `identity_mismatch`, or `integrity_error` | `source_fail_closed_not_promoted` | `not_promoted` | Stop fail-closed; do not fallback or continue. |
| Public provenance shows ineligible or unknown fallback category | `source_not_eligible_not_promoted` | `not_promoted` | Stop; do not treat as eligible. |
| Provenance eligible, quality P0 block on `manager_strategy_text` | `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready` | `not_promoted` | Record root cause and required next action; do not promote. |
| Provenance eligible, quality P0 block on another field | `quality_blocked_after_provenance` | `not_promoted` | Record exact field/rule and next action. |
| Provenance eligible, quality `warn` with P1 residuals only | `candidate_public_evidence_warn_not_promoted` | `not_promoted` | Controller review decides whether a later durable-baseline plan is justified. |
| Provenance eligible, quality `pass` | `candidate_public_evidence_pass_not_promoted` | `not_promoted` | Still not promoted; controller may open a separate durable-baseline gate. |

## 8. Fallback Contingency Planning

Fallback is only contingency planning in this gate. It does not authorize fallback execution.

If `096001` fails in a later accepted evidence gate, the preserved fallback order is:

1. `040046`
2. `019172`
3. remaining eligible equity QDII rows from the accepted enumeration table

The controller must authorize a new plan before any fallback candidate evidence run. That new plan must repeat public CLI preflight, source provenance stop checks, quality stop checks, terminal states, and `promotion_disposition=not_promoted`.

Preserved exclusions:

- `017641` remains excluded because accepted evidence classified it as `disclosure_data_gap_not_baseline_ready` and `not_promoted`.
- QDII-FOF candidates remain excluded unless a taxonomy gate accepts QDII-FOF for this replacement slot.
- `013308` remains excluded from evidence until the QDII name vs `国内股票类` category conflict is resolved by a future taxonomy/controller gate.
- Bond QDII candidates require an asset-class replacement fitness gate before evidence.

## 9. Future Evidence Artifact Expectations

The future tracked evidence summary must include:

- Startup Packet replay and statement that it follows the accepted next entry point, not a gate switch.
- Candidate identity: `096001`, `2024`, accepted enumeration row identity, CSV path, and run id.
- Preflight help command results and exact flag verification outcome.
- Exact public commands executed and exit codes.
- Generated ignored paths.
- Public provenance tuple.
- Provenance stop-check decision before quality interpretation.
- Quality status.
- P0 issues and P1 issues.
- `manager_strategy_text` status and root-cause classification if relevant.
- False-positive suspicion, if any, plus the evidence basis and required next action.
- Terminal classification from this plan's terminal-state matrix.
- `promotion_disposition=not_promoted`.
- Confirmation that no direct PDF/cache/source-helper/downloader/source-adapter inspection was used.
- Confirmation that no code, tests, README, fixtures, reports promotion, design doc, or control doc were changed by the evidence worker.
- `git diff --check` result.

## 10. Review Matrix

The controller must use `init-agents` / tmux discovery before actual handoff. This planning worker did not dispatch agents.

| Stage | Agent | Required artifact |
|---|---|---|
| Plan review 1 | AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-review-mimo-20260527.md` |
| Plan review 2 | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-review-ds-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-controller-judgment-20260527.md` |
| Control-doc update after acceptance | Controller | `docs/implementation-control.md` Startup Packet / Current Gate / Active Gate Ledger update after accepted judgment only |

Review focus:

- confirm this is plan-only and does not run evidence;
- confirm `096001` / 2024 is the only planned candidate and remains `provenance_unknown` / `quality_unknown`;
- confirm public CLI command plan uses only public paths and has help/flag mismatch stop behavior;
- confirm provenance is checked before quality or promotion interpretation;
- confirm fail-closed source categories stop;
- confirm `manager_strategy_text` P0 quality handling;
- confirm every terminal state has `promotion_disposition=not_promoted`;
- confirm fallback ordering is contingency-only and exclusions are preserved;
- confirm no code/test/product-flow/source-helper/taxonomy/renderer/golden/baseline changes are authorized.

## 11. Stop Conditions And Non-Goals

Stop conditions for this plan gate:

- do not run evidence;
- do not run `fund-analysis extraction-snapshot`;
- do not run `fund-analysis extraction-score`;
- do not run `fund-analysis quality-gate`;
- do not run `fund-analysis analyze`;
- do not run `fund-analysis checklist`;
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
- no source strategy or fallback behavior redesign.

## 12. Validation For This Plan Gate

This plan gate validation is limited to:

```bash
git diff --check
```

No other validation, evidence command, fund-analysis command, PDF/cache inspection, external web access, code execution for extraction, or CLI help run is part of this planning worker scope.
