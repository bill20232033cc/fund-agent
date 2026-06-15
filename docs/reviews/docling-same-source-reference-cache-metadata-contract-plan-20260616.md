# Docling Same-source Reference Cache Metadata Contract Plan - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Contract Planning Gate`
Role: `planning worker`
Release/readiness: `NOT_READY`
Verdict: `PLAN_METADATA_ONLY_CONTRACT_REQUIRED_NOT_READY`

## Scope

Design whether a future no-live, no-body, no-PDF metadata-only cache contract can safely establish same-source reference availability for:

| Sample | fund_code | document_year | report_type |
| --- | --- | ---: | --- |
| S4 | `006597` | 2024 | `annual_report` |
| S5 | `017641` | 2024 | `annual_report` |
| S6 | `110020` | 2024 | `annual_report` |

This plan is documentation only. It does not execute cache, repository, FDR, PDF, live/network, Docling, pdfplumber, provider, LLM, analyze, checklist, golden, readiness, release, PR, push or merge actions.

## Non-goals

- Do not modify source, tests, runtime, control docs, design docs, README, cache files, repository behavior, parser behavior, source policy, fallback behavior, `EvidenceAnchor`, Service/UI/Host/renderer/quality-gate behavior, readiness, release or PR state.
- Do not prove source truth, field correctness, full correctness, taxonomy compatibility, raw XML availability, parser replacement, Docling baseline promotion or release readiness.
- Do not inspect parsed report body content, raw text, sections, tables, table cells, evidence anchors, rendered report content, PDF body, PDF metadata or source adapter output.
- Do not use arbitrary untracked residue, candidate Docling/pdfplumber JSON, local PDF corpus, PDF paths, source helper internals or source adapters as proof.

## Truth Inputs

- `AGENTS.md`: production annual-report access must go through `FundDocumentRepository`; fallback decisions are fail-closed for `schema_drift`, `identity_mismatch` and `integrity_error`; current route must preserve evidence traceability and `NOT_READY`.
- `docs/current-startup-packet.md`: current active gate is this planning gate; S4/S5/S6 candidate JSON artifacts exist, but Route A found no accepted same-source reference artifact; Route B/FDR/cache metadata was not attempted or authorized.
- `docs/implementation-control.md`: current gate is planning-only; no FDR/cache metadata inspection/PDF/live/Docling/pdfplumber/manual review/correctness review is authorized; release/readiness remains `NOT_READY`.
- `docs/reviews/docling-multi-sample-same-source-reference-availability-proof-plan-controller-judgment-20260616.md`: Route B is unresolved and requires separate metadata-only authorization; if later authorized, only source metadata envelope fields may be accessed.
- `docs/reviews/docling-multi-sample-same-source-reference-availability-artifact-only-evidence-controller-judgment-20260616.md`: artifact-only evidence accepted `BLOCKED_NO_NO_LIVE_REFERENCE_PROOF_NOT_READY` for S4/S5/S6 and recommends this cache metadata contract planning gate.
- `fund_agent/fund/documents/repository.py`: `FundDocumentRepository.load_annual_report()` may read parsed report cache, fetch PDF, record PDF path, parse PDF and save parsed body depending on cache state; it is not a metadata-only proof method.
- `fund_agent/fund/documents/cache.py`: current cache methods expose either PDF entries with `pdf_path` or parsed report bodies. `load_parsed_report()` deserializes parsed payload body content and applies raw-text/section usability checks. `get_pdf_entry()` returns PDF path and checks path existence.
- `fund_agent/fund/documents/models.py`: `AnnualReportSourceMetadata` contains source provenance fields; `AnnualReportCacheProvenance` contains `pdf_path`, which must not be exposed by this contract.

## Why Artifact-only Evidence Is Blocked

Route A searched only accepted evidence-chain artifacts and found no accepted same-source reference artifact for S4/S5/S6. The accepted result is:

| Sample | Accepted Route A result | repository_attempted | no_live_proof_route |
| --- | --- | --- | --- |
| S4 | `blocked_no_accepted_artifact` | `false` | `none` |
| S5 | `blocked_no_accepted_artifact` | `false` | `none` |
| S6 | `blocked_no_accepted_artifact` | `false` | `none` |

