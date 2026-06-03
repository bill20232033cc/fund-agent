# MVP typed template truth-source replacement Slice 4 controller judgment

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 4, typed consumers regression
- Controller decision date: 2026-06-04
- Baseline checkpoint: `202b396 gateflow: accept typed template truth source slice3`
- Plan checkpoint: `266e18f gateflow: accept plan for typed template truth source replacement`
- Slice 1 checkpoint: `3c2b237 gateflow: accept typed template truth source slice1`
- Slice 2 checkpoint: `0263bc2 gateflow: accept typed template truth source slice2`
- Slice 3 checkpoint: `202b396 gateflow: accept typed template truth source slice3`

## Scope accepted for this slice

Slice 4 is limited to typed consumer regression after the template truth-source replacement:

- Add a `LensKey` runtime closed-set guard in `fund_agent/fund/template/typed_contracts.py` to resolve Slice 3 MiMo M1.
- Confirm `chapter_contract_constraints.py` remains a no-change public-manifest consumer through tests that compare default wrappers with both the untyped manifest and typed projection, while active-fund overlays still resolve.
- Cross-validate `EvidenceAvailability` Ch2/Ch3 private specs against the projected typed manifest:
  - `_CH2_REQUIREMENT_SPECS`
  - `_CH3_REQUIREMENT_SPECS`
  - `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`
  - `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`
  - `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES`
- Strengthen the Service typed path regression so it covers template document -> typed manifest -> `EvidenceAvailability` -> writer/auditor/service typed path, including required output ids/text and `audit_focus` from the typed manifest.

The slice does not change deterministic `analyze/checklist`, renderer output, provider/runtime budgets, live probes, Host/Agent runtime, multi-year runtime, score-loop, golden/readiness state, PR state, release state, or external state.

## Implementation evidence reviewed

Reviewed implementation artifact:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md`

Reviewed changed files:

- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_evidence_availability.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md`

Controller-side validation reproduced:

```text
uv run pytest tests/fund/template/test_typed_contracts.py -q
15 passed

uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
171 passed

uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
46 passed

uv run ruff check fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py
All checks passed!

git diff --check -- fund_agent/fund/template/typed_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md
exit 0, no output
```

## Review results

Independent review artifacts:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-code-review-mimo-20260604.md`

Review verdicts:

- AgentDS: `PASS`, 0 BLOCKING, 0 HIGH, 0 MEDIUM, 2 LOW.
- AgentMiMo: `PASS`, 0 BLOCKING, 0 HIGH, 0 MEDIUM, 1 LOW, plus prior Slice 3 residuals reiterated as deferred.

Both reviewers independently confirmed:

- Slice 4 validates typed consumers against the template-doc-projected typed manifest, not old code-authored mappings.
- `chapter_contract_constraints.py` has no source change and remains a public-manifest consumer.
- The required Ch2/Ch3 `EvidenceAvailability` private specs are cross-validated against the projected typed manifest.
- The Service typed path regression now checks typed manifest required output ids/text and `audit_focus` through writer/auditor/service boundaries.
- The `LensKey` runtime guard resolves Slice 3 MiMo M1 without behavior drift.
- No provider/runtime/live probe, Host/Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/release, repository/PDF/cache/source-helper or external-state behavior was introduced.

## Controller disposition

No blocking findings were accepted. No Slice 4 fix loop is required.

### LOW findings

- **DS D1 / MiMo L1: Ch3 reverse cross-validation can be more explicit.** Accepted as non-blocking. Current assertions prove typed manifest Ch3 output ids are covered by base specs or actual-behavior output ids, and current data is consistent. A future evidence-availability contract cleanup may add bidirectional equality where the intended Ch3 asymmetry is clearer.
- **DS D2: Service monkeypatch uses hardcoded stable requirement ids for two availability spot checks.** Accepted as non-blocking. Those ids are stable contract ids under `EvidenceRequirementId`; the same test now validates required output ids/text and `audit_focus` against `typed_by_id`, so the core typed projection path is covered.

Prior Slice 3 LOW/MEDIUM residuals remain non-blocking and deferred unless a later gate explicitly accepts them:

- Ch2 internal subcontract requirement ids use strict AND coupling across chapter ids and `EvidenceRequirementId`; current data satisfies it.
- Missing template keys may surface as `KeyError` after Slice 2 parser boundaries; still fail-closed.
- Orphan `missing_evidence_reason` with no behavior is not consumed.
- Duplicate template file reads are performance-only.
- Private path parameter is not public API.
- Lazy `typed_contracts` / `evidence_availability` import works through local import.

## Scope check

Accepted staged scope for the Slice 4 checkpoint is limited to:

- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_evidence_availability.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-implementation-evidence-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-code-review-mimo-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice4-controller-judgment-20260604.md`

Unrelated untracked artifacts in the workspace remain outside this checkpoint and must not be staged by this gate.

## Accepted / deferred distinction

Accepted in Slice 4:

- `LensKey` runtime closed-set validation for typed preferred lens.
- Consumer regression coverage for `chapter_contract_constraints.py`, `EvidenceAvailability`, and the Service typed path.
- Slice 4 evidence and review artifacts.

Still deferred to Slice 5 in this same gate:

- Documentation/control sync for `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, and `tests/README.md`.
- Final current/future/deferred wording that says `docs/fund-analysis-template-draft.md` canonical JSON is now the authored template contract truth source.

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

**ACCEPT Slice 4.**

The Slice 4 implementation is correct, independently reviewed by two reviewers with no blocking findings, validated with the required targeted suites, and scope-contained. It may be committed as a local accepted checkpoint for Slice 4 only. This does not accept the full truth-source replacement gate and does not authorize Slice 5, phaseflow, real LLM smoke, provider/runtime work, PR/push, or Agent runtime implementation.
