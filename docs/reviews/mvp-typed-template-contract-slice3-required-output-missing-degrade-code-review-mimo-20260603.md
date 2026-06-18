# MVP typed template contract Slice 3 required-output missing/degrade code review — MiMo

## Worker Self-Check

- Role: AgentMiMo code review worker only; not controller.
- Gate: `MVP typed template contract Slice 3 required-output missing/degrade implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Truth/read set: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-controller-judgment-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-implementation-evidence-20260603.md`, and current diff.
- Actions intentionally not taken: no file edit, no commit, no push, no PR, no live provider probe, no provider/runtime/default change.

## Review Focus Checklist

| Focus area | Expected behavior | Verdict |
|---|---|---|
| `RequiredOutputItem.when_evidence_missing` integrated additively into writer input/preflight/adapter using `EvidenceAvailability` | Additive fields on `ChapterWriterInput` and `ChapterWriterPrompt`; default path unchanged when typed items not supplied | PASS |
| Four behaviors precise: `render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block` | Each behavior maps to a distinct action with specific prompt instruction and validation | PASS |
| `render_evidence_gap` and `render_minimum_verification_question` satisfy missing evidence only through approved gap/degrade wording | `_required_output_degrade_issues` checks segment contains approved phrases; marker without degrade phrase blocked as `missing_required_output_marker` | PASS |
| `delete_if_not_applicable` requires `not_applicable` plus typed reason | `_required_output_action` validates `status != "not_applicable" or item.missing_evidence_reason is None` raises; `_validate_required_output_plan` re-checks | PASS |
| `block` fail-closes before LLM client/provider success path and does not create deterministic fallback | `_required_output_preflight_issues` generates `missing_required_facts` issue; `write_chapter` checks issues before calling client | PASS |
| Current marker policy, missing marker strictness, required_output marker parsing not relaxed | Existing `_required_output_marker_issues` still runs; typed path uses same marker format; `test_existing_missing_marker_contract_remains_strict` verifies | PASS |
| EvidenceAvailability additions limited and same-source | Only `ch3.required_output.item_01` added to `_RequirementSpec` and `EvidenceRequirementId`; mapped to `structured.basic_identity` | PASS |
| No direct document/PDF/cache/source helper, Service, Host, provider, runtime/default, live probe, Agent runtime/tool-loop, score/golden/readiness changes | Diff touches only `chapter_writer.py`, `evidence_availability.py`, `typed_contracts.py`, tests and READMEs | PASS |

## Findings

### F1 — Non-blocking: `ch3.required_output.item_01` has availability but no `when_evidence_missing` behavior

**Severity**: Non-blocking observation.
**Location**: `fund_agent/fund/template/typed_contracts.py:810-821` (`_required_output_missing_behavior`), `fund_agent/fund/evidence_availability.py:228-233` (`_RequirementSpec`).

**Detail**: `ch3.required_output.item_01` (基金经理基本信息) was added to `EvidenceRequirementId` and `_RequirementSpec` in this slice, but `_required_output_missing_behavior()` and `_required_output_missing_reason()` do not map it. If `basic_identity` availability is `missing`/`unavailable`/`unreviewed` at runtime, `_required_output_action()` will raise `ValueError` because `when_evidence_missing` is `None` while status is in `_MISSING_EVIDENCE_STATUSES`.

**Why non-blocking**: This is intentional fail-closed behavior. Item_01 maps to `structured.basic_identity`, which is always `available` when the bundle is populated. The Slice 2 controller judgment explicitly assigned item_01 coverage to Slice 3. The current approach means: if basic identity evidence is somehow absent, the writer fails closed rather than silently degrading. This is correct for a required output that has no approved degrade wording.

**Recommendation for future wiring**: If item_01 should have a degrade path (e.g., `render_evidence_gap`), add explicit behavior and reason in a future slice. If it should remain block-on-absence, document this as intentional in the typed contract manifest.

### F2 — Non-blocking: `_required_output_segment_contains` uses substring matching for degrade phrase verification

**Severity**: Non-blocking observation.
**Location**: `fund_agent/fund/chapter_writer.py:1696-1722`.

**Detail**: The degrade phrase check uses `any(phrase in segment for phrase in phrases)`, which is a substring match. This means a phrase like `证据不足` would match inside `证据不足以支撑该结论` even if the surrounding sentence makes a positive assertion (e.g., `证据不足，但未见明显不一致`).

