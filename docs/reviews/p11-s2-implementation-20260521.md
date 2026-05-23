# P11-S2 Implementation（2026-05-21）

## Scope

Implemented the accepted documentation-only cleanup from `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md` and `docs/reviews/p11-s2-plan-review-controller-judgment-20260521.md`.

Allowed files changed:

- `docs/implementation-control.md`
- `docs/reviews/p11-s2-implementation-20260521.md`

No source, tests, config, runtime, product behavior, `docs/design.md`, `docs/repo-audit-20260521.md`, README, commit, push, PR, or gate transition changes were made.

## Changed Sections

### Active Residuals

- Removed the open `Historical duplicate summary rows` residual from `Active Residuals`.
- Kept RR-13 duplicate `016492` as human-owned.
- Kept `docs/repo-audit-20260521.md` excluded.

### Historical Snapshot Before P11-S1

- Renamed the snapshot to `Historical Snapshot Before P11-S1 Implementation`.
- Added an explicit note that the block is historical and not current gate truth.
- Converted stale `当前` labels to historical wording: `当时分支`, `当时 gate`, `当时下一 entry point`, and `当时残余风险`.
- Preserved the design/control context and the note that detailed gate, artifact, review, commit, validation, and residual records remain below.

### Section 1.1.2 Technical Debt / Follow-up Summary

- Deduplicated duplicate `Repo hygiene` and `Control doc hygiene` rows into one current row per category.
- Recorded P10 repo hygiene as closed by PR #6 while preserving `docs/repo-audit-20260521.md` as excluded.
- Recorded P11-S2 historical summary dedupe as closed by implementation while preserving the evidence-chain constraint.
- Added an explicit RR-13 row stating the `016492` source-data identity conflict remains human-owned and is not auto-fixed.
- Preserved P9 aggregate reviewer limitation.

### Section 1.3 Historical Gate Intro

- Renamed the heading to mark the section as P11-S1 pre-implementation history.
- Converted only the three stale introductory bullets to historical wording.
- Did not shorten, consolidate, deduplicate, or replace the detailed chronological evidence chain around the protected range.

## Validation Results

```bash
git diff --check
```

Result: passed with no output.

```bash
rg -n 'P11-S2' docs/implementation-control.md
```

Result: passed. `P11-S2` remains visible in Startup Packet, Active Gate Ledger, Phase History Index, Archive P11 summary, the deduped Control doc hygiene row, and status log entries.

```bash
nl -ba docs/implementation-control.md | sed -n '205,233p'
```

Result: inspected. Lines 208-218 now contain one row per summary category; lines 229-233 are historical wording (`当时分支`, `当时 gate`, `当时下一 gate`) rather than unqualified current/future state.

```bash
rg -n '016492|RR-13|docs/repo-audit-20260521.md|acc692c7e84c855398de86497b0d05f30b6f5ca5|5f5331b|00411dc|PASS_WITH_FINDINGS|388 passed' docs/implementation-control.md
```

Result: passed. Required preserved references remain present, including RR-13, duplicate `016492`, `docs/repo-audit-20260521.md`, PR #6 merge commit `acc692c7e84c855398de86497b0d05f30b6f5ca5`, `5f5331b`, `PASS_WITH_FINDINGS`, and `388 passed`.

```bash
python - <<'PY'
from pathlib import Path

doc = Path("docs/implementation-control.md").read_text()
required = [
    "docs/reviews/post-p11-follow-up-planning-20260521.md",
    "docs/reviews/p11-s1-implementation-20260521.md",
    "docs/reviews/p11-s1-code-review-controller-judgment-20260521.md",
    "acc692c7e84c855398de86497b0d05f30b6f5ca5",
    "RR-13",
    "016492",
    "docs/repo-audit-20260521.md",
]
missing = [item for item in required if item not in doc]
if missing:
    raise SystemExit(f"missing required references: {missing}")
PY
```

Result: passed with no output.

## Residual Handling

- RR-13 duplicate `016492` remains assigned to User / App source and was not auto-fixed.
- `docs/repo-audit-20260521.md` remains excluded and unmodified.
- Historical duplicate summary rows are no longer listed as an open active residual after P11-S2 implementation.
- Future product feature selection remains deferred until control-doc recovery cleanup is accepted by controller review.

## Scope Compliance

The implementation changed only documentation surfaces allowed by the handoff. It did not alter product behavior, architecture truth, source code, tests, config, runtime, design truth, repo-audit input, README content, commits, pushes, PRs, or gate state.
