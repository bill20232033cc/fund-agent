# Controller Judgment: source provenance public-output implementation plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance public-output implementation gate`
> Latest accepted checkpoint before gate: `918f65d docs: accept source provenance design`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `coverage replacement / source provenance design accepted locally` |
| Reviewed plan gate | `source provenance public-output implementation gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The code-generation-ready implementation plan is accepted for one narrow implementation slice: Fund-owned deterministic source provenance projection, safe public provenance threading through `StructuredFundDataBundle`, and additive snapshot JSONL / summary output. The implementation must not change source orchestration, fallback eligibility, source helpers, renderer, FQ0-FQ6, default analyze/checklist behavior, Host/Agent/dayu, golden fixtures, baseline fixtures, fund-type logic, or extractor logic.

The accepted refinement is the `NOT_APPLICABLE` default factory strategy for `StructuredFundDataBundle.source_provenance`. Production `FundDataExtractor.extract()` must explicitly populate provenance from `ParsedAnnualReport.metadata.source`; tests and fakes not exercising provenance may rely on the safe not-applicable default.

## Review Summary

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | `PASS` | Accepted. Required test/default refinements resolved. |
| AgentGLM | `PASS_WITH_FINDINGS` | `PASS` | Accepted. High fixture-churn and medium format findings resolved. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| Required `StructuredFundDataBundle.source_provenance` would cause broad fixture churn | GLM F1 / MiMo F1 | Accepted and fixed | Plan now requires a safe `default_public_source_provenance()` factory while production extraction explicitly projects real metadata. |
| Summary provenance output format was underspecified | GLM F2 | Accepted and fixed | Plan now requires a separate `## Source Provenance` table with exact columns and a failed-fund out-of-scope note. |
| `SnapshotRecord` new-field default / population strategy was underspecified | GLM F3 | Accepted and fixed | Plan now allows not-applicable-compatible defaults but requires production records to be fully populated through `build_snapshot_records()` / `_snapshot_record()`. |
| Score JSON shape no-change assertion was ambiguous | MiMo F2 | Accepted and fixed | Plan now requires deterministic `score.json` top-level key-set and FQ0-FQ6 gate-sensitive no-change assertions. |
| Same-fund snapshot records should carry identical provenance | MiMo F3 | Accepted and fixed | Plan keeps an explicit snapshot assertion for identical provenance copied from the bundle. |
| `SourceStrategy` single value needed clarification | GLM F4 | Accepted and fixed | Plan states the single Literal value is intentional for v1 and does not open a source-strategy policy surface. |

## Accepted Implementation Scope

- Add `fund_agent/fund/source_provenance.py` with deterministic public projection and stable domains.
- Add `StructuredFundDataBundle.source_provenance` with safe not-applicable default factory.
- Populate production bundles from `ParsedAnnualReport.metadata.source`.
- Add eight additive provenance fields to `SnapshotRecord` / snapshot JSONL.
- Add a separate `## Source Provenance` section to snapshot summary with exact v1 columns.
- Prove score/FQ0-FQ6 and default CLI/service behavior do not reinterpret provenance.

## Required Validation

- Focused tests:
  - `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py`
- Adjacent compatibility:
  - `uv run pytest tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_quality_gate_service.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py`
- Static / whitespace:
  - `uv run ruff check .`
  - `git diff --check`

Bounded CLI evidence for `110020` / 2024 and `017641` / 2024 is not part of plan acceptance. It may run only after implementation and code review are accepted for that evidence step.

## Stop Conditions

Stop before or during implementation if the work requires modifying `FundDocumentRepository` strategy, `documents/sources.py`, source helpers, cache/PDF/downloader behavior, fallback eligibility decisions, source metadata schema, renderer, FQ0-FQ6, default analyze/checklist behavior, Host/Agent/dayu, fund-type logic, extractor logic, replacement candidates, golden/baseline fixtures, or if score/quality-gate semantics change.

## Next Entry Point

`source provenance public-output implementation`

The next handoff may implement only the accepted slice above and must return implementation evidence, focused validation output, and a code-review-ready diff. No commit, push, PR, extraction evidence, golden/baseline promotion, or GitHub mutation is authorized for the implementation worker.
