# Evidence Confirm Productionization RR-09 A0 Fact-level Diagnostic Static Implementation Evidence

Verdict token:

`RR_09_A0_FACT_DIAGNOSTIC_STATIC_IMPLEMENTED_NOT_READY`

## Scope

Gate: `RR-09 A0 R1-R4 Fact-level Diagnostic Static Preparation`.

This slice implements only no-live static preparation for later A1 diagnostics. It adds a Fund-layer in-memory diagnostic helper that consumes an already available `EvidenceConfirmResultV2` and emits safe aggregate/fact metadata. It does not load product samples.

No live/PDF/provider/LLM command, repository load, source/cache/parser read, product CLI re-evidence, PR mutation, push, tag, release, readiness promotion, checklist support, report-body rendering, provider-backed semantic production default, or quality-gate semantic change was authorized or performed.

## Changed Files

- `fund_agent/fund/evidence_confirm_diagnostics.py`
- `tests/fund/test_evidence_confirm_diagnostics.py`
- `fund_agent/fund/README.md`

## Implementation

Added `evidence_confirm_fact_diagnostic.v1`:

- `summarize_evidence_confirm_diagnostics(result: EvidenceConfirmResultV2)` returns `EvidenceConfirmDiagnosticSummary`.
- The summary includes safe fields only:
  - fund code and report year,
  - overall V2 status,
  - checked/failed/warning/not-applicable fact counts,
  - issue count,
  - diagnostic buckets grouped by fail/warn dimension, source field id and chapter id,
  - stable issue ids,
  - V2 next-gate recommendation,
  - conservative root-cause classification.
- The helper does not include excerpt text, PDF/cache paths, source helper details, parser payloads, provider payloads, raw values or report body content.

Current conservative root-cause classification:

| Dimension / status | Classification |
|---|---|
| `anchor_precision` warn | `true_anchor_precision_gap` |
| `missing_evidence` fail/warn | `projection_attachment_defect` |
| `source_support` fail/warn | `projection_attachment_defect` |
| `proof_boundary` fail/warn | `projection_attachment_defect` |
| `value_match` fail/warn | `undetermined` |

This is not a release disposition. It prepares A1 to distinguish true anchor/projection gaps, deterministic V2 false-positive patterns and projection/source attachment defects after explicit live/PDF authorization.

## Tests

Added focused tests:

- grouping by dimension/source field/chapter,
- deterministic issue-id aggregation,
- root-cause classification,
- safe payload exclusion of raw text/path-like content.

## Validation

```bash
uv run pytest tests/fund/test_evidence_confirm_diagnostics.py -q --tb=short
```

Result: `2 passed`.

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short -k "v2"
```

Result: `23 passed, 24 deselected`.

```bash
uv run ruff check fund_agent/fund/evidence_confirm_diagnostics.py tests/fund/test_evidence_confirm_diagnostics.py
```

Result: `All checks passed!`

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/services/test_fund_analysis_service.py tests/services/test_quality_gate_service.py -q --tb=short
```

Result: `95 passed`.

```bash
git diff --check -- fund_agent/fund/evidence_confirm_diagnostics.py tests/fund/test_evidence_confirm_diagnostics.py fund_agent/fund/README.md
```

Result: passed.

## Residuals

| Residual | Status | Destination |
|---|---|---|
| R1-R4 product sample fact-level diagnostic | open | A1, requiring explicit live/PDF authorization before repository-bounded product diagnostics. |
| `017641 / 2024` runtime product CLI re-evidence | open | B1 runtime re-evidence, requiring explicit live/PDF authorization. |
| V2 false-positive identification | unproven | Requires actual diagnostic evidence; A0 only preserves the classification bucket. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Next Entry Point

`RR-09 A0 Code Review / RR-09 A1 Authorization Boundary / RR-09 B1 Runtime Re-evidence Authorization`

Release/readiness remains `NOT_READY`.

Completion token:

`RR_09_A0_FACT_DIAGNOSTIC_STATIC_IMPLEMENTED_NOT_READY`
