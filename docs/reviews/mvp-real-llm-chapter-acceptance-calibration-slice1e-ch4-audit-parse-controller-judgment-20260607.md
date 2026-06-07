# MVP Real LLM Chapter Acceptance Calibration Slice 1E Controller Judgment

## 1. Decision

`PLAN_ACCEPTED_FOR_IMPLEMENTATION`

Slice 1E Ch4 `audit_parse` plan is accepted for local implementation.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-095329.md`

## 3. Accepted Scope

Allowed implementation:

- Harden auditor prompt line-protocol instructions.
- Harden `llm:parse_failure` repair correction in Service repair context.
- Keep `_parse_llm_audit_response()` strict and unchanged.
- Add focused deterministic tests and Fund README synchronization.

Allowed files:

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- Slice 1E evidence/review/control artifacts under `docs/reviews/`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 4. Non-Goals / Prohibited Actions

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not relax `_parse_llm_audit_response()`.
- Do not store raw auditor response in diagnostics, reports or artifacts.
- Do not increase repair budget or change repair retry policy.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop, golden/readiness, Host runtime or Agent runtime.
- Do not fix Ch3/Ch5 LLM blocking residuals.
- Do not claim Ch4 live acceptance or full report acceptance.

## 5. Required Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

## 6. Residual Tracking

Still open after implementation unless separately accepted:

- Ch4 live acceptance.
- Ch4 required-output marker C2 live proof.
- Ch3/Ch5 LLM blocking residuals.
- Ch2 `delete_if_not_applicable` marker-obligation residual if deterministic evidence shows it survives.
- Any surviving Ch6 pressure-test C2 residual.

Controller may proceed to implementation within this scope.
