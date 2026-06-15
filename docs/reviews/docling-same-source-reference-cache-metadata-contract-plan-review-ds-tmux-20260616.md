# Docling Same-source Reference Cache Metadata Contract Plan Review - AgentDS - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Contract Planning Gate`
Role: `AgentDS plan review worker`
Release/readiness: `NOT_READY`
Verdict: `PASS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

## Scope

Review only `docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-20260616.md` against five focus areas prescribed by the controller:

1. Does the plan correctly reject current unsafe APIs: `load_annual_report`, `load_parsed_report`, `get_pdf_entry`/`get_pdf_path` as public evidence routes?
2. Does it preserve `FundDocumentRepository` boundary and avoid encouraging cache internals as an evidence route without implementation contract?
3. Are allowed metadata fields narrow enough and no path/body/source-helper/live/PDF leakage allowed?
4. Is the recommended next gate appropriately implementation planning/implementation before evidence, rather than direct cache probe?
5. Does it preserve `NOT_READY`, no source truth, no field correctness, no parser replacement?

This review does not modify source, tests, runtime, control docs, or design docs. It does not run FDR/cache/repository probes, PDF/live/network/Docling/pdfplumber/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge.

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Repository execution rules, FundDocumentRepository boundary, fallback policy |
| `docs/current-startup-packet.md` | Current gate identity, NOT_READY state |
| `docs/implementation-control.md` | Control truth, current gate scope and non-goals |
| `docs/reviews/docling-multi-sample-same-source-reference-availability-artifact-only-evidence-controller-judgment-20260616.md` | Prior controller judgment establishing Route B unresolved, metadata-only contract required |
| `fund_agent/fund/documents/repository.py` | Actual `load_annual_report()` behavior: can call fetch_pdf, fetch_pdf_path, parse_pdf, load_parsed_report |
| `fund_agent/fund/documents/cache.py` | Actual cache API surface: `get_pdf_entry()` exposes pdf_path, `load_parsed_report()` reads body |
| `fund_agent/fund/documents/models.py` | `AnnualReportSourceMetadata` full field set, `AnnualReportCacheProvenance` contains pdf_path |

## Findings

### F1 — Existing API Safety Assessment Is Correct (PASS)

The plan correctly identifies four existing APIs as unsafe for metadata-only proof:

| API | Plan judgment | Code verification |
|---|---|---|
| `FundDocumentRepository.load_annual_report()` | Not safe | Confirmed: `repository.py:317` can call `fetch_pdf`/`fetch_pdf_path` (lines 379-399), `parse_pdf` (line 401), `load_parsed_report` (line 351), and `save_parsed_report` (line 413) depending on cache state |
| `AnnualReportDocumentCache.load_parsed_report()` | Not safe; body read | Confirmed: `cache.py:434` deserializes full `ParsedAnnualReport` from JSON payload, including `raw_text`, `sections`, `tables` |
| `AnnualReportDocumentCache.get_pdf_entry()` | Not safe; path exposure | Confirmed: `cache.py:295` returns `AnnualReportPdfCacheEntry(pdf_path, source_metadata, updated_at)` and internally calls `pdf_path.exists()` (line 353) |
| `AnnualReportDocumentCache.get_pdf_path()` | Not safe | Confirmed: `cache.py:278` returns `Path` directly |

The "Explicit Forbidden Access" section (plan lines 83-93) systematically enumerates all forbidden call surfaces: parsed report body, PDF path/body/metadata, source helpers/adapters, live/network, `parse_pdf`, `load_annual_report`, `load_parsed_report`, Docling, pdfplumber, provider/LLM/analyze/checklist/golden/readiness/release. Each prohibition is verifiable against the actual code.

### F2 — Repository Boundary Is Preserved (PASS)

The plan correctly identifies Option B (repository facade) as preferable: "This keeps future callers aligned with the repository boundary while preventing `load_annual_report()` execution" (plan line 120).

The plan cites `AGENTS.md` requirement: "production annual-report access must go through `FundDocumentRepository`" (plan line 29). The recommended implementation slices sequence Slice 1 (cache-internal metadata reader) → Slice 2 (repository-safe facade) → Slice 3 (metadata-only evidence gate), ensuring the evidence worker calls the repository facade, not cache internals directly.

Option C (cache-internal method only) is correctly flagged as "narrower but weaker against boundary drift" (plan line 126). The plan does not encourage direct cache-internal access as an evidence route without a repository contract.

### F3 — Allowed Metadata Fields Are Narrow and Leak-Free (PASS)

The allowed fields (plan lines 63-75) are limited to identity (`fund_code`, `document_year`, `report_type`) and EID single-source policy attestation fields (`source`, `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, `primary_failure_category`), plus an optional tamper-evident hash.

Fields present in `AnnualReportSourceMetadata` (models.py lines 52-71) that are correctly **excluded**:
- `source_url`, `fund_id`, `report_code`, `report_desp`, `report_name`
- `upload_info_id`, `upload_info_detail_id`, `table_name`
- `report_send_date`, `operation_upload_type`, `corrections_num`
- `discovery_contract_version`

Path policy (plan lines 77-81) explicitly forbids: PDF path, parsed payload path, cache root, filename, local corpus path, file-existence result. The `AnnualReportCacheProvenance.pdf_path` field (models.py line 165) is correctly blocked from public return.

