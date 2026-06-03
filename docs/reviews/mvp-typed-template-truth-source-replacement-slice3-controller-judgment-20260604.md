# MVP typed template truth-source replacement Slice 3 controller judgment

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 3, typed contracts project from template JSON, remove code-authored typed truth
- Controller decision date: 2026-06-04
- Plan checkpoint: `266e18f gateflow: accept plan for typed template truth source replacement`
- Slice 1 checkpoint: `3c2b237 gateflow: accept typed template truth source slice1`
- Slice 2 checkpoint: `0263bc2 gateflow: accept typed template truth source slice2`

## Scope accepted for this slice

Slice 3 is limited to making `typed_contracts.py` project all typed dataclass fields from the same `TEMPLATE_CONTRACT_MANIFEST_JSON` canonical block used by `contracts.py`:

- Remove all code-authored typed truth: `_CURRENT_TEXT_MAPPING` (~300 lines), `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, `_CH3_STYLE_EVIDENCE_UNREVIEWED`, `_required_output_missing_behavior()`, `_required_output_missing_reason()`, `_build_internal_subcontracts()`, `_must_not_cover_predicate()`, `_must_not_cover_allowed_contexts()`, `_assert_exact_text_mapping()`, `_project_chapter()` and its four `_project_*` helpers.
- Add `_load_raw_template_contract_manifest()` that reads and parses the canonical JSON via Slice 2 parser helpers.
- Add `_project_typed_chapter()` and sub-projectors that construct typed dataclasses from raw JSON fields with strict type/shape validation.
- Add JSON reader helpers (`_read_required_string`, `_read_mapping_array`, `_read_string_array`, `_read_int_array`, `_read_required_int`, `_read_optional_int`, `_read_required_bool`, `_read_optional_string`) for fail-closed field extraction.
- Add `_known_evidence_requirement_ids()` with lazy import of `evidence_availability._KNOWN_REQUIREMENT_IDS` frozenset guard.
- `source_manifest` parameter reduced to compatibility validation only: stale/different → `ValueError`; `None` → skip check; never used to populate typed fields.
- Add validation: conditional must_not_cover must have allowed_contexts (and vice versa); evidence predicate requirement_ids validated against strict guard; Ch2 internal subcontract requirement_ids validated against both chapter clause/item ids and evidence requirement ids; missing evidence behavior must have typed reason.
- Keep typed dataclasses, public API, closed-set Literal constants, public chapter id guard, Ch2 internal subcontract validation, Ch0/Ch7 dependency validation, audit_focus validation, Ch3 evidence predicate validation, required output missing behavior/reason validation.
- Add 6 new tests: code-authored truth symbol absence, exact JSON→typed field matching, stale source_manifest fail-closed, JSON change drives typed projection, unknown requirement id fail-closed, malformed typed values fail-closed.

The slice does not change `docs/fund-analysis-template-draft.md`, `contracts.py`, `__init__.py`, README/design/control/startup docs, renderer, Service, Host/Agent runtime, provider/runtime budgets, live probe, multi-year runtime, score-loop, golden/readiness state, PR state, or release state.

## Implementation evidence reviewed

Reviewed implementation artifact:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`

Reviewed changed files:

- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`

Controller-side validation reproduced:

```text
uv run pytest tests/fund/template/test_typed_contracts.py -q
14 passed

uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
45 passed

uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py
All checks passed!

git diff --check -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py fund_agent/fund/template/__init__.py docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md
exit 0, no output
```

## Review results

Independent review artifacts:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-mimo-20260604.md`

Review verdicts:

- AgentDS: `PASS`, 0 BLOCKING, 0 HIGH, 0 MEDIUM, 3 LOW.
- AgentMiMo: `PASS-WITH-RISKS`, 0 BLOCKING, 0 HIGH, 2 MEDIUM, 4 LOW.

Both reviewers independently confirmed:
- All code-authored typed truth symbols removed; typed fields project exclusively from template JSON.
- `source_manifest` reduced to compatibility validation only, does not populate typed fields.
- Malformed template inputs fail closed across all checked paths.
- Public chapter ids 0-7, Ch0→Ch7 dependency, Ch2-only internal subcontracts preserved.
- No provider/runtime/Agent/score/golden/readiness intrusion.
- 45 tests pass (14 typed + 31 untyped), ruff clean, no whitespace errors.

## Controller disposition

