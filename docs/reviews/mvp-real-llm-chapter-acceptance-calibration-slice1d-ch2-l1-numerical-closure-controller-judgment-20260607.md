# MVP Real LLM Chapter Acceptance Calibration Slice 1D Controller Judgment

## 1. Decision

`PLAN_ACCEPTED_FOR_IMPLEMENTATION`

Slice 1D Ch2 `l1_numerical_closure` plan is accepted for local implementation.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-094336.md`
- Plan re-review after Service repair-context ownership scope fix: `docs/reviews/plan-review-20260607-094515.md`

## 3. Accepted Scope

Allowed implementation:

- Harden Ch2 writer prompt so numeric R/A/B/C/A-C closure statements in body, summary or evidence-source prose require nearby allowed anchor markers.
- Harden `programmatic:L1` repair context so the writer is told to fix conclusion/evidence-source repetitions as well as detailed required-output items.
- Keep L1 auditor fail-closed behavior unchanged.
- Add focused deterministic tests and Fund README synchronization.

Allowed files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`
- Slice 1D evidence/review/control artifacts under `docs/reviews/`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 4. Non-Goals / Prohibited Actions

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not change `_audit_numerical_closure()` to accept unanchored closure percentages.
- Do not increase repair budget or change repair retry policy.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop, golden/readiness, Host runtime or Agent runtime.
- Do not fix Ch4 `audit_parse`.
- Do not fix Ch3/Ch5 LLM blocking residuals.
- Do not fix Ch2 `delete_if_not_applicable` marker-obligation residual unless implementation evidence proves it is inseparable from the L1 prompt repair.
- Do not claim Ch2 live acceptance or full report acceptance.

## 5. Required Validation

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

## 6. Residual Tracking

Still open after implementation unless separately accepted:

- Ch2 live acceptance.
- Ch2 required-output marker C2 live proof.
- Ch2 `delete_if_not_applicable` marker-obligation residual.
- Ch4 `audit_parse`.
- Ch3/Ch5 LLM blocking residuals.
- Any surviving Ch6 pressure-test `must_not_cover` C2 residual.

Controller may proceed to implementation within this scope.
