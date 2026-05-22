# P17-S1 ready-to-open-draft-PR reconciliation（2026-05-22）

## Verdict

`READY_TO_OPEN_DRAFT_PR_PENDING_USER_AUTHORIZATION`

P17-S1 is locally ready for a draft PR. The branch is `main`, upstream is `origin/main`, and local `main` is 6 commits ahead of `origin/main`. The current gate is local reconciliation only; pushing, creating a draft PR, commenting on GitHub, marking ready, merging, or deleting branches still requires explicit user authorization.

## Included Commits

| Commit | Summary | Role |
|---|---|---|
| `1bd3677` | `docs: accept post-p16 follow-up planning` | Selects P17-S1 after P16 closeout. |
| `aa7b30f` | `docs: reconcile design control alignment guide` | Partially accepts design/control alignment guide, updates design v2.1 and README non-goal wording. |
| `8cba095` | `docs: accept p17 s1 tracking error plan` | Records accepted P17-S1 code-generation-ready plan and plan review judgment. |
| `d069862` | `fix: harden tracking error ambiguity notes` | Implements P17-S1 extractor hardening, focused tests, tests README sync, code review artifacts, and controller judgment. |
| `40e8175` | `docs: record p17 s1 implementation commit` | Backfills implementation commit hash in control truth. |
| `2327309` | `docs: accept p17 s1 aggregate review` | Records aggregate deepreview artifacts and moves control state to this reconciliation gate. |

## Included File Set

`origin/main..HEAD` contains 26 tracked files:

- `README.md`
- `docs/design-control-alignment-guide.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `fund_agent/fund/extractors/performance.py`
- `tests/README.md`
- `tests/fund/extractors/test_performance.py`
- `docs/reviews/design-alignment-review-20260522.md`
- `docs/reviews/design-alignment-review-controller-judgment-20260522.md`
- `docs/reviews/design-alignment-review-glm-20260522.md`
- `docs/reviews/design-alignment-review-mimo-20260522.md`
- `docs/reviews/post-p16-follow-up-planning-20260522.md`
- `docs/reviews/post-p16-follow-up-plan-review-mimo-20260522.md`
- `docs/reviews/post-p16-follow-up-plan-review-glm-20260522.md`
- `docs/reviews/post-p16-follow-up-plan-review-controller-judgment-20260522.md`
- `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md`
- `docs/reviews/p17-s1-plan-review-mimo-20260522.md`
- `docs/reviews/p17-s1-plan-review-glm-20260522.md`
- `docs/reviews/p17-s1-plan-review-controller-judgment-20260522.md`
- `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-implementation-20260522.md`
- `docs/reviews/p17-s1-code-review-mimo-20260522.md`
- `docs/reviews/p17-s1-code-review-glm-20260522.md`
- `docs/reviews/p17-s1-code-review-controller-judgment-20260522.md`
- `docs/reviews/p17-s1-aggregate-deepreview-mimo-20260522.md`
- `docs/reviews/p17-s1-aggregate-deepreview-glm-20260522.md`
- `docs/reviews/p17-s1-aggregate-deepreview-controller-judgment-20260522.md`

## Explicitly Excluded Local Files

These local untracked drafts are not part of the PR inclusion set and must remain excluded unless a later scope explicitly asks for them:

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`

## Boundary Check

- No production golden rows or selected CSV/RR-13 data were changed.
- No Service/UI/Runtime/Engine/source orchestration/document adapter/PDF/cache helper files were changed.
- No Dayu runtime, LLM audit, Evidence Confirm, calculated tracking error, external index series, methodology extraction, or constituents extraction was introduced.
- Annual-report access remains via `ParsedAnnualReport` inputs to Fund Capability extractor; no direct PDF/cache/source access was introduced by P17-S1.
- `docs/design.md` v2.1 remains the design truth and `docs/implementation-control.md` remains the control truth.

## Validation

Latest recorded P17-S1 validation:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 22 passed

.venv/bin/python -m pytest tests/fund/extractors -q
# 62 passed

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed

.venv/bin/python -m ruff check fund_agent tests
# All checks passed!

git diff --check origin/main..HEAD
# passed with no output
```

## Residuals With Owners

| Residual | Owner | Handling |
|---|---|---|
| P17-S1 note precision/test residuals | Future note precision / classifier alignment / test pass | Standard-deviation-only diagnostic, `年化` mixed-row note precision, benchmark-only table-context alignment, and table-level mixed/`§2` mixed tests are accepted as future non-blocking refinements. |
| Production `tracking_error` golden rows for `001548` and P16 enhanced-index candidates | Future evidence-backed golden gate | Still blocked without reviewed direct observed disclosure evidence. |
| RR-13 duplicate `016492` | User / App source | Preserve as human-owned; do not edit source CSV automatically. |
| Excluded local drafts | Controller / user | Keep out of PR unless explicitly scoped. |

## Next Step

If the user authorizes the draft PR gate, create a branch from the current local `main`, push it, open a draft PR, then run PR-level review before any merge/ready-for-review action.
