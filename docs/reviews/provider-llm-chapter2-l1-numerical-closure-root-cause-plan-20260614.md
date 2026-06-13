# Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Evidence Plan

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Planning Gate`.

Role: planning worker only, not controller.

Goal: prepare a code-generation-ready, no-live evidence gate for the current Chapter 2 `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` failure observed after the accepted Chapter 3 item 01 bounded live evidence.

The next evidence gate must not implement a fix. It must classify root cause from direct no-live evidence and stop with an evidence artifact plus review inputs. It must preserve EID single-source/no-fallback and `NOT_READY`.

Out of scope:

- Live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.
- Source policy, provider defaults, repair budget calibration, annual-period LLM route, Docling, fallback, release/readiness or PR state changes.
- Reading chapter writer Markdown, auditor feedback Markdown, raw prompt, provider payload, source/cache/PDF body or report body.
- The evidence worker must not treat DS observations about `writer_deleted_item_rule_ids` or repair evidence usage as accepted root cause before direct no-live evidence proves them.

## 2. Planning Inputs Reviewed

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` relevant Route C / CHAPTER_CONTRACT / L1 / repair-budget sections
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md`
- Safe metadata only from:
  - `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/summary.json`
  - `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json`
- Chapter 2 contract excerpts from `docs/fund-analysis-template-draft.md`
- Narrow code excerpts from:
  - `fund_agent/fund/chapter_writer.py`
  - `fund_agent/fund/chapter_auditor.py`
  - `fund_agent/agent/repair.py`
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/services/llm_run_artifacts.py`
- Existing no-live test surface located but not executed:
  - `tests/fund/test_chapter_writer.py`
  - `tests/fund/test_chapter_auditor.py`
  - `tests/services/test_chapter_orchestrator.py`
  - `tests/services/test_llm_run_artifacts.py`
  - `tests/agent/test_repair_policy.py`

This section records planning-worker inputs only. It is not the evidence worker's allowed-read list. The next evidence worker must follow Section 6 and must not read the Chapter 3 item 01 evidence artifact or DS/MiMo review artifacts directly.

## 3. Accepted Current Facts

- The accepted Chapter 3 item 01 post-fix bounded live judgment accepts only safe runtime metadata from `manifest.json`, `summary.json`, `chapters/chapter-02.json` and `chapters/chapter-03.json`; writer Markdown, auditor feedback Markdown, raw prompts, provider payloads, source/cache/PDF bodies and report bodies were not accepted evidence.
- Chapter 3 no longer reproduces the provider-before `ValueError` / `code_bug`; it blocks as `missing_required_facts` / `fact_gap`.
- The first failed chapter is Chapter 2 with:
  - `status=failed`
  - `stop_reason=repair_budget_exhausted`
  - `failure_category=prompt_contract`
  - `failure_subcategory=l1_numerical_closure`
  - `attempt_count=2`
- `summary.json` and `chapter-02.json` agree that both Chapter 2 attempts have one `programmatic:L1` issue and `diagnostic_consistency_status=consistent`.
- Attempt 0 metadata:
  - writer status `drafted`
  - `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`
  - used 5 anchor ids and 3 fact ids
  - programmatic issue `programmatic:L1:line:10:7d718f9164`
  - repair decision `action=regenerate`, `source_repair_hint=patch`
- Attempt 1 metadata:
  - writer status `drafted`
  - `writer_deleted_item_rule_ids=["chapter_2_tracking_error_analysis"]`
  - used 4 anchor ids and 2 fact ids
  - programmatic issue `programmatic:L1:line:26:02ea024a63`
  - repair decision `action=stop`, `stop_reason=repair_budget_exhausted`
- Chapter 2 required output items `ch2.required_output.item_01` through `item_07` all declare `when_evidence_missing="block"` in the canonical template JSON.
- Chapter 2 writer prompt includes a specific instruction: if writing formula/percentage closure assertions, allowed anchor markers must be in the same sentence or within two surrounding lines; conclusion and evidence sections must not repeat unanchored R/A/B/C/A-C concrete percentages.
- Programmatic L1 currently flags a line when the line matches the numerical closure regex and numeric text regex, and the plus/minus two-line context lacks an anchor marker.
- Programmatic L1 emits `repair_hint="patch"`.
- Current Agent and Service repair policies map `patch` and `regenerate` to whole-chapter regenerate while budget remains, then stop as `repair_budget_exhausted`.
- Artifact serialization records safe per-attempt metadata including writer used fact ids, used anchor ids, declared missing reasons, deleted item rule ids, repair decisions and L1 diagnostic counts.
- Current runtime diagnostics still lack some useful metadata for auditor/programmatic phases, including `allowed_fact_count` and `allowed_anchor_count`.

