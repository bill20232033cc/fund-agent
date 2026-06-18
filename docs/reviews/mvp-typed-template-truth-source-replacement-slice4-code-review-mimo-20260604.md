# MVP typed template truth-source replacement Slice 4 code review — AgentMiMo

## Review metadata

- Reviewer: AgentMiMo
- Date: 2026-06-04
- Scope: Slice 4 typed consumers regression
- Baseline checkpoint: `202b396 gateflow: accept typed template truth source slice3`
- Handoff supplement: 用户补充修正了完整 review focus（含 5 个私有符号全名和 7 条 review focus），本 artifact 已纳入该补充修正。
- Changed files reviewed:
  - `fund_agent/fund/template/typed_contracts.py` (diff only)
  - `tests/fund/template/test_typed_contracts.py` (diff only)
  - `tests/fund/template/test_chapter_contract_constraints.py` (diff only)
  - `tests/fund/test_evidence_availability.py` (diff only)
  - `tests/services/test_chapter_orchestrator.py` (diff only)
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md`
- Reference artifacts:
  - `AGENTS.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md` (Slice 4 and validation matrix)
  - `docs/reviews/mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-controller-judgment-20260604.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-ds-20260604.md`
  - `docs/reviews/mvp-typed-template-truth-source-replacement-slice3-code-review-mimo-20260604.md`

## Validation reproduced

```text
uv run pytest tests/fund/template/test_typed_contracts.py -q
15 passed in 0.38s

uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py -q
90 passed in 0.64s

uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
171 passed in 0.70s

uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
46 passed in 0.51s

uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py
All checks passed!

git diff --check -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py
exit 0, no output
```

Reviewer-side additional inspections:

```text
# chapter_contract_constraints.py has ZERO source code diff — only test updated
git diff HEAD -- fund_agent/fund/template/chapter_contract_constraints.py
(no output)

# SUPPORTED_LENS_KEYS contains all 7 expected values
SUPPORTED_LENS_KEYS: ('index_fund', 'active_fund', 'bond_fund', 'enhanced_index', 'qdii_fund', 'fof_fund', 'default')

