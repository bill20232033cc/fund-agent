# Evidence Confirm Productionization EC-P4 Slice 1 Code Review Fix

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `code-review fix`
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-code-review-fix-20260622.md`
- Release/readiness: `NOT_READY`

## Accepted Findings Mapping

| Finding | Status | Fix |
|---|---|---|
| DS-ECP4S1-01 HIGH | fixed in current slice | `hard_gate.informational_issue_ids` now maps into `EvidenceConfirmProductionSummary.warning_issue_ids`. The field docstring and helper docstring state that `warning_issue_ids` means production-visible nonblocking issue ids and includes reviewable plus informational IDs. This is the preferred minimal fix; no schema-version bump or new public field was needed. |
| DS-ECP4S1-02 MEDIUM | fixed in current slice | Added production-summary tests for pass path, warn path, stable not-run reason variants, invalid reason, invalid policy, and deterministic `not_applicable` aggregation boundary. |
| DS-ECP4S1-03 MEDIUM | fixed in current slice | `_ecq_policy_severity()` now raises `ValueError` when a `policy="off"` fail/warn summary reaches ECQ fail projection, preventing silent downgrade to warn. |
| MiMo F-01 LOW | fixed in current slice | Added explicit `evidence_confirm_summary=None` integration test proving `run_quality_gate_for_bundle()` produces no ECQ issues on the default absent-summary path. |
| MiMo F-02 LOW | fixed in current slice | Added pathway failure integration test proving `pathway_status="fail"` + `policy="block"` projects to `ECQ1/block`. |
| MiMo F-03 INFO | fixed in current slice | Added warn-policy deterministic fail integration test proving `ECQ2/warn`. |
| MiMo F-04 INFO | fixed in current slice | Guard and docstring in `_ecq_policy_severity()` make off-policy fail/warn handling explicit. |

## Changed Files

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/fund/quality_gate_integration.py`
- `tests/fund/test_evidence_confirm_production.py`
- `tests/fund/test_quality_gate_integration.py`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-code-review-fix-20260622.md`

No Service/UI/renderer/CLI/control docs, repository/source/PDF/cache/source adapter/parser/Docling/provider modules, or `extraction_score.py` / `score.json` schema behavior were modified by this fix gate.

## Validation

Command:

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

Output:

```text
........................................................                 [100%]
56 passed in 0.83s
```

Command:

```text
uv run ruff check fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
```

Output:

```text
All checks passed!
```

Command:

```text
git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py docs/reviews/evidence-confirm-productionization-ec-p4-slice1-code-review-fix-20260622.md
```

Output:

```text
<no output; command passed>
```

## Residual Risks

| Risk | Classification | Owner |
|---|---|---|
| Service propagation remains unimplemented in this fix gate. | covered by later approved slice | Slice 2 Service owner |
| CLI/UI summary and exit behavior remain unimplemented in this fix gate. | covered by later approved slice | Slice 3 UI owner |
| Renderer non-rendering guard remains unimplemented in this fix gate. | covered by later approved slice | Slice 4 renderer owner |
| Semantic companion propagation remains unimplemented in this fix gate. | covered by later approved slice | Slice 5 semantic owner, if still inside accepted injected-result boundary |
| Release/readiness remains `NOT_READY`. | assigned to later work unit | Controller/release owner |

## Verdict

`EC_P4_SLICE1_FIX_READY_FOR_REREVIEW_NOT_READY`
