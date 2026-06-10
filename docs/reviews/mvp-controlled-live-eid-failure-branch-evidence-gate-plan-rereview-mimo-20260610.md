# Controlled Live EID Failure-Branch Evidence Gate Plan Re-Review - MiMo

## Artifact Re-Reviewed

- `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md` (plan)
- `scripts/controlled_live_eid_failure_branch_observation.py` (helper script)

## Reviewer

AgentMiMo (targeted re-review of previous DS/MiMo findings)

## Role Constraint

No live execution, no network/curl/DNS/sockets/live EID/PDF/FDR acquisition, no source/tests/runtime modification, no stage/commit/push/PR.

## Verdict

**PASS**

All previous findings are resolved. No new blocking findings.

---

## Finding Resolution Matrix

### F1 (MEDIUM): Temporary cache directory cannot be injected into `FundDocumentRepository`

**Status**: RESOLVED

**Resolution**: Plan §Command Shape line 73 now explicitly states:

> configure the repository instance parsed-document cache under a temporary directory by replacing that instance's `_cache` with `AnnualReportDocumentCache(root_dir=...)`; this is a gate-local cache-isolation step because production `FundDocumentRepository` has no public parsed-cache injection parameter

Script line 127 implements this:

```python
repository._cache = AnnualReportDocumentCache(root_dir=root / "document-cache")  # noqa: SLF001
```

**Verification**: `FundDocumentRepository._cache` is a plain instance attribute set at repository.py:315 (`self._cache = _create_default_cache()`), not a property or descriptor. Replacing it with a same-type `AnnualReportDocumentCache` instance with a different `root_dir` is valid. The `# noqa: SLF001` correctly acknowledges intentional private-attribute access. `tempfile.TemporaryDirectory` context manager ensures cleanup.

**No production code change**: Confirmed — the script only touches a live instance attribute, not the class definition or any source file.

---

### F2 (LOW): Redundant constructor steps create ambiguity

**Status**: RESOLVED

**Resolution**: Script lines 120-123 explicitly wire all four components:

```python
eid_source = EidAnnualReportSource(cache_dir=root / "pdf-cache")
orchestrator = AnnualReportSourceOrchestrator((eid_source,))
adapter = AnnualReportPdfAdapter(orchestrator)
repository = FundDocumentRepository(adapter)
```

This is the explicit-wiring path (needed for cache isolation), not the auto-creation path. Plan §Command Shape lines 69-74 describe the same explicit steps. No ambiguity remains.

---

### F3 (LOW): Helper script vs one-shot command ambiguity

**Status**: RESOLVED

**Resolution**: Plan §Validation line 147 now pins the exact command:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

Line 150 states: "No inline fallback command is authorized." The helper script exists at the expected path with 158 lines. No ambiguity remains.

---

### F4 (LOW): Stop condition "EID returns any failure category" contradicts gate objective

**Status**: RESOLVED

**Resolution**: Plan §Stop Conditions line 190 now reads:

> EID returns any failure category; record the classification per the outcome matrix, then stop;

The "record the classification, then stop" phrasing matches the outcome matrix semantics and the gate objective.

---

## Additional Verification

### Specific fixes checklist (user-requested)

| Check | Status |
|---|---|
| Exact helper script is now present | PASS — `scripts/controlled_live_eid_failure_branch_observation.py` exists, 158 lines |
| Command pinned to `uv run python scripts/controlled_live_eid_failure_branch_observation.py` | PASS — plan line 147 |
| No inline fallback command | PASS — plan line 150 |
| EID no config/env readiness declared | PASS — plan line 142: "EID single-source acquisition has no API key, env var or typed config dependency. E1 provider readiness is not applicable." |
| Success label renamed to `accepted_live_window_no_failure_observed` with caveat | PASS — plan line 90: label is `accepted_live_window_no_failure_observed`, caveat is "This does not mean live failure-branch proof was accepted" |
| No-live `ac6bbe9` proof explicitly cross-referenced | PASS — plan line 105: "The no-live evidence at checkpoint `ac6bbe9` remains the accepted proof for all five categories" |
| Stop condition says record classification then stop | PASS — plan line 190: "record the classification per the outcome matrix, then stop" |
| Cache isolation uses `_cache` replacement with temp root, no production code change | PASS — script line 127, plan line 73 |

### Script correctness spot-checks

| Check | Status |
|---|---|
| Single EID source only | PASS — `AnnualReportSourceOrchestrator((eid_source,))` with exactly one source |
| `force_refresh=True` | PASS — script line 129 |
| No Eastmoney/CNINFO import | PASS — script imports only EID-related symbols |
| No `FundDataExtractor` call | PASS — script uses `FundDocumentRepository.load_annual_report()` only |
| Safe exception mapping | PASS — `_safe_exception_payload` maps all relevant EID exception types to safe JSON scalars |
| Safe success mapping | PASS — `_safe_report_payload` includes only scalar metadata fields, no PDF bytes or raw text |
| No raw PDF/text retention | PASS — `tempfile.TemporaryDirectory` auto-cleans; no file copy to artifact directory |
| Output is single-line JSON | PASS — `json.dumps(result, ensure_ascii=False, sort_keys=True)` at line 154 |

---

## New Findings

No new blocking or medium findings.

One informational observation:

**INFO**: The script's `_safe_report_payload` includes `raw_text_length` (line 90: `len(report.raw_text)`). This is a safe scalar (integer), not the raw text itself. It provides useful evidence that the parsed report has non-trivial content. No action needed.

---

## Recommendation

**PASS**: The plan and helper script are ready for controller judgment and live execution authorization. All previous findings are resolved with concrete implementations. The command shape is feasible, cache isolation is achieved without production code changes, overclaim protection is in place, and stop conditions are correctly worded.
