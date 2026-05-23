# P19-S5 Ready-To-Open-Draft-PR Reconciliation — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 ready-to-open-draft-PR reconciliation
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Implementation HEAD before this reconciliation: `87dd8e9`
- Compared against: `origin/main`
- Implementation ahead count before this reconciliation: 11 commits
- This artifact and the matching control-doc update are the final local readiness record for the draft PR gate.

## Inclusion Set

The implementation inclusion set is the 11 commits ahead of `origin/main` before this reconciliation:

```text
87dd8e9 gateflow: record p19-s5 aggregate accepted commit
497a2b7 gateflow: accept p19-s5 aggregate review
2ab9b33 gateflow: record p19-s5 s5-3 accepted commit
355874b gateflow: accept p19-s5 s5-3 cli docs
ff9ff07 gateflow: record p19-s5 s5-2 accepted commit
5eb922c gateflow: accept p19-s5 s5-2 service cache
7a173ec gateflow: record p19-s5 s5-1 accepted commit
459038b gateflow: accept p19-s5 s5-1 capability source
c540334 gateflow: accept plan for p19-s5-all-a-market-thermometer
f4ee668 gateflow: accept p19-s5 source feasibility
6c2f759 gateflow: accept plan for p19-s5-all-a-pe-source-gate
```

Included implementation files:

- `fund_agent/fund/data/thermometer_source.py`
- `fund_agent/fund/data/thermometer_cache.py`
- `fund_agent/services/thermometer_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/data/test_thermometer_source.py`
- `tests/fund/data/test_thermometer_cache.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Included control/review artifacts:

- `docs/implementation-control.md`
- `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md`
- `docs/reviews/p19-s5-all-a-pe-source-gate-plan-patch-20260523.md`
- `docs/reviews/p19-s5-plan-review-mimo-20260523.md`
- `docs/reviews/p19-s5-plan-review-glm-20260523.md`
- `docs/reviews/p19-s5-plan-rereview-mimo-20260523.md`
- `docs/reviews/p19-s5-plan-rereview-glm-20260523.md`
- `docs/reviews/p19-s5-plan-review-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-plan-review-controller-acceptance-20260523.md`
- `docs/reviews/p19-s5-source-feasibility-20260523.md`
- `docs/reviews/p19-s5-source-feasibility-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- `docs/reviews/p19-s5-implementation-plan-review-ds-20260523.md`
- `docs/reviews/p19-s5-implementation-plan-review-glm-20260523.md`
- `docs/reviews/p19-s5-implementation-plan-rereview-ds-20260523.md`
- `docs/reviews/p19-s5-implementation-plan-rereview-glm-20260523.md`
- `docs/reviews/p19-s5-implementation-plan-review-controller-acceptance-20260523.md`
- `docs/reviews/p19-s5-s5-1-capability-source-implementation-20260523.md`
- `docs/reviews/p19-s5-s5-1-code-review-ds-20260523.md`
- `docs/reviews/p19-s5-s5-1-code-review-glm-20260523.md`
- `docs/reviews/p19-s5-s5-1-code-review-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-s5-2-service-cache-implementation-20260523.md`
- `docs/reviews/p19-s5-s5-2-code-review-ds-20260523.md`
- `docs/reviews/p19-s5-s5-2-code-review-glm-20260523.md`
- `docs/reviews/p19-s5-s5-2-code-review-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-s5-3-cli-docs-implementation-20260523.md`
- `docs/reviews/p19-s5-s5-3-code-review-ds-20260523.md`
- `docs/reviews/p19-s5-s5-3-code-review-glm-20260523.md`
- `docs/reviews/p19-s5-s5-3-code-review-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-aggregate-deepreview-ds-20260523.md`
- `docs/reviews/p19-s5-aggregate-deepreview-glm-20260523.md`
- `docs/reviews/p19-s5-aggregate-deepreview-controller-judgment-20260523.md`
- `docs/reviews/p19-s5-ready-to-open-draft-pr-reconciliation-20260523.md`

## Exclusion Set

The following untracked files remain excluded from the P19-S5 draft PR unless a later gate explicitly accepts them:

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`
- `docs/reviews/agentds-repo-deepreview-20260523.md`
- `docs/reviews/agentglm-repo-deepreview-20260523.md`
- `docs/reviews/controller-judgment-repo-deepreview-20260523.md`

## Accepted Behavior

- All-A thermometer source uses `akshare.stock_a_ttm_lyr()` and `akshare.stock_a_all_pb()`.
- All-A source contract is exact `date`, `middlePETTM`, and `middlePB`.
- `wind_all_a` is a market thermometer code, not a six-digit index.
- No-argument `fund-analysis thermometer` routes to self-owned all-A via Service default normalization.
- `wind_all_a` cache uses `cache/thermometer/market/wind_all_a_history.json`; supported indexes remain under `cache/thermometer/index/`.
- Unsupported well-formed index codes remain item-level unavailable and cannot be loaded from forged cache files.
- CLI help, JSON/plain output, root README, Fund README, and tests README now reflect all-A as the default thermometer CLI path.
- `fund-analysis analyze` behavior is not expanded to all-A; automatic valuation-state integration remains limited to exact supported-index behavior accepted in P19-S3.

## Validation

Controller-verified validation across accepted gates:

```text
pytest tests/fund/data/test_thermometer_source.py -q
37 passed

pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
33 passed

pytest tests/ui/test_cli.py -q
38 passed

pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
108 passed

pytest tests/services/test_fund_analysis_service.py -q
20 passed

ruff check required P19-S5 files
All checks passed!

git diff --check
passed with no output
```

## Residuals And Owners

Accepted non-blocking residuals:

- Retry-budget harmonization between index and all-A sources: future production hardening.
- Index duplicate-date fail-closed cleanup: future Capability data-quality cleanup.
- Legacy public-page adapter branch cleanup or explicit opt-in re-exposure: future transitional adapter cleanup.
- All-A `asyncio.gather` cancellation wrapping: future async-hardening cleanup if a true async runtime uses the source directly.
- P19-S4 exact-index PE/PB sources remain unresolved for `399006`, `000688`, `000922`, `000932`, and `000933`; this is outside P19-S5 and already deferred.
- Live akshare / Legulegu availability remains an external-data residual mitigated by cache and unavailable semantics.

## Draft PR Boundary

This reconciliation is local-only. It does not push, create a draft PR, request review, mark ready, merge, comment on GitHub, close PRs/issues, delete branches, or modify external state.

The next step is the draft PR gate, which requires explicit user authorization before any `git push` or GitHub PR action.