Candidate Docling/pdfplumber outputs cannot fill this gap because they are candidate representations, not independent same-source reference proof. Untracked local PDFs or reports also cannot fill the gap because prior accepted judgments explicitly exclude arbitrary residue and PDF paths as proof. Therefore, a future route needs either an accepted external same-source reference artifact or a safe metadata-only cache contract that proves a cached repository reference is available without reading body/PDF/live state.

## Cache Metadata Contract Objective

Create a future narrow contract that can answer one question only:

```text
Does the local document cache contain an exact annual-report identity for fund_code/document_year/report_type whose source metadata proves the current EID single-source/no-fallback policy, without exposing PDF path/body or parsed body content?
```

The contract may support a future evidence gate that records `available`, `missing`, or `unsafe_metadata` per sample. It must not return any object that allows body inspection, PDF path access, PDF existence probing outside the contract, source-helper invocation or parser execution.

## Allowed Metadata Fields

The safe evidence record may contain only:

| Field | Contract rule |
| --- | --- |
| `fund_code` | Exact requested fund code after repository-equivalent normalization; must equal cache `DocumentKey.fund_code` and, if source metadata contains a fund code, `AnnualReportSourceMetadata.fund_code`. |
| `document_year` | Exact requested year; must equal cache `DocumentKey.year` and, if source metadata contains `report_year`, that value. |
| `report_type` | Stable normalized report type, currently only `annual_report`; derived from `DocumentKey.document_kind`, not from report body text. |
| `source` | Allowed only as source name, currently expected `eid`; no URL or adapter detail. |
| `selected_source` | Must be `eid` for current route. |
| `source_mode` | Must be `single_source_only`. |
| `fallback_enabled` | Must be `false`. |
| `fallback_used` | Must be `false`. |
| `primary_failure_category` | Must be `null`; any non-null value is `unsafe_metadata` for this proof. |
| `metadata_identity_hash` | Optional SHA-256 over the canonical JSON of the allowed fields above only. It must not include PDF path, payload path, source URL, body text, table data or timestamps. |

Path policy:

- No PDF path, parsed payload path, cache root, filename, local corpus path or file-existence result may be emitted.
- The implementation may internally use SQLite row presence and parsed-cache row presence only inside the metadata method, but the public return object must collapse this into `metadata_available=true/false` plus the allowed fields above.
- A hash is optional and is only a tamper-evident identity fingerprint for the metadata envelope. It is not source truth and not content correctness proof.

## Explicit Forbidden Access

A future evidence or implementation worker must not access:

- parsed report body content: `raw_text`, `sections`, `tables`, `table_cells`, `metadata.cache.pdf_path`, evidence anchors or rendered report content
- PDF path/body/metadata, PDF headers, page count, file size, mtime, `pdf_path.exists()` results in evidence output, local PDF corpus, or file hash over PDF bytes
- source helpers, source adapters, EID acquisition helpers, Eastmoney/fund-company/CNINFO fallback helpers or adapter discovery outputs
- live/network/EID/PDF acquisition
- `parse_pdf`
- `FundDocumentRepository.load_annual_report()` for this proof, because it can fetch/parse/save depending on cache state
- `AnnualReportDocumentCache.load_parsed_report()` for this proof, because it deserializes parsed report body and validates raw-text/section content
- Docling conversion, pdfplumber export, manual reference review, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge

## Existing API Safety Assessment

Existing APIs cannot be called safely as-is for this evidence gate.

