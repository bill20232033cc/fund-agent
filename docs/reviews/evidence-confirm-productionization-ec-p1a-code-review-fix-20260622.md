# Evidence Confirm Productionization EC-P1A Code Review Fix

## Gate

- Work unit: `Evidence Confirm Productionization Program`
- Gate: `EC-P1A code review fix gate`
- Branch: `evidence-confirm-productionization`
- Accepted plan: `docs/reviews/evidence-confirm-productionization-program-plan-20260622.md`
- Implementation evidence: `docs/reviews/evidence-confirm-productionization-ec-p1a-implementation-evidence-20260622.md`
- Code review artifact: `docs/reviews/code-review-20260622-141733.md`
- Role: fix worker only
- Completion status: `IMPLEMENTATION_FIX_COMPLETE_NOT_READY`

## Reviewed Findings

| Finding | Controller disposition | Fix status |
|---|---|---|
| `EC-P1A-R1` negative `max_section_excerpt_chars` bypasses bound | accepted | fixed in current slice |
| `EC-P1A-R2` dead code in `_anchor_excerpt` dispatch | accepted | fixed in current slice |
| `EC-P1A-R3` no test for zero `max_section_excerpt_chars` | accepted | fixed in current slice |

## Fix Summary Per Finding

### EC-P1A-R1

- Added explicit fail-closed handling for `max_section_excerpt_chars < 0` in `_section_excerpt`.
- Stable blocking issue reason: `invalid_max_section_excerpt_chars`.
- Negative values no longer skip bounding or produce an unbounded section excerpt.
- Added focused no-live test `test_negative_max_section_excerpt_chars_fails_closed_explicitly`.

### EC-P1A-R2

- Removed the unreachable `_anchor_excerpt` branch for `anchor.row_locator` after the `row_locator and not table_id` and `table_id` dispatches.
- Behavior is unchanged for reachable paths.

### EC-P1A-R3

- Preserved `max_section_excerpt_chars=0` behavior: section text is sliced to empty, then fails closed as `empty_section_excerpt`.
- Added focused no-live test `test_zero_max_section_excerpt_chars_fails_closed_as_empty_excerpt`.

## Changed Files

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `docs/reviews/evidence-confirm-productionization-ec-p1a-code-review-fix-20260622.md`

No README update was needed because the public usage surface and test running guidance did not change.

## Validation Outputs

Command:

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
```

Output:

```text
...................................................................      [100%]
67 passed in 1.32s
```

Command:

```bash
uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py
```

Output:

```text
All checks passed!
```

Command:

```bash
git diff --check -- fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py docs/reviews/evidence-confirm-productionization-ec-p1a-code-review-fix-20260622.md fund_agent/fund/README.md tests/README.md
```

Output:

```text
<no output>
```

## Boundary Check

- No live/network/PDF/provider/LLM command was run.
- No `FundDocumentRepository` instantiation was added.
- No Service/UI/Host/renderer/quality-gate behavior was changed.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion was added.
- No source fallback behavior was changed.
- No V1/V2 Evidence Confirm behavior was changed.
- No commit, stage, push, PR mutation, mark-ready, merge, or re-review was performed.

## Residual Risks

| Residual | Classification | Owner / Destination |
|---|---|---|
| Compatibility `page-{page_number}-table-{table_index}` may not cover live annual-report structures. | covered by later approved slice | EC-P2 repository-bounded live source/PDF evidence gate |
| Current extractor anchors may use richer row locators than zero-based `row-N`. | covered by later approved slice | EC-P2 / later documents-model locator gate |
| Section excerpt positive bounds may still truncate long qualitative support. | covered by later approved slice | EC-P2 live evidence and later semantic/materializer gates |
| Semantic entailment, Service/UI/renderer/quality-gate integration, production default, and release/readiness remain unimplemented. | assigned to later work unit | EC-P4 through EC-P11 |

## Completion

`IMPLEMENTATION_FIX_COMPLETE_NOT_READY`
