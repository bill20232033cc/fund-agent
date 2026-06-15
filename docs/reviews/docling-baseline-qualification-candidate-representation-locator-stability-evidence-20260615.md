# Candidate Representation Locator Stability Evidence - 2026-06-15

Gate: `Candidate Representation Locator Stability Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This evidence evaluates locator stability in already accepted candidate representation JSON artifacts.

It does not:

- run Docling conversion
- run pdfplumber extraction
- read PDF bodies
- access EID/network/live endpoints
- compare values to PDF
- claim field correctness
- claim source truth
- claim taxonomy compatibility
- authorize parser replacement
- modify `FundDocumentRepository`, parser, Service, Host, UI, renderer, quality gate, or public `EvidenceAnchor`

## 2. Inputs

Accepted implementation checkpoint:

- `5a189c6 gateflow: accept candidate representation schema implementation`

Accepted evidence and controller judgment:

- `docs/reviews/docling-baseline-qualification-full-representation-export-evidence-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-controller-judgment-20260615.md`

Candidate JSON directory:

- `reports/representation-json/`

Projectable current-schema files:

- `006597_2024_docling_full.json`
- `006597_2024_pdfplumber_full.json`
- `006597_2024_eid_html_render_blocked.json`
- `017641_2024_docling_full.json`
- `017641_2024_pdfplumber_full.json`
- `017641_2024_eid_html_render_blocked.json`
- `110020_2024_docling_full.json`
- `110020_2024_pdfplumber_full.json`
- `110020_2024_eid_html_render_blocked.json`

Non-projectable residual files:

| File | Reason |
| --- | --- |
| `004393_2025_docling_full.json` | Legacy Route A JSON; no current `candidate_annual_report_representation.v1` schema version. |
| `004393_2025_pdfplumber_full.json` | Legacy Route A JSON; no current `candidate_annual_report_representation.v1` schema version. |
| `004393_2025_eid_html_render_full.json` | EID HTML route-specific schema `eid_xbrl_html_render_candidate.full_representation.v1`, not the current candidate envelope. |
| `full-representation-export-manifest-20260615.json` | Manifest, not candidate representation envelope. |

These residuals are not used as locator stability proof.

## 3. Method

The evidence command loaded JSON files from `reports/representation-json/`, projected only files with schema version `candidate_annual_report_representation.v1` through:

- `fund_agent.fund.documents.candidates.representation_projection.project_candidate_representation`

For each projectable document it counted:

- sections
- tables
- cells
- table source refs
- table page locators
- table bbox locators
- cell page locators
- cell bbox locators
- cell row/column locators
- projected cell hash and locator hash availability
- row/column header flags
- route failures and projection issues

## 4. Per-sample Evidence

| Sample | Source kind | Sections | Tables | Cells | Cell page rate | Cell bbox rate | Cell row/column rate | Header-flag cells | Route failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `006597_2024` | `docling_pdf_candidate` | 229 | 96 | 2,759 | 100% | 100% | 100% | 495 | none |
| `006597_2024` | `pdfplumber_pdf_candidate` | 8 | 85 | 2,561 | 100% | 0% | 100% | 0 | none |
| `006597_2024` | `eid_xbrl_html_render_candidate` | 0 | 0 | 0 | n/a | n/a | n/a | 0 | `eid_xbrl_html_render_candidate_not_available` |
| `017641_2024` | `docling_pdf_candidate` | 208 | 121 | 7,060 | 100% | 100% | 100% | 609 | none |
| `017641_2024` | `pdfplumber_pdf_candidate` | 6 | 114 | 6,805 | 100% | 0% | 100% | 0 | none |
| `017641_2024` | `eid_xbrl_html_render_candidate` | 0 | 0 | 0 | n/a | n/a | n/a | 0 | `eid_xbrl_html_render_candidate_not_available` |
| `110020_2024` | `docling_pdf_candidate` | 222 | 124 | 5,940 | 100% | 100% | 100% | 739 | none |
| `110020_2024` | `pdfplumber_pdf_candidate` | 8 | 118 | 5,633 | 100% | 0% | 100% | 0 | none |
| `110020_2024` | `eid_xbrl_html_render_candidate` | 0 | 0 | 0 | n/a | n/a | n/a | 0 | `eid_xbrl_html_render_candidate_not_available` |

## 5. Aggregate Evidence

| Source kind | Samples | Sections | Tables | Cells | Cell page rate | Cell bbox rate | Cell row/column rate | Header-flag cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `docling_pdf_candidate` | 3 | 659 | 341 | 15,759 | 100% | 100% | 100% | 1,843 |
| `pdfplumber_pdf_candidate` | 3 | 22 | 317 | 14,999 | 100% | 0% | 100% | 0 |
| `eid_xbrl_html_render_candidate` | 3 | 0 | 0 | 0 | n/a | n/a | n/a | 0 |

## 6. Stability Classification

| Source kind | Classification | Basis |
| --- | --- | --- |
| `docling_pdf_candidate` | `stable_for_candidate_locator_evidence` | Across 3 current-schema samples, every projected cell has page, bbox, and row/column locator. The projection also provides cell/locator hashes, preserves section structure, and preserves header flags. |
| `pdfplumber_pdf_candidate` | `partly_stable_for_candidate_locator_evidence` | Across 3 current-schema samples, every projected cell has page and row/column locator, but bbox and header flags are absent. It remains useful as a text/table fallback candidate, not a baseline locator candidate. |
| `eid_xbrl_html_render_candidate` | `blocked_for_this_gate` | The 3 current-schema EID HTML sample entries are blocked artifacts, not table-bearing render payloads. The 004393 EID HTML full JSON uses a route-specific schema and is not current candidate envelope proof. |

## 7. Controller-usable Conclusion

Docling has enough no-live structural locator evidence to proceed as the baseline candidate for the next schema/design line.

This conclusion is limited to candidate locator stability. It is not:

- field correctness proof
- source truth proof
- taxonomy compatibility proof
- parser replacement authorization
- readiness proof
- release proof

pdfplumber remains a comparable partial candidate for page + row/column table extraction, but it lacks bbox and header-flag locator richness in this evidence set.

EID HTML render cannot be compared as a full candidate representation in this gate because the current-schema samples are blocked and the one table-bearing 004393 HTML artifact is not in the accepted candidate envelope schema.

## 8. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| `004393_2025` is the user-designated future test fund but its Docling/pdfplumber JSON files are legacy Route A schema in this evidence set. | Deferred | Regenerate or wrap `004393_2025` into current `candidate_annual_report_representation.v1` envelope in a separate no-live artifact-refresh gate if needed. |
| EID HTML render has one route-specific full JSON but no current envelope table-bearing candidate sample. | Deferred | Separate EID HTML candidate envelope mapping gate. |
| Locator stability does not prove extracted value correctness. | Accepted residual | Field-family correctness pilot after baseline decision. |
| Production integration remains unauthorized. | Accepted residual | Separate production design/implementation gate. |

## 9. Validation

Command:

```text
uv run python - <<'PY'
import json
from collections import defaultdict
from pathlib import Path
from fund_agent.fund.documents.candidates.representation_export import ENVELOPE_SCHEMA_VERSION
from fund_agent.fund.documents.candidates.representation_projection import project_candidate_representation

