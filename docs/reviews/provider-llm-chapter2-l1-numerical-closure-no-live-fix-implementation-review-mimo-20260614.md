# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Review (MiMo)

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Gate`.

Role: AgentMiMo implementation reviewer, not controller, not fix worker.

This artifact reviews the no-live fix implementation against the accepted plan and amendments. It does not modify files, stage/commit/push/open PR, or run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.

Release/readiness remains `NOT_READY`. EID annual-report source policy remains single-source/no-fallback.

## Evidence Reviewed

- Implementation evidence: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-implementation-evidence-20260614.md`
- Accepted plan controller judgment: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-controller-judgment-20260614.md`
- Accepted root-cause controller judgment: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-controller-judgment-20260614.md`
- Current diff: `fund_agent/fund/chapter_writer.py`, `tests/fund/test_chapter_writer.py`, `tests/services/test_chapter_orchestrator.py`
- Control truth: `docs/current-startup-packet.md`, `docs/implementation-control.md`

## Review Focus Verification

### 1. Findings (severity ordered)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| F1 | INFO | `_has_l1_numerical_closure_repair_issue` uses `startswith("programmatic:L1")` — deterministic prefix detection only, no sanitized-message fallback. Matches plan amendment requirement. | ACCEPT |
| F2 | INFO | `repair_context` field assembly at lines 737-744 uses `"\n".join()` with `if fragment` filter — correctly handles empty strings from both `_repair_context_prompt()` and `_ch2_l1_repair_guidance_prompt()`. | ACCEPT |
| F3 | INFO | Checklist text is well-structured 5-point guidance: check sections, place anchor near assertion or delete assertion, don't put anchors only in source lists, don't repeat unanchored percentages, don't invent anchors/values. Aligns with H3 root cause. | ACCEPT |
| F4 | INFO | `ChapterRepairContext` dataclass and `_repair_context_prompt()` are unchanged. New checklist is appended as a separate prompt fragment. Clean additive change. | ACCEPT |
| F5 | LOW | Service/Agent alignment not required — checklist injected at Fund writer prompt boundary. Existing Service L1 repair-context test already proves `programmatic:L1` propagation. New orchestrator assertion confirms checklist reaches `writer.requests[1].user_prompt`. | ACCEPT |
| F6 | INFO | `git diff --check` passed — no whitespace issues. | ACCEPT |

No blocking findings. No NEEDS_FIX findings.

### 2. Does implementation match accepted plan and amendments?

**Yes.** The implementation matches the accepted plan at `457253d` with all amendments applied:

- Detection helper uses deterministic `previous_issue_ids` prefix only (amendment: removed optional sanitized-message path).
- Checklist rendered only for `chapter_id == 2` AND `programmatic:L1` prior issue.
- No Service/Agent correction-text changes needed (amendment: red-test-first proof confirmed alignment at Fund writer boundary).
- Write set stays within `chapter_writer.py` + test files. No forbidden files touched.

### 3. Does it preserve L1 blocker semantics and avoid weakening audit?

**Yes.** The implementation is purely additive prompt guidance:

- `_audit_numerical_closure()` semantics unchanged.
- L1 blocking behavior unchanged — the orchestrator test `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` still asserts `stop_reason == "repair_budget_exhausted"` and `failure_subcategory == "l1_numerical_closure"`.
- Checklist strengthens repair guidance (anchor placement, delete-if-no-anchor) without weakening the audit gate itself.

### 4. Does it preserve repair budget/action/stop reason and avoid typed patch API?

**Yes.**

- `max_repair_attempts=1` default unchanged.
- Repair action remains whole-chapter regenerate (no typed patch API introduced).
- `stop_reason`, `failure_category`, `failure_subcategory` semantics unchanged.
- `ChapterRepairContext` fields unchanged.

### 5. Is helper detection narrow and deterministic via `programmatic:L1` issue id only?

**Yes.** `_has_l1_numerical_closure_repair_issue()` at line 1268-1283:

