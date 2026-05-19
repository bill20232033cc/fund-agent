# correctness slice implementation 20260519

## Scope

- Gate: `correctness slice implementation`.
- Goal: implement P4-R10 correctness automatic comparison and connect it to `score.json` / `score.md` / quality gate.
- No commit, push, PR mutation, or review gate action performed.

## Implementation

- Added strict golden answer JSON loading in `fund_agent/fund/golden_answer.py`.
- Added Capability-layer correctness comparison in `fund_agent/fund/extraction_score.py`.
- Added explicit `golden_answer_path` to `ExtractionScoreRequest`, `run_extraction_score(...)`, and CLI `fund-analysis extraction-score --golden-answer-path`.
- Added correctness output to `score.json` and `score.md`.
- Added quality gate handling for correctness:
  - no golden answer or unavailable correctness keeps `FQ0/info`;
  - available correctness with explicit mismatch emits `FQ1/block`.

## Correctness Semantics

- Input is strict `fund-agent.golden-answer.v1` JSON built by `golden-build`; Markdown is not reparsed for scoring.
- Skipped golden answer records are counted as `skipped_records` and never enter the correctness denominator.
- Current comparable field set is intentionally minimal: `classified_fund_type.fund_type`, because P4-S1 snapshot explicitly exposes `classified_fund_type`.
- Golden records whose sub-field is not explicitly exposed by snapshot are marked `unavailable` and do not enter the denominator.
- If snapshot explicitly marks a comparable golden field missing while golden expects a value, the record is a mismatch.
- Normalize is conservative: strip, full-width-space normalization, whitespace collapse, and casefold only. No synonym mapping, no anchor inference, and no experience-based fill.

## Threshold / Gate Policy

- Control docs define FQ1 as “基金类型与 App 类别或 golden answer 明显冲突” but do not define numeric thresholds.
- Minimal conservative policy implemented:
  - `mismatched_records > 0` among comparable correctness records => `FQ1/block`;
  - `comparable_records == 0` => no FQ1, only existing FQ0/info when correctness is unavailable.
- Rationale: a strict golden answer mismatch on an explicitly comparable field is a direct conflict, not an aggregate-quality signal.

## Modified Files

- `fund_agent/fund/golden_answer.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/services/extraction_score_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_golden_answer.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `tests/services/test_extraction_score_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Validation

- `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q` -> `28 passed`
- `.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/fund/golden_answer.py fund_agent/fund/quality_gate.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py` -> passed
- `git diff --check -- fund_agent/fund/extraction_score.py fund_agent/fund/golden_answer.py fund_agent/fund/quality_gate.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py README.md fund_agent/fund/README.md tests/README.md tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py` -> passed
- `.venv/bin/python -m fund_agent.ui.cli extraction-score --snapshot-path reports/extraction-snapshots/p4-s3b-004393-controller-final/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir /tmp/fund-agent-p4-correctness-smoke --golden-answer-path reports/golden-answers/golden-answer.json` -> wrote score artifacts
- `.venv/bin/python -m fund_agent.ui.cli quality-gate --score-path /tmp/fund-agent-p4-correctness-smoke/score.json --output-dir /tmp/fund-agent-p4-correctness-smoke/gate` -> wrote gate artifacts; status remains `block` due existing coverage gaps, not FQ1

Smoke result: strict golden answer has 121 active records and 29 skipped fields; the current real 004393 snapshot exposes one comparable correctness record, `classified_fund_type.fund_type`, which matches `active_fund`.

## Residual Risk

- Correctness comparable coverage is intentionally narrow until snapshot exposes more explicit field values. This avoids indirect evidence inference but means most strict golden rows are currently `unavailable`.