# EvidenceAvailability private symbols verified
_CH2_REQUIREMENT_SPECS ids: ['ch2.must_answer.item_01', ..., 'ch2.required_output.item_07'] (13 total)
_CH3_REQUIREMENT_SPECS ids: ['ch3.requirement.manager_strategy_text_reviewed', ..., 'ch3.required_output.item_06'] (8 total)
_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID: 'ch3.requirement.actual_behavior_reviewed'
_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS: ('ch3.required_output.item_03', 'ch3.required_output.item_04', 'ch3.required_output.item_05')
_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES: ('ch3.requirement.turnover_rate_reviewed', 'ch3.requirement.holdings_snapshot_reviewed', 'ch3.requirement.cross_period_style_evidence_reviewed')
```

## Review Focus Checklist

### Focus 1: Typed consumers use template-doc-projected typed manifest, not old code-authored mapping

**PASS**

Production code change in `typed_contracts.py` is limited to:
- `SUPPORTED_LENS_KEYS` constant (L67-71) — derived from `get_args(LensKey)` → `get_args(literal_group)`, not hardcoded values. `LensKey = FundType | Literal["default"]`, so it flattens `FundType` enum members plus `"default"`.
- `_validate_preferred_lens` guard (L811-812) — `rule.fund_type not in SUPPORTED_LENS_KEYS` → `ValueError`.

No code-authored text/id mapping was re-introduced. The `_CURRENT_TEXT_MAPPING` removal from Slice 3 is preserved. All typed field projection continues to go through `_load_raw_template_contract_manifest()` → `_project_typed_chapter()` from the canonical template JSON.

All consumer tests now assert against typed manifest projection rather than hardcoded strings:
- `test_chapter_contract_constraints.py`: `tuple(item.text for item in typed_by_id[chapter_id].must_answer)` etc.
- `test_evidence_availability.py`: cross-validates `evidence_availability_module._CH2_REQUIREMENT_SPECS` and `_CH3_REQUIREMENT_SPECS` against typed manifest projection.
- `test_chapter_orchestrator.py`: `typed_by_id[2].required_output_items`, `typed_by_id[2].audit_focus`, etc.

### Focus 2: chapter_contract_constraints.py remains no-change public-manifest consumer

**PASS**

- `chapter_contract_constraints.py` has **zero source code diff** — `git diff HEAD` shows no output. Only its test file was updated.
- Test `test_sidecar_wraps_existing_chapter_contract_without_parallel_truth` now asserts dual consistency:
  - `constraint.must_answer == source_by_id[chapter_id].must_answer` (untyped manifest)
  - `constraint.must_answer == tuple(item.text for item in typed_by_id[chapter_id].must_answer)` (typed projection)
  - Same for `must_not_cover`.
- Active_fund overlay tested: `constraints_for_chapter(3, "active_fund")` returns `("default", "active_fund")` slots, both with `must_answer == source_by_id[3].must_answer`.

Conclusion: `chapter_contract_constraints.py` is confirmed as a no-change consumer; default wrappers match both untyped and typed projections; overlays still resolve.

### Focus 3: EvidenceAvailability Ch2/Ch3 private specs cross-validated against projected typed manifest

**PASS**

New test `test_requirement_specs_cross_validate_against_projected_typed_manifest` (test_evidence_availability.py L174-223) validates all 5 required private symbols:

| Symbol | Validation | Result |
|--------|-----------|--------|
| `_CH2_REQUIREMENT_SPECS` | `ch2_spec_ids == ch2_manifest_ids` (exact equality of all 13 requirement ids vs typed manifest Ch2 must_answer + required_output clause/item ids) | PASS |
| `_CH2_REQUIREMENT_SPECS` (subcontract grouping) | `ch2_specs_by_subcontract == ch2_manifest_by_subcontract` (exact equality per subcontract performance/attribution/cost) | PASS |
| `_CH3_REQUIREMENT_SPECS` | `ch3_required_output_ids <= (ch3_base_spec_ids \| set(_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS))` (all Ch3 output ids covered by either base specs or actual-behavior outputs) | PASS |
| `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID` | `in ch3_predicate_requirement_ids` (exists in typed manifest Ch3 must_not_cover clause's `applies_when.requirement_ids`) | PASS |
| `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` | `<= ch3_required_output_ids` (all 3 actual-behavior output ids present in typed manifest Ch3 required_output_items) | PASS |
| `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` | `<= ch3_base_spec_ids` (all 3 dependency requirement ids present in `_CH3_REQUIREMENT_SPECS`) | PASS |

Verified runtime values:
- `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID` = `"ch3.requirement.actual_behavior_reviewed"` — confirmed present in typed manifest `ch3.must_not_cover.item_04.applies_when.requirement_ids`.
- Ch2 subcontract requirement_ids in typed manifest match `_CH2_REQUIREMENT_SPECS` grouping exactly.

### Focus 4: Service typed path regression covers template doc → typed manifest → EvidenceAvailability → writer/auditor/service typed path

**PASS**

`test_typed_contract_path_preserves_independent_body_execution` (test_chapter_orchestrator.py L2087-2151) now validates the full typed pipeline:

1. **template doc → typed manifest**: `typed_manifest = load_typed_template_contract_manifest()` at test start (L2090).
2. **typed manifest → EvidenceAvailability**: `availability_calls` records that `derive_evidence_availability` was called (L2145). Inside the recorder, `availability.require("ch2.required_output.item_01").chapter_id == 2` and `availability.require("ch3.required_output.item_03").status == "unreviewed"` (L2099-2100).
3. **required output ids from typed manifest**: `rows[2].attempts[0].writer_result.prompt.required_output_items == tuple(item.item_id for item in typed_by_id[2].required_output_items)` (L2130-2131). Same for Ch3 (L2133-2134). This replaces the old `startswith("ch2.required_output.")` check with an exact typed manifest equality.
4. **required output text from typed manifest**: `ch3_plan_by_id["ch3.required_output.item_03"].text == typed_by_id[3].required_output_items[2].text` (L2140-2141).
5. **audit_focus from typed manifest**: `auditor.requests[0].audit_focus == typed_by_id[2].audit_focus` (L2147) and `auditor.requests[1].audit_focus == typed_by_id[3].audit_focus` (L2149). This replaces the old hardcoded tuple assertions.

### Focus 5: LensKey runtime guard correctly resolves Slice 3 MiMo M1

**PASS**

- **M1 issue**: `cast(LensKey, _read_required_string(...))` was type-level only; `_validate_preferred_lens` did not check `fund_type` against the LensKey closed set.
- **Fix**: Added `SUPPORTED_LENS_KEYS` constant (L67-71) derived from `get_args(LensKey)`, and `if rule.fund_type not in SUPPORTED_LENS_KEYS: raise ValueError(...)` guard (L811-812) in `_validate_preferred_lens`.
- **Verified content**: `SUPPORTED_LENS_KEYS = ('index_fund', 'active_fund', 'bond_fund', 'enhanced_index', 'qdii_fund', 'fof_fund', 'default')` — all 7 expected values.
- **New test**: `test_preferred_lens_fund_type_literal_is_closed` (test L358-385) injects `fund_type="unsupported_fund"` and asserts `ValueError` with match `"preferred_lens fund_type 不受支持"`.
- **No behavior drift**: The guard runs inside `validate_typed_template_contract_manifest()`, which is called at manifest load time. Valid template JSON passes unchanged; only malformed/invalid fund_type values are now rejected. Existing validation logic (`key != rule.fund_type`, statements check, facets check, priority check) remains unchanged.

### Focus 6: Non-goals unchanged

**PASS**

- Only `typed_contracts.py` (production) and 4 test files were modified.
- No renderer, deterministic analyze/checklist, provider, runtime, Host, Agent, multi-year, score-loop, golden/readiness, PR/release/external state touched.
- Evidence artifact states: "No provider/runtime/live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR, push, or release action was run."

### Focus 7: Tests avoid provider/network/repository/PDF/cache/source helper access

**PASS**

- All tests use `load_typed_template_contract_manifest()` which reads from the in-repo template file.
- No provider mocking, network calls, PDF access, repository calls, or external service dependencies.
- `test_requirement_specs_cross_validate_against_projected_typed_manifest` reads only from typed manifest and `evidence_availability_module` private constants.
- `test_typed_contract_path_preserves_independent_body_execution` uses monkeypatch on local functions, not external services.
- `test_preferred_lens_fund_type_literal_is_closed` constructs a local dataclass and calls validation.

## Findings

### Finding L1: Ch3 base spec coverage gap in cross-validation test

- Severity: LOW
- Location: `tests/fund/test_evidence_availability.py` L221-223
- Description: The test asserts `ch3_required_output_ids <= (ch3_base_spec_ids | set(_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS))` which verifies all Ch3 output ids are covered. However, it does not assert the reverse direction (`ch3_base_spec_ids <= some_expected_set`) or independently verify that non-actual-behavior Ch3 output ids (item_01, item_02, item_06) are in `ch3_base_spec_ids`. The `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` are `item_03/04/05`, which are derived from a different path (actual-behavior aggregation), not from `_CH3_REQUIREMENT_SPECS` base specs. The `<=` check is correct but does not independently verify `item_01`, `item_02`, `item_06` membership in `_CH3_REQUIREMENT_SPECS`.
- Impact: If `_CH3_REQUIREMENT_SPECS` accidentally dropped `ch3.required_output.item_01` or `ch3.required_output.item_02`, the test would still pass as long as they remain in `ch3_required_output_ids` from the typed manifest (the `<=` direction is manifest→spec, not spec→manifest). In practice, the existing Ch3 derivation tests and writer/auditor tests cover this path, so the gap is cosmetic.
- Recommendation: Consider adding `assert ch3_required_output_ids == ch3_base_spec_ids | set(evidence_availability_module._CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS)` for bidirectional coverage, or document the intended asymmetry.

### Residual Slice 3 findings (non-blocking, not addressed by Slice 4)

| Finding | Severity | Status |
|---------|----------|--------|
| M2: Ch2 internal subcontract requirement_ids AND vs OR logic | MEDIUM | Deferred — controller accepted as non-blocking for Slice 3; current data satisfies AND; one-line relaxation if needed |
| DS L1 / MiMo implicit: missing JSON key → KeyError not ValueError | LOW | Deferred — Slice 2 parser catches structural errors first |
| DS L2: orphan missing_evidence_reason (behavior=None, reason non-empty) | LOW | Deferred — no functional impact |
| DS L3 / MiMo L4: double file read in _load_raw_template_contract_manifest | LOW | Deferred — performance only |
| MiMo L1: private path parameter no traversal guard | LOW | Deferred — not exposed in public API |
| MiMo L2: typed_contracts ↔ evidence_availability bidirectional lazy import | LOW | Deferred — works correctly via lazy import |
| MiMo L3: multiple validation paths lack dedicated negative tests | LOW | Partially addressed — M1 fund_type test added in this slice |

## Verdict: PASS

No blocking findings.

Slice 4 implementation correctly validates all typed consumers against the template-doc-projected typed manifest. The `SUPPORTED_LENS_KEYS` runtime guard resolves Slice 3 M1. `chapter_contract_constraints.py` is confirmed as a no-change public-manifest consumer with zero source diff; its test proves default wrappers match both untyped and typed projections and active_fund overlay resolves. EvidenceAvailability Ch2/Ch3 private specs (`_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES`) are cross-validated against the projected typed manifest with exact equality and subset checks. The Service typed path regression covers the full template doc → typed manifest → EvidenceAvailability → writer/auditor pipeline including required output ids/text and audit_focus from typed manifest. No provider, network, repository, PDF, cache, or source helper access in tests. All 171 consumer tests pass, 46 typed consistency tests pass, ruff clean, no whitespace errors.
