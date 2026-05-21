# P11-S2 Historical Summary Dedupe Plan（2026-05-21）

## Objective

Create a documentation-only implementation plan for cleaning stale or duplicate historical summary rows inside `docs/implementation-control.md`.

The future implementation must improve resume clarity without changing product behavior, architecture truth, source/test/config/runtime files, `docs/design.md`, `docs/repo-audit-20260521.md`, or `docs/implementation-control.md` outside the planned documentation cleanup. `Startup Packet` and `Active Gate Ledger` remain the current truth for active state; old archive prose is historical evidence, not the source of current gate state.

The key distinction for implementation is:

- Summarizing stale archive prose is allowed when it removes duplicated or obsolete status wording and points to preserved evidence.
- Deleting evidence is not allowed. Artifact paths, commits, PR references, validation results, residual IDs, owners, reviewer limitations, and historical gate outcomes must remain recoverable in the control record.

## Evidence Reviewed

- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Latest follow-up planning artifact: `docs/reviews/post-p11-follow-up-planning-20260521.md`
- Accepted baseline before this gate: `00411dc`

Relevant design constraints:

- `docs/design.md:22` states the deterministic MVP path does not depend on LLM writing or external Dayu Host/Engine.
- `docs/design.md:45` to `docs/design.md:56` define the current UI -> Service -> Fund Capability architecture and explicitly exclude an external Dayu runtime.
- `docs/design.md:68` to `docs/design.md:70` keep `FundDocumentRepository` as the production document entry point and preserve explicit source fallback taxonomy.

## Exact Target Rows And Sections

### Keep As Current Truth

- `docs/implementation-control.md:11` to `docs/implementation-control.md:30` (`Startup Packet`) must remain the current resume entry point.
- `docs/implementation-control.md:32` to `docs/implementation-control.md:39` (`Active Gate Ledger`) must remain the current accepted-gate ledger.
- `docs/implementation-control.md:73` to `docs/implementation-control.md:80` (`Active Residuals`) must continue to show RR-13, excluded `docs/repo-audit-20260521.md`, historical duplicate summary rows, and future product selection ownership until P11-S2 implementation is accepted.
- `docs/implementation-control.md:82` to `docs/implementation-control.md:96` (`Evidence Preservation Rules` and `Archive / Summarize Strategy`) must remain the governing rule for the cleanup.

Expected post-implementation state for the Active Residuals row:

- Before P11-S2 implementation is accepted, `Historical duplicate summary rows` may remain with owner `P11-S2 plan/review`.
- After P11-S2 implementation is accepted, that row must either be removed from active residuals or rewritten as closed by P11-S2, with any remaining ambiguity assigned to a non-active historical note. It must not remain an open residual that implies the cleanup is still pending.

### Clean Historical Snapshot Before P11-S1

- `docs/implementation-control.md:160` to `docs/implementation-control.md:172`
  - Current issue: this block is correctly labeled as a historical snapshot, but still contains stale active-state wording such as `P11-S1 plan accepted`, `P11-S1 implementation`, and `repo hygiene/control doc hygiene` as current residuals.
  - Proposed edit: keep the block as a compact "pre-P11-S1 historical snapshot"; make every status explicitly historical as of 2026-05-21 before P11-S1 implementation.
  - Required preservation: keep the design/control context and the fact that detailed gate, artifact, review, commit, validation, and residual risk records remain below.

### Clean Duplicate Technical Debt / Follow-up Summary Rows

- `docs/implementation-control.md:205` to `docs/implementation-control.md:216`
  - Current issue: `Repo hygiene` appears twice. The first row says P10 is closed by PR #6, while the second row still describes P10-S1 as the next future phase.
  - Current issue: `Control doc hygiene` appears twice. The first row still says P11-S1 plan/review is accepted and next is implementation, while the second row gives a generic future documentation slice.
  - Proposed edit: collapse the duplicate rows into one row per category:
    - `Repo hygiene`: record that P10 was closed by PR #6 / merge commit already preserved elsewhere, with any remaining repo-audit input explicitly excluded.
    - `Control doc hygiene`: record that P11-S1 recovery is accepted, P11-S2 is the current historical summary dedupe plan/review, and implementation remains documentation-only.
  - Required preservation: keep closed P9/P10/P11 facts, RR-13 human ownership, repo-audit exclusion, and P9 aggregate reviewer limitation.

