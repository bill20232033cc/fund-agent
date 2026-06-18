# Provider/LLM Chapter 3 Required-output Policy Plan Review (DS)

Date: 2026-06-14

Role: AgentDS independent plan review worker.

Gate: `Provider/LLM Chapter 3 Required-output Policy Planning Gate`.

Review target: `docs/reviews/provider-llm-chapter3-required-output-policy-plan-20260614.md`

## 1. Scope

This review assesses whether the plan is code-generation-ready, appropriately scoped, and correct to recommend changing `ch3.required_output.item_01` to `render_evidence_gap` with no-live enforcement and final assembly readiness tests. No implementation, source change, test run, or control-doc update is performed.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` (Route C, typed template, final assembly readiness sections)
- `docs/fund-analysis-template-draft.md` (Chapter 3 `required_output_items`)
- `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-controller-judgment-20260614.md`

Narrow code read for feasibility:

- `fund_agent/fund/chapter_writer.py` (lines 134-165 `RequiredOutputEvidencePlan`, 942-1031 `_required_output_action`, 1751-1770 `_required_output_degrade_issues`)
- `fund_agent/agent/runner.py` (`_final_readiness` contract)
- `fund_agent/services/final_chapter_assembler.py` (lines 66-80 `FinalAssemblyPolicy`, `_validate_orchestration`)
- `fund_agent/fund/evidence_availability.py` (lines 247-249 `ch3.required_output.item_01` mapping)
- `fund_agent/fund/template/typed_contracts.py` (lines 26-31 `MissingEvidenceBehavior`)

No writer markdown, auditor markdown, raw prompts, provider payload/response, source/cache/PDF body, final report body, live/provider/network/FDR/analyze/checklist/readiness/release/PR commands were read or run.

## 3. Findings

### F1 — Scope is correctly bounded and conservative (ACCEPT)

The plan limits itself to one template JSON line change and focused no-live tests across four files. It explicitly defers live/provider/network/source/PDF/FDR commands, EID source policy changes, provider defaults, repair budget calibration, annual-period LLM route, Docling/parser policy, fallback policy, release/readiness, and PR/push/merge. Every Slice ends with a Non-goals section. The next-gate recommendation correctly classifies as `standard` and requires no live work.

### F2 — `MissingEvidenceBehavior` type already supports `render_evidence_gap` (ACCEPT)

Verified in `fund_agent/fund/template/typed_contracts.py:26-31`:

```python
MissingEvidenceBehavior: TypeAlias = Literal[
    "render_evidence_gap",
    "render_minimum_verification_question",
    "delete_if_not_applicable",
    "block",
]
```

The `_required_output_action()` function at `chapter_writer.py:1023-1024` already handles the `render_evidence_gap` branch correctly. No parser, writer, or typed-contract code change is needed to support the new enum value. The plan is correct to list parser changes as a non-goal in Slice 1.

### F3 — Evidence availability mapping is unchanged and correctly preserved (ACCEPT)

Verified in `fund_agent/fund/evidence_availability.py:247-249`: `ch3.required_output.item_01` maps to `structured.basic_identity` and `structured.portfolio_managers`. The plan does not alter this mapping. The envelope-absence fail-closed test (`test_chapter_3_missing_typed_availability_blocks_before_provider`) is preserved in Slice 2 step 4, correctly distinguishing "reviewed evidence is missing" (now degraded) from "availability contract plumbing is missing" (still blocked).

### F4 — Final assembly behavior does not require code changes (ACCEPT)

Verified in `fund_agent/services/final_chapter_assembler.py`: `FinalAssemblyPolicy.require_orchestration_accepted` (line 79), `_validate_orchestration()` checks per-chapter `accepted_draft` and `accepted_conclusion`. When Chapter 3 item 01 degrades to evidence-gap rendering and the writer produces compliant output, the chapter can be accepted. A blocked or unsafe chapter remains non-accepted and blocks assembly. No assembler code change is needed. Slice 3's non-goal correctly states "expected implementation should not need final assembler changes."

### F5 — Test name consistency between plan body and validation matrix (ACCEPT_WITH_NOTE)

Slice 1 step 3 says to rename `test_chapter_3_basic_manager_info_missing_behavior_blocks` with new assertions. The validation matrix Section 7 references `test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap`. These are consistent — rename implies the old name is replaced by the new one. The implementation worker should ensure the old test name is fully removed, not duplicated.

### F6 — Negative degradation test correctly targets writer-output validation (ACCEPT)

Slice 2 step 3 adds a negative test where the writer emits the item marker but omits approved gap wording, and the assertion expects `_required_output_degrade_issues()` to block. Verified in `chapter_writer.py:1751-1770` that this function checks for approved gap phrases (`证据不足`, `数据不足`, `未披露`, `未复核`, `不能据此判断`) in the segment after the marker. The plan's approved gap phrase list (Section 5) matches the existing code. The plan correctly notes that the new blocker classification will follow the writer-output validation mapping, not `required_output_block:ch3.required_output.item_01`.

### F7 — Option comparison is thorough and recommendation is well-supported (ACCEPT)

The plan evaluates three options (keep `block`, switch to `render_evidence_gap`, switch to `render_minimum_verification_question`). The recommendation for Option B is grounded in: consistency with items 02-05 already using evidence-gap rendering; preservation of fail-closed safety through writer output validation; and the CHAPTER_CONTRACT design goal of "lowest cognitive burden stable next action." The rejected Option A (keep block) would be inconsistent, and Option C (minimum verification question) mischaracterizes a descriptive required output as a process todo.

### F8 — Documentation sync (Slice 4) is appropriately conditional (ACCEPT)

Slice 4 uses a grep-based discovery approach before updating any docs. It explicitly forbids updating `docs/current-startup-packet.md` or `docs/implementation-control.md` unless a controller opens a sync gate. It correctly distinguishes between general design text (which need not change) and specific hard-block statements (which must be updated). This is conservative and appropriate for a planning gate.

### F9 — Residual risk tracking is complete (ACCEPT)

Section 9 identifies four risks with explicit mitigations and three residuals with explicit owners. The key risk — that no-live fake writer tests can overfit — is mitigated by the dual positive/negative test structure. The residual that post-implementation bounded live re-evidence remains separate is correctly stated.

## 4. Accepted Points

1. The plan correctly identifies that the current `ch3.required_output.item_01` blocker is policy-driven (`when_evidence_missing="block"`), not a code bug.
2. The recommendation to degrade to `render_evidence_gap` is correct: it aligns with items 02-05, preserves fail-closed safety through writer output validation, and allows Chapter 3 to produce an accepted draft without inventing unsupported manager claims.
3. The three-slice structure (template policy → agent writer tests → service assembly tests) is correctly sequenced and each slice has tight scope boundaries.
4. The plan preserves EID single-source/no-fallback, `NOT_READY`, and does not change provider defaults, repair budget, annual-period LLM route, Docling/parser policy, or fallback policy.
5. No code changes are needed to `typed_contracts.py`, `chapter_writer.py`, `evidence_availability.py`, or `final_chapter_assembler.py` — the template JSON change is sufficient.
6. The validation matrix is no-live only and covers all four affected test files plus a focused regression bundle.
7. The `EvidenceAvailability` envelope-absence test is preserved as fail-closed, correctly distinguishing "reviewed evidence missing" from "contract plumbing missing."

## 5. Required Amendments

None. The plan is code-generation-ready as written.

Minor advisory for the implementation worker (not a plan amendment):

- When renaming `test_chapter_3_basic_manager_info_missing_behavior_blocks` in Slice 1, verify the old test name is fully removed from the test file (no duplicated near-identical tests).
- In Slice 2 step 2 assertion (final assembly readiness for single-target), the plan says "assert Agent readiness is ready for accepted source chapter ids `(3,)`". The implementation worker should verify this assertion against the current `_final_readiness()` contract in `runner.py` to avoid an over-broad readiness claim.

## 6. Verdict

VERDICT: PASS

The plan is code-generation-ready, appropriately scoped, and correct. `ch3.required_output.item_01` should change to `render_evidence_gap`. The `MissingEvidenceBehavior` type and `_required_output_action()` function already support this value. The three implementation slices are well-bounded, the validation matrix is complete and no-live only, and no assembler or parser code changes are needed. EID single-source/no-fallback and `NOT_READY` are preserved. The plan is ready for a no-live policy implementation gate.
