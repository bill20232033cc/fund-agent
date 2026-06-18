# MVP Real LLM Chapter Acceptance Calibration Gate Plan Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM chapter acceptance calibration gate`
- Classification: `heavy`
- Plan artifact: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-20260607.md`
- Initial plan review: `docs/reviews/plan-review-20260607-072727.md`
- Plan re-review: `docs/reviews/plan-review-20260607-072818.md`
- Role: controller judgment after plan review; not implementation evidence, live evidence, PR, push or release.

## 2. Preflight

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace includes unrelated tracked `pyproject.toml` and multiple unrelated untracked files.
- Gate-related current docs/reviews are allowed scope only if explicitly named below.

## 3. Review Summary

Initial plan review conclusion: `fail`

- Finding F1: Slice 1A required auditor to skip deleted typed required-output items without a stable action/marker-obligation contract.
- Controller accepted F1 as a blocking plan issue because implementation would otherwise need to copy writer private action logic or broaden public audit contracts.

Plan fix:

- Slice 1A now requires typed marker ids from `writer_input.typed_required_output_items`.
- Legacy path remains unchanged.
- `delete_if_not_applicable` filtering is deferred to a future marker-obligation sharing gate if real current evidence requires it.

Re-review conclusion: `pass`

- No blocking findings.
- Residual risks are accepted and tracked as follow-up evidence, not as Slice 1A success claims.

## 4. Controller Decision

Decision: `PLAN_ACCEPTED_SLICE_1A_AUTHORIZED`

Authorized Slice 1A:

- Update `fund_agent/fund/chapter_auditor.py` so `_audit_contract_markers()` checks typed required-output item id markers when `writer_input.typed_required_output_items` is present, and preserves legacy text marker checks otherwise.
- Add deterministic tests proving:
  - typed Ch1 item-id markers pass programmatic audit;
  - missing typed marker fails closed with C2;
  - legacy marker behavior remains unchanged;
  - Ch1 typed orchestration no longer fails solely because typed markers are used instead of legacy required-output text markers.
- Write implementation evidence to `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-implementation-evidence-20260607.md`.

Not authorized:

- no live LLM command;
- no provider/default/runtime/budget/timeout/model/base-url/config change;
- no endpoint probe, retry, fallback, PASS-only probe, curl/DNS/socket check;
- no Ch2 L1 numerical-closure calibration;
- no Ch4 audit-parse calibration;
- no Ch6 unknown-anchor fix;
- no Ch3/Ch5 calibration unless deterministic Slice 1A evidence justifies a later plan;
- no template JSON rewrite;
- no quality gate, final judgment, score-loop, golden/readiness, fixture, promotion, snapshot, Agent runtime, Host runtime, multi-year runtime, PR, push or release change.

## 5. Validation Requirements

Implementation must run at minimum:

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

If any command fails, stop and record failure evidence. Do not compensate with a live LLM run.

## 6. Next Action

Proceed to Slice 1A implementation under the allowed scope.
