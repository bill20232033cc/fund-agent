# DS Plan Review: Controlled Live EID Failure-Branch Evidence Gate — 2026-06-10

## Verdict

**PASS_WITH_FINDINGS** — zero blockers. Four findings, all addressable before live execution without replanning.

## Review Lens

Per DS boundary review `mvp-controlled-live-eid-failure-branch-evidence-gate-boundary-review-ds-20260610.md`: source-policy boundary, failure-branch semantics, stop conditions, overclaim risk, gate-local helper script acceptability, exact live command pinning.

---

## Findings

### F1 — MEDIUM — Live command not fully pinned before execution

**File**: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`, lines 142–147.

The plan defines the live command as `uv run python -m scripts.controlled_live_eid_failure_branch_observation` but does not include the script content. The script does not exist yet. The plan says it "may be created only if it is a gate-local disposable script" — conditional language that leaves the execution vehicle unresolved at plan-acceptance time.

The script, if it exists, would import production modules (`EidAnnualReportSource`, `AnnualReportSourceOrchestrator`, `AnnualReportPdfAdapter`, `FundDocumentRepository`) and exercise production paths. This is not a passive observation — it is new code that calls production APIs. The reviewer cannot verify at plan time that it:
- Imports only allowed public APIs
- Pins exact fund_code/year parameters
- Does not mask or reinterpret production exceptions
- Does not add fallback, retry, or non-EID source construction
- Retains only safe scalar metadata in the artifact

**Recommendation**: Either (a) include the full script content in the plan artifact before controller judgment, or (b) add a pre-execution checkpoint: script must be written, reviewed by DS, and accepted before the live command runs. The `uv run python -c` fallback should be pinned to an exact one-liner in the plan if the script route is not taken.

---

### F2 — LOW — No config/env dependency declaration for EID path

**File**: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`, Validation section, lines 133–157.

The plan validates `git status` and `git diff` before the live command but does not declare whether the EID single-source acquisition path has any environment variable, API key, typed config, or local file dependency. Prior live evidence gates (provider smoke, post-config smoke) required E1 typed config readiness checks because the provider path depends on `FUND_AGENT_LLM_*` env vars.

For the EID public data path this is low risk — EID acquisition does not require API keys. But the plan should explicitly state: "EID single-source acquisition has no API key, env var, or typed config dependency. No E1 readiness check is needed."

Without this declaration, a future reviewer could reasonably ask whether a config dependency was overlooked.

**Recommendation**: Add one line in the Validation section: "No API key, env var, or typed config is required for the EID single-source acquisition path. E1 readiness is not applicable."

---

### F3 — LOW — Outcome classification label risks downstream overclaim

**File**: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`, line 90.

The label `accepted_live_success_no_failure_observed` uses the word "accepted" in a way that could drift. In the control truth ledger (`docs/current-startup-packet.md`, `docs/implementation-control.md`), "accepted" prefixes are used for gates that prove specific claims (e.g., "Accepted EID failure-branch evidence checkpoint"). A downstream control sync that writes "Accepted controlled live EID failure-branch evidence: `accepted_live_success_no_failure_observed`" could be misread as "live failure-branch evidence accepted" when the actual observation was "no failure observed, therefore no live failure-branch proof exists."

The plan body itself correctly states: "If the live command succeeds, the evidence only proves that no natural failure branch was observed." The label should match this precision.

**Recommendation**: Rename to `accepted_live_observation_no_natural_failure` or `accepted_live_window_no_failure_observed`. The word "success" is ambiguous between "command succeeded" and "gate succeeded in proving something." Alternatively, keep the label but add a note in the evidence artifact template: "This label does not mean live failure-branch proof was accepted."

---

### F4 — LOW — Five no-live categories not explicitly cross-referenced in residual section

**File**: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`, lines 99–104.

The residual section correctly names `schema_drift`, `identity_mismatch`, `integrity_error`, `not_found`, and `unavailable` individually but does not explicitly cross-reference them against the accepted no-live evidence (`ac6bbe9`). The DS boundary review required: "explicit statement that all five no-live categories remain proven only no-live."

