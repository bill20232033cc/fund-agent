# P7 Acceptance / Ready-to-open-draft-PR Reconciliation

## Scope

- Phase: P7 annual report source migration
- Gate: P7 acceptance / ready-to-open-draft-PR reconciliation
- Design source: `docs/design.md`
- Control doc: `docs/implementation-control-p4.md`
- Accepted aggregate commit: `7599cc2 Accept P7 aggregate review`

## Design ↔ Control ↔ Code Facts

### 1. Annual Report Source Strategy

- Design fact: `docs/design.md` records annual report PDF source as EID / 证监会资本市场统一信息披露平台 primary, 天天基金 / Eastmoney fallback, through the unified document repository interface.
- Control fact: P7-S1 accepted EID live research and P7-S3 accepted EID primary implementation.
- Code fact: `AnnualReportSourceOrchestrator(None)` defaults to `EidAnnualReportSource` followed by `EastmoneyAnnualReportSource`; `AnnualReportPdfAdapter` hides source selection behind the documents adapter.

Judgment: aligned.

### 2. Unified Document Repository Boundary

- Design/control intent: callers must use the document repository interface; source details must remain inside Fund Capability.
- Code fact: `FundDocumentRepository.load_annual_report(...)` public signature is unchanged. Source orchestration is contained under `fund_agent/fund/documents/`.
- Review fact: P7 aggregate and targeted re-review confirmed no Service/UI/Engine/CLI source-awareness leakage and no `extra_payload` usage in the documents path.

Judgment: aligned.

### 3. Error Category Composition

- Control intent: not-found/unavailable may fallback; mismatch/schema must fail closed.
- Code fact: `AnnualReportSourceOrchestrator` continues on `AnnualReportSourceNotFoundError` and `AnnualReportSourceUnavailableError`, and stops on `AnnualReportSourceMismatchError` and `AnnualReportSourceSchemaError`.
- Review fact: aggregate deepreviews verified category composition across source, orchestrator, adapter, and repository layers.

Judgment: aligned.

### 4. Source Metadata And Cache Provenance

- Control intent: source metadata must be carried through PDF fetch, repository parsing, parsed cache, PDF cache, and cache provenance without adapter-wide mutable state.
- Code fact: `AnnualReportPdfFetchResult(pdf_path, source_metadata)` is the per-call contract; `ParsedAnnualReport.metadata` stores source/cache metadata; `documents.source_metadata_json` is additive and legacy-compatible.
- Fix fact: accepted aggregate finding closed cache resilience for malformed or invalid `source_metadata_json`; corrupted source metadata now degrades to `None` without blocking usable PDF path cache hits.

Judgment: aligned.

### 5. Legacy Compatibility

- Control intent: old parsed reports and old documents rows remain readable.
- Code fact: missing parsed `metadata` defaults to empty metadata; missing `source_metadata_json` returns `None`; invalid `source_metadata_json` now also returns `None`.
- Test fact: cache, repository, metadata-aware/legacy loader, force-refresh, PDF cache hit, parsed cache hit, and concurrent metadata tests all pass.

Judgment: aligned.

## Verification

Latest accepted P7 aggregate verification:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py -q
# 11 passed

.venv/bin/python -m pytest tests/ -q
# 293 passed

.venv/bin/python -m ruff check fund_agent/fund/documents/cache.py tests/fund/documents/test_cache.py
# All checks passed

git diff --check
# passed
```

## Residual Risks

| Risk | Severity | Owner |
|---|---|---|
| fallback success does not retain prior failure chain | Low | future provenance/audit enhancement |
| legacy parsed cache does not auto-refresh source metadata without `force_refresh=True` | Low | future cache policy enhancement |
| EID schema drift requires ongoing fake-network and future live smoke monitoring | Low | post-P7 source monitoring |
| unrelated local untracked artifacts remain outside P7 commit scope | Low | workspace hygiene / human-owned |

## Judgment

P7 is accepted for ready-to-open-draft-PR.

P7-S1 through P7-S4, aggregate review, accepted aggregate fix, and targeted re-review are all closed and pushed to `origin/main`. Current code, control doc, and design source are consistent for the P7 annual report source migration.

Next gate: `ready-to-open-draft-PR`.
