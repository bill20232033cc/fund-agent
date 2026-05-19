# correctness slice code review controller judgment 20260519

## Verdict

PASS. P4-R10 correctness slice is accepted after code review and formatter fix.

Accepted review artifacts:

- `docs/reviews/correctness-slice-code-review-mimo-20260519.md`
- `docs/reviews/correctness-slice-code-review-glm-20260519.md`

Implementation artifact:

- `docs/reviews/correctness-slice-implementation-20260519.md`

## Accepted Scope

- `golden_answer.py` now loads and validates strict `fund-agent.golden-answer.v1` JSON for scoring input.
- `extraction_score.py` accepts explicit `golden_answer_path`, computes correctness for snapshot-explicit comparable fields, and writes correctness into `score.json` / `score.md`.
- `quality_gate.py` consumes correctness from `score.json`: unavailable correctness keeps `FQ0/info`, explicit mismatch emits `FQ1/block`.
- Service and CLI layers only pass explicit `golden_answer_path`; correctness logic remains in Capability.

## Findings Judgment

| Finding | Source | Judgment | Resolution |
|---|---|---|---|
| F-1 `ruff format` not executed | MiMo | Accepted | Fixed by running `ruff format` on correctness-scope Python files; re-check passed. |
| F-2 correctness comparable range only covers `classified_fund_type.fund_type` | MiMo / GLM | Accepted as residual risk | This is the intended minimal closure; tracked as RR-16 in `docs/implementation-control.md`. |
| F-3 conservative normalize only handles whitespace/case | MiMo | Accepted as design choice | Correct for the current enum-like comparable field; future free-text comparison needs separate normalization design. |
| Duplicate `_escape_markdown_cell` helpers | GLM | No action | Current duplication is two one-line private helpers; avoid premature shared utility. |
| JSON loader negative-path tests are sparse | GLM | Deferred test hardening | Existing happy path and downstream tests cover current gate; add targeted negative JSON loader tests when expanding strict schema surface. |

## Validation

- `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q` -> `28 passed`
- `.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/fund/golden_answer.py fund_agent/fund/quality_gate.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py` -> passed
- `.venv/bin/python -m ruff format --check fund_agent/fund/extraction_score.py fund_agent/fund/golden_answer.py fund_agent/fund/quality_gate.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py` -> passed
- `git diff --check` on correctness-scope code, tests, docs, and review artifacts -> passed

Real smoke remains as recorded in the implementation artifact: 004393 snapshot with strict `golden-answer.json` produces correctness `available`, one comparable record, and `classified_fund_type.fund_type` matches `active_fund`; quality gate remains block because of existing coverage gaps, not FQ1.

## Residual Risk

- RR-16 remains open: correctness denominator is intentionally narrow until snapshot exposes more explicit sub-field values.
- P4-R8 / RR-15 remains open: quality gate is still an explicit CLI path and is not yet attached to `analyze`.
- P4-R9 remains open for broader FQ rules beyond FQ0/FQ1/FQ2/FQ2F/FQ3.
