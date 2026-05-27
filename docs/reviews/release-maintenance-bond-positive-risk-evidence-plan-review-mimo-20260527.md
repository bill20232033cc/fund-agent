# Bond Positive-Risk Evidence Plan Review — MiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Role: independent plan reviewer (not controller)
> Artifact reviewed: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`
> Also reviewed: `docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md`

## Verdict

**PASS_WITH_FINDINGS**

## Scope Discipline

PASS. Plan is correctly scoped to `006597` / 2024 and `bond_risk_evidence_missing.baseline_blocking=true`. Non-goals explicitly exclude golden corpus, QDII, FOF, release readiness, code implementation, renderer, quality-gate behavior change, Host/Agent/dayu, and GitHub mutation. Consistent with implementation-control.md next entry point.

## Evidence Contract

PASS. The 7 `bond_risk_evidence.v1` groups match code definitions in `extraction_score.py:172-252`. Acceptance criteria require same fund/year, public disclosure, traceability, bond-risk relevance, reviewed status, and no risk suppression. "Cannot satisfy" list is thorough and correctly excludes generic bond classification, warn-level alone, and unanchored prose. `data_gap` and `extractor/evidence-anchor` classifications are well-defined and distinct.

## Evidence-Run Commands (Step A)

PASS with minor note. The three `uv run fund-analysis` CLI commands use correct subcommand names and public output paths. The golden-answer path `reports/golden-answers/golden-answer.json` exists on disk. Output path conventions are consistent with current CLI behavior.

## Step B Repository Inspection Script — BLOCKER

**Severity: HIGH — must fix before plan acceptance.**

The Step B inline Python script (lines 122–148) has multiple API mismatches with the actual `fund_agent/fund/documents/models.py` data classes:

### F1: `report.sections` iteration is wrong

`ParsedAnnualReport.sections` is `dict[str, ReportSection]` (line 550 of `models.py`). The script does `for section in report.sections:` which iterates over dict keys (strings), not `ReportSection` objects. All subsequent `getattr(section, ...)` calls operate on string keys, silently returning defaults.

**Fix**: Change to `for section_id, section in report.sections.items():`.

### F2: `ReportSection` has no `text` attribute

`ReportSection` (lines 408–425 of `models.py`) has: `section_id`, `title`, `start_offset`, `end_offset`, `matched_rule`, `confidence`. The script accesses `getattr(section, "text", "")` which always returns `""`. Section text must be extracted from `report.raw_text[section.start_offset:section.end_offset]`.

**Fix**: Replace `text = getattr(section, "text", "")` with `text = report.raw_text[section.start_offset:section.end_offset]`.

### F3: `ReportSection` has no `tables` attribute

Tables are stored at the report level as `report.tables: tuple[ParsedTable, ...]`, not nested inside sections. The script's `for table in getattr(section, "tables", ()):` always yields nothing. Tables would need to be correlated to sections by `page_number` / offset mapping, or iterated at the report level.

**Fix**: Iterate `report.tables` at the report level and correlate to sections as needed, or iterate tables independently.

### F4: `ParsedTable` has no `table_id` or `caption` attributes

`ParsedTable` (lines 475–488 of `models.py`) has: `page_number`, `table_index`, `headers`, `rows`. The script accesses `getattr(table, "table_id", None)` and `getattr(table, "caption", "")` — both always return defaults. Table identity must use `(page_number, table_index)`. Caption is not available; use `headers` for context.

**Fix**: Replace `table_id` with `(table.page_number, table.table_index)`. Replace `caption` with `str(table.headers)` or similar.

### Impact

If Step B is executed as written, it would silently produce only the top-level `{"fund_code": ..., "year": ..., "section_count": N}` line and no section/table matches, because every keyword check runs against empty strings. The evidence run would falsely conclude no candidate bond-risk evidence was found, potentially leading to a wrong `evidence unavailable` classification when evidence may actually exist in the annual report.

### Required patch

The Step B script must be rewritten to match the actual API:

```python
async def main() -> None:
    report = await FundDocumentRepository().load_annual_report("006597", 2024)
    print({"fund_code": report.key.fund_code, "year": report.key.year, "section_count": len(report.sections)})
    for section_id, section in report.sections.items():
        title = section.title or ""
        text = report.raw_text[section.start_offset:section.end_offset]
        haystack = title + "\n" + text
        if any(keyword in haystack for keyword in KEYWORDS):
            print({"section_id": section_id, "title": title, "snippet": text[:500]})
    for table in report.tables:
        headers_str = str(table.headers)
        rows_preview = str(table.rows[:8])
        if any(keyword in headers_str + rows_preview for keyword in KEYWORDS):
            print({"page": table.page_number, "table_index": table.table_index, "headers": headers_str, "rows_preview": rows_preview[:1200]})
```

## Classification Matrix

PASS. Four final states are correct and mutually exclusive. Stop conditions cover code/test changes, PDF/cache boundary violations, source fail-closed categories, source unavailability, and truth contradictions. Matrix correctly does not weaken FQ0-FQ6 or suppress `bond_risk_evidence_missing`.

## Artifact Disposition

PASS. `--help` stray file is correctly left untracked. Other untracked files are not staged or promoted. Plan adds only its own artifact path.

## Process

PASS. Plan explicitly requires two independent reviews and controller judgment before any evidence run. Section 8 documents the review sequence. Reviewer constraints are stated.

## AGENTS.md Gate Classification Repair

Verified: the truth-preflight artifact records the mismatch and the minimal fix. `AGENTS.md` now contains a valid `Gate 轻重分类规则` section (lines 52–57) defining `fast_path`, `standard`, `heavy`. Repair is correct and consistent with implementation-control.md references.

## Findings Summary

| ID | Severity | Section | Description | Status |
|---|---|---|---|---|
| F1 | HIGH | §3 Step B | `report.sections` dict iteration yields keys, not `ReportSection` objects | Must fix |
| F2 | HIGH | §3 Step B | `ReportSection.text` does not exist; text must come from `raw_text` offsets | Must fix |
| F3 | HIGH | §3 Step B | `ReportSection.tables` does not exist; tables are at report level | Must fix |
| F4 | MEDIUM | §3 Step B | `ParsedTable` has no `table_id` or `caption`; use `(page, index)` and `headers` | Must fix |

## Required Patch Before Plan Acceptance

The Step B script (lines 122–148) must be rewritten to use the actual `ParsedAnnualReport` / `ReportSection` / `ParsedTable` API. The corrected script is provided above. All four findings (F1–F4) must be resolved in a single patch.

No other sections require changes.

## Re-review Required

**Yes.** After the Step B script patch, a re-review is needed to confirm the script matches the API and the evidence contract is preserved. If the patch is mechanical (only fixing API calls, not changing scope or logic), a single re-review suffices.
