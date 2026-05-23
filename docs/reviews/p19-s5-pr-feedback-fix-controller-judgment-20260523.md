# P19-S5 PR Feedback Fix Controller Judgment — 2026-05-23

## Scope

- Work unit: P19-S5 all-A market thermometer default
- Gate: PR 13 user-feedback fix review
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- PR: https://github.com/bill20232033cc/fund-agent/pull/13

## User-Reported Blockers

The user reproduced two blocking runtime failures after PR 13 was marked ready for review:

- `fund-analysis thermometer --index 000300 --json` crashed with `libmini_racer` native fatal.
- `fund-analysis thermometer --index wind_all_a,000300,000905 --json` crashed with the same native fatal.
- `fund-analysis thermometer --json` did not crash but returned unavailable because real all-A PE data had a same-date duplicate conflict.

## Fix Summary

- Index PE/PB source fetch now runs PE then PB sequentially instead of using `asyncio.gather`.
- All-A PE/PB source fetch now runs PE then PB sequentially.
- All-A same-source duplicate positive rows for the same date are deterministically collapsed by keeping the last row in input order.
- Schema drift, bool, non-numeric, NaN/Infinity, no positive rows, and no common PE/PB dates remain fail-closed.
- README files were synchronized with the current source behavior.
- Regression tests now cover thread-overlap detection and a deterministic no-PB-scheduling-before-PE-completion check.

## Review Evidence

- Implementation artifact: `docs/reviews/p19-s5-pr-feedback-fix-implementation-20260523.md`
- AgentDS review: `docs/reviews/p19-s5-pr-feedback-fix-code-review-ds-20260523.md`
- AgentGLM review: `docs/reviews/p19-s5-pr-feedback-fix-code-review-glm-20260523.md`
- Controller diff review of:
  - `fund_agent/fund/data/thermometer_source.py`
  - `tests/fund/data/test_thermometer_source.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Review Judgment

Both independent reviews found no blocking correctness, stability, or maintainability issue.

AgentDS raised one non-blocking test-hardening note: the initial concurrency guard relied on default multi-thread executor overlap. Controller accepted that note as worth fixing before commit. AgentCodex added a deterministic test that monkeypatches `asyncio.to_thread`, makes the PE fetcher fail, and proves PB is not scheduled before PE finishes. This closes the test-boundary concern without changing production logic.

AgentGLM returned PASS and confirmed:

- PE/PB concurrent entry into akshare / mini_racer is removed.
- Duplicate-date collapse stays within a single source table and does not add interpolation or cross-source inference.
- README updates are accurate.

## Validation

Controller-verified:

```text
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
111 passed

ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py tests/services/test_thermometer_service.py tests/ui/test_cli.py
All checks passed!

git diff --check
passed

fund-analysis thermometer --json
exit 0, unavailable=false, index_code=wind_all_a, data_date=2026-05-22

fund-analysis thermometer --index 000300 --json
exit 0, unavailable=false, index_code=000300, data_date=2026-05-22

fund-analysis thermometer --index wind_all_a,000300,000905 --json
exit 0, unavailable=false, partial_unavailable=false, three readings available
```

## Residual Risks

- Real akshare / Legulegu smoke remains externally dependent and should not run in default CI.
- Future code adding concurrent akshare calls must explicitly review native dependency safety.
- Batch thermometer reads remain sequential in Service; this is currently acceptable and avoids reintroducing native concurrency risk.

## Gate Decision

No further fix/re-review loop is required for this user feedback.

The fix is accepted for local commit and push to PR 13.