### Clean Stale Current Gate And Baseline Bullets

- `docs/implementation-control.md:227` to `docs/implementation-control.md:233`
  - Current issue: the section heading and introductory bullets still read like current gate truth for `P11-S1 plan accepted` and `P11-S1 implementation`, even though the real current state is P11-S2 plan/review in the Startup Packet.
  - Proposed edit: rename or annotate only the section heading and stale introductory bullets as a historical baseline before P11-S1 implementation.
  - Required stale-bullet handling: the three stale current-gate bullets at `docs/implementation-control.md:229` to `docs/implementation-control.md:231` (`当前分支`, `当前 gate`, `下一 gate`) must be removed or converted to explicit historical wording. In particular, unqualified `当前 gate：P11-S1 plan accepted` and `下一 gate：P11-S1 implementation` wording must not remain in this area.

- `docs/implementation-control.md:234` to `docs/implementation-control.md:264`
  - These rows are the detailed chronological evidence chain for P7 through P11-S1/P10 merge context.
  - They must not be shortened, consolidated, deduplicated, or replaced by a pointer during P11-S2. Concrete artifact paths, commits, PR #6 details, validation counts, reviewer limitations, residual owner facts, and gate outcomes in this range must remain intact.
  - The only allowed edit touching this range is a narrow wording change if the controller explicitly determines one line would otherwise be misread as current state; absent that determination, leave this range unchanged.

### Do Not Rewrite Detailed Evidence Logs Unless Needed For Stale Summary Cleanup

- `docs/implementation-control.md:266` onward contains detailed historical phase evidence.
- `docs/implementation-control.md:1454` records RR-13 duplicate `016492` as human-owned.
- `docs/implementation-control.md:1621` to `docs/implementation-control.md:1632` contain the current P10/P11 status log evidence, including PR #6 merge, P11-S1 code review, GLM F2 deferral, and post-P11 planning.

These rows are evidence-bearing logs, not duplicate summary rows. They should be left intact unless the implementation needs a narrow wording fix to prevent them from being misread as current state. RR-13 duplicate `016492` must remain human-owned and must not be auto-fixed.

## Proposed Documentation-Level Edits

1. Update stale active-state wording in the pre-P11-S1 historical snapshot so it is unambiguously archived, not current truth.
2. Deduplicate `1.1.2 当前技术债与后续规划摘要` into a single row per category, preserving current closed/deferred owners:
   - Product contract: closed by P9-S1/P9-S2/P9 aggregate as applicable.
   - Repo hygiene: closed by P10 / PR #6; `docs/repo-audit-20260521.md` remains excluded.
   - Control doc hygiene: P11-S1 accepted, P11-S2 historical summary dedupe pending plan/review or implementation depending on gate timing.
   - Dependency strategy: closed by design reconciliation; Dayu remains methodology/reference only.
   - RR-13: human-owned, no automatic CSV edit.
3. Convert any remaining "next phase is P10-S1", unqualified "P11-S1 plan accepted" as current gate, or "next gate is P11-S1 implementation" wording in the old summary area into historical wording or remove it if the same evidence is preserved in nearby detailed logs.
4. Preserve all accepted evidence fields required by `docs/implementation-control.md:82` to `docs/implementation-control.md:96`.
5. Keep the Startup Packet and Active Gate Ledger as the only active resume truth; do not add a second active-state table in the archive.

## Non-goals

