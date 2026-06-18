# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Plan Review — AgentMiMo

Date: 2026-06-14

Role: AgentMiMo independent plan reviewer.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Planning Gate`

Release/readiness: `NOT_READY`

Verdict: `PASS`

## 1. Review Scope

Independent adversarial review of `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md` against five review questions, using `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, the accepted diagnostic evidence and controller judgment, and source/test snippets only as needed.

No source/test/runtime/control-doc/design-doc changes were made.

## 2. Review Questions

### Q1: Does the plan use the accepted diagnostic evidence without overreading runtime metadata, provider behavior, source policy or readiness?

**Finding: PASS**

The plan correctly references only accepted facts from the controller judgment `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-controller-judgment-20260614.md`:

- Attempt 0 drafted content, reached auditor, then received regenerate repair handling.
- Attempt 1 stopped at writer forbidden-phrase validation before any second audit/repair.
- Provider attempt count is `0`; no provider-response classification is claimed.
- Writer and auditor forbidden-phrase guards are deterministic.
- Visible repair correction mapping lacks a forbidden-phrase-specific branch.
- Default repair budget remains `max_repair_attempts=1`.

The plan does not overread runtime metadata (no raw prompt bodies, no provider payload, no report bodies). It explicitly states provider behavior is "not classified because accepted evidence has provider attempt count `0`." Source/FDR/PDF/golden/readiness are stated as unrelated to the no-live writer validation path.

Root-cause section 3 uses same-source logic only, consistent with `AGENTS.md:71` requiring direct root-cause evidence.

### Q2: Is choosing only forbidden-phrase-specific repair prompt guidance justified over diagnostic lineage changes for this implementation slice?

**Finding: PASS**

The plan explicitly defers diagnostic lineage clarification (H4) with a clear rationale: "The same-source evidence shows the blocking behavior happens when attempt 1 enters writer validation with a forbidden phrase after a generic repair attempt. The diagnostic lineage mismatch is accepted as layering, but it does not directly cause the forbidden phrase to be generated or accepted."

This is a sound deferral. The diagnostic lineage (`audit_parse` at attempt 0 vs `prompt_contract/forbidden_phrase` at attempt 1) is a taxonomy layering issue, not the mechanism that produces or blocks the forbidden phrase. The actual blocking mechanism is: (1) repair context lacks forbidden-phrase-specific guidance, (2) writer regenerates with forbidden phrase, (3) writer validation blocks, (4) budget is exhausted.

Choosing prompt guidance alone for this slice targets the actual root cause. Diagnostic lineage can be addressed in a separate gate without blocking this fix.

### Q3: Are proposed source changes narrowly scoped and consistent with Service/Host/Agent/Fund boundaries?

**Finding: PASS**

The plan constrains changes to exactly one file: `fund_agent/fund/chapter_writer.py`. It explicitly excludes:

- `fund_agent/agent/repair.py` (Agent layer)
- `fund_agent/agent/runner.py` (Agent layer)
- `fund_agent/services/chapter_orchestrator.py` (Service layer)
- provider/runtime/config/readiness/source code

Adding a private helper `_ch5_forbidden_phrase_repair_guidance_prompt()` and appending it to the existing `repair_context` assembly in `_chapter_prompt_fragments()` (line 737-744) is consistent with Fund boundary ownership of chapter prompt assembly. The helper follows the same pattern as the existing `_ch2_l1_repair_guidance_prompt()` at line 1289, which is already used in the same assembly block.

The helper returns empty string for non-Chapter 5 or non-repair contexts, preserving existing behavior for all other chapters and initial attempts. `_repair_context_prompt()` is explicitly kept unchanged. `_FORBIDDEN_PHRASES` is explicitly kept unchanged. Agent runner retry behavior is explicitly kept unchanged.

### Q4: Are tests sufficient to prove prompt rendering, runner propagation, no hidden retry, and no budget/default changes?

**Finding: PASS**

The plan requires three new tests:

1. `test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt` — proves the Chapter 5 repair prompt contains the forbidden-phrase-specific checklist with required semantics (trading action, position action, return prediction, manager motive, boundary vocabulary, data-gap phrasing).

