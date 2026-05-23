# Repo-Level Deepreview Controller Reconciliation

## Scope

- Base state: `main` at `1c0b9e1` (`Close P7 draft PR gate`)
- Inputs: `docs/reviews/repo-review-mimo-20260520-235926.md`, `docs/reviews/repo-review-ds-20260520.md`
- Controller date: 2026-05-21 00:19 Asia/Shanghai
- Goal: reconcile P7-post repo-level deepreview findings against current code facts, apply safe aggregate fixes, and record residual work.

## Controller Judgment

| Finding | Verdict | Action |
|---|---:|---|
| MiMo-001 / DS-F001 `CLAUDE.md` describes another project | Accepted, serious | Deferred to doc cleanup. User explicitly said MiMo can update `CLAUDE.md`; not urgent for the current code-risk pass. |
| MiMo-002 corrupt parsed report JSON crash loop | Accepted, high | Fixed. `AnnualReportDocumentCache._load_parsed_report_sync()` now treats corrupt/non-object payloads and bad model fields as cache miss. |
| DS-F002 Eastmoney PDF has no content validation | Accepted, serious | Fixed. Eastmoney downloader now validates `%PDF-` bytes for downloads and cache hits, rejects HTML/error pages, and refreshes invalid cache. |
| DS-F004 / DS-F012 non-atomic PDF writes and invalid PDF cache hits | Accepted, high | Fixed for EID and Eastmoney paths. Both now validate cached PDF header and write via temp file + `os.replace`. |
| DS-F005 Eastmoney `OSError` bypasses source classification | Accepted, high | Fixed. Eastmoney source maps `OSError` and non-PDF `ValueError` to `AnnualReportSourceUnavailableError`. |
| DS-F003 block policy not-run uses generic `ValueError` / exit 1 | Accepted, high | Fixed. Added `QualityGateNotRunBlockedError`; CLI maps it to exit code 2 with `quality_gate_status: not_run`. |
| DS-F007 / DS-F013 fund_code format validation inconsistent | Accepted, medium | Fixed at `FundAnalysisService._validate_request()`: analyze now rejects non-6-digit fund codes before extraction. Repository-level validation remains a follow-up if direct repository calls need same UX. |
| MiMo-005 CSV errors swallowed as not-run | Partially accepted | Block-policy UX now reports not-run structurally. Capability still returns `not_run_reason` for unavailable/invalid selected-pool CSV by design; stricter `ValueError` propagation is deferred because current docs say not-run covers CSV unavailable/schema invalid. |
| DS-F008 EID schema error stops fallback | Rejected for now | Current P7 source policy is fail-closed for schema/mismatch to avoid hiding official-source drift or wrong report identity behind fallback success. Keep behavior unless design changes. |
| MiMo-003 QDII/FOF shadow enhanced-index classification | Accepted as domain follow-up | Not changed in this safety pass. Needs preferred-lens/domain decision on compound type or basis-only evidence; changing classification order can alter report semantics. |
| MiMo-004 share_change A-class fallback | Deferred | Existing tests intentionally cover “非 A 份额不默认 A 类”. Any A-class fallback requires source-level evidence and fixtures, not a generic fallback. |
| MiMo-006 `judge_alpha_nature(())` empty holdings | Deferred | Likely a real quality gap, but not a crash/data-integrity risk. Requires mapping `holdings_snapshot` into alpha observations, not a local one-line fix. |
| MiMo-007 / DS-F010 design/control docs stale | Accepted doc follow-up | Not fixed in this pass beyond package README/test README sync. Needs a dedicated design.md/control reconciliation pass as user requested earlier. |
| MiMo-008 / MiMo-009 / DS-F006 parsed cache dual-write and per-key concurrency | Deferred | Atomic PDF writes reduce the corruption risk. Full per-document lock / DB transaction redesign is a larger repository change. |
| DS-F009 TOCTOU PDF deletion before parse | Deferred | Lower-probability cache hygiene issue; best handled with repository retry/invalidate design together with per-key locking. |
| MiMo-010 Service imports Capability constant | Deferred | Architecture cleanup; no runtime bug. |
| DS-F011 expensive extraction before cheap selected-pool rejection | Deferred | Performance optimization with behavior-ordering implications; not needed for correctness pass. |
| DS-F014 golden Service wrapper tests missing | Deferred | Coverage cleanup; current wrappers are thin delegates. |

## Applied Fixes

- `fund_agent/fund/pdf/downloader.py`
  - Validates downloaded Eastmoney payloads using `%PDF-` magic bytes.
  - Validates cache hits before reuse; invalid cache is deleted and refreshed.
  - Writes PDFs atomically through a temporary file and `os.replace`.

- `fund_agent/fund/documents/sources.py`
  - EID cache hits now validate local PDF files before reuse.
  - EID PDF writes are atomic.
  - Eastmoney wrapper maps HTTP, filesystem, and non-PDF errors to source-unavailable errors so fallback/orchestration can classify them.

- `fund_agent/fund/documents/cache.py`
  - Corrupt parsed report JSON, non-object JSON, and invalid parsed model payloads now return cache miss instead of crashing permanently.

- `fund_agent/services/fund_analysis_service.py`, `fund_agent/services/__init__.py`, `fund_agent/ui/cli.py`
  - Added structured `QualityGateNotRunBlockedError`.
  - CLI exits with code 2 for block-policy not-run, matching quality-gate block semantics.
  - `analyze` validates fund codes as six digits before any extraction.

- Tests and docs updated:
  - Added focused regression tests for PDF validation/cache refresh, Eastmoney `OSError` classification, corrupt parsed JSON cache miss, structured not-run blocking, and fund-code validation.
  - Updated `fund_agent/fund/README.md` and `tests/README.md` to match current behavior.

## Verification

Targeted regression suite passed:

```bash
pytest tests/fund/pdf/test_downloader.py \
  tests/fund/documents/test_cache.py \
  tests/fund/documents/test_annual_report_sources.py \
  tests/services/test_fund_analysis_service.py
```

Result: `61 passed in 0.81s`.

Full repository test suite also passed:

```bash
pytest
```

Result: `299 passed in 0.74s`.

## Residual Risks

- `CLAUDE.md` remains stale and should be rewritten before relying on Claude agents for implementation tasks.
- `docs/design.md` / `docs/implementation-control*.md` still need a dedicated reconciliation against current code facts.
- Compound fund type semantics (`QDII` + `enhanced_index`, `FOF` + index identity) require an explicit design decision.
- Repository concurrency and TOCTOU retry behavior are still not solved end-to-end.
- Real network smoke for EID/Eastmoney remains manual; current tests use fake clients/sources.