## 4. Hypotheses

H1. Writer omits or deletes a required Chapter 2 numerical closure item.

- Current status: unproven.
- Supporting observations only: both attempts record deleted `chapter_2_tracking_error_analysis`, and attempt 1 used fewer anchors/facts than attempt 0.
- Counterweight: safe diagnostics show `required_output_missing_count=0`, so the next evidence gate must distinguish missing required output markers from optional ITEM_RULE deletion and from unanchored required-output content.

H2. Programmatic L1 rule is too strict or mismatched with accepted Chapter 2 contract.

- Current status: unproven.
- Supporting observations only: L1 fails on proximity to anchor marker, not on numerical equality itself; Chapter 2 contract requires numerical closure facts to be same-source and anchored.
- Evidence gate must prove whether plus/minus two-line anchor proximity is the accepted contract, an over-strict implementation detail, or an insufficient diagnostic for a broader contract violation.

H3. Repair regenerate strategy preserves or worsens the L1 failure.

- Current status: plausible but unproven as root cause.
- Supporting observations only: attempt 0 L1 issue receives `patch`, but current policy regenerates the whole chapter; attempt 1 still fails L1 and uses fewer anchors/facts.
- Evidence gate must prove whether the strategy itself causes persistence/regression, or whether the writer output would fail under any current repair mechanism.

H4. Evidence/fact availability is insufficient for Chapter 2 numerical closure.

- Current status: unproven.
- Supporting observations only: Chapter 2 used facts/anchors exist, but diagnostics do not expose all allowed fact/anchor counts in auditor/programmatic runtime metadata.
- Evidence gate must prove whether all seven required output items had available same-source evidence, unavailable evidence that should have blocked before provider, or available facts without usable anchors.

H5. Diagnostic serialization maps the failure correctly but lacks enough metadata.

- Current status: partially supported but not complete.
- Supporting facts: failure maps to `prompt_contract/l1_numerical_closure` consistently, safe diagnostics redact prompt/body content, and L1 count is serialized.
- Open gap: current safe metadata does not expose enough line-level non-body context, allowed fact/anchor counts, or required-output item linkage to distinguish H1-H4 without synthetic no-live reproduction.

## 5. No-live Evidence Plan

The evidence worker should create one evidence artifact under `docs/reviews/` and make no source behavior changes unless a later implementation gate is authorized. If the worker needs code changes only to add no-live diagnostic tests, those tests must be red-test-first and synthetic; they must not alter production behavior in this evidence gate.

### E0. Preflight and boundary proof

Commands:

```bash
git status --short
git diff --check
```

Expected evidence:

- Worktree state recorded only for scope ownership, not readiness.
- No control/design/README/source policy/readiness/release/PR changes.
- No live/provider/network/source/PDF/FDR/analyze/checklist command executed.

### E1. Safe metadata reconstruction

Commands:

```bash
jq '{schema_version,fund_code,report_year,orchestration_status,final_assembly_status,first_failed,chapter_matrix,prompt_contract_diagnostics}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/summary.json
jq '[.attempts[] | {attempt_index, writer_status, writer_stop_reason, writer_finish_reason, writer_max_output_chars, writer_response_chars, writer_deleted_item_rule_ids, writer_used_anchor_ids, writer_used_fact_ids, writer_declared_missing_reasons, audit_status, audit_repair_hint, programmatic_issues, repair_decision}]' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json
jq '{chapter_prompt_contract_diagnostics, chapter_runtime_diagnostics, issues, diagnostic_consistency_status}' reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/chapters/chapter-02.json
```

Expected evidence:

- Reconfirm Chapter 2 is the first failed chapter.
- Reconfirm both attempts fail only one `programmatic:L1` issue.
- Record exact per-attempt `writer_deleted_item_rule_ids`, `writer_used_anchor_ids`, `writer_used_fact_ids`, repair decisions and diagnostic gaps.
- Do not open `writer_draft_file` or `audit_feedback_file`.

