# QDII Replacement Candidate Evidence Plan Review — AgentMiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: `QDII replacement candidate evidence plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Truth Sources Consulted

1. `AGENTS.md` — 规则真源
2. `docs/implementation-control.md` — Startup Packet / Current Gate / Next Entry Point
3. `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` — accepted enumeration plan
4. `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-controller-judgment-20260527.md` — accepted enumeration controller judgment
5. The plan artifact under review

## Review Criteria Evaluation

### 1. Startup Packet Replay — PASS

The plan correctly replays:
- Current phase: `release maintenance` — matches control doc line 8.
- Current gate: `QDII replacement candidate enumeration plan accepted locally` — matches control doc line 28.
- Next entry point: `QDII replacement candidate evidence plan gate; must use init-agents / tmux multi-agent flow` — matches control doc line 29.
- Latest accepted checkpoint: `461ff08 docs: accept qdii replacement enumeration plan` — matches git log.
- This artifact gate: `QDII replacement candidate evidence plan gate` — matches the accepted next entry point.
- Explicit statement: "This plan follows the Startup Packet next entry point. It is not a gate switch." — correct framing.

No blocking issue.

### 2. Candidate Discipline — PASS

- Single candidate: `096001` / `2024` — matches the accepted enumeration controller judgment's accepted next entry point.
- Current source provenance state: `provenance_unknown` — correct; the enumeration plan and controller judgment both state provenance is unknown for all non-excluded candidates.
- Current quality state: `quality_unknown` — correct; no quality evidence has been run.
- Promotion state: `promotion_disposition=not_promoted` — correct.
- The plan explicitly states: "It does not make `096001` source-safe, quality-passing, scoring-ready, baseline-ready, golden-ready, promoted, or accepted as a replacement." — matches the enumeration controller judgment exactly.

No blocking issue.

### 3. Public Command Plan — PASS

The planned commands use only public CLI surface:
- `uv run fund-analysis extraction-snapshot --help` — public preflight.
- `uv run fund-analysis extraction-score --help` — public preflight.
- `uv run fund-analysis quality-gate --help` — public preflight.

