# Controller Judgment - Strict Golden 2025 Coverage Evidence Gate

Date: 2026-06-12

Gate: `Strict golden 2025 coverage evidence gate`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## Basis

- `AGENTS.md`: evidence must be same-source; no source/runtime expansion without reviewed gate; readiness cannot be claimed from indirect proof.
- `docs/current-startup-packet.md`: current active gate before closeout was `Strict golden 2025 coverage evidence gate`.
- `docs/implementation-control.md`: active gate objective was to prove post-fix 2025 strict-golden residual and preserve `NOT_READY`.
- Evidence artifact: `docs/reviews/mvp-strict-golden-2025-coverage-evidence-20260612.md`.
- MiMo review: `docs/reviews/mvp-strict-golden-2025-coverage-evidence-review-mimo-20260612.md`.
- DS review: `docs/reviews/mvp-strict-golden-2025-coverage-evidence-review-ds-20260612.md`.

## Judgment

The evidence gate is accepted.

Direct evidence proves:

- accepted turnover applicability logic removes 2025 `turnover_rate` from field scoring and quality warning identity;
- strict-golden scoring remains year-aware and reports `coverage_scope=year_not_covered` for `004393 / 2025` when strict golden only covers `004393 / 2024`;
- quality gate maps this residual to `FQ0/info`, not `FQ2/FQ2F`;
- current `golden_readiness_preflight` v1 is still fund-level for strict golden coverage and reports `strict_golden_coverage=covered` for the same 2025 artifact;
- promotion/readiness is not proven; preflight remains blocked by `fixture_promotion_absent`.

Release/readiness remains `NOT_READY`.

## Finding Disposition

| Finding | Source | Disposition | Rationale |
|---|---|---|---|
| 2025 `turnover_rate` no longer produces scoring or quality warning failure | Evidence, MiMo, DS | ACCEPT | `turnover_field_score_count=0`, `p1_failed_fields=[]`, no `FQ2/FQ2F` turnover issue. |
| Remaining strict-golden residual is year-specific | Evidence, MiMo, DS | ACCEPT | Score correctness emits `year_not_covered` for `004393 / 2025` with strict golden only for `004393 / 2024`. |
| Quality gate residual is informational | Evidence, MiMo, DS | ACCEPT | `quality_gate.json` emits `FQ0/info` with `coverage_scope=year_not_covered`. |
| Current preflight gap is proven | Evidence, MiMo, DS | ACCEPT_AS_IMPLEMENTATION_INPUT | Preflight reports fund-level `strict_golden_coverage=covered` for the 2025 artifact, so year-aware preflight implementation is the next narrow fix. |
| Synthetic command body is summarized in artifact | MiMo | ACCEPT_AS_NON_BLOCKING | Full generated inputs/outputs have path, size and SHA256; summary/manifest are readable under `/tmp`; no acceptance claim depends on an opaque old report. |
| Control docs need post-acceptance sync | DS | ACCEPT_AS_REQUIRED_ACTION | Startup/control docs must move active gate to the next implementation gate after this judgment. |

## Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| `Strict golden 2025 coverage evidence gate` | ACCEPTED | Evidence and two reviews pass with no blockers. |
| Treat 2025 turnover absence as extractor failure | REJECTED | The accepted applicability rule excludes pre-2026 turnover from scoring. |
| Treat current preflight strict-golden coverage as year-aware | REJECTED | Evidence shows it is fund-level in this path. |
| Fixture/golden promotion now | REJECTED | `fixture_promotion_absent` remains blocking and year-aware preflight is not implemented. |
| Release/readiness claim | REJECTED | This gate is evidence-only and preflight remains `block`. |
| `strict_golden_partial_coverage` work | DEFERRED | Not needed for the current single-fund/year proof. |

## Residuals

| Residual | Owner | Current blocker? | Destination |
|---|---|---:|---|
| Preflight strict-golden coverage is fund-level, not `(fund_code, report_year)` aware | Fund golden/readiness owner | Yes for readiness/promotion | `Strict golden year-aware preflight implementation gate` |
| Fixture promotion state absent | Release/readiness owner | Yes for readiness/promotion | Future fixture promotion/readiness gate |
| Strict golden does not cover `004393 / 2025` | Golden answer owner | Yes for promotion/readiness | Future strict-golden data/promotion gate |

## Next Entry

Primary next entry:

```text
Strict golden year-aware preflight implementation gate
```

Deferred entries:

- fixture promotion state gate
- strict golden 2025 answer/promotion gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate

No live, PR, merge or release external-state action is authorized by this judgment.
