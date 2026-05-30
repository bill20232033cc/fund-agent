# Gate 1 Implementation Evidence: Quality Gate Correctness Report-Year Scope

> Date: 2026-05-27
> Role: AgentCodex implementation / fix specialist
> Gate: Gate 1 correctness report_year scope fix
> Plan: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> Controller judgment: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-controller-judgment-20260527.md`

## Self-Check

- Current gate / role: scoped implementation specialist only; no full Gateflow workflow, no commit, no push, no PR.
- Source of truth: `AGENTS.md`, `docs/design.md` current design, `docs/implementation-control.md` Startup Packet, accepted plan, MiMo/GLM plan reviews, controller judgment.
- Scope boundary: changed only allowed Fund correctness/golden/quality-gate files, focused tests, Fund/tests README sync, and this evidence artifact.
- Non-goals preserved: no renderer/report-writing-audit, Service/CLI defaults, Host/Agent/dayu, document repository, PDF/cache/source helper, NAV, turnover-rate, checklist run-id, or FQ0-FQ6 weakening.
- Validation: focused pytest, focused ruff, and `git diff --check` passed.

## Changed Files

- `fund_agent/fund/golden_answer.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/test_golden_answer.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-implementation-evidence-20260527.md`

## Implemented Contract

- Added `report_year` to `GoldenAnswerFund` and `GoldenAnswerRecord`.
- Legacy strict JSON that omits `report_year` loads as `2024`; new `golden-build` JSON emits `report_year` at both fund and record level.
- Duplicate identity is now `(fund_code, report_year, field_name, sub_field)`.
- The loader allows the same `fund_code` to appear in multiple `GoldenAnswerFund` entries when `report_year` differs.
- `CorrectnessRecordResult` carries `report_year` so `score.json` record results are inspectable.
- `_snapshot_actual_index()` reads `report_year` from each snapshot record and keys actual values by `(fund_code, report_year, field_name, sub_field)`.
- `_correctness_coverage()` is year-scoped:
  - `fund_not_covered`: no golden for the fund code.
  - `year_not_covered`: the fund code has golden rows, but not for the current snapshot `report_year`.
- Added `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED = "year_not_covered"` in score and gate modules.
- Quality gate treats `year_not_covered` as `FQ0/info/pass` when no other blocking issues exist.
- Same-year correctness mismatch remains `FQ1/block`.

## Test Coverage Added

- Legacy JSON without `report_year` loads as 2024.
- Build output includes `report_year` at fund and record level.
- Duplicate same fund/year/field/subfield is rejected.
- Same fund code across different report years is allowed.
- Same-year mismatch path remains mismatch and FQ1/block via existing mismatch tests.
- 2025 snapshot with only 2024 golden returns `year_not_covered`, `comparable_records=0`, `mismatched_records=0`.
- Quality gate handles `year_not_covered` as FQ0/info/pass.
- Integration test constructs a 2025 bundle with only 2024 golden and verifies FQ0/info `year_not_covered`, not FQ1/block.

## Validation Results

```text
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
74 passed in 0.76s
```

```text
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
All checks passed!
```

```text
git diff --check
passed
```

## Docs Decision

- `fund_agent/fund/README.md` updated to document report-year-scoped correctness identity, `year_not_covered`, and legacy 2024 loading.
- `tests/README.md` updated to require score/golden/quality-gate tests to cover report-year identity and `year_not_covered`.
- Root `README.md` was not updated because this implementation does not change user-facing CLI commands or defaults; Fund/tests README cover the implementation contract.

## Residuals

- Existing curated `reports/golden-answers/golden-answer.json` remains legacy-compatible and was not edited.
- Golden build UX still has no explicit user-facing `--report-year` parameter; current build output uses the accepted legacy 2024 default for Markdown-derived rows. Future multi-year curated golden maintenance should add explicit reviewed year workflow before promoting non-2024 corpus rows.
- Product smoke commands were not run; this scoped gate validated the direct correctness-year paths. PDF/network/NAV/turnover/checklist-run-id failures remain unrelated to this implementation.

## Completion Status

Implementation is complete and ready for code review.
