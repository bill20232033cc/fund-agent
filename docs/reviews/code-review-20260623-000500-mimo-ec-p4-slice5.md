# Code Review: EC-P4 Slice 5 — No-Live Semantic Companion Propagation

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code review
- Slice: Slice 5 - No-Live Semantic Companion Propagation
- Classification: heavy
- Branch: evidence-confirm-productionization
- Reviewer: AgentMiMo
- Date: 2026-06-23

## Verdict

**PASS_WITH_FINDINGS**

## Changed Files

| File | Change Summary |
|---|---|
| `fund_agent/fund/evidence_confirm_production.py` | Add optional `semantic_result` kwarg to `summary_from_repository_result()`; add `_semantic_status()`, `_semantic_issue_count()`, `_validate_semantic_result_identity()`; import `EvidenceSemanticResult` |
| `fund_agent/fund/quality_gate_integration.py` | Refactor `_evidence_confirm_quality_gate_issues()` from early-return to accumulate-list; add semantic_status → ECQ4 projection; add `_semantic_ecq_issue()` |
| `tests/fund/test_evidence_confirm_semantic.py` | Add `test_semantic_result_can_be_injected_into_production_summary_without_client` and `test_semantic_production_paths_do_not_construct_provider_or_llm_clients`; add `_call_name` helper |
| `tests/fund/test_quality_gate_integration.py` | Add ECQ4 tests: semantic fail → block, semantic fail + warn policy → warn, deterministic fail blocks when semantic passes; update `_summary()` helper with `semantic_status` param |
| `tests/services/test_fund_analysis_service.py` | Add `semantic_status == "not_run"` assertion to existing EC warn test |

## Validation

| Check | Result |
|---|---|
| `uv run pytest ... -q` | **76 passed in 0.60s** |
| `uv run ruff check ...` | **All checks passed!** |
| `git diff --check` | **Clean** |
| `rg` forbidden imports (OpenAI, provider, LLM config) | **No matches** |
| `rg` semantic propagation references | **All expected locations confirmed** |

## Review Focus Findings

### 1. Optional typed EvidenceSemanticResult propagation is no-live and injected only

**PASS.**

- `summary_from_repository_result()` accepts `semantic_result: EvidenceSemanticResult | None = None` as keyword-only arg.
- The function only reads typed dataclass fields (`overall_status`, `fund_code`, `report_year`, `claim_results`).
- No network, provider, PDF, repository, or LLM construction is introduced in the production path.
- `EvidenceSemanticResult` is imported from `fund_agent.fund.evidence_confirm_semantic`, which itself only imports from `fund_agent.fund.evidence_confirm` (standard library + Fund-layer types).

### 2. No provider, OpenAI, LLM client, network, PDF, repository source, or provider config construction/import

**PASS.**

- Static `rg` scan of production files returns zero matches for `OpenAI`, `AsyncOpenAI`, `load_llm_provider_config_from_env`, `build_chapter_llm_clients`, `fund_agent.config.llm`, `fund_agent.services.llm_provider`.
- AST-based test `test_semantic_production_paths_do_not_construct_provider_or_llm_clients` validates both production modules at test time.
- Module imports are strictly Fund-layer internal: `evidence_confirm_semantic` and `evidence_confirm_sources`.

### 3. Missing semantic result remains semantic_status=not_run

**PASS.**

- `_semantic_status(None)` returns `"not_run"` (line 254-255 of `evidence_confirm_production.py`).
- `not_run_evidence_confirm_summary()` hard-codes `semantic_status="not_run"` (line 174).
- Service test `test_fund_analysis_service_evidence_confirm_warn_calls_runner_without_blocking` asserts `semantic_status == "not_run"` when no semantic result is injected.

### 4. Semantic fail/warn maps to ECQ4 only when semantic result is present

**PASS.**

- `_evidence_confirm_quality_gate_issues()` checks `summary.semantic_status in {"fail", "warn"}` (line 262 of `quality_gate_integration.py`).
- When `semantic_status="not_run"` (default), condition is false — no ECQ4 issue generated.
- Tests `test_quality_gate_integration_without_summary_is_unchanged` and `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` verify no ECQ issues on default path.

