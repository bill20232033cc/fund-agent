# MVP Real LLM Chapter Acceptance Calibration Slice 1F Controller Judgment

## 1. Decision

`PLAN_ACCEPTED_FOR_IMPLEMENTATION`

Slice 1F Ch3/Ch5 missing-semantics auditor plan is accepted for local implementation.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-095953.md`

## 3. Accepted Scope

Allowed implementation:

- Harden LLM auditor prompt so approved missing markers and cautious evidence-gap wording are not treated as missing-anchor/fact failures.
- Keep parser and programmatic audit strict and unchanged.
- Add focused deterministic tests and Fund README synchronization.

Allowed files:

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_chapter_auditor.py`
- Slice 1F evidence/review/control artifacts under `docs/reviews/`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 4. Non-Goals / Prohibited Actions

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not relax `_parse_llm_audit_response()`.
- Do not relax programmatic audit missing-marker, required-output marker or unknown-anchor checks.
- Do not change writer prompt, writer parser, required-output marker protocol or missing-marker parser.
- Do not store raw auditor response in diagnostics, reports or artifacts.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop, golden/readiness, Host runtime or Agent runtime.
- Do not claim Ch3/Ch5 live acceptance or full report acceptance.

## 5. Required Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py -q
```

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py
```

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py fund_agent/fund/README.md tests/fund/test_chapter_auditor.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

## 6. Residual Tracking

Still open after implementation unless separately accepted:

- Ch3/Ch5 live acceptance.
- Ch3/Ch5 required-output marker C2 live proof.
- Ch2 `delete_if_not_applicable` marker-obligation residual if deterministic evidence shows it survives.
- Any surviving Ch6 pressure-test C2 residual.

Controller may proceed to implementation within this scope.
