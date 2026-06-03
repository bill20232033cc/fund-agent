# MVP typed template truth-source replacement Slice 4 implementation evidence

## Scope

- Gate: `MVP typed template truth-source replacement gate`
- Slice: Slice 4 typed consumers regression
- Baseline checkpoint: `202b396 gateflow: accept typed template truth source slice3`
- Role: implementation worker, not controller

## Changes

- Added `LensKey` closed-set runtime validation in `fund_agent/fund/template/typed_contracts.py` via `SUPPORTED_LENS_KEYS` and `_validate_preferred_lens`.
- Added targeted negative regression for unsupported `preferred_lens.fund_type` in `tests/fund/template/test_typed_contracts.py`.
- Strengthened `tests/fund/template/test_chapter_contract_constraints.py` to prove default sidecar wrappers match both the parsed untyped manifest and typed manifest projection, while overlays still resolve.
- Added `EvidenceAvailability` cross-validation in `tests/fund/test_evidence_availability.py` for `_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, and `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` against the projected typed manifest.
- Strengthened `tests/services/test_chapter_orchestrator.py` so the explicit typed Service path checks real typed manifest projection through `EvidenceAvailability`, writer required output ids/text, and auditor `audit_focus`.

## Preserved behavior

- `chapter_contract_constraints.py` remains a no-change public-manifest consumer; only its tests were updated.
- Same-source availability, Ch2 block, Ch3 gap/minimum-verification behavior, Ch3 typed must-not-cover issue id, audit_focus semantic-only LLM input, and Service explicit typed path wiring remain covered by the existing targeted suites.
- No provider/runtime/live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR, push, or release action was run.

## Validation

Targeted tests changed:

```text
uv run pytest tests/fund/template/test_typed_contracts.py -q
15 passed in 0.83s

uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py -q
90 passed in 1.12s
```

Required Slice 4 consumer suite:

```text
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
171 passed in 1.50s
```

Typed template consistency:

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
46 passed in 1.16s
```

Static quality:

```text
uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py
All checks passed!

git diff --check -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md
exit 0, no output

rg -n "[ \t]+$" docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md
exit 1, no output; no trailing whitespace in the untracked evidence artifact
```

`tests/services/test_execution_contract.py` was not touched and was not needed for this Slice 4 validation.

## Residual risks

- Slice 4 did not address unrelated Slice 3 LOW findings such as orphan `missing_evidence_reason`, missing-key `KeyError` shape, or duplicate template file reads.
- `EvidenceAvailability` still owns explicit Ch3 actual-behavior aggregation specs; the new regression cross-validates them against typed manifest projection but does not move those runtime derivation specs into the template document.
