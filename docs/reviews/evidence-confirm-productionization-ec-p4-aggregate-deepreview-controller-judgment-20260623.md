# Evidence Confirm Productionization EC-P4 Aggregate Deepreview Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: aggregate deepreview controller judgment
- Classification: heavy
- Branch: evidence-confirm-productionization
- Latest accepted slice commit: `4c80d86 gateflow: accept ec-p4 service integration slice 6`
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-controller-judgment-20260623.md`

## Inputs

- DS aggregate deepreview: `docs/reviews/code-review-20260623-002000-ds-ec-p4-aggregate-deepreview.md`
- MiMo aggregate deepreview: `docs/reviews/code-review-20260623-002000-mimo-ec-p4-aggregate-deepreview.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-fix-20260623.md`
- DS targeted re-review: `docs/reviews/code-review-rereview-20260623-003000-ds-ec-p4-aggregate-deepreview.md`
- MiMo targeted re-review: `docs/reviews/code-review-rereview-20260623-003000-mimo-ec-p4-aggregate-deepreview.md`

## Controller Decision

Accepted.

EC-P4 aggregate deepreview is accepted after one accepted finding was fixed and re-reviewed. The accepted code now keeps Service above forbidden document/source internals by importing the Evidence Confirm runner through a Fund-layer typed facade:

- `fund_agent/fund/evidence_confirm_runner.py`
- `fund_agent/services/fund_analysis_service.py`

The fix preserves EC-P4 behavior: Service still calls only a typed Fund-layer repository-bounded Evidence Confirm runner contract, and still does not read documents, repository internals, PDF/cache, source helpers, parser artifacts, provider clients, LLMs or network directly.

## Review Results

| Reviewer | Artifact | Verdict | Findings |
|---|---|---|---|
| AgentDS | `docs/reviews/code-review-20260623-002000-ds-ec-p4-aggregate-deepreview.md` | PASS_WITH_FINDINGS | F1 warn, F2 info, F3 info |
| AgentMiMo | `docs/reviews/code-review-20260623-002000-mimo-ec-p4-aggregate-deepreview.md` | PASS | 0 |

## Finding Disposition

| Finding | Controller disposition | Reason / destination |
|---|---|---|
| F1 Service import boundary test failed on `evidence_confirm_sources` import path | accepted | The controller reproduced the failing boundary test. Fix introduced Fund-layer facade `evidence_confirm_runner` and updated Service import. DS and MiMo targeted re-review both mark F1 `已修复`. |
| F2 `_evidence_confirm_quality_gate_issues(None)` differs from `run_quality_gate_for_bundle(None)` | rejected-with-reason | This is an intentional compatibility boundary: public production quality-gate entry preserves no-summary/no-ECQ legacy behavior, while the private helper can represent explicit not-run summaries. It is not a current EC-P4 defect. Optional docstring cleanup can be handled only if this helper becomes a public contract. |
| F3 `_semantic_issue_count` private helper name is broader than block/warn-only behavior | rejected-with-reason | The behavior is correct for `issue_count`, tested, private, and not a production contract defect. Renaming would be readability-only churn outside the accepted fix scope. |

## Re-review Results

| Reviewer | Artifact | Verdict | F1 status |
|---|---|---|---|
| AgentDS | `docs/reviews/code-review-rereview-20260623-003000-ds-ec-p4-aggregate-deepreview.md` | PASS | 已修复 |
| AgentMiMo | `docs/reviews/code-review-rereview-20260623-003000-mimo-ec-p4-aggregate-deepreview.md` | PASS | 已修复 |

## Controller Validation

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries -q
1 passed
```

```text
uv run pytest tests/services/test_fund_analysis_service.py -q -k evidence_confirm
8 passed, 32 deselected
```

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/test_evidence_confirm_semantic.py -q
47 passed
```

```text
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/fund/evidence_confirm_runner.py
All checks passed!
```

```text
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/fund/evidence_confirm_runner.py docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-fix-20260623.md
<no output>
```

Reviewer-recorded broader validation:

- DS recorded full project pytest result `2259 passed`.
- MiMo recorded EC-P4 focused suite result `255 passed`.

## Residual Risks

| Residual | Classification | Destination |
|---|---|---|
| Checklist Evidence Confirm CLI support remains absent | assigned to later work unit | explicit checklist EC gate |
| Default-on Evidence Confirm remains unauthorized | assigned to later work unit | default policy decision gate |
| Provider-backed semantic quality remains unproven | assigned to later work unit | provider-backed semantic quality gate |
| Release/readiness remains `NOT_READY` | tracked by existing control state | later readiness/release gate |
| EC-P4 branch has not yet been pushed after local Slice 1-6 and aggregate deepreview commits | covered by later gate | ready-to-open-draft-PR / push gate |

## Next Entry Point

EC-P4 ready-to-open-draft-PR gate.

Do not push, mutate PR-40, mark ready, merge or claim release/readiness before the later reviewed gates.

## Verdict

ACCEPT_EC_P4_AGGREGATE_DEEPREVIEW_READY_FOR_ACCEPTED_DEEPREVIEW_COMMIT_NOT_READY