### E2. Contract-to-rule comparison

Reads:

- `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON only.
- `fund_agent/fund/chapter_writer.py` Chapter 2 numerical closure prompt and deleted ITEM_RULE handling only.
- `fund_agent/fund/chapter_auditor.py` `_audit_numerical_closure()` and `_audit_item_rule_deleted_sections()` only.

Expected evidence:

- Map each Chapter 2 required output item to evidence behavior: all seven are `block` when evidence is missing.
- Map optional/conditional ITEM_RULE deletion to `chapter_2_tracking_error_analysis`; show whether deletion is allowed for this fund type and whether deletion can legally remove only optional tracking-error content, not required-output markers.
- Compare writer prompt proximity rule with auditor L1 proximity implementation.
- Produce a table: `contract clause -> writer instruction -> auditor predicate -> current metadata signal -> remaining ambiguity`.

### E3. H1 no-live reproducer: required item omitted vs optional item deleted

Use synthetic no-live tests only. Candidate tests:

```bash
uv run pytest tests/fund/test_chapter_writer.py --collect-only -q
uv run pytest tests/fund/test_chapter_auditor.py --collect-only -q
uv run pytest tests/fund/test_chapter_writer.py -k "required_output_block or l1_numerical_closure or tracking_error"
uv run pytest tests/fund/test_chapter_auditor.py -k "required output item marker or l1"
```

Before using any `-k` selector, collect test names first. If no existing test matches a selector, record `no matching existing tests` as evidence instead of treating empty selection as a pass.

If adding evidence-only tests is authorized by the evidence gate, add focused tests that:

- Build a Chapter 2 projection with `chapter_2_tracking_error_analysis` deleted.
- Prove deleting that ITEM_RULE does not permit missing `ch2.required_output.item_01` through `item_07`.
- Prove current safe metadata can or cannot distinguish:
  - missing required output marker,
  - present required marker with unanchored numerical closure,
  - optional tracking-error section correctly deleted.

Acceptance evidence for H1:

- Root cause H1 can be accepted only if a synthetic no-live reproduction shows the writer/metadata path omits a required Chapter 2 numerical closure required output or deletes required-output content because of the ITEM_RULE deletion.
- If `required_output_missing_count=0` remains true and synthetic tests show ITEM_RULE deletion is optional-only, H1 must be rejected or narrowed to presentation/metadata ambiguity.

### E4. H2 no-live reproducer: L1 rule strictness or mismatch

Use synthetic no-live tests:

```bash
uv run pytest tests/fund/test_chapter_auditor.py --collect-only -q
uv run pytest tests/services/test_chapter_orchestrator.py --collect-only -q
uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework"
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_prompt_contract_serialization or l1_repair_context or l1_failure_after_repair_budget_exhausted"
```

Before using any `-k` selector, collect test names first. If no existing test matches a selector, record `no matching existing tests` as evidence instead of treating empty selection as a pass.

If adding tests is authorized, add boundary cases:

- Anchor marker same line as numeric closure assertion: must pass L1.
- Anchor marker two lines away: must pass L1 if that is the intended contract.
- Anchor marker three lines away: must fail L1.
- A formula framework without concrete percentage: must pass L1.
- A missing-data sentence with a concrete percentage closure: must fail L1.
- A valid same-source fact with no evidence anchor id: must not be silently converted into an anchored numerical closure.

Acceptance evidence for H2:

- Accept H2 only if the current L1 predicate rejects content that the Chapter 2 contract explicitly permits, or if the contract is materially ambiguous and tests cannot encode an accepted boundary without a design decision.
- Reject H2 if tests prove the implementation matches the accepted prompt/contract boundary and the observed failure is a valid L1 blocker.

### E5. H3 no-live reproducer: repair regenerate preserves or worsens L1 failure

Reads:

- `fund_agent/agent/repair.py` repair decision mapping.
- `fund_agent/services/chapter_orchestrator.py` repair decision mapping and prompt-contract diagnostic construction.
- `tests/agent/test_repair_policy.py`
- `tests/services/test_chapter_orchestrator.py`

Commands:

```bash
uv run pytest tests/agent/test_repair_policy.py --collect-only -q
uv run pytest tests/services/test_chapter_orchestrator.py --collect-only -q
uv run pytest tests/agent/test_repair_policy.py -k "repair_budget_exhausted"
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted"
```

Before using any `-k` selector, collect test names first. If no existing test matches a selector, record `no matching existing tests` as evidence instead of treating empty selection as a pass.

If adding tests is authorized, add a synthetic two-attempt orchestrator test where:

- Attempt 0 fails L1 with an unanchored numerical closure.
- Repair context contains the Chapter 2 L1 required correction.
- Attempt 1 drops at least one previously used anchor/fact and still fails L1.
- The final failure remains `repair_budget_exhausted/prompt_contract/l1_numerical_closure`.

Acceptance evidence for H3:

- Accept H3 only if no-live evidence proves the current whole-chapter regenerate strategy fails to preserve or improve the specific L1 repair target even when the repair context is correct.
- Do not use H3 to authorize repair budget changes; budget calibration remains a separate gate.

### E6. H4 no-live evidence/fact availability proof

Reads:

- Safe metadata from Chapter 2 JSON.
- `fund_agent/fund/chapter_facts.py` only if needed to identify which Chapter 2 facts/anchors are projected.
- `tests/fund/test_chapter_facts.py` only if needed for projection tests.

Commands:

```bash
uv run pytest tests/fund/test_chapter_facts.py --collect-only -q
uv run pytest tests/fund/test_chapter_writer.py --collect-only -q
uv run pytest tests/fund/test_chapter_facts.py -k "chapter_2 or tracking_error"
uv run pytest tests/fund/test_chapter_writer.py -k "required_output_block"
```

Before using any `-k` selector, collect test names first. If no existing test matches a selector, record `no matching existing tests` as evidence instead of treating empty selection as a pass.

If adding tests is authorized, add synthetic projection/evidence availability tests that:

- Enumerate required output ids `ch2.required_output.item_01` through `item_07`.
- Record whether each id has `available`, `missing`, `unavailable`, `not_applicable` or `unreviewed` same-source evidence.
- Record whether available facts have usable evidence anchor ids.
- Prove missing Chapter 2 required evidence blocks before provider, rather than letting writer draft unsupported numbers.

Acceptance evidence for H4:

- Accept H4 if required Chapter 2 numerical closure facts or anchors are unavailable and current code fails to block early or fails to expose the fact gap clearly.
- Reject H4 if required facts/anchors are available and the failure is solely unanchored writer output.

### E7. H5 diagnostic serialization proof

Reads:

- `fund_agent/services/llm_run_artifacts.py` serialization only.
- `tests/services/test_llm_run_artifacts.py`
- `tests/services/test_chapter_orchestrator.py`

Commands:

```bash
uv run pytest tests/services/test_llm_run_artifacts.py --collect-only -q
uv run pytest tests/services/test_chapter_orchestrator.py --collect-only -q
uv run pytest tests/services/test_llm_run_artifacts.py -k "l1 or repair_budget_exhausted or writer_used"
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_prompt_contract_serialization"
```

Before using any `-k` selector, collect test names first. If no existing test matches a selector, record `no matching existing tests` as evidence instead of treating empty selection as a pass.

If adding tests is authorized, add assertions that the safe artifact exposes enough metadata to answer:

- Which required output ids were missing or present.
- Which optional ITEM_RULE ids were deleted.
- Which allowed/used fact ids and anchor ids changed between attempts.
- Which L1 issue prefix/count/subcategory triggered stop.
- Which diagnostic fields remain intentionally redacted and which are missing but safe to add later.

Acceptance evidence for H5:

- Accept H5 as a contributing diagnostic gap if current serialization maps the category correctly but cannot separate H1-H4 without reading forbidden bodies or adding synthetic tests.
- Do not accept H5 as the content root cause unless diagnostic absence itself caused an incorrect runtime decision.

## 6. Allowed Read/Command Matrix

| Category | Allowed | Forbidden |
| --- | --- | --- |
| Control truth | `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md` relevant Route C / CHAPTER_CONTRACT / L1 / repair-budget sections | Control/design/README edits |
| Accepted evidence | Chapter 3 item 01 controller judgment `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Direct reads of `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md`, `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-ds-20260614.md`, or `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-review-mimo-20260614.md` in the evidence gate |
| Runtime artifacts | `summary.json`, `chapters/chapter-02.json`, and if needed `manifest.json` safe metadata via `jq` | writer draft Markdown, repair draft Markdown, auditor feedback Markdown, raw prompts, provider payload, report body |
| Template | `docs/fund-analysis-template-draft.md` Chapter 2 canonical JSON and Chapter 2 template excerpt | Non-Chapter-2 template rewrites or future design edits |
| Code reads | `chapter_writer.py` `_ch2_numerical_closure_contract_prompt()` / `_deleted_item_rule_ids()` / `_allowed_anchor_ids()` only; `chapter_auditor.py` `_audit_numerical_closure()` / `_audit_item_rule_deleted_sections()` / `_aggregate_repair_hint()` only; `agent/repair.py` `AgentRepairDecision` / `decide_repair()` / `repair_context_from_audit()` only; `services/chapter_orchestrator.py` `ChapterRepairDecision` / `serialize_chapter_prompt_contract_diagnostics()` / `_audit_prompt_contract_diagnostic()` / `_decide_repair()` / `_repair_context_from_audit()` / `_stop_reason_from_repair_decision()` / `_prompt_contract_diagnostic_payload()` only; `services/llm_run_artifacts.py` `write_llm_incomplete_run_artifacts()` / `_build_chapter_payload()` / `_repair_decision_payload()` / `_chapter_matrix_row()` / `_prompt_contract_diagnostic_payload()` only; `chapter_facts.py` `project_chapter_facts()` / `_chapter_field_specs()` / `_project_chapter()` / `_item_rule_decisions_for_chapter()` only if needed | Source helper, PDF/cache parser body, FDR live/source access internals unless separately authorized |
| Tests | Focused no-live pytest with fake/synthetic inputs under `tests/fund`, `tests/services`, `tests/agent` | Live/provider/network/analyze/checklist/readiness/release/PR commands |
| Shell | `git status --short`, `git diff --check`, `rg`, `sed`, `nl`, `jq`, focused `uv run pytest <file> --collect-only -q`, focused `uv run pytest ... -k ...` after collection confirms matching tests or after recording `no matching existing tests` | `fund-analysis analyze`, `fund-analysis checklist`, network/provider commands, source/PDF/FDR commands, `git add`, commit, push, PR |

