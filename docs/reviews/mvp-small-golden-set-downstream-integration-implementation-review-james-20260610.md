# MVP Small Golden Set Downstream Integration Implementation Review - James - 2026-06-10

## Scope

- Gate: EID single-source downstream integration implementation gate.
- Role: independent read-only code review.
- Reviewed current diff for:
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/report_evidence.py`
  - `fund_agent/fund/chapter_facts.py`
  - `fund_agent/fund/evidence_availability.py`
  - `tests/fund/test_data_extractor.py`
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_report_evidence.py`
  - `tests/fund/test_chapter_facts.py`
  - `tests/fund/test_evidence_availability.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - `docs/reviews/mvp-small-golden-set-downstream-integration-implementation-evidence-20260610.md`

## Boundaries

- No file edits.
- No staging, commit, push or PR.
- No live EID, network, PDF, FDR, fallback, provider, curl, DNS or socket execution.

## Initial Review Findings

Verdict: PASS.

Blocking findings: none.

Direct evidence:

- `fund_agent/fund/data_extractor.py:232` added `StructuredFundDataBundle.portfolio_managers` and `risk_characteristic_text` default fields.
- `fund_agent/fund/data_extractor.py:343` and `fund_agent/fund/data_extractor.py:344` populate the fields from existing extractor results.
- `fund_agent/fund/extraction_snapshot.py:41` and `fund_agent/fund/extraction_snapshot.py:46` add the fields to snapshot ordering.
- `fund_agent/fund/extraction_snapshot.py:85` and `fund_agent/fund/extraction_snapshot.py:86` add only stable comparable subfields.
- `fund_agent/fund/report_evidence.py:277` and `fund_agent/fund/report_evidence.py:279` add report fact specs for existing bundle fields.
- `fund_agent/fund/chapter_facts.py:82` and `fund_agent/fund/chapter_facts.py:85` add stable source field ids.
- `fund_agent/fund/chapter_facts.py:309`, `fund_agent/fund/chapter_facts.py:355` and `fund_agent/fund/chapter_facts.py:412` map the fields to chapters 1, 3 and 6.
- `fund_agent/fund/evidence_availability.py:199`, `fund_agent/fund/evidence_availability.py:247` and `fund_agent/fund/evidence_availability.py:266` add availability requirements without changing the existing no-fact and no-anchor semantics.
- No top-level `bond_top_holdings` or `target_fund_holdings` bundle fields were introduced.

Non-blocking residual identified:

- `tests/fund/test_data_extractor.py` initially checked `portfolio_managers` and `risk_characteristic_text` with `hasattr`, which did not prove the fields carried extractor-produced values.

## Re-review

Verdict: PASS.

Accepted finding resolved.

Direct evidence:

- `tests/fund/test_data_extractor.py:334` now asserts `portfolio_managers` extraction mode, note, schema, fund identity, report year, manager payload and anchor row locator.
- `tests/fund/test_data_extractor.py:355` now asserts `risk_characteristic_text` extraction mode, note, full value payload and anchor row locator.
- `tests/fund/test_data_extractor.py:727` provides in-memory `ParsedTable` fixture inputs for the risk characteristic row and portfolio manager tenure table.

## Residual Risks

- Review was read-only and did not independently run tests.
- Controlled live EID failure-branch evidence remains a separate authorized gate.