The mandatory invariants (plan lines 159-163) align precisely with the existing `_is_current_eid_single_source_metadata()` function in `repository.py:267-291`, which checks the same six conditions. This means the implementation can reuse existing validation without duplicating policy logic.

### F4 — Implementation Sequencing Is Correct (PASS)

The plan sequences three implementation slices (lines 166-213):
1. Cache metadata reader — add bodyless query to `cache.py`
2. Repository-safe facade — add repository method delegating to cache metadata
3. Metadata-only evidence gate — call accepted method for S4/S5/S6

Slice 3 is gated on Slice 1+2 being complete. The next gate recommendation is "Docling Same-source Reference Cache Metadata No-live Implementation Gate" (plan line 253), not a direct cache probe or evidence gate. This correctly enforces implementation-before-evidence ordering.

The stop conditions (plan lines 239-246) include: requiring `load_annual_report`/`load_parsed_report`/`get_pdf_path`/`get_pdf_entry` as public evidence API, PDF path/body access, source helper/adapters, live/network, Docling, pdfplumber — any of which would halt the gate. These are correct negative guardrails.

### F5 — NOT_READY and Non-claims Are Preserved (PASS)

The plan states `Release/readiness: NOT_READY` at line 5 and its own verdict as `PLAN_METADATA_ONLY_CONTRACT_REQUIRED_NOT_READY` at line 6. Non-goals (plan lines 21-25) explicitly disclaim source truth, field correctness, full correctness, taxonomy compatibility, raw XML availability, parser replacement, Docling baseline promotion, and release readiness. These are preserved throughout.

The hash is correctly qualified as "not source truth and not content correctness proof" (plan line 81). The validation matrix (plan lines 230-235) treats the future evidence gate as producing per-sample `available`/`missing`/`unsafe_metadata` status, not correctness proof.

### F6 — Contract Alignment with Existing Code (PASS — positive)

The plan's `available` condition invokes the same six-field check as `repository.py:_is_current_eid_single_source_metadata()` (lines 267-291):

```text
source == "eid" AND fallback_used == False AND primary_failure_category is None
AND selected_source == "eid" AND source_mode == "single_source_only"
AND fallback_enabled == False
```

This is an exact match. The implementation can call the existing helper rather than reimplementing the policy check, reducing drift risk.

### F7 — DocumentKey Identity Coverage (NOTE — implementation detail)

The SQLite `documents` table (cache.py lines 232-240) stores `fund_code`, `year`, `document_kind` as separate columns, and the `parsed_reports` table (cache.py lines 243-254) has the same three columns. The plan correctly identifies that identity matching on exact `(fund_code, year, document_kind)` is feasible from the SQLite schema. The `report_type` field in the evidence contract maps to `DocumentKey.document_kind` (currently always `ANNUAL_REPORT_DOCUMENT_KIND = "annual_report"`).

The implementation gate should clarify whether "available" requires only the `documents` row (which carries `source_metadata_json`), or both `documents` and `parsed_reports` rows. Since `source_metadata_json` lives in the `documents` table, it is the authoritative source for this metadata-only contract; `parsed_reports` row presence is a secondary signal about whether a parsed body was cached. This is not a plan defect — it is an appropriate implementation-level decision for the next gate.

## Required Amendments

None. The plan is internally consistent, correctly rejects unsafe APIs, preserves the repository boundary, defines appropriately narrow allowed fields with explicit path/body/live/PDF prohibitions, sequences implementation before evidence, and preserves NOT_READY with no overclaimed source truth, field correctness, or parser replacement.

The minor clarification about cross-table semantics (F7) is an implementation detail appropriately deferred to the no-live implementation gate. The report_type/document_kind naming difference is a cosmetic user-facing-vs-code naming choice that the implementation gate can resolve.

## Deferred Risks

| Risk | Severity | Why deferred |
|---|---|---|
| SQLite `documents` vs `parsed_reports` cross-table semantics for `available` status | Low | `source_metadata_json` is in `documents` table; implementation gate can decide whether parsed_reports row presence is required or advisory |
| `report_type` / `document_kind` naming inconsistency in evidence record vs code | Low | Plan already clarifies derivation (plan line 68); implementation gate resolves final naming |
| Concurrent write safety during metadata query | Low | Read-only SQLite query under default WAL/journal locking; no plan-level risk |
| Hash canonical JSON stability across Python versions | Very Low | Allowed fields are simple strings/ints/bools/nulls; JSON key ordering is deterministic in Python 3.7+ |
| Stale cache metadata after external cache mutation | Not a plan risk | Cache metadata reflects cache state at query time; staleness is inherent to any cache contract |

## Verdict

```text
VERDICT: PASS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY
```

The plan correctly rejects `load_annual_report`, `load_parsed_report`, `get_pdf_entry`, and `get_pdf_path` as unsafe for metadata-only proof. It preserves the `FundDocumentRepository` boundary by recommending a repository facade over cache-internal access. Allowed metadata fields are narrow (identity + EID single-source attestation) with explicit prohibitions on path, body, source-helper, live, and PDF leakage. The next gate is correctly sequenced as implementation before evidence. `NOT_READY`, no source truth, no field correctness, and no parser replacement are preserved throughout.

No source, test, runtime, control, or design files were modified. No FDR/cache/repository probe, PDF/live/network/Docling/pdfplumber/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge command was run.
