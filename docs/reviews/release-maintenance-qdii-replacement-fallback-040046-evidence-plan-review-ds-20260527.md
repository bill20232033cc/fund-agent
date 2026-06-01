# QDII Replacement Fallback Candidate Evidence Plan Review — AgentDS

> Date: 2026-05-27
> Reviewer: AgentDS (independent plan reviewer, not controller, not evidence runner)
> Gate: `QDII replacement fallback candidate evidence plan gate for 040046`
> Plan under review: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`
> Verdict: **PASS**

## Scope Compliance

This review is plan-only. No fund-analysis command (including --help) was run. No PDFs, cache, source-helper, downloader, source-adapter internals, or external web were inspected. No code, tests, renderer, FQ0-FQ6, Service/CLI, FundDocumentRepository, source helpers, taxonomy, extractor, Host/Agent/dayu, fixtures, baseline/golden corpus, docs/design.md, or docs/implementation-control.md were modified.

## Truth Sources Consulted

| Source | Path | Relevance |
|---|---|---|
| AGENTS.md | `AGENTS.md` | Rule authority, module boundaries, fallback strategy |
| Design doc | `docs/design.md` (v2.2) | Architecture boundaries, current execution chain |
| Control doc | `docs/implementation-control.md` | Startup Packet, current gate, next entry point, accepted artifacts |
| Accepted enumeration plan | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` | Fallback order, candidate identities, exclusions |
| Accepted enumeration controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-controller-judgment-20260527.md` | Accepted fallback sequence, next-gate constraints |
| Accepted 096001 evidence plan | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md` | Command/path convention baseline |
| Accepted 096001 evidence | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md` | Provenance tuple structure, quality results, terminal classification |
| Accepted 096001 evidence controller judgment | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-controller-judgment-20260527.md` | Accepted 096001 state, next entry point authorization, reuse constraint |

## Findings

### Finding 1 — Severity: NONE (Accepted Strength)

**Startup Packet replay is correct and follows next entry point, not a gate switch.**

Plan §1 accurately replays the Startup Packet from `docs/implementation-control.md` line 29: current phase `release maintenance`, current gate `QDII replacement candidate evidence accepted locally`, next entry point `QDII replacement fallback candidate evidence plan gate for 040046`. The plan explicitly states it follows the next entry point and is not a gate switch (§1 final paragraph). All referenced accepted artifacts exist and their hash/checkpoint references are consistent with the git log (HEAD `c6a5042`).

### Finding 2 — Severity: NONE (Accepted Strength)

**Candidate discipline is preserved: 040046/2024 is the only planned fallback candidate.**

Plan §2 correctly identifies 040046 / 华安纳斯达克100ETF联接(QDII)A as the single fallback candidate, matching the accepted enumeration plan's candidate order (row 2, first fallback after 096001). The plan states current state as `provenance_unknown`, `quality_unknown`, `promotion_disposition=not_promoted`, and explicitly disclaims source-safety, scoring-readiness, baseline-readiness, golden-readiness, replacement acceptance, and promotion (§2 final paragraph). Selection basis correctly cites the enumeration fallback order after 096001 quality-blocked.

### Finding 3 — Severity: NONE (Accepted Strength)

**096001 accepted state is fully preserved and not rerun or weakened.**

Plan §3 records the complete accepted 096001 state with all fields matching the accepted evidence artifact: source provenance eligible complete public fallback provenance (eastmoney, fallback_used=true, primary_failure_category=unavailable, fallback_eligibility=eligible, source_provenance_status=complete), quality_gate_status=block, terminal classification `quality_blocked_after_provenance`, promotion_disposition=not_promoted. The plan correctly notes that `manager_strategy_text` passed in 096001 and is not the blocker. Explicit statement: "This plan must not weaken or reopen that accepted state."

### Finding 4 — Severity: NONE (Accepted Strength)

**Public CLI command plan uses public CLI only, explicit paths, preflight mismatch stop.**

Plan §4 specifies three preflight `--help` commands. Preflight acceptance criteria name the required flag equivalents. Mismatch stop behavior is explicit: `terminal_classification=cli_flag_mismatch_not_run`, `promotion_disposition=not_promoted`, record exact mismatch. Plan §5 specifies three public evidence commands with explicit paths, run-id, and output directory. Generated-output provenance reading (§6) explicitly requires inspection of `summary.md` and `snapshot.jsonl`, not stdout-only.

Command/path conventions compared against accepted 096001 plan and evidence: flag names, argument order, output directory pattern, generated file names, and run-id convention are materially consistent. The only difference is the run-id prefix (`qdii-replacement-fallback-040046` vs `qdii-replacement-candidate-096001`), which correctly reflects the fallback nature and is not a convention error.

### Finding 5 — Severity: NONE (Accepted Strength)

**Source provenance discipline: provenance before quality, fail-closed categories stop, missing/incomplete provenance not eligible.**

Plan §7 specifies the public provenance tuple to record (8 fields, including `source_provenance_schema_version` and `source_provenance_reason` — a refinement derived from actual 096001 evidence output, not an invention). Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) are enumerated with explicit stop-before-quality instruction. Eligible provenance conditions enumerate both primary-success and eligible-fallback paths. Ineligible conditions are exhaustively listed: missing `primary_failure_category`, incomplete tuple, unknown fallback category, missing `fallback_eligibility`, internal-only values, command-success-without-fields.

### Finding 6 — Severity: NONE (Accepted Strength)

