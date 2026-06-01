# MVP Independent Body Chapter Execution Plan Review

## Review Role

- Role: Gateflow plan review worker only.
- Gate: `MVP independent body chapter execution gate`.
- Artifact under review: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`

## Review Scope

Challenge plan handoff-readiness / code-generation-readiness against 7 criteria specified by controller.

## Verdict

**PASS**

## Evidence Summary

### Criterion 1: Body chapters 1-6 independent write/audit/repair from same ChapterFactProjection

**Assessment: PASS**

- Plan Slice 1 step 2 explicitly replaces the `stop_remaining` loop with a simple per-chapter loop that always calls `_run_single_chapter()` for each target body chapter.
- Current code at `chapter_orchestrator.py:601-620` confirms the exact problem: `stop_remaining=True` after first non-accepted chapter causes `_skipped_result()` for later chapters. Plan targets this precisely.
- Plan step 3 stops appending `_skipped_result()` for previous body chapter failure.
- Plan step 5 preserves `_orchestration_result()` status aggregation semantics, which already handles `accepted`/`partial`/`blocked` correctly.
- Shared `ChapterFactProjection` is resolved before the loop (`_resolve_projection()` at line 582) and remains unchanged.

### Criterion 2: Final assembly fail-closed preserved

**Assessment: PASS**

- Plan Slice 2 step 1 correctly identifies that existing `final_chapter_assembler.py` already fail-closes: `_validate_orchestration()` checks `require_orchestration_accepted` and `_validate_required_chapter()` checks `status != "accepted"`, `accepted_draft is None`, `accepted_conclusion is None`.
- Source code at `final_chapter_assembler.py:374-414` confirms: any non-accepted orchestration status or non-accepted body chapter produces blocking issues and returns `incomplete` with `report_markdown=None`.
- Plan correctly states no production-code change expected for final assembler.
- Slice 2 only adds tests to strengthen coverage of partial/blocked orchestration with real chapter rows (not synthetic skipped rows).

### Criterion 3: first_failed preserved, all chapter matrix output, no secret leakage

**Assessment: PASS**

- Service serializers `serialize_chapter_prompt_contract_diagnostics()` (line 623) and `serialize_chapter_runtime_diagnostics()` (line 653) already output `first_failed` plus per-chapter matrices. Plan preserves these.
- Plan Slice 3 adds `_chapter_matrix_summary()` helper to CLI that iterates `chapter_results` and renders safe scalar rows only.
- Plan explicitly enumerates safe fields: `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`.
- Plan explicitly prohibits: issue messages, prompts, drafts, raw responses, provider messages, model names, request bodies.
- Existing `_first_failed_chapter_summary()` (cli.py:835) already uses allowlisted scalars. New matrix helper follows same pattern.
- `_sanitize_text()` in orchestrator (line 2158) already redacts `Authorization`, `Bearer`, `sk-`, `api_key`, `prompt`. CLI never accesses these fields.

### Criterion 4: fail_fast compatibility/deprecation, no dependency_missing re-trigger path

**Assessment: PASS**

- Plan Slice 1 step 1: deprecate `fail_fast` as legacy/no-op for body chapters, or change default to `False`.
- Plan explicitly states: "Keep `_map_writer_stop_reason('chapter_requires_accepted_conclusions') -> dependency_missing` only for a true writer contract dependency failure."
- Plan step 9 adds test: `dependency_missing` used only for true writer stop reason like `chapter_requires_accepted_conclusions`, not for prior body chapter failure.
- Current `_skipped_result()` at line 2752 hardcodes `stop_reason="dependency_missing"` and `failure_category="fact_gap"` — this is the exact path the plan eliminates.
- No code path remains that can re-trigger `dependency_missing` for a body chapter solely because a prior body chapter failed.

### Criterion 5: Test coverage adequacy

**Assessment: PASS**

- Slice 1 step 7: chapter 1 timeout, chapters 2-6 still receive writer requests — covers the primary independence scenario.
- Slice 1 step 8: mixed matrix (ch1 timeout, ch2 accepted, ch3 prompt-contract, ch4 audit-parse, ch5 fact-gap, ch6 accepted) — covers diversity of failure modes.
- Slice 1 step 6: updates `test_fail_fast_true_skips_later_chapters_after_first_blocked` to assert chapter 2 executes.
- Slice 2 steps 2-4: final assembly incomplete with all chapter rows present, partial matrix diagnostic-only.
- Slice 3 steps 4-6: CLI tests for first-failed fields preserved, multi-chapter matrix in stderr, secret-safety assertions on matrix string.
- Dependency test (step 9): `dependency_missing` only for real dependency, not body failure cascade.
- Validation plan covers targeted pytest, ruff, full coverage, deterministic analyze/checklist, missing-config smoke, and secret scan.

### Criterion 6: Boundary compliance

**Assessment: PASS**

- Allowed files list is precise: `chapter_orchestrator.py`, `final_chapter_assembler.py` (conditional), `cli.py`, and their test files.
- Explicitly disallowed: `chapter_writer.py`, `chapter_auditor.py`, `config/`, `llm_provider.py`, score/quality/golden/fixture/snapshot/manifest files, `AGENTS.md`, template docs, Host/Agent/dayu packages.
- Non-Goals section (lines 20-27) explicitly prohibits: Gate 5, Host, Agent, dayu, writer/auditor audit rules, prompt parsing, repair budgets, evidence-anchor rules, final judgment semantics, golden fixtures, score, quality gate, manifests, deterministic analyze/checklist changes.
- Plan does not enter `fund_agent/fund/` or `fund_agent/host/` or `fund_agent/agent/`.

### Criterion 7: Dirty worktree handling

**Assessment: PASS**

- Dirty Scope Boundary section (lines 29-49) explicitly states: "Implementation must treat them as existing local state and must not revert, clean, delete, restage, rename or normalize unrelated files."
- This gate is strictly incremental — it modifies only the orchestrator loop, adds CLI matrix helper, and adds tests. No rollback or folding of prior gate changes.

## Residual Risks

1. **`fail_fast` field semantics ambiguity**: If `fail_fast` remains as a constructor field with default `True` but is documented as no-op for body chapters, callers who explicitly set `fail_fast=True` expecting the old skip behavior will get silent behavioral change. The plan addresses this by either changing default to `False` or rejecting/ignoring `True` for body chapters. Implementation must choose one and update docstring. This is a minor API clarity risk, not a correctness risk.

2. **`skipped_chapter_ids` always empty for body chapters**: After implementation, `ChapterOrchestrationResult.skipped_chapter_ids` will be `()` for ordinary body chapter failures. If any downstream consumer (outside allowed files) checks `skipped_chapter_ids` to detect fail-fast behavior, it will break. The plan limits scope to orchestrator/CLI/tests, so this is contained.

3. **Mixed-matrix test complexity**: The mixed-matrix test (6 chapters with 6 different outcomes) requires careful fake client setup. If the test is too tightly coupled to internal implementation, it may be brittle. Implementation should use the existing `_FakeChapterLLMClient` / `_FakeAuditLLMClient` patterns from `test_chapter_orchestrator.py`.

4. **CLI matrix format stability**: The suggested `chapter_matrix=1:failed/llm_timeout/llm_timeout/unknown;2:accepted/...` format is semicolon-delimited with slash-separated fields. If a field value contains `;` or `/`, parsing breaks. Current safe scalar fields (status, stop_reason, category, subcategory) are enum-like and won't contain these characters, but future extension should be mindful.

## Conclusion

The plan is handoff-ready and code-generation-ready. It correctly identifies the exact code paths to change, preserves all safety boundaries, maintains final assembly fail-closed semantics, provides adequate test coverage, and respects the dirty worktree boundary. No blocking findings.

---

Reviewer: MiMo
Date: 2026-05-31
