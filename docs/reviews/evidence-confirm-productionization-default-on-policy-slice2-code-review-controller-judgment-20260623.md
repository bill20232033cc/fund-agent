# Evidence Confirm Productionization Default-on Policy Slice 2 Code Review Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Slice: EC-DO-2 CLI Surface And No-opt-out Guard.
- Gate: code review controller judgment.
- Classification: heavy.
- Branch: `evidence-confirm-productionization`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-controller-judgment-20260623.md`.

## Inputs

| Role | Dispatch skill trigger | Artifact | Verdict |
|---|---|---|---|
| AgentCodex implementation worker | `$gateflow` | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md` | `IMPLEMENTATION_SLICE_READY_FOR_REVIEW` |
| AgentDS code reviewer | `/deepreview` | `docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice2.md` | `CODE_REVIEW_PASS_WITH_FINDINGS` |
| AgentMiMo code reviewer | `/deepreview` | `docs/reviews/code-review-20260623-033922.md` | `CODE_REVIEW_PASS` |
| AgentCodex fix worker | `$gateflow` | `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md` | `FIX_READY_FOR_REREVIEW` |
| AgentDS targeted re-reviewer | `/deepreview` | `docs/reviews/code-review-rereview-20260623-ds-evidence-confirm-default-on-policy-slice2.md` | `CODE_REVIEW_REREVIEW_PASS` |

## Controller Decision

Accepted.

Slice EC-DO-2 is accepted after one focused fix/re-review loop. The implementation aligns CLI help and tests with the accepted product default-on policy without exposing a product opt-out:

- `--evidence-confirm-policy` help now describes a developer override, not product opt-in.
- Product `fund-analysis analyze` CLI default can surface safe Evidence Confirm `warn` summary fields from the Service result.
- No `--no-evidence-confirm`, public `--evidence-confirm`, or checklist Evidence Confirm CLI flag is exposed.
- Plain `--dev-override` without `--evidence-confirm-policy` remains developer-mode Evidence Confirm `off` and does not inherit product `warn`.
- Explicit developer `block` behavior remains covered.
- CLI stays boundary-safe and does not import Fund Evidence Confirm runners, repository/source/PDF/parser/provider internals, Docling or pdfplumber.

## Changed Files

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md`
- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md`

Review/control artifacts:

- `docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice2.md`
- `docs/reviews/code-review-20260623-033922.md`
- `docs/reviews/code-review-rereview-20260623-ds-evidence-confirm-default-on-policy-slice2.md`
- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-controller-judgment-20260623.md`

## Finding Disposition

| Finding / note | Controller disposition | Status / destination |
|---|---|---|
| DS finding 1 low: accepted plan expected standalone `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off` | accepted | fixed by `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md`; re-reviewed as pass by `docs/reviews/code-review-rereview-20260623-ds-evidence-confirm-default-on-policy-slice2.md` |
| DS open question: `analyze-annual-period` CLI does not echo `current_year_result.evidence_confirm_summary` | deferred-with-owner | EC-DO-4 documentation/control sync must record current behavior or route a later annual-period CLI Evidence Confirm display gate; not part of EC-DO-2 approved required tests |
| MiMo residual: quality gate ECQ warn-policy regressions | covered by later approved slice | EC-DO-3 |
| MiMo residual: docs/control truth sync | covered by later approved slice | EC-DO-4 |

## Controller Validation

```text
uv run pytest tests/ui/test_cli.py -q
83 passed
```

```text
uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
git diff --check -- fund_agent/ui/cli.py tests/ui/test_cli.py docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice2.md docs/reviews/code-review-20260623-033922.md docs/reviews/code-review-rereview-20260623-ds-evidence-confirm-default-on-policy-slice2.md docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-code-review-fix-20260623.md docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md
<no output>
```

## Residual Risks

| Residual | Classification | Owner / destination |
|---|---|---|
| Quality gate ECQ warn-policy regressions not updated | covered by later approved slice | EC-DO-3 |
| Docs/control truth sync for default-on policy not completed | covered by later approved slice | EC-DO-4 |
| `analyze-annual-period` CLI Evidence Confirm summary display not implemented | deferred-with-owner | EC-DO-4 current-fact documentation or later annual-period CLI Evidence Confirm display gate |
| Checklist Evidence Confirm CLI/support remains absent | separate blocker | checklist Evidence Confirm gate |
| Provider-backed/live semantic quality remains unproven | separate blocker | provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage remains unproven | separate blocker | multi-sample live evidence gate |
| Release/readiness remains `NOT_READY` | release/readiness gate | after blocker closure |

## Next Entry Point

Accepted slice commit, then Slice EC-DO-3 Quality Gate Regression Guard implementation.

Do not push, mark PR-40 ready, merge, claim release/readiness, or run live/PDF/network/provider/LLM commands before separate reviewed gates.

## Verdict

ACCEPT_DEFAULT_ON_POLICY_SLICE2_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY
