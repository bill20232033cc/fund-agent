# P14 Main-Branch Closeout（2026-05-22）

## Result

P14-S1 is merged to `main`.

## PR

- PR: https://github.com/bill20232033cc/fund-agent/pull/9
- Title: P14-S1 index quality denominators
- State: `MERGED`
- Base: `main`
- Head: `docs/post-p13-follow-up-planning`
- Merge method: squash
- Merge commit: `746bfda7975e7c6922e80ab8c7a3e89cba3c6822`
- Merged at: `2026-05-22T03:13:56Z`

## Accepted Scope

- Post-P13 follow-up planning selected P14-S1 quality-denominator coverage.
- `index_profile` and `tracking_error` are conditional P1 quality fields for `index_fund` / `enhanced_index`.
- Non-index fund types are excluded from these two denominator fields.
- Missing, unknown, or conflicting fund type remains conservative and scorable.
- Snapshot comparable values and golden prefill support dataclass-valued structured fields through a Fund Capability internal helper.
- Reviewed `001548` `index_profile` production golden rows were added for benchmark-derived fields only.
- `161725` deterministic enhanced-index fixture covers the direct disclosure path.

## Validation and Review

- PR CI `test`: passed.
- Local full suite before PR: `428 passed`.
- Ruff: passed.
- `git diff --check HEAD`: passed.
- Code reviews: MiMo PASS; GLM PASS_WITH_FINDINGS then targeted re-review PASS/PASS.
- Aggregate reviews: MiMo PASS; GLM PASS_WITH_FINDINGS accepted after controller documented golden substitution rationale.
- PR reviews: MiMo PASS; GLM PASS_WITH_FINDINGS accepted after PR body golden note update.

## Excluded Scope

- No calculated tracking error.
- No external index series adapter.
- No methodology or constituents extraction.
- No QDII subtype redesign.
- No E1-E3, Evidence Confirm, Dayu runtime, Host, Engine, or tool loop.
- No RR-13 source data edits.
- `docs/repo-audit-20260521.md` remains excluded and untracked.

## Local Reconciliation

- Local `main` had diverged from `origin/main`; the pre-sync local branch was preserved as `backup/p14-pre-sync-main`.
- Local `main` was aligned to `origin/main` at `746bfda7975e7c6922e80ab8c7a3e89cba3c6822`.

## Next Entry Point

Post-P14 follow-up planning / next phase selection.
