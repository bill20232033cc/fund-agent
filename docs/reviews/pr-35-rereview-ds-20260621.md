# PR 35 Targeted Re-review - AgentDS

## Scope

- Role: AgentDS targeted PR re-review worker only, not controller.
- Gate: FundDisclosureDocument source-truth post-merge control sync PR Review Re-review Gate corrective dispatch.
- PR: #35 `https://github.com/bill20232033cc/fund-agent/pull/35`
- Reviewed remote head oid: `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
- Reviewed finding: 001 from `docs/reviews/pr-35-review-20260620-230555.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md`
- Output file: `docs/reviews/pr-35-rereview-ds-20260621.md`

## PR 35 Metadata (current)

| Field | Value |
|---|---|
| State | `OPEN` |
| Draft | `true` |
| Base | `main` |
| Head branch | `funddisclosure-source-truth-post-merge-control-sync` |
| Head oid | `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` |
| Merge state | `CLEAN` |
| CI `test` | `pass` (55s) |

## Finding 001 Fix Verification

### Finding Recap

Finding 001 (`docs/reviews/pr-35-review-20260620-230555.md`) reported that PR #35 control records used placeholder `the push-gate commit` instead of the exact pushed head oid in push judgment, startup packet, and implementation-control ledger.

### Fix Claimed

`docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-fix-evidence-20260620.md` claims:

1. Push judgment `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md` was updated so accepted push evidence records exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.
2. `docs/implementation-control.md` ledger item 188 was updated to use exact head.
3. Current control surfaces were updated to route to re-review.

### Verification Evidence

**Push judgment (line 31)** — exact head present:
```
Remote branch ... was created at pushed head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`.
```

**Implementation-control ledger item 188 (line 300)** — exact head present:
```
branch `funddisclosure-source-truth-post-merge-control-sync` was pushed to origin at exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
```

**Startup packet** — exact head present at lines 24, 63, 228. Example (line 24):
```
reviewed head oid `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`
```

**Placeholder `the push-gate commit` remaining occurrences** — only in historical review finding text:
- `docs/reviews/pr-35-review-20260620-230555.md` lines 25, 27, 28, 30: original review finding description (historical evidence).
- `docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-pr-review-controller-judgment-20260620.md` line 35: controller rationale quoting original finding (historical evidence).

These are permissible as historical review finding text cited as history.

**Cross-check**: `rg -n "the push-gate commit" docs/current-startup-packet.md docs/implementation-control.md docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md` returns zero matches in active control/push records.

**git diff --check**: passed with no output on all touched files.

## Findings

未发现实质性问题。

Finding 001 is confirmed fixed. The placeholder `the push-gate commit` has been replaced with exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` in:

- Push judgment (`docs/reviews/funddisclosuredocument-source-truth-post-merge-control-sync-push-controller-judgment-20260620.md` line 31)
- Implementation-control ledger item 188 (`docs/implementation-control.md` line 300)
- Startup packet current control surfaces (`docs/current-startup-packet.md` lines 24, 63, 228)

The exact head `c2799e9dccf51dbf534bc7e8ddce3982d71fd404` appears consistently across all active control records. Remaining `the push-gate commit` text exists only in the original review artifact and controller judgment rationale, where it is cited as historical context — this is permitted.

PR #35 metadata confirms: head oid matches `c2799e9dccf51dbf534bc7e8ddce3982d71fd404`, draft/open, merge state `CLEAN`, CI `test` pass.

## Open Questions

无。

## Residual Risk

- This re-review verified only the fix for finding 001. It did not re-review PR #35 diff, implementation PRs #31-#34, source code, tests, field correctness, `EvidenceSourceKind`/`EvidenceAnchor` contracts, or readiness/release.
- The local commit `715bf80 gateflow: record fdd source truth post-merge sync pr` is not part of the reviewed remote head and does not affect the fix verification.

## Verdict

PR_REREVIEW_PASS