## 7. Acceptance Criteria

The next evidence artifact is acceptable only if it:

- States `NOT_READY` and does not claim release, MVP, provider/LLM path or PR readiness.
- Reconstructs Chapter 2 failure from safe metadata without reading forbidden bodies.
- Separates all five hypotheses and assigns each one one of:
  - `accepted root cause`
  - `accepted contributing cause`
  - `rejected`
  - `needs more evidence`
  - `blocked by forbidden read or missing authorization`
- Provides direct no-live evidence for every accepted or rejected hypothesis.
- Distinguishes required-output marker omission from optional ITEM_RULE deletion.
- Distinguishes L1 rule mismatch from valid enforcement of the accepted Chapter 2 contract.
- Distinguishes writer/fact availability failure from repair strategy failure.
- Identifies any diagnostic metadata that is safe and necessary to add in a later implementation gate.
- Includes exact commands run, exit status, and relevant assertions.
- Leaves source policy, provider defaults, repair budget, annual-period LLM route, fallback, readiness/release and PR state unchanged.

## 8. Residuals

- Full LLM completion remains unproven.
- Chapter 3 remains a fact-gap block and has no accepted draft/conclusion.
- Chapter 2 root cause is not yet accepted by this plan.
- Runtime diagnostic completeness remains incomplete for auditor/programmatic allowed fact/anchor counts and required-output linkage.
- Repair budget calibration is a separate future gate; this plan must not authorize changing `max_repair_attempts`.
- Product policy for rendering Chapter 2 or Chapter 3 evidence gaps is a separate gate.
- Live/provider/content-quality/additional-sample/readiness/release/PR states remain deferred.

## 9. Next Gate Recommendation

Proceed to `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`.

Recommended evidence artifact path:

`docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`

Recommended review:

- At least two independent reviews of the evidence artifact.
- Reviewers must check that no forbidden body/source/live read was used and that DS observations were treated as hypotheses unless proven by direct no-live evidence.
- Controller judgment must preserve `NOT_READY` unless a later, separately authorized gate changes readiness disposition.

## 10. Final Verdict

VERDICT: READY_FOR_NO_LIVE_ROOT_CAUSE_EVIDENCE_GATE