**Why non-blocking**: The Slice 0 calibration artifact (section 3 `evidence_gap_statement`) explicitly defines the allowed-context matching spec for future Slice 4 programmatic audit. The writer degrade check here is a safety net on the writer output, not the auditor. The auditor's `must_not_cover` enforcement (Slice 4 scope) will handle the polarity/context issue. Current `_GAP_OUTPUT_PHRASES` are narrow enough that false positives from substring matching are unlikely in practice. The test `test_required_output_missing_evidence_renders_gap_marker` verifies the happy path.

**Recommendation**: Slice 4 should consider whether the writer degrade check needs polarity-aware matching or whether it can remain a coarse safety net with the auditor owning precise enforcement.

### F3 — Non-blocking: `cast(EvidenceRequirementId, item.item_id)` bypasses static type checking

**Severity**: Non-blocking observation.
**Location**: `fund_agent/fund/chapter_writer.py:984`.

**Detail**: `cast(EvidenceRequirementId, item.item_id)` tells the type checker that `item.item_id` is a valid `EvidenceRequirementId` without runtime validation. If a `RequiredOutputItem` has an `item_id` that is not in the `EvidenceRequirementId` literal set, `evidence_availability.require()` will raise `ValueError` at runtime, which is caught by the except clause.

**Why non-blocking**: The `cast` is guarded by a `try/except ValueError` that converts the error into a meaningful message. The typed contract loader validates item ids at construction time, and the writer validates chapter membership. The runtime path is fail-closed. The alternative (using a Protocol or runtime isinstance check) would add complexity without safety benefit.

### F4 — Non-blocking: `_required_output_action` returns `"block"` as implicit default for unknown `MissingEvidenceBehavior` values

**Severity**: Non-blocking observation.
**Location**: `fund_agent/fund/chapter_writer.py:991-1017` (`_required_output_action`).

**Detail**: The function uses `if/elif` chains and falls through to `return "block"` for any `behavior` value not explicitly handled. If a future `MissingEvidenceBehavior` variant is added without updating this function, it would silently default to `block`.

**Why non-blocking**: `MissingEvidenceBehavior` is a `Literal` type defined in `typed_contracts.py`. The `_validate_required_output_items` function in `typed_contracts.py:1136` already validates that `when_evidence_missing` is from the supported set. Adding a new variant would require updating both the Literal type and the validation, which would surface as a test failure. The block default is the correct fail-closed behavior.

## Validation

### Validation run

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py tests/fund/template/test_typed_contracts.py -q
```

Result: `57 passed in 0.76s`.

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/evidence_availability.py fund_agent/fund/template/typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md
```

Result: exited `0`.

### Validation intentionally not run

- Live provider probe: not authorized in this gate.
- Full project pytest (`uv run pytest`): scope limited to touched files per gate classification.
- Coverage report: single-file coverage targets are deferred to controller judgment.

## Non-Goals Preserved

Confirmed from diff analysis:

- No provider/runtime/default/budget/endpoint changes.
- No live PASS-only probe.
- No deterministic fallback and no stdout partial report behavior.
- No Service, Host, CLI, quality gate, final judgment, score-loop, golden/readiness or promotion changes.
- No template truth replacement and no `docs/fund-analysis-template-draft.md` edit.
- No Agent runtime/tool-loop implementation.
- No multi-year annual evidence runtime loading.
- No direct repository/PDF/cache/source-helper access from writer or availability code.
- No `extra_payload` business params.
- No edits to `docs/design.md`, `docs/current-startup-packet.md`, or `docs/implementation-control.md`.

## Residual Risks

| Risk | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|
| Item_01 has no degrade path; basic_identity absence would block the chapter | Medium | Low (basic_identity is always populated in current bundle) | Fail-closed is correct default; explicit behavior can be added in future wiring | Future Service/Agent wiring gate |
| Degrade phrase substring matching could accept mixed-polarity output | Medium | Low (narrow phrase set; auditor owns polarity enforcement in Slice 4) | Slice 4 must own polarity-aware enforcement; writer check remains coarse safety net | Slice 4 implementation |
| Writer prompt exposes `availability_status` and `action` to LLM | Low | Medium (LLM could attempt to game the status) | Prompt instruction is deterministic and constraining; LLM output is post-validated by degrade check | Acceptable for current slice; future prompt hardening if needed |
| `_required_output_preflight_issues` re-calls `_required_output_evidence_plan` which re-derives the full plan | Low | Low (plan derivation is pure and cheap) | Could cache plan in `build_chapter_prompt` and pass to preflight; current approach is correct | Performance optimization if needed |

## Blocking Findings

None.

## Conclusion

PASS-WITH-RISKS. The implementation correctly integrates `RequiredOutputItem.when_evidence_missing` into the writer path using `EvidenceAvailability` with all four behaviors precise and fail-closed. No blocking findings. Four non-blocking observations documented above with assigned owners for future slices.
