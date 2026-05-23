# P17 Main Branch Closeout（2026-05-22）

## Verdict

`MERGED`

P17-S1 tracking-error hardening and thermometer design-direction correction has been merged to `main` through PR #11.

## Merge Facts

| Field | Value |
|---|---|
| PR | https://github.com/bill20232033cc/fund-agent/pull/11 |
| PR title | `P17-S1 tracking error hardening and thermometer direction` |
| Source branch | `p17-tracking-error-thermometer-direction` |
| Target branch | `main` |
| Merge method | squash merge |
| Merge commit | `5c54994b9e7232e6144e730fff6d83d5c8ab80fb` |
| Merged at | `2026-05-22T13:56:49Z` |
| Local main alignment | local `main` reset to `origin/main` after creating `backup/p17-pre-squash-main` |

## Accepted Scope

- `tracking_error` direct-disclosure extraction now fails closed with specific blocker notes instead of stale generic `tracking_error_ambiguous` semantics.
- Target-only and mixed actual/target rows no longer prematurely suppress later valid direct disclosures.
- Multi-match, table/text inconsistency, manager narrative, benchmark-only, standard-deviation-only, unparseable, and `§2` fallback cases have focused coverage.
- `docs/design.md` v2.2 and `docs/implementation-control.md` now share the corrected thermometer direction: current public-page query/cache is transitional; future project-owned thermometer capability is accepted as a direction; automatic thermometer-to-`valuation_state` mapping remains a separate gate.

## Validation

| Validation | Result |
|---|---|
| PR #11 CI `test` | success |
| PR merge state before merge | `CLEAN` |
| MiMo PR review | `PASS_WITH_FINDINGS`, no accepted blocker |
| GLM PR review | `PASS_WITH_FINDINGS`, no accepted blocker |
| Controller PR judgment | `ACCEPTED_DRAFT_PR_PASS` |

## Exclusions Preserved

- No production `tracking_error` golden rows were added.
- No source CSV or RR-13 edits were made.
- No Service/UI/Runtime/Engine annual-report source access changes were introduced.
- No calculated tracking error, external index series, methodology extraction, constituents extraction, Dayu runtime, LLM audit, or Evidence Confirm execution was introduced.
- Local input drafts remain excluded from the PR and closeout: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Next Gate

P17 is merged on `main`. The next gate is post-P17 follow-up planning.