| API | Current behavior | Safety judgment |
| --- | --- | --- |
| `FundDocumentRepository.load_annual_report()` | May return parsed body, call `load_parsed_report()`, read PDF cache, fetch PDF, call `parse_pdf()` and save parsed report. | Not safe for metadata-only proof. |
| `AnnualReportDocumentCache.load_parsed_report()` | Reads parsed JSON payload, constructs `ParsedAnnualReport`, checks raw text length and required sections. | Not safe; body read. |
| `AnnualReportDocumentCache.get_pdf_entry()` | Returns `AnnualReportPdfCacheEntry(pdf_path, source_metadata, updated_at)` and checks `pdf_path.exists()`. | Not safe as public evidence API; path exposure. |
| `AnnualReportDocumentCache.get_pdf_path()` | Returns local PDF path. | Not safe. |
| private SQLite rows | Contain enough identity/source metadata to design a safe method, but current access requires implementation work and tests. | Candidate implementation surface only. |

## Candidate Future Options

### Option A: Evidence-only after explicit metadata method exists

Use a new no-live metadata method exposed by `AnnualReportDocumentCache` or a repository-owned wrapper. The evidence worker calls only that method for S4/S5/S6 and records sample-specific `available`, `missing`, or `unsafe_metadata`.

This option is acceptable only after a separate no-live implementation gate adds and tests the method.

### Option B: Repository facade over cache metadata

Add a repository-level method such as `get_annual_report_reference_metadata(fund_code, year, report_type="annual_report")` that delegates to a cache metadata method and returns a bodyless dataclass. This keeps future callers aligned with the repository boundary while preventing `load_annual_report()` execution.

This option is preferable if the future evidence worker is outside `fund_agent/fund/documents` internals, because AGENTS requires production annual-report access through `FundDocumentRepository`.

### Option C: Cache-internal method only

Add a cache method such as `get_annual_report_source_metadata_envelope(DocumentKey)`. It may be useful for repository tests, but it should not become the evidence worker's direct public entry unless the controller explicitly authorizes cache-internal metadata inspection.

This option is narrower but weaker against boundary drift.

## Recommended Implementation Contract

Future implementation gate should add a bodyless metadata return type, preferably repository-facing:

```python
@dataclass(frozen=True, slots=True)
class AnnualReportReferenceMetadata:
    fund_code: str
    document_year: int
    report_type: Literal["annual_report"]
    source: AnnualReportSourceName | None
    selected_source: AnnualReportSourceName | None
    source_mode: AnnualReportSourceMode | None
    fallback_enabled: bool | None
    fallback_used: bool
    primary_failure_category: AnnualReportSourceFailureCategory | None
    metadata_identity_hash: str | None = None
```

The method should return a status wrapper rather than exceptions for ordinary cache absence:

```python
@dataclass(frozen=True, slots=True)
class AnnualReportReferenceMetadataResult:
    status: Literal["available", "missing", "unsafe_metadata"]
    metadata: AnnualReportReferenceMetadata | None
    reason: str | None = None
```

Mandatory invariants:

- `available` only if exact fund/year/report_type identity matches and source metadata satisfies EID single-source/no-fallback: `source="eid"`, `selected_source="eid"`, `source_mode="single_source_only"`, `fallback_enabled=False`, `fallback_used=False`, `primary_failure_category is None`.
- `missing` if no matching cache metadata row exists.
- `unsafe_metadata` if a row exists but exact identity or EID single-source/no-fallback policy fails.
- No return field may include `pdf_path`, parsed payload path, `updated_at`, `source_url`, source report name/code/description, upload IDs, body excerpts or any file-derived data.
- The method must not call `fetch_pdf`, `fetch_pdf_path`, `parse_pdf`, `load_annual_report`, `load_parsed_report`, source adapters, Docling or pdfplumber.

## Implementation Slices For A Future Gate

### Slice 1: cache metadata reader

Allowed files:

- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/models.py`
- targeted tests under the matching documents test area

Exact changes:

- Add bodyless dataclasses for metadata result if they belong in `models.py`, or private cache dataclasses if repository facade owns public shape.
- Add a method that queries only SQLite `documents` and, if needed, `parsed_reports` row presence for exact `DocumentKey`.
- Do not read parsed JSON payload file.
- Do not return or expose `pdf_path`, payload path or `updated_at`.
- Convert source metadata JSON with existing `AnnualReportSourceMetadata.from_dict()`.
- Return `missing`/`unsafe_metadata`/`available` with deterministic reasons.

Tests:

- SQLite fixture with matching EID single-source metadata returns `available` and only allowed fields.
- Missing row returns `missing`.
- Wrong fund/year/report_type returns `missing` or `unsafe_metadata` according to exact identity rules.
- `fallback_used=True`, `fallback_enabled=True`, `selected_source!="eid"`, `source!="eid"`, `source_mode` missing/wrong or `primary_failure_category` non-null returns `unsafe_metadata`.
- Monkeypatch file payload read and PDF path access so the test fails if parsed body/PDF path is accessed.

### Slice 2: repository-safe facade

Allowed files:

- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/models.py` if public result types are not added in Slice 1
- targeted repository tests
- conditional `fund_agent/fund/README.md` only if public developer contract changes

Exact changes:

- Add a repository method that validates fund code/year using existing helpers and delegates only to the metadata cache method.
- Do not change `load_annual_report()` behavior.
- Do not alter fallback policy.
- Do not add source adapter calls.

Tests:

- Facade calls cache metadata method and never invokes `load_annual_report`, `fetch_pdf`, `fetch_pdf_path`, `parse_pdf` or source adapters.
- Invalid fund code/year fails closed with existing validation semantics.
- Return payload contains no path/body fields.

### Slice 3: metadata-only evidence gate

Allowed files:

- one evidence artifact under `docs/reviews/`
- optional machine-readable evidence JSON only if the controller explicitly authorizes it

Exact actions:

- Call only the accepted metadata-only method for S4/S5/S6.
- Record per-sample status and allowed fields.
- Preserve `NOT_READY`.
- Do not run correctness review until all required samples have accepted same-source reference availability.

## Validation Matrix

| Gate | Command / check | Expected result |
| --- | --- | --- |
| Current planning gate | `git diff --check -- docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-20260616.md` | PASS |
| Future Slice 1 | targeted cache tests | Prove no parsed payload/PDF path/body/source helper access and correct status mapping |
| Future Slice 2 | targeted repository tests | Prove facade delegates only to metadata method and preserves `load_annual_report()` behavior |
| Future evidence gate | metadata-only sample query for S4/S5/S6 | `available` only if exact EID single-source/no-fallback metadata exists; otherwise blocked per sample |

## Stop Conditions

Stop and return control to the controller if:

- any planned evidence requires `load_annual_report()`, `load_parsed_report()`, `get_pdf_path()`, `get_pdf_entry()` as a public evidence API, PDF path/body access, parsed body access, source helper/adapters, live/network, Docling or pdfplumber
- current cache schema cannot distinguish exact `fund_code`, `document_year` and `report_type` without reading parsed payload body
- source metadata is absent, malformed, non-EID, fallback-used, fallback-enabled, non-`single_source_only`, or has non-null `primary_failure_category`
- a method would need to emit PDF path, payload path, source URL, report name/code/description, upload IDs, timestamps or file hashes
- S4/S5/S6 produce mixed availability and the controller has not decided whether partial availability is enough for any later correctness gate
- tests cannot prove body/PDF/source-helper non-access

## Exact Next Gate Recommendation

Proceed to:

```text
Docling Same-source Reference Cache Metadata No-live Implementation Gate
```

Recommended verdict for this planning gate:

```text
PLAN_METADATA_ONLY_CONTRACT_REQUIRED_NOT_READY
```

The next gate should implement and test a narrow metadata-only repository/cache method before any S4/S5/S6 evidence worker attempts cache inspection. Do not proceed directly to FDR/cache probes, correctness review, production parser replacement, source policy changes, readiness, release, PR, push or merge.

## Completion Report Contract

The planning worker completion report should include:

- artifact path
- verdict
- validation command and result
- confirmation that no source/tests/runtime/control/design files were modified
- confirmation that no FDR/cache/repository probe, PDF/live/network/Docling/pdfplumber/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge command was run

Self-check: pass. The artifact stays within the assigned planning gate, touches only the requested artifact path, preserves `NOT_READY`, and routes implementation/evidence to later reviewed gates.
