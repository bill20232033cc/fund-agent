# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Gate`.

Role: AgentCodex implementation worker, not controller.

This artifact records the no-live implementation evidence for the accepted narrow Chapter 2 L1 repair prompt fix. It does not claim release readiness, update control/design truth, run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands, stage, commit, push or open a PR.

Release/readiness remains `NOT_READY`. EID annual-report source policy remains single-source/no-fallback.

## Files Changed By This Worker

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-evidence-20260614.md`

No changes were made to:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/agent/repair.py`
- `tests/agent/test_repair_policy.py`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- root `README.md`
- provider config/defaults, source policy, fallback, Docling, annual-report repository code, reports runtime artifacts, readiness/release/PR artifacts

## Implementation Summary

- Added `_has_l1_numerical_closure_repair_issue(repair_context)` in `fund_agent/fund/chapter_writer.py`.
  - Detection is deterministic and narrow: it returns true only when `previous_issue_ids` contains an id starting with `programmatic:L1`.
  - It does not inspect provider text, sanitized messages or indirect diagnostics.
- Added `_ch2_l1_repair_guidance_prompt(chapter, repair_context)` in `fund_agent/fund/chapter_writer.py`.
  - It renders only for `chapter_id == 2` and prior `programmatic:L1`.
  - It instructs repair attempts to treat whole-chapter regenerate as a localized L1 anchor-placement correction:
    - check `### 结论要点`, `### 详细情况` and `### 证据与出处`;
    - for concrete R/A/B/C/A-C formula, A-C, Alpha/Beta/Cost or percentage closure assertions, place an existing allowed anchor in the same sentence or within two surrounding lines;
    - if no same-source anchor is known, delete the concrete numerical closure assertion and write a data-gap/minimum-verification sentence without concrete percentages;
    - do not put anchors only in detached source lists;
    - do not invent anchors or values.
- Appended the checklist beside the existing generic repair context prompt.
  - `ChapterRepairContext` fields are unchanged.
  - Generic `_repair_context_prompt()` remains generic.
  - L1 audit semantics, repair action, stop reason and repair budget defaults are unchanged.
  - No typed patch API was introduced.

## Red-test-first Evidence

New red tests were written before implementation:

```text
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1_repair" -q
```

Initial result:

```text
FAILED test_ch2_l1_repair_context_renders_local_anchor_placement_checklist
AssertionError: '第2章 L1 数字闭环 repair checklist' not in prompt.user_prompt
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context" -q
```

Initial result:

```text
FAILED test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair
AssertionError: '第2章 L1 数字闭环 repair checklist' not in writer.requests[1].user_prompt
```

After implementation, the same tests passed:

```text
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1_repair" -q
..                                                                       [100%]
2 passed, 44 deselected

uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context" -q
.                                                                        [100%]
1 passed, 79 deselected
```

## Validation Evidence

Allowed no-live/local commands run:

```text
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1_repair or l1_numerical_closure or repair_context" -q
......                                                                   [100%]
6 passed, 40 deselected
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted" -q
....                                                                     [100%]
4 passed, 76 deselected
```

```text
uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section" -q
......                                                                   [100%]
6 passed, 43 deselected
```

```text
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py
All checks passed!
```

```text
git diff --check
```

Result: passed with no output.

```text
git status --short
```

Relevant touched files:

```text
 M fund_agent/fund/chapter_writer.py
 M tests/fund/test_chapter_writer.py
 M tests/services/test_chapter_orchestrator.py
```

Pre-existing unrelated workspace residue observed and not modified by this worker includes `AGENTS.md`, `README.md`, `docs/design.md`, multiple untracked `docs/reviews/` artifacts, `reports/`, `reviews/`, scripts and local data directories.

```text
git status --branch --short
## feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 89]
```

Relevant touched files were the same three implementation/test paths above. The branch already contained unrelated modified/untracked residue.

## Service / Agent Alignment Branch

The implementation did not change Service or Agent correction text:

- Existing Service L1 repair-context test already proves `programmatic:L1` issue ids and L1-specific required corrections are propagated.
- The new Service assertion proves the actual second writer request receives the Fund writer checklist in `user_prompt`.
- Because alignment is achieved at the Fund writer prompt boundary, no red no-live assertion required changing `fund_agent/services/chapter_orchestrator.py`.
- Because Service correction text was not changed, the Agent duplicate path in `fund_agent/agent/repair.py` did not need alignment.

Accordingly, `tests/agent/test_repair_policy.py` was not changed and the optional agent repair validation command was omitted.

## Residuals

- Live provider adherence to the new checklist remains unproven and requires a later explicitly authorized bounded live evidence gate.
- H4 safe metadata and H5 diagnostic serialization remain future diagnostic/projection scope.
- Chapter repair budget calibration remains a separate future gate.
- Release/readiness remains `NOT_READY`.

## Verdict

VERDICT: IMPLEMENTED_NO_LIVE_FIX_EVIDENCE_READY_FOR_REVIEW_NOT_READY
