# Evidence Confirm Productionization RR-09 B1 Manager-strategy QDII Implementation Evidence

Verdict token:

`RR_09_B1_MANAGER_STRATEGY_QDII_IMPLEMENTED_NOT_READY`

## Scope

Executable gate:

`RR-09 B1 R5a Manager-strategy QDII Extraction/Anchor Implementation Gate`

Accepted plan input:

- `docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-residual-plan-20260623.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-plan-controller-judgment-20260623.md`

This implementation keeps `manager_strategy_text` as P0 and does not change quality-gate semantics, score priority, Service/CLI behavior, Evidence Confirm policy, source policy, PR state, tag, release, or readiness.

No live/PDF/provider/LLM command, `FundDocumentRepository` product diagnostic, raw PDF/cache/source-helper access, or external state mutation was performed.

## Motivation

Accepted R5a static evidence narrowed `017641 / 2024` to a generic P0 `manager_strategy_text` coverage/traceability block. The current code selected `manager_strategy_text` only from stable paragraph `heading_path` tokens. Therefore the narrow no-live B1 fix is to improve strategy/outlook heading coverage for QDII/overseas annual-report wording while preserving the heading-only guard.

## Changed Files

| File | Change |
|---|---|
| `fund_agent/fund/processors/fund_disclosure_processor.py` | Added QDII/overseas strategy/outlook heading variants and made `_MANAGER_PROFILE_MATCH_GROUPS` reuse the same strategy/outlook constants used by the selector. |
| `tests/fund/test_data_extractor.py` | Added positive fixture for QDII/overseas heading variants through `017641` / `qdii_fund` FDD dispatch and negative fixture proving body-only keywords do not self-authorize `manager_strategy_text`. |
| `fund_agent/fund/README.md` | Documented current FDD source-truth `manager_strategy_text` heading-only behavior and QDII/overseas heading variant support. |

## Direct Code Evidence

Current selector:

- `_select_manager_profile_strategy_text()` reads only stable `paragraph_blocks`.
- `_manager_profile_paragraph_matches_strategy()` matches only `_tuple_text(paragraph.heading_path)`.
- Body text is used as extracted value only after heading-path match.

Implementation:

- Added strategy heading variants:
  - `报告期内基金的投资策略和业绩表现说明`
  - `基金投资策略和业绩表现说明`
  - `投资策略和业绩表现说明`
  - `基金投资策略和运作分析`
  - `运作回顾`
- Added outlook heading variants:
  - `管理人对宏观经济、证券市场和行业走势的简要展望`
  - `管理人对境外市场走势的简要展望`
  - `宏观经济、证券市场及行业走势展望`
  - `市场及行业走势展望`
- Replaced duplicated match-group literals with:

```python
(*_MANAGER_PROFILE_STRATEGY_HEADINGS, *_MANAGER_PROFILE_OUTLOOK_HEADINGS)
```

This keeps candidate/source-truth matching and direct selection aligned.

## Tests / Validation

```bash
uv run pytest tests/fund/test_data_extractor.py -q --tb=short -k "manager_strategy_text"
```

Result: `2 passed, 52 deselected`.

The positive case uses `017641` / `qdii_fund` parsed-report classification and matching FDD admission identity; it is not an active-fund-only fixture.

```bash
uv run pytest tests/fund/test_data_extractor.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q --tb=short
```

Result: `144 passed`.

```bash
uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short
```

Result: `46 passed`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Result: `All checks passed!`

```bash
git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md
```

Result: pass.

## Residual Risks

| Residual | Classification | Destination |
|---|---|---|
| `017641 / 2024` product CLI quality-gate re-evidence | assigned to later work unit | Requires explicit live/PDF authorization before running `fund-analysis analyze 017641 --report-year 2024 --valuation-state unavailable --force-refresh`. |
| R1-R4 EC `fail` under `warn` | assigned to later work unit | A1 sample-specific fact-level diagnostic; not touched by B1. |
| Product decision to make `manager_strategy_text` non-P0 for QDII | not taken | B2 remains separate product applicability decision gate. |
| Release/readiness | still blocked | Separate release-boundary authorization and accepted readiness evidence required. |

## Result

B1 no-live implementation is ready for code review.

Completion token:

`RR_09_B1_MANAGER_STRATEGY_QDII_IMPLEMENTED_NOT_READY`