The plan says "The no-live proof remains the accepted code-behavior evidence for those categories" — this is close but "those categories" is a backward reference that a reader must resolve. Making it explicit would reduce interpretative burden.

**Recommendation**: Add: "The no-live evidence at `ac6bbe9` remains the accepted proof for all five categories (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`). This live gate cannot replace or upgrade that proof regardless of outcome."

---

## What the Plan Gets Right

**Source-policy boundary**: Correctly pins `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`. Correctly forbids Eastmoney, CNINFO, fund-company construction. Correctly forbids multi-source orchestrator. Lines 18–21 and 42–47 are consistent with `docs/design.md` §P8-S3, `AGENTS.md` fallback strategy table, and `docs/current-startup-packet.md` §6 residuals.

**Failure-branch semantics**: Outcome matrix (lines 87–97) distinguishes eight outcomes including `blocked_policy_violation` for fallback/non-EID detection. Correctly states that `unavailable` is the only plausibly observable category. Correctly states success is not failure-branch proof. Aligns with DS boundary review Q1–Q2.

**Stop conditions**: Comprehensive two-phase stops (pre-live lines 173–180, during/post lines 182–190). Covers plan-review gaps, missing controller judgment, code changes, ambiguous authorization, non-EID source detection, fallback invocation, >1 attempt, unsafe retention, and weekly-CI implication. Aligns with DS boundary review Q4.

**Overclaim risk**: Objective (lines 10–13) and residual section (lines 99–104) both state that success does not prove failure branches. Evidence artifact template (lines 112–130) requires explicit no-fallback statement and explicit "success is not live failure-branch proof" statement. Aligns with DS boundary review Q1–Q3.

**Single-row discipline**: Pins `006597 / 2024` as the only row. No fallback row. No multi-row sweep. Lines 49–63 correctly justify: it's already a live-proven small-golden row, so a success outcome is expected and adds no false confidence.

**Command shape**: Lines 66–83 define exact module instantiation sequence, forbid extractor/Service/Host/LLM path, forbid Eastmoney import, forbid multi-source orchestrator, and forbid PDF/text retention. The sequence correctly follows the production boundary: `EidAnnualReportSource → AnnualReportSourceOrchestrator → AnnualReportPdfAdapter → FundDocumentRepository`.

**Review routing**: Explicitly routes to DS (source-policy boundary, failure-branch semantics) and MiMo (live authorization, evidence retention, overclaim risk). Follows the two-reviewer precedent from prior heavy gates.

---

## Helper Script Acceptability

The gate-local `scripts/controlled_live_eid_failure_branch_observation.py` concept is acceptable **only if** F1 is resolved before execution. The script is a thin wrapper over existing public APIs — it does not change production behavior. However, because it exercises production code paths, it must be:

- Written and reviewed as part of the plan (not discovered at execution time)
- Limited to importing existing public modules only
- Free of new exception handling, retry logic, fallback construction, or non-EID source references
- Explicit about what it prints (safe scalar metadata only)

If writing a script is too heavyweight for a one-shot observation, the `uv run python -c` alternative should be pinned to an exact command in the plan. The current plan leaves both options open, which is the root of F1.

---

## Summary

| # | Severity | Topic | Blocking? |
|---|---|---|---|
| F1 | MEDIUM | Script content not provided; live command not fully pinned | No — addressable by including script or pinning one-liner before execution |
| F2 | LOW | No config/env dependency declaration | No — EID is public, but declaration removes ambiguity |
| F3 | LOW | Outcome label `accepted_live_success_no_failure_observed` risks overclaim drift | No — rename or add caveat |
| F4 | LOW | No explicit cross-reference to no-live evidence `ac6bbe9` in residual section | No — add one sentence |

**Verdict**: PASS_WITH_FINDINGS. The plan preserves source-policy boundary, correctly scopes failure-branch semantics, and resists overclaim. All four findings are addressable without restructuring the gate. Controller may accept the plan and require F1–F4 resolution before authorizing the live command.
