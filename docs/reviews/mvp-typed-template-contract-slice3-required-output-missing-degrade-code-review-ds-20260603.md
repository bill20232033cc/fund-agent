# MVP typed template contract Slice 3 required-output missing/degrade code review (DS)

## Worker Self-Check

- Role: AgentDS code review worker only; not controller and not implementation worker.
- Gate: `MVP typed template contract Slice 3 required-output missing/degrade implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Output path: `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-code-review-ds-20260603.md`.
- Actions intentionally not taken: no source edits, no tests edits, no commit, no push, no PR, no live provider probe, no provider/runtime/default/budget/endpoint changes, no Agent runtime/tool-loop implementation, no score/golden/readiness changes.

## Validation Executed

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py tests/fund/template/test_typed_contracts.py
# 57 passed in 0.44s

uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/fund/evidence_availability.py fund_agent/fund/template/typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py
# All checks passed!

git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/evidence_availability.py fund_agent/fund/template/typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md
# exit 0
```

Validation intentionally not run: full project test suite (out of scope for focused Slice 3 review; 57 targeted tests are sufficient), live provider probe (explicitly not authorized), import isolation test for `chapter_writer.py` new imports (new imports are all Fund-layer: `evidence_availability` and `typed_contracts`; existing import isolation test `test_writer_does_not_import_repository_source_service_dayu_or_openai` continues to pass).

## Review Result

**NO BLOCKING FINDINGS.** All six review focus areas verified, five non-blocking observations recorded below.

---

## Findings

### Non-Blocking

#### N1: `_required_output_evidence_plan()` computed twice in write path

`fund_agent/fund/chapter_writer.py:903-904` (`_required_output_preflight_issues`) and `fund_agent/fund/chapter_writer.py:616` (`build_chapter_prompt`) each call `_required_output_evidence_plan(input_data)` independently.

**Assessment**: The plan is a pure deterministic computation over frozen dataclass inputs, so double evaluation is a minor efficiency concern, not a correctness issue. The plan shape is identical both times. Acceptable as non-blocking; future refactor could cache the plan in `build_chapter_prompt` and thread it into preflight.

#### N2: `ch3.required_output.item_01` has no `when_evidence_missing` — would crash on missing basic_identity

`fund_agent/fund/template/typed_contracts.py:787-788` returns `None` for `ch3.required_output.item_01` because basic manager identity is structurally always available. If basic_identity facts were somehow absent, `_required_output_action()` at `fund_agent/fund/chapter_writer.py:370` would raise `ValueError("typed required output 缺证但未声明 when_evidence_missing")`.

**Assessment**: Basic identity is a structurally guaranteed fact in current `ChapterFactProjection` — it has no `extraction_mode="missing"` path. This is a "can't happen" scenario in the current system. The behavior is fail-closed (ValueError), not fail-open. Acceptable as non-blocking; if future evidence loading makes basic_identity optionally absent, a `when_evidence_missing` should be added.

#### N3: `_required_output_segment_contains` segment boundary is marker-greedy

`fund_agent/fund/chapter_writer.py:1726-1731` delimits segments by finding the next `<!-- required_output:` marker. If the LLM were to reorder markers or output a degrade phrase in a different segment, the check would miss.

**Assessment**: The prompt instruction per `_required_output_prompt_instruction()` ties each marker to its required degrade phrase explicitly (e.g., "必须输出该 marker，但只能写证据缺口"). The LLM is instructed to put the gap/verification phrase immediately after the marker. The segment model matches the prompt contract. Acceptable as non-blocking.

#### N4: `_required_output_degrade_issues` stop_reason reuses `missing_required_output_marker`

`fund_agent/fund/chapter_writer.py:1680-1698` classifies gap/verification degrade failures with `stop_reason="missing_required_output_marker"`. The issue_id prefix distinguishes the cases (`writer:required_output_gap_missing:` / `writer:required_output_verification_missing:`), but the stop reason category is the same as for plain missing markers.

**Assessment**: This follows the documented pattern (Slice 2 residual explicitly noted `block` reuses `missing_required_facts`). The issue_id is diagnostic and the stop_reason is stable for Service-layer routing. Acceptable as non-blocking; future taxonomy refinement could introduce `missing_required_output_degrade` if Service needs distinct routing.

#### N5: Gap/verification reason is optional in `_required_output_prompt_instruction` but always set in factory

`fund_agent/fund/chapter_writer.py:400-408` falls back to `'typed reason absent'` if `item.missing_evidence_reason` is None for gap/verification actions. The typed contracts factory at `fund_agent/fund/template/typed_contracts.py:733-746` always sets reasons for Ch3 items 02-06.

**Assessment**: The fallback is a safe diagnostic string, not a crash. Current factory always populates reasons. If future code constructs `RequiredOutputItem` without a reason for gap/verification, the prompt instruction degrades gracefully to `'typed reason absent'`. Acceptable; validation in `_validate_required_output_items` could optionally require reasons for all non-None `when_evidence_missing` values in a future hardening gate.

---

## Review Focus Area Verification

### 1. Additive typed writer input integration

`ChapterWriterInput.typed_required_output_items` (default `()`) and `ChapterWriterInput.evidence_availability` (default `None`) are additive. `build_chapter_prompt()` calls `_required_output_evidence_plan()` only when typed items are present; default path returns empty plan and falls through to existing `contract.required_output_items` behavior at `fund_agent/fund/chapter_writer.py:1493-1494`.

`_availability_for_required_output()` uses `evidence_availability.require(cast(EvidenceRequirementId, item.item_id))` with runtime ValueError for unknown ids. The `cast` is type-level only.

**Verdict**: PASS.

### 2. Four behaviors precision