- No source, tests, config, runtime, schema, CLI, Service, Engine, Capability, renderer, quality gate, or product behavior changes.
- No edits to `docs/design.md`, `docs/repo-audit-20260521.md`, or any README.
- No publishing, moving, or rewriting `docs/repo-audit-20260521.md`.
- No automatic fix for RR-13 duplicate `016492` in CSV or documentation beyond preserving the human-owned residual.
- No commit, push, PR, or gate transition as part of the plan artifact.
- No artifact existence sweep during normal resume; reference checks are implementation acceptance validation only.

## Validation Commands

Run after the future implementation edits:

```bash
git diff --check
rg -n 'P11-S2' docs/implementation-control.md
nl -ba docs/implementation-control.md | sed -n '205,233p'
rg -n '016492|RR-13|docs/repo-audit-20260521.md|acc692c7e84c855398de86497b0d05f30b6f5ca5|5f5331b|00411dc|PASS_WITH_FINDINGS|388 passed' docs/implementation-control.md
```

The first `rg` is a positive check: `P11-S2` must still be visible in the active control state. The `sed` output is a reviewer-inspection check for the narrowed stale summary area, not a binary grep gate by itself; the reviewer must confirm lines 205-233 no longer contain unqualified current/future wording for `P10-S1`, `P11-S1 plan accepted`, or `P11-S1 implementation`.

Mandatory implementation acceptance check after reference edits:

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

## Acceptance Criteria

- Only `docs/implementation-control.md` is changed by the future implementation, and only in historical summary cleanup areas.
- `Startup Packet` and `Active Gate Ledger` remain the current truth and still identify P11-S2 correctly.
- Duplicate `Repo hygiene` and `Control doc hygiene` rows in `docs/implementation-control.md:205` to `docs/implementation-control.md:216` are collapsed or rewritten so they no longer contradict accepted P10/P11 facts.
- Old `P10-S1`, unqualified `P11-S1 plan accepted` as current gate, and `P11-S1 implementation` future-state wording is either explicitly marked historical or removed where duplicated by preserved detailed evidence.
- The three stale bullets around `docs/implementation-control.md:229` to `docs/implementation-control.md:231` are removed or converted to historical wording.
- The detailed chronological evidence chain around `docs/implementation-control.md:234` to `docs/implementation-control.md:264` is not shortened or consolidated.
- The Active Residuals row for historical duplicate summary rows is no longer left as an open pending P11-S2 residual after implementation acceptance; it is removed or closed by P11-S2.
- Artifact paths, commits, PR references, validation results, residual IDs, owners, and reviewer limitations remain recoverable.
- The mandatory Python required-reference check passes.
- RR-13 duplicate `016492` remains human-owned.
- `docs/repo-audit-20260521.md` remains excluded and unmodified.
- `git diff --check` passes.

## Risks

- Over-pruning may delete evidence that future phaseflow resume needs. Mitigation: only summarize stale archive prose and preserve all required evidence fields.
- Leaving ambiguous "current gate" wording in archive sections may keep confusing future resumes. Mitigation: label those sections as historical snapshots and keep current truth only in the Startup Packet / Active Gate Ledger.
- Deduplicating rows may accidentally obscure reviewer limitations, especially P9-S2 independent review limitations and P11 GLM F2 deferral. Mitigation: verify limitation strings remain searchable.
- RR-13 may be mistaken for documentation cleanup. Mitigation: keep explicit human owner and no-auto-fix wording.

## Stop Condition

Stop and return to controller review if the implementation requires changing source, tests, config, runtime behavior, product behavior, `docs/design.md`, `docs/repo-audit-20260521.md`, or any artifact outside `docs/implementation-control.md`.

Also stop if a required evidence field cannot be preserved from the existing control record, if P10/P11 accepted facts conflict with `Startup Packet` or `Active Gate Ledger`, if the implementation would edit `Startup Packet` or `Active Gate Ledger` outside explicit controller-authorized gate bookkeeping, or if cleaning RR-13 would require deciding which `016492` row is correct.
