# MVP Real Provider Smoke Independent Body Matrix Controller Judgment

## Gate / Role

- Gate: `MVP real provider smoke acceptance rerun with independent body chapter matrix`
- Role: Gateflow controller, not implementation worker.
- Date: 2026-05-31.
- Branch: `codex/local-reconciliation`.
- PR status: PR #21 remains draft/open; no push, merge, release or PR state change was made.

## Judgment

**Status: blocked with diagnostic complete.**

The real provider smoke did not pass because it did not produce a complete 0-7 report. The gate objective of rerunning the real provider after independent body chapter execution was satisfied, and the new evidence proves that chapters 1-6 are no longer hidden by synthetic `dependency_missing`.

Unique primary blocker: `provider_runtime_timeout`.

## Source Evidence

- Smoke evidence: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md`
- MiMo review: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-mimo-20260531.md`
- GLM review: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-review-glm-20260531.md`
- CLI raw files: `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/real-provider-cli.*`
- Service diagnostic JSON: `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`

## Validation Results

| Check | Result |
|---|---|
| deterministic analyze `006597 / 2024` | PASS, exit `0` |
| deterministic checklist `006597 / 2024` | PASS, exit `0` |
| missing-config `--use-llm` | PASS, exit `1`, stdout empty |
| real provider CLI smoke | BLOCKED, exit `1`, stdout empty |
| service-level safe diagnostic | PASS, JSON emitted |
| secret leak scan | PASS; one evidence wording match was a constraint sentence, not a secret |

No runtime code was changed, so full pytest/ruff were not rerun in this gate.

## Real Provider Outcome

CLI smoke:

- `exit_code=1`
- stdout bytes: `0`
- stderr classified `orchestration_status=partial`, `final_assembly_status=incomplete`
- no deterministic fallback
- CLI matrix: chapters 1-6 all visible; no `dependency_missing`

Service diagnostic:

- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- `report_markdown_present=false`
- `deterministic_fallback_observed=false`
- `generated_chapter_ids=[1,2,3,4,5,6]`
- `skipped_chapter_ids=[]`
- `accepted_chapter_ids=[4]`

## Controller Finding

Independent body chapter execution is proven in the real provider path:

- All six body chapters produced rows.
- `skipped_chapter_ids=[]`.
- No chapter 2-6 row was masked as synthetic `dependency_missing`.
- Final assembly correctly failed closed and did not emit a partial accepted report.

The real provider blocker is runtime timeout:

- Failed chapter rows have `stop_reason=llm_timeout`.
- Provider diagnostics record `ReadTimeout`, provider runtime category `timeout`, and elapsed time near the configured 60s per attempt.
- Timeout appears in both writer and auditor operations.
- Chapters 2 and 6 have very large writer prompt cost by existing heuristic: approximately `26086` and `29078` prompt tokens.
- Chapter 4 accepted in the service diagnostic, which is direct evidence that the write-audit pipeline can succeed when provider responses arrive.

## Rejected Classifications

| Candidate | Controller decision |
|---|---|
| `provider_config` | Rejected: config/auth had already been verified and current run reached real provider attempts. |
| `prompt_contract` | Rejected for this gate: diagnostic rows are timeout, not marker/contract failures. |
| `audit_parse` | Rejected: no audit parse failure evidence in this run. |
| `audit_rule_calibration` | Rejected as primary blocker: no accepted provider audit response reached a rule-calibration failure in failed rows. |
| `fact_gap` | Rejected: no missing-fact stop reason; final assembly failure is caused by timeout-blocked chapters. |
| `code_bug` | Rejected: chapter 4 accepted and final assembly fail-closed; no code exception or inconsistent state evidence. |
| `unknown` | Rejected: direct timeout diagnostics are sufficient. |

## Review Disposition

- MiMo review: PASS, no blocking findings.
- GLM review: PASS, no blocking findings.
- Shared residual: prompt cost for chapters 2 and 6 is extreme and should be addressed before another full smoke acceptance attempt.

## Next Smallest Entry Point

`MVP provider runtime budget and prompt-cost calibration gate`

Minimum scope:

- Keep provider config/auth out of scope unless env loading fails.
- Do not relax writer/auditor safety boundaries, evidence anchors, ITEM_RULE, candidate facet handling, transaction-advice boundary or E2 deferred semantics.
- Use the existing safe diagnostics to reduce prompt/runtime cost, especially chapters 2 and 6.
- Consider progress/phase observability for long CLI smoke, because current CLI intentionally emits only final stdout/stderr.
- Preserve deterministic analyze/checklist behavior and final assembly fail-closed semantics.

This gate is not accepted as a real-provider smoke pass. It is accepted as a diagnostic gate with a precise blocker and next entry.
