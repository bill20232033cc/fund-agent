# MVP typed template contract Slice 7 Service Facade Wiring Re-Review — MiMo

## Reviewer

- Role: AgentMiMo, code review worker only.
- Gate: `MVP typed template contract Slice 7 Service Facade Wiring Behind Explicit Typed Path implementation gate`.
- Follow-up: re-review after blocking finding F1 fix.
- Prior review: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-code-review-mimo-20260603.md`
- Fix evidence: `docs/reviews/mvp-typed-template-contract-slice7-service-facade-wiring-fix-evidence-20260603.md`
- Sources read: prior review, fix evidence, full updated diff, touched source/test files.
- Actions intentionally not taken: no source code edit, no commit, no push, no PR.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/services/test_execution_contract.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | **178 passed** (was 177; +1 new test) |
| `uv run ruff check fund_agent/services tests/services tests/ui` | **All checks passed** |
| `git diff --check` | **Passed (no whitespace errors)** |

## Review Point Verification

### 1. F1 blocker fixed — typed_required_output_items wired to writer — PASS

Fix adds `_typed_required_output_items()` helper (chapter_orchestrator.py) that:

- Delegates to `_typed_chapter_contract()` which calls `get_typed_chapter_contract(chapter_id)`.
- Returns `typed_contract.required_output_items` when on typed path, `()` on legacy path.
- Is called at both writer invocation sites and passed as `typed_required_output_items=` to `build_chapter_writer_input()`.

Activation path verified:

1. Orchestrator → `build_chapter_writer_input(typed_required_output_items=..., evidence_availability=...)`
2. → `ChapterWriterInput.typed_required_output_items` populated
3. → `build_chapter_prompt()` → `_required_output_evidence_plan()` → computes `RequiredOutputEvidencePlan` for each item using `EvidenceAvailability`
4. → `ChapterWriterPrompt.required_output_evidence_plan` populated
5. → Writer prompt template renders gap markers / block instructions per item action

The Slice 3 `when_evidence_missing` behaviors (`render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block`) are now activatable through the Service facade.

### 2. Initial and repair paths both pass typed_required_output_items — PASS

- **Initial path** (line 1081-1091): `build_chapter_writer_input()` with `typed_required_output_items=_typed_required_output_items(chapter_id, typed_inputs=typed_inputs)` and `evidence_availability=_typed_evidence_availability(typed_inputs)`.
- **Repair path** (line 1275-1289): same parameters passed to `build_chapter_writer_input()` during regenerate.

Both paths use the same `_typed_required_output_items()` helper, ensuring consistent typed behavior across attempts.

### 3. Legacy path does not activate typed required-output behavior — PASS

`_typed_required_output_items()` calls `_typed_chapter_contract()` which returns `None` when `typed_inputs is None` (legacy path). The helper then returns `()`. In `chapter_writer.py:914-916`, `_required_output_evidence_plan()` checks `typed_items = input_data.typed_required_output_items; if not typed_items: return ()`. Legacy path produces empty plan; no typed behavior activates.

### 4. Prior accepted behaviors preserved — PASS

| Behavior | Status | Evidence |
|---|---|---|
| Independent body execution | Preserved | Test verifies Ch1 timeout does not skip Ch2/Ch3; `skipped_chapter_ids == ()`; no `dependency_missing` on later chapters. |
| `audit_focus` wiring | Preserved | Test verifies auditor receives `audit_focus` tuples for Ch2 `(r_abc, evidence_anchors)` and Ch3 `(manager_consistency, evidence_anchors)`. |
| Explicit `typed_template_path` | Preserved | No changes to execution_contract.py; cross-type validation unchanged. |
| Default `analyze`/`checklist` | Preserved | `test_default_analyze_unchanged_with_typed_contract_modules_present` unchanged and passing. |
| Host opacity | Preserved | No Host files touched; `host_context` only used for cancel/phase events. |
| Provider/runtime non-goals | Preserved | No provider, config, default, timeout, or runtime changes. |

### 5. New blocking findings — NONE

No new blocking findings identified.

**Non-blocking observations:**

- `TypedTemplatePathMode` Literal remains duplicated in `chapter_orchestrator.py` and `execution_contract.py` (style note S1 from prior review, still non-blocking).
- Test helper `_required_item_from_prompt_payload()` and `_required_line_text()` were added to handle typed item id format in test assertions; these are test-only helpers and do not affect production code.
- The test assertion `rows[2].status == "failed"` (Ch2) confirms that typed required-output items with missing evidence cause writer failure through the facade, which is the expected `block` or `render_evidence_gap` → auditor-blocked behavior.

## Summary

The blocking finding F1 is fully resolved. `_typed_required_output_items()` correctly extracts items from `TypedChapterContract` and passes them to `build_chapter_writer_input()` in both initial and repair paths. Legacy path remains inactive. Slice 3's `RequiredOutputItem.when_evidence_missing` behavior is now activatable through the Service facade. All prior accepted behaviors preserved. 178 tests pass, ruff clean, no whitespace errors. No new blocking findings.

## Conclusion

Gate acceptance condition from prior review is satisfied. No remaining blockers for Slice 7 acceptance.

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