### 5. Deterministic V2 fail remains blocking even when semantic status is pass

**PASS.**

- `quality_gate_integration.py` accumulates ECQ2 (deterministic fail) into `issues` list, then separately checks semantic_status. ECQ2 is not removed or overridden by semantic pass.
- Test `test_quality_gate_integration_deterministic_fail_blocks_even_when_semantic_passes` explicitly verifies: `status == "block"`, ECQ2 present with `severity == "block"`, and no ECQ4 issue emitted.

### 6. Identity mismatch handling does not create unsafe cross-sample propagation

**PASS (with finding F-01).**

- `_validate_semantic_result_identity()` raises `ValueError` when `semantic_result.fund_code != result.fund_code` or `semantic_result.report_year != result.report_year`.
- This is called before any status extraction, ensuring fail-closed behavior.
- **Finding F-01**: No test covers the identity mismatch `ValueError` path. See below.

### 7. Service/UI/renderer boundaries are not expanded in this slice

**PASS.**

- `fund_agent/services/fund_analysis_service.py` has zero code changes (only a one-line test assertion addition).
- No UI or renderer files are touched.
- `quality_gate_integration.py` is Fund-layer, not Service-layer.

### 8. Tests actually cover the above

**PASS (with finding F-01).**

- 8 new test functions added across 3 test files.
- Key scenarios covered: semantic injection into production summary, ECQ4 block/warn projection, deterministic fail overrides semantic pass, no-live static import guards, no provider/LLM construction guards.
- **Finding F-01**: Identity mismatch ValueError not tested.

## Findings

### F-01 (Non-blocking): `_validate_semantic_result_identity()` ValueError not tested

**Severity**: informational

**Description**: `evidence_confirm_production.py:283-303` implements `_validate_semantic_result_identity()` which raises `ValueError("semantic result 与 Evidence Confirm repository result 身份不一致")` when `semantic_result.fund_code` or `semantic_result.report_year` does not match the deterministic result. This is a safety-critical fail-closed path that prevents cross-sample propagation. No test in any of the three test files covers this ValueError.

**Recommendation**: Add a test in `test_evidence_confirm_semantic.py` that constructs a `EvidenceSemanticResult` with mismatched `fund_code` or `report_year` and asserts `ValueError` is raised when passed to `summary_from_repository_result()`.

**Blocking**: No — the implementation is correct and the guard is in place; only test coverage is missing.

## Adversarial Failure Pass

| Attack Vector | Result |
|---|---|
| Inject malformed `EvidenceSemanticResult` with wrong fund_code | Blocked by `_validate_semantic_result_identity()` ValueError |
| Inject `EvidenceSemanticResult` with `overall_status="not_applicable"` | Correctly mapped to `semantic_status="not_applicable"`, not propagated to ECQ4 |
| Deterministic fail + semantic pass | ECQ2/block preserved, no ECQ4 emitted — verified by test |
| `policy="off"` + semantic fail/warn | `_ecq_policy_severity()` raises ValueError — existing guard applies |
| Empty `claim_results` with `overall_status="fail"` | `_semantic_issue_count()` returns 0; summary.status still "fail" from semantic — edge case is safe |

## Project Instruction Check

| Instruction | Compliance |
|---|---|
| No provider/OpenAI/LLM imports | Yes |
| No PDF/repository/source adapter access | Yes |
| No Service/UI/Host/renderer boundary expansion | Yes |
| Fund-layer only changes | Yes |
| No `extra_payload` usage | Yes |
| Docstring present (Chinese) | Yes — all new functions have complete Chinese docstrings |
| No magic numbers/strings | Yes |
| Tests follow implementation boundary | Yes |

## Over-Coupling Check

No over-coupling detected. The only new cross-module dependency is `evidence_confirm_production.py` importing `EvidenceSemanticResult` from `evidence_confirm_semantic.py`, which is a Fund-layer internal typed data class — this is the intended design boundary.

## Artifact Path

`docs/reviews/code-review-20260623-000500-mimo-ec-p4-slice5.md`
