# Candidate Representation Schema No-live Implementation Controller Judgment - 2026-06-15

Gate: `Candidate Representation Schema No-live Implementation Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the no-live implementation gate for the Fund documents internal candidate representation schema and projection layer.

Reviewed implementation evidence:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-evidence-20260615.md`

Reviewed files:

- `fund_agent/fund/documents/candidates/representation_models.py`
- `fund_agent/fund/documents/candidates/representation_projection.py`
- `tests/fund/documents/test_candidate_representation_models.py`
- `tests/fund/documents/test_candidate_representation_projection.py`
- `fund_agent/fund/README.md`

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`

## 3. Accepted Implementation Facts

- Candidate source kinds remain closed to:
  - `docling_pdf_candidate`
  - `pdfplumber_pdf_candidate`
  - `eid_xbrl_html_render_candidate`
- The implementation adds candidate-internal dataclasses only.
- Projection consumes existing candidate representation JSON-like payloads only.
- Docling projection preserves page number, source ref, bbox, row/column offsets, row/column header flags, hashes, and locator fields when present.
- pdfplumber projection can synthesize table cells from `headers` + `rows` without inventing bbox or header flags.
- EID HTML blocked route remains a route failure without creating table facts.
- Candidate anchor note is internal and does not modify public `EvidenceAnchor`.
- All candidate status fields remain non-proof.

## 4. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Zero-valued row/column offsets could be dropped. | MiMo `MIMO-IMPL-F1` | ACCEPT_FIXED | Projection now uses first-present semantics and tests assert zero-based locators survive. MiMo targeted re-review passed. |
| Tests did not cover zero-valued locators. | MiMo `MIMO-IMPL-F2` | ACCEPT_FIXED | Docling and pdfplumber projection tests now assert zero row/column locator preservation. MiMo targeted re-review passed. |
| Docling row/column header flags were not preserved. | DS `DS-IMPL-F1` | ACCEPT_FIXED | `CandidateTableCell` now carries `row_header` and `column_header`; projection maps both; tests assert preservation and default false behavior. DS targeted re-review passed. |

## 5. Validation

Command:

```text
uv run pytest tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
11 passed in 0.47s
```

Command:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
35 passed in 2.51s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_models.py fund_agent/fund/documents/candidates/representation_projection.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 6. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Locator stability is represented but not empirically accepted across the full candidate sample set. | Deferred | `Candidate Representation Locator Stability Evidence Gate` |
| Field correctness remains unproven. | Deferred | Later field-family correctness pilot only after locator evidence. |
| Candidate schema does not authorize production parser replacement. | Accepted residual | Preserve `production_parser_replacement_status=not_authorized`. |
| EID HTML render route remains blocked for samples without accepted render payload. | Accepted residual | Separate EID HTML artifact evidence/design gate if resumed. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No readiness/release/PR claim. |

## 7. Final Verdict

`VERDICT: ACCEPT_IMPLEMENTATION_READY_FOR_LOCATOR_STABILITY_EVIDENCE_GATE_NOT_READY`

Next recommended gate:

`Candidate Representation Locator Stability Evidence Gate`

Do not proceed to production integration, parser replacement, field correctness promotion, readiness, release or PR from this gate.