2. `test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair` — proves the guidance is not injected for Chapter 5 initial attempts, other chapters, or other repair contexts. This guards against over-broad prompt injection.

3. `test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance` — proves end-to-end runner propagation: first writer request has no repair context, second writer request carries `repair_context.previous_issue_ids` including `llm:parse_failure`, second writer request `user_prompt` contains the forbidden-phrase guidance, and no third writer request is made. This proves prompt rendering, runner propagation, no hidden retry, and budget preservation in a single integration test.

The existing focused suite (11 tests) continues to cover:
- Writer forbidden-phrase blocking (`test_writer_rejects_forbidden_trading_advice`)
- Generic repair context rendering (`test_repair_context_is_rendered_into_writer_prompt_without_extra_payload`)
- Chapter 2 L1 guidance (2 tests)
- Repair budget exhaustion (3 tests across policy/runner/orchestrator)
- Forbidden-phrase subcategory diagnostics (2 tests)
- Audit parse failure diagnostic (1 test)

No new Service diagnostic-lineage test is required because diagnostic lineage is deliberately deferred. This is consistent with the deferral rationale.

### Q5: Are there blockers before implementation?

**Finding: NO BLOCKERS**

Source references verified:

- `chapter_writer.py:97-110` — `_FORBIDDEN_PHRASES` confirmed at exact lines.
- `chapter_writer.py:617-620` — system prompt broad policy text confirmed.
- `chapter_writer.py:737-742` — `_chapter_prompt_fragments()` repair_context assembly confirmed; `_ch2_l1_repair_guidance_prompt()` call at line 741 is the insertion point for the new helper.
- `chapter_writer.py:1458-1480` — `_repair_context_prompt()` confirmed rendering generic issue ids/messages/corrections.
- `chapter_writer.py:1612-1645` — writer validation chain including `_forbidden_phrase_issues(text)` at line 1643 confirmed.
- `chapter_writer.py:1939-1960` — `_forbidden_phrase_issues()` emitting `writer:forbidden_phrase:<index>` confirmed.
- `repair.py:277-340` — `_required_correction_from_issue()` confirmed: no forbidden-phrase-specific branch; `llm:parse_failure` maps to auditor line-protocol correction at line 338-339.

Existing test function names verified in codebase:
- `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist` (line 1326)
- `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context` (line 1364)
- `test_repair_budget_exhausted_records_each_regenerate_attempt` (line 489)
- `test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry` (line 553)

`ChapterPromptFragments` class at line 305 has a `repair_context: str` field, confirming the new helper's output fits the existing dataclass.

The plan's suggested prompt text is concrete and testable. The helper signature uses existing types (`ChapterFactInput`, `ChapterRepairContext | None`). The insertion point after `_ch2_l1_repair_guidance_prompt()` in the assembly block is correct.

No architectural, boundary, scope, sequencing, or control-doc blockers identified.

## 3. Findings Summary

| # | Question | Verdict | Notes |
|---|---|---|---|
| Q1 | Evidence fidelity | PASS | No overreading; provider behavior unclassified; source/FDR/readiness excluded |
| Q2 | Path justification | PASS | Diagnostic lineage deferred with sound rationale; prompt guidance targets actual blocking mechanism |
| Q3 | Scope and boundaries | PASS | Single file, Fund boundary, same pattern as existing Ch2 L1 guidance |
| Q4 | Test sufficiency | PASS | 3 new tests cover rendering, absence guard, and end-to-end propagation; 11 existing tests preserved |
| Q5 | Blockers | NONE | All source references verified; no boundary/scope/control-doc blockers |

## 4. Verdict

```text
PASS
```

The plan is code-generation-ready. It narrowly targets the Chapter 5 forbidden-phrase repair-context gap with a single-file Fund-layer change, follows the established Ch2 L1 guidance pattern, provides sufficient tests to prove prompt rendering and runner propagation without hidden retry or budget changes, and correctly defers diagnostic lineage to a separate gate. No blocking findings.
