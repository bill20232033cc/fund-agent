# Report-Quality Validator Quasi-Real Bundle Controller Judgment - 2026-05-26

## Scope

This judgment closes the local-only `report-quality validator quasi-real bundle evidence run` gate.

Accepted evidence artifact:

- `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`

Scratch evidence:

- `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
- `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json`

The scratch files are not durable fixtures, not baseline material, not tracked reports, and not product-flow output.

## Controller Verification

Read-back verification of `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json`:

| Field | Value |
|---|---:|
| `run_id` | `evidence:report-quality-validator-quasi-real-bundle:20260525` |
| `schema_version` | `report_evidence_bundle.v0` |
| `bundle_record_count` | 1 |
| `score_issue_record_count` | 2 |
| bundle API `summary.total_records` | 1 |
| bundle API `summary.scoring_ready_record_count` | 0 |
| bundle API `summary.failed_closed` | `false` |
| bundle API `summary.error_code_counts` | `[]` |
| JSONL API `summary.total_records` | 3 |
| JSONL API `summary.scoring_ready_record_count` | 0 |
| JSONL API `summary.failed_closed` | `false` |
| JSONL API `summary.error_code_counts` | `[]` |

Focused validation:

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_report_quality_validation.py` | `25 passed` |
| `uv run ruff check fund_agent/fund/report_quality_validation.py fund_agent/fund/report_evidence.py tests/fund/test_report_quality_validation.py` | `All checks passed!` |
| `git diff --check` | passed with no output |
| `git ls-files \| rg -n "report-quality-validator-real-bundle\|input\\.jsonl\|result\\.json"` | exit 1, expected no tracked scratch match |

Boundary verification:

- no source, tests, README, renderer, Service, CLI, FQ0-FQ6, quality gate, extraction score, fixtures, tracked reports, Host/Agent/dayu, pyproject, or lockfile changes were made for the evidence run;
- no annual report fetch or parse was performed;
- no `FundDocumentRepository`, PDF/cache/source helper, downloader, source adapter, or production extractor was used;
- the input is labeled `quasi_real_review_evidence`;
- the input does not claim `repository_verified`, `scoring_ready`, or `accepted_baseline`.

## Failure-Category Decision

The validator contract is not the blocker for this quasi-real input.

Accepted classification:

| Category | Decision | Evidence |
|---|---|---|
| `validator schema` | not the next blocker | both bundle and JSONL validation returned no issues, no fail-closed state |
| `evidence traceability` | narrow positive evidence | manager-holding traceability issue row is `pass` and anchor-backed |
| `chapter contract` | recommended next gate | material quasi-real issue is `turnover_rate` gap in `chapter_3`; current control decision already says turnover stability wording should be constrained before extraction work |
| `data/source extraction` | defer | do not open extraction until chapter contract decides the exact required turnover/style-change evidence |
| `report writing quality` | defer | no renderer/report-writing evidence was generated in this gate |
| `corpus selection / fund-type taxonomy` | defer | FOF coverage and QDII-FOF taxonomy remain unresolved; not touched here |

## Accepted Conclusion

The quasi-real evidence run is accepted as consumer-contract evidence for the current report-quality validator.

It proves:

- one manually assembled `quasi_real_review_evidence` `ReportEvidenceBundle` can be consumed by `validate_report_quality_bundle()`;
- a single-bundle JSONL with linked score-issue records can be consumed by `validate_report_quality_jsonl()`;
- summary fields, schema version, run id, source path, record counts, and issue localization are replayable from the scratch result JSON;
- the next implementation decision should be driven by failure category, not subjective report taste.

It does not prove:

- repository identity;
- extraction correctness;
- durable baseline readiness;
- Service/CLI integration readiness;
- renderer or FQ0-FQ6 readiness;
- Host/Agent/dayu runtime readiness;
- FOF corpus coverage.

## Recommended Next Gate

Recommended next gate:

`active-fund chapter 3 turnover/style-consistency contract wording plan`

Goal:

- define the exact CHAPTER_CONTRACT / ITEM_RULE / scoring wording behavior for active-fund chapter 3 when turnover-rate or style-change evidence is unavailable or not reviewed;
- ensure the report must state insufficiency and the next minimum validation question instead of making unsupported stability / style-consistency claims;
- only after this contract is accepted, decide whether data extraction work is required.

Stop conditions:

- do not modify renderer or report output until the contract plan is accepted and reviewed;
- do not add turnover extraction until the accepted chapter contract requires it;
- do not promote this quasi-real bundle to durable baseline;
- do not enter Service/CLI/FQ0-FQ6 integration;
- do not open Host/Agent/dayu work.

Rejected next paths:

| Path | Reason |
|---|---|
| durable baseline promotion | evidence is quasi-real and intentionally not scoring-ready |
| Service/CLI integration | no user/developer workflow boundary review yet |
| FQ0-FQ6 integration | explicitly outside current non-goals |
| renderer change | would turn diagnostic evidence into product output change prematurely |
| data extraction first | chapter contract must define the exact evidence requirement first |
| Host/Agent/dayu | unrelated architecture gate |

## Residuals

| Residual | Owner / next gate | Blocker? |
|---|---|---|
| quasi-real evidence is not repository-verified | future corpus / repository evidence gate | No |
| FOF pure-fund coverage remains missing | future corpus selection / fund-type taxonomy gate | No |
| fallback upstream category recovery remains unresolved | future source reliability evidence gate | No |
| multi-bundle validator aggregation remains unproven | future validator hardening/tooling gate | No |
| `nav_data` and derived calculations remain excluded | future source-contract/calculation projection gate | No |

## Local Acceptance

This gate is accepted locally. The next safe task is planning/review for the active-fund chapter 3 turnover/style-consistency contract.
