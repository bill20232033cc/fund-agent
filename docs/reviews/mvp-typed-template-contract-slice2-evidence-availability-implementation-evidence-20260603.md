# MVP typed template contract Slice 2 EvidenceAvailability implementation evidence

## Worker Self-Check

- Role: AgentCodex implementation worker only; not controller.
- Gate: `MVP typed template contract Slice 2 same-source EvidenceAvailability implementation gate`.
- Classification: `heavy`.
- Scope: Fund-layer same-source `EvidenceAvailability` only.
- Actions intentionally not taken: no commit, no push, no PR, no live provider probe, no control/design/template truth edit, no renderer/auditor/runtime/provider/default/budget/endpoint/score/golden/readiness/promotion change.

## Touched Files

- `fund_agent/fund/evidence_availability.py`
- `fund_agent/fund/__init__.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_evidence_availability.py`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md`

## Behavior Summary

- Added additive `evidence_availability.v1` dataclasses:
  - `EvidenceAvailability`
  - `RequirementAvailability`
  - `EvidenceGapReference`
  - `AvailabilityStatus`
  - `EvidenceRequirementId`
- Added `derive_evidence_availability()` and `derive_chapter_evidence_availability()`.
- Derivation is pure and same-source:
  - consumes `ChapterFactProjection` / `ChapterFactInput`
  - uses fact ids, source field ids, evidence anchor ids, fact statuses, missing reasons and typed contract requirement ids
  - does not read repository, PDF/cache/source helper, Service, Host, provider, retained report, filesystem, env or dayu runtime
- Availability statuses remain distinct:
  - `available`
  - `missing`
  - `unavailable`
  - `not_applicable`
  - `unreviewed`
- Ch2 requirement-sensitive availability stays under public chapter 2:
  - internal subcontract ids are `performance`, `attribution`, `cost`
  - no public Ch2 split or new public chapter ids are introduced
- Ch3 requirement ids cover:
  - manager strategy text
  - turnover
  - holdings snapshot
  - cross-period style evidence
  - manager alignment
  - actual behavior aggregate
- Current single-year projection does not load prior-year documents. Cross-period style evidence is represented as `unreviewed` with safe gap references.
- Unknown typed contract requirement ids fail closed before derivation.

## Validation

```bash
uv run pytest tests/fund/test_evidence_availability.py tests/fund/test_chapter_facts.py tests/fund/template/test_typed_contracts.py
```

Result:

```text
28 passed in 0.41s
```

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- fund_agent/fund/evidence_availability.py fund_agent/fund/__init__.py fund_agent/fund/README.md tests/fund/test_evidence_availability.py tests/README.md
```

Initial result before this evidence artifact:

```text
exit 0
```

## Test Coverage Added

- `test_derives_available_requirements_from_fact_ids_and_anchor_ids`
- `test_distinguishes_missing_unavailable_not_applicable_unreviewed`
- `test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent`
- `test_ch2_subcontract_availability_stays_under_public_chapter_2`
- `test_derivation_does_not_call_document_repository`
- `test_unknown_requirement_id_fails_closed`
- Additional closed-set smoke for `AvailabilityStatus`.

## Explicit Non-Goals Preserved

- Did not replace `ChapterFactProjection`.
- Did not change current `contracts.py`, renderer, auditor, deterministic `analyze/checklist`, `--use-llm` fail-closed behavior or CLI output.
- Did not edit `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` or `docs/fund-analysis-template-draft.md`.
- Did not add repository/PDF/cache/source helper access, Service/Host/provider/runtime wiring, retained-report reading, filesystem reads, env reads, dayu runtime or Agent tool-loop behavior.
- Did not pass business parameters through `extra_payload`, `**kwargs` or untyped payload bags.
- Did not implement multi-year annual evidence runtime loading.
- Did not change score-loop, golden/readiness/promotion, quality gate, final judgment or provider endpoint/default/budget behavior.

## Residual Risks

- Ch2 requirement-to-field mapping is intentionally conservative and same-source. It maps current typed Ch2 requirements to existing current-year structured facts; it does not prove full 1/3/5-year horizon completeness beyond what `ChapterFactProjection` currently exposes.
- Ch3 cross-period style evidence remains `unreviewed` in the current single-year projection. A later multi-year evidence runtime gate must decide how prior-year anchors and source-year references satisfy it.
- `derive_chapter_evidence_availability()` reconstructs fund code/year from fact ids for the single-chapter convenience path. The main production-grade path should prefer `derive_evidence_availability(projection)` so fund identity remains explicit on the projection root.
