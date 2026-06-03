# MVP typed template contract Slice 3 required-output missing/degrade implementation evidence

## Worker Self-Check

- Role: AgentCodex implementation worker only; not controller.
- Gate: `MVP typed template contract Slice 3 required-output missing/degrade implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Actions intentionally not taken: no commit, no push, no PR, no live provider probe, no provider/runtime/default/budget/endpoint change, no Agent runtime/tool-loop implementation, no score/golden/readiness/promotion change, no direct document/PDF/cache/source-helper access, no `extra_payload` business params, no edits to `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` or `docs/fund-analysis-template-draft.md`.

## Touched Files

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/evidence_availability.py`
- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_evidence_availability.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice3-required-output-missing-degrade-implementation-evidence-20260603.md`

## Behavior Summary

- Added additive typed writer input support:
  - `ChapterWriterInput.typed_required_output_items`
  - `ChapterWriterInput.evidence_availability`
  - `RequiredOutputEvidencePlan`
- Default writer path remains unchanged when typed required output items are not supplied: current `contract.required_output_items` markers and parser policy still apply.
- Typed writer path uses stable required output ids as exact markers, for example `<!-- required_output:ch3.required_output.item_05 -->`, rather than free-form fallback labels.
- Missing evidence handling now supports:
  - `render_evidence_gap`: writer must output the typed marker and approved evidence-gap wording.
  - `render_minimum_verification_question`: writer must output the typed marker and approved minimum-verification wording.
  - `delete_if_not_applicable`: writer may omit the marker only when availability is `not_applicable` and a typed reason is present.
  - `block`: writer emits a preflight `missing_required_facts` block before calling the LLM client.
- Missing evidence can satisfy a typed required output only through approved gap or verification wording. A marker without the required degrade phrase remains blocked as `missing_required_output_marker`.
- Existing anchor/missing marker policy remains strict; invalid missing markers still fail closed as `llm_contract_violation`.
- `EvidenceAvailability` now covers Slice 2 residual `ch3.required_output.item_01` through `structured.basic_identity`; Ch3 actual behavior aggregate remains unchanged.
- `RequiredOutputItem` now carries optional `missing_evidence_reason`; `delete_if_not_applicable` validates that the reason exists.

## Validation

Command:

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py tests/fund/template/test_typed_contracts.py
```

Result:

```text
57 passed in 0.47s
```

Command:

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result:

```text
All checks passed!
```

Command:

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/evidence_availability.py fund_agent/fund/template/typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md
```

Result: exited `0`.

## Non-Goals Preserved

- No provider/runtime/default/budget/endpoint changes.
- No live PASS-only probe.
- No deterministic fallback and no stdout partial report behavior.
- No Service, Host, CLI, quality gate, final judgment, score-loop, golden/readiness or promotion changes.
- No template truth replacement and no `docs/fund-analysis-template-draft.md` edit.
- No Agent runtime/tool-loop implementation.
- No multi-year annual evidence runtime loading.
- No direct repository/PDF/cache/source-helper access from writer or availability code.

## Residual Risks

- Typed required-output behavior is additive and only active when callers explicitly pass typed items plus `EvidenceAvailability`; broader Service/Agent wiring remains a later gate.
- Writer `block` currently reuses the existing `missing_required_facts` stop reason to avoid changing Service stop-reason mappings in this slice. Issue ids distinguish typed required-output block cases.
- `delete_if_not_applicable` is implemented and reason-guarded, but broad real-template usage awaits future typed wiring and review of item-level applicability predicates.
- Degrade phrase checks are deterministic and intentionally narrow; future Slice 4 audit work still owns polarity/allowed-context enforcement for positive or quasi-positive Ch3 consistency claims.
