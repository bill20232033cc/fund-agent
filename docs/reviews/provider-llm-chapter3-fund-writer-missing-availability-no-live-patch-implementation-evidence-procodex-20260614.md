# Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Implementation Evidence - ProcCodex - 2026-06-14

Status: `FIX_IMPLEMENTED_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

Gate: `Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Gate`.

Implemented within authorized primary write set:

- `fund_agent/fund/chapter_writer.py`
- `tests/agent/test_runner.py`

Evidence artifact:

- `docs/reviews/provider-llm-chapter3-fund-writer-missing-availability-no-live-patch-implementation-evidence-procodex-20260614.md`

Out of scope and not performed:

- live/provider/network/analyze/checklist/readiness/release/PR commands;
- source/PDF/cache/FDR/FundDocumentRepository access;
- chapter body, raw prompt, provider payload, credential, raw report body, raw PDF/cache/source body reads;
- source policy/fallback, annual-period LLM route, Docling, repair budget or provider default changes;
- stage, commit, push, PR, merge, delete, move, archive or cleanup.

Pre-existing unrelated tracked diffs observed before this artifact write:

- `AGENTS.md`
- `README.md`
- `docs/design.md`

They were not edited by this worker.

## 2. Root-cause Confirmation

Accepted controller judgment `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-controller-judgment-20260614.md` authorized a Fund writer / typed availability boundary fix.

Confirmed root cause:

- `ChapterWriterInput` typed path correctly treats `evidence_availability is None` as a true configuration error.
- When an `EvidenceAvailability` object is present but lacks a required-output requirement for a typed item with declared `when_evidence_missing`, `_availability_for_required_output()` raised `ValueError`.
- That happened before writer preflight could convert the item into `missing_required_facts`, so Agent runner surfaced a pre-provider `ValueError` / `code_bug`.

Required boundary preserved:

- complete absence of typed `EvidenceAvailability` remains fail-closed `ValueError`;
- only provided-but-missing requirement availability is converted to deterministic writer-preflight fact-gap blocking;
- runner, Service bridge and orchestrator were not patched to mask Fund semantics.

## 3. Red-test-first Evidence

Added failing regression first in `tests/agent/test_runner.py`:

- test: `test_chapter_3_missing_typed_availability_blocks_before_provider`
- setup: monkeypatch `derive_evidence_availability` to return same-identity `EvidenceAvailability` with `requirements=()`;
- route: Chapter 3 only, `typed_template_path="typed_template_contract"`;
- provider guard: fake writer records requests; expected `writer.requests == []`.

Red command:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider -q
```

Observed red result before implementation:

```text
1 failed in 0.86s
AssertionError: assert 'failed' == 'blocked'
```

Important retained fact from the red run:

- `writer.requests == []` passed before the failing assertion, proving zero provider calls on the missing availability path.

## 4. Implementation Summary

Changed `fund_agent/fund/chapter_writer.py` only at the typed required-output availability boundary:

- `_availability_for_required_output()` now returns `None` when a provided `EvidenceAvailability` object lacks the item requirement.
- `_required_output_plan_item()` maps `requirement is None and item.when_evidence_missing is not None` to `action="block"`.
- Existing `_required_output_preflight_issues()` then emits `missing_required_facts`.
- Existing `write_chapter()` blocked-result path prevents LLM writer/provider invocation.

Preserved true configuration error behavior:

- `_required_output_evidence_plan()` still raises `ValueError("typed required output 写作路径必须显式传入 EvidenceAvailability")` when typed items are enabled and `evidence_availability is None`.
- Added `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` to prove the envelope-missing path still raises `ValueError` and does not call fake writer.

No conditional write-set file was edited:

- `fund_agent/fund/evidence_availability.py` was inspected but not changed.
- No typed sidecar mapping was changed.
- `fund_agent/fund/README.md` was not changed because no public Fund package behavior or documented interface became outdated; this is an internal fail-closed routing fix.

## 5. Validation Results

Red-test-first command:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider -q
```

Result before implementation:

```text
1 failed in 0.86s
```

Focused post-fix tests:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider tests/agent/test_runner.py::test_chapter_3_missing_evidence_availability_envelope_remains_value_error tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q
```

Result:

```text
3 passed in 0.57s
```

Touched test file:

```text
uv run pytest tests/agent/test_runner.py -q
```

Result:

```text
15 passed in 0.69s
```

Service/orchestrator no-masking guards:

```text
uv run pytest tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
```

Result:

```text
3 passed in 0.52s
```

Ruff on touched source/tests:

```text
uv run ruff check fund_agent/fund/chapter_writer.py tests/agent/test_runner.py
```

Result:

```text
All checks passed!
```

Whitespace check:

```text
git diff --check
```

Result: passed with no output.

No live/provider/network/analyze/checklist/readiness/release/PR command was run.

## 6. Accepted / Rejected / Residual Claims

Accepted:

| Claim | Disposition | Evidence |
|---|---|---|
| Covered missing typed required-output availability now blocks as writer-preflight fact gap. | ACCEPT | `test_chapter_3_missing_typed_availability_blocks_before_provider` passed; task `status="blocked"`, `stop_reason="missing_required_facts"`, `failure_category="fact_gap"`. |
| Missing availability path makes zero provider calls. | ACCEPT | Regression asserts `writer.requests == []`; post-fix focused test passed. |
| True missing `EvidenceAvailability` envelope remains fail-closed `ValueError`. | ACCEPT | `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` passed. |
| Runner/Service/orchestrator were not used to mask the issue. | ACCEPT | No runner/Service/orchestrator source was edited; targeted no-masking tests passed. |
| EID single-source/no-fallback and `NOT_READY` are preserved. | ACCEPT | No source/fallback/live/readiness command or source-policy file was touched. |

Rejected:

| Claim | Disposition | Reason |
|---|---|---|
| Provider readiness is proven. | REJECT | No provider call was made or accepted; regression proves zero fake writer calls on the fixed path. |
| LLM content quality is accepted. | REJECT | No chapter/report body was read or accepted. |
| Release/readiness can advance. | REJECT | `NOT_READY` remains current truth and this gate was not a readiness/release gate. |
| Source policy or fallback changed. | REJECT | No source/FDR/fallback file or command was used. |

Residuals:

| Residual | Owner | Next handling |
|---|---|---|
| Provider readiness and provider-response classification remain unproven. | Provider/runtime owner | Future reviewed live/provider gate only after controller authorization. |
| LLM content quality remains unaccepted. | Provider/runtime + chapter owners | Future content-quality gate after a complete accepted run exists. |
| Release/readiness remains `NOT_READY`. | Release owner/controller | Separate readiness/release gate only. |
| Pre-existing unrelated workspace diffs/residue remain visible. | Controller/artifact owners | Separate disposition gates; not changed by this worker. |

## 7. Final Verdict

VERDICT: FIX_IMPLEMENTED_NOT_READY
