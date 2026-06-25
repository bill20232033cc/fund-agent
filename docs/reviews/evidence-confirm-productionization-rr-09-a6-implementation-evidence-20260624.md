# Evidence Confirm Productionization RR-09 A6 No-live Implementation Evidence

Verdict token:

`RR_09_A6_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## Scope

Gate: `RR-09 A6 No-live Projection / Runtime Locator Adoption Implementation Gate`.

Accepted plan/controller judgment:

- `docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a6-plan-controller-judgment-20260624.md`

This implementation used only the authorized no-live files:

- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_evidence_confirm_sources.py`

No live/PDF command, product CLI command, provider/LLM command, FundDisclosureDocument default-on route switch, checklist support, report-body rendering, V2 threshold change, ECQ/quality-gate semantic change, release, tag, push, or PR mutation was performed.

## Implementation

1. Default parsed annual processor projection now wraps legacy extractor anchors with a semantic top-level scope:
   - `source_field_path=<bundle_field>; locator=<legacy_locator>`
   - The wrapper is applied in `ActiveFundAnnualProcessor` field-family output.
   - The wrapper only uses `mapping.output_field_name`.
   - It does not infer `source_field_path=<field>.<subfield>` from composite dict values.

2. `StructuredFundDataBundle` projection now treats both locator families as field-identity capable:
   - Processor locator: `field=...; table_id=...; row=...`
   - Semantic locator: `source_field_path=...`
   - Anchors whose identity path does not match the requested top-level field are not borrowed by sibling fields.
   - Legacy families with no field-identity locator still keep their original family anchors.

3. Evidence Confirm materializer now scopes semantic row narrowing tokens when `source_field_path` is present:
   - `source_field_path=<field>` uses the top-level fact value.
   - Explicit `source_field_path=<field>.<subfield>` uses only that subfield value.
   - Unparseable scope, source-field mismatch, unresolved subpath, duplicate row match, or partial token match safely degrades to table/section excerpt and keeps the existing informational downgrade issue.
   - `source_field_path` is not added to the Processor row-locator protocol and therefore does not trigger Processor fail-closed validation.

## No-live Regression Evidence

Focused tests:

```bash
uv run pytest tests/fund/test_data_extractor.py tests/fund/test_evidence_confirm_sources.py -q
```

Result:

```text
112 passed in 0.92s
```

Lint:

```bash
uv run ruff check fund_agent/fund/processors/active_annual.py fund_agent/fund/data_extractor.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_data_extractor.py tests/fund/test_evidence_confirm_sources.py
```

Result:

```text
All checks passed!
```

Whitespace check:

```bash
git diff --check
```

Result: passed with no output.

## Regression Coverage Added

`tests/fund/test_data_extractor.py`:

- Default parsed annual processor emits top-level `source_field_path=fee_schedule`.
- Default parsed annual processor does not emit dot-subfield scope for composite fee values.
- `source_field_path` anchors are filtered by top-level bundle field and not borrowed across `fee_schedule` / `nav_benchmark_performance`.
- Existing FDD `field=` Processor locator projection remains covered and unchanged.

`tests/fund/test_evidence_confirm_sources.py`:

- Top-level composite `source_field_path=fee_schedule` does not fabricate row-level subfield proof and safely degrades to table excerpt.
- Explicit subfield scope `source_field_path=fee_schedule.management_fee` / `source_field_path=fee_schedule.custody_fee` narrows to unique matching rows and passes strict V2 in the no-live fixture.
- Duplicate token matches under subfield scope still degrade to table excerpt.
- Existing Processor row locator tests remain in place.

## Boundary Checks

- Repository/source/PDF access was not executed in this implementation gate.
- FDD default route was not enabled; `disclosure_intermediate=None` remains parsed annual only.
- Public `EvidenceAnchor` schema and `EvidenceSourceKind` were not expanded.
- V2 `value_match`, `anchor_precision`, hard-gate, ECQ and quality-gate semantics were not changed.
- `column` and `cell_id` remain non-proof-bearing context.

## Residuals

| Residual | Status after A6 no-live implementation | Destination |
|---|---|---|
| R1-R4 live/PDF impact | not yet measured | Requires separately authorized A6 R1-R4 live/PDF re-evidence. |
| Composite subfield row precision from default parsed annual route | still not inferred by design | Requires direct subfield provenance from extractor-specific future gate if needed. |
| R3 `missing_section=3` | not touched | Separate R3 missing-section diagnostic/fix gate. |
| B1 `017641 / 2024` product CLI block | not touched | Separate B1 runtime product CLI gate. |
| Release/readiness | `NOT_READY` | Separate release/readiness gate after accepted evidence. |

## Next Entry Point

`RR-09 A6 No-live Code Review Gate`

Completion token:

`RR_09_A6_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`
