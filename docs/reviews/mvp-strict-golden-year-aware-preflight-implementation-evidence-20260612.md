# Strict Golden Year-aware Preflight Implementation Evidence

Date: 2026-06-12

Gate: `Strict golden year-aware preflight implementation gate`

Verdict: `IMPLEMENTATION_FOR_REVIEW`

## Scope

This is a narrow no-live implementation gate.

## Accepted Inputs

- `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-controller-judgment-20260612.md`
- `docs/reviews/mvp-strict-golden-2025-coverage-evidence-controller-judgment-20260612.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Changed Files

| File | Change |
|---|---|
| `fund_agent/fund/golden_readiness_preflight.py` | Replaces fund-only strict golden coverage index with `StrictGoldenCoverage(fund_codes, fund_years)` and emits `strict_golden_year_not_covered` when the fund exists but `(fund_code, report_year)` is absent. Legacy missing `report_year` keeps `DEFAULT_REPORT_YEAR=2024`. |
| `tests/fund/test_golden_readiness_preflight.py` | Adds year-miss and matching-year tests; preserves `strict_golden_partial_coverage` as not emitted. |
| `fund_agent/fund/README.md` | Updates Fund README preflight semantics from fund-level-only to fund/year coverage. |

No source policy, extractor, PDF/cache/repository, provider, LLM, analyze/checklist, readiness/release, PR, cleanup or external-state behavior was changed.

## Implementation Decisions

| Decision | Status | Rationale |
|---|---|---|
| Keep `strict_golden_not_configured` when no strict golden answer path exists | IMPLEMENTED | Preserves existing configured/unconfigured semantics. |
| Keep `strict_golden_fund_not_covered` when the fund code is absent | IMPLEMENTED | Preserves existing fund-level miss semantics. |
| Add `strict_golden_year_not_covered` when fund exists but report year is absent | IMPLEMENTED | Closes the accepted evidence gap from the prior gate. |
| Preserve legacy missing `report_year` as `2024` | IMPLEMENTED | Existing minimal v1 tests keep legacy shape; loader uses `DEFAULT_REPORT_YEAR`. |
| Keep `strict_golden_partial_coverage` deferred | IMPLEMENTED | No partial coverage implementation was needed for this gate. |
| Keep promotion/readiness deferred | IMPLEMENTED | Preflight still blocks on strict-golden year miss and fixture promotion absence; no readiness claim is made. |

## Validation

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
16 passed in 1.05s
```

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py -q
138 passed in 0.99s
```

```text
uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py fund_agent/fund/README.md
All checks passed!
```

```text
git diff --check
<no output>
```

## No-live Synthetic Evidence

Evidence directory:

```text
/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612
```

Synthetic setup:

- snapshot: `004393 / 2025`
- strict golden answer: `004393 / 2024` only
- `turnover_rate`: absent in the 2025 annual-report snapshot
- source CSV: `docs/code_20260519.csv`

Output summary:

```json
{
  "preflight_blocker_codes": [
    "strict_golden_year_not_covered",
    "fixture_promotion_absent"
  ],
  "preflight_overall_status": "block",
  "preflight_strict_golden_coverage": "year_not_covered",
  "quality_issues": [
    {
      "coverage_scope": "year_not_covered",
      "reason": "year_not_covered",
      "rule_code": "FQ0",
      "severity": "info"
    }
  ],
  "quality_status": "pass",
  "score_coverage_scope": "year_not_covered"
}
```

Generated artifact manifest:

| Artifact | Size | SHA256 |
|---|---:|---|
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/inputs/snapshot-004393-2025.jsonl` | 3359 | `dbe4e110e9557a71c1857e3f383122e22b57a71f4470eb06491d50e455948c61` |
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/inputs/strict-golden-004393-2024-only.json` | 969 | `3fd99d0fe6e10cdc45f8bdba2635dcb6725a33cf9381b29f7ad24ec505b64a2c` |
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/score/score.json` | 9612 | `5e9b37252884b4ecd58bd6e95e83ec979fb57f7a3d4c4ee58431f83b4354f704` |
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/quality/quality_gate.json` | 1755 | `3544efd9623054ffec5f5b76e5fb365296df83de1610786bbe7f07d1bda84a5c` |
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/preflight/golden_readiness_preflight.json` | 15894 | `866b03e1f411bb3d1e127585f7e72ec43626dcd45c948162c4ddf599e72fe739` |
| `/tmp/fund-agent-strict-golden-year-aware-preflight-implementation/run-20260612/implementation-evidence-summary.json` | 545 | `7cb353b2b859c96239c11fa190508427f2f782a8cfa787ecfe7ce6e5fa61baa2` |

## Residuals

| Residual | Owner | Destination |
|---|---|---|
| Fixture promotion state remains absent | Release/readiness owner | Future fixture promotion/readiness gate |
| Strict golden 2025 accepted answer is not promoted | Golden answer owner | Future strict golden 2025 data/promotion gate |
| Release/readiness remains `NOT_READY` | Release owner | Future release-readiness rollup gate |

## Recommended Next Entry

Primary next entry:

```text
Strict golden year-aware preflight implementation review / controller acceptance
```

If accepted, route next mainline to:

```text
Fixture promotion state / strict golden 2025 promotion planning gate
```
