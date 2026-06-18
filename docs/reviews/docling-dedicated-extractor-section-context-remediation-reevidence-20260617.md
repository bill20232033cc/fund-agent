# Docling Dedicated Extractor Section-context Remediation Re-evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Section-context Remediation Re-evidence Gate`
Role: evidence worker
Accepted plan commit: `29f4fab`
Status: `REEVIDENCE_COMPLETE_NOT_READY`
Verdict: `SECTION_CONTEXT_REMEDIATION_COVERAGE_UPLIFT_NOT_READY`
Release/readiness: `NOT_READY`

## Evidence Artifact

- `reports/docling-dedicated-extractor-section-context-remediation-reevidence/20260617/template_field_coverage_after_section_context.json`

## Aggregate Result

| Metric | Before | After |
|---|---:|---:|
| Runnable samples | 4 | 4 |
| Target field slots | 92 | 92 |
| Direct slots | 0 | 48 |
| Missing slots | 92 | 44 |
| Candidate anchors | 0 | 52 |
| Direct coverage ratio | 0.0 | 0.5217391304347826 |

## Per-sample Direct Coverage

| Sample | Fund | Direct | Missing |
|---|---:|---:|---:|
| S1 | 004393 | 13 | 10 |
| S4 | 006597 | 12 | 11 |
| S5 | 017641 | 11 | 12 |
| S6 | 110020 | 12 | 11 |

## Fields With Non-zero Direct Hits

| Field | Direct count |
|---|---:|
| `basic_identity.fund_name` | 4 |
| `basic_identity.fund_code` | 4 |
| `basic_identity.management_company` | 4 |
| `basic_identity.custodian` | 4 |
| `product_profile.investment_objective` | 4 |
| `benchmark.benchmark_text` | 4 |
| `risk_characteristic_text.risk_characteristic_text` | 4 |
| `fee_schedule.management_fee` | 4 |
| `fee_schedule.custody_fee` | 4 |
| `portfolio_managers` | 4 |
| `manager_alignment.manager_holding_range` | 4 |
| `holdings_snapshot.top_holdings` | 2 |
| `holdings_snapshot.bond_top_holdings` | 2 |

## Interpretation

Accepted facts:

- Section-context remediation produces non-zero candidate field coverage on the same four real candidate envelopes.
- The primary diagnostic cause `section_candidates_exist_but_blocks_unlinked` is materially remediated for key/value and text/table label fields.
- Row/column label dependent fields remain limited.
- Direct hits remain candidate-only and do not prove field correctness.
- This evidence does not authorize baseline promotion, parser replacement, production integration, release readiness, or PR readiness.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
50 passed in 0.68s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

## Next Gate Recommendation

Proceed to:

`Docling Dedicated Extractor Row-column Label Derivation Planning Gate`

Purpose:

- derive row/column label paths for candidate table cells;
- target performance, manager, and holdings fields that still depend on table semantics;
- preserve candidate-only and `NOT_READY` boundaries.

VERDICT: `SECTION_CONTEXT_REMEDIATION_COVERAGE_UPLIFT_NOT_READY`
