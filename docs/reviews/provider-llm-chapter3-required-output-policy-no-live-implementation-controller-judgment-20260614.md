# Provider/LLM Chapter 3 Required-output Policy No-live Implementation Controller Judgment

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`.

This judgment accepts or rejects the scoped no-live implementation for accepted policy plan checkpoint `2725c74` and controller judgment `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`.

It does not run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands, does not change source acquisition policy, provider defaults, repair budget, annual-period LLM route, Docling/parser policy, fallback policy, release state or PR state.

Release/readiness remains `NOT_READY`. EID remains the only operational annual-report source path.

## Evidence Reviewed

- Implementation evidence: `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-evidence-20260614.md`
- DS review: `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-review-ds-20260614.md`
- MiMo review: `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-review-mimo-20260614.md`
- Scoped implementation diff:
  - `docs/fund-analysis-template-draft.md`
  - `tests/fund/template/test_typed_contracts.py`
  - `tests/agent/test_runner.py`
  - `tests/services/test_fund_analysis_service_llm.py`
  - `tests/README.md`
- Controller validation:
  - `uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q`
  - `uv run ruff check tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py`
  - `git diff --check`

Forbidden body/payload/live/source reads were not used for this judgment.

## Accepted Current Facts

- Canonical `ch3.required_output.item_01` now uses `when_evidence_missing="render_evidence_gap"`.
- Item 01 reason now requires missing reviewed evidence to output an evidence gap and forbids unsupported manager-profile judgment.
- Item id, ordering, other Chapter 3 required-output policies, chapter ids, `must_answer`, `must_not_cover` and preferred lens are unchanged.
- `tests/fund/test_evidence_availability.py` is unchanged; item 01 still maps to `structured.basic_identity` and `structured.portfolio_managers`.
- Missing `EvidenceAvailability` envelope remains fail-closed before provider.
- Agent runner tests prove:
  - reviewed missing manager basic info with approved gap wording calls writer and accepts Chapter 3;
  - unsafe item 01 output without approved gap wording blocks after writer-output validation;
  - the new unsafe-output issue is `writer:required_output_gap_missing:ch3.required_output.item_01`, not old `required_output_block:ch3.required_output.item_01`.
- Service tests prove:
  - a full fake Route C body run with gap-rendered Chapter 3 can assemble chapters `0..7`;
  - unsafe Chapter 3 item 01 output keeps final assembly incomplete and report markdown absent.
- `tests/README.md` was updated only for two current test-surface descriptions matching the new item 01 behavior.
- No control docs, root README, `docs/design.md`, source acquisition code, provider runtime, repair budget, annual-period LLM route, Docling/parser policy, fallback policy or readiness/release/PR state was changed by this implementation.

## Review Finding Disposition

| Finding | Source | Disposition | Controller rationale |
| --- | --- | --- | --- |
| Template item 01 policy change is narrow and exact. | DS, MiMo | ACCEPT | Diff changes only item 01 behavior/reason in the canonical template. |
| Missing envelope fail-closed behavior is preserved. | DS, MiMo | ACCEPT | Existing fail-closed tests remain and focused suite passes. |
| Agent runner positive/negative coverage is complete. | DS, MiMo | ACCEPT | Tests cover accepted gap rendering and unsafe gap wording block with correct issue classification. |
| Service final assembly positive test uses full 1-6 body run and asserts chapters `0..7`. | DS, MiMo | ACCEPT | Satisfies controller amendment 1. |
| Service final assembly negative test directly covers unsafe Chapter 3 item 01 output. | DS, MiMo | ACCEPT | Satisfies controller amendment 2. |
| Docs update is narrow discovery-only. | DS, MiMo | ACCEPT | Only `tests/README.md` current test-surface lines changed; control/design/root README/historical artifacts untouched. |
| Scope boundaries and `NOT_READY` are preserved. | DS, MiMo | ACCEPT | No forbidden live/provider/source/readiness/release/PR action or overclaim observed. |
| `_FakeWriter` gained callable action support. | DS residual | ACCEPT_AS_TEST_INFRA_DETAIL | This is test-only infrastructure needed for the new targeted fixture and does not affect production behavior. |

## Validation Accepted

Controller re-ran:

```bash
uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q
```

Result: `74 passed`.

```bash
uv run ruff check tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Result: passed.

```bash
git diff --check
```

Result: passed.

## Accepted / Rejected / Residual Table

| Item | Decision | Basis | Next handling |
| --- | --- | --- | --- |
| No-live implementation | ACCEPT | DS PASS, MiMo PASS, controller validation passed | Local accepted checkpoint |
| Live/provider completion | NOT_CLAIMED | No live/provider command run | Separate bounded live evidence gate only |
| LLM content quality | NOT_CLAIMED | No provider/report content evidence accepted | Future content-quality/evidence gate |
| Source fallback / Eastmoney / CNINFO / fund-company expansion | REJECT | EID single-source/no-fallback remains current policy | Not authorized |
| Provider defaults / repair budget / annual-period LLM route / Docling/parser changes | REJECT | Out of scope and unchanged | Future reviewed gates only |
| Release/readiness / MVP-ready / LLM path ready | REJECT | No-live implementation is not readiness proof | Preserve `NOT_READY` |

## Next Gate Recommendation

Proceed after checkpoint and control-doc sync to:

`Provider/LLM Chapter 3 Required-output Policy Post-fix Bounded Live Re-evidence Gate`

That future gate must remain bounded to exact `004393 / 2025`, use safe runtime metadata only, preserve EID single-source/no-fallback, and must not declare release-ready, MVP-ready or LLM-path-ready. If live authorization is not active for that exact gate, route first to a no-live closeout/status gate.

## Control-doc Update Recommendation

After checkpointing this implementation, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Record:

- implementation accepted;
- checkpoint commit id;
- `NOT_READY` preserved;
- next entry point as post-fix bounded live re-evidence or no-live closeout depending on current authorization.

## Final Verdict

VERDICT: ACCEPT_IMPLEMENTATION_READY_FOR_BOUNDED_LIVE_RE_EVIDENCE_GATE_NOT_READY

The no-live implementation is accepted. It changes item 01 to safe evidence-gap rendering and proves no-live writer/final-assembly safety. Release/readiness remains `NOT_READY`.
