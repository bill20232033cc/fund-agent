# Plan Review: Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Plan

Date: 2026-06-14
Reviewer: MiMo
Artifact under review: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-20260614.md`
Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Planning Gate`

## Findings

### F1. Evidence-reviewed list over-reads allowed-reads boundary [NON-BLOCKING]

The plan's Section 2 "Evidence Reviewed" lists four artifacts from the Chapter 3 item 01 evidence chain:

- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md` (evidence artifact)
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-ds-20260614.md` (DS review)
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-mimo-20260614.md` (MiMo review)
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` (controller judgment)

Only the controller judgment is in the explicit allowed-reads list. The other three are review-chain artifacts, not forbidden content (not writer Markdown, auditor feedback, raw prompts, provider payloads, or source/PDF bodies), but they are not explicitly authorized either. All four files exist on disk.

Impact: The evidence worker may read artifacts beyond the explicit allowed-reads boundary. Since the evidence/review artifacts are process evidence (not forbidden body content), this is a precision issue, not a safety violation.

Amendment: Either add the three review artifacts to the allowed-reads list for the evidence gate, or remove them from Section 2 and rely solely on the controller judgment for accepted Chapter 3 facts.

### F2. `docs/design.md` referenced but not in allowed reads [NON-BLOCKING]

Section 2 lists `docs/design.md` relevant Route C / CHAPTER_CONTRACT / L1 / repair-budget sections as reviewed evidence. `docs/design.md` is not in the explicit allowed-reads list for this review gate. However, it is referenced in `AGENTS.md` as a must-read, and the plan uses it only to map contract-to-rule relationships in E2, not to read forbidden body content.

Impact: The evidence worker will need to read `docs/design.md` for contract mapping. This is legitimate scope for a root-cause evidence gate but should be explicitly authorized.

Amendment: Add `docs/design.md` relevant sections to the allowed-reads list for the evidence gate, or restructure E2 to derive contract rules solely from `AGENTS.md`, `docs/implementation-control.md`, and the template JSON.

### F3. Code-read boundaries use "only if needed" qualifiers [NON-BLOCKING]

Section 2 lists several code files for narrow reading:

- `fund_agent/fund/chapter_writer.py` — "Chapter 2 numerical closure prompt and deleted ITEM_RULE handling only"
- `fund_agent/fund/chapter_auditor.py` — "`_audit_numerical_closure()` and `_audit_item_rule_deleted_sections()` only"
- `fund_agent/agent/repair.py` — "repair decision mapping"
- `fund_agent/services/chapter_orchestrator.py` — "repair decision mapping and prompt-contract diagnostic construction"
- `fund_agent/services/llm_run_artifacts.py` — "serialization only"
- `fund_agent/fund/chapter_facts.py` — "only if needed"

The function-level boundaries for `chapter_writer.py` and `chapter_auditor.py` are precise. The remaining files use broader qualifiers ("repair decision mapping", "serialization only", "only if needed") that could allow a worker to read more than necessary.

Impact: Execution ambiguity; a disciplined worker would scope correctly, but the plan could be tighter.

Amendment: For each code file, specify the exact function/class or line range to read, consistent with the precision applied to `chapter_writer.py` and `chapter_auditor.py`.

### F4. `docs/fund-analysis-template-draft.md` referenced without explicit allowed-reads entry [NON-BLOCKING]

E2 reads "Chapter 2 canonical JSON only" from `docs/fund-analysis-template-draft.md`. This file is not in the explicit allowed-reads list. It is the template truth source referenced in `AGENTS.md` and `docs/implementation-control.md`.

Impact: The evidence worker needs template contract data to map required output items. This is legitimate scope.

