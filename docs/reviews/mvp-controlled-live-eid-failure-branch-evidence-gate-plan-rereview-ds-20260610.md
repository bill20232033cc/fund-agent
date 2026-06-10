# DS Targeted Re-Review: Controlled Live EID Failure-Branch Evidence Gate Plan — 2026-06-10

## Verdict

**PASS** — all four DS findings and all four MiMo findings confirmed resolved.

---

## DS Finding Resolution

### DS F1 (MEDIUM): Script content now present; live command fully pinned

**Verified in** `scripts/controlled_live_eid_failure_branch_observation.py` (159 lines) and plan lines 144–150.

The helper script is committed and reviewable. It:
- Imports only `fund_agent.fund.documents` public modules (sources, adapters, cache, repository)
- Pins `FUND_CODE = "006597"` and `REPORT_YEAR = 2024` as `Final` constants
- Constructs explicit single-source chain: `EidAnnualReportSource` → `AnnualReportSourceOrchestrator` → `AnnualReportPdfAdapter` → `FundDocumentRepository`
- Uses `tempfile.TemporaryDirectory` for auto-cleanup of both PDF and parsed-document caches
- Outputs exactly one line of JSON via `print(json.dumps(...))`
- No CLI args, no env vars, no config loading, no Eastmoney import

Plan line 147 pins the exact command to `uv run python scripts/controlled_live_eid_failure_branch_observation.py`. Plan line 150 states "No inline fallback command is authorized."

**Status**: ✅ RESOLVED

---

### DS F2 (LOW): Config/env dependency declaration added

**Verified in** plan line 142.

> EID single-source acquisition has no API key, env var or typed config dependency. E1 provider readiness is not applicable.

**Status**: ✅ RESOLVED

---

### DS F3 (LOW): Success label renamed with caveat

**Verified in** plan line 90.

Label changed from `accepted_live_success_no_failure_observed` to `accepted_live_window_no_failure_observed`. Evidence meaning column now appends: "This does not mean live failure-branch proof was accepted."

**Status**: ✅ RESOLVED

---

### DS F4 (LOW): No-live evidence `ac6bbe9` explicitly cross-referenced

**Verified in** plan lines 105.

> The no-live evidence at checkpoint `ac6bbe9` remains the accepted proof for all five categories (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`). This live gate cannot replace or upgrade that proof regardless of outcome.

**Status**: ✅ RESOLVED

---

## MiMo Finding Resolution

### MiMo F1 (MEDIUM): Cache directory injection feasible via instance `_cache` replacement

**Verified in** script lines 118–127.

The script uses `tempfile.TemporaryDirectory(prefix="fund-agent-live-eid-")` for both caches:

- PDF cache: `EidAnnualReportSource(cache_dir=root / "pdf-cache")` — explicit construction, not auto-creation
- Parsed-document cache: `repository._cache = AnnualReportDocumentCache(root_dir=root / "document-cache")` — instance-level replacement with `# noqa: SLF001`

The inline comment (script lines 124–127) documents the rationale: production code has no public parsed-cache injection parameter, so this gate-local script replaces the instance cache without changing runtime source code or global defaults. The temp directory context manager guarantees cleanup.

This is approach (a)-adjacent: explicit wiring with `EidAnnualReportSource` taking a temp cache dir, and a minimal `_cache` instance replacement. No monkeypatch, no `_create_default_cache` bypass, no production `cache/documents/` contamination.

**Status**: ✅ RESOLVED

---

### MiMo F2 (LOW): Constructor ambiguity eliminated by explicit wiring

**Verified in** script lines 120–123.

The script explicitly constructs every component: `EidAnnualReportSource` → `AnnualReportSourceOrchestrator((eid_source,))` → `AnnualReportPdfAdapter(orchestrator)` → `FundDocumentRepository(adapter)`. No auto-creation is relied upon. This is necessary for cache isolation (temp PDF cache dir in `EidAnnualReportSource`).

**Status**: ✅ RESOLVED

---

### MiMo F3 (LOW): Helper script ambiguity resolved

**Verified in** plan lines 144–150.

The plan no longer uses conditional language ("may be created only if"). It pins exactly `uv run python scripts/controlled_live_eid_failure_branch_observation.py`. The script is present and reviewable. No inline `python -c` fallback is authorized.

**Status**: ✅ RESOLVED

---

### MiMo F4 (LOW): Stop condition rephrased to "record then stop"

**Verified in** plan line 190.

> EID returns any failure category; record the classification per the outcome matrix, then stop;

Matches MiMo's recommended phrasing exactly.

**Status**: ✅ RESOLVED

---

## Script Adversarial Pass

Independent check of `scripts/controlled_live_eid_failure_branch_observation.py`:

| Check | Result |
|---|---|
| Imports only `fund_agent.fund.documents` public APIs | PASS — no Eastmoney, provider, LLM, Service, Host, Agent imports |
| Parameters are `Final` constants, no CLI/env/config input | PASS |
| Single-source orchestrator with exactly one EID source | PASS — `AnnualReportSourceOrchestrator((eid_source,))` |
| Single `load_annual_report()` call, no extractor/Service/Host/LLM | PASS |
| All exceptions caught and mapped to safe JSON | PASS — `_safe_exception_payload()` extracts type/message/category only |
| Success output contains only scalar metadata | PASS — no raw text, PDF bytes, section/table contents |
| Temp directory auto-cleanup | PASS — `TemporaryDirectory` context manager |
| `noqa: SLF001` documented with rationale | PASS — inline comment explains gate-local necessity |
| `noqa: BLE001` on broad except | PASS — intentional catch-all for safe observation |
| Output is single-line JSON, stdout only | PASS — `print(json.dumps(...))` |

No new findings.

---

## Summary

| Source | Finding | Status |
|---|---|---|
| DS F1 | Script content not provided | ✅ RESOLVED |
| DS F2 | No config/env dependency declaration | ✅ RESOLVED |
| DS F3 | Success label overclaim risk | ✅ RESOLVED |
| DS F4 | No cross-reference to `ac6bbe9` | ✅ RESOLVED |
| MiMo F1 | Cache directory injection feasibility | ✅ RESOLVED |
| MiMo F2 | Constructor ambiguity | ✅ RESOLVED |
| MiMo F3 | Helper script vs one-shot ambiguity | ✅ RESOLVED |
| MiMo F4 | Stop condition wording | ✅ RESOLVED |

**Verdict: PASS**. The plan and script are ready for controller judgment. No residual findings.
