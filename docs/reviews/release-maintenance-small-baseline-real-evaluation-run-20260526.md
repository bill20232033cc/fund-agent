# Gate A Small Baseline Real Evaluation Run

> Date: 2026-05-26
> Worker: AgentCodex implementation/evidence specialist
> Scope: Gate A evidence only. No commit, push, PR, merge, delete, reset, rebase, GitHub mutation, source/test/default-flow change, durable fixture, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, repository/PDF/cache/source helper, `FundDocumentRepository`, `nav_data`, or quality-gate change.

## Truth Sources

- `AGENTS.md`
- `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / Current Gate
- `docs/design.md` current design sections
- Accepted artifacts:
  - `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`
  - `docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md`
  - `docs/reviews/release-maintenance-first-report-quality-improvement-slice-implementation-controller-judgment-20260526.md`

## Boundary

This run is a small offline evidence run over accepted candidates and accepted review evidence. It used current `ReportEvidenceBundle` JSON shape and current report-quality validator APIs:

- `fund_agent.fund.report_quality_validation.validate_report_quality_bundle`
- `fund_agent.fund.report_quality_validation.validate_report_quality_jsonl`
- `fund_agent.fund.report_evidence.REPORT_EVIDENCE_SCHEMA_VERSION`

Input boundary:

- Included only accepted candidate rows and reviewed-note facts derived from the accepted artifacts above.
- Did not call `fund-analysis analyze` or `fund-analysis checklist`.
- Did not fetch, parse, or read annual-report PDFs.
- Did not call production extractors, `FundDocumentRepository`, PDF/cache/source helpers, downloaders, source adapters, renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `nav_data`, or quality gate.
- Did not claim `scoring_ready`, `accepted_baseline`, durable fixture status, or new repository verification.

Source boundary:

- Bundle facts use `source_boundary="manual_review"` and `source_kind="reviewed_note"`.
- Source documents preserve accepted S0 identity provenance as `identity_status="verified_annual_report"` and `source_failure_category="none"` only for the three clean candidates.
- Fallback-blocked and type-gap rows remain exclusions / failure-category rows, not clean denominator inputs.

Scratch outputs:

- `/tmp/fund-agent-small-baseline-real-eval-20260526/manifest.json`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004393-2024.json`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004393-2024.jsonl`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004194-2024.json`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004194-2024.jsonl`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-006597-2024.json`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-006597-2024.jsonl`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/bundles.jsonl`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/failure-categories.json`
- `/tmp/fund-agent-small-baseline-real-eval-20260526/validator-result.json`

These files are scratch evidence only.

## Commands

| Step | Command | Exit | Result |
|---|---|---:|---|
| Read rule / control / design / accepted artifacts | `sed ... AGENTS.md docs/implementation-control.md docs/design.md docs/reviews/...` and `rg ...` | 0 | Confirmed current gate scope and API locations. |
| Initial evidence run | `mkdir -p /tmp/fund-agent-small-baseline-real-eval-20260526 && .venv/bin/python - <<'PY' ... PY` | 0 | Wrote manifest, 3 bundle JSON files, combined JSONL, failure categories, validator result. |
| Per-sample JSONL rerun | `.venv/bin/python - <<'PY' ... PY` | 0 | Wrote 3 single-sample JSONL files and appended per-sample JSONL validator results. |
| Category correction and rerun | `.venv/bin/python - <<'PY' ... PY` | 0 | Corrected active turnover issue to `chapter_contract`; rebuilt JSONL and validator summaries. |
| Result inspection | `jq ... /tmp/fund-agent-small-baseline-real-eval-20260526/validator-result.json` | 0 | Confirmed summary and failure-category matrix. |
| Scratch listing | `find /tmp/fund-agent-small-baseline-real-eval-20260526 -maxdepth 1 -type f -print | sort` | 0 | Confirmed expected scratch files. |
| JSONL line count | `wc -l /tmp/fund-agent-small-baseline-real-eval-20260526/*.jsonl` | 0 | Three per-sample JSONLs have 3 lines each; combined JSONL has 9 lines. |

## Evaluated Candidates

| fund_code | year | fund_type_slot | included in clean denominator | source_boundary | bundle path | JSONL path |
|---|---:|---|---|---|---|---|
| `004393` | 2024 | `active_fund` | Yes | `manual_review` reviewed-note evidence over accepted S0/S1/Gate D artifacts | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004393-2024.json` | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004393-2024.jsonl` |
| `004194` | 2024 | `enhanced_index` | Yes | `manual_review` reviewed-note evidence over accepted S0/Gate A/B artifacts | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004194-2024.json` | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-004194-2024.jsonl` |
| `006597` | 2024 | `bond_fund` | Yes | `manual_review` reviewed-note evidence over accepted S0/Gate A/B artifacts | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-006597-2024.json` | `/tmp/fund-agent-small-baseline-real-eval-20260526/bundle-006597-2024.jsonl` |
| `110020` | 2024 | `index_fund` | No | Exclusion row only | n/a | n/a |
| `017641` | 2024 | `qdii_fund` | No | Exclusion row only | n/a | n/a |
| `007721` | 2024 | `fof_fund` attempt | No | Data-gap row only | n/a | n/a |
| `017970` | 2024 | `fof_fund` attempt | No | Data-gap plus fallback-blocked row only | n/a | n/a |

The clean run covers three fund-type slots: `active_fund`, `enhanced_index`, and `bond_fund`. The requested priority slots are partially satisfied: active and bond are cleanly evaluated; `index_fund` remains fallback-blocked by accepted evidence, so it is recorded as `unknown_upstream_failure_category` instead of being promoted.

## Schema / Run IDs

| Field | Value |
|---|---|
| `run_id` | `evidence:small-baseline-real-eval:20260526` |
| `schema_version` | `report_evidence_bundle.v0` |
| `corpus_id` | `corpus:small-baseline-real-eval:20260526` |
| clean bundle count | 3 |
| clean score issue count | 6 |
| per-sample JSONL record count | 3 each: 1 bundle + 2 score_issue records |
| combined JSONL record count | 9: 3 bundle + 6 score_issue records |

## Validator Summary

Single-bundle API results:

| fund_code | total_records | blocking | material | minor | failed_closed | scoring_ready |
|---|---:|---:|---:|---:|---|---:|
| `004194` | 1 | 0 | 0 | 0 | false | 0 |
| `004393` | 1 | 0 | 0 | 0 | false | 0 |
| `006597` | 1 | 0 | 0 | 0 | false | 0 |

Single-sample JSONL API results:

| fund_code | total_records | blocking | material | minor | failed_closed | scoring_ready |
|---|---:|---:|---:|---:|---|---:|
| `004194` | 3 | 0 | 0 | 0 | false | 0 |
| `004393` | 3 | 0 | 0 | 0 | false | 0 |
| `006597` | 3 | 0 | 0 | 0 | false | 0 |

Combined JSONL result:

| JSONL | total_records | blocking | material | minor | failed_closed | scoring_ready | error_code_counts |
|---|---:|---:|---:|---:|---|---:|---|
| `/tmp/fund-agent-small-baseline-real-eval-20260526/bundles.jsonl` | 9 | 4 | 0 | 0 | true | 0 | `RQV_REF_MISSING=4` |

Interpretation:

- The current validator accepts each clean sample through both single-bundle and single-sample JSONL paths.
- The combined multi-bundle JSONL failed because current `validate_report_quality_jsonl()` validates extra `record_type="score_issue"` rows against the first bundle only. Score-issue rows for later bundles therefore reference ids outside the first bundle index. This is a validator/consumer limitation for multi-bundle JSONL, not a data-source or report-quality failure in the evaluated samples.
- No evaluated sample is `scoring_ready`; this is intentional.

## Issue Localization

| fund_code | chapter | dimension | status | severity | field / claim | primary category | localization |
|---|---|---|---|---|---|---|---|
| `004393` | `chapter_3` | `evidence_traceability` | `pass` | n/a | `manager_alignment.manager_holding` | evidence traceability | Narrow positive S1 dry-run row remains traceable. |
| `004393` | `chapter_3` | `chapter_contract_completeness` | `issue` | material | `turnover_rate` / style-consistency claim | chapter contract | Gate D wording contract is required before stable/style-consistency claim; renderer/report-writing remains deferred. |
| `004194` | `chapter_2` | `evidence_traceability` | `pass` | n/a | `benchmark` | evidence traceability | Benchmark context is represented with accepted candidate provenance. |
| `004194` | `chapter_2` | `fact_coverage` | `issue` | material | `tracking_error` | data/source extraction | Enhanced-index tracking-error / enhanced-deviation readiness is not proven by benchmark context alone. |
| `006597` | `chapter_1` | `evidence_traceability` | `pass` | n/a | `basic_identity` | evidence traceability | Bond-fund identity provenance is represented. |
| `006597` | `chapter_6` | `fact_coverage` | `issue` | material | `risk.bond_lens` | data/source extraction | Bond preferred-lens facts for duration/credit/leverage/liquidity/drawdown are not reviewed in this slice. |

## Failure Categories

| Candidate / issue | Category | Evidence |
|---|---|---|
| `004393` turnover/style-consistency | chapter contract | Same-source accepted evidence: S1 localized `turnover_rate` gap; Gate D accepted explicit insufficiency / next-minimum-validation wording and deferred renderer/report-writing. |
| `004194` tracking-error readiness | data/source extraction | Accepted candidate evidence supports enhanced-index identity and benchmark context only; no reviewed tracking-error readiness was promoted. |
| `006597` bond risk lens | data/source extraction | Accepted verifier design requires duration/credit/leverage/liquidity/drawdown facts before bond risk conclusions; current reviewed input does not include those values. |
| combined JSONL `RQV_REF_MISSING=4` | validator schema / consumer limitation | Current JSONL validator indexes extra score_issue rows against the first bundle only; per-sample JSONLs pass. |
| `110020` index | data/source extraction | Accepted S0 candidate is fallback-used via Eastmoney with unknown upstream failure category; excluded from clean denominator. |
| `017641` QDII | data/source extraction | Same fallback-blocked status as `110020`; excluded from clean denominator. |
| `007721` FOF attempt | corpus selection/fund-type taxonomy | Accepted evidence classifies QDII-FOF as `qdii_fund`; pure FOF coverage remains `data_gap`. |
| `017970` FOF attempt | corpus selection/fund-type taxonomy + data/source extraction | Type gap plus unknown upstream fallback category. |

## Evidence Traceability

- Each clean bundle contains reviewed-note anchors with `source_kind="reviewed_note"` and `source_strength="manual_review"`.
- Each valued fact has `source_anchor_ids` and `source_document_ids`.
- Each material issue links to a concrete `data_gap_refs` id.
- Each gap links back to the score issue through `score_issue_ids`.
- The per-sample JSONL validator returned no `RQV_TRACEABILITY_GAP`, `RQV_REF_MISSING`, `RQV_GAP_LINK_INCOMPLETE`, or `RQV_FIELD_MISSING`.

Evidence traceability is sufficient for this offline evidence run. It is not sufficient for durable baseline because the inputs are reviewed-note assemblies, not fully reviewed fact-prefill rows across all selected chapters.

## Chapter Contract

- Active-fund Chapter 3: current evidence supports Gate D's accepted contract direction. Missing or unreviewed turnover/style-change evidence must block unsupported stability / style-consistency / 言行一致 strong claims and preserve the next minimum validation question.
- Enhanced-index Chapter 2: benchmark context alone must not satisfy tracking-error or enhanced-return quality claims.
- Bond Chapter 6: bond risk conclusions need reviewed duration, credit, leverage, liquidity, and drawdown facts or explicit insufficiency wording.

The run supports a Gate B decision to prioritize chapter-contract / writing behavior for active-fund Chapter 3 only if the next gate is specifically renderer/report-writing scoped. For enhanced-index and bond, the immediate pressure is reviewed fact coverage / extraction evidence before writing quality.

## Validator Schema

Current schema is usable for single-sample evidence:

- `ReportEvidenceBundle` schema version is accepted.
- Bundle and per-sample JSONL validation pass for all three evaluated candidates.
- `N/A` / `chapter_summary` semantics were not stressed by the clean samples, because this run localized issues through explicit score_issue records and data gaps.

Observed schema / consumer limitation:

- Multi-bundle JSONL with extra score_issue rows is not currently consumable as a single combined artifact when score_issue rows reference later bundles. It fails with `RQV_REF_MISSING=4`.
- This does not require weakening the validator. A later dev-only reporting tool can either emit one JSONL per bundle, or the validator can receive a reviewed multi-bundle ownership change that scopes score_issue rows to their owning bundle.

## Report Writing Quality

The run did not evaluate rendered Markdown and did not call renderer or product default commands. Writing-quality conclusions are therefore limited:

- Active-fund Chapter 3 has a known required wording behavior from Gate D.
- Enhanced-index and bond rows should avoid strong conclusions until reviewed facts exist.
- No "buy" / "sell" recommendation boundary was tested here.

The evidence is enough to define writing constraints, not enough to score current product report writing.

## Corpus Selection / Fund-Type Taxonomy

- Clean denominator: `004393` / active, `004194` / enhanced index, `006597` / bond.
- Fallback-blocked: `110020` / index, `017641` / QDII.
- FOF remains `data_gap`: `007721` and `017970` are QDII-FOF/type-gap evidence, not fulfilled pure FOF coverage.
- This run satisfies "at least 3 fund_type_slot values" only by using `active_fund`, `enhanced_index`, and `bond_fund`. It does not cleanly cover `index_fund`, `qdii_fund`, or `fof_fund`.

## Root Cause Hypotheses

These hypotheses are limited to the same accepted evidence and scratch run outputs:

1. Active-fund Chapter 3: the immediate blocker is not validator schema; it is chapter-contract / report-writing behavior around unsupported stability or style-consistency claims when turnover/style-change evidence is missing or unreviewed.
2. Enhanced-index: the next likely blocker is data/source extraction or reviewed fact coverage for tracking-error / enhanced-deviation facts.
3. Bond: the next likely blocker is data/source extraction or reviewed fact coverage for bond preferred-lens risk facts.
4. Index/QDII fallback rows: the blocker is source-boundary recovery. The original upstream failure category must be recovered as `not_found` or `unavailable`, or the candidates must be replaced.
5. FOF: the blocker is corpus selection / fund-type taxonomy, because accepted QDII-FOF evidence does not fulfill pure `fof_fund` coverage.
6. Combined JSONL: the blocker is validator consumer semantics for multi-bundle score_issue rows, not the evaluated sample content.

## Sufficiency For Gate B

Evidence is sufficient for Gate B to make a narrow next-step decision:

- The current validator APIs can consume per-sample `ReportEvidenceBundle` and JSONL evidence for three clean candidates.
- The first concrete quality pressure is localized:
  - active: chapter contract / report-writing wording around turnover/style-consistency gap;
  - enhanced index and bond: data/source extraction or reviewed fact coverage;
  - index/QDII: source failure-category recovery;
  - FOF: taxonomy/corpus gap.

Evidence is not sufficient for:

- durable baseline fixture promotion;
- `scoring_ready` status;
- renderer or FQ0-FQ6 behavior change;
- product-flow integration;
- default `analyze` / `checklist` behavior change;
- Host/Agent/dayu work.

## Validation

Post-artifact validation commands:

```text
.venv/bin/python - <<'PY'
from fund_agent.fund.report_evidence import REPORT_EVIDENCE_SCHEMA_VERSION
from fund_agent.fund.report_quality_validation import validate_report_quality_bundle, validate_report_quality_jsonl
print(REPORT_EVIDENCE_SCHEMA_VERSION)
print(validate_report_quality_jsonl)
print(validate_report_quality_bundle)
PY
```

Expected purpose: minimal import / validator API availability check. Full tests and ruff are not necessary because no source or test file changed, and this gate intentionally did not touch runtime code paths. `git diff --check` is still required.

```text
git diff --check
```

Expected purpose: tracked Markdown whitespace check.

```text
git status --short
```

Expected purpose: confirm only the tracked review artifact changed, plus pre-existing unrelated untracked files.
