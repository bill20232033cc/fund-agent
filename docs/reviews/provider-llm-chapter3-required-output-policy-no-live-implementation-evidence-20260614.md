# Provider/LLM Chapter 3 Required-output Policy No-live Implementation Evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`.

Role: AgentCodex implementation worker only. This artifact records the scoped implementation for accepted policy plan checkpoint `2725c74` and controller judgment `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`.

No live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command was run. No provider clients, provider env/config/runtime defaults, source acquisition, repository/cache/downloader/PDF/FDR/fallback code, repair budget, annual-period LLM route, Docling/parser policy, readiness/release/PR state, control docs, `AGENTS.md`, root `README.md`, or `docs/design.md` were changed.

Release/readiness remains `NOT_READY`. EID single-source/no-fallback remains unchanged.

Self-check: pass. Work stayed inside the assigned no-live implementation gate; no commit, stage, push, PR, merge, readiness, or release action was performed.

## Files Changed

- `docs/fund-analysis-template-draft.md`
- `tests/fund/template/test_typed_contracts.py`
- `tests/agent/test_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/README.md`
- `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-evidence-20260614.md`

`tests/fund/test_evidence_availability.py` was validated but not changed; its mapping remains unchanged.

## Implementation

- Changed canonical `ch3.required_output.item_01` from `when_evidence_missing="block"` to `when_evidence_missing="render_evidence_gap"`.
- Updated item 01 `missing_evidence_reason` to state that missing reviewed evidence can only output an evidence gap and cannot support manager-profile judgment.
- Preserved item id, ordering, other Chapter 3 item policies, chapter ids, `must_answer`, `must_not_cover`, and preferred lens.
- Replaced the old template hard-block expectation with `render_evidence_gap`; the test asserts the reason contains `缺少已复核证据` and `只能输出证据缺口`.
- Kept missing `EvidenceAvailability` envelope fail-closed before provider.
- Added Agent runner positive coverage proving missing manager basic info with approved gap wording calls writer and accepts Chapter 3.
- Added Agent runner negative coverage proving writer is called, but item 01 marker without approved gap wording blocks after writer-output validation with `writer:required_output_gap_missing:ch3.required_output.item_01`, not old `required_output_block`.
- Added Service positive coverage using typed contract and full fake Route C body chapters 1-6; accepted gap-rendered Chapter 3 participates in final assembly with assembled chapters `(0, 1, 2, 3, 4, 5, 6, 7)`.
- Updated the existing Service incomplete test to directly cover unsafe Chapter 3 item 01 output: final assembly remains incomplete and report markdown remains absent.
- Performed conditional docs discovery for item 01 hard-block prose. Updated only two current test-surface lines in `tests/README.md`; historical review artifacts and control docs were left unchanged.

## Controller Amendments Handling

1. Full final assembly shape chosen for the Service positive test: the fake run accepts all required body chapters 1-6 and asserts final assembly chapters `0..7`.
2. Direct negative service-level assertion added through `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`: unsafe Chapter 3 item 01 output leaves final assembly `incomplete`, `report_markdown is None`, and `result.report_markdown` raises.
3. Docs search was discovery-only. Only current `tests/README.md` hard-block wording was updated; control docs, root README, design doc, and historical review artifacts were not edited.
4. Missing `EvidenceAvailability` envelope remains fail-closed; only reviewed missing manager basic info degrades to visible evidence gap.

## Validation Results

Final passing commands:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap -q
```

Result: `1 passed in 0.79s`.

```bash
uv run pytest tests/fund/test_evidence_availability.py::test_ch3_basic_manager_info_required_output_uses_basic_identity_availability -q
```

Result: `1 passed in 0.78s`.

```bash
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer -q
```

Result: `3 passed in 0.45s`.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_accepts_final_assembly_when_ch3_item01_degrades_to_gap tests/services/test_fund_analysis_service_llm.py::test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness -q
```

Result: `2 passed in 0.56s`.

```bash
uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q
```

Final result after `tests/README.md` narrow sync: `74 passed in 0.56s`.

```bash
uv run ruff check tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Result: `All checks passed!`

```bash
git diff --check
```

Result: exit `0`, no output.

Intermediate failures during implementation:

- Agent runner negative selector initially accepted because the default fake writer already emitted approved Ch2/Ch3 gap wording. Fixed by adding a targeted unsafe item 01 fixture that preserves the marker but removes approved gap wording.
- Service negative selector initially accepted because `analyze_with_llm()` default policy is `legacy_contract`, and then because the default fake writer echoed prompt gap instructions. Fixed by enabling `typed_template_path="typed_template_contract"` in scoped Service tests and adding a targeted unsafe writer.
- Focused regression bundle initially failed after an accidental helper patch affected an unrelated runner test. Restored the unrelated test to the default fake writer and reran the bundle successfully.

## Residuals

- No live/provider completion, provider-response classification, content quality, bounded live re-evidence, additional samples, cleanup, PR, release, or readiness proof is provided by this no-live implementation.
- Historical review artifacts still describe prior item 01 hard-block facts as historical evidence-chain records; they were not updated by this implementation gate.
- Release/readiness remains `NOT_READY`.

## Final Verdict

VERDICT: IMPLEMENTED_READY_FOR_REVIEW_NOT_READY
