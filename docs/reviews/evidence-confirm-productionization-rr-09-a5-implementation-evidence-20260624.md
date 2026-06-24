# RR-09 A5 No-live Implementation Evidence

Verdict: `RR_09_A5_NO_LIVE_IMPLEMENTATION_EVIDENCE_READY_FOR_CODE_REVIEW_NOT_READY`

Gate: `RR-09 A5-S0/A5-S1 Projection Locator Adoption No-live Implementation Gate`

Accepted plan: `docs/reviews/evidence-confirm-productionization-rr-09-a5-plan-controller-judgment-20260624.md`

## Scope

Implemented no-live projection locator adoption for field-locator-capable Processor families.

No live/PDF, product CLI, provider/LLM, repository/source-helper, V2/ECQ/quality-gate semantic, checklist, report-body, tag, release or readiness action was run.

## Changed Files

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a5-implementation-evidence-20260624.md`

## Implementation Summary

### A5-S0 / A5-S1

`_field_from_family()` no longer assigns the entire `FundFieldFamilyResult.anchors` tuple to every top-level field when the family contains recognizable Processor `field=` locators.

New private helpers:

- `_anchors_for_family_field()`
- `_processor_locator_field_path()`
- `_field_path_matches_top_level()`

Behavior:

- Semicolon-delimited Processor locator `field=` values are parsed only for field identity.
- A locator matches a top-level field only when:
  - `field_path == field_name`; or
  - `field_path.startswith(f"{field_name}.")`.
- If the family contains at least one recognized `field=` locator, only matching anchors are bound to the projected `ExtractedField`.
- If the family contains recognized `field=` locators but none match the requested field, the projected field keeps its value but receives `anchors=()`, preserving fail-closed downstream evidence behavior.
- If the family contains no recognized semicolon `field=` locator, the existing `family_result.anchors` behavior is preserved for no-`field=` processor paths that wrap legacy extractor anchors.

The implementation does not parse or validate `row`, `table_id`, `column` or `cell_id` as proof. Row/table validity remains Evidence Confirm materializer responsibility.

## Test Coverage Added

`tests/fund/test_data_extractor.py` now covers:

- no-`field=` processor family anchors are preserved for marker active fund processor output;
- FDD `return_attribution.v1` projection binds `fee_schedule` only to `fee_schedule.*` anchors;
- FDD `return_attribution.v1` projection binds `nav_benchmark_performance` only to `nav_benchmark_performance.*` anchors;
- field-locator-capable family with no compatible anchor returns empty anchors instead of borrowing unrelated anchors;
- FDD `manager_profile.v1` projection binds `manager_alignment` only to `manager_alignment.*` representative anchors;
- FDD `manager_profile.v1` projection binds `manager_strategy_text` only to `manager_strategy_text.*` representative anchors.

During validation, an initial test assertion expected two public anchors for `manager_alignment` and `manager_strategy_text`. Static code evidence showed current processor behavior intentionally chooses a single representative anchor for those composite public values. The test was corrected to assert field-compatible anchoring rather than requiring both child anchors.

## Documentation

`fund_agent/fund/README.md` now documents:

- field-locator-capable processor family projection filters anchors by exact/dot-prefix field path;
- no-`field=` processor families preserve existing anchors;
- row/table/section validity remains Evidence Confirm materializer responsibility;
- `column` / `cell_id` are not proof-bearing fields.

## Validation

```text
uv run pytest tests/fund/test_data_extractor.py -q
```

Result:

```text
55 passed
```

```text
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
```

Result:

```text
52 passed
```

```text
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

## Residuals

| Residual | Disposition |
| --- | --- |
| Runtime R1-R4 may still produce `processor_row_locator_rows=0` if the live path uses legacy/no-`field=` locators or fails table/section preflight. | Later explicit live/PDF re-evidence authorization must classify runtime locator protocol and preflight issues. |
| R3 `missing_section=3` remains unresolved. | Separate A5-S2 / missing-section diagnostic residual; not hidden by this implementation. |
| FDD `manager_alignment` and `manager_strategy_text` public values currently use single representative anchors even when values contain two child entries. | Existing processor behavior; current slice prevents unrelated family-anchor broadcast but does not change source selection semantics. |
| Release/readiness remains unproven. | `NOT_READY`; future release boundary gate required. |

## Final Token

`RR_09_A5_NO_LIVE_IMPLEMENTATION_EVIDENCE_READY_FOR_CODE_REVIEW_NOT_READY`
