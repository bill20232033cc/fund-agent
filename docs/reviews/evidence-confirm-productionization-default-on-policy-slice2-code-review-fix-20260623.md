# Evidence Confirm Default-on Policy Slice 2 Code Review Fix

## Gate

- Work unit: Evidence Confirm default-on policy
- Slice: EC-DO-2
- Gate: code review fix worker only
- Accepted finding fixed: `docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice2.md` finding 1 low
- Allowed write set:
  - `tests/ui/test_cli.py`
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md`

## Scope

- Added standalone CLI regression test:
  - `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`
- No production code was edited in this fix pass.
- No live, PDF, network, provider, or LLM commands were run.
- No PR, git commit, git staging, or control-doc mutation was performed.

## Fix

The new test invokes:

```text
analyze 110011 --dev-override
```

It asserts:

- the deterministic CLI analyze path succeeds;
- the Service request mode is `developer_override`;
- `developer_overrides` is not `None`;
- `developer_overrides.evidence_confirm_policy == "off"`.

This directly covers the review concern that the plain `--dev-override` / no
`--evidence-confirm-policy` case was previously only embedded inside
`test_analyze_cli_calls_service_and_prints_report`, while the accepted plan
expected a standalone test with this exact purpose and name.

## Validation

- `uv run pytest tests/ui/test_cli.py -q -k test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`
  - Result: passed, `1 passed, 82 deselected`
- `uv run pytest tests/ui/test_cli.py -q`
  - Result: passed, `83 passed`
- `uv run ruff check tests/ui/test_cli.py`
  - Result: passed
- `git diff --check -- tests/ui/test_cli.py docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md`
  - Result: passed, no whitespace diagnostics
- `git diff --check --no-index -- /dev/null docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md`
  - Result: no whitespace diagnostics; exit code `1` is expected for `--no-index` when the compared new file differs from `/dev/null`

## Finding Status

- Finding 1 low: 已修复

## Residual Risks

- Quality gate ECQ warn-policy regression coverage: covered by later approved slice EC-DO-3.
- Control-plane truth sync: covered by later approved slice EC-DO-4.
- Checklist Evidence Confirm CLI support: assigned to a separate work unit.
- `analyze-annual-period` Evidence Confirm summary display question from the review artifact: requiring explicit user/controller decision because it is outside Slice EC-DO-2 fix scope.

## Verdict

FIX_READY_FOR_REREVIEW
