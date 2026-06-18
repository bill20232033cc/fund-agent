# Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Controller Judgment

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`.

This judgment closes the no-live implementation review for the accepted root cause in:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`

The accepted root cause was: `ch3.required_output.item_01` reached missing-evidence status while the typed template had `when_evidence_missing=null`, causing Fund writer required-output planning to raise provider-before `ValueError`, which the Agent runner correctly surfaced as `llm_exception` / `code_bug` with provider attempt count `0`.

## Evidence Reviewed

- Implementation evidence: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-evidence-20260614.md`
- DS implementation review: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-review-ds-20260614.md`
- MiMo implementation review: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-review-mimo-20260614.md`
- Scoped diff:
  - `docs/fund-analysis-template-draft.md`
  - `tests/agent/test_runner.py`
  - `tests/fund/template/test_typed_contracts.py`
  - `tests/README.md`

## Accepted Current Facts

- The canonical template truth source now declares `ch3.required_output.item_01` as fail-closed when required same-source evidence is missing:
  - `when_evidence_missing: "block"`
  - `missing_evidence_reason: "第 3 章基金经理基本信息缺少已复核证据时不能进入基金经理画像写作。"`
- The fix is in the template contract, not in Service/runner masking.
- The no-live runner test proves missing `portfolio_managers` blocks Chapter 3 before any writer/provider request.
- The typed contract test locks the template projection for `ch3.required_output.item_01`.
- Existing invariant coverage remains: a fully absent `EvidenceAvailability` envelope still fails closed as code-bug/`ValueError`.
- EID remains the only operational annual-report source path. No Eastmoney, fund-company website, CNINFO, source fallback, provider default, repair budget, annual-period LLM route, Docling, readiness, release, PR or external-state behavior was changed.
- Release/readiness remains `NOT_READY`.

## Review Finding Disposition

| Finding | Source | Disposition | Controller rationale |
| --- | --- | --- | --- |
| `ch3.required_output.item_01` missing evidence should no longer raise provider-before `ValueError`. | Implementation evidence, DS review, MiMo review | ACCEPT | The accepted root cause is fixed at the canonical template truth source, and no-live tests prove zero-provider fact-gap blocking. |
| `missing_availability` currently treats any non-null `when_evidence_missing` with absent requirement mapping as `block`, which may be overly conservative for future `render_*` behaviors. | DS review | DEFER | This behavior is outside the accepted item 01 root cause. It is fail-closed, not a readiness claim, and should be handled only by a future template/availability coverage-hardening gate with explicit behavior policy. |
| Other typed required-output items may still have `when_evidence_missing=null`. | Implementation evidence, DS review, MiMo review | DEFER | Current gate is deliberately scoped to the proven Chapter 3 item 01 failure. Broader typed-template audit/fix would be a separate no-live gate. |
| No post-fix live evidence exists for this item 01 fix. | Implementation evidence, DS review, MiMo review | ACCEPTED_RESIDUAL | Expected for this no-live implementation gate. User has separately authorized later bounded live evidence, but it is not part of this acceptance. |

## Validation Accepted

Accepted validation from implementation evidence and reviews:

```bash
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_evidence_availability_envelope_remains_value_error -q
```

Result: `3 passed`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks tests/fund/template/test_typed_contracts.py::test_current_typed_projection_matches_template_json_exact_fields -q
```

Result: `2 passed`.

```bash
uv run ruff check tests/agent/test_runner.py tests/fund/template/test_typed_contracts.py
```

Result: passed.

```bash
uv run python -m fund_agent.fund.template.contracts --validate-template-doc
```

Result: template manifest valid, exit code `0`; existing `runpy` warning is non-blocking.

Broader focused suites accepted:

- `uv run pytest tests/agent/test_runner.py -q` -> `16 passed`
- `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py tests/fund/test_evidence_availability.py -q` -> `57 passed`
- `uv run pytest tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` -> `3 passed`
- `git diff --check` -> passed

## Residuals

| Residual | Owner | Disposition |
| --- | --- | --- |
| Broader typed required-output null missing behavior audit. | Fund template / controller | Deferred candidate; no current implementation in this gate. |
| `missing_availability` behavior policy for absent requirement mappings. | Fund writer / template availability owner | Deferred candidate; keep current fail-closed behavior until a reviewed policy gate decides otherwise. |
| Post-fix live provider/LLM result for exact `004393 / 2025`. | Controller / evidence owner | Next bounded live evidence gate after local checkpoint; readiness still `NOT_READY`. |
| Release/readiness, PR and external-state actions. | Release owner / user authorization | Not authorized by this gate; remains `NOT_READY`. |

## Control-doc Update Recommendation

After checkpointing the scoped implementation, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

The next entry point should become:

`Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence Gate`

The next gate must remain bounded to exact `004393 / 2025`, preserve EID single-source/no-fallback, avoid source/PDF/cache body reads, and report only fail-closed or completion evidence without declaring readiness.

## Final Verdict

VERDICT: ACCEPT_IMPLEMENTATION_NOT_READY

The implementation is accepted for the no-live item 01 root-cause fix. Release/readiness remains `NOT_READY`.
