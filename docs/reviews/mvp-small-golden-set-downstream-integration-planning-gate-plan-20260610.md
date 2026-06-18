# MVP Small Golden Set Downstream Integration Planning Gate Plan - 2026-06-10

## Goal

Plan the downstream integration for the four accepted row-shape extractor output surfaces:

- `portfolio_manager_tenure_list.v1`
- `risk_characteristic_text.v1`
- `bond_top_holding_row.v1`
- `target_fund_holding_row.v1`

This planning gate does not implement downstream wiring. It produces an implementation-ready sequence for later gates.

## Direct Evidence

- Current control truth states all four row-shape contracts are current passing extractor surfaces only.
- `portfolio_managers` is currently exposed by `extract_manager_ownership().portfolio_managers`, but `StructuredFundDataBundle` does not carry it.
- `risk_characteristic_text` is currently exposed by `extract_profile().risk_characteristic_text`, but `StructuredFundDataBundle` does not carry it.
- `bond_top_holdings` and `target_fund_holdings` are currently sub-shapes inside `extract_holdings_share_change().holdings_snapshot.value`, so they must not be duplicated as top-level bundle fields without a separate contract decision.
- Existing downstream projection surfaces include:
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/report_evidence.py`
  - `fund_agent/fund/chapter_facts.py`
  - `fund_agent/fund/evidence_availability.py`

## Scope

Allowed planning scope:

- Define downstream implementation slices and file ownership.
- Define contract decisions for bundle fields, snapshot rows, report evidence facts and chapter fact projection.
- Define tests and validation commands.
- Define explicit non-goals and stop conditions.

Allowed artifact/docs files for this planning gate:

- `docs/reviews/mvp-small-golden-set-downstream-integration-planning-gate-*.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Non-Goals

- No production code changes in this planning gate.
- No PDF read, repository live acquisition, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No renderer text change, checklist behavior change, quality gate scoring change or score-loop change.
- No Service, Host or Agent runtime expansion.
- No new target ETF code inference.
- No EID failure-branch evidence work in this gate; that is the next user-directed planning topic.

## Planning Decisions

### Decision 1: Integrate manager and risk as top-level bundle fields

`portfolio_managers` and `risk_characteristic_text` should become explicit `StructuredFundDataBundle` fields because their extractor results currently live outside existing bundle fields and would otherwise be invisible to snapshot, report evidence and chapter fact projection.

Implementation owner files for a later gate:

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/models.py` only if docstrings/types need alignment
- tests that construct `StructuredFundDataBundle`

Expected implementation:

- Add `portfolio_managers: ExtractedField[dict[str, object]]` to `StructuredFundDataBundle`.
- Add `risk_characteristic_text: ExtractedField[dict[str, object]]` to `StructuredFundDataBundle`.
- Populate them from `manager_ownership_result.portfolio_managers` and `profile_result.risk_characteristic_text`.
- Update fake bundle constructors in tests.

### Decision 2: Keep bond and target holdings inside holdings_snapshot

`bond_top_holdings` and `target_fund_holdings` should remain sub-shapes of `holdings_snapshot.value`. They are holdings variants, not independent top-level P1 fields. The downstream plan must not duplicate them as `StructuredFundDataBundle` fields.

Implementation owner files for a later gate:

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/report_evidence.py`
- `fund_agent/fund/chapter_facts.py`
- tests for those surfaces

Expected implementation:

- Keep `holdings_snapshot` as the single bundle field.
- Add snapshot comparable metadata only if it is descriptive and does not alter quality/golden semantics, for example presence/count subfields such as `bond_top_holdings_count` and `target_fund_holdings_count`.
- Ensure report evidence and chapter facts preserve `bond_top_holdings` and `target_fund_holdings` inside the `holdings_snapshot` fact value.
- Do not change `top_holdings_status` / `top_holdings_source` quality semantics.

### Decision 3: Downstream integration slices

Slice A: Bundle fan-in for manager/risk.

- Add bundle fields for `portfolio_managers` and `risk_characteristic_text`.
- Update `FundDataExtractor.extract()`.
- Update tests that instantiate `StructuredFundDataBundle`.
- No snapshot/report/chapter changes in this slice unless necessary for constructor compatibility.

Slice B: Snapshot and report evidence projection.

- Add `portfolio_managers` and `risk_characteristic_text` to snapshot field ordering.
- Add comparable subfields:
  - `portfolio_managers`: `schema_version`, `manager_count`
  - `risk_characteristic_text`: `schema_version`, `risk_characteristic_text`
- Add report evidence specs for the two new bundle fields.
- Preserve holdings sub-shapes as part of `holdings_snapshot`; add descriptive sub-shape presence/count only if tests prove no score/golden semantics change.

Slice C: Chapter facts and evidence availability.

- Add source field ids for `portfolio_managers` and `risk_characteristic_text`.
- Map:
  - `portfolio_managers` to chapter 1 and chapter 3 planning/review contexts where manager identity and actual behavior are relevant.
  - `risk_characteristic_text` to chapter 1 and chapter 6 contexts where product risk and core risk are relevant.
  - existing `holdings_snapshot` remains the source field for bond/target holdings sub-shapes in chapters 3, 5 and 6.
- Add tests that `ChapterFactProjection` and `EvidenceAvailability` expose these fields without changing renderer output.

Slice D: Documentation/control sync.

- Update `fund_agent/fund/README.md`, `tests/README.md`, `docs/current-startup-packet.md` and `docs/implementation-control.md` after the implementation gate is accepted.

## Validation Matrix For Later Implementation

Required commands for implementation gates:

```bash
uv run pytest tests/fund/test_data_extractor.py -q
uv run pytest tests/fund/test_extraction_snapshot.py -q
uv run pytest tests/fund/test_report_evidence.py -q
uv run pytest tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py -q
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py
git diff --check -- fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-downstream-integration-*.md
```

Expected outcomes:

- Existing extractor correctness remains passing.
- Existing quality gate and golden readiness behavior remain unchanged.
- New bundle fields are visible through snapshot/report/chapter-fact surfaces.
- Holdings sub-shapes remain inside `holdings_snapshot` and are not duplicated.

## Stop Conditions

- Stop if implementation would require PDF/network/source/fallback/provider/live behavior.
- Stop if renderer, checklist, quality gate, score-loop, golden/readiness or Service/Host behavior needs to change.
- Stop if holdings sub-shapes cannot be projected without changing existing `holdings_snapshot` quality semantics.
- Stop if any plan step requires inferring target ETF code.
- Stop if user asks to switch to EID failure-branch evidence planning before downstream implementation starts.

## Completion Report Format

Later implementation closeout must report:

- implemented slices;
- changed files;
- exact validation commands and results;
- downstream surfaces now consuming each field;
- final `source_field_id` names used for `portfolio_managers` and `risk_characteristic_text`;
- residual non-goals preserved;
- next recommended gate.