Planned evidence commands:
- `extraction-snapshot` with `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, `--force-refresh` — all public options.
- `extraction-score` with `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path` — all public options.
- `quality-gate` with `--score-path`, `--output-dir` — all public options.

Help/flag mismatch stop behavior is explicitly declared in section 3: "If any flag has changed, the runner must stop and record `terminal_classification=cli_flag_mismatch_not_run`" — correct.

No blocking issue.

### 4. Source Provenance Ordering — PASS

Section 5 correctly establishes provenance-before-quality ordering:
- "Source provenance must be interpreted before quality status, candidate usefulness, or any replacement language." — clear ordering.
- Fail-closed categories are explicitly listed: `schema_drift`, `identity_mismatch`, `integrity_error` — matches AGENTS.md fallback strategy.
- "If any fail-closed category appears in public provenance, the future evidence run must stop before quality or promotion interpretation" — correct fail-closed behavior.
- Eligible provenance requires either primary success or fallback with `primary_failure_category` exactly `not_found` or `unavailable` — matches AGENTS.md.
- Non-eligible conditions are explicitly enumerated, including command success without public provenance fields — prevents inferring safety from indirect evidence.

No blocking issue.

### 5. Quality Stop Checks — PASS

Section 6 correctly handles quality after provenance:
- "Quality interpretation is allowed only after source provenance reaches an eligible state." — correct ordering.
- P0 `manager_strategy_text` handling is precise:
  - If P0-blocking: classify as `quality_blocked_after_provenance` when provenance is eligible.
  - If missing because public disclosure genuinely lacks it: classify as `disclosure_data_gap_not_baseline_ready` when public evidence supports that conclusion.
  - If P0 blocks before provenance is eligible: classify by provenance first, not by quality — prevents inferring extractor/policy fixes from indirect evidence.
- P1 issues remain visible and cannot be hidden by replacement-candidate framing.
- A future durable-baseline gate, not this evidence gate, decides P1 acceptability.

No blocking issue.

### 6. Terminal States — PASS

Section 7's terminal-state matrix covers all expected outcomes:
- `cli_flag_mismatch_not_run` — `not_promoted`
- `snapshot_command_failed_not_promoted` — `not_promoted`
- `score_command_failed_not_promoted` — `not_promoted`
- `quality_gate_command_failed_not_promoted` — `not_promoted`
- `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted` — `not_promoted`
- `source_fail_closed_not_promoted` — `not_promoted`
- `source_not_eligible_not_promoted` — `not_promoted`
- `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready` — `not_promoted`
- `candidate_public_evidence_warn_not_promoted` — `not_promoted`
- `candidate_public_evidence_pass_not_promoted` — `not_promoted`

Every terminal state has `promotion_disposition=not_promoted`. No durable baseline, golden, or source-safe state is claimed anywhere in the plan.

No blocking issue.

### 7. Fallback/Exclusion Discipline — PASS

Section 8 correctly preserves:
- Fallback ordering is contingency-only: `040046`, then `019172`, then remaining eligible equity QDII rows.
- "The controller must authorize a new plan before any fallback candidate evidence run." — correct.
- `017641` remains excluded because accepted evidence classified it as `disclosure_data_gap_not_baseline_ready` and `not_promoted`.
- QDII-FOF candidates remain excluded unless a taxonomy gate accepts QDII-FOF.
- `013308` remains excluded until the QDII name vs `国内股票类` category conflict is resolved.
- Bond QDII candidates require an asset-class replacement fitness gate before evidence.

All exclusions match the accepted enumeration plan and controller judgment. No fallback execution is authorized by this plan.

No blocking issue.

### 8. Boundary Compliance — PASS

Section 11 (Stop Conditions And Non-Goals) explicitly prohibits:
- Running evidence, extraction-snapshot, extraction-score, quality-gate, analyze, checklist.
- Inspecting PDFs, cache, source-helper, downloader, source-adapter, or external web.
- Editing implementation-control.md, design.md, code, tests, README, fixtures, reports, generated outputs.
- Changing renderer, FQ0-FQ6, Service, CLI, default behavior, FundDocumentRepository, source-helper, taxonomy, extractor, Host, Agent, dayu, golden files, baseline fixtures, corpus state.
- Committing, pushing, opening PR, merging, deleting branch, or mutating GitHub.

Non-goals section explicitly lists: no durable-baseline decision, no scoring-ready decision, no golden answer corpus decision, no accepted replacement decision, no taxonomy conflict resolution, no QDII-FOF acceptance, no bond QDII asset-class fitness decision, no source strategy or fallback behavior redesign.

No production code, renderer, FQ0-FQ6, default CLI behavior, direct PDF/cache/source helper, Host/Agent/dayu, taxonomy, extractor, product-flow, or GitHub mutation is authorized.

No blocking issue.

### 9. Command/Path Conventions — PASS_WITH_FINDINGS

**F1 (informational)**: The planned `extraction-snapshot` output directory is `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527`. The plan calls these "ignored output directories" (section 4) and the future evidence artifact expectations (section 9) require confirmation that no generated outputs were promoted. The convention is consistent with the accepted enumeration plan's section 8 requirements. However, the plan does not explicitly state whether `reports/` is in `.gitignore`. If it is not, the evidence runner should verify this or document the ignore status. This is informational only — the evidence runner's preflight can resolve it.

**F2 (informational)**: The planned `extraction-snapshot` command includes `--force-refresh`. This is a reasonable default for a replacement-candidate evidence run to avoid stale cache, but the plan does not explain why `--force-refresh` was chosen over relying on existing cache. This is informational only and does not block plan acceptance.

**F3 (informational)**: The expected ignored paths for `extraction-snapshot` list `snapshot.jsonl`, `summary.md`, and `errors.jsonl`. The expected ignored paths for `extraction-score` list `score.json`, `score.md`, and `golden_set.json`. The expected ignored paths for `quality-gate` list `quality_gate.json` and `quality_gate.md`. These are plausible based on the CLI interface, but the plan acknowledges the runner must verify actual flag/output behavior via `--help` preflight. This is acceptable — the preflight will catch any discrepancy.

No blocking issue.

## Findings Summary

| ID | Severity | Section | Description | Blocks Acceptance? |
|---|---|---|---|---|
| F1 | informational | §4, §9 | `reports/` gitignore status not explicitly stated; evidence runner preflight should verify | No |
| F2 | informational | §4 | `--force-refresh` rationale not explained; acceptable default for candidate evidence | No |
| F3 | informational | §4, §9 | Expected ignored paths are plausible but unverified; preflight resolves this | No |

## Accepted Strengths

1. **Startup Packet replay is precise and complete.** The plan correctly identifies the current gate, next entry point, latest accepted checkpoint, and accepted artifacts. The framing as "plan artifact only, not a gate switch" is correct.

2. **Candidate discipline is strict.** `096001` / `2024` is the only planned candidate. The plan explicitly preserves `provenance_unknown`, `quality_unknown`, and `not_promoted` states. No premature source-safety or quality claims are made.

3. **Source provenance ordering is correct and fail-closed.** Provenance must be interpreted before quality. Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) stop the run. Eligible provenance conditions match AGENTS.md fallback strategy exactly. The non-eligible list prevents inferring safety from command success alone.

4. **Quality stop checks are precise.** `manager_strategy_text` P0 handling distinguishes between P0-blocking, disclosure data gap, and pre-provenance classification. No extractor or policy fixes are inferred from indirect evidence.

5. **Terminal states are comprehensive.** Every outcome from CLI mismatch to quality pass has a terminal classification, and all maintain `promotion_disposition=not_promoted`. No durable baseline or golden state is claimed.

6. **Fallback/exclusion discipline preserves all accepted constraints.** `017641`, QDII-FOF, `013308`, and bond QDII exclusions are all preserved. Fallback is contingency-only and requires a new plan before any fallback evidence run.

7. **Boundary compliance is thorough.** The stop conditions and non-goals explicitly prohibit all prohibited actions. No production code, renderer, CLI defaults, source helpers, Host/Agent/dayu, taxonomy, extractor, or GitHub mutation is authorized.

8. **Review matrix is correctly specified.** AgentMiMo and AgentDS as reviewers, controller for judgment, with explicit review focus items matching the enumeration plan review pattern.

## Required Fixes Before Acceptance

None. All findings are informational and can be resolved by the evidence runner's preflight.

## Residual Risks Suitable for Controller Doc

| Residual | Owner / Next Gate | Required Handling |
|---|---|---|
| `096001` source provenance unknown | Evidence runner (after plan acceptance) | Run preflight, then evidence commands; interpret provenance before quality; stop on fail-closed. |
| `096001` quality unknown, including possible P0 `manager_strategy_text` block | Evidence runner (after plan acceptance) | Record quality status only after provenance is eligible; classify P0 precisely per section 6. |
| `reports/` gitignore status | Evidence runner preflight | Verify output directory is gitignored or document ignore status in evidence summary. |
| `--force-refresh` may cause unnecessary network/cache activity | Evidence runner | Acceptable for single-candidate evidence run; document in evidence summary if cache hit would have been preferred. |
| CLI flag verification needed before execution | Evidence runner preflight | Run `--help` for all three commands; stop on mismatch. |

## Plan Acceptance Recommendation

**Yes.** This plan may be accepted as a plan for a later `096001` evidence run, without authorizing evidence now.

The plan correctly follows the accepted next entry point from the enumeration controller judgment. It preserves all candidate discipline, provenance ordering, quality stop checks, terminal states, fallback/exclusion constraints, and boundary compliance. The informational findings (F1-F3) are resolvable by the evidence runner's preflight and do not require plan revision.

The controller may accept this plan and update the control doc's current gate and next entry point accordingly. The evidence runner must not begin evidence execution until the controller has accepted this plan and authorized the evidence gate.