agg = defaultdict(lambda: defaultdict(int))
rows = []
excluded = []
for path in sorted(Path("reports/representation-json").glob("*.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
        excluded.append(path.name)
        continue
    doc = project_candidate_representation(payload)
    cells = [cell for table in doc.tables for cell in table.cells]
    tables = list(doc.tables)
    kind = doc.identity.source_kind.value
    rows.append(
        {
            "sample": f"{doc.identity.fund_code}_{doc.identity.document_year}",
            "kind": kind,
            "sections": len(doc.sections),
            "tables": len(tables),
            "cells": len(cells),
            "cell_page": sum(c.source_locator.page_number is not None for c in cells),
            "cell_bbox": sum(c.source_locator.bbox is not None for c in cells),
            "cell_row_col": sum(
                c.row_start is not None and c.column_start is not None for c in cells
            ),
            "header_flags": sum(c.row_header or c.column_header for c in cells),
        }
    )
    agg[kind]["samples"] += 1
    agg[kind]["sections"] += rows[-1]["sections"]
    agg[kind]["tables"] += rows[-1]["tables"]
    agg[kind]["cells"] += rows[-1]["cells"]
    agg[kind]["cell_page"] += rows[-1]["cell_page"]
    agg[kind]["cell_bbox"] += rows[-1]["cell_bbox"]
    agg[kind]["cell_row_col"] += rows[-1]["cell_row_col"]
    agg[kind]["header_flags"] += rows[-1]["header_flags"]

for row in rows:
    print(json.dumps(row, ensure_ascii=False, sort_keys=True))
for kind, data in sorted(agg.items()):
    print(json.dumps({"kind": kind, **data}, ensure_ascii=False, sort_keys=True))
print(json.dumps({"excluded": excluded}, ensure_ascii=False, sort_keys=True))
PY
```

Result:

```text
3 Docling current-schema samples projectable.
3 pdfplumber current-schema samples projectable.
3 EID HTML current-schema blocked samples projectable.
4 files excluded as non-projectable residuals.
```

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 10. Verdict Candidate

`EVIDENCE_SUPPORTS_DOCLING_BASELINE_CANDIDATE_FOR_LOCATOR_STABILITY_NOT_READY`

Recommended next gate:

`Docling Baseline Candidate Decision Controller Gate`
