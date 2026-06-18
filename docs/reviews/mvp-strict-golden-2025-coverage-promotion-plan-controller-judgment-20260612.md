# Controller Judgment - Strict Golden 2025 Coverage / Promotion Planning Gate

Date: 2026-06-12

Gate: `Strict golden 2025 coverage / promotion planning gate`

Verdict: `ACCEPT_NOT_READY`

## Basis

- `AGENTS.md`: evidence must be same-source; no indirect proof; no source/runtime expansion without reviewed gate.
- `docs/current-startup-packet.md`: current active gate is `Strict golden 2025 coverage / promotion planning gate`.
- `docs/implementation-control.md`: current mainline follows accepted turnover-rate regulatory applicability narrow fix implementation.
- Accepted plan: `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-20260612.md`.
- MiMo review: `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-review-mimo-20260612.md`.
- DS review: `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-review-ds-20260612.md`.

## Judgment

The plan is accepted.

The next mainline gate is:

`Strict golden 2025 coverage evidence gate`

This must be an evidence-first, no-live, no source/test/runtime behavior change gate. It should not proceed directly to implementation or promotion.

## Finding Disposition

| Finding | Source | Disposition | Rationale |
|---|---|---|---|
| Plan distinguishes accepted turnover fix from strict-golden residual | MiMo, DS | ACCEPT | The plan preserves accepted scoring/applicability facts and does not reclassify 2025 non-disclosed turnover as extractor failure. |
| Plan routes next step to evidence, not implementation | MiMo, DS | ACCEPT | Evidence must first prove the remaining residual is `year_not_covered` / `FQ0/info` after turnover warning removal. |
| Plan does not prematurely claim promotion/readiness | MiMo, DS | ACCEPT | Promotion and release/readiness remain explicitly deferred. |
| Evidence gate must not reuse arbitrary `reports/` residue | MiMo | ACCEPT_AS_REQUIRED_GUARD | The evidence gate must use current-gate generated inputs or captured path/size/hash/lineage. |

## Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| `Strict golden 2025 coverage evidence gate` as next entry | ACCEPTED | Both reviews agree evidence must precede implementation. |
| Direct `Strict golden year-aware preflight implementation gate` now | REJECTED | Implementation requires evidence that current preflight semantics are an active product gap. |
| Treat 2025 `turnover_rate` as current blocker | REJECTED | Accepted turnover applicability fix excludes pre-2026 turnover from scoring. |
| Promote 2025 strict golden/fixture now | REJECTED | Year-specific coverage and fixture promotion state are not accepted. |
| Claim release/readiness | REJECTED | This is planning only; release/readiness remains `NOT_READY`. |
| Future year-aware preflight implementation | DEFERRED | Open only if evidence gate proves need. |

## Next Gate Boundary

Next gate:

`Strict golden 2025 coverage evidence gate`

Allowed write set:

- evidence artifact under `docs/reviews/`
- two review artifacts under `docs/reviews/`
- controller judgment under `docs/reviews/`
- `docs/current-startup-packet.md` and `docs/implementation-control.md` after acceptance

Allowed commands:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py -q
uv run ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py
```

Explicitly disallowed:

- source/test/runtime behavior changes
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR commands
- golden answer edits
- fixture promotion state edits
- source fallback or source expansion
- cleanup/delete/archive/import/ignore

## Validation

Planning gate validation:

```text
git diff --check
<no output>
```

Full status checks are deferred to final control-sync validation for this planning closeout.

## Final State

`Strict golden 2025 coverage / promotion planning gate` is accepted.

Release/readiness remains `NOT_READY`.
