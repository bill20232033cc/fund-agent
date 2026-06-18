# Quality Warning Issue Root-cause Planning Gate Plan

Date: 2026-06-12

Role: controller-authored planning artifact

Gate: `Quality warning issue root-cause planning gate`

Classification: `standard`

Accepted input:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-20260612.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md`
- `docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md`
- `docs/reviews/mvp-ci-quality-warn-only-evidence-controller-judgment-20260612.md`
- Checkpoint `0e50986`
- Control-sync checkpoint `ebe74ae`

## 1. Objective

Plan the next evidence work for the accepted live residual:

- `quality_gate_status=warn`
- `quality_gate_issues=3`

This planning gate does not claim the identity, rule code, field name or root cause of the three issues. The accepted durable evidence currently proves only the issue count and readiness residual classification.

## 2. Current Accepted Facts

| Fact | Source type | Source |
|---|---|---|
| Controlled live annual-period narrative command exited `0`. | accepted controller fact | `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md` |
| The run emitted `quality_gate_status=warn` and `quality_gate_issues=3`. | accepted controller fact | Same controller judgment and execution evidence artifact |
| `warn` is not release/readiness proof. | accepted controller fact | `docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md` and `docs/reviews/mvp-ci-quality-warn-only-evidence-controller-judgment-20260612.md` |
| Current code/docs/tests preserve block/warn/not-run policy semantics. | accepted controller fact | `docs/reviews/mvp-ci-quality-warn-only-evidence-controller-judgment-20260612.md` |
| The three issue identities are not yet accepted durable facts. | controller fact | The accepted live evidence artifact records count only, not issue rows. |

## 3. Non-goals

This planning gate does not authorize:

- source, tests, runtime, README, design or config changes
- quality gate severity/default/semantic changes
- FQ0-FQ6 weakening
- treating `warn` as release/readiness pass
- fixture/golden/readiness promotion
- provider/LLM acceptance
- cleanup/archive/delete/import/ignore
- PR/push/merge/mark-ready/release external state
- using arbitrary untracked `reports/` residue as proof

## 4. Process Note

During planning, an exploratory `rg` over `reports/quality-gate-runs`, `reports/live-evidence` and `reports/manual-llm-smoke` produced workspace observations. Those observations are **discarded for proof** because they are arbitrary untracked runtime residue and were not accepted as durable evidence in the current chain.

The next evidence gate must establish issue identity from an accepted lineage before any rule-code, field-name or message can be accepted.

## 5. Proposed Next Gate

Recommended next mainline:

`Quality warning issue identity evidence gate`

Purpose:

1. Establish a direct, accepted lineage from the accepted live run to the quality gate issue rows.
2. Extract only the minimal structured issue fields needed for disposition:
   - `status`
   - `issues_count`
   - per issue: `rule_code`, `severity`, `fund_code`, `field_name`, `reason`, `coverage_scope`, `message`
3. Classify each issue as one of:
   - `extractor_data_gap`
   - `strict_golden_coverage_gap`
   - `quality_gate_policy_gap`
   - `artifact_lineage_gap`
   - `unknown_needs_live_reproduction`
4. Recommend whether each issue needs implementation, test-only coverage, docs/control disposition, live reproduction or deferral.

Expected outcome:

- `ACCEPT_WITH_ROOT_CAUSE_CANDIDATES_NOT_READY` if identities and likely root causes are proven but fixes are out of scope.
- `ACCEPT_WITH_LINEAGE_BLOCKER_NOT_READY` if issue identity cannot be proven from durable or controlled evidence.

## 6. Evidence Route

The next evidence gate should use this sequence:

| Step | Route | Acceptance |
|---|---|---|
| E0 | Re-read accepted artifacts and control docs. | PASS if current gate and checkpoint match `Quality warning issue identity evidence gate`. |
| E1 | Try no-live durable lineage first: use only issue rows or artifact identity already recorded in accepted artifacts. | PASS only if an accepted artifact already records the issue rows, or records exact `quality_gate_json` / `quality_gate_md` path plus stable identity such as hash, size and run id, and the current file matches that identity. |
| E2 | If E1 fails because accepted artifacts only contain issue count, record `artifact_lineage_gap`. | PASS if no issue identity is claimed. |
| E3 | If live authorization is active and controller accepts a separate live execution boundary, run one controlled reproduction command. | PASS only for the exact accepted sample command under the evidence gate, with bounded capture. |
| E4 | Extract structured issue rows from the resulting `quality_gate.json` only; do not read full generated report/PDF/cache. | PASS if count equals `3` and rows are summarized minimally. |
| E5 | Map each issue to root-cause candidate using `fund_agent/fund/quality_gate.py`, `quality_gate_integration.py` and focused tests. | PASS if each candidate has owner and next handling. |

Controlled live reproduction command, if E1/E2 cannot establish issue identity and live remains authorized:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Live reproduction stop conditions:

- stop after one command
- capture stdout/stderr under `/tmp`
- do not promote full stdout/report body
- record metadata, stderr quality lines and `quality_gate_json` issue summary only
- do not run provider/LLM/`--use-llm`
- do not run readiness/release/PR commands
- do not change source/test/runtime behavior

The user's current live authorization may be consumed only by this separately accepted evidence gate, not by this planning gate.

## 7. Allowed Commands For Next Evidence Gate

No-live commands:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
rg -n "quality_gate_status|quality_gate_issues|quality_gate_json|quality_gate_md" docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-20260612.md docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md
rg -n "FQ0|FQ1|FQ2|FQ2F|FQ3|FQ4|FQ5|FQ6|QualityGateIssue|_aggregate_gate_status" fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py
```

Optional no-live deterministic checks:

```bash
uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py -q
uv run ruff check fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py
```

Live command:

- allowed only if the accepted evidence gate explicitly opens E3 live reproduction using the exact command above.

## 8. Residual Owner Table

| Residual | Owner | Next handling |
|---|---|---|
| Issue identity is not yet accepted durable fact | controller/evidence owner | `Quality warning issue identity evidence gate` |
| Three live quality issues remain unresolved | release/readiness owner + quality gate owner | root-cause evidence, then possible implementation/fix planning |
| Possible extractor data gap | Fund/extractor owner | only after issue identity proves extractor-related rule |
| Possible strict golden coverage gap | golden/readiness owner | only after issue identity proves correctness/coverage-related rule |
| Possible artifact lineage gap | controller/evidence owner | record as blocker; do not infer issue identities |
| Additional live sample coverage | evidence/release owner | separate live sample gate |
| Provider/LLM readiness | provider/runtime owner | separate provider/LLM live acceptance gate |

## 9. Required Reviews

Before accepting this plan:

- DS review
- MiMo review

Review focus:

- whether the plan refuses to infer issue identities from unaccepted residue
- whether live reproduction is properly separated from planning and bounded
- whether root-cause evidence precedes implementation
- whether `warn` and `quality_gate_issues=3` still block readiness
- whether residual owners and next gates are explicit

## 10. Acceptance Criteria

This planning gate can be accepted only if:

1. DS and MiMo review the plan.
2. Controller judgment disposes every finding.
3. `git status --short`, `git status --branch --short`, `git diff --name-only` and `git diff --check` are recorded.
4. Local accepted checkpoint contains only plan/review/controller artifacts.
5. Release/readiness remains `NOT_READY`.

## 11. Next Entry

If accepted:

`Quality warning issue identity evidence gate`

Deferred entries:

- quality warning implementation/fix gate
- additional EID live sample gate
- live provider / LLM acceptance gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready / release external-state gate
