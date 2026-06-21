# FundDisclosureDocument Non-active Facade/Processor Route PR Review Fix Evidence

## Scope

- Gate: PR review fix
- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- PR: #36 `https://github.com/bill20232033cc/fund-agent/pull/36`
- Review artifact: `docs/reviews/pr-36-review-20260621-035635.md`
- Accepted finding: 001, stale control/startup current gate and next entry.
- Output file: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-pr-review-fix-evidence-20260621-035848.md`

## Changes

- Updated `docs/current-startup-packet.md` current mainline gate, next entry point, and resume checklist from stale implementation/code-review wording to PR #36 PR review fix/re-review and accepted PR review commit/follow-up push.
- Updated `docs/implementation-control.md` latest control update, current gate table, implementation objective, next entry point, and resume checklist to the same PR #36 chain.
- Preserved production facts and non-goal boundaries: no parser replacement, no source-policy change, no Service/UI/Host/renderer/quality-gate FDD consumption, no real-report correctness/golden/readiness/release claim, no mark-ready or merge.

## Validation

- `rg -n "Current active gate|Active gate|Next entry point|Current next entry|current next entry|Validation/Review Gate|Fund Processor Non-active ParsedAnnualReport Registry Integration Code Review Gate|fund-processor-non-active-registry-integration|post-merge control sync accepted PR review" docs/current-startup-packet.md docs/implementation-control.md`
  - Result: current entry points now refer to PR #36 PR review fix/re-review and accepted PR review commit/follow-up push; stale old gate strings remain only in unrelated historical ledger entries.
- `git diff --check`
  - Result: passed, no output.
- `gh pr checks 36`
  - Result: `test pass 56s`.

## Finding Status

- 001: `已修复`

## Residual Risks

- No production code was changed or re-tested in this fix gate because the accepted finding is docs/control-only.
- The PR #36 follow-up push will create a new remote head, so draft-PR-pass must re-check CI after push.
- Historical ledger entries were not rewritten; they remain evidence-chain history and do not override the current control surface.