**Quality: P0/P1 and manager_strategy_text handling is precise; no extractor/policy fixes inferred.**

Plan §8 correctly orders quality interpretation after provenance eligibility. `manager_strategy_text` handling distinguishes P0-blocking (`quality_blocked_after_provenance`) from disclosure-gap (`disclosure_data_gap_not_baseline_ready`), with the latter conditioned on public evidence support. The plan correctly states that quality-block-before-provenance must classify by provenance first. P1 residuals remain visible and are gated to a future durable-baseline gate. False-positive suspicion recording is permitted but does not authorize code or policy changes.

### Finding 7 — Severity: NONE (Accepted Strength)

**Terminal matrix: every state is not_promoted and uses accepted names.**

Plan §9 covers 10 terminal conditions. All use `promotion_disposition=not_promoted`. Terminal classification names are consistent with the accepted 096001 plan matrix. Two additional entries (`snapshot_outputs_missing_not_promoted`, `source_not_eligible_not_promoted`) are refinements learned from the 096001 evidence review findings and use consistent naming conventions. No new promotion state is introduced.

### Finding 8 — Severity: NONE (Accepted Strength)

**Fallback/exclusion discipline preserved.**

Plan §10 preserves:
- 019172 as contingency-only (not authorized for evidence)
- 017641 excluded (disclosure_data_gap_not_baseline_ready / not_promoted)
- QDII-FOF excluded pending taxonomy gate
- 013308 excluded pending name/category conflict resolution
- Bond QDII requires asset-class fitness gate

All match the accepted enumeration plan and controller judgment.

### Finding 9 — Severity: NONE (Accepted Strength)

**Boundary: no code/product/source-helper/taxonomy/renderer/golden/baseline changes or evidence run authorized.**

Plan §13 stop conditions enumerate all prohibited actions explicitly. Non-goals list all out-of-scope decisions. The plan states it is plan-only and defers evidence execution to a future gate after controller acceptance.

### Finding 10 — Severity: NONE (Accepted Strength)

**Command/path conventions are materially consistent with accepted 096001 plan/evidence.**

Cross-reference between this plan and the accepted 096001 evidence plan confirms: same three-command pipeline (extraction-snapshot → extraction-score → quality-gate), same flag names, same `docs/code_20260519.csv` source CSV, same output directory structure under `reports/extraction-snapshots/`, same generated file names (`snapshot.jsonl`, `summary.md`, `errors.jsonl`, `score.json`, `score.md`, `golden_set.json`, `quality_gate.json`, `quality_gate.md`). The `--fund-code` value changes from `096001` to `040046`, and the run-id/directory prefix changes from `qdii-replacement-candidate` to `qdii-replacement-fallback`, both correct for the fallback context. No material convention error found.

## Accepted Strengths

1. The plan incorporates both review lessons from the 096001 evidence gate: it explicitly requires reading provenance from generated public files (summary.md/snapshot.jsonl), not stdout-only, and it adds `snapshot_outputs_missing_not_promoted` to the terminal matrix.
2. The provenance tuple is more detailed than the 096001 plan (adding `source_provenance_schema_version`, `source_strategy`, `source_provenance_reason`), derived from actual 096001 CLI output rather than plan speculation.
3. The stop conditions (§13) are exhaustive and leave no ambiguity about what this plan gate must not do.
4. The future evidence artifact expectations (§11) provide a complete checklist for the evidence worker, reducing the risk of another BLOCKED review cycle.
5. The plan correctly defers all agent dispatch to the controller (§12) and does not independently initiate tmux/session handoff.

## Required Fixes Before Acceptance

None.

## Residual Risks (for controller doc)

| Residual | Owner | Handling |
|---|---|---|
| CLI flags may change between plan acceptance and evidence execution | Evidence runner | Preflight help check (§4) catches flag mismatch; runner stops with `cli_flag_mismatch_not_run` |
| 040046 may exhibit the same P0 `nav_benchmark_performance` gap as 096001 | Future evidence gate | Terminal matrix (§9) covers `quality_blocked_after_provenance`; controller proceeds to 019172 or later |
| 040046 may encounter a novel provenance state not covered by the terminal matrix | Evidence runner / controller | Runner stops and records actual state; controller interprets against plan intent |
| `manager_strategy_text` disclosure gap vs extractor gap distinction cannot be resolved without PDF inspection | Future diagnosis gate | Plan §8 requires recording public evidence basis only; PDF inspection is prohibited in evidence gate |
| Plan review sequence (§12) assumes AgentMiMo and AgentDS availability | Controller | `init-agents` / tmux discovery before handoff |

## Acceptance Recommendation

**Yes**, this plan may be accepted as a plan for later 040046 evidence without authorizing evidence now.

The plan correctly follows the Startup Packet next entry point, preserves 096001 accepted state, applies candidate discipline (single fallback candidate, not_promoted), specifies public CLI commands with explicit paths and preflight mismatch stop, requires provenance-before-quality with fail-closed stop, handles P0/P1 and manager_strategy_text precisely, uses a terminal matrix where every state is not_promoted, preserves fallback/exclusion discipline, and authorizes no code/test/product/source-helper/taxonomy/renderer/golden/baseline changes. Command/path conventions are materially consistent with the accepted 096001 plan and evidence. No blocking or material finding identified.

## Validation

| Command | Exit code | Result |
|---|---|---|
| `git diff --check` | 0 | passed |

No other validation was performed. This review artifact is the only file created or modified.
