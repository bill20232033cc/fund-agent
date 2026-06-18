# Docling Same-source Reference Cache Metadata Evidence — DS Review - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Evidence Gate`
Reviewer: AgentDS
Release/readiness: `NOT_READY`
Verdict: `PASS_BLOCKED_EVIDENCE_ACCEPTABLE_NOT_READY`

## Scope

This review assesses the evidence artifact `docs/reviews/docling-same-source-reference-cache-metadata-evidence-20260616.md` against the accepted controller judgment `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-controller-judgment-20260616.md`, the implementation in `fund_agent/fund/documents/repository.py` and `fund_agent/fund/documents/cache.py`, and the gate scope defined in `docs/implementation-control.md` and `docs/current-startup-packet.md`.

Only allowed checks were executed: `git diff --check` on the evidence file (passed). No live/network/EID/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were run.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-20260616.md` | Under review |
| `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-controller-judgment-20260616.md` | Accepted controller judgment defining gate scope |
| `fund_agent/fund/documents/repository.py` | Implementation: `get_annual_report_reference_metadata()` facade |
| `fund_agent/fund/documents/cache.py` | Implementation: `get_reference_metadata()` metadata-only query |

## Findings

### F1 — Repository boundary (PASS)

The evidence command calls only `FundDocumentRepository.get_annual_report_reference_metadata(fund_code, year)`. It does not call `load_annual_report()`, any cache method directly, any PDF path access, or any parsed body access.

Repository facade at `repository.py:421-447` delegates to `self._cache.get_reference_metadata(document_key)`. Cache method at `cache.py:358-378` calls `_get_reference_metadata_sync`. The sync method at `cache.py:380-432` selects only `fund_code, year, document_kind, source_metadata_json` from `documents` table — no `pdf_path` column, no `parsed_reports` table join. This is verified against the implementation source.

### F2 — Forbidden access paths avoided (PASS)

The evidence does not:
- Call `load_annual_report()`
- Access cache internals (`_get_pdf_entry_sync`, `_load_parsed_report_sync`, `get_pdf_path`, `get_pdf_entry`)
- Read PDF paths or PDF file metadata
- Read parsed report payloads, sections, or body text
- Execute live/network/EID acquisition
- Run Docling conversion or pdfplumber export
- Call provider/LLM/analyze/checklist/golden/readiness/release commands

The evidence scope claim at evidence line 16 matches actual command behavior.

### F3 — S4/S5/S6 status interpretation (PASS)

All three samples return `unsafe_metadata`:

| Sample | Fund | Year | Status | Reason |
| --- | --- | --- | --- | --- |
| S4 | `006597` | 2024 | `unsafe_metadata` | `selected_source_not_eid` |
| S5 | `017641` | 2024 | `unsafe_metadata` | `source_not_eid` |
| S6 | `110020` | 2024 | `unsafe_metadata` | `source_not_eid` |

The evidence correctly interprets that these do NOT prove EID source unavailability — they only prove local cache metadata is insufficient. The `_build_reference_metadata_result` logic at `cache.py:171-241` confirms the fail-closed chain: `selected_source_not_eid` (line 217-220) is reached when `source == "eid"` but `selected_source != "eid"`; `source_not_eid` (line 211-215) is reached when the top-level `source` field itself is not `"eid"`.

The evidence does not claim these results prove EID lacks public annual reports, nor does it use `unsafe_metadata` as a same-source proof.

### F4 — Non-claims coverage (PASS)

The evidence non-claims section (lines 91-98) correctly disclaims:
- Source truth
- Field correctness
- Full correctness
- Docling baseline promotion
- Production parser replacement
- Readiness/release proof
- Proof that EID lacks public annual reports
- Authorization for live/EID/PDF acquisition

All non-claims are true and complete.

### F5 — Next gate recommendation (PASS)

The three viable routes (lines 111-113) are correct and preserve `NOT_READY`:
1. Keep multi-sample correctness expansion blocked — consistent with current state.
2. Authorize controlled same-source reference acquisition — requires separate controller gate.
3. Narrow Docling baseline to `004393 / 2025` pilot — consistent with accepted bounded fact.

The prohibition on proceeding directly to correctness review, parser replacement, baseline promotion, readiness, release, PR, push or merge is correct and matches controller judgment scope.

### F6 — Residual ownership (PASS)

Three residuals (lines 102-106) are correctly owned and routed:
- S4/S5/S6 same-source reference proof → controller/future evidence gate
- Local cache metadata unsafe for S4/S5/S6 → future cache/evidence owner
- Multi-sample correctness expansion blocked → controller

### F7 — Verdict consistency (PASS)

Evidence verdict `BLOCKED_UNSAFE_METADATA_NOT_READY` is consistent with findings. `NOT_READY` is preserved throughout. Release/readiness is correctly stated as `NOT_READY` at line 5.

### F8 — Formal correctness (PASS)

- `git diff --check` passed with zero issues
- Command exit code reported as `0` — expected for metadata-only facade call
- Fund codes (`006597`, `017641`, `110020`) match the accepted multi-sample expansion plan: S4/S5/S6
- Years (`2024`) match the accepted plan
- Output format is valid JSON with correct structure matching `AnnualReportReferenceMetadataResult`

## Required Fixes

None. The evidence is clean, stays within gate scope, uses only the accepted facade, correctly interprets `unsafe_metadata` results, makes no overclaims, preserves `NOT_READY`, and recommends correct next steps.

## Deferred Risks

| Risk | Owner | Handling |
| --- | --- | --- |
| S4/S5/S6 same-source reference remains absent | Controller | Requires separate authorization gate before correctness review |
| Cache metadata does not prove parsed body co-availability | Future gate owner | Already recorded in controller judgment residuals |
| MiMo review not available | Controller | MiMo channel blocked in prior interactive prompt per controller judgment; DS review is the single review for this gate |

## Verdict

```text
VERDICT: PASS_BLOCKED_EVIDENCE_ACCEPTABLE_NOT_READY
```

The evidence correctly calls only the accepted metadata-only repository facade, avoids all forbidden access paths, correctly interprets `unsafe_metadata` for all three expansion samples, makes no overclaims, and recommends valid next steps. No fixes required.
