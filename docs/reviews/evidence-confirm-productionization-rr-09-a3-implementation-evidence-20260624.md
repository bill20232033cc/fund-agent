# RR-09 A3 No-live Implementation Evidence

Date: 2026-06-24
Branch: `evidence-confirm-productionization`
Gate: `RR-09 A3-S1/S2 No-live Implementation`
Verdict: `RR_09_A3_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## Scope

Authorized scope implemented:

- A3-S1: project `bond_risk_evidence` group-level anchor refs into ordinary annual-report `ChapterEvidenceAnchor` entries when the structured field is available.
- A3-S2: narrow semantic table `row_locator` references only when a single available non-derived fact is attached to the anchor and all deterministic V2 material tokens uniquely match one parsed table row.
- Keep writer fail-closed behavior for synthesized or internal bond-risk anchor ids.
- Update Fund package README for the changed current behavior.

Non-goals preserved:

- No live/PDF/product CLI execution.
- No checklist, report body, provider default, release, tag, PR, or readiness mutation.
- No Evidence Confirm V2 threshold relaxation.
- No ECQ / quality-gate semantic change.
- No new source kind or public `EvidenceAnchor` schema extension.
- No direct PDF/cache/source helper access outside `FundDocumentRepository` boundaries.

## Changed Files

- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_chapter_facts.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_evidence_confirm_sources.py`

## Implementation Notes

### A3-S1

`project_chapter_facts()` now converts `BondRiskEvidenceAnchorRef` entries from `BondRiskEvidenceValue.anchors` into normal annual-report anchors with:

- `source_kind="annual_report"`
- source section/page/table/row copied from the group anchor ref
- stable note preserving `evidence_role` and the internal `source_anchor`

The public fact still receives only projected chapter anchor ids. Missing or not-applicable bond-risk evidence still emits no chapter anchors and does not fabricate evidence.

### A3-S2

`build_annual_report_evidence_confirm_references()` now builds a local `facts_by_anchor` map and uses it only inside the annual-report materializer. Semantic table row locators remain conservative:

- If the anchor has exactly one available, non-derived, non-synthetic fact and all V2 material tokens match exactly one table row, the reference keeps the semantic `row_locator` and uses that single row excerpt.
- If multiple facts share the anchor, tokens are missing, tokens do not all match one row, or multiple rows match, the materializer keeps the existing table-level downgrade and informational issue.
- Section downgrade for semantic row locators without `table_id` is unchanged.

The narrowing reuses deterministic V2 token primitives and does not introduce an approximate matcher.

### Writer Guard

The writer prompt and unknown-anchor diagnostic now state the current contract: `bond_risk_evidence` may only cite ids present in the allowed anchor list. Internal `source_anchor_ids`, `source_field_id`, and fact values cannot be used to synthesize anchor markers.

## Verification

Executed no-live checks:

```text
uv run pytest tests/fund/test_chapter_facts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_value_diagnostics.py
```

Result:

```text
163 passed in 0.97s
```

Executed static checks:

```text
uv run ruff check fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/chapter_writer.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm.py
git diff --check
```

Result:

```text
All checks passed.
git diff --check produced no output.
```

## Boundary Result

This is a no-live implementation checkpoint only. It removes the known A2 root causes at the deterministic projection/materializer layer, but it does not prove runtime live/PDF R1-R4 pass. Release/readiness remains `NOT_READY` until the subsequent authorized runtime re-evidence and downstream gates complete.
