# 004393 Current-envelope Candidate Artifact Refresh Evidence - 2026-06-15

Gate: `004393 Current-envelope Candidate Artifact Refresh No-live Implementation/Evidence Gate`
Role: implementation/evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This gate executed Path A from the accepted plan: no-conversion current-envelope wrapper.

No Docling conversion, pdfplumber extraction, PDF body read, EID/network/live/provider/LLM command, production repository change, parser replacement, Service/Host/UI/renderer/quality gate change, or public `EvidenceAnchor` change was performed.

## 2. Accepted Plan Basis

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-plan-controller-judgment-20260615.md`

## 3. Inputs

Read-only legacy / route-specific inputs:

| Input | Status |
| --- | --- |
| `reports/representation-json/004393_2025_docling_full.json` | Legacy Route A JSON, no current envelope schema version. |
| `reports/representation-json/004393_2025_pdfplumber_full.json` | Legacy Route A JSON, no current envelope schema version. |
| `reports/representation-json/004393_2025_eid_html_render_full.json` | Route-specific EID HTML render JSON, not current candidate envelope. |

These inputs were treated as candidate structural artifacts only, not source truth or field correctness proof.

## 4. Outputs

| Output | Size | SHA-256 |
| --- | ---: | --- |
| `reports/representation-json/004393_2025_docling_current_envelope.json` | 3,102,753 bytes | `f4ea5e1fa028a364c2286a9244e7d482c4851afbcefb506c5b5b08db4ff02d28` |
| `reports/representation-json/004393_2025_pdfplumber_current_envelope.json` | 4,836,739 bytes | `c0fa747e157098efe6ca5c2ca4d68e47f64e22b2e63a7aeedb4d5aa547393794` |
| `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json` | 1,976 bytes | `6f0f6f52da5cad5ba14a5b1c7ebcbf87e8085c83ca7f42552f5a1770553a7d42` |
| `reports/representation-json/004393-current-envelope-refresh-manifest-20260615.json` | 1,134 bytes | `ce56736f952a0d024078345629e9a6e61116cd6dbb5e7d9f8c78d3e2fe91df1b` |

No existing legacy JSON path was overwritten.

## 5. Mapping Rules

Docling:

- legacy sections mapped to current `sections`;
- legacy text blocks mapped to current `text_blocks`;
- legacy tables/cells mapped to current `tables[].cells`;
- page number, bbox, row/column offsets, row/column spans, row/column header flags, content hash, and table/cell identifiers were preserved when explicitly present.

pdfplumber:

- legacy sections mapped to current `sections`;
- legacy text blocks mapped to current `text_blocks`;
- legacy tables/cells mapped to current `tables[].cells`;
- page number, bbox where present, row/column coordinates, and content hash were preserved when explicitly present;
- no header flags were invented.

EID HTML:

- emitted only as blocked current-envelope artifact;
- zero sections/tables/cells;
- route failure: `eid_html_current_envelope_mapping_deferred`;
- no table-bearing EID HTML current-envelope mapping was performed.

## 6. Projection Validation

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
    print(name, len(doc.sections), len(doc.tables), len(cells))
PY
```

Result:

| Output | Source kind | Sections | Tables | Cells | Cell page locators | Cell bbox locators | Cell row/column locators | Header-flag cells | Route failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `004393_2025_docling_current_envelope.json` | `docling_pdf_candidate` | 25 | 95 | 3,493 | 3,493 | 3,493 | 3,493 | 524 | none |
| `004393_2025_pdfplumber_current_envelope.json` | `pdfplumber_pdf_candidate` | 8 | 92 | 3,640 | 3,640 | 3,426 | 3,640 | 0 | none |
| `004393_2025_eid_html_render_blocked_current_envelope.json` | `eid_xbrl_html_render_candidate` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `eid_html_current_envelope_mapping_deferred` |

## 7. Boundary Checks

- `candidate_status`: `not_proven`
- `field_correctness_status`: `not_proven`
- `source_truth_status`: `not_proven`
- `taxonomy_compatibility_status`: `not_proven`
- `production_parser_replacement_status`: `not_authorized`
- blocked claims retained by current envelope construction
- EID HTML remains blocked, not table-bearing
- release/readiness remains `NOT_READY`

## 8. Validation Commands

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 9. Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Path A wrapper does not prove values match PDF. | Accepted residual | Field-family correctness pilot. |
| Path A wrapper depends on legacy diagnostic structure for 004393. | Accepted residual | Do not treat as source truth; use only current-envelope candidate proof. |
| EID HTML table-bearing mapping remains deferred. | Accepted residual | Separate EID HTML Candidate Envelope Mapping Gate. |
| Production integration remains unauthorized. | Accepted residual | Separate production design/implementation gate. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No release/readiness/PR claim. |

## 10. Verdict Candidate

`IMPLEMENTATION_EVIDENCE_READY_FOR_REVIEW_NOT_READY`

Recommended next gate:

`004393 Current-envelope Candidate Artifact Refresh Review Gate`