Amendment: Add `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON to the allowed-reads list for the evidence gate.

### F5. Safe metadata verification confirms plan's accepted facts [STRENGTH]

Verified from `summary.json` and `chapters/chapter-02.json`:

- First failed chapter: Chapter 2, `status=failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`, `attempt_count=2`.
- Both attempts: `required_output_missing_count=0`, `l1_numerical_closure_count=1`, `diagnostic_consistency_status=consistent`.
- Attempt 0: `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`, 5 anchor ids, 3 fact ids, `repair_hint=patch`, `repair_decision=regenerate`.
- Attempt 1: `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`, 4 anchor ids, 2 fact ids, `repair_hint=patch`, `repair_decision=stop` with `repair_budget_exhausted`.
- Chapter runtime diagnostics: `allowed_anchor_count=null`, `allowed_fact_count=null`, `max_output_chars=null` for both attempts.

The plan's Section 3 "Accepted Current Facts" accurately reflects the safe metadata. The diagnostic gaps noted in H5 (`allowed_fact_count`, `allowed_anchor_count` missing) are confirmed by the `null` values in runtime diagnostics.

### F6. NOT_READY and EID single-source/no-fallback preserved [STRENGTH]

The plan explicitly preserves these in:
- Section 1: "It must preserve EID single-source/no-fallback and `NOT_READY`."
- Section 7: Acceptance criteria require stating `NOT_READY`.
- Section 10: Verdict `READY_FOR_NO_LIVE_ROOT_CAUSE_EVIDENCE_GATE` does not claim readiness.

### F7. Forbidden commands and reads correctly enumerated [STRENGTH]

Section 1 "Out of scope" and Section 6 "Allowed Read/Command Matrix" correctly enumerate forbidden items:
- Live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.
- Source policy, provider defaults, repair budget calibration, annual-period LLM route, Docling, fallback, release/readiness or PR state changes.
- Chapter writer Markdown, auditor feedback Markdown, raw prompts, provider payloads, source/cache/PDF bodies, report bodies.
- Treating DS observations as accepted root cause before no-live evidence.

### F8. H1-H5 separated with direct evidence paths [STRENGTH]

Each hypothesis has:
- A clear statement of what must be proven.
- Current status (unproven / plausible / partially supported).
- Supporting observations and counterweights.
- A dedicated evidence section (E3-E7) with specific test commands, code reads, and acceptance criteria.
- Explicit conditions for acceptance vs. rejection.

The plan correctly treats DS observations about `writer_deleted_item_rule_ids` and repair evidence usage as hypotheses (H1, H3), not accepted root cause.

### F9. No implementation over-authorization [STRENGTH]

The plan consistently uses conditional language for code/test additions:
- "If adding evidence-only tests is authorized by the evidence gate" (E3)
- "If adding tests is authorized" (E4, E5, E6, E7)

The plan explicitly states: "The evidence worker should create one evidence artifact under `docs/reviews/` and make no source behavior changes unless a later implementation gate is authorized."

This correctly scopes the evidence gate as classification-only, not implementation.

### F10. Acceptance criteria are complete and precise [STRENGTH]

Section 7 requires the evidence artifact to:
- State `NOT_READY`.
- Reconstruct failure from safe metadata.
- Separate all five hypotheses with explicit disposition.
- Provide direct no-live evidence for every accepted/rejected hypothesis.
- Distinguish required-output omission from optional ITEM_RULE deletion.
- Distinguish L1 rule mismatch from valid enforcement.
- Distinguish writer/fact availability failure from repair strategy failure.
- Identify diagnostic metadata safe to add later.
- Include exact commands, exit status, and assertions.
- Leave all policy/budget/readiness/PR state unchanged.

These criteria are sufficient for the evidence worker to produce a complete artifact without scope drift.

## Verdict

**ACCEPT_WITH_AMENDMENTS**

The plan is safe, correctly scoped, and ready for the no-live root-cause evidence gate. The four non-blocking findings (F1-F4) are precision improvements to the allowed-reads boundary that should be resolved before the evidence worker executes. The plan's core safety properties (NOT_READY preservation, EID single-source, live-command prohibition, hypothesis-as-hypotheses, no implementation over-authorization) are all correctly maintained.

### Required Amendments

1. **F1**: Add the three Chapter 3 item 01 review artifacts to the evidence gate's allowed-reads list, or remove them from Section 2.
2. **F2**: Add `docs/design.md` relevant sections to the evidence gate's allowed-reads list.
3. **F3**: Specify exact function/class or line-range boundaries for code reads of `repair.py`, `chapter_orchestrator.py`, `llm_run_artifacts.py`, and `chapter_facts.py`.
4. **F4**: Add `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON to the evidence gate's allowed-reads list.

### Preflight Evidence

- `git diff --check`: exit 0, no whitespace errors.
- `git status --short`: working tree has unstaged changes to `AGENTS.md`, `README.md`, `docs/design.md` and untracked review artifacts. No forbidden stage/commit/push/PR activity.
- Safe metadata verified from `summary.json` and `chapters/chapter-02.json`; plan's accepted facts confirmed accurate.
