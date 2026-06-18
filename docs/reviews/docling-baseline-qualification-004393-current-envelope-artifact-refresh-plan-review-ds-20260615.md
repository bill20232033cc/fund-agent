# 004393 Current-envelope Candidate Artifact Refresh Plan Review - DS - 2026-06-15

Verdict: `BLOCKED`

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| DS-PLAN-F1 | Blocking | Path A initially allowed a 004393 EID HTML current-envelope output path and did not explicitly prevent wrapping the route-specific 004393 EID HTML JSON into a table-bearing current envelope. This could bypass the deferred `EID HTML Candidate Envelope Mapping Gate`. | Amend Path A so EID HTML is emitted only as blocked current-envelope with route failure and zero sections/tables/cells unless a separate accepted EID HTML Candidate Envelope Mapping Gate has accepted table-bearing mapping rules. Add this to acceptance criteria and stop conditions. |

## Non-blocking Accepted Points

- Docling/pdfplumber Path A wrapper is otherwise scoped as read-only legacy input and no invented locator facts.
- Path B local conversion requires separate authorization.
- Output paths are no-clobber.
- Field correctness/source truth/readiness/parser replacement claims are blocked.

## Controller Disposition

`DS-PLAN-F1` was accepted and fixed before targeted re-review.