- **render_evidence_gap**: `_required_output_action()` returns `"render_evidence_gap"` for matching behavior. `_required_output_degrade_issues()` checks output contains ≥1 of `_GAP_OUTPUT_PHRASES` (8 Chinese gap phrases). Prompt instruction requires gap phrase and forbids positive conclusion. Test: `test_required_output_missing_evidence_renders_gap_marker`.
- **render_minimum_verification_question**: Same structure with `_VERIFICATION_OUTPUT_PHRASES` (5 verification phrases). Prompt requires "下一步最小验证问题" or equivalent. Test: `test_required_output_minimum_verification_question_satisfies_missing_evidence`.
- **delete_if_not_applicable**: Requires `status == "not_applicable"` AND `missing_evidence_reason is not None` at `_required_output_action()` line 373. Also validated at plan level in `_validate_required_output_plan()` line 436. Deleted items excluded from `required_output_items` in `_prompt_required_output_marker_items()` line 1538. Test: `test_required_output_delete_if_not_applicable_requires_typed_reason`.
- **block**: Returns `"block"` as fallthrough in `_required_output_action()`. `_required_output_preflight_issues()` generates `writer:required_output_block:<item_id>` issues that `_preflight_issues()` collects before LLM client call. `write_chapter()` preflight blocks with `status="blocked"`, `stop_reason="missing_required_facts"`, `draft=None`. No deterministic fallback. Test: `test_required_output_block_stops_before_provider_success_path` verifies `client.requests == []`.

**Verdict**: PASS.

### 3. Current marker policy not relaxed

`test_existing_missing_marker_contract_remains_strict()` verifies `<!-- missing:{reason} -->` still fails as `llm_contract_violation`. `_required_output_marker_issues()` still called in `_draft_from_llm_response()` at line 1529. Default path still uses `contract.required_output_items` as marker items. Typed path uses stable ids like `ch3.required_output.item_05` via `_prompt_required_output_marker_items()`.

`_required_output_marker_issues()` at line 1646-1680 checks markers against `prompt.required_output_items` which is populated correctly for both paths. Typed items excluded from this check only when `action == "delete"`.

**Verdict**: PASS.

### 4. EvidenceAvailability additions limited and same-source

`evidence_availability.py` changes: one new literal `"ch3.required_output.item_01"` added to `EvidenceRequirementId` (line 57); one new `_RequirementSpec` for `ch3.required_output.item_01` mapped to `("structured.basic_identity",)` (lines 228-232). No new imports. No repository/PDF/cache/source-helper/Service/Host/provider access.

`chapter_writer.py` new imports: `evidence_availability` and `typed_contracts` — both Fund-layer. No Service/Host/provider/runtime/default/live-probe/Agent-runtime/tool-loop/score/golden/readiness imports.

**Verdict**: PASS.

### 5. Tests and README sufficient, no overclaim

Tests added (all passing):
- `test_required_output_missing_evidence_renders_gap_marker` — gap via item_05
- `test_required_output_delete_if_not_applicable_requires_typed_reason` — delete guard
- `test_required_output_minimum_verification_question_satisfies_missing_evidence` — verification via item_06
- `test_required_output_block_stops_before_provider_success_path` — block via Ch2 item_01
- `test_writer_prompt_contains_typed_required_output_ids_not_freeform_fallbacks` — stable ids, no fallback
- `test_existing_missing_marker_contract_remains_strict` — marker strictness preserved
- `test_ch3_basic_manager_info_required_output_uses_basic_identity_availability` — Slice 2 residual

READMEs: `fund_agent/fund/README.md` documents `when_evidence_missing` behavior per chapter, writer typed path, and Ch3 basic manager info. `tests/README.md` updates test descriptions. No overclaim of future features as current fact.

**Verdict**: PASS.

### 6. Non-goals preserved

Diff confirms no changes to: provider/runtime/default/budget/endpoint/config, live probe, deterministic fallback, stdout partial report, Service/Host/provider/Agent runtime/tool-loop, score/golden/readiness, template truth, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, multi-year evidence runtime.

**Verdict**: PASS.

---

## Residual Risks (Non-Blocking)

| Risk | Severity | Owner |
|---|---|---|
| Typed path is additive and only active with explicit caller wiring; no Service/Agent integration yet | Low — explicit design constraint | Slice 7 Service facade wiring gate |
| `block` reuses `missing_required_facts` stop reason; future Service routing may need finer-grained distinction | Low — issue_id already distinct | Future Service routing refinement |
| `delete_if_not_applicable` reason-guarded but broad template usage awaits future typed wiring of item-level applicability predicates | Low — explicitly deferred | Future template contract wiring gate |
| `_required_output_segment_contains` segment model assumes marker ordering matches prompt instruction; adversarial LLM output reordering could bypass degrade check | Low — prompt contract makes this explicit; programmatic audit still catches missing markers | Future audit hardening |
| `ch3.required_output.item_01` has no `when_evidence_missing` — structurally safe now, but would crash if basic_identity becomes optionally absent | Low — current projection guarantees basic_identity availability | Future evidence loading gate |

---

## Verdict

**PASS — NO BLOCKING FINDINGS.**

The implementation adds typed `RequiredOutputItem.when_evidence_missing` behavior to `ChapterWriterInput` / `build_chapter_prompt()` / preflight as an additive path. Four behaviors (`render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block`) are correctly implemented with precise guard conditions. Current marker policy, missing marker strictness, and required_output marker parsing are preserved. `EvidenceAvailability` additions are limited to the Slice 2 residual (`ch3.required_output.item_01`) and remain same-source. Tests cover all four behaviors plus marker strictness and stable id usage; READMEs are accurate and do not overclaim. All 57 targeted tests pass, ruff is clean, and non-goals (provider/runtime/Agent/score/golden/readiness) are preserved.

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
