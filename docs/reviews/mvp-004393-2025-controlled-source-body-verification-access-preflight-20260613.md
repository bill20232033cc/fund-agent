# 004393 / 2025 Controlled Source-body Verification Access Preflight

Date: 2026-06-13

Gate: `004393 / 2025 Controlled Source-body Verification Gate`

Verdict: `ACCESS_PREFLIGHT_BLOCKED_NEEDS_AUTHORIZATION_NOT_READY`

## 1. Scope

This preflight checks whether the gate may proceed to source-body verification
without running live EID/network/PDF/FDR commands.

This preflight did not read the 2025 annual-report body, did not call
`FundDocumentRepository.load_annual_report()`, did not inspect local PDFs, did
not run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR
commands, and did not edit tracked golden content.

## 2. Basis

- Rules truth: `AGENTS.md`
- Current startup: `docs/current-startup-packet.md`
- Control truth: `docs/implementation-control.md`
- Accepted planning judgment:
  `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-controller-judgment-20260613.md`
- Repository implementation: `fund_agent/fund/documents/repository.py`
- Repository cache implementation: `fund_agent/fund/documents/cache.py`
- Repository regression tests: `tests/fund/documents/test_repository.py`

## 3. Preflight Findings

| ID | Finding | Evidence | Disposition |
|---|---|---|---|
| PF1 | Public repository access is not cache-only. | `FundDocumentRepository.load_annual_report(..., force_refresh=False)` checks parsed cache first, then PDF cache, but if no usable cache exists it calls loader `fetch_pdf()` or `fetch_pdf_path()`. | `BLOCKS_NO_NEW_LIVE_VERIFICATION` |
| PF2 | No public no-new-live/cache-only method was found for `FundDocumentRepository`. | Static search found `load_annual_report()` as the public repository entry; cache access methods live on internal `AnnualReportDocumentCache`. | `BLOCKS_SAFE_PREFLIGHT_CALL` |
| PF3 | Internal parsed cache can prove a parsed report only by loading a `ParsedAnnualReport` payload. | `AnnualReportDocumentCache.load_parsed_report()` returns the full parsed report object, not an availability-only public contract. | `DO_NOT_USE_AS_CURRENT_GATE_PROOF` |
| PF4 | Repository regression tests confirm the risk. | Tests assert second `load_annual_report()` may hit parsed cache, but force-refresh bypasses cache and cache-miss paths call fetch/parse. | `CONFIRMS_BEHAVIOR` |
| PF5 | Current control truth forbids live/source/PDF commands in this gate unless separately bounded. | Current startup and control docs require repository-bounded no-new-live access or separate live EID sub-slice authorization. | `BOUNDARY_ACTIVE` |

## 4. Access Decision

Repository-bounded no-new-live access is not proven.

The gate must not call `FundDocumentRepository.load_annual_report("004393",
2025)` under current authorization because the call could fall through to
source/PDF fetch if parsed cache is missing or unusable.

The gate also must not directly inspect local PDF/data-artifact directories to
establish source-body truth, because the current route requires repository
boundary and the data/PDF artifacts remain user-owned residue unless a separate
gate authorizes that access pattern.

## 5. Row Verification Status

| Row family | Status |
|---|---|
| Seven accepted candidate rows from prior judgment | `NOT_VERIFIED_SOURCE_BODY` |
| `fee_schedule.management_fee` / `fee_schedule.custody_fee` | `REJECTED_FOR_THIS_ROUTE`; not eligible for verification here |

No row is promoted from candidate status to tracked strict golden truth by this
preflight.

## 6. Required Next Authorization

Proceed only through one of these paths:

1. `004393 / 2025 Controlled Live EID Source-body Verification Sub-slice`
   - Requires explicit user authorization for live EID/network/PDF/FDR access.
   - Must keep access through `FundDocumentRepository`.
   - Must verify only the seven accepted candidate rows.

2. `Repository Cache-only Access Design / Implementation Gate`
   - Adds or accepts a public no-new-live/cache-only repository contract before
     source-body verification.
   - Would be source/runtime contract work and therefore a separate reviewed
     implementation gate.

3. `Data-source Artifact Authorization Gate`
   - Separately authorizes a specific local PDF/data artifact access route.
   - Must reconcile with `AGENTS.md` repository-boundary rule before use.

## 7. Boundary Confirmation

This preflight did not perform or authorize:

- tracked golden answer content edits;
- fixture promotion edits;
- source/test/runtime behavior changes;
- `FundDocumentRepository.load_annual_report()` execution;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- cleanup, archive, push or merge actions;
- readiness/release status changes.

## 8. Recommended Next Entry

Recommended next entry:

```text
Controlled live EID source-body verification authorization decision
```

If live authorization is granted, the follow-up gate can verify the seven
candidate rows through the repository boundary. If live authorization is not
granted, the mainline remains blocked or must route to a separate cache-only
repository contract gate.
