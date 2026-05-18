# P2-S10 Implementation

## Gate

- Gate: `P2-S10 implementation + review`
- Date: 2026-05-18
- Worker: AgentCodex
- Scope: Capability template renderer evidence anchor labeling

## Changed Files

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p2-s10-implementation-2026-05-18.md`

## Implementation Summary

- Standardized body evidence lines through dedicated formatting helpers.
- Annual report body anchors now include report year, section, optional page metadata, and a source description.
- Annual report appendix anchors now follow `年报{年份}§{章节}表{编号}行{行号}` and explicitly degrade missing section, table, or row as `未定位`.
- Page number is retained as additional location metadata without changing the year/section/table/row order.
- Non-annual anchors render explicit source kind labels instead of being formatted as annual report anchors.
- Per-chapter evidence groups now drive missing evidence output, so a chapter without anchors emits both a body `数据不足` evidence line and an appendix missing-evidence entry.
- `TemplateRenderInput`, `TemplateRenderResult`, and `ProgrammaticAuditInput` compatibility were preserved.

## Validation

```bash
.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
```

Result: `23 passed in 0.40s`

`tests/fund/analysis` was not run because P2-S10 only changed template evidence formatting and did not touch analysis behavior or shared analysis contracts.

## Residual Risks

- This remains MVP programmatic template formatting only; LLM audit and Evidence Confirm are still out of scope.
- Non-annual source labels currently cover the existing `EvidenceSourceKind` literals: `external_api` and `derived`. Future source kinds should add an explicit label if the model expands.
- Missing evidence appendix entries are chapter-level, not item-level. Item-level evidence completeness remains a later audit/confirmation concern.

## Stop Status

- Implementation complete.
- Required validation passed.
- Ready for P2-S10 code review.
