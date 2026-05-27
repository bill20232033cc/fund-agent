# 110020 Reviewed Coverage Candidate Evidence

> Worker: AgentCodex evidence worker, not controller  
> Date: 2026-05-27  
> Gate: `110020 reviewed coverage candidate evidence gate`  
> Scope: public-only evidence matrix for `110020` / report_year `2024`; no implementation, no promotion, no `docs/implementation-control.md` update

## Startup Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `110020 reviewed coverage candidate decision plan accepted locally` |
| Evidence gate | `110020 reviewed coverage candidate evidence gate` |
| Next entry point replayed | `110020 reviewed coverage candidate evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest checkpoint | `110020 reviewed coverage candidate decision plan local accepted commit; use latest branch HEAD for exact hash` |
| Current HEAD observed | `46e4f1318c7058d5447168bec6458f306b07b5b8` |
| Truth sources replayed | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted decision plan artifacts |
| Accepted plan artifacts | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md` |

Allowed:

- Run only the accepted public CLI evidence matrix for `110020` / `2024`.
- Keep generated outputs under ignored path `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/`.
- Write this tracked summary artifact only.
- Record public provenance, quality status, strict-golden absence, CSV identity, and independent index evidence assessment.

Forbidden:

- No code implementation.
- No renderer, FQ0-FQ6, Service, CLI default `analyze` / `checklist`, source strategy, `FundDocumentRepository`, source helper, extractor, cache, or PDF behavior changes.
- No direct PDF/cache/source-helper inspection.
- No durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus promotion.
- No `docs/implementation-control.md` update.
- No commit, push, PR, merge, branch deletion, or GitHub mutation.

## Command Summary

| Step | Command | Exit code | Output paths |
|---|---|---:|---|
| Public snapshot | `uv run fund-analysis extraction-snapshot --run-id 110020-reviewed-coverage-candidate-2024-20260527 --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527 --force-refresh` | 0 | `snapshot.jsonl`, `summary.md`, `errors.jsonl` under ignored run dir |
| Public score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527 --errors-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/errors.jsonl` | 0 | `score.json`, `score.md`, `golden_set.json` under ignored run dir |
| Public quality gate | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/score.json --output-dir reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527` | 0 | `quality_gate.json`, `quality_gate.md` under ignored run dir |
| Whitespace check | `git diff --check` | 0 | no output |

Generated outputs are ignored by `.gitignore` rule `reports/extraction-snapshots/`.

## CSV Identity / Version Note

| Item | Observed value |
|---|---|
| CSV path | `docs/code_20260519.csv` |
| Current HEAD | `46e4f1318c7058d5447168bec6458f306b07b5b8` |
| CSV last commit | `7596c5ece4894166d5479ee764fc8641a23cfc0d` |
| Git status | dirty due to pre-existing untracked docs: `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`, `docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md`, `docs/reviews/repo-review-20260526-231040.md`, `docs/tmux-agent-memory-store.md`; `docs/code_20260519.csv` itself is clean |
| CSV mtime | `May 19 00:28:41 2026` |
| CSV size | `3213 bytes` |

The accepted plan recorded an older observed repo HEAD `188f150cf27c6b3792a92ed11ebedb164b485ebb`; this run records current HEAD separately as evidence identity. CSV last commit, mtime, and size match the accepted plan.

## Public Output Shape

| Item | Observed value |
|---|---|
| Snapshot rows | 16 |
| Errors rows | 0 |
| Selected funds | 1 |
| Succeeded funds | 1 |
| Failed funds | 0 |
| Score field count | 16 |
| Score fund count | 1 |
| Score failed fund count | 0 |
| Quality gate status | `warn` |
| Quality gate issue count | 3 |

## Provenance Tuple

Accepted tuple from plan:

| Field | Accepted value |
|---|---|
| `fund_type_slot` | `index_fund` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |

Observed tuple from public `snapshot.jsonl`:

