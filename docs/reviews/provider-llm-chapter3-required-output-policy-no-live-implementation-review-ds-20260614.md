# Provider/LLM Chapter 3 Required-output Policy No-live Implementation Review DS

Date: 2026-06-14

Role: AgentDS independent implementation review worker.

## 1. Scope

Gate under review: `Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`.

This review assesses whether the no-live implementation correctly applies the accepted plan (`2725c74`) and all four binding controller amendments from `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`.

Review only. No implementation, no control-doc updates, no live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.

## 2. Evidence Reviewed

- Implementation evidence: `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-evidence-20260614.md`
- Controller judgment (binding amendments): `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`
- Truth/control: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- Actual code diff: `git diff HEAD -- docs/fund-analysis-template-draft.md tests/fund/template/test_typed_contracts.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/README.md`
- Controller pre-validated results: pytest 74 passed, ruff passed, `git diff --check` passed

Forbidden bodies not read: writer/auditor markdown, raw prompt, provider payload/response, source/cache/PDF body, final report body.

## 3. Findings

No findings of severity FAIL. All four controller amendments are correctly applied. Scope boundaries are respected.

### 3.1 Cross-check: Controller Amendment 1 — Full assembly shape (PASS)

**Requirement**: Slice 3 must choose full fake Route C body run with all required body chapters 1-6 accepted, asserting `assembled_chapter_ids == (0,1,2,3,4,5,6,7)`.

**Evidence**: `test_analyze_with_llm_accepts_final_assembly_when_ch3_item01_degrades_to_gap` asserts:
- `[request.chapter_id for request in writer.requests] == [1, 2, 3, 4, 5, 6]` (line ~466)
- `result.final_assembly_result.assembled_chapter_ids == (0, 1, 2, 3, 4, 5, 6, 7)` (line ~469)
- `result.final_assembly_result.report_markdown is not None` (line ~470)
- `result.llm_orchestration_result.status == "accepted"` (line ~466)
- `chapter_3.status == "accepted"` (line ~467)

The test uses `_Chapter3Item01GapWriterLLMClient` which inserts approved gap wording for Chapter 3 item 01. Full 6-chapter body run with final 8-chapter assembly is asserted. Amendment satisfied.

### 3.2 Cross-check: Controller Amendment 2 — Direct negative service-level assertion (PASS)

**Requirement**: Must include or identify a direct negative service-level assertion that unsafe Chapter 3 item 01 output keeps final assembly incomplete and report markdown absent.

**Evidence**: `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness` was updated to directly target unsafe Chapter 3 item 01:
- Uses `_Chapter3Item01UnsafeWriterLLMClient` + `_bundle_with_missing_portfolio_managers()`
- Uses `typed_template_path="typed_template_contract"`
- Asserts `chapter_3.status == "blocked"` (line ~1173)
- Asserts `chapter_3.stop_reason == "missing_required_output_marker"` (line ~1174)
- Asserts `chapter_3.failure_category == "prompt_contract"` (line ~1175)
- Asserts `chapter_3.failure_subcategory == "missing_required_marker"` (line ~1176)
- Asserts `writer:required_output_gap_missing:ch3.required_output.item_01` in chapter issues (line ~1178)
- Asserts `required_output_block:ch3.required_output.item_01` NOT in chapter issues (line ~1182)
- Asserts `result.final_assembly_result.status == "incomplete"` (line ~1185)
- Asserts `result.final_assembly_result.report_markdown is None` (line ~1186)
- Asserts `result.final_assembly_result.chapter7_markdown is None` (line ~1187)
- Asserts `result.report_markdown` raises (line ~1188)

The negative assertion is direct, Chapter 3 item 01 specific, and proves incomplete assembly + absent report markdown. Amendment satisfied.

### 3.3 Cross-check: Controller Amendment 3 — Docs search discovery only (PASS)

**Requirement**: Slice 4 broad search is discovery only. Update only item 01 hard-block statements if they exist.

**Evidence**: Diff shows exactly two narrow changes in `tests/README.md`:
- Line 53: `block` → `render_evidence_gap` in test description for `test_typed_contracts.py`
- Line 63: `zero-provider fact-gap 阻断` → `evidence-gap 降级与 unsafe gap wording 阻断` in `test_runner.py` description

No changes to control docs (`AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`). No changes to root `README.md`. No changes to historical review artifacts. Amendment satisfied.

### 3.4 Cross-check: Controller Amendment 4 — EvidenceAvailability envelope fail-closed (PASS)

**Requirement**: Keep the missing EvidenceAvailability envelope fail-closed. Do not degrade missing contract plumbing to evidence gap.

**Evidence**: 
- `test_chapter_3_missing_typed_availability_blocks_before_provider` — unchanged, still blocks before provider
- `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` — unchanged, still asserts ValueError for completely absent typed availability
- `tests/fund/test_evidence_availability.py` — not in diff, mapping unchanged, `test_ch3_basic_manager_info_required_output_uses_basic_identity_availability` passes independently (1 passed in 0.78s per controller validation)

The distinction between missing reviewed facts (→ evidence gap) and broken contract plumbing (→ fail-closed) is correctly preserved. Amendment satisfied.

### 3.5 Cross-check: Template policy change (PASS)

**Requirement**: Change `ch3.required_output.item_01` from `when_evidence_missing="block"` to `when_evidence_missing="render_evidence_gap"`.

