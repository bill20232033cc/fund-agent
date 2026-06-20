# FundDisclosureDocument Source-truth Post-merge Control Sync PR Review Fix Evidence - 2026-06-20

## Scope

This artifact records the fix for accepted PR review finding 001 from `docs/reviews/pr-35-review-20260620-230555.md`.

The fix is control-plane only. It does not change source code, tests, parser behavior, source policy, public evidence contracts, field correctness status, readiness, release state, mark-ready state, merge state, or GitHub PR state.

## Accepted Finding

### 001-PR head records the pushed branch with a placeholder instead of the exact pushed commit

- Status: `已修复`.
- Review artifact: `docs/reviews/pr-35-review-20260620-230555.md`.
- Controller judgment: `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-controller-judgment-20260620.md`.
- Exact pushed / reviewed head evidence: `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.

## Fix Applied

- Updated `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md` so accepted push evidence records the exact remote branch head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` instead of placeholder `the push-gate commit`.
- Updated `docs/implementation-control.md` ledger item 188 so the pushed branch record uses the exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.
- Updated current control surfaces to record this fix gate and route to PR review re-review.

## Validation

Required local validation:

```text
rg -n "the push-gate commit|c2799e9dccf51dbf534bc7e8ddce3982d71fd404" docs/current-startup-packet.md docs/implementation-control.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md docs/reviews/pr-35-review-20260620-230555.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-controller-judgment-20260620.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md
git diff --check -- docs/current-startup-packet.md docs/implementation-control.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md
```

## Boundaries Preserved

- No PR comment, approval, request-changes, mark-ready, merge, force-push/reset, parser replacement, real-report correctness, full field correctness, `EvidenceSourceKind` / `EvidenceAnchor` expansion, upper-layer candidate consumption, readiness or release transition was performed.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command was executed.

## Next Entry

Next entry point is `FundDisclosureDocument source-truth post-merge control sync PR Review Re-review Gate`.

Release/readiness remains `NOT_READY`.
