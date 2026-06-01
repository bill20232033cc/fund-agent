# MVP provider auth/config verification controller judgment

Gate: `MVP provider auth/config verification gate`
Role: Gateflow controller
Date: 2026-05-31
Decision: `provider_auth_passed_then_blocked_by_llm_contract`

## Preflight

- Branch: `codex/local-reconciliation`
- Worktree: already contained prior smoke/diagnostic artifacts and unrelated untracked files; this gate only added `20260531-auth-verification` evidence and review artifacts.
- Protected branch check: current branch is not `main`, `master`, `develop` or `release/*`.

## Decision

The configured MiMo-compatible provider is now usable:

- typed config loads successfully;
- minimal production-provider request succeeds with `model_name=mimo-v2.5-pro`;
- no API key leakage was found in this gate's report directory.

The PR #21 real `--use-llm` smoke still fails closed, but the root cause has moved past provider authentication. Same-source Service diagnostic shows chapter 1 reached a real writer draft and then failed programmatic/LLM audit contract checks:

- missing required section markers: `结论要点`, `详细情况`, `证据与出处`;
- missing required output item marker: `会改变产品理解的特别情况（如有）`;
- non-asserted candidate facets were written as asserted facts;
- LLM audit response parse failed;
- regenerate was attempted but the follow-up provider call timed out.

Therefore the current blocker is not the old HTTP `401` provider_config issue. The next gate should be `MVP LLM writer/auditor contract hardening gate`.

## Code Fix Decision

No runtime code fix is accepted in this gate. The evidence supports a new implementation gate focused on writer/auditor prompt/protocol hardening and timeout policy, with fake-client tests before another live provider smoke.

## Boundaries

- No runtime code changed.
- No default deterministic `analyze/checklist` behavior changed.
- No deterministic fallback added to `--use-llm`.
- No PR push, merge, ready-for-review, release or promotion action performed.
- No golden fixture, quality gate, score, snapshot, Host/Agent/dayu or schema changes made.
- Secret hygiene preserved.

## Accepted Evidence

- Gate evidence: `docs/reviews/mvp-provider-auth-config-verification-20260531.md`
- Raw directory: `reports/mvp-local-acceptance/20260531-auth-verification/`
- Chapter diagnostic: `reports/mvp-local-acceptance/20260531-auth-verification/chapter1-api-diagnostic.json`

## Next Entry

`MVP LLM writer/auditor contract hardening gate`

The next gate should start with a plan/review pass because it may affect writer/auditor contracts, prompt protocol, repair behavior and provider timeout configuration.
