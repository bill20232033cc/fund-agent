# PR 35 Targeted Re-review - AgentMiMo

## Scope

- Mode: targeted PR re-review
- Repository: `bill20232033cc/fund-agent`
- Branch or PR: PR #35 `FundDisclosureDocument source-truth post-merge control sync`
- URL: `https://github.com/bill20232033cc/fund-agent/pull/35`
- Head: `funddisclosure-source-truth-post-merge-control-sync` at `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
- Base: `main`
- Reviewed head oid: `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
- Included scope: accepted finding 001 from `docs/reviews/pr-35-review-20260620-230555.md`, local fix evidence `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md`, and the changed control-plane records that close the finding.
- Excluded scope: PR #31-#34 source changes, runtime behavior, source code, tests, parser behavior, provider/live/PDF/FDR/Docling conversion/pdfplumber export/manual reference review, field correctness, readiness and release behavior.
- Parallel review coverage: 无。
- Output file: `docs/reviews/pr-35-rereview-mimo-20260621.md`

## PR Metadata Verification

- State: `OPEN`
- Draft: `true`
- Base: `main`
- Head branch: `funddisclosure-source-truth-post-merge-control-sync`
- Head oid: `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
- Merge state: `CLEAN`
- CI `test`: `SUCCESS` (completed 2026-06-20T14:59:14Z)

## Findings

未发现实质性问题。

## Finding Status

### 001-已修复-中-PR head records the pushed branch with a placeholder instead of the exact pushed commit

- Original review artifact: `docs/reviews/pr-35-review-20260620-230555.md`.
- Fix evidence: `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md`.
- Final status: `已修复`.
- Direct evidence of fix:
  - `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md` line 31 now records the remote branch at pushed head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` (not placeholder).
  - `docs/implementation-control.md` line 300 (ledger item 188) now records the pushed branch exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` (not placeholder).
  - `docs/current-startup-packet.md` lines 24, 63, 228 all record exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.
  - `docs/implementation-control.md` lines 10, 51, 105, 300-304, 565 all record exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.
- Placeholder verification: `rg -n "the push-gate commit" docs/` confirms the placeholder only appears in historical review finding text (original review artifact, controller judgment rationale, fix evidence description) — not in active push evidence or control records.
- `git diff --check` on touched control/review docs: clean, exit 0.
- Re-review judgment: the accepted finding is closed. The fix only changes control-plane audit wording and does not introduce a new blocker.

## Required Checks Summary

| Check | Result |
|---|---|
| PR metadata (state, draft, base, head oid, merge state, CI) | PASS — matches reviewed head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` |
| Placeholder `the push-gate commit` removed from active push/control evidence | PASS — only in historical review finding text |
| Exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` in fixed push/control evidence | PASS — present in push judgment, implementation-control ledger 188, startup packet |
| `git diff --check` on touched docs | PASS — clean |

## Open Questions

无。

## Residual Risk

- PR #35 remote head does not yet include local create-PR, PR-review, fix, re-review and this targeted re-review bookkeeping commits. If this re-review is accepted, the next gate should create the accepted PR review commit locally before a follow-up push gate.
- This targeted re-review did not re-review merged implementation PRs #31-#34, source code, parser behavior, field correctness, real-report correctness, `EvidenceSourceKind` / `EvidenceAnchor` contracts, upper-layer consumption, readiness or release.

## Verdict

PR_REREVIEW_PASS
