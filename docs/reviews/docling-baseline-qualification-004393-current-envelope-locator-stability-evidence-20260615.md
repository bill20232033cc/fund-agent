# 004393 Current-envelope Locator Stability Evidence - 2026-06-15

Gate: `004393 Current-envelope Locator Stability Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This evidence evaluates locator stability for the accepted `004393_2025` current-envelope candidate artifacts.

It does not:

- compare extracted values to PDF
- claim field correctness
- claim source truth
- authorize parser replacement
- change production repository/parser behavior
- expose candidate internals to Service/Host/UI/renderer/quality gate
- change readiness/release status

## 2. Inputs

Accepted refresh checkpoint:

- `1e055fa gateflow: accept 004393 current envelope refresh`

Accepted artifacts:

- `reports/representation-json/004393_2025_docling_current_envelope.json`
- `reports/representation-json/004393_2025_pdfplumber_current_envelope.json`
- `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-controller-judgment-20260615.md`

## 3. Evidence

| Source kind | Sections | Tables | Cells | Cell page rate | Cell bbox rate | Cell row/column rate | Header-flag cells | Route failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `docling_pdf_candidate` | 25 | 95 | 3,493 | 100% | 100% | 100% | 524 | none |
| `pdfplumber_pdf_candidate` | 8 | 92 | 3,640 | 100% | 94.1% | 100% | 0 | none |
| `eid_xbrl_html_render_candidate` | 0 | 0 | 0 | n/a | n/a | n/a | 0 | `eid_html_current_envelope_mapping_deferred` |

## 4. Classification

| Source kind | Classification | Reason |
| --- | --- | --- |
| `docling_pdf_candidate` | `stable_for_004393_candidate_locator_evidence` | All 3,493 projected cells have page, bbox, and row/column locators; 524 cells preserve explicit header flags. |
| `pdfplumber_pdf_candidate` | `partly_stable_for_004393_candidate_locator_evidence` | All 3,640 cells have page and row/column locators; 3,426 cells have bbox; no header flags are present or invented. |
| `eid_xbrl_html_render_candidate` | `blocked_for_004393_current_envelope` | EID HTML remains blocked pending separate EID HTML Candidate Envelope Mapping Gate. |

## 5. Decision Support

004393 now satisfies the current-envelope locator prerequisite for a later field-family correctness pilot, with Docling as the candidate-layer structural locator baseline and pdfplumber as comparator.

This is not:

- correctness proof
- source truth proof
- production integration approval
- readiness/release proof

## 6. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Field correctness remains unproven. | Deferred | `004393 Field-family Correctness Pilot Planning Gate` |
| EID HTML table-bearing current-envelope mapping remains deferred. | Deferred | Separate EID HTML Candidate Envelope Mapping Gate. |
| Production consumption remains unauthorized. | Deferred | Production integration design gate only after correctness/design acceptance. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Controller |

## 7. Validation

Command:

```text
uv run python - <<'PY'
from pathlib import Path
import json
from fund_agent.fund.documents.candidates.representation_projection import project_candidate_representation

for name in [
    "004393_2025_docling_current_envelope.json",
    "004393_2025_pdfplumber_current_envelope.json",
    "004393_2025_eid_html_render_blocked_current_envelope.json",
]:
    payload = json.loads((Path("reports/representation-json") / name).read_text(encoding="utf-8"))
    doc = project_candidate_representation(payload)
    cells = [cell for table in doc.tables for cell in table.cells]
    print(
        name,
        len(doc.sections),
        len(doc.tables),
        len(cells),
        sum(cell.source_locator.page_number is not None for cell in cells),
        sum(cell.source_locator.bbox is not None for cell in cells),
        sum(cell.row_start is not None and cell.column_start is not None for cell in cells),
        sum(cell.row_header or cell.column_header for cell in cells),
        [failure.failure_code for failure in doc.route_failures],
    )
PY
```

Result:

```text
004393_2025_docling_current_envelope.json -> 25 sections / 95 tables / 3493 cells
004393_2025_pdfplumber_current_envelope.json -> 8 sections / 92 tables / 3640 cells
004393_2025_eid_html_render_blocked_current_envelope.json -> 0 sections / 0 tables / 0 cells
```

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 8. Verdict Candidate

`EVIDENCE_SUPPORTS_004393_LOCATOR_STABILITY_FOR_FIELD_CORRECTNESS_PLANNING_NOT_READY`

Recommended next gate:

`004393 Field-family Correctness Pilot Planning Gate`
