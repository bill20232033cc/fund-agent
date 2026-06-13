# Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`.

Accepted root cause:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
- Verdict: `ACCEPT_ROOT_CAUSE_PROVEN_READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`

This implementation fixes only the no-live provider-before `ValueError` path for `ch3.required_output.item_01` when same-source evidence availability is in missing-evidence states.

## Guardrails

- No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command was run.
- No source/cache/PDF body was read.
- No Service/runner masking was introduced.
- EID remains the single operational source path.
- No Eastmoney, fund-company website, CNINFO or fallback path was introduced.
- `release/readiness` remains `NOT_READY`.

## Implementation Summary

Changed files:

- `docs/fund-analysis-template-draft.md`
- `tests/agent/test_runner.py`
- `tests/fund/template/test_typed_contracts.py`
- `tests/README.md`

Behavior change:

- `ch3.required_output.item_01` now declares:
  - `when_evidence_missing: "block"`
  - `missing_evidence_reason: "第 3 章基金经理基本信息缺少已复核证据时不能进入基金经理画像写作。"`

This keeps the behavior in the canonical template truth source instead of adding Service/runner exception masking. Runtime projection continues through the existing typed template loader and Fund writer required-output plan.

## Red-test-first Evidence

Added red test before the template fix:

- `tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider`

Pre-fix result:

```text
FAILED tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider
AssertionError: assert 'failed' == 'blocked'
```

This confirmed the current path still surfaced as provider-before `ValueError` / `code_bug` instead of writer-preflight fact-gap blocking.

## Post-fix Behavior

The same test now proves:

- missing `portfolio_managers` makes `ch3.required_output.item_01` availability status `missing`;
- the typed item action becomes `block`;
- writer/fake-provider requests remain `0`;
- task status is `blocked`;
- terminal state is `blocked_fact_gap`;
- stop reason is `missing_required_facts`;
- failure category is `fact_gap`;
- writer result is a blocked result with a required-output evidence plan entry for `ch3.required_output.item_01`.

Added typed projection guard:

- `tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks`

This locks the canonical template projection so future changes cannot silently revert `ch3.required_output.item_01` to null missing behavior.

Updated test documentation:

- `tests/README.md` now records the typed template and Agent runner coverage added by this gate.

## Validation

Commands run:

```bash
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_evidence_availability_envelope_remains_value_error -q
```

Result:

```text
3 passed in 0.79s
```

```bash
uv run pytest tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks tests/fund/template/test_typed_contracts.py::test_current_typed_projection_matches_template_json_exact_fields -q
```

Result:

```text
2 passed in 0.41s
```

```bash
uv run ruff check tests/agent/test_runner.py tests/fund/template/test_typed_contracts.py
```

Result:

```text
All checks passed!
```

```bash
uv run python -m fund_agent.fund.template.contracts --validate-template-doc
```

Result:

```text
template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8
```

The validator also emitted the existing `runpy` warning about module import order; exit code was `0`.

Broader focused validation:

```bash
uv run pytest tests/agent/test_runner.py -q
```

Result:

```text
16 passed in 0.75s
```

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py tests/fund/test_evidence_availability.py -q
```

Result:

```text
57 passed in 0.72s
```

```bash
uv run pytest tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
```

Result:

```text
3 passed in 0.73s
```

```bash
git diff --check
```

Result: passed with no output.

## Residuals

| Residual | Disposition |
| --- | --- |
| Other typed required-output items with null missing behavior may have future risk if evidence availability becomes non-available. | Deferred candidate; not touched by this gate. |
| Existing service diagnostic tests still intentionally cover synthetic pre-writer `ValueError` injection paths. | Not changed; these remain diagnostic regression tests for code-bug mapping. |
| No post-fix live command was run. | Expected; current gate is no-live implementation. Post-fix live evidence requires a separate bounded live gate. |
| Release/readiness remains `NOT_READY`. | Preserved. |

## Verdict

VERDICT: FIX_IMPLEMENTED_NO_LIVE_NOT_READY

Recommended next gate:

`Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Review and Controller Acceptance Gate`
