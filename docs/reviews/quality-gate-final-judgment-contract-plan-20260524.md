# Quality Gate And Final Judgment Contract Plan

## Gate

- Work unit: quality gate and final judgment contract audit
- Branch: `codex/checklist-host-engine-design`
- Date: 2026-05-24
- Status: handoff-ready local plan

## Goal

Make the Quality Gate and `derive_final_judgment()` behavior explicit as a small executable design contract, then add focused regression coverage for the highest-risk state combinations.

The intent is not to redesign product rules. The intent is to reduce future ambiguity around how `analyze` and `fund-analysis checklist` treat:

- quality gate policy: `off / warn / block`
- gate status: `pass / warn / block / not_run`
- final judgment: `worth_holding / needs_attention / suggest_replace`
- developer override conflict handling

## Direct Evidence

- `FundAnalysisService._run_analysis_core()` is the shared deterministic path for `analyze()` and `checklist()`.
- `_run_quality_gate_if_enabled()` returns either a `QualityGateResult` or a not-run reason without re-extracting annual reports.
- `quality_gate_policy=block` raises `QualityGateBlockedError` for gate `block` and `QualityGateNotRunBlockedError` when gate is not run.
- `_resolve_final_judgment_quality_gate_status()` maps gate result / not-run reason to `pass / warn / block / not_run`.
- `derive_final_judgment()` chooses highest-priority product judgment from checklist, risk, stress, and gate status, while developer override changes only selected judgment and records conflicts.

## Non-Goals

- Do not change quality gate scoring rules.
- Do not change final judgment business semantics.
- Do not change renderer, audit schema, snapshot schema, selected fund CSV, golden answer rows, thermometer behavior, or annual-report source handling.
- Do not introduce Host/Agent runtime, LLM audit, Evidence Confirm, calculated tracking error, or external index adapters.
- Do not push or create PR.

## Implementation Slices

### S1 - Design Contract Tables

Allowed files:

- `docs/design.md`
- `docs/implementation-control.md`

Changes:

- Add a compact decision table for `quality_gate_policy` x gate execution outcome.
- Add a compact final judgment precedence table.
- State the difference between `analyze` and `checklist`: same core and gate behavior, but only `analyze` renders/audits the 8-chapter report.
- Record that `warn` gate status does not by itself downgrade an otherwise all-green fund, while `block/not_run` means data confidence is insufficient and yields `needs_attention` on continuing paths.

### S2 - Regression Tests

Allowed files:

- `tests/fund/analysis/test_final_judgment.py`
- `tests/services/test_fund_analysis_service.py`

Changes:

- Add a unit test proving `quality_gate_status="warn"` can still derive `worth_holding` when all product signals are green.
- Add a unit test proving `quality_gate_status="not_run"` plus otherwise green inputs derives `needs_attention`.
- Add a Service test proving `checklist()` is blocked under `quality_gate_policy=block` when the quality gate result is `block`, matching `analyze()`.

## Validation

Required commands:

```bash
uv run pytest tests/fund/analysis/test_final_judgment.py tests/services/test_fund_analysis_service.py -q
uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py -q
uv run pytest -q
uv run ruff check .
git diff --check
```

## Stop Conditions

Stop and ask before implementation if the code evidence contradicts the intended contract, especially if `analyze` and `checklist` do not share the same gate/final-judgment path.

## Residual Risks

- This gate documents and tests current deterministic behavior. It does not validate future Host/Agent tool-loop behavior because that runtime does not exist yet.
