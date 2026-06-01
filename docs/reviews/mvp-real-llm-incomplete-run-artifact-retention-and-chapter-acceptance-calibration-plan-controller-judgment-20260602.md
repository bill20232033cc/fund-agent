# Controller Judgment: MVP Real LLM Incomplete-Run Artifact Retention And Chapter Acceptance Calibration Plan

## Self-check

- Current gate / role: plan review closeout for `MVP real LLM incomplete-run artifact retention and chapter acceptance calibration gate`; controller only.
- Source of truth: user request, manual smoke evidence, plan artifact, AgentDS plan review artifact, current branch/status.
- Scope boundary: plan artifacts only; no implementation, no phaseflow start, no push/PR/merge, no unrelated residual handling.
- Stop conditions: no blocking findings; one work-unit shape decision required and resolved below.
- Next action: create accepted plan checkpoint, then implement only the current narrowed gate scope.

## Inputs

- Plan: `docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-20260602.md`
- Plan review: `docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-review-ds-20260602.md`
- Manual smoke evidence:
  - `reports/manual-llm-smoke/006597-2024/stderr.txt`
  - `reports/manual-llm-smoke/006597-2024/stdout.md` is empty
  - `reports/manual-llm-smoke/006597-2024/exitcode` is `1`

## Plan Review Judgment

AgentDS verdict: `PASS with recommendations`.

No blocking findings were raised. Informational findings F1-F9 confirm the plan is code-generation-ready, accurate against current code facts, sufficiently concrete on artifact schema, redaction, trigger policy, fail-closed invariants, and tests. Low findings F10/F11 are non-blocking and are accepted as residual/implementation guidance:

| Item | Controller judgment | Reason / owner |
|---|---|---|
| F10: artifact retention lifecycle policy not explicit | deferred-with-owner | Local `reports/llm-runs/` retention cleanup is broader lifecycle policy. Owner: future observability phase/control policy if disk growth becomes material. Current gate may add manifest `retention_policy=manual_local_cleanup` but must not build cleanup automation. |
| F11: accepted-final diagnostic future behavior not specified | deferred-with-owner | Current gate only writes incomplete-run artifacts. Accepted-run diagnostics stay future explicit scope. Owner: future observability phase gate if needed. |
| OQ1: phase upgrade decision | accepted | Broader work should become `MVP real LLM observability and chapter acceptance phase`; current gate is narrowed to artifact retention only. |
| OQ2: CLI flag decision | accepted recommendation | Current gate should automatically write artifacts for typed incomplete `--use-llm` runs and print a safe path line. No new CLI flag in Slice 1 unless implementation discovers a blocking need. |
| OQ3: raw auditor response | accepted recommendation | Do not save `ChapterLLMAuditResult.raw_response` by default. If normalized issue feedback is insufficient, implementation must stop and return a controller question before saving raw responses. |

## Work-Unit Shape Decision

Decision: upgrade the broader initiative to `MVP real LLM observability and chapter acceptance phase`, but do not start `$phaseflow` in this plan checkpoint.

Current accepted gate name/scope for implementation:

- Gate: `MVP incomplete LLM run artifact retention gate`
- Slice: `slice-1-incomplete-llm-run-artifact-retention`
- Scope: retain local ignored, per-chapter incomplete-run artifacts for typed incomplete `analyze --use-llm` runs.
- Stop point: after Slice 1 implementation, code review, fix/re-review if needed, accepted slice checkpoint, and aggregate deepreview for this narrowed gate.

Deferred owners:

| Deferred work | Owner / destination |
|---|---|
| LLM run progress and timeout UX | Future `MVP real LLM observability and chapter acceptance phase` gate |
| Chapter acceptance calibration for chapters 2/3/6, starting with chapter 2 `l1_numerical_closure` | Future `MVP real LLM chapter acceptance calibration gate`, after artifact retention evidence exists |
| Provider runtime budget calibration | Future provider runtime budget calibration gate |
| Chapter generation score-loop entry | Future score-loop entry gate, after real chapter accepted rate is stable |
| Phaseflow control/design synchronization | Controller, after this narrowed gate reaches an accepted checkpoint or when explicitly starting phaseflow |

## Accepted Plan Scope

Implementation may touch only the files/modules listed by the plan for Slice 1, unless code review/fix discovers a tightly scoped need:

- new `fund_agent/services/llm_run_artifacts.py`
- `fund_agent/ui/cli.py`
- `.gitignore`
- focused tests under `tests/services/` and `tests/ui/test_cli.py`
- optional `fund_agent/services/__init__.py` only if export is needed
- optional root README troubleshooting line only if implementation adds user-visible CLI option; otherwise docs decision can remain in implementation artifact

Implementation must preserve:

- deterministic `analyze/checklist` unchanged;
- incomplete `--use-llm` stdout empty;
- incomplete `--use-llm` exit code `1`;
- no deterministic fallback;
- no Host success fabrication;
- no quality gate semantic change;
- no repair budget increase;
- no auditor relaxation;
- no external `dayu-agent`, `dayu.host`, or `dayu.engine` production dependency;
- no progress UX, runtime budget calibration, score-loop entry, or chapter acceptance calibration in this gate.

## Required Validation For Slice 1

Minimum validation expected from implementation:

- `uv run pytest tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py -q`
- `uv run ruff check .`
- targeted assertions that:
  - `reports/llm-runs/` is ignored;
  - incomplete LLM writes manifest/summary/chapter artifacts;
  - writer draft, repair draft and normalized auditor feedback files are present when source data exists;
  - secret canaries and forbidden prompt/raw payload canaries are absent from all artifact files;
  - missing config/construction/quality-gate-block/Host failure without typed result do not write chapter artifacts;
  - artifact writer failure still exits fail-closed with empty stdout.

Real provider smoke after Slice 1 is desirable if credentials/network are available. If unavailable or still incomplete, implementation must record safe blocked evidence and must not fake acceptance.

## Verdict

Accepted. The plan is handoff-ready and code-generation-ready for the narrowed `MVP incomplete LLM run artifact retention gate`.

Proceed to accepted plan commit, then Slice 1 implementation only.