### MEDIUM findings

**M1 (MiMo): preferred_lens fund_type 缺少 LensKey 闭集运行时校验**

Accepted as non-blocking for Slice 3. `cast(LensKey, ...)` is type-level only, but:
- The template JSON is authored truth, not untrusted user input.
- `_validate_preferred_lens` already checks `key != rule.fund_type` (dict key vs fund_type field consistency), catching mismatches between JSON keys and fund_type values.
- An invalid fund_type literal would be stored in the dataclass but downstream consumers (`resolve_preferred_lens`) would encounter it as an unrecognized key.
- Added to Slice 4 punch list: add `rule.fund_type not in get_args(LensKey)` guard in `_validate_preferred_lens`.

**M2 (MiMo): Ch2 internal subcontract requirement_ids AND vs OR 逻辑**

Accepted as non-blocking for Slice 3. The AND logic (must be in both `known_chapter_requirement_ids` AND `known_evidence_requirement_ids`) is consistent with the accepted plan's strict coupling design: Ch2 internal subcontract clause/item ids are a subset of EvidenceRequirementId by construction. Current data satisfies this constraint and all tests pass. If future slices need to relax this to OR, the change is a one-line guard relaxation, not a structural refactor.

### LOW findings (all accepted as non-blocking)

- **DS L1 / MiMo (implicit)**: Missing JSON key → `KeyError` not `ValueError`. Slice 2 parser catches structural errors first; KeyError is still fail-closed.
- **DS L2**: Orphan `missing_evidence_reason` (behavior=None, reason non-empty) passes validation. No functional impact; orphan data is not consumed.
- **DS L3 / MiMo L4**: Double file read in `_load_raw_template_contract_manifest`. Performance-only, no correctness impact.
- **MiMo L1**: Private `path` parameter no traversal guard. Not exposed in public API; default path is a constant.
- **MiMo L2**: `typed_contracts ↔ evidence_availability` bidirectional lazy import. Works correctly; lazy import prevents module-level cycle.
- **MiMo L3**: Several validation paths lack dedicated negative tests. Covered indirectly by Slice 2 parser validation; can be added in Slice 4.

No Slice 3 fix loop is required.

## Scope check

Accepted staged scope for the Slice 3 checkpoint is limited to:

- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-implementation-evidence-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-mimo-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-controller-judgment-20260604.md`

Unrelated untracked artifacts in the workspace remain outside this checkpoint and must not be staged by this gate.

## Accepted / deferred distinction

Accepted in Slice 3:

- `typed_contracts.py` no longer contains any code-authored stable id/text mapping, audit focus, missing behavior/reason, Ch2 internal subcontract truth, or Ch3 evidence predicate truth.
- All typed dataclass fields project from the canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block via `_load_raw_template_contract_manifest()`.
- `source_manifest` parameter is compatibility validation only; stale input fail-closed.
- Malformed template JSON fail-closed across all typed projection and validation paths.
- Public chapter ids 0-7, Ch0→Ch7 dependency, Ch2-only internal subcontracts (performance/attribution/cost) preserved.
- 6 new tests cover code-authored truth removal, JSON→typed exact projection, stale source_manifest, JSON-driven projection, unknown requirement id, and malformed typed values.
- Slice 3 evidence and review artifacts are accepted.

Still deferred to Slice 4 in this same gate:

- Typed consumer regression: verify all typed consumers (renderer, audit, deterministic analyze/checklist, `--use-llm` path) produce identical output after truth source change.
- M1 fix: add LensKey runtime guard in `_validate_preferred_lens`.
- Additional negative tests for validation edge paths.
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, and `tests/README.md` synchronization.

Explicit non-goals remain deferred:

- Agent runtime or tool-loop implementation.
- Provider/default/runtime budget changes or live probe.
- Multi-year evidence runtime.
- Score-loop.
- Ch2 public split.
- Deterministic default behavior changes.
- Golden/readiness/release/PR external-state changes.
- Phaseflow stabilization.

## Controller verdict

**ACCEPT Slice 3.**

The Slice 3 implementation is correct, independently reviewed by two reviewers with no blocking findings, validated with 45 passing tests, and scope-contained. It may be committed as a local accepted checkpoint for Slice 3 only. This does not accept the full truth-source replacement gate and does not authorize Slice 4, phaseflow, real LLM smoke, provider/runtime work, or Agent runtime implementation.