- Returns `False` if `repair_context is None`.
- Uses `any(issue_id.startswith("programmatic:L1") for issue_id in repair_context.previous_issue_ids)`.
- No fallback to sanitized messages, provider text, or indirect diagnostics.

### 6. Is checklist rendered only for Chapter 2 L1 repair context and absent elsewhere?

**Yes.** `_ch2_l1_repair_guidance_prompt()` at line 1286-1316:

- Guard: `chapter.chapter_id != 2 or not _has_l1_numerical_closure_repair_issue(repair_context)` → returns `""`.
- Positive test: `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist` — ch2 + L1 context → checklist present.
- Negative tests: `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context` covers:
  - Initial attempt (no repair context) → absent.
  - Ch1 with L1 repair context → absent.
  - Ch2 with non-L1 repair context (`programmatic:C2:item`) → absent.

### 7. Are tests sufficient and no-live? Any selector/test fragility?

**Yes, sufficient and no-live.**

- 2 new writer tests + 1 orchestrator assertion addition.
- All tests use local fixtures, fake clients, no network/provider/source/PDF commands.
- Test selectors: `ch2_l1_repair` (writer), `l1_repair_context` (orchestrator) — both are specific and non-fragile.
- Validation suite: 6 passed (writer), 4 passed (orchestrator), 6 passed (auditor), ruff passed, `git diff --check` passed.
- No selector collision risk observed.

### 8. Did worker avoid forbidden files, source/fallback/provider/readiness/release/Pull Request scope?

**Yes.** Implementation evidence confirms:

- Changed: `fund_agent/fund/chapter_writer.py`, `tests/fund/test_chapter_writer.py`, `tests/services/test_chapter_orchestrator.py` + evidence artifact only.
- Not changed: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, root `README.md`, provider config/defaults, source policy, fallback, Docling, annual-report repository code, reports, readiness/release/PR artifacts.
- No live/provider/network/source/PDF/readiness/release/PR commands run.

### 9. Are docs/test README triggers correctly handled?

**Yes.** The implementation modifies `fund_agent/fund/chapter_writer.py` (Fund package) and `tests/` files. Per AGENTS.md trigger rules:

- `fund_agent/fund/` change → should update `fund_agent/fund/README.md`. The checklist is an internal prompt-assembly detail, not a public contract change. No README update needed.
- `tests/` change → should update `tests/README.md`. Test conventions unchanged. No README update needed.

No trigger-driven README update is required for this narrow prompt-assembly fix.

## Adversarial Failure Pass

| Scenario | Assessment |
|----------|------------|
| Provider ignores checklist and repeats unanchored assertion | L1 audit still catches it → fail-closed preserved. This is the accepted plan residual (DS F3). |
| Checklist text causes provider confusion / output degradation | Unproven; deferred to later bounded live evidence gate. |
| `startswith("programmatic:L1")` matches unintended issue ids | Only `programmatic:L1:*` ids would match; current codebase only emits `programmatic:L1:line:*` variants. Narrow enough. |
| Checklist leaks to non-ch2 or non-L1 contexts | Negative tests prove isolation. Dual guard (`chapter_id != 2` AND `not _has_l1_numerical_closure_repair_issue`) is correct. |
| Empty `previous_issue_ids` tuple | `any()` on empty iterable returns `False`. Correct. |

## Residuals

| Residual | Owner | Current blocker? |
|----------|-------|-----------------|
| Live provider adherence to the new checklist remains unproven. | Provider/LLM evidence owner | Yes, for readiness |
| H4 safe metadata / H5 diagnostic serialization remain future scope. | Service/Agent diagnostics owner | No |
| Repair budget calibration remains separate future gate. | Service/Agent chapter orchestration owner | No |

## Final Verdict

VERDICT: PASS_WITH_FINDINGS

Implementation correctly matches the accepted plan with all amendments applied. L1 blocker semantics preserved, repair budget/action/stop reason unchanged, helper detection is narrow and deterministic, checklist scope is correctly bounded to Chapter 2 L1 repair context, tests are sufficient and no-live, no forbidden files or scope violations. Six INFO/LOW findings recorded — none blocking.