| Field | Observed value | Match |
|---|---|---|
| `fund_type_slot` | `index_fund` | yes |
| `source_strategy` | `primary_then_fallback` | yes |
| `resolved_source_name` | `eastmoney` | yes |
| `fallback_used` | `true` | yes |
| `primary_failure_category` | `unavailable` | yes |
| `fallback_eligibility` | `eligible` | yes |
| `source_provenance_status` | `complete` | yes |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | yes |

Disposition: provenance tuple is unchanged from the accepted tuple. No source/provenance stop condition triggered.

## Quality Gate Status And Warnings

| Rule | Severity | Observed issue | Accepted known set status |
|---|---|---|---|
| `FQ2` | `warn` | P1 field `turnover_rate` coverage / traceability below threshold | known accepted warning |
| `FQ2F` | `warn` | fund `110020` has P1 field failure: `turnover_rate` | known accepted warning |
| `FQ0` | `info` | strict golden answer not configured; correctness oracle not executed | known accepted info |

Quality gate status is `warn`, not `block`. No new P0/P1 warning beyond the accepted known warning set was observed.

## Strict Golden Absence Disposition

`score.md` and `quality_gate.md` both record correctness as unavailable because strict golden answer is not configured. This remains a carried-forward residual. The score in this evidence gate is not a strict correctness proof and must not be used as golden, fixture, clean denominator, or report-quality corpus acceptance.

## Index Evidence Assessment

| Evidence item | Assessment | Reason | Source pointer |
|---|---|---|---|
| `index_profile` | `sufficient` | Public snapshot classifies `110020` as `index_fund`, records benchmark context `沪深300指数收益率×95%+活期存款利率(税后)×5%`, has `value_present=true` and `anchor_present=true`, and score shows `index_profile` P1 pass with 100% coverage / traceability. This is sufficient for index identity / benchmark-context review, not for methodology or constituents claims. | `snapshot.jsonl` row `field_name=index_profile`, `section_id=§2`, `page=6`, `row_id=benchmark`; `score.md` Field Scores row `profile/index_profile` |
| `tracking_error` | `sufficient` | Public snapshot contains direct disclosed tracking-error evidence with `value_text=2%`, `source_type=direct_disclosure`, `calculation_method=disclosed`, `value_present=true`, and `anchor_present=true`; score shows `tracking_error` P1 pass with 100% coverage / traceability. `benchmark_identity_status=missing` is a residual limitation for later mature baseline/golden preflight, but the current reviewed tracking evidence is present and reviewable. | `snapshot.jsonl` row `field_name=tracking_error`, `section_id=§2`, `row_id=tracking_error`; `score.md` Field Scores row `performance/tracking_error` |
| benchmark-methodology / constituents / tracking evidence | `insufficient` | Public snapshot explicitly limits `index_profile` to benchmark context: `methodology_availability=benchmark_only`, `constituents_availability=benchmark_only`, `source_tier=benchmark_context`, and note says it must not be used as index methodology or constituent evidence. Tracking-error evidence is present, but methodology and constituents evidence remain insufficient without a separate reviewed public source. | `snapshot.jsonl` row `field_name=index_profile`, `comparable_values.methodology_availability`, `comparable_values.constituents_availability`, and `note` |

## Residuals Carried Forward

- `turnover_rate` remains a P1 coverage / traceability warning.
- Strict golden absence remains unresolved; correctness oracle was not executed.
- Reviewed-fact freeze for durable index-lens facts is not established by this evidence gate.
- Methodology / constituents evidence remains insufficient because public snapshot exposes only benchmark context.
- No fixture-promotion, baseline, clean denominator, report-quality corpus, or golden gate has accepted `110020`.

## Terminal State

`reviewed_coverage_candidate_input_accepted`

Rationale: public provenance is complete and unchanged from accepted tuple, quality remains `warn` with only the accepted known warning set, index identity and tracking-error evidence are reviewable from public outputs, and unresolved risks are explicitly carried forward. The candidate may be considered by a later baseline/golden preflight only after separate reviewed-fact, methodology/constituents, strict-golden, and promotion-gate requirements are satisfied.

## Promotion Disposition

`not_promoted`
