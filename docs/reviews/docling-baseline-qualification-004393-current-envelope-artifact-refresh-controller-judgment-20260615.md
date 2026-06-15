# 004393 Current-envelope Candidate Artifact Refresh Controller Judgment - 2026-06-15

Gate: `004393 Current-envelope Candidate Artifact Refresh No-live Implementation/Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the no-live Path A current-envelope refresh for the user-designated fund:

- `004393` / 安信企业价值优选混合A
- report year: `2025`

Reviewed evidence:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-evidence-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-current-envelope-artifact-refresh-review-mimo-20260615.md`

## 2. Accepted Outputs

| Output | Decision |
| --- | --- |
| `reports/representation-json/004393_2025_docling_current_envelope.json` | ACCEPT |
| `reports/representation-json/004393_2025_pdfplumber_current_envelope.json` | ACCEPT |
| `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json` | ACCEPT |
| `reports/representation-json/004393-current-envelope-refresh-manifest-20260615.json` | ACCEPT_AS_WRAPPER_SPECIFIC_MANIFEST |

## 3. Accepted Facts

- Path A no-conversion wrapper succeeded.
- No legacy `004393_2025_*_full.json` artifact was overwritten.
- Docling current-envelope output projects as:
  - 25 sections
  - 95 tables
  - 3,493 cells
  - 3,493 page locators
  - 3,493 bbox locators
  - 3,493 row/column locators
  - 524 header-flag cells
- pdfplumber current-envelope output projects as:
  - 8 sections
  - 92 tables
  - 3,640 cells
  - 3,640 page locators
  - 3,426 bbox locators
  - 3,640 row/column locators
  - 0 header-flag cells
- EID HTML output remains blocked:
  - 0 sections
  - 0 tables
  - 0 cells
  - route failure `eid_html_current_envelope_mapping_deferred`

## 4. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Wrapper manifest is not generic export manifest shape. | MiMo review | ACCEPTED_RESIDUAL | Plan allowed Path A wrapper-specific manifest. It must not be treated as `CandidateRepresentationExportManifest`. |
| Raw output cell `locator_hash` may be null. | MiMo review | ACCEPTED_RESIDUAL | Evidence does not rely on locator-hash completeness; projection can derive hashes for internal use. |
| Review did not re-read legacy JSON/PDF body. | DS review | ACCEPTED_RESIDUAL | Gate scope is current-envelope artifact/evidence consistency and boundary review, not field correctness/PDF truth. |

## 5. Boundary Decision

Accepted outputs are candidate artifacts only.

They do not prove:

- field correctness
- source truth
- taxonomy compatibility
- production parser replacement
- public `EvidenceAnchor` compatibility
- release/readiness

They do not authorize:

- production `FundDocumentRepository` behavior changes
- Service/Host/UI/renderer/quality gate consumption
- EID HTML table-bearing mapping
- live/network/provider/LLM commands

## 6. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

Projection validation:

```text
004393_2025_docling_current_envelope.json -> 25 sections / 95 tables / 3493 cells
004393_2025_pdfplumber_current_envelope.json -> 8 sections / 92 tables / 3640 cells
004393_2025_eid_html_render_blocked_current_envelope.json -> 0 sections / 0 tables / 0 cells
```

## 7. Final Verdict

`VERDICT: ACCEPT_004393_CURRENT_ENVELOPE_REFRESH_PATH_A_NOT_READY`

Next recommended gate:

`004393 Current-envelope Locator Stability Evidence Gate`

Do not proceed to field correctness, production integration, parser replacement, readiness, release, PR, or EID HTML table-bearing mapping from this gate.
