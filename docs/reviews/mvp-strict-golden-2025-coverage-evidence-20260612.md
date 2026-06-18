# Strict Golden 2025 Coverage Evidence Gate

Date: 2026-06-12

Gate: `Strict golden 2025 coverage evidence gate`

Verdict: `EVIDENCE_FOR_REVIEW`

## Scope

This is a no-live evidence gate.

It does not modify source, tests, runtime behavior, golden answers, fixture promotion state, source policy, fallback policy, README, design docs, release state, PR state or external state.

## Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-20260612.md`
- `docs/reviews/mvp-strict-golden-2025-coverage-promotion-plan-controller-judgment-20260612.md`
- accepted turnover narrow-fix implementation artifacts under `docs/reviews/`
- current code facts in:
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/fund/golden_readiness_preflight.py`

## Evidence Method

The evidence bundle was generated under:

```text
/tmp/fund-agent-strict-golden-2025-evidence/run-20260612
```

The synthetic input models one fund identity:

- snapshot: `004393 / 2025`
- strict golden answer: `004393 / 2024` only
- `turnover_rate`: absent in the 2025 annual-report snapshot
- source CSV: repository static selected-funds CSV `docs/code_20260519.csv`

No PDF, repository, cache, downloader, network, provider, LLM, analyze, checklist, readiness or release command was used.

The bundle calls the current in-repo APIs:

1. `run_extraction_score(...)`
2. `run_quality_gate(...)`
3. `run_golden_readiness_preflight(...)`

## Validation Commands

```text
git diff --name-only
docs/current-startup-packet.md
docs/implementation-control.md
fund_agent/fund/extraction_score.py
tests/fund/test_extraction_score.py
tests/services/test_fund_analysis_service.py
```

```text
git diff --check
<no output>
```

```text
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py -q
138 passed in 0.87s
```

```text
uv run ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py tests/fund/test_golden_readiness_preflight.py
All checks passed!
```

No-live synthetic evidence command:

```text
uv run python - <<'PY'
<script wrote /tmp/fund-agent-strict-golden-2025-evidence/run-20260612 and called score, quality gate and preflight APIs>
PY
```

Result: command exited `0`.

## Generated Evidence Artifacts

| Artifact | Size | SHA256 |
|---|---:|---|
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/inputs/snapshot-004393-2025.jsonl` | 3359 | `dbe4e110e9557a71c1857e3f383122e22b57a71f4470eb06491d50e455948c61` |
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/inputs/strict-golden-004393-2024-only.json` | 969 | `3fd99d0fe6e10cdc45f8bdba2635dcb6725a33cf9381b29f7ad24ec505b64a2c` |
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/score/score.json` | 9568 | `593cbd66aee6ea0ab76855d887be52ab708320f4d157eb280a7b5e5b36c67361` |
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/quality/quality_gate.json` | 1711 | `1a002509bc205849695815543adfbb26d917cac42134c9ec0d9ba4619c442e9a` |
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/preflight/golden_readiness_preflight.json` | 15435 | `9f414bac8bcf733e43e099455a5ea336897f7bdc5c04a9aac98972a0bd43351c` |
| `/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/evidence-summary.json` | 1986 | `730f5f25e0d791d789350c176ca4a3409ee122c7197ff4867230615163fe179e` |

The manifest is:

```text
/tmp/fund-agent-strict-golden-2025-evidence/run-20260612/artifact-manifest.json
```

## Direct Evidence

| Question | Evidence | Disposition |
|---|---|---|
| Does 2025 `turnover_rate` still produce field scoring failure? | `score.json`: `turnover_field_score_count=0`; `p1_failed_fields_by_fund["004393"]=[]`; `score_applicability_issues=[]`. | ACCEPT |
| Is 2025 `turnover_rate` excluded by applicability, not hidden by golden/readiness? | `score.json`: one `turnover_rate` applicability decision with `applicability_status=not_applicable_excluded`, `reason_code=turnover_rate_pre_effective_report_year`, `denominator_effect=excluded_no_replacement_issue`, `replacement_issue_ids=[]`. | ACCEPT |
| Does strict golden still identify year-specific residual? | `score.json`: `correctness.status=available`, `coverage_scope=year_not_covered`, `coverage_reason=year_not_covered`, `missing_fund_codes=["004393"]`. | ACCEPT |
| Does quality gate represent this residual as informational FQ0 rather than FQ2/FQ2F? | `quality_gate.json`: `status=pass`, issue `{rule_code=FQ0, severity=info, reason=year_not_covered, coverage_scope=year_not_covered}`; `turnover_fq2_or_fq2f_count=0`; `year_not_covered_fq0_count=1`. | ACCEPT |
| Is current preflight strict-golden coverage year-aware? | `golden_readiness_preflight.json`: row `strict_golden_coverage=covered` even though the artifact is `004393 / 2025` and strict golden only covers `004393 / 2024`; row blocker is `fixture_promotion_absent`, not `strict_golden_year_not_covered`. | ACCEPT_AS_GAP |
| Is promotion/readiness allowed now? | Preflight `overall_status=block`, `row_readiness=deferred_with_owner`, global blocker `fixture_promotion_absent`; evidence proves no readiness pass. | REJECT_PROMOTION_NOW |

## Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Accepted turnover fix removes the 2025 turnover warning path | ACCEPT | Current score/quality evidence shows no `turnover_rate` field score, no P1 failed field and no `FQ2/FQ2F` for turnover. |
| Remaining strict-golden residual is year-specific | ACCEPT | Score correctness is year-aware and reports `year_not_covered` for `004393 / 2025` when strict golden only covers `004393 / 2024`. |
| Quality gate blocks release on `year_not_covered` | REJECT | Current quality gate emits `FQ0/info` and aggregate `status=pass`; readiness must be decided by preflight/promotion gates, not by FQ0 alone. |
| Current preflight proves year-specific strict-golden coverage | REJECT | Current preflight v1 only loads fund-level strict golden coverage and returns `covered` for the synthetic 2025 artifact. |
| Fixture/golden promotion now | REJECT | `fixture_promotion_absent` remains a blocker and year-aware preflight semantics are not implemented. |
| Release/readiness claim | REJECT | This gate is evidence-only; preflight remains `block`. |
| `strict_golden_partial_coverage` implementation | DEFER | Not needed for the current single-fund/single-year evidence path. |

## Residuals

| Residual | Owner | Blocking for readiness? | Next gate |
|---|---|---:|---|
| Preflight strict-golden coverage is fund-level, not `(fund_code, report_year)` aware | Fund golden/readiness owner | Yes | `Strict golden year-aware preflight implementation gate` |
| Fixture promotion state absent | Release/readiness owner | Yes | Future fixture promotion / readiness gate after year-aware preflight |
| Strict golden does not cover `004393 / 2025` | Golden answer owner | Yes for promotion/readiness | Future strict-golden data/promotion gate, not this evidence gate |

## Controller Recommendation

Primary next entry:

```text
Strict golden year-aware preflight implementation gate
```

Deferred entries:

- fixture promotion state gate
- strict golden 2025 answer/promotion gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate

Release/readiness remains `NOT_READY`.
