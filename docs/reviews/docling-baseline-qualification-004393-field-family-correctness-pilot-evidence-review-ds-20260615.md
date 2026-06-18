# 004393 Field-family Correctness Pilot Evidence Review - DS - 2026-06-15

Gate: `004393 Field-family Correctness Pilot Evidence Gate`  
Role: DS review worker  
Release/readiness: `NOT_READY`

## 1. Reviewed Artifact

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-20260615.md`
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json`

## 2. Initial Findings

| Severity | Finding | Disposition |
| --- | --- | --- |
| High | Evidence extraction command was initially only a command shape, without exact crop/review command, output path, or independently checkable same-source excerpt chain. | ACCEPT_FIXED |
| Medium | `pdf_cache_hit=False` plus direct-looking `cache/pdf/...` path needed explanation to avoid being read as cache bypass. | ACCEPT_FIXED |

## 3. Targeted Re-review Result

Verdict: `PASS`

Unclosed findings: none.

Accepted closure points:

- Evidence artifact records reviewed-facts output, output path, and SHA-256.
- Local checked SHA-256 for `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` is `8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb`.
- Section 3 records actual extraction command, `FACTS` tuple, input JSONs, output JSON, hash calculation, and observed output.
- Section 2 explains that `cache/pdf/004393_2025_annual_report_eid.pdf` came from `document.metadata.cache.pdf_path` after `FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)` succeeded.
- Section 2 explains `pdf_cache_hit=False` and does not present it as direct cache bypass.

## 4. Accepted Points

- Evidence uses same-source repository-loaded annual-report PDF crop excerpts, not parser-vs-parser agreement.
- Docling result is bounded to selected reviewed facts and is not promoted to source truth, production parser replacement, full field correctness, readiness, release, or PR.
- pdfplumber mismatch is limited to selected comparator locator/crop rows and is not generalized to all pdfplumber extraction.
- EID HTML remains blocked/deferred and is not part of this correctness claim.

## 5. Residuals

- Bounded pilot does not cover full annual-report correctness.
- PDF crop excerpts are local same-source excerpts, not human visual screenshots.
- Production integration still requires a separate design and implementation gate.

## 6. Final Verdict

`VERDICT: PASS_004393_FIELD_FAMILY_CORRECTNESS_PILOT_EVIDENCE_NOT_READY`