**Evidence**: `docs/fund-analysis-template-draft.md` diff:
- `"when_evidence_missing": "block"` → `"when_evidence_missing": "render_evidence_gap"`
- `missing_evidence_reason` updated to state gap-only output with `缺少已复核证据` and `只能输出证据缺口`

Typed contract test `test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap` asserts:
- `item.when_evidence_missing == "render_evidence_gap"`
- `"缺少已复核证据" in item.missing_evidence_reason`
- `"只能输出证据缺口" in item.missing_evidence_reason`

Item id, ordering, other Chapter 3 items, chapter ids, `must_answer`, `must_not_cover`, preferred lens all preserved. Correct.

### 3.6 Cross-check: Agent runner positive/negative coverage (PASS)

**Positive test** `test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts`:
- Writer called for chapter 3
- Run status `accepted`
- Task status `accepted`, `accepted_draft` and `accepted_conclusion` not None
- `final_assembly_readiness.ready is True`
- `item_01.action == "render_evidence_gap"` (not `"block"`)
- `item_01.availability_status == "missing"`

**Negative test** `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer`:
- Writer called for chapter 3
- Run status `blocked`
- Task `terminal_state == "blocked_prompt_contract"`
- `stop_reason == "missing_required_output_marker"`
- `failure_category == "prompt_contract"`, `failure_subcategory == "missing_required_marker"`
- `"writer:required_output_gap_missing:ch3.required_output.item_01"` in blocked reasons
- `"required_output_block:ch3.required_output.item_01"` NOT in blocked reasons (old block issue classification replaced)

Both tests use `typed_template_path="typed_template_contract"`. The old test name with "blocks_before_provider" was correctly removed. Coverage is complete.

### 3.7 Cross-check: Scope boundaries (PASS)

**Allowed scope respected**: Only `docs/fund-analysis-template-draft.md`, `tests/fund/template/test_typed_contracts.py`, `tests/agent/test_runner.py`, `tests/services/test_fund_analysis_service_llm.py`, `tests/README.md`, and the evidence artifact itself were changed.

**Forbidden scope avoided**: No live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands. No source acquisition policy or fallback changes. No provider default, repair budget, annual-period LLM route, or Docling/parser policy changes. No control-doc updates by implementation worker. No stage/commit/push/PR/merge.

**Existing unrelated diffs not touched**: `AGENTS.md`, `README.md`, `docs/design.md` remain unchanged by this implementation (their pre-existing modifications are unrelated tracked diffs).

### 3.8 Cross-check: No readiness overclaim (PASS)

Evidence file explicitly states release/readiness remains `NOT_READY`. No readiness, MVP-ready, or LLM-path-ready claim is made. EID single-source/no-fallback is preserved. Correct.

### 3.9 Cross-check: Validation results (PASS)

Controller pre-validated with:
- `uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q` → 74 passed
- `uv run ruff check` on touched files → passed
- `git diff --check` → passed

Evidence documents intermediate failures and their resolutions, which increases confidence in the implementation's correctness:
- Agent runner negative selector initially gave false positive due to default fake writer emitting approved gap wording → fixed with targeted unsafe fixture
- Service negative selector initially gave false positive due to default `legacy_contract` policy and default fake writer → fixed with `typed_template_path="typed_template_contract"` and targeted unsafe writer
- Accidental helper patch affected unrelated test → restored and reran successfully

## 4. Accepted Points

| Item | Disposition |
|---|---|
| Template item 01 `block` → `render_evidence_gap` with updated reason | ACCEPT |
| Full assembly positive test with chapters 0-7 | ACCEPT |
| Direct negative service-level unsafe Chapter 3 → incomplete assembly | ACCEPT |
| Discovery-only docs update (2 lines in tests/README.md) | ACCEPT |
| EvidenceAvailability envelope fail-closed preserved | ACCEPT |
| Agent runner positive/negative coverage with correct issue classification | ACCEPT |
| Scope boundaries respected, no forbidden operations | ACCEPT |
| No readiness overclaim, NOT_READY preserved | ACCEPT |

## 5. Residuals

- No live/provider completion, LLM content quality, provider-response classification, additional samples, cleanup, PR, release, or readiness proof is provided by this no-live implementation.
- Historical review artifacts still describe prior item 01 hard-block facts as historical evidence-chain records; not updated (correctly, per scope).
- The `_FakeWriter` in agent tests gained callable action support. This is a test-infrastructure extension scoped to the new tests; it does not affect production behavior.
- Release/readiness remains `NOT_READY`.

## 6. Verdict

VERDICT: **PASS**

The implementation correctly applies the accepted plan and all four controller amendments. Template policy is changed from `block` to `render_evidence_gap` with aligned reason wording. Missing EvidenceAvailability envelope remains fail-closed. Agent runner positive/negative coverage is complete with correct issue classification (`writer:required_output_gap_missing`, not old `required_output_block`). Service final assembly positive test exercises full 8-chapter assembly; negative test directly proves unsafe Chapter 3 item 01 output blocks final assembly and leaves report markdown absent. Docs change is narrow discovery-only (2 lines in tests/README.md). No control docs, source policy, or readiness state was touched. All validation commands pass. Scope boundaries are respected. No readiness overclaim.
