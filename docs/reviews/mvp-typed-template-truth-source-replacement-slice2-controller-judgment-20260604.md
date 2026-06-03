# MVP typed template truth-source replacement Slice 2 controller judgment

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 2, parse template doc into current untyped manifest
- Controller decision date: 2026-06-04
- Plan checkpoint: `266e18f gateflow: accept plan for typed template truth source replacement`
- Slice 1 checkpoint: `3c2b237 gateflow: accept typed template truth source slice1`

## Scope accepted for this slice

Slice 2 is limited to making the current untyped template contract API project from the canonical JSON block in `docs/fund-analysis-template-draft.md`:

- `fund_agent/fund/template/contracts.py` strictly extracts exactly one `TEMPLATE_CONTRACT_MANIFEST_JSON` block.
- The parser uses stdlib `json` and fail-closed validation for missing, duplicated, empty, malformed, unknown-key, id drift, shape drift, lens drift, and sidecar-field structural drift cases.
- `load_template_contract_manifest()`, `validate_template_contract_manifest()`, `get_chapter_contract()`, and `resolve_preferred_lens()` remain the public compatibility API.
- `tests/fund/template/test_contracts.py` covers the current 8-chapter projection, malformed template cases, unknown keys, stable id/text shape, preferred_lens validation, cache/path behavior, and local no-provider validation entry.

The slice does not change `typed_contracts.py`, typed projection authority, README/design/control/startup docs, renderer, Service, Host/Agent runtime, provider/runtime budgets, live probe, multi-year runtime, score-loop, golden/readiness state, PR state, release state, or deterministic default behavior.

## Implementation evidence reviewed

Reviewed implementation artifact:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md`

Reviewed changed files:

- `fund_agent/fund/template/contracts.py`
- `tests/fund/template/test_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md`

Controller-side validation reproduced:

```text
uv run pytest tests/fund/template/test_contracts.py -q
31 passed

uv run ruff check fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py
All checks passed!

git diff --check -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
exit 0, no output

uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py -q
12 passed

uv run python -m fund_agent.fund.template.contracts --validate-template-doc
exit 0, validation output correct; stderr contains a non-blocking runpy RuntimeWarning.
```

## Review results

Independent review artifacts:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-code-review-mimo-20260604.md`

Review verdicts:

- AgentDS: `PASS`, no blocking findings; one LOW finding about the `python -m` validation path emitting a `runpy` RuntimeWarning.
- AgentMiMo: `PASS`, no blocking findings; the same LOW RuntimeWarning finding.

Controller disposition:

- The LOW RuntimeWarning finding is accepted as non-blocking. The validation command exits `0`, returns the correct validation result, performs no provider/runtime action, and both reviewers traced the warning to Python runpy/package import behavior rather than parser correctness.
- No Slice 2 fix loop is required.

## Scope check

Accepted staged scope for the Slice 2 checkpoint is limited to:

- `fund_agent/fund/template/contracts.py`
- `tests/fund/template/test_contracts.py`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-code-review-mimo-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-controller-judgment-20260604.md`

Unrelated untracked artifacts in the workspace remain outside this checkpoint and must not be staged by this gate.

## Accepted / deferred distinction

Accepted in Slice 2:

- The current untyped `TemplateContractManifest` path is now a strict projection from `docs/fund-analysis-template-draft.md` canonical JSON.
- Python-authored untyped `_CHAPTERS`, `_lens()`, and `_chapter()` contract truth has been removed from `contracts.py`.
- No-provider template validation path exists.
- Slice 2 evidence and review artifacts are accepted.

Still deferred to later slices in this same gate:

- `typed_contracts.py` must project typed ids, missing behavior, audit focus, dependencies, Ch2 internal subcontracts, and Ch3 predicate from the template JSON rather than code-authored sidecar truth.
- Typed consumer regression and evidence availability cross-validation remain for later slices.
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, and `tests/README.md` remain deferred until documentation/control sync.

Explicit non-goals remain deferred:

- Agent runtime or tool-loop implementation.
- Provider/default/runtime budget changes or live probe.
- Multi-year evidence runtime.
- Score-loop.
- Ch2 public split.
- Deterministic default behavior changes.
- Golden/readiness/release/PR external-state changes.

## Controller verdict

**ACCEPT Slice 2.**

The Slice 2 implementation is correct, reviewed, validated, and scope-contained. It may be committed as a local accepted checkpoint for Slice 2 only. This does not accept the full truth-source replacement gate and does not authorize Slice 3, phaseflow, real LLM smoke, provider/runtime work, or Agent runtime implementation.
