# Evidence Confirm Productionization Default-on Policy Slice 2 Implementation Evidence

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Slice: EC-DO-2 CLI Surface And No-opt-out Guard.
- Role: AgentCodex implementation worker only.
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`.
- Prior accepted slice: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-code-review-controller-judgment-20260623.md`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md`.

## Scope

Allowed source/test files changed:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Allowed artifact file changed:

- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md`

Files intentionally not changed:

- Service, quality gate, docs/control, README, PR state, git state, and all other files.

## Implementation

- Updated `--evidence-confirm-policy` help text from opt-in wording to developer override wording: the flag is for `off|warn|block` and only takes effect with `--dev-override`.
- Kept `_build_developer_overrides()` rejection when `--evidence-confirm-policy` is provided without `--dev-override`.
- Kept plain `--dev-override` default `evidence_confirm_policy="off"` behavior.
- Kept checklist without Evidence Confirm parameters.
- Kept `_echo_evidence_confirm_summary()` limited to safe summary fields only.
- Did not add `--no-evidence-confirm`, `--evidence-confirm`, checklist Evidence Confirm flags, report-body rendering changes, product opt-out, Service changes, quality gate changes, live/PDF/network/provider/LLM commands, commit, or push.

## Test Changes

- Replaced the old default analyze no-EC-lines test with a default product analyze test that:
  - asserts `mode == "product"`;
  - asserts `developer_overrides is None`;
  - asserts Evidence Confirm safe summary lines print for status, policy `warn`, checked count, failed count, and auditability score;
  - asserts the report body still prints after the summary;
  - asserts unsafe excerpt, PDF path, parser payload, and provider payload strings do not appear.
- Kept developer override `warn` summary coverage and renamed it to developer override wording.
- Kept the existing plain `--dev-override` regression in `test_analyze_cli_calls_service_and_prints_report`, asserting developer default `evidence_confirm_policy == "off"`.
- Kept rejection coverage for `--evidence-confirm-policy` without `--dev-override`.
- Kept explicit developer `block` CLI coverage.
- Extended analyze/checklist option guards to assert no public product `--no-evidence-confirm` or `--evidence-confirm` flags are exposed.

## Validation

```text
uv run pytest tests/ui/test_cli.py -q -k "evidence_confirm or checklist_cli_rejects_use_llm_option or checklist_cli_help_does_not_expose_evidence_confirm_policy or analyze_cli_help_documents_auto_valuation_and_opt_out or analyze_cli_calls_service_and_prints_report"
9 passed, 73 deselected in 0.67s
```

```text
uv run pytest tests/ui/test_cli.py -q
82 passed in 0.98s
```

```text
uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
git diff --check -- fund_agent/ui/cli.py tests/ui/test_cli.py
<no output>
```

```text
git diff --check --no-index /dev/null docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md
<no output; exit 1 because /dev/null vs new file has diff, not because of whitespace errors>
```

## Residual Risks

| Residual | Classification | Owner / destination |
|---|---|---|
| Quality gate ECQ warn-policy regressions not updated in this slice | covered by later approved slice | EC-DO-3 |
| Docs/control truth sync for default-on policy not completed | covered by later approved slice | EC-DO-4 |
| Checklist Evidence Confirm CLI/support remains absent | assigned to later work unit | checklist Evidence Confirm gate |
| Provider-backed/live semantic quality remains unproven | assigned to later work unit | provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage remains unproven | assigned to later work unit | multi-sample live evidence gate |
| Release/readiness remains `NOT_READY` | assigned to later work unit | release/readiness gate after blocker closure |

No unclassified residual risk remains in EC-DO-2 implementation scope.

## Verdict

IMPLEMENTATION_SLICE_READY_FOR_REVIEW
