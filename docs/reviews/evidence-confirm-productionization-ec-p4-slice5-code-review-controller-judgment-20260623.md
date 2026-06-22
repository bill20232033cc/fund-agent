# Evidence Confirm Productionization EC-P4 Slice 5 Code Review Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code review / fix / targeted re-review controller judgment
- Slice: Slice 5 - No-Live Semantic Companion Propagation
- Classification: heavy
- Branch: evidence-confirm-productionization
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-controller-judgment-20260623.md`

## Inputs

- Implementation evidence: `docs/reviews/evidence-confirm-productionization-ec-p4-slice5-implementation-evidence-20260622.md`
- DS code review: `docs/reviews/code-review-20260623-000500-ds-ec-p4-slice5.md`
- MiMo code review: `docs/reviews/code-review-20260623-000500-mimo-ec-p4-slice5.md`
- Fix evidence: `docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-fix-20260623.md`
- DS targeted re-review: `docs/reviews/code-review-rereview-20260623-000900-ds-ec-p4-slice5.md`
- MiMo targeted re-review: `docs/reviews/code-review-rereview-20260623-000900-mimo-ec-p4-slice5.md`

## Controller Decision

Accepted.

Slice 5 now has no-live semantic companion propagation for already-produced typed semantic results:

- `summary_from_repository_result()` accepts optional injected `EvidenceSemanticResult`.
- Missing semantic input remains `semantic_status="not_run"`.
- Injected semantic fail/warn can project to ECQ4 through the quality-gate summary path.
- Deterministic V2 fail remains blocking even when semantic status is pass.
- Semantic result identity mismatch fails closed before propagation.
- No provider, OpenAI, LLM client, network, PDF, repository source, or provider config construction is introduced.

## Finding Disposition

| Finding | Source | Controller disposition | Final status |
|---|---|---|---|
| F-01: identity mismatch `ValueError` path lacked direct regression coverage | MiMo code review | accepted | 已修复 |

Rationale: F-01 covers the cross-sample contamination guard for injected semantic results. Even though the reviewer marked it informational, this is safety-critical test coverage for the slice invariant, so the controller accepted it and routed a test-only fix.

## Validation

Controller reproduced the focused validation after the fix:

```text
uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py -q
........................................................................ [ 92%]
......                                                                   [100%]
78 passed in 0.59s
```

```text
uv run ruff check tests/fund/test_evidence_confirm_semantic.py
All checks passed!
```

```text
git diff --check -- tests/fund/test_evidence_confirm_semantic.py docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-fix-20260623.md
<no output>
```

Pre-fix implementation validation also passed:

```text
uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py -q
76 passed

uv run ruff check fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate_integration.py fund_agent/services/fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py
All checks passed!
```

## Residual Risks

| Residual | Classification | Destination |
|---|---|---|
| Provider-backed semantic quality remains unproven | assigned to later work unit | Provider-backed semantic quality gate |
| Checklist Evidence Confirm CLI support remains absent | covered by later approved slice/gate | EC-P4 later slice or follow-up gate |
| Release/readiness remains `NOT_READY` | tracked by existing control state | PR-40 / EC-P4 readiness gates |

## Next Entry Point

EC-P4 implementation gate - Slice 6 Docs Sync and Control Evidence.

Do not claim default-on Evidence Confirm, checklist Evidence Confirm CLI support, provider-backed semantic quality, release/readiness, mark-ready or merge before separate reviewed gates.

## Verdict

ACCEPT_EC_P4_SLICE5_CODE_REVIEW_FIX_REREVIEW_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY
