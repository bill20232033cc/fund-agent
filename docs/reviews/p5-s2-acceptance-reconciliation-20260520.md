# P5-S2 Acceptance Reconciliation - 2026-05-20

## Verdict

P5-S2 accepted.

P4-R9 closed: quality gate now covers FQ1 App category conflicts, FQ4 snapshot missing-field ratio, and FQ5 preferred_lens resolvability using structured `score.json.fund_quality`.

下一 gate：`P5-S3 snapshot sub-field exposure plan/review`。

## Inputs

- Plan: `docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md`
- Plan review: `docs/reviews/p5-s2-plan-review-controller-20260520.md`
- Plan re-review: `docs/reviews/p5-s2-plan-rereview-controller-20260520.md`
- Implementation: `docs/reviews/p5-s2-implementation-20260520.md`
- Code review: `docs/reviews/code-review-p5-s2-20260520.md`
- Global control doc: `docs/implementation-control.md`
- P4 control doc: `docs/implementation-control-p4.md`

## Accepted Scope

- `score.json` now includes `fund_quality`.
- `fund_quality` is derived from snapshot records, not from report Markdown, Service state, CLI output, PDF, cache, or LLM judgment.
- FQ1 supports both correctness mismatch and App category conflict.
- FQ4 uses structured `missing_field_rate` with explicit warn/block thresholds.
- FQ5 validates preferred_lens resolvability, not final rendered report lens.
- `QualityGateIssue` includes structured metadata for App category, fund type, lens key, observed rate, and threshold.
- Old `score.json` without `fund_quality` remains compatible via `FQ0/info`.

## Review Closure

Controller code review found one high-risk issue:

- FQ5 source data did not become `mismatch` when App category conflicted with fund type.

Fix accepted:

- `_preferred_lens_status(...)` now receives `app_category_status`.
- App category conflict forces `preferred_lens_status=mismatch`.
- Regression test covers the real snapshot-derived path.

## Validation Accepted

- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`: `37 passed`
- `.venv/bin/python -m pytest tests/ -q`: `185 passed`
- `.venv/bin/ruff check .`: passed
- `git diff --check`: passed

## Boundary Judgment

- Capability owns all new quality rules and mappings.
- Service and CLI quality gate strategy from P5-S1 remains unchanged.
- FQ4 does not parse rendered report wording.
- FQ5 is named and documented as resolvability; actual CHAPTER_CONTRACT lens validation remains future work.
- No explicit parameters were moved into `extra_payload`.

## Deferred Scope

- P5-S3: widen correctness denominator by exposing more P0 sub-fields.
- P5-S4: failed-fund accounting for failures only recorded in `errors.jsonl`.
- RR-13: `016492` duplicate still needs user/App source reconciliation.

## Gate Decision

当前 gate 从 `P5-S2 code review passed after fix` 推进为 `P5-S2 accepted`。

下一步进入 `P5-S3 snapshot sub-field exposure plan/review`。
