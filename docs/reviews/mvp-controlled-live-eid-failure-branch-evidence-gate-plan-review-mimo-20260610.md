# Controlled Live EID Failure-Branch Evidence Gate Plan Review - MiMo

## Artifact Reviewed

`docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`

## Reviewer

AgentMiMo (independent plan reviewer)

## Role Constraint

No live execution, no network/curl/DNS/sockets/live EID/PDF/FDR acquisition, no source/tests/runtime modification, no stage/commit/push/PR.

## Verdict

**PASS_WITH_FINDINGS**

One medium finding (cache directory injection feasibility) and three low findings. No blocking findings that prevent gate entry, but the medium finding requires the controller/executor to choose a concrete resolution before running the live command.

---

## Findings

### F1: Temporary cache directory cannot be injected into `FundDocumentRepository` as the plan requires

**Severity**: MEDIUM

**Location**: Plan §Command Shape, lines 69-74

**Plan text**:
> - configure repository parsed-document cache under a temporary directory;
> - call exactly one `await repository.load_annual_report("006597", 2024, force_refresh=True)`;

**Repo fact**: `FundDocumentRepository.__init__` (repository.py:301) accepts only `annual_report_loader: _AnnualReportLoader | None`. It has no parameter for cache directory. The parsed-document cache is created internally by `_create_default_cache()` which calls `AnnualReportDocumentCache()` with `root_dir=None`, falling back to `DOCUMENT_CACHE_ROOT = Path("cache") / "documents"` (paths.py:25). There is no env var or config override.

To use a temporary cache directory, the executor must either:
- (a) Construct `AnnualReportDocumentCache(root_dir=tmp_path)` and wire it through a custom `_AnnualReportLoader`, bypassing the `FundDocumentRepository` convenience constructor; or
- (b) Monkeypatch `_create_default_cache` or `DOCUMENT_CACHE_ROOT`; or
- (c) Accept that the live run writes to the default `cache/documents/` directory and clean up afterward.

**Impact**: The plan's stated command shape cannot be implemented as literally written. Option (a) is the cleanest but means the live command does not use `FundDocumentRepository` as the only boundary — it constructs the lower-level components directly. Option (c) is simplest but means the live command writes production-cache artifacts to the workspace.

**Recommendation**: The controller must choose one of (a)/(b)/(c) and record the choice in the evidence artifact. If (c), add a post-command cleanup step to the validation section. If (a), update the command shape description to reflect the actual wiring.

---

### F2: Redundant constructor steps create ambiguity about the actual wiring

**Severity**: LOW

**Location**: Plan §Command Shape, lines 69-74

The plan lists five explicit constructor steps:
1. `EidAnnualReportSource` with temporary PDF cache
2. `AnnualReportSourceOrchestrator` with exactly one source
3. `AnnualReportPdfAdapter` with that orchestrator
4. `FundDocumentRepository` with that adapter
5. Configure parsed-document cache under temporary directory

**Repo fact**: `AnnualReportSourceOrchestrator(None)` auto-creates a single `EidAnnualReportSource` with defaults (sources.py:602). `AnnualReportPdfAdapter()` auto-creates an `AnnualReportSourceOrchestrator()` internally. So steps 1-3 are redundant if the executor relies on auto-creation.

**Impact**: Not a blocker, but the plan should clarify whether the executor must explicitly wire each component (for cache isolation) or may rely on auto-creation (simpler but default cache). This decision is coupled with F1.

---

### F3: Helper script vs one-shot command ambiguity

**Severity**: LOW

**Location**: Plan §Validation, lines 144-148

**Plan text**:
> The helper module may be created only if it is a gate-local disposable script under `scripts/` and is staged only with this gate's evidence if reviewers accept it.

**Issue**: The plan does not specify the exact one-shot `uv run python -c` command as an alternative. The executor must either create a helper script (which then needs review acceptance before staging) or construct an inline command. Neither path is fully specified.

**Recommendation**: Provide the exact inline command in the plan so the executor does not need to improvise. The inline command is more auditable than a helper script because it appears verbatim in the evidence artifact.

---

### F4: Stop condition "EID returns any failure category" contradicts the gate's stated objective

**Severity**: LOW

**Location**: Plan §Stop Conditions, line 187

**Plan text**:
> - EID returns any failure category;

**Plan objective** (line 12):
> Observe the current EID single-source annual-report path under one bounded live acquisition window and record whether a natural live failure occurs.

**Issue**: If the gate's objective is to observe whether a natural failure occurs, stopping immediately when a failure occurs seems contradictory. The plan's own outcome matrix (lines 90-97) has specific classifications for each failure category, implying the gate should record the failure and then stop — not stop before recording.

**Impact**: Low, because the outcome matrix and stop conditions are consistent in practice (both say "stop" after a failure). But the stop condition wording could be read as "stop before recording," which would defeat the gate's purpose.

**Recommendation**: Rephrase to: "EID returns any failure category — record the classification per the outcome matrix, then stop."

---

## Positive Observations

1. **Overclaim protection is excellent**: The plan explicitly states (line 14) that success "must not be described as live proof for `not_found`, `unavailable`, `schema_drift`, `identity_mismatch` or `integrity_error`." The outcome matrix (line 90) correctly classifies success as `accepted_live_success_no_failure_observed`, not as failure-branch proof.

2. **Live authorization boundary is well-defined**: The "Still forbidden" list (lines 43-48) is comprehensive and matches control truth. No ambiguity about what is authorized vs forbidden.

3. **Single-row selection is correct**: Using only `006597 / 2024` avoids live sweep risk and is sufficient for one bounded observation.

4. **Evidence artifact shape is safe**: The plan requires only scalar metadata in the artifact (lines 118-129), explicitly excludes PDF bytes, raw text and full parsed report text.

5. **Review routing is appropriate**: Both AgentDS and AgentMiMo are assigned for plan and evidence review, matching the `heavy` gate classification.

6. **Completion report format is comprehensive**: All required closeout fields are specified.

---

## Classification Summary

| Finding | Severity | Requires action before live execution? |
|---|---|---|
| F1: Cache directory injection | MEDIUM | Yes — controller must choose resolution |
| F2: Redundant constructors | LOW | No — executor clarifies in evidence |
| F3: Helper script ambiguity | LOW | No — executor chooses approach |
| F4: Stop condition wording | LOW | No — cosmetic rephrase |

## Recommendation

**PASS_WITH_FINDINGS**: The plan is sound in its objective, authorization boundary, outcome matrix, evidence retention and overclaim protection. F1 requires the controller to decide how to handle cache isolation before the live command runs. The other findings are informational and do not block gate entry.

The controller should accept this plan with the F1 resolution recorded (e.g., "accept default cache directory, add post-command cleanup to validation") before authorizing the live command.
