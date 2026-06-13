# Provider/LLM Chapter 3 Code-bug Root-cause Evidence Review (DS)

Date: 2026-06-13

Reviewer: AgentDS (visible-panel evidence review)

Gate: `Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

Review target: `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-20260613.md`

Status: `REVIEW_COMPLETE`

Release/readiness: `NOT_READY`

## Verdict: PASS

With one non-blocking process finding (F1) and one cosmetic finding (F2). No evidence finding affects H1-H5 classification correctness or gate acceptance.

## Review Questions

### Q1: No-live Boundary

**PASS.** The evidence artifact declares a no-live boundary at Section 1 and Section 3 records only allowed commands: `git status`, `git diff`, `rg`/`sed` for static read-only inspection, `uv run pytest` on existing tests and `uv run ruff check`. No source, test, fixture, assertion, runtime behavior, design truth, control doc or README was modified. No `fund-analysis analyze/checklist/analyze-annual-period`, live provider/LLM/network/PDF/FDR/source, readiness/release/PR, cleanup, stage, commit, push, merge or archive command was run.

The one exception, the memory `rg` command over `.codex/memories/MEMORY.md`, is self-identified as `DEVIATION_NOT_EVIDENCE` and recorded as process residual (see Q3). It is not a source/test/runtime/control/design change.

### Q2: EID Single-source Preservation

**PASS.** Section 1 and Section 10 explicitly preserve EID single-source/no-fallback: `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`. Eastmoney, fund-company/CDN, CNINFO and annual-report fallback are correctly declared as not current execution paths, not current source truth and not authorized current sources. The artifact does not modify source acquisition policy and does not reintroduce fallback. Accepted live/provider evidence is not described as fallback-enabled.

### Q3: Unauthorized Memory Command Classification

**PASS.** The `rg` command over `/Users/maomao/.codex/memories/MEMORY.md` is:
- Labeled `DEVIATION_NOT_EVIDENCE` in the Section 3 command table.
- Addressed in a dedicated Section 4 with explicit statement: "No H1-H5 classification relies on memory output."
- Routed as a process residual requiring reviewer/controller disposition.

The evidence artifact correctly neither hides the deviation nor relies on its output for any root-cause conclusion. This is the expected handling under the accepted plan's allowed-command boundary.

### Q4: H1-H5 Disposition Consistency With Accepted Plan

**PASS.** All five hypotheses are dispositioned with evidence from existing tests and static read-only inspection, consistent with the accepted plan's evidence fields and accept/reject signals:

| Hypothesis | Artifact classification | Plan-expected classification | Match |
|---|---|---|---|
| H1 | `rejected` for covered no-live typed path | Expected if fake writer receives Chapter 3 request and no untested ValueError path found | Consistent |
| H2 | `rejected` for currently inspected rows | Expected if typed requirements/availability coherent | Consistent |
| H3 | `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` | `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` | Exact match |
| H4 | `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` | `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` | Exact match |
| H5 | `rejected` | Expected if artifact writer faithful to serializer | Consistent |

Each classification is supported by specific source function references, existing test names and static code path analysis. The required questions in Section 8 are all answered with evidence-anchored reasoning. Missing reproducers/assertions/fixtures are correctly routed as residuals in Section 9.

### Q5: Targeted Validation Sufficiency

**PASS.** The allowed pytest command passed (`125 passed in 1.07s`) and ruff passed (`All checks passed!`). These results confirm that current existing tests and static analysis are green for the inspected files. The evidence artifact correctly notes that existing test coverage is partial: it proves Chapter 3 can reach fake writer in the typed no-live fixture but does not provide an exact reproducer for the live `004393 / 2025` pre-provider `ValueError` shape. This gap is properly recorded as a residual rather than treated as evidence of bug absence. For a no-live evidence gate limited to existing tests and static inspection, this is sufficient.

### Q6: NOT_READY and Forbidden Claims Preservation

**PASS.** The artifact preserves `NOT_READY` at:
- Status line: `EVIDENCE_READY_FOR_REVIEW_NOT_READY`
- Release/readiness field: `NOT_READY`
- Section 10: "Release/readiness remains `NOT_READY`"
- Section 9 residuals explicitly forbid readiness/release claims

The artifact explicitly rejects provider readiness, LLM content quality, release readiness, PR readiness, repeat-live, fallback and source-policy claims in Section 10. The recommended next gate is review of this evidence artifact followed by a future no-live test-reproducer/diagnostic implementation planning gate, not implementation or live execution.

## Findings

| # | Severity | Location | Finding | Required fix |
|---|---|---|---|---|
| F1 | `PROCESS_NONBLOCKING` | Section 3, command row 1; Section 4 | The `rg` over `.codex/memories/MEMORY.md` was not in the handoff-authorized command list. The artifact self-identifies and quarantines it correctly; no H1-H5 classification depends on it. | None for this gate. Reviewer/controller should confirm the residual disposition and remind evidence workers not to probe agent memory in future no-live gates. |
| F2 | `COSMETIC_NONBLOCKING` | Section 6 subsections | Subsections under `## 6. Direct Static/Test Evidence` are numbered `5.1`–`5.6` instead of `6.1`–`6.6`. No semantic impact. | None required. May be corrected if the artifact is revised for other reasons. |

## Residual Table

| Residual | Source | Disposition |
|---|---|---|
| Unauthorized memory `rg` command | F1 / evidence artifact Section 4 | Process residual; correctly self-identified as `DEVIATION_NOT_EVIDENCE`. Reviewer/controller disposition confirms no impact on H1-H5. |
| Missing exact Chapter 3 fake-writer reproducer for live failure shape | Evidence artifact Section 9 | Correctly routed to future no-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`. |
| Missing bridge projection assertion for pre-provider `ValueError` shape | Evidence artifact Section 9 | Correctly routed to future no-live diagnostic/test implementation planning gate. |
| Missing pre-provider `max_output_chars` assertion | Evidence artifact Section 9 | Correctly routed to future no-live diagnostic/test implementation planning gate. |
| Missing artifact code-bug/pre-provider fixture | Evidence artifact Section 9 | Correctly routed to future no-live artifact diagnostic/test implementation planning gate. |
| Section numbering inconsistency (5.x under Section 6) | F2 | Cosmetic; no action required. |

## Reviewer Summary

The evidence artifact respects the no-live boundary, preserves EID single-source/no-fallback, correctly quarantines the unauthorized memory command, produces plan-consistent H1-H5 classifications anchored in existing tests and static inspection, records sufficient targeted validation results, and preserves `NOT_READY` while rejecting all forbidden readiness/provider/fallback/repeat-live claims. All four evidence-gap residuals are correctly routed to future no-live planning gates. Verdict: PASS.
